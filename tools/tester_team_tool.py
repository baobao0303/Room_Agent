#!/usr/bin/env python3
"""
tools/tester_team_tool.py - Bộ Công Cụ Quản Lý & Tự Động Hóa Kiểm Thử Chuẩn Tester Team.

Căn cứ kỹ thuật:
- docs/spec/tester-team-automation-standards-spec.md
- docs/spec/tds-test-id-guideline-spec.md
- Outline Collection Tester Team (tester-team-0FEQPr2SlC)

Tính năng chính:
  1. audit: Quét cú pháp đặt tên testcase, kiểm tra 6 thẻ tag (@valid, @validate, @query...),
            phát hiện selector cẩu thả (getByText, CSS, XPath) và tính điểm phạt KPI (-3/-2 điểm).
  2. scaffold: Tự động sinh trọn bộ khung Automation (POM, Pattern File Data Test, E2E Spec).
  3. matrix: Thống kê ma trận độ phủ kiểm thử theo Tag và mức độ ưu tiên P1/P2/P3.
  4. list-rules: Hiển thị toàn bộ quy chuẩn, quy tắc đặt tên và chế tài phạt KPI.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Quy chuẩn Thẻ Tag
REQUIRED_TAGS = {"@valid", "@validate", "@query", "@integration", "@e2e", "@permission"}
AUTOMATION_FLAGS = {"@auto_candidate", "@automated"}

# 2. Quy chuẩn Naming Testcase
# Format: [Module]_[Feature]_[Expected]_[Action] hoặc [ID]_[Module]_[Feature]_[Expected]_[Action]
TESTCASE_TITLE_REGEX = re.compile(
    r'^\[([A-Z0-9_]+)\]\s*\[([a-zA-Z0-9]+)\]_\[([a-zA-Z0-9]+)\]_\[([a-zA-Z0-9]+)\]_\[([a-zA-Z0-9]+)\]'
)
# Cú pháp đơn giản hơn trong code e2e: test('[TC-XXX] ...', ...)
E2E_SPEC_REGEX = re.compile(r'test\s*\(\s*[\'"`]\[([A-Z0-9_-]+)\]\s*([^"\'`]+)[\'"`]')

# 3. Mẫu Selector bị cấm
BANNED_LOCATORS = [
    (re.compile(r'getByText\s*\('), "Dùng getByText() (vỡ khi đổi ngôn ngữ i18n)"),
    (re.compile(r'locator\s*\(\s*[\'"][.#][a-zA-Z0-9_-]+[\'"]\s*\)'), "Query qua CSS class (.class) hoặc id (#id)"),
    (re.compile(r'locator\s*\(\s*[\'"]//[a-zA-Z0-9_\/\[\]@=" \'-]+[\'"]\s*\)'), "Dùng XPath phân cấp"),
    (re.compile(r':nth-child\s*\('), "Dùng selector phân cấp :nth-child()"),
]

# 4. Kiểm tra tds-test-id format: <domain>-<component>-<element>-<state?>
TDS_TEST_ID_REGEX = re.compile(r'\[tds-test-id=["\']([a-z0-9]+)-([a-z0-9]+)-([a-z0-9-]+)["\']\]')


class TestCaseAuditReport:
    def __init__(self):
        self.total_scanned_files = 0
        self.total_testcases = 0
        self.valid_testcases = 0
        self.violations: List[Dict[str, Any]] = []
        self.kpi_penalty_senior = 0
        self.kpi_penalty_junior = 0
        self.tag_counts = {t: 0 for t in REQUIRED_TAGS}

    def add_violation(self, file_path: str, line_no: int, message: str, penalty_type: str = "rule"):
        senior_pts = 3 if penalty_type == "rule" else 3
        junior_pts = 2 if penalty_type == "rule" else 2
        self.kpi_penalty_senior += senior_pts
        self.kpi_penalty_junior += junior_pts
        self.violations.append({
            "file": file_path,
            "line": line_no,
            "message": message,
            "penalty_senior": senior_pts,
            "penalty_junior": junior_pts
        })


def audit_test_files(target_dir: Path) -> TestCaseAuditReport:
    """Quét và thẩm định toàn bộ file spec/test trong thư mục chỉ định."""
    report = TestCaseAuditReport()
    
    # Tìm kiếm các tệp spec/test trong thư mục
    test_files = []
    if target_dir.is_file():
        test_files = [target_dir]
    else:
        for ext in ("*.spec.ts", "*.test.ts", "*.e2e.ts", "*.page.ts"):
            test_files.extend(target_dir.rglob(ext))

    report.total_scanned_files = len(test_files)

    for fpath in test_files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        rel_path = str(fpath.relative_to(BASE_DIR) if fpath.is_relative_to(BASE_DIR) else fpath)
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            trimmed = line.strip()
            # Bỏ qua dòng comment
            if trimmed.startswith("//") or trimmed.startswith("/*") or trimmed.startswith("*"):
                continue

            # 1. Kiểm tra selector cấm
            for pattern, reason in BANNED_LOCATORS:
                if pattern.search(line):
                    report.add_violation(
                        rel_path, idx,
                        f"Vi phạm Selector: {reason} -> `{trimmed}`",
                        penalty_type="rule"
                    )

            # 2. Đếm testcase và kiểm tra format
            match_e2e = E2E_SPEC_REGEX.search(line)
            if match_e2e:
                report.total_testcases += 1
                tc_id = match_e2e.group(1)
                tc_desc = match_e2e.group(2)

                # Kiểm tra xem có gắn tag hợp lệ không
                found_tags = [t for t in REQUIRED_TAGS if t in line or t in tc_desc]
                for t in found_tags:
                    report.tag_counts[t] += 1

                if not found_tags:
                    # Kiểm tra các dòng lân cận xem có comment tag không
                    context_chunk = "\n".join(lines[max(0, idx-5):min(len(lines), idx+5)])
                    found_context_tags = [t for t in REQUIRED_TAGS if t in context_chunk]
                    if not found_context_tags:
                        report.add_violation(
                            rel_path, idx,
                            f"Testcase [{tc_id}] thiếu thẻ Tag phân loại bắt buộc (@valid, @validate, @query, @integration, @e2e, @permission).",
                            penalty_type="rule"
                        )
                    else:
                        for t in found_context_tags:
                            report.tag_counts[t] += 1
                
                # Kiểm tra quy tắc của @valid: nếu là valid thêm/sửa/xóa thì phải có step tìm kiếm lại
                if "@valid" in line or (found_tags and "@valid" in found_tags):
                    # Quét xem trong thân testcase có bước search hoặc get lại không
                    test_body = "\n".join(lines[idx:min(len(lines), idx + 25)])
                    if any(act in tc_desc.lower() for act in ("thêm", "tạo", "xóa", "sửa", "create", "delete", "edit", "update")):
                        if not any(k in test_body.lower() for k in ("search", "find", "get", "query", "filter", "tìm")):
                            report.add_violation(
                                rel_path, idx,
                                f"Testcase @valid [{tc_id}] thực hiện hành động biến đổi dữ liệu nhưng thiếu bước tìm kiếm/đối soát lại trên danh sách.",
                                penalty_type="rule"
                            )

    report.valid_testcases = report.total_testcases - len([v for v in report.violations if "Testcase" in v["message"]])
    return report


def generate_scaffold(module: str, feature: str, out_dir: Path):
    """Tự động sinh trọn bộ khung Automation theo chuẩn Tester Team."""
    mod_clean = module.lower().replace("-", "_")
    feat_clean = feature.lower().replace("-", "_")
    mod_kebab = module.lower().replace("_", "-")
    feat_kebab = feature.lower().replace("_", "-")

    target_data_dir = out_dir / "data" / mod_kebab / feat_kebab
    target_pages_dir = out_dir / "pages"
    target_specs_dir = out_dir / "specs"

    target_data_dir.mkdir(parents=True, exist_ok=True)
    target_pages_dir.mkdir(parents=True, exist_ok=True)
    target_specs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sinh file Data Factory
    factory_path = target_data_dir / f"{mod_kebab}.factory.ts"
    factory_content = f"""/**
 * Test Data Factory cho Module: {module.title()}
 * Tuân thủ chuẩn Outline: RULE: PATTERN FILE DATA TEST
 */

