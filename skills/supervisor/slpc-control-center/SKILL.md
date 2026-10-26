---
name: slpc-control-center
description: "Skill vận hành Paseo SLPC Control Center Dashboard (Stitch Obsidian Cyber-Matrix), thực thi Build/Test tự động, điều phối 4 cổng Agent (Supervisor -> Lead -> Peer -> QC) và sinh Unit Test 5-Stage ISTQB."
version: 1.0.0
author: Antigravity, BaoLTB
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [slpc, harness-dashboard, stitch-ui, qc-test-generator, istqb-5-stage, automation, floci, tfs]
---

# Paseo SLPC Control Center & 5-Stage QC Automation Skill (`slpc-control-center`)

Tài liệu kỹ năng chuẩn hóa giúp các Agent (**Supervisor, Lead, Peer, QC**) và Developer điều khiển trực tiếp **Paseo SLPC Control Center (`http://127.0.0.1:8765/harness_dashboard.html`)**, kích hoạt **Build / Unit Test / E2E Automation**, chạy **Pipeline 5 bước ISTQB sinh Unit Test (`tools/qc_test_generator.py`)**, và đồng bộ **343+ Work Items** giữa **Remote Backlog** và **Floci DynamoDB / Local Fallback DB**.

---

## 1. Khi nào sử dụng Skill này (When to Use)

Kích hoạt skill này khi:
- Cần khởi chạy, kiểm tra trạng thái hoặc nâng cấp giao diện **Paseo SLPC Control Center & Harness Matrix** (`scripts/harness_dashboard.py`).
- Cần **sinh tự động Unit Test (`*.spec.ts`, `test_*.py`) và kịch bản `Testcase` theo chuẩn ISTQB 5-Stage** từ Source Code + Spec Markdown (`tools/qc_test_generator.py`).
- Cần gọi REST API của Dashboard để **chạy lệnh Build / Unit Test / Đồng bộ TFS ngầm** (`/api/automation/run`) hoặc **đánh thức Agent SLPC** (`/api/agents/call`).
- Cần tùy biến giao diện theo hệ thống thiết kế **Stitch Obsidian Cyber-Matrix** (`projects/3273106135274644624` • Design System `assets/85a5c121afaa464d9e82a046131901fd`).

---

## 2. Kiến trúc Tổng thể & Đường dẫn Chuẩn (Canonical Paths)

| Thành phần | Đường dẫn chuẩn | Vai trò |
| :--- | :--- | :--- |
| **Dashboard Server & UI** | `scripts/harness_dashboard.py` | HTTP Server (`127.0.0.1:8765`) + Giao diện Stitch Obsidian Cyber-Matrix |
| **5-Stage QC Test Generator** | `tools/qc_test_generator.py` | Pipeline 5 bước phân tích AST Codebase + Spec ➔ Sinh Unit Test & đẩy Harness |
| **Harness State Manager** | `tools/harness_manager.py` | Quản lý State Machine (`New ➔ Accepted ➔ Active ➔ Resolved ➔ Closed`) |
| **Floci & Local Fallback DB** | `tools/floci_client.py` | Kết nối Floci DynamoDB (`127.0.0.1:14566`) kèm fallback `.harness_local_db.json` (0.4s TCP check) |
| **Remote Backlog Sync** | `tools/remote_sync.py` | Đồng bộ Work Items (`Epic`, `User Story`, `Task`, `Testcase`, `Bug`) từ Remote Backlog |
| **SLPC Agent Dispatcher** | `tools/call_agent.py` | Giao thức đánh thức Agent (`Supervisor`, `Lead`, `Peer`, `QC`) qua Paseo CLI |

---

## 3. Quy trình 1: Vận hành SLPC Control Center & REST API (`127.0.0.1:8765`)

### A. Khởi động / Khởi động lại Dashboard Daemon
```bash
python3 scripts/harness_dashboard.py --daemon
```
- **URL Truy cập**: `http://127.0.0.1:8765/harness_dashboard.html`
- **Cơ chế tự động phân vai SLPC (`_infer_slpc_profile`)**:
  - `Epic` ➔ `supervisor` (Gate 1: Scope & Intent Guard)
  - `Feature` / `User Story` ➔ `lead` (Gate 2: Technical Architect & Task Breakdown)
  - `Task` ➔ `peer` (Gate 3: Code Executor & TDD)
  - `Testcase` / `Bug` ➔ `qc` (Gate 4: Quality Gate & 5-Stage Verification)

### B. Danh mục REST API của Control Center
Các Agent hoặc script có thể gọi trực tiếp qua HTTP JSON:

1. **Lấy danh sách Work Items (`GET /api/work-items`)**:
   ```bash
   curl -s "http://127.0.0.1:8765/api/work-items?force=1" | jq 'length'
   ```
