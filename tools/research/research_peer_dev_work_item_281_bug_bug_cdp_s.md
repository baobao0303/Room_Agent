# Research Report: [Peer Dev] Work Item #281 [Bug]: [Bug] [CDP/Shell]: Khi mở CDP Raw Event và sidebar /setting thì nguồn bị mock tĩnh và active route sai
Khắc phục lỗi trên nhánh fix/20261015-RemoveMockSources (projects/wicx-crm-fe):
1. mfe-cdp: Xóa mock sources tĩnh trong raw-event-list, lấy động từ API và tự động phát hiện sources từ eventsList; xóa tenantSubName thừa.
2. app-shell: LayoutStore hỗ trợ generic path cho route con (/setting/employee); chuẩn hóa breadcrumbs và sidebar menu item.
3. Đảm bảo toàn bộ Unit Test (raw-event-list, layout, sidebar) pass 100%.

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:45:06

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Work Item #281 [Bug]: [Bug] [CDP/Shell]: Khi mở CDP Raw Event và sidebar /setting thì nguồn bị mock tĩnh và active route sai
Khắc phục lỗi trên nhánh fix/20261015-RemoveMockSources (projects/wicx-crm-fe):
1. mfe-cdp: Xóa mock sources tĩnh trong raw-event-list, lấy động từ API và tự động phát hiện sources từ eventsList; xóa tenantSubName thừa.
2. app-shell: LayoutStore hỗ trợ generic path cho route con (/setting/employee); chuẩn hóa breadcrumbs và sidebar menu item.
3. Đảm bảo toàn bộ Unit Test (raw-event-list, layout, sidebar) pass 100%.`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Work Item 281 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 95 matches across 15 files. Top 3 shown:

┌── [Rank #1 | Score: 18.18] /home/baoltb/Desktop/Paseo_Project/docs/spec/example-project/dev/architecture-spec.md:1-2
│   Section: # Technical Architecture & Dev Spec: Example Project
├── ────────────────────────────────────────────────────────
│   # Technical Architecture & Dev Spec: Example Project
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 18.1] /home/baoltb/Desktop/Paseo_Project/docs/spec/research-raw-data-mapping-projection.md:1-9
│   Section: # Nghiên cứu Chuyên sâu: CDP Raw Data Mapping & Event Projection Field Mapping UI
├── ────────────────────────────────────────────────────────
│   # Nghiên cứu Chuyên sâu: CDP Raw Data Mapping & Event Projection Field Mapping UI
│   
│   > **Mã tài liệu:** `RESEARCH-CDP-RAW-DATA-MAPPING-PROJECTION-20261015`  
│   > **Ngày lập:** 15/10/2026  
│   > **Người thực hiện:** Combo-Lead (Paseo SLPC Architecture)  
│   > **Phạm vi:** Micro-frontend `apps/mfe-cdp` (`/cdp/data-raw`), library `libs/features/raw-event-data`, Backend services (`WiCX.Ingestion`, `WiCX.EventArchive`, `WiCX.DataExtraction`, `WiCX.Crm`), cơ chế Event Projection DB `wicx_projection`.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 17.6] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:354-357
│   Section: ## 9. Mở

### Local Evidence (profiles):
🔍 Query: "Peer Dev Work Item 281 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 32.62] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
🔍 Query: "Peer Dev Work Item 281 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 172 matches across 34 files. Top 3 shown:

┌── [Rank #1 | Score: 101.01] /home/baoltb/Desktop/Paseo_Project/tools/research/harness_framework_research.md:18-25
│   Section: ### B. Cấu trúc Phân cấp Work Item (Portfolio Hierarchy)
├── ────────────────────────────────────────────────────────
│   ### B. Cấu trúc Phân cấp Work Item (Portfolio Hierarchy)
│   ```text
│   Epic (CPO) 
│     └── Feature (BA) 
│           ├── User Story (BA) ➔ Tasks, Bugs, Testcases
│           └── Technical Story (Dev) ➔ Tasks, Bugs
│   ```
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 49.13] /home/baoltb/Desktop/Paseo_Project/tools/research/harness_framework_research.md:39-45
│   Section: ## 3. Hệ thống Chuyển đổi Trạng thái (State Machine Matrix)
├── ────────────────────────────────────────────────────────
│   ## 3. Hệ thống Chuyển đổi Trạng thái (State Machine Matrix)
│   - **User Story**: `New` ➔ `Accepted` (BA duyệt) ➔ `Active` (Dev kéo vào Sprint) ➔ `Resolved` (Pass PR, test) ➔ `Closed` (Sprint Review).
│   - **Task**: `New` ➔ `Active` ➔ `Resolved` ➔ `Closed`.
│   - **Bug**: `New` ➔ `Active` ➔ `Resolved` ➔ `Closed` (Tester verify).
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 38.64] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Resear

### Local Evidence (projects):
🔍 Query: "Peer Dev Work Item 281 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 4991 matches across 5862 files. Top 3 shown:

┌── [Rank #1 | Score: 91.53] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:277-279
│   Section: # Bug fix commits
├── ────────────────────────────────────────────────────────
│   # Bug fix commits
│   git commit -m "fix: resolve authentication token refresh issue"
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 53.47] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:454-459
│   Section: ### Team Resources
├── ────────────────────────────────────────────────────────
│   ### Team Resources
│   - Technical discussions: [Team chat/channel]
│   - Bug tracking: [Issue tracker]
│   - Code review: [PR review process]
│   - Knowledge sharing: [Wiki/Notion]
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 51.31] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:265-271
│   Section: ### Branch Strategy
├── ────────────────────────────────────────────────────────
│   ### Branch Strategy
│   - **dev** - Main development branch
│   - **feature/** - Feature branches
│   - **bugfix/** - Bug fix branches
│   - **hotfix/** - Production hotfixes
│   - **release/** - Release preparation branches
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Peer Dev Work Item 281 Bug Bug CDP" | Category: all
📊 Tìm thấy 1188 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 144.72] /home/baoltb/Desktop/wicx-crm-doc/BA/team-process/tfs-work-item-management.md:52-61
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

┌── [Rank #2 | Score: 144.72] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/team-process/tfs-work-item-management.md:52-61
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
