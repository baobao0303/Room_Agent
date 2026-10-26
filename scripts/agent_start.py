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
        "[Supervisor] Scope, Intent Guard & Product Manager in SLPC (Enterprise AI 4-Pillar Spec). "
        "Chuyên trách quản trị phạm vi, đánh giá Feasibility & Alignment (Kev System One <50ms hoặc Heuristic), "
        "kiểm soát AC & trần vòng lặp (Turn Ceiling <= 3), tạo Epic/Task trên Harness DB, "
        "điều phối Lead, Peer, QC, kiểm soát EVOS Release Gate (>=98%) và bảo vệ Single-Ownership Invariant."
    ),
    "lead": (
        "[Lead Dev] Technical Architect & Reviewer (Enterprise AI 4-Pillar Spec). "
        "Chuyên trách kiến trúc, truy xuất Context-Bounded RAG (Top-3 chunks), phân rã task chuẩn Zero-Search (JSON Schema AgentHandoffEnvelope) và phản biện chéo (Cross-Critique)."
    ),
    "peer": (
        "[Peer Dev / Coder Agent] Code & UI Executor (Enterprise AI 4-Pillar Spec). "
        "Chuyên trách thực thi mã nguồn Full-Stack trên Working Memory tinh gọn (<30k tokens), ánh xạ Figma/TDS UI tokens và nộp Resolved theo JSON Schema của Lead."
    ),
    "qc": (
        "[QC / Tester & EVOS Verifier] 5-Stage ISTQB & Destructive Tester (Enterprise AI 4-Pillar Spec). "
        "Chuyên trách sinh test matrix, thực thi kiểm thử phá hoại (gửi Feedback/Retry Loop kèm Error Stack Trace nếu lỗi), chạy EVOS Engine (Pass Rate >= 98%) và độc quyền đóng task."
    ),
}

TITLES = {
    "supervisor": "[Supervisor] Scope, Intent & PM Guard",
    "lead": "[Lead Dev] Technical Architect",
    "peer": "[Peer Dev] Code & UI Executor",
    "qc": "[QC] 5-Stage ISTQB Verifier",
}

MODELS = {
    "supervisor": "ag/gemini-3.8-flash-high",
    "lead": "ag/gemini-3.8-flash-high",
    "peer": "ag/gemini-3.8-flash-high",
    "qc": "ag/gemini-3.8-flash-high",
}

REASONINGS = {
    "supervisor": "high",
    "lead": "high",
    "peer": "high",
    "qc": "high",
}

PERSISTENT_ROLES = ["supervisor"]
EPHEMERAL_ROLES = ["lead", "peer", "qc"]
ALL_ROLES = ["supervisor", "lead", "peer", "qc"]


def normalize_role(role: str) -> str:
    r = role.strip().lower()
    if r in ("peer1", "peer2", "peer3", "peer4", "peer_2", "peer_3", "peer_4", "design", "peer_design", "peer-dev"):
        return "peer"
    return r


