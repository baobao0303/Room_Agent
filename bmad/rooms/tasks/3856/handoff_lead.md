# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 2

- **Thời gian**: `2026-10-21 14:10:00`
- **Work Item**: `#3856` (Parent Epic: `#3854`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 2` (`peer2`)
- **Nội dung**: Sửa apps/mfe-crm/src/app/remote-entry/entry.routes.ts chuẩn hóa link path và xóa route lặp customers

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Chuẩn hóa link path theo mục 2.2 của spec `docs/spec-wionpos-mfe-integration.md`:
- Đường dẫn `''` trỏ vào `CustomerListComponent`.
- Đường dẫn `':id'` trỏ vào `DetailCustomerComponent`.
- Xóa triệt để các route lặp `path: 'customers'` và `path: 'customers/:id'` để tránh tạo URL rác `/:shopId/customers/customers`.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa `apps/mfe-crm/src/app/remote-entry/entry.routes.ts` (và file spec nếu có). Tuyệt đối không can thiệp module khác.
- Đảm bảo i18n providers và title trên các route con được giữ nguyên vẹn.

### 1.3. Giải pháp gợi ý (Suggested Path)
Trong `apps/mfe-crm/src/app/remote-entry/entry.routes.ts`:
- Giữ route `path: ''` (component: `CustomerListComponent`).
- Xóa route `path: 'customers'` (dòng 15-21).
- Xóa route `path: 'customers/:id'` (dòng 22-28).
- Giữ route `path: ':id'` (component: `DetailCustomerComponent`).
- Giữ route `path: '**'` (redirectTo: `'/error/not-found'`).
- Chạy `npx nx test mfe-crm` để xác minh.
