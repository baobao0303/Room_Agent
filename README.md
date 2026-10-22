# Room_Agent — Paseo SLPPC Multi-Agent Workspace

Không gian làm việc điều hành đa tác nhân theo mô hình **SLPPC (Supervisor - PM - Lead - Peer - QC)** tích hợp hệ điều hành **Paseo**, **Hermes Agent** và **Harness CLI v0.1.14**.

---

## ⚡ CÀI ĐẶT 1 BƯỚC (ONE-COMMAND SETUP)

Khi clone repository về máy trạm mới, chỉ cần chạy **1 lệnh duy nhất**:

```bash
./setup.sh
```

Hoặc vừa cấu hình môi trường, vừa tự động khởi chạy toàn bộ **9 Agent tabs** trực tiếp trên Orca Desktop Workspace:

```bash
./setup.sh --launch
# hoặc: ./scripts/launch_room.sh
```

### Script tự động thực hiện trọn gói:
1. **Kiểm tra công cụ**: Tự động nhận diện `orca`, `hermes`, `python3`, `git`, `cargo`.
2. **Cấu hình Model**: Mặc định sử dụng model chuẩn `ag/gemini-3.8-flash-high` cho toàn bộ các Agent (kết hợp phân tầng 4 bậc tiết kiệm token cho Peer Devs).
3. **Master Skills Tree (85+ Skills)**: Tập trung duy nhất tại thư mục canonical `skills/<tên>/SKILL.md`, tự động symlink vào `~/.hermes/skills/`.
4. **Đồng bộ 9 Profiles SLPPC**: Đăng ký `Supervisor`, `PM Agent`, `Lead Dev`, `Peer Dev 1..4`, `Peer Design`, `QC` vào `~/.paseo/config.json`.
5. **Native Rust Binary v0.1.14**: Nạp và xác thực `scripts/bin/harness-cli` (v0.1.14) chạy sub-millisecond.
6. **Dual-Store Learning Engine**: Khởi tạo SQLite local (`harness.db` - migration 007) và kết nối Floci Cloud DynamoDB (`harness_experience` - port `:14566`).
7. **Security & Governance Guards**: Tự động kích hoạt Anti-Leak Sentinel và SLPPC Flow Guard trước commit và trong CI.

---

## 1. Mô Hình Điều Hành Phòng Ban SLPPC & 5 Cổng Kiểm Soát

