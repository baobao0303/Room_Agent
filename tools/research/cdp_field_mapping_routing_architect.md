# Research Report: CDP Field Mapping routing architecture mfe-cdp

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 14:16:31

## 1. Problem Statement & Scope
- **Research Topic**: `CDP Field Mapping routing architecture mfe-cdp`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "CDP Field Mapping routing architecture mfe-cdp" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 30 matches across 24 files. Top 3 shown:

┌── [Rank #1 | Score: 119.19] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-ui-spec.md:1-8
│   Section: # ĐẶC TẢ YÊU CẦU PHẦN MỀM: CDP ADMIN - MAPPING DỮ LIỆU SỰ KIỆN (FIELD MAPPING UI)
├── ────────────────────────────────────────────────────────
│   # ĐẶC TẢ YÊU CẦU PHẦN MỀM: CDP ADMIN - MAPPING DỮ LIỆU SỰ KIỆN (FIELD MAPPING UI)
│   > **Mã tài liệu**: `SPEC-CDP-MAPPING-2026-V1`  
│   > **Nguồn thiết kế**: `Field mapping UI.pdf` (9 trang)  
│   > **Module mục tiêu**: `projects/wicx-crm-fe/apps/mfe-cdp` (Angular 18, Standalone, TDS UI)  
│   > **Ngày phê duyệt**: 2026-10-19  
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 72.45] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-ui-spec.md:21-41
│   Section: ## 2. ĐIỀU HƯỚNG & CẤU TRÚC PHÂN CẤP (NAVIGATION ARCHITECTURE)
├── ────────────────────────────────────────────────────────
│   ## 2. ĐIỀU HƯỚNG & CẤU TRÚC PHÂN CẤP (NAVIGATION ARCHITECTURE)
│   
│   ```
│   CDP Admin
│   ├── Tổng quan
│   ├── Hồ sơ khách hàng
│   ├── Dữ liệu sự kiện
│   │   ├── [Tab 1] Dữ liệu thô (Raw Events List)
│   │   └── [Tab 2] Mapping dữ liệu (Field Mapping UI)  <-- PHẠM VI TÀI LIỆU NÀY
│   │       ├── 1. Màn hình Tổng quan sự kiện nhận về
│   │       ├── 2. Màn hình Cấu hình chung trang liên kết (CRM / Website / Fanpage /

### Local Evidence (profiles):
🔍 Query: "CDP Field Mapping routing architecture mfe-cdp" | Target: /home/baoltb/Desktop/Room_Agent/profiles
📊 Found 3 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 2.21] /home/baoltb/Desktop/Room_Agent/profiles/supervisor.md:1-39 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Supervisor
│   provider: antigravity
│   model: gemini-4-argon-high
│   modeId: full-access
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User directly.
│   - DO NO

### Local Evidence (tools):
🔍 Query: "CDP Field Mapping routing architecture mfe-cdp" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 30 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 69.06] /home/baoltb/Desktop/Room_Agent/tools/research/research_supervisor_create_harness_db_tasks_f.md:1-4
│   Section: # Research Report: [Supervisor] Create Harness DB tasks for CDP Field Mapping UI
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Create Harness DB tasks for CDP Field Mapping UI
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 13:53:49
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 68.85] /home/baoltb/Desktop/Room_Agent/tools/research/research_supervisor_generate_specification_fo.md:1-4
│   Section: # Research Report: [Supervisor] Generate specification for CDP Field Mapping UI from PDF
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Generate specification for CDP Field Mapping UI from PDF
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 13:44:53
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 68.78] /home/baoltb/Desktop/Room_Agent/tools/research/research_supervisor_dispatch_lead_and_peer_fo.md:1-4
│   Section: # Research Report: [Supervisor] Dispatch Lead and Peer for CDP Field Mapping implementation

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
