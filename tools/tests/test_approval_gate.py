#!/usr/bin/env python3
"""
tools/tests/test_approval_gate.py - Unit test suite for One-Key Approval Gate.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys_path = str(BASE_DIR / "tools")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from approval_gate import create_approval_request, approve_request, verify_approval, APPROVALS_DIR  # type: ignore


class TestApprovalGate(unittest.TestCase):
    """Test cryptographic approval workflow: request -> approve -> verify."""

    def test_workflow_lifecycle(self):
        # 1. Create request
        req = create_approval_request("git push origin main", risk="critical", requested_by="peer")
        req_id = req["id"]
        self.assertTrue(req_id.startswith("appr_"))
        self.assertEqual(req["status"], "pending")

        # 2. Verify should fail before approval
        unapproved = verify_approval(req_id)
        self.assertFalse(unapproved["valid"])
        self.assertIn("chưa được duyệt", unapproved["reason"])

        # 3. Approve request
        appr = approve_request(req_id, approver="human")
        self.assertEqual(appr["status"], "success")

        # 4. Verify should succeed after approval
        verified = verify_approval(req_id)
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["approved_by"], "human")
        self.assertEqual(verified["action"], "git push origin main")

        # Clean up test file
        test_file = APPROVALS_DIR / f"{req_id}.json"
        test_file.unlink(missing_ok=True)

    def test_verify_nonexistent_token(self):
        res = verify_approval("appr_nonexistent_12345")
        self.assertFalse(res["valid"])
        self.assertIn("Không tồn tại token", res["reason"])


if __name__ == "__main__":
    unittest.main()