```text
[Yêu cầu từ User]
       │
       ▼
1. Supervisor (Scope & Intent Guard) ──► Phân tích scope, tiếp nhận ý định User, cấm trực tiếp code
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

### Chi Tiết 5 Vai Trò Cốt Lõi:
1. **Supervisor (`supervisor`)**: Scope & Intent Guard. Kênh giao tiếp độc nhất với User. Phân tích phạm vi, tạo Epic/Task trên Harness DB (`--engine auto`), điều phối PM/Lead/Peer và kiểm soát rủi ro. Tuyệt đối cấm can thiệp code (`role_trespass`).
2. **PM Agent (`pm`)**: Product Manager & Decision Arbiter (Kev System One Engine). Cố vấn định lượng ngầm cho Supervisor & Lead: đánh giá mức độ **Khả thi (Feasibility 0..3)** và **Phù hợp (Alignment)**, tính điểm rủi ro sub-50ms trước khi phân rã task. Chặn đứng lỗi `pm_bypass`.
3. **Lead Dev (`lead`)**: Technical Architect & PM. Thiết kế kiến trúc, tra cứu bài học cũ qua `harness learn query`, duyệt giải pháp kỹ thuật và phân rã task Zero-Search 5 thành phần cho Peer. Nghiêm cấm tự ý code (`role_trespass`).
4. **Peer Devs (`peer`, `peer2`, `peer3`, `peer4`, `design`)**: Code Executors. Lập trình theo spec, tuân thủ Strict Typing (0% `any`, 0% `unknown`), viết unit test và chuyển task sang `Resolved`. Nghiêm cấm tự tiện đóng task (`premature_close`).
5. **QC (`qc`)**: Independent Quality Gate & Test Architect. Độc quyền quyền hạn chuyển trạng thái task sang `Closed`. Nghiệm thu độc lập, sinh testcase theo chuẩn ISTQB 5-Stage (`tools/qc_test_generator.py`), xác nhận AC, ghi nhận bài học kinh nghiệm và chạy audit bảo đảm 100% tuân thủ quy trình.
6. **Security Sentinel (`security`)**: Continuous Anti-Leak Gatekeeper & Open-Source Auditor. Giám sát liên tục chống lộ API spec tính năng, luồng nghiệp vụ FE, địa chỉ công ty và secrets; sở hữu quyền VETO chặn đứng mọi commit/push vi phạm.

---

## 2. Cấu Trúc Thư Mục Chuẩn (Directory Architecture)

```text
.
├── AGENTS.md                  # Quy chuẩn điều hành & pháp lệnh rào cản SLPPC
├── profiles/                  # 9 Hồ sơ Agent: supervisor, pm, lead, peer 1..4, design, qc, security
├── skills/                    # Master Skills Registry (85+ skills canonical dạng skills/<name>/SKILL.md)
├── docs/
│   ├── spec/                  # Đặc tả kỹ thuật các tính năng & nâng cấp
│   │   ├── harness-cli-v0.1.14-upgrade-spec.md # Bản đặc tả nâng cấp v0.1.14 & SLPPC
│   │   └── kev-system-one-spec.md              # Chuẩn wire protocol Kev TypeSafe System One
│   └── AGENT_PROGRESS.md      # Sổ cái ghi nhận tiến độ liên tục & bàn giao đa tác nhân
├── bmad/                      # Bộ não tri thức kiến trúc tập trung
│   ├── architecture.json      # Đồ thị tương tác module & ranh giới hệ thống
│   ├── rooms/                 # Không gian bàn giao của các Agent (supervisor, pm, lead, peer, qc)
│   └── rooms/violations/      # Sổ cái biên bản vi phạm kỷ luật (role_trespass, pm_bypass...)
├── scripts/
│   ├── bin/harness-cli        # Native Rust CLI v0.1.14 (supervise, learn, work-item)
│   ├── launch_room.sh         # Khởi chạy đồng bộ 9 agent terminals trên Orca Workspace
│   ├── anti_leak_sentinel.py  # Script kiểm tra an ninh chống rò rỉ dữ liệu trước commit
│   └── schema/                # Các migrations SQL SQLite (001-init đến 007-experience)
├── tools/                     # Bộ công cụ điều hành hệ thống
│   ├── harness_manager.py     # Quản lý Work Items Floci DynamoDB & SQLite (--engine auto)
│   ├── harness_rust.py        # Python-Rust Typed Bridge kết nối Kev System One & Learning Store
│   ├── harness_learning_search.py # Tra cứu, thẩm định và thanh trừng bài học tự học tào lao
│   ├── slppc_flow_guard.py    # Bộ canh gác rào cản vai trò và quy trình SLPPC
│   ├── agent_heartbeat.py     # Theo dõi nhịp tim 9 agent & cảnh báo sức khỏe tri thức realtime
│   ├── agent_progress.py      # Ghi nhận và truy vấn sổ cái tiến độ bàn giao
│   ├── floci_client.py        # Client DynamoDB Floci Cloud (:14566)
│   └── qc_test_generator.py   # Máy sinh testcase tự động 5-Stage ISTQB
├── .github/workflows/
│   └── slppc-governance-guard.yml # CI Actions kiểm soát bảo mật & quy trình tự động trên PR
└── README.md
```

---

## 3. Hướng Dẫn Sử Dụng Các Công Cụ Cốt Lõi

### A. Harness Manager Tool (`tools/harness_manager.py`)
Hỗ trợ quản lý Work Items qua Floci DynamoDB và SQLite fallback, tích hợp rào cản vai trò cứng (Role Fence Gate cấm gán Task cho Lead/Supervisor):

```bash
# Xem thống kê tổng quan
python3 tools/harness_manager.py stats

