# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev

- **Thời gian**: `2026-10-21 13:14:59`
- **Work Item**: `#3814`
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev`
- **Nội dung tóm tắt**: Thi công Task #3814: Refactor index.tsx auto-redirect and remove video timeout theo chuẩn SLPC.

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > Sửa packages/frontend/core/src/desktop/pages/index/index.tsx trong projects/Aevum để tự động redirect vào workspace khi authenticated và bỏ timeout delay 600ms.

2. **Ràng buộc cứng (Hard Constraints)**:
   > projects/Aevum, không thêm dependency mới, tuân thủ kiến trúc hiện có, format code bằng oxfmt, không tự ý sửa các file ngoài scope.

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > Khôi phục useNavigateHelper, RouteLogic trong index.tsx. Tại useLayoutEffect gọi openPage(openWorkspace.id, defaultIndexRoute, RouteLogic.REPLACE). Xóa useState/useEffect của videoReady 600ms và bỏ khối div chứa WorkspaceNavigator.


---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/peer/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
