# Research Report: Raw Data Mapping Step 1 Channel Connector List Flattened 12 Column Table ISTQB Test Cases

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:54:20

## 1. Problem Statement & Scope
- **Research Topic**: `Raw Data Mapping Step 1 Channel Connector List Flattened 12 Column Table ISTQB Test Cases`
- **Workspace**: `.`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Raw Data Mapping Step 1 Channel Connector List" | Target: ./docs
📊 Found 187 matches across 16 files. Top 3 shown:

┌── [Rank #1 | Score: 104.09] ./docs/spec/wicx-crm-fe/testcases/US-raw-data-mapping-testcases.md:1-14
│   Section: # Bộ Test Case Kiểm Thử 5 Giai Đoạn ISTQB: Phân Hệ Ánh Xạ Dữ Liệu Thô (Raw Data Mapping)
├── ────────────────────────────────────────────────────────
│   # Bộ Test Case Kiểm Thử 5 Giai Đoạn ISTQB: Phân Hệ Ánh Xạ Dữ Liệu Thô (Raw Data Mapping)
│   
│   > **Mã tài liệu:** `TC-SPEC-CDP-RAW-DATA-MAPPING-01`  
│   > **Áp dụng theo:** Chuẩn 5 giai đoạn ISTQB (Requirement Analysis -> Test Point Extraction -> ISTQB Techniques -> Executable Test Design -> Quality Gate)  
│   > **Parent Stories:**  
│   > - US #266: Cấu hình chung và lấy mẫu dữ liệu thô (Step 1)  
│   > - US #267: Quản lý sự kiện hành vi & Drawer tạo sự kiện tùy biến (Step 2)  
│   > - US #268: Ma trận ánh xạ trường & Bộ chuẩn hóa (Step 3)  
│   > - US #269: Chạy thử nghiệm & Quản lý lịch sử phiên bản (Step 4)  
│   > **QC Tasks:** #278, #279, #280, #277  
│   > **Chế độ phát triển:** TDD (Test-Driven Development) — QC viết test trước, Peer Dev HOLD chưa code.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 82.98] ./docs/spec/research-raw-data-mapping-projection.md:1-9
│   Section: # Nghiên cứu Chuyên sâu: CDP Raw Data Mapping & Event Pr

