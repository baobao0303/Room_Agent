# Đặc tả Kỹ thuật & Giao diện Toàn diện: Phân hệ Quản lý & Ánh xạ Dữ liệu Sự kiện Thô (Event Data Mapping & Projection System)

> **Mã đặc tả:** `SPEC-CDP-RAW-DATA-MAPPING-MASTER`  
> **Nguồn tham chiếu:** Claude Design Artifact `Field mapping UI` (11 Boards: `Main`, `SourceList`, `WebSource`, `WebSource-forms`, `CreateEvent`, `Mapping`, `TestRun`, `Review`, `FbSource`, `FbSource-recent`, `RawData`) kết hợp **UI Wizard 4 bước từ Mockup**.  
> **Phạm vi triển khai:** Micro-frontend `apps/mfe-cdp` (`/cdp/data-raw`), thư viện nghiệp vụ `libs/features/raw-event-data`, Backend `DataExtraction` & `Crm`.  
> **Công nghệ áp dụng:** Angular 18 Standalone, Signals, Reactive Forms, Thư viện component `tds-ui`, Tailwind CSS, Event-Sourcing Pipeline.

---

## 1. Kiến trúc Tổng thể & Hệ thống Điều hướng (System Architecture & Navigation)

Toàn bộ phân hệ Dữ liệu sự kiện thô nằm trong menu **CDP Admin -> Dữ liệu sự kiện** (`/cdp/data-raw`), được phân cấp qua 2 Tab chính ở cấp độ cao nhất:

1. **Tab 1: `Dữ liệu thô` (`RawData.dc.html`)**
   - Giám sát luồng sự kiện thô thời gian thực từ mọi nguồn (Kafka stream `wicx.events.raw.v1` / bảng `cdp.events`).
   - Bộ lọc thời gian, phạm vi Tenant (Hiện tại / Tất cả), lọc theo Nguồn (`Website`, `Facebook`, `Zalo`, `TPOS`, `API`).
   - Bảng dữ liệu thô với tính năng mở rộng dòng xem trực tiếp JSON Payload qua `JsonViewerComponent`, Drawer chi tiết metadata, và Modal so sánh Diff 2 payload.
2. **Tab 2: `Mapping dữ liệu` (`Main.dc.html` & `Mapping.dc.html`)**
   - Quản trị danh mục trang/kênh liên kết (Website, Facebook Page, Zalo OA, POS/API Partner).
   - Cấu hình Wizard 4 bước: (1) Cấu hình chung -> (2) Sự kiện hành vi -> (3) Mapping field -> (4) Hoàn tất.
   - Trình biên tập ánh xạ thuộc tính form/event sang trường chuẩn CDP (`phone`, `email`, `name`, `custom_fields`).
   - Môi trường Chạy thử (Dry Run / Test Run) kiểm tra quy tắc trên dữ liệu mẫu thực tế.
   - Sổ cái kiểm toán lịch sử thay đổi phiên bản (Versioning & Audit Trail).

---

## 2. Bản đồ 11 Màn hình Thiết kế (Artifact Boards Breakdown)

