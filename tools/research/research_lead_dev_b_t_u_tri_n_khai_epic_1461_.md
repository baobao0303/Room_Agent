# Research Report: [Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
Nhiệm vụ:
1. Thiết kế DTOs và Customer360Store (Signals) quản lý state của 3 cột (Profile, Purchase, Heatmap, Appointments, Notes) theo đặc tả docs/spec/customer-360-profile-spec.md.
2. Cấu hình route /customers/:id trong mfe-cdp và app-shell.
3. Chỉ đạo QC triển khai trước 4 bộ Unit Test (Tasks #1467..#1470) theo chuẩn TDD trước khi Peer Dev code UI.

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:48:11

## 1. Problem Statement & Scope
- **Research Topic**: `[Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
Nhiệm vụ:
1. Thiết kế DTOs và Customer360Store (Signals) quản lý state của 3 cột (Profile, Purchase, Heatmap, Appointments, Notes) theo đặc tả docs/spec/customer-360-profile-spec.md.
2. Cấu hình route /customers/:id trong mfe-cdp và app-shell.
3. Chỉ đạo QC triển khai trước 4 bộ Unit Test (Tasks #1467..#1470) theo chuẩn TDD trước khi Peer Dev code UI.`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Lead Dev Bắt đầu triển khai Epic 1461" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 415 matches across 18 files. Top 3 shown:

┌── [Rank #1 | Score: 166.76] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:898-905
│   Section: ### Phiên #53 — `2026-10-15 13:41:58 +0700` | **Lead**
├── ────────────────────────────────────────────────────────
│   ### Phiên #53 — `2026-10-15 13:41:58 +0700` | **Lead**
│   - **Tóm tắt**: Đã phân rã chi tiết 11 Task cho Epic #265 và 4 User Story #266..#269: chỉ định rõ file đích, AC chuẩn ISTQB, lệnh phong tỏa Peer Dev chưa code vội, và giao 4 Task Unit Test trước (TDD) cho QC
│   - **Đã thực hiện**:
│     - Phân rã 5 Task cho Peer Dev (#271, #272, #273, #275, #276) gắn AC chi tiết và lệnh CHƯA ĐƯỢC CODE VỘI
│     - Phân công 4 Task Unit Test TDD (#278, #279, #280, #277) cho QC theo chuẩn 5 giai đoạn ISTQB
│     - Hoàn thiện AC và mô tả cho 2 Task kiến trúc của Lead Dev (#270, #274)
│   - **Bàn giao bước tiếp theo**: Triệu hồi QC để triển khai viết Unit Test spec cho Step 1 (#278), Step 2 (#279), Step 3 (#280), Step 4 (#277) theo TDD
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 154.8] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:966-974
│   Section: ### Phiên #43 — `2026-10-15 13:36:02 +0700` | **Supervisor**
├── ────────────────────────────────────────────────────────
│   ### Phiên #43 — `2026-10-15 13:36:02 +0700` | **Supervisor**
│   - **Tóm tắt**: Đã khởi tạo E

### Local Evidence (profiles):
🔍 Query: "Lead Dev Bắt đầu triển khai Epic 1461" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 37.97] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User directly.
│  

### Local Evidence (tools):
🔍 Query: "Lead Dev Bắt đầu triển khai Epic 1461" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 583 matches across 64 files. Top 3 shown:

┌── [Rank #1 | Score: 162.38] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:39:14
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 135.73] /home/baoltb/Desktop/Paseo_Project/tools/research/harness_framework_research.md:5-9
│   Section: ## 1. Tổng quan & Bản chất của Harness
├── ────────────────────────────────────────────────────────
│   ## 1. Tổng quan & Bản chất của Harness
│   `harness` là một hệ điều hành cấp repository (Operating Framework) viết bằng **Rust**, quản lý toàn bộ vòng đời ph

### Local Evidence (projects):
🔍 Query: "Lead Dev Bắt đầu triển khai Epic 1461" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25526 matches across 5885 files. Top 3 shown:

┌── [Rank #1 | Score: 148.83] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-wicx-core-hardening.md:1-10
│   Section: # SPEC: Củng Cố An Ninh & Tối Ưu Nền Tảng `libs/wicx-core`
├── ────────────────────────────────────────────────────────
│   # SPEC: Củng Cố An Ninh & Tối Ưu Nền Tảng `libs/wicx-core`
│   
│   - **Trạng thái:** Sẵn sàng triển khai (Ready for Execution)
│   - **Phiên bản:** 1.0
│   - **Ngày:** 2026-10-11
│   - **Phạm vi:** `libs/wicx-core`
│   - **Mục tiêu:** Khắc phục triệt để các lỗ hổng bảo mật, lỗi treo request khi hết hạn phiên làm việc (token refresh hang), đảm bảo an toàn ngoại lệ (Storage SSR-safe), và dọn dẹp nợ kỹ thuật (technical debt).
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 141.3] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/azure-pipelines/AGENTS.md:13-26
│   Section: ## 2. Các bước triển khai (`steps`)
├── ────────────────────────────────────────────────────────
│   ## 2. Các bước triển khai (`steps`)
│   
│   1. **`Install`**:
│      - Lệnh: `npm install --force`
│      - Mục đích: Cài đặt toàn bộ thư viện dependencies (cờ `--force` bắt buộc để xử lý xung đột peer dependencies).
│   2. **`Build môi trường QA`**:
│      - Lệnh: `npm run build:qa`
│      - Mục đích: Build đồng loạt Host (`app-shell`) và các 

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
