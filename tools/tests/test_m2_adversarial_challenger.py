#!/usr/bin/env python3
"""
tools/tests/test_m2_adversarial_challenger.py - Rigorous Empirical Adversarial Stress Test Suite for M2.

Focus Areas:
1. G-LOP-1: Loop bound invariants (exact 1, 2, 3, 4 attempts; never 3 or 5 upon persisting failures).
2. G-LOP-1: Peer and QC failure origins, alternating failures, and verbatim error message passing.
3. G-LOP-1: State machine escalation to "Blocked" on both Task and Epic upon retry exhaustion.
4. G-LOP-1: Supervisor handoff memo line count (<= 150) and Zero-Leak cleanliness.
5. G-OBS-2: Shared run_id continuity across head, lead, peer, qc, and discussion stages.
6. G-OBS-2: Trace span persistence in SQLite with strict foreign keys (PRAGMA foreign_keys = ON) and legacy schemas.
7. G-LOP-1: auto_dispatch_agent handling of "Blocked" state (reaping ephemeral subagents, alerting supervisor).
8. EMPIRICAL VULNERABILITY REPRODUCTION: Documenting and reproducing foreign key failures with alphanumeric story IDs and 001-init.sql schema.
"""

import datetime as dt
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
sys.path.insert(0, str(BASE_DIR / "tools"))

from scripts import run_pipeline
from tools.harness_manager import HarnessManager, auto_dispatch_agent


