#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.agent_reprimand as ar


class TestAgentReprimand(unittest.TestCase):
    def test_sanitize_role(self):
        self.assertEqual(ar.sanitize_role("Supervisor (Scope Guard)"), "supervisor")
        self.assertEqual(ar.sanitize_role("Lead Dev"), "lead")
        self.assertEqual(ar.sanitize_role("Peer 1"), "peer")
        self.assertEqual(ar.sanitize_role("QC Verifier"), "qc")
        self.assertEqual(ar.sanitize_role("unknown"), "unknown")

    def test_main_creates_violation_memo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            with patch.object(ar, "PROJECT_ROOT", tmp_root):
                test_args = [
                    "agent_reprimand.py",
                    "--from-role", "supervisor",
                    "--to-role", "lead",
                    "--violation", "hardcoded_hex",
                    "--evidence", "color: #ffffff",
                    "--message", "Do not use hex codes",
                    "--task-id", "999",
                ]
                with patch.object(sys, "argv", test_args):
                    with patch("shutil.which", return_value=None):
                        with patch("harness_manager.HarnessManager") as mock_hm:
                            mock_hm.return_value.add_work_item.return_value = {"id": 9999}
                            ar.main()

                violations_dir = tmp_root / "bmad" / "rooms" / "violations"
                self.assertTrue(violations_dir.exists())
                memos = list(violations_dir.glob("reprimand_999_supervisor_to_lead_*.md"))
                self.assertEqual(len(memos), 1)
                content = memos[0].read_text(encoding="utf-8")
                self.assertIn("HARDCODED_HEX", content)
                self.assertIn("Do not use hex codes", content)
                self.assertIn("color: #ffffff", content)


if __name__ == "__main__":
    unittest.main()
