#!/usr/bin/env python3
"""
tools/orca_harness_bridge.py - Cầu nối đồng bộ Harness DB (Floci DynamoDB) và Orca Workspace Board.

Chức năng:
1. Đồng bộ trạng thái 1:1 từ Harness DB sang cột Kanban Orca:
   - New      <-> todo
   - Active   <-> in-progress
   - Resolved <-> in-review
   - Closed   <-> completed
2. Đẩy Sub-agent lên Workspace Board:
   - Cách 1: Đẩy agent mới vào card active (orca agent launch).
   - Cách 2: Tạo hierarchical sub-agent có task cha-con (orca orchestration worker-start --parent).
3. Đóng gói context vào bmad/rooms/tasks/<task_id>/ để chống loạn context.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from floci_client import FlociHarnessDB  # type: ignore
except ImportError:
    from tools.floci_client import FlociHarnessDB  # type: ignore

STATE_MAP = {
    "New": "todo",
    "Active": "in-progress",
    "Resolved": "in-review",
    "Closed": "completed",
    "Blocked": "in-progress",
    "Removed": "removed",
}


def sync_state_to_orca(task_id: str, state: str, worktree: str = "active"):
    if not shutil.which("orca"):
        print("⚠️ Orca CLI không khả dụng trên môi trường này.")
        return

    # Xử lý trường hợp đặc biệt: Removed
    if state == "Removed":
        print(f"🗑️ [Orca Board Sync]: Xử lý gỡ bỏ Task #{task_id} (State: Removed)...")
        # 1. Nếu là worktree độc lập (không phải main/active), gỡ sạch khỏi board
        if worktree not in ("active", "main", "primary"):
            cmd_rm = ["orca", "worktree", "rm", "--worktree", worktree, "--force", "--json"]
            try:
                subprocess.run(cmd_rm, capture_output=True, text=True, check=True)
                print(f"✅ Đã gỡ bỏ hoàn toàn thẻ Worktree '{worktree}' khỏi Orca Board.")
            except Exception as e:
                print(f"⚠️ Không thể gỡ worktree: {e}", file=sys.stderr)
        else:
            # Nếu trên workspace main/active, cập nhật comment và chuyển sang completed hoặc lưu archive
            cmd_set = [
                "orca", "worktree", "set",
                "--worktree", worktree,
                "--comment", f"Harness WI #{task_id} [REMOVED - TASK CANCELLED]",
                "--json"
            ]
            try:
                subprocess.run(cmd_set, capture_output=True, text=True)
                print(f"✅ Đã đánh dấu REMOVED cho Task #{task_id} trên Workspace '{worktree}'.")
            except Exception:
                pass

        # 2. Lưu trữ an toàn thư mục task vào archive/task_<id>_removed/
        task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
        if task_dir.exists():
            archive_target = PROJECT_ROOT / "bmad" / "rooms" / "archive" / f"task_{task_id}_removed"
            archive_target.parent.mkdir(parents=True, exist_ok=True)
            if archive_target.exists():
                shutil.rmtree(archive_target)
            shutil.move(str(task_dir), str(archive_target))
            print(f"📦 Đã di chuyển context Task #{task_id} vào {archive_target.relative_to(PROJECT_ROOT)}.")
        return

    orca_status = STATE_MAP.get(state, "in-progress")
    cmd = [
        "orca", "worktree", "set",
        "--worktree", worktree,
        "--workspace-status", orca_status,
        "--comment", f"Harness WI #{task_id} [{state}]",
        "--json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ [Orca Board Sync]: Đã cập nhật Workspace '{worktree}' ➔ Cột [{orca_status.upper()}] (Harness #{task_id}: {state})")
    except subprocess.CalledProcessError as e:
        if worktree == "active":
            try:
                cmd[4] = "name:main"
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✅ [Orca Board Sync]: Đã cập nhật Workspace 'name:main' ➔ Cột [{orca_status.upper()}] (Harness #{task_id}: {state})")
                return
            except Exception:
                pass
        print(f"❌ [Orca Board Sync Lỗi]: {e.stderr or e.stdout}", file=sys.stderr)


def launch_agent_on_board(agent_id: str, prompt: str, task_id: str | None = None, worktree: str = "active"):
    if not shutil.which("orca"):
        print("⚠️ Orca CLI không khả dụng.")
        return

    prefix = f"[WI-#{task_id}] " if task_id else ""
    full_prompt = f"{prefix}{prompt}"

    cmd = [
        "orca", "agent", "launch",
        "--worktree", worktree,
        "--agent", agent_id,
        "--prompt", full_prompt,
        "--json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"🚀 [Orca Agent Launch]: Đã spawn agent '{agent_id}' lên Workspace '{worktree}'.")
        print(f"   Task: {full_prompt}")
    except subprocess.CalledProcessError as e:
        print(f"❌ [Orca Launch Lỗi]: {e.stderr or e.stdout}", file=sys.stderr)


def spawn_hierarchical_subagent(parent_task_id: str, agent_id: str, title: str, spec: str):
    if not shutil.which("orca"):
        print("⚠️ Orca CLI không khả dụng.")
        return

    cmd = [
        "orca", "orchestration", "worker-start",
        "--parent", parent_task_id,
        "--agent", agent_id,
        "--task-title", title,
        "--spec", spec,
        "--json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"🌳 [Orca Sub-Agent Spawn]: Đã tạo sub-agent '{agent_id}' trực thuộc Task cha #{parent_task_id}.")
        print(f"   Sub-task: {title}")
    except subprocess.CalledProcessError as e:
        print(f"❌ [Orca Sub-Agent Lỗi]: {e.stderr or e.stdout}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Bridge đồng bộ Harness DB và Orca Workspace Board.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    # Subcommand: sync-status
    p_sync = subparsers.add_parser("sync-status", help="Đồng bộ trạng thái từ Harness DB sang Orca Board")
    p_sync.add_argument("--task-id", required=True, help="Harness Work Item ID (VD: 3623)")
    p_sync.add_argument("--state", choices=["New", "Active", "Resolved", "Closed", "Blocked", "Removed"], help="Trạng thái Harness (nếu không truyền sẽ tự query DB)")
    p_sync.add_argument("--worktree", default="active", help="Worktree selector (mặc định: active)")

    # Subcommand: launch-agent
    p_launch = subparsers.add_parser("launch-agent", help="Đẩy một agent lên danh sách Workspace Board")
    p_launch.add_argument("--agent", default="hermes", help="Agent runtime (hermes, codex, claude, antigravity)")
    p_launch.add_argument("--prompt", required=True, help="Nhiệm vụ cho agent")
    p_launch.add_argument("--task-id", help="Harness Work Item ID liên kết")
    p_launch.add_argument("--worktree", default="active", help="Worktree selector")

    # Subcommand: spawn-subagent
    p_sub = subparsers.add_parser("spawn-subagent", help="Tạo sub-agent phân cấp cha - con trong Orca Orchestration")
    p_sub.add_argument("--parent", required=True, help="ID task cha của Lead")
    p_sub.add_argument("--agent", default="hermes", help="Agent runtime (mặc định: hermes)")
    p_sub.add_argument("--title", required=True, help="Tiêu đề subtask")
    p_sub.add_argument("--spec", required=True, help="Đặc tả yêu cầu chi tiết cho sub-agent")

    args = parser.parse_args()

    if args.action == "sync-status":
        state = args.state
        if not state:
            db = FlociHarnessDB()
            numeric_id = int("".join(filter(str.isdigit, str(args.task_id))))
            item = db.get_work_item(numeric_id)
            if not item:
                print(f"❌ Không tìm thấy Task #{args.task_id} trên Harness DB.")
                sys.exit(1)
            state = item.get("state", "New")
        sync_state_to_orca(args.task_id, state, args.worktree)

    elif args.action == "launch-agent":
        launch_agent_on_board(args.agent, args.prompt, args.task_id, args.worktree)

    elif args.action == "spawn-subagent":
        spawn_hierarchical_subagent(args.parent, args.agent, args.title, args.spec)


if __name__ == "__main__":
    main()
