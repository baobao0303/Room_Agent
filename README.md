# Room_Agent — Paseo SLPPC Multi-Agent Workspace

Không gian làm việc điều hành đa tác nhân theo mô hình **SLPPC (Supervisor - PM - Lead - Peer - QC)** tích hợp hệ điều hành **Paseo**, **Hermes Agent** và **Harness Framework v0.1.14**.

---

## ⚡ CÀI ĐẶT 1 BƯỚC (ONE-COMMAND SETUP)

Khi clone repository về máy nhà hoặc máy trạm mới, chỉ cần chạy **1 lệnh duy nhất**:

```bash
./setup.sh
```

Hoặc vừa cấu hình môi trường, vừa tự động mở sẵn toàn bộ **9 Agent tabs** trực tiếp trên Orca Desktop:

```bash
./setup.sh --launch
# hoặc: ./scripts/launch_room.sh
```

### Script tự động thực hiện trọn gói:
1. **Kiểm tra công cụ cơ sở**: Tự động nhận diện `python3`, `git`, `orca`, `hermes`.
2. **Cấu hình `.env`**: Khởi tạo cấu hình với model chuẩn `ag/gemini-3.8-flash-high`.
3. **Master Skills Tree (85+ Skills)**: Quản lý tập trung tại thư mục canonical `skills/<tên>/SKILL.md`, tự động symlink vào `~/.hermes/skills/`.
4. **Đồng bộ 9 Profiles SLPPC**: Tự động đăng ký `Supervisor`, `PM Agent`, `Lead Dev`, `Peer Dev 1..4`, `Peer Design`, `QC`, `Security Sentinel` vào `~/.paseo/config.json`.
5. **Cài đặt Git Pre-Commit Guard**: Tự động kích hoạt hook kiểm soát thẩm quyền vai trò và chống mã màu hex cứng.
6. **Đồng bộ Harness DB & Aevum Kanban**: Khởi tạo kết nối Floci DynamoDB Cloud (`:14566`) và tự động kích hoạt cơ chế Local Fallback nếu Floci offline.
7. **Khởi chạy Multi-Agent Room**: (Khi dùng cờ `--launch` hoặc chạy `./scripts/launch_room.sh`).

---

## 1. Mô Hình Điều Hành Phòng Ban SLPPC & 5 Cổng Kiểm Soát

Mọi tác vụ kỹ thuật trong workspace tuân thủ quy trình chuyển giao qua 5 cổng kiểm soát độc lập:

```text
[Yêu cầu từ User]
       │
       ▼
1. Supervisor (Scope & Intent Guard) ──► Tiếp nhận ý định User, tạo Epic/Task, cấm can thiệp code
       │
       ▼
2. PM Agent (Feasibility & Alignment) ─► Thẩm định Khả thi / Phù hợp qua Kev System One (<50ms)
       │
       ▼
3. Lead Dev (Architect & Technical PM) ─► Thiết kế kiến trúc, tra cứu bài học cũ, phân rã Zero-Search (Cấm tự code)
       │
       ▼
4. Peer Devs (Code Executors 1..4) ───► Lập trình theo spec, tuân thủ Strict Typing, nộp Resolved (Cấm tự đóng task)
       │
       ▼
5. QC (Quality Gate & Test Architect) ─► Sinh testcase 5-Stage ISTQB, kiểm tra anti-leak, độc quyền nghiệm thu & Closed
       │
       ▼
[Task CLOSED]
```

