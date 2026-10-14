# AGENTS.md - Global Workspace Directives & Multi-Agent Execution Protocols

> **QUY CHUẨN ĐỒNG BỘ TOÀN HỆ THỐNG**: Mọi Agent hoạt động trong workspace `/home/baoltb/Desktop/Paseo_Project` phải tuân thủ nghiêm ngặt các nguyên tắc, đường dẫn chuẩn và luồng phối hợp kế thừa từ **Obsidian Knowledge Base** (`/home/baoltb/Desktop/obsidian-obsidian`).

---

## 1. Workspace Identity & Canonical Paths

- **Root Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Frontend Source Code**: `/home/baoltb/Desktop/Paseo_Project/projects/crm-fe` (Angular 18, Module Federation, Nx, UI-Lib)
- **REMOTE Docs Repository**: `/home/baoltb/Desktop/crm-doc` (REMOTE `_git/crm` branch `docs/base`)
- **Obsidian Knowledge Base**: `/home/baoltb/Desktop/obsidian-obsidian` (Specs, ADRs, Protocols, Beats, Metas)
- **Harness Cloud Storage**: Floci DynamoDB & S3 (`http://<FLOCI_HOST>:14566`, Web UI `http://<FLOCI_HOST>:4566`)
- **REMOTE Azure DevOps Server**: `https://remote.example.com/MainCollection/ACME` (via MCP `remote-crm`)

---

## 2. Team Multi-Agent Roles & Workflow Gates

Mọi tác vụ phải tuân thủ nghiêm ngặt quy trình chuyển giao qua các cổng kiểm soát (Workflow Gates):

```text
[Yêu cầu từ User]
       │
       ▼
1. BA (Analysis) ────► Bóc tách Use Case, AC & đồng bộ vào Harness / Docs
       │
       ▼
2. Scrum Master ──► Kích hoạt & Điều phối Gates trên Harness:
       ├──► 3. API Analyst  [Cổng: Contract READY / Swagger Mock]
       ├──► 4. Architect    [Cổng: MFE Arch & Token Mapping APPROVED]
       ├──► 5. FE Dev          [Cổng: Green Build & AC Implemented in projects/crm-fe]
       ├──► 6. Code Reviewer     [Cổng: Review APPROVED & Clean Diff]
       └──► 7. QC & Release [Cổng: QC PASSED & Test Matrix Verified]
       │
       ▼
[Task DONE]
```

### Chi tiết vai trò:
1. **BA (`ba`, `crm-doc-read`)**: Phân tích nghiệp vụ từ REMOTE Use Cases (`UC1.01`..`UC4.09`), viết Acceptance Criteria (AC), quản lý `docs/spec/`.
2. **Scrum Master (`scrum-master`, `harness-ops`)**: Quản trị bảng điều khiển Harness, theo dõi trạng thái `New ➔ Accepted ➔ Active ➔ Resolved ➔ Closed`, kiểm soát gates.
3. **API Analyst (`api-analyst`)**: Swagger/OpenAPI contracts, Ingestion APIs, mock data mapping.
4. **Architect & Reviewer (`grandmaster`, `code-review`)**: Thiết kế kiến trúc Micro-Frontend, module boundaries, audit token UI-Lib, duyệt PR.
5. **Frontend Engineer (`angular-fe`, `fe-jr`, `ui-lib-usage`, `ui-lib-figma`)**: Lập trình Angular 18 tại `projects/crm-fe/`, sử dụng UI Lib tokens, tuân thủ TDD.
6. **QC & Tester (`qc`, `automation-functional-testing`)**: Viết E2E test cases, xác thực `verify_command` và cập nhật Test Matrix trên Harness.

---

## 3. Available Tools & Skills Index

### A. Harness Manager Tool (`tools/harness_manager.py` / Skill `harness-ops`)
- **Lưu trữ**: Floci DynamoDB endpoint `http://<FLOCI_HOST>:14566` (tables `harness_work_items`, `harness_stories`, `harness_tools`, `harness_metadata`).
- **Lệnh thực thi**:
  - Xem ma trận kiểm thử: `./scripts/harness query matrix`
  - Xem backlog đa chiều: `./scripts/harness query backlog [--sprint <sprint>] [--source remote|local] [--top 25]`
  - Xem thống kê: `./scripts/harness query stats`
  - Đồng bộ lại từ REMOTE: `./scripts/harness sync-remote`
  - Thêm mới / Cập nhật trạng thái: `python3 tools/harness_manager.py add ...` | `python3 tools/harness_manager.py update ...`

### B. REMOTE ACME MCP Server (`tools/remote_mcp_server.py`)
- **Server**: `remote-crm` (cấu hình trong `~/.gemini/config/mcp_config.json`).
- **Tools**: `remote_list_work_items`, `remote_get_work_item`, `remote_query_wiql`, `remote_list_repositories`, `remote_list_pull_requests`, `remote_search_use_cases`, `remote_get_use_case`, `remote_sync_docs`, `remote_list_doc_tree`, `remote_git_status`, `remote_git_log`.

### C. Query Reader Tool (`tools/query_reader.py` / Skill `query-read`)
- **Mục đích**: Duyệt cấu trúc thư mục chống lỗi `EISDIR`, tìm kiếm ngữ cảnh chính xác cao bằng thuật toán BM25.
- **Lệnh thực thi**: `python3 tools/query_reader.py <folder_path> ["<từ_khóa>"]`

### D. UI-Lib & Figma Skills (`ui-lib-usage`, `ui-lib-figma`)
- **`ui-lib-figma`**: Token lookup qua `ui-token-lookup.js`, chuyển đổi Figma sang Angular UI Lib.
- **`ui-lib-usage`**: Danh mục gần 80 components UI Lib, recipes, troubleshooting.

---

## 4. Coding & Operation Rules
1. **Lazy Senior Developer Philosophy**:
   - Stdlib & Native Platform trước tiên.
   - Đọc kỹ source code và specs trước khi chỉnh sửa.
   - Diff ngắn gọn, giữ nguyên code style hiện tại, không thêm boilerplate thừa.
2. **Path Integrity**:
   - Luôn sử dụng đường dẫn tuyệt đối khi thao tác file.
   - Mã nguồn FE luôn trỏ về `/home/baoltb/Desktop/Paseo_Project/projects/crm-fe`.
3. **No Raw HTML in Data**:
   - Dữ liệu bóc tách từ REMOTE hoặc nạp vào DynamoDB/Harness bắt buộc phải được làm sạch qua `clean_html()` để loại bỏ thẻ HTML.
