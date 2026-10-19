# ĐẶC TẢ YÊU CẦU PHẦN MỀM: CDP ADMIN - MAPPING DỮ LIỆU SỰ KIỆN (FIELD MAPPING UI)
> **Mã tài liệu**: `SPEC-CDP-MAPPING-2026-V1`  
> **Nguồn thiết kế**: `Field mapping UI.pdf` (9 trang)  
> **Module mục tiêu**: `projects/wicx-crm-fe/apps/mfe-cdp` (Angular 18, Standalone, TDS UI)  
> **Ngày phê duyệt**: 2026-10-19  

---

## 1. TỔNG QUAN HỆ THỐNG & MỤC TIÊU (OVERVIEW & GOALS)

Hệ thống **CDP Admin - Dữ liệu sự kiện (Mapping dữ liệu)** cung cấp bộ công cụ trực quan cho quản trị viên cấu hình ánh xạ dữ liệu thu thập từ các kênh liên kết (Website, CRM nội bộ CentralFlow, Facebook Page, Zalo OA) vào kho dữ liệu khách hàng tập trung (CDP Profile).

### Mục tiêu cốt lõi:
1. **Theo dõi tổng thể**: Báo cáo lưu lượng sự kiện thu thập được theo từng trang và nguồn kết nối trong chu kỳ 30 - 180 ngày.
2. **Chuẩn hóa cấu hình JSON**: Ánh xạ linh hoạt các trường dữ liệu thô (`site_id`, `system_event_type`, `event_id`, `received_at`) từ JSON payload sang thực thể CDP.
3. **Quản lý hành vi & Form mapping**: Kiểm soát loại sự kiện nào được phép ghi nhận vào Hồ sơ khách hàng; cấu hình quy tắc chuẩn hóa định dạng (SĐT, Họ tên, Email) và độ tin cậy của dữ liệu form.
4. **Quản lý phiên bản cấu hình (Version Control)**: Lưu trữ lịch sử thay đổi cấu hình, hiển thị so sánh chênh lệch (Diff) giữa các phiên bản và hỗ trợ khôi phục phiên bản cũ an toàn 1-click.

---

## 2. ĐIỀU HƯỚNG & CẤU TRÚC PHÂN CẤP (NAVIGATION ARCHITECTURE)

```
CDP Admin
├── Tổng quan
├── Hồ sơ khách hàng
├── Dữ liệu sự kiện
│   ├── [Tab 1] Dữ liệu thô (Raw Events List)
│   └── [Tab 2] Mapping dữ liệu (Field Mapping UI)  <-- PHẠM VI TÀI LIỆU NÀY
│       ├── 1. Màn hình Tổng quan sự kiện nhận về
│       ├── 2. Màn hình Cấu hình chung trang liên kết (CRM / Website / Fanpage / Zalo)
│       ├── 3. Màn hình Cấu hình Sự kiện hành vi & Mapping Form
│       └── 4. Màn hình Lịch sử thay đổi mapping & Khôi phục phiên bản
├── Từ điển dữ liệu
├── Quy tắc
├── Hàng chờ xử lý
└── Lịch sử thay đổi
```

---

## 3. CHI TIẾT CÁC MÀN HÌNH CHỨC NĂNG (SCREEN SPECIFICATIONS)

### 3.1. Màn hình 1: Tổng quan sự kiện nhận về (Overview Dashboard)
*Tham chiếu: Trang 1 & Trang 6 trong tài liệu PDF*

#### A. Khối KPI Tổng quan (Header Stat Cards):
1. **Tổng sự kiện nhận về**: Hiển thị tổng số lượng sự kiện ghi nhận (VD: `9.737`).
2. **Trang liên kết đang nhận**: Tỷ lệ trang đang hoạt động bình thường (VD: `4 / 4`).
3. **Khách đã nhận diện**: Số lượng khách hàng được nhận diện (có SĐT, Email hoặc Social ID gộp vào hồ sơ; VD: `549`).
4. **Bộ lọc thời gian**: Dropdown chọn khung thời gian (30 ngày qua, 90 ngày qua, 180 ngày qua).

