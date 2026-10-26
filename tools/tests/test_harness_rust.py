#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import tools.harness_rust as hr


class TestHarnessRust(unittest.TestCase):
    def test_supervise_task_fallback_tiny(self):
        bridge = hr.HarnessRustBridge(bin_path=Path("/non/existent/bin"))
        self.assertFalse(bridge.is_available())

        res = bridge.supervise_task("Update readme and fix typo")
        self.assertEqual(res.decision, "green")
        self.assertEqual(res.risk_lane, "tiny")
        self.assertEqual(res.status, "fallback")
        self.assertFalse(res.requires_human_review)

    def test_supervise_task_fallback_red(self):
        bridge = hr.HarnessRustBridge(bin_path=Path("/non/existent/bin"))
        res = bridge.supervise_task("rm -rf all database in prod")
        self.assertEqual(res.decision, "red")
        self.assertEqual(res.risk_lane, "high-risk")
        self.assertTrue(res.requires_human_review)

    @patch("subprocess.run")
    def test_supervise_task_with_mock_binary(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"decision":"green","risk_lane":"tiny","confidence":0.95,"requires_human_review":false,"suggested_route":"automated_pipeline","explanation":"Safe task"}',
        )
        with patch.object(hr.HarnessRustBridge, "is_binary_available", return_value=True):
            bridge = hr.HarnessRustBridge()
            res = bridge.supervise_task("Safe task description")
            self.assertEqual(res.decision, "green")
            self.assertEqual(res.risk_lane, "tiny")
            self.assertEqual(res.confidence, 0.95)
            self.assertEqual(res.status, "success")


if __name__ == "__main__":
    unittest.main()
