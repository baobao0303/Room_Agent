# Research Report: [QC] Bàn giao nghiệm thu 8 work items đã Resolved trên nhánh fix/20261015-RemoveMockSources:
1. Bug #281: Bỏ mock sources trong CDP Raw Event & Genericize sidebar active route.
2. Bug #282: Sửa layout dropdown Theo Tenant-id (flex-col, padding, viền bo chuẩn TDS UI).
3. Bug #443: Loại bỏ hoàn toàn tab UNKNOWN khỏi thanh lọc nguồn.
4. Bug #444: Hỗ trợ bôi đen quét chuột chọn và copy từng field text trong wicx-json-viewer.
5. Task #445 & Bug #448: Hover cột Khách hàng đạt 100% Figma (interactive color, underline, font-semibold 600).
6. Task #446: Mặc định lọc phạm vi Tất cả (isAllTenants = true).
7. Bug #447: Chuẩn hóa icon chevron-down-fill và icon checkmark tròn xanh tdsi-success-fill.
Kiểm tra test suite pass 100% và đóng task trên Harness DB.

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:26:55

## 1. Problem Statement & Scope
- **Research Topic**: `[QC] Bàn giao nghiệm thu 8 work items đã Resolved trên nhánh fix/20261015-RemoveMockSources:
1. Bug #281: Bỏ mock sources trong CDP Raw Event & Genericize sidebar active route.
2. Bug #282: Sửa layout dropdown Theo Tenant-id (flex-col, padding, viền bo chuẩn TDS UI).
3. Bug #443: Loại bỏ hoàn toàn tab UNKNOWN khỏi thanh lọc nguồn.
4. Bug #444: Hỗ trợ bôi đen quét chuột chọn và copy từng field text trong wicx-json-viewer.
5. Task #445 & Bug #448: Hover cột Khách hàng đạt 100% Figma (interactive color, underline, font-semibold 600).
6. Task #446: Mặc định lọc phạm vi Tất cả (isAllTenants = true).
7. Bug #447: Chuẩn hóa icon chevron-down-fill và icon checkmark tròn xanh tdsi-success-fill.
Kiểm tra test suite pass 100% và đóng task trên Harness DB.`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "QC Bàn giao nghiệm thu 8 work items" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 358 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 154.97] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:292-298
│   Section: ### 7.2. Bộ 4 Kịch bản Nghiệm thu Hành vi (`docs/acceptance/core4.md`)
├── ────────────────────────────────────────────────────────
│   ### 7.2. Bộ 4 Kịch bản Nghiệm thu Hành vi (`docs/acceptance/core4.md`)
│   Một bản cài đặt `codex-room-setup` chỉ được coi là vận hành đúng về mặt hành vi khi vượt qua 4 bài kiểm tra (Core-4 Acceptance Drills):
│   1. **Drill 1 – Normal Sequential Slice**: `Human -> Supervisor -> Lead -> 1 Writable Peer -> Lead ACCEPT -> Supervisor`. Kiểm chứng Supervisor ẩn danh cuộc trò chuyện riêng với Human và không tự nghiệm thu.
│   2. **Drill 2 – Parallel Disjoint Slices**: Lead mở $\ge 2$ Writable Peers song song khi và chỉ khi đầu vào đã được `ACCEPT` và tập file ghi tách rời nhau hoàn toàn.
│   3. **Drill 3 – Peer Challenge (`REOPEN_REQUEST` / `DEPENDENCY_REQUEST` / `BLOCKED`)**: Peer phát hiện giả định sai của Lead, dừng lại và phát tín hiệu phản biện kèm bằng chứng thay vì tự ý sửa tràn lan.
│   4. **Drill 4 – Read-only Review Peer**: Lead mở một `codex-peer` ở chế độ chỉ-đọc để review một commit/snapshot cụ thể; Peer không sửa working tree và không tự ra phán quyết `ACCEPT`.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 143.22] /home/baoltb/Desk

### Local Evidence (profiles):
🔍 Query: "QC Bàn giao nghiệm thu 8 work items" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 32.2] /home/baoltb/Desktop/Paseo_Project/profiles/lead.md:1-44 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Lead
│   provider: router9
│   model: ag/gemini-3.8-flash-high
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: Lead (Technical Architect & Project Manager in SLPC).
│   
│   MISSION:
│   You hold final technical responsibility in the SLPC (`Supervisor - Lead - Peer - QC`) pipeline. You do not edit production code yourself; you break requirements into subtasks, assign implementation to `peer`, and coordinate independent verification with `qc`.
│   
│   WORKFLOW:
│   1. POLL: Find new Epics/Features (`python3 tools/harness_manager.py list --source bot --assigned-to-profile lead --state New`).
│   2. ANALYZE: Read the codebase, specs, and architecture.
│   3. ASSIGN:
│      - Break down into Tasks with clear Acceptance Criteria (`--ac`) and target source files.
│      - Assign implementation Tasks to `peer`:
│        `python3 tools/harness_manager.py add --type Task --title "[<Module>] - <Action>" --ac "<AC list>" --source bot --created-by-profile lead --assigned-to-profile peer --parent-id <epic_id> --dispatch`
│      - Notify or assign `qc` to generate `Testcase` items and unit test suites 

### Local Evidence (tools):
🔍 Query: "QC Bàn giao nghiệm thu 8 work items" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 535 matches across 58 files. Top 3 shown:

┌── [Rank #1 | Score: 155.57] /home/baoltb/Desktop/Paseo_Project/tools/research/codex_room_setup_research.md:55-63
│   Section: ## 3. Giao thức Làm việc & Chuỗi Bàn giao (Handoff Sequence)
├── ────────────────────────────────────────────────────────
│   ## 3. Giao thức Làm việc & Chuỗi Bàn giao (Handoff Sequence)
│   
│   Chuỗi bàn giao bắt buộc: **BA ➔ DESIGN ➔ DEV**:
│   1. **Bước 1 (BA)**: Lead BA định nghĩa User Stories kèm Acceptance Criteria (AC) tại `docs/spec/<project>/ba/`.
│   2. **Bước 2 (DESIGN)**: Lead Design thiết kế component, ánh xạ token màu/typography tại `docs/spec/<project>/design/` dựa trên AC của BA.
│   3. **Bước 3 (DEV)**: Lead Dev nhận đầu vào đã được nghiệm thu (BA + Design) để tạo Technical Story / Tasks và giao cho Peer Dev lập trình tại `projects/<project>/`.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 155.35] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_282_bug_bug_cdp_r.md:1-8
│   Section: # Research Report: [Peer Dev] Work Item #282 [Bug]: [Bug] [CDP Raw Event]: Khi bấm mở dropdown Theo Tenant-id thì danh sách bị dàn ngang và đè lên tiêu đề bảng
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Work Item #282 [Bug]: [Bug] [CDP Raw Event]: Khi bấm mở dropdown Theo Tenant

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
