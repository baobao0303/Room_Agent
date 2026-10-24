#!/usr/bin/env python3
from __future__ import annotations
"""
tools/tests/test_task509_mechanical_verification_istqb.py - 5-Stage ISTQB Audit Suite for Task #509:
[Task 3] - Mechanical Verification & Doctor Health Check

Traceability Matrix:
- REQ-509-AC1: ./scripts/verify --source passes 100% (exit 0, outputs VERIFY_OK)
- REQ-509-AC2: ./scripts/doctor exits 0 (outputs DOCTOR_OK)
- REQ-509-AC3: slppc_flow_guard audit reports 0 violations (PASS 100%)
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CODEX_SETUP_DIR = BASE_DIR / "codex-room-setup"


class TestTask509MechanicalVerificationISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task #509 Mechanical Verification."""

    def test_stage1_ac1_verify_source_passes(self):
        """[AC-1] Verify that ./scripts/verify --source exits 0 and passes 100%."""
        verify_script = CODEX_SETUP_DIR / "scripts" / "verify"
        self.assertTrue(verify_script.exists(), f"verify script missing at {verify_script}")
        self.assertTrue(os.access(verify_script, os.X_OK), "verify script must be executable")

        res = subprocess.run(
            [str(verify_script), "--source"],
            cwd=str(CODEX_SETUP_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"verify --source failed with exit code {res.returncode}: {res.stderr}")
        self.assertIn("VERIFY_OK", res.stdout, "verify output must end with VERIFY_OK")

    def test_stage1_ac2_doctor_health_check_exits_zero(self):
        """[AC-2] Verify that ./scripts/doctor exits 0 and reports DOCTOR_OK."""
        doctor_script = CODEX_SETUP_DIR / "scripts" / "doctor"
        self.assertTrue(doctor_script.exists(), f"doctor script missing at {doctor_script}")
        self.assertTrue(os.access(doctor_script, os.X_OK), "doctor script must be executable")

        res = subprocess.run(
            [str(doctor_script)],
            cwd=str(CODEX_SETUP_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"doctor failed with exit code {res.returncode}: {res.stderr}")
        self.assertIn("DOCTOR_OK", res.stdout, "doctor output must include DOCTOR_OK")

    def test_stage1_ac3_slppc_flow_guard_zero_violations(self):
        """[AC-3] Verify that slppc_flow_guard audit reports 0 violations."""
        flow_guard = BASE_DIR / "tools" / "slppc_flow_guard.py"
        self.assertTrue(flow_guard.exists(), f"slppc_flow_guard.py missing at {flow_guard}")

        res = subprocess.run(
            [sys.executable, str(flow_guard), "audit", "--json"],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"slppc_flow_guard failed with exit code {res.returncode}")
        self.assertIn('"violations_detected": 0', res.stdout, "violations_detected must be 0")

    def test_stage2_non_interactive_execution(self):
        """[Stage 2] Verify doctor script executes non-interactively without stdin."""
        doctor_script = CODEX_SETUP_DIR / "scripts" / "doctor"
        res = subprocess.run(
            [str(doctor_script)],
            cwd=str(CODEX_SETUP_DIR),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("DOCTOR_OK", res.stdout)


if __name__ == "__main__":
    unittest.main()
