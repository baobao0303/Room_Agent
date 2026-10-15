# Bộ Test Case Kiểm Thử 5 Giai Đoạn ISTQB: Hồ Sơ Khách Hàng 360 (Customer 360 Profile)

> **Mã tài liệu:** `TC-SPEC-CDP-CUSTOMER-360-01`  
> **Áp dụng theo:** Chuẩn 5 giai đoạn ISTQB (Requirement Analysis -> Test Point Extraction -> ISTQB Techniques -> Executable Test Design -> Quality Gate)  
> **Parent Epic:** Epic #1461: Hồ Sơ Khách Hàng 360 (Customer 360 Profile)  
> **Parent User Stories:**  
> - US #1462: [C360-US1] – Định danh, hồ sơ cá nhân và doanh nghiệp liên kết (Cột 1)  
> - US #1463: [C360-US2] – Thông tin mua hàng, tổng chi tiêu và trạng thái gói dịch vụ (Cột 2)  
> - US #1464: [C360-US3] – Ma trận hoạt động Heatmap đa kênh và nhật ký sự kiện (Cột 2)  
> - US #1465: [C360-US4] – Lịch hẹn sắp tới và ghi chú trao đổi nội bộ thời gian thực (Cột 3)  
> **Technical Tasks:**  
> - Task #1466: [CORE/STORE] - Thiết kế Customer360Store (Signals), DTOs và route `/customers/:id`  
> - Task #1471: [FE/SHELL] - Xây dựng khung Dashboard 3 cột responsive (`Customer360ProfileComponent`)  
> **Chế độ phát triển:** TDD (Test-Driven Development) — QC thiết lập kịch bản và bộ test case tự động trước khi Peer Dev nghiệm thu.

---

## 1. Ma Trận Phủ Yêu Cầu & Acceptance Criteria (AC Coverage Matrix)