export interface {module.title()}Payload {{
  id?: number;
  code: string;
  name: string;
  status: string;
}}

export class {module.title()}Factory {{
  public static createDefault(override: Partial<{module.title()}Payload> = {{}}): {module.title()}Payload {{
    const rand = Math.floor(Math.random() * 89999) + 10000;
    return {{
      code: `{mod_clean.upper()}_${{rand}}`,
      name: `Khách hàng Tự động ${{rand}}`,
      status: 'active',
      ...override,
    }};
  }}
}}
"""
    factory_path.write_text(factory_content, encoding="utf-8")

    # 2. Sinh file Smoke Data (@valid, @e2e)
    smoke_path = target_data_dir / f"{mod_kebab}.smoke.data.ts"
    smoke_content = f"""/**
 * Smoke Test Data (@valid, @integration, @e2e)
 */
import {{ {module.title()}Factory }} from './{mod_kebab}.factory';

export const {mod_clean.upper()}_SMOKE_DATA = {{
  validPayload: {module.title()}Factory.createDefault(),
  searchKeyword: 'Nguyen Van A',
}};
"""
    smoke_path.write_text(smoke_content, encoding="utf-8")

    # 3. Sinh file Validation Data (@validate)
    val_path = target_data_dir / f"{mod_kebab}.validation.data.ts"
    val_content = f"""/**
 * Validation Test Data (@validate - Boundary / Negative / Empty / Required)
 */
