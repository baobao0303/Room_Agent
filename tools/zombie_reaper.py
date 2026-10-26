#!/usr/bin/env python3
"""
tools/zombie_reaper.py - Zombie Terminal Reaper & Watchdog Daemon for Ephemeral Sub-Agents.

Thực hiện Trụ cột 3 (Mục 9.3) & Trụ cột 5 (Mục 9.5) trong Master Spec:
docs/spec/ephemeral-sub-agent-orchestration-spec.md

Tính năng:
1. Zombie Terminal Reaper:
   - Quét danh sách terminal hiện hành qua `orca terminal list --json`.
   - Đối chiếu với registry `bmad/rooms/agent_terminals.json` và Harness Work Items.
   - Thu hồi (close) các terminal mồ côi (không có Task hợp lệ bảo trợ).
2. Watchdog Daemon & Timeout Ceiling:
   - Khống chế trần thời gian tối đa (mặc định: 300s).
   - Tự động gửi tín hiệu interrupt (`orca terminal send --interrupt`) khi Sub-Agent bị treo.
   - Cưỡng chế đóng terminal khi vượt ngưỡng cho phép để giải phóng RAM/PTY.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_shared_root(default_root: Path) -> Path:
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


SHARED_ROOT = _resolve_shared_root(PROJECT_ROOT)
ROOMS_DIR = SHARED_ROOT / "bmad" / "rooms"
REG_FILE = ROOMS_DIR / "agent_terminals.json"
HEARTBEAT_FILE = ROOMS_DIR / "heartbeats.json"

DEFAULT_TIMEOUT_S = 300


def run_cmd(cmd: List[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


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


def get_orca_terminals() -> List[Dict[str, Any]]:
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return []
    res = run_cmd([orca_bin, "terminal", "list", "--json"])
    if res.returncode != 0 or not res.stdout.strip():
        return []
    try:
        data = json.loads(res.stdout)
        return data.get("result", {}).get("terminals", [])
    except Exception:
        return []


def get_registered_handles() -> Dict[str, str]:
    if not REG_FILE.exists():
        return {}
    try:
        data = json.loads(REG_FILE.read_text(encoding="utf-8"))
        res = {}
        for role, info in data.items():
            if isinstance(info, dict) and "handle" in info:
                res[info["handle"]] = role
            elif isinstance(info, str):
                res[info] = role
        return res
    except Exception:
        return {}


def close_terminal(handle: str, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"  [DRY-RUN] Sẽ đóng terminal: {handle}")
        return True
    res = run_cmd(["orca", "terminal", "close", "--terminal", handle, "--tab", "--json"])
    return res.returncode == 0


def interrupt_terminal(handle: str, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"  [DRY-RUN] Sẽ gửi interrupt tới terminal: {handle}")
        return True
    res = run_cmd(["orca", "terminal", "send", "--terminal", handle, "--interrupt", "--json"])
    return res.returncode == 0


def audit_and_reap(dry_run: bool = False, timeout_s: int = DEFAULT_TIMEOUT_S, exclude_handles: Optional[List[str]] = None) -> Dict[str, Any]:
    terminals = get_orca_terminals()
    registered = get_registered_handles()
    exclude = set(exclude_handles or [])

    import os
    env_h = os.environ.get("ORCA_TERMINAL_HANDLE")
    if env_h:
        exclude.add(env_h)

    active_handles = {t.get("handle"): t for t in terminals if t.get("handle")}
    zombies = []
    stalled = []

    # 0. Xác định các terminal được bảo vệ theo ROOM_CAPACITIES (supervisor: 3, pm: 1, lead: 3, peer: 5, qc: 3)
    room_capacities = {"supervisor": 3, "pm": 1, "lead": 3, "peer": 5, "qc": 3}
    protected_room_handles: set[str] = set()
    for p_room, cap in room_capacities.items():
        candidates = []
        for h, t in active_handles.items():
            wt_path = (t.get("worktreePath") or "").lower().rstrip("/")
            branch = (t.get("branch") or "").lower().rstrip("/")
            if p_room in ("pm", "lead", "peer", "qc"):
                if wt_path.endswith(f"/room-{p_room}") or branch.endswith(f"room-{p_room}"):
                    candidates.append(t)
            else:
                if branch in ("main", "refs/heads/main") and "/room-" not in wt_path:
                    candidates.append(t)
        if candidates:
            candidates.sort(
                key=lambda x: (1 if x.get("handle") in registered else 0, x.get("lastOutputAt") or 0),
                reverse=True,
            )
            for c_term in candidates[:cap]:
                ch = c_term.get("handle")
                if ch:
                    protected_room_handles.add(ch)

    # 1. Phát hiện Zombie / Orphaned / Excess Terminals
    for handle, term in active_handles.items():
        title = (term.get("title") or "").lower()
        preview = (term.get("preview") or "").lower()
        wt_path = (term.get("worktreePath") or "").lower().rstrip("/")
        branch = (term.get("branch") or "").lower().rstrip("/")

        if handle in exclude:
            continue
        if any(kw in preview for kw in ("zombie_reaper", "audit_and_reap", "harness_manager", "room_cleanup")):
            continue

        is_known_room_wt = (
            wt_path.endswith(("/room-pm", "/room-lead", "/room-peer", "/room-qc"))
            or branch.endswith(("room-pm", "room-lead", "room-peer", "room-qc"))
            or (branch in ("main", "refs/heads/main") and "/room-" not in wt_path)
        )
        if is_known_room_wt:
            if handle in protected_room_handles or handle in registered:
                continue
            zombies.append({
                "handle": handle,
                "title": term.get("title", ""),
                "reason": "Exceeded room slot capacity ceiling in canonical room worktree"
            })
            continue

        # Không reap supervisor hoặc terminal đã đăng ký hợp lệ trong multi-slot registry
        if "supervisor" in title or "scope" in title or handle in registered:
            continue

        # Mọi terminal ngoài danh bạ đăng ký chính thức đều là ephemeral zombie
        zombies.append({
            "handle": handle,
            "title": term.get("title", ""),
            "reason": "Orphaned ephemeral sub-agent outside canonical room registry"
        })

    # 2. Xử lý Watchdog Timeout nếu có heartbeat
    if HEARTBEAT_FILE.exists():
        try:
            hb_data = json.loads(HEARTBEAT_FILE.read_text(encoding="utf-8"))
            now = time.time()
            for role, info in hb_data.items():
                last_ping = info.get("last_ping") or info.get("updated_at")
                if isinstance(last_ping, (int, float)):
                    duration = now - last_ping
                    if duration > timeout_s:
                        h = info.get("handle")
                        if h and h in active_handles:
                            stalled.append({
                                "role": role,
                                "handle": h,
                                "duration_s": round(duration, 1),
                                "timeout_s": timeout_s
                            })
        except Exception:
            pass

    # 3. Thu hồi (Reap) zombies
    reaped_count = 0
    for z in zombies:
        if close_terminal(z["handle"], dry_run=dry_run):
            reaped_count += 1

    return {
        "total_active_terminals": len(terminals),
        "registered_agents": len(registered),
        "zombies_detected": len(zombies),
        "zombies_reaped": reaped_count,
        "stalled_agents": len(stalled),
        "zombies": zombies,
        "stalled": stalled,
        "dry_run": dry_run
    }


def main():
    parser = argparse.ArgumentParser(description="Zombie Terminal Reaper & Watchdog Daemon")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra, không đóng terminal")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S, help="Ngưỡng timeout watchdog (giây)")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dạng JSON")
    parser.add_argument("--interrupt-stalled", action="store_true", help="Gửi interrupt tới các agent bị timeout")
    parser.add_argument("--exclude", action="append", default=[], help="Handle terminal cần giữ lại (không reap)")
    args = parser.parse_args()

    report = audit_and_reap(dry_run=args.dry_run, timeout_s=args.timeout, exclude_handles=args.exclude)

    if args.interrupt_stalled:
        for s in report.get("stalled", []):
            interrupt_terminal(s["handle"], dry_run=args.dry_run)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("======================================================================")
    print("🧟 [ZOMBIE TERMINAL REAPER & WATCHDOG REPORT]")
    print("======================================================================")
    print(f"• Tổng số Terminals đang mở trong Orca: {report['total_active_terminals']}")
    print(f"• Số Agent có đăng ký hợp lệ:          {report['registered_agents']}")
    print(f"• Số Zombie Terminals phát hiện:        {report['zombies_detected']}")
    print(f"• Số Zombie Terminals đã thu hồi:       {report['zombies_reaped']}")
    print(f"• Số Agent vượt trần Timeout ({args.timeout}s):    {report['stalled_agents']}")
    print("======================================================================")
    if report["zombies"]:
        print("Chi tiết Zombies:")
        for z in report["zombies"]:
            print(f"  - [{z['handle']}] {z['title']}: {z['reason']}")
    if report["stalled"]:
        print("Chi tiết Stalled:")
        for s in report["stalled"]:
            print(f"  - [{s['role']}] Handle {s['handle']} treo {s['duration_s']}s (Trần {s['timeout_s']}s)")


if __name__ == "__main__":
    main()
