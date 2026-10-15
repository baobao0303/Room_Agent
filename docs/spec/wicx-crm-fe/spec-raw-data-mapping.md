# Đặc tả Kỹ thuật & Giao diện: Màn hình Cấu hình Ánh xạ Dữ liệu (Raw Data Mapping Wizard)

> **Mã đặc tả:** `SPEC-CDP-RAW-DATA-MAPPING-UI-01`  
> **Tham chiếu thiết kế:** UI Mockup `Mapping dữ liệu` (Wizard 4 bước, 2-Pane Layout, TDS UI Component System)  
> **Vị trí màn hình:** `mfe-cdp` route `/cdp/data-raw` (Tab: "Mapping dữ liệu")  
> **Component chủ đạo:** `RawDataMappingComponent`, `ChannelConnectorListComponent`, `MappingGeneralConfigComponent`, `RawDataSampleTableComponent`  
> **Thư viện UI áp dụng:** `tds-ui` (Tabs, Steps, DataTable, Input, Select, Button, Tag, Alert/Message, DatePicker)

---

## 1. Tổng quan Kiến trúc Giao diện (Layout Overview)

Giao diện được thiết kế theo mô hình **Master-Detail (2-Pane Layout)** kết hợp **Wizard 4 bước tuần tự**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Tabs chính: [ Dữ liệu thô ]  [ Mapping dữ liệu (ACTIVE) ]                                                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Stepper (Wizard):  (1) Cấu hình chung ─────── (2) Sự kiện hành vi ─────── (3) Mapping field ─────── (4) Hoàn tất       │
├─────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┤
│ Pane Trái: Danh sách kết nối    │ Pane Phải: Chi tiết Cấu hình theo Kênh đã chọn                                       │
│                                 │ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ - Ô tìm kiếm kênh + Bộ lọc      │ │ Header Kênh: [TPOS - Store VN #01] [Tag: Đã kết nối]  [Làm mới]  [Lưu cấu hình]   │ │
│ - Danh sách Connector:          │ │ Sub-info: Web - Website | Cập nhật: 2026-10-13 14:19:34                         │ │
│   * TPOS - Store VN #01 (Active)│ │ Sub-tabs: [ Cấu hình chung ]  [ Sự kiện hành vi ]                                │ │
│   * TPOS - Store HCM #02        │ ├────────────────────────────────────────┬─────────────────────────────────────────┤ │
│   * TPOS - Store ĐN #03 (Cảnhbáo│ │ 1. Thông tin kết nối & ánh xạ dữ liệu  │ Xem trước dữ liệu JSON (mẫu)            │ │
│   * Facebook (Social)           │ │ - Nguồn dữ liệu: Website / TPOS        │ { "event_id": "evt_000123",             │ │
│   * Zalo (Social)               │ │ - Endpoint: https://api.tpos.vn/events │   "site_id": "VN001",                   │ │
│   * Partner A / B (API)         │ │ - Ánh xạ Channel: site_id              │   "data": { "system_event_type": ... }  │ │
│                                 │ │ - Ánh xạ Event Type: data.system_event │ } [Copy JSON]                           │ │
│                                 │ ├────────────────────────────────────────┴─────────────────────────────────────────┤ │
│                                 │ │ 2. Thiết lập lấy dữ liệu thô                                                     │ │
│                                 │ │ - Khoảng thời gian: [ 01/10/2026 00:00 -> 13/10/2026 23:59 ]                     │ │
│                                 │ │ - Giới hạn bản ghi: (500) [1.000 - Active] (2.000) (Tùy chỉnh) [> Lấy mẫu]        │ │
│                                 │ ├──────────────────────────────────────────────────────────────────────────────────┤ │
│                                 │ │ Dữ liệu thô mẫu: [Tag: Đã tải thành công] (Tổng: 1.000 bản ghi | 12 field)        │ │
│                                 │ │ [ Bảng TDS DataTable: event_id | site_id | site | data.system_event_type | ... ] │ │
│                                 │ └──────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Đặc tả Chi tiết Các Vùng Giao diện

### 2.1. Thanh Stepper Wizard 4 Bước (Top Stepper)
- **Vị trí:** Ngay dưới thanh tab điều hướng chính (`Dữ liệu thô` / `Mapping dữ liệu`).
- **4 Bước tiến trình:**
  1. `(1) Cấu hình chung` (Active): Khai báo nguồn dữ liệu, kết nối kênh, endpoint và lấy mẫu JSON payload thô.
  2. `(2) Sự kiện hành vi`: Phân loại và đăng ký các loại sự kiện (`pageView`, `formSubmit`, `click`, `orderCreated`).
  3. `(3) Mapping field`: Ánh xạ trực quan từng trường JSON sang định danh Contact (Phone, Email, UID) và Profile/Custom fields.
  4. `(4) Hoàn tất`: Tổng kết quy tắc ánh xạ, kiểm tra tính hợp lệ và kích hoạt (Activate Pipeline & Backfill).
- **Hành vi tương tác:**
  - Bước hiện tại có badge số vòng tròn màu cam (`#E05206` / `tds-color-primary`), văn bản in đậm.
  - Các bước sau ở trạng thái chờ (`disabled`/chưa cho click nhảy cóc khi chưa cấu hình xong bước trước).

### 2.2. Pane Trái: Danh sách Kênh Kết nối (`ChannelConnectorListComponent`)
- **Độ rộng:** Cố định `300px` - `340px`, viền phải `1px border-solid tds-color-border-secondary`.
- **Thanh tìm kiếm & Lọc:**
  - Input tìm kiếm (`TDSInputSearch`): Placeholder `"Tìm kiếm kênh liên kết..."`.
  - Nút icon lọc (`tds-button-outline-icon` với icon `tdsi-filter-line`).
- **Danh sách Connector Card:**
  - Mỗi item hiển thị:
    * Icon đại diện kênh: TPOS (icon cam), Facebook (icon xanh fb), Zalo (icon xanh zalo), Partner API (icon đối tác).
    * Tiêu đề: Tên kết nối (e.g. `TPOS - Store VN #01`).
    * Phụ đề: Loại kết nối (e.g. `Web - Website`, `Social - Facebook`, `Partner - API`).
    * Trạng thái kết nối (`TDSTag`):
      - `Đã kết nối`: Tag màu xanh lá (`status="success"`), có chấm icon trạng thái.
      - `Cần cấu hình`: Tag màu vàng cam cảnh báo (`status="warning"`), icon tam giác cảnh báo.
    * Mũi tên điều hướng `tdsi-chevron-right-line`.
  - Item được chọn có nền `tds-color-primary-minimalist` và viền viền trái/khung màu primary.

### 2.3. Pane Phải - Header Tác vụ Kênh
- **Tiêu đề kênh:** Icon logo + Tên connector (`TPOS - Store VN #01`) + Tag trạng thái `Đã kết nối`.
- **Thông tin phụ:** `Web - Website | Cập nhật: 2026-10-13 14:19:34`.
- **Nhóm nút tác vụ góc phải:**
  - Nút `Làm mới dữ liệu`: `button tds-button-outline color="secondary"`, icon `tdsi-refresh-line`.
  - Nút `Lưu cấu hình`: `button tds-button color="primary"` (màu cam), icon `tdsi-save-line`.
- **Tab con:** `Cấu hình chung` (Active) và `Sự kiện hành vi`.

### 2.4. Khối 1: Thông tin Kết nối & Ánh xạ Dữ liệu (Grid 2 Cột)

#### Cột Trái: Cấu hình Khóa & Endpoint
1. **Thông tin connector (Read-only / cấu hình sẵn):**
   - `Nguồn dữ liệu`: Dropdown Select chọn kênh (e.g. `Website`, `POS`, `App`).
   - `Tên connector`: Dropdown Select chọn connector cụ thể (e.g. `TPOS`).
   - `URL / Endpoint`: Input văn bản readonly: `https://api.tpos.vn/events`.
2. **Ánh xạ dữ liệu từ JSON (Trường khóa bắt buộc):**
   - `Channel liên kết *`: Select chọn trường định danh cửa hàng/kênh từ payload (e.g. `site_id`, `site`, `domain`). Gợi ý dưới chân: `"Ví dụ: site_id / site / domain ..."`.
   - `Channel event type *`: Select chọn trường định danh loại sự kiện (e.g. `data.system_event_type`, `event`, `eventType`). Gợi ý dưới chân: `"Ví dụ: event / eventtype / event_type ..."`.
3. **Alert Box hướng dẫn (TDS Alert info):**
   - Nền xanh nhạt, icon thông tin `tdsi-information-line`:
   - Nội dung: *"Các trường trên sẽ được lấy từ dữ liệu JSON thực tế. Bạn có thể xem mẫu dữ liệu ở bên phải để xác định chính xác tên trường."*

#### Cột Phải: Xem trước Dữ liệu JSON Mẫu (JSON Sample Viewer)
- Tiêu đề: `Xem trước dữ liệu JSON (mẫu)` kèm nút sao chép `tdsi-copy-line`.
- Hộp hiển thị code JSON với số dòng (Line Numbers: 1 đến 14):
  ```json
  {
    "event_id": "evt_000123",
    "site_id": "VN001",
    "site": "tpos.vn",
    "data": {
      "system_event_type": "formSubmit",
      "user_id": "u12345",
      "page_url": "/contact",
      "form_id": "contact_001",
      "form_value": { ... }
    },
    "created_at": "2026-10-13T14:19:34Z"
  }
  ```

### 2.5. Khối 2: Thiết lập Lấy Dữ liệu Thô
- **Khoảng thời gian *:**
  - Date Range Picker với định dạng `dd/MM/yyyy HH:mm` (mẫu: `01/10/2026 00:00 -> 13/10/2026 23:59`).
- **Giới hạn bản ghi *:**
  - Nhóm nút Segmented Radio: `500` | `1.000` (mặc định chọn màu cam) | `2.000` | `Tùy chỉnh`.
  - Chú thích: *"Tối đa 2.000 bản ghi/lần lấy."*
- **Nút hành động:**
  - Nút `Lấy dữ liệu mẫu`: `button tds-button color="primary"`, icon `tdsi-play-circle-line` / `tdsi-download-line`.

### 2.6. Khối 3: Bảng Dữ liệu Thô Mẫu (Flattened Raw Sample Table)
- **Thanh trạng thái bảng:**
  - Tag trạng thái: `Đã tải thành công` (màu xanh lá).
  - Tóm tắt số lượng: `Tổng: 1.000 bản ghi | 12 field`.
- **TDS Data Table (Cột tự động làm phẳng từ JSON):**
  - Cột `#`: Số thứ tự dòng.
  - Cột `event_id`: ID sự kiện (e.g. `evt_000123`, `evt_000124`).
  - Cột `site_id`: Mã cửa hàng/site (e.g. `VN001`, `VN002`).
  - Cột `site`: Tên miền (e.g. `tpos.vn`).
  - Cột `data.system_event_type`: Loại hành vi (e.g. `formSubmit`, `pageView`, `click`).
  - Cột `user_id`: ID người dùng (e.g. `u12345`, `u67890`).
  - Cột `page_url`: Đường dẫn trang (e.g. `/contact`, `/product`, `/home`).
  - Cột `form_id`: ID biểu mẫu (e.g. `contact_001`, `btn_buy`, `-`).
  - Cột `form_value`: Chi tiết giá trị biểu mẫu `{...}`.
  - Cột `created_at`: Thời điểm tạo `2026-10-13 14:19:34`.
  - Cột `...`: Menu thao tác mở rộng.

---

## 3. Data Contracts & State Model (Frontend mfe-cdp)

```typescript
export interface ChannelConnectorItem {
  id: string;
  name: string;
  channelType: 'website' | 'facebook' | 'zalo' | 'partner_api';
  categoryLabel: string; // e.g. "Web - Website", "Social - Facebook"
  status: 'connected' | 'needs_config' | 'disconnected';
  lastUpdatedAt: string;
  endpointUrl: string;
  iconType: string;
}

export interface GeneralMappingConfigDto {
  connectorId: string;
  channelKeyField: string;        // e.g. "site_id"
  channelEventTypeField: string;   // e.g. "data.system_event_type"
  timeRange: {
    startDate: string;
    endDate: string;
  };
  sampleRecordLimit: 500 | 1000 | 2000 | number;
  samplePayload?: Record<string, unknown>;
  flattenedSampleRows?: Array<Record<string, unknown>>;
}
```

---

## 4. Tiêu chí Chấp thuận (Acceptance Criteria)

| Mã AC | Tiêu chí nghiệm thu |
|---|---|
| **AC-MAP-01** | Khi vào tab "Mapping dữ liệu", hiển thị danh sách kênh bên trái và mặc định chọn kênh đầu tiên. |
| **AC-MAP-02** | Chọn một kênh khác trên pane trái sẽ cập nhật toàn bộ thông tin cấu hình, endpoint và mẫu JSON tương ứng bên phải. |
| **AC-MAP-03** | Khung JSON mẫu hỗ trợ nút copy vào clipboard và hiển thị đúng định dạng JSON có số dòng. |
| **AC-MAP-04** | Nhấn "Lấy dữ liệu mẫu" gọi API lấy danh sách bản ghi theo khoảng thời gian và giới hạn đã chọn, hiển thị bảng phẳng dữ liệu mẫu. |
| **AC-MAP-05** | Dropdown "Channel liên kết" và "Channel event type" cho phép chọn trực tiếp từ danh sách các trường quét được từ JSON mẫu. |
| **AC-MAP-06** | Nhấn "Lưu cấu hình" xác thực các trường có dấu `*` và lưu draft thành công qua `TDSMessageService.success`. |