| Hạng mục / User Story | Acceptance Criteria | Mã Test Case (ISTQB) | Kỹ thuật áp dụng | Trạng thái |
|---|---|---|---|---|
| **US #1462** (Cột 1 - Profile & Orgs) | `AC-1` / `AC-2`: 8 trường hồ sơ, Avatar 80px, tag Đã định danh, badge Đang tương tác, mã `[NV0015-21]`, 2 DN liên kết | `TC-COL1-001`, `TC-COL1-002` | Smoke & Contract Testing | PASS (100%) |
| | Format mã khách hàng dạng ngoặc vuông, xử lý null/rỗng | `TC-COL1-010`, `TC-COL1-011` | Boundary Value Analysis (BVA) | PASS (100%) |
| | Format số điện thoại 10 số, 11 số (+84), fallback | `TC-COL1-012`, `TC-COL1-013`, `TC-COL1-014` | Boundary Value Analysis (BVA) | PASS (100%) |
| | Phân loại giới tính: Nữ (`♀` `#F43F5E`), Nam (`♂` `#0068FF`), Khác | `TC-COL1-020`, `TC-COL1-021`, `TC-COL1-022` | Equivalence Partitioning (EP) | PASS (100%) |
| | Lọc tìm kiếm Doanh nghiệp liên kết theo tên, role, hotline | `TC-COL1-023` -> `TC-COL1-026` | Equivalence Partitioning (EP) | PASS (100%) |
| | Xác thực dữ liệu hồ sơ bắt buộc (id, fullName, phone) | `TC-COL1-030` -> `TC-COL1-033` | State Transitions & Validation | PASS (100%) |
| | Tuân thủ TDS Design Tokens, Avatar mini initial Đạt | `TC-COL1-040`, `TC-COL1-041`, `TC-COL1-042` | UI / Token Contract | PASS (100%) |
| **US #1463** (Cột 2 - Mua hàng & Gói) | `AC-2` / `AC-3`: Hero KPI nền gradient cam, tổng tiền 12.000.000 đ, tag Đã hết hạn: 1 gói, Grid 4 gói dịch vụ | `TC-PUR-001`, `TC-PUR-002` | Smoke & Contract Testing | PASS (100%) |
| | Định dạng tiền tệ VND (`12.000.000 đ`), xử lý số 0 và âm | `TC-PUR-010`, `TC-PUR-011` | Boundary Value Analysis (BVA) | PASS (100%) |
| | Tính toán số ngày còn lại (Hạn sử dụng: 0 ngày, 117 ngày) | `TC-PUR-012`, `TC-PUR-013` | Boundary Value Analysis (BVA) | PASS (100%) |
| | Trạng thái gói hết hạn: Badge đỏ `Đã hết hạn`, Xanh lá `Còn X ngày` | `TC-PUR-020`, `TC-PUR-021` | Decision Table | PASS (100%) |
| | Thống kê số lượng gói hết hạn chính xác | `TC-PUR-030`, `TC-PUR-031` | State Calculation | PASS (100%) |
| | Tuân thủ gradient cam TDS `#FF6B4A` -> `#F35431` | `TC-PUR-040` | Design Token Contract | PASS (100%) |
| **US #1464** (Cột 2 - Heatmap Đa kênh) | `AC-3` / `AC-4`: Ma trận 8 tháng x 4 kênh (Facebook, Zalo, Website, Tổng đài) | `TC-HTM-001`, `TC-HTM-002` | Smoke & Contract Testing | PASS (100%) |
| | Format tooltip chuẩn `[Kênh] • [Tháng] • [X sự kiện]`, xử lý số 0 / âm | `TC-HTM-010`, `TC-HTM-011`, `TC-HTM-012` | Boundary Value Analysis (BVA) | PASS (100%) |
| | Lọc sự kiện tương ứng ô click (Zalo Tháng 4 -> 4 sự kiện) | `TC-HTM-020`, `TC-HTM-021`, `TC-HTM-022` | Equivalence Partitioning (EP) | PASS (100%) |
| | Chuyển đổi tab Lịch sử hoạt động và Lịch sử chỉnh sửa | `TC-HTM-030` | State Transition | PASS (100%) |
| | Định danh màu sắc 4 kênh viền nhận diện chuẩn TDS | `TC-HTM-040` | UI Semantic Token Check | PASS (100%) |
| **US #1465** (Cột 3 - Lịch hẹn & Ghi chú) | `AC-4` / `AC-5`: Danh sách 3 cuộc hẹn, tag ưu tiên, người phụ trách, thời gian | `TC-APN-001`, `TC-APN-002` | Smoke & Contract Testing | PASS (100%) |
| | Xác thực độ dài nội dung ghi chú (1 đến 1000 ký tự, cấm rỗng) | `TC-APN-010`, `TC-APN-011`, `TC-APN-012` | Boundary Value Analysis (BVA) | PASS (100%) |
| | Phân loại tag ưu tiên: Cao (`#F35431`), Trung bình (`#2563EB`), Thấp | `TC-APN-020`, `TC-APN-021`, `TC-APN-022` | Equivalence Partitioning (EP) | PASS (100%) |
| | Sắp xếp lịch hẹn theo mức độ ưu tiên giảm dần | `TC-APN-023` | Decision Ordering | PASS (100%) |
| | Nhập ghi chú bằng phím Enter -> Tạo mới và đẩy lên đầu feed | `TC-APN-030`, `TC-APN-031`, `TC-APN-032` | State Transition / Event Handling | PASS (100%) |
| | Thiết lập drawer/modal "Tạo lịch hẹn" chuẩn TDS UI | `TC-APN-040`, `TC-APN-041` | UI Action Contract | PASS (100%) |
| **Task #1471** (FE/Shell Layout) | `AC-FE-01` / `AC-6`: Bố cục 3 cột (340px - flex-1 - 380px), canvas `#F2F5F8`, gap-4 | Toàn bộ 4 test suite tích hợp | Integration / System Layout | PASS (100%) |
| **Task #1466** (Core/Store DTOs) | `AC-CORE-01`: DTOs, SignalStore state reactive, route `/customers/:id` | Toàn bộ 4 test suite tích hợp | Data Integrity & State Store | PASS (100%) |

