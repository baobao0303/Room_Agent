#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import os
import unittest
from unittest.mock import MagicMock, patch

import tools.remote_sync as rs


class TestRemoteSync(unittest.TestCase):
    def test_clean_html(self):
        self.assertEqual(rs.clean_html(""), "")
        self.assertEqual(rs.clean_html(None), "")
        html_input = "<p>First line</p><br/><div>Second line &amp; &lt;tag&gt;</div>"
        cleaned = rs.clean_html(html_input)
        self.assertIn("First line", cleaned)
        self.assertIn("Second line & <tag>", cleaned)

        list_html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        cleaned_list = rs.clean_html(list_html)
        self.assertIn("• Item 1", cleaned_list)
        self.assertIn("• Item 2", cleaned_list)

    def test_validate_remote_config_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                rs.validate_remote_config()
            self.assertIn("Missing required environment variables", str(cm.exception))

    def test_validate_remote_config_success(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg/",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "my_pat",
        }
        with patch.dict(os.environ, test_env, clear=True):
            org, proj, pat = rs.validate_remote_config()
            self.assertEqual(org, "https://dev.azure.com/myorg")
            self.assertEqual(proj, "MyProject")
            self.assertEqual(pat, "my_pat")

    def test_get_auth_headers(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "secret_pat",
        }
        with patch.dict(os.environ, test_env, clear=True):
            headers = rs.get_auth_headers()
            self.assertEqual(headers["Content-Type"], "application/json")
            self.assertTrue(headers["Authorization"].startswith("Basic "))

    @patch("urllib.request.urlopen")
    def test_fetch_all_remote_work_item_ids(self, mock_urlopen):
        resp_data = {"workItems": [{"id": 101}, {"id": 102}, {"id": 103}]}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "secret_pat",
        }
        with patch.dict(os.environ, test_env, clear=True):
            ids = rs.fetch_all_remote_work_item_ids()
            self.assertEqual(ids, [101, 102, 103])

    @patch("urllib.request.urlopen")
    def test_fetch_work_items_batch(self, mock_urlopen):
        self.assertEqual(rs.fetch_work_items_batch([]), [])

        resp_data = {
            "value": [
                {"id": 101, "fields": {"System.Title": "Item 1"}},
                {"id": 102, "fields": {"System.Title": "Item 2"}},
            ]
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "secret_pat",
        }
        with patch.dict(os.environ, test_env, clear=True):
            items = rs.fetch_work_items_batch([101, 102])
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]["id"], 101)

    @patch("tools.remote_sync.FlociHarnessDB")
    @patch("tools.remote_sync.fetch_work_items_batch")
    @patch("tools.remote_sync.fetch_all_remote_work_item_ids")
    @patch("tools.remote_sync.validate_remote_config")
    def test_sync_full_backlog(self, mock_val, mock_fetch_ids, mock_fetch_batch, mock_db_cls):
        mock_val.return_value = ("https://dev.azure.com/test", "TestProj", "pat")
        mock_fetch_ids.return_value = [201, 202]
        mock_fetch_batch.return_value = [
            {
                "id": 201,
                "fields": {
                    "System.WorkItemType": "User Story",
                    "System.Title": "<b>User Story 1</b>",
                    "System.State": "Active",
                    "Microsoft.VSTS.Common.Priority": 1,
                    "Microsoft.VSTS.Common.AcceptanceCriteria": "<p>AC text</p>",
                },
            },
            {
                "id": 202,
                "fields": {
                    "System.WorkItemType": "Task",
                    "System.Title": "Dev Task 2",
                    "System.State": "New",
                    "Microsoft.VSTS.Common.Priority": 2,
                },
            },
        ]
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        with patch("sys.stdout", new=io.StringIO()):
            res = rs.sync_full_backlog()

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_synced"], 2)
        self.assertEqual(res["stories_synced"], 1)
        self.assertEqual(mock_db.put_work_item.call_count, 2)
        self.assertEqual(mock_db.put_story.call_count, 1)


if __name__ == "__main__":
    unittest.main()
