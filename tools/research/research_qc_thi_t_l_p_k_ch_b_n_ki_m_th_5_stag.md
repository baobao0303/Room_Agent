# Research Report: [QC] Thiết lập kịch bản kiểm thử 5-Stage ISTQB và sinh unit test cases cho Epic #1461 Hồ Sơ Khách Hàng 360 theo docs/spec/customer-360-profile-spec.md

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:04:35

## 1. Problem Statement & Scope
- **Research Topic**: `[QC] Thiết lập kịch bản kiểm thử 5-Stage ISTQB và sinh unit test cases cho Epic #1461 Hồ Sơ Khách Hàng 360 theo docs/spec/customer-360-profile-spec.md`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "QC Thiết lập kịch bản kiểm thử 5-Stage" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 1031 matches across 19 files. Top 3 shown:

┌── [Rank #1 | Score: 333.11] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:125-132
│   Section: #### `TC-MAP-017` - [Decision Table] Thiết lập điều kiện kích hoạt sự kiện (Trigger Rules)
├── ────────────────────────────────────────────────────────
│   #### `TC-MAP-017` - [Decision Table] Thiết lập điều kiện kích hoạt sự kiện (Trigger Rules)
│   - **Given:** Drawer tạo sự kiện.
│   - **When:** Người dùng chọn điều kiện: Trường `URL` + Toán tử `chứa` + Giá trị `/bang-gia`.
│   - **And:** Click "Lưu sự kiện".
│   - **Then:** Sự kiện mới được thêm vào danh sách sự kiện tự tạo của kênh với tag `Tự tạo`, đóng Drawer và hiển thị toast thành công.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 291.96] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:354-357
│   Section: ## 9. Mở rộng lên 4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`) & Tích hợp `031_claude_code_sub_agents`
├── ────────────────────────────────────────────────────────
│   ## 9. Mở rộng lên 4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`) & Tích hợp `031_claude_code_sub_agents`
│   
│   Vì hệ thống của chúng ta vận hành theo mô hình **4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`)** có thêm cực **`QC`** độc lập (Independent Quality Gate & ISTQ

### Local Evidence (profiles):
🔍 Query: "QC Thiết lập kịch bản kiểm thử 5-Stage" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 43.41] /home/baoltb/Desktop/Paseo_Project/profiles/lead.md:1-44 (truncated to 30 lines)
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
│      - Notify or assign `qc` to generate `Testcase` items and unit test sui

### Local Evidence (tools):
🔍 Query: "QC Thiết lập kịch bản kiểm thử 5-Stage" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 678 matches across 78 files. Top 3 shown:

┌── [Rank #1 | Score: 311.7] /home/baoltb/Desktop/Paseo_Project/tools/research/research_qc_th_c_thi_ki_m_th_tr_c_tdd_theo_ch.md:1-4
│   Section: # Research Report: [QC] Thực thi kiểm thử trước (TDD) theo chuẩn 5 giai đoạn ISTQB: Viết Unit Test cho Step 1 (Channel List, General Config & Bảng mẫu 12 cột) theo Task #278 và spec docs/spec/raw-data-mapping-spec.md
├── ────────────────────────────────────────────────────────
│   # Research Report: [QC] Thực thi kiểm thử trước (TDD) theo chuẩn 5 giai đoạn ISTQB: Viết Unit Test cho Step 1 (Channel List, General Config & Bảng mẫu 12 cột) theo Task #278 và spec docs/spec/raw-data-mapping-spec.md
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:51:14
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 272.78] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Đọc

### Local Evidence (projects):
🔍 Query: "QC Thiết lập kịch bản kiểm thử 5-Stage" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25568 matches across 5890 files. Top 3 shown:

┌── [Rank #1 | Score: 304.24] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-channel-management.md:395-402
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

┌── [Rank #2 | Score: 275.04] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/rule.md:1-6
│   Section: # Chuẩn Thiết Kế API & Quy Tắc Nghiệp Vụ: Phân Hệ Quản Lý Thành Viên (Member Management)
├── ────────────────────────────────────────────────────────
│   # Chuẩn Thiết Kế API & Quy Tắc Nghiệp Vụ: Phân Hệ Quản Lý Thành Viên (Member Management)
│   
│   Tài liệu này đặc tả chi tiết toàn bộ các API thuộc phân hệ **Quản lý Thành viên / Nhân viên (Member Management)** theo cấu trúc phân cấp Doanh nghiệp & Cửa hàng (`tenantId` và `shopId`), đồng bộ chính xác với Swagger Backend và mã nguồn CRM Frontend.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 265.68] /home

### CRM BA Spec Evidence:
🔍 Query: "QC Thiết lập kịch bản kiểm thử 5-Stage" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 446.55] /home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/stories/Phase 1_User_Stories/UC2.01 - Bật-tắt connector.md:90-95
│   Section: #### 1.3. Bật kết nối chưa thiết lập
├── ────────────────────────────────────────────────────────
│   #### 1.3. Bật kết nối chưa thiết lập
│   
│   1. **[Tác nhân]** Gạt công tắc **Bật** trên một kết nối *chưa thiết lập*.
│   2. **[Hệ thống WiCX CRM]** Không đổi trạng thái; hiển thị thông báo: *"Kết nối chưa được thiết lập. Vui lòng thiết lập trước khi bật."* kèm nút **"Kết nối"**.
│   3. **[Tác nhân]** Nhấn **"Kết nối"** → hệ thống điều hướng sang màn thiết lập của kênh tương ứng (UC-2.02 → UC-2.05).
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 446.55] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 1_User_Stories/UC2.01 - Bật-tắt connector.md:90-95
│   Section: #### 1.3. Bật kết nối chưa thiết lập
├── ────────────────────────────────────────────────────────
│   #### 1.3. Bật kết nối chưa thiết lập
│   
│   1. **[Tác nhân]** Gạt công tắc **Bật** trên một kết nối *chưa thiết lập*.
│   2. **[Hệ thống WiCX CRM]** Không đổi trạng thái; hiển thị thông báo: *"Kết nối chưa được thiết lập. Vui lòng thiết lập trước khi bật."* kèm nút **"Kết nối"**.
│   3. **[Tác nhân]** Nhấn **"Kết nối"** → hệ thống điều 

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
