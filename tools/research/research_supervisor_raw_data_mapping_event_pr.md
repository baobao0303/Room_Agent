# Research Report: [Supervisor] Raw Data Mapping & Event Projection Field Mapping UI implementation with tds-tabset card

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:03:35

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Raw Data Mapping & Event Projection Field Mapping UI implementation with tds-tabset card`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Raw Data Mapping Event Projection Field Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 200 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 229.51] /home/baoltb/Desktop/Paseo_Project/docs/spec/research-raw-data-mapping-projection.md:1-9
│   Section: # Nghiên cứu Chuyên sâu: CDP Raw Data Mapping & Event Projection Field Mapping UI
├── ────────────────────────────────────────────────────────
│   # Nghiên cứu Chuyên sâu: CDP Raw Data Mapping & Event Projection Field Mapping UI
│   
│   > **Mã tài liệu:** `RESEARCH-CDP-RAW-DATA-MAPPING-PROJECTION-20261015`  
│   > **Ngày lập:** 15/10/2026  
│   > **Người thực hiện:** Combo-Lead (Paseo SLPC Architecture)  
│   > **Phạm vi:** Micro-frontend `apps/mfe-cdp` (`/cdp/data-raw`), library `libs/features/raw-event-data`, Backend services (`WiCX.Ingestion`, `WiCX.EventArchive`, `WiCX.DataExtraction`, `WiCX.Crm`), cơ chế Event Projection DB `wicx_projection`.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 173.39] /home/baoltb/Desktop/Paseo_Project/docs/spec/raw-data-mapping-spec.md:1-9
│   Section: # Đặc tả Kỹ thuật & Giao diện Toàn diện: Phân hệ Quản lý & Ánh xạ Dữ liệu Sự kiện Thô (Event Data Mapping & Projection System)
├── ────────────────────────────────────────────────────────
│   # Đặc tả Kỹ thuật & Giao diện Toàn diện: Phân hệ Quản lý & Ánh xạ Dữ liệu Sự kiện Thô (Event Data Mapping & Projection System)
│   
│   > **Mã đặc tả:** `SP

### Local Evidence (profiles):
🔍 Query: "Supervisor Raw Data Mapping Event Projection Field Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 17.18] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell t

### Local Evidence (tools):
🔍 Query: "Supervisor Raw Data Mapping Event Projection Field Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 185 matches across 45 files. Top 3 shown:

┌── [Rank #1 | Score: 292.18] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_cdp_raw_data_mapping_even.md:1-4
│   Section: # Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 11:26:58
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 129.62] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_supervisor_cdp_raw_data_mapping_even.md:1-8
│   Section: # Auto-Generated Execution Brief (Supervisor)
├── ────────────────────────────────────────────────────────
│   # Auto-Generated Execution Brief (Supervisor)
│   
│   - **Profile**: `Supervisor`
│   - **Topic / Task**: CDP Raw Data Mapping & Event Projection Field Mapping UI
│   - **Task ID**: `N/A`
│   - **Generated At**: `2026-10-15 11:27:02 +0700`
│   - **Research Report**: `tools/research/research_supervisor_cdp_raw_data_mapping_even.md`
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 118.74] /home/baoltb/Desktop/Paseo_Project/tools/research/raw_data_mapping_step_1_cha

### Local Evidence (projects):
🔍 Query: "Supervisor Raw Data Mapping Event Projection Field Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 11310 matches across 5870 files. Top 3 shown:

┌── [Rank #1 | Score: 59.87] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/data-raw/step1-general-mapping.spec.ts:401-414
│   Section: Lines 401-414
├── ────────────────────────────────────────────────────────
│   created_at: '2026-10-13 14:18:12',
│           },
│         ];
│   
│         const rows = flattenRawEventList(events);
│         expect(rows).toHaveLength(2);
│         expect(rows[0].rowNumber).toBe(1);
│         expect(rows[0]['data.system_event_type']).toBe('formSubmit');
│         expect(rows[1].rowNumber).toBe(2);
│         expect(rows[1]['data.system_event_type']).toBe('pageView');
│         expect(rows[1].form_value).toBe('{}');
│       });
│     });
│   });
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 58.77] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/libs/features/raw-event-data/data-access/src/utils/step1-general-mapping.ts:176-225 (truncated to 30 lines)
│   Section: Lines 176-225
├── ────────────────────────────────────────────────────────
│   /**
│    * Format JSON payload with line numbers (1..N).
│    * Suitable for code viewers, and exposes raw string for direct clipboard copying.
│    */
│   export function formatJsonWithLineNumbers(payload: unknown): FormattedJsonPreview {
│     if (pa

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
