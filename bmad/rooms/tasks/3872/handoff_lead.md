# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 2

- **Thời gian**: `2026-10-21 14:26:00`
- **Work Item**: `#3872` (Parent Epic: `#3870`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 2` (`peer2`)
- **Nội dung**: Khai báo route customer nạp remote WiOnPOS kèm contexts

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Khai báo route `customer` dưới `path: ':id'` trong `apps/app-shell/src/app/app.routes.ts` để nạp `loadRemoteMfeRoutes('customer', './Routes')` kèm `provideWiRemoteContexts()` theo đúng Pattern A mục 3 của spec `docs/spec-wionpos-mfe-integration.md`. Cập nhật `apps/app-shell/src/app/app.routes.spec.ts`.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa `apps/app-shell/src/app/app.routes.ts` và `apps/app-shell/src/app/app.routes.spec.ts`.
- Giữ nguyên 100% các route hiện hữu (`customers`, `crm`, `dashboard`, `data-raw`, `setting`...).
- Không bọc thêm `provideWII18n` hoặc `createRemoteRouteScope` trùng lặp trên route `customer`.
- `npx nx test app-shell` pass 100%.

### 1.3. Giải pháp gợi ý (Suggested Path)
Trong `apps/app-shell/src/app/app.routes.ts`, dưới nhánh con của `:id`:
```ts
{
  path: 'customer',
  title: 'CUSTOMER.TITLE',
  providers: [
    ...provideWiRemoteContexts(),
  ],
  loadChildren: () =>
    loadRemoteMfeRoutes('customer', './Routes').catch(
      handleRemoteError('customer')
    ),
},
```
Cập nhật `app.routes.spec.ts` để kiểm tra sự tồn tại và cấu hình của route `customer`.
