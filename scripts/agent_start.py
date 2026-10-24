#!/usr/bin/env python3
"""
scripts/agent_start.py - All-in-One CLI để quản lý, khởi chạy và giám sát các Agent SLPPC.

Sử dụng:
  ./agent-start                 Khởi chạy toàn bộ phòng multi-agent (idempotent, không mở trùng)
  ./agent-start <role>          Khởi chạy một agent cụ thể (pm, lead, peer, peer2, peer3, peer4, design, qc)
  ./agent-start status          Xem trạng thái chi tiết của tất cả các Agent và nhịp tim
  ./agent-start restart         Khởi động lại toàn bộ các Agent
  ./agent-start stop [role]     Đóng tab của agent (hoặc tất cả nếu dùng --all)
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
    "pm": (
        "[PM Agent] Product Manager & Decision Arbiter in SLPPC. "
        "Chuyên trách đánh giá Feasibility và Alignment qua Kev System One (<50ms), "
        "kiểm soát AC và kiểm tra bẫy lỗi cũ từ Harness Learn."
    ),
    "lead": (
        "[Lead Dev] Architect & PM. "
        "Chuyên trách kiến trúc, phân rã task và review code qua 5 tiêu chí."
    ),
    "peer": (
        "[Peer Dev 1] Code Executor. "
        "Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ),
    "peer2": (
        "[Peer Dev 2] Code Executor. "
        "Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ),
    "peer3": (
        "[Peer Dev 3] Code Executor. "
        "Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ),
    "peer4": (
        "[Peer Dev 4] Code Executor. "
        "Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ),
    "design": (
        "[Peer Design] UI/UX & Tokens. "
        "Chuyên trách tra cứu token TDS, Figma node mapping, SCSS/CSS design tokens."
    ),
    "qc": (
        "[QC] 5-Stage ISTQB Verifier. "
        "Chuyên trách sinh test matrix, nghiệm thu độc lập và đóng task."
    ),
}

TITLES = {
    "supervisor": "[Supervisor] Scope & Intent Guard",
    "pm": "[PM] Feasibility & Alignment",
    "lead": "[Lead Dev] Architect & PM",
    "peer": "[Peer Dev 1] Code Executor",
    "peer2": "[Peer Dev 2] Code Executor",
    "peer3": "[Peer Dev 3] Code Executor",
    "peer4": "[Peer Dev 4] Code Executor",
    "design": "[Peer Design] UI/UX & Tokens",
    "qc": "[QC] 5-Stage ISTQB Verifier",
}

MODELS = {
    "supervisor": "ag/gemini-3.8-flash-high",
    "pm": "ag/gemini-3.8-flash-high",
    "lead": "ag/gemini-3.8-flash-high",
    "peer": "ag/gemini-3.8-flash-medium",
    "peer2": "ag/gemini-3.8-flash-low",
    "peer3": "ag/gemini-3.8-flash-high",
    "peer4": "ag/gemini-4-argon-high",
    "design": "ag/gemini-3.8-flash-high",
    "qc": "ag/gemini-3.8-flash-high",
}

REASONINGS = {
    "supervisor": "high",
    "pm": "high",
    "lead": "high",
    "peer": "medium",
    "peer2": "low",
    "peer3": "high",
    "peer4": "high",
    "design": "high",
    "qc": "high",
}

PERSISTENT_ROLES = ["supervisor", "pm", "lead"]
ALL_ROLES = ["supervisor", "pm", "lead", "peer", "peer2", "peer3", "peer4", "design", "qc"]


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


def launch_single(role: str, registry: dict[str, dict], live_terms: dict[str, dict]) -> str:
    """Khởi chạy 1 role nếu chưa có tab sống."""
    existing_handle = registry.get(role, {}).get("handle")
    if existing_handle and existing_handle in live_terms:
        title = TITLES.get(role, role)
        print(f"  ⚡ {title} ({role}) đã sẵn sàng (Handle: {existing_handle}).")
        return existing_handle

    prompt = AGENTS[role]
    title = TITLES.get(role, role)
    print(f"--- 🚀 Đang khởi chạy: {title} ({role}) ---")

    wt_target = "name:main" if role == "supervisor" else (f"name:room-{role}" if role in ("pm", "lead", "peer", "qc") else "active")
    model = MODELS.get(role)
    effort = REASONINGS.get(role)

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

        # Dọn dẹp terminal shell mặc định trong worktree nếu có tab thừa
        current_terms = get_live_terminals()
        for t_h, t_val in current_terms.items():
            if t_h != handle:
                wt_path = t_val.get("worktreePath", "").rstrip("/")
                is_target_wt = (wt_path == str(SCRIPT_DIR).rstrip("/")) if role == "supervisor" else wt_path.endswith(f"/room-{role}")
                if is_target_wt and not any(v.get("handle") == t_h for k, v in registry.items() if k != role):
                    run_cmd(["orca", "terminal", "close", "--terminal", t_h, "--json"])
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
    print("⚡ [SLPPC MULTI-AGENT ROOM - AGENT START CONTROLLER] ⚡")
    print("======================================================================")

    if target_roles:
        roles_to_run = [r.lower() for r in target_roles]
    elif launch_all:
        roles_to_run = ALL_ROLES
    else:
        roles_to_run = PERSISTENT_ROLES
        print("💡 [SLPPC Architecture]: Mặc định khởi chạy các tab thường trực (Supervisor, PM, Lead Dev).")
        print("   Các vai trò Peer 1..4, Design, QC kích hoạt tự động theo task on-demand (hoặc dùng --all).")

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

    print("\n📋 TRẠNG THÁI HIỆN TẠI CỦA CÁC AGENT:")
    print("──────────────────────────────────────────────────────────────────────────────────────────────────────────")
    print(f"{'VAI TRÒ (ROLE)':<22} | {'HANDLE':<24} | {'STATUS':<12} | {'MODEL':<24} | {'HEARTBEAT':<12}")
    print("──────────────────────────────────────────────────────────────────────────────────────────────────────────")

    all_check = ALL_ROLES
    for role in all_check:
        title = TITLES.get(role, role)
        reg_info = registry.get(role, {})
        handle = reg_info.get("handle", "N/A")
        is_alive = handle in live_terms

        status_str = "🟢 ALIVE" if is_alive else "🔴 STOPPED"
        model = MODELS.get(role, "default")
        hb = hb_data.get(role, {}).get("status", "idle")
        hb_str = f"💓 {hb.upper()}" if is_alive else "—"

        print(f"{title:<22} | {handle:<24} | {status_str:<12} | {model:<24} | {hb_str:<12}")

    print("──────────────────────────────────────────────────────────────────────────────────────────────────────────")
    return 0


def cmd_stop(target_roles: list[str], stop_all: bool = False) -> int:
    registry = load_registry()
    live_terms = get_live_terminals()

    if stop_all:
        roles_to_stop = ALL_ROLES
    elif target_roles:
        roles_to_stop = [r.lower() for r in target_roles]
    else:
        print("⚠️ Vui lòng chỉ định vai trò cần dừng, hoặc dùng --all để dừng toàn bộ.")
        return 1

    for role in roles_to_stop:
        reg_info = registry.get(role)
        if not reg_info:
            continue
        handle = reg_info.get("handle")
        if handle and handle in live_terms:
            title = TITLES.get(role, role)
            print(f"🛑 Đang đóng {title} ({handle})...")
            run_cmd(["orca", "terminal", "close", "--terminal", handle, "--json"])
            registry.pop(role, None)

    save_registry(registry)
    print("✅ Đã hoàn tất đóng các tab được chỉ định.")
    return 0


def cmd_clear_ephemerals() -> int:
    """Đóng tất cả các sub-agent tạm thời (Peer, Design, QC) để chống phình to Context."""
    ephemeral_roles = ["peer", "peer2", "peer3", "peer4", "design", "qc"]
    print("🧹 [CONTEXT HYGIENE]: Đang dọn dẹp và đóng tất cả Sub-Agent tạm thời để chống phình to context...")
    res = cmd_stop(ephemeral_roles)
    if shutil.which("orca"):
        try:
            subprocess.run(["python3", str(SCRIPT_DIR / "tools" / "zombie_reaper.py")], capture_output=True, text=True, timeout=5)
        except Exception:
            pass
    print("✨ Toàn bộ sub-agent tạm thời đã được đóng. Context đưa về trạng thái sạch sẽ, RAM đưa về 0.")
    return res


def cmd_restart(target_roles: list[str]) -> int:
    print("🔄 Đang khởi động lại các Agent...")
    cmd_stop(target_roles, stop_all=(not target_roles))
    time.sleep(2)
    return cmd_start(target_roles)


def main():
    parser = argparse.ArgumentParser(
        description="Agent Start & Manager CLI cho phòng Multi-Agent SLPPC.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  ./agent-start                  Khởi chạy toàn bộ phòng multi-agent (PM, Lead thường trực)
  ./agent-start clear            Đóng toàn bộ Sub-Agent (Peer, QC) để chống phình to Context
  ./agent-start pm               Khởi chạy riêng PM Agent
  ./agent-start lead peer qc     Khởi chạy Lead, Peer 1 và QC
  ./agent-start status           Xem bảng trạng thái chi tiết
  ./agent-start restart          Khởi động lại toàn bộ
  ./agent-start stop --all       Đóng tất cả agent
"""
    )
    parser.add_argument("roles", nargs="*", help="Tên vai trò (pm, lead, peer, peer2, peer3, peer4, design, qc, status, restart, stop, clear)")
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
