#!/usr/bin/env python3
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import tools.profile_research_gen as prg


class TestProfileResearchGen(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(prg.slugify("Hello World! 123"), "hello_world_123")
        self.assertEqual(prg.slugify(""), "task")
        long_str = "a" * 50
        self.assertEqual(len(prg.slugify(long_str, max_len=20)), 20)

    @patch("subprocess.run")
    def test_run_cmd_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output\n", stderr="")
        code, out, err = prg.run_cmd(["echo", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "output")
        self.assertEqual(err, "")

    @patch("subprocess.run")
    def test_run_cmd_exception(self, mock_run):
        mock_run.side_effect = RuntimeError("Subprocess failed")
        code, out, err = prg.run_cmd(["invalid_command"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Subprocess failed", err)

    @patch("tools.profile_research_gen.ra.run_research")
    @patch("tools.profile_research_gen.run_cmd")
    def test_execute_pipeline_ba_profile(self, mock_run_cmd, mock_research):
        mock_research.return_value = {
            "source": "mock_engine",
            "output_file": "tools/research/research_ba_test.md",
        }
        mock_run_cmd.side_effect = [
            (0, '{"threads": []}', ""),  # agent_progress find-thread
            (0, "CRM doc excerpt mock", ""),  # crm_doc_reader
            (0, "Distilled BA beats", ""),  # distill_ba_beats
        ]

        res = prg.execute_pipeline(
            profile="Lead BA",
            topic="Refine UC01.01 Contact Sync",
            uc_code="UC01.01",
        )
        self.assertEqual(res["profile"], "Lead BA")
        self.assertTrue(res["success"])
        self.assertIn("research_report", res)
        self.assertTrue(len(res["generated_files"]) > 0)


if __name__ == "__main__":
    unittest.main()
