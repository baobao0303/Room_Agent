# Paseo Project Command Cheatsheet

## 1. Slash Commands (Claude Code / Chat)

| Command | Mục đích |
|---|---|
| `/paseo` | Trạng thái bot SLPC, cron heartbeat, bàn cờ Harness |
| `/paseo-agent` | Hướng dẫn vai trò agent (Supervisor, Lead, Peer, QC) |
| `/paseo-advisor` | Spawn sub-agent tư vấn ý kiến thứ hai (second opinion) |
| `/paseo-committee` | Spawn 2 sub-agent phân tích RCA và lập kế hoạch |
| `/paseo-review` | Spawn sub-agents review chéo (Code, Spec, UI) |
| `/paseo-handoff` | Bàn giao task sang profile khác |
| `/harness-ops` | Thao tác CRUD work item trên Harness DB |
| `/code-review` | Review code song song (Standards & Spec) |
| `/simplify` | Rút gọn diff, tối ưu code theo YAGNI |
| `/supervisor-call` | Supervisor phân rã task và gọi Lead/Peer |

---

## 2. Harness Manager CLI (`tools/harness_manager.py`)

### Danh sách & Thống kê
```bash
# Xem danh sách work item
python3 tools/harness_manager.py list

# Xem chi tiết work item
python3 tools/harness_manager.py get --id <ITEM_ID>

# Xem thống kê work item
python3 tools/harness_manager.py stats

# Xem danh sách Agent Profiles
python3 tools/harness_manager.py profiles
```

### Thêm Work Item
```bash
python3 tools/harness_manager.py add \
  --type {Epic,Feature,"User Story","Technical Story",Task,Bug,Testcase} \
  --title "<Title>" \
  [--description "<Desc>"] \
  [--priority {P0,P1,P2,P3}] \
  [--assigned-to-profile <profile>] \
  [--created-by-profile <profile>] \
  [--dispatch]
```

### Cập nhật Work Item
```bash
python3 tools/harness_manager.py update \
  --id <ITEM_ID> \
  --state {New,Accepted,Active,Resolved,Closed,Blocked,Removed} \
  [--assigned-to-profile <profile>]
```

---

## 3. Agent Dispatch CLI (`tools/call_agent.py`)

```bash
# Gọi agent thực thi task
python3 tools/call_agent.py --profile <Profile> --prompt "<Task>"

# Gắn kèm Work Item ID
python3 tools/call_agent.py --profile <Profile> --prompt "<Task>" --item-id <ITEM_ID>

# Dry run (kiểm tra lệnh, không chạy)
python3 tools/call_agent.py --profile <Profile> --prompt "<Task>" --dry-run
```

---

## 4. Scripts & Utilities

```bash
# Mở dashboard Harness UI
python3 scripts/harness_dashboard.py

# Dọn dẹp dữ liệu harness cũ/rác
python3 scripts/harness_cleanup.py

# Sinh unit test tự động (QC)
python3 tools/qc_test_generator.py

# Đồng bộ tài liệu
python3 tools/doc_sync.py
```
