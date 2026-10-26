---
name: rtk
description: Rust Token Killer (RTK) high-performance CLI proxy skill for SLPPC architecture. Compresses terminal output by 60%–90% to keep context windows under 30k tokens across Supervisor, PM, Lead, Peer, and QC roles.
---

# Rust Token Killer (RTK) Skill for SLPPC Architecture (`skills/shared/rtk`)

> **MỤC TIÊU CỐT LÕI**: Triệt tiêu lãng phí token (tiết kiệm 60%–90% token tiêu thụ), tăng tốc độ phản hồi TTFT, và giữ Context Window luôn tinh gọn (<30k tokens) cho mọi Agent trong hệ thống SLPPC (`Supervisor - PM - Lead - Peer - QC`).

---

## 1. Tổng Quan & Cơ Chế Hoạt Động

RTK (`rtk`) là một công cụ proxy hiệu năng cao viết bằng Rust thuần, đứng giữa hệ thống và các mô hình LLM. Thay vì nạp toàn bộ output khổng lồ của terminal vào context:
- `rtk` lọc bỏ boilerplate, progress bar, whitespace thừa, và các test case pass vô nghĩa.
- Chỉ giữ lại thông tin hành động cần thiết: dòng lỗi (failure diff), thay đổi git thực sự, cấu trúc cây rút gọn.
- Nếu cần xem lại output đầy đủ đã bị rút gọn, Agent có thể dùng `rtk recall <hash>`.

```text
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ LỆNH TERMINAL   │ ────► │ RTK PROXY (Rust)│ ────► │ LLM CONTEXT     │
│ (git, jest, tsc)│       │ Nén 60% - 90%   │       │ (< 30k tokens)  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## 2. Ma Trận Lệnh Chuẩn Cho Từng Vai Trò (Role-Based RTK Commands)

Mỗi Agent trong phòng SLPPC BẮT BUỘC sử dụng các lệnh qua RTK proxy:

### 2.1. Supervisor (Scope & Intent Guard)
- `rtk git status` (hoặc alias `stat`): Xem trạng thái thay đổi ngắn gọn.
- `rtk git log -n 5` (hoặc alias `log`): Rà soát 5 commit gần nhất của Lead/Peer.
- `rtk gain`: Kiểm tra tổng số token đã tiết kiệm được trên toàn phòng ban.

### 2.2. PM Agent (Feasibility & Alignment)
- `rtk diff`: Soi nhanh diff của yêu cầu mới so với baseline kiến trúc.
- `rtk find <dir> -name "<pattern>"`: Khảo sát nhanh cây thư mục mà không làm tràn context.

### 2.3. Lead Dev (Technical Architect)
- `rtk git diff`: Soát xét code diff của Peer nộp về trước khi duyệt `Resolved`.
- `rtk tsc`: Quét lỗi TypeScript compile dạng nhóm lỗi (grouped errors), loại bỏ hàng trăm dòng thừa.
- `rtk read <file> -l aggressive`: Đọc file mục tiêu với cơ chế lọc thông minh, gọt tỉa comment/whitespace.

### 2.4. Peer Dev (Maker Pool - Code Executor)
- `rtk read <target_file>` (hoặc alias `cat`): Đọc file mã nguồn nhanh gọn.
- `rtk tsc`: Kiểm tra strict typing trước khi nộp task.
- `rtk jest <test_file>`: Chạy unit test cục bộ; RTK tự động ẩn toàn bộ test PASS, **chỉ hiển thị lỗi FAIL** kèm stack trace ngắn nhất.

### 2.5. QC Verifier (Independent Quality Gate)
- `rtk jest run`: Chạy toàn bộ test matrix; báo cáo rút gọn `X/Y PASS` (100% test pass chỉ chiếm 2 dòng).
- `rtk test`: Chạy runner kiểm thử cơ học (Mechanical Gate).
- `rtk err <command>`: Chạy lệnh bất kỳ và chỉ in ra stderr/warning nếu có lỗi.

---

## 3. Các Biến Môi Trường Bắt Buộc (Environment Setup)

Tất cả session, script và terminal Orca đều phải export:

```bash
export PATH="$HOME/.local/bin:$PATH"
export RTK_TELEMETRY_DISABLED=1
export RTK_COMPACT_MODE=1
export RTK_TEST_FAILURES_ONLY=1
```

Script nạp tự động theo vai trò:
```bash
source scripts/rtk_profile_env.sh <role>  # e.g: source scripts/rtk_profile_env.sh peer
```

---

## 4. Tích Hợp Hai Môi Trường (Dual-IDE Integration)

1. **Môi trường Claude Code & Paseo (PreToolUse Hook)**:
   - File cấu hình: `.claude/settings.json` & `~/.paseo/claude-config/settings.json`
   - Đăng ký hook:
     ```json
     "PreToolUse": [
       {
         "matcher": "Bash",
         "hooks": [{ "type": "command", "command": "rtk hook claude" }]
       }
     ]
     ```
   - Mọi lệnh Bash thực thi trong Claude Code sẽ tự động được RTK rewrite và nén output.

2. **Môi trường Orca Desktop Workspace (PTY Terminal)**:
   - Các file `scripts/agent_start.py`, `scripts/launch_room.py` và `tools/harness_manager.py` tự động kích hoạt `source scripts/rtk_profile_env.sh <role>` ngay khi mở tab.
   - Các lệnh gõ trực tiếp trong terminal tab tự động nhận alias của RTK.

---

## 5. Thống Kê & Kiểm Tra Hiệu Quả (Economics & Health Check)

```bash
# Xem báo cáo số lượng token đã tiết kiệm:
rtk gain

# Kiểm tra cơ hội tiết kiệm token bị bỏ lỡ từ lịch sử:
rtk discover

# Kiểm tra tính toàn vẹn của các bộ lọc TOML trong .rtk/:
rtk verify

# Khôi phục output đầy đủ bị gọt bớt:
rtk recall <hash>
```
