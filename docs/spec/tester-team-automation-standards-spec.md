# BẢN ĐẶC TẢ KỸ THUẬT TOÀN DIỆN: QUY CHUẨN AUTOMATION TESTING & QUY TRÌNH KIỂM THỬ TESTER TEAM

**Tài liệu**: Enterprise Automation Testing Standards & Test Data Architecture Spec  
**Mã tài liệu**: `SPEC-TESTER-TEAM-AUTO-2026-V1`  
**Phiên bản**: `1.0.0 (Enterprise Official)`  
**Ngày ban hành**: `2026-10-23`  
**Cơ quan ban hành**: Ban Đảm Bảo Chất Lượng SLPPC (QC Architect & Tester Team Lead)  
**Căn cứ tham chiếu gốc từ Outline**:
- Bộ sưu tập: *Tester Team* (`https://outline.tpos.app/collection/tester-team-0FEQPr2SlC`)
- Tài liệu quy trình: *Quy Định Viết TestCase & LogBug, Tag, ENV - Quy Trình Làm Việc* (ID: `a9ba5f70-fa5c-40d7-b5a3-d821494d7a17`)
- Tài liệu kế hoạch: *PLAN AUTO & Ma Trận Coverage Priority* (ID: `88a25242-9a41-4929-9a85-cf6bca6175a0`)
- Tài liệu dữ liệu kiểm thử: *RULE: PATTERN FILE DATA TEST* (ID: `abe09805-3383-4c90-98fe-e87cba5f5624`)
- Tài liệu dự án: *TPAGE WEB Automation Plan Q4/2026* (ID: `3634a5d4-dc37-4907-8747-fdff7173c287`)
- Tài liệu contract: *TDS TEST ID DESIGN GUIDELINE* (`docs/spec/tds-test-id-guideline-spec.md`)

---

## 1. MỤC TIÊU & TỔNG QUAN HỆ THỐNG

1. **Chuẩn hóa quy trình kiểm thử tự động (Automation Testing)** theo đúng chuẩn mực của đội ngũ Tester Team công ty: Sử dụng **Playwright + TypeScript**, chạy kiểm thử hồi quy tự động trong Azure DevOps CI/CD Pipeline.
2. **Khớp nối hoàn hảo với Testing Contract `tds-test-id`**:
   - 100% kịch bản kiểm thử query phần tử DOM thông qua `[tds-test-id="..."]` hoặc helper `getByTdsTestId()`.
   - Tuyệt đối cấm query qua `getByText()`, class CSS (`.className`), chỉ mục phân cấp (`nth-child`), hoặc XPath tuyệt đối.
3. **Tổ chức dữ liệu kiểm thử tách rời (Separation of Test Data)**: Không để toàn bộ logic và dữ liệu kiểm thử trong một file lớn; bắt buộc phân tách thành `factory`, `smoke.data`, `validation.data`, `query.data`, `permission.data`, và `constants`.

---

## 2. QUY ĐỊNH ĐẶT TÊN & ĐỊNH DANH TEST CASE

### 2.1. Cú Pháp Đặt Tên Bắt Buộc
Mọi tiêu đề Test Case phải tuân thủ nghiêm ngặt định dạng:
$$\mathbf{[Module]\_[Feature]\_[Expected]\_[Action]}$$

- **Mã tiền tố ID Testcase**: Bắt buộc có ID tăng dần đều đặt ở đầu tiêu đề:
  `[MODULE_FEATURE_XXX][Tóm tắt kịch bản]`
- **Ví dụ chuẩn**:
  - `[AUTH_LOGIN_001] [Auth]_[Login]_[Success]_[SubmitValidCredentials]`
  - `[CUST_LIST_001] [Customer]_[List]_[DisplayCorrectly]_[LoadPageWithEntityId]`
  - `[CUST_FILTER_002] [Customer]_[Filter]_[FilterByKeyword]_[SearchName]`

---

## 3. HỆ THỐNG 6 THẺ TAG KIỂM THỬ BẮT BUỘC & MA TRẬN ĐỘ ƯU TIÊN (PRIORITY)

Toàn bộ các ca kiểm thử trong hệ thống bắt buộc phải được phân loại bằng 6 thẻ Tag nghiệp vụ chuẩn:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MA TRẬN PHÂN LOẠI THẺ TAG NGHIỆP VỤ                   │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ 🟢 @valid       │ Happy path / Workflow chính (Bắt buộc verify sau action) │
│ 🟡 @validate    │ Negative / Boundary / Required / Min-Max / Ký tự đặc biệt │
│ 🟢 @query       │ Search / Filter / Sort / Pagination / Detail / Export     │
│ 🔵 @integration │ Flow liên kết dữ liệu chéo giữa Feature A -> Feature B   │
│ 🟣 @e2e         │ Luồng nghiệp vụ End-to-End xuyên suốt (10 - 20 bước)     │
│ 🔴 @permission  │ Phân quyền / Kiểm soát truy cập Role / Ẩn hiện button     │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 3.1. Chi Tiết Từng Loại Tag:

