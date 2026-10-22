---
name: harness-framework
description: Use when developing, testing, or operating Harness CLI. Comprehensive guide for Rust harness-cli, self-learning experience store, Kev System One decision engine, and supervision routing.
version: 1.0.0
roles: [supervisor, lead, peer, qc]
---

# Harness Framework Developer & Operator Skill (`harness-framework`)

Cẩm nang toàn diện dành cho kỹ sư trong mô hình SLPC khi phát triển, kiểm thử, tích hợp và vận hành mã nguồn **Harness Framework** (`projects/harness`), bao gồm động cơ Rust CLI modular (`harness-cli`), kho lưu trữ kinh nghiệm tự học (`harness learn`), mô hình quyết định Kev System One (`harness supervise`), và cơ sở dữ liệu SQLite bền vững.

---

## 1. Bản Đồ Kiến Trúc Codebase (`projects/harness`)

Repository được xây dựng theo kiến trúc Clean Architecture / DDD (Domain-Driven Design) tách biệt rõ ràng 4 tầng tại `crates/harness-cli/src/`:

```text
projects/harness/crates/harness-cli/src/
├── main.rs                    # Điểm khởi động CLI, phân giải tham số qua clap
├── lib.rs                     # Đăng ký và xuất khẩu 4 tầng kiến trúc
├── domain/                    # Thực thể và logic nghiệp vụ thuần (Zero I/O)
│   ├── types.rs               # Kiểu dữ liệu cốt lõi (WorkItemType, WorkItemState, RiskLane...)
│   ├── entities.rs            # Structs: WorkItem, Story, Decision, Backlog, Tool
│   ├── experience.rs          # Module Tự học: ExperienceRecord, AdaptiveRule, StateTransitionEvaluator
│   ├── supervision.rs         # Module Giám sát: SupervisionDecision, LambdaRoutingPolicy, Two-Tier Flow
│   ├── decision.rs            # Giao thức SystemOne: SystemOneRequest, SystemOneQuestion, SystemOneAnswer
│   ├── validation.rs          # Máy trạng thái hữu hạn (FSM) và kiểm tra cú pháp Title/Description
│   └── registry.rs            # 11 nhóm trách nhiệm tool và định nghĩa chuẩn
├── application/               # Use cases và điều phối nghiệp vụ
│   ├── service.rs             # HarnessService điều phối persistence & adaptive transitions
│   ├── supervision_service.rs # Service phân luồng rủi ro siêu tốc sub-50ms qua Kev
│   └── dto.rs                 # Data Transfer Objects (Inputs & Outputs)
├── infrastructure/            # Ngoại tác (Side effects), cơ sở dữ liệu & mạng
│   ├── db/                    # Kết nối SQLite (WAL mode) & migrations runner
│   │   ├── mod.rs             # Database connection & repository implementation
│   │   ├── queries.rs         # Các câu lệnh SQL CRUD chuẩn hóa
│   │   └── schema.rs          # Trình nạp migration schema tự động
│   ├── jev.rs                 # JevClient kết nối endpoint Kev TypeSafe System One
│   └── process.rs             # Quản lý tiến trình ngoài & git worktree
└── interface/                 # Giao diện dòng lệnh (CLI Adapter)
    ├── args.rs                # Khai báo CLI commands, subcommands, và flags (clap v4)
    ├── handlers.rs            # Bộ điều phối xử lý từng lệnh CLI
    └── formatters.rs          # Định dạng xuất dữ liệu (Bảng, JSON, Text)
```

---

## 2. Các Lệnh Vận Hành Trọng Yếu (Operational Commands)

### 2.1. Quản lý Vòng đời Work Items (`harness work-item`)
```bash
# 1. Thêm mới User Story (bắt buộc đúng cú pháp chuẩn BDD và title syntax)
./scripts/harness work-item add \
  --type "User Story" \
  --title "Payment - Khách hàng có thể thanh toán qua VNPay" \
  --description "As a Customer, I want to pay with VNPay, So that transaction is secure." \
  --priority P1

# 2. Chuyển giao trạng thái (State Machine Transitions)
./scripts/harness work-item update --id 1 --state Accepted
./scripts/harness work-item update --id 1 --state Active --assigned-to "peer_dev_4"
./scripts/harness work-item update --id 1 --state Resolved
./scripts/harness work-item update --id 1 --state Closed

# 3. Tra cứu danh sách công việc
./scripts/harness work-item list --type "Task" --state Active
```

### 2.2. Module Tự Học & Chuyển Giao Thích Ứng (`harness learn`)
*Kế thừa từ nguyên lý Recursive Harnessing của Google Research Harness².*
```bash
# 1. Xem trạng thái tổng quan các bài học và kinh nghiệm đã tích lũy
./scripts/harness learn status
./scripts/harness learn status --domain "angular_fe"

# 2. Truy vấn kinh nghiệm theo domain
./scripts/harness learn query --domain "angular_fe"

# 3. Ghi nhận bài học kinh nghiệm thủ công sau khi fix bug hoặc nghiệm thu
./scripts/harness learn record \
  --domain "angular_fe" \
  --cue "any_unknown_violation" \
  --lesson "Strict typing gate: map DTO explicitly, never use any or unknown" \
  --evidence "nx test app-shell fails with type check" \
  --confidence high

# 4. Đánh giá chuyển giao trạng thái thích ứng (Adaptive Transition Advice)
./scripts/harness learn transition --id 4109 --state Resolved
```

