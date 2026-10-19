# Research Report: QC Verify Task 888 Behavior Events Toggle Form Field Mapping AC-MAP-05 AC-MAP-06

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 16:10:54

## 1. Problem Statement & Scope
- **Research Topic**: `QC Verify Task 888 Behavior Events Toggle Form Field Mapping AC-MAP-05 AC-MAP-06`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "QC Verify Task 888 Behavior Events Toggle Form" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 13 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 130.01] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:385-399
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
│          - `form.tds-input-1` (`"0969733325"`) ➔ `phone` · `CH-SDT

### Local Evidence (profiles):
🔍 Query: "QC Verify Task 888 Behavior Events Toggle Form" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 17.36] /home/baoltb/Desktop/Room_Agent/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile QC --

### Local Evidence (tools):
🔍 Query: "QC Verify Task 888 Behavior Events Toggle Form" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 27 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 192.54] /home/baoltb/Desktop/Room_Agent/tools/research/research_peer_task_888_behavior_events_toggle.md:1-4
│   Section: # Research Report: [Peer] Task #888: Behavior Events Toggle & Form Field Mapping (AC-MAP-05..06)
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] Task #888: Behavior Events Toggle & Form Field Mapping (AC-MAP-05..06)
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 15:29:02
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 130.46] /home/baoltb/Desktop/Room_Agent/tools/research/gen_brief_qc_verify_resolved_task_888_behavior.md:1-8
│   Section: # Auto-Generated Execution Brief (QC)
├── ────────────────────────────────────────────────────────
│   # Auto-Generated Execution Brief (QC)
│   
│   - **Profile**: `QC`
│   - **Topic / Task**: Verify Resolved Task #888 (Behavior Events Toggle & Form Field Mapping AC-MAP-05, AC-MAP-06) and run unit test suite
│   - **Task ID**: `888`
│   - **Generated At**: `2026-10-19 16:06:03 +0700`
│   - **Research Report**: `tools/research/research_qc_verify_resolved_task_888_behavior.md`
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 89.08] /home/baoltb/Desktop/Room_Agent/tools/research/

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
