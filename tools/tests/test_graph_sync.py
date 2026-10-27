#!/usr/bin/env python3
"""
Unit tests for tools/graph_sync.py
Covering push, pull, CLI args, fallback logic, and error handling.
"""

import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tools.graph_sync as gs


class DummyClientError(Exception):
    def __init__(self, message: str, code: str = "NoSuchKey"):
        super().__init__(message)
        self.response = {"Error": {"Code": code}}


class TestGraphSync(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_graph_sync_")
        self.project_dir = Path(self.temp_dir) / "demo_proj"
        self.project_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_graph_file(self, subdir=".ua", content=None):
        if content is None:
            content = {"nodes": [{"id": "node1", "label": "AppModule"}], "edges": []}
        target_dir = self.project_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        graph_file = target_dir / "knowledge-graph.json"
        graph_file.write_text(json.dumps(content), encoding="utf-8")
        return graph_file

    def test_find_graph_file_ua(self):
        expected = self._create_graph_file(".ua")
        found = gs.find_graph_file(self.project_dir)
        self.assertEqual(found.resolve(), expected.resolve())

    def test_find_graph_file_understand_anything(self):
        expected = self._create_graph_file(".understand-anything")
        found = gs.find_graph_file(self.project_dir)
        self.assertEqual(found.resolve(), expected.resolve())

    def test_find_graph_file_direct_path(self):
        expected = self._create_graph_file(".ua")
        found = gs.find_graph_file(expected)
        self.assertEqual(found.resolve(), expected.resolve())

    def test_find_graph_file_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            gs.find_graph_file(self.project_dir)

    def test_push_graph_dry_run(self):
        self._create_graph_file(".ua")
        res = gs.push_graph(self.project_dir, commit_sha="abc1234", dry_run=True)
        self.assertEqual(res["status"], "dry_run")
        self.assertEqual(res["project"], "demo_proj")
        self.assertIn("graphs/demo_proj/latest.json", res["keys"])
        self.assertIn("graphs/demo_proj/commits/abc1234.json", res["keys"])
        self.assertGreater(res["bytes"], 0)

    def test_push_graph_success_with_commit(self):
        self._create_graph_file(".ua")
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = True
        mock_db.s3_bucket = "harness-data"
        mock_s3 = MagicMock()
        mock_db.s3_client = mock_s3

        res = gs.push_graph(self.project_dir, commit_sha="def5678", db=mock_db)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["project"], "demo_proj")
        self.assertEqual(mock_s3.put_object.call_count, 2)
        uploaded_keys = res["uploaded_keys"]
        self.assertEqual(
            uploaded_keys,
            ["graphs/demo_proj/latest.json", "graphs/demo_proj/commits/def5678.json"],
        )

    def test_push_graph_floci_offline_raises(self):
        self._create_graph_file(".ua")
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = False
        mock_db.s3_client = MagicMock()

        with self.assertRaises(ConnectionError):
            gs.push_graph(self.project_dir, db=mock_db)

    def test_push_graph_invalid_json_raises(self):
        target = self.project_dir / ".ua"
        target.mkdir(parents=True, exist_ok=True)
        (target / "knowledge-graph.json").write_text("{not-valid-json", encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            gs.push_graph(self.project_dir)

    def test_pull_graph_dry_run(self):
        res = gs.pull_graph(self.project_dir, commit_sha="abc999", dry_run=True)
        self.assertEqual(res["status"], "dry_run")
        self.assertEqual(res["project"], "demo_proj")
        self.assertEqual(res["target_key"], "graphs/demo_proj/commits/abc999.json")
        expected_dest = self.project_dir / ".ua" / "knowledge-graph.json"
        self.assertEqual(res["destination"], str(expected_dest))
        self.assertFalse(expected_dest.exists())

    def test_pull_graph_success_latest(self):
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = True
        mock_db.s3_bucket = "harness-data"
        mock_s3 = MagicMock()
        mock_db.s3_client = mock_s3

        sample_graph = {"nodes": [{"id": "crm_main"}], "edges": []}
        mock_body = MagicMock()
        mock_body.read.return_value = json.dumps(sample_graph).encode("utf-8")
        mock_s3.get_object.return_value = {"Body": mock_body}

        res = gs.pull_graph(self.project_dir, db=mock_db)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["pulled_key"], "graphs/demo_proj/latest.json")

        dest = Path(res["destination"])
        self.assertTrue(dest.exists())
        loaded = json.loads(dest.read_text(encoding="utf-8"))
        self.assertEqual(loaded, sample_graph)

    def test_pull_graph_commit_fallback_latest(self):
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = True
        mock_db.s3_bucket = "harness-data"
        mock_s3 = MagicMock()
        mock_db.s3_client = mock_s3

        sample_graph = {"nodes": [{"id": "fallback_node"}], "edges": []}

        def mock_get_object(Bucket, Key):
            if "commits" in Key:
                raise DummyClientError("NoSuchKey: The specified key does not exist.", "NoSuchKey")
            mock_body = MagicMock()
            mock_body.read.return_value = json.dumps(sample_graph).encode("utf-8")
            return {"Body": mock_body}

        mock_s3.get_object.side_effect = mock_get_object

        res = gs.pull_graph(
            self.project_dir, commit_sha="missing_sha", fallback_latest=True, db=mock_db
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["pulled_key"], "graphs/demo_proj/latest.json")
        dest = Path(res["destination"])
        self.assertTrue(dest.exists())
        self.assertEqual(json.loads(dest.read_text(encoding="utf-8")), sample_graph)

    def test_pull_graph_commit_no_fallback_raises(self):
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = True
        mock_db.s3_bucket = "harness-data"
        mock_s3 = MagicMock()
        mock_db.s3_client = mock_s3

        mock_s3.get_object.side_effect = DummyClientError("NoSuchKey", "NoSuchKey")

        with self.assertRaises(FileNotFoundError):
            gs.pull_graph(
                self.project_dir,
                commit_sha="missing_sha",
                fallback_latest=False,
                db=mock_db,
            )

    def test_pull_graph_offline_preserves_local_file(self):
        # Create existing local file
        existing_file = self._create_graph_file(".ua", content={"preserved": "ok"})
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = False
        mock_db.s3_client = MagicMock()

        with self.assertRaises(ConnectionError):
            gs.pull_graph(self.project_dir, db=mock_db)

        # Confirm existing file is completely intact
        self.assertEqual(
            json.loads(existing_file.read_text(encoding="utf-8")),
            {"preserved": "ok"},
        )

    def test_pull_graph_corrupt_payload_preserves_local_file(self):
        existing_file = self._create_graph_file(".ua", content={"intact": True})
        mock_db = MagicMock()
        mock_db.is_floci_reachable.return_value = True
        mock_db.s3_bucket = "harness-data"
        mock_s3 = MagicMock()
        mock_db.s3_client = mock_s3

        mock_body = MagicMock()
        mock_body.read.return_value = b"corrupted payload <not json>"
        mock_s3.get_object.return_value = {"Body": mock_body}

        with self.assertRaises(ValueError):
            gs.pull_graph(self.project_dir, db=mock_db)

        self.assertEqual(
            json.loads(existing_file.read_text(encoding="utf-8")),
            {"intact": True},
        )

    def test_cli_push_json_dry_run(self):
        self._create_graph_file(".ua")
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = gs.main(["push", str(self.project_dir), "--dry-run", "--json"])
        self.assertEqual(code, 0)
        output = json.loads(buf.getvalue())
        self.assertEqual(output["status"], "dry_run")
        self.assertEqual(output["project"], "demo_proj")

    def test_cli_pull_json_dry_run(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = gs.main(
                ["pull", str(self.project_dir), "--commit", "testsha", "--dry-run", "--json"]
            )
        self.assertEqual(code, 0)
        output = json.loads(buf.getvalue())
        self.assertEqual(output["status"], "dry_run")
        self.assertEqual(output["commit_sha"], "testsha")

    def test_cli_error_exit_code(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            # No graph file in empty dir -> error
            code = gs.main(["push", str(self.project_dir), "--json"])
        self.assertEqual(code, 1)
        output = json.loads(buf.getvalue())
        self.assertEqual(output["status"], "error")

    def test_scripts_executable_permission(self):
        for script_name in ["scripts/push_graph", "scripts/pull_graph"]:
            path = REPO_ROOT / script_name
            self.assertTrue(path.is_file(), f"{script_name} must exist")
            file_stat = path.stat()
            self.assertTrue(
                bool(file_stat.st_mode & stat.S_IXUSR),
                f"{script_name} must be executable (+x)",
            )

    def test_bash_script_wrappers(self):
        self._create_graph_file(".ua")
        res_push = subprocess.run(
            [str(REPO_ROOT / "scripts/push_graph"), str(self.project_dir), "--dry-run", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_push.returncode, 0)
        data = json.loads(res_push.stdout)
        self.assertEqual(data["status"], "dry_run")

        res_pull = subprocess.run(
            [str(REPO_ROOT / "scripts/pull_graph"), str(self.project_dir), "--dry-run", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_pull.returncode, 0)
        data = json.loads(res_pull.stdout)
        self.assertEqual(data["status"], "dry_run")


if __name__ == "__main__":
    unittest.main()
