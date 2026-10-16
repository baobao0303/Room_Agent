---
name: lead-review
description: Bộ kỹ năng Lead Dev liên tục rà soát code, kiểm soát kiến trúc và hỗ trợ giảm tải cho Peer Dev.
---

# Kỹ Năng Lead Dev Continuous Review & Scaffolding

Bộ kỹ năng chuyên biệt cho vai trò **Lead Dev** trong mô hình SLPC:
1. **Rà soát code liên tục**: Chạy `python3 tools/lead_code_review.py` để quét diff thay đổi của Peer Dev.
2. **Kiểm tra chuẩn mực**:
   - Angular 18 Standalone + `ChangeDetectionStrategy.OnPush`.
   - TDS UI semantic tokens (loại bỏ màu hex cứng).
   - Ranh giới Single-Ownership (không sửa chéo file ngoài module được giao).
   - YAGNI: Xóa boilerplate thừa, chỉ giữ lại code tối thiểu cần thiết.
3. **Giảm tải cho Peer Dev**:
   - Định nghĩa trước interface DTO/models trong `models/` trước khi giao task.
   - Giao việc chuẩn 3 phần (Ultimate Goal, Hard Constraints, Suggested Path).
   - Ký nhận biên bản bàn giao tại `bmad/rooms/lead/latest_handoff.md`.