# Thêm Epic mới (Dành riêng cho Supervisor / Lead)
python3 tools/harness_manager.py add --type Epic --title "[Feature] - Tích hợp Core mới" \
  --description "Mô tả tính năng" --priority P1 --assigned-to lead

# Thêm Task thi công (BẮT BUỘC gán cho Peer 1..4 hoặc QC; tự động chặn nếu gán cho Lead)
python3 tools/harness_manager.py add --type Task --title "[Phase 1] - Xây dựng Module DTO" \
  --description "Chi tiết 5 thành phần Zero-Search" --assigned-to peer

# Cập nhật trạng thái Task (Peer nộp Resolved, QC nghiệm thu Closed)
python3 tools/harness_manager.py update --id <id> --state Resolved
python3 tools/harness_manager.py update --id <id> --state Closed
```

### B. Hệ Thống Tự Học Khép Kín Đa Tầng (`tools/harness_learning_search.py`)
Tri thức tự học được lưu đồng bộ kép trên **SQLite local** và **Floci DynamoDB cloud** (`harness_experience`):

```bash
# 1. Tra cứu bài học kinh nghiệm theo từ khóa hoặc domain (Hỗ trợ Lead & Peer trước khi code)
python3 tools/harness_learning_search.py search "strict_typing" --domain angular_fe
python3 tools/harness_learning_search.py search --confidence high --limit 10

# 2. Thẩm định chất lượng kho tri thức (PM & Supervisor Audit)
python3 tools/harness_learning_search.py audit

# 3. Tự động thanh trừng bài học rác / tào lao không đạt chuẩn (< 0.60 điểm)
python3 tools/harness_learning_search.py audit --prune --threshold 0.60
```

### C. Bộ Canh Gác Quy Trình & Kỷ Luật Điều Hành (`tools/slppc_flow_guard.py`)
Tự động quét và phát hiện các hành vi sai lệch quy trình, lưu biên bản bất biến tại `bmad/rooms/violations/`:

```bash
# Quét kiểm tra tuân thủ toàn diện phòng ban
python3 tools/slppc_flow_guard.py
# hoặc xuất JSON
python3 tools/slppc_flow_guard.py --json
```

### D. Cảnh Vệ An Ninh Open-Source (`scripts/anti_leak_sentinel.py`)
Bảo vệ kho lưu trữ trước khi mở công khai (Open-Source Readiness):

```bash
# Quét kiểm tra zero API contracts, zero business flows, zero địa chỉ công ty
python3 scripts/anti_leak_sentinel.py
```

### E. Giám Sát Nhịp Tim Đa Tác Nhân Realtime (`tools/agent_heartbeat.py`)
```bash
# Xem bảng trạng thái 9 Agent và chỉ số sức khỏe tri thức tự học
python3 tools/agent_heartbeat.py status

# Bắn tín hiệu ping nhịp tim đồng loạt cho các Agent
python3 tools/agent_heartbeat.py broadcast
```

### F. Sổ Cái Bàn Giao & Tiến Độ (`tools/agent_progress.py`)
```bash
# Xem nhanh tiến độ để tiếp tục công việc
python3 tools/agent_progress.py status

# Ghi nhận bàn giao sau khi hoàn tất một bước
python3 tools/agent_progress.py log --agent "Lead" --summary "Phân rã xong 4 tasks" \
  --done "Đã giao Peer 1..4" --next "Chờ Peer nộp Resolved" --files "path/to/file"
```

---

## 4. Quy Chuẩn Kỹ Thuật Bắt Buộc (Engineering Standards)

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
