#!/usr/bin/env python3
"""
scripts/agent_start.py - All-in-One CLI để quản lý, khởi chạy và giám sát các Agent SLPPC.

Sử dụng:
  ./cli/agent-start                 Khởi chạy toàn bộ phòng multi-agent (idempotent, không mở trùng)
  ./cli/agent-start <role>          Khởi chạy một agent cụ thể (pm, lead, peer, peer2, peer3, peer4, design, qc)
  ./cli/agent-start status          Xem trạng thái chi tiết của tất cả các Agent và nhịp tim
  ./cli/agent-start restart         Khởi động lại toàn bộ các Agent
  ./cli/agent-start stop [role]     Đóng tab của agent (hoặc tất cả nếu dùng --all)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
REG_FILE = SCRIPT_DIR / "bmad" / "rooms" / "agent_terminals.json"
HB_FILE = SCRIPT_DIR / "bmad" / "rooms" / "heartbeats.json"

AGENTS = {
    "supervisor": (
        "[Supervisor] Scope & Intent Guard in SLPPC. "
        "Chuyên trách quản trị phạm vi, tạo Epic/Task trên Harness DB, "
        "điều phối PM, Lead, Peer, QC và bảo vệ Single-Ownership Invariant."
    ),
    "supervisor2": (
        "[Supervisor 2] Nested Scope & Intent Guard in SLPPC. "
        "Chuyên trách điều phối nhánh Sub-Epic hoặc Epic song song lồng ghép với Master Supervisor."
    ),
    "supervisor3": (
        "[Supervisor 3] Nested Scope & Intent Guard in SLPPC. "
        "Chuyên trách điều phối nhánh Sub-Epic hoặc Epic song song lồng ghép với Master Supervisor."
    ),
    "pm": (
        "[PM Agent] Product Manager & Decision Arbiter in SLPPC. "
        "Chuyên trách đánh giá Feasibility và Alignment qua Kev System One (<50ms), "
        "kiểm soát AC và kiểm tra bẫy lỗi cũ từ Harness Learn."
    ),
    "lead": (
        "[Lead Dev] Technical Architect. "
        "Chuyên trách kiến trúc, phân rã task chuẩn Zero-Search và review code qua 7 tiêu chí."
    ),
    "lead2": (
        "[Lead Dev 2] Technical Architect (Slot 2). "
        "Chuyên trách kiến trúc nhánh song song, phân rã task chuẩn Zero-Search và review code."
    ),
    "lead3": (
        "[Lead Dev 3] Technical Architect (Slot 3). "
        "Chuyên trách kiến trúc nhánh song song, phân rã task chuẩn Zero-Search và review code."
    ),
    "peer": (
        "[Peer Dev] Code & UI Executor. "
        "Chuyên trách thực thi mã nguồn Full-Stack, ánh xạ Figma/TDS UI tokens và nộp Resolved theo điều phối của Lead."
    ),
    "peer2": (
        "[Peer Dev 2] Code & UI Executor (Slot 2). "
        "Chuyên trách thực thi mã nguồn song song theo Single-Ownership và nộp Resolved."
    ),
    "peer3": (
        "[Peer Dev 3] Code & UI Executor (Slot 3). "
        "Chuyên trách thực thi mã nguồn song song theo Single-Ownership và nộp Resolved."
    ),
    "peer4": (
        "[Peer Dev 4] Code & UI Executor (Slot 4). "
        "Chuyên trách thực thi mã nguồn song song theo Single-Ownership và nộp Resolved."
    ),
    "peer_design": (
        "[Peer Design] UI/UX & Tokens Executor. "
        "Chuyên trách bóc tách Figma/TDS UI tokens và thiết kế giao diện chuẩn Angular 18."
    ),
    "qc": (
        "[QC] 5-Stage ISTQB Verifier. "
        "Chuyên trách sinh test matrix, nghiệm thu độc lập và đóng task."
    ),
    "qc2": (
        "[QC 2] 5-Stage ISTQB Verifier (Slot 2). "
        "Chuyên trách sinh test matrix, nghiệm thu độc lập song song và đóng task."
    ),
    "qc3": (
        "[QC 3] 5-Stage ISTQB Verifier (Slot 3). "
        "Chuyên trách sinh test matrix, nghiệm thu độc lập song song và đóng task."
    ),
}

TITLES = {
    "supervisor": "[Supervisor] Scope & Intent Guard",
    "supervisor2": "[Supervisor 2] Nested Scope Guard",
    "supervisor3": "[Supervisor 3] Nested Scope Guard",
    "pm": "[PM] Feasibility & Alignment",
    "lead": "[Lead Dev] Technical Architect",
    "lead2": "[Lead Dev 2] Technical Architect",
    "lead3": "[Lead Dev 3] Technical Architect",
    "peer": "[Peer Dev] Code & UI Executor",
    "peer2": "[Peer Dev 2] Code & UI Executor",
    "peer3": "[Peer Dev 3] Code & UI Executor",
    "peer4": "[Peer Dev 4] Code & UI Executor",
    "peer_design": "[Peer Design] UI/UX & Tokens",
    "qc": "[QC] 5-Stage ISTQB Verifier",
    "qc2": "[QC 2] 5-Stage ISTQB Verifier",
    "qc3": "[QC 3] 5-Stage ISTQB Verifier",
}

MODELS = {k: "ag/gemini-3.8-flash-high" for k in AGENTS}
REASONINGS = {k: "high" for k in AGENTS}

ROOM_CAPACITIES = {
    "supervisor": 3,
    "pm": 1,
    "lead": 3,
    "peer": 5,
    "qc": 3,
}

PERSISTENT_ROLES = ["supervisor"]
EPHEMERAL_ROLES = ["pm", "lead", "lead2", "lead3", "peer", "peer2", "peer3", "peer4", "peer_design", "qc", "qc2", "qc3"]
ALL_ROLES = ["supervisor", "pm", "lead", "peer", "qc"]


def normalize_room(role: str) -> str:
    """Chuẩn hóa về tên phòng (worktree) của role."""
    r = role.strip().lower().replace("-", "_")
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


def normalize_role(role: str) -> str:
    """Chuẩn hóa định danh từng slot cụ thể để cho phép mở nhiều Peer, nhiều Lead, nhiều QC, nhiều Supervisor."""
    r = role.strip().lower().replace("-", "_")
    if r in ("main", "supervisor", "supervisor1", "supervisor_1"):
        return "supervisor"
    for idx in (2, 3):
        if r in (f"supervisor{idx}", f"supervisor_{idx}"):
            return f"supervisor{idx}"
    if r in ("pm", "pm1", "pm_1"):
        return "pm"
    if r in ("lead", "lead1", "lead_1", "lead_dev"):
        return "lead"
    for idx in (2, 3):
        if r in (f"lead{idx}", f"lead_{idx}", f"lead_dev_{idx}"):
            return f"lead{idx}"
    if r in ("design", "peer_design"):
        return "peer_design"
    if r in ("peer", "peer1", "peer_1", "peer_dev", "dev", "dev1"):
        return "peer"
    for idx in (2, 3, 4):
        if r in (f"peer{idx}", f"peer_{idx}", f"peer_dev_{idx}", f"dev{idx}"):
            return f"peer{idx}"
    if r in ("qc", "qc1", "qc_1"):
        return "qc"
    for idx in (2, 3):
        if r in (f"qc{idx}", f"qc_{idx}"):
            return f"qc{idx}"
    return r


def get_orca_ide_bin() -> str | None:
    """
    Trả về đường dẫn Orca IDE CLI thật.
    TUYỆT ĐỐI CHẶN `/usr/bin/orca` và `/bin/orca` (Linux GNOME Screen Reader)
    để không bao giờ kích hoạt nhầm trình đọc màn hình giọng nói (speech-dispatcher / espeak-ng).
    """
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


def disable_linux_screen_reader() -> None:
    """Tắt trình đọc màn hình GNOME/Cinnamon Screen Reader (/usr/bin/orca) nếu bị bật nhầm trên Linux."""
    if sys.platform != "linux":
        return
    for schema in ("org.gnome.desktop.a11y.applications", "org.cinnamon.desktop.a11y.applications"):
        if shutil.which("gsettings"):
            subprocess.run(
                ["gsettings", "set", schema, "screen-reader-enabled", "false"],
                capture_output=True,
                check=False,
            )


def run_cmd(args: list[str]) -> tuple[int, str]:
    try:
        if args and args[0] == "orca":
            orca_bin = get_orca_ide_bin()
            if not orca_bin:
                return 1, "Orca IDE CLI not found (blocked /usr/bin/orca GNOME Screen Reader)"
            args = [orca_bin] + args[1:]
        res = subprocess.run(args, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        return res.returncode, res.stdout.strip()
    except Exception as exc:
        return 1, str(exc)


def get_live_terminals() -> dict[str, dict]:
    """Lấy danh sách các terminal đang thực sự sống trong Orca Runtime."""
    if not get_orca_ide_bin():
        return {}
    code, out = run_cmd(["orca", "terminal", "list", "--json"])
    if code != 0 or not out:
        return {}
    try:
        data = json.loads(out)
        terms = data.get("result", {}).get("terminals", [])
        return {t.get("handle"): t for t in terms if t.get("handle")}
    except Exception:
        return {}


def load_registry() -> dict[str, dict]:
    if not REG_FILE.exists():
        return {}
    try:
        return json.loads(REG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_registry(registry: dict[str, dict]) -> None:
    REG_FILE.parent.mkdir(parents=True, exist_ok=True)
    REG_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def ensure_orca_ready() -> bool:
    disable_linux_screen_reader()
    orca_bin = get_orca_ide_bin()
    if not orca_bin:
        print(
            "❌ Lỗi: Không tìm thấy Orca IDE CLI (~/.config/orca/linux-orca-cli-shim/orca). "
            "Đã tự động chặn '/usr/bin/orca' (GNOME Screen Reader) để tránh lỗi phát giọng nói.",
            file=sys.stderr,
        )
        return False
    code, _ = run_cmd([orca_bin, "status", "--json"])
    if code != 0:
        print("🚀 Đang khởi động Orca Desktop...")
        run_cmd([orca_bin, "open"])
        time.sleep(2)
    return True


def _is_term_in_role_room(t_val: dict, role: str) -> bool:
    wt_path = (t_val.get("worktreePath") or "").rstrip("/")
    branch = (t_val.get("branch") or "").rstrip("/")
    target_room = normalize_room(role)
    if target_room == "supervisor":
        return branch in ("main", "refs/heads/main") and "/room-" not in wt_path
    return wt_path.endswith(f"/room-{target_room}") or branch.endswith(f"room-{target_room}")


def launch_single(role: str, registry: dict[str, dict], live_terms: dict[str, dict]) -> str:
    """Khởi chạy 1 slot agent (hỗ trợ mở đồng thời nhiều Peer, nhiều Lead, nhiều QC, nhiều Supervisor theo ROOM_CAPACITIES)."""
    slot_id = normalize_role(role)
    target_room = normalize_room(slot_id)
    capacity = ROOM_CAPACITIES.get(target_room, 1)
    title = TITLES.get(slot_id, slot_id)
    existing_handle = registry.get(slot_id, {}).get("handle")

    room_matches = [
        t_val for t_h, t_val in live_terms.items()
        if _is_term_in_role_room(t_val, slot_id)
    ]

    # Chỉ tái sử dụng nếu đúng slot_id này đã có handle sống; hoặc nếu là slot mặc định và room chỉ cho phép 1 agent
    if existing_handle and existing_handle in live_terms and _is_term_in_role_room(live_terms[existing_handle], slot_id):
        primary_h = existing_handle
        primary_tab = live_terms[existing_handle].get("tabId") or ""
    elif slot_id == target_room and capacity == 1 and room_matches:
        room_matches.sort(key=lambda x: x.get("lastOutputAt") or 0, reverse=True)
        primary_h = room_matches[0].get("handle") or ""
        primary_tab = room_matches[0].get("tabId") or ""
    else:
        primary_h = ""
        primary_tab = ""

    if primary_h:
        # Chỉ đóng các terminal vượt quá giới hạn ROOM_CAPACITIES
        room_matches.sort(key=lambda x: (1 if x.get("handle") == primary_h else 0, x.get("lastOutputAt") or 0), reverse=True)
        for m in room_matches[capacity:]:
            mh = m.get("handle")
            if mh and mh != primary_h:
                run_cmd(["orca", "terminal", "close", "--terminal", mh, "--tab", "--json"])
                live_terms.pop(mh, None)
        registry[slot_id] = {"handle": primary_h, "tabId": primary_tab, "room": target_room}
        save_registry(registry)
        print(f"  ⚡ {title} ({slot_id}) đã sẵn sàng (Handle: {primary_h}).")
        return primary_h

    prompt = AGENTS.get(slot_id, AGENTS.get(target_room, ""))
    print(f"--- 🚀 Đang khởi chạy: {title} ({slot_id}) ---")

    wt_target = "name:main" if target_room == "supervisor" else (f"name:room-{target_room}" if target_room in ("pm", "lead", "peer", "qc") else "active")

    launch_cmd = [
        "orca", "agent", "launch",
        "--worktree", wt_target,
        "--agent", "hermes",
        "--prompt", prompt,
        "--focus",
        "--json"
    ]
    # Hermes đọc model & effort trực tiếp từ ~/.hermes/config.yaml (Orca chặn --model đối với agent hermes)

    code, out = run_cmd(launch_cmd)

    handle = ""
    tab_id = ""
    if code == 0 and out:
        try:
            data = json.loads(out)
            outcome = data.get("result", {}).get("outcome", {})
            handle = outcome.get("handle") or ""
            pk = outcome.get("paneKey") or ""
            tab_id = pk.split(":")[0] if ":" in pk else pk
        except Exception:
            pass

    if handle:
        print(f"  ✅ Khởi chạy thành công: {handle} (Tab: {tab_id})")
        run_cmd(["orca", "terminal", "rename", "--terminal", handle, "--title", title, "--json"])
        run_cmd(["orca", "terminal", "set-pane-title", "--terminal", handle, "--title", title, "--json"])

        registry[slot_id] = {"handle": handle, "tabId": tab_id, "room": target_room}
        save_registry(registry)

        # Chỉ dọn dẹp các terminal không nằm trong danh sách các slot đã đăng ký hợp lệ và vượt quá ROOM_CAPACITIES
        current_terms = get_live_terminals()
        registered_room_handles = {
            info.get("handle")
            for k, info in registry.items()
            if isinstance(info, dict) and normalize_room(k) == target_room and info.get("handle")
        }
        room_live = [
            t_val for t_h, t_val in current_terms.items()
            if _is_term_in_role_room(t_val, slot_id)
        ]
        if len(room_live) > capacity:
            room_live.sort(
                key=lambda x: (1 if x.get("handle") in registered_room_handles else 0, x.get("lastOutputAt") or 0),
                reverse=True,
            )
            for extra in room_live[capacity:]:
                eh = extra.get("handle")
                if eh and eh != handle and eh not in registered_room_handles:
                    run_cmd(["orca", "terminal", "close", "--terminal", eh, "--tab", "--json"])
    else:
        print(f"  ⚠️  Không nhận được handle từ Orca cho agent {slot_id}.")

    time.sleep(1)
    return handle


def cmd_start(target_roles: list[str], launch_all: bool = False) -> int:
    if not ensure_orca_ready():
        return 1

    registry = load_registry()
    live_terms = get_live_terminals()

    print("======================================================================")
    print("⚡ [SLPPC MULTI-SLOT & RECURSIVE AGENT CONTROLLER] ⚡")
    print("======================================================================")

    if target_roles:
        roles_to_run = []
        for r in target_roles:
            nr = normalize_role(r)
            if nr not in roles_to_run:
                roles_to_run.append(nr)
    elif launch_all:
        roles_to_run = ALL_ROLES
    else:
        roles_to_run = PERSISTENT_ROLES
        print("💡 [SLPPC Architecture]: Mặc định khởi chạy Persistent Supervisor.")
        print("   Hỗ trợ mở song song nhiều slot: peer, peer2..4, peer_design, lead, lead2..3, qc, qc2..3, supervisor2..3.")

    for role in roles_to_run:
        if role not in AGENTS:
            print(f"⚠️  Không tìm thấy vai trò '{role}'. Các vai trò khả dụng: {', '.join(AGENTS.keys())}")
            continue
        launch_single(role, registry, live_terms)

    print("\n🎉 HOÀN TẤT KHỞI CHẠY!")
    cmd_status()
    return 0


def cmd_status() -> int:
    registry = load_registry()
    live_terms = get_live_terminals()

    hb_data: dict[str, dict] = {}
    if HB_FILE.exists():
        try:
            hb_data = json.loads(HB_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    print("\n📋 TRẠNG THÁI HIỆN TẠI CỦA 5 PHÒNG AGENT SLPPC:")
    print("──────────────────────────────────────────────────────────────────────────────────────────────────────────")
    print(f"{'VAI TRÒ (ROLE)':<34} | {'HANDLE':<24} | {'STATUS':<12} | {'MODEL':<24} | {'HEARTBEAT':<12}")
    print("──────────────────────────────────────────────────────────────────────────────────────────────────────────")

    for role in ALL_ROLES:
        title = TITLES.get(role, role)
        reg_info = registry.get(role, {})
        handle = reg_info.get("handle", "N/A")
        is_alive = handle in live_terms and _is_term_in_role_room(live_terms[handle], role)
        if not is_alive:
            # Quét trực tiếp theo worktree để không bao giờ bỏ sót terminal đang mở trong room
            room_matches = [t_val for t_val in live_terms.values() if _is_term_in_role_room(t_val, role)]
            if room_matches:
                room_matches.sort(key=lambda x: x.get("lastOutputAt") or 0, reverse=True)
                handle = room_matches[0].get("handle", "N/A")
                is_alive = True
                registry[role] = {"handle": handle, "tabId": room_matches[0].get("tabId") or ""}
            else:
                handle = "N/A"

        status_str = "🟢 ALIVE" if is_alive else "🔴 STOPPED"
        model = MODELS.get(role, "default")
        hb = hb_data.get(role, {}).get("status", "idle")
        hb_str = f"💓 {hb.upper()}" if is_alive else "—"

        print(f"{title:<34} | {handle:<24} | {status_str:<12} | {model:<24} | {hb_str:<12}")

    save_registry(registry)
    print("──────────────────────────────────────────────────────────────────────────────────────────────────────────")
    return 0


def cmd_stop(target_roles: list[str], stop_all: bool = False) -> int:
    registry = load_registry()
    live_terms = get_live_terminals()

    if stop_all:
        roles_to_stop = ALL_ROLES
    elif target_roles:
        roles_to_stop = [normalize_role(r) for r in target_roles]
    else:
        print("⚠️ Vui lòng chỉ định vai trò cần dừng, hoặc dùng --all để dừng toàn bộ.")
        return 1

    for role in roles_to_stop:
        title = TITLES.get(role, role)
        closed_handles = set()
        reg_info = registry.get(role)
        if reg_info:
            handle = reg_info.get("handle")
            if handle and handle in live_terms:
                print(f"🛑 Đang đóng {title} ({handle})...")
                run_cmd(["orca", "terminal", "close", "--terminal", handle, "--tab", "--json"])
                closed_handles.add(handle)
            registry.pop(role, None)

        # Đóng mọi terminal còn sót trong worktree của role
        for t_h, t_val in live_terms.items():
            if t_h not in closed_handles and _is_term_in_role_room(t_val, role):
                print(f"🛑 Đang đóng {title} ({t_h})...")
                run_cmd(["orca", "terminal", "close", "--terminal", t_h, "--tab", "--json"])
                closed_handles.add(t_h)

        if role in ("pm", "lead", "peer", "qc"):
            run_cmd(["orca", "terminal", "close", "--worktree", f"name:room-{role}", "--all", "--json"])

    save_registry(registry)
    print("✅ Đã hoàn tất đóng các tab được chỉ định.")
    return 0


def cmd_clear_ephemerals() -> int:
    """Đóng tất cả các sub-agent tạm thời (Peer, QC) để chống phình to Context."""
    print("🧹 [CONTEXT HYGIENE]: Đang dọn dẹp và đóng tất cả Sub-Agent tạm thời (Peer, QC)...")
    res = cmd_stop(EPHEMERAL_ROLES)
    if get_orca_ide_bin():
        try:
            subprocess.run(["python3", str(SCRIPT_DIR / "tools" / "zombie_reaper.py")], capture_output=True, text=True, timeout=5)
        except Exception:
            pass
    print("✨ Toàn bộ sub-agent tạm thời (Peer, QC) đã được đóng. Context đưa về trạng thái sạch sẽ, RAM đưa về 0.")
    return res


def cmd_restart(target_roles: list[str]) -> int:
    print("🔄 Đang khởi động lại các Agent...")
    cmd_stop(target_roles, stop_all=(not target_roles))
    time.sleep(2)
    return cmd_start(target_roles)


def main():
    parser = argparse.ArgumentParser(
        description="Agent Start & Manager CLI cho hệ thống 5-Room SLPPC (Supervisor, PM, Lead, Peer, QC).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  ./cli/agent-start                  Khởi chạy 3 Persistent Agents (Supervisor, PM, Lead)
  ./cli/agent-start clear            Đóng toàn bộ Sub-Agent tạm thời (Peer, QC)
  ./cli/agent-start pm               Khởi chạy riêng PM Agent
  ./cli/agent-start lead peer qc     Khởi chạy Lead, Peer và QC
  ./cli/agent-start status           Xem bảng trạng thái chi tiết 5 phòng
  ./cli/agent-start restart          Khởi động lại toàn bộ
  ./cli/agent-start stop --all       Đóng tất cả agent
"""
    )
    parser.add_argument("roles", nargs="*", help="Tên vai trò (supervisor, pm, lead, peer, qc, status, restart, stop, clear)")
    parser.add_argument("--status", action="store_true", help="Xem bảng trạng thái")
    parser.add_argument("--stop", action="store_true", help="Dừng agent")
    parser.add_argument("--all", action="store_true", help="Áp dụng cho tất cả agent")
    parser.add_argument("--restart", action="store_true", help="Khởi động lại")

    args = parser.parse_args()

    # Route subcommands passed as first positional arg
    if args.roles and args.roles[0].lower() in ("clear", "purge", "clean"):
        return cmd_clear_ephemerals()
    if args.roles and args.roles[0].lower() == "status":
        return cmd_status()
    if args.roles and args.roles[0].lower() == "restart":
        return cmd_restart(args.roles[1:])
    if args.roles and args.roles[0].lower() == "stop":
        return cmd_stop(args.roles[1:], stop_all=args.all)

    if args.status:
        return cmd_status()
    if args.restart:
        return cmd_restart(args.roles)
    if args.stop:
        return cmd_stop(args.roles, stop_all=args.all)

    # Default action: start
    return cmd_start(args.roles, launch_all=args.all)


if __name__ == "__main__":
    sys.exit(main())
