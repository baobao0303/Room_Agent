# Research Report: [Peer Dev] Work Item #446 [Task]: [FE/CDP] - Chuyển phạm vi lọc mặc định sang Tất cả (isAllTenants = true) trong Raw Event
Tại apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts:
- Chuyển giá trị mặc định của isAllTenants từ false sang true để khi vào màn hình mặc định chọn 'Tất cả'.
- Cập nhật unit test raw-event-list.component.spec.ts khớp với hành vi mặc định mới.

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:14:21

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Work Item #446 [Task]: [FE/CDP] - Chuyển phạm vi lọc mặc định sang Tất cả (isAllTenants = true) trong Raw Event
Tại apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts:
- Chuyển giá trị mặc định của isAllTenants từ false sang true để khi vào màn hình mặc định chọn 'Tất cả'.
- Cập nhật unit test raw-event-list.component.spec.ts khớp với hành vi mặc định mới.`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Work Item 446 Task FE CDP" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 223 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 75.02] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:166-179
│   Section: ### Phiên #92 — `2026-10-15 14:10:21 +0700` | **Peer Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #92 — `2026-10-15 14:10:21 +0700` | **Peer Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Peer Dev: Work Item #445 [Task]: [FE/CDP] - Áp dụng màu Alias/color/text/interactive và gạch chân khi hover cột Khách hàng
│   Tại apps/mfe-cdp/src/app/pages/contact/components/contact-list/contact-list.component.html:
│   - Cột Khách hàng (fullName / customerTpl) hiện đang dùng 'hover:tds-color-primary-500-light' và thiếu underline khi hover.
│   - Cần cập nhật chuẩn Design System TDS:
│     + Khi hover vào text giá trị (Phan Tấn Hải, Đặng Viết Quý,...), đổi màu sang token 'Alias/color/text/interactive' (class: hover:tds-color-text-interactive).
│     + Thêm đường kẻ gạch chân (class: hover:underline) và con trỏ chuột pointer (cursor-pointer).
│     + Rà soát các cột link/value tương tự trong bảng dữ liệu để đảm bảo đồng nhất chuẩn TDS UI.
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_peer_dev_work_item_445_task_fe_cdp_p.md
│     - Ge

### Local Evidence (profiles):
🔍 Query: "Peer Dev Work Item 446 Task FE CDP" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 31.81] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile QC -

### Local Evidence (tools):
🔍 Query: "Peer Dev Work Item 446 Task FE CDP" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 275 matches across 50 files. Top 3 shown:

┌── [Rank #1 | Score: 189.37] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_445_task_fe_cdp_p.md:1-10
│   Section: # Research Report: [Peer Dev] Work Item #445 [Task]: [FE/CDP] - Áp dụng màu Alias/color/text/interactive và gạch chân khi hover cột Khách hàng
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Work Item #445 [Task]: [FE/CDP] - Áp dụng màu Alias/color/text/interactive và gạch chân khi hover cột Khách hàng
│   Tại apps/mfe-cdp/src/app/pages/contact/components/contact-list/contact-list.component.html:
│   - Cột Khách hàng (fullName / customerTpl) hiện đang dùng 'hover:tds-color-primary-500-light' và thiếu underline khi hover.
│   - Cần cập nhật chuẩn Design System TDS:
│     + Khi hover vào text giá trị (Phan Tấn Hải, Đặng Viết Quý,...), đổi màu sang token 'Alias/color/text/interactive' (class: hover:tds-color-text-interactive).
│     + Thêm đường kẻ gạch chân (class: hover:underline) và con trỏ chuột pointer (cursor-pointer).
│     + Rà soát các cột link/value tương tự trong bảng dữ liệu để đảm bảo đồng nhất chuẩn TDS UI.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:10:17
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 134.45] /home/baoltb/Deskt

### Local Evidence (projects):
🔍 Query: "Peer Dev Work Item 446 Task FE CDP" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25376 matches across 5870 files. Top 3 shown:

┌── [Rank #1 | Score: 74.91] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:68-69
│   Section: ## 🔨 Daily Development Tasks
├── ────────────────────────────────────────────────────────
│   ## 🔨 Daily Development Tasks
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 62.04] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:263-264
│   Section: ## 🔄 Working with Git
├── ────────────────────────────────────────────────────────
│   ## 🔄 Working with Git
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 61.88] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:379-381
│   Section: # Use Nx affected commands to work only with changed projects
├── ────────────────────────────────────────────────────────
│   # Use Nx affected commands to work only with changed projects
│   npx nx serve affected
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Peer Dev Work Item 446 Task FE CDP" | Category: all
📊 Tìm thấy 3101 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 120.22] /home/baoltb/Desktop/wicx-crm-doc/BA/team-process/tfs-work-item-management.md:52-61
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

┌── [Rank #2 | Score: 120.22] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/team-process/tfs-work-item-management.md:52-61
│   Section: #### 4.1.1 Các loại Work Item
├── ────────────────────────────────────────────────────────
│   #### 4.1.1 Các loại Work Item
│   
│   | Work Item | Người tạo | Mô tả |
│   |----|----|----|
│   | **Epic** | CPO | Mục tiêu lớn, cấp chiến lược; gắn nhiều User Story |
│   | **User Story** | BA | Yêu cầu cụ thể của người dù

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
