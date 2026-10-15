# Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:39:14

## 1. Problem Statement & Scope
- **Research Topic**: `[Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Lead Đọc 4 User Story 266 267 268" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 246 matches across 15 files. Top 3 shown:

┌── [Rank #1 | Score: 91.19] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/stories/US-customer-detail-drawer.md:1-8
│   Section: # User Story: Xem chi tiết hồ sơ khách hàng dạng drawer
├── ────────────────────────────────────────────────────────
│   # User Story: Xem chi tiết hồ sơ khách hàng dạng drawer
│   
│   - Parent: Feature #123 (Resolved, spec xong)
│   - Spec nguồn: `docs/spec/wicx-crm-fe/design/customer-detail-drawer.md` (mục 6 AC, mục 7 câu hỏi mở, mục 9 kế hoạch)
│   - BA nguồn: `Phase 0.5_User_Stories/UC4.04 - Chi tiết hồ sơ khách hàng.md`, `UC4.01` (2.1-2.4)
│   - Figma: file `yOglVOGf6KdoroEulwFYcg`, node `1175:5513`, `1659:38575`
│   - Trạng thái: user đã chốt 4 điểm (mục "Quyết định của user"). Chưa tạo Harness item, chưa dispatch.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 90.23] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/stories/US-customer-detail-drawer.md:139-145
│   Section: ## Việc sau khi user duyệt
├── ────────────────────────────────────────────────────────
│   ## Việc sau khi user duyệt
│   
│   ```bash
│   python3 tools/harness_manager.py add --type "User Story" --title "<tiêu đề story>" --parent-id 123 --priority P1 --ac "AC-01..AC-16, AC-18, AC-21, AC-22 và 3 scenario mới (docs/spec/wicx-crm-fe/stories/US-customer-detail-drawer.md)" --cre

### Local Evidence (profiles):
🔍 Query: "Lead Đọc 4 User Story 266 267 268" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 23.21] /home/baoltb/Desktop/Paseo_Project/profiles/lead.md:1-44 (truncated to 30 lines)
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
│      - Notify or assign `qc` to generate `Testcase` items and unit test suites (

### Local Evidence (tools):
🔍 Query: "Lead Đọc 4 User Story 266 267 268" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 346 matches across 32 files. Top 3 shown:

┌── [Rank #1 | Score: 75.78] /home/baoltb/Desktop/Paseo_Project/tools/research/codex_room_setup_research.md:55-63
│   Section: ## 3. Giao thức Làm việc & Chuỗi Bàn giao (Handoff Sequence)
├── ────────────────────────────────────────────────────────
│   ## 3. Giao thức Làm việc & Chuỗi Bàn giao (Handoff Sequence)
│   
│   Chuỗi bàn giao bắt buộc: **BA ➔ DESIGN ➔ DEV**:
│   1. **Bước 1 (BA)**: Lead BA định nghĩa User Stories kèm Acceptance Criteria (AC) tại `docs/spec/<project>/ba/`.
│   2. **Bước 2 (DESIGN)**: Lead Design thiết kế component, ánh xạ token màu/typography tại `docs/spec/<project>/design/` dựa trên AC của BA.
│   3. **Bước 3 (DEV)**: Lead Dev nhận đầu vào đã được nghiệm thu (BA + Design) để tạo Technical Story / Tasks và giao cho Peer Dev lập trình tại `projects/<project>/`.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 66.83] /home/baoltb/Desktop/Paseo_Project/tools/research/harness_framework_research.md:26-38
│   Section: ### C. Quy tắc Cú pháp Bắt buộc (Title & Description Syntax)
├── ────────────────────────────────────────────────────────
│   ### C. Quy tắc Cú pháp Bắt buộc (Title & Description Syntax)
│   - **User Story Title**: `[Module] – [Vai trò] có thể [hành động]`
│   - **User Story Description**: Chuẩn BDD:
│     ```text
│     As a [User Role],
│     I want

### Local Evidence (projects):
🔍 Query: "Lead Đọc 4 User Story 266 267 268" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25265 matches across 5862 files. Top 3 shown:

┌── [Rank #1 | Score: 68.25] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-store-architecture.md:130-134
│   Section: ### Rule 4: Quản lý Side-Effects trong `withMethods` hoặc `StoreHelper`
├── ────────────────────────────────────────────────────────
│   ### Rule 4: Quản lý Side-Effects trong `withMethods` hoặc `StoreHelper`
│   * Các thao tác đồng bộ `LocalStorage`, `CookieStorage`, thông báo Toast (`TDSMessageService`) và bắn sự kiện (`EventBusService`) phải được cấu hình tập trung trong Store method options hoặc effect pipeline.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 63.7] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe.md:31-33
│   Section: # Tra cứu User Stories / Specs từ TFS wicx-doc-read
├── ────────────────────────────────────────────────────────
│   # Tra cứu User Stories / Specs từ TFS wicx-doc-read
│   python3 tools/wicx_doc_reader.py --uc UC1.01
│   ```
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 63.04] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/libs/features/social-connection/spec.md:531-537
│   Section: ##### 3. Danh mục 4 Nhóm Dữ Liệu Webhook:
├── ────────────────────────────────────────────────────────
│   ##### 3. Danh mục 4 Nhóm Dữ Liệu Webhook:
│   
│   1. 💬 **Tin nhắn

### CRM BA Spec Evidence:
🔍 Query: "Lead Đọc 4 User Story 266 267 268" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 108.56] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 0.5_User_Stories/UC3.04 - Contact chưa gộp xuyên kênh & visitor ẩn danh.md:68-72
│   Section: #### 1.2. Tương tác thứ N cùng PSID/Zalo user ID (gom lịch sử kênh)
├── ────────────────────────────────────────────────────────
│   #### 1.2. Tương tác thứ N cùng PSID/Zalo user ID (gom lịch sử kênh)
│   
│   1. Tương tác mới đến, PSID/Zalo user ID đã có contact Chưa định danh.
│   2. **[WiCX CRM]** Gom vào contact hiện có; tích lũy lịch sử tương tác trên kênh đó. Mọi thứ về khách này trên kênh ngày càng đầy đủ — sẵn sàng gom khi cầu nối mạnh xuất hiện.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 106.89] /home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/sprints/sprint-4/sprint-4.md:61-74
│   Section: ## 🎯 Mục tiêu Sprint 4
├── ────────────────────────────────────────────────────────
│   ## 🎯 Mục tiêu Sprint 4
│   
│   **📋 Mục tiêu Sprint 4** *(đồng bộ theo board — cập nhật 23/09/2026)*
│   
│   | Priority | Mục tiêu | Target/Impact | Related Work Items | Success Criteria | Nguồn |
│   | -------- | -------- | ------------- | ------------------ | ---------------- | ----- |
│   | **P1** | **Xử lý 10 bug P1** phát sinh từ test IAM (đăng nhập/đăng xuất) + Thông tin doanh nghiệp | Đưa 5 bug `

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
