# Research Report: [Supervisor] Them Outline MCP server vao Claude va Paseo

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-16 09:21:25

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Them Outline MCP server vao Claude va Paseo`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Them Outline MCP server vao Claude va" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 486 matches across 24 files. Top 3 shown:

┌── [Rank #1 | Score: 32.31] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:5797-5805
│   Section: ### Phiên #331 — `2026-10-15 16:02:20 +0700` | **Supervisor**
├── ────────────────────────────────────────────────────────
│   ### Phiên #331 — `2026-10-15 16:02:20 +0700` | **Supervisor**
│   - **Tóm tắt**: Sua giao dien Ho so khach hang CustomerSummaryCardComponent khop 100% Figma Hinh 1
│   - **Đã thực hiện**:
│     - Chuyen top section thanh horizontal: Avatar ben trai kem badge Da dinh danh
│     - Ben phai la Ho ten + Icon gioi tinh, Ma KH [NV0015-21], Nut [Chinh sua] va nut vuong [Xoa]
│     - Dua Trạng thái khách hàng va Kênh nguồn vao danh sach thuoc tinh ben duoi
│     - Pass 67/67 tests Customer 360 va 23/23 tests Data-Raw
│   - **Bàn giao bước tiếp theo**: User kiem tra lai giao dien browser man Customer 360
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 29.54] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:6537-6542
│   Section: ### Phiên #232 — `2026-10-15 15:26:30 +0700` | **Supervisor**
├── ────────────────────────────────────────────────────────
│   ### Phiên #232 — `2026-10-15 15:26:30 +0700` | **Supervisor**
│   - **Tóm tắt**: SLPC Heartbeat: Epic #1461 va 7 Tasks C360 da Closed boi QC; Peer 4c69584 va QC 4cf407b dang xu ly Task #1696
│   - **Đ

### Local Evidence (profiles):
🔍 Query: "Supervisor Them Outline MCP server vao Claude va" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User di

### Local Evidence (tools):
🔍 Query: "Supervisor Them Outline MCP server vao Claude va" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 360 matches across 123 files. Top 3 shown:

┌── [Rank #1 | Score: 61.55] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_slpc_heartbeat_kiem_tra_t.md:1-4
│   Section: # Research Report: [Supervisor] SLPC Heartbeat kiem tra tien do va trang thai agent
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] SLPC Heartbeat kiem tra tien do va trang thai agent
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 16:00:48
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 61.39] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_fix_layout_stepper_4_buoc.md:1-4
│   Section: # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:52:36
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 61.12] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_bo_icon_tab_va_padding_x_.md:1-4
│   Section: # Research Report: [Supervisor] Bo icon tab va padding-x ve 0 cho 

### Local Evidence (projects):
🔍 Query: "Supervisor Them Outline MCP server vao Claude va" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 994 matches across 5906 files. Top 3 shown:

┌── [Rank #1 | Score: 32.14] /home/baoltb/Desktop/Paseo_Project/projects/fe-mfes/CLAUDE.md:3-8
│   Section: ## Project context
├── ────────────────────────────────────────────────────────
│   ## Project context
│   
│   Nx 19 monorepo containing Angular 18 publishable libraries shared across multiple external repositories. Each lib is built to a `.tgz` and uploaded to a private server for consumption by other repos.
│   
│   Apps may be added later (e.g., for integration testing), but the current focus is shared libraries.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 30.25] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/libs/file/data-access/src/auto-gen/models/customer-avatar-upload-result-dto.ts:26-52
│   Section: Lines 26-52
├── ────────────────────────────────────────────────────────
│   */
│     type?: MediaType;
│   
│     /**
│      * tên file upload lên server
│      */
│     uniqueName?: string | null;
│   
│     /**
│      * url download của hình ảnh
│      */
│     url?: string | null;
│   
│     /**
│      * url proxy của hình ảnh
│      */
│     urlImageProxy?: string | null;
│     urlThumbnail?: string | null;
│     urlThumbnailSizeL?: string | null;
│     urlThumbnailSizeM?: string | null;
│     urlThumbnailSizeS?: string | null;
│   
│     /**
│    

### CRM BA Spec Evidence:
🔍 Query: "Supervisor Them Outline MCP server vao Claude va" | Category: all
📊 Tìm thấy 1008 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 76.7] /home/baoltb/Desktop/wicx-crm-doc/WiCX/FE/scripts/README.md:5-8
│   Section: ## Harness MCP Server (Recommended)
├── ────────────────────────────────────────────────────────
│   ## Harness MCP Server (Recommended)
│   
│   Harness provides a native Model Context Protocol (MCP) server that runs over standard I/O (stdio). This is the **primary, recommended, and modern way** to integrate Harness with AI Coding Agents (such as Claude Code, Cursor, Windsurf, or Copilot), enabling them to run Harness actions autonomously without requiring manual terminal commands.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 63.75] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/deploy/helm/wicx-postgres/values.yaml:61-61
│   Section: # wicx_hangfire: cùng storage nghĩa là cùng hàng đợi "default", server của service này sẽ nhặt job
├── ────────────────────────────────────────────────────────
│   # wicx_hangfire: cùng storage nghĩa là cùng hàng đợi "default", server của service này sẽ nhặt job
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 63.7] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/deploy/helm/wicx-ingestion/values.yaml:77-77
│   Section: # Cụm prod chưa chốt nên host để placeholder: bước deploy phải thay, chưa thay thì API server từ chối
├── ──────────

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
