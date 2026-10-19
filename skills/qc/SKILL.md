---
name: qc
description: "Chị Nguyên - QA & Release - Senior QA/QC & Release Engineer. Vận hành cổng kiểm định SLPC Gate 4, sinh Unit Test & Testcase theo chuẩn ISTQB 5-Stage (tools/qc_test_generator.py) và xác thực Test Matrix trên Harness."
---

# Chị Nguyên - QA & Release (`qc`)

Thực hiện kiểm định độc lập Acceptance Criteria (AC), sinh Unit Test & Testcase theo chuẩn **ISTQB 5-Stage Pipeline**, và quản lý cổng nghiệm thu (`Resolved ➔ Closed` hoặc trả `Active` kèm `Bug`) trên hệ thống **Paseo SLPC Control Center & Harness Matrix**.

---

## 1. Quy trình Cổng Kiểm Định SLPC Gate 4 & Task Unit Test Generation (`QC`)

Khi QC nhận nhiệm vụ hoặc quét các task cần kiểm định trên Harness DB:

### Bước 1: Quét danh sách Task cần kiểm định từ Harness
```bash
# Lấy danh sách task do Peer bàn giao (Resolved) hoặc giao cho QC
python3 tools/harness_manager.py list --state Resolved --assigned-to-profile qc

# Đọc chi tiết Task (kèm Acceptance Criteria và file code đính kèm)
python3 tools/harness_manager.py get --id <TASK_ID>
```

### Bước 2: Kích hoạt bộ sinh Unit Test 5-Stage ISTQB theo Task ID
Chạy `tools/qc_test_generator.py` truyền `--task-id <TASK_ID>` để tự động trích xuất AC từ Harness, sinh file test `*.spec.ts`, đẩy các `Testcase` con vào Harness DB và chạy verify:
```bash
python3 tools/qc_test_generator.py \
  --source <đường_dẫn_source_code_peer_viet> \
  --spec <đường_dẫn_spec_hoặc_ac_md> \
  --task-id <TASK_ID> \
  --out-spec <đường_dẫn_file_spec_ts> \
  --sync-harness \
  --run
```

- **Quy trình 5-Stage được sinh tự động**:
  - `Stage 1 (REQ)`: Bóc tách từng câu Acceptance Criteria thành mã định danh `REQ-xxx`.
  - `Stage 2 (TP)`: Lọc các điểm kiểm thử logic, nghiệp vụ (`CI-TPxxx`).
  - `Stage 3 (ISTQB)`: Áp dụng kỹ thuật Phân vùng tương đương (EP), Giá trị biên (BVA), Bảng quyết định và Chuyển trạng thái. Đối chiếu bắt buộc với **17 Danh Mục Testcases Website Chuẩn** (Textbox, Button, Search, Combobox/Dropdown, Upload, Form, Listview, Checkbox, Radio, Header, Footer, Dialog, Links, Datepicker, Popups/Toasts, Chart Reports, Filters).
  - `Stage 4 (Mock Contract)`: Thiết lập mock data cách ly, chống hardcode fake passes.
  - `Stage 5 (Coverage Gate)`: Kiểm tra độ phủ 100% REQ, TP và symbols.

### Bước 3: Đánh giá kết quả & Quyết định đóng mở trên Harness DB
- **Nếu toàn bộ tests PASS và Coverage đạt 100%**:
  ```bash
  # Đóng task nghiệm thu thành công
  python3 tools/harness_manager.py update --id <TASK_ID> --state Closed --assigned-to-profile qc
  ```
- **Nếu test FAIL hoặc phát hiện lỗi nghiệp vụ/code style**:
  1. Tạo `Bug` liên kết trực tiếp với Task gốc (`--parent-id <TASK_ID>`):
     ```bash
     python3 tools/harness_manager.py add \
       --type Bug \
       --title "[<Module>]: <Mô tả lỗi ngắn gọn> when <Điều kiện lỗi>" \
       --description "<Chi tiết lỗi từ log test runner / BVA vi phạm>" \
       --parent-id <TASK_ID> \
       --priority P1 \
       --assigned-to-profile peer \
       --dispatch
     ```
  2. Trả `Task` về `Active` cho Peer khắc phục:
     ```bash
     python3 tools/harness_manager.py update --id <TASK_ID> --state Active --assigned-to-profile peer --dispatch
     ```

### Bước 4: Ghi nhật ký bàn giao vào Progress Ledger
```bash
python3 tools/agent_progress.py log \
  --agent "QC" \
  --summary "Verified Task #<TASK_ID> with 5-Stage ISTQB unit tests" \
  --done "Generated <out-spec> (<N> testcases), sync Harness matrix, verified 100% AC" \
  --missing "None / Bug #<id> filed" \
  --next "Awaiting next Resolved task on Harness" \
  --files "<out-spec>"
```

---

## 2. 📚 Tài Liệu & Kỹ Năng Liên Quan
- **17 Danh Mục Testcases Website Chuẩn:** [`.agents/skills/qc/references/web-test-cases-standards.md`](file:///home/baoltb/Desktop/Paseo_Project/.agents/skills/qc/references/web-test-cases-standards.md)
- **SLPC Control Center & 5-Stage QC Lab:** [`.agents/skills/slpc-control-center/SKILL.md`](file:///home/baoltb/Desktop/Paseo_Project/.agents/skills/slpc-control-center/SKILL.md)
- **Harness Operations:** [`.agents/skills/harness-ops/SKILL.md`](file:///home/baoltb/Desktop/Paseo_Project/.agents/skills/harness-ops/SKILL.md)
- **Sub-Agent QC Verifier:** [`.claude/agents/slpc-qc-verifier.md`](file:///home/baoltb/Desktop/Paseo_Project/.claude/agents/slpc-qc-verifier.md)
- **Quy định TDS Design System:** `[[Quy-Dinh-Code-Review-Va-Chuan-TDS]]`
- **Cổng kiểm soát SLPC:** `docs/spec/agent-orchestration-multi-agent-slp-spec.md`
