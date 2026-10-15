# Research Report: [Supervisor] Mapping dữ liệu thô

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 11:02:29

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Mapping dữ liệu thô`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Mapping dữ liệu thô" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 157 matches across 12 files. Top 3 shown:

┌── [Rank #1 | Score: 97.17] /home/baoltb/Desktop/Paseo_Project/docs/AGENTS.md:15-22
│   Section: ## 2. Kỹ năng áp dụng
├── ────────────────────────────────────────────────────────
│   ## 2. Kỹ năng áp dụng
│   1. **Business Analysis (BA)**:
│      - Sử dụng `mattpocock-skills/skills/engineering/grill-with-docs/SKILL.md` để phỏng vấn sâu và làm rõ yêu cầu.
│      - Chuẩn hóa mô hình nghiệp vụ qua `mattpocock-skills/skills/engineering/domain-modeling/SKILL.md`.
│      - Chuyển thảo luận thành tài liệu đặc tả qua `mattpocock-skills/skills/engineering/to-spec/SKILL.md`.
│      - Đồng bộ User Stories lên Harness qua `tools/harness_manager.py add ...`.
│   2. **UI/UX Design**:
│      - Sử dụng `ui-lib-figma/SKILL.md` để mapping component Figma sang UI Angular và tra cứu color tokens.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 95.55] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:305-308
│   Section: ## 8. Cơ chế Lưu trữ Tiến độ & Bàn giao giữa các Agent (Agent Progress & Handoff Ledger)
├── ────────────────────────────────────────────────────────
│   ## 8. Cơ chế Lưu trữ Tiến độ & Bàn giao giữa các Agent (Agent Progress & Handoff Ledger)
│   
│   Để giải quyết bài toán **liên tục ngữ cảnh (Session Continuity)** — giúp bất kỳ Agent nào (Antigravity, Claude Code, Codex, Hermes, h

### Local Evidence (profiles):
🔍 Query: "Supervisor Mapping dữ liệu thô" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 30.0] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Supervisor
│   provider: router9
│   model: ag/claude-sonnet-5-5-medium
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: Supervisor (Scope & Intent Guard - SLPC Orchestrator).
│   
│   MISSION:
│   You are the project referee in the SLPC (`Supervisor - Lead - Peer - QC`) architecture. Do not write code, design systems, or review code.
│   Your job:
│   1. Ensure Lead, Peer, and QC do not drift from the User's original intent.
│   2. Track progress through the Harness DB.
│   3. Escalate to the User for decisions on: scope changes, data-deletion risk, cost, or production deploys.
│   
│   WORKFLOW:
│   - Check the board with `python3 tools/harness_manager.py list --source bot --state Active` or `--state Resolved` or `--state Blocked`.
│   - WHEN the User gives a new request: run `python3 tools/harness_manager.py add --type Epic --title "[CDP] - <name>" --source bot --created-by-profile supervisor --assigned-to-profile lead --dispatch` to assign it to Lead.
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User directly.
│   - DO NO

### Local Evidence (tools):
🔍 Query: "Supervisor Mapping dữ liệu thô" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 318 matches across 28 files. Top 3 shown:

┌── [Rank #1 | Score: 91.25] /home/baoltb/Desktop/Paseo_Project/tools/research/harness_framework_research.md:46-50
│   Section: ## 4. Mục tiêu Xây dựng Tool Quản lý Harness cho Agent
├── ────────────────────────────────────────────────────────
│   ## 4. Mục tiêu Xây dựng Tool Quản lý Harness cho Agent
│   Tạo một bộ wrapper tool Python/TS trực tiếp tương tác với `harness-cli` hoặc SQLite database `harness.db` giúp các Agent (BA, Design, Dev, Supervisor) tự động:
│   1. Tạo đúng cú pháp Work Item theo vai trò.
│   2. Kiểm tra State Machine hợp lệ trước khi chuyển trạng thái.
│   3. Truy vấn nhanh bảng phân cấp, truy vết ma trận kiểm thử (`query matrix`, `query stats`).
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 77.97] /home/baoltb/Desktop/Paseo_Project/tools/research/codex_room_setup_research.md:48-54
│   Section: ### C. Tầng Giám sát (Supervisor)
├── ────────────────────────────────────────────────────────
│   ### C. Tầng Giám sát (Supervisor)
│   - Quan sát luồng làm việc giữa các Lead.
│   - Can thiệp nếu Dev bắt đầu viết code khi chưa có AC từ BA hoặc mockup từ Design.
│   - Theo dõi tiến độ qua sự kiện Kanban và Cron jobs, không spam hỏi trạng thái.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 73.79] /home/baoltb/Desktop/Paseo_Project/tool

### Local Evidence (projects):
🔍 Query: "Supervisor Mapping dữ liệu thô" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25242 matches across 5859 files. Top 3 shown:

┌── [Rank #1 | Score: 140.41] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-channel-management.md:186-187
│   Section: ## 3. Đặc Tả Kiến Trúc & Luồng Dữ Liệu Toàn Hệ Thống
├── ────────────────────────────────────────────────────────
│   ## 3. Đặc Tả Kiến Trúc & Luồng Dữ Liệu Toàn Hệ Thống
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 139.59] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/spec_shop_user_permission.md:426-427
│   Section: ## 7. ĐẶC TẢ GIAO THỨC DỮ LIỆU & API BACKEND (DATA CONTRACT & APIS)
├── ────────────────────────────────────────────────────────
│   ## 7. ĐẶC TẢ GIAO THỨC DỮ LIỆU & API BACKEND (DATA CONTRACT & APIS)
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 113.33] /home/baoltb/Desktop/Paseo_Project/projects/fe-mfes/README.md:283-288
│   Section: ## Tài liệu thêm
├── ────────────────────────────────────────────────────────
│   ## Tài liệu thêm
│   
│   - Project context for AI assistants: `CLAUDE.md`
│   - Design spec: `docs/superpowers/specs/2026-07-07-wi-mfes-wi-oauth-workspace-design.md`
│   - Implementation plan: `docs/superpowers/plans/2026-07-07-wi-mfes-wi-oauth-setup.md`
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Supervisor Mapping dữ liệu thô" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 190.42] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 0.5_User_Stories/UC2.05 - Connector Zalo OA.md:129-133
│   Section: #### 4. Đăng ký nhận dữ liệu thất bại
├── ────────────────────────────────────────────────────────
│   #### 4. Đăng ký nhận dữ liệu thất bại
│   
│   1. Bước 9 gặp lỗi (Zalo trả lỗi / hết thời gian chờ).
│   2. **[WiCX CRM]** Giữ kết nối ở trạng thái *chưa xác minh*, không xoá token đã lưu; thoát bằng nút **"Kết nối lại"** có sẵn trên dòng trang liên kết (luồng 1.2 — xem *Dòng trang liên kết Zalo OA trên hub* cuối mục này).
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 190.16] /home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/stories/Phase 0.5_User_Stories/UC2.05 - Connector Zalo OA.md:130-136
│   Section: #### 4. Đăng ký nhận dữ liệu thất bại
├── ────────────────────────────────────────────────────────
│   #### 4. Đăng ký nhận dữ liệu thất bại
│   
│   1. Bước 9 gặp lỗi (Zalo trả lỗi / hết thời gian chờ).
│   2. **[WiCX CRM]** Giữ kết nối ở trạng thái *chưa xác minh*, không xoá token đã lưu; thoát bằng nút **"Kết nối lại"** có sẵn trên dòng trang liên kết (luồng 1.2 — xem *Dòng trang liên kết Zalo OA trên hub* cuối mục này).
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Sco

## 3. Findings & Spec Mapping
- **Documentation & Spec Targets**: `docs/spec/`, `AGENTS.md`, `CLAUDE.md`, `docs/AGENT_PROGRESS.md`.
- **Sub-Agents Available**:
  - `gemini-codebase-analyzer`: Holistic 1M+ token context scan.
  - `strategic-reasoning-architect`: Deep architectural trade-off and root-cause analysis.
  - `slpc-qc-verifier`: 5-Stage ISTQB Testcase & Unit Test generation (`tools/qc_test_generator.py`).

## 4. Trade-offs & Edge Cases
- Maintain single moving write-scope ownership per Peer.
- Ensure all business rules and boundary values are verified via deterministic unit tests before `QC` transitions any item to `Closed`.

## 5. Actionable Recommendations & Next Generation Steps
1. **Task / Spec Generation**: Register or update Work Items via `python3 tools/harness_manager.py`.
2. **Test Generation (5-Stage ISTQB)**: Run `python3 tools/qc_test_generator.py --source <target_file> --spec <spec_file> --sync-harness`.
3. **Progress Ledger Update**: Log completion via `python3 tools/agent_progress.py log --agent "<Role>" ...`.
