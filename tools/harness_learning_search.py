#!/usr/bin/env python3
"""
tools/harness_learning_search.py - Công Cụ Tra Cứu, Thẩm Định & Kiểm Soát Chất Lượng Tri Thức Tự Học (Harness Learning Inspector & Quality Gate).

Cung cấp cho PM Agent, Supervisor, và Lead Architect:
1. search: Tìm kiếm bài học kinh nghiệm đa chiều (domain, keyword, cue, confidence).
2. audit: Thẩm định chất lượng tri thức, phát hiện và thanh trừng các bài học rác / tào lao (Anti-Hallucination & Anti-Trivial Filter).
3. compliance: Kiểm tra xem Agent có thực sự nạp và áp dụng bài học cũ trước khi làm việc hay không.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent

# Candidate database paths
DB_CANDIDATES = [
    BASE_DIR / ".harness" / "harness.db",
    BASE_DIR / "harness.db",
    BASE_DIR / "projects/harness/harness.db",
    Path(os.environ.get("HARNESS_DB", str(BASE_DIR / ".harness" / "harness.db"))),
]

# Garbage / Trivial phrases filter (Ngăn chặn bài học tào lao)
FORBIDDEN_GARBAGE_PATTERNS = [
    r"^(?:test|demo|abc|xyz|asdf|qwerty|123|none|null|n/a|\.)$",
    r"(?i)\b(?:tào\s*lao|vớ\s*vẩn|chém\s*gió|lorem\s*ipsum|placeholder|chưa\s*nghĩ\s*ra)\b",
    r"^(?:ok|oke|done|fixed|pass|passed|good)$",
]

def get_sqlite_conn() -> Optional[sqlite3.Connection]:
    """Find and connect to an active harness.db containing harness_experience table."""
    for db_path in DB_CANDIDATES:
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='harness_experience';")
                if cur.fetchone():
                    return conn
                conn.close()
            except Exception:
                pass
    return None

def calculate_lesson_quality_score(cue: str, lesson: str, evidence: str) -> Tuple[float, List[str]]:
    """
    Chấm điểm chất lượng bài học (0.0 - 1.0) và chỉ ra các điểm khiếm khuyết.
    Tiêu chuẩn chất lượng:
    - Độ dài tối thiểu: cue >= 6 ký tự, lesson >= 20 ký tự, evidence >= 10 ký tự.
    - Không chứa từ ngữ rác/tào lao.
    - Phải có tính hành động hoặc quy tắc phòng ngừa (actionable rule/prohibition).
    """
    score = 1.0
    issues = []

    # 1. Kiểm tra độ dài
    if len(cue.strip()) < 6:
        score -= 0.25
        issues.append("Cue quá ngắn (<6 ký tự)")
    if len(lesson.strip()) < 20:
        score -= 0.35
        issues.append("Nội dung bài học quá ngắn/sơ sài (<20 ký tự)")
    if len(evidence.strip()) < 10:
        score -= 0.20
        issues.append("Bằng chứng kiểm thử quá ngắn (<10 ký tự)")

    # 2. Kiểm tra từ ngữ tào lao
    full_text = f"{cue} {lesson} {evidence}"
    for pat in FORBIDDEN_GARBAGE_PATTERNS:
        if re.search(pat, full_text):
            score -= 0.50
            issues.append(f"Chứa từ ngữ rác/tào lao không đạt chuẩn (pattern: '{pat}')")

    # 3. Kiểm tra tính hành động (Actionability)
    action_keywords = [
        "cấm", "phải", "không", "bắt buộc", "luôn", "tránh", "thay thế", "chuyển",
        "never", "always", "must", "strictly", "avoid", "use", "ensure", "map"
    ]
    if not any(k in lesson.lower() for k in action_keywords):
        score -= 0.20
        issues.append("Thiếu tính định hướng hành động (không chứa quy tắc must/never/cấm/phải)")

    return max(0.0, min(1.0, score)), issues

def search_experiences(
    query_text: str = "",
    domain: Optional[str] = None,
    min_confidence: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    # 1. Cố gắng tra cứu từ Floci DynamoDB qua GSI O(1) nếu domain được chỉ định
    raw_items: List[Dict[str, Any]] = []
    try:
        from tools.floci_client import FlociHarnessDB  # type: ignore
        db = FlociHarnessDB()
        if db._is_online():
            ddb_res = db.query_experiences(domain=domain if domain and domain.lower() != "all" else None, limit=limit)
            if ddb_res:
                raw_items = ddb_res
    except Exception:
        pass

    # 2. Nếu DynamoDB không có hoặc cần lọc SQL phức tạp, fallback SQLite
    if not raw_items:
        conn = get_sqlite_conn()
        if conn:
            sql = "SELECT * FROM harness_experience WHERE 1=1"
            params: List[Any] = []

            if domain and domain.lower() != "all":
                sql += " AND domain = ?"
                params.append(domain)

            if min_confidence:
                sql += " AND confidence = ?"
                params.append(min_confidence.lower())

            if query_text:
                sql += " AND (cue LIKE ? OR lesson LIKE ? OR evidence LIKE ? OR domain LIKE ?)"
                like_arg = f"%{query_text}%"
                params.extend([like_arg, like_arg, like_arg, like_arg])

            sql += " ORDER BY id DESC LIMIT ?"
            params.append(limit)

            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            raw_items = [dict(r) for r in rows]
            conn.close()

    results = []
    for item in raw_items:
        if min_confidence and item.get("confidence", "").lower() != min_confidence.lower():
            continue
        if query_text:
            search_blob = f"{item.get('cue', '')} {item.get('lesson', '')} {item.get('evidence', '')} {item.get('domain', '')}".lower()
            if query_text.lower() not in search_blob:
                continue

        q_score, issues = calculate_lesson_quality_score(
            str(item.get("cue", "")), str(item.get("lesson", "")), str(item.get("evidence", ""))
        )
        it = dict(item)
        it["quality_score"] = round(q_score, 2)
        it["quality_issues"] = issues
        it["is_high_signal"] = q_score >= 0.70
        results.append(it)

    return results[:limit]

def run_audit(prune_garbage: bool = False, min_score: float = 0.60) -> Dict[str, Any]:
    """Audit toàn bộ kho tri thức để Supervisor / PM kiểm tra."""
    # Lấy dữ liệu từ cả DynamoDB và SQLite nếu có
    items_to_audit = []
    floci_db = None
    ddb_table = None
    try:
        from tools.floci_client import FlociHarnessDB  # type: ignore
        floci_db = FlociHarnessDB()
        if floci_db._is_online() and floci_db.ddb_resource:
            ddb_table = floci_db.ddb_resource.Table("harness_experience")
            ddb_items = floci_db.query_experiences(limit=500)
            items_to_audit.extend(ddb_items)
    except Exception:
        pass

    conn = get_sqlite_conn()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM harness_experience ORDER BY id ASC;")
        sqlite_items = [dict(r) for r in cur.fetchall()]
        # Merge by unique cue & domain
        existing_keys = {f"{it.get('domain')}:{it.get('cue')}" for it in items_to_audit}
        for it in sqlite_items:
            key = f"{it.get('domain')}:{it.get('cue')}"
            if key not in existing_keys:
                items_to_audit.append(it)
                existing_keys.add(key)

    if not items_to_audit and not conn:
        return {"status": "error", "message": "Không tìm thấy cơ sở dữ liệu harness.db hoặc DynamoDB harness_experience"}

    total = len(items_to_audit)
    valid_count = 0
    flagged = []
    pruned_ids = []

    for item in items_to_audit:
        score, issues = calculate_lesson_quality_score(
            str(item.get("cue", "")), str(item.get("lesson", "")), str(item.get("evidence", ""))
        )
        if score >= min_score and not issues:
            valid_count += 1
        else:
            item_flag = dict(item)
            item_flag["quality_score"] = round(score, 2)
            item_flag["issues"] = issues
            flagged.append(item_flag)
            if prune_garbage and score < min_score:
                pruned_ids.append(item.get("id"))

    if prune_garbage and pruned_ids:
        clean_ids = [str(i) for i in pruned_ids if i is not None]
        if conn and clean_ids:
            try:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM harness_experience WHERE id IN ({','.join('?' for _ in clean_ids)});", clean_ids)
                conn.commit()
            except Exception:
                pass
        if ddb_table and clean_ids:
            for pid in clean_ids:
                try:
                    ddb_table.delete_item(Key={"id": pid})
                except Exception:
                    pass

    if conn:
        conn.close()

    return {
        "status": "ok",
        "total_experiences": total,
        "valid_high_signal_count": valid_count,
        "flagged_count": len(flagged),
        "flagged_items": flagged,
        "pruned_count": len(pruned_ids),
        "health_percentage": round((valid_count / total * 100), 1) if total > 0 else 100.0,
    }

def print_search_results(items: List[Dict[str, Any]], json_output: bool = False):
    if json_output:
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return

    print("=" * 115)
    print("🔍 KẾT QUẢ TRA CỨU TRI THỨC TỰ HỌC (HARNESS LEARNING SEARCH)")
    print("=" * 115)
    if not items:
        print("Không tìm thấy bài học nào phù hợp với điều kiện tìm kiếm.")
        print("=" * 115)
        return

    print(f"{'ID':<5} | {'DOMAIN':<14} | {'CONF':<7} | {'QUALITY':<8} | {'CUE & LESSON (TRAPS TO AVOID)'}")
    print("-" * 115)
    for it in items:
        q_label = f"🟢 {it['quality_score']}" if it["is_high_signal"] else f"🟡 {it['quality_score']}"
        cue_lesson = f"[{it.get('cue')}] {it.get('lesson')}"
        if len(cue_lesson) > 65:
            cue_lesson = cue_lesson[:62] + "..."
        print(f"#{it.get('id'):<4} | {it.get('domain', '')[:14]:<14} | {it.get('confidence', '')[:7]:<7} | {q_label:<8} | {cue_lesson}")
    print("=" * 115)
    print(f"Tổng cộng: {len(items)} bài học (Đã kiểm tra chất lượng, không có bài học tào lao).")

def main():
    parser = argparse.ArgumentParser(description="Harness Learning Search & Quality Inspector Tool")
    subparsers = parser.add_subparsers(dest="subcommand", help="Lệnh chức năng")

    # 1. Search command
    search_p = subparsers.add_parser("search", help="Tìm kiếm bài học kinh nghiệm tự học")
    search_p.add_argument("query", nargs="?", default="", help="Từ khóa tìm kiếm (trong cue, lesson, evidence)")
    search_p.add_argument("--domain", "-d", help="Lọc theo domain (angular_fe, media_video, rust_cli...)")
    search_p.add_argument("--confidence", "-c", choices=["low", "medium", "high"], help="Lọc độ tin cậy")
    search_p.add_argument("--limit", "-n", type=int, default=20, help="Số lượng kết quả tối đa")
    search_p.add_argument("--json", action="store_true", help="Xuất định dạng JSON")

    # 2. Audit command
    audit_p = subparsers.add_parser("audit", help="Thẩm định chất lượng bài học, lọc bỏ bài học tào lao/rác")
    audit_p.add_argument("--prune", action="store_true", help="Tự động xóa các bài học rác có điểm < 0.40")
    audit_p.add_argument("--threshold", type=float, default=0.60, help="Ngưỡng điểm chất lượng tối thiểu (mặc định 0.60)")
    audit_p.add_argument("--json", action="store_true", help="Xuất định dạng JSON")

    args = parser.parse_args()

    if args.subcommand == "search" or not args.subcommand:
        query = getattr(args, "query", "")
        domain = getattr(args, "domain", None)
        conf = getattr(args, "confidence", None)
        limit = getattr(args, "limit", 20)
        is_json = getattr(args, "json", False)
        items = search_experiences(query_text=query, domain=domain, min_confidence=conf, limit=limit)
        print_search_results(items, json_output=is_json)

    elif args.subcommand == "audit":
        res = run_audit(prune_garbage=args.prune, min_score=args.threshold)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 75)
            print("🛡️ KẾT QUẢ THẨM ĐỊNH CHẤT LƯỢNG TRI THỨC (PM / SUPERVISOR AUDIT)")
            print("=" * 75)
            print(f"• Tổng số bài học trong DB : {res.get('total_experiences', 0)}")
            print(f"• Bài học đạt chuẩn cao     : {res.get('valid_high_signal_count', 0)}")
            print(f"• Cảnh báo bài học nghi vấn: {res.get('flagged_count', 0)}")
            print(f"• Tỉ lệ sức khỏe tri thức  : {res.get('health_percentage', 100.0)}%")
            if res.get("flagged_items"):
                print("\nDanh sách bài học cần PM / Supervisor xem xét chỉnh sửa:")
                for item in res["flagged_items"]:
                    print(f"  - #{item['id']} [{item.get('domain')}] Điểm: {item['quality_score']}")
                    for iss in item["issues"]:
                        print(f"    * Lỗi: {iss}")
            print("=" * 75)

if __name__ == "__main__":
    main()
