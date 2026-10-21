# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev

- **Thời gian**: `2026-10-21 13:26:01`
- **Work Item**: `#3824`
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev`
- **Nội dung tóm tắt**: Thi công Task #3824: Gỡ bỏ hoàn toàn tính năng Skills Hub và tab skills khỏi Aevum workspace.

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > Gỡ bỏ hoàn toàn tính năng Skills Hub và tab skills khỏi Aevum workspace theo 4 hạng mục của Task #3824.

2. **Ràng buộc cứng (Hard Constraints)**:
   > Single-Ownership 4 file chỉ định, không phá vỡ Kanban, dọn sạch dead code, format bằng oxfmt.

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > 1. kanban/index.tsx về thuần Kanban. 2. workbench-router.ts gỡ route /skills. 3. root-app-sidebar gỡ AppSidebarSkillsButton và xóa skills-button.tsx. 4. auth controller gỡ các endpoint /open-app/skills.


---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/peer/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
