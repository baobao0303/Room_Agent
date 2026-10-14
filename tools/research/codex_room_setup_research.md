# Technical Research: `hoangnb24/codex-room-setup` Architecture & Multi-Agent Room Protocols

> **Target**: GitHub Repository `hoangnb24/codex-room-setup`
> **Ecosystem Alignment**: Paseo Multi-Agent Room & Codex Autonomous Orchestration

---

## 1. Bản chất & Mục tiêu cốt lõi (Core Objective)
`codex-room-setup` là bộ khung chuẩn hóa (Standard Operating Framework & Room Protocol) dùng để cấu hình và vận hành phòng làm việc cộng tác đa Agent (**Multi-Agent Room**) cho các engine AI Agent (Codex, Claude Code, Paseo).

Repo này định nghĩa các nguyên tắc cộng tác khép kín giữa các vai trò kỹ thuật chuyên biệt (Department Roles), ngăn chặn tình trạng Agent làm việc chồng chéo, xung đột quyền ghi (write scope) hoặc code khi chưa có nghiệm thu thiết kế/nghiệp vụ.

---

## 2. Kiến trúc Phân tầng & Phân quyền Vai trò (Room Topology)

Hệ thống phân chia thành 3 nhóm tác nhân chính:

```text
                           ┌──────────────────────────┐
                           │      HUMAN (OWNER)       │ (Mục tiêu, Chi phí, Rủi ro)
                           └─────────────┬────────────┘
                                         │
                           ┌─────────────▼────────────┐
                           │        SUPERVISOR        │ (Giám sát luồng & Kanban)
                           └─────────────┬────────────┘
                                         │
       ┌─────────────────────────────────┼─────────────────────────────────┐
       ▼                                 ▼                                 ▼
┌──────────────┐                  ┌──────────────┐                  ┌──────────────┐
│   LEAD BA    │                  │ LEAD DESIGN  │                  │   LEAD DEV   │
└──────┬───────┘                  └──────┬───────┘                  └──────┬───────┘
       │                                 │                                 │
┌──────▼───────┐                  ┌──────▼───────┐                  ┌──────▼───────┐
│   PEER BA    │                  │ PEER DESIGN  │                  │   PEER DEV   │
└──────────────┘                  └──────────────┘                  └──────────────┘
```

### A. Tầng Lãnh đạo (Lead Roles)
- **Lead BA**: Sở hữu phạm vi phân tích nghiệp vụ, tạo User Stories, Use Cases và Acceptance Criteria (AC).
- **Lead Design**: Sở hữu giao diện UI/UX, Design Tokens, wireframes, và mapping components (Figma sang TDS-UI).
- **Lead Dev**: Sở hữu kiến trúc hệ thống, API contracts, schema database, phân rã task và phê duyệt kỹ thuật trước khi merge.

### B. Tầng Thực thi (Peer Roles)
- **Peer BA / Peer Design / Peer Dev**: Nhận đúng **1 nhiệm vụ độc lập (bounded outcome)** từ Lead tương ứng.
- **Quy tắc Bounded Scope**: Mỗi Peer chỉ có quyền ghi trên phạm vi được giao (`moving write scope`), không sửa code hoặc tài liệu của department khác.

### C. Tầng Giám sát (Supervisor)
- Quan sát luồng làm việc giữa các Lead.
- Can thiệp nếu Dev bắt đầu viết code khi chưa có AC từ BA hoặc mockup từ Design.
- Theo dõi tiến độ qua sự kiện Kanban và Cron jobs, không spam hỏi trạng thái.

---

## 3. Giao thức Làm việc & Chuỗi Bàn giao (Handoff Sequence)

Chuỗi bàn giao bắt buộc: **BA ➔ DESIGN ➔ DEV**:
1. **Bước 1 (BA)**: Lead BA định nghĩa User Stories kèm Acceptance Criteria (AC) tại `docs/spec/<project>/ba/`.
2. **Bước 2 (DESIGN)**: Lead Design thiết kế component, ánh xạ token màu/typography tại `docs/spec/<project>/design/` dựa trên AC của BA.
3. **Bước 3 (DEV)**: Lead Dev nhận đầu vào đã được nghiệm thu (BA + Design) để tạo Technical Story / Tasks và giao cho Peer Dev lập trình tại `projects/<project>/`.

---

## 4. Cơ chế Độc lập & Phản hồi (Independent Peer Judgment)
Khi một Peer gặp trở ngại, không được tự ý sửa phạm vi mà phải gửi tín hiệu chuẩn:
- **`REOPEN_REQUEST`**: Khi tiền đề bài toán hoặc yêu cầu đầu vào bị sai.
- **`DEPENDENCY_REQUEST`**: Khi thiếu tài nguyên tiên quyết từ department khác.
- **`BLOCKED`**: Khi gặp lỗi kỹ thuật hoặc rủi ro không thể tiếp tục an toàn.

---

## 5. Ánh xạ vào Workspace `Paseo_Project`

Bộ cấu hình trong `codex-room-setup` đã được tích hợp đầy đủ vào hệ sinh thái Paseo hiện tại:
1. **`~/.paseo/config.json`**: Đã load sẵn toàn bộ 9 Profiles (`Lead BA`, `Lead Design`, `Lead Dev`, `Peer BA`, `Peer Design`, `Peer Dev`, `Lead`, `Peer`, `Supervisor`).
2. **`AGENTS.md`**: Đã đồng bộ quy chuẩn phân vai, handoff pipeline (BA -> DESIGN -> DEV) và cơ chế gọi tools (`harness_manager`, `query_reader`, `tds-ui-figma`, `tds-ui-usage`).
3. **`docs/spec/`**: Đã cấu trúc chuẩn theo 3 thư mục `ba/`, `design/`, `dev/` cho từng dự án.
