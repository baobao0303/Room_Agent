# Paseo Project Workspace

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
│       ├── tds-ui-figma/    # Skill phân tích & chuyển đổi Figma sang TDS Angular
│       ├── tds-ui-usage/    # Skill tra cứu API & mẫu code Angular TDS-UI
│       ├── crm-doc-read/   # Skill tra cứu User Stories & Specs từ REMOTE crm
│       └── workflow-launch-exec/     # Skill điều phối thực thi workflow đa tác nhân
├── docs/                    # Tài liệu đặc tả và thiết kế
│   └── spec/                # Đặc tả chia theo từng dự án
│       ├── README.md
│       └── <project-name>/  # Thư mục spec dự án cụ thể
│           ├── ba/          # User Stories, Acceptance Criteria (BA)
│           ├── design/      # Figma Component & Token Mapping (Design)
│           └── dev/         # API Contracts, Architecture, DTOs (Dev)
├── projects/                # Thư mục chứa mã nguồn các dự án thực tế
├── tools/                   # Bộ công cụ mở rộng
│   ├── README.md
│   ├── floci_client.py      # Client DynamoDB & S3 kết nối Floci emulator
│   ├── harness_manager.py   # Tool quản lý Work Items & State Machine (SQLite + Floci)
│   ├── query_reader.py      # Tool đọc file/thư mục thông minh theo query (BM25 + Semantic Chunking)
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

## 2. Hướng dẫn sử dụng Tools

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

### B. Tool Research (`tools/research/`)

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
# Room_Agent
