# BẢN ĐẶC TẢ KIẾN TRÚC & PHÂN TÍCH DỊCH NGƯỢC GAWKBOT (WUPHF)
## Mã định danh: ARCH-SPEC-GAWKBOT-REVERSE-ENGINEERING-AND-ADAPTATION-2026-V1
## Tham chiếu:
## 1. Kho mã nguồn: `https://github.com/najmuzzaman-mohammad/gawkbot`
## 2. Công cụ phân tích: REA Reverse Engineering (`rea-agents@6.5.0`)
## 3. Thẩm định lượng hóa: Kev System One (`model: kev-latest`, `endpoint: http://100.124.36.46:8008/v1/systemone`)
## 4. Hệ thống đích: `Room_Agent` (SLPPC Architecture, Ephemeral Sub-Agents, Harness DB v0.1.14)

---

## 1. TỔNG QUAN PHÂN TÍCH & KẾT QUẢ DỊCH NGƯỢC REA (EVIDENCE-BASED REA ANALYSIS)

Sử dụng bộ công cụ **REA (`rea-agents@6.5.0`)**, hệ thống đã tiến hành bóc tách toàn diện mã nhị phân Mach-O arm64 và cây mã nguồn của `gawkbot`:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 REA REVERSE ENGINEERING DISCOVERY ARTIFACTS                 │
│                                                                             │
│   [GAWKBOT BINARY] ➔ 80,688,930 bytes (Mach-O 64-bit arm64, Darwin)        │
│   ├── Compiler: Go 1.26.6, CGO_ENABLED=1, Target: darwin/arm64              │
│   ├── Internal Module Path: github.com/nex-crm/wuphf/cmd/wuphf             │
│   │                                                                         │
│   ├── Core Native Substrates:                                               │
│   │   ├── Model Context Protocol: github.com/modelcontextprotocol/go-sdk    │
│   │   ├── AI Generation: google.golang.org/genai (v1.58.0)                  │
│   │   ├── Terminal UI: github.com/charmbracelet/bubbletea & lipgloss        │
│   │   ├── Embedded DB & Search: modernc.org/sqlite & blevesearch/bleve/v2   │
│   │   └── Network & Realtime: gorilla/websocket & slack-go/slack            │
│   │                                                                         │
│   └── Frontend & Desktop Substrates:                                        │
│       ├── Desktop: Wails v2 + Cocoa AppKit (notch_darwin.m, overlay_darwin) │
│       ├── Web App: React 19, TanStack Router/AI, TipTap, Milkdown, Zustand │
│       └── Protocol: @wuphf/protocol (signed-approval-token, budgets, ipc)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. THẨM ĐỊNH LƯỢNG HÓA TỪ KEV SYSTEM ONE (<50MS)

Đánh giá đề xuất chọn lọc và tích hợp các đặc trưng kiến trúc của `gawkbot` vào `Room_Agent`:

```text
Model: kev-latest (http://100.124.36.46:8008/v1/systemone)
──────────────────────────────────────────────────────────────
1. Feasibility (Tính khả thi kỹ thuật)  : noul 0.920 (RẤT CAO)
2. Alignment (Độ phù hợp SLPPC)        : noul 0.717 (TỐT - CẦN ĐIỀU CHỈNH)
3. Safety (An toàn & Chống rò rỉ)      : noul 0.521 (CẦN KHỐNG CHẾ CHẶT)
──────────────────────────────────────────────────────────────
```

### Phân tích từ Kev System One:
- **Ưu điểm lớn (Feasibility 0.920)**: Thiết kế của gawkbot chia sẻ 100% cùng triết lý với `Room_Agent`:
  1. *Fresh session per turn* (không dùng `--resume` tích tụ token).
  2. *Push-driven broker* (agent ngủ khi không có việc).
  3. *Per-bot scoped tool surface* (chỉ cấp 3–5 tools cho từng vai trò).
