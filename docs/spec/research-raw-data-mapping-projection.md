# Nghiên cứu Chuyên sâu: CDP Raw Data Mapping & Event Projection Field Mapping UI

> **Mã tài liệu:** `RESEARCH-CDP-RAW-DATA-MAPPING-PROJECTION-20261015`  
> **Ngày lập:** 15/10/2026  
> **Người thực hiện:** Combo-Lead (Paseo SLPC Architecture)  
> **Phạm vi:** Micro-frontend `apps/mfe-cdp` (`/cdp/data-raw`), library `libs/features/raw-event-data`, Backend services (`WiCX.Ingestion`, `WiCX.EventArchive`, `WiCX.DataExtraction`, `WiCX.Crm`), cơ chế Event Projection DB `wicx_projection`.

---

## 1. Nguồn Dữ liệu Sơ cấp (Primary Sources & Citations)

Nghiên cứu này được tổng hợp và đối chiếu trực tiếp từ 3 nhóm nguồn dữ liệu thực tế:

### 1.1. Mã nguồn Frontend (`/home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe`)
- `apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts`: Logic hiển thị danh sách sự kiện thô, lọc nguồn (`fetchEventSources`), phân trang, mở rộng dòng inline (`toggleRowInline`), drawer xem chi tiết payload (`openDrawer`), modal so sánh diff giữa 2 payload (`openCompareModal`), quản lý Tenant (`effectiveTenantId`).
- `apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.html`: Template Angular 18 Standalone, sử dụng hệ thống `tds-ui` (`tds-table`, `tds-drawer`, `tds-modal`, `tds-tab`, `tds-tag`) và `JsonViewerComponent`.
- `libs/features/raw-event-data/data-access/src/auto-gen/services/raw-event-data.service.ts`: OpenAPI HTTP client giao tiếp với backend:
  * `GET /v1/tenants/{tenantId}/cdp/data-raw/event-sources/list`
  * `POST /v1/tenants/{tenantId}/cdp/data-raw/events/list`
  * `GET /v1/tenants/{tenantId}/cdp/data-raw/events/{eventId}`
- `libs/features/raw-event-data/data-access/src/stores/raw-event-data.store.ts`: State management sử dụng `@ngrx/signals` (`signalStore`, `withBaseStore`, `StoreHelper`).
- `node_modules/tds-ui`: Design system chuẩn TDS (table, select, button, modal, drawer, step, checkbox, tags).

### 1.2. Tài liệu Kiến trúc & Đặc tả Backend (`/home/baoltb/Desktop/wicx-crm-doc`)
- `WiCX/docs/docs/event-field-catalog.md`: Thiết kế và thực tế triển khai của Pipeline quét namepath từ payload Kafka (`wicx.tmt.ingestion.v1` và `wicx.events.raw.v1`). Thuật toán `JsonPathWalker` (streaming Utf8JsonReader), băm vân tay cấu trúc `ShapeHasher` (xxHash64), gom bộ nhớ `CatalogBuffer`, ghi theo lô `CatalogFlushService` qua COPY binary vào 4 bảng catalog (`catalog_data_type`, `catalog_field`, `catalog_shape`, `catalog_field_note`).
- `WiCX/docs/docs/projection-pipeline.md`: Kiến trúc trích xuất trường tự động vào database vật lý `wicx_projection` (schema `proj`), bộ máy DDL động an toàn, luồng live consumer trên topic `wicx.events.canonical.v1`, tiến trình Hangfire backfill `ProjectionBackfillJob` quét MinIO theo lô 500 bản ghi.
- `WiCX/docs/docs/architecture.md`: Kiến trúc 4 service (`Ingestion`, `EventArchive`, `DataExtraction`, `Crm`), bus Kafka, lưu trữ MinIO raw verbatim, phân tách database/schema cô lập.
- `WiCX/wicx-crm/docs/Guide/WICX-CRM/cdp-event-analyze.md`: Đặc tả endpoint `POST /v1/events/{eventId}/analyze` khám phá cấu trúc JSON và lưu trữ vào `cdp.event_schemas` + `cdp.event_schema_properties`.
- `WiCX/wicx-crm/docs/Guide/WICX-CRM/cdp-connection-configuration.md`: Cấu hình Connection tenant-scoped (`cdp.connections`) tích hợp Webhook Ingestion và Runtime Config snapshot.
- `BA/implementation-artifacts/stories/Phase 1_User_Stories/UC3.01 - Tiếp nhận & khớp định danh event.md`: Nghiệp vụ Identity Resolution, 3 cấp độ tin cậy định danh (Mạnh, Trung bình, Yếu), điều kiện gộp và gán nhãn hồ sơ khách hàng.

