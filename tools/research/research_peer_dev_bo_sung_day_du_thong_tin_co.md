# Research Report: [Peer Dev] Bo sung day du Thong tin connector va Alert box tren cot trai GeneralMappingConfig theo mockup

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:57:10

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Bo sung day du Thong tin connector va Alert box tren cot trai GeneralMappingConfig theo mockup`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Bo sung day du Thong tin" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 1058 matches across 22 files. Top 3 shown:

┌── [Rank #1 | Score: 41.4] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:1983-1991
│   Section: ### Phiên #83 — `2026-10-15 14:02:03 +0700` | **Peer Dev**
├── ────────────────────────────────────────────────────────
│   ### Phiên #83 — `2026-10-15 14:02:03 +0700` | **Peer Dev**
│   - **Tóm tắt**: Fix Bug #443 [CDP Raw Event]: Loại trừ tab UNKNOWN và hoàn thiện mapping nhận diện nguồn từ connectorId/metadata
│   - **Đã thực hiện**:
│     - Loại trừ unknown và all khỏi fetchEventSources và updateSourceTabsFromEvents
│     - Bổ sung mapping nhận diện nguồn từ metadata (source, provider, channel) và connectorId (fb, zalo, tpos, shopee, lazada, tiktok, telegram, partner hoặc khớp sourceTabs từ API)
│     - Bổ sung 3 BDD unit tests kiểm thử triệt để kịch bản Bug #443 (22/22 unit tests passed)
│   - **File đã tạo/cập nhật**: `apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts`, `apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.spec.ts`
│   - **Bàn giao bước tiếp theo**: QC thực thi kiểm thử độc lập cho Work Item #443
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 40.1] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:1752-1761
│   Section: ### Phiên #113 — `2026-10-15 14:22:22 +0700` | **Peer Dev**
├── ──────────────────────────────────────────────────────

### Local Evidence (profiles):
🔍 Query: "Peer Dev Bo sung day du Thong tin" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 16.38] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Peer
│   provider: router9
│   model: ag/gemini-3.8-flash-high
│   modeId: bypassPermissions
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
🔍 Query: "Peer Dev Bo sung day du Thong tin" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 468 matches across 115 files. Top 3 shown:

┌── [Rank #1 | Score: 71.52] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_work_item_1819_task_ui_data_raw.md:1-5
│   Section: # Research Report: [Peer] Work Item #1819 [Task]: [UI/Data-Raw]: Mac dinh chon Tat ca (isAllTenants = true) tai tab Du lieu tho
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer] Work Item #1819 [Task]: [UI/Data-Raw]: Mac dinh chon Tat ca (isAllTenants = true) tai tab Du lieu tho
│   Chuyen gia tri mac dinh cua isAllTenants tu false sang true de khi vao URL /customers/data-raw he thong mac dinh hien thi Tat ca du lieu.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:53:42
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 65.13] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_peer_dev_fix_layout_stepper_4_buoc_t.md:1-8
│   Section: # Auto-Generated Execution Brief (Peer Dev)
├── ────────────────────────────────────────────────────────
│   # Auto-Generated Execution Brief (Peer Dev)
│   
│   - **Profile**: `Peer Dev`
│   - **Topic / Task**: Fix layout Stepper 4 buoc tren cung va dua 2 pane vao Step 1
│   - **Task ID**: `N/A`
│   - **Generated At**: `2026-10-15 14:54:28 +0700`
│   - **Research Report**: `tools/research/research_peer_dev_fix_layou

### Local Evidence (projects):
🔍 Query: "Peer Dev Bo sung day du Thong tin" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 10287 matches across 5897 files. Top 3 shown:

┌── [Rank #1 | Score: 37.49] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/apps/dashboard/src/assets/i18n/vi/product.json:726-726
│   Section: Lines 726-726
├── ────────────────────────────────────────────────────────
│   }
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 37.49] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/apps/dashboard/src/assets/i18n/en/product.json:726-726
│   Section: Lines 726-726
├── ────────────────────────────────────────────────────────
│   }
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 37.49] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/apps/cashbook/src/assets/i18n/vi/product.json:726-726
│   Section: Lines 726-726
├── ────────────────────────────────────────────────────────
│   }
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Peer Dev Bo sung day du Thong tin" | Category: all
📊 Tìm thấy 2149 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 79.19] /home/baoltb/Desktop/wicx-crm-doc/WiCX/FE/docs/development/spec_remote_setting_and_modular_i18n.md:1-8
│   Section: # 📖 Technical Specification: Remote Setting (UMAC) Integration, Modular i18n & Dev Proxy Architecture
├── ────────────────────────────────────────────────────────
│   # 📖 Technical Specification: Remote Setting (UMAC) Integration, Modular i18n & Dev Proxy Architecture
│   
│   > **Mã tài liệu:** `SPEC-20260825-REMOTE-SETTING-I18N`  
│   > **Trạng thái:** Active / In-Progress  
│   > **Áp dụng cho:** App Shell (`apps/app-shell`), Core Infrastructure (`libs/wicx-core`), Dev Tooling (`module-federation.shared.ts`)  
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 73.9] /home/baoltb/Desktop/wicx-crm-doc/WiCX/FE/docs/development/spec_remote_setting_and_modular_i18n.md:176-187
│   Section: #### B. Menu Sidebar Navigation (`sidebar-nav.mock.ts`)
├── ────────────────────────────────────────────────────────
│   #### B. Menu Sidebar Navigation (`sidebar-nav.mock.ts`)
│   Bổ sung item phân quyền người dùng:
│   ```typescript
│   {
│     id: 'permission',
│     labelKey: 'SHELL.SIDEBAR.PERMISSION',
│     routerLink: ['setting', 'permission'],
│   }
│   ```
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 71.87] /home/baoltb

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
