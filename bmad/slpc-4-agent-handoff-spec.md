# ĐẶC TẢ HỆ THỐNG ĐIỀU PHỐI 4 AGENT SLPC QUA BMAD ROOMS
## (SLPC 4-AGENT HANDOFF & CONTEXT PROPAGATION SPECIFICATION)

- **Mã đặc tả**: `bmad/slpc-4-agent-handoff-spec.md`
- **Phiên bản**: 1.0.0
- **Mục tiêu**: Chuẩn hóa luồng trao đổi, lưu vết ngữ cảnh và bàn giao công việc giữa 4 Agent chuyên trách (Supervisor -> Lead -> Peer -> QC) thông qua kho lưu trữ trung tâm `bmad/rooms/`, đảm bảo không làm tràn Context Window và không mất mát thông tin.

---

## 1. NGUYÊN TẮC CỐT LÕI (CORE PRINCIPLES)

1. **Single Point of Contact (SPOC)**:
   - User **chỉ chat trực tiếp với Supervisor**.
   - Supervisor nhận lệnh, tra cứu dữ liệu, điều phối Lead, Peer, QC và báo cáo kết quả cuối cùng cho User.
2. **Zero Context Pollution (Chống tràn Context)**:
   - Không nạp lại toàn bộ mã nguồn thô (248.000 file) vào conversation.
   - Mỗi Agent chỉ đọc đúng **Biên bản bàn giao gần nhất (`latest_handoff.md`)** trong phòng của Agent tiền nhiệm để tiếp nối công việc.
3. **File-Based Communication (`bmad/rooms/`)**:
   - Mọi quyết định kỹ thuật, phân tích scope, diff code và kết quả test được ký thác thành văn bản tại thư mục `bmad/rooms/<role>/`.
4. **Harness State Synchronization**:
   - Mọi bước bàn giao phải gắn liền với sự thay đổi trạng thái của Work Item trên Harness DB (Floci Cloud): `New` -> `Accepted` -> `Active` -> `Resolved` -> `Closed`.

---

## 2. BẢN ĐỒ VAI TRÒ & PHÒNG LÀM VIỆC (ROLE & ROOM DIRECTORY)

```text
/home/baoltb/Desktop/Paseo_Project/bmad/rooms/
├── README.md               # Quy chế điều phối & hướng dẫn nạp context
├── template-handoff.md     # Biểu mẫu biên bản bàn giao chuẩn
│
├── supervisor/             # PHÒNG 1: SCOPE GUARD & RESEARCH
│   ├── latest_handoff.md   # Biên bản mới nhất Supervisor giao cho Lead
│   └── handoff_<id>_*.md   # Lịch sử phân rã yêu cầu
│
├── lead/                   # PHÒNG 2: TECHNICAL ARCHITECTURE & DELEGATION
│   ├── latest_handoff.md   # Biên bản mới nhất Lead giao cho Peer
│   └── handoff_<id>_*.md   # Lịch sử thiết kế & phân bổ subtask
│
├── peer/                   # PHÒNG 3: CODE IMPLEMENTATION & DIFF
│   ├── latest_handoff.md   # Biên bản mới nhất Peer bàn giao cho QC
│   └── handoff_<id>_*.md   # Lịch sử thay đổi code & tự test
│
└── qc/                     # PHÒNG 4: QUALITY GATE & VERIFICATION
    ├── latest_handoff.md   # Biên bản nghiệm thu kiểm thử 5-Stage ISTQB
    └── handoff_<id>_*.md   # Báo cáo pass/fail trả về Supervisor
```

---

## 3. QUY TRÌNH LUÂN CHUYỂN 5 BƯỚC (5-STAGE RELAY PIPELINE)

```text
[User Prompt] ──▶ (1. Supervisor) ──[Handoff #1]──▶ (2. Lead Dev)
                        │                                  │
                  [Harness Work Item]               [Technical Plan]
                        ▲                                  ▼
                        │                            [Handoff #2]
                        │                                  │
                 (5. User Report)                   (3. Peer Dev)
                        ▲                                  │
                        │                             [Code Diff]
                        │                                  ▼
                  [Handoff #4]                       [Handoff #3]
                        │                                  │
                 (4. QC Verifier) ◀────────────────────────┘
                 [ISTQB Testcases]
```