def run_cmd(args: list[str]) -> tuple[int, str]:
    try:
        res = subprocess.run(args, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        return res.returncode, res.stdout.strip()
    except Exception as exc:
        return 1, str(exc)


def get_live_terminals() -> dict[str, dict]:
    """Lấy danh sách các terminal đang thực sự sống trong Orca Runtime."""
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
    if not shutil.which("orca"):
        print("❌ Lỗi: Lệnh 'orca' không có trong PATH. Hãy kiểm tra cài đặt Orca Desktop.", file=sys.stderr)
        return False
    code, _ = run_cmd(["orca", "status", "--json"])
    if code != 0:
        print("🚀 Đang khởi động Orca Desktop...")
        run_cmd(["orca", "open"])
        time.sleep(2)
    return True


def _is_term_in_role_room(t_val: dict, role: str) -> bool:
    wt_path = (t_val.get("worktreePath") or "").rstrip("/")
    branch = (t_val.get("branch") or "").rstrip("/")
    target_room = normalize_role(role)
    if target_room == "supervisor":
        return branch in ("main", "refs/heads/main") and "/room-" not in wt_path
    return wt_path.endswith(f"/room-{target_room}") or branch.endswith(f"room-{target_room}")


def launch_single(role: str, registry: dict[str, dict], live_terms: dict[str, dict]) -> str:
    """Khởi chạy 1 role nếu chưa có tab sống (đảm bảo tối đa 1 agent/room, tự động đóng tab trùng)."""
    role = normalize_role(role)
    title = TITLES.get(role, role)
    existing_handle = registry.get(role, {}).get("handle")

    room_matches = [
        t_val for t_h, t_val in live_terms.items()
        if _is_term_in_role_room(t_val, role)
    ]
    if existing_handle and existing_handle in live_terms and _is_term_in_role_room(live_terms[existing_handle], role):
        primary_h = existing_handle
        primary_tab = live_terms[existing_handle].get("tabId") or ""
    elif room_matches:
        room_matches.sort(key=lambda x: x.get("lastOutputAt") or 0, reverse=True)
        primary_h = room_matches[0].get("handle") or ""
        primary_tab = room_matches[0].get("tabId") or ""
    else:
        primary_h = ""
        primary_tab = ""

    if primary_h:
        # Đóng mọi terminal dư thừa trong cùng room (--tab)
        for m in room_matches:
            mh = m.get("handle")
            if mh and mh != primary_h:
                run_cmd(["orca", "terminal", "close", "--terminal", mh, "--tab", "--json"])
                live_terms.pop(mh, None)
        registry[role] = {"handle": primary_h, "tabId": primary_tab}
        save_registry(registry)
        print(f"  ⚡ {title} ({role}) đã sẵn sàng (Handle: {primary_h}).")
        return primary_h

    prompt = AGENTS[role]
    try:
        sys.path.insert(0, str(SCRIPT_DIR / "tools"))
        from agent_context_manager import build_rehydration_prompt  # type: ignore
        hydration_block = build_rehydration_prompt(role=role, user_id=os.environ.get("USER", "enterprise_user"), project_id="Room_Agent")
        prompt = f"{prompt}\n\n{hydration_block}"
    except Exception:
        pass

    print(f"--- 🚀 Đang khởi chạy: {title} ({role}) ---")

    target_room = normalize_role(role)
    wt_target = "name:main" if target_room == "supervisor" else (f"name:room-{target_room}" if target_room in ("pm", "lead", "peer", "qc") else "active")

    launch_cmd = [
        "orca", "agent", "launch",
        "--worktree", wt_target,
        "--agent", "hermes",
        "--prompt", prompt,
        "--surface", "terminal",
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

        registry[role] = {"handle": handle, "tabId": tab_id}
        save_registry(registry)

        # Dọn dẹp terminal shell mặc định hoặc dư thừa trong worktree (--tab)
        current_terms = get_live_terminals()
        for t_h, t_val in current_terms.items():
            if t_h != handle and _is_term_in_role_room(t_val, role):
                run_cmd(["orca", "terminal", "close", "--terminal", t_h, "--tab", "--json"])
    else:
        print(f"  ⚠️  Không nhận được handle từ Orca cho agent {role}.")

    time.sleep(1)
    return handle


def cmd_start(target_roles: list[str], launch_all: bool = False) -> int:
    if not ensure_orca_ready():
        return 1

    registry = load_registry()
    live_terms = get_live_terminals()

    print("======================================================================")
    print("⚡ [SLPPC 5-ROOM MULTI-AGENT - AGENT START CONTROLLER] ⚡")
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
        print("💡 [SLPPC Ephemeral Architecture]: Mặc định duy trì Persistent Supervisor (Context sạch, RAM nền = 0).")
        print("   Các vai trò Ephemeral (PM, Lead, Peer, QC) tự động kích hoạt on-demand kèm 3-Tier Dynamic Hydration (hoặc dùng --all).")

    for role in roles_to_run:
        if role not in AGENTS:
            print(f"⚠️  Không tìm thấy vai trò '{role}'. Các vai trò khả dụng: {', '.join(ALL_ROLES)}")
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
    if shutil.which("orca"):
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