### 1.3. Mockup Giao diện HTML Tương tác (`/tmp/artifact_field_mapping`)
- `Main.dc.html`: Bố cục phân hệ 2 Tab chính (`Dữ liệu thô` vs `Mapping dữ liệu`), thanh điều hướng Sidebar, tổng quan KPI (Trang liên kết, Cần cấu hình, Trường chưa map).
- `SourceList.dc.html`: Panel danh sách nguồn (Web, Facebook, Zalo, POS/Partner) bên trái rộng 320px.
- `WebSource.dc.html` & `WebSource-forms.dc.html`: Quản lý nguồn Website (WEB-01, site_id WiPix), hiển thị luồng 3 bước (Khách ẩn danh -> Khách gửi form -> Nhận diện), 2 sub-tab `Sự kiện hành vi (9)` (4 tracker + 5 custom) và `Form (2)` (/dang-ky, /lien-he).
- `CreateEvent.dc.html`: Slide-over Drawer (720px) cấu hình sự kiện tùy biến từ sự kiện gốc tracker + bộ quy tắc điều kiện (ALL/ANY), toán tử (`chứa`, `bằng`, `bắt đầu bằng`, `khác`, `có giá trị`), giá trị mẫu gợi ý từ 30 ngày gần nhất, chạy thử trên 7 ngày dữ liệu cũ, checkbox áp dụng hồi tố (backfill).
- `Mapping.dc.html`: Bảng ma trận ánh xạ 5 cột (`Trường dữ liệu nguồn`, `Giá trị mẫu gần nhất`, `Trường CDP`, `Quy tắc chuẩn hóa`, `Mức tin cậy`). Hệ thống gợi ý `data-cdp` cho lập trình viên web.
- `TestRun.dc.html`: Môi trường kiểm thử Dry Run mô phỏng 4 bước xử lý (1. Lọc nguồn -> 2. Nhận diện field -> 3. Chuẩn hóa -> 4. Hợp nhất định danh) và bảng đối chiếu hồ sơ khách hàng Trước vs Sau.
- `Review.dc.html`: Sổ cái kiểm toán lịch sử phiên bản (`v1`, `v2`, `v3`), diff so sánh chi tiết giữa các phiên bản, chức năng hoàn tác (Rollback) an toàn.
- `FbSource.dc.html`: Quản trị nguồn Fanpage Facebook (FB-01), quy trình bóc tách SĐT/Email từ nội dung chat.
- `RawData.dc.html`: Bảng giám sát sự kiện thô thời gian thực.

---

## 2. Luồng Dữ liệu Toàn hệ thống (End-to-End Event Lifecycle)

