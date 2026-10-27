#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.harness_learning_search as hls


class TestHarnessLearningSearch(unittest.TestCase):
    def test_calculate_lesson_quality_score_high_quality(self):
        cue = "Valid cue name for test"
        lesson = "You must always ensure that single ownership is strictly maintained."
        evidence = "Test logs passed 100% in local runner"
        score, issues = hls.calculate_lesson_quality_score(cue, lesson, evidence)
        self.assertGreaterEqual(score, 0.8)
        self.assertEqual(issues, [])

    def test_calculate_lesson_quality_score_short_and_garbage(self):
        cue = "abc"
        lesson = "none"
        evidence = "1"
        score, issues = hls.calculate_lesson_quality_score(cue, lesson, evidence)
        self.assertLess(score, 0.5)
        self.assertTrue(any("ngắn" in issue.lower() for issue in issues))

    def test_search_experiences_sqlite_fallback(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".db") as tmp:
            tmp_path = Path(tmp.name)

        try:
            conn = sqlite3.connect(str(tmp_path))
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE harness_experience (
                    id INTEGER PRIMARY KEY,
                    domain TEXT,
                    confidence TEXT,
                    cue TEXT,
                    lesson TEXT,
                    evidence TEXT
                )
            """)
            cur.execute("""
                INSERT INTO harness_experience (id, domain, confidence, cue, lesson, evidence)
                VALUES (1, 'angular', 'high', 'State cue test', 'Must avoid mutating state directly in components.', 'Spec test pass')
            """)
            conn.commit()
            conn.close()

            with patch.dict(os.environ, {"HARNESS_DB": str(tmp_path)}):
                with patch.object(hls, "DB_CANDIDATES", [tmp_path]):
                    with patch("tools.floci_client.FlociHarnessDB._is_online", return_value=False):
                        results = hls.search_experiences(query_text="mutating", domain="angular")
                    self.assertEqual(len(results), 1)
                    self.assertEqual(results[0]["cue"], "State cue test")
                    self.assertGreater(results[0]["quality_score"], 0.5)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
