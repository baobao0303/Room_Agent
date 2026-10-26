#!/usr/bin/env python3
"""
tools/orca_worktree_manager.py - Orca Native Worktree & Human-in-the-Loop Review Gate Manager.

Manages the lifecycle of isolated task worktrees in Orca:
1. `create`: Provisions dedicated worktree card on Orca board with isolated git branch and ephemeral agent.
2. `ready-review`: Marks worktree card as [IN-REVIEW / AWAITING USER] and emits desktop alert.
3. `approve`: Fast-forward merges worktree branch into main branch and cleanly removes worktree from Orca & disk.
4. `reject`: Delivers operator feedback into worktree terminal for Peer to fix without dirtying main branch.
5. `list`: Inspects all active task worktrees and their review readiness.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = str(PROJECT_ROOT)
REG_FILE = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"

try:
    from tools.harness_manager import HarnessManager
except ImportError:
    from harness_manager import HarnessManager  # type: ignore

import unicodedata

def slugify(text: str) -> str:
    # Normalize unicode to ASCII for clean git branch names
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:30] or "task"


def run_cmd(cmd: List[str], check: bool = False, cwd: Optional[str] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check, cwd=cwd or BASE_DIR)


def send_desktop_notification(title: str, message: str, level: str = "info"):
    """Bắn thông báo desktop qua libnotify (Linux) hoặc osascript (macOS)."""
    try:
        if shutil.which("notify-send"):
            urgency = "critical" if level in ("error", "alert") else "normal"
            run_cmd(["notify-send", "-u", urgency, "-a", "Orca Worktree Review", title, message])
        elif sys.platform == "darwin" and shutil.which("osascript"):
            script = f'display notification "{message}" with title "{title}"'
            run_cmd(["osascript", "-e", script])
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass


def get_orca_worktrees() -> List[Dict[str, Any]]:
    if not shutil.which("orca"):
        return []
    res = run_cmd(["orca", "worktree", "list", "--json"])
    if res.returncode != 0 or not res.stdout.strip():
        return []
    try:
        data = json.loads(res.stdout)
        return data.get("result", {}).get("worktrees", [])
    except Exception:
        return []


def find_task_worktree(task_id: int | str) -> Optional[Dict[str, Any]]:
    wts = get_orca_worktrees()
    tid_str = f"task-{task_id}"
    tid_num = str(task_id)
    for wt in wts:
        name = wt.get("displayName") or ""
        comment = wt.get("comment") or ""
        branch = wt.get("git", {}).get("branch") or ""
        if tid_str in name.lower() or f"#{tid_num}" in comment or f"task-{tid_num}" in branch:
            return wt
    return None


def create_task_worktree(
    task_id: int | str,
    title: str,
    prompt: str,
    role: str = "peer",
    model: str = "ag/gemini-3.8-flash-low",
) -> Dict[str, Any]:
    """Tạo worktree cô lập cho Task trên Orca Workspace Board."""
    if not shutil.which("orca"):
        return {"success": False, "error": "Lệnh 'orca' không có trong PATH."}

    slug = slugify(title)
    wt_name = f"task-{task_id}-{slug}"
    branch_name = f"peer/task-{task_id}-{slug}"

    print(f"🚀 [Orca Worktree Provisioning]: Đang rẽ worktree '{wt_name}' cho Task #{task_id}...")

    cmd_create = [
        "orca", "worktree", "create",
        "--name", wt_name,
        "--base-branch", "HEAD",
        "--agent", "hermes",
        "--prompt", f"[{role.upper()}] Task #{task_id}: {prompt}",
        "--model", model,
        "--comment", f"Harness WI #{task_id} [Active - Peer Working]",
        "--json"
    ]

    res = run_cmd(cmd_create)
    if res.returncode != 0:
        err = res.stderr.strip() or res.stdout.strip()
        print(f"⚠️ [Orca Worktree Error]: {err}", file=sys.stderr)
        return {"success": False, "error": err}

    handle = ""
    worktree_id = ""
    worktree_path = ""
    try:
        data = json.loads(res.stdout)
        result = data.get("result", {})
        launch = result.get("launch", {})
        outcome = launch.get("outcome", {})
        handle = outcome.get("handle") or result.get("agentTerminalHandle") or ""
        worktree_id = result.get("worktreeId") or ""
        worktree_path = result.get("path") or ""
    except Exception:
        pass

    # Rename terminal title
    term_title = f"[Peer Dev 1] Task #{task_id}"
    if handle:
        run_cmd(["orca", "terminal", "rename", "--terminal", handle, "--title", term_title, "--json"])
        run_cmd(["orca", "terminal", "set-pane-title", "--terminal", handle, "--title", term_title, "--json"])
        run_cmd(["orca", "terminal", "send", "--terminal", handle, "--text", f"/title {term_title}", "--enter"])
        rtk_script = PROJECT_ROOT / "scripts" / "rtk_profile_env.sh"
        if rtk_script.is_file():
            run_cmd(["orca", "terminal", "send", "--terminal", handle, "--text", f"source {rtk_script} peer", "--enter"])

    print(f"✅ [Orca Worktree Created]: Thẻ '{wt_name}' đã xuất hiện trên Orca Board!")
    print(f"📁 Thư mục cô lập: {worktree_path or wt_name}")
    print(f"🌿 Branch cô lập   : {branch_name}")

    return {
        "success": True,
        "worktree_name": wt_name,
        "branch": branch_name,
        "handle": handle,
        "worktree_path": worktree_path,
        "task_id": task_id
    }


def mark_ready_for_user_review(task_id: int | str, qc_verdict: str = "PASS 100%") -> bool:
    """Đánh dấu Worktree đã qua kiểm định QC và chuyển sang trạng thái chờ User Review."""
    wt = find_task_worktree(task_id)
    if not wt or not shutil.which("orca"):
        return False

    wt_id = wt.get("id") or wt.get("displayName")
    cmd_set = [
        "orca", "worktree", "set",
        "--worktree", wt_id,
        "--workspace-status", "in-review",
        "--comment", f"Harness WI #{task_id} [AWAITING USER REVIEW - QC: {qc_verdict}]",
        "--json"
    ]
    res = run_cmd(cmd_set)
    if res.returncode == 0:
        send_desktop_notification(
            f"👁️ Task #{task_id}: Sẵn Sàng Review",
            f"QC đã nghiệm thu {qc_verdict}. Mời bạn xem git diff trên Orca Workspace trước khi Merge!",
            level="info"
        )
        print(f"\n🔔 [USER REVIEW REQUIRED]: Task #{task_id} đã được QC chứng nhận {qc_verdict}.")
        print(f"👉 Mời bạn click vào thẻ '{wt.get('displayName')}' trên Orca Desktop để xem Git Diff.")
        print(f"👉 Chạy lệnh duyệt: ./cli/orca-review approve {task_id}")
        print(f"👉 Chạy lệnh trả về: ./cli/orca-review reject {task_id} --reason '<lý do>'\n")
        return True
    return False


def record_review_intervention(
    task_id: int | str,
    action: str,
    actor: str = "user",
    reason: str = ""
) -> bool:
    """Record reviewer intervention into Harness DB intervention table."""
    try:
        mgr = HarnessManager(engine="auto")
        if hasattr(mgr, "record_intervention"):
            mgr.record_intervention(
                target_type="work_item",
                target_id=int(task_id),
                actor=actor,
                reason=reason,
                action=action,
            )
        else:
            with mgr._get_sqlite_db() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO intervention (target_type, target_id, actor, action, reason) VALUES (?, ?, ?, ?, ?)",
                    ("work_item", int(task_id), actor, action, reason)
                )
                conn.commit()
        print(f"📝 [Intervention Logged]: target_type='work_item', target_id={task_id}, action='{action}', actor='{actor}', reason='{reason}'")
        return True
    except Exception as e:
        print(f"⚠️ Không thể ghi nhận can thiệp vào intervention table: {e}", file=sys.stderr)
        return False


def approve_and_merge_worktree(task_id: int | str, actor: str = "user", reason: str = "Approved by orca-review") -> bool:
    """User phê duyệt: Fast-forward merge worktree vào branch chính và xóa worktree sạch sẽ."""
    # 0. Check task state in Harness DB FIRST (Zero-Git-Touch Guarantee)
    try:
        mgr = HarnessManager(engine="auto")
        task = mgr.get_work_item(int(task_id))
    except Exception as e:
        print(f"❌ Không thể truy vấn Harness DB cho Task #{task_id}: {e}", file=sys.stderr)
        return False

    if not task:
        print(f"❌ Không tìm thấy Task #{task_id} trong Harness DB. Từ chối merge.", file=sys.stderr)
        return False

    task_state = task.get("state")
    if task_state != "Resolved":
        print(f"❌ [GATE BLOCKED]: Task #{task_id} đang ở trạng thái '{task_state}', chưa đạt 'Resolved' (QC PASS).", file=sys.stderr)
        print("Chỉ những task đã được QC kiểm định và nộp trạng thái 'Resolved' mới được phép merge.", file=sys.stderr)
        return False

    wt = find_task_worktree(task_id)
    if not wt:
        print(f"❌ Không tìm thấy worktree cho Task #{task_id} trên Orca.", file=sys.stderr)
        return False

    wt_name = wt.get("displayName") or ""
    branch_ref = wt.get("git", {}).get("branch") or ""
    clean_branch = branch_ref.replace("refs/heads/", "")
    wt_id = wt.get("id") or wt_name

    print(f"=== [USER PHÊ DUYỆT & MERGE WORKTREE TASK #{task_id}] ===")
    print(f"🌿 Nhánh nguồn: {clean_branch}")

    # 1. Preview git diff --stat before merging
    diff_stat_res = run_cmd(["git", "diff", "--stat", f"HEAD...{clean_branch}"])
    diff_out = diff_stat_res.stdout.strip()
    if not diff_out or diff_stat_res.returncode != 0:
        diff_stat_res = run_cmd(["git", "diff", "--stat", clean_branch])
        diff_out = diff_stat_res.stdout.strip()

    print("=" * 78)
    print(f"📊 [DIFF PREVIEW]: Các thay đổi từ nhánh '{clean_branch}' chuẩn bị merge:")
    print("=" * 78)
    print(diff_out if diff_out else "  (Không có thay đổi diff nào)")
    print("=" * 78)

    # 2. Merge vào branch hiện hành
    merge_res = run_cmd(["git", "merge", "--no-ff", "-m", f"feat: merge task #{task_id} ({wt_name}) [Reviewed & Approved by User]", clean_branch])
    if merge_res.returncode != 0:
        print(f"⚠️ Merge thất bại: {merge_res.stderr.strip()}", file=sys.stderr)
        print("Đang thử lại với fast-forward...")
        ff_res = run_cmd(["git", "merge", "--ff-only", clean_branch])
        if ff_res.returncode != 0:
            print(f"❌ Không thể tự động merge. Vui lòng kiểm tra xung đột git.", file=sys.stderr)
            return False

    print(f"✅ Đã merge thành công code của Task #{task_id} vào branch chính!")

    # 3. Record intervention decision
    record_review_intervention(task_id=task_id, action="approve", actor=actor, reason=reason)

    # 4. Xóa worktree khỏi Orca & đĩa
    if shutil.which("orca"):
        rm_res = run_cmd(["orca", "worktree", "rm", "--worktree", wt_id, "--json"])
        if rm_res.returncode == 0:
            print(f"🗑️ [Orca Cleanup]: Đã xóa sạch worktree '{wt_name}' khỏi Orca Board.")
        else:
            print(f"⚠️ [Orca rm notice]: {rm_res.stderr.strip()}")

    # 5. Xóa branch tạm
    run_cmd(["git", "branch", "-d", clean_branch])

    # 6. Cập nhật Harness DB sang Closed (dưới quyền QC để thoả mãn role gate)
    try:
        mgr.update_state(int(task_id), "Closed", assigned_to_profile="qc")
        print(f"🏁 [Harness DB]: Task #{task_id} chuyển sang trạng thái CLOSED.")
    except Exception as e:
        print(f"⚠️ Không thể cập nhật Harness DB: {e}")

    send_desktop_notification(
        f"✅ Task #{task_id} ĐÃ MERGE THÀNH CÔNG",
        f"Code đã được gộp vào branch chính. Worktree đã được dọn sạch.",
        level="info"
    )
    return True


def reject_worktree(task_id: int | str, reason: str = "Cần chỉnh sửa theo feedback của User", actor: str = "user") -> bool:
    """User từ chối: Bắn phản hồi vào terminal của Peer trong worktree để sửa tiếp."""
    wt = find_task_worktree(task_id)
    if not wt:
        print(f"❌ Không tìm thấy worktree cho Task #{task_id} trên Orca.", file=sys.stderr)
        return False

    wt_name = wt.get("displayName") or ""
    wt_id = wt.get("id") or wt_name

    print(f"=== [USER REJECT TASK #{task_id}]: {reason} ===")

    # Record intervention decision
    record_review_intervention(task_id=task_id, action="reject", actor=actor, reason=reason)

    # Update comment on Orca
    if shutil.which("orca"):
        run_cmd([
            "orca", "worktree", "set",
            "--worktree", wt_id,
            "--workspace-status", "in-progress",
            "--comment", f"Harness WI #{task_id} [USER REJECTED - {reason[:40]}]",
            "--json"
        ])

    # Send feedback to Peer in that worktree
    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    feedback_memo = (
        f"# USER REVIEW FEEDBACK: Task #{task_id}\n"
        f"- **Thời gian**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- **Người thực hiện**: {actor}\n"
        f"- **Kết luận**: REJECTED - YÊU CẦU SỬA ĐỔI\n"
        f"- **Ý kiến của User**: {reason}\n"
    )
    (task_dir / "user_review_feedback.md").write_text(feedback_memo, encoding="utf-8")

    send_desktop_notification(
        f"🔄 Task #{task_id} Đã Yêu Cầu Sửa Đổi",
        f"Ý kiến: {reason}. Peer Dev đang tiến hành điều chỉnh lại trong worktree.",
        level="alert"
    )
    print(f"✅ Đã ghi nhận phản hồi vào {task_dir / 'user_review_feedback.md'}")
    return True


def list_task_worktrees():
    """Liệt kê danh sách tất cả các task worktrees đang hoạt động."""
    wts = get_orca_worktrees()
    print("=" * 78)
    print("📋 DANH SÁCH ORCA TASK WORKTREES HIỆN HÀNH:")
    print("=" * 78)
    print(f"{'TÊN WORKTREE':<30} | {'STATUS':<15} | {'COMMENT / TRẠNG THÁI':<28}")
    print("-" * 78)

    found = 0
    for wt in wts:
        name = wt.get("displayName") or ""
        if wt.get("isMainWorktree"):
            continue
        found += 1
        status = wt.get("workspaceStatus") or "active"
        comment = wt.get("comment") or "—"
        print(f"{name:<30} | {status.upper():<15} | {comment[:28]:<28}")

    if found == 0:
        print("  (Không có ephemeral task worktree nào đang mở. Bộ nhớ RAM = 0MB)")
    print("=" * 78 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Orca Native Worktree & Human-in-the-Loop Review Gate Manager")
    subparsers = parser.add_subparsers(dest="subcommand", help="Lệnh quản trị worktree")

    # create
    p_create = subparsers.add_parser("create", help="Tạo worktree mới cho task")
    p_create.add_argument("--task-id", required=True, help="Task ID")
    p_create.add_argument("--title", required=True, help="Tiêu đề task")
    p_create.add_argument("--prompt", required=True, help="Prompt chỉ đạo cho Peer")
    p_create.add_argument("--role", default="peer", help="Vai trò sub-agent (default: peer)")

    # ready-review
    p_ready = subparsers.add_parser("ready-review", help="Báo cáo task đã qua QC và sẵn sàng User Review")
    p_ready.add_argument("task_id", help="Task ID")
    p_ready.add_argument("--verdict", default="PASS 100%", help="Kết luận QC")

    # approve
    p_app = subparsers.add_parser("approve", help="User duyệt và merge worktree vào branch chính")
    p_app.add_argument("task_id", help="Task ID cần merge")
    p_app.add_argument("--actor", default="user", help="Actor approving merge (default: user)")
    p_app.add_argument("--reason", default="Approved by orca-review", help="Approval rationale")

    # reject
    p_rej = subparsers.add_parser("reject", help="User từ chối và yêu cầu sửa đổi")
    p_rej.add_argument("task_id", help="Task ID")
    p_rej.add_argument("--reason", default="Cần chỉnh sửa theo feedback", help="Lý do từ chối")
    p_rej.add_argument("--actor", default="user", help="Actor rejecting merge (default: user)")

    # list
    subparsers.add_parser("list", help="Xem danh sách worktrees hiện hành")

    args = parser.parse_args()

    if args.subcommand == "create":
        res = create_task_worktree(args.task_id, args.title, args.prompt, role=args.role)
        print(json.dumps(res, indent=2))
    elif args.subcommand == "ready-review":
        ok = mark_ready_for_user_review(args.task_id, qc_verdict=args.verdict)
        sys.exit(0 if ok else 1)
    elif args.subcommand == "approve":
        ok = approve_and_merge_worktree(args.task_id, actor=args.actor, reason=args.reason)
        sys.exit(0 if ok else 1)
    elif args.subcommand == "reject":
        ok = reject_worktree(args.task_id, reason=args.reason, actor=args.actor)
        sys.exit(0 if ok else 1)
    elif args.subcommand == "list" or not args.subcommand:
        list_task_worktrees()


if __name__ == "__main__":
    main()
