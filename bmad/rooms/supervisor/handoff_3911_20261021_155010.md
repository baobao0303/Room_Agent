# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Supervisor ➔ Lead

- **Thời gian**: `2026-10-21 15:50:10`
- **Work Item**: `#3911`
- **Agent bàn giao (From)**: `Supervisor`
- **Agent tiếp nhận (To)**: `Lead`
- **Nội dung tóm tắt**: Work Item #3911 [Epic]: [AppShell] - Tích hợp shopUserList$ vào WI_USER_CONTEXT từ MemberService
1. Target Files: apps/app-shell/src/app/pages/setting/provider/context.provider.ts và context.provider.spec.ts. 2. Anchors/Lines: Dòng 104-111 tại context.provider.ts trong provide WI_USER_CONTEXT. 3. Concrete Changes: Thay thế mock of({shopUsers: [], totalUser: 1}) bằng stream gọi MemberService.v1TenantsTenantIdShopsShopIdMembersListPost, ánh xạ qua mapEmployeeListToShopUsers (id=shopUserId, userId=accountUserId, role, isActive, totalUser từ backend), gắn shareReplay và catchError fallback. 4. AC: AC-SUL-01..05 trong docs/spec/shop-user-list-context-spec.md. 5. Test: npx nx test app-shell --testFile=context.provider.spec.ts. Tuân thủ nghiêm ngặt quy trình phản biện Peer-Lead Review Loop.

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > Work Item #3911 [Epic]: [AppShell] - Tích hợp shopUserList$ vào WI_USER_CONTEXT từ MemberService
1. Target Files: apps/app-shell/src/app/pages/setting/provider/context.provider.ts và context.provider.spec.ts. 2. Anchors/Lines: Dòng 104-111 tại context.provider.ts trong provide WI_USER_CONTEXT. 3. Concrete Changes: Thay thế mock of({shopUsers: [], totalUser: 1}) bằng stream gọi MemberService.v1TenantsTenantIdShopsShopIdMembersListPost, ánh xạ qua mapEmployeeListToShopUsers (id=shopUserId, userId=accountUserId, role, isActive, totalUser từ backend), gắn shareReplay và catchError fallback. 4. AC: AC-SUL-01..05 trong docs/spec/shop-user-list-context-spec.md. 5. Test: npx nx test app-shell --testFile=context.provider.spec.ts. Tuân thủ nghiêm ngặt quy trình phản biện Peer-Lead Review Loop.

2. **Ràng buộc cứng (Hard Constraints)**:
   > Tuân thủ TDS UI tokens, Angular 18 Standalone, không nạp thêm lib thừa (YAGNI), bảo đảm single-ownership.

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > Xem mã nguồn liên quan trong bmad/modules/ và bmad/flows/.


---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/lead/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
