#!/usr/bin/env python3
"""
tools/tests/test_smoke_discovery.py - Unit test suite for smoke discovery and sandbox staging.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "tools"))

from smoke_discovery import check_skills, check_profiles, check_plugins  # type: ignore
from stage import stage  # type: ignore


class TestSmokeDiscoveryAndStaging(unittest.TestCase):
    """Test verification of offline discovery and sandbox staging."""

    def test_skills_discovery(self):
        skills_map = check_skills(BASE_DIR / "skills")
        self.assertIn("supervisor", skills_map)
        self.assertIn("lead", skills_map)
        self.assertIn("peer", skills_map)
        self.assertIn("qc", skills_map)
        total_skills = sum(len(items) for items in skills_map.values())
        self.assertGreaterEqual(total_skills, 50, "Expected at least 50 skills")

    def test_profiles_discovery(self):
        profiles = check_profiles(BASE_DIR / "profiles")
        names = [p["name"] for p in profiles]
        self.assertIn("Supervisor", names)
        self.assertIn("Lead", names)
        self.assertIn("PM", names)
        self.assertIn("Peer", names)
        self.assertIn("QC", names)
        self.assertEqual(len(profiles), 5, "Expected 5 SLPPC profiles")

    def test_plugins_discovery(self):
        plugins = check_plugins(BASE_DIR / "plugins")
        ids = [p["id"] for p in plugins]
        self.assertIn("slpc-lifecycle-hooks", ids)

    def test_sandbox_staging(self):
        with tempfile.TemporaryDirectory(prefix="room-stage-test-") as tmpdir:
            dest = stage(Path(tmpdir) / "sandbox")
            self.assertTrue(dest.is_dir())
            self.assertTrue((dest / "skills").is_dir())
            self.assertTrue((dest / "profiles").is_dir())
            self.assertTrue((dest / "plugins").is_dir())
            self.assertTrue((dest / "WORKSPACE_PROTOCOL.md").is_file())


if __name__ == "__main__":
    unittest.main()
