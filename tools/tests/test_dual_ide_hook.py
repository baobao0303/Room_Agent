#!/usr/bin/env python3
"""
tools/tests/test_dual_ide_hook.py - Unit test suite for Dual-IDE Hook Router.
"""

import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
from tools import dual_ide_hook


class TestDualIdeHook(unittest.TestCase):
    def test_01_parse_thao_luan_prefix(self):
        prompt = "[THẢO LUẬN] Nên dùng SQLite hay DynamoDB cho local?"
        cleaned, intent = dual_ide_hook.parse_prompt_intent(prompt)
        self.assertEqual(cleaned, "Nên dùng SQLite hay DynamoDB cho local?")
        self.assertEqual(intent["category"], "DISCUSS")
        self.assertIn("THẢO LUẬN", intent["mode"])
        self.assertIn("KHÔNG VIẾT CODE", intent["directive"])

    def test_02_parse_thuan_prefix(self):
        prompt = "[TÍNH-NĂNG] Thêm modal xác nhận đơn hàng"
        cleaned, intent = dual_ide_hook.parse_prompt_intent(prompt)
        self.assertEqual(cleaned, "Thêm modal xác nhận đơn hàng")
        self.assertEqual(intent["category"], "FORWARD")
        self.assertIn("THUẬN", intent["mode"])

    def test_03_parse_nghich_prefix(self):
        prompt = "[BẪY-LỖI] Test trường hợp token hết hạn"
        cleaned, intent = dual_ide_hook.parse_prompt_intent(prompt)
        self.assertEqual(cleaned, "Test trường hợp token hết hạn")
        self.assertEqual(intent["category"], "REVERSE")
        self.assertIn("NGHỊCH", intent["mode"])

    def test_04_default_dual_prefix(self):
        prompt = "Refactor logic thanh toán giỏ hàng"
        cleaned, intent = dual_ide_hook.parse_prompt_intent(prompt)
        self.assertEqual(cleaned, prompt)
        self.assertEqual(intent["category"], "DUAL")
        self.assertIn("LƯỠNG DIỆN", intent["mode"])

    def test_05_detect_environments_structure(self):
        env = dual_ide_hook.detect_environments()
        self.assertIn("orca", env)
        self.assertIn("paseo", env)
        self.assertIn("active_primary", env)
        self.assertIsInstance(env["orca"]["available"], bool)
        self.assertIsInstance(env["paseo"]["configured"], bool)

    def test_06_build_hook_output(self):
        cleaned, intent = dual_ide_hook.parse_prompt_intent("[THẢO LUẬN] Đánh giá kiến trúc")
        env = dual_ide_hook.detect_environments()
        out = dual_ide_hook.build_hook_output(cleaned, intent, env)
        self.assertIn("DUAL-IDE UNIVERSAL HOOK", out)
        self.assertIn(intent["mode"], out)
        self.assertIn("KHÔNG tạo Task thi công", out)


if __name__ == "__main__":
    unittest.main()
