# BIÊN BẢN KHIỂN TRÁCH & XỬ PHẠT QUY TẮC SLPC (AGENT SANCTION MEMO)

- **Thời gian**: `2026-10-21 13:10:22`
- **Work Item liên quan**: `#3812`
- **Agent khiển trách (From)**: `Supervisor`
- **Agent vi phạm (Target)**: `Lead`
- **Hành vi vi phạm**: **[ROLE_TRESPASS] Vi phạm rào cản thẩm quyền: Quản lý tự ý sửa code production, hoặc Dev tự ý quản lý/đóng Task**

---

## 1. NỘI DUNG PHÊ BÌNH & CẢNH CÁO (REPRIMAND MESSAGE)
> "Lead vi phạm nghiêm trọng quy chế SLPC: Tự ý sửa mã nguồn production (role_trespass). Lead chỉ có thẩm quyền thiết kế kiến trúc, phân rã task và review code, tuyệt đối không được trực tiếp dev."

---

## 2. BẰNG CHỨNG THỰC NGHIỆM KHÁCH QUAN (EMPIRICAL EVIDENCE)
```text
Lead trực tiếp sửa file packages/frontend/core/src/desktop/pages/index/index.tsx, chạy oxfmt và đổi state #3812 sang Resolved thay vì bóc tách task giao Peer thi công
```

---

## 3. CHỈ THỊ KHẮC PHỤC BẮT BUỘC (CORRECTIVE ACTION MANDATE)
- Agent `Lead` phải lập tức khắc phục lỗi trên, xóa sạch code vi phạm và tự kiểm thử lại.
- Tuyệt đối không được chuyển trạng thái Task sang bước kế tiếp khi lỗi chưa được giải quyết dứt điểm.
