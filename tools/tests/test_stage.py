#!/usr/bin/env python3
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.stage as stage_tool


class TestStage(unittest.TestCase):
    def test_stage_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "isolated_workspace"
            dest = stage_tool.stage(target)
            self.assertEqual(dest, target.resolve())
            self.assertTrue(target.exists())
            self.assertTrue((target / "skills").exists())
            self.assertTrue((target / "profiles").exists())
            self.assertTrue((target / "bmad" / "rooms" / "supervisor").exists())
            self.assertTrue((target / "bmad" / "rooms" / "qc").exists())

    def test_stage_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "already_exists"
            target.mkdir()
            with self.assertRaises(FileExistsError):
                stage_tool.stage(target)

    def test_stage_refuses_nonexistent_parent(self):
        nonexistent = Path("/non/existent/parent/dir/target")
        with self.assertRaises(ValueError):
            stage_tool.stage(nonexistent)

    def test_stage_cleanup_on_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "fail_target"
            with patch("shutil.copytree", side_effect=RuntimeError("Copy failed")):
                with self.assertRaises(RuntimeError):
                    stage_tool.stage(target)
            self.assertFalse(target.exists())

    def test_main_cli(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "cli_workspace"
            with patch("sys.argv", ["stage.py", str(target)]):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    stage_tool.main()
                    self.assertIn("Successfully staged isolated sandbox", fake_out.getvalue())
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
