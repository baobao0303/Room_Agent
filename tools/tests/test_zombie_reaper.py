#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import tools.zombie_reaper as zr


class TestZombieReaper(unittest.TestCase):
    def test_run_cmd(self):
        res = zr.run_cmd(["echo", "hello"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("hello", res.stdout)

    @patch("shutil.which", return_value=None)
    def test_get_orca_terminals_no_orca(self, mock_which):
        terminals = zr.get_orca_terminals()
        self.assertEqual(terminals, [])

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("tools.zombie_reaper.run_cmd")
    def test_get_orca_terminals_success(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"terminals": [{"id": "term1", "title": "peer"}]}}),
        )
        terminals = zr.get_orca_terminals()
        self.assertEqual(len(terminals), 1)
        self.assertEqual(terminals[0]["id"], "term1")

    def test_get_registered_handles_no_file(self):
        with patch.object(zr, "REG_FILE", Path("/non/existent/path/agent_terminals.json")):
            handles = zr.get_registered_handles()
            self.assertEqual(handles, {})

    def test_get_registered_handles_with_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp.write(json.dumps({"peer": "term_123", "qc": "term_456"}))
            tmp_path = Path(tmp.name)
        try:
            with patch.object(zr, "REG_FILE", tmp_path):
                handles = zr.get_registered_handles()
                self.assertEqual(handles.get("term_123"), "peer")
                self.assertEqual(handles.get("term_456"), "qc")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_close_and_interrupt_terminal_dry_run(self):
        self.assertTrue(zr.close_terminal("term_123", dry_run=True))
        self.assertTrue(zr.interrupt_terminal("term_123", dry_run=True))

    @patch("tools.zombie_reaper.get_orca_terminals")
    @patch("tools.zombie_reaper.get_registered_handles")
    def test_audit_and_reap_dry_run(self, mock_handles, mock_terms):
        mock_terms.return_value = [
            {"handle": "term_subagent", "title": "Subagent Task #101"},
            {"handle": "term_keep", "title": "Supervisor"},
        ]
        mock_handles.return_value = {"term_keep": "supervisor"}

        report = zr.audit_and_reap(dry_run=True, timeout_s=300)
        self.assertEqual(report["total_active_terminals"], 2)
        self.assertEqual(report["zombies_detected"], 1)
        self.assertEqual(report["registered_agents"], 1)


if __name__ == "__main__":
    unittest.main()
