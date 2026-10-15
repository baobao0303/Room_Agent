# Room_Agent — Paseo Project Workspace

Không gian làm việc cho các Agent và Tool tích hợp của Paseo.

## 1. Cấu trúc thư mục

```text
.
├── .agents/                 # Cấu hình và tài nguyên của Agent
│   └── skills/              # Các bộ kỹ năng mở rộng (Skills)
│       ├── README.md
│       ├── doc-updater/     # Skill cập nhật & đồng bộ tài liệu đặc tả và AGENTS.md
│       ├── fewer-permission-prompts/ # Skill tối ưu cấu hình quyền tự động
│       ├── harness-ops/     # Skill quản trị SDLC, State Machine & Matrix theo Harness
│       ├── hermes-research/ # Skill nghiên cứu kỹ thuật & xuất báo cáo Markdown
│       ├── mattpocock-skills/# Bộ kỹ năng kỹ thuật & năng suất chuẩn Matt Pocock
│       ├── query-read/      # Skill tìm kiếm ngữ cảnh BM25 & duyệt thư mục an toàn
│       ├── ui-lib-figma/    # Skill phân tích & chuyển đổi Figma sang UI Angular
│       ├── ui-lib-usage/    # Skill tra cứu API & mẫu code Angular UI-Lib
│       ├── crm-doc-read/   # Skill tra cứu User Stories & Specs từ REMOTE crm
│       └── workflow-launch-exec/     # Skill điều phối thực thi workflow đa tác nhân
├── docs/                    # Tài liệu đặc tả và thiết kế
│   └── spec/                # Đặc tả chia theo từng dự án
│       ├── README.md
│       └── <project-name>/  # Thư mục spec dự án cụ thể
│           ├── ba/          # User Stories, Acceptance Criteria (BA)
│           ├── design/      # Figma Component & Token Mapping (Design)
│           └── dev/         # API Contracts, Architecture, DTOs (Dev)
├── profiles/                # Profile agent: supervisor, lead, peer, qc
├── scripts/                 # Harness CLI, dashboard UI, init/seed DB
│   ├── harness              # CLI chính (./scripts/harness)
│   └── harness_dashboard.py # Dashboard realtime (UI web)
├── setup_harness.sh         # Setup Harness lần đầu
├── projects/                # Thư mục chứa mã nguồn các dự án thực tế
├── tools/                   # Bộ công cụ mở rộng
│   ├── README.md
│   ├── floci_client.py      # Client DynamoDB & S3 kết nối Floci emulator
│   ├── harness_manager.py   # Tool quản lý Work Items & State Machine (SQLite + Floci)
│   ├── query_reader.py      # Tool đọc file/thư mục thông minh theo query (BM25 + Semantic Chunking)
│   ├── qc_test_generator.py # Tool sinh Testcase & Unit Test 5-Stage ISTQB Pipeline
│   └── research/            # Tool nghiên cứu (Hermes 3-Tier Prompt & Gateway)
│       ├── codex_room_setup_research.md
│       ├── harness_framework_research.md
│       ├── hermes_spec.md
│       ├── hermes_research_client.py
│       ├── research_agent.py
│       ├── research_agent.ts
│       └── README.md
└── README.md
```

## 2. Chạy Harness & Dashboard UI

### A. Setup lần đầu
```bash
cp .env.example .env          # điền FLOCI_ENDPOINT, AWS_*, ...
./setup_harness.sh            # tạo .env nếu thiếu, init bảng, seed, kiểm tra
```

### B. Harness CLI (`./scripts/harness`)
```bash
./scripts/harness init                      # Khởi tạo bảng DynamoDB & S3
./scripts/harness seed                      # Seed dữ liệu mẫu
./scripts/harness query stats               # Thống kê
./scripts/harness query matrix [--source remote|local]
./scripts/harness query backlog [--sprint "Sprint 1"] [--type Task] [--state Active] [--source remote|local] [--top 25]
./scripts/harness query item <id>
./scripts/harness query tools [--json] [--responsibility <r>]
./scripts/harness sync-remote               # Đồng bộ backlog từ remote
./scripts/harness work-item ...             # Quản lý work item
```