```
[Nguồn Dữ Liệu]
Web Tracker / Fanpage / Zalo / POS / Partner API
      │
      ▼ HTTP POST /v1/events  hoặc  POST /v1/webhooks/{connectionId}
╔═══════════════════════════════════════════════════════════════════════╗
║ ① WiCX.Ingestion.Host                                                 ║
║   - Xác thực API Key / HMAC Signature / Ingest Token                   ║
║   - Khử trùng theo (tenant, connector, externalEventId)               ║
║   - Ghi MỘT transaction Outbox vào PostgreSQL DB wicx                  ║
║   - Hangfire ProcessOutboxJob claim & publish Kafka                   ║
╚═══════════════════════════════╤═══════════════════════════════════════╝
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼ topic: wicx.events.raw.v1                     ▼ topic: ProviderRaw
╔═══════════════════════════════╗               ╔═══════════════════════╗
║ ② WiCX.EventArchive           ║               ║ ② WiCX.EventArchive   ║
║   - Consumer group `lake`     ║               ║   - Consumer group    ║
║   - PUT MinIO verbatim        ║               ║     `provider-raw`    ║
║     Key: tenant/{t}/events/   ║               ║   - PUT MinIO verbatim║
║          {eventId}.json       ║               ╚═══════════╤═══════════╝
║   - Ghi wicx_eventarchive     ║                           │
║     .event_archive            ║                           │
║   - Publish claim-check con trỏ                           │
╚═══════════════╤═══════════════╝                           │
                │                                           │
                ▼ topic: wicx.events.stored.v1              │
╔═══════════════════════════════════════════════╗           │
║ ③ WiCX.DataExtraction.Consumer                ║           │
║   - Consumer group `canonicalization`         ║           │
║   - Ghi checkpoint `event_processing`         ║           │
║   - Hangfire: GET MinIO -> Validate ->        ║           │
║     PassThroughCanonicalPropertyPolicy        ║           │
║   - Publish canonical.v1                      ║           │
╚═══════════════╤═══════════════════════════════╝           │
                │                                           │
                ├──────────────────────────┐                │
                ▼ topic:                   ▼ topic:         ▼
        wicx.events.canonical.v1    wicx.events.raw.v1  (EventArchive catalog)
                │                          │                │
                │                          ▼                ▼
                │                  ╔════════════════════════════════════╗
                │                  ║ ④ Field Catalog Discovery Pipeline  ║
                │                  ║   - DataExtraction Consumer        ║
                │                  ║     group `field-catalog-raw`      ║
                │                  ║   - JsonPathWalker (Utf8JsonReader)║
                │                  ║   - ShapeHasher (xxHash64)         ║
                │                  ║   - In-memory CatalogBuffer        ║
                │                  ║   - Flush mỗi 10s / 50k paths      ║
                │                  ║     vào 4 bảng `catalog_*`         ║
                │                  ╚════════════════════════════════════╝
                │
                ▼
╔═══════════════════════════════════════════════════════════════════════╗
║ ⑤ WiCX.DataExtraction.Projection                                      ║
║   - Consumer group `projection-engine` trên `canonical.v1`            ║
║   - In-memory cache danh sách pipeline active (poll DB mỗi 15s)       ║
║   - ApplyCanonicalEventCommand: trích xuất field theo JSONPath        ║
║   - Thực thi chuỗi Transform (trim, lower, regex, to_date)            ║
║   - Idempotent Upsert vào bảng vật lý riêng:                          ║
║     DB wicx_projection, schema proj."<table>"                         ║
║   - Bảo đảm thứ tự: WHERE (EXCLUDED.occurred_at, EXCLUDED.event_id) >=║
║                           (t.occurred_at, t.event_id)                 ║
║   - Hangfire ProjectionBackfillJob: quét MinIO nạp dữ liệu lịch sử     ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 3. Chi tiết Hợp đồng Kỹ thuật Backend (Backend Contracts)

### 3.1. Phân định Danh mục Kafka Topics & Consumer Groups

| Tên Topic | Định dạng Message / Payload | Producer | Consumer Group | Mục đích / Xử lý |
|---|---|---|---|---|
| `wicx.events.raw.v1` | `EventIngestedIntegrationEvent` (JSON) chứa Metadata envelope + `Properties` thô | Ingestion Outbox | `lake` (`WiCX.EventArchive`) | Lưu trữ nguyên bản (verbatim) lên MinIO, ghi metadata vào catalog `event_archive` |
| `wicx.events.raw.v1` | `EventIngestedIntegrationEvent` | Ingestion Outbox | `field-catalog-raw` (`WiCX.DataExtraction`) | Quét tự động cấu trúc namepath và kiểu dữ liệu JSON, gom nhóm shape hash |
| `wicx.events.raw.v1` | `EventIngestedIntegrationEvent` | Ingestion Outbox | `core` (`WiCX.Crm`) | Identity Resolution & hợp nhất hồ sơ khách hàng 360° |
| `wicx.tmt.ingestion.v1` | `TmtPublicApiKafkaEvent` | TMT Pull Controller | `field-catalog` (`WiCX.DataExtraction`) | Quét namepath dữ liệu từ cổng TMT Public API |
| `wicx.tmt.ingestion.v1` | `TmtPublicApiKafkaEvent` | TMT Pull Controller | `event-archive-tmt` (`WiCX.EventArchive`) | Lưu trữ MinIO dữ liệu đồng bộ từ TMT |
| `ProviderRaw` | `ProviderRawWebhookEvent` | Ingestion Webhook | `provider-raw-archive` (`WiCX.EventArchive`) | Lưu trữ MinIO dữ liệu webhook thô từ Facebook, Zalo, Partner API |
| `wicx.events.stored.v1` | `EventStoredIntegrationEvent` (Claim-check: `bucket`, `objectKey`, `eventId`) | EventArchive | `canonicalization` (`WiCX.DataExtraction`) | Báo hiệu object đã lưu MinIO thành công để DataExtraction tiến hành giải nén & chuẩn hóa |
| `wicx.events.canonical.v1`| `EventCanonicalizedIntegrationEvent` | DataExtraction | `projection-engine` (`WiCX.DataExtraction.Projection`) | Đầu vào cho bộ máy trích xuất thuộc tính tự động vào bảng vật lý |

### 3.2. Bộ Khung Schema Discovery & Cataloging (Field Catalog Engine)

Để phục vụ màn hình chọn trường dữ liệu tự động mà không bắt người dùng tự gõ JSONPath, hệ thống triển khai pipeline quét namepath với 4 bảng:

#### Bảng 1: `catalog_data_type`
- **Khóa chính:** `(source, data_type)` *(Lưu ý: Không có `tenant_id` vì schema là hợp đồng chung của nguồn dữ liệu)*.
- **Cột:**
  * `total_events` (bigint): Mẫu số tính độ phủ (`occurrence_count / total_events`).
  * `truncated_events` (bigint): Số event chạm ngưỡng trần (10.000 path/event).
  * `first_seen_at` / `last_seen_at` (timestamptz): Dấu thời gian phát hiện.

#### Bảng 2: `catalog_field`
- **Khóa chính:** `(source, data_type, path)`.
- **Cột:**
  * `parent_path` (text), `depth` (smallint), `is_leaf` (boolean): Dựng cây phân cấp UI mà không cần parse chuỗi.
  * `is_array_member` (boolean): Nằm dưới mảng `[*]`.
  * `is_dynamic_map` (boolean): Khóa động (dữ liệu là key).
  * `json_types` (jsonb): Thống kê tần suất kiểu JSON thô (`{"string": 1200, "null": 5}`).
  * `inferred_type` (varchar(20)): Kiểu suy luận (`text`, `integer`, `numeric`, `boolean`, `timestamp`, `uuid`, `mixed`).
  * `int64_count` (bigint): Số lượng giá trị số vừa vặn kiểu 64-bit int để phân biệt chính xác `integer` vs `numeric`.
  * `value_shape` (jsonb): Thống kê biên độ độ dài (`minLen`, `maxLen`) và bộ đếm regex pattern (`uuid`, `digits`, `iso8601`, `other`) — **Tuyệt đối không lưu giá trị thật để ngăn ngừa rò rỉ PII**.
  * `occurrence_count` (bigint): Số lần xuất hiện.
  * `null_count` (bigint): Số lần xuất hiện nhưng giá trị rỗng/null.
  * `first_seen_at`, `last_seen_at`, `is_stale`.

#### Bảng 3: `catalog_shape`
- **Khóa chính:** `(source, data_type, shape_hash)`.
- **Thuật toán:** `shape_hash` tính bằng `xxHash64` trên tập các cặp `(path, kind)` đã được sắp xếp tăng dần và khử trùng lặp. Độc lập với thứ tự xuất hiện của thuộc tính trong payload JSON.

#### Bảng 4: `catalog_field_note`
- **Khóa chính:** `(source, data_type, path, tenant_id)`.
- **Cột:** `description` (varchar(250)), `described_at` (timestamptz), `described_by` (uuid).
- **Nguyên tắc ranh giới:** Bảng duy nhất có `tenant_id` chứa chú giải do con người định nghĩa; tiến trình quét tự động không bao giờ được phép ghi đè vào bảng này.

### 3.3. Endpoint Khám phá Cấu trúc: `POST /v1/events/{eventId}/analyze`

- **Đơn vị sở hữu:** Service `WiCX.Crm.Host` (schema `cdp`).
- **Xác thực & Quyền:** `Authorization: Bearer <sessionToken>`, quyền `cdp.events.analyze`.
- **Luồng xử lý:**
  1. Tra cứu bảng `wicx_eventarchive.event_archive` theo `(TenantId, EventId)`.
  2. Dùng `ILakeObjectReader` stream trực tiếp file JSON thô từ MinIO theo `ObjectKey`.
  3. Duyệt cấu trúc cây `Properties` (độ sâu tối đa 10, tối đa 500 path distinct, kích thước tối đa 512 KiB).
  4. Tính `SchemaHash` (SHA-256 chữ thường trên danh sách node `path|jsonKind` đã sort).
  5. Đối chiếu khóa duy nhất `ux_event_schemas_identity` (`TenantId + EventType + EventSource + ConnectorId + SchemaHash`):
     - Nếu đã tồn tại: Trả về bản ghi cũ kèm cờ `reused = true`.
     - Nếu chưa: Insert vào `cdp.event_schemas` và chi tiết các thuộc tính vào `cdp.event_schema_properties`.

### 3.4. Bộ máy Chiếu Dữ liệu (Projection Pipeline) & DDL Động An toàn

Toàn bộ dữ liệu sau khi trích xuất được lưu vào **Database độc lập `wicx_projection`**, schema `proj`, hoàn toàn tách biệt khỏi `wicx_dataextraction` và `wicx_crm` để bảo vệ EF Core ModelSnapshot không bị drift.

#### Cấu trúc Bảng Định nghĩa (Control Plane - DB `wicx_dataextraction`)
1. `projection_pipeline`: `id` (uuid PK), `tenant_id` (uuid), `code` (varchar(48)), `display_name`, `status` (`draft` | `active` | `paused` | `archived`), `version` (int), `source_filter` (jsonb), `record_key_expression`, `target_table`, `created_at`, `updated_at`.
2. `projection_field`: `id` (uuid PK), `pipeline_id` (FK), `ordinal` (int), `column_name` (varchar(63)), `source_path` (varchar(500)), `data_type` (varchar(20)), `transform` (varchar(200)), `is_required` (boolean), `default_value` (text), `is_indexed` (boolean), `added_in_version`, `retired_in_version`.
3. `projection_run`: `id`, `pipeline_id`, `tenant_id`, `kind` (`backfill` | `rebuild`), `status` (`queued` | `running` | `succeeded` | `failed` | `cancelled`), `window_from`, `window_to`, `cursor_stored_at`, `cursor_event_id`, `total_scanned`, `total_written`, `total_failed`.
4. `projection_error`: `id`, `pipeline_id`, `tenant_id`, `event_id`, `occurred_at`, `error_code`, `error_detail` (Không chứa PII).
5. `projection_ddl_log`: Nhật ký audit câu lệnh DDL vật lý đã thực thi.

#### Cấu trúc Bảng Sinh động (Data Plane - DB `wicx_projection`, schema `proj`)
Mọi bảng vật lý `proj."<code>"` luôn sở hữu 6 cột hệ thống bắt buộc trước các cột nghiệp vụ:
```sql
CREATE TABLE proj."form_consultation" (
    tenant_id          uuid        NOT NULL,
    record_key         text        NOT NULL,
    event_id           uuid        NOT NULL,
    occurred_at        timestamptz NOT NULL,
    definition_version int         NOT NULL,
    updated_at         timestamptz NOT NULL,
    -- Các cột dữ liệu người dùng ánh xạ:
    phone              text,
    full_name          text,
    email              text,
    district           text,
    PRIMARY KEY (tenant_id, record_key)
);
```

#### Quy tắc An toàn Tuyệt đối khi Sinh DDL (DDL Whitelist Rules)
1. Chỉ cho phép đúng 4 cú pháp DDL:
   - `CREATE SCHEMA IF NOT EXISTS proj`
   - `CREATE TABLE IF NOT EXISTS proj."..." (...)`
   - `ALTER TABLE proj."..." ADD COLUMN IF NOT EXISTS "..." <data_type>`
   - `CREATE INDEX CONCURRENTLY IF NOT EXISTS "..." ON proj."..." (...)`
2. **Nghiêm cấm hoàn toàn:** `DROP TABLE`, `DROP COLUMN`, `ALTER COLUMN TYPE`, `RENAME COLUMN`, `TRUNCATE`.
3. Khi thay đổi kiểu dữ liệu cột cũ: Hệ thống giữ nguyên cột cũ, đánh dấu `retired_in_version` và tạo cột mới với tên mới (`column_v2`).
4. Tên định danh bảng và cột bắt buộc phải thỏa mãn Regex `^[a-z][a-z0-9_]{0,62}$` và loại trừ danh sách từ khóa hệ thống của PostgreSQL.

#### Cú pháp Ghi Idempotent và Giải quyết Xung đột Thứ tự (Order Guard)
```sql
INSERT INTO proj."form_consultation" AS t (
    tenant_id, record_key, event_id, occurred_at, definition_version, updated_at, phone, full_name, email, district
) VALUES (
    @tenantId, @recordKey, @eventId, @occurredAt, @version, @updatedAt, @phone, @fullName, @email, @district
)
ON CONFLICT (tenant_id, record_key) DO UPDATE SET
    event_id           = EXCLUDED.event_id,
    occurred_at        = EXCLUDED.occurred_at,
    definition_version = EXCLUDED.definition_version,
    updated_at         = EXCLUDED.updated_at,
    phone              = EXCLUDED.phone,
    full_name          = EXCLUDED.full_name,
    email              = EXCLUDED.email,
    district           = EXCLUDED.district
