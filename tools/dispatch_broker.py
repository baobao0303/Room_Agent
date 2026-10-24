#!/usr/bin/env python3
"""
tools/dispatch_broker.py - Push-Driven Dispatch Broker & Event Bus.
Dispatches work packets directly to target agent PTY terminals or queues without polling.
Adapted from gawkbot's push-driven broker architecture with zero external dependencies.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TERMINALS_JSON_PATH = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
ROOM_LEDGER_PATH = PROJECT_ROOT / "bmad" / "rooms" / "room_ledger.json"
ROOMS_ROOT = PROJECT_ROOT / "bmad" / "rooms"


def get_terminal_handle(role: str) -> str | None:
    """Look up active terminal handle for a role in agent_terminals.json."""
    if not TERMINALS_JSON_PATH.is_file():
        return None
    try:
        data = json.loads(TERMINALS_JSON_PATH.read_text(encoding="utf-8"))
        entry = data.get(role.lower())
        if isinstance(entry, dict):
            return entry.get("handle")
    except Exception:
        pass
    return None


def construct_work_packet(
    target_role: str,
    action: str,
    task_id: int | None = None,
    payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build a rich, self-contained work packet for fresh turn execution."""
    return {
        "event_id": f"evt_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:21]}",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target_role": target_role.lower(),
        "task_id": task_id,
        "action": action,
        "payload": payload or {},
        "handshake_version": "1.0"
    }


def send_to_terminal(handle: str, message: str) -> bool:
    """Attempt to push command directly into Orca terminal stdin if orca CLI exists."""
    orca_bin = shutil.which("orca") or str(Path.home() / ".config" / "orca" / "linux-orca-cli-shim")
    if Path(orca_bin).is_file() or shutil.which("orca"):
        try:
            res = subprocess.run(
                [orca_bin, "terminal", "send", handle, f"{message}\n"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return res.returncode == 0
        except Exception:
            return False
    return False


def queue_work_packet(target_role: str, packet: dict[str, Any]) -> Path:
    """Queue the work packet into role's local queue file."""
    role_dir = ROOMS_ROOT / target_role.lower()
    role_dir.mkdir(parents=True, exist_ok=True)
    queue_file = role_dir / "dispatch_queue.json"

    items = []
    if queue_file.is_file():
        try:
            items = json.loads(queue_file.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                items = []
        except Exception:
            items = []

    items.append(packet)
    # Rolling FIFO max 20 packets per queue
    if len(items) > 20:
        items = items[-20:]
    queue_file.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    return queue_file


def log_dispatch_to_ledger(packet: dict[str, Any], delivery_mode: str):
    """Log the dispatch event to room_ledger.json."""
    if not ROOM_LEDGER_PATH.exists():
        return
    try:
        data = json.loads(ROOM_LEDGER_PATH.read_text(encoding="utf-8"))
        events = data.get("recent_events", [])
        events.append({
            "timestamp": packet["timestamp"],
            "event": "PUSH_DISPATCH",
            "target": packet["target_role"],
            "task_id": packet["task_id"],
            "delivery": delivery_mode
        })
        if len(events) > 50:
            events = events[-50:]
        data["recent_events"] = events
        ROOM_LEDGER_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def dispatch(
    target_role: str,
    action: str,
    task_id: int | None = None,
    payload: dict[str, Any] | None = None,
    dry_run: bool = False
) -> dict[str, Any]:
    """Execute push-driven dispatch to target agent."""
    packet = construct_work_packet(target_role, action, task_id, payload)
    handle = get_terminal_handle(target_role)

    if dry_run:
        return {
            "status": "dry_run",
            "packet": packet,
            "target_terminal_handle": handle,
            "delivery_mode": "terminal_push" if handle else "queue_fallback"
        }

    delivered = False
    delivery_mode = "queue_fallback"
    if handle:
        # Push notification or wake command to terminal
        cmd = f"# [PUSH_DISPATCH]: Task #{task_id or 'N/A'} - {action}"
        delivered = send_to_terminal(handle, cmd)
        if delivered:
            delivery_mode = "terminal_push"

    # Always persist in role's dispatch_queue.json for audit and state recovery
    queue_file = queue_work_packet(target_role, packet)
    log_dispatch_to_ledger(packet, delivery_mode)

    return {
        "status": "success",
        "event_id": packet["event_id"],
        "target_role": target_role,
        "delivery_mode": delivery_mode,
        "queue_file": str(queue_file.relative_to(PROJECT_ROOT))
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Target role (supervisor, pm, lead, peer, qc)")
    parser.add_argument("--action", required=True, help="Action directive or prompt")
    parser.add_argument("--task-id", type=int, help="Task ID from Harness DB")
    parser.add_argument("--payload", help="Optional JSON string payload")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without delivering")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()
    payload_dict = None
    if args.payload:
        try:
            payload_dict = json.loads(args.payload)
        except Exception as e:
            sys.stderr.write(f"Error parsing payload JSON: {e}\n")
            sys.exit(1)

    res = dispatch(
        target_role=args.target,
        action=args.action,
        task_id=args.task_id,
        payload=payload_dict,
        dry_run=args.dry_run
    )

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        if res["status"] == "success":
            print(f"🚀 [PUSH BROKER] Đã đẩy gói công việc thành công tới [{res['target_role']}]:")
            print(f"   • Event ID : {res['event_id']}")
            print(f"   • Delivery : {res['delivery_mode']}")
            print(f"   • Queue    : {res['queue_file']}")
        else:
            print(f"🔍 [DRY-RUN]: {res['packet']}")


if __name__ == "__main__":
    main()
