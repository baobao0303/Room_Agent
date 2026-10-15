# Research Report: [Lead Dev] Triển khai Task #1466: [CORE/STORE] Customer360Store (Signals), DTOs và route /customers/:id theo docs/spec/customer-360-profile-spec.md

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:02:46

## 1. Problem Statement & Scope
- **Research Topic**: `[Lead Dev] Triển khai Task #1466: [CORE/STORE] Customer360Store (Signals), DTOs và route /customers/:id theo docs/spec/customer-360-profile-spec.md`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Lead Dev Triển khai Task 1466 CORE STORE" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 1015 matches across 19 files. Top 3 shown:

┌── [Rank #1 | Score: 138.77] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:195-202
│   Section: ### Phiên #176 — `2026-10-15 15:01:52 +0700` | **Lead Dev (Auto Research+Gen)**
├── ────────────────────────────────────────────────────────
│   ### Phiên #176 — `2026-10-15 15:01:52 +0700` | **Lead Dev (Auto Research+Gen)**
│   - **Tóm tắt**: Chạy tự động pipeline Research + Gen cho profile Lead Dev: Triển khai Task #1466: Customer360Store
│   - **Đã thực hiện**:
│     - Research Report generated via Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader) -> tools/research/research_lead_dev_tri_n_khai_task_1466_custom.md
│     - Generated Role Execution Brief -> tools/research/gen_brief_lead_dev_tri_n_khai_task_1466_custom.md
│   - **File đã tạo/cập nhật**: `tools/research/research_lead_dev_tri_n_khai_task_1466_custom.md`, `tools/research/gen_brief_lead_dev_tri_n_khai_task_1466_custom.md`
│   - **Bàn giao bước tiếp theo**: Profile Lead Dev tiếp tục hoàn thiện task dựa trên tools/research/research_lead_dev_tri_n_khai_task_1466_custom.md và tools/research/gen_brief_lead_dev_tri_n_khai_task_1466_custom.md.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 124.64] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:1113-1120
│   Section: ### Phiên #53 — `2026-10-15 13:41:58

### Local Evidence (profiles):
🔍 Query: "Lead Dev Triển khai Task 1466 CORE STORE" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 19.52] /home/baoltb/Desktop/Paseo_Project/profiles/lead.md:1-44 (truncated to 30 lines)
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
│      - Notify or assign `qc` to generate `Testcase` items and unit test s

### Local Evidence (tools):
🔍 Query: "Lead Dev Triển khai Task 1466 CORE STORE" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 591 matches across 74 files. Top 3 shown:

┌── [Rank #1 | Score: 224.96] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_dev_tri_n_khai_task_1466_custom.md:1-4
│   Section: # Research Report: [Lead Dev] Triển khai Task #1466: Customer360Store
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead Dev] Triển khai Task #1466: Customer360Store
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:01:49
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 162.21] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_dev_b_t_u_tri_n_khai_epic_1461_.md:1-8
│   Section: # Research Report: [Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
│   Nhiệm vụ:
│   1. Thiết kế DTOs và Customer360Store (Signals) quản lý state của 3 cột (Profile, Purchase, Heatmap, Appointments, Notes) theo đặc tả docs/spec/customer-360-profile-spec.md.
│   2. Cấu hình route /customers/:id trong mfe-cdp và app-shell.
│   3. Chỉ đạo QC triển khai trước 4 bộ Unit Test (Tasks #1467..#1470) theo chuẩn TDD trước khi Peer Dev code UI.
│   
│   > Generated via *

### Local Evidence (projects):
🔍 Query: "Lead Dev Triển khai Task 1466 CORE STORE" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25346 matches across 5890 files. Top 3 shown:

┌── [Rank #1 | Score: 105.75] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-store-architecture.md:224-225
│   Section: ## 5. Lộ Trình Triển Khai Refactor (Roadmap)
├── ────────────────────────────────────────────────────────
│   ## 5. Lộ Trình Triển Khai Refactor (Roadmap)
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 83.27] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-refactor-tenant-guards.md:123-129
│   Section: ## 5. Kế hoạch Triển khai (Migration Steps)
├── ────────────────────────────────────────────────────────
│   ## 5. Kế hoạch Triển khai (Migration Steps)
│   
│   1. **Bước 1:** Trích xuất `isPotentialTenant` và `extractTenantId` vào `tenant-format.guard.ts`.
│   2. **Bước 2:** Tạo `profile-completed.guard.ts` đảm nhiệm kiểm tra display name.
│   3. **Bước 3:** Tinh gọn `tenant-access.guard.ts`, gỡ bỏ `AccountStore` và logic token.
│   4. **Bước 4:** Cập nhật `app.routes.ts`: khai báo mảng `canActivate: [tenantFormatGuard, authorizationGuard, profileCompletedGuard, tenantAccessGuard]` và bỏ `canActivateChild`.
│   5. **Bước 5:** Phân tách và chạy lại bộ Unit Tests đảm bảo 100% test suites pass.
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 79.03] /home/baoltb/Desktop/Paseo_Project/projects/wic

### CRM BA Spec Evidence:
🔍 Query: "Lead Dev Triển khai Task 1466 CORE STORE" | Category: all
📊 Tìm thấy 7889 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 130.88] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/docs/plan.md:1-14
│   Section: # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
├── ────────────────────────────────────────────────────────
│   # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
│   
│   > 🔶 **Cập nhật kiến trúc (2026-08-13).** Đã cập nhật để phản ánh kiến trúc **MinIO tenant-based storage + CDC/publish event** (3-phase processing).
│   
│   Gộp từ hai tài liệu cũ (`infra-dev.md` + `plan-lake-webhook.md`, 2026-08-12). Nguồn:
│   [`architecture.md`](architecture.md) · [`iam.md`](iam.md) · bộ tài liệu đối tác `tmt-domain` (7 file).
│   
│   **Hai phần, hai người đọc khác nhau:**
│   
│   | Phần | Mục | Ai đọc |
│   | --- | --- | --- |
│   | **A — Hạ tầng** | §1–§9 | Team system, và ta để biết đang chờ gì |
│   | **B — Triển khai** | §10–§16 | Đội dev |
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 130.88] /home/baoltb/Desktop/wicx-crm-doc/WiCX/wicx-crm/docs/plan.md:1-14
│   Section: # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
├── ────────────────────────────────────────────────────────
│   # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
│   
│   > 🔶 **Cập nhật kiến trúc (2026-08-13).** Đ

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
