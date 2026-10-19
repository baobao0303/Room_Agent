# Đặc Tả Kiến Trúc Toàn Diện: AFFiNE System & Reverse Engineering Specification

> **Tài liệu**: Báo Cáo Kỹ Thuật Đảo Ngược & Đặc Tả Hệ Thống AFFiNE (Reverse Engineering & System Architecture Specification)  
> **Cấp độ**: L4 Full-System Specification  
> **Tác giả**: Supervisor (Scope & Intent Guard in SLPC)  
> **Cơ sở phân tích**: Mã nguồn đối chiếu `clone/AFFiNE` & Công cụ REA (Reverse Engineering Anything)  
> **Ngày lập**: 2026-10-17  
> **Mục tiêu**: Hệ thống hoá toàn bộ cấu trúc kiến trúc đa tầng của AFFiNE (từ Native Storage Rust, CRDT Yjs Engine, BlockSuite Model/Data-View đến Electron Client Shell) và xây dựng phương án tích hợp tương thích 100% vào `notion-offline-rust`.

---

## 1. Bản Đồ Tổng Quan Hệ Thống (Full-System Topology)

Mã nguồn AFFiNE được tổ chức dưới dạng Monorepo đa ngôn ngữ (Rust, TypeScript/Node.js, Electron, Lit/Web Components):

```
clone/AFFiNE/
├── Cargo.toml                              # Rust Workspace Root
├── packages/
│   ├── frontend/
│   │   ├── native/                         # Native Rust Storage Engine (NAPI-rs / UniFFI)
│   │   │   ├── schema/                     # SQLite DDL, v1/v2 Migrations, Validation
│   │   │   ├── sqlite_v1/                  # SQLite Pool, WAL Mode, NAPI Bindings
│   │   │   └── nbstore/                    # New Block Store (y-octo CRDT, snapshots, updates)
│   │   ├── apps/
│   │   │   ├── electron/                   # Electron Desktop Shell (Main, Preload, Helper)
│   │   │   │   ├── src/main/shared-storage # JSON File & IPC State Synchronization
│   │   │   │   └── src/preload/            # Context Bridge & Sandboxed APIs
│   │   │   └── web/                        # Web Client Shell
│   └── common/                             # Shared Utilities & Infra
└── blocksuite/                             # Block-based Collaborative Editing Framework
    ├── framework/
    │   ├── store/                          # Doc, Workspace, Collection, Schema, BlockModel
    │   └── sync/                           # CRDT Yjs State Vectors & Sync Engine
    └── affine/
        ├── model/                          # Block Definitions (affine:database, affine:page...)
        └── data-view/                      # Table View, Kanban Board, Typed Columns
```

---

## 2. Tầng Lưu Trữ & Đồng Bộ Native (Rust Storage Engine)

AFFiNE sử dụng Rust kết hợp SQLite ở chế độ WAL (Write-Ahead Logging) để đạt hiệu năng I/O tối đa và an toàn dữ liệu cục bộ.

### 2.1. Cấu Trúc Schema v1 (`affine_schema::v1`)
Áp dụng cho các phiên bản cơ sở ban đầu (`packages/frontend/native/schema/src/v1.rs`):

```sql
CREATE TABLE IF NOT EXISTS "updates" (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data BLOB NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  doc_id TEXT
);

CREATE TABLE IF NOT EXISTS "blobs" (
  key TEXT PRIMARY KEY NOT NULL,
  data BLOB NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "version_info" (
  version NUMBER NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "server_clock" (
  key TEXT PRIMARY KEY NOT NULL,
  data BLOB NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "sync_metadata" (
  key TEXT PRIMARY KEY NOT NULL,
  data BLOB NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### 2.2. Cấu Trúc Schema v2 (`affine_schema::init_v2`) & `affine_nbstore`
Phiên bản kiến trúc mới tối ưu hoá snapshot và trạng thái đồng bộ P2P/Cloud (`packages/frontend/native/schema/src/lib.rs`):

```sql
CREATE TABLE "meta" (
  space_id VARCHAR PRIMARY KEY NOT NULL
);

