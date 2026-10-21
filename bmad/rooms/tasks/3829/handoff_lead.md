# BÁO CÁO THẨM THẤU KIẾN TRÚC & PHÂN RÃ NHIỆM VỤ TASK #3829
## Chuẩn Hóa Module Federation, Providers & Contexts WiOnPOS Integration

- **Thời gian**: `2026-10-21 13:58:00`
- **Work Item**: `#3829`
- **Lead Architect & PM**: `Lead Dev`
- **Tài liệu thẩm định**: 10 tài liệu chuẩn trong `projects/wicx-crm-fe/docs/` (`providers/` và `contexts/`)

---

## 1. Bản Đồ Trọng Tâm Kiến Trúc (Architectural Blueprint)

### 1.1. Kiến Trúc Module Federation & Phiên Bản Remote Dev
- **Quy tắc phiên bản**: Remote bản `dev`/`development` bắt buộc phải từ **`ver261019-3` trở lên** (bản số 3 ngày 19/10/2026).
  - Thuật toán so sánh: Phân tích `verYYMMDD-N` ➔ so sánh số nguyên ngày `YYMMDD` trước, sau đó so sánh số bản `N` (không so sánh chuỗi thô).
  - *Hiện trạng vi phạm*: `manifest/development/module-federation.manifest.json` đang trỏ bản cũ `ver261008-2` ➔ Phải nâng lên `>= ver261019-3`.
- **Runtime Federation**: Bắt buộc dùng `@module-federation/enhanced/runtime` kết hợp shared singleton cho Angular (Core, Common, Forms, Router, CDK), RxJS, TDS UI (gồm entry phụ `/modal`), và bộ `@wi-mfes/*`.

### 1.2. Quy Tắc Routing: `./Routes` vs `./Providers`
- **Entry `./Routes` (Dùng nguyên màn hình)**:
  - Bản thân remote entry `./Routes` đã xuất mảng Routes được bọc sẵn `createRemoteRouteScope()` (bao gồm API services, child i18n và resolver).
  - **CẤM TUYỆT ĐỐI**: Tuyệt đối **KHÔNG bọc thêm** `provideRemote()`, `createRemoteRouteScope()`, hoặc `provideWII18n()` ở `app.routes.ts` của Host khi đã tải `./Routes`. Việc bọc lặp sẽ tạo 2 scope trùng nhau, ghi đè token translation và làm nhân đôi API services.
- **Entry `./Providers` (Component lẻ / trang host tự xây)**:
  - Chỉ dùng khi host tự code component và cần mượn API services/child translation của remote qua `createRemoteRouteScope()`.

### 1.3. Cấp Đủ 4 Context Nghiệp Vụ Tại Injector Cha (Parent/Root Injector)
Context thuộc sở hữu của Host Shell (quản lý session/login/tenant) và **PHẢI** được cấp ở Injector cha (Root Shell hoặc Shell Layout Injector) trước khi router kích hoạt remote:
1. `WI_SHOP_CONTEXT`:
   - Contract: `current`, `changes$`.
   - Kiểu dữ liệu: `WIShopIdentity` gồm `shopId: number` (số nguyên hợp lệ, không ép từ UUID) và `tenantId: string`.
2. `WI_BUSINESS_CONTEXT`:
   - Contract: `hasActiveShop`, `isLocked`, `isOwner`, `data$`.
   - Dữ liệu: Chứa `currentShop`, `isHeadOffice` lấy từ API/store thật. Không deduplicate chỉ theo ID (nội dung đổi vẫn phải phát).
3. `WI_USER_CONTEXT`:
   - Contract: `currentUser`, `user$`, `shopUserList$`.
   - Getter `currentUser` và observable `user$` phải đọc cùng store có replay (`BehaviorSubject`).
   - `shopUserList$` phân biệt rõ `null` (chưa tải/lỗi) với `[]` (danh sách rỗng hợp lệ). Nghiêm cấm gán `shopUserList$: of(null)` cố định hoặc dùng static `of(getUser())` mất tính reactive.
   - Phân biệt rõ `ShopUserDto.id` (ID nhân viên) và `ShopUserDto.userId` (ID tài khoản).
4. `WI_PERMISSION_CONTEXT`:
   - Contract: `check`, `checkAny`, `checkAll`, `permissions$`.
   - Ánh xạ quyền thực từ permission store của host. Nghiêm cấm dùng mock allow-all `['*']`.

### 1.4. Chuẩn Hóa Manifest & Gateway URL
- Chuẩn hóa key cấu hình trong manifest sang `gatewayUrl` theo đúng schema `WIMfManifest` (thay vì dùng `apiBaseUrl`).
- Đăng ký `setManifest(manifest)` và `setManifestStore(manifest, remoteUrls)` đầy đủ trước khi bootstrap/tải remote.

---

## 2. Phân Rã Checklist Nhiệm Vụ Cho Đội Ngũ (Work Breakdown)

### 📌 Peer Dev 1 (Routing & Manifest Hardening)
- [ ] Cập nhật `apps/app-shell/public/assets/manifest/development/module-federation.manifest.json`:
  - Thay key `apiBaseUrl` ➔ `gatewayUrl`.
  - Nâng remote `setting` từ `ver261008-2` ➔ `ver261019-3` (hoặc bản mới nhất đạt chuẩn).
- [ ] Rà soát `apps/app-shell/src/app/app.routes.ts`:
  - Dọn dẹp việc bọc thừa `provideWII18n` và duplicate providers tại nhánh route tải `./Routes` của remote `setting`.

### 📌 Peer Dev 2 (Context Providers Architecture & Reactive Store)
- [ ] Refactor `apps/app-shell/src/app/pages/setting/provider/context.provider.ts`:
  - Bổ sung đủ 4 token: `WI_SHOP_CONTEXT`, `WI_BUSINESS_CONTEXT`, `WI_USER_CONTEXT`, `WI_PERMISSION_CONTEXT`.
  - Thay thế `of(getUser())` và `of(null)` bằng `BehaviorSubject` kết nối với `AccountStore` và session thật của host.
  - Chuyển việc đăng ký 4 context lên injector cha (Root/Layout) để toàn bộ remote MFEs đều dùng chung.

### 📌 Peer Dev 3 (HTTP Interceptor & Session Lifecycle)
- [ ] Đồng bộ hóa header `shopId`, tenant ID trong HTTP Interceptor với dữ liệu từ `WI_SHOP_CONTEXT`.
- [ ] Xử lý vòng đời chuyển đổi shop: Khi đổi shop/tenant hoặc logout, lập tức hủy request đang chạy (via `switchMap`), reset store và phát dữ liệu mới.

### 📌 QC (Quality Gate & ISTQB 5-Stage Test Suite)
- [ ] Thiết kế ma trận kiểm thử 6 ca tích hợp cốt lõi:
  1. **Late Subscriber Test**: Subscriber vào sau vẫn nhận được giá trị mới nhất của User & Shop qua ReplaySubject/BehaviorSubject.
  2. **Route Scope Isolation**: Xác nhận `./Routes` tự resolve i18n và API service mà không bị NullInjectorError.
  3. **Race Condition Switch Shop**: Đổi shop A ➔ B khi request A đang bay, xác nhận dữ liệu của B không bị A đè.
  4. **Direct F5 Navigation**: Truy cập trực tiếp URL remote, xác nhận context được khôi phục chuẩn xác.
  5. **Logout Cleanup**: Đăng xuất cùng tab xóa sạch toàn bộ 4 context ngay lập tức.
  6. **Error Resiliency**: Khi một API phụ bị lỗi, stream context không bị terminate vĩnh viễn và cho phép retry.
