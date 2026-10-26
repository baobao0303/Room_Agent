#!/usr/bin/env python3
"""
tools/tests/test_pipeline_loop.py - Unit test suite for G-LOP-1 (Pipeline Retry Loop)
and G-OBS-2 (Observability Spans & Shared Run ID).
"""

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))

from scripts import run_pipeline
from tools.harness_manager import HarnessManager


class TestPipelineLoopAndObservability(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "harness_test.db")
        self.rooms_dir = Path(self.temp_dir.name) / "bmad" / "rooms"
        self.rooms_dir.mkdir(parents=True, exist_ok=True)
        (self.rooms_dir / "supervisor").mkdir(parents=True, exist_ok=True)
        (self.rooms_dir / "pm").mkdir(parents=True, exist_ok=True)

        os.environ["HARNESS_DB"] = self.db_path
        os.environ["HARNESS_ENGINE"] = "sqlite"
        os.environ["HARNESS_BACKEND"] = "sqlite"
        os.environ["SLPPC_DRY_RUN"] = "1"

    def tearDown(self):
        os.environ.pop("HARNESS_DB", None)
        os.environ.pop("HARNESS_ENGINE", None)
        os.environ.pop("HARNESS_BACKEND", None)
        os.environ.pop("SLPPC_DRY_RUN", None)
        self.temp_dir.cleanup()



    def test_01_run_peer_maker_gate_returns_tuple_and_captures_error(self):
        """Verify run_peer_maker_gate returns (ok: bool, error: str) for pass and fail commands."""
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        task = mgr.add_work_item(wi_type="Task", title="[Exec] - Test Peer Gate Success", assigned_to="peer", assigned_to_profile="peer")
        
        # Passing command
        ok, err = run_pipeline.run_peer_maker_gate(task["id"], test_cmd="python3 -c 'import sys; sys.exit(0)'")
        self.assertTrue(ok)
        self.assertEqual(err, "")
        self.assertEqual(mgr.get_work_item(task["id"])["state"], "Resolved")

        # Failing command
        fail_task = mgr.add_work_item(wi_type="Task", title="[Exec] - Test Peer Gate Fail", assigned_to="peer", assigned_to_profile="peer")
        ok_f, err_f = run_pipeline.run_peer_maker_gate(fail_task["id"], test_cmd="python3 -c 'import sys; sys.stderr.write(\"AssertionError: Expected 200, got 500\\n\"); sys.exit(1)'")
        self.assertFalse(ok_f)
        self.assertIn("AssertionError", err_f)

    def test_02_run_qc_tail_gate_returns_tuple_and_captures_error(self):
        """Verify run_qc_tail_gate returns (ok: bool, error: str) when tests fail or pass."""
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        epic = mgr.add_work_item(wi_type="Epic", title="[Pipeline] - Epic Test", assigned_to="lead", assigned_to_profile="lead")
        task = mgr.add_work_item(wi_type="Task", title="[Exec] - Task Test", parent_id=epic["id"], assigned_to="peer", assigned_to_profile="peer")
        mgr.update_state(task["id"], "Resolved", assigned_to_profile="peer")

        # QC fails on test failure
        ok_f, err_f = run_pipeline.run_qc_tail_gate(task["id"], epic["id"], test_cmd="python3 -c 'import sys; sys.exit(2)'")
        self.assertFalse(ok_f)
        self.assertTrue(len(err_f) > 0)

        # QC passes
        ok_p, err_p = run_pipeline.run_qc_tail_gate(task["id"], epic["id"], test_cmd="python3 -c 'import sys; sys.exit(0)'")
        self.assertTrue(ok_p)
        self.assertEqual(err_p, "")
        self.assertEqual(mgr.get_work_item(task["id"])["state"], "Closed")

    def test_03_pipeline_succeeds_after_two_retries(self):
        """
        Verify: Pipeline with a test command that fails twice then succeeds ends
        successfully after retries; trace spans show 2 failures and 1 pass for peer.
        """
        counter_file = Path(self.temp_dir.name) / "counter.txt"
        counter_file.write_text("0")
        
        # Script increments counter: fails if counter < 2, passes when counter >= 2
        cmd = f'python3 -c "import sys, pathlib; p = pathlib.Path(\'{counter_file}\'); c = int(p.read_text()); p.write_text(str(c+1)); sys.exit(0 if c >= 2 else 1)"'

        exit_code = run_pipeline.main(["[THUẬN] - Auto retry test", "--test-cmd", cmd])
        self.assertEqual(exit_code, 0)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        items = mgr.list_work_items(wi_type="Task")
        self.assertTrue(len(items) > 0)
        task = items[0]
        self.assertEqual(task["state"], "Closed")

        # Verify traces
        traces = mgr.list_traces(story_id=str(task["id"]))
        peer_traces = sorted([t for t in traces if t["agent"] == "peer"], key=lambda t: t["id"])
        self.assertEqual(len(peer_traces), 3)
        self.assertEqual(peer_traces[0]["outcome"], "failed")
        self.assertEqual(peer_traces[1]["outcome"], "failed")
        self.assertEqual(peer_traces[2]["outcome"], "completed")

    def test_04_pipeline_stops_after_three_retries_in_blocked_state(self):
        """
        Verify: One that always fails stops after exactly 3 retries in a blocked state.
        (Total 4 attempts = 1 initial + 3 retries).
        """
        fail_cmd = "python3 -c 'import sys; sys.stderr.write(\"Fatal test failure\\n\"); sys.exit(1)'"
        exit_code = run_pipeline.main(["[THUẬN] - Flaky run to block", "--test-cmd", fail_cmd])
        self.assertEqual(exit_code, 1)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        items = mgr.list_work_items(wi_type="Task")
        self.assertTrue(len(items) > 0)
        task = items[0]
        self.assertEqual(task["state"], "Blocked")

        # Exactly 4 peer traces (1 initial + 3 retries)
        peer_traces = [t for t in mgr.list_traces(story_id=str(task["id"])) if t["agent"] == "peer"]
        self.assertEqual(len(peer_traces), 4)
        for pt in peer_traces:
            self.assertEqual(pt["outcome"], "failed")
            self.assertIn("Fatal test failure", pt["errors"] or "")

        # Verify supervisor latest_handoff.md was written
        sup_handoff = Path(run_pipeline.PROJECT_ROOT) / "bmad" / "rooms" / "supervisor" / "latest_handoff.md"
        self.assertTrue(sup_handoff.exists())
        content = sup_handoff.read_text(encoding="utf-8")
        self.assertIn("Blocked", content)
        self.assertIn("Fatal test failure", content)

    def test_05_qc_failure_triggers_retry_to_peer(self):
        """Verify that QC failure triggers retry carrying QC error back to Peer."""
        call_count = {"qc": 0}
        orig_qc = run_pipeline.run_qc_tail_gate

        def mock_qc(*args, **kwargs):
            call_count["qc"] += 1
            if call_count["qc"] == 1:
                return False, "QC Mock Rejection: Missing edge-case test"
            return orig_qc(*args, **kwargs)

        with patch("scripts.run_pipeline.run_qc_tail_gate", side_effect=mock_qc):
            exit_code = run_pipeline.main(["[THUẬN] - QC retry trigger test", "--test-cmd", "python3 -c 'import sys; sys.exit(0)'"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(call_count["qc"], 2)

    def test_06_shared_run_id_across_all_spans(self):
        """Verify all trace spans recorded during one pipeline run share the exact same run_id."""
        exit_code = run_pipeline.main(["[THUẬN] - Shared run_id trace test", "--test-cmd", "python3 -c 'import sys; sys.exit(0)'"])
        self.assertEqual(exit_code, 0)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT run_id, agent, outcome, notes FROM trace WHERE run_id IS NOT NULL;").fetchall()

        self.assertGreaterEqual(len(rows), 4)
        run_ids = {r[0] for r in rows}
        self.assertEqual(len(run_ids), 1, f"Expected exactly 1 shared run_id across all spans, got: {run_ids}")
        shared_run = list(run_ids)[0]
        self.assertTrue(re.match(r"^run_\d+_[a-f0-9]{8}$", shared_run))


if __name__ == "__main__":
    unittest.main()
