#!/usr/bin/env python3
"""
tools/tests/test_rag_envelope.py - Unit Test Suite for G-RAG-1 and G-MAG-1.
Verifies context-bounded Top-3 RAG prompt generation and live path AgentHandoffEnvelope validation.
"""
from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

import tools.agent_context_manager as acm
import tools.query_reader as qr
import tools.slppc_flow_guard as sfg


class TestRagPromptBuilder(unittest.TestCase):
    """Test suite for G-RAG-1: Context-bounded top-3 prompt builder."""

    def test_top3_clamping_default(self):
        chunks = [
            {"file": f"doc_{i}.md", "heading": f"Section {i}", "content": f"Content {i}"}
            for i in range(1, 10)
        ]
        prompt = qr.build_context_bounded_prompt("Test Query", chunks)
        self.assertIn("[Chunk #1", prompt)
        self.assertIn("[Chunk #2", prompt)
        self.assertIn("[Chunk #3", prompt)
        self.assertNotIn("[Chunk #4", prompt)
        self.assertNotIn("[Chunk #9", prompt)
        self.assertIn("Nói có sách, mách có chứng", prompt)

    def test_top3_clamping_with_large_max_chunks(self):
        chunks = [
            {"file": f"doc_{i}.md", "heading": f"Section {i}", "content": f"Content {i}"}
            for i in range(1, 10)
        ]
        # Even if caller passes max_chunks=8, must still strictly clamp at 3
        prompt = qr.build_context_bounded_prompt("Test Query", chunks, max_chunks=8)
        self.assertIn("[Chunk #3", prompt)
        self.assertNotIn("[Chunk #4", prompt)

    def test_less_than_3_chunks(self):
        chunks = [
            {"file": "single.md", "heading": "Only", "content": "Solo chunk"}
        ]
        prompt = qr.build_context_bounded_prompt("Query Solo", chunks, max_chunks=3)
        self.assertIn("[Chunk #1", prompt)
        self.assertNotIn("[Chunk #2", prompt)

    def test_experience_chunks_compatibility(self):
        exp_chunks = [
            {"domain": "angular", "cue": "anti_any_rule", "lesson": "Never use any in Angular models."},
            {"domain": "harness", "cue": "sqlite_lock", "lesson": "Use WAL mode to prevent busy timeouts."},
        ]
        prompt = qr.build_context_bounded_prompt("Best practices", exp_chunks)
        self.assertIn("anti_any_rule", prompt)
        self.assertIn("Never use any in Angular models", prompt)
        self.assertIn("Source: angular", prompt)


