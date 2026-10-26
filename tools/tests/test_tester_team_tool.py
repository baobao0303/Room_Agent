#!/usr/bin/env python3
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.tester_team_tool as ttt


class TestTesterTeamTool(unittest.TestCase):
    def test_audit_report_penalty(self):
        report = ttt.TestCaseAuditReport()
        report.add_violation("test.spec.ts", 10, "Banned selector")
        self.assertEqual(report.kpi_penalty_senior, 3)
        self.assertEqual(report.kpi_penalty_junior, 2)
        self.assertEqual(len(report.violations), 1)

    def test_audit_test_files_detects_banned_locators(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "sample.spec.ts"
            test_file.write_text(
                """
                test('[TC_001][@valid] Test with banned selector', async ({ page }) => {
                    await page.getByText('Submit').click();
                    await page.locator('.btn-primary').click();
                    await page.locator('//button[@id="submit"]').click();
                    await page.locator('div:nth-child(2)').click();
                    await page.locator('[tds-test-id="submit-btn"]').click();
                });
                """,
                encoding="utf-8",
            )
            report = ttt.audit_test_files(test_file)
            self.assertEqual(report.total_testcases, 1)
            # Should have violations for getByText, CSS, xpath, nth-child
            violation_msgs = " ".join(v["message"] for v in report.violations)
            self.assertIn("getByText", violation_msgs)
            self.assertIn("CSS class", violation_msgs)
            self.assertIn("XPath", violation_msgs)
            self.assertIn(":nth-child", violation_msgs)

    def test_audit_test_files_missing_tag(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "sample.spec.ts"
            test_file.write_text(
                """
                test('[TC_002] Test without required tag', async ({ page }) => {
                    await page.locator('[tds-test-id="submit-btn"]').click();
                });
                """,
                encoding="utf-8",
            )
            report = ttt.audit_test_files(test_file)
            self.assertEqual(report.total_testcases, 1)
            violation_msgs = " ".join(v["message"] for v in report.violations)
            self.assertIn("thiếu thẻ Tag phân loại bắt buộc", violation_msgs)

    def test_audit_test_files_valid_create_missing_verification(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "sample.spec.ts"
            test_file.write_text(
                """
                test('[TC_003][@valid] Tạo mới khách hàng', async ({ page }) => {
                    await page.locator('[tds-test-id="submit-btn"]').click();
                });
                """,
                encoding="utf-8",
            )
            report = ttt.audit_test_files(test_file)
            self.assertEqual(report.total_testcases, 1)
            violation_msgs = " ".join(v["message"] for v in report.violations)
            self.assertIn("thiếu bước tìm kiếm/đối soát lại trên danh sách", violation_msgs)

    def test_audit_test_files_clean_pass(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "sample.spec.ts"
            test_file.write_text(
                """
                test('[TC_004][@valid] Tạo mới khách hàng thành công', async ({ page }) => {
                    await page.locator('[tds-test-id="name-input"]').fill('Test');
                    await page.locator('[tds-test-id="submit-btn"]').click();
                    await page.locator('[tds-test-id="search-input"]').fill('Test');
                    const row = page.locator('[tds-test-id="customer-row"]');
                    await expect(row).toBeVisible();
                });
                """,
                encoding="utf-8",
            )
            report = ttt.audit_test_files(test_file)
            self.assertEqual(report.total_testcases, 1)
            self.assertEqual(len(report.violations), 0)
            self.assertEqual(report.valid_testcases, 1)

    def test_generate_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)
            with patch("sys.stdout", new=io.StringIO()):
                ttt.generate_scaffold("customer", "create", out_path)

            data_dir = out_path / "data" / "customer" / "create"
            self.assertTrue((data_dir / "customer.factory.ts").exists())
            self.assertTrue((data_dir / "customer.smoke.data.ts").exists())
            self.assertTrue((data_dir / "customer.validation.data.ts").exists())
            self.assertTrue((data_dir / "customer.query.data.ts").exists())

            page_file = out_path / "pages" / "customer-create.page.ts"
            self.assertTrue(page_file.exists())
            page_content = page_file.read_text(encoding="utf-8")
            self.assertIn("CustomerCreatePage", page_content)
            self.assertIn("customer-create-container", page_content)

            spec_file = out_path / "specs" / "customer-create.e2e.spec.ts"
            self.assertTrue(spec_file.exists())
            spec_content = spec_file.read_text(encoding="utf-8")
            self.assertIn("[CUSTOMER_CREATE_001][@valid]", spec_content)

    def test_print_rules(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ttt.print_rules()
            out = fake_out.getvalue()
            self.assertIn("BẢNG QUY CHUẨN KIỂM THỬ", out)
            self.assertIn("@valid", out)
            self.assertIn("Senior : -3 điểm", out)


if __name__ == "__main__":
    unittest.main()
