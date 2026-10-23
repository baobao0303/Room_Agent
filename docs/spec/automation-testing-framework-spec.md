# ĐẶC TẢ KIẾN TRÚC & QUY CHUẨN AUTOMATION TEST SUITE (ROOM_AGENT E2E PIPELINE)

**Tài liệu**: Room Automation Testing Framework Architecture & Catalog Spec  
**Mã tài liệu**: `SPEC-ROOM-AUTO-TEST-2026-V1`  
**Phiên bản**: `1.0.0`  
**Ngày ban hành**: `2026-10-23`  
**Cơ quan ban hành**: Ban Đảm Bảo Chất Lượng SLPPC (QC Architect & Lead Dev)  
**Tiêu chuẩn cốt lõi**: **100% Query độc quyền qua `tds-test-id` (Zero `getByText`, Zero CSS classes, Zero XPath)**  
**Hệ thống mục tiêu**: `projects/wicx-crm-fe` (App Shell, MFE CRM, MFE CDP, MFE Account, MFE Dashboard)  

---

## 1. MỤC TIÊU & NGUYÊN TẮC CỐT LÕI

1. **Kháng 100% sự cố vỡ test (Zero Test Fragility)**:
   - Toàn bộ kịch bản kiểm thử tự động hóa (E2E / Regression Test) tương tác với hệ thống qua **Testing Contract bất biến: `[tds-test-id="..."]`**.
   - Thay đổi bản dịch i18n, nâng cấp token giao diện TDS UI, refactor class Tailwind hoặc tái cấu trúc thẻ HTML **hoàn toàn không làm ảnh hưởng** đến bộ automation.
2. **Tuân thủ mô hình Page Object Model (POM)**:
   - Tách rời mã kịch bản test (Test Specs) và cấu trúc điều khiển giao diện (Page Objects).
   - Mọi locator được đóng gói bên trong class Page đại diện theo từng Domain (`auth`, `customer`, `cdp`, `system`).
3. **Tích hợp cơ chế kiểm định cơ học SLPPC (Mechanical Gate)**:
   - Bộ automation được tích hợp trực tiếp vào lệnh kiểm thử của QC (`tests/automation/runner.py`).
   - Kết quả thực thi (Exit code 0, 100% assertions pass) là **điều kiện tiên quyết** để QC có thẩm quyền chuyển trạng thái Task/Epic sang `Closed`.

---

## 2. KIẾN TRÚC TỔ CHỨC THƯ MỤC AUTOMATION TRONG ROOM

```text
Room_Agent/
├── tests/
│   └── automation/
│       ├── config/
│       │   └── playwright.config.ts        # Cấu hình Playwright, BaseURL, Timeouts, Browsers
│       ├── fixtures/
│       │   └── test-fixtures.ts           # Fixture mở rộng, khởi tạo context, inject QA Helper
│       ├── helpers/
│       │   └── qa-locator-helper.ts       # Bộ helper getByTdsTestId, getDynamicTdsTestId
│       ├── pages/                         # Cấu trúc Page Object Model (POM)
│       │   ├── base.page.ts               # Lớp cơ sở (chứa navigation, wait, helper locator)
│       │   ├── auth-login.page.ts         # Page Object: Đăng nhập & Xác thực
│       │   ├── customer-list.page.ts      # Page Object: Danh sách & Bộ lọc khách hàng
│       │   ├── customer-360.page.ts       # Page Object: Hồ sơ khách hàng Customer 360
│       │   └── notification-hub.page.ts   # Page Object: Chuông thông báo & SignalR Hub
│       ├── specs/                         # Kịch bản kiểm thử tự động hóa (E2E Test Suites)
│       │   ├── auth.e2e.spec.ts           # Test cases kiểm thử đăng nhập & hết hạn phiên
│       │   ├── customer.e2e.spec.ts       # Test cases danh sách, lọc, xóa khách hàng
│       │   └── notification.e2e.spec.ts   # Test cases nhận realtime message và session expired
│       └── runner.py                      # Bộ điều phối tự động hóa tích hợp Harness DB
```

---

## 3. DANH MỤC CA KIỂM THỬ AUTOMATION CHUẨN HÓA (CATALOG)

### 3.1. Phân Hệ Xác Thực (`auth-login-*`)

