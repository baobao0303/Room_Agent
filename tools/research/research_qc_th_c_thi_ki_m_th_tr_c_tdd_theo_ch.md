# Research Report: [QC] Thực thi kiểm thử trước (TDD) theo chuẩn 5 giai đoạn ISTQB: Viết Unit Test cho Step 1 (Channel List, General Config & Bảng mẫu 12 cột) theo Task #278 và spec docs/spec/raw-data-mapping-spec.md

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:51:14

## 1. Problem Statement & Scope
- **Research Topic**: `[QC] Thực thi kiểm thử trước (TDD) theo chuẩn 5 giai đoạn ISTQB: Viết Unit Test cho Step 1 (Channel List, General Config & Bảng mẫu 12 cột) theo Task #278 và spec docs/spec/raw-data-mapping-spec.md`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "QC Thực thi kiểm thử trước TDD theo" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 267 matches across 15 files. Top 3 shown:

┌── [Rank #1 | Score: 241.68] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:8-18
│   Section: ## 1. Kiến trúc tổng thể: "Three-Role Codex Room" trên Paseo `v0.8.0`
├── ────────────────────────────────────────────────────────
│   ## 1. Kiến trúc tổng thể: "Three-Role Codex Room" trên Paseo `v0.8.0`
│   
│   Khác với các mô hình thử nghiệm đa hồ sơ trước đây (như 9 profile BA/Design/Dev hoặc mô hình 5 role có tách riêng `Review` và `Harness`), phiên bản chuẩn hiện tại của `codex-room-setup` đã thực hiện **Core-3 hard-cut**: chuẩn hóa về đúng **3 ghế (3-seat room)** chạy trên bản phát hành ổn định chính thức của **Paseo `v0.8.0`**.
│   
│   ```text
│   Human (Operator)
│     └── Supervisor (codex-supervisor)  ──► Quản trị danh mục, định tuyến ý định, giữ biên thông tin
│           └── Lead (codex-lead)        ──► Quyền kỹ thuật, chia việc, kiểm chứng & ACCEPT/REJECT
│                 └── Peer (codex-peer)  ──► Thực thi 1 đầu việc độc lập (code hoặc review chỉ-đọc)
│   ```
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 233.53] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:275-278
│   Section: ## 7. Hệ thống Kiểm thử Tự động (Test Suite), Nghiệm thu & Cập nhật Desktop
├── ────────────────────────────────────────────────────────
│   ## 7. Hệ thống Kiểm 

### Local Evidence (profiles):
🔍 Query: "QC Thực thi kiểm thử trước TDD theo" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 29.05] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile QC 

### Local Evidence (tools):
🔍 Query: "QC Thực thi kiểm thử trước TDD theo" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 388 matches across 38 files. Top 3 shown:

┌── [Rank #1 | Score: 333.43] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:39:14
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 190.95] /home/baoltb/Desktop/Paseo_Project/tools/research/codex_room_setup_research.md:44-47
│   Section: ### B. Tầng Thực thi (Peer Roles)
├── ────────────────────────────────────────────────────────
│   ### B. Tầng Thực thi (Peer Roles)
│   - **Peer BA / Peer Design / Peer Dev**: Nhận đúng **1 nhiệm vụ độc lập (bounded outcome)** từ Lead tương ứng.
│   - **Quy tắc

### Local Evidence (projects):
🔍 Query: "QC Thực thi kiểm thử trước TDD theo" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25265 matches across 5862 files. Top 3 shown:

┌── [Rank #1 | Score: 234.29] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-channel-management.md:395-402
│   Section: ## 6. Báo Cáo Kiểm Thử & Đảm Bảo Chất Lượng (QA & Test Verification)
├── ────────────────────────────────────────────────────────
│   ## 6. Báo Cáo Kiểm Thử & Đảm Bảo Chất Lượng (QA & Test Verification)
│   
│   Bộ kiểm thử tự động với Jest đã được thực thi độc lập cho `TenantAccessGuard` để xác thực toàn bộ các kịch bản:
│   
│   ```bash
│   npx nx test app-shell --testFile="tenant-access.guard.spec.ts"
│   ```
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 213.82] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/libs/features/social-connection/spec.md:430-439
│   Section: ##### 1. Cấu trúc thông tin đầu trang (Header & Meta):
├── ────────────────────────────────────────────────────────
│   ##### 1. Cấu trúc thông tin đầu trang (Header & Meta):
│   
│   - **Tên nền tảng & Card Fanpage**:
│     - Icon: Facebook blue icon tròn.
│     - Tên hiển thị: `Facebook Page`.
│     - Phụ đề: `{Tên Page} | Mã liên kết FB: ****{4_ký_tự_cuối}` (VD: `Menswear Simple | Mã liên kết FB: ****H4y1`).
│   - **Trạng thái kết nối & Lần kiểm tra:**
│     - Trạng thái: Badge `[Đang hoạt động]` (xanh lá) hoặc Badge `[Lỗi xác thực]` (đỏ).
│     - Lần kiểm tra gần nhất: 

### CRM BA Spec Evidence:
🔍 Query: "QC Thực thi kiểm thử trước TDD theo" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 342.04] /home/baoltb/Desktop/wicx-crm-doc/BA/team-process/pre-process-actions.md:62-79
│   Section: ### 5. Phân công kiểm thử — Trần Thị Thanh Kiều (QA Lead)
├── ────────────────────────────────────────────────────────
│   ### 5. Phân công kiểm thử — Trần Thị Thanh Kiều (QA Lead)
│   
│   Phân bổ QC responsibility trước Sprint 1 — mỗi domain có 1 người chịu trách nhiệm:
│   
│   | Domain | Owner | Reviewer | Status |
│   |---|---|---|---|
│   | **Frontend** | Lê Tấn Bảo Bảo | Nguyễn Thanh Phương | ⬜ |
│   | **Backend / Connector** | Phạm Hải Đăng | Võ Bá Thuần | ⬜ |
│   | **Identity / Data model** | Đào Tiến Thiện | Hồ Văn Kính | ⬜ |
│   | **Infrastructure / CI-CD** | Võ Bá Thuần | Đào Tiến Thiện | ⬜ |
│   | **Requirement / BA doc** | Trần Đại Phát | Nguyễn Tú Quyên | ⬜ |
│   | **UI/UX** | Nguyễn Ngọc Tân | — | ⬜ |
│   | **Coding Agent / Process** | Phạm Quốc Nguyên | — | ⬜ |
│   | **Sprint / Process** | Nguyễn Trần Thùy Vy | — | ⬜ |
│   | **QC Testing (epic)** | Trần Thị Thanh Kiều | — | ⬜ |
│   
│   > P0.5 không có feature AI → bỏ domain "AI/LLM/Model/Flow" (Phase 6). Đội DA (dashboard DA-1..6) chưa tuyển → dashboard build sau khi E3/E4 có data thật (Sprint 3+), không blocker Sprint 1.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 342.04] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base

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
