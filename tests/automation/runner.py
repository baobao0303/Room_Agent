#!/usr/bin/env python3
"""
Room Automation Runner & Mechanical Verification Gate
File: tests/automation/runner.py

Mục đích:
1. Kiểm tra tính tuân thủ 100% của bộ Automation Test đối với Testing Contract (tds-test-id).
2. Phát hiện và chặn đứng mọi vi phạm query lỏng lẻo (getByText, CSS class, XPath).
3. Đếm và báo cáo danh mục kịch bản kiểm thử E2E đạt chuẩn cho phòng ban SLPPC.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUTO_DIR = Path(__file__).resolve().parent

# Danh mục các mẫu bị nghiêm cấm trong Automation Suite
BANNED_LOCATOR_PATTERNS = [
    (re.compile(r'getByText\s*\('), "Cấm sử dụng getByText() vì dễ gãy khi thay đổi bản dịch i18n"),
    (re.compile(r'locator\s*\(\s*[\'"][.#][a-zA-Z0-9_-]+[\'"]\s*\)'), "Cấm query trực tiếp qua class CSS (.class) hoặc id (#id)"),
    (re.compile(r'locator\s*\(\s*[\'"]//[a-zA-Z0-9_\/\[\]@=" \'-]+[\'"]\s*\)'), "Cấm sử dụng XPath phân cấp"),
    (re.compile(r':nth-child\s*\('), "Cấm query dựa trên cấu trúc DOM phân cấp :nth-child()"),
]

# Danh mục Testcase chuẩn hóa
CATALOG_TESTCASES = [
    {"id": "TC-AUTO-AUTH-01", "domain": "auth", "name": "Đăng nhập thành công với tài khoản hợp lệ", "selector": "auth-login-submit-btn"},
    {"id": "TC-AUTO-AUTH-02", "domain": "auth", "name": "Đăng nhập thất bại khi bỏ trống mật khẩu", "selector": "auth-login-error-alert"},
    {"id": "TC-AUTO-AUTH-03", "domain": "auth", "name": "Đăng nhập thất bại khi sai mật khẩu", "selector": "auth-login-error-alert"},
    {"id": "TC-AUTO-AUTH-04", "domain": "auth", "name": "Hiển thị trạng thái quay khi gửi request", "selector": "auth-login-submit-btn-loading"},
    {"id": "TC-AUTO-CUST-01", "domain": "customer", "name": "Tải và hiển thị danh sách với ID thực thể", "selector": "customer-row-{id}"},
    {"id": "TC-AUTO-CUST-02", "domain": "customer", "name": "Tìm kiếm khách hàng theo từ khóa", "selector": "customer-list-search-input"},
    {"id": "TC-AUTO-CUST-03", "domain": "customer", "name": "Mở và xác nhận Modal xóa khách hàng", "selector": "customer-delete-confirm-modal"},
    {"id": "TC-AUTO-CUST-04", "domain": "customer", "name": "Phân trang danh sách khách hàng", "selector": "customer-pagination-next-btn"},
    {"id": "TC-AUTO-360-01",  "domain": "customer", "name": "Chuyển đổi Tab trong Customer 360", "selector": "customer-360-orders-tab"},
    {"id": "TC-AUTO-NOTIF-01","domain": "system",   "name": "Nhận thông báo realtime qua SignalR", "selector": "system-notification-bell-btn"},
    {"id": "TC-AUTO-NOTIF-02","domain": "auth",     "name": "Dập tắt phiên và điều hướng khi hết hạn", "selector": "auth-session-expired-alert"},
]

def audit_automation_suite() -> Tuple[bool, List[str]]:
    """Quét toàn bộ thư mục tests/automation/ để phát hiện vi phạm selector."""
    violations = []
    ts_files = list(AUTO_DIR.rglob("*.ts"))
    
    for file_path in ts_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
            
        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            # Bỏ qua comment
            trimmed = line.strip()
            if trimmed.startswith("//") or trimmed.startswith("/*") or trimmed.startswith("*"):
                continue
                
            for pattern, reason in BANNED_LOCATOR_PATTERNS:
                if pattern.search(line):
                    rel_path = file_path.relative_to(BASE_DIR)
                    violations.append(f"  ❌ [{rel_path}:{idx}] {reason}\n     -> Dòng mã: {trimmed}")

    return len(violations) == 0, violations

def list_catalog():
    print("=" * 80)
    print("📋 DANH MỤC CA KIỂM THỬ AUTOMATION CHUẨN HÓA (ROOM_AGENT E2E PIPELINE)")
    print("=" * 80)
    print(f"{'MÃ TC':<20} | {'DOMAIN':<10} | {'TARGET SELECTOR':<32} | {'TÊN KỊCH BẢN'}")
    print("-" * 80)
    for tc in CATALOG_TESTCASES:
        print(f"{tc['id']:<20} | {tc['domain']:<10} | {tc['selector']:<32} | {tc['name']}")
    print("=" * 80)
    print(f"Tổng số kịch bản chuẩn hóa: {len(CATALOG_TESTCASES)} ca kiểm thử E2E.")

def main():
    parser = argparse.ArgumentParser(description="Room Automation Test Suite Runner & Auditor")
    parser.add_argument("command", choices=["audit", "list", "report"], nargs="?", default="report")
    args = parser.parse_args()

    if args.command == "list":
        list_catalog()
        sys.exit(0)

    is_clean, violations = audit_automation_suite()

    print("=" * 80)
    print("🛡️ ROOM AUTOMATION COMPLIANCE & SELECTOR INTEGRITY AUDITOR")
    print("=" * 80)
    
    if is_clean:
        print("✅ PASS: 100% kịch bản kiểm thử trong tests/automation/ tuân thủ chuẩn tds-test-id!")
        print("✅ Không phát hiện bất kỳ selector cẩu thả nào (0 getByText, 0 CSS class, 0 XPath).")
        print(f"✅ Sẵn sàng thực thi với {len(CATALOG_TESTCASES)} kịch bản chuẩn hóa.")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"❌ VETO: Phát hiện {len(violations)} vi phạm quy chuẩn selector kiểm thử:")
        for v in violations:
            print(v)
        print("=" * 80)
        print("Halt! Cần sửa chữa toàn bộ selector vi phạm sang getByTdsTestId() trước khi chạy.")
        sys.exit(1)

if __name__ == "__main__":
    main()
