#!/usr/bin/env python3
from __future__ import annotations

import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import tools.floci_client as fc


class TestFlociClient(unittest.TestCase):
    def test_decimal_encoder(self):
        data = {
            "int_val": Decimal("10"),
            "float_val": Decimal("10.5"),
            "str_val": "hello",
            "nested_list": [Decimal("1"), Decimal("2.5")],
            "nested_dict": {"val": Decimal("42")},
        }
        decoded = fc.DecimalEncoder.decode(data)
        self.assertEqual(decoded["int_val"], 10)
        self.assertEqual(decoded["float_val"], 10.5)
        self.assertEqual(decoded["str_val"], "hello")
        self.assertEqual(decoded["nested_list"], [1, 2.5])
        self.assertEqual(decoded["nested_dict"]["val"], 42)

    def test_tokenize_for_search(self):
        tokens = fc.tokenize_for_search("Hello-world! Testing_token/search.py")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)
        self.assertIn("testing", tokens)
        self.assertIn("search", tokens)

        # Empty string
        self.assertEqual(fc.tokenize_for_search(""), [])

    def test_normalize_item_profiles(self):
        # Peer prefix
        item1 = fc._normalize_item({"assigned_to_profile": "Peer Dev 1", "type": "Task"})
        self.assertEqual(item1["assigned_to_profile"], "peer")
        self.assertEqual(item1["assigned_to"], "Peer Dev 1")

        # Lead prefix
        item2 = fc._normalize_item({"assigned_to_profile": "Lead Architect", "type": "Task"})
        self.assertEqual(item2["assigned_to_profile"], "lead")

        # Sup prefix
        item3 = fc._normalize_item({"assigned_to_profile": "Supervisor Intent Guard"})
        self.assertEqual(item3["assigned_to_profile"], "supervisor")

        # QC prefix
        item4 = fc._normalize_item({"assigned_to_profile": "QA Tester"})
        self.assertEqual(item4["assigned_to_profile"], "qc")

        # Inferred from type
        item5 = fc._normalize_item({"type": "Epic"})
        self.assertEqual(item5["assigned_to_profile"], "supervisor")

        item6 = fc._normalize_item({"type": "Feature"})
        self.assertEqual(item6["assigned_to_profile"], "lead")

        item7 = fc._normalize_item({"type": "TestCase"})
        self.assertEqual(item7["assigned_to_profile"], "qc")

        item8 = fc._normalize_item({"type": "Random"})
        self.assertEqual(item8["assigned_to_profile"], "peer")

    def test_load_and_save_local_store(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            with patch.object(fc, "LOCAL_DB_PATH", tmp_path):
                store = fc._load_local_store()
                self.assertIn("work_items", store)
                store["work_items"]["item_1"] = {"id": "item_1", "title": "Test"}
                fc._save_local_store(store)

                reloaded = fc._load_local_store()
                self.assertIn("item_1", reloaded["work_items"])
                self.assertEqual(reloaded["work_items"]["item_1"]["title"], "Test")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @patch("tools.floci_client._check_endpoint_reachable", return_value=False)
    def test_floci_db_local_fallback(self, mock_reach):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            with patch.object(fc, "LOCAL_DB_PATH", tmp_path):
                db = fc.FlociHarnessDB()
                self.assertFalse(db.is_floci_reachable())

                # Test put_work_item and get_work_item via local fallback
                item = {"id": "1001", "title": "Test Work Item", "type": "Task", "state": "Active"}
                self.assertTrue(db.put_work_item(item))

                fetched = db.get_work_item("1001")
                self.assertIsNotNone(fetched)
                self.assertEqual(fetched.get("title"), "Test Work Item")

                # Test list_work_items
                items = db.list_work_items()
                self.assertEqual(len(items), 1)

                # Test delete_work_item
                self.assertTrue(db.delete_work_item("1001"))
                self.assertIsNone(db.get_work_item("1001"))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
