#!/usr/bin/env python3
"""
tools/agent_context_manager.py - Bộ quản lý Context Window, Auto-Compact & Auto-Rehydration cho Agent SLPPC.

Tính năng:
1. Ping check & kiểm tra trạng thái Terminal (is_ready, is_busy, token_count_k) trước khi gửi tin.
2. Tự động Compact (`/compact`) khi context đạt ngưỡng cao (> 200k tokens), giảm tải 60-70% request size.
3. Tự động Re-hydrate sau khi `/new`: Nạp lại hồ sơ vai trò (profiles/*.md), task active trên Harness DB và latest handoff.
4. Chống flood: Kiểm tra TUI idle, không ngắt quãng turn đang chạy của agent khác.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = str(PROJECT_ROOT)
REGISTRY_FILE = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"

COMPACT_THRESHOLD_K = 200.0  # Ngưỡng token (k) để kích hoạt tự động /compact


def get_live_terminals() -> Dict[str, str]:
    """Trả về mapping {role: handle} cho các terminal đang active trong Orca."""
    if not shutil.which("orca") or not REGISTRY_FILE.exists():
        return {}
    try:
        reg_data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return {}
        terminals = json.loads(res.stdout).get("result", {}).get("terminals", [])
        live_handles = {t.get("handle") for t in terminals}
        
        valid_map = {}
        for role, meta in reg_data.items():
            h = meta.get("handle")
            if h and h in live_handles:
                valid_map[role.lower()] = h
        return valid_map
    except Exception:
        return {}


def inspect_terminal(handle: str) -> Dict[str, Any]:
    """Đọc màn hình terminal, trích xuất token usage, trạng thái bận/rảnh."""
    info = {
        "handle": handle,
        "is_live": False,
        "is_ready": False,
        "is_busy": True,
        "token_count_k": 0.0,
        "needs_compact": False,
        "status_line": ""
    }
    if not shutil.which("orca"):
        return info

    try:
        res = subprocess.run(
            ["orca", "terminal", "read", "--terminal", handle, "--screen"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode != 0:
            return info
        info["is_live"] = True
        screen = res.stdout

        # Tìm token count (VD: 243.6k t hoặc 180.2k t)
        match = re.search(r"([\d\.]+)k\s*t", screen)
        if match:
            tokens_k = float(match.group(1))
            info["token_count_k"] = tokens_k
            info["needs_compact"] = tokens_k >= COMPACT_THRESHOLD_K

        # Kiểm tra trạng thái prompt
        lines = [line.strip() for line in screen.split("\n") if line.strip()]
        tail = " \n ".join(lines[-5:]) if lines else ""
        info["status_line"] = tail

        # Ready khi có dấu nhắc ❯ và KHÔNG có cảnh báo 'Ctrl+C to interrupt' hoặc đang chạy command
        if "Ctrl+C to interrupt" in tail or "brainstorming" in tail or "cogitating" in tail or "computing" in tail:
            info["is_busy"] = True
            info["is_ready"] = False
        elif "ready" in tail or (lines and lines[-1].endswith("❯")):
            info["is_busy"] = False
            info["is_ready"] = True
        else:
            info["is_busy"] = False
            info["is_ready"] = True

    except Exception:
        pass
    return info


def wait_for_terminal_ready(handle: str, max_wait_sec: int = 10) -> bool:
    """Chờ cho đến khi terminal ở trạng thái sẵn sàng (ready prompt ❯)."""
    start = time.time()
    while time.time() - start < max_wait_sec:
        state = inspect_terminal(handle)
        if state["is_ready"]:
            return True
        time.sleep(1)
    return False


def compact_agent_terminal(handle: str, max_wait_sec: int = 25) -> bool:
    """Gửi lệnh /compact tới terminal và chờ quá trình nén hoàn tất."""
    if not shutil.which("orca"):
        return False
    print(f"🗜️ [Auto-Compact]: Kích hoạt /compact trên terminal {handle}...")
    try:
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", "/compact", "--enter"],
            capture_output=True, timeout=5
        )
        # Chờ quá trình nén hoàn tất
        start = time.time()
        time.sleep(2)
        while time.time() - start < max_wait_sec:
            state = inspect_terminal(handle)
            if state["is_ready"] and "Compacting context" not in state["status_line"]:
                print(f"✅ [Auto-Compact]: Đã nén context thành công cho {handle}! Tokens hiện tại: {state['token_count_k']}k")
                return True
            time.sleep(1.5)
    except Exception as e:
        print(f"⚠️ [Auto-Compact Error]: {e}")
    return False


def build_rehydration_prompt(role: str) -> str:
    """Tạo bản tin context nạp lại cho Agent khi phiên bị /new hoặc khởi động lại."""
    clean_role = role.lower().replace("-", "_").replace(" ", "_")
    
    # 1. Tra cứu file profile
    profile_map = {
        "supervisor": "profiles/supervisor.md",
        "pm": "profiles/pm.md",
        "lead": "profiles/lead.md",
        "peer": "profiles/peer.md",
        "peer2": "profiles/peer_2.md",
        "peer3": "profiles/peer_3.md",
        "peer4": "profiles/peer_4.md",
        "design": "profiles/peer_design.md",
        "qc": "profiles/qc.md"
    }
    profile_file = PROJECT_ROOT / profile_map.get(clean_role, f"profiles/{clean_role}.md")
    mission = f"Vai trò {role.upper()} trong mô hình điều hành 5 vai trò SLPPC."
    if profile_file.exists():
        try:
            lines = profile_file.read_text(encoding="utf-8").split("\n")
            for line in lines:
                if "MISSION:" in line or "Room role:" in line:
                    mission = line.strip()
                    break
        except Exception:
            pass

    # 2. Tra cứu task active trên Harness DB
    active_tasks_info = "Không có task Active tồn đọng"
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "tools"))
        from tools.harness_manager import HarnessManager  # type: ignore
        mgr = HarnessManager()
        active_items = mgr.list_work_items(state="Active", assigned_to_profile=clean_role)
        if active_items:
            task_strs = [f"#{item['id']} [{item.get('type')}] {item.get('title')}" for item in active_items[:3]]
            active_tasks_info = "; ".join(task_strs)
    except Exception:
        pass

    # 3. Tra cứu handoff gần nhất
    handoff_info = "Không có biên bản handoff gần đây"
    role_dir = PROJECT_ROOT / "bmad" / "rooms" / clean_role
    if role_dir.exists():
        latest = role_dir / "latest_handoff.md"
        if latest.exists():
            try:
                txt = latest.read_text(encoding="utf-8")
                summary_match = re.search(r"-\s*\*\*Tóm tắt\*\*:\s*(.+)", txt)
                if summary_match:
                    handoff_info = summary_match.group(1).strip()
            except Exception:
                pass

    prompt = (
        f"=== [SLPPC AUTO-REHYDRATION BOOT] ===\n"
        f"Vai trò: {role.upper()}\n"
        f"Sứ mệnh: {mission}\n"
        f"Nhiệm vụ Active hiện tại: {active_tasks_info}\n"
        f"Biên bản bàn giao gần nhất: {handoff_info}\n"
        f"Kỷ luật: 100% Strict Typing (0 any/unknown), Chuẩn Zero-Search 5 thành phần, Anti-Leak, cấm role_trespass.\n"
        f"Xác nhận đã nạp lại context đầy đủ và sẵn sàng làm việc."
    )
    return prompt


def rehydrate_agent(role: str, handle: str) -> bool:
    """Thực thi lệnh /new và nạp lại context tức thời cho agent."""
    if not shutil.which("orca"):
        return False
    print(f"🔄 [Auto-Rehydration]: Khởi tạo phiên mới (/new) và nạp lại context cho {role.upper()}...")
    try:
        # 1. Gửi lệnh /new
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", "/new", "--enter"],
            capture_output=True, timeout=5
        )
        time.sleep(2)
        wait_for_terminal_ready(handle, max_wait_sec=10)

        # 2. Bắn prompt rehydration
        boot_prompt = build_rehydration_prompt(role)
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", boot_prompt, "--enter"],
            capture_output=True, timeout=5
        )
        print(f"✅ [Auto-Rehydration]: Đã nạp lại context thành công cho {role.upper()} ({handle}).")
        return True
    except Exception as e:
        print(f"⚠️ [Auto-Rehydration Error]: {e}")
        return False


def safe_send_agent_message(role: str, message: str, auto_compact: bool = True) -> bool:
    """Gửi thông điệp an toàn cho agent: Có ping check, có kiểm tra context để compact, chống đè lệnh."""
    live_map = get_live_terminals()
    clean_role = role.lower().strip().replace("-", "_").replace(" ", "_")
    handle = live_map.get(clean_role)
    if not handle:
        for k, h in live_map.items():
            if clean_role in k or k in clean_role:
                handle = h
                break

    if not handle:
        return False

    # 1. Ping check: Kiểm tra terminal còn sống và trạng thái hiện tại
    state = inspect_terminal(handle)
    if not state["is_live"]:
        print(f"⚠️ [Ping Check]: Terminal của {role.upper()} ({handle}) không phản hồi.")
        return False

    # 2. Nếu agent đang bận, chờ tối đa 8s
    if state["is_busy"]:
        print(f"⏳ [Ping Check]: {role.upper()} đang bận xử lý, chờ TUI idle...")
        if not wait_for_terminal_ready(handle, max_wait_sec=8):
            print(f"⚠️ [Ping Check]: {role.upper()} vẫn bận sau 8s. Hủy gửi để tránh gián đoạn tiến trình.")
            return False

    # 3. Kiểm tra Context Window & Auto-Compact
    if auto_compact and state["needs_compact"]:
        print(f"⚠️ [Context Warning]: {role.upper()} đạt {state['token_count_k']}k tokens (> {COMPACT_THRESHOLD_K}k). Đang tự động nén context...")
        compact_agent_terminal(handle, max_wait_sec=20)
        wait_for_terminal_ready(handle, max_wait_sec=5)

    # 4. Gửi lệnh
    try:
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", message, "--enter"],
            capture_output=True, timeout=10
        )
        return True
    except Exception as e:
        print(f"⚠️ [Send Error]: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quản trị Context Window, Auto-Compact & Rehydration cho Agent SLPPC.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p_inspect = subparsers.add_parser("inspect", help="Kiểm tra context window và trạng thái của một hoặc toàn bộ role")
    p_inspect.add_argument("--role", default=None, help="Tên role cần kiểm tra (mặc định kiểm tra toàn bộ)")

    p_compact = subparsers.add_parser("compact", help="Kích hoạt nén context (/compact) cho một role")
    p_compact.add_argument("--role", required=True, help="Tên role (supervisor, lead, peer, qc...)")

    p_rehydrate = subparsers.add_parser("rehydrate", help="Kích hoạt /new và nạp lại context (re-hydrate) cho một role")
    p_rehydrate.add_argument("--role", required=True, help="Tên role")

    args = parser.parse_args()

    if args.action == "inspect":
        live_map = get_live_terminals()
        print("\n=========================================================================")
        print("      SLPPC AGENT CONTEXT WINDOW & TOKEN USAGE MONITOR")
        print("=========================================================================")
        print(f"{'ROLE':<12} | {'HANDLE':<38} | {'TOKENS':<10} | {'STATUS'}")
        print("-" * 73)
        for r, h in live_map.items():
            if args.role and args.role.lower() not in r:
                continue
            st = inspect_terminal(h)
            ready_str = "🟢 Ready" if st["is_ready"] else "🟡 Busy"
            compact_str = " (⚠️ CẦN COMPACT)" if st["needs_compact"] else ""
            tok_str = f"{st['token_count_k']}k t" if st['token_count_k'] > 0 else "N/A"
            print(f"{r.upper():<12} | {h:<38} | {tok_str:<10} | {ready_str}{compact_str}")
        print("=========================================================================\n")

    elif args.action == "compact":
        live_map = get_live_terminals()
        handle = live_map.get(args.role.lower())
        if not handle:
            print(f"❌ Không tìm thấy live terminal cho role '{args.role}'.")
            sys.exit(1)
        compact_agent_terminal(handle)

    elif args.action == "rehydrate":
        live_map = get_live_terminals()
        handle = live_map.get(args.role.lower())
        if not handle:
            print(f"❌ Không tìm thấy live terminal cho role '{args.role}'.")
            sys.exit(1)
        rehydrate_agent(args.role, handle)


if __name__ == "__main__":
    main()
