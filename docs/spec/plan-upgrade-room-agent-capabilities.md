# KẾ HOẠCH NÂNG CẤP NĂNG LỰC TOÀN DIỆN (CAPABILITIES UPGRADE PLAN)
## Mã kế hoạch: PLAN-ROOM-AGENT-CAPABILITIES-UPGRADE-2026-V1
## Tham chiếu:
## 1. Bản đặc tả phân tích Gawkbot: `docs/spec/gawkbot-reverse-engineering-and-adaptation-spec.md`
## 2. Giao thức hoạt động: `WORKSPACE_PROTOCOL.md` & `bmad/WORKSPACE_PROTOCOL.md`
## 3. Thẩm định lượng hóa: Kev System One (`feasibility: 0.879`, `impact: 0.831`)
## 4. Tôn chỉ thực thi: Lazy Senior Developer & YAGNI Extremist (Ưu tiên cấu trúc chuẩn, code ít nhưng sâu)

---

## 1. MỤC TIÊU & TÔN CHỈ THỰC THI (OBJECTIVES)

Nâng cấp năng lực cốt lõi (**Capabilities / "Capas"**) của `Room_Agent` từ các phát hiện thực chiến sau khi dịch ngược `gawkbot` (WUPHF) và tích hợp các chuẩn mực từ `codex-room-setup`, `paseo-supervision`, `pstack-codex`.

### 3 Tôn chỉ Bất biến (Invariants):
1. **YAGNI & Lazy Senior Developer**: Không thêm dependency nặng; tận dụng stdlib Python $\ge 3.9$ và native OS Darwin arm64.
2. **Ephemeral by Default**: Không giữ worker tabs IDLE; giải phóng RAM về 0 ngay khi hoàn thành nhiệm vụ (`Resolved` / `Closed`).
3. **Fail-Closed & Zero-Leak**: 100% hoạt động local offline, cấm kết nối SaaS bên thứ ba không kiểm soát, bảo vệ tuyệt đối secrets.

---

## 2. BẢNG THẨM ĐỊNH KEV SYSTEM ONE CHO KẾ HOẠCH

```text
Đánh giá tình huống: 4-Capability Upgrade Plan for Room_Agent
Model: kev-latest (http://100.124.36.46:8008/v1/systemone)
──────────────────────────────────────────────────────────────
• Feasibility (Tính khả thi)           : noul 0.879 (RẤT CAO)
• Impact (Tác động nâng cấp hiệu năng) : noul 0.831 (RẤT CAO)
• Alignment (Độ khớp SLPPC & YAGNI)    : noul 0.583 (CHẤP NHẬN ĐƯỢC - CẦN GIỮ GỌN)
──────────────────────────────────────────────────────────────
Khuyến nghị từ Kev: Không dàn trải 5-6 phân hệ cùng lúc. Tập trung dứt điểm 
vào 4 năng lực trọng tâm, mỗi năng lực hoàn thành kèm 1 test runner cơ học.
```

---

