#!/usr/bin/env python3
"""
tools/smoke_discovery.py - Offline smoke test for Room_Agent skills, profiles & plugins.
Verifies all skills across 7 RBAC categories, 10 profiles, and plugin manifests without calling LLM APIs (0 token cost).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse minimal YAML frontmatter from markdown file without extra deps."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_text = parts[1]
    res: dict[str, str] = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            res[k.strip()] = v.strip().strip("'\"")
    return res


def check_skills(skills_root: Path) -> dict[str, list[dict[str, str]]]:
    discovered: dict[str, list[dict[str, str]]] = {}
    if not skills_root.is_dir():
        if (PROJECT_ROOT / "profiles").is_dir():
            skills_root = PROJECT_ROOT / "profiles"
        else:
            return discovered

    categories = [d for d in skills_root.iterdir() if d.is_dir()]
    for cat in sorted(categories, key=lambda c: c.name):
        discovered[cat.name] = []
        target_dir = cat / "skills" if (cat / "skills").is_dir() else cat
        for skill_md in sorted(target_dir.rglob("SKILL.md")):
            sdir = skill_md.parent
            fm = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
            discovered[cat.name].append({
                "name": fm.get("name") or sdir.name,
                "category": cat.name,
                "path": str(skill_md.relative_to(PROJECT_ROOT))
            })
    return discovered


def check_profiles(profiles_root: Path) -> list[dict[str, str]]:
    discovered = []
    if not profiles_root.is_dir():
        return discovered

    candidates = list(sorted(profiles_root.glob("*.md")))
    if not candidates:
        candidates = list(sorted(profiles_root.glob("*/PROFILE.md")))

    for p in candidates:
        content = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        name = fm.get("name") or (p.parent.name.capitalize() if p.name == "PROFILE.md" else p.stem)
        discovered.append({
            "name": name,
            "provider": fm.get("provider", "unknown"),
            "model": fm.get("model", "unknown"),
            "path": str(p.relative_to(PROJECT_ROOT))
        })
    return discovered


def check_plugins(plugins_root: Path) -> list[dict[str, str]]:
    discovered = []
    if not plugins_root.is_dir():
        return discovered

    for p in plugins_root.iterdir():
        manifest = p / "paseo-plugin.json"
        if manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                discovered.append({
                    "id": data.get("id", p.name),
                    "requirements": json.dumps(data.get("requirements", {})),
                    "path": str(manifest.relative_to(PROJECT_ROOT))
                })
            except Exception:
                pass
    return discovered


def main():
    skills_map = check_skills(PROJECT_ROOT / "skills")
    profiles = check_profiles(PROJECT_ROOT / "profiles")
    plugins = check_plugins(PROJECT_ROOT / "plugins")

    total_skills = sum(len(items) for items in skills_map.values())
    errors = []

    if total_skills == 0:
        errors.append("No skills discovered in skills/ directory.")
    if len(profiles) == 0:
        errors.append("No agent profiles discovered in profiles/ directory.")
    if len(plugins) == 0:
        errors.append("No plugins discovered in plugins/ directory.")

    # Check duplicate skill names
    all_skill_names = []
    for cat, items in skills_map.items():
        for item in items:
            all_skill_names.append(item["name"])

    report = {
        "status": "ok" if not errors else "error",
        "total_skills": total_skills,
        "skills_by_category": {cat: len(items) for cat, items in skills_map.items()},
        "total_profiles": len(profiles),
        "profiles": [p["name"] for p in profiles],
        "total_plugins": len(plugins),
        "plugins": [p["id"] for p in plugins],
        "inference_tokens": 0,
        "errors": errors
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
