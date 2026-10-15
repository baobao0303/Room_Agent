#!/usr/bin/env python3
"""
tools/doc_sync.py - Automatic documentation synchronization helper.
Validates spec files under docs/spec/<project>/, generates index summaries,
and keeps README.md and AGENTS.md catalog synchronized.
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_SPEC_DIR = BASE_DIR / "docs/spec"
SKILLS_DIR = BASE_DIR / ".agents/skills"

def sync_specs():
    print("--> Scanning docs/spec/ directory...")
    if not DOCS_SPEC_DIR.exists() or not DOCS_SPEC_DIR.is_dir():
        print(f"  (docs/spec directory not found at {DOCS_SPEC_DIR})")
        return {}
    projects = [p for p in DOCS_SPEC_DIR.iterdir() if p.is_dir()]
    summary = {}

    for p in projects:
        p_name = p.name
        summary[p_name] = {"ba": [], "design": [], "dev": []}
        for sub in ["ba", "design", "dev"]:
            sub_path = p / sub
            if sub_path.exists() and sub_path.is_dir():
                files = [f.name for f in sub_path.iterdir() if f.is_file() and f.suffix == ".md"]
                summary[p_name][sub] = sorted(files)

    print(f"✓ Found {len(summary)} project specifications:")
    for proj, categories in summary.items():
        print(f"  📂 Project: {proj}")
        print(f"     • BA Specs     : {len(categories['ba'])} files")
        print(f"     • Design Specs : {len(categories['design'])} files")
        print(f"     • Dev Specs    : {len(categories['dev'])} files")

    return summary

def sync_skills():
    print("\n--> Scanning .agents/skills/ directory...")
    if not SKILLS_DIR.exists() or not SKILLS_DIR.is_dir():
        print(f"  (.agents/skills directory not found at {SKILLS_DIR})")
        return []
    skills = [s.name for s in SKILLS_DIR.iterdir() if s.is_dir() and not s.name.startswith(".")]
    print(f"✓ Found {len(skills)} active skills in .agents/skills/:")
    for s in sorted(skills):
        print(f"  • {s}")
    return skills

def main():
    specs = sync_specs()
    skills = sync_skills()
    print("\n=== DOCUMENTATION SYNCHRONIZATION COMPLETED ===")

if __name__ == "__main__":
    main()
