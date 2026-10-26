#!/usr/bin/env python3
"""
tools/tests/test_slppc_flow_guard.py - Unit test suite for SLPC Flow Guard & 4-Role Model Compliance.
"""
import unittest
from pathlib import Path
from tools.slppc_flow_guard import run_slppc_audit, run_audit


class TestSlppcFlowGuard(unittest.TestCase):
    def test_flow_guard_audit_runs_clean_without_pm_checks(self):
        """Verify audit executes cleanly and violation types contain no pm_bypass."""
        res = run_slppc_audit(auto_record=False)
        self.assertIn("violations_detected", res)
        self.assertIn("violations_list", res)

        violation_types = [v.get("type") for v in res.get("violations_list", [])]
        self.assertNotIn("pm_bypass", violation_types)

        # Verify from/to roles only reference canonical roles
        for v in res.get("violations_list", []):
            self.assertNotEqual(v.get("from"), "PM")
            self.assertNotEqual(v.get("to"), "PM")

    def test_run_audit_alias_exists(self):
        """Verify run_audit alias works identically to run_slppc_audit."""
        self.assertEqual(run_audit, run_slppc_audit)


if __name__ == "__main__":
    unittest.main()
