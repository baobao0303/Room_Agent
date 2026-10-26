#!/usr/bin/env python3
"""
Adversarial Challenger Test Suite: Milestone 2 Iteration 2
Comprehensive empirical stress tests for Foreign Key Constraint & Trace Integrity.

Tests cover:
1. Alphanumeric story IDs ("US-001", "story_alpha_99", "EPIC-404", "feat/auth", spaces, unicode)
2. Integer story IDs (101, "202", 0, -5, large ints)
3. Non-existent and pre-existing intake IDs
4. Schema variants: full_schema.sql vs 001-init.sql
5. Strict enforcement of PRAGMA foreign_keys = ON;
6. Query precision in get_trace() and list_traces(story_id="...") (exact matching, no false positives)
7. Notes co-existence with custom user notes and stage tags
8. Unresolvable schema constraints fallback (strict NOT NULL without default)
9. Multi-span trace execution with shared run_id and alphanumeric story_id
"""

import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.harness_manager import HarnessManager


class TestM2It2AdversarialChallenger(unittest.TestCase):
    """Deep adversarial stress testing for trace foreign keys and query integrity."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_m2_it2_fk_")
        self.full_schema_db = os.path.join(self.test_dir, "full_schema.db")
        self.init_001_db = os.path.join(self.test_dir, "init_001.db")

        # Initialize full_schema.sql DB
        conn_full = sqlite3.connect(self.full_schema_db)
        with open(BASE_DIR / "scripts" / "schema" / "full_schema.sql") as f:
            conn_full.executescript(f.read())
        conn_full.close()

        # Initialize 001-init.sql DB
        conn_init = sqlite3.connect(self.init_001_db)
        with open(BASE_DIR / "scripts" / "schema" / "001-init.sql") as f:
            conn_init.executescript(f.read())
        conn_init.close()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # =========================================================================
    # 1. ALPHANUMERIC STORY IDS ON full_schema.sql (INTEGER PRIMARY KEY)
    # =========================================================================

    def test_adv2_01_alphanumeric_story_ids_on_full_schema(self):
        """
        Under full_schema.sql, story.id is INTEGER PRIMARY KEY AUTOINCREMENT.
        Alphanumeric story IDs cannot be inserted into story.id.
        Verification:
        - Insertion succeeds with 0 exceptions under PRAGMA foreign_keys = ON.
        - trace.story_id in SQLite is NULL to satisfy the foreign key constraint.
        - story_id is preserved in notes as story_id=<id>.
        - get_trace() returns the original alphanumeric story_id.
        - list_traces(story_id=...) finds the record.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.full_schema_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        test_story_ids = [
            "US-001",
            "story_alpha_99",
            "EPIC-404",
            "FEAT/M2-AUTH-LOGIN",
            "STORY WITH SPACES",
            "STORY_TIẾNG_VIỆT_123",
            "US_SPECIAL!@#$",
        ]

        for s_id in test_story_ids:
            trace_id = mgr.record_trace_span(
                run_id="run_1001_alphanumeric",
                stage="lead",
                agent="lead",
                task_summary=f"Trace span for {s_id}",
                duration_seconds=5,
                outcome="completed",
                story_id=s_id,
            )
            self.assertGreater(trace_id, 0, f"Failed to record trace for {s_id}")

            # Verify raw DB state has foreign keys satisfied
            with mgr._get_sqlite_db() as conn:
                row = conn.execute("SELECT id, story_id, notes FROM trace WHERE id = ?", (trace_id,)).fetchone()
                self.assertIsNotNone(row)
                # In full_schema.sql, story.id is INT, so raw column must be NULL
                self.assertIsNone(row["story_id"])
                self.assertIn(f"story_id={s_id}", row["notes"])

            # Verify get_trace transparently returns original story_id
            t = mgr.get_trace(trace_id)
            self.assertIsNotNone(t)
            self.assertEqual(t.get("story_id"), s_id)

            # Verify list_traces finds it
            traces = mgr.list_traces(story_id=s_id)
            self.assertGreaterEqual(len(traces), 1)
            found_ids = [tr["id"] for tr in traces]
            self.assertIn(trace_id, found_ids)

    # =========================================================================
    # 2. INTEGER STORY IDS ON full_schema.sql
    # =========================================================================

    def test_adv2_02_integer_story_ids_on_full_schema(self):
        """
        Under full_schema.sql, integer story IDs (both int and digit-strings)
        should create a stub record in story and link directly in trace.story_id.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.full_schema_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        test_cases = [
            (101, "101"),
            ("202", "202"),
            (0, "0"),
            (999999, "999999"),
        ]

        for input_id, expected_str in test_cases:
            trace_id = mgr.record_trace_span(
                run_id="run_1002_integer",
                stage="peer",
                agent="peer",
                task_summary=f"Trace span for int story {input_id}",
                duration_seconds=3,
                outcome="completed",
                story_id=input_id,
            )
            self.assertGreater(trace_id, 0)

            # Verify raw DB state: story stub created, trace.story_id is populated
            with mgr._get_sqlite_db() as conn:
                story_row = conn.execute("SELECT id, title, state FROM story WHERE id = ?", (int(expected_str),)).fetchone()
                self.assertIsNotNone(story_row)
                self.assertEqual(story_row["state"], "New")

                trace_row = conn.execute("SELECT story_id FROM trace WHERE id = ?", (trace_id,)).fetchone()
                self.assertEqual(str(trace_row["story_id"]), expected_str)

            # Verify get_trace
            t = mgr.get_trace(trace_id)
            self.assertEqual(str(t.get("story_id")), expected_str)

            # Verify list_traces with both int and string search
            traces_str = mgr.list_traces(story_id=expected_str)
            self.assertIn(trace_id, [tr["id"] for tr in traces_str])

    # =========================================================================
    # 3. ALPHANUMERIC & INTEGER STORY IDS ON 001-init.sql (TEXT PRIMARY KEY)
    # =========================================================================

    def test_adv2_03_alphanumeric_and_integer_story_ids_on_001_init_schema(self):
        """
        Under 001-init.sql, story.id is TEXT PRIMARY KEY, with NOT NULL columns:
        - risk_lane TEXT NOT NULL CHECK(risk_lane IN ('tiny','normal','high_risk'))
        - status TEXT NOT NULL DEFAULT 'planned'
        Verification:
        - Stub records inserted satisfy all column constraints and CHECK constraints.
        - trace.story_id references story(id) directly as TEXT under PRAGMA foreign_keys = ON.
        - get_trace and list_traces return exact results.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.init_001_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        test_ids = ["US-001", "story_alpha_99", "EPIC-404", "101", "202"]

        for s_id in test_ids:
            trace_id = mgr.record_trace_span(
                run_id="run_1003_001_init",
                stage="qc",
                agent="qc",
                task_summary=f"Trace span on 001-init for {s_id}",
                duration_seconds=4,
                outcome="completed",
                story_id=s_id,
            )
            self.assertGreater(trace_id, 0)

            # Check that story stub exists in 001-init DB with compliant constraints
            with mgr._get_sqlite_db() as conn:
                s_row = conn.execute("SELECT id, title, risk_lane, status FROM story WHERE id = ?", (s_id,)).fetchone()
                self.assertIsNotNone(s_row)
                self.assertEqual(s_row["risk_lane"], "normal")
                self.assertEqual(s_row["status"], "planned")

                t_row = conn.execute("SELECT story_id FROM trace WHERE id = ?", (trace_id,)).fetchone()
                self.assertEqual(t_row["story_id"], s_id)

            t = mgr.get_trace(trace_id)
            self.assertEqual(t.get("story_id"), s_id)

            traces = mgr.list_traces(story_id=s_id)
            self.assertIn(trace_id, [tr["id"] for tr in traces])

    # =========================================================================
    # 4. INTAKE ID INTEGRITY ON BOTH SCHEMAS
    # =========================================================================

    def test_adv2_04_intake_id_foreign_key_handling_full_schema(self):
        """
        On full_schema.sql, intake.id is INTEGER PRIMARY KEY AUTOINCREMENT.
        When non-existent intake_id is provided, stub record is created cleanly.
        When intake_id is None, trace.intake_id is NULL.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.full_schema_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        # Case A: Non-existent intake_id
        trace_id1 = mgr.record_trace_span(
            run_id="run_1004_intake",
            stage="head",
            agent="supervisor",
            task_summary="Non-existent intake trace",
            duration_seconds=1,
            outcome="completed",
            intake_id=7777,
        )
        self.assertGreater(trace_id1, 0)

        with mgr._get_sqlite_db() as conn:
            intake_row = conn.execute("SELECT id, title, state FROM intake WHERE id = 7777").fetchone()
            self.assertIsNotNone(intake_row)
            self.assertEqual(intake_row["title"], "Intake #7777")
            self.assertEqual(intake_row["state"], "New")

            trace_row = conn.execute("SELECT intake_id FROM trace WHERE id = ?", (trace_id1,)).fetchone()
            self.assertEqual(trace_row["intake_id"], 7777)

        # Case B: Pre-existing intake_id (must not be clobbered)
        with mgr._get_sqlite_db() as conn:
            conn.execute("INSERT INTO intake (id, title, state) VALUES (8888, 'Existing Intake Title', 'Active');")
            conn.commit()

        trace_id2 = mgr.record_trace_span(
            run_id="run_1004_intake",
            stage="head",
            agent="supervisor",
            task_summary="Existing intake trace",
            duration_seconds=1,
            outcome="completed",
            intake_id=8888,
        )
        self.assertGreater(trace_id2, 0)

        with mgr._get_sqlite_db() as conn:
            intake_row2 = conn.execute("SELECT title, state FROM intake WHERE id = 8888").fetchone()
            self.assertEqual(intake_row2["title"], "Existing Intake Title")
            self.assertEqual(intake_row2["state"], "Active")

        # Case C: None intake_id
        trace_id3 = mgr.record_trace_span(
            run_id="run_1004_intake",
            stage="head",
            agent="supervisor",
            task_summary="None intake trace",
            duration_seconds=1,
            outcome="completed",
            intake_id=None,
        )
        with mgr._get_sqlite_db() as conn:
            trace_row3 = conn.execute("SELECT intake_id FROM trace WHERE id = ?", (trace_id3,)).fetchone()
            self.assertIsNone(trace_row3["intake_id"])

    def test_adv2_05_intake_id_foreign_key_handling_001_init_schema(self):
        """
        On 001-init.sql, intake table has strict constraints:
        - input_type NOT NULL CHECK(...)
        - summary NOT NULL
        - risk_lane NOT NULL CHECK(...)
        Verification:
        - Stubs inserted into intake satisfy all CHECK and NOT NULL constraints.
        - trace.intake_id references intake(id) with PRAGMA foreign_keys = ON.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.init_001_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        trace_id = mgr.record_trace_span(
            run_id="run_1005_intake_001",
            stage="head",
            agent="supervisor",
            task_summary="001-init intake trace",
            duration_seconds=2,
            outcome="completed",
            intake_id=5555,
        )
        self.assertGreater(trace_id, 0)

        with mgr._get_sqlite_db() as conn:
            intake_row = conn.execute("SELECT id, summary, input_type, risk_lane FROM intake WHERE id = 5555").fetchone()
            self.assertIsNotNone(intake_row)
            self.assertEqual(intake_row["summary"], "Intake #5555")
            self.assertEqual(intake_row["input_type"], "maintenance")
            self.assertEqual(intake_row["risk_lane"], "normal")

            trace_row = conn.execute("SELECT intake_id FROM trace WHERE id = ?", (trace_id,)).fetchone()
            self.assertEqual(trace_row["intake_id"], 5555)

    # =========================================================================
    # 5. QUERY PRECISION & EXACT MATCHING (NO FALSE POSITIVES)
    # =========================================================================

    def test_adv2_06_list_traces_exact_story_id_filtering_no_false_positives(self):
        """
        Adversarial search collision test:
        If trace A has story_id="US-001", trace B has "US-0010", trace C has "NOT-US-001",
        list_traces(story_id="US-001") MUST return only trace A (and other exact matches),
        and NEVER return trace B or trace C.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.full_schema_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        id_a = mgr.record_trace_span(
            run_id="run_coll_1", stage="peer", agent="peer",
            task_summary="Span A", duration_seconds=1, outcome="completed",
            story_id="US-001",
        )
        id_b = mgr.record_trace_span(
            run_id="run_coll_2", stage="peer", agent="peer",
            task_summary="Span B", duration_seconds=1, outcome="completed",
            story_id="US-0010",
        )
        id_c = mgr.record_trace_span(
            run_id="run_coll_3", stage="peer", agent="peer",
            task_summary="Span C", duration_seconds=1, outcome="completed",
            story_id="NOT-US-001",
        )
        id_d = mgr.record_trace_span(
            run_id="run_coll_4", stage="qc", agent="qc",
            task_summary="Span D", duration_seconds=1, outcome="completed",
            story_id="US-001",
        )

        # Query for "US-001"
        res_001 = mgr.list_traces(story_id="US-001")
        matched_ids = [r["id"] for r in res_001]
        self.assertIn(id_a, matched_ids)
        self.assertIn(id_d, matched_ids)
        self.assertNotIn(id_b, matched_ids, "False positive: US-0010 matched query for US-001")
        self.assertNotIn(id_c, matched_ids, "False positive: NOT-US-001 matched query for US-001")

        # Query for "US-0010"
        res_0010 = mgr.list_traces(story_id="US-0010")
        matched_0010_ids = [r["id"] for r in res_0010]
        self.assertEqual(matched_0010_ids, [id_b])

    # =========================================================================
    # 6. NOTES CO-EXISTENCE AND CUSTOM NOTES
    # =========================================================================

    def test_adv2_07_notes_coexistence_with_custom_user_notes(self):
        """
        When custom notes are provided along with alphanumeric story_id and stage,
        all fields must coexist without clobbering each other.
        get_trace() must extract story_id accurately.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.full_schema_db)
        custom_notes = "user_custom_data=12345; reason=hotfix; priority=P0"

        trace_id = mgr.record_trace_span(
            run_id="run_notes_1",
            stage="qc",
            agent="qc",
            task_summary="Custom notes trace",
            duration_seconds=2,
            outcome="completed",
            story_id="HOTFIX-999",
            notes=custom_notes,
        )

        t = mgr.get_trace(trace_id)
        self.assertEqual(t.get("story_id"), "HOTFIX-999")
        self.assertIn("user_custom_data=12345", t.get("notes", ""))
        self.assertIn("stage=qc", t.get("notes", ""))
        self.assertIn("story_id=HOTFIX-999", t.get("notes", ""))

        traces = mgr.list_traces(story_id="HOTFIX-999")
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["id"], trace_id)

    # =========================================================================
    # 7. UNRESOLVABLE SCHEMA CONSTRAINTS GRACEFUL FALLBACK
    # =========================================================================

    def test_adv2_08_unresolvable_schema_constraints_graceful_fallback(self):
        """
        Simulate an adversarial schema modification:
        Add a strict NOT NULL column without a default to story table.
        Stub insertion into story will fail.
        Verification:
        - record_trace does NOT crash with sqlite3.IntegrityError.
        - trace row is inserted with final_story_id = None.
        - story_id is stored in notes.
        - get_trace() returns the expected story_id.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.init_001_db)
        with mgr._get_sqlite_db() as conn:
            # Add strict NOT NULL column
            conn.execute("ALTER TABLE story ADD COLUMN unfulfillable_field TEXT;")
            # Now trigger a trigger or constraint that blocks insert without unfulfillable_field
            conn.execute("""
                CREATE TRIGGER strict_story_insert BEFORE INSERT ON story
                WHEN NEW.unfulfillable_field IS NULL
                BEGIN
                    SELECT RAISE(ABORT, 'unfulfillable_field is strictly required');
                END;
            """)
            conn.commit()

        # Now attempt to record a trace with a new story_id
        trace_id = mgr.record_trace_span(
            run_id="run_fallback_1",
            stage="peer",
            agent="peer",
            task_summary="Trace with unfulfillable story stub",
            duration_seconds=3,
            outcome="completed",
            story_id="STORY-FALLBACK-1",
        )
        self.assertGreater(trace_id, 0)

        # Verify trace was stored safely with foreign keys satisfied
        with mgr._get_sqlite_db() as conn:
            row = conn.execute("SELECT story_id, notes FROM trace WHERE id = ?", (trace_id,)).fetchone()
            self.assertIsNone(row["story_id"])
            self.assertIn("story_id=STORY-FALLBACK-1", row["notes"])

        t = mgr.get_trace(trace_id)
        self.assertEqual(t.get("story_id"), "STORY-FALLBACK-1")

    # =========================================================================
    # 8. MULTI-SPAN PIPELINE TRACE CONTINUITY UNDER FOREIGN KEYS
    # =========================================================================

    def test_adv2_09_multi_span_pipeline_continuity_under_foreign_keys(self):
        """
        Simulate an entire multi-stage pipeline run (head -> lead -> peer -> qc)
        sharing the same run_id and alphanumeric story_id, strictly enforcing foreign keys.
        Verification:
        - All 4 spans record cleanly with 0 exceptions.
        - list_traces(run_id=...) returns all 4 spans in correct order.
        - list_traces(story_id=...) returns all 4 spans.
        - get_trace for each returns the shared alphanumeric story_id.
        """
        mgr = HarnessManager(engine="sqlite", db_path=self.full_schema_db)
        with mgr._get_sqlite_db() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")

        run_id = "run_20261026_spec_hardening_01"
        story_id = "US-HARDENING-001"
        stages = [
            ("head", "supervisor", "Intent and feasibility triage", 2),
            ("lead", "lead", "Architecture and task decomposition", 8),
            ("peer", "peer", "Code implementation and local tests", 45),
            ("qc", "qc", "ISTQB verification and acceptance gate", 12),
        ]

        recorded_ids = []
        for stage, agent, summary, dur in stages:
            tid = mgr.record_trace_span(
                run_id=run_id,
                stage=stage,
                agent=agent,
                task_summary=summary,
                duration_seconds=dur,
                outcome="completed",
                story_id=story_id,
            )
            self.assertGreater(tid, 0)
            recorded_ids.append(tid)

        # Check run_id continuity
        run_traces = mgr.list_traces(run_id=run_id, limit=10)
        self.assertEqual(len(run_traces), 4)
        run_trace_ids = [t["id"] for t in run_traces]
        for tid in recorded_ids:
            self.assertIn(tid, run_trace_ids)

        # Check story_id continuity
        story_traces = mgr.list_traces(story_id=story_id, limit=10)
        self.assertEqual(len(story_traces), 4)

        for tid in recorded_ids:
            t = mgr.get_trace(tid)
            self.assertEqual(t.get("story_id"), story_id)


if __name__ == "__main__":
    unittest.main()
