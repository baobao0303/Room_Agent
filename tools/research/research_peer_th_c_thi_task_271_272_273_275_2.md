# Research Report: [Peer] Thực thi Task #271, #272, #273, #275, #276: Xây dựng các component Raw Data Mapping theo tds-tabset card và spec research-raw-data-mapping-projection.md

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:14:14

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer] Thực thi Task #271, #272, #273, #275, #276: Xây dựng các component Raw Data Mapping theo tds-tabset card và spec research-raw-data-mapping-projection.md`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Thực thi Task 271 272 273 275" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 335 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 99.66] /home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md:186-191
│   Section: ### Phiên #90 — `2026-10-15 14:06:48 +0700` | **Supervisor**
├── ────────────────────────────────────────────────────────
│   ### Phiên #90 — `2026-10-15 14:06:48 +0700` | **Supervisor**
│   - **Tóm tắt**: Chuyển 5 task Dev #271, #272, #273, #275, #276 sang Active và hướng dẫn code theo tds-tabset card
│   - **Đã thực hiện**:
│     - Nhận việc 5 task FE Dev #271, #272, #273, #275, #276 trên Harness DB, chuyển state sang Active
│   - **Bàn giao bước tiếp theo**: Peer Dev thực thi mã nguồn FE theo chuẩn tds-ui và spec research-raw-data-mapping-projection.md
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 96.43] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:180-181
│   Section: ### Giai đoạn 4: Kiểm thử Bước 4 - Chạy thử (Dry Run) & Sổ cái Phiên bản (Task #277 / US #269)
├── ────────────────────────────────────────────────────────
│   ### Giai đoạn 4: Kiểm thử Bước 4 - Chạy thử (Dry Run) & Sổ cái Phiên bản (Task #277 / US #269)
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 93.34] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:37-38
│   Section: ### Gi

### Local Evidence (profiles):
🔍 Query: "Peer Thực thi Task 271 272 273 275" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 28.86] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
🔍 Query: "Peer Thực thi Task 271 272 273 275" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 480 matches across 50 files. Top 3 shown:

┌── [Rank #1 | Score: 129.49] /home/baoltb/Desktop/Paseo_Project/tools/research/codex_room_setup_research.md:44-47
│   Section: ### B. Tầng Thực thi (Peer Roles)
├── ────────────────────────────────────────────────────────
│   ### B. Tầng Thực thi (Peer Roles)
│   - **Peer BA / Peer Design / Peer Dev**: Nhận đúng **1 nhiệm vụ độc lập (bounded outcome)** từ Lead tương ứng.
│   - **Quy tắc Bounded Scope**: Mỗi Peer chỉ có quyền ghi trên phạm vi được giao (`moving write scope`), không sửa code hoặc tài liệu của department khác.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 123.21] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TD

### Local Evidence (projects):
🔍 Query: "Peer Thực thi Task 271 272 273 275" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25379 matches across 5870 files. Top 3 shown:

┌── [Rank #1 | Score: 85.68] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-channel-management.md:395-402
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

┌── [Rank #2 | Score: 81.64] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/spec.md:1-9
│   Section: # Tài liệu Phân tích & Đặc tả Kỹ thuật: Thiết lập PWA & Angular Service Worker (`@angular/service-worker`) cho Hệ thống WiCX
├── ────────────────────────────────────────────────────────
│   # Tài liệu Phân tích & Đặc tả Kỹ thuật: Thiết lập PWA & Angular Service Worker (`@angular/service-worker`) cho Hệ thống WiCX
│   
│   > **Tham chiếu chuẩn:** [Angular Service Worker Repository (`angular/service-worker-builds`)](https://github.com/angular/service-worker-builds) & [Angular Official PWA Guide](https://angular.dev/ecosystem/service-workers).  
│   > **Hệ thống áp dụng:** WiCX Enterprise CRM (Host `apps/app-shell`

### CRM BA Spec Evidence:
🔍 Query: "Peer Thực thi Task 271 272 273 275" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 127.66] /home/baoltb/Desktop/wicx-crm-doc/BA/planning-artifacts/references/10. Product Roadmap 2026.md:1-4
│   Section: # 5\. Product Roadmap 2026 (Thực thi)
├── ────────────────────────────────────────────────────────
│   # 5\. Product Roadmap 2026 (Thực thi)
│   
│   **Mục tiêu tài liệu:** Lịch thực thi năm 2026. Khác với `4. Product Roadmap (Tổng thể)` (chiến lược đa năm), bản này là lịch chi tiết cho 2026 để mình biết đang đi đúng hay trượt.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 127.66] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/planning-artifacts/references/10. Product Roadmap 2026.md:1-4
│   Section: # 5\. Product Roadmap 2026 (Thực thi)
├── ────────────────────────────────────────────────────────
│   # 5\. Product Roadmap 2026 (Thực thi)
│   
│   **Mục tiêu tài liệu:** Lịch thực thi năm 2026. Khác với `4. Product Roadmap (Tổng thể)` (chiến lược đa năm), bản này là lịch chi tiết cho 2026 để mình biết đang đi đúng hay trượt.
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 115.75] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/docs/event-field-catalog.md:114-125
│   Section: ### `catalog_shape` — thứ khiến toàn bộ việc này khả thi
├── ────────────────────────────────────────────────────────
│   ### `catalog_shape` — thứ khiến toàn bộ vi

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
