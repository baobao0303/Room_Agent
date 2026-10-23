---
name: workflow-launch-exec
description: "Launch, orchestrate, and drive end-to-end multi-agent pipelines (BA -> DESIGN -> DEV -> VERIFY) for any task."
---

# Workflow Launch & Execution Skill (`workflow-launch-exec`)

Điều phối và thực thi tự động toàn bộ luồng phát triển phần mềm qua chuỗi phòng ban khép kín (BA ➔ DESIGN ➔ DEV ➔ VERIFY).

---

## 1. Quick Start / Agent Run Path
Chạy driver điều phối tự động một task qua toàn bộ quy trình:

```bash
python3 .agents/skills/workflow-launch-exec/driver.py "<tên_dự_án>" "<mô_tả_task_hoặc_user_story>"
```

### Ví dụ:
```bash
python3 .agents/skills/workflow-launch-exec/driver.py "crm-portal" "Customer Export to Excel"
```

---

## 2. Pipeline Execution Stages

1. **Stage 1 (BA)**: Tự động khởi tạo và chuẩn hóa User Story + Acceptance Criteria tại `docs/spec/<project>/ba/`.
2. **Stage 2 (Design)**: Tạo bản ánh xạ component TDS UI và Color Token tại `docs/spec/<project>/design/`.
3. **Stage 3 (Dev)**: Dựng DTO contracts và Architecture spec tại `docs/spec/<project>/dev/`.
4. **Stage 4 (Verify)**: Kiểm tra tính toàn vẹn và đồng bộ trạng thái vào Harness SDLC.

---

## 3. Human Run Path (Manual Execution)
Dành cho lập trình viên muốn kích hoạt thủ công từng bước:
- Tạo spec BA: Viết file tại `docs/spec/<project>/ba/<task>-spec.md`
- Tạo spec UI: Viết file tại `docs/spec/<project>/design/<task>-ui.md`
- Quản lý task: `python3 tools/harness_manager.py add --type "User Story" ...`
