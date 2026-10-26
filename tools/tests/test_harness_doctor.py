#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import tools.harness_doctor as hd


class TestHarnessDoctor(unittest.TestCase):
    def test_record_heal(self):
        entry = hd._record_heal("test_subsystem", "test_action", True, "ok")
        self.assertEqual(entry["subsystem"], "test_subsystem")
        self.assertEqual(entry["action"], "test_action")
        self.assertTrue(entry["success"])
        self.assertEqual(entry["detail"], "ok")

    @patch("socket.create_connection")
    def test_tcp_ping_success(self, mock_conn):
        mock_conn.return_value.__enter__.return_value = MagicMock()
        self.assertTrue(hd._tcp_ping("127.0.0.1", 8080))

    @patch("socket.create_connection", side_effect=Exception("Failed"))
    def test_tcp_ping_failure(self, mock_conn):
        self.assertFalse(hd._tcp_ping("127.0.0.1", 8080))

    @patch("tools.harness_doctor._http_get_json")
    def test_check_dashboard_api_online(self, mock_get):
        mock_get.return_value = {"ok": True}
        res = hd.check_dashboard_api(auto_heal=False)
        self.assertEqual(res["status"], "ok")
        self.assertIn("Online", res["summary"])

    @patch("tools.harness_doctor._http_get_json", return_value=None)
    def test_check_dashboard_api_offline(self, mock_get):
        res = hd.check_dashboard_api(auto_heal=False)
        self.assertEqual(res["status"], "error")
        self.assertIn("Offline", res["summary"])

    def test_check_work_items_hygiene_normalization(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)
            store = {
                "work_items": {
                    "1": {"id": "1", "assigned_to_profile": "Peer Dev 1", "source": "bot"},
                    "2": {"id": "2", "assigned_to_profile": "Lead Architect", "source": "tfs"},
                }
            }
            tmp_path.write_text(json.dumps(store), encoding="utf-8")

        try:
            with patch.object(hd, "BASE_DIR", tmp_path.parent):
                with patch.object(hd, "BASE_DIR", tmp_path.parent):
                    # temporarily rename tmp_path to match BASE_DIR / .harness_local_db.json
                    db_target = tmp_path.parent / ".harness_local_db.json"
                    db_target.write_text(json.dumps(store), encoding="utf-8")
                    try:
                        res = hd.check_work_items_hygiene(auto_heal=True)
                        self.assertEqual(res["status"], "ok")
                        updated = json.loads(db_target.read_text(encoding="utf-8"))
                        self.assertEqual(updated["work_items"]["1"]["assigned_to_profile"], "peer")
                        self.assertEqual(updated["work_items"]["1"]["source"], "local")
                        self.assertEqual(updated["work_items"]["2"]["assigned_to_profile"], "lead")
                        self.assertEqual(updated["work_items"]["2"]["source"], "tfs")
                    finally:
                        if db_target.exists():
                            db_target.unlink()
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    @patch("shutil.which", return_value=None)
    @patch("os.path.isfile", return_value=False)
    @patch("os.access", return_value=False)
    def test_check_rtk_binary_missing(self, mock_access, mock_isfile, mock_which):
        res = hd.check_rtk_binary(auto_heal=False)
        self.assertEqual(res["id"], "rtk_binary")
        self.assertEqual(res["status"], "warn")
        self.assertIn("không tìm thấy trên PATH", res["summary"])
        self.assertIsNotNone(res.get("remediation"))
        self.assertIn("install.sh", res["remediation"])

    @patch("shutil.which", return_value="/usr/local/bin/rtk")
    @patch("os.path.isfile", return_value=True)
    @patch("os.access", return_value=True)
    @patch("subprocess.run")
    def test_check_rtk_binary_present(self, mock_run, mock_access, mock_isfile, mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="rtk 1.0.1\n")
        res = hd.check_rtk_binary(auto_heal=False)
        self.assertEqual(res["id"], "rtk_binary")
        self.assertEqual(res["status"], "ok")
        self.assertIn("rtk 1.0.1", res["summary"])
        self.assertIsNone(res.get("remediation"))

    @patch("tools.harness_doctor.check_rtk_binary", return_value={"id": "rtk_binary", "name": "RTK", "status": "warn", "summary": "RTK missing", "remediation": "curl ...", "healed": None})
    def test_run_doctor_includes_rtk_check(self, mock_rtk):
        rep = hd.run_doctor(auto_heal=False)
        check_ids = [c["id"] for c in rep["checks"]]
        self.assertIn("rtk_binary", check_ids)
        self.assertEqual(rep["total_checks"], 9)

    @patch("tools.harness_doctor._tcp_ping", return_value=False)
    def test_check_paseo_daemon_canonical_4_roles(self, mock_ping):
        """Verify check_paseo_daemon validates canonical 4 roles and repo profiles."""
        res = hd.check_paseo_daemon(auto_heal=False)
        self.assertEqual(res["id"], "paseo_daemon")
        # In standby, valid profiles yields status "warn" (not "error")
        self.assertIn(res["status"], ("ok", "warn"))
        self.assertIn("SLPC Profiles: 4/4", res["summary"])


if __name__ == "__main__":
    unittest.main()