2. **Chạy lệnh Build / Unit Test / CLI Automation ngầm (`POST /api/automation/run`)**:
   ```bash
   curl -s -X POST http://127.0.0.1:8765/api/automation/run \
     -H "Content-Type: application/json" \
     -d '{
       "kind": "automation",
       "title": "Run Core Unit Tests",
       "command": "npx jest libs/core/src/utils/validator.helper.spec.ts --no-cache",
       "cwd": "projects/crm-fe"
     }'
   ```
3. **Kích hoạt Pipeline 5-Stage Sinh Unit Test qua API (`POST /api/automation/qc-generate`)**:
   ```bash
   curl -s -X POST http://127.0.0.1:8765/api/automation/qc-generate \
     -H "Content-Type: application/json" \
     -d '{
       "source": "projects/crm-fe/libs/core/src/utils/validator.helper.ts",
       "spec": "projects/crm-fe/libs/core/spec.md",
       "task_id": 161502,
       "out_spec": "/tmp/validator.generated.spec.ts",
       "sync_harness": true,
       "run_test": true
     }'
   ```
4. **Đánh thức Agent SLPC nhận việc (`POST /api/agents/call`)**:
   ```bash
   curl -s -X POST http://127.0.0.1:8765/api/agents/call \
     -H "Content-Type: application/json" \
     -d '{
       "profile": "QC",
       "item_id": 161095,
       "prompt": "Kiểm tra Task #161095 đang ở trạng thái Resolved, sinh unit test bằng qc_test_generator.py và verify."
     }'
   ```

---

## 4. Quy trình 2: Sinh Unit Test & Testcase 5-Stage ISTQB (`tools/qc_test_generator.py`)

Công cụ `tools/qc_test_generator.py` kết hợp phân tích cú pháp mã nguồn (**AST / Symbol Scanner** cho TypeScript/Angular & Python) với tài liệu **Spec / Acceptance Criteria** qua 5 bước khép kín:

```text
[Source Code (.ts/.py) + Spec (.md/AC)]
       │
       ▼
Stage 1: Requirement Extractor ──► Tách các mệnh đề REQ-001..REQ-N & Exported Symbols/Methods
       │
       ▼
Stage 2: Test Point Reviewer   ──► Lọc trùng lặp, chấm điểm Testability, tạo TP-001..TP-N
       │
       ▼
Stage 3: Test Design Planner   ──► Áp dụng kỹ thuật ISTQB (EP, BVA, Decision Table, State Transition) ➔ CI-001..CI-N
       │
       ▼
Stage 4: Test Case & Spec Gen  ──► Sinh Traceable TestCases (TC-001..TC-N) + khung mã nguồn Unit Test (*.spec.ts / test_*.py)
       │
       ▼
Stage 5: Coverage Reviewer     ──► Tính % độ phủ (REQ Coverage, CI Coverage, Symbol Coverage) & đồng bộ lên Harness DB
```

### Lệnh CLI thực thi chuẩn:
```bash
# 1. Phân tích & sinh file Unit Test + Báo cáo JSON 5-Stage
python3 tools/qc_test_generator.py \
  --source projects/crm-fe/libs/core/src/utils/validator.helper.ts \
  --spec projects/crm-fe/libs/core/spec.md \
  --out-spec /tmp/validator.helper.generated.spec.ts \
  --out-json /tmp/validator_5stage_report.json

# 2. Sinh Unit Test, đẩy các Testcase lên Harness DB gắn với Task ID, và chạy Jest kiểm tra ngay
python3 tools/qc_test_generator.py \
  --source projects/crm-fe/libs/core/src/utils/validator.helper.ts \
  --spec projects/crm-fe/libs/core/spec.md \
  --task-id 161502 \
  --sync-harness \
  --run
```

---

## 5. Quy chuẩn Giao diện Stitch Obsidian Cyber-Matrix

Khi chỉnh sửa hoặc mở rộng giao diện trong `scripts/harness_dashboard.py`, bắt buộc giữ vững các Design Tokens từ Stitch (`assets/85a5c121afaa464d9e82a046131901fd`):
- **Nền chính (`--bg-abyss`)**: `#0B0F17` kèm lưới tọa độ quang học `32px × 32px` và radial glow Cyan/Violet.
- **Bề mặt Panel (`--bg-panel`)**: `rgba(17, 24, 39, 0.84)` với `backdrop-filter: blur(12px)` và viền mảnh `1px solid rgba(255, 255, 255, 0.08)`.
- **Typography (Chuẩn tiếng Việt SaaS)**:
  - Toàn bộ UI / Display / KPI / Labels / System Prompt: `'Be Vietnam Pro', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` (bật `-webkit-font-smoothing: antialiased` để hiển thị dấu tiếng Việt sắc nét, không dùng font monospace cho chữ tiếng Việt).
- **Thanh cuộn (`::-webkit-scrollbar`)**: Bắt buộc dùng `color-scheme: dark`, độ rộng `6px`, nền `rgba(6, 9, 15, 0.72)`, thanh trượt bo tròn gradient `linear-gradient(180deg, rgba(6, 182, 212, 0.45), rgba(139, 92, 246, 0.45))`.