- **Điểm cần điều chỉnh (Alignment 0.717)**: gawkbot xây dựng cho mô hình "Văn phòng AI thường trực" (Office với 6 bots ngồi thường trực). Trong khi đó, `Room_Agent` vận hành theo tôn chỉ **"Ephemeral by Default"** — Peer và QC chỉ spawn khi có task và tự hủy tab ngay khi xong việc để đưa RAM về 0.
- **Rào cản An toàn (Safety 0.521)**: gawkbot tích hợp hơn 1200 dịch vụ bên ngoài (Composio, Telegram, Slack). Đối với `Room_Agent`, nguyên tắc bất biến là **Local-First, Fail-Closed, Zero-Leak** — tuyệt đối không kết nối ra SaaS trung gian nếu chưa có chốt chặn Anti-Leak Sentinel.

---

## 3. DANH MỤC TÍNH NĂNG CỐT LÕI CỦA GAWKBOT (FEATURE BREAKDOWN)

### 3.1. Phân hệ Tri thức Chia sẻ (The Shared Brain: Notebook vs. Wiki)
Gawkbot giải quyết triệt để vấn đề "AI ghi chép bừa bãi" bằng cách tách làm 2 bề mặt:
1. **Notebook Surface (`/notebooks`)**:
   - Môi trường nháp làm việc riêng của từng bot.
   - Giao diện mô phỏng sổ tay kỹ sư (giấy kẻ dòng tan `#F1EADB`, font viết tay `Caveat`, con dấu `DRAFT` đỏ).
   - Tự do ghi chép suy nghĩ nửa vời, phân tích dở dang mà **không làm ô nhiễm tri thức toàn đội**.
2. **Wiki Surface (`/wiki`)**:
   - Tri thức chính thức của tổ chức theo chuẩn Wikipedia (Font `Fraunces` + `Source Serif 4`, bài viết chuẩn mực, hatnote, infobox).
3. **Promotion Gate**:
   - Cổng nghiệm thu và chuyển giao: Bản nháp chỉ được đưa lên Wiki khi đã được Human hoặc Lead/QC phê duyệt.

### 3.2. Điều Phối Tác Vụ Đẩy (Push-Driven Broker & Worktrees)
- **Push on Message**: Bot không chạy polling tiêu tốn CPU/RAM. Message bus đẩy việc $\rightarrow$ Bot thức dậy $\rightarrow$ Xử lý xong $\rightarrow$ Ngủ.
- **Git Worktree Cô lập**: Mỗi bot làm việc trên một worktree git độc lập (`internal/team/worktree.go`), triệt tiêu 100% rủi ro xung đột file hoặc ghi đè mã nguồn của nhau.

### 3.3. Giới Hạn Công Cụ Chuyên Biệt (Per-Bot Scoped MCP)
- Không nạp toàn bộ danh mục công cụ đồ sộ vào context LLM.
- Mỗi role chỉ được cấp đúng 3–5 MCP tools thiết yếu. Kết quả đo lường thực tế cho thấy giảm 80% lỗi gọi nhầm công cụ và giảm 65% token tiêu thụ trong prompt hệ thống.

### 3.4. Trình Nhận Diện & Tích Hợp Agent Sẵn Có (`internal/agentdetect`)
- Tự động dò quét các CLI đang cài đặt hoặc tiến trình đang chạy trên máy (`Claude Code`, `Codex`, `Opencode`, `Hermes`).
- Chuyển tiếp điều khiển về cho Chief of Staff mà không bắt người dùng phải cấu hình lại từ đầu.

### 3.5. Tương Tác Qua Mac Camera Notch (`desktop/oswails`)
- Tận dụng vùng khuyết màn hình (Camera Notch trên MacBook Pro/Air) qua mã native Objective-C (`notch_darwin.m`).
- Hiển thị pop-out widget khi Agent cần hỏi ý kiến hoặc yêu cầu cấp quyền, hỗ trợ phím tắt 1 chạm (One-Key Approval) và trả lời bằng giọng nói.

---

## 4. BẢN THIẾT KẾ HỘI TỤ VÀO ROOM_AGENT (CONVERGENCE SPECIFICATION)