### Bước 1: User ➔ Supervisor (Scope Guard & Research Generation)
- **Nhiệm vụ**:
  - Nhận đề bài từ User, phân tích ý đồ (Intent) và ranh giới nghiệp vụ (Scope).
  - Sử dụng bộ công cụ Research: `query_reader.py`, `research_agent.py`, `crm_doc_reader.py`, Outline MCP, Figma MCP để tra cứu mã nguồn thực tế.
  - Tạo Work Item (User Story / Task / Bug) trên Harness DB qua `tools/harness_manager.py add`.
- **Generation Artifacts**:
  - Tóm tắt yêu cầu nghiệp vụ, Acceptance Criteria (AC dạng BDD).
- **Handoff Output**:
  - Ghi biên bản vào `bmad/rooms/supervisor/latest_handoff.md` (kèm mã `handoff_<id>_supervisor_<timestamp>.md`).
  - Gọi Lead Dev qua lệnh: `python3 tools/call_agent.py --profile "Lead Dev" --item-id <id> --prompt "..."`.

---

### Bước 2: Supervisor ➔ Lead Dev (Technical Architecture & Delegation)
- **Nhiệm vụ**:
  - Đọc `bmad/rooms/supervisor/latest_handoff.md` để nắm toàn bộ yêu cầu mà không cần User giải thích lại.
  - Phân tích kiến trúc: Xác định module đích (`mfe-cdp`, `mfe-crm`, `app-shell`), ranh giới Module Federation, và token giao diện `tds-ui`.
  - Có thể tham vấn sub-agents: `gemini-codebase-analyzer` (quét luồng dữ liệu 1M token) hoặc `strategic-reasoning-architect` (đánh giá rủi ro).
  - Chuyển trạng thái task sang `Active` trên Harness DB.
- **Generation Artifacts**:
  - Danh sách file cụ thể cần sửa/tạo mới.
  - Ràng buộc kỹ thuật (YAGNI, single file diff, native platform feature).
- **Handoff Output**:
  - Ghi biên bản vào `bmad/rooms/lead/latest_handoff.md`.
  - Bàn giao việc cho Peer Dev qua: `python3 tools/call_agent.py --profile "Peer Dev" --item-id <id> --prompt "..."`.

---

### Bước 3: Lead Dev ➔ Peer Dev (Execution & Code Minimization)
- **Nhiệm vụ**:
  - Đọc `bmad/rooms/lead/latest_handoff.md` để lấy danh sách file và phương án kỹ thuật.
  - Viết code thực thi theo nguyên tắc **Lazy Senior Dev**: Tối giản nhất, ít file nhất, xóa trước thêm sau, không viết boilerplate thừa.
  - Kiểm tra cú pháp, build thử (`nx build` hoặc `rsbuild`).
  - Tự chạy runnable check / unit test cơ bản.
  - Chuyển trạng thái task sang `Resolved` trên Harness DB.
- **Generation Artifacts**:
  - Code production hoàn chỉnh.
  - Bảng tổng hợp Git Diff ngắn gọn.
- **Handoff Output**:
  - Ghi biên bản vào `bmad/rooms/peer/latest_handoff.md`.
  - Bàn giao cho QC Verifier: `python3 tools/call_agent.py --profile "QC" --item-id <id> --prompt "..."`.

---

### Bước 4: Peer Dev ➔ QC Verifier (Independent Quality Gate)
- **Nhiệm vụ**:
  - Đọc `bmad/rooms/peer/latest_handoff.md` để lấy danh sách file đã thay đổi và AC từ Harness DB.
  - Sinh bộ test độc lập theo chuẩn 5-Stage ISTQB qua: `python3 tools/qc_test_generator.py --source <file> --sync-harness`.
  - Kiểm tra 5 tầng:
    1. Smoke / Syntax / Import integrity.
    2. Boundary / Edge cases (null, empty, overflow).
    3. State transition (router, signal change).
    4. Integration / Mock contracts.
    5. Regression / Security checks.
  - Nếu Test Pass: Đổi trạng thái task sang `Closed`.
  - Nếu Test Fail: Trả ngược biên bản lỗi về `bmad/rooms/lead/` để Lead chỉ đạo Peer fix.