class TestM2AdversarialChallenger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        self.db_path = str(self.test_root / "adversarial_harness.db")

        self.sup_handoff_path = BASE_DIR / "bmad" / "rooms" / "supervisor" / "latest_handoff.md"
        self.sup_handoff_backup = None
        if self.sup_handoff_path.exists():
            self.sup_handoff_backup = self.sup_handoff_path.read_text(encoding="utf-8")

        self.orig_env = os.environ.copy()
        os.environ["HARNESS_DB"] = self.db_path
        os.environ["HARNESS_ENGINE"] = "sqlite"
        os.environ["HARNESS_BACKEND"] = "sqlite"
        os.environ["SLPPC_DRY_RUN"] = "1"

    def tearDown(self):
        if self.sup_handoff_backup is not None:
            self.sup_handoff_path.write_text(self.sup_handoff_backup, encoding="utf-8")
        os.environ.clear()
        os.environ.update(self.orig_env)
        self.temp_dir.cleanup()

    # =========================================================================
    # 1. LOOP BOUND & EXACT ATTEMPTS INVARIANCES (Oracle Testing)
    # =========================================================================

    def test_adv_01_exact_attempt_bounds_on_success_after_n_failures(self):
        """
        Verify that:
        - N=0 failures -> exactly 1 attempt total.
        - N=1 failures -> exactly 2 attempts total (1 initial + 1 retry).
        - N=2 failures -> exactly 3 attempts total (1 initial + 2 retries).
        - N=3 failures -> exactly 4 attempts total (1 initial + 3 retries).
        """
        for n_failures in [0, 1, 2, 3]:
            with self.subTest(n_failures=n_failures):
                counter_file = self.test_root / f"counter_{n_failures}.txt"
                counter_file.write_text("0", encoding="utf-8")
                
                cmd = (
                    f'python3 -c "'
                    f'import sys, pathlib; '
                    f'p = pathlib.Path(\'{counter_file}\'); '
                    f'c = int(p.read_text()); '
                    f'p.write_text(str(c+1)); '
                    f'sys.exit(0 if c >= {n_failures} else 1)"'
                )

                exit_code = run_pipeline.main([f"[THUẬN] - Attempt bound test N={n_failures}", "--test-cmd", cmd])
                self.assertEqual(exit_code, 0, f"Pipeline should succeed when failures={n_failures}")

                mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
                with mgr._get_sqlite_db() as conn:
                    cur = conn.cursor()
                    task_row = cur.execute(
                        "SELECT id, state FROM work_item WHERE title LIKE ? ORDER BY id DESC LIMIT 1;",
                        (f"%Attempt bound test N={n_failures}%",)
                    ).fetchone()
                    self.assertIsNotNone(task_row)
                    task_id, task_state = task_row["id"], task_row["state"]
                    self.assertEqual(task_state, "Closed")

                    peer_spans = cur.execute(
                        "SELECT id, outcome FROM trace WHERE story_id = ? AND agent = 'peer' ORDER BY id ASC;",
                        (str(task_id),)
                    ).fetchall()
                    
                    expected_attempts = n_failures + 1
                    self.assertEqual(
                        len(peer_spans),
                        expected_attempts,
                        f"Expected exactly {expected_attempts} peer attempts for n_failures={n_failures}, got {len(peer_spans)}"
                    )

    def test_adv_02_persisting_failure_stops_at_exactly_4_attempts_never_3_or_5(self):
        """
        Verify that when test command persistently fails (e.g. 10 times if allowed),
        the pipeline terminates after EXACTLY 4 attempts (1 initial + 3 retries).
        It must never stop prematurely at 3 or overshoot to 5.
        """
        counter_file = self.test_root / "infinite_fail_counter.txt"
        counter_file.write_text("0", encoding="utf-8")

        fail_cmd = (
            f'python3 -c "'
            f'import sys, pathlib; '
            f'p = pathlib.Path(\'{counter_file}\'); '
            f'c = int(p.read_text()); '
            f'p.write_text(str(c+1)); '
            f'sys.stderr.write(f\'Permanent Failure #{{c}}\\n\'); '
            f'sys.exit(1)"'
        )

        exit_code = run_pipeline.main(["[THUẬN] - Infinite fail boundary check", "--test-cmd", fail_cmd])
        self.assertEqual(exit_code, 1, "Pipeline must exit with code 1 on retry exhaustion")

        executed_attempts = int(counter_file.read_text(encoding="utf-8"))
        self.assertEqual(
            executed_attempts, 4,
            f"Adversarial assertion failed: Expected exactly 4 test attempts, but executed {executed_attempts}"
        )

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            task_row = cur.execute(
                "SELECT id, state FROM work_item WHERE type = 'Task' ORDER BY id DESC LIMIT 1;"
            ).fetchone()
            self.assertEqual(task_row["state"], "Blocked")

            peer_traces = cur.execute(
                "SELECT id, outcome, errors FROM trace WHERE story_id = ? AND agent = 'peer' ORDER BY id ASC;",
                (str(task_row["id"]),)
            ).fetchall()
            self.assertEqual(len(peer_traces), 4, f"Expected exactly 4 peer trace spans, got {len(peer_traces)}")
            for idx, pt in enumerate(peer_traces):
                self.assertEqual(pt["outcome"], "failed")
                self.assertIn(f"Permanent Failure #{idx}", pt["errors"])

    # =========================================================================
    # 2. ADVERSARIAL FAILURE ORIGINS & ERROR CONTEXT PROPAGATION
    # =========================================================================

    def test_adv_03_qc_failure_retries_and_recovers_on_attempt_4(self):
        """
        QC fails 3 times, succeeds on attempt 4.
        Verify Peer runs 4 times, QC runs 4 times, and pipeline concludes with 'Closed'.
        """
        qc_attempts = {"count": 0}
        orig_qc = run_pipeline.run_qc_tail_gate

        def adversarial_qc(*args, **kwargs):
            qc_attempts["count"] += 1
            if qc_attempts["count"] < 4:
                return False, f"QC Adversarial Failure Attempt #{qc_attempts['count']}"
            return orig_qc(*args, **kwargs)

        with patch("scripts.run_pipeline.run_qc_tail_gate", side_effect=adversarial_qc):
            exit_code = run_pipeline.main([
                "[THUẬN] - QC persistent fail recovery",
                "--test-cmd", "python3 -c 'import sys; sys.exit(0)'"
            ])
            self.assertEqual(exit_code, 0)
            self.assertEqual(qc_attempts["count"], 4)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            task_row = cur.execute("SELECT id, state FROM work_item WHERE type = 'Task' ORDER BY id DESC LIMIT 1;").fetchone()
            self.assertEqual(task_row["state"], "Closed")

            qc_traces = cur.execute(
                "SELECT id, outcome, errors FROM trace WHERE story_id = ? AND agent = 'qc' ORDER BY id ASC;",
                (str(task_row["id"]),)
            ).fetchall()
            self.assertEqual(len(qc_traces), 4)
            self.assertEqual(qc_traces[0]["outcome"], "failed")
            self.assertEqual(qc_traces[1]["outcome"], "failed")
            self.assertEqual(qc_traces[2]["outcome"], "failed")
            self.assertEqual(qc_traces[3]["outcome"], "completed")

    def test_adv_04_alternating_peer_and_qc_failures(self):
        """
        Alternating failure sequence:
        - Attempt 1: Peer fails
        - Attempt 2: Peer passes, QC fails
        - Attempt 3: Peer fails
        - Attempt 4: Peer passes, QC fails -> All 3 retries exhausted -> Blocked!
        Verify exactly 4 total attempts, exactly 4 peer spans, exactly 2 qc spans.
        """
        peer_counter_file = self.test_root / "peer_counter.txt"
        peer_counter_file.write_text("0", encoding="utf-8")

        script_file = self.test_root / "alternating_test.py"
        script_file.write_text(f"""
import sys, pathlib
p = pathlib.Path("{peer_counter_file}")
c = int(p.read_text()) if p.exists() else 0
p.write_text(str(c + 1))
if (c + 1) in (1, 3):
    sys.stderr.write(f"Peer Failure on Attempt #{{c + 1}}\\n")
    sys.exit(1)
sys.exit(0)
""", encoding="utf-8")

        qc_call_count = {"count": 0}

        def adversarial_qc(*args, **kwargs):
            qc_call_count["count"] += 1
            return False, f"QC Rejection on Attempt #{qc_call_count['count']}"

        with patch("scripts.run_pipeline.run_qc_tail_gate", side_effect=adversarial_qc):
            exit_code = run_pipeline.main([
                "[THUẬN] - Alternating fail test",
                "--test-cmd", f"python3 {script_file}"
            ])
            self.assertEqual(exit_code, 1, "Pipeline must exit 1 after 4 alternating failures")

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            task_row = cur.execute("SELECT id, state FROM work_item WHERE type = 'Task' ORDER BY id DESC LIMIT 1;").fetchone()
            self.assertEqual(task_row["state"], "Blocked")

            peer_traces = cur.execute("SELECT id, outcome FROM trace WHERE story_id = ? AND agent = 'peer';", (str(task_row["id"]),)).fetchall()
            qc_traces = cur.execute("SELECT id, outcome FROM trace WHERE story_id = ? AND agent = 'qc';", (str(task_row["id"]),)).fetchall()
            
            self.assertEqual(len(peer_traces), 4, "Peer should have run exactly 4 times")
            self.assertEqual(len(qc_traces), 2, "QC should have run exactly 2 times (attempts 2 and 4)")

    def test_adv_05_verbatim_error_message_passing_and_stdout_fallback(self):
        """
        Verify:
        - When command outputs to stderr, exact stderr is captured in trace and error_context.
        - When command outputs ONLY to stdout, stdout is captured as fallback.
        - Special characters, Vietnamese Unicode, JSON payloads, and quotes are preserved verbatim without corruption.
        """
        test_payload = "❌ [LỖI NGHIÊM TRỌNG]: KeyError('missing_token') tại line 42; Payload: {\"status\": 500}"
        
        script_file = self.test_root / "unicode_error.py"
        script_file.write_text(f"""
import sys
sys.stderr.write({repr(test_payload)} + "\\n")
sys.exit(1)
""", encoding="utf-8")

        exit_code = run_pipeline.main(["[THUẬN] - Unicode error test", "--test-cmd", f"python3 {script_file}"])
        self.assertEqual(exit_code, 1)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            traces = cur.execute("SELECT errors FROM trace WHERE agent = 'peer' AND errors IS NOT NULL;").fetchall()
            self.assertTrue(len(traces) > 0)
            for t in traces:
                self.assertIn(test_payload, t["errors"])

        # Test stdout fallback
        stdout_payload = "STDOUT_ONLY_FAILURE: Test runner exited with assertion error"
        script_stdout = self.test_root / "stdout_error.py"
        script_stdout.write_text(f"""
import sys
sys.stdout.write({repr(stdout_payload)} + "\\n")
sys.exit(2)
""", encoding="utf-8")

        exit_code2 = run_pipeline.main(["[THUẬN] - Stdout error test", "--test-cmd", f"python3 {script_stdout}"])
        self.assertEqual(exit_code2, 1)

        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            traces2 = cur.execute("SELECT errors FROM trace WHERE agent = 'peer' ORDER BY id DESC LIMIT 1;").fetchone()
            self.assertIn(stdout_payload, traces2["errors"])

    # =========================================================================
    # 3. BOTH TASK AND EPIC UPDATED TO BLOCKED
    # =========================================================================

    def test_adv_06_both_task_and_epic_updated_to_blocked(self):
        """
        Verify that when pipeline retries are exhausted:
        1. Task is set to state 'Blocked'.
        2. Epic is set to state 'Blocked'.
        3. Work item types and assigned profiles remain intact.
        """
        fail_cmd = "python3 -c 'import sys; sys.stderr.write(\"Persistent Block Test Error\\n\"); sys.exit(1)'"
        exit_code = run_pipeline.main(["[THUẬN] - State escalation test", "--test-cmd", fail_cmd])
        self.assertEqual(exit_code, 1)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            task_row = cur.execute("SELECT id, type, state, parent_id, assigned_to_profile FROM work_item WHERE type = 'Task' ORDER BY id DESC LIMIT 1;").fetchone()
            self.assertIsNotNone(task_row)
            self.assertEqual(task_row["state"], "Blocked", "Task state must be Blocked")
            self.assertEqual(task_row["assigned_to_profile"], "peer")

            epic_id = task_row["parent_id"]
            self.assertIsNotNone(epic_id)
            epic_row = cur.execute("SELECT id, type, state, assigned_to_profile FROM work_item WHERE id = ?;", (epic_id,)).fetchone()
            self.assertIsNotNone(epic_row)
            self.assertEqual(epic_row["type"], "Epic")
            self.assertEqual(epic_row["state"], "Blocked", "Epic state must be Blocked")
            self.assertEqual(epic_row["assigned_to_profile"], "lead")

    # =========================================================================
    # 4. SUPERVISOR MEMO LINE COUNT & ZERO-LEAK AUDIT
    # =========================================================================

    def test_adv_07_supervisor_memo_size_and_zero_leak(self):
        """
        Verify:
        - latest_handoff.md is created under bmad/rooms/supervisor/.
        - Total lines <= 150.
        - Zero-leak clean (no internal URLs, secrets, phone numbers, API keys, etc.).
        """
        fail_cmd = "python3 -c 'import sys; sys.stderr.write(\"Zero Leak Fail Check\\n\"); sys.exit(1)'"
        exit_code = run_pipeline.main(["[THUẬN] - Memo audit test", "--test-cmd", fail_cmd])
        self.assertEqual(exit_code, 1)

        self.assertTrue(self.sup_handoff_path.exists(), f"Expected supervisor memo at {self.sup_handoff_path}")

        content = self.sup_handoff_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        self.assertLessEqual(
            len(lines), 150,
            f"Supervisor memo exceeded 150 lines: got {len(lines)} lines"
        )
        self.assertIn("Blocked", content)
        self.assertIn("Run ID", content)
        self.assertIn("Tổng số lần thử", content)

        # Anti-leak audit: forbidden patterns
        leak_patterns = [
            r"ghp_[a-zA-Z0-9]{36}",
            r"AIza[0-9A-Za-z-_]{35}",
            r"sk-[a-zA-Z0-9]{48}",
            r"09\d{8}",
            r"03\d{8}",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
            r"192\.168\.\d+\.\d+",
            r"10\.\d+\.\d+\.\d+",
        ]
        for pat in leak_patterns:
            matches = re.findall(pat, content)
            self.assertEqual(matches, [], f"Detected potential secret leak in supervisor memo matching: {pat}")

    # =========================================================================
    # 5. SHARED RUN_ID CONTINUITY ACROSS ALL TRACE SPANS
    # =========================================================================

    def test_adv_08_shared_run_id_across_all_spans_in_normal_and_retry_flows(self):
        """
        Verify:
        - In a normal flow (head, lead, peer, qc): all spans share 1 identical run_id.
        - In a multi-retry flow (head, lead, 4x peer, 4x qc): all 10 spans share the exact same run_id.
        - run_id format adheres strictly to ^run_\\d+_[a-f0-9]{8}$.
        """
        # Test normal flow
        exit_code = run_pipeline.main(["[THUẬN] - Shared run_id normal flow", "--test-cmd", "python3 -c 'import sys; sys.exit(0)'"])
        self.assertEqual(exit_code, 0)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT run_id, notes, outcome FROM trace ORDER BY id DESC LIMIT 4;").fetchall()
            run_ids = {r["run_id"] for r in rows}
            self.assertEqual(len(run_ids), 1, f"Expected 1 shared run_id, got {run_ids}")
            shared_id = list(run_ids)[0]
            self.assertRegex(shared_id, r"^run_\d+_[a-f0-9]{8}$")

        # Test retry flow
        fail_cmd = "python3 -c 'import sys; sys.stderr.write(\"Retry RunID Check\\n\"); sys.exit(1)'"
        exit_code2 = run_pipeline.main(["[THUẬN] - Shared run_id retry flow", "--test-cmd", fail_cmd])
        self.assertEqual(exit_code2, 1)

        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            latest_task = cur.execute("SELECT id FROM work_item WHERE type = 'Task' ORDER BY id DESC LIMIT 1;").fetchone()
            task_traces = cur.execute("SELECT run_id, notes, agent FROM trace WHERE story_id = ?;", (str(latest_task["id"]),)).fetchall()
            self.assertEqual(len(task_traces), 5) # 1 lead + 4 peer traces
            task_run_ids = {t["run_id"] for t in task_traces}
            self.assertEqual(len(task_run_ids), 1)

            # Check that head is also linked by the same run_id
            shared_run_id = list(task_run_ids)[0]
            all_run_traces = cur.execute("SELECT agent FROM trace WHERE run_id = ?;", (shared_run_id,)).fetchall()
            self.assertEqual(len(all_run_traces), 6) # 1 head + 1 lead + 4 peer traces

    def test_adv_09_shared_run_id_in_discussion_mode(self):
        """
        Verify that in [THẢO LUẬN] mode:
        - head, lead, and discussion spans are emitted.
        - All spans share the identical run_id.
        - No peer or qc spans are emitted.
        """
        exit_code = run_pipeline.main(["[THẢO LUẬN] - Architectural evaluation of database caching"])
        self.assertEqual(exit_code, 0)

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            traces = cur.execute("SELECT run_id, task_summary, notes FROM trace ORDER BY id DESC LIMIT 3;").fetchall()
            self.assertEqual(len(traces), 3)
            run_ids = {t["run_id"] for t in traces}
            self.assertEqual(len(run_ids), 1, f"Expected 1 run_id in discussion mode, got {run_ids}")
            notes_joined = " ".join([t["notes"] or "" for t in traces])
            self.assertIn("stage=head", notes_joined)
            self.assertIn("stage=lead", notes_joined)
            self.assertIn("stage=discussion", notes_joined)

    # =========================================================================
    # 6. SQLITE SCHEMA & FOREIGN KEY RESILIENCE (NUMERIC STUBS)
    # =========================================================================

    def test_adv_10_sqlite_strict_foreign_keys_numeric_stubs(self):
        """
        Verify that numeric story IDs and intake IDs correctly generate stub rows
        and allow trace span insertion under PRAGMA foreign_keys = ON.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        # Numeric string story_id
        trace_id1 = mgr.record_trace_span(
            run_id="run_1234567890_abcdef12",
            stage="peer",
            agent="peer",
            task_summary="Trace span with numeric story_id",
            duration_seconds=5,
            outcome="completed",
            story_id="999999",
            intake_id=888888
        )
        self.assertGreater(trace_id1, 0)

        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            story = cur.execute("SELECT id FROM story WHERE id = 999999;").fetchone()
            self.assertIsNotNone(story)
            intake = cur.execute("SELECT id FROM intake WHERE id = 888888;").fetchone()
            self.assertIsNotNone(intake)

        # None story_id and None intake_id
        trace_id2 = mgr.record_trace_span(
            run_id="run_1234567890_abcdef12",
            stage="head",
            agent="supervisor",
            task_summary="Trace span with None story and intake",
            duration_seconds=1,
            outcome="completed",
            story_id=None,
            intake_id=None
        )
        self.assertGreater(trace_id2, 0)

    def test_adv_11_legacy_sqlite_trace_migration_preserves_data(self):
        """
        Verify that when a legacy trace table (e.g. from an older schema with 'content' column)
        is encountered, the auto-migration preserves legacy records and accepts new spans with run_id.
        """
        legacy_db_path = str(self.test_root / "legacy_migration_test.db")
        conn = sqlite3.connect(legacy_db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE trace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                tier TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
        cur.execute("INSERT INTO trace (content, tier) VALUES ('Legacy trace item 1', 'bronze');")
        cur.execute("INSERT INTO trace (content, tier) VALUES ('Legacy trace item 2', 'silver');")
        conn.commit()
        conn.close()

        mgr = HarnessManager(engine="sqlite", db_path=legacy_db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT id, task_summary, notes, run_id FROM trace ORDER BY id ASC;").fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["task_summary"], "Legacy trace item 1")
            self.assertIn("tier=bronze", rows[0]["notes"] or "")

        new_id = mgr.record_trace_span(
            run_id="run_9999999999_fedcba98",
            stage="lead",
            agent="lead",
            task_summary="Post-migration newly inserted span",
            duration_seconds=3,
            outcome="completed"
        )
        self.assertEqual(new_id, 3)

        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            new_row = cur.execute("SELECT run_id, task_summary FROM trace WHERE id = 3;").fetchone()
            self.assertEqual(new_row["run_id"], "run_9999999999_fedcba98")
            self.assertEqual(new_row["task_summary"], "Post-migration newly inserted span")

    # =========================================================================
    # 7. AUTO_DISPATCH_AGENT BLOCKED STATE ESCALATION
    # =========================================================================

    def test_adv_12_auto_dispatch_agent_handles_blocked_state(self):
        """
        Verify auto_dispatch_agent on 'Blocked':
        - Dispatches notification to 'supervisor'.
        - Calls close_ephemeral_subagent for 'peer' and 'qc'.
        - Records heartbeat ping.
        """
        import tools.agent_heartbeat
        try:
            import agent_heartbeat
        except ImportError:
            agent_heartbeat = tools.agent_heartbeat

        with patch("tools.harness_manager.send_orca_notification") as mock_notify, \
             patch("tools.harness_manager.close_ephemeral_subagent") as mock_close, \
             patch.object(tools.agent_heartbeat, "record_ping") as mock_ping1, \
             patch.object(agent_heartbeat, "record_ping") as mock_ping2:

            auto_dispatch_agent(
                item_id=101,
                wi_type="Task",
                title="[Exec] - Test Critical Failure",
                target_state="Blocked",
                assigned_to="peer",
                assigned_to_profile="peer",
                prev_state="Active"
            )

            mock_notify.assert_called_once()
            call_role, call_msg = mock_notify.call_args[0]
            self.assertEqual(call_role, "supervisor")
            self.assertIn("TASK BLOCKED", call_msg)
            self.assertIn("#101", call_msg)

            closed_roles = [call_args[0][0] for call_args in mock_close.call_args_list]
            self.assertIn("peer", closed_roles)
            self.assertIn("qc", closed_roles)

            self.assertTrue(mock_ping1.called or mock_ping2.called)

    # =========================================================================
    # 8. EMPIRICAL VULNERABILITY REPRODUCTION: FOREIGN KEY CONSTRAINTS
    # =========================================================================

    def test_adv_13_empirical_vulnerability_alphanumeric_story_id_crashes_on_foreign_keys(self):
        """
        REGRESSION TEST FOR FOREIGN KEY CONSTRAINTS ON ALPHANUMERIC STORY_ID:
        When PRAGMA foreign_keys = ON, passing an alphanumeric story_id (e.g. 'US-001' or 'story_alpha_99')
        must cleanly record the trace span with 0 foreign key exceptions, recording story_id in notes
        when story.id is strictly INTEGER, and returning story_id transparently on lookup.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        trace_id = mgr.record_trace_span(
            run_id="run_1234567890_abcdef12",
            stage="qc",
            agent="qc",
            task_summary="Trace span with alphanumeric story_id",
            duration_seconds=2,
            outcome="completed",
            story_id="US-001"
        )
        self.assertGreater(trace_id, 0)

        # Verify trace retrieval transparently preserves story_id
        t = mgr.get_trace(trace_id)
        self.assertIsNotNone(t)
        self.assertEqual(t.get("story_id"), "US-001")

        # Verify list_traces finds it by story_id filter
        traces = mgr.list_traces(story_id="US-001")
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["id"], trace_id)

    def test_adv_14_empirical_vulnerability_001_init_schema_crashes_on_foreign_keys(self):
        """
        REGRESSION TEST FOR 001-INIT.SQL CANONICAL SCHEMA UNDER FOREIGN KEYS:
        When a database is initialized using 001-init.sql, inserting a trace span
        referencing a new story_id must succeed cleanly with 0 foreign key exceptions,
        adaptively creating stub records matching the 001-init schema columns.
        """
        init_db_path = str(self.test_root / "init_001_harness.db")
        conn = sqlite3.connect(init_db_path)
        with open(BASE_DIR / "scripts" / "schema" / "001-init.sql") as f:
            conn.executescript(f.read())
        conn.close()

        # Connect with HarnessManager pointing to 001-init.sql database
        mgr = HarnessManager(engine="sqlite", db_path=init_db_path)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        trace_id = mgr.record_trace_span(
            run_id="run_1234567890_abcdef12",
            stage="peer",
            agent="peer",
            task_summary="Trace span on 001-init DB",
            duration_seconds=3,
            outcome="completed",
            story_id="12345"
        )
        self.assertGreater(trace_id, 0)

        # Verify trace retrieval
        t = mgr.get_trace(trace_id)
        self.assertIsNotNone(t)
        self.assertEqual(t.get("story_id"), "12345")


if __name__ == "__main__":
    unittest.main()
