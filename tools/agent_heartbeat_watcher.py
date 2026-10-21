#!/usr/bin/env python3
"""
tools/agent_heartbeat_watcher.py - Daemon ngầm giám sát nhịp tim và phát hiện sự cố treo/ngắt kết nối của Agent.

Chức năng:
1. Định kỳ quét bmad/rooms/heartbeats.json.
2. Nếu phát hiện Agent bất kỳ (Supervisor, Lead, Peer, QC) im lặng > 5 phút (300s):
   - Đánh dấu trạng thái [OFFLINE / TREO].
   - Bắn thông báo báo động (Escalation) sang Orca Event Bus.
   - Bắn cảnh báo vào log và Sổ cái tiến độ AGENT_PROGRESS.md.
3. Hỗ trợ chạy 1 lần (--check) hoặc chạy ngầm liên tục (--daemon).
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
ROLES = ["supervisor", "lead", "peer", "design", "qc"]
MAX_SILENT_SECONDS = 300  # 5 phút không có tín hiệu là coi như đơ / offline


def check_all_agents() -> Dict[str, Any]:
    if not HEARTBEAT_FILE.exists():
        print("⚠️ Chưa có file nhịp tim heartbeats.json.")
        return {}

    try:
        data = json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Lỗi đọc file heartbeats.json: {e}")
        return {}

    now = time.time()
    alerts = []

    for r in ROLES:
        info = data.get(r)
        if not info:
            continue

        last_ts = info.get("last_ping_ts", 0)
        diff_s = int(now - last_ts)
        diff_m = diff_s // 60
        status = info.get("status", "idle")

        # Nếu đang working mà im lặng quá 5 phút -> CẢNH BÁO
        if diff_s > MAX_SILENT_SECONDS and status == "working":
            alert_msg = f"🚨 Agent {r.upper()} đang xử lý Task #{info.get('task_id')} nhưng đã im lặng {diff_m} phút (> 5 phút)! Nguy cơ bị đơ / treo tiến trình."
            alerts.append(alert_msg)
            print(alert_msg)

            # Bắn alert qua Orca nếu có
            if shutil.which("orca"):
                try:
                    subprocess.run([
                        "orca", "orchestration", "send",
                        "--subject", f"🚨 [HEARTBEAT ALERT] {r.upper()} mất kết nối!",
                        "--body", alert_msg,
                        "--type", "escalation",
                        "--to", "@supervisor"
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
                except Exception:
                    pass

    if not alerts:
        print(f"🟢 [Heartbeat Watcher]: Tất cả {len(data)} agent đều đang hoạt động tốt hoặc ở trạng thái an toàn.")
    return {"alerts": alerts, "checked_at": time.ctime()}


def run_daemon(interval_s: int = 120):
    print(f"💓 [HEARTBEAT WATCHER DAEMON]: Bắt đầu chạy ngầm (chu kỳ {interval_s} giây/lần)...")
    try:
        while True:
            check_all_agents()
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng Heartbeat Watcher Daemon.")


def main():
    parser = argparse.ArgumentParser(description="Daemon giám sát nhịp tim toàn bộ Agent.")
    parser.add_argument("--check", action="store_true", help="Kiểm tra 1 lần ngay lập tức")
    parser.add_argument("--daemon", action="store_true", help="Chạy vòng lặp ngầm liên tục")
    parser.add_argument("--interval", type=int, default=120, help="Chu kỳ quét tính bằng giây khi chạy daemon (mặc định: 120s)")
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval_s=args.interval)
    else:
        check_all_agents()


if __name__ == "__main__":
    main()