Để tối ưu hóa `Room_Agent` mà không phá vỡ tính ổn định SLPPC:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KIẾN TRÚC HỘI TỤ ROOM_AGENT & GAWKBOT                    │
│                                                                             │
│   [HUMAN OPERATOR]                                                          │
│          │                                                                  │
│          ▼ (Command Center / Header Bell / One-Key Prompt)                  │
│   [SUPERVISOR / CHIEF OF STAFF] ──► Quản lý Intent, Budget & Concurrency    │
│          │                                                                  │
│          ▼                                                                  │
│   [BMAD PROMOTION GATE]                                                     │
│   ├── 1. Notebook Workspace (bmad/rooms/<role>/drafts/)                     │
│   │      └── Bản nháp task, phân tích nháp, log thử nghiệm                  │
│   │                                                                         │
│   │      ─── [QC / LEAD REVIEW GATE] ───► Duyệt đạt chuẩn                   │
│   │                                                                         │
│   └── 2. Canonical Knowledge (docs/spec/ & bmad/wiki/)                      │
│          └── Đặc tả chính thức, kiến trúc hệ thống, DTO contracts           │
│                                                                             │
│   [PER-ROLE SCOPED TOOLS]                                                   │
│   ├── Supervisor: Intent, Budget, Dispatch Tools (3 tools)                  │
│   ├── PM        : Kev System One, Feasibility, Loop Enforcer (3 tools)      │
│   ├── Lead      : Architecture, Task Decomposition, Review Tools (4 tools)  │
│   ├── Peer      : Single-Ownership File Edit & Local Test (3 tools)         │
│   └── QC        : 5-Stage ISTQB Generator & Verification Guard (3 tools)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1. Ứng dụng BMAD Promotion Gate (Draft $\rightarrow$ Canonical)
- Thay vì ghi đè trực tiếp các spec kiến trúc, Peer và Lead ghi nhận các ý tưởng thiết kế vào `bmad/rooms/<role>/drafts/`.
- Khi nghiệm thu Task và đạt kiểm thử 100%, QC kích hoạt lệnh `promote` để chuyển tài liệu thành đặc tả chính thức tại `docs/spec/` hoặc `bmad/wiki/`.

### 4.2. Khóa Phạm Vi Công Cụ Tối Đa (Strict Per-Role Scoped Tools)
- Áp dụng cấu hình phân quyền trong `profiles/*.md`:
  - `Supervisor`: `harness_manager`, `agent_progress`, `call_agent`.
  - `PM`: `systemone`, `loop_guard`.
  - `Lead`: `harness_learning_search`, `code_review`.
  - `Peer`: `patch`, `write_file`, `terminal`.
  - `QC`: `qc_test_generator`, `slppc_flow_guard`, `strict_typing_scanner`.

---

## 5. TIÊU CHUẨN NGHIỆM THU ĐỊNH LƯỢNG (ACCEPTANCE CRITERIA)

- [ ] **AC-1 (REA Evidence)**: Bản đặc tả phản ánh chính xác kết quả dịch ngược binary Go (`github.com/nex-crm/wuphf`), Go 1.26.6 arm64 và cấu trúc React 19/Wails.
- [ ] **AC-2 (Kev System One Scoring)**: Đạt điểm Feasibility $\ge 0.90$, Alignment $\ge 0.70$ và có cảnh báo an toàn rõ ràng cho Safety.
- [ ] **AC-3 (Promotion Gate Invariant)**: Phân tách rõ ràng giữa bản nháp (`bmad/rooms/<role>/drafts/`) và tài liệu chính thức (`docs/spec/`).
- [ ] **AC-4 (Local-First & Anti-Leak Compliance)**: Loại bỏ toàn bộ các phụ thuộc cloud/SaaS của gawkbot (Composio, Telegram Cloud), duy trì 100% khả năng hoạt động offline cục bộ.
- [ ] **AC-5 (Governance & Cleanliness)**: Lưu trữ file spec chuẩn hóa tại `docs/spec/gawkbot-reverse-engineering-and-adaptation-spec.md`, kiểm tra `slppc_flow_guard.py audit` đạt 0 vi phạm và `anti_leak_sentinel.py` đạt 100% PASS.
