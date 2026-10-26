#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.record_discussion as rd


class TestRecordDiscussion(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(rd.slugify("Nguyên Tắc Thiết Kế!"), "nguyên_tắc_thiết_kế")
        self.assertEqual(rd.slugify("Architecture Review - Task 101"), "architecture_review_task_101")
        self.assertEqual(rd.slugify(""), "discussion")

    def test_main_creates_minutes_and_adr(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            tmp_disc = tmp_root / "bmad" / "rooms" / "discussions"
            tmp_adr = tmp_root / "bmad" / "adrs"

            with patch.object(rd, "DISCUSSIONS_DIR", tmp_disc):
                with patch.object(rd, "ADR_DIR", tmp_adr):
                    test_args = [
                        "record_discussion.py",
                        "--task-id", "889",
                        "--topic", "State Management Strategy",
                        "--parties", "Peer, Lead",
                        "--conflict", "Component store vs signal store",
                        "--consensus", "Use signal store for Angular 18",
                        "--actions", "- Refactor current stores",
                        "--adr",
                    ]
                    with patch.object(sys, "argv", test_args):
                        rd.main()

                    latest = tmp_disc / "latest_discussion.md"
                    self.assertTrue(latest.exists())
                    latest_content = latest.read_text(encoding="utf-8")
                    self.assertIn("#889", latest_content)
                    self.assertIn("State Management Strategy", latest_content)
                    self.assertIn("Use signal store for Angular 18", latest_content)

                    # Check ADR creation
                    adr_files = list(tmp_adr.glob("ADR-889-*.md"))
                    self.assertEqual(len(adr_files), 1)
                    adr_content = adr_files[0].read_text(encoding="utf-8")
                    self.assertIn("State Management Strategy", adr_content)
                    self.assertIn("Accepted", adr_content)


if __name__ == "__main__":
    unittest.main()
