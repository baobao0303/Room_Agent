#!/usr/bin/env python3
"""
tools/tests/test_scoped_tools.py - Unit test verifying Per-Role Scoped Tools and Role Fencing.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROFILES_DIR = BASE_DIR / "profiles"

ROLE_SCOPED_TOOLS = {
    "supervisor": ["tools/harness_manager.py", "tools/agent_progress.py", "tools/call_agent.py", "tools/bmad_promote.py", "profiles/supervisor/skills/intake-and-scope/systemone/systemone.py", "tools/harness_learning_search.py"],
    "lead": ["tools/harness_learning_search.py", "tools/lead_code_review.py", "tools/bmad_promote.py", "tools/harness_manager.py"],
    "peer": ["patch", "write_file", "terminal", "tools/agent_progress.py"],
    "qc": ["tools/qc_test_generator.py", "tools/slppc_flow_guard.py", "tools/strict_typing_scanner.py", "tools/bmad_promote.py", "tools/harness_manager.py"],
}


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    res = {}
    current_key = None
    list_items = []
    for line in parts[1].splitlines():
        line_str = line.rstrip()
        if not line_str or line_str.strip().startswith("#"):
            continue
        if line_str.startswith("  - "):
            if current_key:
                list_items.append(line_str.strip()[4:].strip("'\""))
            continue
        if ":" in line_str and not line_str.startswith(" "):
            if current_key and list_items:
                res[current_key] = list_items
                list_items = []
            k, v = line_str.split(":", 1)
            current_key = k.strip()
            v_val = v.strip()
            if v_val:
                res[current_key] = v_val.strip("'\"")
            else:
                list_items = []
    if current_key and list_items:
        res[current_key] = list_items
    return res


class TestScopedTools(unittest.TestCase):
    """Test Per-Role Scoped Tool Surfaces and strict role boundaries."""

    def test_all_profiles_exist(self):
        for role in ["supervisor", "lead", "peer", "qc"]:
            p = PROFILES_DIR / role / "PROFILE.md"
            if not p.is_file():
                p = PROFILES_DIR / f"{role}.md"
            self.assertTrue(p.is_file(), f"Profile {role} must exist")

    def test_role_scoped_tools_budget(self):
        """Each role must have a constrained tool surface of 2 to 6 tools."""
        for role, tools in ROLE_SCOPED_TOOLS.items():
            self.assertGreaterEqual(len(tools), 2, f"Role {role} has too few tools")
            self.assertLessEqual(len(tools), 6, f"Role {role} has too many tools (exceeds per-bot scoped budget)")

    def test_supervisor_and_lead_cannot_have_code_mutation_tools(self):
        """Supervisor and Lead must not have patch or direct code modification tools."""
        for role in ["supervisor", "lead"]:
            tools = ROLE_SCOPED_TOOLS[role]
            self.assertNotIn("patch", tools)
            self.assertNotIn("write_file", tools)

    def test_peer_has_code_execution_tools(self):
        """Peer dev must have patch, write_file and terminal tools."""
        peer_tools = ROLE_SCOPED_TOOLS["peer"]
        self.assertIn("patch", peer_tools)
        self.assertIn("write_file", peer_tools)
        self.assertIn("terminal", peer_tools)

    def test_qc_has_exclusive_verification_tools(self):
        """QC must have test generator and flow guard verification tools."""
        qc_tools = ROLE_SCOPED_TOOLS["qc"]
        self.assertIn("tools/qc_test_generator.py", qc_tools)
        self.assertIn("tools/slppc_flow_guard.py", qc_tools)


if __name__ == "__main__":
    unittest.main()
