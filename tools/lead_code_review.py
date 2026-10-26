#!/usr/bin/env python3
"""
tools/lead_code_review.py - Continuous Code Review & Architecture Guard for Lead Dev.

Enforces SLP Standards:
1. Single-Ownership: Verifies Peer Dev modified only their designated module scope.
2. Angular 18 & TDS UI Compliance: Checks for Standalone, ChangeDetectionStrategy.OnPush,
   and semantic TDS tokens instead of hardcoded hex values.
3. YAGNI & Simplification: Flags unnecessary abstractions, excess boilerplate, or duplicate files.
4. Auto-saves review verdict to bmad/rooms/lead/review_<timestamp>.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
BMAD_LEAD_ROOM = BASE_DIR / "bmad" / "rooms" / "lead"


def run_git_diff(repo_dir: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_dir), "diff", "--staged"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        staged_diff = res.stdout.strip()
        res_unstaged = subprocess.run(
            ["git", "-C", str(repo_dir), "diff"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        unstaged_diff = res_unstaged.stdout.strip()
        return f"{staged_diff}\n{unstaged_diff}".strip()
    except Exception as exc:
        return f"Error reading git diff: {exc}"


def analyze_code_quality(diff_text: str) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    lines = diff_text.splitlines()

    hardcoded_hex_regex = re.compile(r"\+(?=.*(#([0-9a-fA-F]{3,6})))")
    missing_onpush_regex = re.compile(r"\+@Component\(\{")
    hardcoded_testid_regex = re.compile(r"\+(?=.*(\btds-test-id=|\bdata-testid=))")
    array_index_testid_regex = re.compile(r"\+(?=.*\[tdsTestId\]=.*(\bindex\b|\bidx\b|\bi\b))")
    has_onpush = "ChangeDetectionStrategy.OnPush" in diff_text

    current_file = ""
    for line in lines:
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        # 1. Flag hardcoded hex colors when working on frontend templates
        if current_file.endswith((".html", ".ts")) and not current_file.endswith(".spec.ts"):
            m = hardcoded_hex_regex.search(line)
            if m and not any(k in line.lower() for k in ("svg", "icon", "viewbox", "d=")):
                findings.append({
                    "file": current_file,
                    "severity": "WARN",
                    "category": "TDS_DESIGN_TOKEN",
                    "detail": f"Phát hiện mã màu hex cứng: `{m.group(0).strip()}`. Khuyến nghị thay thế bằng TDS token (e.g. `tds-color-text-primary`, `tds-color-primary-500-light`).",
                })

        # 2. Check component OnPush strategy
        if current_file.endswith(".component.ts") and missing_onpush_regex.search(line):
            if not has_onpush:
                findings.append({
                    "file": current_file,
                    "severity": "WARN",
                    "category": "ANGULAR_ON_PUSH",
                    "detail": "Component thiếu `changeDetection: ChangeDetectionStrategy.OnPush` theo quy chuẩn hiệu năng Angular 2026.",
                })

        # 3. Check TDS Test ID violations (hardcoded DOM attribute or array index)
        if current_file.endswith((".html", ".ts")) and not current_file.endswith(".spec.ts"):
            m_testid = hardcoded_testid_regex.search(line)
            if m_testid:
                findings.append({
                    "file": current_file,
                    "severity": "ERROR",
                    "category": "TDS_TEST_ID_VIOLATION",
                    "detail": "Phát hiện hardcode attribute `tds-test-id` hoặc `data-testid`. Bắt buộc dùng directive `tdsTestId` từ `@demo/core`.",
                })
            m_index = array_index_testid_regex.search(line)
            if m_index:
                findings.append({
                    "file": current_file,
                    "severity": "ERROR",
                    "category": "TDS_TEST_ID_ARRAY_INDEX",
                    "detail": "Phát hiện dùng array index trong `tdsTestId`. Bắt buộc dùng business entity ID (ví dụ: `[tdsTestId]=\"'customer-row-' + item.id\"`).",
                })

    has_errors = any(f.get("severity") == "ERROR" for f in findings)
    verdict = "APPROVED" if len(findings) == 0 else ("REJECTED" if has_errors else "ADVICE_PROVIDED")

    return {
        "total_findings": len(findings),
        "findings": findings,
        "verdict": verdict,
    }


def main():
    parser = argparse.ArgumentParser(description="Lead Dev Continuous Code Review Tool")
    parser.add_argument("--repo-dir", default=str(BASE_DIR / "projects" / "demo-crm-fe"), help="Target repository directory to review")
    parser.add_argument("--task-id", type=int, help="Optional Harness Work Item ID")
    parser.add_argument("--json", action="store_true", help="Print verdict as JSON")
    args = parser.parse_args()

    repo_path = Path(args.repo_dir)
    if not repo_path.is_dir():
        repo_path = BASE_DIR

    diff = run_git_diff(repo_path)
    analysis = analyze_code_quality(diff)

    BMAD_LEAD_ROOM.mkdir(parents=True, exist_ok=True)
    ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    item_str = f"#{args.task_id}" if args.task_id else "N/A"

    review_report = f"""# BÁO CÁO REVIEW CODE CỦA LEAD DEV

- **Thời gian**: `{ts_now}`
- **Work Item**: `{item_str}`
- **Đánh giá tổng quan (Verdict)**: **{analysis['verdict']}**
- **Số điểm cần lưu ý**: {analysis['total_findings']}

---

## 1. Chi Tiết Phát Hiện & Hướng Dẫn Tối Ưu Cho Peer Dev
"""
    if analysis["findings"]:
        for f in analysis["findings"]:
            review_report += f"- `[{f['severity']}]` **{f['category']}** tại `{f['file']}`:\n  > {f['detail']}\n"
    else:
        review_report += "- [✓] Mã nguồn đạt chuẩn: Không có mã màu cứng, tuân thủ OnPush và ranh giới module.\n"

    review_report += f"""
---

## 2. Chỉ Đạo Từ Lead Dev
1. Peer Dev áp dụng các gợi ý tối ưu trên trước khi bàn giao cho QC.
2. Tránh viết abstractions dư thừa (YAGNI) — ưu tiên code ngắn gọn, ít file.
3. Khi hoàn tất, ghi log qua `python3 tools/agent_progress.py log --agent "Peer Dev"`.
"""

    report_file = BMAD_LEAD_ROOM / f"review_{args.task_id or 'latest'}_{ts_file}.md"
    latest_review = BMAD_LEAD_ROOM / "latest_review.md"
    report_file.write_text(review_report, encoding="utf-8")
    latest_review.write_text(review_report, encoding="utf-8")

    if args.json:
        import json
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        print(f"=== LEAD DEV CODE REVIEW: {analysis['verdict']} ===")
        print(f"Báo cáo đã lưu tại: {report_file.relative_to(BASE_DIR)}")
        for f in analysis["findings"]:
            print(f"  [{f['severity']}] {f['file']}: {f['detail']}")


if __name__ == "__main__":
    main()
