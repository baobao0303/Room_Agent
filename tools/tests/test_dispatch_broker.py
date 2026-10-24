#!/usr/bin/env python3
"""
tools/tests/test_dispatch_broker.py - Unit test suite for Push-Driven Dispatch Broker.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys_path = str(BASE_DIR / "tools")
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from dispatch_broker import construct_work_packet, queue_work_packet, dispatch  # type: ignore


class TestDispatchBroker(unittest.TestCase):
    """Test packet construction, queue persistence, and dispatch execution."""

    def test_construct_work_packet(self):
        packet = construct_work_packet("peer", "Implement Angular component", task_id=150, payload={"file": "foo.ts"})
        self.assertEqual(packet["target_role"], "peer")
        self.assertEqual(packet["task_id"], 150)
        self.assertEqual(packet["action"], "Implement Angular component")
        self.assertIn("evt_", packet["event_id"])
        self.assertEqual(packet["payload"]["file"], "foo.ts")

    def test_dry_run_dispatch(self):
        res = dispatch("lead", "Review architecture", task_id=200, dry_run=True)
        self.assertEqual(res["status"], "dry_run")
        self.assertIn("packet", res)
        self.assertEqual(res["packet"]["target_role"], "lead")

    def test_queue_persistence(self):
        packet = construct_work_packet("qc", "Run ISTQB matrix", task_id=300)
        queue_file = queue_work_packet("qc", packet)
        self.assertTrue(queue_file.is_file())
        items = json.loads(queue_file.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[-1]["task_id"], 300)


if __name__ == "__main__":
    unittest.main()
