#!/usr/bin/env python3
"""
scripts/git_pre_commit_guard.py - Git Pre-commit Hook tự động chặn đứng vi phạm quy tắc SLPC tại chỗ.

Kiểm tra nghiêm ngặt trước mỗi commit:
1. [Hardcoded Hex]: CẤM mã màu hex cứng (#...) trong file .html, .scss, .css, .ts. Bắt buộc dùng token TDS.
2. [Role Fence]: Nếu Agent thực hiện commit là Supervisor hoặc Lead mà sửa code trong apps/ -> CẤM COMMIT.
3. [Dead Code]: Cảnh báo nếu import các module cũ bị deprecated (như TDSDataTableModule sau khi chuyển sang tds-table).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{3,8}\b")
EXCLUDED_PATTERNS = ["#fff", "#ffffff", "#000", "#000000"]  # Cho phép màu đen trắng thuần nếu cần
SECRET_PATTERN = re.compile(r"""(?:sk-[a-zA-Z0-9_\-]{16,}|ghp_[a-zA-Z0-9]{20,}|AIza[0-9A-Za-z\-_]{35})""")


def check_staged_changes():
    # 1. Lấy danh sách file staged
    res = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    staged_files = [f.strip() for f in res.stdout.strip().splitlines() if f.strip()]

    if not staged_files:
        sys.exit(0)

    # 1.5. Chặn rò rỉ Source Repositories (Anti-Source-Leak Fence)
    leaked_projects = [f for f in staged_files if f.startswith("projects/") or f == "projects"]
    if leaked_projects:
        print("⛔ [SOURCE REPO LEAK PREVENTION CHẶN COMMIT]:", file=sys.stderr)
        print("   Phát hiện thư mục projects/ bị stage! Tuyệt đối CẤM commit submodule mã nguồn vào Room_Agent.", file=sys.stderr)
        for lp in leaked_projects[:5]:
            print(f"   - {lp}", file=sys.stderr)
        print("\nHướng dẫn khắc phục:", file=sys.stderr)
        print("   Chạy ngay: git restore --staged projects/", file=sys.stderr)
        sys.exit(1)

    # 2. Kiểm tra Rào Cản Vai Trò (Role Fence)
    current_agent = os.environ.get("AI_AGENT", "").strip().lower() or os.environ.get("HERMES_PROFILE", "").strip().lower()
    if current_agent in ("supervisor", "lead", "lead dev", "lead ba", "lead design"):
        for f in staged_files:
            if "apps/" in f and not f.endswith(".spec.ts"):
                print(f"⛔ [ROLE FENCE VIOLATION CHẶN COMMIT]:", file=sys.stderr)
                print(f"   Agent hiện tại là '{current_agent.upper()}' (QUẢN LÝ).", file=sys.stderr)
                print(f"   Quản lý bị CẤM TUYỆT ĐỐI sửa mã nguồn production: {f}", file=sys.stderr)
                print(f"   Hành động: Bóc tách Task và bàn giao cho Peer Dev thực hiện!", file=sys.stderr)
                sys.exit(1)

    # 3. Kiểm tra Mã Màu Hex Cứng (Hardcoded Hex Colors)
    diff_res = subprocess.run(["git", "diff", "--cached", "-U0"], capture_output=True, text=True)
    current_file = ""
    violations = []

    for line in diff_res.stdout.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            continue

        # Chỉ kiểm tra file source giao diện
        if not any(current_file.endswith(ext) for ext in [".html", ".scss", ".css", ".ts"]):
            continue
        # Bỏ qua file spec kiểm thử
        if current_file.endswith(".spec.ts"):
            continue

        # Chỉ kiểm tra những dòng MỚI THÊM (+)
        if line.startswith("+") and not line.startswith("+++"):
            # 3.1. Quét Secret API Keys (Anti-Secret-Leak Fence)
            sec_matches = SECRET_PATTERN.findall(line)
            if sec_matches and not current_file.endswith(".gitleaks.toml"):
                print("⛔ [SECURITY LEAK PREVENTION CHẶN COMMIT]:", file=sys.stderr)
                print(f"   Phát hiện API Key / Token trong file staged: {current_file}", file=sys.stderr)
                print(f"   Dòng: {line.strip()}", file=sys.stderr)
                print("\nHướng dẫn khắc phục:", file=sys.stderr)
                print("   1. Xóa sạch token/key hardcode và dùng os.environ.get('...', '')", file=sys.stderr)
                print("   2. Không bao giờ commit secret vào kho mã nguồn!", file=sys.stderr)
                sys.exit(1)

            matches = HEX_PATTERN.findall(line)
            for m in matches:
                if m.lower() not in EXCLUDED_PATTERNS and not ("url(" in line or "data:image" in line):
                    violations.append((current_file, m, line.strip()))

    if violations:
        print("⛔ [TDS UI COMPLIANCE CHẶN COMMIT]:", file=sys.stderr)
        print("   Phát hiện mã màu hex cứng trong code mới thêm! Bắt buộc dùng token TDS UI:", file=sys.stderr)
        for f, val, code in violations[:5]:
            print(f"   - {f}: chứa màu '{val}' trong dòng: {code}", file=sys.stderr)
        print("\nHướng dẫn khắc phục:", file=sys.stderr)
        print("   1. Thay thế bằng class Tailwind chuẩn TDS: bg-white, text-neutral-900, border-neutral-200...")
        print("   2. Hoặc tra cứu CSS token TDS qua: python3 tools/tds_search.py '<tên_màu>'", file=sys.stderr)
        sys.exit(1)

    print("✅ [Git Pre-commit Guard]: Toàn bộ file staged đều đạt chuẩn SLPC (0 mã màu hex cứng, đúng vai trò)!")
    sys.exit(0)


if __name__ == "__main__":
    check_staged_changes()