```text
Phân hệ Dữ liệu Sự kiện (/cdp/data-raw)
│
├── [Tab 1] Dữ liệu thô (Board 0: RawData.dc.html)
│     ├── Bảng sự kiện thô (TDS Data Table, phân trang, lọc nguồn)
│     ├── Cột mở rộng hiển thị JsonViewer đa cấp độ
│     ├── Drawer Slide-over xem chi tiết sự kiện & metadata
│     └── Modal Diff so sánh 2 bản ghi payload
│
└── [Tab 2] Mapping dữ liệu (Board 1: Main.dc.html)
      │
      ├── Thành phần dùng chung: Danh sách trang liên kết (Board SourceList.dc.html - Pane trái 320px)
      │     ├── Input tìm kiếm (Tên, site_id, page_id) + Nút lọc
      │     └── Danh sách Connector: TPOS, Facebook, Zalo, Partner API kèm Tag trạng thái
      │
      ├── Màn hình Tổng quan Cần xử lý (Board 1: Main.dc.html - Pane phải mặc định)
      │     ├── Thẻ KPI: Tổng số trang (6) | Cần cấu hình (1) | Trường chưa map (1)
      │     ├── Danh sách việc cần xử lý (Form chưa cấu hình, trường thiếu map)
      │     └── Khối hướng dẫn chọn kênh
      │
      ├── Cụm Nguồn Website (Board 2a, 2b, 2e)
      │     ├── Tab Sự kiện hành vi (Board 2a: WebSource.dc.html)
      │     │     ├── Quy trình 3 bước: Khách ẩn danh -> Khách gửi form -> Nhận diện
      │     │     ├── Bảng 9 sự kiện: Gửi form, Cuộn trang, Click, Xem trang, Giỏ hàng...
      │     │     └── Nút "+ Tạo sự kiện"
      │     ├── Drawer Tạo sự kiện tự định nghĩa (Board 2e: CreateEvent.dc.html - 720px)
      │     │     └── Đặt tên chuẩn CDP, điều kiện kích hoạt (URL, Element ID, CSS Selector)
      │     └── Tab Quản lý Form (Board 2b: WebSource-forms.dc.html)
      │           └── Danh sách form phát hiện: /lien-he, /dang-ky kèm trạng thái mapping
      │
      ├── Cụm Nguồn Fanpage / Zalo (Board 2c, 2d)
      │     ├── Tab Mapping sự kiện Fanpage (Board 2c: FbSource.dc.html)
      │     │     └── Mapping trường tin nhắn, lead form từ webhook Facebook
      │     └── Tab Tin nhắn gần đây (Board 2d: FbSource-recent.dc.html)
      │           └── Giám sát log tương tác chat & payload gần nhất
      │
      ├── Trình Biên tập Mapping Field (Board 3: Mapping.dc.html)
      │     ├── Bảng ma trận ánh xạ 5 cột:
      │     │   [Trường nguồn] | [Giá trị mẫu] | [Trường CDP] | [Quy tắc chuẩn hóa] | [Độ tin cậy]
      │     ├── Thanh phiên bản: Đang chạy · Phiên bản 3 (Tự động tăng phiên bản khi lưu)
      │     └── Nút tác vụ: Lưu thay đổi, Chạy thử, Lịch sử thay đổi
      │
      ├── Màn hình Chạy thử Quy tắc (Board 4: TestRun.dc.html)
      │     ├── Chọn mẫu bản ghi thực tế từ nguồn
      │     └── Bảng đối chiếu Trước (Nguồn) vs Sau (CDP Target) kèm thông báo validate
      │
      └── Màn hình Sổ cái Lịch sử Thay đổi (Board 5: Review.dc.html)
            ├── Danh sách phiên bản (v3, v2, v1) kèm ngày giờ và người thực hiện
            ├── Chi tiết Diff sai khác giữa 2 phiên bản
            └── Nút Khôi phục về phiên bản cũ (Rollback)
```

---

## 3. Đặc tả Chi tiết Màn hình Wizard 4 Bước (Mockup & Main Screen)

Khi chọn một trang liên kết cần thiết lập hoặc tạo mới, giao diện chuyển sang **Wizard 4 bước tuần tự** hiển thị trên Pane phải:

### 3.1. Stepper Wizard
- **Bước 1 - Cấu hình chung (Active):** Khai báo kênh, xác thực endpoint, ánh xạ khóa liên kết và lấy mẫu dữ liệu thô.
- **Bước 2 - Sự kiện hành vi:** Đăng ký các sự kiện hành vi được theo dõi (`pageView`, `formSubmit`, `click`, `orderCreated`, hoặc sự kiện tùy biến).
- **Bước 3 - Mapping field:** Thiết lập ma trận ánh xạ trường dữ liệu form/payload vào hồ sơ khách hàng.
- **Bước 4 - Hoàn tất:** Kiểm tra tổng thể, chạy thử nghiệm xác nhận và kích hoạt pipeline.

---

### 3.2. Bước 1: Cấu hình Chung (General Settings)

#### 1. Header Kênh & Tác vụ
- **Tiêu đề kênh:** Icon logo kênh (TPOS cam, Facebook xanh, Zalo xanh, Partner) + Tên connector (`TPOS - Store VN #01`).
- **Tag trạng thái:**
  - `Đã kết nối`: Màu xanh lá (`tds-tag status="success"`), có chấm tròn trạng thái.
  - `Cần cấu hình`: Màu vàng cam (`tds-tag status="warning"`), có icon tam giác cảnh báo.
- **Thông tin phụ:** `Loại kênh (Web - Website / Social) | Cập nhật lần cuối: YYYY-MM-DD HH:mm:ss`.
- **Nút tác vụ góc phải:**
  - `Làm mới dữ liệu`: Button outline secondary, icon `tdsi-refresh-line`.
  - `Lưu cấu hình`: Button primary cam `#E05206`, icon `tdsi-save-line`.

