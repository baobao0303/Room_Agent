#!/usr/bin/env python3
"""
tools/agent_reprimand.py - Bộ công cụ kiểm soát kỷ luật, chất vấn & xử phạt vi phạm giữa các Agent (SLPC Agent Reprimand & Sanction Tool).

Mục đích:
- Trao quyền cho từng vai trò (Supervisor, Lead, Peer, QC, Sub-Agents) "chửi" / phê bình chính thức agent khác khi phát hiện vi phạm quy tắc.
- Bắt buộc phải có bằng chứng thực nghiệm (Evidence-based Blame).
- Ghi nhận biên bản vi phạm vào bmad/rooms/violations/, tự động giáng cấp trạng thái trên Harness DB và bắn thông báo cảnh cáo qua Orca.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from floci_client import FlociHarnessDB  # type: ignore
except ImportError:
    from tools.floci_client import FlociHarnessDB  # type: ignore

VIOLATIONS = {
    "hardcoded_hex": "Dùng mã màu hex cứng (#...) thay vì TDS Design Tokens",
    "broken_ownership": "Vi phạm Single-Ownership: Sửa chéo sang file/module khác",
    "dead_code": "Để lại import rác, ViewChild mồ côi hoặc code thừa sau refactor",
    "untested_code": "Nộp code ẩu (Resolved) khi chưa test hoặc test suite thất bại",
    "flawed_architecture": "Thiết kế kiến trúc lỗi thời, gây build panic hoặc crash thực tế",
    "vague_specs": "Giao đề bài mơ hồ, thiếu Acceptance Criteria (BDD) hoặc thiếu Anchor",
    "scope_creep": "Tự ý làm thêm tính năng ngoài phạm vi Epic/Task được giao",
    "premature_close": "Tự tiện đóng Task khi chưa có xác nhận nghiệm thu 100% từ QC",
    "context_pollution": "Ghi đè file handoff hoặc nạp bừa context của task khác",
    "role_trespass": "Vi phạm rào cản thẩm quyền: Quản lý tự ý sửa code production, hoặc Dev tự ý quản lý/đóng Task",
}

VALID_CALLERS = {
    "supervisor": ["lead", "qc"],
    "lead": ["peer", "supervisor"],
    "peer": ["lead", "qc"],
    "qc": ["peer", "lead"],
    "gemini-codebase-analyzer": ["peer", "lead"],
    "strategic-reasoning-architect": ["peer", "lead"],
    "slpc-qc-verifier": ["peer", "lead"],
}


def sanitize_role(role: str) -> str:
    r = role.strip().lower()
    for valid in VALID_CALLERS:
        if valid in r:
            return valid
    return r


def main():
    parser = argparse.ArgumentParser(description="SLPC Agent Reprimand & Violation Callout Tool.")
    parser.add_argument("--from-role", required=True, help="Role phát hiện và khiển trách (Supervisor, Lead, Peer, QC, sub-agent...)")
    parser.add_argument("--to-role", required=True, help="Role vi phạm bị khiển trách (Lead, Peer, QC, Supervisor)")
    parser.add_argument("--violation", required=True, choices=list(VIOLATIONS.keys()), help="Loại lỗi vi phạm quy tắc")
    parser.add_argument("--evidence", required=True, help="Bằng chứng thực nghiệm (log lỗi, git diff, mã file, tên class)")
    parser.add_argument("--message", required=True, help="Nội dung phê bình chi tiết, đanh thép")
    parser.add_argument("--task-id", help="Harness Work Item ID liên quan (nếu có)")
    parser.add_argument("--penalize", action="store_true", help="Tự động giáng cấp task trên Harness DB (Active -> Blocked hoặc Resolved -> Active)")
    args = parser.parse_args()

    caller = sanitize_role(args.from_role)
    target = sanitize_role(args.to_role)

    # 1. Kiểm tra thẩm quyền
    allowed_targets = VALID_CALLERS.get(caller, [])
    if target not in allowed_targets:
        print(f"⚠️ Cảnh báo: Role '{args.from_role}' thường không trực tiếp xử phạt '{args.to_role}'.", file=sys.stderr)

    violation_title = VIOLATIONS[args.violation]
    now = datetime.now()
    ts_now = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_file = now.strftime("%Y%m%d_%H%M%S")
    tid_str = f"#{args.task_id}" if args.task_id else "N/A"

    # 2. Tạo Biên Bản Khiển Trách / Phê Bình Chính Thức
    violations_dir = PROJECT_ROOT / "bmad" / "rooms" / "violations"
    violations_dir.mkdir(parents=True, exist_ok=True)
    violation_file = violations_dir / f"reprimand_{args.task_id or 'general'}_{caller}_to_{target}_{ts_file}.md"

    memo_content = f"""# BIÊN BẢN KHIỂN TRÁCH & XỬ PHẠT QUY TẮC SLPC (AGENT SANCTION MEMO)

