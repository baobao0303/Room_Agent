# BẢN ĐẶC TẢ KIẾN TRÚC: TỐI ƯU HÓA HỆ THỐNG BMAD ROOMS & EPHEMERAL STATE LEDGER
## Mã định danh: ARCH-SPEC-BMAD-ROOMS-OPTIMIZATION-2026-V1
## Tham chiếu: SLPPC Multi-Agent Architecture | Kev System One (<50ms) | Issue #4 & Issue #5

---

## 1. BẢNG THẨM ĐỊNH KEV SYSTEM ONE & QUYẾT NGHỊ PM AGENT

- **Cơ quan thẩm định**: PM Agent phối hợp Kev System One (`http://100.124.36.46:8008/v1/systemone`, Model `kev-latest`).
- **Thời gian thẩm định**: 2026-10-23.
- **Trạng thái**: **APPROVED / READY FOR ZERO-SEARCH DISPATCH**.

| Chỉ số / Tiêu chí | Điểm số Kev | Đánh giá PM Agent |
| :--- | :---: | :--- |
| **Feasibility (Tính khả thi)** | **2.9 / 3.0** | Rất cao. Chỉ sử dụng Python standard library (`json`, `pathlib`, `shutil`), không cài thêm bất kỳ dependency nào. |
| **Architectural Alignment** | **1.00 (100%)** | Hoàn toàn phù hợp nguyên lý *"Ephemeral by Default, Persistent by Exception"* của SLPPC. |
| **Risk Lane** | **GREEN** | Không gây rủi ro logic, chỉ chuẩn hóa tầng giao tiếp biên bản trung gian. |
| **Structured State Confidence** | **0.933** | Kev khuyến nghị mạnh mẽ gom trạng thái về JSON cấu trúc thay vì sinh file markdown rải rác. |
| **Archive On Closed Confidence** | **0.784** | Tự động dọn dẹp artifacts khi QC nghiệm thu `Closed` để đưa RAM/Disk overhead về 0. |
| **Zero-Leak Sanitization Confidence** | **0.762** | Tự động lọc sạch đường dẫn tuyệt đối và secret trong biên bản bàn giao. |

---

## 2. HIỆN TRẠNG & NGUYÊN NHÂN GỐC RỄ (ROOT CAUSE)

1. **Bùng nổ file rác (File Proliferation)**:
   - Hệ thống cũ tại `tools/agent_progress.py` mỗi lần log tiến độ lại sinh ra một file mới theo định dạng:
     `bmad/rooms/<role>/handoff_YYYYMMDD_HHMMSS.md`
   - Chỉ qua vài phiên làm việc, thư mục `bmad/rooms/` tích lũy hàng chục file mồ côi, gây chậm trễ khi duyệt thư mục và khó theo dõi tiến độ thực tế.
2. **Ô nhiễm Context Window (Context Pollution)**:
   - Khi một Agent mới khởi động và đọc thư mục `bmad/rooms/`, nó dễ bị nạp toàn bộ các file handoff cũ không còn giá trị, tiêu tốn 10.000–30.000 tokens vô ích.
3. **Nguy cơ rò rỉ dữ liệu (Anti-Leak Hazard)**:
   - Các file handoff tự do thường sao chép cả đường dẫn tuyệt đối của máy cá nhân (`/home/...`, `/Users/...`) hoặc các đoạn mã nguồn lớn, làm tăng nguy cơ vi phạm bảo mật.

---

## 3. MÔ HÌNH KIẾN TRÚC MỤC TIÊU: 3 TẦNG EPHEMERAL STATE

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BMAD ROOMS EPHEMERAL STATE ARCHITECTURE                  │
│                                                                             │
│  TẦNG 1: SINGLE-POINTER IN-PLACE MEMOS (Mỗi vai trò chỉ 1 file duy nhất)    │
│  ├── bmad/rooms/supervisor/latest_handoff.md (Ghi đè in-place)              │
│  ├── bmad/rooms/pm/latest_handoff.md         (Ghi đè in-place)              │
│  ├── bmad/rooms/lead/latest_handoff.md       (Ghi đè in-place)              │
│  ├── bmad/rooms/peer/latest_handoff.md       (Ghi đè in-place)              │
│  └── bmad/rooms/qc/latest_handoff.md         (Ghi đè in-place)              │
│                                                                             │
│  TẦNG 2: STRUCTURED ROOM LEDGER (Sổ cái JSON tập trung, Rolling FIFO 50)    │
│  └── bmad/rooms/room_ledger.json                                            │
│      ├── active_handoffs: Con trỏ trạng thái hiện tại của từng role         │
│      └── history: Mảng 50 log gần nhất (Tự động xoay vòng FIFO)            │
│                                                                             │
│  TẦNG 3: TASK-SCOPED ISOLATION & AUTO-ARCHIVE TRÊN QC GATE                  │
│  ├── Khi task ĐANG CHẠY: Artifacts lưu tại bmad/rooms/tasks/<task_id>/      │
│  └── Khi task CLOSED   : QC Gate tự động nén/dọn vào bmad/rooms/archive/   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Chi tiết 3 Tầng:

### 3.1. Tầng 1: Single-Pointer In-Place Memos
- Mỗi thư mục vai trò (`supervisor/`, `pm/`, `lead/`, `peer/`, `qc/`) chỉ duy trì duy nhất một file:
  `bmad/rooms/<role>/latest_handoff.md`