- **Handoff Output**:
  - Ghi biên bản vào `bmad/rooms/qc/latest_handoff.md`.

---

### Bước 5: QC ➔ Supervisor ➔ User (Final Acceptance & Reporting)
- **Nhiệm vụ**:
  - Supervisor đọc `bmad/rooms/qc/latest_handoff.md`.
  - Xác nhận Work Item đã `Closed` trên Floci DB.
  - Tổng hợp báo cáo ngắn gọn (ultra-terse, telegraphic) gửi lại cho User:
    - Việc đã hoàn thành.
    - File đã chạm.
    - Kết quả kiểm thử.

---

## 4. CẤU TRÚC BIÊN BẢN BÀN GIAO MẪU (STANDARDIZED MEMO FORMAT)

Mỗi file trong `bmad/rooms/<role>/latest_handoff.md` tuân thủ nghiêm ngặt định dạng sau:

```markdown
# BIÊN BẢN BÀN GIAO: [TÊN_ROLE]

- **Mã Work Item**: #[ID] - [TITLE]
- **Thời gian lập**: YYYY-MM-DD HH:mm:ss +0700
- **Agent bàn giao**: [Vai trò hiện tại]
- **Agent nhận tiếp**: [Vai trò tiếp nhận]

### 1. Việc Đã Hoàn Thành Trong Phiên
- [x] [Đầu việc 1 đã hoàn tất và kiểm tra]
- [x] [Đầu việc 2]

### 2. Danh Sách File Đã Tác Động
- `projects/path/to/file.ts`: [Mô tả sửa đổi]

### 3. Ngữ Cảnh Kỹ Thuật (Context Snapshot)
- **State/Signals**: [Mô tả trạng thái đang lưu]
- **Điểm neo (Anchors)**: [Hàm/Class quan trọng đang xử lý]

### 4. Việc Còn Thiếu & Hướng Đi Kế Tiếp (Cho Agent Sau)
- [ ] [Việc cần làm tiếp theo]
- **Lệnh thực thi ngay**:
  ```bash
  python3 tools/agent_progress.py status
  ```
```

---

## 5. ĐIỀU KIỆN RÀO CẢN ĐẦU VÀO YÊU CẦU ĐỂ ĐẢM BẢO CHẤT LƯỢNG ĐẦU RA (REQ ENTRY GUARDRAILS)

Để đảm bảo kết quả đầu ra luôn chính xác, không ảo giác, không viết code thừa và không tràn Context Window, hệ thống thiết lập **5 Cổng Rào Cản Kiểm Soát (Quality Guardrails)** bắt buộc:

```text
[Yêu Cầu Đầu Vào]
        │
        ▼
[Cổng 1: Neo Ngữ Cảnh] ──(Thiếu file/URL/Figma?)──► [BÁO LỖI / TỪ CHỐI TIẾP NHẬN]
        │
        ▼ (Hợp lệ)
[Cổng 2: Giao Việc 3 Phần] ──(Thiếu Goal/Constraint?)──► [CHẶN DISPATCH LEAD/PEER]
        │
        ▼ (Hợp lệ)
[Cổng 3: Lead Review] ──(Dính màu hex/sửa chéo?)──► [YÊU CẦU PEER TỐI ƯU LẠI]
        │
        ▼ (Verdict = APPROVED)
[Cổng 4: QC 5-Stage Test] ──(Test thất bại?)──► [TRẢ VỀ LEAD ĐIỀU CHỈNH]
        │
        ▼ (100% Pass)
[Cổng 5: Closed & Auto-Clean] ──► [DỌN SẠCH BIÊN BẢN TẠM TRONG BMAD/ROOMS]
```

### 5.1 Cổng 1: Neo Ngữ Cảnh Nguồn (Source Anchoring Gate)
- **Điều kiện**: Mỗi yêu cầu từ User hoặc Spec bắt buộc phải cung cấp ít nhất một điểm neo thực tế:
  - **Điểm neo URL/Route**: Ví dụ `http://localhost:4200/#/:shopId/customers`.
  - **Điểm neo File/Component**: Ví dụ `apps/mfe-cdp/.../contact-list.component.ts`.
  - **Điểm neo Thiết kế Figma**: Phải có Node ID cụ thể (ví dụ `Node 1723:37492`).
  - **Điểm neo Dữ liệu/API**: Tên DTO hoặc Service trong `models/`.
