# Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 11:26:58

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor CDP Raw Data Mapping Event Projection Field" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 114 matches across 14 files. Top 3 shown:

┌── [Rank #1 | Score: 149.03] /home/baoltb/Desktop/Paseo_Project/docs/spec/raw-data-mapping-spec.md:1-9
│   Section: # Đặc tả Kỹ thuật & Giao diện Toàn diện: Phân hệ Quản lý & Ánh xạ Dữ liệu Sự kiện Thô (Event Data Mapping & Projection System)
├── ────────────────────────────────────────────────────────
│   # Đặc tả Kỹ thuật & Giao diện Toàn diện: Phân hệ Quản lý & Ánh xạ Dữ liệu Sự kiện Thô (Event Data Mapping & Projection System)
│   
│   > **Mã đặc tả:** `SPEC-CDP-RAW-DATA-MAPPING-MASTER`  
│   > **Nguồn tham chiếu:** Claude Design Artifact `Field mapping UI` (11 Boards: `Main`, `SourceList`, `WebSource`, `WebSource-forms`, `CreateEvent`, `Mapping`, `TestRun`, `Review`, `FbSource`, `FbSource-recent`, `RawData`) kết hợp **UI Wizard 4 bước từ Mockup**.  
│   > **Phạm vi triển khai:** Micro-frontend `apps/mfe-cdp` (`/cdp/data-raw`), thư viện nghiệp vụ `libs/features/raw-event-data`, Backend `DataExtraction` & `Crm`.  
│   > **Công nghệ áp dụng:** Angular 18 Standalone, Signals, Reactive Forms, Thư viện component `tds-ui`, Tailwind CSS, Event-Sourcing Pipeline.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 149.03] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/spec-raw-data-mapping.md:1-9
│   Section: # Đặc tả Kỹ thuật & Giao diện Toàn diện: Phân hệ Quả

### Local Evidence (profiles):
🔍 Query: "Supervisor CDP Raw Data Mapping Event Projection Field" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 21.45] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Supervisor
│   provider: router9
│   model: ag/claude-sonnet-5-5-medium
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: Supervisor (Scope & Intent Guard - SLPC Orchestrator).
│   
│   MISSION:
│   You are the project referee in the SLPC (`Supervisor - Lead - Peer - QC`) architecture. Do not write code, design systems, or review code.
│   Your job:
│   1. Ensure Lead, Peer, and QC do not drift from the User's original intent.
│   2. Track progress through the Harness DB.
│   3. Escalate to the User for decisions on: scope changes, data-deletion risk, cost, or production deploys.
│   
│   WORKFLOW:
│   - Check the board with `python3 tools/harness_manager.py list --source bot --state Active` or `--state Resolved` or `--state Blocked`.
│   - WHEN the User gives a new request: run `python3 tools/harness_manager.py add --type Epic --title "[CDP] - <name>" --source bot --created-by-profile supervisor --assigned-to-profile lead --dispatch` to assign it to Lead.
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the U

### Local Evidence (tools):
🔍 Query: "Supervisor CDP Raw Data Mapping Event Projection Field" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 125 matches across 30 files. Top 3 shown:

┌── [Rank #1 | Score: 62.29] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_mapping_d_li_u_th.md:1-4
│   Section: # Research Report: [Supervisor] Mapping dữ liệu thô
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Mapping dữ liệu thô
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 11:02:29
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 48.92] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_supervisor_mapping_d_li_u_th.md:1-8
│   Section: # Auto-Generated Execution Brief (Supervisor)
├── ────────────────────────────────────────────────────────
│   # Auto-Generated Execution Brief (Supervisor)
│   
│   - **Profile**: `Supervisor`
│   - **Topic / Task**: Mapping dữ liệu thô
│   - **Task ID**: `N/A`
│   - **Generated At**: `2026-10-15 11:02:32 +0700`
│   - **Research Report**: `tools/research/research_supervisor_mapping_d_li_u_th.md`
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 44.46] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_paseo_m_u1edf_ch_u01b0a_l.md:131-137
│   Section: ## 3. Findings & Spec Mapping
├── ────────────────────────────────────────────────────────
│   ## 3

### Local Evidence (projects):
🔍 Query: "Supervisor CDP Raw Data Mapping Event Projection Field" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 11421 matches across 5859 files. Top 3 shown:

┌── [Rank #1 | Score: 59.8] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/apps/mfe-cdp/public/assets/i18n/en/raw-event-data.json:51-74
│   Section: Lines 51-74
├── ────────────────────────────────────────────────────────
│   "TITLE": "Compare Event Payloads (JSON Diff)",
│           "LOADING": "Loading 2 event payloads for comparison...",
│           "CHECK_VALUE": "Compare value differences (Check Value)",
│           "STRUCT_HINT": "Default: structure comparison (highlights missing fields / key differences)",
│           "LEGEND_KEY_DIFF": "Missing field / Key difference",
│           "LEGEND_VAL_DIFF": "Value difference",
│           "EVENT_A": "Event A",
│           "EVENT_B": "Event B",
│           "CLOSE": "Close"
│         },
│         "MESSAGES": {
│           "FETCH_ERROR": "Unable to load raw event list.",
│           "FETCH_DETAIL_ERROR": "Unable to load event payload details.",
│           "COMPARE_WARN": "Please select 2 rows to compare payloads.",
│           "COPIED": "Copied!",
│           "COPIED_EVENT_ID": "Event ID copied!",
│           "COPIED_EVENT_ID_A": "Event ID A copied!",
│           "COPIED_EVENT_ID_B": "Event ID B copied!",
│           "COPIED_PAYLOAD_A": "Payload Event A copied!",
│           "COPIED_PAYLOAD_B": "Payload Event B copied!"
│         }
│       }
│     

### CRM BA Spec Evidence:
🔍 Query: "Supervisor CDP Raw Data Mapping Event Projection Field" | Category: all
📊 Tìm thấy 2328 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 84.7] /home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/stories/Phase 1_User_Stories/UC4.08 - Quản lý custom field theo tenant.md:133-139
│   Section: #### 1.5. Hard-delete field (chưa có data)
├── ────────────────────────────────────────────────────────
│   #### 1.5. Hard-delete field (chưa có data)
│   
│   1. **[Quản trị viên]** Nhấn **"Xoá"** trên dòng field chưa có data (`custom_field_value` count = 0).
│   2. **[WiCX CRM]** Xoá definition (hard); ghi audit log.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 84.7] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 1_User_Stories/UC4.08 - Quản lý custom field theo tenant.md:133-139
│   Section: #### 1.5. Hard-delete field (chưa có data)
├── ────────────────────────────────────────────────────────
│   #### 1.5. Hard-delete field (chưa có data)
│   
│   1. **[Quản trị viên]** Nhấn **"Xoá"** trên dòng field chưa có data (`custom_field_value` count = 0).
│   2. **[WiCX CRM]** Xoá definition (hard); ghi audit log.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 80.94] /home/baoltb/Desktop/wicx-crm-doc/BA/planning-artifacts/references/07. Data Model CDP tổng thể.md:1-9
│   Section: # 3\. Data Model CDP tổng thể

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