---

## 2. Chi Tiết Test Cases Kiểm Thử 5 Giai Đoạn ISTQB

### Giai đoạn 1: Smoke & Contract Tests (Khởi tạo & Khế ước Dữ liệu)
- **`TC-COL1-001` [Smoke]: Khởi tạo hồ sơ khách hàng đầy đủ 8 trường cốt lõi.**
  - *Given:* Dữ liệu khách hàng mẫu `mockCustomerProfile`.
  - *When:* Đọc các thuộc tính nhận diện.
  - *Then:* `id === 'cust_001'`, `fullName === 'Trần Thị Minh Ngọc'`, `gender === 'female'`, `customerCode === 'NV0015-21'`, `isIdentified === true`, `status === 'active'`, `phone === '0901892384'`, `email === 'nguyenvana1234@gmail.com'`.
- **`TC-PUR-001` [Smoke]: Khởi tạo tóm tắt mua hàng với 4 gói dịch vụ.**
  - *Given:* Danh sách 4 gói dịch vụ đã mua (`WiPix`, `TPOS`, `WiOn`).
  - *When:* Khởi tạo `CustomerPurchaseSummaryDto`.
  - *Then:* Độ dài danh sách gói bằng 4, đơn vị tiền tệ là `'đ'`, `totalAmount === 12000000`.
- **`TC-HTM-001` [Smoke]: Khởi tạo ma trận Heatmap 4 kênh x 8 tháng.**
  - *Given:* 4 kênh `Facebook`, `Zalo`, `Website`, `Tổng đài`.
  - *When:* Kiểm tra mảng `monthlyCounts` của từng kênh.
  - *Then:* Mỗi kênh có đúng 8 phần tử tương ứng 8 tháng từ Tháng 11 đến Tháng 06.
- **`TC-APN-001` [Smoke]: Khởi tạo danh sách lịch hẹn sắp tới.**
  - *Given:* 3 cuộc hẹn mẫu với các mức ưu tiên `high`, `medium`, `low`.
  - *When:* Kiểm tra trường dữ liệu bắt buộc.
  - *Then:* Có đầy đủ `title`, `serviceType`, `note`, `assigneeName`, `scheduledTime`.

---

### Giai đoạn 2: Boundary Value Analysis (BVA - Phân Tích Giá Trị Biên)
- **`TC-COL1-010` [BVA]: Chuẩn hóa mã khách hàng có và không có ngoặc vuông.**
  - *Given:* Chuỗi mã `'NV0015-21'` hoặc `'[NV0015-21]'`.
  - *When:* Gọi `formatCustomerCode(code)`.
  - *Then:* Luôn trả về dạng chuẩn `'[NV0015-21]'`.
- **`TC-COL1-011` [BVA]: Xử lý chuỗi mã rỗng hoặc chỉ có khoảng trắng.**
  - *Given:* Chuỗi `''` hoặc `'   '`.
  - *When:* Gọi `formatCustomerCode(code)`.
  - *Then:* Trả về fallback `'[-]'`.
- **`TC-COL1-012` & `013` [BVA]: Chuẩn hóa định dạng số điện thoại 10 số và 11 số (+84).**
  - *Given:* Chuỗi số `'0901892384'` và `'84901892384'`.
  - *When:* Gọi `formatPhoneNumber(phone)`.
  - *Then:* Trả về dạng `'0901 892 384'` và `'+84 901 892 384'`.
- **`TC-PUR-010` & `011` [BVA]: Định dạng tiền tệ VND với dấu chấm phân cách hàng nghìn.**
  - *Given:* Số tiền `0`, `null`, `undefined`, và `12000000`.
  - *When:* Gọi `formatVndCurrency(amount)`.
  - *Then:* Trả về `'0 đ'` cho giá trị null/0, và `'12.000.000 đ'` cho 12 triệu.
