# Research Report: Verify Resolved Task #887 GeneralConfigComponent 4-Step Stepper AC-MAP-03 AC-MAP-04

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:14:57

## 1. Problem Statement & Scope
- **Research Topic**: `Verify Resolved Task #887 GeneralConfigComponent 4-Step Stepper AC-MAP-03 AC-MAP-04`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Verify Resolved Task 887 GeneralConfigComponent 4-Step Stepper AC-MAP-03" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 23 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 81.72] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:360-376
│   Section: ### 4.3. Task #887: Screen 2 - General Configuration & JSON Field Mapping Stepper (`AC-MAP-03`, `AC-MAP-04`)
├── ────────────────────────────────────────────────────────
│   ### 4.3. Task #887: Screen 2 - General Configuration & JSON Field Mapping Stepper (`AC-MAP-03`, `AC-MAP-04`)
│   - **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/general-config/general-config.component.{ts,html,scss,spec.ts}`
│   - **Requirements**:
│     1. **4-Step Progress Stepper (`AC-MAP-03`)**:
│        - Hiển thị 4 bước: `1. Chưa cấu hình` ➔ `2. Đã cấu hình chung` ➔ `3. Đang mapping (0/2 form đã map xong)` ➔ `4. Hoàn tất`.
│     2. **Sub-navigation Tabs**:
│        - `[Tab] Cấu hình chung`, `[Tab] Sự kiện hành vi (4)`, `[Tab] Lịch sử hoạt động`.
│     3. **JSON Field Mapping Table (`AC-MAP-03`)**:
│        - `Trang liên kết` ➔ `site_id` (Locked icon, không cho sửa/xóa).
│        - `Loại sự kiện` ➔ `data.system_event_type` (Locked icon, không cho sửa/xóa).
│        - `Mã sự kiện` ➔ `event_id` (Cho phép chọn path / xóa).
│        - `Thời gian nhận` ➔ `received_at` (Cho phép chọn path / xóa).
│        - Nút `+ Thêm trường` và `[Lưu cấu hình]`.
│     4. **Sam

### Local Evidence (profiles):
🔍 Query: "Verify Resolved Task 887 GeneralConfigComponent 4-Step Stepper AC-MAP-03" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 15.45] /home/baoltb/Desktop/Room_Agent/profiles/peer.md:1-40 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Peer
│   provider: antigravity
│   model: gemini-4-argon-high
│   modeId: full-access
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
│        `python3 tools/cal

### Local Evidence (tools):
🔍 Query: "Verify Resolved Task 887 GeneralConfigComponent 4-Step Stepper AC-MAP-03" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 30 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 153.88] /home/baoltb/Desktop/Room_Agent/tools/research/task_887_generalconfigcomponent_ste.md:1-4
│   Section: # Research Report: Task 887 GeneralConfigComponent Stepper 4 buoc json mapping AC-MAP-03 AC-MAP-04
├── ────────────────────────────────────────────────────────
│   # Research Report: Task 887 GeneralConfigComponent Stepper 4 buoc json mapping AC-MAP-03 AC-MAP-04
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:01:50
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 89.08] /home/baoltb/Desktop/Room_Agent/tools/research/research_qc_verify_resolved_task_1173_and_run.md:1-4
│   Section: # Research Report: [QC] Verify Resolved Task #1173 and run unit test suite
├── ────────────────────────────────────────────────────────
│   # Research Report: [QC] Verify Resolved Task #1173 and run unit test suite
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:55:26
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 88.48] /home/baoltb/Desktop/Room_Agent/tools/research/research_qc_verify_resolved_task_138_parent_b.md:1-4
│   Section: # Research Report: [QC] Verify Resolved Task #138 (Parent Bug WI-2

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
