# Tools Directory - Cấu Trúc Bộ Công Cụ Dự Án Paseo

Thư mục chứa toàn bộ các công cụ bổ trợ, CLI và script tự động hóa dành cho các Agent (`Supervisor`, `Lead`, `Peer`, `QC`) và nhà phát triển trong hệ thống SLPC.

---

## 📂 Phân Loại Cấu Trúc Thư Mục

```text
tools/
├── tests/                     # Toàn bộ test suite kiểm thử cho các tools
│   ├── test_harness.py        # Kiểm thử tích hợp Harness Manager & Floci DynamoDB
│   ├── test_qc_generator.py   # Kiểm thử quy chuẩn 5-Stage ISTQB QC Generator
│   └── test_tds_search.py     # Kiểm thử cổng tra cứu TDS UI Component Gateway
├── research/                  # Bộ công cụ nghiên cứu kỹ thuật & Hermes Gateway
│   ├── research_agent.py      # Sub-agent nghiên cứu kỹ thuật đa tầng (Hermes / Router9)
│   ├── hermes_research_client.py # Client kết nối Hermes Gateway
│   └── reports/               # Lưu trữ các báo cáo nghiên cứu kỹ thuật dạng Markdown
│       ├── raw_data_mapping_step_1_channel_con.md
│       ├── tds_icon_list_from_https_tds_tmtco_.md
│       ├── codex_room_setup_research.md
│       └── harness_framework_research.md
├── harness_manager.py         # Quản trị Work Items & State Machine trên Floci DynamoDB
├── harness_doctor.py          # Continuous Doctor Health Monitor & Auto-Healer
├── floci_client.py            # Client kết nối Floci DynamoDB & S3 Local
├── agent_progress.py          # Sổ cái Tiến độ & Quản lý Handoff Ledger (docs/AGENT_PROGRESS.md)
├── call_agent.py              # CLI Runner điều phối kích hoạt 4 Role SLPC
├── paseo_hooks.py             # CLI điều khiển Paseo Daemon Lifecycle Hooks
├── profile_research_gen.py    # Pipeline ép cổng Research & Gen Brief tự động
├── qc_test_generator.py       # Bộ sinh Test Matrix & Unit Test 5-Stage ISTQB
├── query_reader.py            # Đọc ngữ cảnh thông minh, chống lỗi EISDIR, xếp hạng BM25
├── tds_search.py              # Tra cứu nhanh offline và online cho thư viện TDS UI Angular
├── crm_doc_reader.py          # Tra cứu tài liệu nghiệp vụ từ repo TFS wicx-crm doc/base
├── distill_ba_beats.py        # Chắt lọc tài liệu BA thành các beat ngắn gọn
├── remote_mcp_server.py       # MCP Server kết nối TFS / Azure DevOps Server
├── remote_sync.py             # Đồng bộ toàn bộ backlog từ TFS về Floci DynamoDB
└── doc_sync.py                # Đồng bộ và kiểm tra cấu trúc đặc tả trong docs/spec/
```

---

## 🛠️ Danh Mục Công Cụ Theo Nhóm Nghiệp Vụ

### 1. Điều Phối Đa Agent & Quản Trị Tiến Độ (SLPC & Orchestration)
- **`agent_progress.py`**: Xem trạng thái và ghi nhận bàn giao giữa các phiên làm việc.
  ```bash
  python3 tools/agent_progress.py status
  python3 tools/agent_progress.py log --agent "Peer" --summary "..." --done "..." --next "..."
  ```
- **`call_agent.py`**: Kích hoạt vai trò cụ thể (`supervisor`, `lead`, `peer`, `qc`).
  ```bash
  python3 tools/call_agent.py --role supervisor --prompt "..."
  ```
- **`profile_research_gen.py`**: Tự động hóa khâu Research + Gen Brief theo đặc tả trước khi lập trình.
  ```bash
  python3 tools/profile_research_gen.py --profile "Supervisor" --topic "..."
  ```
- **`paseo_hooks.py`**: Kiểm tra và điều khiển Paseo Daemon Lifecycle Hooks (Port 6767).
  ```bash
  python3 tools/paseo_hooks.py status
  ```

### 2. Kiểm Thử & Đảm Bảo Chất Lượng (Quality Assurance & Testing)
- **`qc_test_generator.py`**: Sinh test case và file unit test chuẩn ISTQB 5-Stage.
  ```bash
  python3 tools/qc_test_generator.py --source <file.ts> --spec <spec.md> --task-id <id> --out-spec <test.spec.ts>
  ```
- **`tests/`**: Toàn bộ unit tests cho tools được gom gọn độc lập tại `tools/tests/`:
  ```bash
  python3 -c "import unittest; unittest.main(module=None, argv=['unittest', 'discover', '-s', 'tools/tests'])"
  ```

### 3. Lưu Trữ Phân Tán & Quản Lý Backlog (Harness & Floci)
- **`harness_manager.py`**: Thao tác CRUD và chuyển đổi trạng thái Work Item trên Floci DynamoDB (317 items).
  ```bash
  python3 tools/harness_manager.py list --status Active
  ./scripts/harness query matrix
  ```
- **`harness_doctor.py`**: Chẩn đoán kết nối Floci, cấu trúc bảng DynamoDB và sửa lỗi tự động.
  ```bash
  python3 tools/harness_doctor.py --check
  ```
- **`floci_client.py`**: Client tầng thấp tương tác trực tiếp với DynamoDB & S3 trên Floci.
- **`remote_sync.py`**: Đồng bộ dữ liệu mới nhất từ Azure DevOps Server về Floci:
  ```bash
  ./scripts/harness sync-remote
  ```

### 4. Đọc Dữ Liệu & Tra Cứu Thông Minh (Search & Reading Engine)
- **`query_reader.py`**: Đọc thư mục/file an toàn chống tràn context, trích xuất đoạn văn theo BM25.
  ```bash
  python3 tools/query_reader.py <folder_path> ["keyword"]
  ```
- **`crm_doc_reader.py`**: Tra cứu Use Case (UC1.01..UC4.09) từ kho tài liệu gốc.
  ```bash
  python3 tools/crm_doc_reader.py --uc UC4.01
  ```
- **`distill_ba_beats.py`**: Chuyển đổi đặc tả dài thành các beat hành động ngắn cho dev.

### 5. Giao Diện & Thiết Kế (UI & Design System)
- **`tds_search.py`**: Tra cứu selector, input, output và code ví dụ của 92+ component TDS UI.
  ```bash
  python3 tools/tds_search.py "table"
  python3 tools/tds_search.py --catalog
  ```

### 6. Nghiên Cứu Kỹ Thuật (Research Sub-Agent)
- **`research/research_agent.py`**: Tổng hợp kiến trúc đa tầng qua Router9 / Hermes Gateway:
  ```bash
  python3 tools/research/research_agent.py "Kiến trúc Module Federation 2.0"
  ```
