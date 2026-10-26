#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import tools.remote_mcp_server as rms


class TestRemoteMcpServer(unittest.TestCase):
    def test_escape_wiql_literal(self):
        self.assertEqual(rms.escape_wiql_literal("It's fine"), "It''s fine")
        self.assertEqual(rms.escape_wiql_literal("Project 'Demo'"), "Project ''Demo''")
        self.assertEqual(rms.escape_wiql_literal(123), "123")

    def test_get_remote_config_missing_vars(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                rms.get_remote_config()
            self.assertIn("Missing required environment variables", str(cm.exception))

    def test_get_remote_config_success(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg/",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "secret_pat_token",
        }
        with patch.dict(os.environ, test_env, clear=True):
            org_url, project, pat = rms.get_remote_config()
            self.assertEqual(org_url, "https://dev.azure.com/myorg")
            self.assertEqual(project, "MyProject")
            self.assertEqual(pat, "secret_pat_token")

    def test_get_auth_header(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "test_token",
        }
        with patch.dict(os.environ, test_env, clear=True):
            headers = rms.get_auth_header()
            self.assertTrue(headers["Authorization"].startswith("Basic "))

    def test_execute_tool_invalid_type(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "test_token",
        }
        with patch.dict(os.environ, test_env, clear=True):
            with self.assertRaises(ValueError) as cm:
                rms.execute_tool("remote_list_work_items", {"work_item_type": "InvalidType123"})
            self.assertIn("Invalid work_item_type", str(cm.exception))

    def test_execute_tool_invalid_state(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "test_token",
        }
        with patch.dict(os.environ, test_env, clear=True):
            with self.assertRaises(ValueError) as cm:
                rms.execute_tool("remote_list_work_items", {"state": "NonExistentState"})
            self.assertIn("Invalid state", str(cm.exception))

    def test_execute_tool_get_work_item_invalid_id(self):
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "test_token",
        }
        with patch.dict(os.environ, test_env, clear=True):
            with self.assertRaises(ValueError) as cm:
                rms.execute_tool("remote_get_work_item", {"work_item_id": "not-an-int"})
            self.assertIn("Must be an integer", str(cm.exception))

    @patch("tools.remote_mcp_server.remote_api_get")
    def test_execute_tool_get_work_item_success(self, mock_get):
        mock_get.return_value = {
            "id": 999,
            "fields": {
                "System.Id": 999,
                "System.Title": "Test Work Item",
                "System.WorkItemType": "Task",
                "System.State": "Active",
            },
        }
        test_env = {
            "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/myorg",
            "AZURE_DEVOPS_PROJECT": "MyProject",
            "AZURE_DEVOPS_PAT": "test_token",
        }
        with patch.dict(os.environ, test_env, clear=True):
            res_str = rms.execute_tool("remote_get_work_item", {"work_item_id": "999"})
            data = json.loads(res_str)
            self.assertEqual(data["id"], 999)
            self.assertEqual(data["title"], "Test Work Item")
            self.assertEqual(data["type"], "Task")


if __name__ == "__main__":
    unittest.main()
