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

    def test_multi_slot_peers_do_not_close_each_other(self):
        """Verify opening multiple Peer slots (peer, peer2, peer3) within SLOT_CAPACITIES does not close siblings."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_orch = SlppcOrchestrator(Path(tmp_dir))
            fake_list_out = json.dumps({
                "result": {
                    "terminals": [
                        {
                            "handle": "term_peer_1",
                            "tabId": "tab_p1",
                            "worktreePath": "/Users/test/orca/workspaces/Room_Agent/room-peer",
                            "branch": "refs/heads/room-peer",
                            "title": "[Peer Dev] Task #1",
                            "connected": True,
                            "lastOutputAt": 100,
                        },
                        {
                            "handle": "term_peer_2",
                            "tabId": "tab_p2",
                            "worktreePath": "/Users/test/orca/workspaces/Room_Agent/room-peer",
                            "branch": "refs/heads/room-peer",
                            "title": "[Peer Dev 2] Task #2",
                            "connected": True,
                            "lastOutputAt": 200,
                        },
                        {
                            "handle": "term_peer_3",
                            "tabId": "tab_p3",
                            "worktreePath": "/Users/test/orca/workspaces/Room_Agent/room-peer",
                            "branch": "refs/heads/room-peer",
                            "title": "[Peer Dev 3] Task #3",
                            "connected": True,
                            "lastOutputAt": 300,
                        },
                    ]
                }
            })
            with patch("shutil.which", return_value="/fake/orca"), \
                 patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=fake_list_out)), \
                 patch.object(tmp_orch, "close_terminal", return_value=True) as mock_close:
                p_h = tmp_orch.find_live_terminal_for_role("peer")
                self.assertEqual(p_h, "term_peer_3")
                # Không đóng bất kỳ Peer nào vì 3 <= SLOT_CAPACITIES['peer'] (5)
                mock_close.assert_not_called()

    def test_nested_supervisor_registration_and_origin_routing(self):
        """Verify Supervisor 2 nests cleanly under Supervisor 1 and routes child task notifications back to Supervisor 2."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_orch = SlppcOrchestrator(Path(tmp_dir))
            tmp_orch.register_nested_supervisor(
                slot_id="supervisor",
                handle="term_sup_1",
                epic_id="100",
            )
            nested = tmp_orch.register_nested_supervisor(
                slot_id="supervisor2",
                handle="term_sup_2",
                parent_supervisor="supervisor",
                parent_epic_id="100",
                epic_id="200",
            )
            self.assertFalse(nested["is_master_reaper"])
            self.assertEqual(nested["parent_supervisor"], "supervisor")
            self.assertEqual(nested["epic_id"], "200")

            items = [
                {"id": "100", "type": "Epic", "state": "Active", "title": "Root Program"},
                {"id": "200", "type": "Epic", "parent_id": "100", "state": "Active", "title": "POS Sub-Epic"},
                {"id": "201", "type": "Task", "parent_id": "200", "state": "Closed", "title": "POS Leaf Task"},
            ]
            origin = tmp_orch.resolve_origin_supervisor(items[2], all_items=items)
            self.assertEqual(origin, "supervisor2")

    @patch.object(SlppcOrchestrator, "spawn_ephemeral_subagent", side_effect=lambda role, **kw: f"handle_{role}")
    def test_recursive_orchestration_fanout_and_cascade_rollup(self, mock_spawn):
        """Verify orchestrate_recursive fans out multiple Leads, Peers (with file-conflict guard), QCs, and rolls up parent tree."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_orch = SlppcOrchestrator(Path(tmp_dir))
            mock_mgr = MagicMock()

            # Cây công việc:
            # - Epic #500 có Story #501 (con của #500), và Story #501 có 1 Task #502 đã Closed -> Roll-up sẽ đóng #501 rồi đệ quy đóng #500!
            # - 2 Task New (#601 và #602) khác file -> Spawn 2 Peer song song (peer, peer2)
            # - 1 Task New (#603) trùng file với #601 -> Bị giữ lại chờ vòng đệ quy sau (Single-Ownership)
            # - 2 Task Resolved (#701, #702) -> Spawn 2 QC song song (qc, qc2)
            items = [
                {"id": "500", "type": "Epic", "state": "Active", "title": "Root Epic"},
                {"id": "501", "type": "Story", "parent_id": "500", "state": "Active", "title": "Child Story"},
                {"id": "502", "type": "Task", "parent_id": "501", "state": "Closed", "title": "Completed Leaf Task"},
                {
                    "id": "601",
                    "type": "Task",
                    "state": "New",
                    "assigned_to_profile": "peer",
                    "title": "Edit CRM Header",
                    "description": "Target: projects/demo-crm-fe/src/header.component.ts",
                },
                {
                    "id": "602",
                    "type": "Task",
                    "state": "New",
                    "assigned_to_profile": "peer",
                    "title": "Edit POS Footer",
                    "description": "Target: projects/demo-pos-fe/src/footer.component.ts",
                },
                {
                    "id": "603",
                    "type": "Task",
                    "state": "New",
                    "assigned_to_profile": "peer",
                    "title": "Conflicting CRM Header Edit",
                    "description": "Target: projects/demo-crm-fe/src/header.component.ts",
                },
                {"id": "701", "type": "Task", "state": "Resolved", "title": "Verify Module A"},
                {"id": "702", "type": "Task", "state": "Resolved", "title": "Verify Module B"},
            ]

            def update_state_side_effect(item_id, new_state, **kwargs):
                for it in items:
                    if str(it["id"]) == str(item_id):
                        it["state"] = new_state
                return {"success": True, "new_state": new_state}

            mock_mgr.list_work_items.return_value = items
            mock_mgr.update_state.side_effect = update_state_side_effect
            tmp_orch.mgr = mock_mgr

            res = tmp_orch.orchestrate_recursive()
            # 1. Phải thu gọn đệ quy cả Story #501 lẫn Root Epic #500
            self.assertIn("501", res["rolled_up_parents"])
            self.assertIn("500", res["rolled_up_parents"])

            # 2. Phải fan-out 2 QC song song (qc, qc2) cho #701 và #702
            qc_slots = [q["slot"] for q in res["spawned_qcs"]]
            self.assertEqual(qc_slots, ["qc", "qc2"])

            # 3. Phải fan-out 2 Peer song song (peer, peer2) cho #601 và #602, nhưng chặn #603 do trùng file với #601
            peer_tasks_spawned = [p["task_id"] for p in res["spawned_peers"]]
            self.assertEqual(peer_tasks_spawned, ["601", "602"])
            self.assertNotIn("603", peer_tasks_spawned)

    def test_linux_screen_reader_orca_blocked(self):
        """Đảm bảo tuyệt đối không bao giờ nhầm /usr/bin/orca (Linux Screen Reader) thành Orca IDE CLI."""
        from slppc_orchestrator import _get_orca_ide_bin
        with patch("shutil.which", return_value="/usr/bin/orca"):
            self.assertIsNone(_get_orca_ide_bin())
        with patch("shutil.which", return_value="/bin/orca"):
            self.assertIsNone(_get_orca_ide_bin())
        with patch("shutil.which", return_value="/fake/orca"):
            self.assertEqual(_get_orca_ide_bin(), "/fake/orca")

    def test_harness2_integration_ledger_library_and_judge(self):
        """Kiểm thử tích hợp đầy đủ Google Harness² (Ledger R=4k/P=3k, Per-Domain Library INDEX/EXPERIENCE, Judge Scored) trong Orca."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_orch = SlppcOrchestrator()
            tmp_orch.rooms_dir = Path(tmpdir) / "rooms"
            tmp_orch.reg_file = tmp_orch.rooms_dir / "agent_terminals.json"
            tmp_orch.ledger_file = tmp_orch.rooms_dir / "room_ledger.json"

            # 1. Test Parallel Mode (`agg`, k=2 -> R=8, P=6)
            agg_res = tmp_orch.run_harness2_recursion_cycle(task_id="801", mode="agg", k=2, domain="angular_mfe")
            self.assertTrue(agg_res.get("ok"))
            self.assertEqual(agg_res["ledger"]["R"], 8)
            self.assertEqual(agg_res["ledger"]["P"], 6)
            self.assertEqual(agg_res["finals"], ["agg1", "agg2"])

            # 2. Test Sequential Mode (`seq`, k=2 -> R=8, P=6)
            seq_res = tmp_orch.run_harness2_recursion_cycle(task_id="802", mode="seq", k=2, domain="angular_mfe")
            self.assertTrue(seq_res.get("ok"))
            self.assertEqual(seq_res["ledger"]["R"], 8)
            self.assertEqual(seq_res["ledger"]["P"], 6)
            self.assertEqual(seq_res["finals"], ["c1", "c2"])

            # 3. Test Per-Domain Library (record + query INDEX.md & EXPERIENCE.md)
            exp_dir = tmp_orch.record_harness2_experience(
                task_id="801",
                domain="angular_mfe",
                cue="mfe_singleton_mismatch",
                lesson="Always enforce strictVersion: true in Module Federation shared singletons.",
                evidence="Verified on Orca QC Gate #801",
                label="agg1",
            )
            self.assertIsNotNone(exp_dir)
            ctx = tmp_orch.query_harness2_library_context(domain="angular_mfe", limit=3)
            self.assertIn("mfe_singleton_mismatch", ctx)
            self.assertIn("strictVersion: true", ctx)

            # 4. Test Harness² Judge Scoring (5/5 ISTQB criteria -> frac=1.0, all_pass=True)
            scored = tmp_orch.score_with_harness2_judge(
                task_id="801", mode="agg", k=2, label="agg1", n_passed=5, n_criteria=5
            )
            self.assertIsNotNone(scored)
            self.assertTrue(scored["graded"])
            self.assertEqual(scored["frac"], 1.0)
            self.assertTrue(scored["all_pass"])


if __name__ == "__main__":
    unittest.main()



