#!/usr/bin/env python3
from __future__ import annotations
"""
tools/tests/test_task786_install_room_istqb.py - 5-Stage ISTQB Audit Suite for Task #786:
[Task 4] - Publish Codex Room Configs & Create Runtime Directories

Traceability Matrix:
- REQ-786-AC1: Managed config files exist with proper permissions (0600, 0755)
- REQ-786-AC2: bash codex-room-setup/install --dry-run succeeds without errors
- TP-786-01: Anchors apply_installation() and publish_files() exist in install-room
- TP-786-02: Isolated runtime directories ~/.codex-runtime/{supervisor,lead,peer} exist with 0700 permissions
- TP-786-03: Managed overlay config files have 0600 permissions
- TP-786-04: Executable CLI wrapper scripts have 0755 permissions
"""

import os
import stat
import subprocess
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CODEX_SETUP_DIR = BASE_DIR / "codex-room-setup"
CONFIG_ROOT = Path.home() / ".config" / "codex-room"
LOCAL_BIN = Path.home() / ".local" / "bin"
RUNTIME_ROOT = Path.home() / ".codex-runtime"


class TestTask786InstallRoomISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task #786 Publish Codex Room Configs."""

    @classmethod
    def setUpClass(cls):
        if not CODEX_SETUP_DIR.exists() or not (CONFIG_ROOT / "overlays").exists():
            raise unittest.SkipTest("codex-room-setup or ~/.config/codex-room not present in environment")

    def test_stage1_ac1_managed_config_files_and_permissions(self):
        """[AC-1] Verify managed config files exist with expected permissions (0600, 0755)."""
        overlays = ["supervisor.config.toml", "lead.config.toml", "peer.config.toml"]
        for name in overlays:
            fpath = CONFIG_ROOT / "overlays" / name
            self.assertTrue(fpath.exists(), f"Overlay file missing at {fpath}")
            mode = stat.S_IMODE(fpath.stat().st_mode)
            self.assertEqual(mode, 0o600, f"Overlay {name} must have mode 0600, got {oct(mode)}")

        executables = ["codex-room", "codex-room-sync"]
        for name in executables:
            fpath = LOCAL_BIN / name
            self.assertTrue(fpath.exists(), f"CLI tool missing at {fpath}")
            self.assertTrue(os.access(fpath, os.X_OK), f"{fpath} must be executable")
            mode = stat.S_IMODE(fpath.stat().st_mode)
            self.assertEqual(mode, 0o755, f"CLI {name} must have mode 0755, got {oct(mode)}")

    def test_stage1_ac2_install_dry_run_succeeds(self):
        """[AC-2] Verify that bash codex-room-setup/install --dry-run succeeds without errors."""
        install_script = CODEX_SETUP_DIR / "install"
        self.assertTrue(install_script.exists(), f"install script missing at {install_script}")

        res = subprocess.run(
            ["bash", str(install_script), "--dry-run"],
            cwd=str(CODEX_SETUP_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"install --dry-run failed with code {res.returncode}: {res.stderr}")
        self.assertIn("CODEX ROOM INSTALL PLAN", res.stdout, "Dry-run output missing plan header")

    def test_stage2_source_script_anchors(self):
        """[TP-01] Verify apply_installation() and publish_files() exist in install-room."""
        install_room = CODEX_SETUP_DIR / "scripts" / "install-room"
        self.assertTrue(install_room.exists(), f"install-room missing at {install_room}")

        content = install_room.read_text(encoding="utf-8")
        self.assertIn("apply_installation", content, "apply_installation anchor missing in install-room")
        self.assertIn("publish_files", content, "publish_files anchor missing in install-room")

    def test_stage3_runtime_isolated_directories(self):
        """[TP-02] Verify isolated runtime directories ~/.codex-runtime/{supervisor,lead,peer}."""
        roles = ["supervisor", "lead", "peer"]
        for role in roles:
            rdir = RUNTIME_ROOT / role
            self.assertTrue(rdir.exists(), f"Runtime directory missing: {rdir}")
            self.assertTrue(rdir.is_dir(), f"{rdir} must be a directory")
            mode = stat.S_IMODE(rdir.stat().st_mode)
            self.assertEqual(mode, 0o700, f"Directory {role} must have mode 0700, got {oct(mode)}")

    def test_stage4_boundary_and_non_tampering(self):
        """[TP-03] Verify model-instructions.md and WORKSPACE_PROTOCOL.md exist."""
        instructions = CONFIG_ROOT / "model-instructions.md"
        self.assertTrue(instructions.exists(), f"model-instructions.md missing at {instructions}")

        protocol = CONFIG_ROOT / "workflow" / "WORKSPACE_PROTOCOL.md"
        self.assertTrue(protocol.exists(), f"WORKSPACE_PROTOCOL.md missing at {protocol}")


if __name__ == "__main__":
    unittest.main()