#### B. Khối Danh sách Trang liên kết (Sidebar trái):
- Ô tìm kiếm: Tìm theo tên, `site_id`, `page_id`.
- Nhóm **CENTRALFLOW (NỘI BỘ)**:
  - `CRM` (Website · CRM) | Badge: `✔ Đang nhận`
- Nhóm **MẠNG XÃ HỘI**:
  - `TMT 1` (Facebook Page · Page ID: 547851926310482) | Badge: `✔ Đang nhận`
  - `TMT 2` (Facebook Page · Page ID: 1322815864251565) | Badge: `✔ Đang nhận`
  - `TMT 1` (Zalo OA · Zalo ID: 1838472937455621204) | Badge: `✔ Đang nhận`

#### C. Bảng Thống kê chi tiết theo Trang liên kết (Main Content):
- Cột:
  1. `Trang liên kết` (Tên trang, loại kết nối)
  2. `Sự kiện nhận về` (Số lượng số nguyên có format dấu chấm)
  3. `Khách đã nhận diện` (Số lượng hồ sơ đã merge)
  4. `Nhận gần nhất` (Thời gian ngày/tháng/giờ:phút)
- Ghi chú chân trang: *"Khách đã nhận diện: khách có SĐT, email hoặc ID mạng xã hội để gộp vào hồ sơ. CRM đang là 0 vì form CentralFlow hiện chưa gửi giá trị khách điền."*

---

### 3.2. Màn hình 2: Chi tiết Cấu hình chung Trang liên kết (General Configuration)
*Tham chiếu: Trang 2, Trang 4 & Trang 5 trong tài liệu PDF*

#### A. Thanh tiến trình Stepper (4 bước):
- Bước 1: `Chưa cấu hình`
- Bước 2: `Đã cấu hình chung`
- Bước 3: `Đang mapping` (VD: `0/2 form đã map xong`)
- Bước 4: `Hoàn tất`

#### B. Thanh Tab điều hướng con:
- `[Tab] Cấu hình chung` (Active)
- `[Tab] Sự kiện hành vi (4)`
- `[Tab] Lịch sử hoạt động`

#### C. Khối 1: Thông tin kết nối & Ánh xạ dữ liệu (Form & Table):
1. **Thông tin kết nối**:
   - `Nguồn dữ liệu *`: Dropdown chọn loại nguồn (Website, Mobile App, Server-to-Server).
   - `Tên trang liên kết *`: Dropdown/Input tên trang liên kết (VD: `CentralFlow`).
2. **Bảng Ánh xạ dữ liệu từ JSON**:
   - Định cấu hình khớp các trường khóa bắt buộc:
     | Tên trong CDP * | Lấy từ trường JSON * | Hành động |
     | :--- | :--- | :--- |
     | `Trang liên kết` (Khóa định danh nguồn) | `site_id` | Khóa cố định (Lock icon) |
     | `Loại sự kiện` (Xem trang, click, gửi form) | `data.system_event_type` | Khóa cố định (Lock icon) |
     | `Mã sự kiện` | `event_id` | Dropdown chọn path JSON / Nút xóa |
     | `Thời gian nhận` | `received_at` | Dropdown chọn path JSON / Nút xóa |
   - Nút hành động: `+ Thêm trường`.
   - Nút lưu: `[Lưu cấu hình]` góc phải trên.
