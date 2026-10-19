# Research Report: JsonViewer Bug 1508 position absolute segment-copy-path-btn

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:21:05

## 1. Problem Statement & Scope
- **Research Topic**: `JsonViewer Bug 1508 position absolute segment-copy-path-btn`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "JsonViewer Bug 1508 position absolute segment-copy-path-btn" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 22 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 37.12] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:290-341 (truncated to 30 lines)
│   Section: ### 4.1. Task #885, Bug #1173 & Bug #1508: `wicx-json-viewer` Text Selection, 1-Click Copy Path (Out-of-Flow Overlay Beside Key) & 1-Click Copy Value (Beside Value) (`AC-MAP-09`, `AC-MAP-10`, `Bug #1173`, `Bug #1508`)
├── ────────────────────────────────────────────────────────
│   ### 4.1. Task #885, Bug #1173 & Bug #1508: `wicx-json-viewer` Text Selection, 1-Click Copy Path (Out-of-Flow Overlay Beside Key) & 1-Click Copy Value (Beside Value) (`AC-MAP-09`, `AC-MAP-10`, `Bug #1173`, `Bug #1508`)
│   - **Files**: `projects/wicx-crm-fe/libs/wicx-core/src/libs/json-viewer/json-viewer.component.{ts,html,scss,spec.ts}`
│   - **Requirements**:
│     1. **`AC-MAP-09` (Bôi đen văn bản tự do - Free Text Selection)**:
│        - Trong `json-viewer.component.scss`, loại bỏ hoặc ghi đè hành vi chặn bôi đen của thẻ `<button>` bằng quy tắc:
│          ```scss
│          .segment-key,
│          .segment-value,
│          .segment-primitive {
│            user-select: text !important;
│            -webkit-user-select: text !important;
│            cursor: text;
│          }
│          .toggler {
│            user-select: none;
│            cursor: pointer;
│          }
│   

### Local Evidence (profiles):
🔍 Query: "JsonViewer Bug 1508 position absolute segment-copy-path-btn" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 3 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 2.05] /home/baoltb/Desktop/Room_Agent/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --p

### Local Evidence (tools):
🔍 Query: "JsonViewer Bug 1508 position absolute segment-copy-path-btn" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 26 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 39.5] /home/baoltb/Desktop/Room_Agent/tools/research/research_lead_kh_c_ph_c_bug_wi_386_tds_panel_.md:1-4
│   Section: # Research Report: [Lead] Khắc phục Bug WI-386 tds-panel-scroll DetailCustomerComponent
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Khắc phục Bug WI-386 tds-panel-scroll DetailCustomerComponent
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 10:09:07
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 39.07] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_jsonviewer_large_gap_between_ke.md:1-4
│   Section: # Research Report: [Peer] [JsonViewer]: Large gap between key and colon when hidden copy button occupies layout space
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] [JsonViewer]: Large gap between key and colon when hidden copy button occupies layout space
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:16:33
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 39.04] /home/baoltb/Desktop/Room_Agent/tools/research/research_supervisor_bug_1174_tab_unknown_hien.md:1-4
│   Section: # Resea

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