CREATE TABLE "snapshots" (
  doc_id VARCHAR PRIMARY KEY NOT NULL,
  data BLOB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE "updates" (
  doc_id VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  data BLOB NOT NULL,
  PRIMARY KEY (doc_id, created_at)
);

CREATE TABLE "clocks" (
  doc_id VARCHAR PRIMARY KEY NOT NULL,
  timestamp TIMESTAMP NOT NULL
);

CREATE TABLE "blobs" (
  key VARCHAR PRIMARY KEY NOT NULL,
  data BLOB NOT NULL,
  mime VARCHAR NOT NULL,
  size INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  deleted_at TIMESTAMP
);

CREATE TABLE "peer_clocks" (
  peer VARCHAR NOT NULL,
  doc_id VARCHAR NOT NULL,
  remote_clock TIMESTAMP NOT NULL DEFAULT 0,
  pulled_remote_clock TIMESTAMP NOT NULL DEFAULT 0,
  pushed_clock TIMESTAMP NOT NULL DEFAULT 0,
  PRIMARY KEY (peer, doc_id)
);
CREATE INDEX peer_clocks_doc_id ON peer_clocks (doc_id);
```

### 2.3. Động Cơ CRDT & Gộp Cập Nhật (`y-octo`)
Trong `packages/frontend/native/nbstore/src/doc.rs`:
- **Động cơ**: Sử dụng `y-octo` (triển khai Yjs CRDT hiệu năng cao bằng Rust) với cờ `large_refs`.
- **Cơ chế nén**: Nén dữ liệu blob/snapshot bằng thuật toán `zstd` (level 0.13) và `bincode`.
- **Quy trình đọc**:
  1. Đọc bản `snapshot` gần nhất của `doc_id` từ bảng `snapshots`.
  2. Đọc chuỗi `updates` gia tăng có `created_at > snapshot.updated_at`.
  3. Gộp các update thành tài liệu hoàn chỉnh thông qua `y_octo::merge_updates_v1`.
- **Nén & Thu gọn (Compaction)**: Định kỳ gộp toàn bộ `updates` vào `snapshot` mới và dọn dẹp các bản ghi cũ để giữ kích thước file SQLite tối thiểu.

### 2.4. Kết Nối NAPI-rs & SQLite WAL (`affine_sqlite_v1`)
Trong `packages/frontend/native/sqlite_v1/src/lib.rs`:
- Cấu hình SQLite:
  ```rust
  let sqlite_options = SqliteConnectOptions::new()
    .filename(&path)
    .foreign_keys(false)
    .journal_mode(sqlx::sqlite::SqliteJournalMode::Wal);
  let pool = SqlitePoolOptions::new()
    .max_connections(4)
    .connect_lazy_with(sqlite_options);
  ```
- Cung cấp các hàm xuất khẩu NAPI sang TypeScript:
  - `add_blob()`, `get_blob()`, `delete_blob()`, `get_blob_keys()`
  - `insert_updates()`, `get_updates()`, `delete_updates()`, `replace_updates()`
  - `checkpoint()`: Kích hoạt `PRAGMA wal_checkpoint(FULL)` đưa dữ liệu từ log WAL về file db chính.
  - `vacuum_into()`: Kích hoạt `VACUUM INTO ?` sao lưu snapshot db an toàn mà không chặn luồng ghi.

---

## 3. Tầng Framework BlockSuite & Document Model

BlockSuite là trái tim của hệ thống văn bản cộng tác trên AFFiNE.

### 3.1. Phân Tầng BlockSuite Framework
- **`framework/store`**:
  - `Workspace`: Quản lý tập hợp các document (`Doc`), trạng thái kết nối và metadata không gian làm việc.
  - `Doc`: Đại diện cho một trang hoặc tài liệu Yjs, quản lý cây khối (`BlockModel`).
  - `Schema`: Định nghĩa các khối hợp lệ và quan hệ lồng ghép cha-con.
  - `BlockModel`: Đơn vị dữ liệu nhỏ nhất, lưu trữ thuộc tính (`props`) và liên kết cây (`parent`, `children`).
- **`framework/sync`**:
  - Quản lý đồng bộ hai chiều giữa bộ nhớ RAM và tầng lưu trữ Native (IndexedDB / SQLite).
  - So khớp Vector Clock (`StateVector`) để chỉ trao đổi phần sai biệt (`diff updates`).

### 3.2. Cấu Trúc Khối Cơ Sở AFFiNE (`affine/model`)
Hệ thống khối được định nghĩa trong `@blocksuite/affine/model`:
- `affine:page`: Khối gốc của trang văn bản.
- `affine:note`: Khối ghi chú hoặc container bố cục.
- `affine:paragraph`: Khối văn bản thường (Text, Heading, Quote, Code).
- `affine:surface`: Khối bảng vẽ vô cực (Whiteboard / Canvas / Edgeless mode).
- `affine:database`: Khối cơ sở dữ liệu quan hệ nội dòng (Data-View Hub).
- `affine:table`: Khối bảng tính tĩnh đơn giản.

### 3.3. Đặc Tả Khối Cơ Sở Dữ Liệu (`affine:database` & `data-view`)
Căn cứ tại `blocksuite/affine/model/src/blocks/database/` và `blocksuite/affine/data-view/`:

```typescript
export type DatabaseBlockProps = {
  views: ViewBasicDataType[];      // Danh sách view: Table, Kanban, Calendar
  title: Text;                     // Tiêu đề của Database
  cells: SerializedCells;          // Record<rowId, Record<columnId, CellDataType>>
  columns: Array<ColumnDataType>;  // Định nghĩa các cột thuộc tính
};

export interface ColumnDataType<Data extends Record<string, unknown> = Record<string, unknown>> {
  id: string;                      // Định danh duy nhất của cột
  type: string;                    // Kiểu: text, number, select, multi-select, status, date, checkbox
  name: string;                    // Tên hiển thị
  data: Data;                      // Metadata mở rộng (options, format, color)
}

export type ViewBasicDataType = {
  id: string;
  name: string;
  mode: 'table' | 'kanban' | 'calendar';
  group_by?: string;               // Cột dùng gom nhóm trong Kanban (status / select)
  filter?: FilterGroup;            // Cấu hình lọc dữ liệu
  sort?: SortRule[];               // Quy tắc sắp xếp
};
```

---

## 4. Tầng Ứng Dụng Desktop & Shell (Electron Architecture)

Kiến trúc Electron đa tiến trình đảm bảo cô lập bảo mật và quản lý I/O native (`packages/frontend/apps/electron/`):

### 4.1. Phân Chia Tiến Trình (Multi-Process Model)
1. **Main Process (`src/main/`)**:
   - Quản lý vòng đời ứng dụng, menu hệ thống, cửa sổ (`BrowserWindow`).
   - Khởi tạo kết nối SQLite native qua `affine_sqlite_v1` và `affine_nbstore`.
   - Vận hành dịch vụ đồng bộ lưu trữ chia sẻ (`shared-storage`).
2. **Preload Scripts (`src/preload/`)**:
   - Chạy trong ngữ cảnh cô lập (`contextIsolation: true`, `nodeIntegration: false`).
   - Phơi bày các API an toàn sang renderer thông qua `contextBridge.exposeInMainWorld()`.
3. **Helper & Shared-Storage Subsystem (`src/main/shared-storage/`)**:
   - Lưu trữ cấu hình desktop, cài đặt ứng dụng, thông tin workspace gần nhất vào file JSON (`json-file.ts`).
   - Giao tiếp hai chiều với Renderer thông qua IPC events (`handlers.ts`, `events.ts`).

---

## 5. Bản Đồ Tương Thích & Tích Hợp Vào `notion-offline-rust` (Zero-Migration Blueprint)

Để mang toàn bộ sức mạnh Database & Data-View của AFFiNE vào `notion-offline-rust` mà **không phá vỡ schema SQLite hiện hữu**:

### 5.1. Thiết Kế Lưu Trữ Zero-Migration
Áp dụng bảng `block` hiện hữu của `notion-offline-rust`:

| Trường SQLite | Database Block (`block_type = "database"`) | Database Row Block (`block_type = "database_row"`) |
| :--- | :--- | :--- |
| `id` | UUID Database (VD: `db_01...`) | UUID Hàng (VD: `row_01...`) |
| `parent_id` | ID của Page cha | ID của Database cha (`db_01...`) |
| `block_type` | `"database"` | `"database_row"` |
| `content` | Tiêu đề Database | Tiêu đề hàng (Primary Text) |
| `properties` | JSON `DatabaseProperties` (chứa `columns` & `views`) | JSON `DatabaseRowProperties` (chứa `cells`) |
| `alive` | `1` (Active) / `0` (Deleted) | `1` (Active) / `0` (Deleted) |

### 5.2. Mô Hình Dữ Liệu Rust (`models.rs`)
```rust
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
    pub group_by: Option<String>,
    pub filter: Option<FilterGroup>,
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

### 5.3. Kế Hoạch Triển Khai SLPC (Harness Board Sync)
- **FT-04 (#87)**: Multi-property Database Schema & Column Types (Task #90, #91).
- **FT-05 (#88)**: Data-View Table & Kanban Board UI (Task #92, #93).
- **FT-06 (#89)**: Database Filtering, Sorting & Search Engine (Task #94, #95).
- **Quality Gate**: Kiểm thử độc lập 5 giai đoạn ISTQB bởi sub-agent QC (`tools/qc_test_generator.py`).

---

## 6. Danh Mục Tính Năng & Danh Sách Biến Môi Trường Hệ Thống

### 6.1. Danh Mục Tính Năng Cốt Lõi (Core Features Matrix)
1. **Local-First Native Storage**:
   - Lưu trữ phòng thủ SQLite WAL mode, kiểm tra snapshot & Yjs updates (`updates`, `blobs`).
   - Nén snapshot Yjs bằng `zstd` và tuần tự hoá nhị phân `bincode` qua `y-octo`.
   - Backup nóng không khoá `VACUUM INTO` và checkpoint chủ động `PRAGMA wal_checkpoint(FULL)`.
2. **BlockSuite Data-View Engine**:
   - Khối dữ liệu Hub `affine:database` và khối dòng `affine:database_row`.
   - 7 kiểu cột thuộc tính: `text`, `number`, `select`, `multi_select`, `status`, `date`, `checkbox`.
   - Đa góc nhìn dữ liệu: Table View (chỉnh sửa inline) và Kanban Board (kéo thả thẻ, gom nhóm cột).
   - Động cơ lọc điều kiện đa toán tử (`eq`, `contains`, `in`, `gt`, `lt`), sắp xếp đa thuộc tính (`SortClause`), và tìm kiếm toàn văn.
3. **Electron Multi-Process Desktop Shell**:
   - Cô lập an toàn (`contextIsolation: true`, `nodeIntegration: false`).
   - Lưu trữ cấu hình ứng dụng qua IPC JSON store (`shared-storage`).
4. **Harness & Floci Distributed Sync**:
   - Tích hợp S3-compatible remote sync lưu trữ snapshot trạng thái, bàn cờ Caro và artifacts giữa các Agent.

### 6.2. Cấu Hình Biến Môi Trường Cơ Sở Dữ Liệu & Hạ Tầng Floci (Harness S3 DB Environment)
Cấu hình S3/DB phục vụ đồng bộ phân tán và lưu trữ dữ liệu bàn cờ Harness:

```env
FLOCI_ENDPOINT=http://100.124.36.46:14566
FLOCI_S3_BUCKET=harness-data
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
```

### 6.3. Danh Mục Biến Môi Trường AFFiNE Toàn Hệ Thống (System Env Matrix)
| Nhóm | Tên Biến | Giá trị / Định dạng | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **Floci / S3 DB** | `FLOCI_ENDPOINT` | `http://100.124.36.46:14566` | Endpoint dịch vụ lưu trữ phân tán Floci S3 |
| **Floci / S3 DB** | `FLOCI_S3_BUCKET` | `harness-data` | S3 bucket chứa dữ liệu bàn cờ Harness & snapshots |
| **Floci / S3 DB** | `AWS_ACCESS_KEY_ID` | `test` | Access key xác thực dịch vụ S3/Floci |
| **Floci / S3 DB** | `AWS_SECRET_ACCESS_KEY` | `test` | Secret key xác thực dịch vụ S3/Floci |
| **Floci / S3 DB** | `AWS_REGION` | `us-east-1` | Vùng lưu trữ S3 mặc định |
| **Backend / Sync** | `REDIS_SERVER_HOST` | Hostname / IP (VD: `localhost`, `redis`) | *(Tùy chọn/Mở rộng)* Host Redis cho session cache & WebSocket Pub/Sub khi scale server |
| **Backend / Sync** | `REDIS_SERVER_PORT` | Port number (Mặc định: `6379`) | *(Tùy chọn)* Port kết nối Redis server |
| **Backend / Sync** | `REDIS_SERVER_PASSWORD` | String | *(Tùy chọn)* Mật khẩu xác thực Redis server |
| **Backend / Sync** | `DATABASE_URL` | `postgres://user:pass@host:5432/db` | *(Tùy chọn/Mở rộng)* CSDL quan hệ Postgres khi kích hoạt AFFiNE Cloud backend |
| **Runtime Desktop** | `NODE_ENV` | `development` / `production` | Chế độ chạy môi trường Node.js / Electron |
| **Runtime Desktop** | `BUILD_TYPE` | `stable` / `canary` / `internal` | Phân kênh phân phối và cập nhật ứng dụng |
| **Rust Native** | `SQLITE_PATH` | File path (VD: `data/storage.db`) | Đường dẫn tệp cơ sở dữ liệu SQLite cục bộ |
| **Rust Native** | `RUST_LOG` | `info` / `debug` / `warn` | Mức ghi log hệ thống của Rust crate |

---

## 7. Kết Luận
Bản đặc tả này đóng vai trò kim chỉ nam thống nhất toàn bộ nghiên cứu kỹ thuật đảo ngược từ codebase AFFiNE sang hệ sinh thái `notion-offline-rust` và hạ tầng phân tán Floci, bảo toàn nguyên lý YAGNI, không làm biến dạng cấu trúc dữ liệu và sẵn sàng cho đội ngũ kỹ thuật thực thi.
