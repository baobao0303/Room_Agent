# Room_Agent Command Cheatsheet (SLPPC Architecture)

## 1. Quản lý Vòng đời Agent (All-in-One CLI: `./agent-start`)

```bash
# Khởi chạy 2 tabs Agent thường trực (PM, Lead Dev) - Supervisor là terminal hiện hành
./agent-start

# Khởi chạy toàn bộ 8 vai trò (khi cần chạy full pool)
./agent-start --all

# Khởi chạy một vai trò cụ thể on-demand
./agent-start peer
./agent-start qc

# Xem bảng trạng thái chi tiết của tất cả Agent & nhịp tim
./agent-start status

# Khởi động lại toàn bộ các Agent
./agent-start restart

# Đóng tab của một agent hoặc đóng tất cả
./agent-start stop peer
./agent-start stop --all
```

---

## 2. Điều phối Tự hành Plugin Hooks (`plugins/slpc-lifecycle-hooks/`)

```bash
# Kiểm tra trạng thái 3 tầng hooks và cấu hình Paseo daemon
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py status

# Kích hoạt điều phối tự hành thủ công (State Navigation)
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py orchestrate --role supervisor --json
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py orchestrate --role lead --json
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py orchestrate --role peer --json
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py orchestrate --role qc --json

# Dọn dẹp task đã Closed và xoay vòng FIFO sổ cái
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py clean-rooms --keep 2
```

---

## 3. Quản trị Work Item & Bàn cờ Harness (`tools/harness_manager.py`)

```bash
# Xem danh sách work item
python3 tools/harness_manager.py list

# Xem chi tiết work item
python3 tools/harness_manager.py get --id <ITEM_ID>

# Xem thống kê work item
python3 tools/harness_manager.py stats

# Thêm Work Item mới
python3 tools/harness_manager.py add \
  --type {Epic,Feature,"User Story","Technical Story",Task,Bug,Testcase} \
  --title "<Title>" \
  [--description "<Desc>"] \
  [--priority {P0,P1,P2,P3}] \
  [--assigned-to-profile <profile>]

# Cập nhật trạng thái Work Item (State Transition)
python3 tools/harness_manager.py update \
  --id <ITEM_ID> \
  --state {New,Accepted,Active,Resolved,Closed,Blocked,Removed} \
  [--assigned-to-profile <profile>]
```

---

## 4. Kiểm tra Chất lượng & Chốt chặn An ninh (Quality & Governance Gates)

```bash
# 1. Chạy toàn bộ 92 unit tests của bộ công cụ
python3 -m unittest discover -s tools/tests

# 2. Kiểm tra tuân thủ phân luồng SLPPC & vệ sinh phòng ban
python3 tools/slppc_flow_guard.py audit

# 3. Quét an ninh chống lộ dữ liệu nội bộ, địa chỉ và secrets (Fail-Closed)
python3 scripts/anti_leak_sentinel.py

# 4. Quét Zombie Terminals mồ côi và Watchdog timeout
python3 tools/zombie_reaper.py --dry-run
```

---

## 5. Tiến độ & Bàn giao Context (`tools/agent_progress.py`)

```bash
# Xem trạng thái tiến độ hiện hành
python3 tools/agent_progress.py status

# Ghi log tiến độ và đồng bộ latest_handoff.md + room_ledger.json
python3 tools/agent_progress.py log \
  --agent "Supervisor" \
  --summary "<Tóm tắt việc đã làm>" \
  --done "<Chi tiết mục hoàn thành>" \
  --next "<Hành động tiếp theo>" \
  --files "<Danh sách file đã sửa>"
```

---

## 6. Pipeline Tự Hành 5 Cổng 1 Chạm (`./trigger-flow`)

```bash
# Kích hoạt toàn bộ luồng tự hành (PM -> Lead -> Peer -> QC):
./trigger-flow "[FEATURE] Làm tính năng xuất Excel"
./trigger-flow "[BUGFIX] Vá lỗi null pointer trong CartService"
./trigger-flow "[DISCUSS] Đánh giá phương án kiến trúc JWT vs Cookie"
./trigger-flow "[ADVERSARIAL] Test bẫy lỗi timeout mạng và rollback"
./trigger-flow "[REFACTOR] Tối ưu hóa signal trong component"

# Kiểm tra trạng thái luồng vừa chạy:
./trigger-flow --status
```

---

## 7. Quản Trị Worktree Cô Lập & Phê Duyệt Merge (`./orca-review`)

```bash
# Xem danh sách các Worktree Task đang mở trên Orca Board:
./orca-review list

# User xem xong Git Diff trực quan và đồng ý Merge vào main:
./orca-review approve <task_id>

# User từ chối và yêu cầu Peer sửa đổi (bắn phản hồi vào terminal của Peer):
./orca-review reject <task_id> --reason "Đổi màu nút sang TDS Primary token"
```

---

## 8. Quản Trị Nén Token RTK (`rtk`)

```bash
# Xem tổng số token đã tiết kiệm qua RTK:
rtk gain

# Kiểm tra cơ hội tiết kiệm token bị bỏ lỡ từ lịch sử:
rtk discover

# Xác thực tính toàn vẹn của các bộ lọc TOML trong .rtk/:
rtk verify
```

---

## 9. Vệ Sinh Context & Xóa Sạch Sub-Agent (`./agent-start clear`)

```bash
# Đóng toàn bộ Sub-Agent (Peer, QC, Design), đưa RAM về 0, giữ lại PM và Lead:
./agent-start clear

# Đóng sạch toàn bộ tất cả agent:
./agent-start stop --all
```
