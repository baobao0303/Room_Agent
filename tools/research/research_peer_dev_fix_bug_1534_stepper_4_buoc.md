# Research Report: [Peer Dev] Fix Bug 1534: Stepper 4 buoc nam ngoai tren cung va layout 2-pane nam trong Step 1

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:39:15

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Fix Bug 1534: Stepper 4 buoc nam ngoai tren cung va layout 2-pane nam trong Step 1`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Fix Bug 1534 Stepper 4 buoc" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 713 matches across 21 files. Top 3 shown:

┌── [Rank #1 | Score: 74.82] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:948-955
│   Section: ### Phiên #167 — `2026-10-15 14:54:28 +0700` | **Peer Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #167 — `2026-10-15 14:54:28 +0700` | **Peer Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Peer Dev: Fix layout Stepper 4 buoc tren cung va dua 2 pane vao Step 1
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_peer_dev_fix_layout_stepper_4_buoc_t.md
│     - Generated Role Execution Brief -> tools/research/gen_brief_peer_dev_fix_layout_stepper_4_buoc_t.md
│   - **File đã tạo/cập nhật**: `tools/research/research_peer_dev_fix_layout_stepper_4_buoc_t.md`, `tools/research/gen_brief_peer_dev_fix_layout_stepper_4_buoc_t.md`
│   - **Bàn giao bước tiếp theo**: Profile Peer Dev tiếp tục hoàn thiện task dựa trên tools/research/research_peer_dev_fix_layout_stepper_4_buoc_t.md và tools/research/gen_brief_peer_dev_fix_layout_stepper_4_buoc_t.md.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 66.82] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:930-935
│   Section: ### Phiên #170 — `2026-1

### Local Evidence (profiles):
🔍 Query: "Peer Dev Fix Bug 1534 Stepper 4 buoc" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 20.39] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile QC

### Local Evidence (tools):
🔍 Query: "Peer Dev Fix Bug 1534 Stepper 4 buoc" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 459 matches across 97 files. Top 3 shown:

┌── [Rank #1 | Score: 192.97] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_fix_layout_stepper_4_buoc_t.md:1-4
│   Section: # Research Report: [Peer Dev] Fix layout Stepper 4 buoc tren cung va dua 2 pane vao Step 1
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Fix layout Stepper 4 buoc tren cung va dua 2 pane vao Step 1
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:54:24
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 119.53] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_fix_layout_stepper_4_buoc.md:1-4
│   Section: # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:52:36
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 116.1] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_peer_dev_fix_layout_stepper_4_buoc_t.md:1-8
│   Section: # Auto-Generated Execution Brief (Peer Dev)
├── ──────────────

### Local Evidence (projects):
🔍 Query: "Peer Dev Fix Bug 1534 Stepper 4 buoc" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 3960 matches across 5899 files. Top 3 shown:

┌── [Rank #1 | Score: 80.94] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:277-279
│   Section: # Bug fix commits
├── ────────────────────────────────────────────────────────
│   # Bug fix commits
│   git commit -m "fix: resolve authentication token refresh issue"
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 40.68] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:265-271
│   Section: ### Branch Strategy
├── ────────────────────────────────────────────────────────
│   ### Branch Strategy
│   - **dev** - Main development branch
│   - **feature/** - Feature branches
│   - **bugfix/** - Bug fix branches
│   - **hotfix/** - Production hotfixes
│   - **release/** - Release preparation branches
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 34.01] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:454-459
│   Section: ### Team Resources
├── ────────────────────────────────────────────────────────
│   ### Team Resources
│   - Technical discussions: [Team chat/channel]
│   - Bug tracking: [Issue tracker]
│   - Code review: [PR review process]
│   - Knowledge sharing: [Wiki/Notion]
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Peer Dev Fix Bug 1534 Stepper 4 buoc" | Category: all
📊 Tìm thấy 2348 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 74.74] /home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/sprints/sprint-4/sprint-4.md:61-74
│   Section: ## 🎯 Mục tiêu Sprint 4
├── ────────────────────────────────────────────────────────
│   ## 🎯 Mục tiêu Sprint 4
│   
│   **📋 Mục tiêu Sprint 4** *(đồng bộ theo board — cập nhật 23/09/2026)*
│   
│   | Priority | Mục tiêu | Target/Impact | Related Work Items | Success Criteria | Nguồn |
│   | -------- | -------- | ------------- | ------------------ | ---------------- | ----- |
│   | **P1** | **Xử lý 10 bug P1** phát sinh từ test IAM (đăng nhập/đăng xuất) + Thông tin doanh nghiệp | Đưa 5 bug `New` + 2 bug `Active` về `Resolved/Closed`, verify & close 3 bug đã `Resolved`; gỡ chặn nghiệm thu nhóm story IAM | 159339 · 159341 · 159344 · 159345 · 159352 · 159353 · 159450 · 159452 · 159453 · 159458 | 10 bug đạt `Resolved/Closed`, không còn bug `New` | 🔄 Carry-over Sprint 3 |
│   | **P2** | **Đóng nghiệm thu 13 User Story IAM/E1/E2** — đã xong dev từ Sprint 3, còn `Active` | Gỡ điểm nghẽn story completion; đưa 13 US `Active` về `Resolved/Closed` (12 US đã ở iteration Sprint 4 + #156631 dời nốt) | 156587 · 156594 · 156596 · 156597 · 156598 · 156631 · 156662 · 156663 · 157000 · 157001 · 157098 · 157100 · 157946 | 13 US đạt `Resolved/Closed`; khâu verify/đóng story theo kịp dev | 🔄 Carry-over Sprint 3 |
│   | **P3** | **De

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
