# Research Report: JsonViewer hover copy path value auto hide badge Version History Diff Rollback

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:47:57

## 1. Problem Statement & Scope
- **Research Topic**: `JsonViewer hover copy path value auto hide badge Version History Diff Rollback`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "JsonViewer hover copy path value auto hide badge" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 12 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 81.49] /home/baoltb/Desktop/Room_Agent/docs/AGENT_PROGRESS.md:358-366
│   Section: ### Phiên #185 — `2026-10-19 15:30:27 +0700` | **Lead (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #185 — `2026-10-19 15:30:27 +0700` | **Lead (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Lead: Work Item #2103 [Bug]: [JsonViewer]: Tách biệt hover copy path/value và tự động tắt badge sau khi sao chép
│   1. Hover field (key) chỉ hiển thị nút copy path, hover value chỉ hiển thị nút copy value (tránh hiện cả 2 cùng lúc). 2. Sau khi bấm sao chép (copy path / copy value), badge 'Đã chép ...' phải tự động ẩn (reset state về null sau 1.5s-2s) thay vì dính cứng trên giao diện.
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_lead_work_item_2103_bug_jsonviewer_t.md
│     - Generated Role Execution Brief -> tools/research/gen_brief_lead_work_item_2103_bug_jsonviewer_t.md
│   - **File đã tạo/cập nhật**: `tools/research/research_lead_work_item_2103_bug_jsonviewer_t.md`, `tools/research/gen_brief_lead_work_item_2103_bug_jsonviewer_t.md`
│   - **Bàn giao bước tiếp theo**: Profile Lead tiếp tục hoàn thiện task dựa trên tools/research/re

### Local Evidence (profiles):
🔍 Query: "JsonViewer hover copy path value auto hide badge" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 2 matches across 4 files. Top 2 shown:

┌── [Rank #1 | Score: 3.59] /home/baoltb/Desktop/Room_Agent/profiles/qc.md:1-288 (truncated to 30 lines)
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
│        `python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> --task-id <id> --out-spe

### Local Evidence (tools):
🔍 Query: "JsonViewer hover copy path value auto hide badge" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 12 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 125.56] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_jsonviewer_ambiguous_1_click_co.md:1-4
│   Section: # Research Report: [Peer] [JsonViewer]: Ambiguous 1-click copy path instead of value when user clicks copy button beside value
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] [JsonViewer]: Ambiguous 1-click copy path instead of value when user clicks copy button beside value
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:50:48
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 60.78] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_jsonviewer_large_gap_between_ke.md:1-4
│   Section: # Research Report: [Peer] [JsonViewer]: Large gap between key and colon when hidden copy button occupies layout space
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] [JsonViewer]: Large gap between key and colon when hidden copy button occupies layout space
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:22:07
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 55.97] /home/baoltb/Desktop/Room_Agent/tools/research/rese

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
