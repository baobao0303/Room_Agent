#!/usr/bin/env python3
"""
tools/agent_scanner.py - Native Process Scanner & Agent Discovery Engine.
Detects running AI Agent processes (Hermes, Claude Code, Codex, Opencode, Orca) on macOS/Linux
and synchronizes active sessions into bmad/rooms/agent_terminals.json.
Adapted from gawkbot/internal/agentdetect with zero external dependencies.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TERMINALS_JSON_PATH = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"

AGENT_SIGNATURES = [
    ("hermes", re.compile(r"\b(hermes|python[0-9.]*\s+.*hermes)\b", re.IGNORECASE)),
    ("claude-code", re.compile(r"\b(claude|@anthropic-ai/claude-code)\b", re.IGNORECASE)),
    ("codex", re.compile(r"\b(codex(-[a-z0-9_-]+)?)\b", re.IGNORECASE)),
    ("opencode", re.compile(r"\b(opencode)\b", re.IGNORECASE)),
    ("orca", re.compile(r"\b(orca(\.app)?|linux-orca-cli-shim)\b", re.IGNORECASE)),
]


def list_running_processes() -> list[dict[str, Any]]:
    """List processes with pid, ppid, comm, and full command line via ps."""
    procs = []
    try:
        # Standard POSIX ps command available on macOS and Linux
        res = subprocess.run(
            ["ps", "-eo", "pid,ppid,args"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in res.stdout.splitlines()[1:]:
            parts = line.strip().split(None, 2)
            if len(parts) >= 3:
                try:
                    pid = int(parts[0])
                    ppid = int(parts[1])
                    args = parts[2]
                    procs.append({"pid": pid, "ppid": ppid, "args": args})
                except ValueError:
                    continue
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to scan processes via ps: {e}\n")
    return procs


def detect_agents(processes: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Filter running processes against known AI Agent signatures."""
    if processes is None:
        processes = list_running_processes()

    discovered = []
    my_pid = os.getpid()

    for p in processes:
        if p["pid"] == my_pid:
            continue
        args = p["args"]
        for kind, pattern in AGENT_SIGNATURES:
            if pattern.search(args):
                # Classify role if mentioned in command line
                inferred_role = "worker"
                for role in ("supervisor", "pm", "lead", "peer", "qc", "security"):
                    if re.search(rf"\b{role}([_-][a-z0-9_-]+|[0-9]+)?\b", args, re.IGNORECASE):
                        inferred_role = role
                        break

                discovered.append({
                    "pid": p["pid"],
                    "ppid": p["ppid"],
                    "kind": kind,
                    "inferred_role": inferred_role,
                    "command": args[:120],
                    "detected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                break
    return discovered


def sync_to_terminals_registry(agents: list[dict[str, Any]]) -> dict[str, Any]:
    """Sync detected agents into bmad/rooms/agent_terminals.json."""
    data = {}
    if TERMINALS_JSON_PATH.exists():
        try:
            data = json.loads(TERMINALS_JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    updated_count = 0
    for ag in agents:
        role = ag["inferred_role"]
        if role in ("supervisor", "pm", "lead", "peer", "qc"):
            if role not in data:
                data[role] = {
                    "handle": f"proc_{ag['pid']}",
                    "tabId": f"auto_{ag['kind']}_{ag['pid']}",
                    "kind": ag["kind"]
                }
                updated_count += 1

    if updated_count > 0:
        TERMINALS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        TERMINALS_JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "updated": updated_count,
        "total_registry_entries": len(data)
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dưới định dạng JSON")
    parser.add_argument("--sync", action="store_true", help="Tự động đồng bộ vào bmad/rooms/agent_terminals.json")
    args = parser.parse_args()

    agents = detect_agents()
    sync_result = None
    if args.sync:
        sync_result = sync_to_terminals_registry(agents)

    report = {
        "status": "ok",
        "total_detected": len(agents),
        "agents": agents,
        "sync_result": sync_result
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"🔍 [AGENT PROCESS SCANNER] Phát hiện {len(agents)} tiến trình Agent đang chạy:")
        for ag in agents:
            print(f"  • PID {ag['pid']:<7} | Kind: {ag['kind']:<12} | Role: {ag['inferred_role']:<10} | {ag['command']}")
        if sync_result:
            print(f"  ✅ Đã đồng bộ {sync_result['updated']} agents mới vào bmad/rooms/agent_terminals.json")


if __name__ == "__main__":
    main()
