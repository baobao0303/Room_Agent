#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import tools.orca_slpc_bridge as osb


class TestOrcaSlpcBridge(unittest.TestCase):
    def test_state_map(self):
        self.assertEqual(osb.STATE_MAP["New"], "todo")
        self.assertEqual(osb.STATE_MAP["Active"], "in-progress")
        self.assertEqual(osb.STATE_MAP["Resolved"], "in-review")
        self.assertEqual(osb.STATE_MAP["Closed"], "completed")

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_sync_board_status(self, mock_run, _mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")
        osb.sync_board_status("501", "Active", "active")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("--workspace-status", args)
        self.assertIn("in-progress", args)

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    @patch("tools.orca_slpc_bridge.HarnessManager")
    def test_cmd_init_run(self, mock_mgr_cls, mock_run, _mock_which):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"runId": "run-test-123"}}),
            stderr="",
        )
        mock_mgr = MagicMock()
        mock_mgr.add_work_item.return_value = {"id": 888}
        mock_mgr_cls.return_value = mock_mgr

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            with patch.object(osb, "PROJECT_ROOT", tmp_root):
                with patch.object(osb, "sync_board_status") as mock_sync:
                    res = osb.cmd_init_run("test-run", "Test Epic Title")
                    self.assertEqual(res["run_id"], "run-test-123")
                    self.assertEqual(res["epic_id"], 888)
                    mock_sync.assert_called_once_with("888", "Active")

                    handoff = tmp_root / "bmad" / "rooms" / "tasks" / "888" / "handoff_supervisor.md"
                    self.assertTrue(handoff.exists())
                    self.assertIn("run-test-123", handoff.read_text(encoding="utf-8"))

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    @patch("tools.orca_slpc_bridge.HarnessManager")
    def test_cmd_create_task(self, mock_mgr_cls, mock_run, _mock_which):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=json.dumps({"result": {"taskId": "orca-task-1"}})),
            MagicMock(returncode=0, stdout=json.dumps({"result": {"gateId": "orca-gate-1"}})),
        ]
        mock_mgr = MagicMock()
        mock_mgr.add_work_item.return_value = {"id": 889}
        mock_mgr_cls.return_value = mock_mgr

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            with patch.object(osb, "PROJECT_ROOT", tmp_root):
                res = osb.cmd_create_task(
                    run_id="run-123",
                    parent_id="888",
                    title="Implement service",
                    spec="Detail specs here",
                )
                self.assertEqual(res["task_id"], 889)
                self.assertEqual(res["orca_task_id"], "orca-task-1")
                self.assertEqual(res["gate_id"], "orca-gate-1")

                memo = tmp_root / "bmad" / "rooms" / "tasks" / "889" / "latest_handoff.md"
                self.assertTrue(memo.exists())
                content = memo.read_text(encoding="utf-8")
                self.assertIn("TASK #889", content)
                self.assertIn("orca-gate-1", content)

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_find_live_terminal_for_role_from_registry(self, mock_run, _mock_which):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "result": {
                    "terminals": [
                        {"handle": "term-lead-1", "tabId": "tab-1", "title": "Lead Terminal"}
                    ]
                }
            }),
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            reg_dir = tmp_root / "bmad" / "rooms"
            reg_dir.mkdir(parents=True, exist_ok=True)
            reg_file = reg_dir / "agent_terminals.json"
            reg_file.write_text(json.dumps({"lead": {"handle": "term-lead-1"}}), encoding="utf-8")

            with patch.object(osb, "PROJECT_ROOT", tmp_root):
                handle = osb.find_live_terminal_for_role("Lead Dev")
                self.assertEqual(handle, "term-lead-1")

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_send_to_terminal_safely(self, mock_run, _mock_which):
        osb.send_to_terminal_safely("term-123", "echo 'hello'", wait_timeout_ms=100)
        self.assertEqual(mock_run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
