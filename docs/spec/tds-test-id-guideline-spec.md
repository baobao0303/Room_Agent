# BẢN ĐẶC TẢ KỸ THUẬT TOÀN DIỆN & TIÊU CHUẨN KIỂM THỬ TỰ ĐỘNG HÓA: TDS TEST ID DESIGN GUIDELINE & TESTING CONTRACT (FE ↔ QA)

**Mã tài liệu**: `SPEC-TDS-TEST-ID-2026-V2-ENTERPRISE`  
**Phiên bản**: `2.2.0 (Enterprise Comprehensive Edition)`  
**Ngày ban hành**: `2026-10-23`  
**Cơ quan ban hành**: Ban Kỹ thuật Kiến trúc Frontend (Lead Dev) & Quản lý Sản phẩm (PM Agent) & Kiến trúc Kiểm thử (QC Architect)  
**Tham chiếu gốc**: *📘 TDS TEST ID DESIGN GUIDELINE (Angular Shared Library – FE & QA)* (`https://docs.example.com/s/66321f37-3b10-43b8-9f16-f0b2d7e55d33`)  
**Hệ thống áp dụng**: Toàn bộ hệ sinh thái Monorepo `projects/demo-crm-fe` (App Shell, Remote MFEs: `mfe-crm`, `mfe-cdp`, `mfe-account`, `mfe-dashboard`, Thư viện nền tảng `@demo/core`, Shared Libs `tds-ui`)  

---

