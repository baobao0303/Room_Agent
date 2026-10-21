# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Supervisor ➔ Peer

- **Thời gian**: `2026-10-21 16:17:33`
- **Work Item**: `#3923`
- **Agent bàn giao (From)**: `Supervisor`
- **Agent tiếp nhận (To)**: `Peer`
- **Nội dung tóm tắt**: Work Item #3923 [Task]: [AppShell/Routes] - Khai báo route customer nạp remote WiOnPOS kèm contexts
1. Target Files: apps/app-shell/src/app/app.routes.ts và apps/app-shell/src/app/app.routes.spec.ts. 2. Anchors/Lines: Dưới nhánh con ':id', thêm route 'customer'. 3. Concrete Changes: Nạp loadRemoteMfeRoutes('customer', './Routes') kèm provideWiRemoteContexts(), title 'CUSTOMER.TITLE'. 4. AC: Route customer nạp remote hợp lệ, app.routes.spec.ts pass 100%. 5. Test: npx nx test app-shell --testFile=app.routes.spec.ts.

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > Work Item #3923 [Task]: [AppShell/Routes] - Khai báo route customer nạp remote WiOnPOS kèm contexts
1. Target Files: apps/app-shell/src/app/app.routes.ts và apps/app-shell/src/app/app.routes.spec.ts. 2. Anchors/Lines: Dưới nhánh con ':id', thêm route 'customer'. 3. Concrete Changes: Nạp loadRemoteMfeRoutes('customer', './Routes') kèm provideWiRemoteContexts(), title 'CUSTOMER.TITLE'. 4. AC: Route customer nạp remote hợp lệ, app.routes.spec.ts pass 100%. 5. Test: npx nx test app-shell --testFile=app.routes.spec.ts.

2. **Ràng buộc cứng (Hard Constraints)**:
   > Tuân thủ TDS UI tokens, Angular 18 Standalone, không nạp thêm lib thừa (YAGNI), bảo đảm single-ownership.

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > Xem mã nguồn liên quan trong bmad/modules/ và bmad/flows/.


---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/peer/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
