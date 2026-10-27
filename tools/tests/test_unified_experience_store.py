#!/usr/bin/env python3
"""
tools/tests/test_unified_experience_store.py - Tests for G-MEM-2 Unified Experience Store.
Verifies bidirectional consistency between SQLite harness_experience and local_db.json.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.floci_client import FlociHarnessDB, _ensure_sqlite_experience_table
from tools.harness_learning_search import search_experiences
from tools.harness_manager import HarnessManager


class TestUnifiedExperienceStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        (self.test_root / ".harness").mkdir(parents=True, exist_ok=True)
        self.test_db = self.test_root / ".harness" / "harness.db"
        self.test_json = self.test_root / ".harness" / "local_db.json"

        # Initialize empty local_db.json
        with open(self.test_json, "w", encoding="utf-8") as f:
            json.dump({"experiences": []}, f)

        # Initialize SQLite database with table
        conn = sqlite3.connect(str(self.test_db))
        _ensure_sqlite_experience_table(conn)
        conn.close()

        self.orig_harness_db = os.environ.get("HARNESS_DB")
        os.environ["HARNESS_DB"] = str(self.test_db)

        self.patch_local_db = patch("tools.floci_client.LOCAL_DB_PATH", str(self.test_json))
        self.patch_local_db.start()

        self.patch_base_dir = patch("tools.harness_learning_search.BASE_DIR", self.test_root)
        self.patch_base_dir.start()

        self.patch_online = patch.object(FlociHarnessDB, "_is_online", return_value=False)
        self.patch_online.start()

    def tearDown(self):
        self.patch_online.stop()
        self.patch_base_dir.stop()
        self.patch_local_db.stop()

        if self.orig_harness_db is not None:
            os.environ["HARNESS_DB"] = self.orig_harness_db
        else:
            os.environ.pop("HARNESS_DB", None)

        self.temp_dir.cleanup()

    def test_record_via_floci_searchable_via_sqlite(self):
        db = FlociHarnessDB()
        item = db.record_experience(
            domain="engineering",
            cue="strict_typing_rule",
            lesson="Zero any, zero unknown, and zero sloppy fallbacks in code.",
            evidence="Unit tests passed 100% without any warnings.",
            confidence="high"
        )
        self.assertEqual(item["cue"], "strict_typing_rule")

        # Verify it was written directly into SQLite
        conn = sqlite3.connect(str(self.test_db))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM harness_experience WHERE domain = ? AND cue = ?", ("engineering", "strict_typing_rule"))
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["cue"], "strict_typing_rule")
        self.assertIn("Zero any", row["lesson"])

        # Verify it is searchable via harness_learning_search
        results = search_experiences(query_text="strict_typing", domain="engineering")
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["cue"], "strict_typing_rule")
        self.assertEqual(results[0]["domain"], "engineering")

    def test_record_via_sqlite_retrievable_via_floci(self):
        # Insert directly into SQLite table
        conn = sqlite3.connect(str(self.test_db))
        conn.execute(
            "INSERT INTO harness_experience (domain, cue, lesson, evidence, confidence) VALUES (?, ?, ?, ?, ?)",
            ("security", "token_leak_prevention", "Never commit raw credentials to repository.", "Git hook detected 0 leaks.", "high")
        )
        conn.commit()
        conn.close()

        # Query via FlociHarnessDB
        db = FlociHarnessDB()
        results = db.query_experiences(domain="security")
        self.assertTrue(len(results) >= 1)
        cues = [r["cue"] for r in results]
        self.assertIn("token_leak_prevention", cues)

        # Verify query_experiences synced it to local_db.json
        with open(self.test_json, "r", encoding="utf-8") as f:
            store = json.load(f)
        json_cues = [e.get("cue") for e in store.get("experiences", [])]
        self.assertIn("token_leak_prevention", json_cues)

    def test_offline_fallback_returns_identical_record_sets(self):
        db = FlociHarnessDB()
        # Record multiple experiences
        db.record_experience("peer_implementation", "rtk_token_compression", "Always use rtk for shell proxying.", "Token usage dropped by 70%.")
        db.record_experience("qc_verification", "istqb_5_stage_testing", "Must execute 5 stages before closing.", "Test generator coverage 100%.")

        floci_res = db.query_experiences(limit=10)
        search_res = search_experiences(limit=10)

        floci_cues = sorted([r["cue"] for r in floci_res])
        search_cues = sorted([r["cue"] for r in search_res])
        self.assertEqual(floci_cues, search_cues)

    def test_schema_alias_compatibility(self):
        db = FlociHarnessDB()
        payload = {
            "category": "architecture",
            "trigger_pattern": "single_ownership_invariant",
            "content": "Only touch target files specified in task.",
            "tags": ["diff", "safety"],
            "severity": "critical"
        }
        item = db.put_experience(payload)
        self.assertEqual(item["domain"], "architecture")
        self.assertEqual(item["category"], "architecture")
        self.assertEqual(item["cue"], "single_ownership_invariant")
        self.assertEqual(item["trigger_pattern"], "single_ownership_invariant")
        self.assertEqual(item["confidence"], "high")
        self.assertEqual(item["severity"], "high")
        self.assertIn("diff, safety", item["evidence"])

        # Query should also return aliases
        queried = db.query_experiences(domain="architecture")
        self.assertTrue(len(queried) >= 1)
        self.assertEqual(queried[0]["category"], "architecture")
        self.assertEqual(queried[0]["trigger_pattern"], "single_ownership_invariant")
        self.assertEqual(queried[0]["severity"], "high")

    def test_harness_manager_facade(self):
        mgr = HarnessManager(db_path=str(self.test_db))
        rec = mgr.record_experience(
            domain="supervisor_intake",
            cue="user_intent_clarification",
            lesson="Always clarify ambiguous requirements before decomposing tasks.",
            evidence="Passed all stakeholder interviews.",
            confidence=0.95
        )
        self.assertEqual(rec["domain"], "supervisor_intake")
        self.assertEqual(rec["cue"], "user_intent_clarification")

        queried = mgr.query_experiences(domain="supervisor_intake")
        self.assertTrue(len(queried) >= 1)
        self.assertEqual(queried[0]["cue"], "user_intent_clarification")


if __name__ == "__main__":
    unittest.main()
