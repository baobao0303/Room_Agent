#!/usr/bin/env python3
"""
tools/tests/test_slppc_orchestrator.py - Unit Test Suite for Autonomous SLPPC Orchestrator.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PLUGIN_DIR = BASE_DIR / "plugins" / "slpc-lifecycle-hooks"
sys.path.insert(0, str(PLUGIN_DIR))
sys.path.insert(0, str(BASE_DIR / "tools"))
sys.path.insert(0, str(BASE_DIR))

from slppc_orchestrator import SlppcOrchestrator  # type: ignore


class TestSlppcOrchestrator(unittest.TestCase):
    """Test suite for autonomous state navigation in SLPPC."""

    def setUp(self):
        self.orch = SlppcOrchestrator(BASE_DIR)

    def test_registry_operations(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_orch = SlppcOrchestrator(Path(tmp_dir))
            reg = tmp_orch.get_terminals_registry()
            self.assertIsInstance(reg, dict)
            reg["supervisor"] = {"handle": "term_test", "tabId": "tab_test"}
            tmp_orch.save_terminals_registry(reg)
            loaded = tmp_orch.get_terminals_registry()
            self.assertIn("supervisor", loaded)
            self.assertEqual(loaded["supervisor"]["handle"], "term_test")

    def test_feasibility_evaluation_structure(self):
        eval_res = self.orch.evaluate_feasibility("Sample task for testing")
        self.assertIn("feasibility_score", eval_res)
        self.assertIn("alignment", eval_res)
        self.assertIn("risk_lane", eval_res)
        self.assertGreaterEqual(eval_res["feasibility_score"], 0.0)

    @patch.object(SlppcOrchestrator, "spawn_ephemeral_subagent", return_value="term_mock")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role", return_value="term_existing")
    @patch.object(SlppcOrchestrator, "send_terminal_safely", return_value=True)
    def test_supervisor_ended_flow(self, mock_send, mock_find, mock_spawn):
        res = self.orch.handle_supervisor_ended({})
        self.assertEqual(res.get("stage"), "supervisor_to_pm_lead")
        self.assertIn("evaluation", res)
        # Check decision memo created
        memo_path = BASE_DIR / "bmad" / "rooms" / "pm" / "decision_memo.md"
        self.assertTrue(memo_path.is_file())
        mock_spawn.assert_not_called()

    @patch.object(SlppcOrchestrator, "spawn_ephemeral_subagent", return_value="term_lead_mock")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role", return_value="term_lead_existing")
    @patch.object(SlppcOrchestrator, "send_terminal_safely", return_value=True)
    def test_pm_ended_flow(self, mock_send, mock_find, mock_spawn):
        res = self.orch.handle_pm_ended({})
        self.assertEqual(res.get("stage"), "pm_to_lead")
        mock_spawn.assert_not_called()

    def test_single_agent_per_room_deduplication_and_worktree_isolation(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_orch = SlppcOrchestrator(Path(tmp_dir))
            fake_list_out = json.dumps({
                "result": {
                    "terminals": [
                        {
                            "handle": "term_lead_1",
                            "tabId": "tab_lead_1",
                            "worktreePath": "/Users/test/orca/workspaces/Room_Agent/room-lead",
                            "branch": "refs/heads/room-lead",
                            "title": "[Lead Dev] Architect & PM",
                            "connected": True,
                            "lastOutputAt": 200,
                        },
                        {
                            "handle": "term_pm_old",
                            "tabId": "tab_pm_old",
                            "worktreePath": "/Users/test/orca/workspaces/Room_Agent/room-pm",
                            "branch": "refs/heads/room-pm",
                            "title": "[PM] Feasibility & Alignment",
                            "connected": True,
                            "lastOutputAt": 100,
                        },
                        {
                            "handle": "term_pm_new",
                            "tabId": "tab_pm_new",
                            "worktreePath": "/Users/test/orca/workspaces/Room_Agent/room-pm",
                            "branch": "refs/heads/room-pm",
                            "title": "⠋ Hermes",
                            "connected": True,
                            "lastOutputAt": 300,
                        },
                    ]
                }
            })
            with patch("shutil.which", return_value="/fake/orca"), \
                 patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=fake_list_out)), \
                 patch.object(tmp_orch, "close_terminal", return_value=True) as mock_close:
                pm_h = tmp_orch.find_live_terminal_for_role("pm")
                # Phải chọn đúng terminal mới nhất trong room-pm (không bị nhầm sang room-lead dù title Lead có chữ PM)
                self.assertEqual(pm_h, "term_pm_new")
                # Phải tự động đóng terminal thứ 2 dư thừa trong room-pm
                mock_close.assert_called_once_with("term_pm_old")

    def test_unmapped_role_route(self):
        res = self.orch.route_turn_ended("unknown_role")
        self.assertEqual(res.get("stage"), "unmapped")

    @patch("slppc_orchestrator.query_lessons")
    @patch.object(SlppcOrchestrator, "spawn_ephemeral_subagent", return_value="sub_peer_123")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role", return_value=None)
    def test_lead_ended_self_learning_injection(self, mock_find, mock_spawn, mock_query):
        from dataclasses import dataclass

        @dataclass
        class MockLesson:
            cue: str
            lesson: str

        mock_query.return_value = [
            MockLesson(cue="avoid_eval", lesson="Never use eval in python scripts.")
        ]
        mock_mgr = MagicMock()
        mock_mgr.list_work_items.return_value = [
            {
                "id": "100",
                "title": "Build Secure Parser",
                "description": "Parse input safely",
                "state": "New",
                "assigned_to_profile": "peer",
                "domain": "security"
            }
        ]
        self.orch.mgr = mock_mgr

        res = self.orch.handle_lead_ended({})
        self.assertEqual(res.get("stage"), "lead_to_peer")
        self.assertEqual(res.get("action"), "spawned_ephemeral_peer")

        mock_spawn.assert_called_once()
        call_kwargs = mock_spawn.call_args[1]
        prompt = call_kwargs.get("prompt", "")
        self.assertIn("[BẪY QUÁ KHỨ & BÀI HỌC KINH NGHIỆM TỰ HỌC - HARNESS²]", prompt)
        self.assertIn("Never use eval in python scripts.", prompt)

    @patch("slppc_orchestrator.record_lesson")
    @patch.object(SlppcOrchestrator, "spawn_ephemeral_subagent", return_value="sub_qc_123")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role", return_value=None)
    def test_peer_ended_self_learning_extraction(self, mock_find, mock_spawn, mock_record):
        mock_mgr = MagicMock()
        mock_mgr.list_work_items.return_value = [
            {
                "id": "101",
                "title": "Fix Auth Bug",
                "state": "Resolved",
                "domain": "authentication"
            }
        ]
        self.orch.mgr = mock_mgr

        res = self.orch.handle_peer_ended({})
        self.assertEqual(res.get("stage"), "peer_to_qc")
        self.assertEqual(res.get("action"), "closed_peer_and_spawned_qc")

        mock_record.assert_called_once()
        rec_args = mock_record.call_args[1]
        self.assertEqual(rec_args.get("domain"), "authentication")
        self.assertEqual(rec_args.get("cue"), "task_101_peer_resolved")
        self.assertEqual(rec_args.get("work_item_id"), "101")

    @patch("slppc_orchestrator.record_lesson")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role", return_value=None)
    def test_qc_ended_self_learning_extraction(self, mock_find, mock_record):
        mock_mgr = MagicMock()
        mock_mgr.list_work_items.return_value = [
            {
                "id": "102",
                "title": "Verify Encryption Protocol",
                "state": "Closed",
                "domain": "crypto_qc"
            }
        ]
        self.orch.mgr = mock_mgr

        res = self.orch.handle_qc_ended({})
        self.assertEqual(res.get("stage"), "qc_to_supervisor")

        mock_record.assert_called_once()
        rec_args = mock_record.call_args[1]
        self.assertEqual(rec_args.get("domain"), "crypto_qc")
        self.assertEqual(rec_args.get("cue"), "task_102_qc_verified")
        self.assertEqual(rec_args.get("work_item_id"), "102")

    @patch("shutil.which", return_value="/fake/orca")
    @patch("subprocess.run")
    def test_cleanup_role_worktree_permissions(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)

        # Duy nhất Supervisor (main) là Persistent tab được bảo vệ
        self.assertFalse(self.orch.cleanup_role_worktree("supervisor"))
        self.assertFalse(self.orch.cleanup_role_worktree("main"))

        # 4 phòng Sub-Agents (PM, Lead, Peer, QC) đều được phép tự đóng khi xong việc
        self.assertTrue(self.orch.cleanup_role_worktree("pm"))
        self.assertTrue(self.orch.cleanup_role_worktree("lead"))
        self.assertTrue(self.orch.cleanup_role_worktree("peer"))
        mock_run.assert_called_with(
            ["orca", "terminal", "close", "--worktree", "name:room-peer", "--all", "--json"],
            capture_output=True,
            timeout=5
        )

        self.assertTrue(self.orch.cleanup_role_worktree("qc"))
        mock_run.assert_called_with(
            ["orca", "terminal", "close", "--worktree", "name:room-qc", "--all", "--json"],
            capture_output=True,
            timeout=5
        )

    @patch.object(SlppcOrchestrator, "cleanup_role_worktree")
    @patch.object(SlppcOrchestrator, "close_terminal")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role")
    @patch.object(SlppcOrchestrator, "send_terminal_safely", return_value=True)
    def test_pm_ended_auto_closes_pm(self, mock_send, mock_find, mock_close, mock_cleanup):
        def find_side_effect(role):
            if role == "lead":
                return "term_lead_123"
            if role == "pm":
                return "term_pm_999"
            return None

        mock_find.side_effect = find_side_effect
        res = self.orch.handle_pm_ended({})
        self.assertEqual(res.get("stage"), "pm_to_lead")
        mock_close.assert_called_once_with("term_pm_999")
        mock_cleanup.assert_called_once_with("pm")

    @patch.object(SlppcOrchestrator, "cleanup_role_worktree")
    @patch.object(SlppcOrchestrator, "close_terminal")
    @patch.object(SlppcOrchestrator, "find_live_terminal_for_role")
    @patch.object(SlppcOrchestrator, "spawn_ephemeral_subagent", return_value="sub_peer_123")
    def test_lead_ended_auto_closes_lead(self, mock_spawn, mock_find, mock_close, mock_cleanup):
        mock_mgr = MagicMock()
        mock_mgr.list_work_items.return_value = [
            {
                "id": "105",
                "title": "Lead Task Breakdown",
                "state": "New",
                "assigned_to_profile": "peer",
                "domain": "frontend"
            }
        ]
        self.orch.mgr = mock_mgr

        def find_side_effect(role):
            if role == "peer":
                return None
            if role == "lead":
                return "term_lead_888"
            return None

        mock_find.side_effect = find_side_effect
        res = self.orch.handle_lead_ended({})
        self.assertEqual(res.get("stage"), "lead_to_peer")
        mock_close.assert_called_once_with("term_lead_888")
        mock_cleanup.assert_called_once_with("lead")

    def test_cli_orchestrate_command(self):
        hook_py = PLUGIN_DIR / "paseo_hooks.py"
        env = os.environ.copy()
        env["SLPPC_DRY_RUN"] = "1"
        res = subprocess.run(
            [sys.executable, str(hook_py), "orchestrate", "--role", "supervisor", "--json"],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
            env=env,
        )
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get("stage"), "supervisor_to_pm_lead")


if __name__ == "__main__":
    unittest.main()