- **Chặn vi phạm**: Nếu yêu cầu mơ hồ ("làm đẹp trang", "sửa lỗi chung"), Supervisor **lập tức từ chối đưa vào pipeline**, không tự ý đoán mò (No Guessing).

### 5.2 Cổng 2: Rào Cản Giao Việc 3 Phần (3-Part Delegation Gate)
- **Điều kiện**: Mọi lệnh điều phối qua `tools/call_agent.py` bắt buộc phải có đủ 3 tham số:
  1. `--goal`: Mục tiêu đo lường được (Acceptance Criteria dạng BDD: Given/When/Then).
  2. `--constraints`: Ràng buộc kỹ thuật cứng (Framework Angular 18 OnPush, TDS UI tokens, không nạp lib ngoài, Single-Ownership).
  3. `--suggested-path`: Gợi ý file đích tạm thời để Peer tham khảo.
- **Chặn vi phạm**: Nếu thiếu một trong ba thành phần, hệ thống phát cảnh báo và không cấp quyền thực thi xuống Peer.

### 5.3 Cổng 3: Rà Soát Kiến Trúc & Code Review (Lead Code Review Gate)
- **Điều kiện**: Peer Dev hoàn thành code bắt buộc phải được Lead Dev chạy `tools/lead_code_review.py` thẩm định:
  - **Single-Ownership**: 100% file thay đổi nằm đúng trong module được giao; không sửa chéo file của module khác.
  - **TDS Design Tokens**: Không tồn tại mã màu hex cứng (ví dụ `#FF4E00`, `#2EB032`) trong template; bắt buộc dùng class hoặc token chuẩn TDS.
  - **Angular Performance**: Bắt buộc có `changeDetection: ChangeDetectionStrategy.OnPush`.
- **Chặn vi phạm**: Nếu verdict khác `APPROVED`, task không được phép chuyển sang trạng thái `Resolved`.

### 5.4 Cổng 4: Rào Cản Nghiệm Thu Độc Lập (Independent Verification Gate)
- **Điều kiện**: QC sinh và chạy kiểm thử tự động 5 tầng ISTQB (`tools/qc_test_generator.py`):
  1. Smoke / Import integrity.
  2. Boundary & Null checks.
  3. State transition / Signals.
  4. Integration / Mock contracts.
  5. Regression checks.
- **Chặn vi phạm**: Tỷ lệ Pass phải đạt 100%. Nếu có lỗi thực nghiệm, trả về cho Lead Dev điều chỉnh kiến trúc.

### 5.5 Cổng 5: Ký Thác & Tự Động Dọn Phòng (Closed & Room Cleanup Gate)
- **Điều kiện**: Khi Work Item đạt trạng thái `Closed` trên Harness DB:
  - Hệ thống tự động xóa sạch các file handoff tạm thời của task đó trong `bmad/rooms/`.
  - Ngữ cảnh các phòng được reset về trạng thái tinh khiết, sẵn sàng nhận task kế tiếp mà không để lại rác bộ nhớ.

---

## 6. CƠ CHẾ KẾT NỐI VỚI UNDERSTAND-ANYTHING

1. **Trực quan hóa luồng công việc**:
   - `bmad/architecture.json` khai báo 4 phòng bàn giao như các nút xử lý (Processing Nodes), nối với nhau bằng các luồng `handoff-edge`.
   - Khi chạy [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything), toàn bộ sơ đồ 4 bước sẽ hiển thị thành Knowledge Graph tương tác trên trình duyệt.
2. **Truy vết lỗi (Root-Cause Traceability)**:
   - Khi xuất hiện bug, User hoặc Supervisor chỉ cần nhìn vào đồ thị phòng `bmad/rooms/` để xem tại cổng rào cản nào tiêu chuẩn bị phá vỡ (Lead thiết kế sai, Peer code thiếu hay QC bỏ sót test case).
