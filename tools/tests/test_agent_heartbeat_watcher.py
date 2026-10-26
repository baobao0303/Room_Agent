#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.agent_heartbeat_watcher as ahw


class TestAgentHeartbeatWatcher(unittest.TestCase):
    def test_check_all_agents_file_not_found(self):
        with patch.object(ahw, "HEARTBEAT_FILE", Path("/non/existent/heartbeats.json")):
            res = ahw.check_all_agents()
            self.assertEqual(res, {})

    def test_check_all_agents_healthy(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)
            data = {
                "peer": {
                    "status": "working",
                    "task_id": "123",
                    "last_ping_ts": time.time() - 60,
                }
            }
            tmp_path.write_text(json.dumps(data), encoding="utf-8")

        try:
            with patch.object(ahw, "HEARTBEAT_FILE", tmp_path):
                res = ahw.check_all_agents()
                self.assertEqual(res.get("alerts"), [])
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_check_all_agents_stale_alert(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)
            data = {
                "peer": {
                    "status": "working",
                    "task_id": "456",
                    "last_ping_ts": time.time() - 400,  # > 300s
                }
            }
            tmp_path.write_text(json.dumps(data), encoding="utf-8")

        try:
            with patch.object(ahw, "HEARTBEAT_FILE", tmp_path):
                with patch("shutil.which", return_value=None):
                    res = ahw.check_all_agents()
                    self.assertGreater(len(res.get("alerts", [])), 0)
                    self.assertIn("PEER", res["alerts"][0])
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