#### 1. `@valid` (Happy Path / Workflow chính):
- Tập trung vào kịch bản nghiệp vụ thành công cốt lõi.
- ⚠️ **Quy tắc bắt buộc**: Sau khi thực hiện hành động Thêm / Sửa / Xóa / Đổi trạng thái THÀNH CÔNG, **bắt buộc phải có bước tìm kiếm hoặc đối soát lại trên danh sách** để xác nhận dữ liệu đã được ghi nhận chuẩn xác.

#### 2. `@validate` (Kiểm định ranh giới & dữ liệu đầu vào):
- Phân tích giá trị biên (Boundary Value Analysis), trường bắt buộc (Required), dữ liệu rỗng (Null/Empty), độ dài tối thiểu/tối đa (Min/Max length), ký tự đặc biệt, định dạng sai (Regex validation).

#### 3. `@query` (Truy vấn không làm biến đổi dữ liệu):
- Các thao tác chỉ đọc: Tìm kiếm (Search), Bộ lọc (Filter), Sắp xếp (Sort), Phân trang (Pagination), Xem chi tiết (View Detail), Chuyển Tab (Tab Navigation), Báo cáo (Report), Xuất Excel (Export).

#### 4. `@integration` (Tương tác liên kết đa tính năng):
- Xác định rõ: *Tính năng A thay đổi $\rightarrow$ Ảnh hưởng dữ liệu gì tới Tính năng B*.
- Ví dụ: Cập nhật thông tin khách hàng ở `mfe-crm` $\rightarrow$ Kiểm tra thông tin hiển thị trong lịch sử sự kiện `mfe-cdp`.

#### 5. `@e2e` (Luồng xuyên suốt End-to-End):
- Áp dụng độc quyền cho **Critical Business Flow**.
- Bắt đầu từ Entry point (màn hình danh sách/dashboard) $\rightarrow$ trải qua 10–20 bước liên hoàn $\rightarrow$ kết thúc tại kết quả cuối cùng user quan tâm.
- Mỗi bước trung gian đều phải verify điều kiện tiên quyết trước khi đi tiếp.

#### 6. `@permission` (Kiểm soát phân quyền & Bảo mật):
- Kiểm tra quyền truy cập theo vai trò (Role-based Access Control): Quyền xem, tạo, sửa, xóa, xuất dữ liệu; ẩn/hiện nút bấm tương ứng với role; chặn truy cập URL trực tiếp khi không có quyền.

---

### 3.2. Ma Trận Xác Định Độ Ưu Tiên (Priority Matrix):
Theo quy tắc cốt lõi của Tester Team: **BUSINESS quyết định Priority, COVERAGE quyết định cần Auto những gì.**

| Coverage Tag | Mục tiêu kiểm thử | Business Critical | Business Important | Business Normal | Quy tắc đưa vào Kế hoạch Auto |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 🟢 **`@valid`** | Happy path / Luồng chính | 🔴 **P1** | 🟠 **P2** | 🟢 **P3** | **Bắt buộc 100%** cho mọi workflow chính |
| 🟢 **`@query`** | Search / Filter / Detail / Export | 🔴 **P1** | 🟠 **P2** | 🟢 **P3** | Ưu tiên cao cho màn hình dùng thường xuyên |
| 🟡 **`@validate`**| Negative / Boundary / Required | 🔴 **P1** | 🟠 **P2** | 🟢 **P3** | Ưu tiên các trường dữ liệu tài chính/đơn hàng |
| 🔵 **`@integration`**| Liên kết chéo đa phân hệ | 🔴 **P1** | 🟠 **P2** | 🟢 **P3** | Bắt buộc khi có đồng bộ dữ liệu |
| 🟣 **`@e2e`** | Luồng xuyên suốt toàn hệ thống | 🔴 **P1** | 🟠 **P2** | 🟢 **P3** | Chỉ áp dụng cho các hành trình cốt lõi |
| 🔴 **`@permission`** | Phân quyền bảo vệ dữ liệu | 🔴 **P1** | 🟠 **P2** | 🟢 **P3** | Bắt buộc cho tính năng phân cấp nhân viên |

---

## 4. QUY CHUẨN CẤU TRÚC TÁCH FILE DỮ LIỆU KIỂM THỬ (PATTERN FILE DATA TEST)

Theo tài liệu *RULE: PATTERN FILE DATA TEST* của Tester Team, **nghiêm cấm để toàn bộ dữ liệu kiểm thử trong một file test lớn**. Toàn bộ dữ liệu kiểm thử phải được phân tách theo cấu trúc mô-đun:

