from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = Path(os.environ.get("PASEO_CONFIG", Path.home() / ".paseo" / "config.json"))
PROFILES_DIR = Path(os.environ.get("PASEO_PROFILES_DIR", PROJECT_ROOT / "profiles"))
PROFILE_FILES = ["supervisor.md", "lead.md", "peer.md", "qc.md"]
DEFAULT_IDS = {
    "Supervisor": "agent_profile_supervisor_slp",
    "Lead": "agent_profile_lead_slp",
    "Peer": "agent_profile_peer_slp",
    "QC": "agent_profile_qc_slpc",
}

DEFAULT_DEPARTMENT_PROFILES = [
    {
        "id": "agent_profile_lead_ba",
        "name": "Lead BA",
        "provider": "antigravity",
        "model": "gemini-4-argon-high",
        "modeId": "full-access",
        "thinkingOptionId": "high",
        "notes": (
            "Room role: Lead BA (Business Analyst Lead).\n"
            "Own business requirement analysis, User Stories, Use Cases (UC), and Acceptance Criteria (AC) in `docs/spec/<project>/ba/`.\n"
            "Coordinate with Lead Design and Lead Dev via Harness DB."
        ),
    },
    {
        "id": "agent_profile_peer_ba",
        "name": "Peer BA",
        "provider": "antigravity",
        "model": "gemini-4-argon-high",
        "modeId": "full-access",
        "thinkingOptionId": "high",
        "notes": (
            "Room role: Peer BA (Business Analyst Executor).\n"
            "Execute bounded BA tasks assigned by Lead BA, extract atomic requirement beats (`tools/distill_ba_beats.py`), and write specs in `docs/spec/<project>/ba/`."
        ),
    },
    {
        "id": "agent_profile_lead_design",
        "name": "Lead design",
        "provider": "antigravity",
        "model": "gemini-4-argon-high",
        "modeId": "full-access",
        "thinkingOptionId": "high",
        "notes": (
            "Room role: Lead Design (UI/UX & Design System Architect).\n"
            "Own UI/UX architecture, Figma token mapping (`tds-ui-figma`), and component specs in `docs/spec/<project>/design/`."
        ),
    },
    {
        "id": "agent_profile_peer_design",
        "name": "Peer Design",
        "provider": "antigravity",
        "model": "gemini-4-argon-high",
        "modeId": "full-access",
        "thinkingOptionId": "high",
        "notes": (
            "Room role: Peer Design (UI/UX Design Executor).\n"
            "Execute bounded Figma-to-TDS UI component and token mapping tasks in `docs/spec/<project>/design/`."
        ),
    },
    {
        "id": "agent_profile_lead_dev",
        "name": "Lead Dev",
        "provider": "antigravity",
        "model": "gemini-4-argon-high",
        "modeId": "full-access",
        "thinkingOptionId": "high",
        "notes": (
            "Room role: Lead Dev (Technical Architect & Dev Lead).\n"
            "Own technical architecture, API contracts (`docs/spec/<project>/dev/`), task breakdown, and code review before merge."
        ),
    },
    {
        "id": "agent_profile_peer_dev",
        "name": "Peer Dev",
        "provider": "antigravity",
        "model": "gemini-4-argon-high",
        "modeId": "full-access",
        "thinkingOptionId": "high",
        "notes": (
            "Room role: Peer Dev (Software Engineer Executor).\n"
            "Implement assigned tasks in Angular 18 / Nx / TDS UI, write unit tests, and transition completed tasks to `Resolved` for QC verification."
        ),
    },
]


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


def parse_profile(path: Path):
    content = path.read_text(encoding="utf-8")
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2].lstrip("\r\n")
    return meta, body


