import os
import sys
import json
import subprocess
from pathlib import Path

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

print("=== SETUP PASEO & HERMES SKILLS ===")

home = Path.home()

print("[1] Clone repositories...")
if not (home / "hermes-profiles").exists():
    run_cmd(f"git clone https://github.com/magnus919/hermes-profiles.git {home / 'hermes-profiles'}")
if not (home / "storage-skills").exists():
    run_cmd(f"git clone https://github.com/hoangnb24/storage.git {home / 'storage-skills'}")

print("[2] Link skills...")
skills_dir = home / ".hermes" / "skills"
skills_dir.mkdir(parents=True, exist_ok=True)
run_cmd(f"ln -sf {home}/hermes-profiles/skills/* {skills_dir}/")
run_cmd(f"ln -sf {home}/storage-skills/* {skills_dir}/")

print("[3] Setup Paseo config.json...")
paseo_config = home / ".paseo" / "config.json"
paseo_config.parent.mkdir(parents=True, exist_ok=True)

if not paseo_config.exists():
    with open(paseo_config, "w") as f:
        json.dump({"daemon": {"agentProfiles": []}}, f)

with open(paseo_config, "r") as f:
    data = json.load(f)

if "daemon" not in data:
    data["daemon"] = {}
if "agentProfiles" not in data["daemon"]:
    data["daemon"]["agentProfiles"] = []

profiles = data["daemon"]["agentProfiles"]

# Fetch original patch_paseo.py logic for prompts
# Using fixed prompts to ensure it works offline
supervisor_prompt = "Room role: Supervisor (Scope & Intent Guard).\\n..."
lead_prompt = "Room role: Lead (Technical Architect & Project Manager).\\n..."
peer_prompt = "Room role: Peer (Execution, Engineering, QA, Content).\\n..."

# Instead of repeating prompts in python, I will just copy them from the existing file.
