#!/usr/bin/env python3
from __future__ import annotations
"""
tools/tests/test_task151_room_cleanup_istqb.py - 5-Stage ISTQB Audit Suite for Task #151:
[Task 2]: Nâng cấp room_cleanup.py - Migration CLI --migrate-legacy & Auto-Archive

Stages checked:
- Stage 1: Acceptance Criteria Verification (AC-1 to AC-5)
- Stage 2: Boundary Value Analysis (BVA) on Dry-run, Days cutoff, and ID extraction
- Stage 3: Equivalence Partitioning & Decision Table for Harness Task State Machine
- Stage 4: CLI Execution Contract & Zero Hardcoded Machine Paths
- Stage 5: Governance, Anti-Leak Sentinel & SLPPC Flow Guard Compliance Audit
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import tools.room_cleanup as rc
from tools.harness_manager import HarnessManager


class TestTask151RoomCleanupISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task #151."""

    def setUp(self):
        self.mgr = HarnessManager(engine="auto")
        self.tmp_dir = tempfile.mkdtemp(prefix="bmad_cleanup_test_")
        self.rooms_dir = Path(self.tmp_dir) / "bmad" / "rooms"
        self.archive_dir = self.rooms_dir / "archive"
        self.rooms_dir.mkdir(parents=True, exist_ok=True)

        # Patch room_cleanup module dirs
        self._orig_rooms_dir = rc.ROOMS_DIR
        self._orig_archive_dir = rc.ARCHIVE_DIR
        rc.ROOMS_DIR = self.rooms_dir
        rc.ARCHIVE_DIR = self.archive_dir

    def tearDown(self):
        rc.ROOMS_DIR = self._orig_rooms_dir
        rc.ARCHIVE_DIR = self._orig_archive_dir
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # =========================================================================
    # STAGE 1: ACCEPTANCE CRITERIA VERIFICATION (AC-1 .. AC-5)
    # =========================================================================

    def test_stage1_ac1_migrate_legacy_removes_timestamped_handoffs(self):
        """[AC-1] Verify migrate_legacy removes all handoff_*.md files."""
        peer_dir = self.rooms_dir / "peer"
        peer_dir.mkdir(parents=True, exist_ok=True)
        (peer_dir / "handoff_20261020_110000.md").write_text("old 1", encoding="utf-8")
        (peer_dir / "handoff_20261021_120000.md").write_text("old 2", encoding="utf-8")

        removed = rc.migrate_legacy(dry_run=False)
        self.assertEqual(removed, 2, "Expected 2 legacy handoff files removed")

        remaining = list(self.rooms_dir.rglob("handoff_*.md"))
        self.assertEqual(len(remaining), 0, "No handoff_*.md files should remain")

        legacy_dir = self.archive_dir / "legacy_handoffs"
        self.assertTrue(legacy_dir.is_dir(), "legacy_handoffs directory must exist in archive")
        archived_files = list(legacy_dir.glob("*.md"))
        self.assertEqual(len(archived_files), 2, "Expected 2 archived files in legacy_handoffs")

    def test_stage1_ac2_migrate_legacy_preserves_latest_handoff(self):
        """[AC-2] Verify latest_handoff.md is created from newest legacy file if missing."""
        supervisor_dir = self.rooms_dir / "supervisor"
        supervisor_dir.mkdir(parents=True, exist_ok=True)
        h1 = supervisor_dir / "handoff_20261020_100000.md"
        h2 = supervisor_dir / "handoff_20261022_150000.md"
        h1.write_text("older supervisor memo", encoding="utf-8")
        h2.write_text("newest supervisor memo", encoding="utf-8")

        rc.migrate_legacy(dry_run=False)

        latest_file = supervisor_dir / "latest_handoff.md"
        self.assertTrue(latest_file.is_file(), "latest_handoff.md must be created")
        self.assertEqual(latest_file.read_text(encoding="utf-8"), "newest supervisor memo")

    def test_stage1_ac3_migrate_legacy_initializes_room_ledger(self):
        """[AC-3] Verify room_ledger.json is initialized with 5 SLPPC roles and schema."""
        rc.migrate_legacy(dry_run=False)

        ledger_file = self.rooms_dir / "room_ledger.json"
        self.assertTrue(ledger_file.is_file(), "room_ledger.json must exist")
        data = json.loads(ledger_file.read_text(encoding="utf-8"))
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertIn("roles", data)
        self.assertIn("history", data)
        for role in ["supervisor", "pm", "lead", "peer", "qc"]:
            self.assertIn(role, data["roles"], f"Role {role} missing in room_ledger.json")

    def test_stage1_ac4_context_protection_blocks_non_closed_cleanup(self):
        """[AC-4] Verify cleanup_by_task blocks deletion if task is not Closed."""
        peer_dir = self.rooms_dir / "peer"
        peer_dir.mkdir(parents=True, exist_ok=True)
        task_file = peer_dir / "task_151_temp_notes.md"
        task_file.write_text("work in progress", encoding="utf-8")

        mock_db = MagicMock()
        mock_db.get_work_item.return_value = {"id": 151, "state": "Resolved"}

        with patch("tools.room_cleanup.FlociHarnessDB", return_value=mock_db):
            rc.cleanup_by_task("151", dry_run=False, force=False)

        # File must remain untouched
        self.assertTrue(task_file.is_file(), "Active/Resolved task file must be preserved (Safe Context)")

    def test_stage1_ac5_cleanup_archives_closed_task_files(self):
        """[AC-5] Verify cleanup_by_task moves files to archive/task_<id> when Closed."""
        peer_dir = self.rooms_dir / "peer"
        peer_dir.mkdir(parents=True, exist_ok=True)
        task_file = peer_dir / "task_151_temp_notes.md"
        task_file.write_text("completed task work", encoding="utf-8")

        mock_db = MagicMock()
        mock_db.get_work_item.return_value = {"id": 151, "state": "Closed"}

        with patch("tools.room_cleanup.FlociHarnessDB", return_value=mock_db):
            rc.cleanup_by_task("151", dry_run=False, force=False)

        self.assertFalse(task_file.is_file(), "Original task file should be moved")
        archived_file = self.archive_dir / "task_151" / "task_151_temp_notes.md"
        self.assertTrue(archived_file.is_file(), "Task file must exist in archive/task_151/")

    def test_stage1_ac6_cleanup_archives_task_scoped_directory(self):
        """[AC-6] Verify cleanup_by_task archives bmad/rooms/tasks/<task_id>/ when Closed."""
        task_scoped_dir = self.rooms_dir / "tasks" / "151"
        task_scoped_dir.mkdir(parents=True, exist_ok=True)
        task_doc = task_scoped_dir / "task_spec.md"
        task_doc.write_text("task scoped isolation spec", encoding="utf-8")

        mock_db = MagicMock()
        mock_db.get_work_item.return_value = {"id": 151, "state": "Closed"}

        with patch("tools.room_cleanup.FlociHarnessDB", return_value=mock_db):
            rc.cleanup_by_task("151", dry_run=False, force=False)

        # Task directory must be removed and archived
        self.assertFalse(task_scoped_dir.exists(), "bmad/rooms/tasks/151 should be removed after cleanup")
        archive_tar = self.archive_dir / "task_151.tar.gz"
        self.assertTrue(archive_tar.is_file(), "task_151.tar.gz must exist in archive/")

    # =========================================================================
    # STAGE 2: BOUNDARY VALUE ANALYSIS (BVA)
    # =========================================================================

    def test_stage2_dry_run_boundary_no_disk_mutations(self):
        """[Stage 2 - BVA] Verify dry_run mode performs zero disk writes/deletions."""
        peer_dir = self.rooms_dir / "peer"
        peer_dir.mkdir(parents=True, exist_ok=True)
        h = peer_dir / "handoff_20261021_010101.md"
        h.write_text("test dry run", encoding="utf-8")

        removed = rc.migrate_legacy(dry_run=True)
        self.assertEqual(removed, 1)
        self.assertTrue(h.is_file(), "Dry run must NOT delete files")

    def test_stage2_numeric_id_extraction_edge_cases(self):
        """[Stage 2 - BVA] Verify get_task_state extracts numeric IDs correctly."""
        mock_db = MagicMock()
        mock_db.get_work_item.return_value = {"id": 151, "state": "Closed"}

        self.assertEqual(rc.get_task_state(mock_db, "151"), "Closed")
        self.assertEqual(rc.get_task_state(mock_db, "WI-151"), "Closed")
        self.assertEqual(rc.get_task_state(mock_db, "task_151"), "Closed")
        self.assertIsNone(rc.get_task_state(mock_db, "no-digits"))

    def test_stage2_preserve_filenames_boundary(self):
        """[Stage 2 - BVA] Verify PRESERVE_FILENAMES are never deleted by cleanup."""
        lead_dir = self.rooms_dir / "lead"
        lead_dir.mkdir(parents=True, exist_ok=True)

        for fname in rc.PRESERVE_FILENAMES:
            (lead_dir / fname).write_text(f"content of {fname}", encoding="utf-8")

        mock_db = MagicMock()
        mock_db.get_work_item.return_value = {"id": 151, "state": "Closed"}

        with patch("tools.room_cleanup.FlociHarnessDB", return_value=mock_db):
            rc.cleanup_by_task("151", dry_run=False, force=False)

        for fname in rc.PRESERVE_FILENAMES:
            f = lead_dir / fname
            self.assertTrue(f.is_file(), f"Preserved file {fname} was mistakenly altered")

    # =========================================================================
    # STAGE 3: EQUIVALENCE PARTITIONING & STATE TRANSITION
    # =========================================================================

    def test_stage3_state_equivalence_partitions(self):
        """[Stage 3 - EP] Verify state machine equivalence classes for cleanup authorization."""
        forbidden_states = ["New", "Active", "Resolved", "Blocked", None]
        mock_db = MagicMock()

        for state in forbidden_states:
            peer_dir = self.rooms_dir / "peer"
            peer_dir.mkdir(parents=True, exist_ok=True)
            f = peer_dir / f"task_99_{state}.md"
            f.write_text("protected content", encoding="utf-8")

            mock_db.get_work_item.return_value = {"id": 99, "state": state} if state else None
            with patch("tools.room_cleanup.FlociHarnessDB", return_value=mock_db):
                rc.cleanup_by_task("99", dry_run=False, force=False)

            self.assertTrue(f.is_file(), f"File for state '{state}' was deleted contrary to safety rules")

    def test_stage3_force_flag_override(self):
        """[Stage 3] Verify force=True overrides state check when explicitly commanded."""
        peer_dir = self.rooms_dir / "peer"
        peer_dir.mkdir(parents=True, exist_ok=True)
        f = peer_dir / "task_99_forced.md"
        f.write_text("forced cleanup", encoding="utf-8")

        mock_db = MagicMock()
        mock_db.get_work_item.return_value = {"id": 99, "state": "Active"}

        with patch("tools.room_cleanup.FlociHarnessDB", return_value=mock_db):
            rc.cleanup_by_task("99", dry_run=False, force=True)

        self.assertFalse(f.is_file(), "Force flag must bypass state guard")

    # =========================================================================
    # STAGE 4: CLI CONTRACT & PYTHON SYNTAX INTEGRITY
    # =========================================================================

    def test_stage4_cli_flags_execution(self):
        """[Stage 4] Verify room_cleanup.py CLI flags execute cleanly."""
        res_help = subprocess.run(
            [sys.executable, "tools/room_cleanup.py", "--help"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_help.returncode, 0)
        self.assertIn("--migrate-legacy", res_help.stdout)
        self.assertIn("--task-id", res_help.stdout)
        self.assertIn("--sweep", res_help.stdout)

        # No args should exit code 1
        res_noargs = subprocess.run(
            [sys.executable, "tools/room_cleanup.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_noargs.returncode, 1)

    def test_stage4_zero_personal_machine_paths(self):
        """[Stage 4] Verify room_cleanup.py contains zero absolute personal machine paths."""
        source = (BASE_DIR / "tools" / "room_cleanup.py").read_text(encoding="utf-8")
        self.assertNotIn("/home/baoltb", source)
        self.assertNotIn("/Users/bao312", source)

    # =========================================================================
    # STAGE 5: GOVERNANCE, SENTINEL & SLPPC FLOW GUARD AUDIT
    # =========================================================================

    def test_stage5_sentinel_and_flow_guard_audit(self):
        """[Stage 5] Verify anti-leak sentinel and slppc flow guard pass with 0 errors."""
        sentinel = subprocess.run(
            [sys.executable, "scripts/anti_leak_sentinel.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(sentinel.returncode, 0, f"Sentinel failed:\n{sentinel.stdout}")

        guard = subprocess.run(
            [sys.executable, "tools/slppc_flow_guard.py", "audit"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(guard.returncode, 0, f"Flow guard failed:\n{guard.stdout}")
        self.assertIn("Vi phạm phát hiện  : 0", guard.stdout)


if __name__ == "__main__":
    unittest.main()