- **Nguyên tắc ghi**: Thực hiện ghi đè nguyên tử (atomic overwrite). Nghiêm cấm sinh file có hậu tố timestamp (`handoff_YYYYMMDD_HHMMSS.md`).
- **Nội dung giới hạn**: File markdown tối đa 150 dòng, tập trung vào:
  - Task ID đang xử lý.
  - Tóm tắt quyết định và kết quả.
  - Danh sách file can thiệp (relative paths).
  - Trạng thái kiểm thử (Exit code 0, kết quả test).

### 3.2. Tầng 2: Structured Room Ledger (`bmad/rooms/room_ledger.json`)
- Thay thế việc lưu trữ phân tán bằng 1 file JSON chuẩn hóa duy nhất tại `bmad/rooms/room_ledger.json`.
- **Cấu trúc JSON Schema**:
  ```json
  {
    "version": "1.0.0",
    "updated_at": "2026-10-23T22:45:00Z",
    "roles": {
      "supervisor": {
        "status": "IDLE",
        "last_action": "Phân rã task",
        "active_task_id": "WI-002",
        "updated_at": "2026-10-23T22:45:00Z"
      },
      "pm": {
        "status": "IDLE",
        "feasibility_score": 2.9,
        "alignment": "perfect_fit",
        "active_task_id": "WI-002",
        "updated_at": "2026-10-23T22:45:00Z"
      }
    },
    "history": [
      {
        "timestamp": "2026-10-23T22:45:00Z",
        "agent": "Supervisor",
        "action": "log",
        "task_id": "WI-002",
        "summary": "Tối ưu hóa bmad/rooms"
      }
    ]
  }
  ```
- **Chính sách tự động nén (FIFO Rolling Policy)**:
  - Mảng `history` giới hạn tối đa **50 bản ghi gần nhất**.
  - Khi bản ghi thứ 51 được thêm vào, tự động loại bỏ bản ghi cũ nhất (FIFO).
  - Đảm bảo dung lượng file luôn dưới **50 KB**, nạp siêu nhanh, không tốn RAM.

### 3.3. Tầng 3: Task-Scoped Isolation & Auto-Archive
- Các file tài liệu tạm của task đang active được cô lập tại:
  `bmad/rooms/tasks/<task_id>/`
- Khi vai trò QC xác nhận nghiệm thu và chuyển trạng thái task sang `Closed`:
  - Công cụ `tools/room_cleanup.py` được gọi tự động.
  - Toàn bộ thư mục `bmad/rooms/tasks/<task_id>/` được đóng gói thành file zip/tar lưu vào `bmad/rooms/archive/<task_id>.tar.gz` (hoặc dọn sạch nếu là task kiểm thử).
  - Không để lại bất kỳ file rác nào trong không gian làm việc.

---

## 4. KẾ HOẠCH TRIỂN KHAI 4 BƯỚC (ZERO-SEARCH TASK DECOMPOSITION)

### Bước 1: Chuẩn hóa `tools/agent_progress.py`
- Sửa hàm `log_progress()`:
  - Bỏ hoàn toàn logic tạo file `handoff_{timestamp}.md`.
  - Ghi thẳng in-place vào `bmad/rooms/<role_folder>/latest_handoff.md`.
  - Cập nhật đồng bộ vào `bmad/rooms/room_ledger.json` (áp dụng chính sách FIFO 50).
  - Tự động áp dụng Anti-Leak regex (thay thế path máy tính bằng relative path).

### Bước 2: Nâng cấp công cụ dọn dẹp `tools/room_cleanup.py`
- Bổ sung lệnh CLI:
  ```bash
  python3 tools/room_cleanup.py --migrate-legacy
  ```
  - Quét và xóa toàn bộ các file `handoff_*.md` cũ có timestamp trong `bmad/rooms/supervisor/` và các phòng ban khác.
  - Khởi tạo file `bmad/rooms/room_ledger.json` chuẩn hóa.

### Bước 3: Tích hợp vào QC Gate (`tools/slppc_flow_guard.py` & `.rtk/pipelines/30-qc-tail-gate.toml`)
- Bổ sung rule kiểm tra:
  - Thư mục `bmad/rooms/` không được chứa bất kỳ file `handoff_*.md` cũ nào.
  - Mỗi phòng ban chỉ có tối đa 1 file `latest_handoff.md`.
  - File `room_ledger.json` hợp lệ schema và dung lượng $< 50$ KB.

### Bước 4: Kiểm thử toàn diện ISTQB 5-Stage
- Chạy unit tests và Flow Guard audit để xác nhận 100% tuân thủ quy chuẩn mới.

---

## 5. TIÊU CHUẨN NGHIỆM THU (ACCEPTANCE CRITERIA)

- [ ] **AC-1**: Lệnh `find bmad/rooms -name "handoff_*.md"` trả về đúng **0 file**.
- [ ] **AC-2**: Mỗi phòng ban trong `bmad/rooms/{supervisor,pm,lead,peer,qc}` chỉ có file `latest_handoff.md`.
- [ ] **AC-3**: `bmad/rooms/room_ledger.json` tồn tại, lưu cấu trúc trạng thái hiện hành của các vai trò, dung lượng $< 50$ KB.
- [ ] **AC-4**: Khi chạy lệnh `python3 tools/agent_progress.py log ...`, không sinh thêm file mới, chỉ cập nhật `latest_handoff.md` và `room_ledger.json`.
- [ ] **AC-5**: 26 unit tests của bộ công cụ và `python3 tools/slppc_flow_guard.py audit` đạt PASS 100%.