def patch():
    dry_run = "--dry-run" in sys.argv

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"daemon": {"agentProfiles": []}}
    else:
        data = {"daemon": {"agentProfiles": []}}

    profiles = data.setdefault("daemon", {}).setdefault("agentProfiles", [])
    providers = data.setdefault("agents", {}).setdefault("providers", {})

    backup_path = CONFIG_PATH.parent / "config.json.bak-pre-codex-room"
    if backup_path.exists():
        try:
            bak_data = json.loads(backup_path.read_text(encoding="utf-8"))
            bak_providers = bak_data.get("agents", {}).get("providers", {})
            for prov_key in ("router9", "servre"):
                if prov_key in bak_providers and prov_key not in providers:
                    prov_cfg = dict(bak_providers[prov_key])
                    prov_cfg["paseoTools"] = {"enabled": False}
                    providers[prov_key] = prov_cfg
            bak_profiles = bak_data.get("daemon", {}).get("agentProfiles", [])
            existing_names = {p.get("name") for p in profiles if isinstance(p, dict)}
            for bp in bak_profiles:
                if isinstance(bp, dict) and bp.get("name") not in existing_names:
                    profiles.append(bp)
                    existing_names.add(bp.get("name"))
        except Exception:
            pass

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
                "provider": meta.get("provider", os.environ.get("PASEO_PROVIDER", "antigravity")),
                "model": model or "gemini-4-argon-high",
                "modeId": meta.get("modeId", "full-access"),
                "thinkingOptionId": meta.get("thinkingOptionId", "high"),
                "notes": body,
            }
            profiles.append(entry)

    existing_by_name = {p.get("name"): p for p in profiles if isinstance(p, dict)}
    for dept_prof in DEFAULT_DEPARTMENT_PROFILES:
        existing = existing_by_name.get(dept_prof["name"])
        if existing is not None:
            existing["provider"] = dept_prof["provider"]
            existing["model"] = dept_prof["model"]
            existing["modeId"] = dept_prof["modeId"]
            existing["thinkingOptionId"] = dept_prof["thinkingOptionId"]
        else:
            profiles.append(dict(dept_prof))
            existing_by_name[dept_prof["name"]] = profiles[-1]

    mandatory_gate_marker = "MANDATORY RESEARCH & GENERATION GATE (TOOL-FIRST ENFORCEMENT)"
    global_research_gen_directive = (
        "MANDATORY RESEARCH & GENERATION GATE (TOOL-FIRST ENFORCEMENT):\n"
        "Whenever Paseo runs any profile (Supervisor, Lead, Peer, QC, Lead BA, Peer BA, Lead Dev, Peer Dev, Lead design, Peer Design), "
        f"you MUST execute the workspace Research and Generation tools in `{PROJECT_ROOT}`:\n"
        f"1. Unified Research & Gen Pipeline: `python3 {PROJECT_ROOT}/tools/profile_research_gen.py --profile \"<Role>\" --topic \"<Task>\" [--source <file>] [--task-id <id>]`\n"
        f"2. Research Tools: `python3 {PROJECT_ROOT}/tools/research/research_agent.py \"<topic>\"`, "
        f"`python3 {PROJECT_ROOT}/tools/query_reader.py <path> \"<query>\"`, "
        f"`python3 {PROJECT_ROOT}/tools/crm_doc_reader.py \"<query>\" [--uc <UC>]`, "
        f"and `python3 {PROJECT_ROOT}/tools/agent_progress.py find-thread \"<keyword>\"`.\n"
        "3. Sub-Agents (`031_claude_code_sub_agents`): `gemini-codebase-analyzer`, `strategic-reasoning-architect`, `slpc-qc-verifier`.\n"
        f"4. Generation Tools: `python3 {PROJECT_ROOT}/tools/qc_test_generator.py --source <file> --spec <spec> --out-spec <spec_ts> --sync-harness`, "
        f"`python3 {PROJECT_ROOT}/tools/distill_ba_beats.py`, "
        f"`python3 {PROJECT_ROOT}/tools/harness_manager.py`, "
        f"and `python3 {PROJECT_ROOT}/tools/agent_progress.py log --agent \"<Role>\" ...`."
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
        print(f"Updated {CONFIG_PATH} with {len(profiles)} Paseo profiles and Mandatory Research+Gen enforcement from {PROFILES_DIR}.")
        paseo_bin = find_paseo_bin()
        if paseo_bin:
            res = subprocess.run([paseo_bin, "reload", "--json"], capture_output=True, text=True, check=False, timeout=15)
            if res.returncode == 0:
                print(f"Reloaded Paseo daemon live config via {paseo_bin}.")
    else:
        print(f"[dry-run] Would update {CONFIG_PATH} with {len(profiles)} Paseo profiles.")

    return data


if __name__ == "__main__":
    patch()

