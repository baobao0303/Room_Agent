# Research Report: TDS icon list from https://tds.tmtco.org/#/components/icon for store website facebook zalo partner api

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:33:54

## 1. Problem Statement & Scope
- **Research Topic**: `TDS icon list from https://tds.tmtco.org/#/components/icon for store website facebook zalo partner api`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "TDS icon list from https tds.tmtco.org components icon" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 90 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 24.05] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:362-372
│   Section: ### Phiên #107 — `2026-10-15 14:17:36 +0700` | **Peer Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #107 — `2026-10-15 14:17:36 +0700` | **Peer Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Peer Dev: Work Item #447 [Bug]: [Bug] [CDP Raw Event]: Khi mở dropdown lọc Tenant thì icon checkmark và mũi tên chưa đúng chuẩn TDS UI
│   Tại apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.html:
│   1. Nút dropdown lọc Tenant đang dùng tdsSuffixIcon='tdsi-arrow-down-fill' (tam giác đặc) -> Cần đổi sang chuẩn TDS: tdsSuffixIcon='tdsi-chevron-down-fill' (hoặc chevron down thanh mảnh).
│   2. Icon check chọn của option item đang dùng 'tdsi-check-line' (dấu tích đen gạch) -> Cần đổi sang icon chuẩn TDS UI như hình mẫu: icon tròn xanh có dấu tích trắng 'tdsi-success-fill tds-color-icon-success text-base shrink-0'.
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_peer_dev_work_item_447_bug_bug_cdp_r.md
│     - Generated Role Execution Brief -> tools/research/gen_brief_peer_dev_work_item_447_bug_bug_cdp_r.md
│

### Local Evidence (profiles):
🔍 Query: "TDS icon list from https tds.tmtco.org components icon" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 5.5] /home/baoltb/Desktop/Paseo_Project/profiles/lead.md:1-44 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Lead
│   provider: router9
│   model: ag/gemini-3.8-flash-high
│   modeId: bypassPermissions
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
│      - Notify or assign `qc` to generate `Testcase` items and

### Local Evidence (tools):
🔍 Query: "TDS icon list from https tds.tmtco.org components icon" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 226 matches across 63 files. Top 3 shown:

┌── [Rank #1 | Score: 68.8] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_447_bug_bug_cdp_r.md:1-7
│   Section: # Research Report: [Peer Dev] Work Item #447 [Bug]: [Bug] [CDP Raw Event]: Khi mở dropdown lọc Tenant thì icon checkmark và mũi tên chưa đúng chuẩn TDS UI
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Work Item #447 [Bug]: [Bug] [CDP Raw Event]: Khi mở dropdown lọc Tenant thì icon checkmark và mũi tên chưa đúng chuẩn TDS UI
│   Tại apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.html:
│   1. Nút dropdown lọc Tenant đang dùng tdsSuffixIcon='tdsi-arrow-down-fill' (tam giác đặc) -> Cần đổi sang chuẩn TDS: tdsSuffixIcon='tdsi-chevron-down-fill' (hoặc chevron down thanh mảnh).
│   2. Icon check chọn của option item đang dùng 'tdsi-check-line' (dấu tích đen gạch) -> Cần đổi sang icon chuẩn TDS UI như hình mẫu: icon tròn xanh có dấu tích trắng 'tdsi-success-fill tds-color-icon-success text-base shrink-0'.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:17:30
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 28.14] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_peer_dev_work_item_447_bug_bug_cdp_r.md:1-11
│   

### Local Evidence (projects):
🔍 Query: "TDS icon list from https tds.tmtco.org components icon" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 15499 matches across 5882 files. Top 3 shown:

┌── [Rank #1 | Score: 69.74] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/data-raw/components/channel-connector-list/channel-connector-list.component.ts:1-50 (truncated to 30 lines)
│   Section: Lines 1-50
├── ────────────────────────────────────────────────────────
│   import {
│     ChangeDetectionStrategy,
│     Component,
│     EventEmitter,
│     Input,
│     OnInit,
│     Output,
│     computed,
│     signal,
│   } from '@angular/core';
│   import { CommonModule } from '@angular/common';
│   import { FormsModule } from '@angular/forms';
│   import { TDSInputSearchModule } from 'tds-ui/input-search';
│   import { TDSTagModule } from 'tds-ui/tag';
│   import { TDSButtonModule } from 'tds-ui/button';
│   import { TDSToolTipModule } from 'tds-ui/tooltip';
│   import {
│     ChannelConnectorSummary,
│     filterChannelConnectors,
│   } from '../../raw-data-mapping.models';
│   
│   export const DEFAULT_MOCK_CHANNELS: ChannelConnectorSummary[] = [
│     {
│       id: '1',
│       name: 'TPOS - Store VN #01',
│       channelType: 'website',
│       categoryLabel: 'Website',
│       status: 'connected',
│       lastUpdatedAt: '2026-10-15 08:30',
│       endpointUrl: 'https://api.tpos.vn/events',
└── ────────────────────────────────────────────────────────

┌── [Rank #2

### CRM BA Spec Evidence:
🔍 Query: "TDS icon list from https tds.tmtco.org components icon" | Category: all
📊 Tìm thấy 1297 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 58.02] /home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/stories/Phase 1_User_Stories/UC4.09 - Thông báo (chuông).md:130-136
│   Section: ### Màn hình 1 — Icon chuông + badge (thanh top bar, mọi màn)
├── ────────────────────────────────────────────────────────
│   ### Màn hình 1 — Icon chuông + badge (thanh top bar, mọi màn)
│   
│   | STT | Tên trường | Kiểu trường | Kiểu dữ liệu | Mô tả |
│   | --- | --- | --- | --- | --- |
│   | 1 | Icon chuông | Icon button | — | Nút mở dropdown. Luôn hiện trên top bar ở mọi màn. |
│   | 2 | Badge số | Label | Số | Đếm thông báo chưa đọc. Ẩn khi = 0; > 99 hiện "99+". |
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 58.02] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 1_User_Stories/UC4.09 - Thông báo (chuông).md:130-136
│   Section: ### Màn hình 1 — Icon chuông + badge (thanh top bar, mọi màn)
├── ────────────────────────────────────────────────────────
│   ### Màn hình 1 — Icon chuông + badge (thanh top bar, mọi màn)
│   
│   | STT | Tên trường | Kiểu trường | Kiểu dữ liệu | Mô tả |
│   | --- | --- | --- | --- | --- |
│   | 1 | Icon chuông | Icon button | — | Nút mở dropdown. Luôn hiện trên top bar ở mọi màn. |
│   | 2 | Badge số | Label | Số | Đếm thông báo chưa đọc. Ẩn khi =

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
