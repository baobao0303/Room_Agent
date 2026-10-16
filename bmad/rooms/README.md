# Phòng Bàn Giao Context Giữa Các Agent (BMAD Agent Handoff Rooms)

Thư mục lưu trữ biên bản bàn giao (Handoff Records) và ảnh chụp ngữ cảnh (Context Snapshots) giữa các Agent trong hệ thống SLPC (Supervisor, Lead, Peer, QC).

Mỗi phòng đại diện cho một vai trò chuyên trách, lưu vết lại trạng thái công việc mỗi khi chuyển giao task trên Harness DB (Floci).

---

## 1. Cấu Trúc Các Phòng
```text
bmad/rooms/
├── README.md               # Quy chế bàn giao context & lưu trữ
├── template-handoff.md     # Mẫu biên bản bàn giao chuẩn
├── supervisor/             # Phòng Supervisor: Phân rã scope, kiểm soát ranh giới, nghiệm thu bàn giao từ User
├── lead/                   # Phòng Lead Dev: Thiết kế kiến trúc, phân chia subtask cho Peer Dev
├── peer/                   # Phòng Peer Dev: Nhật ký code, diff thay đổi, unit test tự chạy
└── qc/                     # Phòng QC: Biên bản nghiệm thu kiểm thử độc lập 5-Stage ISTQB
```

---

## 2. Quy Chuẩn Đặt Tên Biên Bản
Mỗi biên bản bàn giao được lưu dưới dạng:
`handoff_<item_id>_<role>_<timestamp>.md`

Ví dụ:
- `bmad/rooms/peer/handoff_5081_peer_dev_20261016_1645.md`
- `bmad/rooms/lead/handoff_5080_lead_dev_20261016_1630.md`

---

## 3. Tự Động Hóa Với Paseo Tools
Khi Agent hoàn thành lượt làm việc và gọi lệnh:
```bash
python3 tools/agent_progress.py log --agent "Peer Dev" ...
```
Hệ thống sẽ lưu vết vào Sổ cái trung tâm đồng thời ghi lại biên bản bàn giao tại phòng tương ứng để Agent kế tiếp (`paseo run` hoặc phiên chat mới) có thể nạp thẳng context mà không cần hỏi lại từ đầu.
