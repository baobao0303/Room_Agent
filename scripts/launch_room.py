#!/usr/bin/env python3
"""
scripts/launch_room.py - Khởi chạy và liên kết 8 Agent Tabs trong Orca Workspace (SLPPC).
Hoạt động tương thích 100% trên cả macOS (Darwin arm64/x86) và Linux.
"""
from __future__ import annotations

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
    "pm": "[PM] Feasibility & Alignment",
    "lead": "[Lead Dev] Architect & PM",
    "peer": "[Peer Dev 1 - Low] Code Executor",
    "peer2": "[Peer Dev 2 - Medium] Code Executor",
    "peer3": "[Peer Dev 3 - High] Code Executor",
    "peer4": "[Peer Dev 4 - Extra] Code Executor",
    "design": "[Peer Design] UI/UX & Tokens",
    "qc": "[QC] 5-Stage ISTQB Verifier",
}

MODELS = {
    "pm": "ag/gemini-3.8-flash-high",
    "lead": "ag/gemini-3.8-flash-high",
    "peer": "ag/gemini-3.8-flash-low",
    "peer2": "ag/gemini-3.8-flash-medium",
    "peer3": "ag/gemini-3.8-flash-high",
    "peer4": "ag/gemini-3.8-flash-high",
    "design": "ag/gemini-3.8-flash-high",
    "qc": "ag/gemini-3.8-flash-high",
}

REASONINGS = {
    "pm": "high",
    "lead": "high",
    "peer": "low",
    "peer2": "medium",
    "peer3": "high",
    "peer4": "max",
    "design": "high",
    "qc": "high",
}


def run_cmd(args: list[str]) -> tuple[int, str]:
    try:
        res = subprocess.run(args, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        return res.returncode, res.stdout.strip()
    except Exception as exc:
        return 1, str(exc)


def main():
    print("=== [ORCA SLPC MULTI-AGENT ROOM LAUNCHER] ===")

    orca_bin = shutil.which("orca")
    if not orca_bin:
        print("⚠️  Lệnh 'orca' chưa có trong PATH. Hãy kiểm tra ~/.config/orca/linux-orca-cli-shim hoặc Orca Desktop.")
        sys.exit(1)

    print("🔍 Kiểm tra trạng thái Orca Runtime...")
    code, out = run_cmd(["orca", "status", "--json"])
    if code != 0:
        print("🚀 Đang mở Orca Desktop...")
        run_cmd(["orca", "open"])
        time.sleep(2)

    REG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if REG_FILE.exists():
        backup_path = REG_FILE.with_suffix(".json.bak")
        try:
            shutil.copy2(REG_FILE, backup_path)
        except Exception:
            pass

    registry: dict[str, dict[str, str]] = {}
    if REG_FILE.exists():
        try:
            registry = json.loads(REG_FILE.read_text(encoding="utf-8"))
        except Exception:
            registry = {}

    print("🚀 Bắt đầu khởi động các Agent Tabs...")

    # Khởi chạy các Agent thường trực (Supervisor, PM, Lead).
    # Các Sub-Agent (Peer, QC) là Ephemeral - kích hoạt tự động theo task on-demand.
    roles = ["pm", "lead"]
    for role in roles:
        prompt = AGENTS[role]
        title = TITLES[role]
        print(f"--- Khởi chạy: {title} ({role}) ---")

        code, out = run_cmd([
            "orca", "agent", "launch",
            "--worktree", "active",
            "--agent", "hermes",
            "--prompt", prompt,
            "--json"
        ])

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
            print(f"  ✅ Handle: {handle} (Tab: {tab_id})")
            run_cmd(["orca", "terminal", "rename", "--terminal", handle, "--title", title, "--json"])
            run_cmd(["orca", "terminal", "set-pane-title", "--terminal", handle, "--title", title, "--json"])
            run_cmd(["orca", "terminal", "send", "--terminal", handle, "--text", f"/title {title}", "--enter"])

            model = MODELS.get(role)
            if model:
                run_cmd(["orca", "terminal", "send", "--terminal", handle, "--text", f"/model {model}", "--enter"])

            reasoning = REASONINGS.get(role)
            if reasoning:
                run_cmd(["orca", "terminal", "send", "--terminal", handle, "--text", f"/reasoning {reasoning}", "--enter"])

            # Tự động nạp RTK (Rust Token Killer) Profile Environment để nén 60-90% token
            rtk_script = SCRIPT_DIR / "scripts" / "rtk_profile_env.sh"
            if rtk_script.is_file():
                run_cmd(["orca", "terminal", "send", "--terminal", handle, "--text", f"source {rtk_script} {role}", "--enter"])

            registry[role] = {"handle": handle, "tabId": tab_id}
            REG_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        else:
            print(f"  ⚠️  Agent {role} đã mở hoặc không trả handle mới.")

        time.sleep(1)

    # Detect and rename Supervisor handle
    code, out = run_cmd(["orca", "terminal", "list", "--json"])
    if code == 0 and out:
        try:
            data = json.loads(out)
            terms = data.get("result", {}).get("terminals", [])
            spawned_handles = {v.get("handle") for k, v in registry.items() if k != "supervisor"}
            for t in terms:
                sup_handle = t.get("handle")
                if sup_handle and sup_handle not in spawned_handles:
                    sup_title = "[Supervisor] Scope & Intent Guard"
                    registry["supervisor"] = {"handle": sup_handle, "tabId": t.get("tabId", "")}
                    run_cmd(["orca", "terminal", "rename", "--terminal", sup_handle, "--title", sup_title, "--json"])
                    run_cmd(["orca", "terminal", "set-pane-title", "--terminal", sup_handle, "--title", sup_title, "--json"])
                    REG_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
                    break
        except Exception:
            pass

    print("\n🎉 HOÀN TẤT KHỞI CHẠY MULTI-AGENT ROOM!")
    print(f"📋 Danh sách Agent hiện hành trong {REG_FILE.relative_to(SCRIPT_DIR)}:")
    print(json.dumps(registry, indent=2))


if __name__ == "__main__":
    main()