## 3. PHÂN RÃ 4 NĂNG LỰC TRỌNG TÂM (4 CORE CAPABILITY WORKSTREAMS)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN 4 NĂNG LỰC NÂNG CẤP (CAPAS MATRIX)                  │
│                                                                             │
│   CAPA 1: THE SHARED BRAIN PROMOTION GATE                                   │
│   ├── bmad/rooms/<role>/drafts/ (Sổ nháp kỹ thuật, không làm loãng wiki)    │
│   ├── tools/bmad_promote.py (Cổng duyệt chuyển Draft ➔ Canonical Wiki)      │
│   └── bmad/wiki/ (Bách khoa toàn thư dự án, phiên bản chuẩn hóa)            │
│                                                                             │
│   CAPA 2: STRICT PER-ROLE SCOPED TOOLS                                      │
│   ├── profiles/*.md: Khóa cứng 3–5 tools đặc thù cho từng vai trò           │
│   ├── Triệt tiêu 100% role trespass và gọi nhầm công cụ                     │
│   └── Giảm 65% token tiêu hao trong system prompt                           │
│                                                                             │
│   CAPA 3: LOCAL AGENT PROCESS SCANNER                                       │
│   ├── tools/agent_scanner.py: Tự động quét tiến trình agent đang chạy        │
│   ├── Nhận diện Claude Code, Codex, Opencode, Hermes trên macOS              │
│   └── Tự động đăng ký vào bmad/rooms/agent_terminals.json                   │
│                                                                             │
│   CAPA 4: PUSH-DRIVEN DISPATCH BROKER                                       │
│   ├── Thay thế polling kiểm tra hòm thư rỗng                                │
│   ├── Đẩy chỉ thị trực tiếp vào PTY terminal đích qua Orca / Hermes CLI     │
│   └── Kèm work packet đầy đủ để agent chạy fresh session per turn           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### CHI TIẾT TỪNG NĂNG LỰC:

### 🌟 Capa 1: The Shared Brain & BMAD Promotion Gate
- **Bài toán**: Hiện tại các Agent thường ghi đè trực tiếp tài liệu spec hoặc để các ghi chú rải rác trong `bmad/rooms/`, gây nguy cơ ô nhiễm tri thức chuẩn.
- **Giải pháp**:
  - Mỗi phòng ban có thư mục nháp riêng: `bmad/rooms/<role>/drafts/<topic>.md`.
  - Tri thức chuẩn hóa được lưu trữ tập trung tại: `bmad/wiki/<domain>/<article>.md`.
  - Viết công cụ `tools/bmad_promote.py`:
    - Cú pháp: `python3 tools/bmad_promote.py --draft <path> --target-wiki <domain>/<name> [--reviewer <lead|qc>]`
    - Cơ chế: Kiểm tra bằng chứng nghiệm thu, xác thực cú pháp markdown, tự động di chuyển bản nháp vào `archive/` và xuất bản bài viết vào `bmad/wiki/`.

### 🛡️ Capa 2: Strict Per-Role Scoped Tool Surfaces
- **Bài toán**: Khi mọi profile đều nạp danh mục tool phẳng (20+ tools), LLM dễ bị phân tâm ("hallucination"), gọi nhầm công cụ của vai trò khác (ví dụ: Supervisor tự gọi lệnh code, Lead tự gọi lệnh sửa file).
- **Giải pháp**:
  - Giới hạn cứng mỗi profile chỉ được nạp đúng 3–5 công cụ cốt lõi:
    - **Supervisor**: `harness_manager`, `agent_progress`, `call_agent`.
    - **PM**: `systemone`, `loop_guard`.
    - **Lead**: `harness_learning_search`, `code_review`, `bmad_promote`.
    - **Peer**: `patch`, `write_file`, `terminal`.
    - **QC**: `qc_test_generator`, `slppc_flow_guard`, `strict_typing_scanner`.
  - Bổ sung chốt chặn `tools/tests/test_scoped_tools.py` xác thực tính tuân thủ.

### 🔍 Capa 3: Local Agent Process Scanner (`tools/agent_scanner.py`)
- **Bài toán**: Khi lập trình viên khởi động các agent bằng tay (mở terminal chạy `claude`, `hermes`, hoặc `codex`), hệ thống phòng ban không nhận diện được để giao việc.
- **Giải pháp**:
  - Tích hợp module quét tiến trình native (`pgrep` / `ps aux` trên Darwin arm64) tương tự `gawkbot/internal/agentdetect`.
  - Tự động phát hiện các phiên làm việc của Hermes / Claude Code / Codex đang mở và tự động map vào bảng `bmad/rooms/agent_terminals.json`.
  - Cú pháp: `python3 tools/agent_scanner.py [--watch] [--json]`.

### ⚡ Capa 4: Push-Driven Dispatch Broker (`tools/dispatch_broker.py`)
- **Bài toán**: Cơ chế heartbeat polling kiểm tra file trạng thái gây tốn I/O đĩa và có độ trễ (delay 5–10s).
- **Giải pháp**:
  - Xây dựng broker hướng sự kiện siêu nhẹ (Push-Driven Event Bus).
  - Khi có task mới hoặc chuyển giao trạng thái (`agent.turn_ended`), Broker lập tức bắn payload chỉ thị trực tiếp vào stdin của terminal đích (thông qua `orca terminal send` hoặc Hermes IPC).
  - Khởi chạy fresh context cho Sub-Agent, thực thi xong tự hủy.

---

## 4. LỘ TRÌNH TRIỂN KHAI 3 GIAI ĐOẠN (EXECUTION PHASES)

```text
[GIAI ĐOẠN 1: TRI THỨC & CÔNG CỤ CỐT LÕI (CAPA 1 & 2)]
├── 1.1. Khởi tạo cấu trúc thư mục bmad/wiki/ và bmad/rooms/<role>/drafts/
├── 1.2. Phát triển công cụ tools/bmad_promote.py & unit test
├── 1.3. Chuẩn hóa profiles/*.md khóa chặt scoped tools
└── 1.4. Kiểm tra: python3 -m unittest discover -s tools/tests

[GIAI ĐOẠN 2: TỰ HÀNH & ĐIỀU PHỐI (CAPA 3 & 4)]
├── 2.1. Phát triển tools/agent_scanner.py quét tiến trình agent
├── 2.2. Nâng cấp dispatch broker kết nối trực tiếp Orca / Hermes TUI
└── 2.3. Kiểm tra tích hợp: python3 tools/agent_scanner.py --json

[GIAI ĐOẠN 3: KIỂM ĐỊNH CHẤT LƯỢNG & COMMIT]
├── 3.1. Chạy full unit tests (Đạt 105+ tests PASS)
├── 3.2. Chạy slppc_flow_guard.py audit (0 vi phạm)
├── 3.3. Chạy anti_leak_sentinel.py (100% clean)
└── 3.4. Commit atomic và push cập nhật Pull Request
```

---

## 5. TIÊU CHUẨN NGHIỆM THU ĐỊNH LƯỢNG (ACCEPTANCE CRITERIA)

- [ ] **AC-1 (Promotion Gate)**: `tools/bmad_promote.py` hoạt động hoàn hảo, chỉ promote bản nháp khi có phê duyệt hợp lệ, tạo bài viết tại `bmad/wiki/` và tự động dọn bản nháp vào `archive/`.
- [ ] **AC-2 (Tool Fencing)**: Toàn bộ 10 profile chỉ nạp đúng 3–5 công cụ đặc thù theo RBAC, kiểm tra Flow Guard không có lỗi `role_trespass`.
- [ ] **AC-3 (Scanner Efficiency)**: `tools/agent_scanner.py` quét xong toàn bộ tiến trình trên macOS trong $< 50$ms, không tốn token LLM, trả về JSON chính xác.
- [ ] **AC-4 (Test Suite Expansion)**: Toàn bộ bộ test suites đạt $\ge 105$ tests PASS 100%.
- [ ] **AC-5 (Zero-Leak)**: 100% không phát sinh file rác, không lộ bí mật, tuân thủ `WORKSPACE_PROTOCOL.md`.