### Chi Tiết Phân Quyền Các Vai Trò:
1. **Supervisor (`supervisor`)**: Scope & Intent Guard. Kênh giao tiếp độc nhất với User. Phân tích phạm vi, tạo Epic/Task trên Harness DB (`--engine auto`), điều phối PM/Lead/Peer và kiểm soát rủi ro. Tuyệt đối cấm can thiệp code (`role_trespass`).
2. **PM Agent (`pm`)**: Product Manager & Decision Arbiter (Kev System One Engine). Cố vấn định lượng ngầm cho Supervisor & Lead: đánh giá mức độ **Khả thi (Feasibility 0..3)** và **Phù hợp (Alignment)**, phân luồng sub-50ms trước khi phân rã task. Chặn đứng lỗi `pm_bypass`.
3. **Lead Dev (`lead`)**: Technical Architect & PM. Thiết kế kiến trúc hệ thống, tra cứu bài học cũ qua `harness learn query`, duyệt giải pháp kỹ thuật và phân rã task Zero-Search 5 thành phần cho Peer. Nghiêm cấm tự ý code (`role_trespass`).
4. **Peer Devs (`peer`, `peer2`, `peer3`, `peer4`, `design`)**: Code Executors (4 bậc tiết kiệm token: Low, Medium, High, Extra). Lập trình theo spec, tuân thủ Strict Typing (0% `any`, 0% `unknown`), nộp `Resolved`. Nghiêm cấm tự tiện đóng task (`premature_close`).
5. **QC (`qc`)**: Independent Quality Gate & Test Architect. Độc quyền quyền hạn chuyển trạng thái task sang `Closed`. Nghiệm thu độc lập, sinh testcase theo chuẩn ISTQB 5-Stage (`tools/qc_test_generator.py`), xác nhận Acceptance Criteria và chạy audit bảo đảm 100% tuân thủ quy trình.
6. **Security Sentinel (`security`)**: Continuous Anti-Leak Gatekeeper & Open-Source Auditor. Giám sát liên tục chống lộ API spec tính năng, luồng nghiệp vụ FE, địa chỉ công ty và secrets; sở hữu quyền VETO chặn đứng mọi commit/push vi phạm.

---

## 2. Cấu Trúc Thư Mục Chuẩn (Directory Architecture)

```text
.
├── setup.sh                   # Script cài đặt 1 bước trọn gói all-in-one
├── setup_harness.sh           # Script thiết lập nhanh cấu hình Harness và Floci
├── patch_paseo.py             # Script đồng bộ 9 Agent Profiles vào cấu hình Paseo daemon
├── AGENTS.md                  # Quy chuẩn điều hành & pháp lệnh rào cản SLPPC toàn hệ thống
├── profiles/                  # Hồ sơ 9 Agent: supervisor, pm, lead, peer, peer_2..4, peer_design, qc, security
├── skills/                    # Master Skills Registry (85+ skills canonical dạng skills/<name>/SKILL.md)
├── docs/                      # Tài liệu đặc tả và thiết kế
│   ├── spec/                  # Đặc tả kỹ thuật các tính năng, nâng cấp & phân hệ
│   │   ├── harness-cli-v0.1.14-upgrade-spec.md # Bản đặc tả nâng cấp v0.1.14 & SLPPC
│   │   ├── kev-system-one-spec.md              # Chuẩn wire protocol Kev TypeSafe System One
│   │   └── shop-user-list-context-spec.md      # Đặc tả kỹ thuật Context Provider
│   └── AGENT_PROGRESS.md      # Sổ cái ghi nhận tiến độ liên tục & bàn giao đa tác nhân
├── bmad/                      # Bộ não tri thức kiến trúc tập trung
│   ├── architecture.json      # Đồ thị tương tác module & ranh giới hệ thống
│   ├── rooms/                 # Không gian bàn giao của các Agent (supervisor, pm, lead, peer, qc)
│   └── rooms/violations/      # Sổ cái biên bản vi phạm kỷ luật (role_trespass, pm_bypass...)
├── scripts/                   # Bộ kịch bản vận hành & khởi chạy
│   ├── harness                # CLI quản lý Harness chính thức (./scripts/harness)
│   ├── harness_dashboard.py   # Web Dashboard realtime giám sát Work Items (cổng :8765)
│   ├── launch_room.sh         # Khởi chạy đồng bộ 9 agent terminals trên Orca Workspace
│   ├── anti_leak_sentinel.py  # Script kiểm tra an ninh chống rò rỉ dữ liệu trước commit
│   ├── git_pre_commit_guard.py# Hook Git tự động bảo vệ token màu và rào cản vai trò
│   ├── start_aevum.sh         # Khởi động ứng dụng Aevum Workspace (:8080 :3010)
│   ├── bin/harness-cli        # Native Rust CLI v0.1.14 (supervise, learn, work-item)
│   └── schema/                # Các migrations SQL SQLite (001-init đến 007-experience)
├── tools/                     # Bộ công cụ điều hành hệ thống
│   ├── harness_manager.py     # Quản lý Work Items Floci DynamoDB & SQLite (--engine auto)
│   ├── harness_rust.py        # Python-Rust Typed Bridge kết nối Kev System One & Learning Store
│   ├── harness_learning_search.py # Tra cứu, thẩm định và thanh trừng bài học tự học tào lao
│   ├── slppc_flow_guard.py    # Bộ canh gác rào cản vai trò và quy trình SLPPC
│   ├── agent_heartbeat.py     # Theo dõi nhịp tim 9 agent & cảnh báo sức khỏe tri thức realtime
│   ├── agent_progress.py      # Ghi nhận và truy vấn sổ cái tiến độ bàn giao
│   ├── floci_client.py        # Client DynamoDB & S3 kết nối Floci Cloud (:14566)
│   ├── query_reader.py        # Tool đọc file/thư mục thông minh theo query (BM25 + chống EISDIR)
│   ├── qc_test_generator.py   # Máy sinh Testcase & Unit Test 5-Stage ISTQB Pipeline
│   ├── skill_manager.py       # Quản trị Master Skills Registry & Inverted Index DB Search
│   ├── tds_search.py          # Tra cứu offline components, APIs và tokens TDS UI
│   └── research/              # Tool nghiên cứu kỹ thuật (Hermes 3-Tier Prompt & Gateway)
├── .github/workflows/
│   ├── ci.yml                 # Pipeline CI kiểm tra lint và unit tests
│   └── slppc-governance-guard.yml # Pipeline CI kiểm soát an ninh & quy trình tự động trên PR
└── README.md
```

