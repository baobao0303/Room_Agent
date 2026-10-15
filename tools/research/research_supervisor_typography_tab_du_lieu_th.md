# Research Report: [Supervisor] Typography tab Du lieu tho va Mapping du lieu tds-body-2 font-semibold icon 14px

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:07:47

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Typography tab Du lieu tho va Mapping du lieu tds-body-2 font-semibold icon 14px`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Typography tab Du lieu tho va Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 572 matches across 19 files. Top 3 shown:

┌── [Rank #1 | Score: 69.24] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:39-43
│   Section: #### `TC-MAP-001` - [State Transition] Chuyển đổi giữa tab Dữ liệu thô và Mapping dữ liệu
├── ────────────────────────────────────────────────────────
│   #### `TC-MAP-001` - [State Transition] Chuyển đổi giữa tab Dữ liệu thô và Mapping dữ liệu
│   - **Given:** Người dùng đang ở màn hình `/cdp/data-raw` (mặc định tab "Dữ liệu thô").
│   - **When:** Người dùng click vào tab "Mapping dữ liệu".
│   - **Then:** Tab "Mapping dữ liệu" chuyển sang active (viền dưới màu cam thương hiệu `#E05206`), URL cập nhật query param `?tab=mapping`, hiển thị Stepper 4 bước với Bước 1 "Cấu hình chung" đang active.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 45.38] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:150-158
│   Section: #### `TC-MAP-021` - [BVA & Normalization] Chuẩn hóa số điện thoại VN sang chuẩn E.164 (`CH-SDT`)
├── ────────────────────────────────────────────────────────
│   #### `TC-MAP-021` - [BVA & Normalization] Chuẩn hóa số điện thoại VN sang chuẩn E.164 (`CH-SDT`)
│   - **Given:** Các giá trị số điện thoại đầu vào đa dạng.
│   - **Test Matrix:**
│     * Đầu vào `"0969733325"` -> Kế

### Local Evidence (profiles):
🔍 Query: "Supervisor Typography tab Du lieu tho va Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 17.18] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
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
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User di

### Local Evidence (tools):
🔍 Query: "Supervisor Typography tab Du lieu tho va Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 219 matches across 80 files. Top 3 shown:

┌── [Rank #1 | Score: 88.55] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_fix_layout_stepper_4_buoc.md:1-4
│   Section: # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Fix layout Stepper 4 buoc va Scope Wizard Raw Data Mapping
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 14:52:36
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 64.65] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_cdp_raw_data_mapping_even.md:1-4
│   Section: # Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 11:26:58
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 63.89] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_raw_data_mapping_event_pr.md:1-4
│   Section: # Research Report: [Supervisor] Raw Data Mapping & Event 

### Local Evidence (projects):
🔍 Query: "Supervisor Typography tab Du lieu tho va Mapping" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 4965 matches across 5890 files. Top 3 shown:

┌── [Rank #1 | Score: 37.06] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/libs/integration/data-access/src/auto-gen/models/loyalty-promotion-product-available-response-dto.ts:101-102
│   Section: Lines 101-102
├── ────────────────────────────────────────────────────────
│   totalRemain?: number | null;
│   }
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 36.51] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/libs/product/ui/src/modal-view-variant/modal-view-variant.component.ts:776-781
│   Section: Lines 776-781
├── ────────────────────────────────────────────────────────
│   }
│   
│       get permModule() {
│         return PermissionModuleEnum;
│       }
│   }
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 36.48] /home/baoltb/Desktop/Paseo_Project/projects/wion_pos_fe/libs/product/data-access/src/auto-gen/fn/attribute-value/attribute-value-delete.ts:26-30
│   Section: Lines 26-30
├── ────────────────────────────────────────────────────────
│   })
│     );
│   }
│   
│   attributeValueDelete.PATH = '/api/v1/attribute-value/{id}';
└── ────────────────────────────────────────────────────────

### CRM BA Spec Evidence:
🔍 Query: "Supervisor Typography tab Du lieu tho va Mapping" | Category: all
📊 Tìm thấy 1395 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 52.32] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 0.5_User_Stories/UC4.06 - Xem Hoạt động trên hồ sơ (Tab Hoạt động).md:148-153
│   Section: ### Màn hình 1 — Tab Hoạt động (UC4.06 thuộc Hồ sơ 360°)
├── ────────────────────────────────────────────────────────
│   ### Màn hình 1 — Tab Hoạt động (UC4.06 thuộc Hồ sơ 360°)
│   
│   > Vị trí: Tab Hoạt động của UC4.02 Màn 1. Khi nhấn Tab → Màn 1 này thay nội dung bên dưới thanh tab; thanh tab + header (dải màu · tên · trạng thái theo dõi · người phụ trách · nút hành động) giữ nguyên của UC4.02.
│   
│   **Cấu trúc màn:** 2 khối xếp dọc — **Khối A** (Hoạt động của khách) phía trên + **Khối B** (Hoạt động của nhân viên) phía dưới. Trên cùng có **thanh filter** chung (loại + kênh) áp cho cả 2 khối.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 50.86] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs-base/BA/implementation-artifacts/stories/Phase 0.5_User_Stories/UC4.02 - Hồ sơ khách hàng 360° (2 tab).md:65-71
│   Section: #### 1.2. Xem Tab Hoạt động
├── ────────────────────────────────────────────────────────
│   #### 1.2. Xem Tab Hoạt động
│   
│   1. **[Người dùng]** Nhấn Tab Hoạt động.
│   2. **[WiCX CRM]** Hiển thị 2 khối: Hoạt động của khách + Hoạt động của nhân viên; bộ lọc theo loại/kênh

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