WHERE (EXCLUDED.occurred_at, EXCLUDED.event_id) >= (t.occurred_at, t.event_id);
```
*Ghi chú:* Sử dụng điều kiện `>=` thay vì `>` để khi tiến trình Rebuild chạy lại trên cùng một tập dữ liệu lịch sử, các bản ghi có cùng `occurred_at` và `event_id` (UUIDv7) vẫn được phép ghi đè hợp lệ.

### 3.5. Tiến trình Nạp Dữ liệu Quá khứ qua Hangfire (Backfill Execution)

```
projection_run (queued)
      │
      ▼
Hangfire Worker (ProjectionBackfillJob)
      │
      ├─ 1. Quét wicx_dataextraction.event_processing:
      │     WHERE status = 'published' AND stored_at BETWEEN window_from AND window_to
      │     ORDER BY stored_at ASC, event_id ASC
      │     Phân trang mỗi lô 500 bản ghi (LIMIT 500)
      │
      ├─ 2. Đọc payload gốc từ MinIO:
      │     IRawObjectReader.GetAsync(bucket, objectKey)
      │
      ├─ 3. Dựng Canonical Event:
      │     Sử dụng chính CanonicalizationService thuần (không I/O)
      │
      ├─ 4. Ánh xạ & Ghi dữ liệu:
      │     Chạy bộ mapper thuộc tính -> Thực thi câu lệnh Upsert vào DB wicx_projection
      │
      └─ 5. Lưu checkpoint:
            Cập nhật cursor_stored_at, cursor_event_id, total_scanned, total_written vào projection_run
            Nghỉ 100ms giữa các lô để bảo vệ I/O MinIO
