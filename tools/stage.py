#!/usr/bin/env python3
"""
tools/stage.py - Stage Room_Agent skills, profiles & tools into an isolated sandbox.
Never overwrites or installs globally.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def stage(target_dir: str | Path) -> Path:
    target = Path(target_dir).expanduser().resolve()
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing existing destination: {target}")
    if not target.parent.is_dir():
        raise ValueError("Destination parent directory must already exist")

    target.mkdir(parents=True)
    try:
        # 1. Stage canonical skills
        skills_dest = target / "skills"
        skills_src = PROJECT_ROOT / "skills"
        if skills_src.is_dir():
            shutil.copytree(skills_src, skills_dest)
        elif (PROJECT_ROOT / "profiles").is_dir():
            skills_dest.mkdir(parents=True, exist_ok=True)
            for role_dir in (PROJECT_ROOT / "profiles").iterdir():
                role_skills = role_dir / "skills"
                if role_skills.is_dir():
                    shutil.copytree(role_skills, skills_dest / role_dir.name)

        # 2. Stage profiles
        profiles_dest = target / "profiles"
        profiles_src = PROJECT_ROOT / "profiles"
        if profiles_src.is_dir():
            shutil.copytree(profiles_src, profiles_dest)

        # 3. Stage plugins
        plugins_dest = target / "plugins"
        plugins_src = PROJECT_ROOT / "plugins"
        if plugins_src.is_dir():
            shutil.copytree(plugins_src, plugins_dest)

        # 4. Stage bmad room structure
        bmad_dest = target / "bmad" / "rooms"
        bmad_dest.mkdir(parents=True, exist_ok=True)
        for room in ("supervisor", "pm", "lead", "peer", "qc", "tasks", "archive", "violations"):
            (bmad_dest / room).mkdir(parents=True, exist_ok=True)

        # 5. Copy protocol
        protocol_src = PROJECT_ROOT / "docs" / "WORKSPACE_PROTOCOL.md"
        if not protocol_src.is_file():
            protocol_src = PROJECT_ROOT / "WORKSPACE_PROTOCOL.md"
        if protocol_src.is_file():
            (target / "docs").mkdir(parents=True, exist_ok=True)
            shutil.copy2(protocol_src, target / "docs" / "WORKSPACE_PROTOCOL.md")
            shutil.copy2(protocol_src, target / "WORKSPACE_PROTOCOL.md")

    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise

    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("new_workspace", help="Path to new isolated test workspace")
    args = parser.parse_args()
    dest = stage(args.new_workspace)
    print(f"✅ Successfully staged isolated sandbox: {dest}")


if __name__ == "__main__":
    main()
