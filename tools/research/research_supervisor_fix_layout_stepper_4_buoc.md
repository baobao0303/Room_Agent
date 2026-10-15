# Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:52:36

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Fix layout Stepper 4 buoc va Scope" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 167 matches across 18 files. Top 3 shown:

┌── [Rank #1 | Score: 41.38] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:358-361
│   Section: ### 9.1. Nâng cấp Codex Room từ 3 Role lên 4 Role (`supervisor | lead | peer | qc`)
├── ────────────────────────────────────────────────────────
│   ### 9.1. Nâng cấp Codex Room từ 3 Role lên 4 Role (`supervisor | lead | peer | qc`)
│   - **Overlay thứ 4 (`qc.config.toml`)**: Tạo mới tại `codex-room-setup/home/.config/codex-room/overlays/qc.config.toml` và `~/.config/codex-room/overlays/qc.config.toml` (`model = "gpt-6.1-sol"`, `model_reasoning_effort = "medium"`, `paseoTools.enabled = false`).
│   - **Runtime thứ 4 (`~/.codex-runtime/qc`)**: Cập nhật `codex-room`, `codex-room-sync`, `scripts/sync-all`, `scripts/install-room`, `scripts/verify`, `scripts/lib/model-alignment.py`, và `scripts/lib/paseo-tools.jq` để hỗ trợ đầy đủ 4 role `supervisor | lead | peer | qc` và 4 provider `codex-supervisor | codex-lead | codex-peer | codex-qc`.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 40.77] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:354-357
│   Section: ## 9. Mở rộng lên 4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`) & Tích hợp `031_claude_code_sub_agents`
├── ────────────────────────────────────────────────────────
│   ## 9. Mở rộng lên 4 Ro

### Local Evidence (profiles):
🔍 Query: "Supervisor Fix layout Stepper 4 buoc va Scope" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 24.05] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User direc

### Local Evidence (tools):
🔍 Query: "Supervisor Fix layout Stepper 4 buoc va Scope" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 287 matches across 68 files. Top 3 shown:

┌── [Rank #1 | Score: 55.0] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_443_bug_bug_cdp_r.md:11-21
│   Section: ## 1. Problem Statement & Scope
├── ────────────────────────────────────────────────────────
│   ## 1. Problem Statement & Scope
│   - **Research Topic**: `[Peer Dev] Work Item #443 [Bug]: [Bug] [CDP Raw Event]: Khi sự kiện thiếu source thì hệ thống tự động sinh tab UNKNOWN trên thanh lọc nguồn
│   Tại apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts:
│   - Hàm enhanceEventItem() gán fallback source = 'unknown' khi event thiếu trường source/eventSource.
│   - Hàm updateSourceTabsFromEvents() duyệt qua eventsList và tự động append 'UNKNOWN' vào sourceTabs.
│   - Cần fix:
│     1. Loại trừ 'unknown' khỏi updateSourceTabsFromEvents (không bao giờ sinh tab UNKNOWN).
│     2. Bổ sung mapping nhận diện nguồn từ connectorId/metadata nếu có hoặc giữ nguyên nguồn chuẩn từ API fetchEventSources().`
│   - **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
│   - **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 53.45] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_444_bug_bug_json_

### Local Evidence (projects):
🔍 Query: "Supervisor Fix layout Stepper 4 buoc va Scope" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 2239 matches across 5885 files. Top 3 shown:

┌── [Rank #1 | Score: 28.47] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/apps/app-shell/src/app/layouts/layout.component.html:26-40
│   Section: Lines 26-40
├── ────────────────────────────────────────────────────────
│   </tds-layout>
│   </tds-layout>
│   
│   <!-- Full-screen Translucent Blurred Loading Overlay when switching tenant -->
│   @if (isSwitchingTenant()) {
│   <div
│     class="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-white/70 dark:bg-black/60 backdrop-blur-sm transition-all duration-300 select-none">
│     <img tds-image [tdsSrc]="'images/spinner.gif'" [disablePreview]="true" alt="Loading..."
│       class="w-[200px] h-[200px] object-contain" />
│     <span class="mt-4 tds-body-2 font-medium tds-color-text-secondary">
│       {{ 'SHELL.REDIRECTING' | translate }}
│     </span>
│   </div>
│   }
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 28.1] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/libs/cashbook/data-access/src/auto-gen/models/customer-accounts-receivable-request-dto.ts:26-26
│   Section: Lines 26-26
├── ────────────────────────────────────────────────────────
│   };
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 27.79] /home/baoltb/Desktop/Paseo_Project/projects/wion_

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
