#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.agent_heartbeat as ah


class TestAgentHeartbeat(unittest.TestCase):
    def test_save_and_load_heartbeats(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)

        try:
            with patch.object(ah, "HEARTBEAT_FILE", tmp_path):
                data = {"peer": {"status": "working", "task_id": "101"}}
                ah.save_heartbeats(data)
                loaded = ah.load_heartbeats()
                self.assertEqual(loaded.get("peer", {}).get("task_id"), "101")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_record_ping(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)

        try:
            with patch.object(ah, "HEARTBEAT_FILE", tmp_path):
                ah.record_ping(role="peer", status="working", task_id="202", activity="writing code")
                loaded = ah.load_heartbeats()
                self.assertIn("peer", loaded)
                self.assertEqual(loaded["peer"]["status"], "working")
                self.assertEqual(loaded["peer"]["task_id"], "202")
                self.assertEqual(loaded["peer"]["activity"], "writing code")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    @patch("shutil.which", return_value=None)
    def test_get_live_terminal_handles_no_orca(self, mock_which):
        handles = ah.get_live_terminal_handles()
        self.assertEqual(handles, {})

    @patch("shutil.which", return_value=None)
    def test_print_status(self, mock_which):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)
            tmp_path.write_text(
                json.dumps({
                    "lead": {"status": "idle", "task_id": "99", "last_ping_ts": time.time(), "activity": "reviewing"}
                }),
                encoding="utf-8",
            )

        try:
            with patch.object(ah, "HEARTBEAT_FILE", tmp_path):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    ah.print_status()
                    output = fake_out.getvalue()
                    self.assertIn("SLPC MULTI-AGENT HEARTBEAT MONITOR", output)
                    self.assertIn("LEAD", output)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
