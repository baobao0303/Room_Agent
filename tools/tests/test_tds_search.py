import sys
import unittest
from pathlib import Path

_cur = Path(__file__).resolve()
BASE_DIR = _cur.parent.parent if _cur.parent.name == "tools" else _cur.parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tools.tds_search import search_tds, check_gateway_health, TDS_CATALOG

class TestTdsSearch(unittest.TestCase):
    def test_catalog_loaded(self):
        self.assertGreaterEqual(len(TDS_CATALOG), 50)

    def test_search_table(self):
        results = search_tds("table", limit=5)
        self.assertTrue(any(r["slug"] == "table" for r in results))
        self.assertEqual(results[0]["module"], "TdsTableModule")

    def test_search_button_with_category(self):
        results = search_tds("button", category_filter="Button", limit=10)
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r["category"] == "Button" for r in results))

    def test_search_modal(self):
        results = search_tds("modal", limit=3)
        self.assertTrue(any(r["slug"] == "modal" for r in results))
        self.assertEqual(results[0]["selector"], "tds-modal, TdsModalService")

    def test_gateway_health(self):
        # Should be accessible
        is_healthy = check_gateway_health()
        self.assertTrue(is_healthy)

if __name__ == "__main__":
    unittest.main()