#### 2. Khối 1: Thông tin Kết nối & Ánh xạ Dữ liệu (Grid 2 Cột)
- **Cột Trái - Thông tin kết nối & Trường khóa:**
  - *Thông tin connector (có sẵn):*
    * `Nguồn dữ liệu`: Dropdown Select (Disabled) - e.g. `Website`.
    * `Tên connector`: Dropdown Select (Disabled) - e.g. `TPOS`.
    * `URL / Endpoint`: Input text (Disabled) - e.g. `https://api.tpos.vn/events`.
  - *Ánh xạ dữ liệu từ JSON (Bắt buộc):*
    * `Channel liên kết *`: Select chọn trường khóa kênh từ payload JSON (e.g. `site_id`, `site`, `domain`).
      - Helper text: `Ví dụ: site_id / site / domain ...`
    * `Channel event type *`: Select chọn trường khóa loại sự kiện (e.g. `data.system_event_type`, `event`, `eventType`).
      - Helper text: `Ví dụ: event / eventtype / event_type ...`
  - *Hộp Alert hướng dẫn:*
    - Khung xanh nhạt `border border-blue-200 bg-blue-50 text-blue-800 rounded-md p-3`.
    - Icon: `tdsi-information-line`.
    - Văn bản: *"Các trường trên sẽ được lấy từ dữ liệu JSON thực tế. Bạn có thể xem mẫu dữ liệu ở bên phải để xác định chính xác tên trường."*
- **Cột Phải - Khung Xem trước JSON Mẫu (JSON Viewer):**
  - Tiêu đề `Xem trước dữ liệu JSON (mẫu)` kèm nút sao chép `tdsi-copy-line` vào clipboard.
  - Trình xem code có số dòng (Line Numbers 1 đến 14):
    ```json
    1  {
    2    "event_id": "evt_000123",
    3    "site_id": "VN001",
    4    "site": "tpos.vn",
    5    "data": {
    6      "system_event_type": "formSubmit",
    7      "user_id": "u12345",
    8      "page_url": "/contact",
    9      "form_id": "contact_001",
    10     "form_value": { ... }
    11   },
    12   "created_at": "2026-10-13T14:19:34Z"
    13 }
    ```

#### 3. Khối 2: Thiết lập Lấy Dữ liệu Thô (Sampling Controls)
- **Khoảng thời gian *:** `tds-date-range-picker` định dạng `dd/MM/yyyy HH:mm` (mẫu: `01/10/2026 00:00 -> 13/10/2026 23:59`).
- **Giới hạn bản ghi *:** Nhóm nút Segmented Radio Group:
  - `500` (viền xám).
  - `1.000` (màu cam primary `#E05206` - Mặc định).
  - `2.000` (viền xám).
  - `Tùy chỉnh` (nhập số thủ công, tối đa 2.000 bản ghi/lần lấy).
- **Nút thực thi:** `Lấy dữ liệu mẫu` (Primary cam, icon `tdsi-play-circle-line`).

#### 4. Khối 3: Bảng Dữ liệu Thô Mẫu (Flattened Sample Table)
- **Thanh trạng thái:** Tag `Đã tải thành công` (`status="success"`), text tóm tắt: `Tổng: 1.000 bản ghi | 12 field`.
- **Bảng TDS Data Table (12 cột làm phẳng tự động từ cấu trúc JSON lồng nhau):**

| # | event_id | site_id | site | data.system_event_type | user_id | page_url | form_id | form_value | created_at | ... |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | `evt_000123` | VN001 | tpos.vn | `formSubmit` | u12345 | /contact | contact_001 | `{...}` | 2026-10-13 14:19:34 | ⋯ |
| **2** | `evt_000124` | VN001 | tpos.vn | `pageView` | u67890 | /product | - | `{}` | 2026-10-13 14:18:12 | ⋯ |
| **3** | `evt_000125` | VN002 | tpos.vn | `click` | u24680 | /home | btn_buy | `{}` | 2026-10-13 14:16:45 | ⋯ |
| **4** | `evt_000126` | VN001 | tpos.vn | `formSubmit` | u13579 | /contact | contact_002 | `{...}` | 2026-10-13 14:15:20 | ⋯ |
| **5** | `evt_000127` | VN003 | tpos.vn | `pageView` | u11223 | /cart | - | `{}` | 2026-10-13 14:12:10 | ⋯ |

