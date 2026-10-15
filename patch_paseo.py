import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path(os.environ.get("PASEO_CONFIG", Path.home() / ".paseo" / "config.json"))
PROFILES_DIR = Path(os.environ.get("PASEO_PROFILES_DIR", Path(__file__).resolve().parent / "profiles"))
PROFILE_FILES = ["supervisor.md", "lead.md", "peer.md", "qc.md"]
DEFAULT_IDS = {
    "Supervisor": "agent_profile_supervisor_slp",
    "Lead": "agent_profile_lead_slp",
    "Peer": "agent_profile_peer_slp",
    "QC": "agent_profile_qc_slpc",
}


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
                "provider": meta.get("provider", os.environ.get("PASEO_PROVIDER", "router9")),
                "model": model or "",
                "modeId": meta.get("modeId", "bypassPermissions"),
                "thinkingOptionId": meta.get("thinkingOptionId", "high"),
                "notes": body,
            }
            profiles.append(entry)

    mandatory_gate_marker = "MANDATORY RESEARCH & GENERATION GATE (TOOL-FIRST ENFORCEMENT)"
    global_research_gen_directive = (
        "MANDATORY RESEARCH & GENERATION GATE (TOOL-FIRST ENFORCEMENT):\n"
        "Whenever Paseo runs any profile (Supervisor, Lead, Peer, QC, Lead BA, Peer BA, Lead Dev, Peer Dev, Lead design, Peer Design), "
        "you MUST execute the workspace Research and Generation tools in `/home/baoltb/Desktop/Paseo_Project`:\n"
        "1. Unified Research & Gen Pipeline: `python3 /home/baoltb/Desktop/Paseo_Project/tools/profile_research_gen.py --profile \"<Role>\" --topic \"<Task>\" [--source <file>] [--task-id <id>]`\n"
        "2. Research Tools: `python3 /home/baoltb/Desktop/Paseo_Project/tools/research/research_agent.py \"<topic>\"`, "
        "`python3 /home/baoltb/Desktop/Paseo_Project/tools/query_reader.py <path> \"<query>\"`, "
        "`python3 /home/baoltb/Desktop/Paseo_Project/tools/crm_doc_reader.py \"<query>\" [--uc <UC>]`, "
        "and `python3 /home/baoltb/Desktop/Paseo_Project/tools/agent_progress.py find-thread \"<keyword>\"`.\n"
        "3. Sub-Agents (`031_claude_code_sub_agents`): `gemini-codebase-analyzer`, `strategic-reasoning-architect`, `slpc-qc-verifier`.\n"
        "4. Generation Tools: `python3 /home/baoltb/Desktop/Paseo_Project/tools/qc_test_generator.py --source <file> --spec <spec> --out-spec <spec_ts> --sync-harness`, "
        "`python3 /home/baoltb/Desktop/Paseo_Project/tools/distill_ba_beats.py`, "
        "`python3 /home/baoltb/Desktop/Paseo_Project/tools/harness_manager.py`, "
        "and `python3 /home/baoltb/Desktop/Paseo_Project/tools/agent_progress.py log --agent \"<Role>\" ...`."
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
        print(f"Updated {CONFIG_PATH} with SLPC profiles and Mandatory Research+Gen enforcement from {PROFILES_DIR}.")
    else:
        print(f"[dry-run] Would update {CONFIG_PATH} with {len(PROFILE_FILES)} SLPC profiles.")

    return data


if __name__ == "__main__":
    patch()

