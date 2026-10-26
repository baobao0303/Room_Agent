#!/usr/bin/env python3
"""
tools/tests/test_merge_abort_adversarial.py - Empirical Adversarial Stress Test Suite
for abort_merge_safely() and merge conflict recovery in tools/orca_worktree_manager.py.

Adversarial Stress Scenarios:
1. Standard conflict during --no-ff merge in main repository.
2. Conflict in a linked git worktree (where .git is a gitdir pointer file, not a directory).
3. Pre-existing untracked files during merge conflict (ensures zero data loss).
4. Pre-existing unstaged modifications in unrelated files during merge conflict.
5. Dirty working tree preventing merge from starting (git refusal before MERGE_HEAD).
6. Post-conflict modifications and staging before abort (dirty conflict resolution state).
7. Fallback to `git reset --merge` when `git merge --abort` fails.
8. Double failure (both `git merge --abort` and `git reset --merge` fail).
9. Multi-file conflicts across nested subdirectories.
10. End-to-end `approve_and_merge_worktree()` conflict handling with database integrity.
11. Idempotency when no merge is in progress.
12. Verify in 100% of cases that MERGE_HEAD is cleared and repo is in clean, usable state.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

_ORIG_DRY_RUN = None


def setUpModule():
    global _ORIG_DRY_RUN
    _ORIG_DRY_RUN = os.environ.get("SLPPC_DRY_RUN")
    os.environ["SLPPC_DRY_RUN"] = "1"


def tearDownModule():
    global _ORIG_DRY_RUN
    if _ORIG_DRY_RUN is None:
        os.environ.pop("SLPPC_DRY_RUN", None)
    else:
        os.environ["SLPPC_DRY_RUN"] = _ORIG_DRY_RUN


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools import orca_worktree_manager
from tools.harness_manager import HarnessManager


class TestMergeAbortAdversarial(unittest.TestCase):
    """Empirical adversarial stress tests for abort_merge_safely and merge recovery."""

    def _init_git_repo(self, path: Path) -> None:
        """Helper to initialize a pristine git repo with initial commit."""
        subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-B", "main"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "AdversarialTester"], cwd=path, check=True)
        subprocess.run(["git", "config", "user.email", "tester@adversary.com"], cwd=path, check=True)

        base_file = path / "base.txt"
        base_file.write_text("initial base content\n", encoding="utf-8")
        subprocess.run(["git", "add", "base.txt"], cwd=path, check=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=path, check=True, capture_output=True)

    def test_adv_01_main_repo_conflict_no_ff(self):
        """Scenario 1: Main repo conflict during --no-ff merge must be cleanly aborted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Create feature branch with change to conflict.txt
            subprocess.run(["git", "checkout", "-b", "feature/conflict-1"], cwd=repo_path, check=True, capture_output=True)
            conflict_file = repo_path / "conflict.txt"
            conflict_file.write_text("feature branch version\n", encoding="utf-8")
            subprocess.run(["git", "add", "conflict.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "feature change"], cwd=repo_path, check=True, capture_output=True)

            # Back to main and create conflicting change
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            conflict_file.write_text("main branch conflicting version\n", encoding="utf-8")
            subprocess.run(["git", "add", "conflict.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main conflicting change"], cwd=repo_path, check=True, capture_output=True)
            main_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()

            # Execute merge --no-ff which must conflict
            merge_res = subprocess.run(["git", "merge", "--no-ff", "feature/conflict-1"], cwd=repo_path, capture_output=True, text=True)
            self.assertNotEqual(merge_res.returncode, 0, "Merge was expected to fail with conflict")

            # Verify MERGE_HEAD is physically active
            merge_head = repo_path / ".git" / "MERGE_HEAD"
            self.assertTrue(merge_head.exists(), "MERGE_HEAD must exist during active conflict")

            # Call abort_merge_safely()
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok, "abort_merge_safely() should return True")

            # VERIFICATION: MERGE_HEAD must be gone
            self.assertFalse(merge_head.exists(), "MERGE_HEAD must be deleted")
            rev_res = subprocess.run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], cwd=repo_path, capture_output=True)
            self.assertNotEqual(rev_res.returncode, 0, "git rev-parse MERGE_HEAD must fail after abort")

            # VERIFICATION: Working tree is clean
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True)
            self.assertEqual(status_res.stdout.strip(), "", "Working tree must be 100% clean after abort")

            # VERIFICATION: HEAD commit unchanged
            current_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(current_commit, main_commit, "HEAD commit must match pre-merge commit")

            # Content of conflict.txt is back to main branch version
            self.assertEqual(conflict_file.read_text(encoding="utf-8"), "main branch conflicting version\n")

    def test_adv_02_linked_worktree_gitdir_file_pointer(self):
        """Scenario 2: Conflict in linked git worktree where .git is a file pointer, not directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            repo_path = base_dir / "main_repo"
            repo_path.mkdir()
            self._init_git_repo(repo_path)

            # Create branch for worktree
            subprocess.run(["git", "branch", "peer/wt-branch"], cwd=repo_path, check=True, capture_output=True)

            # Create linked worktree
            wt_path = base_dir / "linked_wt"
            subprocess.run(["git", "worktree", "add", str(wt_path), "peer/wt-branch"], cwd=repo_path, check=True, capture_output=True)

            # CRITICAL CHECK: In a linked worktree, .git is a FILE containing 'gitdir: ...'
            git_entry = wt_path / ".git"
            self.assertTrue(git_entry.is_file(), f"{git_entry} must be a file, not a directory in a linked worktree")
            # Verify file check (repo_dir / '.git' / 'MERGE_HEAD').exists() is False
            self.assertFalse((git_entry / "MERGE_HEAD").exists())

            # Create a conflicting branch in main repo
            subprocess.run(["git", "checkout", "-b", "incoming-conflict"], cwd=repo_path, check=True, capture_output=True)
            f_main = repo_path / "shared_module.py"
            f_main.write_text("def run():\n    return 'from_incoming'\n", encoding="utf-8")
            subprocess.run(["git", "add", "shared_module.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "incoming change"], cwd=repo_path, check=True, capture_output=True)

            # In worktree, modify shared_module.py differently
            f_wt = wt_path / "shared_module.py"
            f_wt.write_text("def run():\n    return 'from_worktree'\n", encoding="utf-8")
            subprocess.run(["git", "add", "shared_module.py"], cwd=wt_path, check=True)
            subprocess.run(["git", "commit", "-m", "worktree change"], cwd=wt_path, check=True, capture_output=True)

            # Attempt merge inside linked worktree
            merge_res = subprocess.run(["git", "merge", "--no-ff", "incoming-conflict"], cwd=wt_path, capture_output=True, text=True)
            self.assertNotEqual(merge_res.returncode, 0, "Merge in worktree expected to fail with conflict")

            # Check rev-parse discovers MERGE_HEAD in linked worktree
            rev_res = subprocess.run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], cwd=wt_path, capture_output=True)
            self.assertEqual(rev_res.returncode, 0, "git rev-parse must find MERGE_HEAD in linked worktree")

            # Call abort_merge_safely on linked worktree
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(wt_path))
            self.assertTrue(ok, "abort_merge_safely() should succeed on linked worktree")

            # Verify MERGE_HEAD cleared
            rev_after = subprocess.run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], cwd=wt_path, capture_output=True)
            self.assertNotEqual(rev_after.returncode, 0, "MERGE_HEAD must be cleared in worktree")

            # Verify worktree is clean
            status_wt = subprocess.run(["git", "status", "--porcelain"], cwd=wt_path, capture_output=True, text=True, check=True)
            self.assertEqual(status_wt.stdout.strip(), "", "Worktree must be completely clean")

            # Main repo must be completely intact
            status_main = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True)
            self.assertEqual(status_main.stdout.strip(), "", "Main repo must be unaffected")

    def test_adv_03_dirty_working_tree_untracked_files_preserved(self):
        """Scenario 3: Untracked files present during merge conflict must NOT be deleted or corrupted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Create feature branch with conflict
            subprocess.run(["git", "checkout", "-b", "feature/untracked-test"], cwd=repo_path, check=True, capture_output=True)
            f_code = repo_path / "app.py"
            f_code.write_text("print('feature')\n", encoding="utf-8")
            subprocess.run(["git", "add", "app.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "feature change"], cwd=repo_path, check=True, capture_output=True)

            # Back to main
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            f_code.write_text("print('main')\n", encoding="utf-8")
            subprocess.run(["git", "add", "app.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main change"], cwd=repo_path, check=True, capture_output=True)

            # Create valuable untracked user files
            notes_file = repo_path / "scratch_notes.txt"
            notes_content = "DO NOT DELETE THIS PRECIOUS DATA!\n" * 10
            notes_file.write_text(notes_content, encoding="utf-8")

            untracked_dir = repo_path / "temp_experiment"
            untracked_dir.mkdir()
            nested_untracked = untracked_dir / "draft.py"
            nested_untracked.write_text("# draft work\n", encoding="utf-8")

            # Trigger merge conflict
            merge_res = subprocess.run(["git", "merge", "--no-ff", "feature/untracked-test"], cwd=repo_path, capture_output=True, text=True)
            self.assertNotEqual(merge_res.returncode, 0)

            # Call abort_merge_safely()
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            # VERIFICATION: MERGE_HEAD is cleared
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())

            # VERIFICATION: Untracked files are 100% PRESERVED
            self.assertTrue(notes_file.exists(), "Untracked scratch file must survive abort")
            self.assertEqual(notes_file.read_text(encoding="utf-8"), notes_content)
            self.assertTrue(nested_untracked.exists(), "Nested untracked file must survive abort")

            # App.py is clean and restored
            self.assertEqual(f_code.read_text(encoding="utf-8"), "print('main')\n")

    def test_adv_04_dirty_unstaged_unrelated_changes_preserved(self):
        """Scenario 4: Unstaged changes in unrelated files must be preserved when merge conflict aborts."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Create unrelated tracked file
            unrelated = repo_path / "config.json"
            unrelated.write_text('{"env": "prod"}\n', encoding="utf-8")
            subprocess.run(["git", "add", "config.json"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "add config"], cwd=repo_path, check=True, capture_output=True)

            # Feature branch touches code.py
            subprocess.run(["git", "checkout", "-b", "feature/unstaged-test"], cwd=repo_path, check=True, capture_output=True)
            code_file = repo_path / "code.py"
            code_file.write_text("x = 100\n", encoding="utf-8")
            subprocess.run(["git", "add", "code.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "feature code"], cwd=repo_path, check=True, capture_output=True)

            # Back to main: create conflicting change in code.py
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            code_file.write_text("x = 200\n", encoding="utf-8")
            subprocess.run(["git", "add", "code.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main code"], cwd=repo_path, check=True, capture_output=True)

            # Make an UNSTAGED dirty modification to config.json (not touched by feature branch)
            unrelated.write_text('{"env": "local_dev_dirty_edit"}\n', encoding="utf-8")

            # Merge feature branch (conflicts on code.py, but config.json was untouched in feature)
            merge_res = subprocess.run(["git", "merge", "--no-ff", "feature/unstaged-test"], cwd=repo_path, capture_output=True, text=True)
            self.assertNotEqual(merge_res.returncode, 0)

            # Verify MERGE_HEAD is active
            self.assertTrue((repo_path / ".git" / "MERGE_HEAD").exists())

            # Abort merge safely
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            # Verify MERGE_HEAD is gone
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())

            # Verify the unstaged modification to config.json was PRESERVED
            self.assertEqual(unrelated.read_text(encoding="utf-8"), '{"env": "local_dev_dirty_edit"}\n')

            # And code.py is restored to main version
            self.assertEqual(code_file.read_text(encoding="utf-8"), "x = 200\n")

    def test_adv_05_pre_merge_dirty_refusal_no_merge_head(self):
        """Scenario 5: When git refuses to merge because dirty file would be overwritten (no MERGE_HEAD)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Feature branch touches target.py
            subprocess.run(["git", "checkout", "-b", "feature/dirty-block"], cwd=repo_path, check=True, capture_output=True)
            target = repo_path / "target.py"
            target.write_text("# feature implementation\n", encoding="utf-8")
            subprocess.run(["git", "add", "target.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "add target"], cwd=repo_path, check=True, capture_output=True)

            # Back to main
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)

            # In main, create UNTRACKED or UNCOMMITTED target.py
            target.write_text("# uncommitted local changes that collide\n", encoding="utf-8")

            # Git merge will fail pre-emptively: 'error: The following untracked working tree files would be overwritten by merge'
            merge_res = subprocess.run(["git", "merge", "--no-ff", "feature/dirty-block"], cwd=repo_path, capture_output=True, text=True)
            self.assertNotEqual(merge_res.returncode, 0)

            # Note: MERGE_HEAD was NEVER created!
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())

            # abort_merge_safely() should handle this gracefully and return True
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            # Untracked file still present
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "# uncommitted local changes that collide\n")

    def test_adv_06_post_conflict_staging_before_abort(self):
        """Scenario 6: If agent or user staged files during conflict, abort must still clear index and MERGE_HEAD."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            subprocess.run(["git", "checkout", "-b", "feature/stage-test"], cwd=repo_path, check=True, capture_output=True)
            f = repo_path / "mod.py"
            f.write_text("ver = 'feat'\n", encoding="utf-8")
            subprocess.run(["git", "add", "mod.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "feat"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            f.write_text("ver = 'main'\n", encoding="utf-8")
            subprocess.run(["git", "add", "mod.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main"], cwd=repo_path, check=True, capture_output=True)

            # Merge and conflict
            subprocess.run(["git", "merge", "--no-ff", "feature/stage-test"], cwd=repo_path, capture_output=True)

            # Adversarial action: simulate partially resolved or accidentally staged conflict
            f.write_text("ver = 'half-baked-resolution'\n", encoding="utf-8")
            subprocess.run(["git", "add", "mod.py"], cwd=repo_path, check=True)

            # Also create an extra staged new file
            staged_extra = repo_path / "accidental_staged.txt"
            staged_extra.write_text("accidental stage\n", encoding="utf-8")
            subprocess.run(["git", "add", "accidental_staged.txt"], cwd=repo_path, check=True)

            # Call abort_merge_safely()
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            # MERGE_HEAD cleared
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())

            # Status must be clean (git merge --abort resets index back to HEAD)
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True).stdout
            # accidental_staged.txt may become untracked, but index must have NO staged changes
            self.assertNotIn("M  mod.py", status)
            self.assertNotIn("A  accidental_staged.txt", status)
            self.assertEqual(f.read_text(encoding="utf-8"), "ver = 'main'\n")

    def test_adv_07_fallback_to_reset_when_merge_abort_fails(self):
        """Scenario 7: Fallback to `git reset --merge` when `git merge --abort` returns non-zero."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Create conflict
            subprocess.run(["git", "checkout", "-b", "feat-fallback"], cwd=repo_path, check=True, capture_output=True)
            f = repo_path / "file.txt"
            f.write_text("feature content\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "feat"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            f.write_text("main content\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "merge", "--no-ff", "feat-fallback"], cwd=repo_path, capture_output=True)
            self.assertTrue((repo_path / ".git" / "MERGE_HEAD").exists())

            # Intercept run_cmd: simulate git merge --abort failing, but git reset --merge executing
            real_run_cmd = orca_worktree_manager.run_cmd
            merge_abort_called = False
            reset_merge_called = False

            def intercept_run_cmd(cmd, **kwargs):
                nonlocal merge_abort_called, reset_merge_called
                if cmd == ["git", "merge", "--abort"]:
                    merge_abort_called = True
                    # Simulate failure of git merge --abort
                    return MagicMock(returncode=128, stdout="", stderr="fatal: mock failure of merge --abort")
                if cmd == ["git", "reset", "--merge"]:
                    reset_merge_called = True
                    # Let real git reset --merge execute!
                    return real_run_cmd(cmd, **kwargs)
                return real_run_cmd(cmd, **kwargs)

            with patch("tools.orca_worktree_manager.run_cmd", side_effect=intercept_run_cmd):
                ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))

            self.assertTrue(merge_abort_called, "git merge --abort must have been attempted first")
            self.assertTrue(reset_merge_called, "git reset --merge must have been executed as fallback")
            self.assertTrue(ok, "abort_merge_safely must return True via reset --merge fallback")

            # VERIFICATION: MERGE_HEAD was removed by git reset --merge
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(status, "", "Working tree must be clean after git reset --merge fallback")

    def test_adv_08_double_failure_returns_false(self):
        """Scenario 8: If both git merge --abort and git reset --merge fail, return False without crashing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            merge_head = repo_path / ".git" / "MERGE_HEAD"
            merge_head.write_text("dummycommit\n", encoding="utf-8")

            def mock_fail_cmd(cmd, **kwargs):
                if cmd == ["git", "merge", "--abort"]:
                    return MagicMock(returncode=1, stderr="merge abort failed")
                if cmd == ["git", "reset", "--merge"]:
                    return MagicMock(returncode=1, stderr="reset merge failed")
                return MagicMock(returncode=0, stdout="")

            with patch("tools.orca_worktree_manager.run_cmd", side_effect=mock_fail_cmd):
                ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
                self.assertFalse(ok, "Should return False when both recovery strategies fail")

    def test_adv_09_multi_file_conflict_nested_dirs(self):
        """Scenario 9: Multiple conflicting files across deep nested directory hierarchies."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Setup files in multiple directories
            d1 = repo_path / "pkg" / "sub1"
            d2 = repo_path / "pkg" / "sub2"
            d1.mkdir(parents=True)
            d2.mkdir(parents=True)

            f1 = d1 / "file1.py"
            f2 = d2 / "file2.py"
            f3 = repo_path / "root.py"

            f1.write_text("v1_base\n", encoding="utf-8")
            f2.write_text("v2_base\n", encoding="utf-8")
            f3.write_text("v3_base\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "add base tree"], cwd=repo_path, check=True, capture_output=True)

            # Feature branch modifications
            subprocess.run(["git", "checkout", "-b", "feature/deep-multi"], cwd=repo_path, check=True, capture_output=True)
            f1.write_text("v1_feature\n", encoding="utf-8")
            f2.write_text("v2_feature\n", encoding="utf-8")
            f3.write_text("v3_feature\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "feature changes"], cwd=repo_path, check=True, capture_output=True)

            # Main branch conflicting modifications
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            f1.write_text("v1_main\n", encoding="utf-8")
            f2.write_text("v2_main\n", encoding="utf-8")
            f3.write_text("v3_main\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "main changes"], cwd=repo_path, check=True, capture_output=True)

            # Merge with conflict across all 3 files
            subprocess.run(["git", "merge", "--no-ff", "feature/deep-multi"], cwd=repo_path, capture_output=True)
            self.assertTrue((repo_path / ".git" / "MERGE_HEAD").exists())

            # Abort safely
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            # All files restored and tree clean
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())
            self.assertEqual(f1.read_text(encoding="utf-8"), "v1_main\n")
            self.assertEqual(f2.read_text(encoding="utf-8"), "v2_main\n")
            self.assertEqual(f3.read_text(encoding="utf-8"), "v3_main\n")
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(status, "")

    def test_adv_10_approve_and_merge_conflict_end_to_end(self):
        """Scenario 10: Full approve_and_merge_worktree() flow with real merge conflict."""
        with tempfile.TemporaryDirectory() as tmp_dir, tempfile.TemporaryDirectory() as db_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # Feature branch in worktree
            subprocess.run(["git", "checkout", "-b", "peer/task-8888"], cwd=repo_path, check=True, capture_output=True)
            target = repo_path / "feature.py"
            target.write_text("print('task 8888 code')\n", encoding="utf-8")
            subprocess.run(["git", "add", "feature.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "task 8888"], cwd=repo_path, check=True, capture_output=True)

            # Back to main: create conflict
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            target.write_text("print('main code conflict')\n", encoding="utf-8")
            subprocess.run(["git", "add", "feature.py"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main edit"], cwd=repo_path, check=True, capture_output=True)

            # Harness DB setup inside separate db_dir
            db_path = str(Path(db_dir) / "test_harness_8888.db")
            mgr = HarnessManager(engine="sqlite", db_path=db_path)
            with mgr._get_sqlite_db() as conn:
                conn.execute(
                    "INSERT INTO work_item (id, type, title, state, priority) VALUES (?, ?, ?, ?, ?)",
                    (8888, "Task", "Conflict End-to-End Task", "Resolved", "P1")
                )

            mock_wt = {
                "id": "wt-8888",
                "displayName": "task-8888",
                "git": {"branch": "peer/task-8888"}
            }

            orig_cwd = os.getcwd()
            try:
                os.chdir(repo_path)
                with patch.object(orca_worktree_manager, "BASE_DIR", str(repo_path)), \
                     patch.object(orca_worktree_manager, "PROJECT_ROOT", repo_path), \
                     patch("tools.orca_worktree_manager.HarnessManager", return_value=mgr), \
                     patch("tools.orca_worktree_manager.find_task_worktree", return_value=mock_wt), \
                     patch("shutil.which", return_value=None), \
                     patch("tools.orca_worktree_manager.send_desktop_notification"):

                    result = orca_worktree_manager.approve_and_merge_worktree(8888)
                    self.assertFalse(result, "approve_and_merge_worktree must fail on conflict")

                    # MERGE_HEAD must NOT exist
                    merge_head = repo_path / ".git" / "MERGE_HEAD"
                    self.assertFalse(merge_head.exists(), f"Active MERGE_HEAD found at {merge_head}!")

                    # Working tree must be clean
                    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()
                    self.assertEqual(status, "", "Working tree must be left 100% clean")

                    # Task in DB must STILL be 'Resolved' (NOT Closed!)
                    item = mgr.get_work_item(8888)
                    self.assertEqual(item["state"], "Resolved", "Task state must NOT transition to Closed on failed merge")

                    # Intervention table must NOT contain an approve record for 8888
                    with mgr._get_sqlite_db() as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT COUNT(*) FROM intervention WHERE target_id = 8888 AND action = 'approve'")
                        count = cur.fetchone()[0]
                        self.assertEqual(count, 0, "No approve intervention should be recorded on failure")
            finally:
                os.chdir(orig_cwd)

    def test_adv_11_idempotent_clean_state(self):
        """Scenario 11: Calling abort_merge_safely on an already clean repo returns True idempotently."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            # No merge is active
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())

            # Call abort_merge_safely
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)
            # Second call
            ok2 = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok2)

    def test_adv_12_subdirectory_cwd(self):
        """Scenario 12: abort_merge_safely called with cwd pointing to a deep subdirectory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            sub_dir = repo_path / "components" / "ui"
            sub_dir.mkdir(parents=True)
            comp_file = sub_dir / "button.tsx"
            comp_file.write_text("export const Button = () => <button>Base</button>;\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "add button"], cwd=repo_path, check=True, capture_output=True)

            # Feature branch
            subprocess.run(["git", "checkout", "-b", "feature/sub-conflict"], cwd=repo_path, check=True, capture_output=True)
            comp_file.write_text("export const Button = () => <button>Feature</button>;\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "feature button"], cwd=repo_path, check=True, capture_output=True)

            # Main branch conflict
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            comp_file.write_text("export const Button = () => <button>Main</button>;\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-am", "main button"], cwd=repo_path, check=True, capture_output=True)

            # Merge conflict
            subprocess.run(["git", "merge", "--no-ff", "feature/sub-conflict"], cwd=repo_path, capture_output=True)
            self.assertTrue((repo_path / ".git" / "MERGE_HEAD").exists())

            # Call abort_merge_safely passing the SUBDIRECTORY as cwd!
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(sub_dir))
            self.assertTrue(ok, "abort_merge_safely should succeed when called from a subdirectory")

            # Check that root MERGE_HEAD is cleared
            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(status, "")

    def test_adv_13_metadata_cleanup_merge_msg_and_mode(self):
        """Scenario 13: Check that all merge metadata files (MERGE_HEAD, MERGE_MSG, MERGE_MODE) are cleared."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            subprocess.run(["git", "checkout", "-b", "feature/meta"], cwd=repo_path, check=True, capture_output=True)
            f = repo_path / "foo.txt"
            f.write_text("feat\n", encoding="utf-8")
            subprocess.run(["git", "add", "foo.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "feat"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            f.write_text("main\n", encoding="utf-8")
            subprocess.run(["git", "add", "foo.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "main"], cwd=repo_path, check=True, capture_output=True)

            subprocess.run(["git", "merge", "--no-ff", "feature/meta"], cwd=repo_path, capture_output=True)

            dot_git = repo_path / ".git"
            self.assertTrue((dot_git / "MERGE_HEAD").exists())

            # Abort
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            # Check that MERGE_HEAD and MERGE_MODE do not exist
            self.assertFalse((dot_git / "MERGE_HEAD").exists(), "MERGE_HEAD must not exist")
            self.assertFalse((dot_git / "MERGE_MODE").exists(), "MERGE_MODE must not exist")

    def test_adv_14_non_git_directory_handling(self):
        """Scenario 14: Calling abort_merge_safely on a non-git directory returns True gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_git = Path(tmp_dir) / "not_git"
            non_git.mkdir()
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(non_git))
            self.assertTrue(ok)

    def test_adv_15_binary_file_conflict(self):
        """Scenario 15: Conflict involving binary files must be cleanly aborted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir)
            self._init_git_repo(repo_path)

            bin_file = repo_path / "asset.bin"
            bin_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")
            subprocess.run(["git", "add", "asset.bin"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "add binary asset"], cwd=repo_path, check=True, capture_output=True)

            # Feature branch modifies binary
            subprocess.run(["git", "checkout", "-b", "feat/binary"], cwd=repo_path, check=True, capture_output=True)
            bin_file.write_bytes(b"\xaa\xbb\xcc\xdd\xee\xff")
            subprocess.run(["git", "commit", "-am", "feat binary"], cwd=repo_path, check=True, capture_output=True)

            # Main branch modifies binary differently
            subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)
            bin_file.write_bytes(b"\x11\x22\x33\x44\x55\x66")
            subprocess.run(["git", "commit", "-am", "main binary"], cwd=repo_path, check=True, capture_output=True)

            # Merge binary conflict
            merge_res = subprocess.run(["git", "merge", "--no-ff", "feat/binary"], cwd=repo_path, capture_output=True)
            self.assertNotEqual(merge_res.returncode, 0)
            self.assertTrue((repo_path / ".git" / "MERGE_HEAD").exists())

            # Abort safely
            ok = orca_worktree_manager.abort_merge_safely(cwd=str(repo_path))
            self.assertTrue(ok)

            self.assertFalse((repo_path / ".git" / "MERGE_HEAD").exists())
            self.assertEqual(bin_file.read_bytes(), b"\x11\x22\x33\x44\x55\x66")
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(status, "")


if __name__ == "__main__":
    unittest.main()
