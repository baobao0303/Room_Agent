# 🔍 BÁO CÁO AUDIT TRỰC TIẾP TỪ PM AGENT TRÊN ORCA TERMINAL
**Thực hiện trực tiếp tại Terminal Orca**: `term_fbaffa86-e66a-4d48-b426-f96d3d73c4ed`  
**Model**: `ag/gemini-3.8-flash-high`  
**Thời gian**: `2026-10-22 11:45:00`  
**Chủ đề**: Audit mã nguồn `tools/harness_manager.py` theo yêu cầu từ User & Supervisor  

---

## 1. Kết Luận Khảo Sát Thực Tế
PM Agent đã trực tiếp dùng các công cụ `Search Files`, `Read File` và `Terminal` (`git log`, `git diff`) đọc toàn bộ `tools/harness_manager.py` và `floci_client.py`.

👉 **Kết luận**: **Phát hiện chính xác 5 lỗ hổng kiến trúc** trong công cụ quản lý task, giải thích vì sao Lead Dev bị hiểu nhầm và ôm việc:

---

## 2. Bóc Tách Chi Tiết 5 Lỗ Hổng Kỹ Thuật

### 🔴 Lỗ hổng 1: Thiếu chốt chặn cấm gán Task cho Quản lý trong `add_work_item`
- **Mã nguồn**: `tools/harness_manager.py`, dòng 159–167.
- **Chi tiết**: Trước đây tool chỉ kiểm tra `if wi_type == "epic": cấm Dev tạo`. Hoàn toàn không có dòng kiểm tra nào cấm gán `wi_type == "task"` cho `lead` hoặc `supervisor`. Khi gọi lệnh `add --type Task --assigned-to lead`, tool chấp thuận và lưu vào DB.

### 🔴 Lỗ hổng 2: Bất đồng bộ giữa `--assigned-to` và `--assigned-to-profile`
- **Mã nguồn**: `tools/harness_manager.py`, dòng 356–363.
- **Chi tiết**: Tool nhận 2 cờ tách biệt. Khi truyền `--assigned-to "peer"`, tool để `assigned_to_profile = None`. Khi Lead lọc việc bằng `--assigned-to-profile lead`, xảy ra tình trạng thiếu đồng bộ khiến Lead phải viết script ngoài (`update_tasks.py`) để sửa lại.

### 🔴 Lỗ hổng 3: Mô tả Epic Roadmap dễ gây ảo giác cho Agent
- **Chi tiết**: Khi tạo Epic #4116, phần mô tả liệt kê "Phase 1: ..., Phase 2: ...". Nếu thiếu header rào cản `[DELEGATION MANDATE: LEAD ONLY DECOMPOSES, NEVER IMPLEMENTS]`, prompt của mô hình LLM Lead Dev sẽ hiểu nhầm mình phải trực tiếp thi công.

### 🔴 Lỗ hổng 4: Hàm `update_state` bỏ lọt khi kích hoạt `--state Active`
- **Mã nguồn**: `tools/harness_manager.py`, dòng 249–275.
- **Chi tiết**: Khi Lead Dev gọi `harness_manager.py update --id <id> --state Active` mà không truyền `--assigned-to`, biến `new_assignee = ""` nên tool bỏ qua kiểm tra, cho phép Lead Dev kích hoạt `Active` trên Task thi công.

### 🔴 Lỗ hổng 5: Nhánh SQLite fallback hoàn toàn không có chốt chặn vai trò
- **Mã nguồn**: `tools/harness_manager.py`, dòng 303–330.
- **Chi tiết**: Khối lệnh update SQLite hoàn toàn không có bất kỳ dòng `PermissionError` nào. Khi chạy ở chế độ SQLite hoặc Floci offline, mọi rào cản vai trò đều biến mất.

---

## 3. Các Biện Pháp Đã Được Khắc Phục Hoàn Toàn
1. **Khóa chốt tại `add_work_item`**: Ném `PermissionError` nếu bất kỳ ai gán `Task` cho Lead hoặc Supervisor. Tự động map `assigned_to` sang `assigned_to_profile`.
2. **Khóa chốt tại `update_state`**: Kiểm tra `effective_assignee` (bao gồm cả assignee hiện tại trong DB). Cấm Lead/Supervisor kích hoạt `Active` trên Task thi công.
3. **Đồng bộ nhánh SQLite fallback**: Áp dụng cùng logic rào cản vai trò cho cả DynamoDB và SQLite.
4. **Phân rã chuẩn**: Cả 4 tasks #4117..#4120 đã được gán cố định cho Peer 1, Peer 2, Peer 3 và QC.