---

## 3. Chạy Harness CLI & Dashboard UI

### A. Khởi tạo ban đầu
```bash
cp .env.example .env          # Điền FLOCI_ENDPOINT, AWS_* nếu có cấu hình riêng
./setup_harness.sh            # Tạo .env, khởi tạo bảng DynamoDB & S3, seed dữ liệu mẫu
```

### B. Python Harness CLI Wrapper (`./scripts/harness`)
CLI chính thức quản trị cơ sở dữ liệu Floci DynamoDB & S3:
```bash
./scripts/harness init                      # Khởi tạo bảng DynamoDB & S3 trên Floci
./scripts/harness seed                      # Seed dữ liệu mẫu ban đầu
./scripts/harness query stats               # Xem thống kê tổng hợp Work Items
./scripts/harness query matrix [--source remote|local] # Xem ma trận kiểm thử
./scripts/harness query backlog [--sprint "Sprint 1"] [--type Task] [--state Active] [--top 25]
./scripts/harness query item <id>           # Xem chi tiết một Work Item
./scripts/harness query tools [--json]      # Xem danh mục công cụ đã đăng ký
./scripts/harness sync-remote               # Đồng bộ backlog từ nguồn remote
./scripts/harness work-item ...             # Quản trị Work Item qua harness_manager
./scripts/harness doctor                    # Kiểm tra sức khỏe toàn diện hệ sinh thái
```

### C. Native Rust Binary CLI (`scripts/bin/harness-cli`)
Phiên bản nhị phân native Rust v0.1.14 biên dịch sẵn, khởi chạy siêu tốc (<10ms):
```bash
# Phân luồng rủi ro tác vụ qua Kev System One (<50ms)
./scripts/bin/harness-cli supervise evaluate --text "Refactor context provider" --json

# Ghi nhận bài học tự học mới
./scripts/bin/harness-cli learn record --domain "angular_fe" --cue "strict_typing" \
  --lesson "Map DTO tường minh, cấm dùng any/unknown" --evidence "pass 243 tests" --confidence high

# Tra cứu bài học kinh nghiệm theo domain
./scripts/bin/harness-cli learn query --domain "angular_fe"

# Quản lý danh mục Work Item cục bộ
./scripts/bin/harness-cli work-item list --state Active
```

### D. Dashboard UI Realtime
```bash
python3 scripts/harness_dashboard.py          # Sinh file HTML và chạy server nền tại cổng 8765
python3 scripts/harness_dashboard.py --serve  # Chạy foreground trực tiếp
```
Mở trình duyệt truy cập: `http://localhost:8765`.

---