### Local Evidence (profiles):
🔍 Query: "Raw Data Mapping Step 1 Channel Connector List" | Target: ./profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 7.29] ./profiles/qc.md:1-61 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: QC
│   provider: router9
│   model: ag/gemini-3.8-flash-high
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: QC (Test Architect, Unit/E2E Test Generator & Independent Quality Gate).
│   
│   MISSION:
│   You are the `C` in the SLPC (`Supervisor - Lead - Peer - QC`) architecture.
│   You do NOT write or fix production feature code for Peer. Your job is to:
│   1. Generate traceable `Testcase` work items and executable unit tests (`*.spec.ts` / `test_*.py`) from the Spec + Codebase using the 5-Stage ISTQB Pipeline (`tools/qc_test_generator.py`).
│   2. Run deterministic automated tests & coverage checks when Peer marks a task `Resolved`.
│   3. Gatekeep `Closed`: Only transition a task to `Closed` when 100% of required Coverage Items (`CI-TPxxx-xx`), Requirements (`REQ-xxx`), and automated test executions pass.
│   
│   WORKFLOW:
│   1. PHASE 1 — 5-STAGE TEST GENERATION (From Spec + Codebase):
│      - Run the QC Test Generator against the target source file and spec/task:
│        `python3 tools/qc_test_generator.py --source <path/to/file.ts> --spec <path/to/spec.md> --task-id <id>

### Local Evidence (tools):
🔍 Query: "Raw Data Mapping Step 1 Channel Connector List" | Target: ./tools
📊 Found 318 matches across 40 files. Top 3 shown:

┌── [Rank #1 | Score: 92.15] ./tools/research/research_supervisor_cdp_raw_data_mapping_even.md:1-4
│   Section: # Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] CDP Raw Data Mapping & Event Projection Field Mapping UI
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 11:26:58
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 87.64] ./tools/research/research_qc_th_c_thi_ki_m_th_tr_c_tdd_theo_ch.md:1-4
│   Section: # Research Report: [QC] Thực thi kiểm thử trước (TDD) theo chuẩn 5 giai đoạn ISTQB: Viết Unit Test cho Step 1 (Channel List, General Config & Bảng mẫu 12 cột) theo Task #278 và spec docs/spec/raw-data-mapping-spec.md
├── ────────────────────────────────────────────────────────
│   # Research Report: [QC] Thực thi kiểm thử trước (TDD) theo chuẩn 5 giai đoạn ISTQB: Viết Unit Test cho Step 1 (Channel List, General Config & Bảng mẫu 12 cột) theo Task #278 và spec docs/spec/raw-data-mapping-spec.md
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:51:14
└── ──────────

### Local Evidence (projects):
🔍 Query: "Raw Data Mapping Step 1 Channel Connector List" | Target: ./projects
📊 Found 15760 matches across 5864 files. Top 3 shown:

┌── [Rank #1 | Score: 51.63] ./projects/fe-mfes/docs/superpowers/specs/2026-08-06-wi-mfes-i18n-design.md:232-233
│   Section: ## Data flow
├── ────────────────────────────────────────────────────────
│   ## Data flow
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 48.12] ./projects/wicx-crm-fe/libs/features/raw-event-data/data-access/src/auto-gen/models/social-channel-payload-request.ts:51-65
│   Section: Lines 51-65
├── ────────────────────────────────────────────────────────
│   * Channel unique name.
│      */
│     channelUniqueName?: string | null;
│   
│     /**
│      * Channel URL.
│      */
│     channelUrl?: string | null;
│     owner?: SocialChannelOwnerPayloadRequest;
│   
│     /**
│      * Parent channel identity.
│      */
│     parentId?: string | null;
│   }
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 47.95] ./projects/wicx-crm-fe/libs/features/raw-event-data/data-access/src/auto-gen/models/list-members-request.ts:1-35 (truncated to 30 lines)
│   Section: Lines 1-35
├── ────────────────────────────────────────────────────────
│   /* tslint:disable */
│   /* eslint-disable */
│   import { ShopUserStatus } from '../models/sho

### CRM BA Spec Evidence:
🔍 Query: "Raw Data Mapping Step 1 Channel Connector List" | Category: all
📊 Tìm thấy 4865 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 74.91] ../crm-doc/BA/planning-artifacts/epic-breakdown/phase1-epic-breakdown.md:113-132
│   Section: ## Epic E2 — Connector mở rộng (TPOS + Kill-switch)
├── ────────────────────────────────────────────────────────
│   ## Epic E2 — Connector mở rộng (TPOS + Kill-switch)
│   
│   **Giá trị:** 4 connector P0.5 (WiPix/Facebook/Zalo/Tổng đài) đã thu event về ingestion. Phase 1 thêm TPOS — connector cho tenant bán hàng đa kênh (order lifecycle) — và kill-switch bật/tắt connector theo tenant.
│   
│   **Kế thừa từ P0.5:** ingestion API chung, UI credential, UI trạng thái, 4 connector.
│   
│   **Phạm vi Phase 1:**
│   
│   - **Connector TPOS — 2 luồng** (theo cơ chế identity khác nhau):
│     - **(A) FB chat → order lifecycle:** orderPaid / orderBounced / orderCancelled từ chat Facebook; identity mạnh (SĐT/PSID).
│     - **(B) Sàn sync:** đồng bộ đơn từ sàn TMĐT; chỉ có `buyer_id` sàn → anonymous (chưa định danh được).
│   - **Kill-switch:** tenant bật/tắt từng connector; tắt → ngừng thu event, data cũ giữ nguyên.
│   
│   **Tiêu chí chấp nhận (epic):**
│   
│   - Connector TPOS luồng A: event order (paid/bounced/cancelled) đến real-time, mang SĐT/PSID → gộp về contact đúng.
│   - Connector TPOS luồng B: đơn sàn chỉ có `buyer_id` → tạo hồ sơ anonymous, không gộp nhầm.
│   - Tenant bật connector → nh

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