class TestAgentHandoffEnvelopeLiveValidation(unittest.TestCase):
    """Test suite for G-MAG-1: AgentHandoffEnvelope live path validation."""

    def setUp(self):
        self.valid_envelope = sfg.build_agent_handoff_envelope(
            task_id="201",
            from_role="LEAD",
            to_role="PEER",
            status="ACTIVE",
            target_files=["tools/app.py"],
            anchors=["class Worker"],
            concrete_changes="Implement async retry queue",
            acceptance_criteria=["Exit code 0", "Zero any typing"],
            test_command="pytest",
            exit_code=0,
            error_stack_trace="",
            retry_count=0
        )

    @patch("tools.agent_context_manager.get_live_terminals", return_value={"peer": "term_peer_1"})
    @patch("tools.agent_context_manager.inspect_terminal", return_value={"is_live": True, "is_busy": False, "needs_compact": False})
    @patch("subprocess.run")
    def test_safe_send_valid_envelope_dict(self, mock_run, mock_inspect, mock_live):
        mock_run.return_value = MagicMock(returncode=0)
        res = acm.safe_send_agent_message("peer", self.valid_envelope)
        self.assertTrue(res)
        mock_run.assert_called_once()
        sent_text = mock_run.call_args[0][0][6]
        self.assertIn("ARCH-SPEC-ENTERPRISE-AI-4-PILLARS-2026-V1", sent_text)

    @patch("tools.agent_context_manager.get_live_terminals", return_value={"peer": "term_peer_1"})
    @patch("tools.agent_context_manager.inspect_terminal", return_value={"is_live": True, "is_busy": False, "needs_compact": False})
    @patch("subprocess.run")
    def test_safe_send_valid_envelope_json_string(self, mock_run, mock_inspect, mock_live):
        mock_run.return_value = MagicMock(returncode=0)
        res = acm.safe_send_agent_message("peer", json.dumps(self.valid_envelope))
        self.assertTrue(res)
        mock_run.assert_called_once()

    def test_safe_send_rejects_failed_retry_without_stack_trace(self):
        bad_env = dict(self.valid_envelope)
        bad_env["status"] = "FAILED_RETRY"
        bad_env["verification"] = {"exit_code": 1, "error_stack_trace": "", "retry_count": 1}

        # Must reject transmission returning False
        res = acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=False)
        self.assertFalse(res)

        # In strict mode, must raise ValueError
        with self.assertRaises(ValueError):
            acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=True)

    def test_safe_send_rejects_retry_count_exceeded(self):
        bad_env = dict(self.valid_envelope)
        bad_env["verification"] = {"exit_code": 1, "error_stack_trace": "Error", "retry_count": 4}
        res = acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=False)
        self.assertFalse(res)

        with self.assertRaises(ValueError):
            acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=True)

    def test_safe_send_rejects_empty_zero_search_spec(self):
        bad_env = dict(self.valid_envelope)
        bad_env["spec"] = dict(bad_env["spec"])
        bad_env["spec"]["test_command"] = ""  # empty command violates Zero-Search
        res = acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=False)
        self.assertFalse(res)

    @patch("tools.agent_context_manager.safe_send_agent_message", return_value=True)
    def test_send_handoff_envelope_success(self, mock_safe_send):
        res = acm.send_handoff_envelope("lead", "peer", self.valid_envelope, persist_to_room=False)
        self.assertTrue(res)
        mock_safe_send.assert_called_once()

    def test_send_handoff_envelope_strict_rejection(self):
        bad_env = dict(self.valid_envelope)
        bad_env["status"] = "FAILED_RETRY"
        bad_env["verification"] = {"exit_code": 1, "error_stack_trace": "", "retry_count": 1}
        with self.assertRaises(ValueError):
            acm.send_handoff_envelope("tester", "coder", bad_env, strict=True, persist_to_room=False)

    def test_safe_send_rejects_whitespace_zero_search_fields(self):
        # Whitespace test_command
        bad_cmd = dict(self.valid_envelope)
        bad_cmd["spec"] = dict(bad_cmd["spec"], test_command="   ")
        self.assertFalse(acm.safe_send_agent_message("peer", bad_cmd, raise_on_invalid=False))
        with self.assertRaises(ValueError):
            acm.safe_send_agent_message("peer", bad_cmd, raise_on_invalid=True)

        # Whitespace concrete_changes
        bad_chg = dict(self.valid_envelope)
        bad_chg["spec"] = dict(bad_chg["spec"], concrete_changes=" \t\n ")
        self.assertFalse(acm.safe_send_agent_message("peer", bad_chg, raise_on_invalid=False))

        # Whitespace elements in list fields
        bad_files = dict(self.valid_envelope)
        bad_files["spec"] = dict(bad_files["spec"], target_files=["  ", ""])
        self.assertFalse(acm.safe_send_agent_message("peer", bad_files, raise_on_invalid=False))

        bad_anchors = dict(self.valid_envelope)
        bad_anchors["spec"] = dict(bad_anchors["spec"], anchors=["   "])
        self.assertFalse(acm.safe_send_agent_message("peer", bad_anchors, raise_on_invalid=False))

        bad_ac = dict(self.valid_envelope)
        bad_ac["spec"] = dict(bad_ac["spec"], acceptance_criteria=["  "])
        self.assertFalse(acm.safe_send_agent_message("peer", bad_ac, raise_on_invalid=False))

    def test_safe_send_rejects_failed_retry_none_or_dummy_stack_trace(self):
        for dummy in (None, "None", "none", "null", "NULL", "   "):
            bad_env = dict(self.valid_envelope)
            bad_env["status"] = "FAILED_RETRY"
            bad_env["verification"] = {"exit_code": 1, "error_stack_trace": dummy, "retry_count": 1}
            self.assertFalse(
                acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=False),
                f"Failed for dummy stack: {repr(dummy)}"
            )
            with self.assertRaises(ValueError):
                acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=True)

    def test_safe_send_rejects_retry_count_evasion(self):
        for bad_rc in ("4", 4.0, "4.0", 3.5, "invalid", None, True, -1):
            bad_env = dict(self.valid_envelope)
            bad_env["verification"] = {"exit_code": 1, "error_stack_trace": "Error", "retry_count": bad_rc}
            self.assertFalse(
                acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=False),
                f"Failed for retry_count: {repr(bad_rc)}"
            )
            with self.assertRaises(ValueError):
                acm.safe_send_agent_message("peer", bad_env, raise_on_invalid=True)


if __name__ == "__main__":
    unittest.main()
