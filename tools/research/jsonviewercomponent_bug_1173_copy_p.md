# Research Report: JsonViewerComponent Bug 1173 Copy Path vs Copy Value

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:57:57

## 1. Problem Statement & Scope
- **Research Topic**: `JsonViewerComponent Bug 1173 Copy Path vs Copy Value`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "JsonViewerComponent Bug 1173 Copy Path vs Copy Value" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 23 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 88.65] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:290-336 (truncated to 30 lines)
│   Section: ### 4.1. Task #885 & Bug #1173: `wicx-json-viewer` Text Selection, 1-Click Copy Path (Beside Key) & 1-Click Copy Value (Beside Value) (`AC-MAP-09`, `AC-MAP-10`, `Bug #1173`)
├── ────────────────────────────────────────────────────────
│   ### 4.1. Task #885 & Bug #1173: `wicx-json-viewer` Text Selection, 1-Click Copy Path (Beside Key) & 1-Click Copy Value (Beside Value) (`AC-MAP-09`, `AC-MAP-10`, `Bug #1173`)
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
│          ```
│        - Khi người dùng bôi đen văn bản (`window.getSelection()?.toString().length

### Local Evidence (profiles):
🔍 Query: "JsonViewerComponent Bug 1173 Copy Path vs Copy Value" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 3.5] /home/baoltb/Desktop/Room_Agent/profiles/qc.md:1-288 (truncated to 30 lines)
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
│        `python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> --task-id <id> --out-

### Local Evidence (tools):
🔍 Query: "JsonViewerComponent Bug 1173 Copy Path vs Copy Value" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 17 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 101.94] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_jsonviewer_ambiguous_1_click_co.md:1-4
│   Section: # Research Report: [Peer] [JsonViewer]: Ambiguous 1-click copy path instead of value when user clicks copy button beside value
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] [JsonViewer]: Ambiguous 1-click copy path instead of value when user clicks copy button beside value
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:50:48
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 66.58] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_thuc_thi_task_885_sua_loi_user_.md:1-4
│   Section: # Research Report: [Peer] Thuc thi Task #885: Sua loi user-select: none trong wicx-json-viewer de cho phep boi den copy chuot tu do (AC-MAP-09) va bo sung 1-click copy path JSON (AC-MAP-10) theo docs/spec/cdp-field-mapping-ui-spec.md.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] Thuc thi Task #885: Sua loi user-select: none trong wicx-json-viewer de cho phep boi den copy chuot tu do (AC-MAP-09) va bo sung 1-click copy path JSON (AC-MAP-10) theo docs/spec/cdp-field-mapping-ui-spec.md.
│   
│   > Generated

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