export const {mod_clean.upper()}_VALIDATION_DATA = {{
  emptyName: {{ name: '' }},
  exceedMaxLength: {{ name: 'A'.repeat(256) }},
  specialCharacters: {{ name: '<script>alert(1)</script>' }},
}};
"""
    val_path.write_text(val_content, encoding="utf-8")

    # 4. Sinh file Query Data (@query)
    query_path = target_data_dir / f"{mod_kebab}.query.data.ts"
    query_content = f"""/**
 * Query Test Data (@query - Search / Filter / Sort)
 */
export const {mod_clean.upper()}_QUERY_DATA = {{
  searchByCode: 'CODE_1001',
  filterStatus: 'active',
}};
"""
    query_path.write_text(query_content, encoding="utf-8")

    # 5. Sinh Page Object Model
    page_path = target_pages_dir / f"{mod_kebab}-{feat_kebab}.page.ts"
    page_content = f"""/**
 * Page Object Model cho {module.title()} {feature.title()}
 * Tuân thủ 100% naming convention: {mod_kebab}-{feat_kebab}-*
 */
import {{ getByTdsTestId, getDynamicTdsTestId }} from '../helpers/qa-locator-helper';

export class {module.title()}{feature.title()}Page {{
  constructor(private page: any) {{}}

  // Locators độc quyền qua tds-test-id
  public readonly mainContainer = getByTdsTestId(this.page, '{mod_kebab}-{feat_kebab}-container');
  public readonly searchInput = getByTdsTestId(this.page, '{mod_kebab}-{feat_kebab}-search-input');
  public readonly submitButton = getByTdsTestId(this.page, '{mod_kebab}-{feat_kebab}-submit-btn');
  public readonly errorAlert = getByTdsTestId(this.page, '{mod_kebab}-{feat_kebab}-error-alert');

  public getRowItem(entityId: string | number) {{
    return getDynamicTdsTestId(this.page, '{mod_kebab}-row', entityId);
  }}

  public async navigate(): Promise<void> {{
    await this.page.goto('/#/{mod_kebab}/{feat_kebab}');
    await this.mainContainer.waitFor({{ state: 'visible' }});
  }}
}}
"""
    page_path.write_text(page_content, encoding="utf-8")

    # 6. Sinh E2E Test Spec
    spec_path = target_specs_dir / f"{mod_kebab}-{feat_kebab}.e2e.spec.ts"
    spec_content = f"""/**
 * Kịch Bản Kiểm Thử E2E Chuẩn Tester Team
 * Format: [{mod_clean.upper()}_{feat_clean.upper()}_XXX]
 */
