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
    parser = argparse.ArgumentParser(description="Call or wake up a Paseo agent profile (with automatic Research & Gen pipeline).")
    parser.add_argument("--profile", required=True, help="Profile name (e.g. Supervisor, Lead, Peer, QC, Lead BA, Lead Dev, etc.)")
    parser.add_argument("--prompt", required=True, help="Task description or prompt for the agent")
    parser.add_argument("--item-id", type=int, help="Harness Work Item ID (optional)")
    parser.add_argument("--source", help="Optional target source file to auto-generate 5-Stage ISTQB unit tests")
    parser.add_argument("--spec", help="Optional spec file path")
    parser.add_argument("--uc", help="Optional Use Case code (e.g. UC1.01)")
    parser.add_argument("--skip-pre-gen", action="store_true", help="Skip automatic pre-spawn Research & Gen execution")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    profiles = get_profiles()
    key = args.profile.strip().lower()
    profile = profiles.get(key)

    if not profile:
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

    pre_gen_block = ""
    if not args.skip_pre_gen:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import profile_research_gen as prg
            pipeline_res = prg.execute_pipeline(
                profile=profile_name,
                topic=args.prompt,
                source_file=args.source,
                spec_file=args.spec,
                task_id=args.item_id,
                uc_code=args.uc,
                sync_harness=bool(args.item_id),
            )
            gen_list = "\n".join(f"  - `/home/baoltb/Desktop/Paseo_Project/{f}`" for f in pipeline_res.get("generated_files", []))
            pre_gen_block = (
                "\n\n=== AUTO-GENERATED RESEARCH & GEN ARTIFACTS (MANDATORY READ FIRST) ===\n"
                f"Pre-pipeline (`tools/profile_research_gen.py`) has already executed Research & Gen for `{profile_name}`:\n"
                f"{gen_list}\n"
                "You MUST read the generated Research Report & Execution Brief above, use `tools/query_reader.py` / "
                "`tools/research/research_agent.py` for any additional lookup, use `tools/qc_test_generator.py` / "
                "`tools/distill_ba_beats.py` / `tools/harness_manager.py` for generation, and log your result via "
                "`python3 tools/agent_progress.py log`."
            )
        except Exception as exc:
            print(f"[Warning] Pre-pipeline Research+Gen notice: {exc}", file=sys.stderr)

    task_body = args.prompt
    if args.item_id:
        task_body = f"[Harness Item #{args.item_id}] {task_body}"

    full_prompt = f"{instructions}{pre_gen_block}\n\n=== TASK ASSIGNMENT ===\n{task_body}" if instructions else f"{pre_gen_block}\n\n{task_body}"
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
        if pre_gen_block:
            print(pre_gen_block)
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

