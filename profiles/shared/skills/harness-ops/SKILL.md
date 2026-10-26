---
name: harness-ops
description: "Skill for managing SDLC work items, state machine transitions, test verification matrices, and backlog queries via Harness Framework on Floci."
version: 2.0.0
author: BaoLTB, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [harness, sdlc, ddd, backlog, test-matrix, state-machine, floci, tfs]
---

# Harness Operations Skill (`harness-ops`)

Quản trị toàn diện vòng đời phát triển phần mềm (SDLC) theo chuẩn **DDD-COMPANY-2026** và **ISO/IEC 27001:2022** qua Harness CLI kết nối Floci Cloud Storage (DynamoDB & S3).

---

## 1. When to Use
Kích hoạt skill này khi:
- **Lead BA / Peer BA**: Tạo mới `Epic`, `Feature`, hoặc `User Story`; duyệt story sang `Accepted`.
- **Lead Dev / Peer Dev**: Tra cứu backlog theo Sprint, nhận task (`Accepted -> Active`), tạo `Technical Story`, `Task`, hoặc `Bug`.
- **Tester / QA (Chị Nguyên)**: Kiểm tra ma trận kiểm thử (`query matrix`), đối chiếu Acceptance Criteria, cập nhật kết quả test (`PASSED` / `FAILED`).
- **Supervisor / Lead**: Giám sát phân bổ backlog giữa nguồn TFS và Local, kiểm tra tiến độ qua các Sprint.

---

## 2. Thống kê hệ thống hiện tại (Floci DynamoDB & Local Fallback DB)

- **Cơ chế Lưu trữ Kép (Dual-Mode Resilient Storage)**: `tools/floci_client.py` tự động kiểm tra kết nối TCP (`0.4s`) tới Floci (`127.0.0.1:14566`) và tự động chuyển sang cơ sở dữ liệu dự phòng `.harness_local_db.json` nếu Floci offline, đảm bảo tốc độ phản hồi tức thì.
- **Dashboard Trực quan (Stitch Obsidian Cyber-Matrix)**: `http://127.0.0.1:8765/harness_dashboard.html` (xem chi tiết tại skill `skills/supervisor/slpc-control-center/SKILL.md`).

```text
=== HARNESS REPOSITORY & WORK ITEM STATISTICS ===
• Total Work Items : 343
• Total Stories    : 60
• Phân bổ theo Cổng SLPC (Supervisor ➔ Lead ➔ Peer ➔ QC):
  - 1. Supervisor Gate (Epic)           : 7 items
  - 2. Lead Architect (Feature / Story) : 57 items
  - 3. Peer Engineer (Task)             : 131 items
  - 4. QC & Release Gate (Testcase/Bug) : 148 items (137 Testcases, 11 Bugs)
• Phân bổ theo Trạng thái:
  - Active   : 16 items
  - Resolved : 4 items
  - Closed   : 126 items
  - New/Design: 197 items
```

---

## 3. Cú pháp bắt buộc (Syntax Rules)

### A. Title Syntax
- **User Story**: Bắt buộc có dấu gạch ngang (`-`/`–`/`—`) và từ khóa `có thể` / `co the` / `can`:
  `[Module] – [Vai trò] có thể [hành động]`
- **Task / Tech Story**: `[Module/Tính năng] - [Động từ + hành động]`
- **Bug**: `[Module]: [Error message] when [reason]`
- **Testcase**: `[Module]: [Expected result] when [condition]`

### B. User Story Description (Chuẩn BDD)
```text
As a [User Role],
I want [Action / Goal],
So that [Business Value].
```

---

## 4. Các lệnh tra cứu & vận hành Harness CLI

### A. Xem ma trận kiểm thử (Verification Matrix)
Hiển thị toàn bộ các Story kèm lệnh kiểm thử tự động, độ ưu tiên, trạng thái và kết quả:
```bash
./scripts/harness query matrix
```
*Output mẫu:*
```text
ID     | Source | Priority | State      | Title                               | Verify Command            | Result
-------------------------------------------------------------------------------------------------------------------
1      | LOCAL  | P1       | Active     | [Auth] – User có thể đăng nhập bằ   | cargo test auth::oauth    | PASSED (0.24s)
2      | LOCAL  | P0       | New        | [Payment] – Khách hàng có thể qué   | cargo test payment::qr    | UNVERIFIED
3      | LOCAL  | P2       | Accepted   | [Dashboard] – Quản trị viên có th   | npm run test:dashboard    | PASSED
```

### B. Tra cứu Backlog linh hoạt (Lọc theo Sprint / Source / Type)
```bash
# Xem 20 items mới nhất của toàn bộ dự án
./scripts/harness query backlog --top 20

# Chỉ xem các items nguồn TFS của Sprint 5
./scripts/harness query backlog --source tfs --sprint "Sprint 5"

# Chỉ xem các items do Agent/Local tạo
./scripts/harness query backlog --source local

# Lọc theo loại (User Story / Bug / Task) trong Sprint 4
./scripts/harness query backlog --type "User Story" --sprint "Sprint 4"

# Lọc theo trạng thái đang thực hiện (Active)
./scripts/harness query backlog --state Active
```

### C. Đồng bộ dữ liệu từ TFS
Kéo dữ liệu mới nhất từ TFS repository về Floci DynamoDB:
```bash
./scripts/harness sync-tfs
```

### D. Thêm Work Item mới (Local / Native)
```bash
python3 tools/harness_manager.py add \
  --type "User Story" \
  --title "[Auth] – Người dùng có thể đăng nhập bằng OTP" \
  --description "As a User, I want đăng nhập bằng OTP, So that bảo mật tài khoản." \
  --priority P1 --story-points 3
```

### E. Chuyển trạng thái State Machine
```bash
# BA duyệt Story: New -> Accepted
python3 tools/harness_manager.py update --id 1 --state Accepted

# Dev nhận task: Accepted -> Active
python3 tools/harness_manager.py update --id 1 --state Active --assigned-to "lead_dev"

# Hoàn thành: Active -> Resolved -> Closed
python3 tools/harness_manager.py update --id 1 --state Resolved
python3 tools/harness_manager.py update --id 1 --state Closed
```

### F. Thống kê & Quản lý Tools
```bash
./scripts/harness query stats     # Thống kê tổng quan số lượng theo trạng thái
./scripts/harness query tools     # Xem danh mục tools tự động hóa
```
