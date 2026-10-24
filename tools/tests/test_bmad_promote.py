#!/usr/bin/env python3
"""
tools/tests/test_bmad_promote.py - Unit test suite for BMAD Promotion Gate.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys_path = str(BASE_DIR / "tools")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from bmad_promote import promote_draft, slugify, validate_draft_content  # type: ignore


class TestBmadPromote(unittest.TestCase):
    """Test verification of BMAD Promotion Gate."""

    def test_slugify(self):
        self.assertEqual(slugify("Hello World Architecture!"), "hello-world-architecture")
        self.assertEqual(slugify("  Module Federation & Micro-Frontends  "), "module-federation-micro-frontends")

    def test_validation_rejects_too_short(self):
        short = "# Title\nLine 1\n"
        errors = validate_draft_content(short)
        self.assertTrue(any("quá ngắn" in e for e in errors))

    def test_validation_rejects_missing_heading(self):
        no_h1 = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        errors = validate_draft_content(no_h1)
        self.assertTrue(any("tiêu đề Markdown cấp 1" in e for e in errors))

    def test_validation_rejects_leak(self):
        leaked = "# Title\nLine 1\nLine 2\nLine 3\npassword = 'super_secret_123'\n"
        errors = validate_draft_content(leaked)
        self.assertTrue(any("rò rỉ" in e for e in errors))

    def test_rejection_unauthorized_reviewer(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tf:
            tf.write("# Test Spec\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
            tf.flush()
            temp_path = tf.name

        try:
            res = promote_draft(
                draft_path=temp_path,
                domain="architecture",
                title="Test Spec",
                reviewer="peer"  # Peer is forbidden from self-promotion
            )
            self.assertEqual(res["status"], "error")
            self.assertIn("Thẩm quyền không hợp lệ", res["message"])
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_successful_dry_run(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tf:
            tf.write("# Clean Architecture\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
            tf.flush()
            temp_path = tf.name

        try:
            res = promote_draft(
                draft_path=temp_path,
                domain="architecture",
                title="Clean Architecture",
                reviewer="lead",
                dry_run=True
            )
            self.assertEqual(res["status"], "dry_run")
            self.assertIn("clean-architecture.md", res["target_article"])
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
