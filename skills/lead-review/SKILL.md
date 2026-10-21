---
name: lead-review
description: "Bộ kỹ năng rà soát mã nguồn (Code Review) và thẩm định kiến trúc dành riêng cho khối Quản lý (Lead Dev & Supervisor) trong mô hình SLPC."
version: 2.0.0
author: BaoLTB, Lead Architect
roles: [lead, supervisor]
---

# Kỹ Năng Code Review & Thẩm Định Kiến Trúc Dành Cho Quản Lý (SLPC Management Code Review)

Trong mô hình SLPC, **Quản lý (Supervisor & Lead) tuyệt đối KHÔNG viết code tính năng**, nhưng nắm quyền sinh sát về **Chất lượng, Ranh giới và Kiến trúc mã nguồn**.

Bộ kỹ năng này quy định quy chuẩn, danh mục kiểm tra (checklist) và công cụ tự động hóa để Quản lý thẩm định code của Dev trước khi chuyển giao cho QC.

---

## 1. Phân Định Trách Nhiệm Review Giữa Supervisor và Lead

| Vai trò | Phạm vi Review (Review Scope) | Tiêu chí cốt lõi (Core Criteria) | Hành động khi vi phạm |
| :--- | :--- | :--- | :--- |
| **Supervisor** | **Intent & Scope Alignment** | - Code có giải quyết đúng bài toán của User không?<br>- Có phát sinh Scope Creep (tự ý thêm tính năng không ai yêu cầu) không?<br>- Có rủi ro xóa dữ liệu người dùng không? | Trả task về cho Lead bóc tách lại; khiển trách `scope_creep`. |
| **Lead Dev** | **Architecture & Code Standards** | - Tuân thủ Single-Ownership (chỉ sửa module được giao).<br>- Tuân thủ TDS UI Design Tokens (0% mã màu hex cứng).<br>- Angular 18 OnPush performance.<br>- Lazy Senior Dev / YAGNI (xóa trước thêm sau, không dead code). | Từ chối diff; chạy `tools/agent_reprimand.py --penalize` giáng task về `Active`. |

---

## 2. Checklist 5 Điểm Bắt Buộc Của Lead Dev (5-Point Review Gate)

Trước khi cho phép Task chuyển sang bước kiểm định độc lập của QC, Lead Dev bắt buộc phải đối soát qua 5 tiêu chí:

### A. Ranh giới Sở hữu Đơn nhất (Single-Ownership Invariant)
- **Quy tắc**: 100% file thay đổi phải nằm trọn trong module được giao (VD: Task CDP chỉ được sửa trong `apps/mfe-cdp/...`).
- **Vi phạm**: Sửa chéo sang `app-shell`, `libs/`, hoặc module khác ➔ **REJECT NGAY LẬP TỨC**.

### B. Chuẩn Hóa Design Tokens TDS UI (No Raw Hex Codes)
- **Quy tắc**: Nghiêm cấm mã màu hex cứng dạng `#FF4E00`, `#2EB032`, `rgb(...)` trong template HTML và stylesheet SCSS.
- **Tiêu chuẩn**: Bắt buộc dùng class tiện ích Tailwind chuẩn TDS (`bg-white`, `border-neutral-200`) hoặc token CSS `var(--tds-color-...)`.

### C. Hiệu Năng Angular 18 Standalone & OnPush
- **Quy tắc**: Mọi component tạo mới hoặc refactor bắt buộc phải có:
  ```typescript
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  ```
- **Signals**: Ưu tiên Angular Signals (`signal()`, `computed()`, `input()`, `output()`) thay vì quản lý subscription thủ công.

### D. Tinh Gọn Mã Nguồn & YAGNI (Lazy Senior Dev)
- **Quy tắc**: "Code tốt nhất là code không cần viết".
- **Kiểm tra**:
  * Có tạo interface cho 1 implement duy nhất không? (Xóa).
  * Có viết file util chỉ dùng 1 lần không? (Chuyển thành inline/stdlib).
  * Diff có xóa code cũ trước khi thêm code mới không?

### E. Quét Sạch Dead Code & Import Rác
- **Quy tắc**: Khi refactor (VD: từ `tds-data-table` sang `tds-table`), bắt buộc phải dọn sạch:
  * Các import module cũ không còn sử dụng.
  * Các `@ViewChild` mồ côi không có lệnh gọi.
  * Các biến, hàm private không còn nơi nào invoke.

---

## 3. Quy Trình & Công Cụ Review Tự Động Hóa

### Bước 1: Quét Tự Động Bằng Tool
Lead Dev chạy công cụ thẩm định tự động:
```bash
python3 tools/lead_code_review.py --repo-dir projects/wicx-crm-fe --task-id <id>
```
- Công cụ tự động quét Git Diff (cả staged và unstaged).
- Kiểm tra mã màu hex, OnPush, single-ownership.
- Xuất báo cáo tại: `bmad/rooms/lead/latest_review.md`.

### Bước 2: Huy Động Sub-Agents Hỗ Trợ Review Sâu
- Khi diff phức tạp, Lead gọi Sub-agent:
  * `gemini-codebase-analyzer`: Quét 1M+ token để kiểm tra blast radius và import rác.
  * `strategic-reasoning-architect`: Phân tích xem giải pháp của Peer có tối ưu không.

### Bước 3: Đưa Ra Quyết Định (Verdict)

#### Trường hợp 1: APPROVED (Đạt chuẩn 100%)
Lead ký duyệt biên bản và bàn giao việc sang phòng QC:
```bash
# Cập nhật handoff cho QC
python3 tools/agent_progress.py log \
  --agent "Lead" \
  --summary "Code review APPROVED Task #<id>, chuyển giao cho QC" \
  --files "<files>"

# Chuyển trạng thái trên Harness DB
python3 tools/harness_manager.py update --id <id> --state Resolved --assigned-to-profile qc
```

#### Trường hợp 2: REJECTED (Phát hiện lỗi vi phạm ➔ TỰ ĐỘNG TẠO BUG)
Lead không bao giờ sửa code hộ Dev. Thay vào đó, Lead lập tức kích hoạt công cụ xử phạt:
```bash
python3 tools/agent_reprimand.py \
  --from-role Lead \
  --to-role Peer \
  --violation hardcoded_hex \
  --evidence "<dòng code vi phạm trích từ git diff>" \
  --message "Yêu cầu xóa sạch mã màu hex cứng và thay bằng token chuẩn TDS trước khi nộp lại!" \
  --task-id <id> \
  --penalize
```
**Hệ thống tự động kích hoạt**:
1. **Tạo Ticket dạng `Bug` trên Harness DB**: Sinh Bug `[Review]: Phat hien <violation> when reviewed by Lead`, độ ưu tiên `P1`, gán đích danh cho `peer` kèm bằng chứng thực tế.
2. **Giáng cấp Task**: Task chính bị giật ngược từ `Resolved` về `Active`.
3. **Bắn thông báo qua Orca**: Gửi escalation cảnh cáo vào terminal của Peer Dev. Dev bắt buộc phải fix xong Bug này mới được nộp lại cho QC!
