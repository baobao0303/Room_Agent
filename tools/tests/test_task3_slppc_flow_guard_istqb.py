#!/usr/bin/env python3
from __future__ import annotations
"""
tools/tests/test_task3_slppc_flow_guard_istqb.py - 5-Stage ISTQB Audit Suite for Task #2 (Task 3 in Ephemeral Spec):
[Task 3]: Tích hợp QC Gate slppc_flow_guard.py - Chốt chặn Ephemeral Room Hygiene

Stages checked:
- Stage 1: Acceptance Criteria Verification (AC-1 to AC-5 in Ephemeral State Spec)
- Stage 2: Boundary Value Analysis (BVA) on FIFO 50, Line Limit 150, and 50KB Ledger Ceiling
- Stage 3: Equivalence Partitioning & Role Invariants (Supervisor, PM, Lead, Peer, QC) across latest_handoff.md
- Stage 4: CLI Execution Contract & Zero Hardcoded Machine Paths
- Stage 5: Governance, Anti-Leak Sentinel & SLPPC Flow Guard Compliance Audit
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import tools.slppc_flow_guard as fg
from tools.harness_manager import HarnessManager


class TestTask3SlppcFlowGuardISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task 3: Ephemeral Room Hygiene QC Gate."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="flow_guard_test_")
        self.rooms_dir = Path(self.tmp_dir) / "bmad" / "rooms"
        self.rooms_dir.mkdir(parents=True, exist_ok=True)

        # Create valid initial state
        for role in ("supervisor", "pm", "lead", "peer", "qc"):
            role_dir = self.rooms_dir / role
            role_dir.mkdir(parents=True, exist_ok=True)
            (role_dir / "latest_handoff.md").write_text(f"# {role.title()} Handoff\n- Status: OK\n", encoding="utf-8")

        initial_ledger = {
            "version": "1.0.0",
            "updated_at": "2026-10-23T23:00:00Z",
            "roles": {r: {"status": "IDLE"} for r in ("supervisor", "pm", "lead", "peer", "qc")},
            "history": [{"timestamp": "2026-10-23T23:00:00Z", "agent": "Peer", "action": "test", "summary": "init"}]
        }
        (self.rooms_dir / "room_ledger.json").write_text(json.dumps(initial_ledger, indent=2), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # =========================================================================
    # STAGE 1: ACCEPTANCE CRITERIA VERIFICATION (AC-1 .. AC-5)
    # =========================================================================

    def test_stage1_ac1_detect_legacy_timestamped_handoff_files(self):
        """[AC-1] Verify audit detects any legacy handoff_*.md files."""
        # Baseline: 0 violations
        self.assertEqual(len(fg.audit_ephemeral_room_hygiene(self.rooms_dir)), 0)

        # Inject legacy handoff file
        legacy_file = self.rooms_dir / "peer" / "handoff_20261023_100000.md"
        legacy_file.write_text("legacy handoff", encoding="utf-8")

        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertGreaterEqual(len(violations), 1)
        self.assertTrue(any(v.get("type") == "room_hygiene_violation" for v in violations))
        self.assertTrue(any("handoff_20261023_100000.md" in v.get("evidence", "") for v in violations))

    def test_stage1_ac2_single_pointer_memo_per_role(self):
        """[AC-2] Verify each role must maintain exactly single-pointer latest_handoff.md."""
        # 1. Missing latest_handoff.md
        (self.rooms_dir / "lead" / "latest_handoff.md").unlink()
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "missing_handoff_memo" and v.get("role") == "lead" for v in violations))

        # Restore
        (self.rooms_dir / "lead" / "latest_handoff.md").write_text("# Lead\n", encoding="utf-8")

        # 2. Extra handoff file
        (self.rooms_dir / "lead" / "extra_handoff.md").write_text("# Extra\n", encoding="utf-8")
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "room_hygiene_violation" and "extra_handoff.md" in v.get("evidence", "") for v in violations))

    def test_stage1_ac3_room_ledger_json_integrity(self):
        """[AC-3] Verify room_ledger.json exists, adheres to schema, and size < 50KB."""
        ledger_path = self.rooms_dir / "room_ledger.json"

        # 1. Missing ledger
        ledger_path.unlink()
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "missing_ledger_violation" for v in violations))

        # 2. Corrupt JSON
        ledger_path.write_text("{ corrupt json ...", encoding="utf-8")
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "ledger_schema_violation" for v in violations))

        # 3. Missing required key
        ledger_path.write_text(json.dumps({"version": "1.0.0"}), encoding="utf-8")
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any("roles" in v.get("evidence", "") or "history" in v.get("evidence", "") for v in violations))

    def test_stage1_ac4_zero_leak_personal_path_detection(self):
        """[AC-4] Verify absolute machine paths in latest_handoff.md are detected."""
        (self.rooms_dir / "peer" / "latest_handoff.md").write_text(
            "# Peer Handoff\nRan tests at /Users/developer_bob/workspace/project\n",
            encoding="utf-8"
        )
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "anti_leak_violation" for v in violations))

    def test_stage1_ac5_clean_baseline_zero_violations(self):
        """[AC-5] Verify clean state yields exactly 0 violations."""
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertEqual(len(violations), 0)

    # =========================================================================
    # STAGE 2: BOUNDARY VALUE ANALYSIS (BVA)
    # =========================================================================

    def test_stage2_bva_fifo_history_50_vs_51(self):
        """[BVA] Verify history length = 50 passes, history length = 51 fails."""
        ledger_path = self.rooms_dir / "room_ledger.json"

        # Exactly 50 items
        data_50 = {
            "version": "1.0.0",
            "roles": {},
            "history": [{"i": idx} for idx in range(50)]
        }
        ledger_path.write_text(json.dumps(data_50), encoding="utf-8")
        self.assertEqual(len(fg.audit_ephemeral_room_hygiene(self.rooms_dir)), 0)

        # 51 items (Upper boundary + 1)
        data_51 = {
            "version": "1.0.0",
            "roles": {},
            "history": [{"i": idx} for idx in range(51)]
        }
        ledger_path.write_text(json.dumps(data_51), encoding="utf-8")
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "ledger_overflow_violation" for v in violations))

    def test_stage2_bva_line_limit_150_vs_151(self):
        """[BVA] Verify latest_handoff.md line count 150 passes, 151 fails."""
        memo = self.rooms_dir / "peer" / "latest_handoff.md"

        # Exactly 150 lines
        memo.write_text("\n".join([f"Line {i}" for i in range(150)]), encoding="utf-8")
        self.assertEqual(len(fg.audit_ephemeral_room_hygiene(self.rooms_dir)), 0)

        # 151 lines
        memo.write_text("\n".join([f"Line {i}" for i in range(151)]), encoding="utf-8")
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "oversized_handoff_memo" for v in violations))

    def test_stage2_bva_ledger_size_ceiling_50kb(self):
        """[BVA] Verify room_ledger.json <= 50KB passes, > 50KB fails."""
        ledger_path = self.rooms_dir / "room_ledger.json"

        # Bloat payload > 50KB
        bloated_data = {
            "version": "1.0.0",
            "roles": {},
            "history": [{"padding": "x" * 60000}]
        }
        ledger_path.write_text(json.dumps(bloated_data), encoding="utf-8")
        violations = fg.audit_ephemeral_room_hygiene(self.rooms_dir)
        self.assertTrue(any(v.get("type") == "ledger_bloat_violation" for v in violations))

    # =========================================================================
    # STAGE 3: EQUIVALENCE PARTITIONING & ROLE INVARIANTS
    # =========================================================================

    def test_stage3_role_trespass_detected_in_latest_handoff(self):
        """[Stage 3] Verify Lead role trespass is caught in latest_handoff.md."""
        lead_dir = self.rooms_dir / "lead"
        (lead_dir / "latest_handoff.md").write_text(
            "# Lead Handoff #42\nModified files: projects/wicx-crm-fe/src/main.ts directly.\n",
            encoding="utf-8"
        )
        violations = fg.audit_lead_role_trespass(lead_dir=lead_dir)
        self.assertGreaterEqual(len(violations), 1)
        self.assertEqual(violations[0]["task_id"], "42")

    def test_stage3_premature_close_detected_in_latest_handoff(self):
        """[Stage 3] Verify Dev premature close is caught in latest_handoff.md."""
        peer_dir = self.rooms_dir / "peer"
        (peer_dir / "latest_handoff.md").write_text(
            "# Peer Handoff #88\nState: Closed by dev after tests.\n",
            encoding="utf-8"
        )
        violations = fg.audit_premature_close(peer_dir=peer_dir)
        self.assertGreaterEqual(len(violations), 1)
        self.assertEqual(violations[0]["task_id"], "88")

    def test_stage3_pm_bypass_detected_in_latest_handoff(self):
        """[Stage 3] Verify Supervisor pm_bypass is caught in latest_handoff.md."""
        sup_dir = self.rooms_dir / "supervisor"
        pm_dir = self.rooms_dir / "pm"
        (sup_dir / "latest_handoff.md").write_text(
            "# Supervisor Session\nDispatched Epic #5500 to team directly without PM intake.\n",
            encoding="utf-8"
        )
        violations = fg.audit_pm_bypass(supervisor_dir=sup_dir, pm_dir=pm_dir)
        self.assertGreaterEqual(len(violations), 1)
        self.assertEqual(violations[0]["task_id"], "5500")

    # =========================================================================
    # STAGE 4: CLI EXECUTION CONTRACT & ZERO HARDCODED PATHS
    # =========================================================================

    def test_stage4_cli_execution_flags(self):
        """[Stage 4] Verify slppc_flow_guard.py CLI commands execute cleanly."""
        # 1. Help flag
        res_help = subprocess.run([sys.executable, "tools/slppc_flow_guard.py", "--help"], cwd=str(BASE_DIR), capture_output=True, text=True)
        self.assertEqual(res_help.returncode, 0)
        self.assertIn("hygiene", res_help.stdout)

        # 2. Hygiene command
        res_hyg = subprocess.run([sys.executable, "tools/slppc_flow_guard.py", "hygiene"], cwd=str(BASE_DIR), capture_output=True, text=True)
        self.assertEqual(res_hyg.returncode, 0)
        self.assertIn("EPHEMERAL ROOM HYGIENE AUDIT", res_hyg.stdout)

        # 3. Hygiene --json
        res_json = subprocess.run([sys.executable, "tools/slppc_flow_guard.py", "hygiene", "--json"], cwd=str(BASE_DIR), capture_output=True, text=True)
        self.assertEqual(res_json.returncode, 0)
        data = json.loads(res_json.stdout)
        self.assertIn("hygiene_violations", data)
        self.assertEqual(data["count"], 0)

    def test_stage4_zero_hardcoded_personal_paths(self):
        """[Stage 4] Verify tools/slppc_flow_guard.py has zero hardcoded personal machine paths."""
        source = (BASE_DIR / "tools" / "slppc_flow_guard.py").read_text(encoding="utf-8")
        # Check for specific user machine home directories
        for banned in ("/Users/bao312", "/home/bao312", "/Users/baobao"):
            self.assertNotIn(banned, source, f"Hardcoded path detected: {banned}")

    # =========================================================================
    # STAGE 5: FULL REPOSITORY AUDIT PASS
    # =========================================================================

    def test_stage5_repository_hygiene_and_flow_guard_audit(self):
        """[Stage 5] Run complete slppc_flow_guard.py audit on live repository."""
        res_audit = subprocess.run([sys.executable, "tools/slppc_flow_guard.py", "audit"], cwd=str(BASE_DIR), capture_output=True, text=True)
        self.assertEqual(res_audit.returncode, 0, f"slppc_flow_guard audit failed:\n{res_audit.stdout}\n{res_audit.stderr}")
        self.assertIn("100% tuân thủ mô hình SLPPC", res_audit.stdout)


if __name__ == "__main__":
    unittest.main()
