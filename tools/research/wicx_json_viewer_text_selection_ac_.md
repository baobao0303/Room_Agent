# Research Report: wicx-json-viewer text selection AC-MAP-09 AC-MAP-10

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:28:44

## 1. Problem Statement & Scope
- **Research Topic**: `wicx-json-viewer text selection AC-MAP-09 AC-MAP-10`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "wicx-json-viewer text selection AC-MAP-09 AC-MAP-10" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 9 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 125.91] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:290-312
│   Section: ### 4.1. Task #885: `wicx-json-viewer` Text Selection & 1-Click Path Copy (`AC-MAP-09`, `AC-MAP-10`)
├── ────────────────────────────────────────────────────────
│   ### 4.1. Task #885: `wicx-json-viewer` Text Selection & 1-Click Path Copy (`AC-MAP-09`, `AC-MAP-10`)
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
│        - Khi người dùng bôi đen văn bản (`window.getSelection()?.toString().length > 0`) trên dòng JSON, sự kiện click trên `<button>` không được vô tình đóng/mở nhánh JSON làm mất vùng bôi đen.
│     2. **`AC-MAP-10` (1-Click Copy JSON Path)**:
│      

### Local Evidence (profiles):
⚠️ No matching content found for query 'wicx-json-viewer text selection AC-MAP-09 AC-MAP-10' in /home/baoltb/Desktop/Room_Agent/profiles (Scanned 4 files, 4 sections).

### Local Evidence (tools):
🔍 Query: "wicx-json-viewer text selection AC-MAP-09 AC-MAP-10" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 15 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 148.33] /home/baoltb/Desktop/Room_Agent/tools/research/research_qc_verify_resolved_task_885_fix_json.md:1-4
│   Section: # Research Report: [QC] Verify Resolved Task #885 (Fix JSON viewer text selection AC-MAP-09 and 1-click copy JSON path AC-MAP-10 in wicx-json-viewer) and run unit test suite
├── ────────────────────────────────────────────────────────
│   # Research Report: [QC] Verify Resolved Task #885 (Fix JSON viewer text selection AC-MAP-09 and 1-click copy JSON path AC-MAP-10 in wicx-json-viewer) and run unit test suite
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:27:06
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 103.42] /home/baoltb/Desktop/Room_Agent/tools/research/wicx_json_viewer_user_select_text_s.md:1-4
│   Section: # Research Report: wicx-json-viewer user-select text selection 1-click copy path
├── ────────────────────────────────────────────────────────
│   # Research Report: wicx-json-viewer user-select text selection 1-click copy path
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:17:18
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 72.9] /home/baoltb/Desktop/Room_Agent/tools/

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