```

---

## 4. Tích hợp Giao diện & Quản lý State Frontend (Frontend State & Components)

Dựa trên phân tích mã nguồn `projects/wicx-crm-fe` kết hợp các mockup `/tmp/artifact_field_mapping`, kiến trúc phân hệ được tổ chức theo tiêu chuẩn Angular 18 Standalone:

### 4.1. Bản đồ Module & Định tuyến UI

```text
/cdp/data-raw
│
├── Tab 1: [Dữ liệu thô] (RawEventListComponent)
│     ├── TDS Table danh sách sự kiện (Paging, Keyword Search, Sort Direction, Source Tabs)
│     ├── Cột checkbox đa chọn (Selection signal<string[]>)
│     ├── Dòng mở rộng (Inline Expansion): JsonViewerComponent hiển thị cây JSON đa cấp
│     ├── Slide-over Drawer (640px): Xem metadata chi tiết và full raw payload từ API
│     └── Modal Diff so sánh: So sánh side-by-side 2 payload của 2 sự kiện đã chọn
│
└── Tab 2: [Mapping dữ liệu] (EventMappingComponent)
      ├── Panel Trái (320px): SourceListComponent
      │     ├── Input tìm kiếm (Tên, site_id, page_id)
      │     └── Danh sách Connector Items: Phân loại Website (cam), Facebook (xanh dương), Zalo (xanh cyan)
      │
      └── Panel Phải:
            ├── Màn hình Tổng quan Mặc định (Overview Dashboard):
            │     ├── Thẻ thống kê KPI: Tổng số trang | Cần cấu hình | Trường chưa map
            │     └── Hàng chờ xử lý (Action Required Queue)
            │
            ├── Màn hình Chi tiết Nguồn Website (WebSourceComponent):
            │     ├── Sub-tab 1: Sự kiện hành vi (Bảng 9 sự kiện: Gửi form, Click, Xem trang, Cuộn trang...)
            │     │     └── Nút mở Drawer "+ Tạo sự kiện" (CreateEventComponent - 720px)
            │     └── Sub-tab 2: Quản lý Form (Danh sách form phát hiện: /dang-ky, /lien-he)
            │           └── Nút "Cấu hình mapping" -> Chuyển sang Field Mapping Matrix
            │
            ├── Trình Biên tập Mapping Field (FieldMappingMatrixComponent):
            │     ├── Header: Tên Form, Đường dẫn, Sự kiện kích hoạt, Phiên bản hiện tại
            │     ├── Bảng ma trận ánh xạ 5 cột
            │     ├── Khối hướng dẫn kỹ thuật cho Web Team (Gợi ý gắn attribute `data-cdp`)
            │     └── Tác vụ: [Lịch sử thay đổi] (ReviewComponent), [Chạy thử] (TestRunComponent), [Lưu thay đổi]
            │
            ├── Màn hình Chạy thử Quy tắc (TestRunComponent):
            │     ├── Khung dán JSON thô (kèm nút "Lấy bản ghi gần nhất")
            │     ├── Quy trình hiển thị 4 bước xác thực (Lọc nguồn -> Nhận diện -> Chuẩn hóa -> Ghép định danh)
            │     └── Bảng đối chiếu Hồ sơ khách hàng Trước vs Sau nếu ghi thật
            │
            └── Màn hình Kiểm toán Lịch sử (ReviewComponent):
                  ├── Danh sách cây phiên bản (v3, v2, v1)
                  ├── Chi tiết sai khác (Diff Viewer: Thêm / Sửa / Chưa map)
                  └── Nút hoàn tác (Rollback) an toàn