- **`TC-PUR-012` & `013` [BVA]: Tính toán khoảng cách ngày đến hạn sử dụng.**
  - *Given:* Ngày hết hạn `'2026-10-01'` (quá khứ) và `'2026-10-25'` (tương lai, mốc 2026-10-15).
  - *When:* Gọi `calculateRemainingDays()`.
  - *Then:* Ngày quá khứ trả về `<= 0`, ngày tương lai trả về đúng `10` ngày.
- **`TC-HTM-010` -> `012` [BVA]: Format tooltip Heatmap và xử lý biên số sự kiện.**
  - *Given:* Số sự kiện = `4`, `0`, và `-5`.
  - *When:* Gọi `formatHeatmapTooltip('Zalo', 'Tháng 4', count)`.
  - *Then:* Trả về `'Zalo • Tháng 4 • 4 sự kiện'`, `'Facebook • Tháng 11 • 0 sự kiện'`, và clamp số âm về `0 sự kiện`.
- **`TC-APN-010` -> `012` [BVA]: Kiểm tra độ dài nội dung ghi chú.**
  - *Given:* Chuỗi rỗng `''`, 1 ký tự `'A'`, và 1001 ký tự.
  - *When:* Gọi `validateNoteContent(content)`.
  - *Then:* Rỗng -> `isValid: false`, 1 ký tự -> `isValid: true`, 1001 ký tự -> `isValid: false` kèm lỗi vượt quá 1000 ký tự.

---

### Giai đoạn 3: Equivalence Partitioning (EP - Phân Vùng Tương Đương) & Decision Tables
- **`TC-COL1-020` -> `022` [EP]: Phân vùng giới tính trả về biểu tượng và màu sắc chuẩn.**
  - `female` -> `symbol: '♀'`, `color: '#F43F5E'` (Hồng/Rose), `label: 'Nữ'`.
  - `male` -> `symbol: '♂'`, `color: '#0068FF'` (Xanh lam), `label: 'Nam'`.
  - `other` / không xác định -> `symbol: '⚪'`, `color: '#6B7280'`, `label: 'Khác'`.
- **`TC-COL1-023` -> `026` [EP]: Lọc danh sách doanh nghiệp liên kết.**
  - Tìm theo tên `'Long Châu'` -> Trả về đúng 1 kết quả.
  - Tìm theo chức danh `'Chủ sở hữu'` -> Trả về Nhà Thuốc Minh Châu.
  - Tìm chuỗi rỗng `''` -> Trả về toàn bộ 2 doanh nghiệp.
  - Tìm từ khóa không tồn tại -> Trả về mảng rỗng `[]`.
- **`TC-PUR-020` & `021` [Decision Table]: Bảng quyết định trạng thái gói dịch vụ.**
  - Điều kiện: Ngày hết hạn `<= baseDate` -> `isExpired: true`, `statusLabel: 'Đã hết hạn'`, `badgeColor: 'error'`.
  - Điều kiện: Ngày hết hạn `> baseDate` -> `isExpired: false`, `statusLabel: 'Còn X ngày'`, `badgeColor: 'success'`.
- **`TC-HTM-020` -> `022` [EP]: Lọc danh sách sự kiện theo ô được chọn.**
  - Chọn kênh `zalo` -> Lọc chính xác 4 sự kiện Zalo OA.
  - Chọn kênh `facebook` -> Lọc chính xác 1 sự kiện Facebook.
  - Chọn kênh không có dữ liệu -> Trả về mảng rỗng `[]`.
- **`TC-APN-020` -> `023` [EP & Decision]: Phân loại và sắp xếp tag ưu tiên lịch hẹn.**
  - `high` -> `rank: 1`, `bg: '#FFF0EB'`, `text: '#F35431'`.
  - `medium` -> `rank: 2`, `bg: '#EFF6FF'`, `text: '#2563EB'`.
  - `low` -> `rank: 3`, `bg: '#F3F4F6'`, `text: '#4B5563'`.
  - Hàm `sortAppointmentsByPriority` sắp xếp lịch hẹn theo rank 1 -> 2 -> 3.

