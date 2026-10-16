# Research Report: [Supervisor] Dac ta setup project_base Angular su dung Rsbuild chi tiet

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-16 09:53:10

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Dac ta setup project_base Angular su dung Rsbuild chi tiet`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Dac ta setup project_base Angular su dung" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 1994 matches across 27 files. Top 3 shown:

┌── [Rank #1 | Score: 76.75] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:806-812
│   Section: ### Phiên #1096 — `2026-10-16 09:51:19 +0700` | **Supervisor**
├── ────────────────────────────────────────────────────────
│   ### Phiên #1096 — `2026-10-16 09:51:19 +0700` | **Supervisor**
│   - **Tóm tắt**: Xay dung dac ta chi tiet 8 phan ve setup project_base chuan Enterprise su dung Rsbuild
│   - **Đã thực hiện**:
│     - Tao docs/spec/rsbuild-project-base-setup-spec.md: Muc tieu KPIs, cay thu muc chuan, dependency matrix, file cau hinh chi tiet (rsbuild.config.ts, tsconfig.json, env.d.ts, tailwind, postcss), co che env PUBLIC_*, multi-stage Dockerfile NGINX, cac buoc thuc thi step-by-step va Definition of Done
│   - **File đã tạo/cập nhật**: `docs/spec/rsbuild-project-base-setup-spec.md`
│   - **Bàn giao bước tiếp theo**: User review dac ta hoac khoi tao source code project_base mau
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 62.33] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:813-820
│   Section: ### Phiên #1095 — `2026-10-16 09:50:57 +0700` | **Supervisor (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #1095 — `2026-10-16 09:50:57 +0700` | **Supervisor (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy t

### Local Evidence (profiles):
🔍 Query: "Supervisor Dac ta setup project_base Angular su dung" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 22.04] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the Use

### Local Evidence (tools):
🔍 Query: "Supervisor Dac ta setup project_base Angular su dung" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 651 matches across 133 files. Top 3 shown:

┌── [Rank #1 | Score: 236.12] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_dac_ta_setup_project_base.md:1-4
│   Section: # Research Report: [Supervisor] Dac ta setup project_base su dung Rsbuild chi tiet
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Dac ta setup project_base su dung Rsbuild chi tiet
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-16 09:50:54
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 105.81] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_supervisor_dac_ta_setup_project_base.md:1-8
│   Section: # Auto-Generated Execution Brief (Supervisor)
├── ────────────────────────────────────────────────────────
│   # Auto-Generated Execution Brief (Supervisor)
│   
│   - **Profile**: `Supervisor`
│   - **Topic / Task**: Dac ta setup project_base su dung Rsbuild chi tiet
│   - **Task ID**: `N/A`
│   - **Generated At**: `2026-10-16 09:50:57 +0700`
│   - **Research Report**: `tools/research/research_supervisor_dac_ta_setup_project_base.md`
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 104.01] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_dac_ta_ky_thuat_rsbuild_v.md:1

### Local Evidence (projects):
🔍 Query: "Supervisor Dac ta setup project_base Angular su dung" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 11397 matches across 5906 files. Top 3 shown:

┌── [Rank #1 | Score: 49.44] /home/baoltb/Desktop/Paseo_Project/projects/fe-mfes/docs/superpowers/plans/2026-07-07-wi-mfes-wi-oauth-setup.md:1-14
│   Section: # fe-mfes Nx 19 Workspace Setup — Implementation Plan
├── ────────────────────────────────────────────────────────
│   # fe-mfes Nx 19 Workspace Setup — Implementation Plan
│   
│   > **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
│   
│   **Goal:** Setup Nx 19 workspace around 5 existing Angular 18 libs in `fe-mfes`, configure build/pack pipeline producing `.tgz` files in `packs/`, and create `CLAUDE.md` + `README.md` documentation.
│   
│   **Architecture:** Run `npx nx@19 init` in the existing repo to add Nx configs without touching `libs/`. Then add `@nx/angular@19`, `@nx/jest@19`, `@nx/eslint@19` plugins. Rename OAuth package from `@wi-mfes/oauth` → `@wi/oauth` for naming consistency. Configure path mappings in `tsconfig.base.json`, add a `pack` target to `nx.json` (using `npm pack --pack-destination=packs`), and write docs last (so they reflect actual final state).
│   
│   **Tech Stack:** Nx 19.x, Angular 18.2, TypeScript 5.5, Jest 29, ESLint 9 (with legacy `.eslintrc.json

### CRM BA Spec Evidence:
🔍 Query: "Supervisor Dac ta setup project_base Angular su dung" | Category: all
📊 Tìm thấy 4729 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 67.76] /home/baoltb/Desktop/wicx-crm-doc/WiCX/fe-mfes/docs/superpowers/plans/2026-07-07-wi-mfes-wi-oauth-setup.md:1-14
│   Section: # fe-mfes Nx 19 Workspace Setup — Implementation Plan
├── ────────────────────────────────────────────────────────
│   # fe-mfes Nx 19 Workspace Setup — Implementation Plan
│   
│   > **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
│   
│   **Goal:** Setup Nx 19 workspace around 5 existing Angular 18 libs in `fe-mfes`, configure build/pack pipeline producing `.tgz` files in `packs/`, and create `CLAUDE.md` + `README.md` documentation.
│   
│   **Architecture:** Run `npx nx@19 init` in the existing repo to add Nx configs without touching `libs/`. Then add `@nx/angular@19`, `@nx/jest@19`, `@nx/eslint@19` plugins. Rename OAuth package from `@wi-mfes/oauth` → `@wi/oauth` for naming consistency. Configure path mappings in `tsconfig.base.json`, add a `pack` target to `nx.json` (using `npm pack --pack-destination=packs`), and write docs last (so they reflect actual final state).
│   
│   **Tech Stack:** Nx 19.x, Angular 18.2, TypeScript 5.5, Jest 29, ESLint 9 (with legacy `.eslintrc.json` retained per lib), Node 20 L

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
