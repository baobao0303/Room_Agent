#!/usr/bin/env python3
"""
tools/tests/test_agent_scanner.py - Unit test suite for native agent process scanner.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys_path = str(BASE_DIR / "tools")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from agent_scanner import detect_agents, sync_to_terminals_registry  # type: ignore


class TestAgentScanner(unittest.TestCase):
    """Test process signature detection and registry sync."""

    def test_detect_agents_mock(self):
        mock_procs = [
            {"pid": 1001, "ppid": 1, "args": "hermes sessions run --profile supervisor"},
            {"pid": 1002, "ppid": 1, "args": "claude --profile peer_dev"},
            {"pid": 1003, "ppid": 1, "args": "codex-supervisor start"},
            {"pid": 1004, "ppid": 1, "args": "grep -rn foo ."},  # Normal process, should be ignored
        ]

        detected = detect_agents(mock_procs)
        self.assertEqual(len(detected), 3)
        kinds = [d["kind"] for d in detected]
        self.assertIn("hermes", kinds)
        self.assertIn("claude-code", kinds)
        self.assertIn("codex", kinds)

    def test_inferred_roles(self):
        mock_procs = [
            {"pid": 2001, "ppid": 1, "args": "hermes run --role supervisor"},
            {"pid": 2002, "ppid": 1, "args": "claude peer_dev code"},
            {"pid": 2003, "ppid": 1, "args": "hermes qc_test_verifier"},
        ]
        detected = detect_agents(mock_procs)
        role_map = {d["kind"]: d["inferred_role"] for d in detected}
        self.assertEqual(role_map.get("claude-code"), "peer")

    def test_live_scan_does_not_crash(self):
        detected = detect_agents()
        self.assertIsInstance(detected, list)


if __name__ == "__main__":
    unittest.main()
