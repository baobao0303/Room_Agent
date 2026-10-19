# Research Report: tds-select tds-button tds-tabset tds-table tds-input field-mapping

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 16:08:41

## 1. Problem Statement & Scope
- **Research Topic**: `tds-select tds-button tds-tabset tds-table tds-input field-mapping`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "tds-select tds-button tds-tabset tds-table tds-input field-mapping" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 30 matches across 25 files. Top 3 shown:

┌── [Rank #1 | Score: 42.63] /home/baoltb/Desktop/Room_Agent/docs/spec/cdp-field-mapping-architecture-spec.md:363-384
│   Section: ### 4.3. Task #887 & Task #2102 (Bug #2083): Screen 2 - General Configuration & JSON Field Mapping Stepper (`AC-MAP-03`, `AC-MAP-04`, `WI-2083`, `WI-2102`)
├── ────────────────────────────────────────────────────────
│   ### 4.3. Task #887 & Task #2102 (Bug #2083): Screen 2 - General Configuration & JSON Field Mapping Stepper (`AC-MAP-03`, `AC-MAP-04`, `WI-2083`, `WI-2102`)
│   - **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/general-config/general-config.component.{ts,html,scss,spec.ts}`
│   - **Requirements**:
│     1. **4-Step Progress Stepper (`AC-MAP-03`, `WI-2102`)**:
│        - Hiển thị 4 bước: `1. Chưa cấu hình` ➔ `2. Đã cấu hình chung` ➔ `3. Đang mapping (0/2 form đã map xong)` ➔ `4. Hoàn tất`.
│        - Loại bỏ mã màu hex cứng (`#10b981`, `#2563eb`, `#e2e8f0`, `#475569`) trong `general-config.component.scss`, thay bằng semantic utility classes TDS UI (`tds-color-background-success-subtle tds-color-text-white`, `tds-color-background-primary-subtle tds-color-text-white`, `tds-color-background-neutral-subtle tds-color-text-secondary`).
│     2. **Sub-navigation Tabs (`TDSTabsModule` - `WI-2102`)**:
│        - Thay thế 3 `<button>`

### Local Evidence (profiles):
⚠️ No matching content found for query 'tds-select tds-button tds-tabset tds-table tds-input field-mapping' in /home/baoltb/Desktop/Room_Agent/profiles (Scanned 4 files, 4 sections).

### Local Evidence (tools):
🔍 Query: "tds-select tds-button tds-tabset tds-table tds-input field-mapping" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 12 matches across 120 files. Top 3 shown:

┌── [Rank #1 | Score: 9.54] /home/baoltb/Desktop/Room_Agent/tools/research/qc_5stage_task_885.json:801-850 (truncated to 30 lines)
│   Section: Lines 801-850
├── ────────────────────────────────────────────────────────
│   "description": "**Bộ thư viện TDS UI áp dụng**:"
│         },
│         {
│           "id": "REQ-129",
│           "title": "`tds-table`: Hiển thị danh sách sự kiện nhận về, dữ liệu mẫu trả về sau cấu hình",
│           "description": "`tds-table`: Hiển thị danh sách sự kiện nhận về, dữ liệu mẫu trả về sau cấu hình, form mapping."
│         },
│         {
│           "id": "REQ-130",
│           "title": "`tds-steps`: Hiển thị tiến trình 4 bước (Chưa cấu hình -> Hoàn tất).",
│           "description": "`tds-steps`: Hiển thị tiến trình 4 bước (Chưa cấu hình -> Hoàn tất)."
│         },
│         {
│           "id": "REQ-131",
│           "title": "`tds-tabs`: Chuyển đổi giữa Cấu hình chung, Sự kiện hành vi, Lịch sử hoạt động.",
│           "description": "`tds-tabs`: Chuyển đổi giữa Cấu hình chung, Sự kiện hành vi, Lịch sử hoạt động."
│         },
│         {
│           "id": "REQ-132",
│           "title": "`tds-switch` / `tds-checkbox`: Toggle lưu vào hồ sơ khách hàng.",
│           "description": "`tds-switch` / `tds-checkbox`: Toggle lưu vào hồ sơ khách hàng."
│         },
│      

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
