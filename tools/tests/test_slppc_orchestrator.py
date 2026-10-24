#!/usr/bin/env python3
"""
tools/tests/test_slppc_orchestrator.py - Unit Test Suite for Autonomous SLPPC Orchestrator.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PLUGIN_DIR = BASE_DIR / "plugins" / "slpc-lifecycle-hooks"
sys.path.insert(0, str(PLUGIN_DIR))
sys.path.insert(0, str(BASE_DIR / "tools"))
sys.path.insert(0, str(BASE_DIR))

from slppc_orchestrator import SlppcOrchestrator  # type: ignore


class TestSlppcOrchestrator(unittest.TestCase):
    """Test suite for autonomous state navigation in SLPPC."""

    def setUp(self):
        self.orch = SlppcOrchestrator(BASE_DIR)

    def test_registry_operations(self):
        reg = self.orch.get_terminals_registry()
        self.assertIsInstance(reg, dict)
        self.assertIn("supervisor", reg)

    def test_feasibility_evaluation_structure(self):
        eval_res = self.orch.evaluate_feasibility("Sample task for testing")
        self.assertIn("feasibility_score", eval_res)
        self.assertIn("alignment", eval_res)
        self.assertIn("risk_lane", eval_res)
        self.assertGreaterEqual(eval_res["feasibility_score"], 0.0)

    @patch.object(SlppcOrchestrator, "send_terminal_safely", return_value=True)
    def test_supervisor_ended_flow(self, mock_send):
        res = self.orch.handle_supervisor_ended({})
        self.assertEqual(res.get("stage"), "supervisor_to_pm_lead")
        self.assertIn("evaluation", res)
        # Check decision memo created
        memo_path = BASE_DIR / "bmad" / "rooms" / "pm" / "decision_memo.md"
        self.assertTrue(memo_path.is_file())

    @patch.object(SlppcOrchestrator, "send_terminal_safely", return_value=True)
    def test_pm_ended_flow(self, mock_send):
        res = self.orch.handle_pm_ended({})
        self.assertEqual(res.get("stage"), "pm_to_lead")

    def test_unmapped_role_route(self):
        res = self.orch.route_turn_ended("unknown_role")
        self.assertEqual(res.get("stage"), "unmapped")

    def test_cli_orchestrate_command(self):
        hook_py = PLUGIN_DIR / "paseo_hooks.py"
        res = subprocess.run(
            [sys.executable, str(hook_py), "orchestrate", "--role", "supervisor", "--json"],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
        )
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get("stage"), "supervisor_to_pm_lead")


if __name__ == "__main__":
    unittest.main()
