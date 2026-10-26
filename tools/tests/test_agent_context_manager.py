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


if __name__ == "__main__":
    unittest.main()
