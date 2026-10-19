# Research Report: customer list tableColumns visibleColumnsWidth LAST_ACTIVITY

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 10:04:44

## 1. Problem Statement & Scope
- **Research Topic**: `customer list tableColumns visibleColumnsWidth LAST_ACTIVITY`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "customer list tableColumns visibleColumnsWidth LAST_ACTIVITY" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 28 matches across 20 files. Top 3 shown:

┌── [Rank #1 | Score: 29.66] /home/baoltb/Desktop/Room_Agent/docs/spec/wicx-crm-fe/design/customer-detail-drawer.md:468-469
│   Section: ## 7. Câu hỏi mở / Quyết định
├── ────────────────────────────────────────────────────────
│   ## 7. Câu hỏi mở / Quyết định
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 29.47] /home/baoltb/Desktop/Room_Agent/docs/spec/rsbuild-angular-setup-checklist-spec.md:11-12
│   Section: # PHẦN 1: THIẾT LẬP NHỮNG GÌ? (WHAT TO SETUP)
├── ────────────────────────────────────────────────────────
│   # PHẦN 1: THIẾT LẬP NHỮNG GÌ? (WHAT TO SETUP)
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 29.37] /home/baoltb/Desktop/Room_Agent/docs/spec/rsbuild-angular-setup-checklist-spec.md:71-72
│   Section: # PHẦN 2: VIẾT NHỮNG GÌ VÀO TỪNG FILE? (WHAT TO WRITE)
├── ────────────────────────────────────────────────────────
│   # PHẦN 2: VIẾT NHỮNG GÌ VÀO TỪNG FILE? (WHAT TO WRITE)
└── ────────────────────────────────────────────────────────

### Local Evidence (profiles):
🔍 Query: "customer list tableColumns visibleColumnsWidth LAST_ACTIVITY" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 3.32] /home/baoltb/Desktop/Room_Agent/profiles/lead.md:1-44 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Lead
│   provider: antigravity
│   model: gemini-4-argon-high
│   modeId: full-access
│   thinkingOptionId: high
│   ---
│   Room role: Lead (Technical Architect & Project Manager in SLPC).
│   
│   MISSION:
│   You hold final technical responsibility in the SLPC (`Supervisor - Lead - Peer - QC`) pipeline. You do not edit production code yourself; you break requirements into subtasks, assign implementation to `peer`, and coordinate independent verification with `qc`.
│   
│   WORKFLOW:
│   1. POLL: Find new Epics/Features (`python3 tools/harness_manager.py list --source bot --assigned-to-profile lead --state New`).
│   2. ANALYZE: Read the codebase, specs, and architecture.
│   3. ASSIGN:
│      - Break down into Tasks with clear Acceptance Criteria (`--ac`) and target source files.
│      - Assign implementation Tasks to `peer`:
│        `python3 tools/harness_manager.py add --type Task --title "[<Module>] - <Action>" --ac "<AC list>" --source bot --created-by-profile lead --assigned-to-profile peer --parent-id <epic_id> --dispatch`
│      - Notify or assign `qc` to generate `Testcase` items and unit 

### Local Evidence (tools):
🔍 Query: "customer list tableColumns visibleColumnsWidth LAST_ACTIVITY" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 16 matches across 76 files. Top 3 shown:

┌── [Rank #1 | Score: 40.12] /home/baoltb/Desktop/Room_Agent/tools/research/tds_icon_list_from_https_tds_tmtco_.md:1-4
│   Section: # Research Report: TDS icon list from https://tds.tmtco.org/#/components/icon for store website facebook zalo partner api
├── ────────────────────────────────────────────────────────
│   # Research Report: TDS icon list from https://tds.tmtco.org/#/components/icon for store website facebook zalo partner api
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:33:54
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 40.12] /home/baoltb/Desktop/Room_Agent/tools/research/reports/tds_icon_list_from_https_tds_tmtco_.md:1-4
│   Section: # Research Report: TDS icon list from https://tds.tmtco.org/#/components/icon for store website facebook zalo partner api
├── ────────────────────────────────────────────────────────
│   # Research Report: TDS icon list from https://tds.tmtco.org/#/components/icon for store website facebook zalo partner api
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:33:54
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 29.49] /home/baoltb/Desktop/Room_Agent/tools/research/research

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
