# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Supervisor ➔ Lead

- **Thời gian**: `2026-10-21 15:56:47`
- **Work Item**: `#3913`
- **Agent bàn giao (From)**: `Supervisor`
- **Agent tiếp nhận (To)**: `Lead`
- **Nội dung tóm tắt**: Work Item #3913 [Epic]: [WiOnPOS] - Tích hợp lại trang Customer và Menu Sidebar vào App Shell
1. Target Files: 4 manifests apps/app-shell/public/assets/manifest/*/module-federation.manifest.json, apps/app-shell/src/app/app.routes.ts, app.routes.spec.ts, apps/app-shell/src/app/layouts/sidebar/sidebar.mock.ts, apps/app-shell/public/assets/i18n/{vi,en}/shell.json. 2. Anchors/Lines: Thêm remote customer (ver261019-3, lazy: true, config assetsBaseUrl & i18n CUSTOMER/TAGS/PRODUCT, default CRM nguyên bản không gatewayUrl); Route customer nạp loadRemoteMfeRoutes('customer', './Routes') kèm provideWiRemoteContexts(); Sidebar nhóm management item wion-customer (icon tdsi-user-list-fill, routerLink ['customer']); I18n key WION_CUSTOMER. 3. Concrete Changes: Khôi phục cấu hình tích hợp WiOnPOS Customer vào App Shell. 4. AC: 4 manifests valid JSON, route customer kèm context, sidebar chuẩn icon tdsi-user-list-fill, pass 100% test suites app-shell. 5. Test: npx nx test app-shell.

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > Work Item #3913 [Epic]: [WiOnPOS] - Tích hợp lại trang Customer và Menu Sidebar vào App Shell
1. Target Files: 4 manifests apps/app-shell/public/assets/manifest/*/module-federation.manifest.json, apps/app-shell/src/app/app.routes.ts, app.routes.spec.ts, apps/app-shell/src/app/layouts/sidebar/sidebar.mock.ts, apps/app-shell/public/assets/i18n/{vi,en}/shell.json. 2. Anchors/Lines: Thêm remote customer (ver261019-3, lazy: true, config assetsBaseUrl & i18n CUSTOMER/TAGS/PRODUCT, default CRM nguyên bản không gatewayUrl); Route customer nạp loadRemoteMfeRoutes('customer', './Routes') kèm provideWiRemoteContexts(); Sidebar nhóm management item wion-customer (icon tdsi-user-list-fill, routerLink ['customer']); I18n key WION_CUSTOMER. 3. Concrete Changes: Khôi phục cấu hình tích hợp WiOnPOS Customer vào App Shell. 4. AC: 4 manifests valid JSON, route customer kèm context, sidebar chuẩn icon tdsi-user-list-fill, pass 100% test suites app-shell. 5. Test: npx nx test app-shell.

2. **Ràng buộc cứng (Hard Constraints)**:
   > Tuân thủ TDS UI tokens, Angular 18 Standalone, không nạp thêm lib thừa (YAGNI), bảo đảm single-ownership.

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > Xem mã nguồn liên quan trong bmad/modules/ và bmad/flows/.


---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/lead/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
