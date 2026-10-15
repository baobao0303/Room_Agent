# Research Report: [QC] Bắt đầu triển khai 4 bộ Unit Test (ISTQB 5 giai đoạn) cho Epic 1461 Cột 1 CustomerSummaryCard & CustomerOrganizationsCard

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:52:51

## 1. Problem Statement & Scope
- **Research Topic**: `[QC] Bắt đầu triển khai 4 bộ Unit Test (ISTQB 5 giai đoạn) cho Epic 1461 Cột 1 CustomerSummaryCard & CustomerOrganizationsCard`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "QC Bắt đầu triển khai 4 bộ Unit" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 428 matches across 18 files. Top 3 shown:

┌── [Rank #1 | Score: 204.73] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:189-193
│   Section: #### `TC-MAP-026` - [Audit & Versioning] Tự động tăng phiên bản khi Lưu cấu hình
├── ────────────────────────────────────────────────────────
│   #### `TC-MAP-026` - [Audit & Versioning] Tự động tăng phiên bản khi Lưu cấu hình
│   - **Given:** Mapping hiện tại ở `Phiên bản 3`.
│   - **When:** Người dùng thay đổi 1 quy tắc ánh xạ và click "Lưu thay đổi".
│   - **Then:** Phiên bản tự động nâng lên `Phiên bản 4`, banner thông báo: *"Đã lưu thành phiên bản 4. Mapping mới áp dụng ngay cho dữ liệu nhận từ bây giờ."*
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 193.6] /home/baoltb/Desktop/Paseo_Project/docs/spec/raw-data-mapping-spec.md:327-344
│   Section: ## 6. Kế hoạch Phân rã Công việc Triển khai (SLPC Breakdown)
├── ────────────────────────────────────────────────────────
│   ## 6. Kế hoạch Phân rã Công việc Triển khai (SLPC Breakdown)
│   
│   1. **Supervisor**:
│      - Giám sát phạm vi, đảm bảo luồng tuân thủ thiết kế từ 11 board artifact và mockup người dùng cung cấp.
│   2. **Lead Dev**:
│      - Khởi tạo kiến trúc module `data-raw-mapping` trong `apps/mfe-cdp`.
│      - Xây dựng Store quản lý state Wizard 4 bước và State 11 Boards (`RawDataMapp

### Local Evidence (profiles):
🔍 Query: "QC Bắt đầu triển khai 4 bộ Unit" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 34.31] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
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
│   - DO 

### Local Evidence (tools):
🔍 Query: "QC Bắt đầu triển khai 4 bộ Unit" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 610 matches across 68 files. Top 3 shown:

┌── [Rank #1 | Score: 341.25] /home/baoltb/Desktop/Paseo_Project/tools/research/research_qc_b_t_u_tri_n_khai_4_b_unit_test_is.md:1-9
│   Section: # Research Report: [QC] Bắt đầu triển khai 4 bộ Unit Test (ISTQB 5 giai đoạn) cho Epic #1461 Hồ sơ khách hàng 360 theo chuẩn TDD:
├── ────────────────────────────────────────────────────────
│   # Research Report: [QC] Bắt đầu triển khai 4 bộ Unit Test (ISTQB 5 giai đoạn) cho Epic #1461 Hồ sơ khách hàng 360 theo chuẩn TDD:
│   - Task #1467: Unit Test Cột 1 (CustomerSummaryCard & CustomerOrganizationsCard)
│   - Task #1468: Unit Test Cột 2 trên (CustomerPurchaseInfo Hero KPI & Grid gói mua hàng)
│   - Task #1469: Unit Test Cột 2 dưới (CustomerActivityHeatmap Ma trận 4 kênh, Tooltip & Event Log)
│   - Task #1470: Unit Test Cột 3 (CustomerUpcomingAppointments & CustomerNotesFeed)
│   Đặc tả chi tiết tại: docs/spec/customer-360-profile-spec.md.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:48:57
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 281.23] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_dev_b_t_u_tri_n_khai_epic_1461_.md:1-8
│   Section: # Research Report: [Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
├── ─────────────────────────

### Local Evidence (projects):
🔍 Query: "QC Bắt đầu triển khai 4 bộ Unit" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25542 matches across 5886 files. Top 3 shown:

┌── [Rank #1 | Score: 194.45] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-refactor-tenant-guards.md:123-129
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

┌── [Rank #2 | Score: 179.39] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/azure-pipelines/AGENTS.md:13-26
│   Section: ## 2. Các bước triển khai (`steps`)
├── ────────────────────────────────────────────────────────
│   ## 2. Các bước triển khai (`steps`)
│   
│   1. **`Install`**:
│      - Lệnh: `npm install --force`
│      - Mục đích: Cài đặt toàn bộ thư viện dependencies (cờ `--force` bắt buộc để xử lý xung đột peer depen

### CRM BA Spec Evidence:
🔍 Query: "QC Bắt đầu triển khai 4 bộ Unit" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 254.29] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/docs/plan.md:1-14
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

┌── [Rank #2 | Score: 254.29] /home/baoltb/Desktop/wicx-crm-doc/WiCX/wicx-crm/docs/plan.md:1-14
│   Section: # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
├── ────────────────────────────────────────────────────────
│   # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
│   
│   > 🔶 **Cập nhật kiến trúc (2026-08-13).** Đã cập nhậ

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
