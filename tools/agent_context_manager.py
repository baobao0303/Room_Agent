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


def resolve_shared_root(default_root: Path) -> Path:
    """Resolve canonical main worktree root so all room-* worktrees share bmad/rooms."""
    override = os.environ.get("SLPPC_SHARED_ROOT")
    if override:
        p = Path(override)
        if os.access(p, os.R_OK | os.W_OK):
            return p
    git_entry = default_root / ".git"
    try:
        if git_entry.is_file():
            raw = git_entry.read_text(encoding="utf-8").strip()
            if raw.startswith("gitdir:"):
                gitdir = Path(raw.split("gitdir:", 1)[1].strip())
                if not gitdir.is_absolute():
                    gitdir = (default_root / gitdir).resolve()
                if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
                    main_root = gitdir.parent.parent.parent
                    if os.access(main_root, os.R_OK | os.W_OK):
                        return main_root
    except Exception:
        pass
    return default_root


SHARED_ROOT = resolve_shared_root(PROJECT_ROOT)
BASE_DIR = str(SHARED_ROOT)
REGISTRY_FILE = SHARED_ROOT / "bmad" / "rooms" / "agent_terminals.json"

COMPACT_THRESHOLD_K = 200.0  # Ngưỡng token (k) để kích hoạt tự động /compact


def _normalize_room_role(role: str) -> str:
    r = role.lower().strip().replace("-", "_")
    if "supervisor" in r or r == "main":
        return "supervisor"
    if "lead" in r:
        return "lead"
    if "pm" in r:
        return "pm"
    if any(k in r for k in ("peer", "dev", "design")):
        return "peer"
    if "qc" in r:
        return "qc"
    return r


def _infer_terminal_room(term: Dict[str, Any]) -> Optional[str]:
    wt_path = (term.get("worktreePath") or "").lower().rstrip("/")
    wt_id = (term.get("worktreeId") or "").lower().rstrip("/")
    branch = (term.get("branch") or "").lower().rstrip("/")

    for r in ("pm", "lead", "peer", "qc"):
        token = f"room-{r}"
        if (
            wt_path.endswith(f"/{token}")
            or f"/{token}/" in wt_path
            or wt_id.endswith(f"/{token}")
            or branch.endswith(f"/{token}")
            or branch == token
        ):
            return r

    if branch in ("main", "refs/heads/main") or (
        wt_path and "/room-" not in wt_path and not wt_path.endswith(("/room-pm", "/room-lead", "/room-peer", "/room-qc"))
    ):
        return "supervisor"

    title = (term.get("title") or "").lower()
    if "[supervisor]" in title or "scope & intent" in title:
        return "supervisor"
    if "[lead" in title or "technical architect" in title:
        return "lead"
    if "[pm]" in title or "[pm agent]" in title or "feasibility" in title:
        return "pm"
    if "[peer" in title or "code executor" in title:
        return "peer"
    if "[qc]" in title or "istqb" in title or "verifier" in title:
        return "qc"
    return None


ROOM_CAPACITIES: Dict[str, int] = {
    "supervisor": 3,
    "pm": 1,
    "lead": 3,
    "peer": 5,
    "qc": 3,
}


def _get_orca_ide_bin() -> Optional[str]:
    shim_dir = Path.home() / ".config" / "orca" / "linux-orca-cli-shim"
    if shim_dir.is_dir():
        cur_path = os.environ.get("PATH", "")
        if str(shim_dir) not in cur_path.split(os.pathsep):
            os.environ["PATH"] = f"{shim_dir}{os.pathsep}{cur_path}"
    cand = shutil.which("orca")
    if not cand:
        return None
    real_cand = os.path.realpath(cand)
    if cand in ("/usr/bin/orca", "/bin/orca", "/usr/games/orca") or real_cand in ("/usr/bin/orca", "/bin/orca"):
        return None
    try:
        p = Path(real_cand)
        if p.is_file() and p.stat().st_size < 65536:
            head = p.read_bytes()[:512].decode("utf-8", errors="ignore").lower()
            if "screen reader" in head or "gnome" in head or "speech" in head or "import orca" in head:
                return None
    except Exception:
        pass
    return cand


