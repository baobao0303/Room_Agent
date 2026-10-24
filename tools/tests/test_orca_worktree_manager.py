#!/usr/bin/env python3
"""
tools/tests/test_orca_worktree_manager.py - Unit test suite for Orca Worktree Review Gate.
"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

BASE_DIR = Path(__file__).resolve().parent.parent.parent
from tools import orca_worktree_manager


class TestOrcaWorktreeManager(unittest.TestCase):
    def test_01_slugify(self):
        slug = orca_worktree_manager.slugify("Kiểm tra bộ lọc người dùng CRM #123")
        self.assertIn("kiem-tra", slug)
        self.assertNotIn(" ", slug)
        self.assertNotIn("#", slug)

    @patch("tools.orca_worktree_manager.run_cmd")
    def test_02_get_orca_worktrees_parsing(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"result": {"worktrees": [{"displayName": "task-4706-filter", "comment": "Harness WI #4706"}]}}',
            stderr=""
        )
        wts = orca_worktree_manager.get_orca_worktrees()
        self.assertEqual(len(wts), 1)
        self.assertEqual(wts[0]["displayName"], "task-4706-filter")

    @patch("tools.orca_worktree_manager.get_orca_worktrees")
    def test_03_find_task_worktree(self, mock_get):
        mock_get.return_value = [
            {"displayName": "main-wt", "isMainWorktree": True, "comment": ""},
            {"displayName": "task-4706-filter", "comment": "Harness WI #4706 [Active]", "git": {"branch": "peer/task-4706"}}
        ]
        wt = orca_worktree_manager.find_task_worktree(4706)
        self.assertIsNotNone(wt)
        self.assertEqual(wt["displayName"], "task-4706-filter")

    @patch("tools.orca_worktree_manager.find_task_worktree")
    @patch("tools.orca_worktree_manager.run_cmd")
    @patch("tools.orca_worktree_manager.send_desktop_notification")
    def test_04_mark_ready_for_user_review(self, mock_notif, mock_run, mock_find):
        mock_find.return_value = {"id": "wt-id", "displayName": "task-4706-filter"}
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        ok = orca_worktree_manager.mark_ready_for_user_review(4706, "PASS 100%")
        self.assertTrue(ok)
        mock_notif.assert_called_once()


if __name__ == "__main__":
    unittest.main()