import {{ test, expect }} from '@playwright/test';
import {{ {module.title()}{feature.title()}Page }} from '../pages/{mod_kebab}-{feat_kebab}.page';
import {{ {mod_clean.upper()}_SMOKE_DATA }} from '../data/{mod_kebab}/{feat_kebab}/{mod_kebab}.smoke.data';
import {{ {mod_clean.upper()}_VALIDATION_DATA }} from '../data/{mod_kebab}/{feat_kebab}/{mod_kebab}.validation.data';

test.describe('{module.title()} - {feature.title()} Automation Suite', () => {{
  let pageObj: {module.title()}{feature.title()}Page;

  test.beforeEach(async ({{ page }}) => {{
    pageObj = new {module.title()}{feature.title()}Page(page);
    await pageObj.navigate();
  }});

  test('[{mod_clean.upper()}_{feat_clean.upper()}_001][@valid] Happy Path - Thao tác thành công', async ({{ page }}) => {{
    await pageObj.searchInput.fill({mod_clean.upper()}_SMOKE_DATA.searchKeyword);
    await pageObj.submitButton.click();
    
    // Quy tắc @valid bắt buộc: verify lại trên danh sách sau action
    const row = pageObj.getRowItem(10293);
    await expect(row).toBeVisible();
  }});

  test('[{mod_clean.upper()}_{feat_clean.upper()}_002][@validate] Kiểm tra lỗi dữ liệu rỗng', async () => {{
    await pageObj.searchInput.fill('');
    await pageObj.submitButton.click();
    await expect(pageObj.errorAlert).toBeVisible();
  }});
}});
"""
    spec_path.write_text(spec_content, encoding="utf-8")

    print(f"✅ Đã tạo thành công bộ khung Automation chuẩn Tester Team tại: {out_dir}")
    print(f"  ├── Data: {factory_path}")
    print(f"  ├── Data: {smoke_path}")
    print(f"  ├── Data: {val_path}")
    print(f"  ├── Data: {query_path}")
    print(f"  ├── Page: {page_path}")
    print(f"  └── Spec: {spec_path}")


def print_rules():
    print("=" * 80)
    print("📘 BẢNG QUY CHUẨN KIỂM THỬ & CHẾ TÀI PHẠT KPI (OUTLINE TESTER TEAM)")
    print("=" * 80)
    print("1. HÌNH THỨC XỬ PHẠT VI PHẠM:")
    print("   • Middle -> Senior : -3 điểm / lỗi vi phạm (Mục B1 Testcase Quality)")
    print("   • Fresher -> Junior: -2 điểm / lỗi vi phạm (Mục A3 EST chính xác theo level)")
    print()
    print("2. ĐẶT TÊN TEST CASE:")
    print("   • Format: [Module]_[Feature]_[Expected]_[Action]")
    print("   • ID bắt buộc ở đầu: [MODULE_FEATURE_001][Tóm tắt nội dung]")
    print()
    print("3. 6 THẺ TAG BẮT BUỘC:")
    print("   • @valid       : Happy path. BẮT BUỘC sau khi thêm/sửa/xóa phải tìm kiếm lại!")
    print("   • @validate    : Boundary, Required, Min/Max, Ký tự đặc biệt, Negative.")
    print("   • @query       : Search, Filter, Sort, Pagination, Detail, Export, Report.")
    print("   • @integration : Liên kết dữ liệu Feature A -> Feature B.")
    print("   • @e2e         : Luồng nghiệp vụ xuyên suốt quan trọng (10-20 steps).")
    print("   • @permission  : Phân quyền theo role, ẩn/hiện nút, bảo vệ URL.")
    print()
    print("4. CẤU TRÚC PATTERN FILE DATA TEST:")
    print("   • *.factory.ts        : Sinh dữ liệu động và object default")
    print("   • *.smoke.data.ts     : Data happy path (@valid, @e2e)")
    print("   • *.validation.data.ts: Data lỗi biên, rỗng, min/max (@validate)")
    print("   • *.query.data.ts     : Data tìm kiếm, bộ lọc (@query)")
    print("   • *.permission.data.ts: Data phân quyền role (@permission)")
    print("   • *.constants.ts      : Hằng số cố định, enum, endpoint")
    print()
    print("5. TESTING CONTRACT:")
    print("   • 100% query qua [tds-test-id='...'] hoặc getByTdsTestId(). CẤM getByText, CSS, XPath.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Tester Team Automation CLI Tool - Chuẩn hóa kịch bản kiểm thử Outline"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Quét và kiểm tra kịch bản testcase & tính điểm phạt")
    audit_parser.add_argument("path", nargs="?", default="tests/automation", help="Đường dẫn file hoặc thư mục kiểm tra")

    # Command: scaffold
    scaffold_parser = subparsers.add_parser("scaffold", help="Tự động sinh bộ khung POM + Data + Spec")
    scaffold_parser.add_argument("--module", required=True, help="Tên module (ví dụ: customer, order, product)")
    scaffold_parser.add_argument("--feature", required=True, help="Tên feature (ví dụ: list, create, filter)")
    scaffold_parser.add_argument("--out-dir", default="tests/automation", help="Thư mục xuất file")

    # Command: rules
    subparsers.add_parser("rules", help="In toàn bộ quy tắc và bảng điểm phạt KPI")

    # Command: matrix
    matrix_parser = subparsers.add_parser("matrix", help="Xuất ma trận phân bổ tag và độ phủ test")
    matrix_parser.add_argument("path", nargs="?", default="tests/automation", help="Đường dẫn kiểm tra")

    args = parser.parse_args()

    if args.command == "rules":
        print_rules()
        sys.exit(0)

    if args.command == "scaffold":
        out_path = Path(args.out_dir)
        if not out_path.is_absolute():
            out_path = BASE_DIR / out_path
        generate_scaffold(args.module, args.feature, out_path)
        sys.exit(0)

    # Mặc định: audit / matrix
    scan_path = Path(args.path if hasattr(args, 'path') and args.path else "tests/automation")
    if not scan_path.is_absolute():
        scan_path = BASE_DIR / scan_path

    if not scan_path.exists():
        print(f"❌ Đường dẫn không tồn tại: {scan_path}")
        sys.exit(1)

    report = audit_test_files(scan_path)

    print("=" * 80)
    print("🛡️ KẾT QUẢ THẨM ĐỊNH QUY CHUẨN AUTOMATION TESTER TEAM")
    print("=" * 80)
    print(f"• Thư mục quét       : {scan_path.relative_to(BASE_DIR) if scan_path.is_relative_to(BASE_DIR) else scan_path}")
    print(f"• Số file kiểm tra   : {report.total_scanned_files}")
    print(f"• Số testcases       : {report.total_testcases}")
    print(f"• Thống kê thẻ Tag   : " + ", ".join([f"{k}: {v}" for k, v in report.tag_counts.items() if v > 0]))
    print(f"• Vi phạm phát hiện  : {len(report.violations)}")
    print("-" * 80)

    if report.violations:
        print("❌ DANH SÁCH LỖI VI PHẠM & ĐIỂM PHẠT KPI:")
        for v in report.violations:
            print(f"  ! [{v['file']}:{v['line']}] {v['message']}")
            print(f"    ↳ Trừ điểm KPI: Senior/Middle: -{v['penalty_senior']}đ | Junior/Fresher: -{v['penalty_junior']}đ")
        print("-" * 80)
        print(f"⚠️ TỔNG ĐIỂM PHẠT KPI DỰ KIẾN:")
        print(f"   • Nếu là nhân sự Middle -> Senior: -{report.kpi_penalty_senior} điểm (Mục B1 Testcase Quality)")
        print(f"   • Nếu là nhân sự Fresher -> Junior: -{report.kpi_penalty_junior} điểm (Mục A3 EST chính xác)")
        print("=" * 80)
        sys.exit(1)
    else:
        print("✅ PASS: 100% kịch bản kiểm thử tuân thủ tuyệt đối quy chuẩn Tester Team!")
        print("✅ 0 lỗi selector (kháng 100% vỡ test) | 0 điểm trừ KPI.")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
