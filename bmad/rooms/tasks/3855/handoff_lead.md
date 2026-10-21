# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 14:10:00`
- **Work Item**: `#3855` (Parent Epic: `#3854`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Sửa apps/app-shell/src/app/app.routes.ts gỡ bỏ bọc trùng provideWII18n/resolve theo Pattern A spec MFE

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Gỡ bỏ hoàn toàn `providers: provideWII18n(...)` và `resolve: { i18n: i18nResolver }` ở route `customers` và `crm` trong `apps/app-shell/src/app/app.routes.ts` để tuân thủ nghiêm ngặt Pattern A mục 2.1 của spec `docs/spec-wionpos-mfe-integration.md` (entry `./Routes` của remote đã tự bọc scope i18n). Cập nhật `apps/app-shell/src/app/app.routes.spec.ts` cho đồng bộ.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa `apps/app-shell/src/app/app.routes.ts` và `apps/app-shell/src/app/app.routes.spec.ts`. Tuyệt đối không can thiệp file khác.
- **Test Gate**: Đảm bảo chạy `npx nx test app-shell` pass 100%.
- Không gây ảnh hưởng đến các route khác (`dashboard`, `data-raw`, `setting`).

### 1.3. Giải pháp gợi ý (Suggested Path)
1. Trong `apps/app-shell/src/app/app.routes.ts`:
   - Tại route `path: 'customers'`: Xóa `providers: provideWII18n(...)` và `resolve: { i18n: i18nResolver }`. Chỉ giữ `path`, `title` và `loadChildren: () => loadRemoteMfeRoutes('mfe-crm').catch(handleRemoteError('mfe-crm'))`.
   - Tại route `path: 'crm'`: Làm tương tự như `customers`.
2. Trong `apps/app-shell/src/app/app.routes.spec.ts`:
   - Kiểm tra các test case assert providers/resolve của `customers`/`crm`, cập nhật kỳ vọng test theo cấu trúc mới.
3. Chạy `npx nx test app-shell` để xác minh.