- **Thời gian**: `{ts_now}`
- **Work Item liên quan**: `{tid_str}`
- **Agent khiển trách (From)**: `{args.from_role}`
- **Agent vi phạm (Target)**: `{args.to_role}`
- **Hành vi vi phạm**: **[{args.violation.upper()}] {violation_title}**

---

## 1. NỘI DUNG PHÊ BÌNH & CẢNH CÁO (REPRIMAND MESSAGE)
> "{args.message}"

---

## 2. BẰNG CHỨNG THỰC NGHIỆM KHÁCH QUAN (EMPIRICAL EVIDENCE)
```text
{args.evidence}
```

---

## 3. CHỈ THỊ KHẮC PHỤC BẮT BUỘC (CORRECTIVE ACTION MANDATE)
- Agent `{args.to_role}` phải lập tức khắc phục lỗi trên, xóa sạch code vi phạm và tự kiểm thử lại.
- Tuyệt đối không được chuyển trạng thái Task sang bước kế tiếp khi lỗi chưa được giải quyết dứt điểm.
"""
    violation_file.write_text(memo_content, encoding="utf-8")
    print(f"🚨 [BIÊN BẢN XỬ PHẠT ĐÃ KÝ THÁC]: {violation_file.relative_to(PROJECT_ROOT)}")

    # Ghi vào task namespace nếu có
    if args.task_id:
        task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(args.task_id)
        if task_dir.exists():
            (task_dir / "latest_violation.md").write_text(memo_content, encoding="utf-8")

    # 3. TỰ ĐỘNG TẠO TICKET DẠNG 'Bug' TRÊN HARNESS DB KHI REVIEW PHÁT HIỆN LỖI
    bug_id = None
    if args.task_id:
        try:
            from harness_manager import HarnessManager  # type: ignore
            mgr = HarnessManager()
            numeric_id = int("".join(filter(str.isdigit, str(args.task_id))))
            bug_title = f"[Review]: Phat hien {args.violation} when reviewed by {args.from_role}"
            bug_desc = f"{args.message}\n\nEvidence:\n{args.evidence}"
            bug_res = mgr.add_work_item(
                wi_type="Bug",
                title=bug_title,
                description=bug_desc,
                parent_id=numeric_id,
                assigned_to_profile=target,
                source="bot",
                created_by_profile=caller,
                priority="P1"
            )
            bug_id = bug_res.get("id")
            print(f"🐛 [Harness Bug Created]: Đã tự động tạo Bug ticket #{bug_id}: '{bug_title}' gán cho {target.upper()}!")
        except Exception as e:
            print(f"⚠️ Không thể tạo Bug ticket trên Harness: {e}", file=sys.stderr)

    # 4. Giáng cấp trạng thái trên Harness DB nếu có cờ --penalize
    if args.task_id and args.penalize:
        try:
            db = FlociHarnessDB()
            numeric_id = int("".join(filter(str.isdigit, str(args.task_id))))
            item = db.get_work_item(numeric_id)
            if item:
                curr_state = item.get("state")
                new_state = curr_state
                # Resolved mà bị chửi -> Trả về Active (Dev phải làm lại)
                if curr_state == "Resolved":
                    new_state = "Active"
                elif curr_state == "Active":
                    new_state = "Blocked"

                if new_state and new_state != curr_state:
                    db.update_work_item_state(numeric_id, str(new_state))
                    print(f"📉 [Harness DB Penalized]: Task #{args.task_id} bị giáng cấp từ [{curr_state}] ➔ [{new_state}] do vi phạm {args.violation}!")
        except Exception as e:
            print(f"⚠️ Không thể cập nhật Harness DB: {e}", file=sys.stderr)

    # 5. Gửi thông điệp cảnh cáo trực tiếp qua Orca Event Bus nếu có
    if shutil.which("orca"):
        try:
            subprocess.run([
                "orca", "orchestration", "send",
                "--subject", f"🚨 [REPRIMAND] {args.from_role} cảnh cáo {args.to_role}: {violation_title}",
                "--body", f"{args.message}\nBằng chứng: {args.evidence}",
                "--type", "escalation",
                "--to", f"@{target}"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            print(f"📢 [Orca Broadcast]: Đã bắn thông điệp cảnh cáo trực tiếp tới @{target}.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