---

### 3.3. Bước 2: Sự kiện Hành vi & Tạo Sự kiện Tự định nghĩa (Behavior Events & Custom Event Drawer)
- **Quản lý danh sách sự kiện (`WebSource.dc.html`):**
  - Nhóm sự kiện Tracker gửi về mặc định: `form_submit`, `page_view`, `scroll`, `click`.
  - Nhóm sự kiện tự tạo từ hành vi trang (e.g. `scroll_50_percent`, `click_btn_tu_van`, `view_pricing_page`).
  - Toggle bật/tắt: Cho phép quản trị viên chọn sự kiện nào được phép lưu vào dòng thời gian (Timeline) của khách hàng.
- **Drawer Tạo Sự kiện Tự định nghĩa (`CreateEvent.dc.html` - 720px):**
  - `Tên sự kiện`: Tên hiển thị tiếng Việt (e.g. *"Xem trang bảng giá"*).
  - `Tên chuẩn CDP`: Định danh hệ thống dạng snake_case (e.g. `view_pricing_table`).
  - `Loại sự kiện gốc`: Chọn từ tracker (e.g. `AutoPageView` hoặc `AutoClick`).
  - `Điều kiện kích hoạt (Trigger Rules)`:
    * Khối điều kiện: `Đường dẫn trang (URL) chứa /bang-gia`.
    * Hoặc `Element ID bằng #btn-checkout`.
    * Hỗ trợ toán tử: `chứa`, `bằng`, `bắt đầu bằng`, `kết thúc bằng`, `regex`.
  - `Thuộc tính đính kèm`: Danh sách key-value trích xuất từ DOM hoặc URL parameters.

---

### 3.4. Bước 3: Trình Biên tập Mapping Trường (Field Mapping Matrix - `Mapping.dc.html`)
Màn hình trung tâm thiết lập chuyển đổi từ trường nguồn sang dữ liệu khách hàng CDP:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Tiêu đề: Mapping form: Form đăng ký tư vấn  [ Tag: Đang chạy · phiên bản 3 ]                                     │
│ Metadata: Nguồn WEB-01 · Đường dẫn: /dang-ky · Sự kiện: auto_form_submit_custom · Bản ghi gần nhất: 14/10 08:41   │
│ Nút hành động: [ Lịch sử thay đổi ]  [ Chạy thử ]  [ Lưu thay đổi (Primary) ]                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BẢNG MA TRẬN MAPPING:                                                                                            │
│ ┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────┐ │
│ │ Trường dữ liệu nguồn │ Giá trị mẫu gần nhất │ Trường CDP           │ Quy tắc chuẩn hóa    │ Mức tin cậy      │ │
│ ├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────┤ │
│ │ form.tds-input-1     │ "0969733325"         │ [ phone          v ] │ [ CH-SDT         v ] │ [ Cao        v ] │ │
│ │ form.tds-input-2     │ "Tấn "               │ [ name           v ] │ [ CH-TEN         v ] │ [ Cao        v ] │ │
│ │ form.tds-input-3     │ "tan@example.com"    │ [ email          v ] │ [ CH-EMAIL       v ] │ [ Cao        v ] │ │
│ │ form.tds-input-4     │ "Hà Nội"             │ [ custom_attr... v ] │ [ Không áp dụng  v ] │ [ Trung bình v ] │ │
│ └──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Quy tắc Chuẩn hóa Dữ liệu (Normalization Pipes)
1. **`CH-SDT` (Chuẩn hóa Số điện thoại):**
   - Chuyển đổi mọi đầu số hợp lệ tại Việt Nam (`09x`, `03x`, `07x`, `08x`, `84x`) về chuẩn quốc tế E.164 (`+84xxxxxxxxx`).
   - Loại bỏ toàn bộ khoảng trắng, dấu gạch nối, dấu chấm. Bỏ qua giá trị nếu không đủ từ 9 đến 11 số.
2. **`CH-EMAIL` (Chuẩn hóa Email):**
   - Chuyển toàn bộ về ký tự thường (lowercase), loại bỏ khoảng trắng đầu/cuối (`trim`).
   - Kiểm tra định dạng theo chuẩn RFC 5322 regex.
3. **`CH-TEN` (Chuẩn hóa Họ tên):**
   - Xóa khoảng trắng thừa giữa các từ, viết hoa chữ cái đầu từng từ (Title Case).
