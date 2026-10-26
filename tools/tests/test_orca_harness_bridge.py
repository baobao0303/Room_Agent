#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import tools.orca_harness_bridge as ohb


class TestOrcaHarnessBridge(unittest.TestCase):
    def test_state_map(self):
        self.assertEqual(ohb.STATE_MAP.get("New"), "todo")
        self.assertEqual(ohb.STATE_MAP.get("Active"), "in-progress")
        self.assertEqual(ohb.STATE_MAP.get("Resolved"), "in-review")
        self.assertEqual(ohb.STATE_MAP.get("Closed"), "completed")
        self.assertEqual(ohb.STATE_MAP.get("Removed"), "removed")

    def test_sync_state_no_orca(self):
        with patch("shutil.which", return_value=None):
            with patch("subprocess.run") as mock_run:
                ohb.sync_state_to_orca("123", "Active")
                mock_run.assert_not_called()

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_sync_state_active(self, mock_run, _mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")
        ohb.sync_state_to_orca("456", "Active", "active")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("orca", args)
        self.assertIn("--workspace-status", args)
        self.assertIn("in-progress", args)

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_sync_state_removed_custom_worktree(self, mock_run, _mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            task_dir = tmp_root / "bmad" / "rooms" / "tasks" / "789"
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / "handoff.md").write_text("content", encoding="utf-8")

            with patch.object(ohb, "PROJECT_ROOT", tmp_root):
                ohb.sync_state_to_orca("789", "Removed", "wt-custom")

            archive_dir = tmp_root / "bmad" / "rooms" / "archive" / "task_789_removed"
            self.assertTrue(archive_dir.exists())
            self.assertFalse(task_dir.exists())

        args = mock_run.call_args_list[0][0][0]
        self.assertEqual(args[:4], ["orca", "worktree", "rm", "--worktree"])

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_launch_agent_on_board(self, mock_run, _mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")
        ohb.launch_agent_on_board("hermes", "Implement auth", task_id="101", worktree="active")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[:3], ["orca", "agent", "launch"])
        self.assertIn("[WI-#101] Implement auth", args)

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_spawn_hierarchical_subagent(self, mock_run, _mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")
        ohb.spawn_hierarchical_subagent("99", "peer", "Sub task title", "Detailed spec")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[:3], ["orca", "orchestration", "worker-start"])
        self.assertIn("--parent", args)
        self.assertIn("99", args)


if __name__ == "__main__":
    unittest.main()