3. **Khối Xem trước dữ liệu JSON mẫu (Sample JSON Payload Preview) & Tương tác Trường (Field Selection & Copy)**:
   - Hiển thị bản ghi JSON gần nhất gửi từ client/webhook bằng component `wicx-json-viewer`:
   ```json
   {
     "event_id": "5f0e7a12-6b30-43d4-bcea-69581db3e60e",
     "event_name": "auto_form_submit_custom",
     "event_time": "2026-08-13T09:02:10.420Z",
     "site_id": "CRM",
     "visitor_id": "0a7f33c1-f105-46ff-a6a9-7d2ae7d7459d",
     "session_id": "74840eb7-e953-421b-9bb4-737fa144b057",
     "data": {
       "current_url": "https://[tên-miền-CRM]/lien-he.html",
       "system_event_type": "AutoFormSubmit"
     },
     "received_at": "2026-08-13T09:02:11Z"
   }
   ```
   - **Tương tác sao chép & Bôi đen văn bản (Text Selection, Copy Path & Copy Value - Bug #1173)**:
     - **Bôi đen tự do (Highlight Text Selection - `AC-MAP-09`)**: Người dùng có thể quét bôi đen chuột bất kỳ key (`"event_id"`, `"data"`, `"system_event_type"`) hoặc value (`"AutoFormSubmit"`) để copy bằng `Ctrl+C` mà không bị chặn bởi `user-select: none`.
     - **1-Click Copy JSON Path (`button.segment-copy-path-btn` - đặt ngay cạnh Key, trước dấu `:` - `AC-MAP-10` & Bug `#1173`)**: Nút thao tác nhanh đặt sát bên phải nhãn khóa (`.segment-key` / `.segment-label`) để copy chính xác đường dẫn phân cấp (Dot/Bracket notation, ví dụ: `data.system_event_type`, `data.current_url`, `items[0].id`). Hiển thị nhãn `Copy path` (tooltip `Copy path: <path>`) khi hover và chuyển sang badge xác nhận rõ ràng `Đã chép path` (tooltip `Đã chép path: <path>`) sau khi bấm.
     - **1-Click Copy JSON Value (`button.segment-copy-value-btn` - đặt ngay cạnh Value - Bug `#1173`)**: Nút thao tác nhanh đặt sát bên phải giá trị trường (`.segment-preview-container` / `.segment-value`) để sao chép trực tiếp giá trị thực (ví dụ: `https://crm.example.com/lien-he.html`, `5f0e7a12-6b30-43d4-bcea-69581db3e60e`, `AutoFormSubmit` không bọc dấu nháy kép thừa). Hiển thị nhãn `Copy value` (tooltip `Copy value: <value>`) khi hover và chuyển sang badge xác nhận rõ ràng `Đã chép giá trị` (tooltip `Đã chép giá trị: <value>`) sau khi bấm.
     - **Copy toàn bộ Payload**: Nút `[Copy Payload]` góc trên bên phải để sao chép toàn bộ chuỗi JSON format chuẩn.

#### D. Khối 2: Dữ liệu trả về sau cấu hình (Live Event Preview Table):
- Bảng nạp 10 bản ghi mới nhất hiển thị realtime theo cấu hình đã map:
  - Cột: `Trang liên kết`, `Loại sự kiện`, `Mã sự kiện`, `Thời gian nhận`.
  - Phân trang chuẩn: `Hiển thị 1-10 trên 7.505 bản ghi` + Bộ nút trang `[1] [2] ... [751]`.

---

### 3.3. Màn hình 3: Cấu hình Sự kiện hành vi & Mapping Form (Behavior & Form Mapping)
*Tham chiếu: Trang 3 & Trang 7 trong tài liệu PDF*

#### A. Danh sách Sự kiện hành vi nhận về:
Bảng bật/tắt quyền lưu trữ sự kiện vào Hồ sơ khách hàng:
| Tên sự kiện | Loại sự kiện | Số lượt | Ý nghĩa | Lưu vào Hồ sơ KH |
| :--- | :--- | :--- | :--- | :---: |
| Gửi form | `AutoFormSubmit` | 8 | Khách gửi form. Trường trong form được map vào hồ sơ khách. | Checkbox (Checked) |
| Xem trang | `PageView` | 3.281 | Khách xem một trang. Trang bài viết có thêm thông tin bài. | Checkbox (Checked) |
| Nhấp chuột | `AutoClick` | 2.089 | Khách bấm vào link hoặc nút. | Checkbox (Checked) |
| Tỷ lệ đọc trang | `ScrollDepth` | 711 | Tracker gửi 4 mốc 25/50/75/100%. Chỉ lưu mốc 50% và 100%. | Checkbox (Checked) |

- Nút hành động: `[✔ Hoàn tất cấu hình]`.

#### B. Khối Danh sách Form đã ghi nhận:
Hiển thị danh sách các web form mà tracker CDP đã phát hiện:
1. **Form liên hệ**:
   - Đường dẫn: `/lien-he.html` · Mã: `FORM-01` · Gửi gần nhất: `05/08 07:16` · Quy mô: `4 trường`.
   - Nút: `[Cấu hình mapping]`.
2. **Form đăng ký dùng thử**:
   - Đường dẫn: `/dang-ky-dung-thu.html` · Mã: `FORM-02` · Gửi gần nhất: `10/08 04:33` · Quy mô: `3 trường`.
   - Nút: `[Cấu hình mapping]`.

#### C. Màn hình Con: Chi tiết Mapping Form liên hệ:
*Khi bấm [Cấu hình mapping]*:
- Nút điều hướng: `‹ Quay lại`.
- Thông tin header: `Nguồn WEB-01 · CRM`, `Đường dẫn /lien-he.html`, `Sự kiện Gửi form`, `Bản ghi gần nhất 14/10/2026 08:41`.
- Bảng ánh xạ trường Form (`Trường dữ liệu của form`):
  | Trường dữ liệu nguồn | Giá trị mẫu gần nhất | Trường CDP (Target Field) | Quy tắc chuẩn hóa (Transform) | Tin cậy (Confidence) |
  | :--- | :--- | :--- | :--- | :--- |
  | `form.tds-input-1` | `"0969733325"` | `phone` (Dropdown) | `CH-SDT` (Dropdown) | `Cao` (Dropdown) |
  | `form.tds-input-2` | `"Tấn "` | `name` (Dropdown) | `CH-TEN` (Dropdown) | `Cao` (Dropdown) |
  | `form.tds-input-3` | `"tansida@gmail.com"` | `email` (Dropdown) | `CH-EMAIL` (Dropdown) | `Cao` (Dropdown) |
  | `form.tds-input-4` | `"Quận 7"` | *Chưa chọn* | *Chưa chọn* | *Chưa chọn* |
- Nút: `[Lưu thay đổi]`.

---

### 3.4. Màn hình 4: Lịch sử thay đổi & Khôi phục phiên bản (Version Diff & Rollback)
*Tham chiếu: Trang 4 & Trang 8 trong tài liệu PDF*

#### A. Header & Breadcrumbs:
- `‹ Quay lại mapping form`
- Breadcrumb: `Mapping dữ liệu / CRM / Gửi form / Form liên hệ / Lịch sử thay đổi`.
- Tiêu đề: **Lịch sử thay đổi mapping**.
- Phụ đề: `WEB-01 · form /lien-he.html (Form liên hệ). Mỗi lần lưu tạo một phiên bản mới và áp dụng ngay. Chỉ admin được cấu hình mapping.`

#### B. Khối So sánh Phiên bản (Version Diff Detail):
- Tiêu đề: **Phiên bản 3: thay đổi so với phiên bản 2** | Badge: `Đang chạy`.
- Metadata: `Lưu bởi [Tên admin] · 14/10/2026 09:40 · áp dụng cho dữ liệu nhận từ lúc lưu`.
- Danh sách thay đổi phân loại theo màu sắc & nhãn:
  1. `[Thêm - Badge xanh lá]`: `form.tds-input-3 → email · CH-EMAIL · tin cậy Cao` (Hệ thống tự map).
  2. `[Sửa - Badge xanh dương]`: `form.tds-input-2 · quy tắc chuẩn hóa` (Không áp dụng ➔ CH-TEN).
  3. `[Chưa map - Badge cam]`: `form.tds-input-4 → thuộc tính mở rộng` (Chưa có trường CDP phù hợp, dữ liệu vẫn được giữ).

#### C. Khối Danh sách các phiên bản (Sidebar bên phải):
1. **Phiên bản 3** | Badge: `Đang chạy`  
   `[Tên admin] · 14/10/2026 · 3 thay đổi`
2. **Phiên bản 2** | Badge: `Lưu trữ`  
   `[Tên admin] · 10/10/2026 · 2 thay đổi`  
   Hành động: `[Xem]` | `[Khôi phục]`
3. **Phiên bản 1** | Badge: `Lưu trữ`  
   `[Tên admin] · 02/10/2026 · tạo mới`  
   Hành động: `[Xem]` | `[Khôi phục]`
- Chú thích: *"Khôi phục tạo một phiên bản mới từ bản cũ và áp dụng ngay. Lịch sử không bị xóa."*

---

## 4. MÔ HÌNH DỮ LIỆU TYPESCRIPT (DATA CONTRACTS)

```typescript
export interface ConnectedPageSummary {
  id: string;
  name: string;
  category: 'CENTRALFLOW' | 'SOCIAL_NETWORK';
  platformType: 'crm' | 'facebook' | 'zalo' | 'website';
  identifier: string; // page_id, site_id, zalo_id
  status: 'receiving' | 'paused' | 'error';
  totalEvents: number;
  identifiedCustomers: number;
  lastReceivedAt: string; // ISO date
}

export interface JsonFieldMappingConfig {
  pageId: string;
  sourceType: string;
  connectedPageName: string;
  mappings: Array<{
    cdpField: string;
    jsonPath: string;
    isLocked: boolean;
  }>;
  sampleJson: Record<string, any>;
}

export interface BehaviorEventConfig {
  eventType: string; // 'AutoFormSubmit' | 'PageView' | 'AutoClick' | 'ScrollDepth'
  eventName: string;
  eventCount: number;
  description: string;
  saveToCustomerProfile: boolean;
}

export interface FormMappingItem {
  sourceField: string; // e.g. 'form.tds-input-1'
  sampleValue: string;
  cdpField: string | null; // e.g. 'phone'
  normalizationRule: 'CH-SDT' | 'CH-TEN' | 'CH-EMAIL' | null;
  confidence: 'Cao' | 'Trung bình' | 'Thấp' | null;
}

export interface FormMappingDefinition {
  formId: string;
  formName: string;
  pageUrl: string;
  lastSubmittedAt: string;
  fields: FormMappingItem[];
}

export interface MappingVersionDiff {
  type: 'added' | 'modified' | 'unmapped';
  field: string;
  detail: string;
  note?: string;
}

export interface MappingVersionRecord {
  version: number;
  status: 'active' | 'archived';
  authorName: string;
  savedAt: string;
  changeCount: number;
  diffs: MappingVersionDiff[];
}
```

---

## 5. TIÊU CHUẨN KỸ THUẬT & UI (ANGULAR 18 & TDS UI)

1. **Kiến trúc Component Standalone**:
   - `mfe-cdp` sử dụng Standalone Components với Angular Signals (`signal()`, `computed()`, `effect()`).
   - `ChangeDetectionStrategy.OnPush` cho 100% components.
2. **Bộ thư viện TDS UI áp dụng (`Bug #2083` & `Task #2102`)**:
   - `TDSSelectModule` (`import { TDSSelectModule } from 'tds-ui/select'`, selector `<tds-select>`): Thay thế 100% thẻ `<select>` native trong `EventOverviewComponent` (`cycle-range-select`) và `GeneralConfigComponent` (`source-type-select`, `connected-page-select`, `mapping-json-select-*`). Truyền danh sách qua input `[data]="..."` (kèm `valueField`/`textField` nếu là mảng object, hoặc mảng `string[]` trực tiếp), kết hợp `[ngModel]` và `(ngModelChange)`.
   - `TDSButtonModule` (`import { TDSButtonModule } from 'tds-ui/button'`, directives `tds-button`, `tds-button-outline`, `tds-button-flat`): Thay thế 100% thẻ `<button>` thường (nút `Lưu cấu hình`, `+ Thêm trường`, `Xóa`, `Copy Payload`, phân trang `page-btn-*`, và danh sách trang liên kết `sidebar-page-*`).
   - `TDSTabsModule` (`import { TDSTabsModule } from 'tds-ui/tabs'`, selectors `<tds-tabset>`, `<tds-tab>`): Chuẩn hóa 3 sub-tabs (`Cấu hình chung`, `Sự kiện hành vi (4)`, `Lịch sử hoạt động`) trong `GeneralConfigComponent` sang `<tds-tabset tdsType="line">`, bảo toàn `data-testid="subtab-general"`, `subtab-behavior`, `subtab-history`.
   - `TDSTableModule` (`import { TDSTableModule } from 'tds-ui/table'`, selector `<tds-table>`): Thay thế 100% thẻ `<table>` native (`connected-pages-stats-table` trong `EventOverviewComponent`; `json-field-mapping-table` và `live-preview-events-table` trong `GeneralConfigComponent`) bằng `<tds-table [listData]="..." [showPagination]="false" [frontPagination]="false" [templateMode]="true">` chứa trực tiếp `<thead>` và `<tbody>`.
   - `TDSFormInputModule` / `TDSInputModule` (`import { TDSFormInputModule } from 'tds-ui/input'`, directive `tds-input`): Áp dụng cho các ô `<input type="text">` (`sidebar-search-input`, `mapping-cdp-input-*`, `new-cdp-field-input`, `new-json-path-input`).
   - `TDSTagModule` (`tds-tag`): Hiển thị trạng thái `✔ Đang nhận`, `Khóa cố định`, `Đang chạy`, `Lưu trữ`.
3. **Typography, Semantic Color Tokens & Scrollbar (`tds-color-*`, `tds-panel-scroll`)**:
   - Nghiêm cấm sử dụng class màu Tailwind hardcode (`bg-blue-600`, `hover:bg-blue-700`, `text-red-500`, `text-red-600`, `text-emerald-600`, `border-blue-600`, `bg-amber-50`, `text-amber-800`, `border-amber-200`, `bg-slate-100`, `bg-slate-900`, `text-slate-100`, `bg-blue-50`, `border-blue-200`, `text-blue-800`) hoặc mã màu hex cứng trong `.scss` cho Stepper badge.
   - Bắt buộc sử dụng 100% Semantic Tokens chuẩn TDS UI: `tds-color-text-primary`, `tds-color-text-secondary`, `tds-color-text-success`, `tds-color-text-error`, `tds-color-text-warning`, `tds-color-text-info`, `tds-color-text-white`, `tds-color-background-primary-subtle`, `tds-color-background-success-subtle`, `tds-color-background-warning-minimal`, `tds-color-background-info-minimal`, `tds-color-background-neutral-minimal`, `tds-color-background-neutral-boldest`, `tds-color-border-primary`, `tds-color-border-secondary`, `tds-color-border-brand-primary`, `tds-color-border-warning`, `tds-color-border-info`, `tds-color-border-error`.
   - Bổ sung class `tds-panel-scroll` cho toàn bộ các vùng cuộn (`general-config-page`, `json-viewer-container`, `sample-json-syntax-highlight`, `connected-pages-sidebar`, `connected-pages-table-section`).
4. **Quy chuẩn Tương tác JSON Tree (wicx-json-viewer & Text Selection / Dual Copy Actions - Bug #1173, Bug #1508 & Bug #2103)**:
   - Thẻ `<button>` bao quanh dòng segment phải áp dụng `user-select: text !important; -webkit-user-select: text !important;` trên `.segment-key`, `.segment-value`, `.segment-primitive`.
   - Con trỏ chuột trên các nhãn khóa và giá trị phải chuyển thành `cursor: text` để hỗ trợ bôi đen văn bản tự nhiên.
   - Nút mũi tên gập mở `.toggler` giữ nguyên `user-select: none; cursor: pointer;` để duy trì thao tác thu/phóng cây JSON.
   - Tách bạch rõ 2 nút sao chép theo quy luật lân cận thị giác (Gestalt Proximity), **không chiếm không gian layout (`Bug #1508`)**, **tách biệt vùng hover Key vs Value và tự động tắt badge sau khi sao chép (`Bug #2103`)**:
     - **Nút Copy Path (`button.segment-copy-path-btn`)**: Đặt trong DOM ngay sau Key và trước dấu `:`, dùng `position: absolute` (overlay thoát khỏi normal DOM/flex flow, mặc định `opacity: 0; pointer-events: none; z-index: 10;`) kèm cầu nối vùng nhận chuột `::before` (`left: -8px; width: 8px;`) để nhãn Key và dấu `:` luôn nằm liền sát nhau (`"key":`). **Chỉ hiển thị (`opacity: 1; pointer-events: auto;`) khi người dùng hover trực tiếp vào nút Key (`.segment-key-btn:hover + .segment-copy-path-btn` / `button[id]:hover + .segment-copy-path-btn`), hover/focus trên chính nút `.segment-copy-path-btn`, hoặc đang ở trạng thái `.copied`** (tuyệt đối không dùng `.segment-main:hover` làm hiện cả 2 nút cùng lúc).
     - **Nút Copy Value (`button.segment-copy-value-btn`)**: Đặt ngay cạnh Value, dùng `position: absolute` kèm cầu nối `::before` (`left: -8px; width: 8px;`). **Chỉ hiển thị (`opacity: 1; pointer-events: auto;`) khi người dùng hover trực tiếp vào vùng Value (`.segment-preview-container:hover ~ .segment-copy-value-btn`), hover/focus trên chính nút `.segment-copy-value-btn`, hoặc đang ở trạng thái `.copied`**.
     - **Tự động ẩn Badge xác nhận (`Auto-Dismiss Copy Badge - Bug #2103`)**: Sau khi bấm sao chép (`copyPath` hoặc `copyValue`, kể cả từ node con đệ quy `onChildPathCopy` / `onChildValuePathCopy`), badge `'Đã chép path'` / `'Đã chép giá trị'` (`copiedPath` / `copiedValuePath`) chỉ hiển thị trong **1.5s–2s (`1800ms`)** rồi tự động reset signal về `null` (dọn dẹp `clearTimeout` khi bấm liên tiếp hoặc khi `DestroyRef.onDestroy`), tuyệt đối không dính cứng vĩnh viễn trên giao diện.

---

## 6. MA TRẬN TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA MATRIX)

| Mã AC | Màn hình | Tiêu chí nghiệm thu (Acceptance Criteria) |
| :--- | :--- | :--- |
| `AC-MAP-01` | Dashboard Tổng quan | Hiển thị chính xác 3 chỉ số KPI (Tổng sự kiện, Trang nhận, Khách nhận diện) và danh sách trang liên kết lọc theo ngày. |
| `AC-MAP-02` | Dashboard Tổng quan | Tìm kiếm tức thì trang liên kết theo tên, `site_id` hoặc `page_id` trên sidebar trái. |
| `AC-MAP-03` | Cấu hình chung | Hiển thị Stepper 4 bước và cấu hình bảng ánh xạ JSON (`site_id`, `data.system_event_type` bị khóa cố định). |
| `AC-MAP-04` | Cấu hình chung | Xem trước JSON mẫu định dạng chuẩn syntax highlighting kèm nút copy toàn bộ payload. |
| `AC-MAP-05` | Sự kiện hành vi | Checkbox bật/tắt lưu sự kiện vào hồ sơ khách hàng lưu trạng thái tức thì. |
| `AC-MAP-06` | Mapping Form | Bảng ánh xạ trường form cho phép chọn trường CDP, chuẩn hóa (`CH-SDT`, `CH-TEN`, `CH-EMAIL`), và độ tin cậy. |
| `AC-MAP-07` | Lịch sử phiên bản | Hiển thị danh sách phiên bản quá khứ, phân biệt rõ các loại thay đổi (Thêm, Sửa, Chưa map) với badge màu tương ứng. |
| `AC-MAP-08` | Lịch sử phiên bản | Bấm nút `[Khôi phục]` phiên bản cũ sẽ tạo một phiên bản mới mang cấu hình bản được chọn mà không xóa lịch sử cũ. |
| `AC-MAP-09` | Cây JSON Payload | Người dùng có thể bôi đen chuột tự do trên bất kỳ key, value, string literals trong cây JSON và copy qua Ctrl+C / Context Menu. |
| `AC-MAP-10` | Cây JSON Payload | Tách bạch nút 1-click `Copy path` (cạnh Key) và `Copy value` (cạnh Value) (`Bug #1173`); dùng `position: absolute` không tạo khoảng trống (`Bug #1508`); hover Key chỉ hiện nút Copy Path, hover Value chỉ hiện nút Copy Value, và badge `'Đã chép ...'` tự động tắt (reset về `null`) sau `1.5s-2s` (`1800ms`) (`Bug #2103`). |