4. **`Không áp dụng`:** Giữ nguyên giá trị chuỗi gốc.

#### Mức Tin cậy Định danh (Identity Confidence Level)
- **`Cao` (High):** Trường được xác thực qua OTP hoặc nhập trực tiếp từ form chính thống -> Có quyền ghi đè hoặc hợp nhất hồ sơ khách hàng.
- **`Trung bình` (Medium):** Trường trích xuất gián tiếp hoặc tự động điền -> Chỉ cập nhật nếu hồ sơ hiện tại đang rỗng.
- **`Thấp` (Low):** Dữ liệu thu thập từ kênh ngoài không có xác thực -> Chỉ lưu dạng thuộc tính phụ, không dùng để gộp định danh.

---

### 3.5. Bước 4: Chạy thử & Xác nhận (Test Run & Review - `TestRun.dc.html`, `Review.dc.html`)
1. **Chạy thử (`TestRun.dc.html`):**
   - Người dùng chọn 1 trong 5 bản ghi mẫu thu thập gần nhất.
   - Hệ thống chạy mô phỏng quy tắc ánh xạ và hiển thị bảng so sánh Trước vs Sau:
     * Cột Nguồn: `form.tds-input-1 = "0969733325"`.
     * Cột Đích: `phone = "+84969733325"`.
     * Kết quả: Tag xanh `Khớp chuẩn E.164, liên kết với Hồ sơ KH #KH-09823`.
2. **Sổ cái Lịch sử Thay đổi (`Review.dc.html`):**
   - Ghi lại toàn bộ phiên bản (Version Audit).
   - Mỗi lần bấm "Lưu thay đổi", hệ thống tự động tăng phiên bản (`Phiên bản 3` -> `Phiên bản 4`).
   - Hiển thị ai sửa, lúc mấy giờ, trường nào đổi từ gì sang gì.
   - Nút `Khôi phục phiên bản`: Cho phép hoàn tác về bất kỳ phiên bản nào trong quá khứ.

---

## 4. Mô hình Dữ liệu TypeScript (Core Data Models)

```typescript
/** Đại diện 1 kênh kết nối bên Pane trái */
export interface ChannelConnectorSummary {
  id: string;
  name: string;
  channelType: 'website' | 'facebook' | 'zalo' | 'partner_api';
  categoryLabel: string;
  status: 'connected' | 'needs_config' | 'disconnected';
  lastUpdatedAt: string;
  endpointUrl: string;
  icon: string;
}

/** Cấu hình Bước 1: Cấu hình chung */
export interface GeneralMappingConfigDto {
  connectorId: string;
  sourceType: string;
  connectorName: string;
  endpointUrl: string;
  channelKeyPath: string;      // e.g. "site_id"
  eventTypeKeyPath: string;    // e.g. "data.system_event_type"
  sampleFilter: {
    startDate: string;
    endDate: string;
    recordLimit: 500 | 1000 | 2000 | number;
  };
  sampleJsonPayload?: Record<string, unknown>;
  flattenedRows?: Array<Record<string, unknown>>;
}

/** Cấu hình Bước 2: Sự kiện hành vi */
export interface BehaviorEventConfigDto {
  id: string;
  name: string;
  cdpEventCode: string;        // e.g. "form_submit", "page_view"
  origin: 'tracker' | 'custom';
  trackerCode?: string;        // e.g. "AutoFormSubmit"
  description: string;
  properties: string[];        // e.g. ["form_destination", "element_id"]
  isSavedToCdp: boolean;
  triggerRules?: Array<{
    field: string;
    operator: 'contains' | 'equals' | 'starts_with' | 'regex';
    value: string;
  }>;
}

/** Cấu hình Bước 3: Ma trận Ánh xạ Trường */
export interface FieldMappingRuleDto {
  id: string;
  sourceFieldName: string;     // e.g. "form.tds-input-1"
  sampleValue: string;         // e.g. "0969733325"
  targetCdpField: 'phone' | 'name' | 'email' | 'custom_attributes' | 'none';
  customAttributeKey?: string;
  normalizationRule: 'CH-SDT' | 'CH-EMAIL' | 'CH-TEN' | 'none';
  confidenceLevel: 'Cao' | 'Trung bình' | 'Thấp';
}

/** Hồ sơ phiên bản Mapping */
export interface MappingVersionRecordDto {
  version: number;
  formId: string;
  formName: string;
  status: 'active' | 'archived';
  updatedAt: string;
  updatedBy: string;
  rules: FieldMappingRuleDto[];
}
```

