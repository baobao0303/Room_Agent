# Research Report: WI-888 WI-889 WI-890 Behavior Events Form Mapping Version History Diff Rollback

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:48:56

## 1. Problem Statement & Scope
- **Research Topic**: `WI-888 WI-889 WI-890 Behavior Events Form Mapping Version History Diff Rollback`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "WI-888 WI-889 WI-890 Behavior Events Form Mapping Version" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 11 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 104.04] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:377-391
│   Section: ### 4.4. Task #888: Screen 3 - Behavior Events Toggle & Form Field Mapping (`AC-MAP-05`, `AC-MAP-06`)
├── ────────────────────────────────────────────────────────
│   ### 4.4. Task #888: Screen 3 - Behavior Events Toggle & Form Field Mapping (`AC-MAP-05`, `AC-MAP-06`)
│   - **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/behavior-form-mapping/behavior-form-mapping.component.{ts,html,scss,spec.ts}`
│   - **Requirements**:
│     1. **Behavior Events Table (`AC-MAP-05`)**:
│        - Hiển thị 4 sự kiện: `Gửi form` (`AutoFormSubmit`, 8 lượt), `Xem trang` (`PageView`, 3.281 lượt), `Nhấp chuột` (`AutoClick`, 2.089 lượt), `Tỷ lệ đọc trang` (`ScrollDepth`, 711 lượt).
│        - Checkbox `Lưu vào Hồ sơ KH` cập nhật tức thì qua `FieldMappingService.toggleBehaviorEvent(eventType)`.
│     2. **Detected Web Forms & Form Field Mapping Detail (`AC-MAP-06`)**:
│        - Danh sách 2 form đã ghi nhận: `Form liên hệ` (`/lien-he.html`, `FORM-01`, 4 trường) và `Form đăng ký dùng thử` (`/dang-ky-dung-thu.html`, `FORM-02`, 3 trường) với nút `[Cấu hình mapping]`.
│        - Màn hình chi tiết Mapping Form liên hệ:
│          - `form.tds-input-1` (`"0969733325"`) ➔ `phone

### Local Evidence (profiles):
🔍 Query: "WI-888 WI-889 WI-890 Behavior Events Form Mapping Version" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 1 matches across 4 files. Top 1 shown:

┌── [Rank #1 | Score: 1.06] /home/baoltb/Desktop/Room_Agent/profiles/qc.md:1-288 (truncated to 30 lines)
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
│        `python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> --task-id <id> 

### Local Evidence (tools):
🔍 Query: "WI-888 WI-889 WI-890 Behavior Events Form Mapping Version" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 28 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 119.27] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_task_888_behavior_events_toggle.md:1-4
│   Section: # Research Report: [Peer] Task #888: Behavior Events Toggle & Form Field Mapping (AC-MAP-05..06)
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] Task #888: Behavior Events Toggle & Form Field Mapping (AC-MAP-05..06)
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:29:02
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 58.03] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_task_888_behavior_events_toggle.md:11-28
│   Section: ### Local Evidence (docs):
├── ────────────────────────────────────────────────────────
│   ### Local Evidence (docs):
│   🔍 Query: "Peer Task 888 Behavior Events Toggle Form Field" | Target: /home/baoltb/Desktop/Room_Agent/docs
│   📊 Found 19 matches across 25 files. Top 3 shown:
│   
│   ┌── [Rank #1 | Score: 188.0] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:377-391
│   │   Section: ### 4.4. Task #888: Screen 3 - Behavior Events Toggle & Form Field Mapping (`AC-MAP-05`, `AC-MAP-06`)
│   ├── ────────────────────────────────────────────────────────
│   │   ### 4.4

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
