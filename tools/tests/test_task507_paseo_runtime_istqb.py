#!/usr/bin/env python3
from __future__ import annotations
"""
tools/tests/test_task507_paseo_runtime_istqb.py - 5-Stage ISTQB Audit Suite for Task #507:
[Task 1] - Setup & Build Paseo v0.8.0 Runtime Symlink

Traceability Matrix:
- REQ-507-AC1: ~/.local/bin/paseo exists and is an executable symlink
- REQ-507-AC2: paseo --version returns 0.8.0
- TP-507-01: codex-room-setup/scripts/install-paseo contains required anchors (install_paseo, build_clean)
- TP-507-02: Target binary resolved from symlink is valid and executable
- TP-507-03: Paseo runtime repository structure verified
"""

import os
import subprocess
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CODEX_SETUP_DIR = BASE_DIR / "codex-room-setup"
PASEO_SYMLINK = Path.home() / ".local" / "bin" / "paseo"
PASEO_REPO_DIR = Path.home() / "projects" / "supervisors" / "paseo"


class TestTask507PaseoRuntimeISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task #507 Paseo Runtime Symlink Verification."""

    def test_stage1_ac1_symlink_exists_and_executable(self):
        """[AC-1] Verify ~/.local/bin/paseo exists and is executable."""
        self.assertTrue(PASEO_SYMLINK.exists(), f"Symlink missing at {PASEO_SYMLINK}")
        self.assertTrue(PASEO_SYMLINK.is_symlink(), f"{PASEO_SYMLINK} is not a symlink")
        self.assertTrue(os.access(PASEO_SYMLINK, os.X_OK), f"{PASEO_SYMLINK} must be executable")

    def test_stage1_ac2_version_returns_0_8_0(self):
        """[AC-2] Verify paseo --version returns 0.8.0."""
        res = subprocess.run(
            [str(PASEO_SYMLINK), "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        self.assertEqual(res.returncode, 0, f"paseo --version failed: {res.stderr}")
        self.assertIn("0.8.0", res.stdout.strip())

    def test_stage2_source_script_anchors(self):
        """[TP-01] Verify install-paseo script exists, is executable, and contains anchors."""
        script_path = CODEX_SETUP_DIR / "scripts" / "install-paseo"
        self.assertTrue(script_path.exists(), f"install-paseo missing at {script_path}")
        self.assertTrue(os.access(script_path, os.X_OK), "install-paseo must be executable")

        content = script_path.read_text(encoding="utf-8")
        self.assertIn("install_paseo", content, "Anchor install_paseo missing in install-paseo")
        self.assertIn("build_clean", content, "Anchor build_clean missing in install-paseo")

    def test_stage3_symlink_target_validity(self):
        """[TP-02] Verify symlink resolves to a real target file with execute permissions."""
        resolved = PASEO_SYMLINK.resolve()
        self.assertTrue(resolved.exists(), f"Resolved target does not exist: {resolved}")
        self.assertTrue(os.access(resolved, os.X_OK), f"Resolved target not executable: {resolved}")
        self.assertIn("paseo", resolved.name)

    def test_stage4_runtime_dir_structure(self):
        """[TP-03] Verify Paseo project directory structure in ~/projects/supervisors/paseo."""
        self.assertTrue(PASEO_REPO_DIR.exists(), f"Paseo repo directory missing at {PASEO_REPO_DIR}")
        cli_bin = PASEO_REPO_DIR / "packages" / "cli" / "bin" / "paseo"
        self.assertTrue(cli_bin.exists(), f"Paseo CLI binary missing at {cli_bin}")


if __name__ == "__main__":
    unittest.main()
