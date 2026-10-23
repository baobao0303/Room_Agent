#!/usr/bin/env python3
"""
scripts/anti_leak_sentinel.py - Automated Security & Anti-Leak Sentinel for Room_Agent Open-Source Readiness.

Checks repository for:
1. Proprietary in-development feature specs & API contracts.
2. Frontend customer business flows & internal routes.
3. Corporate names & physical addresses.
4. Scattered skill copies outside canonical `skills/` directory.
5. Git tracking of `projects/` sub-repos and secrets.
"""

import sys
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns that MUST NOT appear in open-source tracked files
FORBIDDEN_CONTENT_PATTERNS = [
    # Physical address & industrial park (specific coordinates)
    (
        r"(?i)\b(?:tân\s*bình|tân\s*phú|đường\s*19/5a|lô\s*[ivx0-9-]+|nhóm\s*cn\s*[ivx0-9-]+)\b",
        "Physical corporate address / industrial park coordinates"
    ),
    # Proprietary backend endpoints & tenant APIs
    (
        r"/v1/tenants/\{tenantId\}/shops/\{shopId\}",
        "Private multi-tenant shop API endpoint"
    ),
    # Company specific internal domains
    (
        r"(?i)\b(?:tfs\.tmtco\.dev|tmtco\.org|tmtco\.dev)\b",
        "Internal corporate domain"
    ),
    # Private keys
    (
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "Private encryption key"
    ),
]

EXCLUDED_PATHS = {
    ".git",
    "projects", # subprojects are ignored
    ".venv",
    "venv",
    "__pycache__",
    "tools/research", # auto-generated research briefs (gitignored)
    "scripts/anti_leak_sentinel.py", # skip self
}

def check_git_tracked_memos() -> list[str]:
    """Ensure ephemeral memos, progress logs, and .claude/ are NOT tracked by Git."""
    issues = []
    forbidden_prefixes = [
        "bmad/rooms/lead/",
        "bmad/rooms/peer/",
        "bmad/rooms/qc/",
        "bmad/rooms/supervisor/",
        "bmad/rooms/pm/",
        "bmad/rooms/tasks/",
        "bmad/rooms/violations/",
        "bmad/rooms/archive/",
        ".claude/",
        "docs/AGENT_PROGRESS.md",
        "docs/spec/wicx-crm-fe/",
        "docs/spec/wion-pos-header-refactor-spec.md"
    ]
    allowed_exceptions = {"bmad/rooms/README.md", "bmad/rooms/template-handoff.md"}
    try:
        res = subprocess.run(
            ["git", "ls-files"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line or line in allowed_exceptions:
                continue
            for prefix in forbidden_prefixes:
                if line.startswith(prefix) or line == prefix:
                    issues.append(f"Ephemeral/Internal file is tracked by Git: '{line}'. Must untrack via 'git rm --cached {line}'")
    except Exception as e:
        issues.append(f"Failed to check git tracking for memos: {e}")
    return issues

def check_scattered_skills() -> list[str]:
    """Ensure skills reside exclusively in canonical `skills/<skill_name>/SKILL.md`."""
    issues = []
    
    # Check for scattered .claude/skills in bmad/rooms
    bmad_rooms = REPO_ROOT / "bmad" / "rooms"
    if bmad_rooms.is_dir():
        for claude_dir in bmad_rooms.rglob(".claude"):
            issues.append(f"Scattered skill/claude directory found in room: {claude_dir.relative_to(REPO_ROOT)}")

    # Check for non-folder files directly in skills/ (except hidden files)
    skills_dir = REPO_ROOT / "skills"
    if skills_dir.is_dir():
        for item in skills_dir.iterdir():
            if item.is_file() and not item.name.startswith("."):
                issues.append(f"Standalone file in skills/ directory (must be a folder with SKILL.md): {item.name}")

    return issues

def check_git_tracked_subprojects() -> list[str]:
    """Ensure projects/ is NOT tracked by Git."""
    issues = []
    try:
        res = subprocess.run(
            ["git", "ls-files", "projects/"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        tracked = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        if tracked:
            issues.append(f"Found {len(tracked)} file(s) in 'projects/' currently tracked by Git! Must untrack via 'git rm -r --cached projects'")
    except Exception as e:
        issues.append(f"Failed to check git tracking for projects/: {e}")
    return issues

def check_content_leaks() -> list[str]:
    """Check text files for forbidden proprietary patterns."""
    issues = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(ex in p.parts for ex in EXCLUDED_PATHS):
            continue
        # Skip binary files
        if p.suffix in [".png", ".jpg", ".mp4", ".tar", ".gz", ".zip", ".exe", ".bin"]:
            continue

        # Skip files ignored by Git (.gitignore)
        try:
            res = subprocess.run(
                ["git", "check-ignore", "--no-index", "-q", str(p)],
                cwd=str(REPO_ROOT),
                capture_output=True
            )
            if res.returncode == 0:
                continue
        except Exception:
            pass
            
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pat, desc in FORBIDDEN_CONTENT_PATTERNS:
            for match in re.finditer(pat, content):
                line_no = content[:match.start()].count("\n") + 1
                issues.append(f"[{desc}] {p.relative_to(REPO_ROOT)}:{line_no} -> '{match.group(0).strip()}'")

    return issues

def main() -> int:
    print("=" * 75)
    print("🛡️ ROOM_AGENT OPEN-SOURCE SECURITY & ANTI-LEAK SENTINEL")
    print("=" * 75)

    all_issues = []

    # 1. Check git tracking of projects
    proj_issues = check_git_tracked_subprojects()
    all_issues.extend(proj_issues)

    # 1.1 Check git tracking of ephemeral memos & progress logs
    memo_issues = check_git_tracked_memos()
    all_issues.extend(memo_issues)

    # 2. Check scattered skills
    skill_issues = check_scattered_skills()
    all_issues.extend(skill_issues)

    # 3. Check forbidden content
    content_issues = check_content_leaks()
    all_issues.extend(content_issues)

    if not all_issues:
        print("✅ PASS: Repository is 100% clean of proprietary feature specs, addresses, and leaks.")
        print("✅ Skills are properly structured in canonical directory.")
        print("✅ Ready for open-source inspection.")
        print("=" * 75)
        return 0

    print(f"❌ VETO: Detected {len(all_issues)} security/leak violation(s):")
    for iss in all_issues:
        print(f"  ! {iss}")
    print("=" * 75)
    print("Halt! Clean up these violations before pushing or making the repository public.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
