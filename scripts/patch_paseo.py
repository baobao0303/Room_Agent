#!/usr/bin/env python3
"""
scripts/patch_paseo.py - Đồng bộ 5 Hồ sơ Vai trò chuẩn SLPPC (Supervisor, PM, Lead, Peer, QC) vào ~/.paseo/config.json.
Tự động dọn dẹp các profile phân mảnh cũ (Peer Dev 1..4, Peer Design, Lead BA, Peer BA...).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(os.environ.get("PASEO_CONFIG", Path.home() / ".paseo" / "config.json"))
PROFILES_DIR = Path(os.environ.get("PASEO_PROFILES_DIR", PROJECT_ROOT / "profiles"))

PROFILE_FILES = [
    "supervisor.md",
    "pm.md",
    "lead.md",
    "peer.md",
    "qc.md",
]

DEFAULT_IDS = {
    "Supervisor": "agent_profile_supervisor_slp",
    "PM Agent": "agent_profile_pm_slp",
    "PM": "agent_profile_pm_slp",
    "Lead": "agent_profile_lead_slp",
    "Peer": "agent_profile_peer_slp",
    "QC": "agent_profile_qc_slpc",
}

LEGACY_PROFILE_NAMES = {
    "Peer Dev 1 (Low)",
    "Peer Dev 2",
    "Peer Dev 2 (Medium)",
    "Peer Dev 3",
    "Peer Dev 3 (High)",
    "Peer Dev 4",
    "Peer Dev 4 (Extra High)",
    "Peer Design",
    "Lead BA",
    "Peer BA",
    "Lead design",
    "Lead Design",
    "Lead Dev",
    "Peer Dev",
    "Security Sentinel",
    "Security",
}


def find_paseo_bin() -> str | None:
    which_paseo = shutil.which("paseo")
    if which_paseo:
        return which_paseo
    for candidate in (
        Path.home() / ".local" / "bin" / "paseo",
        Path("/Applications/Paseo.app/Contents/Resources/bin/paseo"),
    ):
        if candidate.exists():
            return str(candidate)
    return None


def parse_profile(path: Path) -> tuple[dict[str, str], str]:
    content = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line and not line.startswith(" "):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2].lstrip("\r\n")
    return meta, body


def patch() -> dict:
    dry_run = "--dry-run" in sys.argv

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"daemon": {"agentProfiles": []}}
    else:
        data = {"daemon": {"agentProfiles": []}}

    raw_profiles = data.setdefault("daemon", {}).setdefault("agentProfiles", [])
    canonical_names = {"Supervisor", "PM", "PM Agent", "Lead", "Peer", "QC"}
    # Chỉ giữ lại đúng 5 profile chuẩn SLPPC (loại bỏ mọi biến thể Peer Dev 1..4, Peer Design, Lead BA...)
    profiles = [
        p for p in raw_profiles
        if isinstance(p, dict) and p.get("name") in canonical_names
    ]
    data["daemon"]["agentProfiles"] = profiles

    for filename in PROFILE_FILES:
        md_path = PROFILES_DIR / filename
        if not md_path.exists():
            continue
        meta, body = parse_profile(md_path)
        name = meta.get("name", md_path.stem.capitalize())
        model = meta.get("model")

        found = False
        for p in profiles:
            if p.get("name") == name:
                p["notes"] = body
                if model:
                    p["model"] = model
                for key in ("provider", "modeId", "thinkingOptionId"):
                    if key in meta:
                        p[key] = meta[key]
                found = True
                break

        if not found:
            entry = {
                "id": meta.get("id", DEFAULT_IDS.get(name, f"agent_profile_{name.lower()}_slp")),
                "name": name,
                "provider": meta.get("provider", os.environ.get("PASEO_PROVIDER", "linux-prod")),
                "model": model or "ag/gemini-3.8-flash-high",
                "modeId": meta.get("modeId", "full-access"),
                "thinkingOptionId": meta.get("thinkingOptionId", "high"),
                "notes": body,
            }
            profiles.append(entry)

    mandatory_gate_marker = "MANDATORY RESEARCH & GENERATION GATE (TOOL-FIRST ENFORCEMENT)"
    global_research_gen_directive = (
        "MANDATORY RESEARCH & GENERATION GATE (TOOL-FIRST ENFORCEMENT):\n"
        "Whenever Paseo runs any SLPPC profile (Supervisor, PM, Lead, Peer, QC), "
        "you MUST execute the workspace Research and Generation tools:\n"
        "1. Unified Research & Gen Pipeline: `python3 tools/profile_research_gen.py --profile \"<Role>\" --topic \"<Task>\" [--source <file>] [--task-id <id>]`\n"
        "2. Research Tools: `python3 tools/research/research_agent.py \"<topic>\"`, "
        "`python3 tools/query_reader.py <path> \"<query>\"`, "
        "and `python3 tools/agent_progress.py find-thread \"<keyword>\"`.\n"
        "3. Generation & Governance Tools: `python3 tools/qc_test_generator.py`, "
        "`python3 tools/harness_manager.py`, "
        "and `python3 tools/agent_progress.py log --agent \"<Role>\" ...`."
    )

    data["pluginsEnabled"] = True
    daemon_cfg = data.setdefault("daemon", {})
    daemon_cfg["enableTerminalAgentHooks"] = True
    daemon_cfg["appendSystemPrompt"] = global_research_gen_directive

    for p in profiles:
        if not isinstance(p, dict):
            continue
        notes = p.get("notes", "") or ""
        if mandatory_gate_marker not in notes:
            p["notes"] = notes.rstrip() + "\n\n" + global_research_gen_directive + "\n"

    if not dry_run:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Đã đồng bộ {len(profiles)} Profiles chuẩn SLPPC (Supervisor, PM, Lead, Peer, QC) vào {CONFIG_PATH}.")
        paseo_bin = find_paseo_bin()
        if paseo_bin:
            res = subprocess.run([paseo_bin, "reload", "--json"], capture_output=True, text=True, check=False, timeout=15)
            if res.returncode == 0:
                print(f"  ✅ Đã reload Paseo daemon qua {paseo_bin}.")
    else:
        print(f"[dry-run] Would update {CONFIG_PATH} with {len(profiles)} Paseo profiles.")

    return data


if __name__ == "__main__":
    patch()
