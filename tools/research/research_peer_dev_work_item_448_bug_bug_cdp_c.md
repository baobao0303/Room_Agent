# Research Report: [Peer Dev] Work Item #448 [Bug]: [Bug] [CDP/Contact]: Khi hover vào cột Khách hàng thì thiếu font-semibold theo đúng thông số Figma
Tại apps/mfe-cdp/src/app/pages/contact/components/contact-list/contact-list.component.html:
- Thông số Figma chuẩn khi hover vào link/giá trị cột Khách hàng:
  + Font: SF Pro Text
  + Weight: 600 (Style: Semibold -> class: hover:font-semibold)
  + Size: 14px, Line height: 20px (tds-body-2)
  + Text decoration: Underline (hover:underline)
  + Color: Alias/color/text/interactive (hover:tds-color-text-interactive)
  + Cursor: pointer (cursor-pointer)
- Hiện tại thiếu 'hover:font-semibold' làm chữ không đậm lên 600 khi hover như thiết kế Figma.
- Cần fix: Thêm 'hover:font-semibold' cùng với 'hover:underline hover:tds-color-text-interactive cursor-pointer'.

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:18:47

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Work Item #448 [Bug]: [Bug] [CDP/Contact]: Khi hover vào cột Khách hàng thì thiếu font-semibold theo đúng thông số Figma
Tại apps/mfe-cdp/src/app/pages/contact/components/contact-list/contact-list.component.html:
- Thông số Figma chuẩn khi hover vào link/giá trị cột Khách hàng:
  + Font: SF Pro Text
  + Weight: 600 (Style: Semibold -> class: hover:font-semibold)
  + Size: 14px, Line height: 20px (tds-body-2)
  + Text decoration: Underline (hover:underline)
  + Color: Alias/color/text/interactive (hover:tds-color-text-interactive)
  + Cursor: pointer (cursor-pointer)
- Hiện tại thiếu 'hover:font-semibold' làm chữ không đậm lên 600 khi hover như thiết kế Figma.
- Cần fix: Thêm 'hover:font-semibold' cùng với 'hover:underline hover:tds-color-text-interactive cursor-pointer'.`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Work Item 448 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 156 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 86.4] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:490-501
│   Section: ### Phiên #63 — `2026-10-15 13:49:16 +0700` | **Peer Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #63 — `2026-10-15 13:49:16 +0700` | **Peer Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Peer Dev: Work Item #282 [Bug]: [Bug] [CDP Raw Event]: Khi bấm mở dropdown Theo Tenant-id thì danh sách bị dàn ngang và đè lên tiêu đề bảng
│   Tại màn hình CDP Raw Event Data (apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.html):
│   - Khi click button 'Theo Tenant-id', menu dropdown chứa 2 item ('Theo Tenant-id' và 'Tất cả') bị dàn ngang (flex-row) thay vì danh sách dọc (flex-col).
│   - Dropdown thiếu container định dạng chuẩn (flex flex-col, py-1, min-w, shadow, rounded) và thiếu class styling trên tds-dropdown-item làm text bị hiển thị thành 1 dòng ngang, che khuất tiêu đề 'THỜI GIAN TẠO'.
│   - Cần sửa lại container dropdown menu theo chuẩn TDS UI (flex flex-col min-w-[140px] py-1, w-full text-left cho từng button item).
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_peer_dev_work_item_282_bug_bug_cdp_r.md
│     - Gen

### Local Evidence (profiles):
🔍 Query: "Peer Dev Work Item 448 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 32.62] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile QC -

### Local Evidence (tools):
🔍 Query: "Peer Dev Work Item 448 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 307 matches across 56 files. Top 3 shown:

┌── [Rank #1 | Score: 211.93] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_281_bug_bug_cdp_s.md:1-8
│   Section: # Research Report: [Peer Dev] Work Item #281 [Bug]: [Bug] [CDP/Shell]: Khi mở CDP Raw Event và sidebar /setting thì nguồn bị mock tĩnh và active route sai
├── ────────────────────────────────────────────────────────
│   # Research Report: [Peer Dev] Work Item #281 [Bug]: [Bug] [CDP/Shell]: Khi mở CDP Raw Event và sidebar /setting thì nguồn bị mock tĩnh và active route sai
│   Khắc phục lỗi trên nhánh fix/20261015-RemoveMockSources (projects/wicx-crm-fe):
│   1. mfe-cdp: Xóa mock sources tĩnh trong raw-event-list, lấy động từ API và tự động phát hiện sources từ eventsList; xóa tenantSubName thừa.
│   2. app-shell: LayoutStore hỗ trợ generic path cho route con (/setting/employee); chuẩn hóa breadcrumbs và sidebar menu item.
│   3. Đảm bảo toàn bộ Unit Test (raw-event-list, layout, sidebar) pass 100%.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:45:06
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 207.62] /home/baoltb/Desktop/Paseo_Project/tools/research/research_peer_dev_work_item_447_bug_bug_cdp_r.md:1-7
│   Section: # Research Report: [Peer Dev] Work Item #447 [Bug]: [Bug] [CDP Raw Event

### Local Evidence (projects):
🔍 Query: "Peer Dev Work Item 448 Bug Bug CDP" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 5059 matches across 5873 files. Top 3 shown:

┌── [Rank #1 | Score: 91.53] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:277-279
│   Section: # Bug fix commits
├── ────────────────────────────────────────────────────────
│   # Bug fix commits
│   git commit -m "fix: resolve authentication token refresh issue"
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 53.47] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:454-459
│   Section: ### Team Resources
├── ────────────────────────────────────────────────────────
│   ### Team Resources
│   - Technical discussions: [Team chat/channel]
│   - Bug tracking: [Issue tracker]
│   - Code review: [PR review process]
│   - Knowledge sharing: [Wiki/Notion]
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 51.31] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/docs/DEVELOPMENT_WORKFLOW.md:265-271
│   Section: ### Branch Strategy
├── ────────────────────────────────────────────────────────
│   ### Branch Strategy
│   - **dev** - Main development branch
│   - **feature/** - Feature branches
│   - **bugfix/** - Bug fix branches
│   - **hotfix/** - Production hotfixes
│   - **release/** - Release preparation branches
└── ────────────────────────────────────────────────────────

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
