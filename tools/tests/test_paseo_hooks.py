#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import importlib.util

import tools.paseo_hooks as ph_wrapper

spec = importlib.util.spec_from_file_location("paseo_hooks_plugin", ph_wrapper.TARGET)
ph = importlib.util.module_from_spec(spec)
sys.modules["paseo_hooks_plugin"] = ph
spec.loader.exec_module(ph)


class TestPaseoHooks(unittest.TestCase):
    def test_wrapper_target_exists(self):
        self.assertTrue(ph_wrapper.TARGET.exists())

    @patch("subprocess.call")
    def test_wrapper_main_forwards(self, mock_call):
        mock_call.return_value = 0
        with patch.object(sys, "argv", ["paseo_hooks.py", "--help"]):
            with self.assertRaises(SystemExit) as cm:
                ph_wrapper.main()
            self.assertEqual(cm.exception.code, 0)
        mock_call.assert_called_once()

    def test_infer_slpc_role(self):
        self.assertEqual(ph.infer_slpc_role("Supervisor agent active"), "Supervisor")
        self.assertEqual(ph.infer_slpc_role("PM task review"), "PM")
        self.assertEqual(ph.infer_slpc_role("Product Manager spec"), "PM")
        self.assertEqual(ph.infer_slpc_role("QC validation run"), "QC")
        self.assertEqual(ph.infer_slpc_role("ISTQB test runner"), "QC")
        self.assertEqual(ph.infer_slpc_role("Lead architecture"), "Lead")
        self.assertEqual(ph.infer_slpc_role("[Lead Dev] Architect & PM"), "Lead")
        self.assertEqual(ph.infer_slpc_role("⠋ Hermes /Users/test/orca/workspaces/Room_Agent/room-pm"), "PM")
        self.assertEqual(ph.infer_slpc_role("⠋ Hermes /Users/test/orca/workspaces/Room_Agent/room-lead"), "Lead")
        self.assertEqual(ph.infer_slpc_role("Peer dev code"), "Peer")
        self.assertEqual(ph.infer_slpc_role("Security Sentinel scan"), "Security Sentinel")
        self.assertIsNone(ph.infer_slpc_role("Random string"))

    def test_redact_sensitive(self):
        raw = {
            "name": "agent1",
            "api_key": "secret123",
            "token": "tok_abc",
            "password": "pass",
            "env": {"FOO": "BAR", "PORT": "8080"},
            "nested": [
                {"secret_data": "hidden", "public_data": "visible"}
            ]
        }
        sanitized = ph.redact_sensitive(raw)
        self.assertEqual(sanitized["name"], "agent1")
        self.assertEqual(sanitized["api_key"], "[redacted]")
        self.assertEqual(sanitized["token"], "[redacted]")
        self.assertEqual(sanitized["password"], "[redacted]")
        self.assertEqual(sanitized["env"]["FOO"], "[redacted]")
        self.assertEqual(sanitized["env"]["PORT"], "[redacted]")
        self.assertEqual(sanitized["nested"][0]["secret_data"], "[redacted]")
        self.assertEqual(sanitized["nested"][0]["public_data"], "visible")

    def test_append_hook_log(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_log = Path(tmp_dir) / ".harness_hooks.jsonl"
            with patch.object(ph, "HOOKS_LOG_FILE", tmp_log):
                ph.append_hook_log({"event": "test_event", "token": "sensitive"})
                self.assertTrue(tmp_log.exists())
                lines = tmp_log.read_text(encoding="utf-8").strip().splitlines()
                self.assertEqual(len(lines), 1)
                data = json.loads(lines[0])
                self.assertEqual(data["event"], "test_event")
                self.assertEqual(data["token"], "[redacted]")
                self.assertIn("timestamp", data)

    @patch("subprocess.run")
    def test_trigger_research_gen(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        mock_script = MagicMock()
        mock_script.exists.return_value = True
        with patch.object(ph, "PROFILE_RESEARCH_GEN_SCRIPT", mock_script):
            res = ph.trigger_research_gen("Lead", "Architecture review")
            self.assertTrue(res["triggered"])
            self.assertEqual(res["exit_code"], 0)
            mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_log_to_agent_progress(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        mock_script = MagicMock()
        mock_script.exists.return_value = True
        with patch.object(ph, "AGENT_PROGRESS_SCRIPT", mock_script):
            ph.log_to_agent_progress("Lead", "Summary text", "Done item", "Next step")
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertIn("--agent", args)
            self.assertIn("Lead", args)
            self.assertIn("--next", args)


if __name__ == "__main__":
    unittest.main()
