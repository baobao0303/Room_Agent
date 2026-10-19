# Đặc Tả Kiến Trúc: AFFiNE Data-View Engine (EP-02)

> **Tài liệu**: Đặc tả kiến trúc kỹ thuật chuẩn (Technical Architecture Specification)  
> **Mã Epic**: EP-02 (Harness Item #86)  
> **Các Feature trực thuộc**: FT-04 (#87), FT-05 (#88), FT-06 (#89)  
> **Tác giả**: Lead (Technical Architect & Project Manager in SLPC)  
> **Ngày phê duyệt**: 2026-10-17  
> **Mục tiêu**: Thiết kế & tích hợp động cơ Data-View (Database đa thuộc tính, Table view, Kanban board view, Filter/Sort/Search) từ kiến trúc gốc AFFiNE (`@blocksuite/affine/model` & `data-view`) vào hệ thống lưu trữ ngoại tuyến Rust SQLite (`notion-offline-rust`).

---

## 1. Bối Cảnh & Mục Tiêu Kỹ Thuật (Executive Summary)

### 1.1. Hiện trạng
- Hệ thống `notion-offline-rust` hiện đã có:
  - SQLite lưu trữ phòng thủ (`SQLITE_DBCONFIG_DEFENSIVE`, `WAL` mode, file permission `0o600`).
  - Thực thi batch SQL an toàn (`exec_sqlite_batch_v2`) và kiểm tra query injection.
  - Quản lý Page và Block cây phân cấp cơ bản (`BlockType`: `Page`, `Text`, `Header`, `Table`, `TableRow`, `TableCell`...).
  - Lưu trữ Yjs updates (`updates`) và Binary Blobs (`blobs`) tương thích chuẩn đồng bộ AFFiNE v1.
- Điểm còn thiếu: Chưa hỗ trợ Database động đa thuộc tính (Database Hub Model), chưa có cột thuộc tính định kiểu (Text, Number, Select, Status, Date, Checkbox), chưa có Data-View Table và Kanban Board với khả năng gom nhóm, lọc và sắp xếp.

### 1.2. Mục tiêu kiến trúc EP-02
1. **Zero-Migration Storage**: Lưu trữ toàn bộ Database Block, Column Schemas, Views, và Row Cell Data trực tiếp trên bảng `block` hiện hữu thông qua trường `properties` (JSON payload) và quan hệ cha-con `parent_id`.
2. **AFFiNE Contract Alignment**: Ánh xạ 1:1 với cấu trúc dữ liệu của BlockSuite AFFiNE (`affine:database`, `ColumnDataType`, `SerializedCells`, `ViewBasicDataType`).
3. **High-Performance Offline Query**: Hỗ trợ truy vấn, lọc điều kiện (Filter) và sắp xếp đa cột (Multi-column Sort) ngay trên SQLite hoặc bộ nhớ đệm trong tiến trình Rust.
4. **Dual Data-View UI**: Tích hợp trực tiếp vào Single-page HTML UI (`HTML_UI` trong `server.rs`) với Table View (chỉnh sửa inline) và Kanban Board View (phân cột theo Status/Select, kéo thả thẻ công việc).

---

## 2. Phân Tích Cấu Trúc Dữ Liệu Tham Chiếu (AFFiNE BlockSuite Reference)

Căn cứ vào mã nguồn tham chiếu tại `clone/AFFiNE/blocksuite/affine/model/src/blocks/database/`:

### 2.1. Schema Khối Database (`affine:database`)
```typescript
export type DatabaseBlockProps = {
  views: ViewBasicDataType[];      // Danh sách view: Table, Kanban
  title: Text;                     // Tiêu đề của Database
  cells: SerializedCells;          // Record<rowId, Record<columnId, CellDataType>>
  columns: Array<ColumnDataType>;  // Định nghĩa các cột thuộc tính
  comments?: Record<string, boolean>;
};

export interface ColumnDataType<Data extends Record<string, unknown> = Record<string, unknown>> {
  id: string;                      // Định danh duy nhất của cột (UUID/nanoid)
  type: string;                    // Kiểu dữ liệu: text, number, select, status, date, checkbox
  name: string;                    // Tên hiển thị của cột
  data: Data;                      // Metadata mở rộng (options, format, color)
}

export type CellDataType<ValueType = unknown> = {
  columnId: ColumnDataType['id'];
  value: ValueType;                // Giá trị cell theo kiểu tương ứng
};

export type ViewBasicDataType = {
  id: string;
  name: string;
  mode: 'table' | 'kanban';        // Kiểu view hiển thị
  group_by?: string;               // Cột dùng để gom nhóm trong Kanban (status / select)
  filter?: FilterGroup;            // Cấu hình bộ lọc
  sort?: SortRule[];               // Quy tắc sắp xếp
};
```

### 2.2. Chi Tiết Các Kiểu Cột (Column Types & Data Payloads)
| Cột (`type`) | Kiểu dữ liệu `value` | Cấu trúc `data` (Metadata) | Hành vi UI |
| :--- | :--- | :--- | :--- |
| `text` | `String` | `{}` | Chỉnh sửa text trực tiếp, wrap text |
| `number` | `f64` hoặc `i64` | `{"format": "number" \| "currency" \| "percent"}` | Căn phải, định dạng số, kiểm tra regex |
| `select` | `String` (Option ID) | `{"options": [{"id": "opt_1", "value": "High", "color": "red"}]}` | Dropdown 1 giá trị, tag màu |
| `multi_select` | `Vec<String>` | `{"options": [{"id": "opt_1", "value": "Rust", "color": "orange"}]}` | Dropdown đa giá trị, danh sách tags |
| `status` | `String` (Status ID) | `{"options": [{"id": "todo", "value": "To Do", "color": "gray"}, ...]}` | Dropdown trạng thái quy chuẩn |
| `date` | `i64` (Epoch ms) hoặc `String` (ISO-8601) | `{"format": "YYYY-MM-DD"}` | Date picker, hiển thị ngày giờ |
| `checkbox` | `bool` | `{}` | Checkbox boolean toggle trực tiếp |

---

## 3. Kiến Trúc Lưu Trữ Trên Rust & SQLite (`notion-offline-rust`)

### 3.1. Thiết Kế Lưu Trữ Không Đổi Schema (Zero Migration Invariant)
Bảng SQLite `block` sẵn có:
```sql
CREATE TABLE IF NOT EXISTS block (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    parent_table TEXT,
    block_type TEXT NOT NULL,
    content TEXT,
    properties TEXT,
    format TEXT,
    alive INTEGER NOT NULL DEFAULT 1,
    version INTEGER NOT NULL DEFAULT 1,
    created_time INTEGER NOT NULL,
    last_edited_time INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_block_parent ON block(parent_id);
```

#### Quy tắc ánh xạ Database:
1. **Database Container Block**:
   - `id`: UUID của Database (VD: `db_01j...`).
   - `parent_id`: ID của Page chứa Database.
   - `block_type`: `"database"`.
   - `content`: Tiêu đề Database (Plain text).
   - `properties`: JSON string hóa của struct `DatabaseProperties`:
     ```json
     {
       "columns": [
         { "id": "col_title", "name": "Title", "type": "text", "data": {} },
         { "id": "col_status", "name": "Status", "type": "status", "data": { "options": [...] } },
         { "id": "col_due", "name": "Due Date", "type": "date", "data": {} }
       ],
       "views": [
         { "id": "view_table", "name": "All Items", "mode": "table" },
         { "id": "view_kanban", "name": "Kanban Board", "mode": "kanban", "group_by": "col_status" }
       ]
     }
     ```
2. **Database Row Block**:
   - `id`: UUID của Hàng (VD: `row_01j...`).
   - `parent_id`: ID của Database cha (`db_01j...`).
   - `parent_table`: `"block"`.
   - `block_type`: `"database_row"`.
   - `content`: Tiêu đề chính của hàng (Primary text).
   - `properties`: JSON string hóa của struct `DatabaseRowProperties`:
     ```json
     {
       "cells": {
         "col_title": { "columnId": "col_title", "value": "Implement Task #90" },
         "col_status": { "columnId": "col_status", "value": "in_progress" },
         "col_due": { "columnId": "col_due", "value": 1792195200000 }
       }
     }
     ```

### 3.2. Cấu Trúc Rust Structs (`models.rs`)
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BlockType {
    Page,
    Text,
    Header,
    SubHeader,
    SubSubHeader,
    ToDo,
    BulletedList,
    NumberedList,
    Callout,
    Code,
    Quote,
    Divider,
    Table,
    TableRow,
    TableCell,
    Math,
    Database,       // Khối Database cha chứa columns & views
    DatabaseRow,    // Khối Hàng con chứa cells
    #[serde(other)]
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ColumnSchema {
    pub id: String,
    pub name: String,
    pub r#type: String, // text, number, select, multi_select, status, date, checkbox
    #[serde(default)]
    pub data: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DataViewConfig {
    pub id: String,
    pub name: String,
    pub mode: String, // "table" hoặc "kanban"
    #[serde(skip_serializing_if = "Option::is_none")]
    pub group_by: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub filter: Option<FilterGroup>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sort: Option<Vec<SortClause>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DatabaseProperties {
    pub columns: Vec<ColumnSchema>,
    pub views: Vec<DataViewConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct CellValue {
    pub column_id: String,
    pub value: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DatabaseRowProperties {
    pub cells: std::collections::HashMap<String, CellValue>,
}
```

---

## 4. Đặc Tả Giao Diện Lập Trình (REST API Specification)

Tất cả các API được triển khai trong `notion-offline-rust/src/server.rs` phục vụ cả Local UI và Client tích hợp:

### 4.1. Quản lý Khối Database
- `POST /api/databases`: Tạo mới một database rỗng trên page.
  - Body: `{"parent_page_id": "...", "title": "My Database", "initial_view": "table"}`
  - Response: `Block` với cấu trúc `DatabaseProperties` mặc định gồm 2 cột: `Title` (`text`) và `Status` (`status`).
- `GET /api/databases/:id`: Lấy thông tin chi tiết database, bao gồm danh sách cột, các view và tất cả hàng con (`alive = 1`).
  - Response:
    ```json
    {
      "database": { ...Block... },
      "columns": [ ... ],
      "views": [ ... ],
      "rows": [
        { "id": "row_1", "content": "Task 1", "cells": { ... } }
      ]
    }
    ```

### 4.2. Quản lý Cột (Columns CRUD)
- `POST /api/databases/:id/columns`: Thêm một cột mới vào schema database.
  - Body: `{"name": "Priority", "type": "select", "data": {"options": [...]}}`
- `PUT /api/databases/:id/columns/:col_id`: Cập nhật tên hoặc metadata của cột.
- `DELETE /api/databases/:id/columns/:col_id`: Xóa cột khỏi schema và tự động dọn dẹp cell data của cột đó trên các hàng con.

### 4.3. Quản lý Hàng & Ô Dữ Liệu (Rows & Cells CRUD)
- `POST /api/databases/:id/rows`: Thêm một hàng mới vào database.
  - Body: `{"content": "New Record", "cells": {"col_status": {"column_id": "col_status", "value": "todo"}}}`
- `PUT /api/databases/:id/rows/:row_id/cells`: Chỉnh sửa cell data của một hàng (inline edit).
  - Body: `{"column_id": "col_status", "value": "done"}`
- `DELETE /api/databases/:id/rows/:row_id`: Xóa mềm (`alive = 0`) một hàng trong database.

### 4.4. Quản lý View & Truy Vấn (Views & Query API)
- `POST /api/databases/:id/views`: Tạo hoặc cập nhật view (Table / Kanban).
- `POST /api/databases/:id/query`: Truy vấn dữ liệu có áp dụng bộ lọc (filter), tìm kiếm (search text) và sắp xếp (sort).
  - Body:
    ```json
    {
      "search": "harness",
      "filters": [
        { "column_id": "col_status", "op": "eq", "value": "in_progress" },
        { "column_id": "col_priority", "op": "in", "value": ["high", "critical"] }
      ],
      "sorts": [
        { "column_id": "col_due", "direction": "asc" }
      ]
    }
    ```

---

## 5. Đặc Tả Giao Diện Người Dùng (UI Architecture - Table & Kanban)

Tích hợp vào `HTML_UI` tại `notion-offline-rust/src/server.rs`:

### 5.1. View Switcher Component
- Nút chuyển đổi mượt mà giữa **Table View** (Biểu tượng bảng tính) và **Kanban Board** (Biểu tượng bảng cột thẻ).
- Trạng thái view được lưu vào cấu hình của Database block để duy trì trạng thái khi người dùng tải lại trang.

### 5.2. Data-View Table Component
1. **Header Row**: Hiển thị icon tương ứng với kiểu cột (Text: `T`, Number: `#`, Select: `🏷️`, Status: `⚪`, Date: `📅`, Checkbox: `☑️`), cho phép bấm vào header để đổi tên hoặc xóa cột.
2. **Inline Cell Editing**:
   - `text`: Nhấp đúp vào ô để mở input text inline; tự động `blur` để lưu (`PUT /api/databases/:id/rows/:row_id/cells`).
   - `checkbox`: Nhấp 1 chạm để đổi trạng thái `true` / `false`.
   - `select` / `status`: Nhấp chuột hiển thị popover bảng màu lựa chọn; chọn xong tự động đóng và cập nhật thẻ màu.
   - `number`: Chỉ cho phép nhập ký tự số; hiển thị cảnh báo vi phạm.
   - `date`: Hiển thị date-picker popover.
3. **Thêm Hàng / Thêm Cột**: Nút `+ New Row` ở cuối bảng và nút `+ Add Column` ở cột cuối cùng.

### 5.3. Data-View Kanban Board Component
1. **Phân Cột (Grouping)**:
   - Nhóm các hàng thành các cột dựa theo giá trị của cột `status` hoặc `select` được chỉ định (`group_by`).
   - Cột mặc định "No Status" cho các hàng chưa gán giá trị.
2. **Card Rendering**: Mỗi thẻ hiển thị tiêu đề chính (`content`), badge trạng thái, hạn chót ngày tháng và checkbox hoàn thành.
3. **Drag & Drop Interaction**:
   - Sử dụng native HTML5 Drag and Drop (`draggable="true"`, `ondragstart`, `ondragover`, `ondrop`).
   - Khi kéo một thẻ từ cột A sang cột B:
     - Cập nhật tức thời trên giao diện (Optimistic UI update).
     - Gửi yêu cầu ngầm `PUT /api/databases/:id/rows/:row_id/cells` với `value = new_column_id`.
     - Rollback vị trí cũ nếu API trả về mã lỗi.

---

## 6. Động Cơ Lọc, Sắp Xếp & Tìm Kiếm (Filter, Sort, Search Engine)

Được thiết kế theo nguyên tắc Functional Pure Engine trong Rust:

### 6.1. Toán Tử Lọc (Filter Operators)
- **Chuỗi (`text`)**: `contains`, `equals`, `starts_with`, `is_empty`, `is_not_empty`.
- **Số (`number`)**: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`.
- **Lựa chọn (`select`, `status`)**: `is`, `is_not`, `in`, `not_in`.
- **Ngày tháng (`date`)**: `before`, `after`, `on_day`, `is_empty`.
- **Checkbox**: `is_checked` (`true`), `is_unchecked` (`false`).

### 6.2. Thuật Toán Sắp Xếp Đa Thuộc Tính (Multi-column Sort)
- Hỗ trợ sắp xếp theo thứ tự ưu tiên của danh sách `SortClause(column_id, direction)`.
- Áp dụng nguyên tắc `nulls_last` để đảm bảo các hàng chưa điền dữ liệu luôn nằm ở cuối danh sách.

---

## 7. Kế Hoạch Phân Rã Công Việc & Tiêu Chí Nghiệm Thu (Work Breakdown & AC)

### Phân Rã Chi Tiết Trên Bàn Cờ Harness DB

#### 1. Feature FT-04 (#87): Multi-property Database Schema & Column Types
- **Task #90 (Active, P1)**: `TK-04 - Database block schema, models & SQLite persistence`
  - *Owner*: `Peer`
  - *Target Files*: `notion-offline-rust/src/models.rs`, `notion-offline-rust/src/db.rs`
  - *Acceptance Criteria (AC)*:
    1. `BlockType` bổ sung 2 biến thể: `Database` và `DatabaseRow` với đầy đủ `as_str()`, `FromStr`, `Display`.
    2. Struct `ColumnSchema`, `DataViewConfig`, `DatabaseProperties`, `CellValue`, `DatabaseRowProperties` được serialize/deserialize chính xác qua `serde_json`.
    3. `NotionDb` hỗ trợ các method: `create_database()`, `get_database()`, `add_database_column()`, `insert_database_row()`, `update_cell_value()`, `get_database_rows()`.
    4. Toàn bộ 25 unit test hiện tại tiếp tục pass 100%, bổ sung ít nhất 4 unit tests mới cho database CRUD.
- **Task #91 (New, P1)**: `TK-05 - REST Endpoints cho Database & Column/Row CRUD trong server.rs`
  - *Owner*: `Peer`
  - *Target Files*: `notion-offline-rust/src/server.rs`
  - *Acceptance Criteria (AC)*:
    1. Endpoint `POST /api/databases`, `GET /api/databases/:id` xử lý thành công payload JSON chuẩn.
    2. Endpoint `POST /api/databases/:id/columns` và `PUT /api/databases/:id/columns/:col_id` thêm/sửa cột đúng schema.
    3. Endpoint `POST /api/databases/:id/rows` và `PUT /api/databases/:id/rows/:row_id/cells` cập nhật cell an toàn.
    4. Thêm tích hợp test case trong `server::tests` mô phỏng luồng HTTP request/response.

#### 2. Feature FT-05 (#88): Data-View Table & Kanban Board UI
- **Task #92 (New, P1)**: `TK-06 - Triển khai Table View Component với Inline Editing trong HTML_UI`
  - *Owner*: `Peer`
  - *Target Files*: `notion-offline-rust/src/server.rs` (chuỗi `HTML_UI`)
  - *Acceptance Criteria (AC)*:
    1. Render bảng với headers tương ứng từng column type.
    2. Cho phép double-click chỉnh sửa inline ô text/number, click checkbox, và chọn status từ popover.
    3. Hỗ trợ nút thêm cột (`+ Add Column`) và thêm hàng (`+ New Row`).
- **Task #93 (New, P1)**: `TK-07 - Triển khai Kanban Board Component với Drag-and-Drop trong HTML_UI`
  - *Owner*: `Peer`
  - *Target Files*: `notion-offline-rust/src/server.rs` (chuỗi `HTML_UI`)
  - *Acceptance Criteria (AC)*:
    1. Phân cột tự động theo các giá trị options của cột `status` hoặc `select`.
    2. Hỗ trợ kéo thả thẻ card giữa các cột với HTML5 DnD API, cập nhật ngầm qua `PUT .../cells`.
    3. Cho phép chuyển đổi linh hoạt giữa Table view và Kanban view qua View Switcher bar.

#### 3. Feature FT-06 (#89): Database Filtering, Sorting & Search Engine
- **Task #94 (New, P2)**: `TK-08 - Động cơ lọc điều kiện & tìm kiếm (Filter & Search) trên Rust SQLite`
  - *Owner*: `Peer`
  - *Target Files*: `notion-offline-rust/src/db.rs`, `notion-offline-rust/src/models.rs`
  - *Acceptance Criteria (AC)*:
    1. Hàm `filter_database_rows()` hỗ trợ toán tử `contains`, `eq`, `gt`, `lt`, `in`, `is_checked`.
    2. Tìm kiếm full-text trên trường `content` và các ô `text`.
- **Task #95 (New, P2)**: `TK-09 - Động cơ sắp xếp đa thuộc tính (Multi-column Sort) & View Presets`
  - *Owner*: `Peer`
  - *Target Files*: `notion-offline-rust/src/db.rs`, `notion-offline-rust/src/server.rs`
  - *Acceptance Criteria (AC)*:
    1. Hỗ trợ sắp xếp asc/desc trên cột `text`, `number`, `date` với quy tắc `nulls_last`.
    2. Lưu cấu hình Sort & Filter vào `views` của Database block.

---

## 8. Chiến Lược Kiểm Thử 5-Stage ISTQB (QC Verification Strategy)

Áp dụng quy trình kiểm thử tự động độc lập của agent `QC` (`tools/qc_test_generator.py`):
1. **Stage 1: Equivalence Partitioning (Phân vùng tương đương)**:
   - Kiểm tra định dạng dữ liệu từng kiểu cột (hợp lệ / không hợp lệ).
2. **Stage 2: Boundary Value Analysis (Phân tích giá trị biên)**:
   - Số cực đại, chuỗi rỗng, ngày âm hoặc ngày vượt quá giới hạn 64-bit, danh sách 0 options.
3. **Stage 3: Decision Table Testing (Bảng quyết định)**:
   - Tổ hợp các điều kiện lọc AND/OR trên nhiều cột khác kiểu dữ liệu.
4. **Stage 4: State Transition Testing (Chuyển đổi trạng thái)**:
   - Vòng đời hàng trong Kanban: `To Do` -> `In Progress` -> `Done` -> `Deleted`.
5. **Stage 5: Error Guessing & Defensive Checks**:
   - Thử chèn SQL injection hoặc ký tự NUL vào tên cột và giá trị cell; đảm bảo `validator.rs` và `SQLITE_DBCONFIG_DEFENSIVE` chặn đứng 100%.
