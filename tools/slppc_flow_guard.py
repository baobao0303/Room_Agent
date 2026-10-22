#!/usr/bin/env python3
"""
tools/slppc_flow_guard.py - Bộ Canh Gác Tuân Thủ Quy Trình Điều Hành SLPPC & Tự Động Lập Biên Bản Vi Phạm (SLPPC Flow Guard & Automated Violation Auditor).

Mô hình SLPPC (Supervisor - PM - Lead - Peer - QC):
Kiểm tra tự động và lập biên bản phạt khi:
1. Lead Dev tự ý gõ code (role_trespass) thay vì bóc tách Zero-Search task giao cho Peers.
2. Supervisor tự ý code tính năng hoặc duyệt task mơ hồ.
3. Bỏ qua cổng thẩm định Khả thi & Phù hợp của PM Agent (pm_bypass).
4. Peer tự tiện đóng task (premature_close) không qua nghiệm thu độc lập của QC.
5. Giao task 1 dòng cẩu thả vi phạm Zero-Search Mandate (vague_specs).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIOLATIONS_DIR = PROJECT_ROOT / "bmad" / "rooms" / "violations"
VIOLATIONS_DIR.mkdir(parents=True, exist_ok=True)

# 4 Tiêu chuẩn bắt buộc của Zero-Search Task Specification
ZERO_SEARCH_MANDATORY_SECTIONS = [
    "target file",
    "anchor",
    "concrete change",
    "acceptance criteria",
]


def record_violation_minute(
    from_role: str,
    to_role: str,
    violation_type: str,
    task_id: Optional[str | int],
    evidence: str,
    message: str,
) -> Path:
    """Tạo biên bản vi phạm chính thức lưu vĩnh viễn trong bmad/rooms/violations/ (tránh ghi trùng lặp)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tid_str = f"{task_id}" if task_id else "general"

    # Tránh tạo file trùng lặp nếu đã có biên bản cho vi phạm này
    existing = list(VIOLATIONS_DIR.glob(f"violation_{tid_str}_{from_role.lower()}_to_{to_role.lower()}_*.md"))
    if existing:
        return existing[0]

    filename = f"violation_{tid_str}_{from_role.lower()}_to_{to_role.lower()}_{ts}.md"
    file_path = VIOLATIONS_DIR / filename

    content = f"""# BIÊN BẢN VI PHẠM KỶ LUẬT ĐIỀU HÀNH SLPPC
**Mã Biên Bản**: `VIO-{ts}-{to_role.upper()}`  
**Thời gian lập**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  
**Người lập biên bản (From)**: `{from_role.upper()}`  
**Đối tượng vi phạm (To)**: `{to_role.upper()}`  
**Loại sai phạm**: `{violation_type}`  
**Work Item ID liên quan**: `#{task_id or 'N/A'}`  

---

## 1. Hành Vi Sai Phạm (Violation Details)
> **Mô tả hành vi**: {message}

## 2. Bằng Chứng Thực Nghiệm (Empirical Evidence)
```text
{evidence.strip()}
```

## 3. Rào Cản Thẩm Quyền Bị Phá Vỡ (Broken Invariant)
- **Quy chế SLPPC**: Phân định rạch ròi 5 vai trò (Supervisor - PM - Lead - Peer - QC).
- **Nguyên tắc vi phạm**: Quản lý cấm ôm code; Dev cấm tự duyệt/đóng task; Giao task cấm mơ hồ; Cấm bypass cổng PM.

## 4. Chế Tài Xử Phạt (Penalties & Next Actions)
1. Giáng cấp trạng thái công việc về `Active` hoặc `Blocked`.
2. Đối tượng `{to_role.upper()}` bắt buộc chấn chỉnh quy trình và khắc phục sai phạm.
3. Ghi nhận vi phạm vào Sổ cái Kỷ luật của phòng ban SLPPC.
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def check_zero_search_compliance(description: str) -> Tuple[bool, List[str]]:
    """Kiểm tra mô tả task có đủ các trường Zero-Search bắt buộc hay không."""
    lower = description.lower()
    missing = []
    for sec in ZERO_SEARCH_MANDATORY_SECTIONS:
        if sec not in lower:
            missing.append(sec)
    return len(missing) == 0, missing


def audit_lead_role_trespass() -> List[Dict[str, Any]]:
    """
    Kiểm tra xem Lead Dev có vi phạm role_trespass:
    Tự ý sửa mã nguồn production thay vì phân rã giao cho Peer.
    """
    violations = []
    bmad_rooms = PROJECT_ROOT / "bmad" / "rooms" / "lead"
    if not bmad_rooms.is_dir():
        return violations

    now = time.time()
    for memo_file in bmad_rooms.glob("handoff_*.md"):
        try:
            # Chỉ quét các biên bản gần nhất trong vòng 2 giờ
            if (now - memo_file.stat().st_mtime) > 7200:
                continue
            content = memo_file.read_text(encoding="utf-8")
            lower = content.lower()
            if ("modified files" in lower or "đã sửa" in lower) and "peer" not in lower:
                if "crates/harness-cli/src" in content or "apps/app-shell/src" in content or "projects/wicx-crm-fe" in content:
                    tid_match = re.search(r"#(\d+)", content)
                    violations.append({
                        "file": str(memo_file.relative_to(PROJECT_ROOT)),
                        "evidence": "Lead Dev ghi nhận trực tiếp sửa mã nguồn sản phẩm thay vì giao cho Peer",
                        "task_id": tid_match.group(1) if tid_match else None,
                    })
        except Exception:
            pass

    return violations


def audit_pm_bypass() -> List[Dict[str, Any]]:
    """
    Kiểm tra xem có bỏ qua cổng PM (pm_bypass):
    Tạo hoặc kích hoạt Epic mà chưa có Intake Memo từ PM Agent.
    """
    violations = []
    supervisor_dir = PROJECT_ROOT / "bmad" / "rooms" / "supervisor"
    pm_dir = PROJECT_ROOT / "bmad" / "rooms" / "pm"

    if not supervisor_dir.is_dir():
        return violations

    now = time.time()
    for handoff in supervisor_dir.glob("handoff_*.md"):
        try:
            # Chỉ quét các biên bản gần nhất trong vòng 2 giờ
            if (now - handoff.stat().st_mtime) > 7200:
                continue
            now = time.time()
            if (now - handoff.stat().st_mtime) > 7200:
                continue
            content = handoff.read_text(encoding="utf-8")
            epic_match = re.search(r"Epic\s*#(\d+)", content, re.IGNORECASE)
            if epic_match:
                epic_id = epic_match.group(1)
                # Bỏ qua các Epic lịch sử trước khi áp dụng chuẩn SLPPC (ID < 4116)
                if int(epic_id) < 4116:
                    continue
                has_pm_memo = False
                if pm_dir.is_dir():
                    for pm_memo in pm_dir.glob("*.md"):
                        if epic_id in pm_memo.name or f"#{epic_id}" in pm_memo.read_text(encoding="utf-8"):
                            has_pm_memo = True
                            break
                if not has_pm_memo:
                    violations.append({
                        "file": str(handoff.relative_to(PROJECT_ROOT)),
                        "evidence": f"Epic #{epic_id} được khởi tạo/giao việc mà chưa qua cổng thẩm định Feasibility/Alignment của PM Agent",
                        "task_id": epic_id,
                    })
        except Exception:
            pass

    return violations


def audit_premature_close() -> List[Dict[str, Any]]:
    """
    Kiểm tra xem Dev/Peer có tự ý đóng task (premature_close):
    Peer chỉ được phép chuyển trạng thái sang Resolved; cấm tự chuyển sang Closed.
    """
    violations = []
    peer_dir = PROJECT_ROOT / "bmad" / "rooms" / "peer"
    if not peer_dir.is_dir():
        return violations

    now = time.time()
    for memo in peer_dir.glob("handoff_*.md"):
        try:
            # Chỉ quét các biên bản gần nhất trong vòng 2 giờ
            if (now - memo.stat().st_mtime) > 7200:
                continue
            content = memo.read_text(encoding="utf-8")
            lower = content.lower()
            if "trạng thái: closed" in lower or "state: closed" in lower or "đã đóng task" in lower or "chuyển sang closed" in lower:
                tid_match = re.search(r"#(\d+)", content)
                violations.append({
                    "file": str(memo.relative_to(PROJECT_ROOT)),
                    "evidence": "Peer Dev tự ý tuyên bố hoặc cập nhật trạng thái Task sang Closed thay vì nộp Resolved cho QC",
                    "task_id": tid_match.group(1) if tid_match else None,
                })
        except Exception:
            pass

    return violations


def audit_vague_specs() -> List[Dict[str, Any]]:
    """
    Kiểm tra xem có vi phạm giao task cẩu thả / mơ hồ (vague_specs):
    Task giao cho Peer thiếu các mục định danh Zero-Search.
    """
    violations = []
    tasks_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks"
    if not tasks_dir.is_dir():
        return violations

    for task_folder in tasks_dir.iterdir():
        if not task_folder.is_dir():
            continue
        task_id = task_folder.name
        for memo in task_folder.glob("handoff_*.md"):
            try:
                content = memo.read_text(encoding="utf-8")
                if "supervisor" in memo.name or "lead" in memo.name:
                    is_compliant, missing = check_zero_search_compliance(content)
                    if not is_compliant and len(content.strip()) < 200:
                        violations.append({
                            "file": str(memo.relative_to(PROJECT_ROOT)),
                            "evidence": f"Mô tả task #{task_id} thiếu các mục Zero-Search bắt buộc: {', '.join(missing)}",
                            "task_id": task_id,
                        })
            except Exception:
                pass

    return violations


def run_slppc_audit(auto_record: bool = True) -> Dict[str, Any]:
    """Chạy toàn bộ các chốt chặn kiểm tra quy trình SLPPC."""
    results = {
        "status": "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "violations_detected": 0,
        "violations_list": [],
        "minutes_created": [],
    }

    # 1. Kiểm tra Lead Role Trespass
    lead_trespasses = audit_lead_role_trespass()
    for v in lead_trespasses:
        results["violations_detected"] += 1
        v_info = {
            "from": "Supervisor",
            "to": "Lead",
            "type": "role_trespass",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Lead Dev tự ý code sản phẩm thay vì phân rã Zero-Search Task cho Peer Devs.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="Supervisor",
                to_role="Lead",
                violation_type="role_trespass",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 2. Kiểm tra PM Bypass
    pm_bypasses = audit_pm_bypass()
    for v in pm_bypasses:
        results["violations_detected"] += 1
        v_info = {
            "from": "PM",
            "to": "Supervisor",
            "type": "pm_bypass",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Bỏ qua cổng thẩm định Khả thi & Phù hợp của PM Agent trước khi tạo/kích hoạt Epic.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="PM",
                to_role="Supervisor",
                violation_type="pm_bypass",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 3. Kiểm tra Premature Close
    premature_closes = audit_premature_close()
    for v in premature_closes:
        results["violations_detected"] += 1
        v_info = {
            "from": "QC",
            "to": "Peer",
            "type": "premature_close",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Peer tự ý đóng task thay vì nộp trạng thái Resolved để QC nghiệm thu độc lập.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="QC",
                to_role="Peer",
                violation_type="premature_close",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 4. Kiểm tra Vague Specs
    vague_specs = audit_vague_specs()
    for v in vague_specs:
        results["violations_detected"] += 1
        v_info = {
            "from": "Peer",
            "to": "Lead",
            "type": "vague_specs",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Giao task vi phạm quy chuẩn Zero-Search Mandate (thiếu các trường bắt buộc).",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="Peer",
                to_role="Lead",
                violation_type="vague_specs",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    if results["violations_detected"] > 0:
        results["status"] = "violations_found"

    return results


def main():
    parser = argparse.ArgumentParser(description="SLPPC Flow Guard & Violation Auditor")
    parser.add_argument("command", nargs="?", default="audit", help="Action to run (default: audit)")
    parser.add_argument("--record", action="store_true", default=True, help="Tự động ghi biên bản vi phạm vào bmad/rooms/violations/")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả JSON")
    args = parser.parse_args()

    res = run_slppc_audit(auto_record=args.record)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    print("=" * 75)
    print("🛡️ SLPPC FLOW GUARD & GOVERNANCE AUDITOR")
    print("=" * 75)
    print(f"• Thời gian quét     : {res['timestamp']}")
    print(f"• Vi phạm phát hiện  : {res['violations_detected']}")
    if res['minutes_created']:
        print(f"• Biên bản đã lập    : {len(res['minutes_created'])}")
        for m in res['minutes_created']:
            print(f"  ➔ {m}")

    if res['violations_detected'] == 0:
        print("✅ PASS: 100% tuân thủ mô hình SLPPC. Không có vi phạm quyền hạn hay quy trình.")
    else:
        print("⚠️ CẢNH BÁO: Đã phát hiện vi phạm rào cản thẩm quyền điều hành.")
    print("=" * 75)


if __name__ == "__main__":
    main()