```

### 4.2. Đặc tả Thành phần Giao diện & Thư viện `tds-ui`

| Màn hình / Thành phần | Component `tds-ui` sử dụng | Vai trò & Hành vi kỹ thuật |
|---|---|---|
| **Bộ lọc nguồn** | `TDSTabsModule` | Chuyển đổi linh hoạt giữa `Tất cả nguồn`, `WEBSITE`, `FACEBOOK`, `ZALO`, `TPOS`. Tự động cập nhật `selectedSource`. |
| **Bảng sự kiện thô** | `TDSDataTableModule` | Hỗ trợ phân trang máy chủ, virtual scroll `calc(100vh - 165px)`, sắp xếp cột `createdAt`. |
| **Cột mở rộng JSON** | `tds-row-expand`, `JsonViewerComponent` | Lazy-loading payload khi người dùng bấm mở rộng dòng, tránh quá tải băng thông mạng. |
| **Drawer chi tiết** | `TDSDrawerModule` | Kích thước 640px trượt từ phải sang, nút copy JSON vào clipboard, tag phân loại mã nguồn. |
| **Drawer tạo sự kiện** | `TDSDrawerModule` (720px) | Chứa form tạo điều kiện kích hoạt, multiselect chips chọn giá trị xuất hiện trong 30 ngày qua. |
| **Modal so sánh Diff** | `TDSModalModule` | So sánh 2 bản ghi payload được tick chọn từ danh sách, hỗ trợ toggle so sánh cấu trúc hoặc giá trị. |
| **Ma trận Mapping** | `TDSSelectModule` | Dropdown chọn trường CDP đích (`phone`, `name`, `email`, `custom_attributes`, `Không lưu`), chọn Pipe chuẩn hóa (`CH-SDT`, `CH-EMAIL`, `CH-TEN`, `Không áp dụng`) và cấp tin cậy (`Cao`, `Trung bình`, `Thấp`). |
| **Thông báo hệ thống** | `TDSMessageService` | Toast thông báo phản hồi thao tác (`Lưu thành công phiên bản mới`, `Đã sao chép vào clipboard`, `Cảnh báo chọn tối thiểu 2 bản ghi để so sánh`). |

### 4.3. Mô hình State Quản lý bằng Signal Store (`RawEventDataStore`)

```typescript
export interface RawEventItem {
  eventId: string;
  tenantId: string;
  tenantName: string;
  tenantSubName?: string;
  connectorId: string;
  source?: string;
  eventType?: string;
  createdAt: string;
  rawPayload?: object | string;
  loadingPayload?: boolean;
}

