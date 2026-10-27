#!/usr/bin/env python3
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import tools.agent_context_manager as acm


class TestAgentContextManager(unittest.TestCase):
    def test_build_rehydration_prompt(self):
        prompt = acm.build_rehydration_prompt("peer")
        self.assertIn("SLPPC AUTO-REHYDRATION BOOT", prompt)
        self.assertIn("PEER", prompt)
        self.assertIn("Zero-Search", prompt)

    @patch("shutil.which", return_value=None)
    def test_get_live_terminals_no_orca(self, mock_which):
        terminals = acm.get_live_terminals()
        self.assertEqual(terminals, {})

    @patch("shutil.which", return_value=None)
    def test_inspect_terminal_no_orca(self, mock_which):
        info = acm.inspect_terminal("term_123")
        self.assertFalse(info["is_live"])
        self.assertFalse(info["is_ready"])
        self.assertTrue(info["is_busy"])

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_inspect_terminal_parsed_tokens(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Some output\nContext: 245.5k t\nReady to assist.\n❯ ",
        )
        info = acm.inspect_terminal("term_123")
        self.assertTrue(info["is_live"])
        self.assertEqual(info["token_count_k"], 245.5)
        self.assertTrue(info["needs_compact"])
        self.assertTrue(info["is_ready"])
        self.assertFalse(info["is_busy"])

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_inspect_terminal_busy_state(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Some output\ncomputing results...\nPress Ctrl+C to interrupt\n",
        )
        info = acm.inspect_terminal("term_123")
        self.assertTrue(info["is_live"])
        self.assertTrue(info["is_busy"])
        self.assertFalse(info["is_ready"])

    @patch("tools.agent_context_manager.inspect_terminal")
    def test_wait_for_terminal_ready(self, mock_inspect):
        mock_inspect.return_value = {"is_ready": True}
        self.assertTrue(acm.wait_for_terminal_ready("term_123", max_wait_sec=1))

    @patch("tools.agent_context_manager.get_live_terminals", return_value={})
    def test_safe_send_agent_message_no_handle(self, mock_live):
        self.assertFalse(acm.safe_send_agent_message("peer", "hello"))

    def test_role_compact_thresholds_exact_values(self):
        self.assertEqual(acm.get_compact_threshold_k("peer"), 30.0)
        self.assertEqual(acm.get_compact_threshold_k("qc"), 30.0)
        self.assertEqual(acm.get_compact_threshold_k("lead"), 60.0)
        self.assertEqual(acm.get_compact_threshold_k("supervisor"), 100.0)

    def test_role_compact_thresholds_aliases_and_fallback(self):
        for role_alias in ("peer1", "peer2", "peer3", "peer4", "peer_design", "dev", "coder"):
            self.assertEqual(acm.get_compact_threshold_k(role_alias), 30.0)
        for qc_alias in ("qc_tester", "tester"):
            self.assertEqual(acm.get_compact_threshold_k(qc_alias), 30.0)
        self.assertEqual(acm.get_compact_threshold_k("lead_architect"), 60.0)
        self.assertEqual(acm.get_compact_threshold_k("pm"), 100.0)
        self.assertEqual(acm.get_compact_threshold_k("unknown_role"), 30.0)
        self.assertEqual(acm.get_compact_threshold_k(None), 30.0)

    @patch("shutil.which", return_value="/usr/local/bin/orca")
    @patch("subprocess.run")
    def test_inspect_terminal_role_threshold_evaluation(self, mock_run, mock_which):
        # 45.0k tokens screen
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Output\nContext: 45.0k t\nReady\n❯ ",
        )
        # Peer & QC threshold 30.0 -> needs compact
        peer_info = acm.inspect_terminal("term_1", role="peer")
        self.assertEqual(peer_info["compact_threshold_k"], 30.0)
        self.assertTrue(peer_info["needs_compact"])

        qc_info = acm.inspect_terminal("term_1", role="qc")
        self.assertEqual(qc_info["compact_threshold_k"], 30.0)
        self.assertTrue(qc_info["needs_compact"])

        # Lead threshold 60.0 -> does NOT need compact at 45k
        lead_info = acm.inspect_terminal("term_1", role="lead")
        self.assertEqual(lead_info["compact_threshold_k"], 60.0)
        self.assertFalse(lead_info["needs_compact"])

        # Supervisor threshold 100.0 -> does NOT need compact at 45k
        sup_info = acm.inspect_terminal("term_1", role="supervisor")
        self.assertEqual(sup_info["compact_threshold_k"], 100.0)
        self.assertFalse(sup_info["needs_compact"])

        # 75.0k tokens screen
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Output\nContext: 75.0k t\nReady\n❯ ",
        )
        # Lead threshold 60.0 -> needs compact at 75k
        lead_info_75 = acm.inspect_terminal("term_1", role="lead")
        self.assertTrue(lead_info_75["needs_compact"])
        # Supervisor threshold 100.0 -> does NOT need compact at 75k
        sup_info_75 = acm.inspect_terminal("term_1", role="supervisor")
        self.assertFalse(sup_info_75["needs_compact"])

    def test_load_curated_memory_full_content(self):
        mem = acm.load_curated_memory("peer")
        self.assertIn("Facts:", mem)
        self.assertIn("Preferences:", mem)
        self.assertIn("Commitments:", mem)
        self.assertIn("Harness Container Architecture", mem)
        self.assertIn("Loop Engineering Execution Mandate", mem)
        self.assertIn("shortest working surgical diffs", mem)
        self.assertIn("premature_close", mem)
        self.assertIn("FAILED_RETRY", mem)

    def test_build_rehydration_prompt_includes_preferences_and_commitments(self):
        prompt = acm.build_rehydration_prompt("peer")
        self.assertIn("Facts:", prompt)
        self.assertIn("Preferences:", prompt)
        self.assertIn("Commitments:", prompt)
        self.assertIn("shortest working surgical diffs", prompt)
        self.assertIn("premature_close", prompt)

    @patch("tools.agent_context_manager.load_curated_memory", side_effect=IOError("disk read failed"))
    @patch("sys.stderr.write")
    def test_rehydration_error_visibility(self, mock_stderr_write, mock_load):
        prompt = acm.build_rehydration_prompt("peer")
        self.assertIn("SLPPC AUTO-REHYDRATION BOOT", prompt)
        # Verify stderr was written to
        written_msgs = "".join(call.args[0] for call in mock_stderr_write.call_args_list)
        self.assertIn("⚠️ [Rehydration Warning]: Lỗi nạp curated MEMORY.md cho peer: disk read failed", written_msgs)



if __name__ == "__main__":
    unittest.main()