## MỤC LỤC CHI TIẾT
1. [1️⃣ Mục Tiêu Cốt Lõi & Kiến Trúc Tách Rời (Decoupling Architecture)](#1️⃣-mục-tiêu-cốt-lõi--kiến-trúc-tách-rời-decoupling-architecture)
2. [2️⃣ Chuẩn Kỹ Thuật Bắt Buộc (Technical Specification)](#2️⃣-chuẩn-kỹ-thuật-bắt-buộc-technical-specification)
3. [3️⃣ Hướng Dẫn Sử Dụng Chuẩn Cho Frontend (FE Usage Patterns)](#3️⃣-hướng-dẫn-sử-dụng-chuẩn-cho-frontend-fe-usage-patterns)
4. [4️⃣ Quy Chuẩn Đặt Tên Toàn Diện (Naming Convention - QUAN TRỌNG NHẤT)](#4️⃣-quy-chuẩn-đặt-tên-toàn-diện-naming-convention---quan-trọng-nhất)
5. [5️⃣ Ma Trận Phân Hệ Nghiệp Vụ (Domain Rules & Registry)](#5️⃣-ma-trận-phân-hệ-nghiệp-vụ-domain-rules--registry)
6. [6️⃣ Quy Tắc Bắt Buộc Dành Cho Đội Ngũ FE (FE Team Rules)](#6️⃣-quy-tắc-bắt-buộc-dành-cho-đội-ngũ-fe-fe-team-rules)
7. [7️⃣ Xử Lý Thành Phần Động, Danh Sách & Bảng Dữ Liệu (Dynamic / List / Table)](#7️⃣-xử-lý-thành-phần-động-danh-sách--bảng-dữ-liệu-dynamic--list--table)
8. [8️⃣ Test ID Dựa Trên Trạng Thái (State-Based Test ID - Tùy Chọn Có Kiểm Soát)](#8️⃣-test-id-dựa-trên-trạng-thái-state-based-test-id---tùy-chọn-có-kiểm-soát)
9. [9️⃣ Quy Tắc Bắt Buộc Dành Cho Đội Ngũ QA & Automation Engine](#9️⃣-quy-tắc-bắt-buộc-dành-cho-đội-ngũ-qa--automation-engine)
10. [🔟 Bản Giao Kèo Trách Nhiệm Hai Chiều (Contract FE ↔ QA)](#🔟-bản-giao-kèo-trách-nhiệm-hai-chiều-contract-fe--qa)
11. [1️⃣1️⃣ Quy Trình Quản Lý Thay Đổi 4 Bước (Change Management Lifecycle)](#1️⃣1️⃣-quy-trình-quản-lý-thay-đổi-4-bước-change-management-lifecycle)
12. [1️⃣2️⃣ Danh Mục Kiểm Tra Khi Tạo Pull Request (PR Checklist Bắt Buộc)](#1️⃣2️⃣-danh-mục-kiểm-tra-khi-tạo-pull-request-pr-checklist-bắt-buộc)
13. [1️⃣3️⃣ Danh Mục Lỗi Cẩu Thả & Biện Pháp Chấn Chỉnh (Anti-Patterns Catalog)](#1️⃣3️⃣-danh-mục-lỗi-cẩu-thả--biện-pháp-chấn-chỉnh-anti-patterns-catalog)
14. [1️⃣4️⃣ Tiêu Chuẩn Định Nghĩa Hoàn Thành (Definition of Done - DoD)](#1️⃣4️⃣-tiêu-chuẩn-định-nghĩa-hoàn-thành-definition-of-done---dod)
15. [1️⃣5️⃣ Hiện Thực Hóa Mã Nguồn Sẵn Sàng Triển Khai (Production-Ready Source Code)](#1️⃣5️⃣-hiện-thực-hóa-mã-nguồn-sẵn-sàng-triển-khai-production-ready-source-code)
16. [1️⃣6️⃣ Kế Hoạch Triển Khai SLPPC Zero-Search (Decomposition Roadmap)](#1️⃣6️⃣-kế-hoạch-triển-khai-slppc-zero-search-decomposition-roadmap)

---

## 1️⃣ Mục Tiêu Cốt Lõi & Kiến Trúc Tách Rời (Decoupling Architecture)

Trong quá trình phát triển các ứng dụng doanh nghiệp quy mô lớn (Enterprise CRM & CDP Monorepo), sự va chạm giữa chu kỳ phát hành nhanh của Frontend (thường xuyên đổi giao diện, i18n, Tailwind CSS, icon, refactor DOM) và tính ổn định của Automation Test (Playwright, Cypress, Jest, Selenium) luôn là nguyên nhân số một gây tắc nghẽn phát hành.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            KIẾN TRÚC TÁCH RỜI (DECOUPLING)                  │
│                                                                             │
│   [Lớp Trình Diễn UI / UX]               [Lớp Kiểm Thử Tự Động QA]          │
│   - CSS Classes (Tailwind, TDS)          - Playwright / Cypress / Robot     │
│   - Cấu trúc DOM (div/flex/grid)         - Query độc quyền qua API Contract │
│   - Bản dịch i18n đa ngôn ngữ            - Kháng 100% thay đổi CSS/Text     │
│             │                                        │                      │
│             └───────────────────┬────────────────────┘                      │
│                                 ▼                                           │
│                 ┌───────────────────────────────┐                           │
│                 │     tds-test-id (Testing API) │                           │
│                 │   Contract Bất Biến FE ↔ QA   │                           │
│                 └───────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4 Trụ Cột Mục Tiêu:
1. **Tạo Contract ổn định vĩnh cửu**: Biến thuộc tính kiểm thử thành một **Public Testing API** chính thức của hệ thống. Bất kỳ thay đổi nào liên quan đến Test ID đều phải tuân thủ quy trình kiểm soát phiên bản.
2. **Refactor UI hoàn toàn tự do (Zero Test Fragility)**: Kỹ sư Frontend có thể đổi từ `<table>` sang `<div>` flexbox, chuyển từ TDS v1 sang TDS v2, thay đổi toàn bộ class Tailwind mà **100% test suite của QA không bị gãy**.
3. **Tuyệt đối không phụ thuộc vào UI Text & i18n**: Ngôn ngữ giao diện có thể chuyển từ Tiếng Việt sang Tiếng Anh, Tiếng Nhật mà selector test vẫn giữ nguyên giá trị cố định.
4. **Phạm vi bao phủ toàn diện**: Áp dụng nhất quán cho cả Shared Libraries (`libs/demo-core`, thư viện dùng chung `tds-ui`) lẫn toàn bộ các tầng ứng dụng App Shell và Micro-Frontend remotes.

> 💡 **Khẩu hiệu cốt lõi**: `tds-test-id = public testing API`

---

## 2️⃣ Chuẩn Kỹ Thuật Bắt Buộc (Technical Specification)

Mọi thành phần tham gia vào hệ thống phải tuân thủ nghiêm ngặt bảng đặc tính kỹ thuật sau:

| Tầng (Layer) | Giá trị tiêu chuẩn | Chi tiết kỹ thuật & Quy tắc bắt buộc |
| :--- | :--- | :--- |
| **Angular Directive** | `tdsTestId` | Khai báo selector `[tdsTestId]`. Viết theo chuẩn `camelCase`. Phải là **Standalone Directive** (`standalone: true`) trong `@demo/core`. |
| **DOM Attribute** | `tds-test-id` | Thuộc tính HTML được directive inject vào phần tử: `[attr.tds-test-id]`. Kháng hoàn toàn xung đột với các thư viện thứ ba dùng `data-testid` hoặc `id`. |
| **Casing** | `kebab-case` | Toàn bộ ký tự viết thường (`lower-case`), các từ phân tách duy nhất bằng dấu gạch ngang (`-`). Cấm dùng `camelCase`, `snake_case`, hoặc khoảng trắng. |
| **Ngôn ngữ** | `English` | Bắt buộc 100% danh từ, động từ và trạng thái bằng tiếng Anh kỹ thuật chuyên ngành. Nghiêm cấm tiếng Việt không dấu (ví dụ: cấm `khach-hang-xoa-btn`). |
| **Cơ chế gắn** | Angular Directive | ❌ **Tuyệt đối cấm hardcode** thuộc tính tĩnh `tds-test-id="..."` trực tiếp trên template HTML. Bắt buộc gắn qua directive `tdsTestId` để hỗ trợ lifecycle và sanitization. |
| **Performance Overhead** | Zero Runtime Impact | Directive chỉ gán attribute tại thời điểm khởi tạo (`HostBinding`), không sử dụng polling hay EventListener ngầm, tiêu tốn 0ms CPU time. |

---

## 3️⃣ Hướng Dẫn Sử Dụng Chuẩn Cho Frontend (FE Usage Patterns)

### 3.1. Các Mẫu Sử Dụng Đúng (✔ Valid Patterns)

#### Mẫu 1: Gán Tĩnh Cho Các Nút Bấm / Phần Tử Hành Động (Action Buttons)
Áp dụng cho mọi nút bấm chức năng, liên kết điều hướng, toggle switch:
```html
<!-- Nút đăng nhập hệ thống -->
<button tds-button 
        color="primary" 
        tdsTestId="auth-login-submit-btn" 
        (click)="onLogin()">
  {{ 'AUTH.LOGIN_BUTTON' | translate }}
</button>

<!-- Nút mở drawer tạo mới khách hàng -->
<button tds-button 
        color="secondary" 
        tdsTestId="customer-list-create-btn" 
        (click)="openCreateDrawer()">
  <i class="tdsi-plus-line mr-1"></i>
  {{ 'CUSTOMER.CREATE_NEW' | translate }}
</button>
```
*Kết quả render trên cây DOM thực tế*:
```html
<button class="tds-btn tds-btn-primary" tds-test-id="auth-login-submit-btn">Đăng nhập</button>
<button class="tds-btn tds-btn-secondary" tds-test-id="customer-list-create-btn">Tạo mới</button>
```

#### Mẫu 2: Gán Động Ràng Buộc Theo ID Thực Thể Nghiệp Vụ (Dynamic Data Binding)
Áp dụng cho các danh sách, bảng dữ liệu, card hiển thị lặp qua mảng đối tượng:
```html
<!-- Dòng dữ liệu trong bảng khách hàng -->
@for (customer of customerList(); track customer.id) {
  <tr [tdsTestId]="'customer-row-' + customer.id">
    <td>{{ customer.name }}</td>
    <td>{{ customer.phone }}</td>
    <td>
      <button tdsTestId="customer-row-edit-btn" (click)="onEdit(customer)">Sửa</button>
      <button [tdsTestId]="'customer-row-delete-' + customer.id + '-btn'" (click)="onDelete(customer)">Xóa</button>
    </td>
  </tr>
}
```
*Kết quả render trên cây DOM thực tế*:
```html
<tr tds-test-id="customer-row-98721">...</tr>
<tr tds-test-id="customer-row-98722">...</tr>
```

#### Mẫu 3: Gán Cho Các Trường Form Nhập Liệu (Form Controls)
```html
<form [formGroup]="loginForm" tdsTestId="auth-login-form">
  <input tds-input 
         formControlName="username" 
         tdsTestId="auth-login-username-input" 
         placeholder="Nhập tài khoản" />

  <input tds-input 
         type="password" 
         formControlName="password" 
         tdsTestId="auth-login-password-input" 
         placeholder="Nhập mật khẩu" />
</form>
```

---

### 3.2. Các Mẫu Sai Trái Bị Cấm Tuyệt Đối (❌ Anti-Patterns)

| Đoạn mã sai phạm | Lý do kỹ thuật bị cấm | Biện pháp chuẩn hóa |
| :--- | :--- | :--- |
| `<button data-testid="login">` | Dùng sai chuẩn tên attribute, phân mảnh công cụ test | Đổi sang `tdsTestId="auth-login-submit-btn"` |
| `<button class="btn-primary">` | QA query qua CSS class; khi designer sửa CSS test sẽ gãy | Gắn thêm `tdsTestId="auth-login-submit-btn"` |
| `<div [tdsTestId]="'row-' + index">` | Dùng chỉ mục index mảng; thứ tự dòng bị xáo trộn khi sắp xếp/lọc | Dùng ID thực thể: `[tdsTestId]="'customer-row-' + item.id"` |
| `<button tdsTestId="btn-save">` | Thiếu thành phần `domain` và `component` trong tên | Đổi thành `tdsTestId="customer-detail-save-btn"` |
| `<button tds-test-id="my-btn">` | Hardcode trực tiếp DOM attribute thay vì dùng Directive | Đổi sang directive `tdsTestId="my-btn"` |

---

## 4️⃣ Quy Chuẩn Đặt Tên Toàn Diện (Naming Convention - QUAN TRỌNG NHẤT)

### 4.1. Công Thức Cấu Trúc Ngữ Pháp (BNF Grammar)
Mọi chuỗi định danh `tdsTestId` phải tuân theo cú pháp chính xác:
$$\mathbf{\langle domain \rangle\text{-}\langle component \rangle\text{-}\langle element \rangle\text{-}\langle state? \rangle}$$

```text
<test-id>   ::= <domain> "-" <component> "-" <element> [ "-" <state> ]
<domain>    ::= [a-z0-9]+
<component> ::= [a-z0-9]+
<element>   ::= [a-z0-9]+ "-" <element-type>
<element-type> ::= "btn" | "input" | "select" | "checkbox" | "radio" | "form" | 
                   "modal" | "drawer" | "toast" | "alert" | "row" | "card" | "tab" | "menu"
<state>     ::= "loading" | "disabled" | "active" | "error" | "success" | "selected"
```

### 4.2. Từ Điển Thành Phần Thành Tố Chuẩn Hóa
1. **`<domain>`**: Đại diện cho phân hệ lớn hoặc module nghiệp vụ cha.
2. **`<component>`**: Đại diện cho màn hình, tính năng, hoặc view cụ thể.
3. **`<element>`**: Tên đối tượng kết hợp hậu tố định danh loại thẻ (Widget Type Suffix):
   - Nút bấm: `*-btn`
   - Ô nhập text: `*-input`
   - Hộp chọn: `*-select`
   - Ô đánh dấu: `*-checkbox`
   - Nút chọn một: `*-radio`
   - Biểu mẫu: `*-form`
   - Hộp thoại nổi: `*-modal`
   - Ngăn kéo trượt: `*-drawer`
   - Thông báo nổi: `*-toast`
   - Cảnh báo: `*-alert`
   - Hàng trong bảng: `*-row`
   - Thẻ hiển thị: `*-card`
   - Thẻ điều hướng tab: `*-tab`
4. **`<state?>` (Tùy chọn)**: Chỉ thêm vào khi QA cần bắt buộc kiểm tra trạng thái tương tác phản hồi (State Assertion).

---

### 4.3. Bảng Ánh Xạ Ví Dụ Toàn Diện (Comprehensive Mapping Matrix)

| Khu vực chức năng | Đối tượng UI hiển thị | Thuộc tính `tdsTestId` hợp lệ |
| :--- | :--- | :--- |
| **Xác thực hệ thống** | Form đăng nhập | `auth-login-form` |
| | Input email/tài khoản | `auth-login-email-input` |
| | Input mật khẩu | `auth-login-password-input` |
| | Nút xác nhận đăng nhập | `auth-login-submit-btn` |
| | Liên kết quên mật khẩu | `auth-forgot-password-link` |
| **Quản lý khách hàng** | Nút mở bộ lọc nâng cao | `customer-list-filter-btn` |
| | Ô tìm kiếm tên/SĐT | `customer-list-search-input` |
| | Nút xuất Excel danh sách | `customer-list-export-btn` |
| | Nút phân trang sang trang kế | `customer-pagination-next-btn` |
| | Hàng dữ liệu khách hàng | `customer-row-8491` |
| | Nút xem chi tiết khách hàng | `customer-row-view-detail-btn` |
| | Nút xác nhận xóa trong Modal | `customer-delete-confirm-primary-btn` |
| | Modal xác nhận xóa khách hàng | `customer-delete-confirm-modal` |
| **Customer 360** | Tab thông tin đơn hàng | `customer-360-orders-tab` |
| | Tab lịch sử chăm sóc | `customer-360-timeline-tab` |
| | Nút lưu cập nhật hồ sơ | `customer-profile-save-btn` |
| | Nút lưu đang ở trạng thái quay | `customer-profile-save-btn-loading` |
| **CDP Data Mapping** | Hàng ánh xạ trường sự kiện | `cdp-mapping-row-event-name` |
| | Nút kích hoạt bản ghi ánh xạ | `cdp-mapping-activate-btn` |
| | Select chọn kiểu dữ liệu | `cdp-field-datatype-select` |
| **Thông báo & Hệ thống** | Dropdown chuông thông báo | `system-notification-bell-btn` |
| | Badge đếm số chưa đọc | `system-notification-unread-badge` |
| | Toast báo thành công | `system-feedback-success-toast` |
| | Alert cảnh báo khóa phiên | `auth-session-expired-alert` |

---

### 4.4. Danh Sách Tên Bị Cấm Tuyệt Đối (Blacklist)

```text
❌ submit                  -> Thiếu domain và component
❌ btn1 / btn2             -> Vô nghĩa, không phân biệt được mục đích
❌ red-button              -> Rò rỉ thông tin thiết kế giao diện (CSS Detail Leaks)
❌ loginBtn                -> Sai chuẩn kebab-case
❌ save-btn                -> Thiếu domain cha
❌ my_special_input        -> Sai cú pháp gạch dưới snake_case
❌ nut-dang-nhap           -> Sai ngôn ngữ (phải dùng 100% tiếng Anh)
```

---

## 5️⃣ Ma Trận Phân Hệ Nghiệp Vụ (Domain Rules & Registry)

Để tránh hiện tượng mỗi lập trình viên tự nghĩ ra một domain khác nhau, bảng danh mục Domain chính thức sau đây được cố định:

| Tên Domain chuẩn | Mô tả phạm vi nghiệp vụ | Các component con điển hình |
| :--- | :--- | :--- |
| **`auth`** | Xác thực danh tính, đăng nhập, đăng xuất, phân quyền người dùng, Tenant switcher | `login`, `logout`, `tenant`, `forgot-password`, `reset-password` |
| **`customer`** | Quản lý quan hệ khách hàng, phân nhóm, phân loại, gắn thẻ tag | `list`, `detail`, `360`, `filter`, `tag`, `activity` |
| **`cdp`** | Nền tảng dữ liệu khách hàng, sự kiện thô, ánh xạ trường, cấu hình ingest | `raw-data`, `field-mapping`, `version-history`, `event-stream` |
| **`order`** | Quản lý đơn hàng, giỏ hàng, thông tin thanh toán, trạng thái giao vận | `list`, `checkout`, `cart`, `payment`, `shipping` |
| **`product`** | Danh mục sản phẩm, biến thể, bảng giá, kho bãi | `list`, `detail`, `inventory`, `pricing`, `category` |
| **`admin`** | Quản trị cửa hàng, cấu hình chi nhánh, tài khoản nhân viên, vai trò | `user`, `role`, `branch`, `employee`, `audit-log` |
| **`setting`** | Cài đặt ứng dụng, tùy chọn giao diện, cấu hình tích hợp thứ ba | `general`, `integration`, `notification`, `security` |
| **`system`** | Các thành phần hạ tầng chung của App Shell: Header, Sidebar, Footer, Toast | `header`, `sidebar`, `footer`, `toast`, `modal-container` |

> ⚠️ **Quy tắc bắt buộc**: Khi xuất hiện phân hệ mới chưa có trong danh mục trên, FE và Lead Dev phải gửi đề xuất mở rộng domain lên PM Agent để cập nhật vào Registry trước khi lập trình.

---

## 6️⃣ Quy Tắc Bắt Buộc Dành Cho Đội Ngũ FE (FE Team Rules)

### 6.1. Danh Mục Thành Phần BẮT BUỘC Phải Gắn `tdsTestId`
Mọi thành phần có khả năng nhận tương tác từ con người hoặc phản hồi dữ liệu động đều bắt buộc phải có `tdsTestId`:
1. **Tất cả các Nút bấm (Buttons)**: Cả button chữ, icon button, split button, dropdown toggle button.
2. **Tất cả các Điều khiển Nhập liệu (Form Controls)**: Input text, number, password, textarea, select dropdown, checkbox, radio group, slider, date-picker, time-picker.
3. **Các Vùng Biểu Mẫu (Forms)**: Thẻ `<form>` bao ngoài để QA có thể trigger submit hoặc reset form.
4. **Các Thành Phần Cửa Sổ Nổi (Overlays)**: Modal, Drawer, Bottom Sheet, Popup confirm, Popover context menu.
5. **Các Thành Phần Phản Hồi Trạng Thái (Feedback Widgets)**: Toast notification, Alert banner, Error callout, Empty state placeholder card.
6. **Các Phần Tử Dữ Liệu Lặp (List/Table Items)**: Từng dòng `<tr>` trong bảng hoặc `<div>` card trong danh sách.
7. **Các Phần Tử Điều Hướng (Navigation Elements)**: Menu item, Tab switch header, Breadcrumb link, Pagination buttons.

### 6.2. Danh Mục Thành Phần KHÔNG CẦN Gắn `tdsTestId`
Để giữ cho template gọn gàng và không gây rác DOM (DOM Bloat), tuyệt đối **không gắn** `tdsTestId` cho:
1. Các thẻ layout thuần túy (`<div class="flex items-center justify-between">`, `<section>`, `<main>`).
2. Các icon trang trí độc lập (`<i class="tdsi-calendar-line"></i>`) trừ khi icon đó là nút bấm có click event.
3. Các wrapper div dùng làm khung viền hoặc hiệu ứng đổ bóng.
4. Các đoạn văn bản tĩnh thuần túy không có logic thay đổi (static labels, footer copyright).

---

## 7️⃣ Xử Lý Thành Phần Động, Danh Sách & Bảng Dữ Liệu (Dynamic / List / Table)

### 7.1. Nguyên Tắc Số 1: Luôn Ưu Tiên ID Thực Thể Nghiệp Vụ
Auto test cần tương tác chính xác với một bản ghi cụ thể bất chấp bản ghi đó bị sắp xếp lại vị trí:
```html
<!-- CHUẨN: Ràng buộc với ID duy nhất của dữ liệu -->
<tr [tdsTestId]="'customer-row-' + item.id">
  <td>{{ item.code }}</td>
  <td>{{ item.name }}</td>
  <td>
    <button [tdsTestId]="'customer-row-edit-' + item.id + '-btn'" (click)="edit(item)">Sửa</button>
  </td>
</tr>
```

### 7.2. Nguyên Tắc Số 2: Tránh Dùng Index Mảng Nếu Không Bắt Buộc
- ❌ **Cấm dùng**: `[tdsTestId]="'customer-row-' + index"`
- **Lý do**: Khi người dùng gõ từ khóa tìm kiếm hoặc bấm sắp xếp cột, bản ghi ở `index = 0` sẽ bị thay đổi thành một người khác. Kịch bản auto test của QA sẽ click nhầm khách hàng và sinh lỗi sai lệch dữ liệu.

### 7.3. Nguyên Tắc Số 3: Khi Bản Ghi Không Có ID Số Nguyên
Trong trường hợp dữ liệu danh mục tĩnh hoặc chưa có database ID:
- Sử dụng thuộc tính `slug` hoặc `code` bất biến:
  ```html
  <div [tdsTestId]="'plan-card-' + plan.slug"></div>
  <!-- Render: plan-card-enterprise-monthly -->
  ```

---

## 8️⃣ Test ID Dựa Trên Trạng Thái (State-Based Test ID - Tùy Chọn Có Kiểm Soát)

Trong các kịch bản kiểm thử hành vi nâng cao (Behavior-Driven Testing), QA cần kiểm chứng hệ thống có phản ứng đúng khi đang xử lý tác vụ mạng hay không (ví dụ: nút bấm phải vô hiệu hóa và hiện loading spinner khi đang gọi API).

### 8.1. Cú Pháp Được Phép:
```html
<button tds-button 
        [disabled]="isLoading()" 
        [tdsTestId]="isLoading() ? 'checkout-submit-btn-loading' : 'checkout-submit-btn'">
  @if (isLoading()) {
    <i class="tdsi-loading animate-spin mr-1"></i> Đang xử lý...
  } @else {
    Thanh toán ngay
  }
</button>
```

### 8.2. Ranh Giới Nghiêm Ngặt Chống Rò Rỉ CSS (No CSS Details):
- QA chỉ quan tâm phần tử đang ở **trạng thái logic** nào (`loading`, `disabled`, `error`).
- ❌ **Tuyệt đối cấm đưa chi tiết thị giác vào testId**:
  - Cấm: `checkout-submit-btn-red`
  - Cấm: `checkout-submit-btn-hidden`
  - Cấm: `customer-status-badge-gray-bg`

---

## 9️⃣ Quy Tắc Bắt Buộc Dành Cho Đội Ngũ QA & Automation Engine

### 9.1. Lệnh Query Độc Quyền: Bắt Buộc Dùng `tds-test-id`
Mọi kịch bản kiểm thử (Playwright, Cypress, Puppeteer) chỉ được phép tìm phần tử qua bộ lọc:
```typescript
// Playwright Locator chuẩn:
const submitButton = page.locator('[tds-test-id="auth-login-submit-btn"]');
await submitButton.click();
```

### 9.2. Danh Sách Các Lệnh Bị Nghiêm Cấm Đối Với QA (Ban List):
1. ❌ **Cấm dùng `page.getByText('Đăng nhập')`**: Vì chỉ cần dịch file i18n sang tiếng Anh `"Sign In"`, test suite sẽ lập tức gãy toàn bộ.
2. ❌ **Cấm query bằng CSS class (`page.locator('.tds-btn-primary')`)**: Vì khi đổi theme màu sắc hoặc cập nhật component thư viện, class CSS sẽ thay đổi.
3. ❌ **Cấm query bằng cấu trúc cây phân cấp (`page.locator('div > span:nth-child(2) > button')`)**: Rất dễ vỡ khi FE thêm một thẻ `div` bọc ngoài để căn chỉnh margin.
4. ❌ **Cấm dùng XPath tuyệt đối (`/html/body/div[1]/section/form/button`)**.

---

### 9.3. Bộ Công Cụ Trợ Giúp QA Chuẩn Hóa (QA Helper Library)
Để thống nhất mã nguồn kiểm thử của đội QA, thư viện `@demo/core` cung cấp sẵn bộ helper tiêu chuẩn:

```typescript
/**
 * Thư viện Helper chính thức cho QA Automation (Playwright / Cypress)
 * File: libs/demo-core/src/utils/qa-test-helper.ts
 */

export const getTdsTestIdSelector = (testId: string): string => `[tds-test-id="${testId}"]`;

export const getByTdsTestId = <T extends { locator: (selector: string) => any }>(
  context: T, 
  testId: string
) => {
  return context.locator(getTdsTestIdSelector(testId));
};

export const getDynamicTdsTestId = <T extends { locator: (selector: string) => any }>(
  context: T, 
  prefix: string, 
  entityId: string | number
) => {
  return context.locator(getTdsTestIdSelector(`${prefix}-${entityId}`));
};
```

---

## 🔟 Bản Giao Kèo Trách Nhiệm Hai Chiều (Contract FE ↔ QA)

Để duy trì tính toàn vẹn của Testing API, hai bên FE và QA cùng ký kết giao kèo trách nhiệm:

```text
┌──────────────────────────────────────────────┐    BẮT BUỘC    ┌──────────────────────────────────────────────┐
│           CAM KẾT CỦA FRONTEND (FE)          │ ─────────────► │             CAM KẾT CỦA QA & TEST            │
│ 1. Không đổi testId nếu không breaking       │                │ 1. Không query bằng CSS, text, nth-child     │
│ 2. Thông báo QA trước khi rename             │ ◄───────────── │ 2. Luôn dùng getByTdsTestId()                │
│ 3. Giữ backward compatibility 1 release      │    PHẢN HỒI    │ 3. Tạo Bug ngay nếu màn hình thiếu testId    │
└──────────────────────────────────────────────┘                └──────────────────────────────────────────────┘
```

1. **FE cam kết**:
   - Coi `tds-test-id` là API công khai, không tự ý xóa hoặc đổi tên tùy tiện.
   - Khi có thay đổi luồng nghiệp vụ buộc phải đổi tên, phải phát hành thông báo chính thức cho QA.
2. **QA cam kết**:
   - Tuyệt đối không "lách luật" bằng cách dùng `getByText` hoặc class CSS khi thấy FE thiếu testId.
   - Khi phát hiện phần tử chưa có `tds-test-id`, QA có quyền **VETO từ chối nghiệm thu** và mở Bug ticket yêu cầu FE bổ sung.

---

## 1️⃣1️⃣ Quy Trình Quản Lý Thay Đổi 4 Bước (Change Management Lifecycle)

Khi có yêu cầu bắt buộc phải thay đổi hoặc tái cấu trúc một `tdsTestId` đã tồn tại:

```text
[Release N]                [Release N+1]               [Release N+1 Verify]          [Release N+2]
   BƯỚC 1                      BƯỚC 2                         BƯỚC 3                     BƯỚC 4
┌──────────────┐            ┌──────────────┐               ┌──────────────┐           ┌──────────────┐
│   FE thêm    │ ─────────► │  Duy trì 2   │ ────────────► │ QA cập nhật  │ ────────► │   FE xóa bỏ  │
│  testId mới  │            │ testId song  │               │ test suite   │           │  testId cũ   │
│              │            │     song     │               │  chạy xanh   │           │  hoàn toàn   │
└──────────────┘            └──────────────┘               └──────────────┘           └──────────────┘
```

1. **Bước 1 (Add New)**: FE bổ sung định danh mới theo đúng naming convention mới.
2. **Bước 2 (Dual Support)**: FE duy trì cả ID cũ và ID mới song song trong suốt một bản phát hành (thông qua mảng alias hoặc bổ sung thuộc tính phụ).
3. **Bước 3 (QA Migration)**: Đội ngũ QA tiến hành cập nhật toàn bộ test script sang định danh mới và xác nhận CI chạy pass 100%.
4. **Bước 4 (Cleanup)**: FE dọn dẹp và gỡ bỏ hoàn toàn định danh cũ ở phiên bản tiếp theo.

---

## 1️⃣2️⃣ Danh Mục Kiểm Tra Khi Tạo Pull Request (PR Checklist Bắt Buộc)

### Dành Cho Lập Trình Viên (Frontend Developer):
- [ ] Mọi button, input, form, select, modal trong phạm vi PR đều đã được gắn directive `tdsTestId`.
- [ ] Giá trị `tdsTestId` tuân thủ đúng 100% cú pháp `<domain>-<component>-<element>-<state?>`.
- [ ] Không hardcode thuộc tính `tds-test-id` thủ công; bắt buộc dùng directive `tdsTestId`.
- [ ] Không sử dụng trùng lặp một `testId` cho hai phần tử tương tác khác nhau trên cùng một màn hình.
- [ ] Danh sách lặp đã sử dụng ID thực thể thay vì chỉ số index mảng.

### Dành Cho Kiểm Thử Viên (QA Engineer):
- [ ] 100% các locator trong file test automation chỉ sử dụng `[tds-test-id="..."]` hoặc helper `getByTdsTestId()`.
- [ ] Đã kiểm tra thử nghiệm đổi ngôn ngữ sang Tiếng Anh/Tiếng Việt và xác nhận test không bị fail.
- [ ] Không còn bất kỳ câu lệnh query nào qua `getByText()`, `.className`, hoặc `nth-child`.

---

## 1️⃣3️⃣ Danh Mục Lỗi Cẩu Thả & Biện Pháp Chấn Chỉnh (Anti-Patterns Catalog)

```text
❌ Anti-pattern 1: Gắn testId theo class CSS (tdsTestId="btn-primary-blue")
   ↳ Hậu quả: Designer đổi màu nút sang cam -> Auto test lập tức báo lỗi đỏ.
   ↳ Chấn chỉnh: Đổi sang bản chất hành động: tdsTestId="customer-create-submit-btn".

❌ Anti-pattern 2: Gắn theo nội dung văn bản (tdsTestId="xoa-khach-hang")
   ↳ Hậu quả: Dùng tiếng Việt không dấu, vi phạm quy chuẩn ngôn ngữ toàn cầu.
   ↳ Chấn chỉnh: Đổi sang tiếng Anh kỹ thuật: tdsTestId="customer-item-delete-btn".

❌ Anti-pattern 3: Đổi testId tùy tiện vì "thấy tên cũ không đẹp"
   ↳ Hậu quả: Gãy toàn bộ test suite hồi quy (Regression Test) của công ty trong đêm.
   ↳ Chấn chỉnh: Bắt buộc tuân thủ quy trình Change Management 4 bước có thông báo trước.

❌ Anti-pattern 4: QA lười yêu cầu FE gắn ID mà tự viết XPath lồng 10 cấp
   ↳ Hậu quả: DOM thay đổi một thẻ div bọc ngoài là kịch bản test chết đứng.
   ↳ Chấn chỉnh: QA mở bug trả về cho FE gắn tdsTestId trước khi viết kịch bản.
```

---

## 1️⃣4️⃣ Tiêu Chuẩn Định Nghĩa Hoàn Thành (Definition of Done - DoD)

Một User Story / Task phát triển giao diện chỉ được phép chuyển trạng thái sang **`Resolved`** và nghiệm thu **`Closed`** khi đạt đủ 4 tiêu chí mechanical gates:
1. ✔ **UI Hoàn Thành (Pixel & Design Parity)**: Đạt chuẩn thiết kế TDS UI, chuẩn token màu sắc, typography và responsive mượt mà.
2. ✔ **Logic Nghiệp Vụ Chuẩn Xác**: Xử lý reactive streams, state management đầy đủ, tuân thủ **Strict Typing Gate (Zero `any`, Zero `unknown`)**.
3. ✔ **TDS Test ID Đầy Đủ 100%**: Tất cả các điểm chạm người dùng (User Touchpoints) đều được gắn `tdsTestId` theo đúng chuẩn 4 thành phần.
4. ✔ **Auto-Test Pass Xanh 100%**: Bộ test automation của QA thực thi hoàn tất với kết quả Pass toàn bộ trên môi trường CI.

---

## 1️⃣5️⃣ Hiện Thực Hóa Mã Nguồn Sẵn Sàng Triển Khai (Production-Ready Source Code)

### 15.1. Directive Lõi: `projects/demo-crm-fe/libs/demo-core/src/directives/tds-test-id.directive.ts`
```typescript
import { Directive, HostBinding, Input } from '@angular/core';

/**
 * Directive gắn Testing Contract ID chuẩn doanh nghiệp (TDS Design Guideline)
 * Selector: [tdsTestId]
 * Output DOM: [attr.tds-test-id]
 */
@Directive({
  selector: '[tdsTestId]',
  standalone: true,
})
export class TdsTestIdDirective {
  /**
   * Định danh kiểm thử theo format: <domain>-<component>-<element>-<state?>
   */
  @Input('tdsTestId')
  public testId: string | number | null | undefined = null;

  @HostBinding('attr.tds-test-id')
  public get hostTestId(): string | null {
    if (this.testId === null || this.testId === undefined) {
      return null;
    }
    const cleanId = String(this.testId).trim();
    return cleanId.length > 0 ? cleanId : null;
  }
}
```

### 15.2. File Cập Nhật Export: `projects/demo-crm-fe/libs/demo-core/src/directives/index.ts`
```typescript
export * from './upload.directive';
export * from './tds-test-id.directive';
```

### 15.3. Thư Viện QA Helper: `projects/demo-crm-fe/libs/demo-core/src/utils/qa-test-helper.ts`
```typescript
/**
 * QA Automation Test Helpers for Playwright, Cypress & DOM Testing
 */
export const getTdsTestIdSelector = (testId: string): string => `[tds-test-id="${testId}"]`;

export const getByTdsTestId = <T extends { locator: (selector: string) => any }>(
  context: T, 
  testId: string
) => {
  return context.locator(getTdsTestIdSelector(testId));
};

export const getDynamicTdsTestId = <T extends { locator: (selector: string) => any }>(
  context: T, 
  prefix: string, 
  entityId: string | number
) => {
  return context.locator(getTdsTestIdSelector(`${prefix}-${entityId}`));
};
```

### 15.4. Unit Test Suite Chuẩn: `projects/demo-crm-fe/libs/demo-core/src/directives/tds-test-id.directive.spec.ts`
```typescript
import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { TdsTestIdDirective } from './tds-test-id.directive';

@Component({
  standalone: true,
  imports: [TdsTestIdDirective],
  template: `
    <button id="static-btn" tdsTestId="auth-login-submit-btn">Login</button>
    <div id="dynamic-row" [tdsTestId]="'customer-row-' + customerId">Row</div>
    <span id="null-span" [tdsTestId]="nullValue">Null</span>
    <span id="empty-span" tdsTestId="   ">Empty</span>
  `,
})
class TestHostComponent {
  public customerId = 10293;
  public nullValue: string | null = null;
}

describe('TdsTestIdDirective', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let component: TestHostComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('nên gán đúng attribute tds-test-id cho static binding', () => {
    const btnEl = fixture.debugElement.query(By.css('#static-btn')).nativeElement;
    expect(btnEl.getAttribute('tds-test-id')).toBe('auth-login-submit-btn');
  });

  it('nên gán đúng attribute tds-test-id cho dynamic binding', () => {
    const rowEl = fixture.debugElement.query(By.css('#dynamic-row')).nativeElement;
    expect(rowEl.getAttribute('tds-test-id')).toBe('customer-row-10293');

    component.customerId = 99999;
    fixture.detectChanges();
    expect(rowEl.getAttribute('tds-test-id')).toBe('customer-row-99999');
  });

  it('không nên render attribute tds-test-id khi giá trị là null hoặc khoảng trắng', () => {
    const nullEl = fixture.debugElement.query(By.css('#null-span')).nativeElement;
    expect(nullEl.hasAttribute('tds-test-id')).toBe(false);

    const emptyEl = fixture.debugElement.query(By.css('#empty-span')).nativeElement;
    expect(emptyEl.hasAttribute('tds-test-id')).toBe(false);
  });
});
```

---

## 1️⃣6️⃣ Kế Hoạch Triển Khai SLPPC Zero-Search (Decomposition Roadmap)

Toàn bộ quy trình triển khai được phân rã thành các gói công việc cụ thể cho từng vai trò trong phòng ban SLPPC:

```text
[Supervisor] ──(Khởi tạo Epic #4255)──► [PM Agent] ──(Kev Thẩm Định 2.49)
                                              │
                                              ▼
                                         [Lead Dev]
                                (Bóc tách Zero-Search Tasks)
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
   [Peer Dev 1]                         [Peer Dev 2]                         [QC Verifier]
 Task 1: Directive & QA Helper       Task 2: Thí điểm Pilot                Task 3: Unit Test & DoD
 libs/demo-core/src/directives/      Login (app-shell) & Customer (crm)    Nghiệm thu độc lập 100%
```

### Chi Tiết Phân Bổ Task:
1. **Task 1 (Peer Dev 1 - Low)**:
   - *Target Files*: `projects/demo-crm-fe/libs/demo-core/src/directives/tds-test-id.directive.ts`, `index.ts`, `libs/demo-core/src/utils/qa-test-helper.ts`.
   - *Nội dung*: Hiện thực hóa directive và QA helpers theo mục 15.1 đến 15.3.
   - *Test Command*: `npx nx build demo-core`.
2. **Task 2 (QC Verifier - Independent Test Architect)**:
   - *Target Files*: `projects/demo-crm-fe/libs/demo-core/src/directives/tds-test-id.directive.spec.ts`.
   - *Nội dung*: Hiện thực hóa test suite theo mục 15.4, kiểm tra static, dynamic, null, undefined, trim space.
   - *Test Command*: `npx jest libs/demo-core/src/directives/tds-test-id.directive.spec.ts`.
3. **Task 3 (Peer Dev 2 - Medium)**:
   - *Target Files*: `projects/demo-crm-fe/apps/app-shell/src/app/pages/account/login/login.component.html`, `projects/demo-crm-fe/apps/mfe-crm/src/app/pages/customer/customer-list/customer-list.component.html`.
   - *Nội dung*: Thí điểm gắn `tdsTestId` cho màn hình đăng nhập và danh sách khách hàng.
   - *AC*: Kiểm tra trên trình duyệt render đúng các attribute `tds-test-id`.
4. **Task 4 (QC Final Sign-Off Gate)**:
   - *Nghiệm thu*: Chạy toàn bộ test suites, kiểm tra anti-leak sentinel, đóng Epic `#4255`.

---

## ✅ Tóm Tắt Ngắn Gọn
* **`tdsTestId`** = Angular API (Frontend).
* **`tds-test-id`** = DOM Testing Contract (QA & Automation).
* **Stable – Readable – Scalable**.
* **FE & QA cùng chịu trách nhiệm** duy trì chất lượng hệ thống.
