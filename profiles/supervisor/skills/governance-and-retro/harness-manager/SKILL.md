---
name: harness-manager
description: Manage SDLC work items, state machine transitions, Kev System One supervision, and self-learning experience store for Harness Framework (https://github.com/baobao0303/harness).
version: 1.0.0
roles: [supervisor]
---

# Harness SDLC & Governance Manager Skill (`harness-manager`)

Kỹ năng dành riêng cho **Supervisor** (Macro Governor & Intent Guard) để quản trị toàn diện hệ thống **Harness Framework** (Repository: `https://github.com/baobao0303/harness`, codebase cục bộ: `projects/harness`), kết hợp công cụ dòng lệnh Rust hiệu năng cao `harness-cli` (v0.1.14), động cơ phân luồng siêu tốc Kev System One (<50ms) và kho tri thức tự học (`harness learn`).

---

## 1. Tổng Quan & Vai Trò Quản Trị Của Supervisor Đối Với Harness

Supervisor là **chủ thể tối cao quản trị vòng đời tác vụ (SDLC Governor)** trên Harness:
1. **Khởi tạo & Thẩm định**: Chuyển hóa ý định người dùng (User Intent) thành `Epic` và `User Story` trên Harness DB (`./scripts/harness work-item add` hoặc `tools/harness_manager.py`).
2. **Kích hoạt Kev System One**: Tự động chấm điểm Khả thi (Feasibility 0..3) và Phù hợp chiến lược (Strategic Alignment) trong <50ms qua `harness supervise`.
3. **Tra cứu bẫy lỗi quá khứ**: Truy vấn kho kinh nghiệm tự học (`harness learn query --domain <domain>`) để đính kèm các bài học thất bại cũ vào đặc tả giao việc cho Lead Dev.
4. **Kiểm soát máy trạng thái (FSM Governance)**: Đảm bảo chuyển giao trạng thái tuân thủ nghiêm ngặt 4 cổng SLPC:
   - `New` (Supervisor tạo) $\rightarrow$ `Accepted` (Supervisor duyệt) $\rightarrow$ `Active` (Lead giao Peer làm) $\rightarrow$ `Resolved` (Peer hoàn thành) $\rightarrow$ `Closed` (Độc quyền QC nghiệm thu).
5. **Nghiệm thu Intent & Dọn dẹp**: Kiểm tra Git diff tổng hợp có khớp 100% với yêu cầu ban đầu của User trước khi đóng Epic; chạy Zombie Reaper đưa RAM về 0.

---

## 2. Bản Đồ Kho Mã Nguồn (`https://github.com/baobao0303/harness`)

Mã nguồn được cấu trúc theo chuẩn Clean Architecture / DDD (Domain-Driven Design) tại `projects/harness/crates/harness-cli/src/`:
- `domain/`: Thực thể và logic nghiệp vụ thuần (`types.rs`, `entities.rs`, `experience.rs`, `supervision.rs`, `decision.rs`, `validation.rs`).
- `application/`: Ca sử dụng (`service.rs`, `supervision_service.rs`, `dto.rs`).
- `infrastructure/`: Ngoại tác và cơ sở dữ liệu (`db/` SQLite WAL mode, `jev.rs` JevClient kết nối Kev System One).
- `interface/`: Giao diện CLI (`args.rs`, `handlers.rs`, `formatters.rs`).

---

## 3. Cẩm Nang Lệnh Vận Hành Trọng Yếu (Operational Commands)

### 3.1. Quản lý Work Items (`harness work-item` / `tools/harness_manager.py`)

```bash
# 1. Supervisor tạo Epic mới từ yêu cầu User
./scripts/harness work-item add \
  --type "Epic" \
  --title "[<Module>] - <Mục tiêu vĩ mô>" \
  --description "Mô tả chi tiết phạm vi và mục tiêu nghiệp vụ" \
  --priority P1

# 2. Tạo User Story chuẩn BDD gắn kèm tiêu chí Acceptance Criteria (AC)
./scripts/harness work-item add \
  --type "User Story" \
  --title "[CRM] - Khách hàng có thể tra cứu lịch sử đơn hàng" \
  --description "As a Customer, I want to view my past orders, So that I can track deliveries." \
  --priority P1 \
  --parent-id <epic_id>

# 3. Chuyển trạng thái công việc tuân thủ SLPC Gate
./scripts/harness work-item update --id <id> --state Accepted
./scripts/harness work-item update --id <id> --state Active --assigned-to "peer"
./scripts/harness work-item update --id <id> --state Resolved
# Chú ý: Chỉ có QC mới được quyền chuyển sang Closed!

# 4. Tra cứu danh sách công việc và thống kê
./scripts/harness work-item list --type "Epic" --state Active
python3 tools/harness_manager.py stats
```

### 3.2. Giám Sát & Phân Luồng Siêu Tốc Kev System One (`harness supervise`)

Được thiết kế để phản hồi dưới **50ms**, phân luồng tác vụ ngay khi vừa tiếp nhận:
```bash
# 1. Đánh giá rủi ro tác vụ (Traffic-Light: Green / Yellow / Red)
./scripts/harness supervise evaluate --text "Refactor auth token expiration logic" --json

# 2. Định tuyến trực tiếp cho Worker (Fast-Path tự động vs Slow-Path cần review)
./scripts/harness supervise route --text "Fix typo in documentation" --json
# Output: {"route": "automated_worker", "confidence": 0.98}
```

### 3.3. Kho Kinh Nghiệm Tự Học Thích Ứng (`harness learn`)

Lưu trữ và truy xuất các bài học thất bại / thành công để không bao giờ lặp lại lỗi cũ:
```bash
# 1. Tra cứu bài học kinh nghiệm trước khi phân rã task
./scripts/harness learn query --domain "angular_fe"
python3 tools/harness_learning_search.py "strict typing any unknown"

# 2. Xem trạng thái tổng quan các bài học đã tích lũy
./scripts/harness learn status

# 3. Ghi nhận bài học kinh nghiệm mới sau buổi Retro hoặc Fix Bug
./scripts/harness learn record \
  --domain "angular_fe" \
  --cue "hardcoded_hex_color" \
  --lesson "Always use TDS SCSS design tokens (e.g. \$tds-color-primary), never hardcode #hex" \
  --evidence "Pre-commit hook rejected commit due to #1890ff" \
  --confidence high

# 4. Đánh giá chuyển giao trạng thái thích ứng (Adaptive State Transition)
./scripts/harness learn transition --id <task_id> --state Resolved
```

### 3.4. Quản lý Backlog & Đồng Bộ Remote (`harness query` & `sync-remote`)

```bash
# 1. Tra cứu Backlog theo Sprint hoặc mức độ ưu tiên
./scripts/harness query backlog --top 20 --source local
./scripts/harness query matrix  # Xem ma trận kiểm thử và độ bao phủ test

# 2. Đồng bộ hai chiều giữa Local SQLite WAL và AWS DynamoDB / Floci Cloud
./scripts/harness sync-remote
```

---

## 4. Quy Chuẩn Vận Hành Của Supervisor (Supervisor Operating Procedure)

1. **Bước 1 (Intake)**: Nhận User Request $\rightarrow$ Chạy `harness supervise evaluate` $\rightarrow$ Đạt Green/Yellow $\rightarrow$ Tạo Epic trên Harness.
2. **Bước 2 (Tra cứu bài học)**: Chạy `harness learn query` $\rightarrow$ Trích xuất Top-3 bài học cũ.
3. **Bước 3 (Decision Memo)**: Soạn `decision_memo_*.md` chứa Feasibility, Alignment, Traps to Avoid, Turn Ceiling ($\le$ 3–5).
4. **Bước 4 (Dispatch sang Lead)**: Chuyển giao Work Item sang Lead Dev xử lý.
5. **Bước 5 (Audit & Review)**: Khi QC chuyển task sang `Closed`, Supervisor chạy `python3 tools/slppc_flow_guard.py audit` và nghiệm thu tổng thể.
