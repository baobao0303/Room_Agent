#!/usr/bin/env python3
"""
tools/tests/test_trace_schema.py - Test suite for G-OBS-1 unified trace schema & auto-migration.
Verifies canonical 16 columns + run_id, auto-migration from legacy tables,
and trace / intervention recording helpers.
"""

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
from tools.harness_manager import HarnessManager


class TestTraceSchemaAndObservability(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_harness.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_fresh_db_canonical_schema(self):
        """Verify that a fresh SQLite database creates trace table with all 17 canonical columns."""
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            cols = {r[1]: r[2] for r in cur.execute("PRAGMA table_info(trace);").fetchall()}

        expected_columns = {
            "id": "INTEGER",
            "created_at": "TEXT",
            "task_summary": "TEXT",
            "intake_id": "INTEGER",
            "story_id": "TEXT",
            "agent": "TEXT",
            "actions_taken": "TEXT",
            "files_read": "TEXT",
            "files_changed": "TEXT",
            "decisions_made": "TEXT",
            "errors": "TEXT",
            "outcome": "TEXT",
            "duration_seconds": "INTEGER",
            "token_estimate": "INTEGER",
            "harness_friction": "TEXT",
            "notes": "TEXT",
            "run_id": "TEXT",
        }

        for col, col_type in expected_columns.items():
            self.assertIn(col, cols, f"Canonical column '{col}' missing from trace table!")
            self.assertEqual(cols[col], col_type, f"Column '{col}' expected type '{col_type}', got '{cols[col]}'")

    def test_02_auto_migration_empty_legacy_db(self):
        """Verify that an empty legacy truncated trace table is dropped and recreated canonically."""
        # Create legacy table with 5 columns
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE trace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER,
                tier INTEGER NOT NULL DEFAULT 1,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        conn.close()

        # Opening with HarnessManager triggers auto-migration
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            cols = {r[1] for r in cur.execute("PRAGMA table_info(trace);").fetchall()}

        self.assertIn("task_summary", cols)
        self.assertIn("run_id", cols)
        self.assertIn("duration_seconds", cols)
        self.assertIn("token_estimate", cols)

    def test_03_auto_migration_populated_legacy_db(self):
        """Verify that a populated legacy trace table is migrated via table-copy preserving data and accepting new traces."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE trace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER,
                tier INTEGER NOT NULL DEFAULT 1,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.execute("INSERT INTO trace (story_id, tier, content) VALUES (101, 2, 'historical trace content');")
        conn.commit()
        conn.close()

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            cols = {r[1] for r in cur.execute("PRAGMA table_info(trace);").fetchall()}
            row = cur.execute("SELECT * FROM trace WHERE id = 1;").fetchone()

        self.assertIn("task_summary", cols)
        self.assertIn("run_id", cols)
        self.assertNotIn("content", cols, "Legacy 'content' column should be retired during table-copy migration")
        self.assertEqual(row["task_summary"], "historical trace content")
        self.assertEqual(str(row["story_id"]), "101")
        self.assertIn("migrated_legacy", row["notes"])

        # Backward compatibility check via get_trace()
        hist = mgr.get_trace(1)
        self.assertIsNotNone(hist)
        self.assertEqual(hist["task_summary"], "historical trace content")
        self.assertEqual(hist["content"], "historical trace content")

        # CRITICAL REGRESSION CHECK:
        # Verify subsequent record_trace and record_trace_span succeed without IntegrityError
        trace_id = mgr.record_trace(
            task_summary="New trace after auto-migration",
            run_id="run-mig-post-01"
        )
        self.assertGreater(trace_id, 1)

        new_row = mgr.get_trace(trace_id)
        self.assertIsNotNone(new_row)
        self.assertEqual(new_row["task_summary"], "New trace after auto-migration")
        self.assertEqual(new_row["run_id"], "run-mig-post-01")

        span_id = mgr.record_trace_span(
            run_id="run-mig-post-01",
            stage="PEER",
            agent="peer",
            task_summary="Verify span insertion",
            duration_seconds=15,
            outcome="completed"
        )
        self.assertGreater(span_id, trace_id)

    def test_04_auto_migration_missing_run_id(self):
        """Verify that a 16-column table missing only run_id is migrated by adding run_id."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE trace (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                task_summary    TEXT NOT NULL,
                intake_id       INTEGER,
                story_id        TEXT,
                agent           TEXT,
                actions_taken   TEXT,
                files_read      TEXT,
                files_changed   TEXT,
                decisions_made  TEXT,
                errors          TEXT,
                outcome         TEXT,
                duration_seconds INTEGER,
                token_estimate   INTEGER,
                harness_friction TEXT,
                notes            TEXT
            );
        """)
        conn.commit()
        conn.close()

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        with mgr._get_sqlite_db() as conn:
            cur = conn.cursor()
            cols = {r[1] for r in cur.execute("PRAGMA table_info(trace);").fetchall()}

        self.assertIn("run_id", cols)

    def test_05_record_trace_and_get_trace(self):
        """Verify record_trace stores data with proper JSON serialization and get_trace retrieves it."""
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        trace_id = mgr.record_trace(
            task_summary="Execute authentication micro-frontend build",
            agent="peer",
            actions_taken=["run_cmd: rsbuild build", "lint"],
            files_read=["projects/demo-crm-fe/src/app.ts"],
            files_changed=["projects/demo-crm-fe/src/auth.ts"],
            decisions_made=["used TDS Token #441"],
            errors=["none"],
            outcome="completed",
            duration_seconds=42,
            token_estimate=12500,
            harness_friction="low",
            notes="Fast-path executed",
            run_id="run-trace-001"
        )
        self.assertGreater(trace_id, 0)

        record = mgr.get_trace(trace_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["task_summary"], "Execute authentication micro-frontend build")
        self.assertEqual(record["agent"], "peer")
        self.assertEqual(record["outcome"], "completed")
        self.assertEqual(record["duration_seconds"], 42)
        self.assertEqual(record["token_estimate"], 12500)
        self.assertEqual(record["run_id"], "run-trace-001")

        # Verify JSON array serialization
        actions = json.loads(record["actions_taken"])
        self.assertEqual(actions, ["run_cmd: rsbuild build", "lint"])

    def test_06_record_trace_span_with_shared_run_id(self):
        """Verify record_trace_span records pipeline stages sharing run_id."""
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        shared_run = "run-pipeline-shared-999"

        span1 = mgr.record_trace_span(
            run_id=shared_run,
            stage="SUPERVISOR",
            agent="supervisor",
            task_summary="Scope and feasibility check",
            duration_seconds=5,
            outcome="completed"
        )
        span2 = mgr.record_trace_span(
            run_id=shared_run,
            stage="LEAD",
            agent="lead",
            task_summary="Architecture decomposition",
            duration_seconds=12,
            outcome="completed"
        )
        span3 = mgr.record_trace_span(
            run_id=shared_run,
            stage="PEER",
            agent="peer",
            task_summary="Code implementation",
            duration_seconds=45,
            outcome="completed"
        )
        span4 = mgr.record_trace_span(
            run_id=shared_run,
            stage="QC",
            agent="qc",
            task_summary="ISTQB 5-Stage verification",
            duration_seconds=18,
            outcome="completed"
        )

        traces = mgr.list_traces(run_id=shared_run)
        self.assertEqual(len(traces), 4)
        for t in traces:
            self.assertEqual(t["run_id"], shared_run)
            self.assertIn("stage=", t["notes"])

    def test_07_record_and_get_intervention(self):
        """Verify record_intervention and get_interventions."""
        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        int_id = mgr.record_intervention(
            target_type="work_item",
            target_id=888,
            actor="test_user",
            action="approve",
            reason="Verified code diff and QC report"
        )
        self.assertGreater(int_id, 0)

        records = mgr.get_interventions(target_type="work_item", target_id=888)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["actor"], "test_user")
        self.assertEqual(records[0]["action"], "approve")
        self.assertEqual(records[0]["reason"], "Verified code diff and QC report")

    def test_08_record_trace_span_on_migrated_populated_db(self):
        """Verify record_trace_span executes cleanly on a migrated legacy populated table."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE trace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER,
                tier INTEGER NOT NULL DEFAULT 1,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.execute("INSERT INTO trace (story_id, tier, content) VALUES (202, 1, 'legacy span content');")
        conn.commit()
        conn.close()

        mgr = HarnessManager(engine="sqlite", db_path=self.db_path)
        span_id = mgr.record_trace_span(
            run_id="run-span-migrated-99",
            stage="QC",
            agent="qc",
            task_summary="ISTQB verification on migrated database",
            duration_seconds=15,
            outcome="completed"
        )
        self.assertGreater(span_id, 1)
        traces = mgr.list_traces(run_id="run-span-migrated-99")
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["agent"], "qc")
        self.assertEqual(traces[0]["task_summary"], "ISTQB verification on migrated database")


if __name__ == "__main__":
    unittest.main()
