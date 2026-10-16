# BIÊN BẢN BÀN GIAO CONTEXT (AGENT HANDOFF RECORD)

- **Mã biên bản**: `HO-[ITEM_ID]-[FROM_ROLE]-[TIMESTAMP]`
- **Thời gian**: `YYYY-MM-DD HH:mm:ss`
- **Agent bàn giao (From)**: `[Supervisor | Lead | Peer | QC]`
- **Agent tiếp nhận (To)**: `[Supervisor | Lead | Peer | QC]`
- **Harness Work Item ID**: `#[ITEM_ID]` - `[TITLE]`

---

## 1. Tóm Tắt Phiên Thực Thi (Execution Summary)
- **Mục tiêu**: [Mục tiêu cốt lõi của phiên làm việc]
- **Kết quả đạt được**:
  - [x] [Việc đã hoàn thành 1]
  - [x] [Việc đã hoàn thành 2]

---

## 2. Danh Sách File Đã Thay Đổi (Touched Files)
- `path/to/file1.ts` (Mô tả thay đổi)
- `path/to/file2.html` (Mô tả thay đổi)

---

## 3. Ngữ Cảnh Kỹ Thuật & Trạng Thái Hiện Tại (State Snapshot)
- **Ranh giới module**: [MFE Shell, CDP, CRM hoặc Shared Lib]
- **State/Store hiện tại**: [Mô tả trạng thái dữ liệu/Signals/API]
- **Điểm neo (Anchors)**: [Hàm/Component trọng tâm đang thao tác dở]

---

## 4. Việc Còn Thiếu & Hướng Đi Kế Tiếp (Missing & Next Steps)
- [ ] [Việc còn thiếu 1 cần làm ngay]
- [ ] [Việc còn thiếu 2]
- **Lệnh khuyến nghị cho Agent tiếp nhận**:
  ```bash
  # Lệnh kiểm tra hoặc chạy tiếp:
  python3 tools/agent_progress.py status
  ```

---

## 5. Rủi Ro & Lưu Ý Đặc Biệt (Gotchas & Constraints)
- [Lưu ý về bộ nhớ, lock, routing, token hoặc design system]
