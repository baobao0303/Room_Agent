# Room_Agent Command Cheatsheet (SLPC Architecture)

## 1. Quản lý Vòng đời Agent (All-in-One CLI: `./cli/agent-start`)

```bash
# Khởi chạy tab Agent thường trực (Lead Dev) - Supervisor là terminal hiện hành
./cli/agent-start

# Khởi chạy toàn bộ 8 vai trò (khi cần chạy full pool)
./cli/agent-start --all

# Khởi chạy một vai trò cụ thể on-demand
./cli/agent-start peer
./cli/agent-start qc

# Xem bảng trạng thái chi tiết của tất cả Agent & nhịp tim
./cli/agent-start status

# Khởi động lại toàn bộ các Agent
./cli/agent-start restart

# Đóng tab của một agent hoặc đóng tất cả
./cli/agent-start stop peer
./cli/agent-start stop --all
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
# 1. Chạy toàn bộ 322+ unit tests của bộ công cụ (326 test cases)
python3 -m unittest discover -s tools/tests

# 2. Kiểm tra tuân thủ phân luồng SLPC & vệ sinh phòng ban
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
