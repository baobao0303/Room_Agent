# Sổ Cái Tiến Độ & Bàn Giao Giữa Các Agent (Agent Progress & Handoff Ledger)

> **QUY TẮC BẮT BUỘC CHO MỌI AGENT**:
> 1. Khi User yêu cầu **"làm tiếp"**, **"tiếp tục"**, hoặc **"báo cáo những gì đã làm"**, Agent phải đọc file này đầu tiên (hoặc chạy `python3 tools/agent_progress.py status`) để báo cáo ngay cho User trước khi bắt tay vào việc.
> 2. Sau khi hoàn thành một đầu việc hoặc trước khi dừng chờ User, Agent phải cập nhật lại tiến độ bằng lệnh `python3 tools/agent_progress.py log ...`.

---

## 1. Trạng thái Tổng quan Hiện tại (Current Snapshot)

- **Cập nhật lần cuối**: `2026-10-16 17:49:37 +0700`
- **Agent cập nhật gần nhất**: `Paseo/Agent`
- **Trọng tâm hiện tại**: [Supervisor] SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Hành động kế tiếp (Khi User bảo "làm tiếp")**:
  > Awaiting next task from User.

---

## 2. Những Hạng Mục Đã Hoàn Thành (Completed Items)

- [x] Đọc và phân tích toàn bộ mã nguồn workspace `/home/baoltb/Desktop/Paseo_Project` (AGENTS.md, CLAUDE.md, setup_home.sh, setup_harness.sh, patch_paseo.py, profiles/*, scripts/*, tools/*, docs/spec/*, game/*).
- [x] Clone repo `https://github.com/hoangnb24/codex-room-setup` vào `/home/baoltb/Desktop/Paseo_Project/codex-room-setup` và thêm `/codex-room-setup/` vào `.gitignore`.
- [x] Đọc 100% mã nguồn của `codex-room-setup` (`install`, `scripts/install-room`, `scripts/install-paseo`, `scripts/verify`, `scripts/doctor`, `home/.local/bin/codex-room*`, `home/.config/codex-room/*`, `home/.paseo/config.json.template`).
- [x] Chạy kiểm chứng mã nguồn `./scripts/verify --source` (đạt 100% `VERIFY_OK`) và chẩn đoán máy trạm qua `./scripts/doctor` & `./install --dry-run`.
- [x] Tạo và hoàn thiện tài liệu đặc tả 8 mục tại `docs/spec/codex-room-setup-spec.md`.
- [x] Xây dựng hệ thống Sổ cái Tiến độ & Bàn giao Agent (`docs/AGENT_PROGRESS.md` + `tools/agent_progress.py`) và tích hợp vào `AGENTS.md`, `CLAUDE.md`.
- [x] Removed tools/figma_tool.py, tools/test_figma_tool.py, tools/tests/test_figma_tool.py
- [x] updated tools/README.md and AGENTS.md
- [x] verified test suite 100% OK (5 tests pass).
- [x] Turn N/A ended with outcome=unknown (agentId=None)
- [x] Đã xóa sạch projects/angular-nx-rsbuild-base và projects/angular-mfe-rsbuild-base (giải phóng 342MB disk và hàng chục nghìn file).
- [x] Removed test_*.py symlinks from tools/ root
- [x] isolated all tests inside tools/tests/ (test_harness.py, test_qc_generator.py, test_tds_search.py)
- [x] updated tools/README.md.
- [x] Tạo phòng bmad/rooms/{supervisor,lead,peer,qc}, mẫu template-handoff.md, và tự động hóa lưu biên bản bàn giao.
- [x] Tạo bmad/slpc-4-agent-handoff-spec.md (quy trình 5 bước, template bàn giao, chống tràn context) và cập nhật nodes/edges trong bmad/architecture.json tương thích Understand-Anything.
- [x] Extracted article content from https://vhlam.com/article/agent-orchestration-multi-agent-slp
- [x] ran Research & Gen pipeline
- [x] authored full architectural specification at docs/spec/agent-orchestration-multi-agent-slp-spec.md covering context, Paseo primitives, role authority, single-ownership invariant, evidence-backed challenge, 5-step lifecycle, and SLPC extension.
- [x] Nâng cấp tools/call_agent.py hỗ trợ 3-Part Delegation (Goal, Constraints, Suggested Path), tự động kết xuất biên bản bàn giao bmad/rooms/<role>/latest_handoff.md và hỗ trợ Right to Challenge kèm bằng chứng thực nghiệm.
- [x] Updated .agents/skills/qc/SKILL.md, profiles/qc.md, and .claude/agents/slpc-qc-verifier.md with full task-driven workflow
- [x] synced ~/.paseo/config.json via patch_paseo.py
- [x] QC now polls Resolved tasks on Harness, runs 5-stage generator with --task-id and --sync-harness, executes runner, and closes task or files Bugs.
- [x] 1. harness_manager.py: tự động xóa file handoff trong bmad/rooms/ khi task Closed. 2. Tạo công cụ tools/lead_code_review.py và skill /lead-review cho Lead Dev bám sát review code, scaffold DTOs để giảm tải cho Peer Dev.
- [x] Created .agents/skills/qc/references/web-test-cases-standards.md detailing all 17 web component categories (Textbox, Button, Search, Combobox, Upload, Form, Listview, Checkbox, Radio, Header, Footer, Dialog, Links, Datepicker, Toast, Charts, Filter)
- [x] updated .agents/skills/qc/SKILL.md, profiles/qc.md, and .claude/agents/slpc-qc-verifier.md
- [x] patched ~/.paseo/config.json.
- [x] Đặc tả chi tiết 5 Cổng: (1) Neo ngữ cảnh nguồn (URL/Figma/DTO), (2) Giao việc chuẩn 3 phần (Goal/Constraints/Suggested Path), (3) Lead Code Review (OnPush & TDS Tokens), (4) QC 5-Stage ISTQB Tests (100% Pass), và (5) Tự động dọn phòng khi Closed.
- [x] 1. paseo_hooks.py: bổ sung clean_closed_task_rooms và subcommand clean-rooms, tự động quét point-lookup task closed trên Floci DB và xóa biên bản cũ. 2. Kích hoạt hook tự động trên agent.closed, agent.turn_ended, Stop và SessionEnd.

---

## 3. Những Mục Còn Thiếu / Đang Chờ Thực Hiện (Missing & Pending Items)

- [ ] **[M1]** [Máy trạm] Chưa có binary `codex` (`npm install -g @openai/codex`) trên PATH.
- [ ] **[M2]** [Máy trạm] Chưa khởi tạo thư mục gốc `~/.codex` cùng 5 tài nguyên bắt buộc (`config.toml`, `auth.json`, `AGENTS.md`, `skills/`, `plugins/`).
- [ ] **[M3]** [Máy trạm] Chưa clone & build Paseo `v0.8.0` tại `~/projects/supervisors/paseo` và chưa có symlink `~/.local/bin/paseo` (có thể chạy ngay bằng `./scripts/install-paseo`).
- [ ] **[M4]** [Máy trạm] Chưa xuất bản 9 file cấu hình Codex Room (`~/.config/codex-room/*`, `~/.local/bin/codex-room*`, `~/.paseo/config.json`) và 3 thư mục `~/.codex-runtime/{supervisor,lead,peer}` qua `./install --apply`.
- [ ] **[M5]** [Daemon] Paseo Daemon chưa khởi chạy ở `127.0.0.1:6767` nên chưa chạy bước kiểm chứng live (`./install --verify --live`).
- [ ] **[M6]** None.

---

## 4. Nhật Ký Bàn Giao Phiên Làm Việc (Session Handoff Log)

> Lưu ý: Hiển thị 20 phiên gần nhất (tổng số: 62 phiên được lưu trong `.harness_progress.json`).

### Phiên #62 — `2026-10-16 17:49:37 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #61 — `2026-10-16 17:49:04 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Cache (TTL) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #60 — `2026-10-16 17:47:07 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #59 — `2026-10-16 17:46:32 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #58 — `2026-10-16 17:43:28 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #57 — `2026-10-16 17:42:59 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Cache (TTL) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #56 — `2026-10-16 17:41:08 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #55 — `2026-10-16 17:40:33 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #54 — `2026-10-16 17:37:34 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #53 — `2026-10-16 17:37:00 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Cache (TTL) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #52 — `2026-10-16 17:34:56 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #51 — `2026-10-16 17:34:30 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #50 — `2026-10-16 17:31:30 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #49 — `2026-10-16 17:31:00 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Cache (TTL) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #48 — `2026-10-16 17:28:56 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #47 — `2026-10-16 17:28:30 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #46 — `2026-10-16 17:25:31 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #45 — `2026-10-16 17:24:55 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Cache (TTL) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

### Phiên #44 — `2026-10-16 17:23:56 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Awaiting next task from User.

### Phiên #43 — `2026-10-16 17:23:32 +0700` | **Supervisor (Auto Research+Gen)**
- **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Supervisor: SLPC Heartbeat Monitor doc tien do kiem tra agent
- **Đã thực hiện**:
  - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_supervisor_slpc_heartbeat_monitor_do.md
  - Generated Role Execution Brief -> tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md
- **File đã tạo/cập nhật**: `tools/research/research_supervisor_slpc_heartbeat_monitor_do.md`, `tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md`
- **Bàn giao bước tiếp theo**: Profile Supervisor tiếp tục hoàn thiện task dựa trên tools/research/research_supervisor_slpc_heartbeat_monitor_do.md và tools/research/gen_brief_supervisor_slpc_heartbeat_monitor_do.md.

---

## 5. Hướng Dẫn Lệnh Nhanh Cho Agent

```bash
# 1. Xem nhanh báo cáo để trả lời User khi được yêu cầu "làm tiếp":
python3 tools/agent_progress.py status

# 2. Ghi nhận công việc vừa làm xong & cập nhật bước tiếp theo:
python3 tools/agent_progress.py log \
  --agent "Lead Dev" \
  --focus "Trọng tâm công việc hiện tại" \
  --summary "Tóm tắt ngắn gọn phiên làm việc" \
  --done "Việc đã xong 1; Việc đã xong 2" \
  --missing "Việc còn thiếu 1; Việc còn thiếu 2" \
  --next "Bước cụ thể cần làm ngay khi User bảo làm tiếp" \
  --files "docs/spec/file1.md,tools/script2.py"
```
