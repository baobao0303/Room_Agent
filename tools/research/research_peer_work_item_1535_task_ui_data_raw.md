# Research Report: [Peer] Work Item #1535 [Task]: [UI/Data-Raw]: Cap nhat tab Du lieu tho & Mapping du lieu sang tds-body-2 font-semibold icon 14px
Cap nhat typography cac tab Du lieu tho va Mapping du lieu tren raw-event-list.component.html: ap dung tds-body-2 font-semibold va icon 14px (text-[14px]).

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:08:43

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer] Work Item #1535 [Task]: [UI/Data-Raw]: Cap nhat tab Du lieu tho & Mapping du lieu sang tds-body-2 font-semibold icon 14px
Cap nhat typography cac tab Du lieu tho va Mapping du lieu tren raw-event-list.component.html: ap dung tds-body-2 font-semibold va icon 14px (text-[14px]).`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Work Item 1535 Task UI Data-Raw Cap" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 570 matches across 19 files. Top 3 shown:

┌── [Rank #1 | Score: 58.3] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:667-675
│   Section: ### Phiên #119 — `2026-10-15 14:25:30 +0700` | **Peer Dev**
├── ────────────────────────────────────────────────────────
│   ### Phiên #119 — `2026-10-15 14:25:30 +0700` | **Peer Dev**
│   - **Tóm tắt**: Fix Work Item #447: Cập nhật icon TDS UI cho dropdown lọc Tenant trong Raw Event List
│   - **Đã thực hiện**:
│     - Đổi tdsSuffixIcon='tdsi-chevron-down-fill' trên button dropdown lọc Tenant
│     - Đổi checkmark option item sang 'tdsi-success-fill tds-color-icon-success text-base shrink-0'
│     - Viết và verify 23 unit test BDD pass 100%
│   - **File đã tạo/cập nhật**: `apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.html`, `apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.spec.ts`
│   - **Bàn giao bước tiếp theo**: QC thực hiện kiểm thử độc lập và nghiệm thu Task #447
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 51.72] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:768-778
│   Section: ### Phiên #107 — `2026-10-15 14:17:36 +0700` | **Peer Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #107 — `2026-10-15 14:17:36 +0700` | **Peer Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipe

### Local Evidence (profiles):
🔍 Query: "Peer Work Item 1535 Task UI Data-Raw Cap" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 37.33] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Peer
│   provider: router9
│   model: ag/gemini-3.8-flash-high
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: Peer (Execution & Engineering in SLPC).
│   
│   MISSION:
│   You work directly on the codebase in the SLPC (`Supervisor - Lead - Peer - QC`) pipeline. You serve the goal, but do NOT blindly follow a technical solution that is wrong in practice.
│   
│   WORKFLOW:
│   1. POLL: Find your assigned Tasks or Bugs (`python3 tools/harness_manager.py list --source bot --assigned-to-profile peer --state New`).
│   2. CLAIM: Run `python3 tools/harness_manager.py update --id <id> --state Active --assigned-to-profile peer` IMMEDIATELY to claim the work.
│   3. WORK: Code, test, patch, terminal. Strictly apply the rules: https://github.com/baobao0303/cursor_rule_angular2026 (Angular 18, Nx, UI Lib).
│   4. HANDOFF TO QC:
│      - Done and self-tested: Transition the task to `Resolved` and hand off to `qc` for independent test verification:
│        `python3 tools/harness_manager.py update --id <id> --state Resolved --assigned-to-profile qc`
│        `python3 tools/call_agent.py --profil

### Local Evidence (tools):
🔍 Query: "Peer Work Item 1535 Task UI Data-Raw Cap" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 461 matches across 82 files. Top 3 shown:

┌── [Rank #1 | Score: 121.51] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_446_task_fe_cdp_c.md:1-7
│   Section: # Research Report: [Peer Dev] Work Item #446 [Task]: [FE/CDP] - Chuyển phạm vi lọc mặc định sang Tất cả (isAllTenants = true) trong Raw Event
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Work Item #446 [Task]: [FE/CDP] - Chuyển phạm vi lọc mặc định sang Tất cả (isAllTenants = true) trong Raw Event
│   Tại apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts:
│   - Chuyển giá trị mặc định của isAllTenants từ false sang true để khi vào màn hình mặc định chọn 'Tất cả'.
│   - Cập nhật unit test raw-event-list.component.spec.ts khớp với hành vi mặc định mới.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:14:21
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 119.54] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_447_bug_bug_cdp_r.md:1-7
│   Section: # Research Report: [Peer Dev] Work Item #447 [Bug]: [Bug] [CDP Raw Event]: Khi mở dropdown lọc Tenant thì icon checkmark và mũi tên chưa đúng chuẩn TDS UI
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Work 

### Local Evidence (projects):
🔍 Query: "Peer Work Item 1535 Task UI Data-Raw Cap" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 6806 matches across 5893 files. Top 3 shown:

┌── [Rank #1 | Score: 50.06] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:68-69
│   Section: ## 🔨 Daily Development Tasks
├── ────────────────────────────────────────────────────────
│   ## 🔨 Daily Development Tasks
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 45.35] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:124-133
│   Section: ### Working with Shared Libraries
├── ────────────────────────────────────────────────────────
│   ### Working with Shared Libraries
│   
│   **When to use shared libraries:**
│   - Code used by multiple micro-frontends
│   - Common UI components
│   - Utility functions
│   - Shared data access services
│   
│   **Creating Shared Components:**
│   ```bash
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 39.74] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:379-381
│   Section: # Use Nx affected commands to work only with changed projects
├── ────────────────────────────────────────────────────────
│   # Use Nx affected commands to work only with changed projects
│   npx nx serve affected
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Peer Work Item 1535 Task UI Data-Raw Cap" | Category: all
📊 Tìm thấy 1251 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 96.27] /home/baoltb/Desktop/wicx-crm-doc/BA/team-process/tfs-work-item-management.md:52-61
│   Section: #### 4.1.1 Các loại Work Item
├── ────────────────────────────────────────────────────────
│   #### 4.1.1 Các loại Work Item
│   
│   | Work Item | Người tạo | Mô tả |
│   |----|----|----|
│   | **Epic** | CPO | Mục tiêu lớn, cấp chiến lược; gắn nhiều User Story |
│   | **User Story** | BA | Yêu cầu cụ thể của người dùng; gắn nhiều Task và Bug |
│   | **Technical Story** | Dev / Team | Các nội dung xử lý kỹ thuật ngoài User Story (ví dụ: test epic, plan release lên production); cùng cấp với User Story; chứa nhiều Task và Bug |
│   | **Task** | Dev / Tester | Việc cụ thể để hoàn thành một PBI; do Dev hoặc Tester thực hiện |
│   | **Bug** | Tester | Lỗi phát hiện trong quá trình test; Dev chịu trách nhiệm sửa |
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 96.27] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/team-process/tfs-work-item-management.md:52-61
│   Section: #### 4.1.1 Các loại Work Item
├── ────────────────────────────────────────────────────────
│   #### 4.1.1 Các loại Work Item
│   
│   | Work Item | Người tạo | Mô tả |
│   |----|----|----|
│   | **Epic** | CPO | Mục tiêu lớn, cấp chiến lược; gắn nhiều User Story |
│   | **User Story** | BA | Yêu cầu cụ thể của ngườ

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
