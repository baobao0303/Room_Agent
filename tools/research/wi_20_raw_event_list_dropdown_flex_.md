# Research Report: WI-20 raw-event-list dropdown flex-col

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 09:53:44

## 1. Problem Statement & Scope
- **Research Topic**: `WI-20 raw-event-list dropdown flex-col`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "WI-20 raw-event-list dropdown flex-col" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 14 matches across 20 files. Top 3 shown:

┌── [Rank #1 | Score: 22.54] /home/baoltb/Desktop/Room_Agent/docs/AGENT_PROGRESS.md:147-155
│   Section: ### Phiên #22 — `2026-10-19 09:46:25 +0700` | **Lead (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #22 — `2026-10-19 09:46:25 +0700` | **Lead (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Lead: Bug WI-20 Dropdown tenant scope raw-event-list flex-col
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_lead_bug_wi_20_dropdown_tenant_scope.md
│     - Generated 5-Stage ISTQB Unit Test Suite -> tools/research/gen_test_lead_bug_wi_20_dropdown_tenant_scope.spec.ts
│     - Generated Role Execution Brief -> tools/research/gen_brief_lead_bug_wi_20_dropdown_tenant_scope.md
│   - **File đã tạo/cập nhật**: `tools/research/research_lead_bug_wi_20_dropdown_tenant_scope.md`, `tools/research/gen_test_lead_bug_wi_20_dropdown_tenant_scope.spec.ts`, `tools/research/gen_brief_lead_bug_wi_20_dropdown_tenant_scope.md`
│   - **Bàn giao bước tiếp theo**: Profile Lead tiếp tục hoàn thiện task dựa trên tools/research/research_lead_bug_wi_20_dropdown_tenant_scope.md và tools/research/gen_brief_lead_bug_wi_20_dropdown_tenant_scope.md.
└── ──────────────────────────

### Local Evidence (profiles):
🔍 Query: "WI-20 raw-event-list dropdown flex-col" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 1 matches across 4 files. Top 1 shown:

┌── [Rank #1 | Score: 2.33] /home/baoltb/Desktop/Room_Agent/profiles/qc.md:1-80 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: QC
│   provider: antigravity
│   model: gemini-4-argon-high
│   modeId: full-access
│   thinkingOptionId: high
│   ---
│   Room role: QC (Test Architect, Unit/E2E Test Generator & Independent Quality Gate).
│   
│   MISSION:
│   You are the `C` in the SLPC (`Supervisor - Lead - Peer - QC`) architecture.
│   You do NOT write or fix production feature code for Peer. Your job is to:
│   1. Generate traceable `Testcase` work items and executable unit tests (`*.spec.ts` / `test_*.py`) from the Spec + Codebase using the 5-Stage ISTQB Pipeline (`tools/qc_test_generator.py`).
│   2. Run deterministic automated tests & coverage checks when Peer marks a task `Resolved`.
│   3. Gatekeep `Closed`: Only transition a task to `Closed` when 100% of required Coverage Items (`CI-TPxxx-xx`), Requirements (`REQ-xxx`), and automated test executions pass.
│   
│   WORKFLOW:
│   1. PHASE 1 — 5-STAGE TEST GENERATION (From Spec + Codebase):
│      - Run the QC Test Generator against the target source file and spec/task:
│        `python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> --task-id <id> --out-spec <path/to/

### Local Evidence (tools):
🔍 Query: "WI-20 raw-event-list dropdown flex-col" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 17 matches across 64 files. Top 3 shown:

┌── [Rank #1 | Score: 159.91] /home/baoltb/Desktop/Room_Agent/tools/research/research_lead_bug_wi_20_dropdown_tenant_scope.md:1-4
│   Section: # Research Report: [Lead] Bug WI-20 Dropdown tenant scope raw-event-list flex-col
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Bug WI-20 Dropdown tenant scope raw-event-list flex-col
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 09:46:19
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 76.07] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_task_138_parent_bug_wi_20_cdp_d.md:1-4
│   Section: # Research Report: [Peer] [Task #138 | Parent Bug WI-20] [CDP/DataRaw] - Chuyển layout dropdown chọn phạm vi tenant sang flex-col chuẩn TDS UI trong raw-event-list.component.html và cập nhật unit test trong raw-event-list.component.spec.ts
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] [Task #138 | Parent Bug WI-20] [CDP/DataRaw] - Chuyển layout dropdown chọn phạm vi tenant sang flex-col chuẩn TDS UI trong raw-event-list.component.html và cập nhật unit test trong raw-event-list.component.spec.ts
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 09:51:35

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
