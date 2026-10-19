#!/usr/bin/env python3
"""
tools/tests/test_skill_manager.py - Unit test suite for Paseo Skill Manager.
"""

import os
import sys
import json
import zipfile
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools import skill_manager


class TestSkillManager(unittest.TestCase):
    def setUp(self):
        self.test_skill_name = f"test-sample-skill-{int(os.getpid())}"

    def tearDown(self):
        # Cleanup test skill if created
        test_dir = skill_manager.MASTER_REGISTRY / self.test_skill_name
        if test_dir.exists():
            skill_manager.delete_skill(self.test_skill_name)

    def test_01_add_skill(self):
        """Test creating a new skill via add_skill."""
        res = skill_manager.add_skill(
            name=self.test_skill_name,
            description="Test skill description",
            content="# Test Skill\n1. Do this\n2. Do that"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["skill_name"], self.test_skill_name)

        # Verify file on disk
        skill_file = skill_manager.MASTER_REGISTRY / self.test_skill_name / "SKILL.md"
        self.assertTrue(skill_file.exists())
        content = skill_file.read_text()
        self.assertIn(f"name: {self.test_skill_name}", content)
        self.assertIn("Test skill description", content)

    def test_02_get_all_skills(self):
        """Test listing skills."""
        skills = skill_manager.get_all_skills()
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)
        # Ensure lead-review or paseo is present
        names = [s["name"] for s in skills]
        self.assertTrue("lead-review" in names or "paseo" in names)

    def test_03_upload_skill_zip(self):
        """Test uploading a zipped skill."""
        zip_skill_name = f"zip-test-{int(os.getpid())}"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_folder = tmp_path / zip_skill_name
            source_folder.mkdir()
            (source_folder / "SKILL.md").write_text(
                f"---\nname: {zip_skill_name}\ndescription: Zipped skill\n---\n# Zipped skill instructions\n"
            )

            zip_file = tmp_path / "test.zip"
            with zipfile.ZipFile(zip_file, "w") as z:
                z.write(source_folder / "SKILL.md", arcname=f"{zip_skill_name}/SKILL.md")

            # Upload bytes
            data = zip_file.read_bytes()
            upload_res = skill_manager.upload_skill_archive("test.zip", data)
            self.assertTrue(upload_res["success"])

            # Verify it exists
            dest_file = skill_manager.MASTER_REGISTRY / zip_skill_name / "SKILL.md"
            self.assertTrue(dest_file.exists())

            # Cleanup
            skill_manager.delete_skill(zip_skill_name)
            self.assertFalse(dest_file.exists())

    def test_04_sync_skills(self):
        """Test sync logic across all target directories."""
        sync_res = skill_manager.sync_skills()
        self.assertTrue(sync_res["success"])
        self.assertGreater(sync_res["synced_count"], 0)
        self.assertGreater(sync_res["target_rooms_count"], 0)


if __name__ == "__main__":
    unittest.main()