export interface FieldMappingRowState {
  sourceField: string;          // e.g. "form.tds-input-1"
  sampleValue: string;          // e.g. "0969733325"
  targetField: string;          // e.g. "phone" | "name" | "email" | "custom_attributes" | ""
  normalizationRule: string;    // e.g. "CH-SDT" | "CH-EMAIL" | "CH-TEN" | "none"
  confidenceLevel: string;      // e.g. "Cao" | "Trung bình" | "Thấp"
  isDirty: boolean;
}

export interface CustomEventCondition {
  id: number;
  attr: 'element_text' | 'element_tag' | 'element_class' | 'element_id' | 'href' | 'current_url' | 'utm_source';
  op: 'chứa' | 'bằng' | 'bắt đầu bằng' | 'khác' | 'có giá trị';
  vals: string[];
  query: string;
}
```

---

## 5. Ma trận Quy tắc Nghiệp vụ (Business Rules Matrix)

### 5.1. Bộ Quy tắc Chuẩn hóa Dữ liệu (Normalization Pipes)

| Mã Quy tắc | Tên gọi | Phạm vi Áp dụng | Thuật toán Thực thi | Ví dụ Trước -> Sau |
|---|---|---|---|---|
| **`CH-SDT`** | Chuẩn hóa Số điện thoại | Trường `phone` | 1. Xóa toàn bộ ký tự không phải số (`\D`).<br>2. Chuyển đổi đầu số nội địa (`03`, `05`, `07`, `08`, `09`) về chuẩn E.164 (`+84`).<br>3. Kiểm tra độ dài 9–11 chữ số. Bỏ qua nếu không hợp lệ. | `"0969 733 325"` -> `"+84969733325"`<br>`"84969733325"` -> `"+84969733325"` |
| **`CH-EMAIL`** | Chuẩn hóa Email | Trường `email` | 1. Loại bỏ khoảng trắng đầu và cuối (`trim`).<br>2. Chuyển đổi toàn bộ thành chữ thường (`lowercase`).<br>3. Kiểm tra tính hợp lệ bằng biểu thức chính quy RFC 5322. | `" TanSiDa@Gmail.COM "` -> `"tansida@gmail.com"` |
| **`CH-TEN`** | Chuẩn hóa Họ và Tên | Trường `name` | 1. Xóa khoảng cách thừa giữa các từ (`regex \s+ -> " "`).<br>2. Viết hoa chữ cái đầu tiên của từng từ (Title Case). | `"nguyễn   văn   tấn "` -> `"Nguyễn Văn Tấn"` |
| **`Không áp dụng`**| Giữ nguyên giá trị | Mọi trường khác | Giữ nguyên chuỗi gốc thu thập từ nguồn. | `"Quận 7, TP.HCM"` -> `"Quận 7, TP.HCM"` |

### 5.2. Cấp độ Tin cậy Định danh & Xử lý Gộp Hồ sơ (Identity Resolution - UC-3.01)

| Cấp độ | Định danh Tiêu biểu | Độ tin cậy Nghiệp vụ | Quy tắc Gộp & Ghi đè Hồ sơ Khách hàng |
|---|---|---|---|
| **Mạnh** (High) | Số điện thoại đã chuẩn hóa E.164, Email đã xác thực OTP | 1 người ↔ 1 giá trị duy nhất | - Khớp đúng 1 hồ sơ: Gộp event và toàn bộ dấu vết ẩn danh cũ vào hồ sơ.<br>- Chưa có hồ sơ: Tạo mới hồ sơ khách hàng (UC-3.03).<br>- Khớp ≥ 2 hồ sơ: Chuyển hàng chờ xử lý nghi trùng (UC-3.02), không tự ý gộp. |
| **Trung bình** (Medium) | Facebook PSID, Zalo User ID, Mã khách hàng sàn TMĐT | Duy nhất trong nền tảng nhưng có thể dùng chung | - Chỉ gộp xuyên kênh nếu định danh này **đã từng liên kết** với một định danh Mạnh trên hồ sơ.<br>- Nếu chưa có liên kết: Lưu hồ sơ mồ côi (UC-3.04). |
| **Yếu** (Low) | Web Cookie (`visitor_id`), IP, Thiết bị, Tên + Địa chỉ | Dễ biến động hoặc trùng lặp nhiều người | - Lưu hồ sơ khách vãng lai ẩn danh (Visitor).<br>- Khi khách gửi form có định danh Mạnh: Toàn bộ timeline sự kiện của `visitor_id` được chuyển quyền sở hữu sang hồ sơ chính thức. |

### 5.3. Quy tắc Lọc và Bảo vệ Dữ liệu Nền tảng

- **`LOC-02`:** Chỉ tiếp nhận sự kiện khi nguồn kết nối (`connectorId`) và biểu mẫu (`formId`) được bật trạng thái hoạt động trong danh mục của Tenant.
- **`LOC-03`:** Bộ lọc môi trường tự động loại bỏ các sự kiện xuất phát từ `localhost`, `127.0.0.1`, IP nội bộ hoặc domain staging.
- **`HN-01`:** Khóa gộp ưu tiên tuyệt đối theo Số điện thoại chuẩn hóa E.164.
- **`UT-01` / `UT-02`:** Nguyên tắc chống xóa dữ liệu — Không bao giờ dùng giá trị rỗng/null từ sự kiện mới để ghi đè lên các trường thông tin đã có giá trị trên hồ sơ khách hàng.

---

## 6. Kết luận & Đề xuất Lộ trình Triển khai (Roadmap)

1. **Giai đoạn 1 (Hoàn tất Core UI & Contracts):**
   - Hoàn thiện Micro-frontend `apps/mfe-cdp` trang `/cdp/data-raw` theo kiến trúc 2 tab (`RawData` và `EventMapping`).
   - Tích hợp trọn bộ `tds-ui` components và kiểm thử hiển thị với các mockup HTML.
2. **Giai đoạn 2 (Kết nối API Discovery & Preview):**
   - Đấu nối client `RawEventDataService` với endpoint `POST /v1/events/{eventId}/analyze` để tự động suy luận danh mục trường form.
   - Dựng API chạy thử `POST /v1/projections/preview` cho phép xem trước bảng đối chiếu dữ liệu trước khi bấm Lưu phiên bản.
3. **Giai đoạn 3 (Kích hoạt Projection Engine & DDL Scheduler):**
   - Bật consumer group `field-catalog-raw` trên topic `wicx.events.raw.v1` trong Helm chart.
   - Hoàn thiện bộ máy sinh DDL an toàn trên database `wicx_projection` và kích hoạt Hangfire backfill job cho các biểu mẫu cũ.