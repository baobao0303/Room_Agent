#!/usr/bin/env python3
"""
tools/tests/test_diagnostics_visibility.py - Tests for Milestone 3 failure visibility:
- G-AGT-1 & G-MEM-4: Unswallowing rehydration and command execution errors.
- G-CTX-1: Missing RTK binary warning.
"""
from __future__ import annotations

import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.agent_start as ags


class TestDiagnosticsVisibility(unittest.TestCase):
    def test_rtk_profile_env_warning_on_missing(self):
        script_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "rtk_profile_env.sh"
        res = subprocess.run(
            ["bash", str(script_path), "peer"],
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin", "HOME": "/tmp"},
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("[WARN] rtk binary not found on PATH; falling back to unproxied commands", res.stderr)

    def test_run_cmd_preserves_stderr(self):
        code, out = ags.run_cmd(["python3", "-c", "import sys; sys.stderr.write('explicit error msg'); sys.exit(2)"])
        self.assertEqual(code, 2)
        self.assertIn("explicit error msg", out)

    def test_rehydration_failure_logged_to_stderr(self):
        import tools.agent_context_manager as acm
        sys.modules["agent_context_manager"] = acm
        with patch("sys.stderr", new=io.StringIO()) as fake_stderr:
            with patch("scripts.agent_start.run_cmd", return_value=(0, '{"result": {"outcome": {"handle": "term_123"}}}')):
                with patch("scripts.agent_start.get_live_terminals", return_value={}):
                    with patch("scripts.agent_start.load_registry", return_value={}):
                        with patch("scripts.agent_start.save_registry"):
                            with patch.object(acm, "build_rehydration_prompt", side_effect=RuntimeError("Forced DB Error")):
                                ags.launch_single("peer", {}, {})
                                err_val = fake_stderr.getvalue()
                                self.assertIn("⚠️ [WARN] Memory rehydration failed for role 'peer': Forced DB Error", err_val)



if __name__ == "__main__":
    unittest.main()