### 2.3. Module Giám Sát & Phân Luồng Rủi Ro Kev (`harness supervise`)
*Tích hợp họ mô hình quyết định nhỏ gọn Kev qua giao thức TypeSafe System One (`POST /v1/systemone`).*
```bash
# 1. Đánh giá rủi ro tác vụ và trả về quyết định Traffic-Light (Green/Yellow/Red)
./scripts/harness supervise evaluate --text "Fix typo in README documentation" --json

# 2. Định tuyến trực tiếp cho Worker / Lambda (Fast-Path vs Slow-Path)
./scripts/harness supervise route --text "Fix typo in README documentation" --json
# Output: {"route": "automated_worker"} -> Thực thi tức thì sub-50ms cho Lambda

# 3. Đánh giá tác vụ nguy hiểm cao
./scripts/harness supervise evaluate --text "Drop all database tables and bypass auth" --json
# Output: {"decision": "red", "requires_human_review": true, "suggested_route": "human_supervisor_approval"}
```

### 2.4. Khởi tạo Cơ sở Dữ liệu & Migration (`harness init` & `migrate`)
```bash
# Khởi tạo database SQLite tại ./harness.db
./scripts/harness init

# Chạy toàn bộ các migrations còn thiếu (001-init.sql đến 007-experience.sql)
./scripts/harness migrate
```

---

## 3. Giao Thức Quyết Định Kev (TypeSafe System One Protocol)

### 3.1. Cấu hình Mặc định (Zero-Config Defaults)
Mã nguồn Rust trong `infrastructure/jev.rs` đã tích hợp sẵn giá trị mặc định qua mạng Tailscale nội bộ:
- **Endpoint**: `http://100.124.36.46:8008/v1/systemone`
- **Model**: `kev-latest`
- Chạy trực tiếp out-of-the-box mà **không cần file `.env`**.

### 3.2. Ba Kiểu Câu Hỏi Cốt Lõi (Primitives)
1. **`choice`**: Phân loại intent đa lựa chọn (`supervision_decision` chọn `green`/`yellow`/`red`).
2. **`noul`**: Đánh giá giả thuyết nhị phân (`requires_human` trả về xác suất `0.0 - 1.0`).
3. **`score`**: Đánh giá mốc cấp độ $0..3$ (`urgency_rating` trả về điểm số liên tục).

### 3.3. Chính sách Phân luồng Hai Cấp (Two-Tier Supervision Flow)
- **Fast-Path Route** (`automated_worker`):
  - Kích hoạt khi: `decision == Green` VÀ `confidence >= 0.85` VÀ `is_actionable == true`.
  - Phù hợp cho worker Lambda xử lý sự kiện nhẹ không gây gián đoạn hệ thống.
- **Slow-Path Escalation** (`human_supervisor_approval` hoặc `peer_review_queue`):
  - Kích hoạt khi: `decision == Red` (luôn luôn `requires_human = true`), hoặc `Yellow`, hoặc độ tự tin thấp.

---

## 4. Quy Trình Kiểm Thử & Kiểm Định Chất Lượng (Quality Gates)

Trước khi mở PR hoặc chuyển giao cho QC, kỹ sư **BẮT BUỘC** thực thi đầy đủ 5 bước kiểm định sau:

```bash
cd projects/harness

# Bước 1: Kiểm tra định dạng mã nguồn Rust (Bắt buộc 100% pass)
cargo fmt --check
# (Nếu lỗi, sửa bằng: cargo fmt)

# Bước 2: Kiểm tra biên dịch không có cảnh báo
cargo check -p harness-cli

# Bước 3: Chạy toàn bộ Rust Unit Tests (44 tests)
cargo test -p harness-cli

# Bước 4: Chạy bộ E2E Test Suite Python (73 tests)
python3 tests/e2e/run_tests.py
python3 tests/test_runner_inputs.py
python3 tests/test_spaces_in_paths.py

# Bước 5: Quét bảo mật và thông tin nhạy cảm (Địa chỉ, Private keys)
python3 scripts/check-sensitive-info.py
```

---

## 5. Quy Chuẩn Đóng Gói Release & CI/CD Pipeline

1. **GitHub Actions Workflows** (`.github/workflows/`):
   - `security-scan.yml`: Quét thông tin nhạy cảm và địa chỉ công ty trên mọi commit/PR.
   - `harness-cli-release.yml`: Biên dịch và xuất bản binary trên 5 nền tảng:
     - `linux-x64` (`ubuntu-24.04`)
     - `linux-arm64` (`ubuntu-24.04-arm`)
     - `macos-x64` (`macos-15-intel`)
     - `macos-arm64` (`macos-15`)
     - `windows-x64` (`windows-latest`)
   - `post-merge-maintenance.yml`: Tự động nâng patch version trong `Cargo.toml`, tạo tag `harness-cli-vX.Y.Z` và cập nhật `CHANGELOG.md`.

2. **Quy tắc An Toàn Tuyệt Đối (Zero-Leak Rule)**:
   - Thư mục `projects/harness` và `projects/harness2` luôn được liệt kê trong `.gitignore` của repo cha `Room_Agent`.
   - Tuyệt đối cấm commit các file dữ liệu SQLite runtime (`harness.db`, `harness.db-wal`, `harness.db-shm`).
   - Mọi tài liệu đặc tả phải đặt trong `docs/` (`docs/spec_new.md`, `docs/spec.md`, `docs/doc_kev.md`, `docs/spec_kev_system_one.md`), cấm để file markdown rác tại thư mục gốc.