| Mã Testcase | Tên kịch bản kiểm thử | Hành động & Dữ liệu đầu vào | Selector `tds-test-id` bắt buộc | Kết quả kỳ vọng (Assertion) |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-AUTO-AUTH-01`** | Đăng nhập thành công với tài khoản hợp lệ | Nhập username, password hợp lệ và nhấn Submit | `auth-login-username-input`<br>`auth-login-password-input`<br>`auth-login-submit-btn` | URL chuyển sang Dashboard, hiển thị `system-notification-bell-btn`, cookie `wicx_session_token` được lưu. |
| **`TC-AUTO-AUTH-02`** | Đăng nhập thất bại khi bỏ trống mật khẩu | Nhập username, để trống password và nhấn Submit | `auth-login-password-input`<br>`auth-login-submit-btn`<br>`auth-login-error-alert` | Nút submit không kích hoạt API hoặc hiển thị alert lỗi `auth-login-error-alert`. Không chuyển trang. |
| **`TC-AUTO-AUTH-03`** | Đăng nhập thất bại khi sai mật khẩu | Nhập mật khẩu sai và nhấn Submit | `auth-login-submit-btn`<br>`auth-login-error-alert` | Hiển thị thông báo lỗi `auth-login-error-alert`. |
| **`TC-AUTO-AUTH-04`** | Hiển thị trạng thái quay khi đang gửi request | Nhấn nút đăng nhập và chờ phản hồi mạng | `auth-login-submit-btn-loading` | Nút đăng nhập chuyển sang `tds-test-id="auth-login-submit-btn-loading"` và bị vô hiệu hóa `disabled`. |

---

### 3.2. Phân Hệ Quản Lý Khách Hàng (`customer-list-*`, `customer-row-*`)

| Mã Testcase | Tên kịch bản kiểm thử | Hành động & Dữ liệu đầu vào | Selector `tds-test-id` bắt buộc | Kết quả kỳ vọng (Assertion) |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-AUTO-CUST-01`** | Tải và hiển thị danh sách khách hàng | Truy cập `/:shopId/customers` | `customer-list-table`<br>`customer-row-{id}` | Bảng dữ liệu render tối thiểu 1 dòng `customer-row-{id}` có ID thực thể nghiệp vụ (không dùng index). |
| **`TC-AUTO-CUST-02`** | Tìm kiếm khách hàng theo từ khóa | Nhập tên vào ô tìm kiếm và nhấn Enter | `customer-list-search-input`<br>`customer-row-{id}` | Danh sách tự động lọc, chỉ hiển thị các dòng khớp từ khóa. |
| **`TC-AUTO-CUST-03`** | Mở và xác nhận Modal xóa khách hàng | Bấm nút xóa trên dòng dữ liệu khách hàng | `customer-row-delete-{id}-btn`<br>`customer-delete-confirm-modal`<br>`customer-delete-confirm-primary-btn` | Modal `customer-delete-confirm-modal` hiển thị; bấm xác nhận gọi API xóa và dòng khách hàng biến mất khỏi bảng. |
| **`TC-AUTO-CUST-04`** | Phân trang danh sách khách hàng | Bấm nút chuyển trang tiếp theo | `customer-pagination-next-btn`<br>`customer-pagination-page-active` | Danh sách nạp dữ liệu trang mới, badge trang active cập nhật đúng số trang. |

---

### 3.3. Phân Hệ Customer 360 (`customer-360-*`)

| Mã Testcase | Tên kịch bản kiểm thử | Hành động & Dữ liệu đầu vào | Selector `tds-test-id` bắt buộc | Kết quả kỳ vọng (Assertion) |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-AUTO-360-01`** | Chuyển đổi giữa các Tab thông tin | Bấm vào tab "Đơn hàng" và tab "Lịch sử" | `customer-360-orders-tab`<br>`customer-360-timeline-tab` | Nội dung tương ứng của tab hiển thị đúng, tab được chọn có trạng thái active. |
| **`TC-AUTO-360-02`** | Cập nhật thông tin hồ sơ khách hàng | Sửa tên/SĐT và nhấn nút lưu | `customer-profile-name-input`<br>`customer-profile-save-btn`<br>`system-feedback-success-toast` | Hiển thị Toast thông báo thành công `system-feedback-success-toast`. |

---

### 3.4. Phân Hệ Thông Báo & Kết Nối SignalR (`system-notification-*`, `auth-session-*`)

| Mã Testcase | Tên kịch bản kiểm thử | Hành động & Dữ liệu đầu vào | Selector `tds-test-id` bắt buộc | Kết quả kỳ vọng (Assertion) |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-AUTO-NOTIF-01`**| Nhận thông báo thời gian thực | Mock gửi socket event `notification.received` | `system-notification-bell-btn`<br>`system-notification-unread-badge` | Badge chưa đọc `system-notification-unread-badge` tăng số lượng ngay tức thì. |
| **`TC-AUTO-NOTIF-02`**| Xử lý hết hạn phiên (Hard Teardown) | Mock response 401 trên Negotiate & Refresh | `auth-session-expired-alert`<br>`auth-login-form` | Dập tắt kết nối SignalR, xóa session và tự động redirect về màn hình đăng nhập `auth-login-form`. |

---

## 4. TIÊU CHUẨN NGHIỆM THU AUTOMATION PIPELINE (AC)

- **[AC-AUTO-1] (Zero XPath / Zero CSS Leaks)**: 100% locator trong thư mục `tests/automation/` chỉ được phép dùng cú pháp `[tds-test-id="..."]` hoặc helper `getByTdsTestId()`.
- **[AC-AUTO-2] (Deterministic Execution)**: Kịch bản chạy độc lập, tự động dọn dẹp state sau mỗi test, không bị flaky khi chạy song song.
- **[AC-AUTO-3] (SLPPC Integration)**: Runner `python3 tests/automation/runner.py` nạp kết quả vào Harness DB, hỗ trợ cờ `--ci` ném exit code 1 khi có lỗi.
