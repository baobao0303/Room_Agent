# BMAD Central Brain (Paseo SLPC Knowledge & Architecture Graph)

Nơi lưu trữ "bộ não" kiến trúc, nghiệp vụ và phòng họp bàn giao giữa các Agent SLPC (Supervisor, Lead, Peer, QC).

Tích hợp với [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) để trực quan hóa đồ thị tri thức (Knowledge Graph) tương tác, định hướng luồng thực thi mà không gây tràn Context Window.

---

## 1. Cấu Trúc Bộ Não BMAD
```text
bmad/
├── architecture.json             # Đồ thị quan hệ kiến trúc hệ thống (Nodes & Edges)
├── slpc-4-agent-handoff-spec.md  # ĐẶC TẢ ĐIỀU PHỐI 4 AGENT SLPC QUA BMAD ROOMS
├── modules/                      # Tóm tắt vai trò, API & công nghệ từng phân hệ
│   ├── app-shell.md              # Host Shell (Layout, Auth Guard, Menu, Remote Loader)
│   ├── mfe-cdp.md                # Micro-Frontend CDP (Khách hàng, Customer 360, Raw Event)
│   ├── harness-ui.md             # Harness SLPC Live Dashboard (:8765, Astro + Bàn cờ Caro)
│   └── tds-ui.md                 # Thư viện Design System (Components, Tokens, Grid)
├── flows/                        # Luồng dữ liệu & tương tác người dùng
│   └── customer-360-flow.md      # Luồng điều hướng click mở /customers/:id
└── rooms/                        # PHÒNG BÀN GIAO CONTEXT GIỮA CÁC AGENT
    ├── README.md                 # Quy chế bàn giao context & lưu trữ
    ├── template-handoff.md       # Biểu mẫu biên bản bàn giao chuẩn
    ├── supervisor/               # Phòng Supervisor: Phân rã scope, kiểm soát ranh giới
    ├── lead/                     # Phòng Lead Dev: Thiết kế kiến trúc, phân công subtask
    ├── peer/                     # Phòng Peer Dev: Code diff, file đã sửa, tự test
    └── qc/                       # Phòng QC: Nghiệm thu kiểm thử độc lập 5-Stage ISTQB
```

---

## 2. Quy Trình Luân Chuyển 4 Agent
Chi tiết xem tại tài liệu đặc tả: [`bmad/slpc-4-agent-handoff-spec.md`](slpc-4-agent-handoff-spec.md).

- **User ➔ Supervisor**: Tra cứu ngữ cảnh, phân tích scope, tạo Work Item trên Harness DB, xuất bản giao vào `bmad/rooms/supervisor/`.
- **Supervisor ➔ Lead Dev**: Nhận bàn giao, thiết kế giải pháp kỹ thuật, phân bổ task cho Peer Dev qua `bmad/rooms/lead/`.
- **Lead Dev ➔ Peer Dev**: Viết code tối giản (YAGNI), tự chạy test, cập nhật diff vào `bmad/rooms/peer/`.
- **Peer Dev ➔ QC**: Sinh 5-Stage ISTQB test, nghiệm thu độc lập, đóng task qua `bmad/rooms/qc/`.
- **QC ➔ Supervisor ➔ User**: Báo cáo kết quả cuối cùng cho User.
