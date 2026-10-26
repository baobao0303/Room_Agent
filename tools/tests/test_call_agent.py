#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.call_agent as ca


class TestCallAgent(unittest.TestCase):
    def test_resolve_room(self):
        self.assertEqual(ca.resolve_room("Supervisor (Scope Guard)"), "supervisor")
        self.assertEqual(ca.resolve_room("Lead Dev"), "lead")
        self.assertEqual(ca.resolve_room("QC Verifier"), "qc")
        self.assertEqual(ca.resolve_room("Peer Dev 1"), "peer")
        self.assertEqual(ca.resolve_room("Peer Design"), "peer")

    def test_resolve_thinking_directive_forward(self):
        cleaned, mode, directive = ca.resolve_thinking_directive("[THUẬN] Làm task login")
        self.assertEqual(cleaned, "Làm task login")
        self.assertIn("THUẬN", mode)
        self.assertIn("luồng thuận", directive)

    def test_resolve_thinking_directive_reverse(self):
        cleaned, mode, directive = ca.resolve_thinking_directive("[NGHỊCH] Kiểm tra lỗi")
        self.assertEqual(cleaned, "Kiểm tra lỗi")
        self.assertIn("NGHỊCH", mode)
        self.assertIn("luồng nghịch", directive)

    def test_resolve_thinking_directive_dual(self):
        cleaned, mode, directive = ca.resolve_thinking_directive("[LƯỠNG-DIỆN] Tối ưu auth")
        self.assertEqual(cleaned, "Tối ưu auth")
        self.assertIn("LƯỠNG DIỆN", mode)
        self.assertIn("BẮT BUỘC", directive)

    def test_resolve_thinking_directive_default(self):
        cleaned, mode, directive = ca.resolve_thinking_directive("Nhiệm vụ chung")
        self.assertEqual(cleaned, "Nhiệm vụ chung")
        self.assertIn("LƯỠNG DIỆN", mode)

    def test_get_profiles_not_found(self):
        with patch.object(ca, "CONFIG_PATH", Path("/non/existent/config.json")):
            self.assertEqual(ca.get_profiles(), {})

    def test_get_profiles_loaded(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp_path = Path(tmp.name)
            data = {
                "daemon": {
                    "agentProfiles": [
                        {"name": "Supervisor", "model": "gemini-3.8-flash-high"},
                        {"name": "Lead", "model": "gemini-3.8-flash-high"},
                    ]
                }
            }
            tmp_path.write_text(json.dumps(data), encoding="utf-8")

        try:
            with patch.object(ca, "CONFIG_PATH", tmp_path):
                profiles = ca.get_profiles()
                self.assertIn("supervisor", profiles)
                self.assertIn("lead", profiles)
                self.assertEqual(profiles["supervisor"]["model"], "gemini-3.8-flash-high")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
