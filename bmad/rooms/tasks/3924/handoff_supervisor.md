# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Supervisor ➔ Peer

- **Thời gian**: `2026-10-21 16:18:28`
- **Work Item**: `#3924`
- **Agent bàn giao (From)**: `Supervisor`
- **Agent tiếp nhận (To)**: `Peer`
- **Nội dung tóm tắt**: Work Item #3924 [Task]: [AppShell/Sidebar] - Thêm menu wion-customer và từ điển i18n shell
1. Target Files: apps/app-shell/src/app/layouts/sidebar/sidebar.mock.ts, apps/app-shell/public/assets/i18n/vi/shell.json, apps/app-shell/public/assets/i18n/en/shell.json. 2. Anchors/Lines: Nhóm management trong sidebar.mock.ts; SHELL.SIDEBAR.MANAGEMENT trong 2 file shell.json. 3. Concrete Changes: Thêm menu item wion-customer (icon tdsi-user-list-fill, routerLink ['customer']); thêm key WION_CUSTOMER vào vi ('Khách hàng WiOnPOS') và en ('WiOnPOS Customer'). 4. AC: Menu hiển thị icon tdsi-user-list-fill chuẩn TDS UI, sidebar.component.spec.ts pass 100%. 5. Test: npx nx test app-shell --testFile=sidebar.component.spec.ts.

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > Work Item #3924 [Task]: [AppShell/Sidebar] - Thêm menu wion-customer và từ điển i18n shell
1. Target Files: apps/app-shell/src/app/layouts/sidebar/sidebar.mock.ts, apps/app-shell/public/assets/i18n/vi/shell.json, apps/app-shell/public/assets/i18n/en/shell.json. 2. Anchors/Lines: Nhóm management trong sidebar.mock.ts; SHELL.SIDEBAR.MANAGEMENT trong 2 file shell.json. 3. Concrete Changes: Thêm menu item wion-customer (icon tdsi-user-list-fill, routerLink ['customer']); thêm key WION_CUSTOMER vào vi ('Khách hàng WiOnPOS') và en ('WiOnPOS Customer'). 4. AC: Menu hiển thị icon tdsi-user-list-fill chuẩn TDS UI, sidebar.component.spec.ts pass 100%. 5. Test: npx nx test app-shell --testFile=sidebar.component.spec.ts.

2. **Ràng buộc cứng (Hard Constraints)**:
   > Tuân thủ TDS UI tokens, Angular 18 Standalone, không nạp thêm lib thừa (YAGNI), bảo đảm single-ownership.

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > Xem mã nguồn liên quan trong bmad/modules/ và bmad/flows/.


---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/peer/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