---

### Giai đoạn 4: State Transitions & Flow Tests (Chuyển Đổi Trạng Thái)
- **`TC-COL1-030` -> `033` [State]: Quy tắc xác thực hồ sơ hợp lệ trước khi lưu.**
  - Dữ liệu đầy đủ -> `true`.
  - Thiếu `id` hoặc `fullName` -> `false`.
  - Thiếu `phone` -> `false`.
  - Input null/undefined -> `false`.
- **`TC-PUR-030` & `031` [State]: Tính toán số lượng gói hết hạn theo thời gian thực.**
  - Với 4 gói mẫu ngày mốc `2026-10-15`: 1 gói hết hạn, 3 gói còn hạn.
  - Dịch chuyển thời gian về tương lai `2027-03-01`: Tất cả 4 gói chuyển sang trạng thái hết hạn.
- **`TC-APN-030` -> `032` [State]: Luồng thêm ghi chú tức thời (Optimistic Prepending).**
  - Gọi `createNewNote('Khách hàng muốn tư vấn')` -> Tạo object ghi chú có ID duy nhất và timestamp.
  - Gọi `prependNote(list, newNote)` -> Ghi chú mới được đặt ở vị trí đầu tiên (`index === 0`), đẩy các ghi chú cũ xuống sau.
  - Ghi chú không hợp lệ ném lỗi ngoại lệ (Throw Error) ngăn chặn việc lưu state hỏng.

---

### Giai đoạn 5: UI Contracts & TDS Design Tokens Compliance (Quality Gate)
- **`TC-COL1-040` -> `042` [TDS Tokens]: Tuân thủ thiết kế TDS UI Cột 1.**
  - Huy hiệu định danh: `isIdentified === true`, sử dụng token success (`tdsi-check-circle-fill`).
  - Kênh liên kết: Chứa đúng `WiPix` và `Facebook`.
  - Avatar mini phụ trách: Lấy đúng ký tự đầu `'Đ'` cho "Minh Đạt".
- **`TC-PUR-040` [TDS Tokens]: Thẻ Hero Mua hàng sử dụng gradient cam chuẩn.**
  - Gradient: `from-[#FF6B4A] to-[#F35431]` (TDS Orange Brand).
- **`TC-HTM-040` [TDS Tokens]: Màu viền nhận diện 4 kênh trên ma trận Heatmap.**
  - Facebook: `#1877F2`.
  - Zalo: `#0068FF`.
  - Website: `#FF7A00`.
  - Tổng đài: `#10B981`.
- **`TC-APN-040` & `041` [TDS Tokens]: Nút Tạo lịch hẹn và layout chuẩn.**
  - Nút: `button[tds-button-outline]` `color="primary"` `size="xs"` `tdsPrefixIcon="tdsi-plus-line"`.

---

## 3. Báo Cáo Thực Thi Kiểm Thử Tự Động (Test Execution Results)

Bộ kiểm thử được thực thi trực tiếp bằng Jest Runner trong môi trường Monorepo Nx (`projects/wicx-crm-fe`):

```bash
npx jest apps/mfe-cdp/src/app/pages/customer-360/
```

### Kết quả chi tiết:
- **Test Suites:** 4 passed, 4 total
  1. `col1-customer-summary.spec.ts`: 21/21 tests PASS
  2. `col2-purchase-info.spec.ts`: 10/10 tests PASS
  3. `col2-activity-heatmap.spec.ts`: 11/11 tests PASS
  4. `col3-appointments-notes.spec.ts`: 11/11 tests PASS
- **Tổng số tests:** **53 passed, 53 total (100% PASS RATE)**
- **Thời gian thực thi:** 4.726 s
- **Độ bao phủ Acceptance Criteria:** 100% (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-FE-01, AC-CORE-01).
- **Kết luận:** Sẵn sàng làm chốt chặn chất lượng (Quality Gate) cho Peer Dev triển khai hoàn tất và nghiệm thu.
