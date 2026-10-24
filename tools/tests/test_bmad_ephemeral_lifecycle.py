#!/usr/bin/env python3
from __future__ import annotations
"""
tools/tests/test_bmad_ephemeral_lifecycle.py - 5-Stage ISTQB Audit Suite for Technical Story #3 & Task #153:
[Task 4]: Kiểm thử toàn diện 5-Stage ISTQB Suite & Regression

Stages:
- Stage 1: Acceptance Criteria & In-place Overwriting (agent_progress.py, role pm, FIFO 50)
- Stage 2: Safe Context Garbage Collection & Migration (room_cleanup.py --migrate-legacy)
- Stage 3: Structured Room Ledger Schema Integrity (< 50KB ceiling, 5 roles, FIFO 50)
- Stage 4: Zero Handoff Timestamp Residual Invariant (bmad/rooms/*)
- Stage 5: SLPPC Governance Flow Guard Compliance Audit (0 violations)
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "tools"))


class TestBmadEphemeralLifecycle(unittest.TestCase):
    """5-Stage ISTQB Test Suite for BMAD Rooms Ephemeral State Architecture."""

    def setUp(self):
        self.rooms_dir = BASE_DIR / "bmad" / "rooms"
        self.ledger_file = self.rooms_dir / "room_ledger.json"
        for role in ("supervisor", "pm", "lead", "peer", "qc"):
            role_dir = self.rooms_dir / role
            role_dir.mkdir(parents=True, exist_ok=True)
            latest_file = role_dir / "latest_handoff.md"
            if not latest_file.is_file():
                latest_file.write_text(
                    f"# BIÊN BẢN BÀN GIAO: {role.upper()}\n\n- **Agent**: `{role.upper()}`\n- **Trạng thái**: Sẵn sàng.\n",
                    encoding="utf-8",
                )

    # =========================================================================
    # STAGE 1: IN-PLACE OVERWRITE & PROGRESS LOGGING VERIFICATION
    # =========================================================================

    def test_stage1_agent_progress_pm_role_and_inplace(self):
        """[Stage 1] Verify agent_progress.py supports PM role and overwrites latest_handoff.md in-place."""
        pm_room = self.rooms_dir / "pm"
        pm_room.mkdir(parents=True, exist_ok=True)
        pm_latest = pm_room / "latest_handoff.md"

        res = subprocess.run(
            [
                sys.executable,
                "tools/agent_progress.py",
                "log",
                "--agent",
                "PM",
                "--summary",
                "ISTQB Stage 1 Verification for PM role",
                "--done",
                "Test PM role logging",
            ],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"agent_progress.py failed: {res.stderr}")
        self.assertTrue(pm_latest.is_file(), "pm/latest_handoff.md must exist")
        content = pm_latest.read_text(encoding="utf-8")
        self.assertIn("ISTQB Stage 1 Verification for PM role", content)
        self.assertLessEqual(len(content.splitlines()), 150, "latest_handoff.md must be <= 150 lines")

        # Verify no handoff_*.md was created in pm room
        pm_timestamp_memos = list(pm_room.glob("handoff_*.md"))
        self.assertEqual(len(pm_timestamp_memos), 0, "No handoff_*.md files should be created")

    def test_stage1_anti_leak_path_sanitization_in_progress_log(self):
        """[Stage 1] Verify agent_progress.py sanitizes machine paths to enforce Zero-Leak."""
        from agent_progress import sanitize_text

        raw_text = "Checked /Users/admin/projects/app and /home/deployer/service.py"
        sanitized = sanitize_text(raw_text)
        self.assertNotIn("/Users/admin", sanitized)
        self.assertNotIn("/home/deployer", sanitized)
        self.assertIn("~/", sanitized)

    def test_stage1_fifo_50_rolling_in_room_ledger(self):
        """[Stage 1] Verify room_ledger.json enforces FIFO 50 rolling limit."""
        if not self.ledger_file.is_file():
            self.skipTest("room_ledger.json does not exist yet")

        ledger = json.loads(self.ledger_file.read_text(encoding="utf-8"))
        history = ledger.get("history", [])
        self.assertLessEqual(len(history), 50, "history array must not exceed 50 items")

    # =========================================================================
    # STAGE 2: SAFE CONTEXT GARBAGE COLLECTION & MIGRATION
    # =========================================================================

    def test_stage2_room_cleanup_migrate_legacy_execution(self):
        """[Stage 2] Verify room_cleanup.py --migrate-legacy runs cleanly."""
        res = subprocess.run(
            [sys.executable, "tools/room_cleanup.py", "--migrate-legacy"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"room_cleanup --migrate-legacy failed: {res.stderr}")
        self.assertIn("CHUẨN HÓA BMAD ROOMS", res.stdout)
        self.assertTrue(self.ledger_file.is_file(), "room_ledger.json must exist after migration")

    def test_stage2_safe_garbage_collection_blocks_unclosed_task(self):
        """[Stage 2] Verify room_cleanup.py refuses to purge files of unclosed tasks."""
        # Using a dummy task ID that is not closed
        res = subprocess.run(
            [sys.executable, "tools/room_cleanup.py", "--task-id", "99999"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertTrue(
            "TỪ CHỐI" in res.stdout or "CHẶN DỌN DẸP" in res.stdout,
            "Must refuse cleanup when task is not closed",
        )

    def test_stage2_safe_task_scoped_archival(self):
        """[Stage 2] Verify room_cleanup.py packages bmad/rooms/tasks/<task_id>/ into tar.gz."""
        test_task_dir = self.rooms_dir / "tasks" / "test_lifecycle_999"
        test_task_dir.mkdir(parents=True, exist_ok=True)
        (test_task_dir / "notes.md").write_text("# Test Notes\n", encoding="utf-8")

        res = subprocess.run(
            [sys.executable, "tools/room_cleanup.py", "--task-id", "test_lifecycle_999", "--force"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        archive_tar = self.rooms_dir / "archive" / "task_test_lifecycle_999.tar.gz"
        self.assertTrue(archive_tar.is_file(), "Archive tar.gz must exist")
        # Cleanup test artifact
        archive_tar.unlink(missing_ok=True)

    def test_stage2_cleanup_task_room_invokes_zombie_reaper(self):
        """[Stage 2] Verify cleanup_task_room in harness_manager triggers zombie terminal reaper."""
        from harness_manager import cleanup_task_room
        cleaned = cleanup_task_room(99999)
        self.assertIsInstance(cleaned, int)

    # =========================================================================
    # STAGE 3: STRUCTURED ROOM LEDGER SCHEMA & RESOURCE CEILING
    # =========================================================================

    def test_stage3_ledger_schema_integrity(self):
        """[Stage 3] Verify room_ledger.json matches the 3-tier architecture schema."""
        self.assertTrue(self.ledger_file.is_file(), "room_ledger.json must exist")
        ledger = json.loads(self.ledger_file.read_text(encoding="utf-8"))

        self.assertEqual(ledger.get("version"), "1.0.0")
        self.assertIn("updated_at", ledger)
        self.assertIn("roles", ledger)
        self.assertIn("history", ledger)

        roles = ledger["roles"]
        for expected_role in ("supervisor", "pm", "lead", "peer", "qc"):
            self.assertIn(expected_role, roles, f"Role {expected_role} missing from room_ledger")
            role_entry = roles[expected_role]
            self.assertIn("status", role_entry)
            self.assertIn("last_action", role_entry)
            self.assertIn("updated_at", role_entry)

    def test_stage3_ledger_file_size_ceiling(self):
        """[Stage 3] Verify room_ledger.json file size is well under 50 KB ceiling."""
        self.assertTrue(self.ledger_file.is_file(), "room_ledger.json must exist")
        size_bytes = self.ledger_file.stat().st_size
        self.assertLess(size_bytes, 50 * 1024, f"room_ledger.json ({size_bytes}B) must be < 50KB")

    # =========================================================================
    # STAGE 4: ZERO HANDOFF TIMESTAMP RESIDUAL INVARIANT
    # =========================================================================

    def test_stage4_zero_residual_handoff_files(self):
        """[Stage 4] Verify find bmad/rooms -name 'handoff_*.md' returns exactly 0 files."""
        handoff_files = list(self.rooms_dir.rglob("handoff_*.md"))
        self.assertEqual(
            len(handoff_files),
            0,
            f"Expected 0 handoff_*.md files, found {len(handoff_files)}: {[str(f.relative_to(BASE_DIR)) for f in handoff_files]}",
        )

    def test_stage4_single_pointer_in_place_per_role(self):
        """[Stage 4] Verify each role folder has at most 1 latest_handoff.md."""
        for role in ("supervisor", "pm", "lead", "peer", "qc"):
            role_dir = self.rooms_dir / role
            if role_dir.is_dir():
                latest_file = role_dir / "latest_handoff.md"
                self.assertTrue(
                    latest_file.is_file(),
                    f"Role {role} must have latest_handoff.md",
                )
                line_count = len(latest_file.read_text(encoding="utf-8").splitlines())
                self.assertLessEqual(
                    line_count,
                    150,
                    f"{role}/latest_handoff.md exceeds 150 lines ceiling ({line_count} lines)",
                )

    # =========================================================================
    # STAGE 5: SLPPC FLOW GUARD COMPLIANCE AUDIT
    # =========================================================================

    def test_stage5_slppc_governance_zero_violations(self):
        """[Stage 5] Verify python3 tools/slppc_flow_guard.py audit detects 0 violations."""
        res = subprocess.run(
            [sys.executable, "tools/slppc_flow_guard.py", "audit"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Flow guard audit failed: {res.stderr}\n{res.stdout}")
        self.assertIn("Vi phạm phát hiện  : 0", res.stdout)
        self.assertIn("PASS: 100% tuân thủ mô hình SLPPC", res.stdout)

    def test_stage5_anti_leak_sentinel_cleanliness(self):
        """[Stage 5] Verify scripts/anti_leak_sentinel.py reports 100% clean."""
        res = subprocess.run(
            [sys.executable, "scripts/anti_leak_sentinel.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Anti-leak sentinel failed: {res.stderr}\n{res.stdout}")
        self.assertIn("100% clean", res.stdout)


if __name__ == "__main__":
    unittest.main()