## 4. Hướng Dẫn Sử Dụng Bộ Công Cụ Cốt Lõi (Core Tools)

### A. Harness Manager Tool (`tools/harness_manager.py`)
Hỗ trợ quản lý Work Items qua Floci DynamoDB và SQLite fallback, tích hợp rào cản vai trò cứng (Role Fence Gate cấm gán Task cho Lead/Supervisor):

```bash
# Xem thống kê tổng quan
python3 tools/harness_manager.py stats

# Thêm Epic mới (Dành riêng cho Supervisor / Lead)
python3 tools/harness_manager.py add --type Epic --title "[Feature] - Tích hợp Core mới" \
  --description "Mô tả tính năng" --priority P1 --assigned-to lead

# Thêm Task thi công (BẮT BUỘC gán cho Peer 1..4 hoặc QC; tự động chặn ném lỗi nếu gán cho Lead)
python3 tools/harness_manager.py add --type Task --title "[Phase 1] - Xây dựng Module DTO" \
  --description "Chi tiết 5 thành phần Zero-Search" --assigned-to peer

# Cập nhật trạng thái Task (Peer nộp Resolved, QC nghiệm thu Closed)
python3 tools/harness_manager.py update --id <id> --state Resolved
python3 tools/harness_manager.py update --id <id> --state Closed

# Xem danh sách Work Items theo trạng thái
python3 tools/harness_manager.py list --state Active

# Xem danh mục 12 Profile Agent được phép phân công
python3 tools/harness_manager.py profiles
```

### B. Query Reader Tool (`tools/query_reader.py`)
Giải quyết triệt để lỗi `EISDIR` khi duyệt folder và tìm kiếm nội dung chính xác cao bằng thuật toán BM25:
```bash
# Xem cây thư mục an toàn không bị lỗi tràn buffer
python3 tools/query_reader.py <folder_path>

# Tìm kiếm nội dung theo từ khóa / ngữ cảnh (Ranking BM25)
python3 tools/query_reader.py <folder_path> "<câu hỏi hoặc từ khóa>"

# Xuất kết quả dạng JSON để xử lý tự động
python3 tools/query_reader.py <folder_path> "<query>" -j
```

### C. QC Agent & Máy Sinh Testcase ISTQB (`tools/qc_test_generator.py`)
Thực thi quy trình 5-Stage ISTQB Pipeline tự động sinh test cases và unit tests:
```bash
# Sinh test case và unit test từ Spec + Source:
python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> \
  --task-id <id> --out-spec <path/to/file.spec.ts> --sync-harness

# Chạy test runner & kiểm định độ phủ:
python3 tools/qc_test_generator.py --source <path/to/file.ts> --task-id <id> --run --verify-cmd "npm test"
```

### D. Hệ Thống Tự Học Khép Kín Đa Tầng (`tools/harness_learning_search.py`)
Tri thức tự học được lưu đồng bộ kép trên **SQLite local** (`harness.db`) và **Floci DynamoDB cloud** (`harness_experience`):
```bash
# 1. Tra cứu bài học kinh nghiệm theo từ khóa hoặc domain (Hỗ trợ Lead & Peer trước khi code)
python3 tools/harness_learning_search.py search "strict_typing" --domain angular_fe
python3 tools/harness_learning_search.py search --confidence high --limit 10

# 2. Thẩm định chất lượng kho tri thức (PM & Supervisor Audit)
python3 tools/harness_learning_search.py audit

# 3. Tự động thanh trừng bài học rác / tào lao không đạt chuẩn (< 0.60 điểm)
python3 tools/harness_learning_search.py audit --prune --threshold 0.60
```

### E. Bộ Canh Gác Quy Trình & Kỷ Luật Điều Hành (`tools/slppc_flow_guard.py`)
Tự động quét và phát hiện các hành vi sai lệch quy trình (`role_trespass`, `pm_bypass`, `premature_close`, `vague_specs`), lưu biên bản bất biến tại `bmad/rooms/violations/`:
```bash
# Quét kiểm tra tuân thủ toàn diện phòng ban
python3 tools/slppc_flow_guard.py

# Xuất báo cáo định dạng JSON cho CI/CD
python3 tools/slppc_flow_guard.py --json
```

