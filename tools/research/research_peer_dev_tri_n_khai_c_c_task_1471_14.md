# Research Report: [Peer Dev] Triển khai các Task #1471, #1472, #1473, #1474, #1475, #1476: Xây dựng Dashboard 3 cột Customer 360 và 6 components con theo docs/spec/customer-360-profile-spec.md

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 15:03:50

## 1. Problem Statement & Scope
- **Research Topic**: `[Peer Dev] Triển khai các Task #1471, #1472, #1473, #1474, #1475, #1476: Xây dựng Dashboard 3 cột Customer 360 và 6 components con theo docs/spec/customer-360-profile-spec.md`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Peer Dev Triển khai các Task 1471 1472" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 1030 matches across 19 files. Top 3 shown:

┌── [Rank #1 | Score: 170.47] /home/baoltb/Desktop/Paseo_Project/docs/spec/raw-data-mapping-spec.md:327-344
│   Section: ## 6. Kế hoạch Phân rã Công việc Triển khai (SLPC Breakdown)
├── ────────────────────────────────────────────────────────
│   ## 6. Kế hoạch Phân rã Công việc Triển khai (SLPC Breakdown)
│   
│   1. **Supervisor**:
│      - Giám sát phạm vi, đảm bảo luồng tuân thủ thiết kế từ 11 board artifact và mockup người dùng cung cấp.
│   2. **Lead Dev**:
│      - Khởi tạo kiến trúc module `data-raw-mapping` trong `apps/mfe-cdp`.
│      - Xây dựng Store quản lý state Wizard 4 bước và State 11 Boards (`RawDataMappingStore`).
│      - Xây dựng HTTP Client DTO kết nối API Ingestion/Projection.
│   3. **Peer Dev**:
│      - Cài đặt `ChannelConnectorListComponent` (Pane trái 320px).
│      - Cài đặt `GeneralMappingConfigComponent` (Bước 1: Form 2 cột, JSON viewer, Sampling controls, Bảng phẳng 12 cột).
│      - Cài đặt `BehaviorEventListComponent` & `CreateEventDrawerComponent` (Bước 2).
│      - Cài đặt `FieldMappingEditorComponent` (Bước 3: Bảng ma trận 5 cột, dropdown chuẩn hóa).
│      - Cài đặt `MappingTestRunComponent` & `MappingVersionHistoryComponent` (Bước 4 & Lịch sử).
│   4. **QC**:
│      - Kiểm thử Unit Test 5 giai đoạn cho bộ chuẩn hóa regex (`CH-SDT`, `CH-EMAIL`, `CH-TEN`).
│      - Kiểm thử UI trên các break

### Local Evidence (profiles):
🔍 Query: "Peer Dev Triển khai các Task 1471 1472" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 33.37] /home/baoltb/Desktop/Paseo_Project/profiles/peer.md:1-40 (truncated to 30 lines)
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
│        `python3 tools/call_agent.py --profile 

### Local Evidence (tools):
🔍 Query: "Peer Dev Triển khai các Task 1471 1472" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 664 matches across 76 files. Top 3 shown:

┌── [Rank #1 | Score: 190.43] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_c_4_user_story_266_267_268_269_.md:1-4
│   Section: # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead] Đọc 4 User Story #266, #267, #268, #269 và tài liệu docs/spec/raw-data-mapping-spec.md. Phân rã task chi tiết cho Peer Dev nhưng ghi rõ Peer chưa được code vội; đồng thời tạo task kiểm thử cho QC để QC viết unit test trước theo chuẩn TDD và 5 giai đoạn ISTQB.
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 13:39:14
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 189.62] /home/baoltb/Desktop/Paseo_Project/tools/research/research_lead_dev_b_t_u_tri_n_khai_epic_1461_.md:1-8
│   Section: # Research Report: [Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
├── ────────────────────────────────────────────────────────
│   # Research Report: [Lead Dev] Bắt đầu triển khai Epic #1461 Hồ sơ khách

### Local Evidence (projects):
🔍 Query: "Peer Dev Triển khai các Task 1471 1472" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 25568 matches across 5890 files. Top 3 shown:

┌── [Rank #1 | Score: 168.1] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/azure-pipelines/AGENTS.md:13-26
│   Section: ## 2. Các bước triển khai (`steps`)
├── ────────────────────────────────────────────────────────
│   ## 2. Các bước triển khai (`steps`)
│   
│   1. **`Install`**:
│      - Lệnh: `npm install --force`
│      - Mục đích: Cài đặt toàn bộ thư viện dependencies (cờ `--force` bắt buộc để xử lý xung đột peer dependencies).
│   2. **`Build môi trường QA`**:
│      - Lệnh: `npm run build:qa`
│      - Mục đích: Build đồng loạt Host (`app-shell`) và các Remote MFEs theo cấu hình QA qua Nx và Rsbuild.
│   3. **`Build version`**:
│      - Lệnh: `npm run buildVersion qa $(Build.BuildNumber) $(Minio_EndPoint) $(Minio_AccessKey) $(Minio_SecretKey)`
│      - Mục đích: Thực thi `build-version.js`:
│        - Cập nhật URL CDN assets vào file `dist/apps/app-shell/index.html`.
│        - Tải toàn bộ thư mục `dist/` lên bucket S3/MinIO QA theo số build version.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 137.34] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-wicx-core-hardening.md:1-10
│   Section: # SPEC: Củng Cố An Ninh & Tối Ưu Nền Tảng `libs/wicx-core`
├── ────────────────────────────────────────────────────────
│   # SPEC: Củng Cố An Ninh & Tối Ưu Nề

### CRM BA Spec Evidence:
🔍 Query: "Peer Dev Triển khai các Task 1471 1472" | Category: all
📊 Tìm thấy 8414 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 231.4] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/docs/plan.md:1-14
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

┌── [Rank #2 | Score: 231.4] /home/baoltb/Desktop/wicx-crm-doc/WiCX/wicx-crm/docs/plan.md:1-14
│   Section: # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
├── ────────────────────────────────────────────────────────
│   # WiCX — kế hoạch triển khai và yêu cầu hạ tầng (Updated cho Tenant-based MinIO)
│   
│   > 🔶 **Cập nhật kiến trúc (2026-08-13).** Đã cậ

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
