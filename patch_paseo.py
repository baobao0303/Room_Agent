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

    if not dry_run:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {CONFIG_PATH} with SLPC profiles from {PROFILES_DIR}.")
    else:
        print(f"[dry-run] Would update {CONFIG_PATH} with {len(PROFILE_FILES)} SLPC profiles.")

    return data


if __name__ == "__main__":
    patch()
