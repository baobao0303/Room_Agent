# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 3

- **Thời gian**: `2026-10-21 14:26:00`
- **Work Item**: `#3873` (Parent Epic: `#3870`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 3` (`peer3`)
- **Nội dung**: Thêm menu wion-customer và từ điển i18n shell

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Bổ sung menu item `wion-customer` vào Sidebar Navigation và cập nhật từ điển i18n theo mục 4 spec `docs/spec-wionpos-mfe-integration.md`:
- `apps/app-shell/src/app/layouts/sidebar/sidebar.mock.ts`: Thêm menu item `wion-customer` vào nhóm `management`.
- `apps/app-shell/public/assets/i18n/vi/shell.json`: Thêm khóa `"WION_CUSTOMER": "Khách hàng WiOnPOS"`.
- `apps/app-shell/public/assets/i18n/en/shell.json`: Thêm khóa `"WION_CUSTOMER": "WiOnPOS Customer"`.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa `sidebar.mock.ts` và 2 file `shell.json`.
- Định dạng menu item chuẩn TDS icon: `icon: 'tdsi-user-star-line'`, `routerLink: ['customer']`.
- Unit test sidebar pass 100%.

### 1.3. Giải pháp gợi ý (Suggested Path)
Trong `sidebar.mock.ts`, nhóm `id: 'management'`:
```ts
{
  id: 'wion-customer',
  labelKey: 'SHELL.NAVIGATION.WION_CUSTOMER',
  icon: 'tdsi-user-star-line',
  routerLink: ['customer'],
},
```
Trong `shell.json` (dưới `SHELL.NAVIGATION`):
- `vi`: `"WION_CUSTOMER": "Khách hàng WiOnPOS"`
- `en`: `"WION_CUSTOMER": "WiOnPOS Customer"`
Chạy `npx nx test app-shell` để xác minh.