### F. Cảnh Vệ An Ninh Open-Source (`scripts/anti_leak_sentinel.py`)
Bảo vệ kho lưu trữ trước khi mở công khai (Open-Source Readiness):
```bash
# Quét kiểm tra zero API contracts, zero business flows, zero địa chỉ công ty
python3 scripts/anti_leak_sentinel.py
```

### G. Giám Sát Nhịp Tim Đa Tác Nhân Realtime (`tools/agent_heartbeat.py`)
```bash
# Xem bảng trạng thái 9 Agent và chỉ số sức khỏe tri thức tự học
python3 tools/agent_heartbeat.py status

# Bắn tín hiệu ping nhịp tim đồng loạt cho các Agent trên Orca
python3 tools/agent_heartbeat.py broadcast
```

### H. Sổ Cái Bàn Giao & Tiến Độ (`tools/agent_progress.py`)
```bash
# Xem nhanh tiến độ để tiếp tục công việc khi nhận lệnh "làm tiếp"
python3 tools/agent_progress.py status

# Ghi nhận bàn giao sau khi hoàn tất một bước
python3 tools/agent_progress.py log --agent "Lead" --summary "Phân rã xong 4 tasks" \
  --done "Đã giao Peer 1..4" --next "Chờ Peer nộp Resolved" --files "path/to/file"
```

### I. Quản Trị Kỹ Năng & Inverted Index DB Search (`tools/skill_manager.py`)
```bash
# Tra cứu skill qua Inverted Index O(1)
python3 tools/skill_manager.py search "angular" --limit 5

# Đồng bộ danh mục kỹ năng vào DynamoDB
python3 tools/skill_manager.py sync-db
```

### J. Tool Nghiên Cứu Kỹ Thuật (`tools/research/`)
Hỗ trợ nghiên cứu kiến trúc sâu và xuất báo cáo Markdown chuẩn:
```bash
# Chạy Research Agent (Python)
python3 tools/research/research_agent.py "Phân tích kiến trúc Microservices vs Monolith"

# Chạy Research Agent (TypeScript / Node)
npx tsx tools/research/research_agent.ts "Đánh giá Redis Cache Pattern"
```

---

## 5. Quy Chuẩn Kỹ Thuật Bắt Buộc (Engineering Standards)

1. **Lazy Senior Developer Philosophy**:
   - Stdlib & Native Platform trước tiên.
   - Không boilerplate thừa, không over-engineering. Shortest working diff wins.
2. **Quy Chuẩn Zero-Search (5 Thành Phần Bắt Buộc Khi Giao Task)**:
   - Khi Lead phân rã task cho Peer, BẮT BUỘC phải đủ 5 trường định danh: 1. Target Files; 2. Anchors/Lines; 3. Concrete Changes; 4. Acceptance Criteria; 5. Test Command. Cấm giao task 1 dòng mơ hồ khiến Peer phải mò mẫm (`search_files`, `find`, `rg`).
3. **Cổng Kiểm Định Kiểu Dữ Liệu Nghiêm Ngặt (Strict Typing Gate)**:
   - Cấm 100% `any`, `unknown`, toán tử chắp vá `||`, `new Optional()` vô căn cứ.
   - Bắt buộc map tường minh theo chuẩn DTO và Dataclass.
4. **Kỷ Luật Git & Chống Rò Rỉ Tuyệt Đối (Open-Source Ready)**:
   - Thư mục `projects/` (`wicx-crm-fe`, `Aevum`, `harness`, `harness2`) nằm trọn trong `.gitignore`.
   - Cấm tuyệt đối đưa API contracts riêng tư, luồng nghiệp vụ FE, tên công ty hay địa chỉ thực tế vào git tracking.
   - Nghiêm cấm tự ý commit Git khi chưa có chỉ thị rõ ràng từ User.
5. **Cổng Chất Lượng Tri Thức Tự Học (Anti-Trivial Quality Gate)**:
   - Mọi bài học ghi nhận bắt buộc phải có độ dài chuẩn (`lesson` $\ge 20$ ký tự), chứa từ khóa hành động rào chắn (`cấm`, `phải`, `never`, `must`), đạt điểm chất lượng $\ge 0.60$.
   - Sức khỏe tri thức toàn phòng ban luôn được duy trì $\ge 90\%$.
