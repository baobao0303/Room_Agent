# Bách Khoa Toàn Thư Phòng Ban (BMAD Canonical Wiki)

> **Mã quy chuẩn**: `bmad/wiki/README.md`  
> **Kiến trúc**: The Shared Brain & BMAD Promotion Gate  
> **Tôn chỉ**: Wikipedia Fidelity — Tri thức chuẩn hóa, bất biến và có nguồn gốc thẩm định.

Chào mừng đến với **BMAD Canonical Wiki** — trung tâm tri thức chính thức của hệ thống đa tác nhân `Room_Agent`.

---

## 1. Nguyên Tắc Vận Hành "Draft ➔ Wiki" (The Promotion Gate)

Khác với các hệ thống AI thông thường cho phép Agent tự ý sửa tài liệu chính thức gây loãng context và mâu thuẫn thông tin:
- **Không bao giờ viết trực tiếp vào Wiki**: Các Agent (Peer Dev, Lead, PM) bắt buộc soạn thảo ghi chú, giải pháp kỹ thuật và phân tích nháp tại `bmad/rooms/<role>/drafts/<topic>.md`.
- **Thẩm định độc lập trước khi xuất bản**: Bản nháp chỉ được chuyển lên Wiki khi có sự phê duyệt chính thức từ **Lead Dev** (thẩm định kiến trúc) hoặc **QC** (thẩm định chất lượng & kiểm thử) thông qua công cụ:
  ```bash
  python3 tools/bmad_promote.py \
    --draft bmad/rooms/lead/drafts/my_design.md \
    --domain architecture \
    --title "Tên Bài Viết Chuẩn" \
    --reviewer lead
  ```
- **Lưu trữ nguồn gốc (Provenance & Proven Drafts)**: Sau khi promote, bản nháp gốc được lưu trữ tự động vào `bmad/rooms/archive/promoted_drafts/` và ghi nhật ký vào `bmad/rooms/room_ledger.json`.

---

## 2. Cấu Trúc Các Phân Vùng Tri Thức (Wiki Domains)

- **`architecture/`**: Kiến trúc tổng thể, sơ đồ module, thiết kế API DTO, Module Federation.
- **`governance/`**: Quy chuẩn phân quyền SLPPC, trần ngân sách vòng lặp, kiểm soát chi phí token.
- **`protocols/`**: Giao thức không gian làm việc (`WORKSPACE_PROTOCOL.md`), tiêu chuẩn Single-Ownership, RPC specs.
- **`testing/`**: Tiêu chuẩn ISTQB 5-Stage, Testing Contract `tds-test-id`, báo cáo ma trận kiểm thử.