```text
tests/automation/data/
└── <module>/                              # Ví dụ: customer, auth, cdp, order
    ├── <module>.factory.ts                # Sinh dữ liệu ngẫu nhiên & object default
    ├── <module>.constants.ts              # Hằng số, Enum tĩnh, Endpoint, Timeout
    └── <feature>/                         # Thư mục tính năng con (ví dụ: customer-list)
        ├── <module>.smoke.data.ts         # Data kịch bản Happy path (@valid, @integration, @e2e)
        ├── <module>.validation.data.ts    # Data lỗi, boundary, rỗng, min/max (@validate)
        ├── <module>.query.data.ts         # Data tìm kiếm, filter criteria, sort keys (@query)
        └── <module>.permission.data.ts    # Dữ liệu tài khoản theo Role và quyền hạn (@permission)
```

### 4.1. Nhiệm Vụ Của Từng Tệp Dữ Liệu:
1. **`*.factory.ts`**: Chứa hàm `createDefaultCustomer()`, sinh số điện thoại ngẫu nhiên, tạo mã khách hàng duy nhất chống trùng lặp dữ liệu trên database test.
2. **`*.smoke.data.ts`**: Cung cấp payload chuẩn cho các kịch bản chạy nhanh (Smoke Test / Happy Path).
3. **`*.validation.data.ts`**: Cung cấp các payload chứa chuỗi ký tự đặc biệt, chuỗi vượt quá 255 ký tự, số âm, ngày tháng không hợp lệ để verify thông báo lỗi.
4. **`*.query.data.ts`**: Cung cấp các từ khóa tìm kiếm (tiếng Việt có dấu, không dấu, chữ hoa, chữ thường) và điều kiện lọc trạng thái.
5. **`*.permission.data.ts`**: Cung cấp credentials của từng nhóm vai trò: Admin, Manager, Staff, Cashier.
6. **`*.constants.ts`**: Chứa các thông số cố định như HTTP status code, URL path, message thông báo thành công.

---

## 5. TÍCH HỢP PAGE OBJECT MODEL & TESTING CONTRACT `tds-test-id`

Mọi file kiểm thử trong bộ Automation bắt buộc phải tương tác qua lớp trừu tượng **Page Object Model (POM)** kết hợp với Testing Contract `tds-test-id`:

```typescript
// tests/automation/pages/customer-list.page.ts
import { BasePage } from './base.page';

export class CustomerListPage extends BasePage {
  // 100% Locators độc quyền qua tds-test-id
  public readonly customerTable = this.getByTestId('customer-list-table');
  public readonly searchInput = this.getByTestId('customer-list-search-input');
  public readonly filterBtn = this.getByTestId('customer-list-filter-btn');
  public readonly deleteConfirmModal = this.getByTestId('customer-delete-confirm-modal');

  // Dynamic locator theo ID thực thể nghiệp vụ (CẤM dùng array index)
  public getCustomerRow(customerId: string | number) {
    return this.getDynamicTestId('customer-row', customerId);
  }
}
```

---

## 6. CHẾ TÀI XỬ PHẠT & QUY TRÌNH NGHIỆM THU SLPPC

### 6.1. Chế Tài Trừ Điểm Kỷ Luật KPI (Theo Quy Định Tester Team)
Để đảm bảo chất lượng tài liệu và tính toàn vẹn của mã kiểm thử:
- **Nhân sự từ Level Middle $\rightarrow$ Senior**: **-3 điểm / lỗi** vi phạm.
- **Nhân sự từ Level Fresher $\rightarrow$ Junior**: **-2 điểm / lỗi** vi phạm.
- **Các lỗi bị xử phạt ngay lập tức**:
  1. Đặt tên testcase sai format `[Module]_[Feature]_[Expected]_[Action]`.
  2. Viết testcase thiếu thẻ Tag phân loại (`@valid`, `@validate`, `@query`...).
  3. Thiếu bước tìm kiếm lại danh sách sau khi thêm/sửa/xóa thành công trong testcase `@valid`.
  4. Gom toàn bộ test data vào 1 file lớn, vi phạm cấu trúc *Pattern File Data Test*.
  5. Sử dụng `getByText`, class CSS hoặc XPath lỏng lẻo trong mã automation.

### 6.2. Cổng Kiểm Định Cơ Học Của QC Verifier (Mechanical Verification Gate)
- Kịch bản kiểm thử phải được kiểm tra tính hợp lệ bằng công cụ:
  ```bash
  python3 tests/automation/runner.py audit
  ```
- Chỉ khi công cụ trả về **`PASS (0 vi phạm)`**, QC mới có thẩm quyền ký biên bản nghiệm thu và đóng Task/Epic trên Floci Harness DB.

---

## 7. BỘ TÀI NGUYÊN ĐÃ TRIỂN KHAI SẴN TRONG ROOM_AGENT

1. **Bộ điều phối kiểm thử**: `tests/automation/runner.py`.
2. **Page Objects**: `tests/automation/pages/base.page.ts`, `auth-login.page.ts`, `customer-list.page.ts`.
3. **Kịch bản E2E mẫu**: `tests/automation/specs/auth.e2e.spec.ts`, `customer.e2e.spec.ts`.
4. **Helper QA locator**: `tests/automation/helpers/qa-locator-helper.ts`.
5. **Cấu hình TypeScript sạch**: `tsconfig.json` (0 errors).