---

## 5. Danh mục Tiêu chí Chấp thuận (Acceptance Criteria Matrix)

| Mã AC | Khu vực | Mô tả Tiêu chí Nghiệm thu |
|---|---|---|
| **AC-NAV-01** | Navigation | Người dùng bấm tab "Mapping dữ liệu" chuyển trạng thái active viền cam, hiển thị Stepper 4 bước và Master-Detail layout. |
| **AC-SRC-01** | Pane Trái | Tìm kiếm tức thì trong danh sách kênh theo tên, `site_id`, `page_id`. Chọn một kênh sẽ cập nhật tiêu đề và toàn bộ dữ liệu Pane phải. |
| **AC-WIZ-01** | Bước 1 | Cho phép chọn `Channel liên kết *` và `Channel event type *` trực tiếp từ danh mục trường quét được từ JSON mẫu. |
| **AC-WIZ-02** | Bước 1 | Khung xem trước JSON mẫu hiển thị đầy đủ số dòng từ 1..14, nút Copy sao chép thành công chuỗi JSON vào clipboard. |
| **AC-WIZ-03** | Bước 1 | Chọn khoảng thời gian và số lượng bản ghi (500, 1000, 2000), bấm "Lấy dữ liệu mẫu" hiển thị loading và trả về bảng phẳng 12 cột. |
| **AC-EVT-01** | Bước 2 | Hiển thị bảng 9 loại sự kiện hành vi. Cho phép bật/tắt lưu sự kiện vào dòng thời gian khách hàng. |
| **AC-EVT-02** | Bước 2 | Mở Drawer 720px "Tạo sự kiện" cho phép tạo sự kiện tự định nghĩa với các điều kiện URL/Element Selector. |
| **AC-MAP-01** | Bước 3 | Bảng ma trận 5 cột cho phép gán trường nguồn sang trường CDP (`phone`, `name`, `email`, `custom_attributes`, `Không lưu`). |
| **AC-MAP-02** | Bước 3 | Áp dụng quy tắc chuẩn hóa `CH-SDT` tự động format số điện thoại sang chuẩn E.164 (`+84...`). |
| **AC-TEST-01**| Bước 4 | Màn hình Chạy thử cho phép chọn bản ghi thực tế, hiển thị bảng so sánh Trước vs Sau khi mapping để người dùng kiểm chứng. |
| **AC-VER-01** | Phiên bản | Bấm "Lưu thay đổi" tự động tăng phiên bản (v3 -> v4), hiển thị thông báo thành công và ghi sổ cái lịch sử tại `Review.dc.html`. |

---

## 6. Kế hoạch Phân rã Công việc Triển khai (SLPC Breakdown)

1. **Supervisor**:
   - Giám sát phạm vi, đảm bảo luồng tuân thủ thiết kế từ 11 board artifact và mockup người dùng cung cấp.
2. **Lead Dev**:
   - Khởi tạo kiến trúc module `data-raw-mapping` trong `apps/mfe-cdp`.
   - Xây dựng Store quản lý state Wizard 4 bước và State 11 Boards (`RawDataMappingStore`).
   - Xây dựng HTTP Client DTO kết nối API Ingestion/Projection.
3. **Peer Dev**:
   - Cài đặt `ChannelConnectorListComponent` (Pane trái 320px).
   - Cài đặt `GeneralMappingConfigComponent` (Bước 1: Form 2 cột, JSON viewer, Sampling controls, Bảng phẳng 12 cột).
   - Cài đặt `BehaviorEventListComponent` & `CreateEventDrawerComponent` (Bước 2).
   - Cài đặt `FieldMappingEditorComponent` (Bước 3: Bảng ma trận 5 cột, dropdown chuẩn hóa).
   - Cài đặt `MappingTestRunComponent` & `MappingVersionHistoryComponent` (Bước 4 & Lịch sử).
4. **QC**:
   - Kiểm thử Unit Test 5 giai đoạn cho bộ chuẩn hóa regex (`CH-SDT`, `CH-EMAIL`, `CH-TEN`).
   - Kiểm thử UI trên các breakpoint 1366x768, 1440x900, 1920x1080.
   - Kiểm thử luồng E2E: Chọn kênh -> Lấy mẫu JSON -> Map field -> Test run -> Lưu phiên bản.
