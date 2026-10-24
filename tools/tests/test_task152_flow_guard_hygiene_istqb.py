#!/usr/bin/env python3
"""
tools/tests/test_task152_flow_guard_hygiene_istqb.py - 5-Stage ISTQB Audit Suite for Task #152:
[Task 3]: Tích hợp QC Gate slppc_flow_guard.py - Chốt chặn Ephemeral Room Hygiene

Stages checked:
- Stage 1: Acceptance Criteria Verification (AC-1 to AC-3)
- Stage 2: Boundary Value Analysis (BVA) on 50KB size ceiling, 150 lines ceiling, and FIFO 50 limit
- Stage 3: Equivalence Partitioning on Violation Types (Legacy Files, Ledger Bloat, Schema, Zero-Leak)
- Stage 4: CLI Execution Contract (`hygiene` command and `--json` flag)
- Stage 5: Governance, Anti-Leak Sentinel & Full Suite Regression Pass
"""

import sys
import json
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools.slppc_flow_guard import audit_ephemeral_room_hygiene, run_slppc_audit


class TestTask152FlowGuardHygieneISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task #152."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="hygiene_test_")
        self.rooms_dir = Path(self.tmp_dir) / "bmad" / "rooms"
        self.rooms_dir.mkdir(parents=True, exist_ok=True)

        # Setup standard 5 clean roles and valid ledger
        for role in ("supervisor", "pm", "lead", "peer", "qc"):
            role_dir = self.rooms_dir / role
            role_dir.mkdir(parents=True, exist_ok=True)
            (role_dir / "latest_handoff.md").write_text(
                f"# Latest Handoff for {role}\n- Status: Done\n", encoding="utf-8"
            )

        valid_ledger = {
            "version": "1.0.0",
            "updated_at": "2026-10-23T23:00:00Z",
            "roles": {
                r: {"status": "IDLE", "last_action": "init", "active_task_id": None, "updated_at": "2026-10-23T23:00:00Z"}
                for r in ("supervisor", "pm", "lead", "peer", "qc")
            },
            "history": [{"timestamp": "2026-10-23T23:00:00Z", "agent": "Peer", "action": "log", "summary": "init"}],
        }
        (self.rooms_dir / "room_ledger.json").write_text(
            json.dumps(valid_ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # =========================================================================
    # STAGE 1: ACCEPTANCE CRITERIA VERIFICATION (AC-1 .. AC-3)
    # =========================================================================

    def test_stage1_ac1_clean_environment_zero_violations(self):
        """[AC-1] Verify clean room setup reports 0 violations."""
        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertEqual(len(violations), 0, f"Expected 0 violations on clean room, got: {violations}")

    def test_stage1_ac2_detects_legacy_timestamped_handoff(self):
        """[AC-2] Verify detection of legacy handoff_*.md files."""
        legacy_file = self.rooms_dir / "peer" / "handoff_20261020_123456.md"
        legacy_file.write_text("old handoff", encoding="utf-8")

        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("room_hygiene_violation", types)

    def test_stage1_ac3_detects_missing_room_ledger(self):
        """[AC-3] Verify detection of missing room_ledger.json."""
        (self.rooms_dir / "room_ledger.json").unlink()
        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("missing_ledger_violation", types)

    # =========================================================================
    # STAGE 2: BOUNDARY VALUE ANALYSIS (BVA)
    # =========================================================================

    def test_stage2_ledger_fifo_50_boundary(self):
        """[Stage 2 - BVA] Verify history > 50 triggers ledger_overflow_violation."""
        ledger_path = self.rooms_dir / "room_ledger.json"
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
        data["history"] = [{"i": i} for i in range(51)]
        ledger_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("ledger_overflow_violation", types)

    def test_stage2_ledger_size_ceiling_50kb(self):
        """[Stage 2 - BVA] Verify room_ledger.json exceeding 50KB triggers ledger_bloat_violation."""
        ledger_path = self.rooms_dir / "room_ledger.json"
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
        data["padding"] = "x" * (51 * 1024)
        ledger_path.write_text(json.dumps(data), encoding="utf-8")

        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("ledger_bloat_violation", types)

    def test_stage2_latest_handoff_line_ceiling_150(self):
        """[Stage 2 - BVA] Verify latest_handoff.md exceeding 150 lines triggers oversized_handoff_memo."""
        long_memo = self.rooms_dir / "supervisor" / "latest_handoff.md"
        long_memo.write_text("\n".join([f"Line {i}" for i in range(155)]), encoding="utf-8")

        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("oversized_handoff_memo", types)

    # =========================================================================
    # STAGE 3: ZERO-LEAK & SCHEMA EQUIVALENCE PARTITIONING
    # =========================================================================

    def test_stage3_zero_leak_personal_path_detection(self):
        """[Stage 3] Verify absolute path to personal machine triggers anti_leak_violation."""
        memo = self.rooms_dir / "lead" / "latest_handoff.md"
        memo.write_text("Modified file at /Users/john_doe/workspace/code.ts\n", encoding="utf-8")

        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("anti_leak_violation", types)

    def test_stage3_ledger_schema_missing_required_keys(self):
        """[Stage 3] Verify missing 'version' or 'roles' triggers ledger_schema_violation."""
        ledger_path = self.rooms_dir / "room_ledger.json"
        ledger_path.write_text(json.dumps({"roles": {}}), encoding="utf-8")

        violations = audit_ephemeral_room_hygiene(self.rooms_dir)
        types = [v.get("type") for v in violations]
        self.assertIn("ledger_schema_violation", types)

    # =========================================================================
    # STAGE 4: CLI EXECUTION CONTRACT
    # =========================================================================

    def test_stage4_cli_hygiene_command(self):
        """[Stage 4] Verify CLI `slppc_flow_guard.py hygiene` runs successfully."""
        res = subprocess.run(
            [sys.executable, "tools/slppc_flow_guard.py", "hygiene"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"hygiene command failed:\n{res.stdout}\n{res.stderr}")
        self.assertIn("EPHEMERAL ROOM HYGIENE AUDIT", res.stdout)
        self.assertIn("Số lượng vi phạm: 0", res.stdout)

    def test_stage4_cli_hygiene_json_output(self):
        """[Stage 4] Verify CLI `slppc_flow_guard.py hygiene --json` emits valid JSON."""
        res = subprocess.run(
            [sys.executable, "tools/slppc_flow_guard.py", "hygiene", "--json"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("hygiene_violations", data)
        self.assertEqual(data.get("count"), 0)

    # =========================================================================
    # STAGE 5: SECURITY SENTINEL & AUDIT INTEGRATION
    # =========================================================================

    def test_stage5_audit_ephemeral_integration(self):
        """[Stage 5] Verify full audit includes ephemeral hygiene check."""
        audit_res = run_slppc_audit(auto_record=False)
        self.assertEqual(audit_res.get("violations_detected"), 0)

    def test_stage5_anti_leak_sentinel_pass(self):
        """[Stage 5] Verify anti-leak sentinel passes 100%."""
        res = subprocess.run(
            [sys.executable, "scripts/anti_leak_sentinel.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)


if __name__ == "__main__":
    unittest.main()
