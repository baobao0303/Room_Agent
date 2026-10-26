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

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("tools.orca_worktree_manager.run_cmd")
    def test_02_get_orca_worktrees_parsing(self, mock_run, mock_which):
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

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("tools.orca_worktree_manager.find_task_worktree")
    @patch("tools.orca_worktree_manager.run_cmd")
    @patch("tools.orca_worktree_manager.send_desktop_notification")
    def test_04_mark_ready_for_user_review(self, mock_notif, mock_run, mock_find, mock_which):
        mock_find.return_value = {"id": "wt-id", "displayName": "task-4706-filter"}
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        ok = orca_worktree_manager.mark_ready_for_user_review(4706, "PASS 100%")
        self.assertTrue(ok)
        mock_notif.assert_called_once()


    @patch("tools.orca_worktree_manager.HarnessManager.get_work_item", return_value=None)
    @patch("tools.orca_worktree_manager.run_cmd")
    def test_05_approve_refuses_when_task_not_found(self, mock_run, mock_get_item):
        """Verify approve_and_merge_worktree refuses when task ID not found in Harness DB."""
        ok = orca_worktree_manager.approve_and_merge_worktree(99999)
        self.assertFalse(ok)
        # Verify zero git commands called
        mock_run.assert_not_called()

    @patch("tools.orca_worktree_manager.HarnessManager.get_work_item")
    @patch("tools.orca_worktree_manager.run_cmd")
    def test_06_approve_refuses_when_task_not_resolved(self, mock_run, mock_get_item):
        """Verify approve_and_merge_worktree refuses without touching git when state is not Resolved."""
        for unapproved_state in ["Active", "New", "Blocked", "Closed"]:
            mock_get_item.return_value = {"id": 1234, "state": unapproved_state, "title": "Test Task"}
            mock_run.reset_mock()

            ok = orca_worktree_manager.approve_and_merge_worktree(1234)
            self.assertFalse(ok, f"Expected refusal for state '{unapproved_state}'")
            # Verify ZERO git commands are called (Zero-Git-Touch Guarantee)
            mock_run.assert_not_called()

    @patch("tools.orca_worktree_manager.HarnessManager.get_work_item")
    @patch("tools.orca_worktree_manager.HarnessManager.update_state")
    @patch("tools.orca_worktree_manager.find_task_worktree")
    @patch("tools.orca_worktree_manager.record_review_intervention")
    @patch("tools.orca_worktree_manager.run_cmd")
    @patch("tools.orca_worktree_manager.send_desktop_notification")
    def test_07_approve_previews_diff_and_merges_when_resolved(
        self, mock_notif, mock_run, mock_rec_int, mock_find, mock_up_state, mock_get_item
    ):
        """Verify approve previews diffstat and merges with --no-ff when task is Resolved."""
        mock_get_item.return_value = {"id": 5555, "state": "Resolved", "title": "Ready Task"}
        mock_find.return_value = {
            "id": "wt-5555",
            "displayName": "task-5555-feature",
            "git": {"branch": "peer/task-5555"}
        }

        # Mock run_cmd responses
        def side_effect(cmd, **kwargs):
            if cmd[:3] == ["git", "diff", "--stat"]:
                return MagicMock(returncode=0, stdout=" file1.py | 2 +-\n 1 file changed, 1 insertion(+), 1 deletion(-)\n", stderr="")
            if cmd[:3] == ["git", "merge", "--no-ff"]:
                return MagicMock(returncode=0, stdout="Merge made by the 'ort' strategy.", stderr="")
            if cmd[:3] == ["git", "branch", "-d"]:
                return MagicMock(returncode=0, stdout="Deleted branch peer/task-5555.", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        mock_run.side_effect = side_effect

        ok = orca_worktree_manager.approve_and_merge_worktree(5555, actor="lead_reviewer", reason="LGTM")
        self.assertTrue(ok)

        # Verify diffstat was executed
        diff_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["git", "diff"]]
        self.assertTrue(len(diff_calls) >= 1, "Expected git diff --stat to be called before merge")

        # Verify git merge --no-ff was executed
        merge_calls = [c for c in mock_run.call_args_list if c[0][0][:3] == ["git", "merge", "--no-ff"]]
        self.assertEqual(len(merge_calls), 1)

        # Verify intervention was recorded
        mock_rec_int.assert_called_once_with(task_id=5555, action="approve", actor="lead_reviewer", reason="LGTM")

        # Verify task was updated to Closed with QC profile
        mock_up_state.assert_called_once_with(5555, "Closed", assigned_to_profile="qc")

    @patch("tools.orca_worktree_manager.HarnessManager.record_intervention")
    def test_08_approve_records_intervention_row(self, mock_record):
        """Verify record_review_intervention logs approve action correctly."""
        ok = orca_worktree_manager.record_review_intervention(
            task_id=777,
            action="approve",
            actor="supervisor",
            reason="Architecture and tests verified"
        )
        self.assertTrue(ok)
        mock_record.assert_called_once_with(
            target_type="work_item",
            target_id=777,
            actor="supervisor",
            reason="Architecture and tests verified",
            action="approve"
        )

    @patch("tools.orca_worktree_manager.find_task_worktree")
    @patch("tools.orca_worktree_manager.record_review_intervention")
    @patch("tools.orca_worktree_manager.send_desktop_notification")
    def test_09_reject_records_intervention_row(self, mock_notif, mock_rec_int, mock_find):
        """Verify reject_worktree records intervention and writes feedback."""
        mock_find.return_value = {"id": "wt-999", "displayName": "task-999"}

        ok = orca_worktree_manager.reject_worktree(999, reason="Needs additional edge case tests", actor="qa_lead")
        self.assertTrue(ok)
        mock_rec_int.assert_called_once_with(
            task_id=999,
            action="reject",
            actor="qa_lead",
            reason="Needs additional edge case tests"
        )

    def test_10_cli_exit_codes_and_argument_forwarding(self):
        """Verify CLI parser parses --actor and --reason properly."""
        import sys
        from unittest.mock import patch

        test_args = ["orca_worktree_manager.py", "approve", "1234", "--actor", "alice", "--reason", "Approved manually"]
        with patch.object(sys, "argv", test_args):
            with patch("tools.orca_worktree_manager.approve_and_merge_worktree", return_value=True) as mock_approve:
                try:
                    orca_worktree_manager.main()
                except SystemExit as e:
                    self.assertEqual(e.code, 0)
                mock_approve.assert_called_once_with("1234", actor="alice", reason="Approved manually")

    @patch("tools.orca_worktree_manager.HarnessManager.get_work_item")
    @patch("tools.orca_worktree_manager.find_task_worktree")
    @patch("tools.orca_worktree_manager.run_cmd")
    def test_11_merge_conflict_aborts_cleanly(self, mock_run, mock_find, mock_get_item):
        """Verify approve_and_merge_worktree calls git merge --abort when merge conflicts occur."""
        mock_get_item.return_value = {"id": 6666, "state": "Resolved", "title": "Conflicting Task"}
        mock_find.return_value = {
            "id": "wt-6666",
            "displayName": "task-6666-conflict",
            "git": {"branch": "peer/task-6666"}
        }

        def side_effect(cmd, **kwargs):
            if cmd[:3] == ["git", "diff", "--stat"]:
                return MagicMock(returncode=0, stdout=" conflict.py | 1 +\n", stderr="")
            if cmd[:3] == ["git", "merge", "--no-ff"]:
                return MagicMock(returncode=1, stdout="", stderr="CONFLICT (content): Merge conflict in conflict.py")
            if cmd[:3] == ["git", "rev-parse", "-q"]:
                return MagicMock(returncode=0, stdout="dummy_merge_head\n", stderr="")
            if cmd[:3] == ["git", "merge", "--abort"]:
                return MagicMock(returncode=0, stdout="", stderr="")
            if cmd[:3] == ["git", "merge", "--ff-only"]:
                return MagicMock(returncode=1, stdout="", stderr="fatal: Not possible to fast-forward, aborting.")
            return MagicMock(returncode=0, stdout="", stderr="")

        mock_run.side_effect = side_effect

        ok = orca_worktree_manager.approve_and_merge_worktree(6666)
        self.assertFalse(ok)

        # Verify git merge --abort was invoked
        abort_calls = [c for c in mock_run.call_args_list if c[0][0][:3] == ["git", "merge", "--abort"]]
        self.assertGreaterEqual(len(abort_calls), 1, "Expected git merge --abort to be called on conflict")

    def test_12_merge_conflict_real_git_cleanup(self):
        """Integration test: Real git merge conflict leaves no active MERGE_HEAD in repository."""
        import subprocess
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "checkout", "-B", "main"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo_path, check=True)
            subprocess.run(["git", "config", "user.email", "tester@example.com"], cwd=repo_path, check=True)

            target_file = repo_path / "app.py"
            target_file.write_text("print('base')\n", encoding="utf-8")
            subprocess.run(["git", "add", "app.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "initial commit"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "checkout", "-b", "peer/task-9001"], cwd=repo_path, check=True, capture_output=True)
            target_file.write_text("print('branch edit')\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "branch edit"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            target_file.write_text("print('main edit')\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "main edit"], cwd=repo_path, check=True, capture_output=True)

            db_path = str(repo_path / "test.db")
            mgr = orca_worktree_manager.HarnessManager(engine="sqlite", db_path=db_path)
            with mgr._get_sqlite_db() as conn:
                conn.execute(
                    "INSERT INTO work_item (id, type, title, state, priority) VALUES (?, ?, ?, ?, ?)",
                    (9001, "Task", "Conflict Task", "Resolved", "P2")
                )

            mock_wt = {
                "id": "wt-9001",
                "displayName": "task-9001-conflict",
                "git": {"branch": "peer/task-9001"}
            }

            with patch.object(orca_worktree_manager, "BASE_DIR", str(repo_path)), \
                 patch.object(orca_worktree_manager, "PROJECT_ROOT", repo_path), \
                 patch("tools.orca_worktree_manager.HarnessManager", return_value=mgr), \
                 patch("tools.orca_worktree_manager.find_task_worktree", return_value=mock_wt), \
                 patch("shutil.which", return_value=None), \
                 patch("tools.orca_worktree_manager.send_desktop_notification"):
                orig_cwd = os.getcwd()
                try:
                    os.chdir(repo_path)
                    res = orca_worktree_manager.approve_and_merge_worktree(9001)
                    self.assertFalse(res)
                    merge_head = repo_path / ".git" / "MERGE_HEAD"
                    self.assertFalse(merge_head.exists(), f"Active MERGE_HEAD found at {merge_head} after failed merge!")
                finally:
                    os.chdir(orig_cwd)

    @patch("tools.orca_worktree_manager.run_cmd")
    def test_13_abort_merge_safely_fallback_to_reset(self, mock_run):
        """Verify abort_merge_safely falls back to git reset --merge when abort fails."""
        def side_effect(cmd, **kwargs):
            if cmd[:3] == ["git", "rev-parse", "-q"]:
                return MagicMock(returncode=0, stdout="ref", stderr="")
            if cmd[:3] == ["git", "merge", "--abort"]:
                return MagicMock(returncode=1, stdout="", stderr="error: could not abort")
            if cmd[:3] == ["git", "reset", "--merge"]:
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        ok = orca_worktree_manager.abort_merge_safely()
        self.assertTrue(ok)
        reset_calls = [c for c in mock_run.call_args_list if c[0][0][:3] == ["git", "reset", "--merge"]]
        self.assertEqual(len(reset_calls), 1)


if __name__ == "__main__":
    unittest.main()
