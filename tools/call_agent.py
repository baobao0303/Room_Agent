#!/usr/bin/env python3
"""
tools/call_agent.py - Dispatcher for Supervisor to call Paseo agent profiles.
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

CONFIG_PATH = Path.home() / ".paseo" / "config.json"

def get_profiles():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    profiles = data.get("daemon", {}).get("agentProfiles", [])
    return {p["name"].lower(): p for p in profiles}

def main():
    parser = argparse.ArgumentParser(description="Call or wake up a Paseo agent profile.")
    parser.add_argument("--profile", required=True, help="Profile name (e.g. Lead, Peer, Lead Dev, etc.)")
    parser.add_argument("--prompt", required=True, help="Task description or prompt for the agent")
    parser.add_argument("--item-id", type=int, help="Harness Work Item ID (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    profiles = get_profiles()
    key = args.profile.strip().lower()
    profile = profiles.get(key)

    if not profile:
        # Partial match
        matches = [p for name, p in profiles.items() if key in name]
        if len(matches) == 1:
            profile = matches[0]
        else:
            print(f"Error: Profile '{args.profile}' not found.")
            print(f"Available profiles: {', '.join(p['name'] for p in profiles.values())}")
            sys.exit(1)

    profile_name = profile["name"]
    provider = profile.get("provider", "router9")
    model = profile.get("model", "ag/claude-sonnet-5-5-medium")
    mode = profile.get("modeId", "bypassPermissions")
    thinking = profile.get("thinkingOptionId", "high")
    instructions = profile.get("notes", "")

    task_body = args.prompt
    if args.item_id:
        task_body = f"[Harness Item #{args.item_id}] {task_body}"

    full_prompt = f"{instructions}\n\n=== TASK ASSIGNMENT ===\n{task_body}" if instructions else task_body
    title = f"{profile_name}: {task_body[:40]}"

    cmd = [
        "paseo", "run", "-d",
        "--title", title,
        "--provider", provider,
        "--model", model,
        "--mode", mode,
        "--thinking", thinking,
        full_prompt
    ]

    if args.dry_run:
        print("Dry run command:", " ".join(cmd[:10]), "...")
        sys.exit(0)

    print(f"Calling {profile_name} ({provider}/{model})...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Success: {profile_name} spawned.")
        if res.stdout.strip():
            print(res.stdout.strip())
    else:
        print(f"Failed to spawn {profile_name}: {res.stderr.strip()}", file=sys.stderr)
        sys.exit(res.returncode)

if __name__ == "__main__":
    main()