### C. Dashboard UI (realtime)
```bash
python3 scripts/harness_dashboard.py          # Sinh /tmp/harness_dashboard.html + chạy server nền, cổng 8765
python3 scripts/harness_dashboard.py --serve  # Chạy foreground, cổng 8765
```
Mở `http://localhost:8765`.

## 3. Hướng dẫn sử dụng Tools

### A. Harness Manager Tool (`tools/harness_manager.py`)
Quản lý Work Item chuẩn Company DDD và State Machine:
```bash
# Thêm User Story mới (validate chuẩn BDD Description và Title)
python3 tools/harness_manager.py add --type "User Story" \
  --title "[Auth] – Người dùng có thể đăng nhập bằng OTP" \
  --description "As a User, I want đăng nhập bằng OTP, So that bảo mật tài khoản." \
  --priority P1 --story-points 3

# Chuyển trạng thái Work Item và phân công cho Profile Paseo
python3 tools/harness_manager.py update --id 1 --state Accepted --assigned-to "Lead BA"
python3 tools/harness_manager.py update --id 1 --state Active --assigned-to "Peer Dev"

# Xem danh sách và thống kê
python3 tools/harness_manager.py list --state Active
python3 tools/harness_manager.py stats
python3 tools/harness_manager.py profiles
```

### B. Query Reader Tool (`tools/query_reader.py`)
Giải quyết triệt để lỗi `EISDIR` khi đọc folder và tìm kiếm nội dung chính xác:
- **Xem cây thư mục an toàn**:
  ```bash
  python3 tools/query_reader.py <folder_path>
  ```
- **Tìm kiếm nội dung theo câu hỏi/từ khóa (Ranking BM25)**:
  ```bash
  python3 tools/query_reader.py <path> "<câu hỏi hoặc từ khóa>"
  ```
- **Xuất dữ liệu dạng JSON**:
  ```bash
  python3 tools/query_reader.py <path> "<query>" -j
  ```

### C. QC Agent & Test Generator (`profiles/qc.md`, `tools/qc_test_generator.py`)
QC là vai trò thứ 4 trong kiến trúc SLPC (`Supervisor - Lead - Peer - QC`), đóng vai trò Test Architect & Independent Quality Gate:
- **Profile QC**: Cấu hình tại `profiles/qc.md`, phụ trách sinh test case truy vết, thẩm định khi Peer chuyển `Resolved`, và nghiệm thu đóng task sang `Closed`.
- **5-Stage ISTQB Pipeline (`tools/qc_test_generator.py`)**:
  - Stage 1: Phân tích Spec & AST Codebase (`RequirementAnalysis`).
  - Stage 2: Xác định Test Points trên 9 dimensions (`TestPointSet`).
  - Stage 3: Lập Test Design Plan theo 7 kỹ thuật ISTQB (`CoverageItem`).
  - Stage 4: Sinh Test Cases & mã kiểm thử tự động (`*.spec.ts` / `test_*.py`) và đồng bộ lên Harness DB.
  - Stage 5: Báo cáo độ phủ và cổng kiểm định tự động (Zero LLM self-grading).

```bash
# Sinh test case và unit test từ Spec + Source:
python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> --task-id <id> --out-spec <path/to/file.spec.ts> --sync-harness

# Chạy test runner & kiểm định độ phủ:
python3 tools/qc_test_generator.py --source <path/to/file.ts> --task-id <id> --run --verify-cmd "npm test"
```

### D. Tool Research (`tools/research/`)

#### 1. Chuẩn bị (Tùy chọn)
Chạy Hermes Gateway nếu muốn gửi qua HTTP API:
```bash
hermes gateway
```
*(Nếu không bật Gateway, tool tự động fallback chạy trực tiếp qua Hermes CLI).*

#### 2. Chạy Research Agent (Python)
```bash
python3 tools/research/research_agent.py "Phân tích kiến trúc Microservices vs Monolith"
```
Kết quả báo cáo Markdown sẽ tự động lưu vào `tools/research/<tên_chủ_đề>.md`.

#### 3. Chạy Research Agent (TypeScript / Node)
```bash
npx tsx tools/research/research_agent.ts "Đánh giá Redis Cache Pattern"
```