def get_live_terminals() -> Dict[str, str]:
    """Trả về mapping {role: handle} cho các terminal đang active trong Orca (chỉ đóng tab khi vượt quá ROOM_CAPACITIES)."""
    if os.environ.get("SLPPC_DRY_RUN") == "1" or not _get_orca_ide_bin():
        return {}
    try:
        reg_data: Dict[str, Any] = {}
        if REGISTRY_FILE.exists():
            try:
                reg_data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            except Exception:
                reg_data = {}

        res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return {}
        terminals = [
            t for t in json.loads(res.stdout).get("result", {}).get("terminals", [])
            if t.get("handle") and not t.get("stopped") and t.get("connected", True)
        ]

        by_room: Dict[str, list[Dict[str, Any]]] = {}
        for t in terminals:
            room = _infer_terminal_room(t)
            if room:
                by_room.setdefault(room, []).append(t)

        valid_map: Dict[str, str] = {}
        updated_reg = False

        registered_handles = {
            v.get("handle"): k
            for k, v in reg_data.items()
            if isinstance(v, dict) and v.get("handle")
        }

        for room, room_terms in by_room.items():
            capacity = ROOM_CAPACITIES.get(room, 1)
            reg_h = (reg_data.get(room) or {}).get("handle") if isinstance(reg_data.get(room), dict) else None
            room_terms.sort(
                key=lambda x: (
                    2 if x.get("handle") == reg_h else (1 if x.get("handle") in registered_handles else 0),
                    x.get("lastOutputAt") or 0,
                ),
                reverse=True,
            )
            primary = room_terms[0]
            primary_h = primary.get("handle")
            if primary_h:
                valid_map[room] = primary_h
                if reg_h != primary_h:
                    reg_data[room] = {"handle": primary_h, "tabId": primary.get("tabId") or "", "room": room}
                    updated_reg = True
                for t in room_terms[:capacity]:
                    th = t.get("handle")
                    if th and th in registered_handles:
                        valid_map[registered_handles[th]] = th
                # Chỉ đóng các terminal vượt quá trần ROOM_CAPACITIES của phòng đó
                for extra in room_terms[capacity:]:
                    extra_h = extra.get("handle")
                    if extra_h and extra_h != primary_h and extra_h not in registered_handles:
                        subprocess.run(["orca", "terminal", "close", "--terminal", extra_h, "--tab", "--json"], capture_output=True, timeout=5)

        if updated_reg:
            try:
                REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
                REGISTRY_FILE.write_text(json.dumps(reg_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception:
                pass

        return valid_map
    except Exception:
        return {}


def has_live_terminal(role: str) -> Optional[str]:
    """Kiểm tra xem room tương ứng với role đã có live terminal hay chưa."""
    live_map = get_live_terminals()
    canonical = _normalize_room_role(role)
    return live_map.get(canonical)


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
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return info

    try:
        res = subprocess.run(
            [orca_bin, "terminal", "read", "--terminal", handle, "--screen"],
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

        # Nhận diện xem terminal có đang chạy AI Agent thật hay ngồi ở raw shell (bash/zsh)
        screen_lower = screen.lower()
        is_agent = (
            "❯" in screen
            or "hermes" in screen_lower
            or "gemini" in screen_lower
            or "claude" in screen_lower
            or "codex" in screen_lower
            or "nous research" in screen_lower
        )
        info["is_agent"] = is_agent

        # Kiểm tra trạng thái prompt
        lines = [line.strip() for line in screen.split("\n") if line.strip()]
        tail = " \n ".join(lines[-5:]) if lines else ""
        info["status_line"] = tail

        # Ready khi có dấu nhắc ❯ và KHÔNG có cảnh báo 'Ctrl+C to interrupt' hoặc đang chạy command
        busy_keywords = ("ctrl+c to interrupt", "brainstorming", "cogitating", "computing", "reflecting", "pondering", "mulling", "synthesizing", "ruminating")
        if any(k in tail.lower() for k in busy_keywords):
            info["is_busy"] = True
            info["is_ready"] = False
        elif is_agent and ("ready" in tail.lower() or (lines and lines[-1].endswith("❯"))):
            info["is_busy"] = False
            info["is_ready"] = True
        elif not is_agent:
            # Ngồi ở raw bash shell: Chưa bật agent, không thể nhận prompt trực tiếp!
            info["is_busy"] = False
            info["is_ready"] = False
        else:
            info["is_busy"] = False
            info["is_ready"] = is_agent

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
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return False
    print(f"🗜️ [Auto-Compact]: Kích hoạt /compact trên terminal {handle}...")
    try:
        subprocess.run(
            [orca_bin, "terminal", "send", "--terminal", handle, "--text", "/compact", "--enter"],
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
    if clean_role in ("peer1", "peer2", "peer3", "peer4", "peer_2", "peer_3", "peer_4", "design", "peer_design", "peer_dev"):
        clean_role = "peer"
    profile_map = {
        "supervisor": "profiles/supervisor.md",
        "pm": "profiles/pm.md",
        "lead": "profiles/lead.md",
        "peer": "profiles/peer.md",
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
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return False
    print(f"🔄 [Auto-Rehydration]: Khởi tạo phiên mới (/new) và nạp lại context cho {role.upper()}...")
    try:
        # 1. Gửi lệnh /new
        subprocess.run(
            [orca_bin, "terminal", "send", "--terminal", handle, "--text", "/new", "--enter"],
            capture_output=True, timeout=5
        )
        time.sleep(2)
        wait_for_terminal_ready(handle, max_wait_sec=10)

        # 2. Bắn prompt rehydration
        boot_prompt = build_rehydration_prompt(role)
        subprocess.run(
            [orca_bin, "terminal", "send", "--terminal", handle, "--text", boot_prompt, "--enter"],
            capture_output=True, timeout=5
        )
        print(f"✅ [Auto-Rehydration]: Đã nạp lại context thành công cho {role.upper()} ({handle}).")
        return True
    except Exception as e:
        print(f"⚠️ [Auto-Rehydration Error]: {e}")
        return False


def safe_send_agent_message(role: str, message: str, auto_compact: bool = True) -> bool:
    """Gửi thông điệp an toàn cho agent: Có ping check, có kiểm tra context để compact, chống đè lệnh."""
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return False
    live_map = get_live_terminals()
    canonical_role = _normalize_room_role(role)
    handle = live_map.get(canonical_role)
    if not handle:
        clean_role = role.lower().strip().replace("-", "_").replace(" ", "_")
        handle = live_map.get(clean_role)
    if not handle:
        return False

    # 1. Ping check: Kiểm tra terminal còn sống và trạng thái hiện tại
    state = inspect_terminal(handle)
    if not state["is_live"]:
        print(f"⚠️ [Ping Check]: Terminal của {role.upper()} ({handle}) không phản hồi.")
        return False

    # 1.1 Khởi động Agent nếu terminal đang ở raw bash/zsh shell
    if not state.get("is_agent", False):
        print(f"🚀 [Auto-Agent-Start]: Terminal {handle} đang ở raw shell (chưa bật Agent). Đang tự động khởi động Hermes cho {role.upper()}...")
        profile_flag = f"--profile {canonical_role}" if canonical_role in ("pm", "lead", "peer", "qc") else ""
        subprocess.run(
            [orca_bin, "terminal", "send", "--terminal", handle, "--text", f"source ~/.bashrc && hermes {profile_flag}".strip(), "--enter"],
            capture_output=True, timeout=5
        )
        if not wait_for_terminal_ready(handle, max_wait_sec=12):
            print(f"⚠️ [Auto-Agent-Start]: Không thể khởi động agent trên {handle} sau 12s. Chuyển sang fallback spawn.")
            return False
        state = inspect_terminal(handle)

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
            [orca_bin, "terminal", "send", "--terminal", handle, "--text", message, "--enter"],
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
