#!/usr/bin/env python3
"""
tools/agent_heartbeat.py - Bộ công cụ quản lý nhịp tim định kỳ (Heartbeat Engine) cho toàn bộ Agent SLPC.

Chức năng:
1. ping: Agent định kỳ báo cáo nhịp tim (Role, Trạng thái: idle/working/blocked, Task ID, Hành động).
2. status: Hiển thị bảng điều khiển nhịp tim của tất cả Agent (Supervisor, Lead, Peer, QC).
   - Đánh dấu 🟢 ONLINE nếu < 3 phút.
   - Đánh dấu 🟡 WARNING nếu 3-5 phút không phản hồi.
   - Đánh dấu 🔴 OFFLINE / DEAD nếu > 5 phút.
3. broadcast-ping: Quét toàn bộ terminal Orca đang mở và gửi yêu cầu ping nhịp tim đồng loạt.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HEARTBEAT_FILE = PROJECT_ROOT / "bmad" / "rooms" / "heartbeats.json"

ROLES = ["supervisor", "pm", "lead", "peer", "qc"]


def load_heartbeats() -> Dict[str, Any]:
    if HEARTBEAT_FILE.exists():
        try:
            return json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_heartbeats(data: Dict[str, Any]):
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_ping(role: str, status: str, task_id: str | None = None, activity: str | None = None):
    r = role.strip().lower()
    now_ts = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = load_heartbeats()
    old_info = data.get(r, {})
    last_ts = old_info.get("last_ping_ts", 0)

    # Chống spam heartbeat: Bỏ qua nếu chưa quá 25s VÀ trạng thái + task_id không đổi
    if (now_ts - last_ts < 25) and old_info.get("status") == status and str(old_info.get("task_id") or "") == str(task_id or ""):
        return

    data[r] = {
        "role": role,
        "status": status,
        "task_id": task_id or old_info.get("task_id"),
        "activity": activity or "Đang hoạt động bình thường",
        "last_ping_ts": now_ts,
        "last_ping_str": now_str,
    }
    save_heartbeats(data)
    print(f"💓 [HEARTBEAT PING]: {role.upper()} [{status.upper()}] lúc {now_str} (Task #{task_id or 'None'})")

    # Chỉ bắn sự kiện heartbeat sang Orca khi trạng thái hoặc task thay đổi (chống flood query liên tục)
    if shutil.which("orca") and (old_info.get("status") != status or str(old_info.get("task_id") or "") != str(task_id or "")):
        try:
            subprocess.run([
                "orca", "orchestration", "send",
                "--subject", f"[Heartbeat] {role.upper()} is {status.upper()}",
                "--body", f"Hành động: {activity or 'Bình thường'}. Task: #{task_id or 'None'}",
                "--type", "heartbeat",
                "--task-id", str(task_id or "")
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        except Exception:
            pass


def get_live_terminal_handles() -> Dict[str, str]:
    """Lấy danh sách terminal đang chạy live trong Orca từ registry."""
    if not shutil.which("orca"):
        return {}
    try:
        reg_file = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
        if not reg_file.exists():
            return {}
        reg_data = json.loads(reg_file.read_text(encoding="utf-8"))
        res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return {}
        terminals = json.loads(res.stdout).get("result", {}).get("terminals", [])
        live_handles = {t.get("handle") for t in terminals}
        return {r.lower(): meta["handle"] for r, meta in reg_data.items() if meta.get("handle") in live_handles}
    except Exception:
        return {}


def print_status():
    data = load_heartbeats()
    now = time.time()
    live_map = get_live_terminal_handles()

    print("\n=========================================================================")
    print("      SLPC MULTI-AGENT HEARTBEAT MONITOR (BẢNG THEO DÕI NHỊP TIM)")
    print("=========================================================================")
    print(f"{'ROLE':<15} | {'TRẠNG THÁI':<15} | {'LAST SEEN':<14} | {'TASK':<8} | {'HÀNH ĐỘNG ĐANG LÀM'}")
    print("-" * 73)

    for r in ROLES:
        info = data.get(r)
        is_live = r in live_map

        if not info and not is_live:
            print(f"{r.upper():<15} | ⚪ NO RECORD    | Chưa từng ping | N/A      | Chưa khởi tạo")
            continue

        last_ts = info.get("last_ping_ts", 0) if info else 0
        diff_s = int(now - last_ts)
        diff_m = diff_s // 60
        seen_str = f"{diff_s}s trước" if diff_s < 180 else f"{diff_m}m trước"

        if is_live:
            curr_status = info.get("status", "idle") if info else "idle"
            health_icon = "🟢 ONLINE "
            status_str = f"{health_icon} ({curr_status})"
        else:
            if diff_s < 180:
                health_icon = "🟡 WARNING"
                status_str = f"{health_icon} (detached)"
            else:
                health_icon = "🔴 OFFLINE"
                status_str = f"{health_icon} (dead)"

        task_str = f"#{info.get('task_id')}" if (info and info.get("task_id")) else "-"
        act = ((info.get("activity") if info else "Live terminal standby") or "")[:28]

        print(f"{r.upper():<15} | {status_str:<15} | {seen_str:<14} | {task_str:<8} | {act}")

    print("-------------------------------------------------------------------------")
    try:
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from tools.harness_learning_search import run_audit  # type: ignore
        audit_res = run_audit(prune_garbage=False)
        total_exp = audit_res.get("total_experiences", 0)
        health = audit_res.get("health_percentage", 100.0)
        flagged = audit_res.get("flagged_count", 0)
        h_icon = "🟢" if flagged == 0 else "🟡"
        print(f"📚 TRI THỨC TỰ HỌC: {total_exp} bài học | {h_icon} Sức khỏe: {health}% | Nghi vấn tào lao: {flagged}")
    except Exception:
        pass
    print("=========================================================================\n")


def broadcast_ping():
    """Gửi lệnh yêu cầu tất cả các terminal Agent đang mở ping heartbeat đồng loạt."""
    if not shutil.which("orca"):
        print("⚠️ Orca CLI không khả dụng.")
        return

    print("📢 [BROADCAST]: Gửi tín hiệu yêu cầu tất cả Agent báo cáo Heartbeat...")
    try:
        t_res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True)
        t_data = json.loads(t_res.stdout)
        terminals = t_data.get("result", {}).get("terminals", [])
        live_handles = {t.get("handle") for t in terminals}

        # Ưu tiên đọc mapping chuẩn từ agent_terminals.json
        reg_file = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
        reg_map = {}
        if reg_file.exists():
            try:
                reg_data = json.loads(reg_file.read_text(encoding="utf-8"))
                for r, meta in reg_data.items():
                    h = meta.get("handle")
                    if h and h in live_handles:
                        reg_map[h] = r.lower()
            except Exception:
                pass

        for t in terminals:
            h = t.get("handle")
            title = (t.get("title") or "").lower()
            role_found = reg_map.get(h)
            if not role_found:
                for r in ROLES:
                    if r in title:
                        role_found = r
                        break
            if role_found and role_found != "supervisor":
                cmd = f"python3 tools/agent_heartbeat.py ping --role {role_found} --status idle --activity 'Standby'"
                subprocess.run(["orca", "terminal", "send", "--terminal", h, "--text", cmd, "--enter"], capture_output=True)
                print(f"  ➔ Đã gửi yêu cầu ping tới terminal {role_found.upper()} ({h})")
    except Exception as e:
        print(f"⚠️ Lỗi broadcast: {e}")


def main():
    parser = argparse.ArgumentParser(description="Quản lý Heartbeat cho SLPC Agent.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    # ping
    p_ping = subparsers.add_parser("ping", help="Báo cáo nhịp tim định kỳ")
    p_ping.add_argument("--role", required=True, choices=ROLES, help="Tên role (supervisor, lead, peer, qc)")
    p_ping.add_argument("--status", default="working", choices=["idle", "working", "blocked"], help="Trạng thái hiện tại")
    p_ping.add_argument("--task-id", help="Work Item ID đang làm (nếu có)")
    p_ping.add_argument("--activity", help="Mô tả ngắn việc đang làm")

    # status
    subparsers.add_parser("status", help="Xem bảng tổng quan trạng thái nhịp tim của tất cả agent")

    # broadcast
    subparsers.add_parser("broadcast", help="Yêu cầu tất cả các agent terminal đang mở ping ngay")

    args = parser.parse_args()

    if args.action == "ping":
        record_ping(args.role, args.status, args.task_id, args.activity)
    elif args.action == "status":
        print_status()
    elif args.action == "broadcast":
        broadcast_ping()


if __name__ == "__main__":
    main()
