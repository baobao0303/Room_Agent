# Research Report: [Peer Dev] Fix layout Stepper 4 buoc tren cung va dua 2 pane vao Step 1

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:54:24

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Fix layout Stepper 4 buoc tren cung va dua 2 pane vao Step 1`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Fix layout Stepper 4 buoc tren" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 612 matches across 19 files. Top 3 shown:

┌── [Rank #1 | Score: 48.36] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:1022-1033
│   Section: ### Phiên #56 — `2026-10-15 13:45:11 +0700` | **Peer Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #56 — `2026-10-15 13:45:11 +0700` | **Peer Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Peer Dev: Work Item #281 [Bug]: [Bug] [CDP/Shell]: Khi mở CDP Raw Event và sidebar /setting thì nguồn bị mock tĩnh và active route sai
│   Khắc phục lỗi trên nhánh fix/20261015-RemoveMockSources (projects/wicx-crm-fe):
│   1. mfe-cdp: Xóa mock sources tĩnh trong raw-event-list, lấy động từ API và tự động phát hiện sources từ eventsList; xóa tenantSubName thừa.
│   2. app-shell: LayoutStore hỗ trợ generic path cho route con (/setting/employee); chuẩn hóa breadcrumbs và sidebar menu item.
│   3. Đảm bảo toàn bộ Unit Test (raw-event-list, layout, sidebar) pass 100%.
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_peer_dev_work_item_281_bug_bug_cdp_s.md
│     - Generated Role Execution Brief -> tools/research/gen_brief_peer_dev_work_item_281_bug_bug_cdp_s.md
│   - **File đã tạo/cập nhật**: `tools/research/research_peer_dev_work_item_2

### Local Evidence (profiles):
🔍 Query: "Peer Dev Fix layout Stepper 4 buoc tren" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 16.38] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile

### Local Evidence (tools):
🔍 Query: "Peer Dev Fix layout Stepper 4 buoc tren" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 299 matches across 70 files. Top 3 shown:

┌── [Rank #1 | Score: 154.34] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_fix_layout_stepper_4_buoc.md:1-4
│   Section: # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:52:36
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 85.88] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn I

### Local Evidence (projects):
🔍 Query: "Peer Dev Fix layout Stepper 4 buoc tren" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 4452 matches across 5887 files. Top 3 shown:

┌── [Rank #1 | Score: 53.6] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:277-279
│   Section: # Bug fix commits
├── ────────────────────────────────────────────────────────
│   # Bug fix commits
│   git commit -m "fix: resolve authentication token refresh issue"
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 32.36] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:265-271
│   Section: ### Branch Strategy
├── ────────────────────────────────────────────────────────
│   ### Branch Strategy
│   - **dev** - Main development branch
│   - **feature/** - Feature branches
│   - **bugfix/** - Bug fix branches
│   - **hotfix/** - Production hotfixes
│   - **release/** - Release preparation branches
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 28.47] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/apps/app-shell/src/app/layouts/layout.component.html:26-40
│   Section: Lines 26-40
├── ────────────────────────────────────────────────────────
│   </tds-layout>
│   </tds-layout>
│   
│   <!-- Full-screen Translucent Blurred Loading Overlay when switching tenant -->
│   @if (isSwitchingTenant()) {
│   <div
│     class="fixed inset-0 z-[9999] flex flex-col items-center justify-cen

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
