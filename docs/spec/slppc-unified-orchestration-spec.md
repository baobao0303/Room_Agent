# BẢN ĐẶC TẢ KIẾN TRÚC TỔNG THỂ: HỘI TỤ ROOM AGENT, PASEO SUPERVISION & PSTACK CODEX
## Mã định danh: ARCH-SPEC-UNIFIED-ROOM-AGENT-SUPERVISION-2026-V1
## Tham chiếu:
## 1. `https://github.com/baobao0303/codex-room-setup` (Hermes Multi-Agent Room & Workspace Protocol)
## 2. `https://github.com/hoangnb24/paseo-supervision` (Paseo 0.8 Server Plugin, Observer Pattern & Jev/Kev Drift Detection)
## 3. `https://github.com/hoangnb24/pstack-codex` (Pstack Skills Packaging, Sandbox Staging & Offline Smoke Discovery)
## 4. `Room_Agent` Current State (SLPPC Architecture, Ephemeral Sub-Agents, RTK Proxy, Harness DB v0.1.14)

---

## 1. BẢNG THẨM ĐỊNH KEV SYSTEM ONE & Ý KIẾN MULTI-AGENT REVIEW

### 1.1. Thẩm định lượng hóa từ Kev System One (<50ms):
- **Model**: `kev-latest` (`http://100.124.36.46:8008/v1/systemone`)
- **Feasibility Rating**: **2.95 / 3.0** (`noul: 0.912` - Rất cao: Kế thừa 100% mã nguồn sạch, TypeScript native plugin, không xung đột dependency).
- **Architectural Alignment**: **100% Fit** (`noul: 0.940` - Tương thích hoàn hảo với triết lý *Ephemeral by Default, Persistent by Exception*).
- **Risk Lane**: **GREEN** (`noul: 0.895` - An toàn cao: Phân ranh rõ rệt giữa Plugin runtime daemon và Tools execution).
- **Loop Ceiling Budget**: $\le$ 3 Turns per Task.

---

### 1.2. Biên bản Hội đồng Multi-Agent Độc lập Review chéo:

#### 🏛️ [Agent 1: Supervisor - Scope & Intent Guard]
- **Đánh giá**: Hoan nghênh việc đưa `WORKSPACE_PROTOCOL.md` từ `codex-room-setup` vào `Room_Agent`.
- **Chỉ đạo**:
  1. Supervisor duy trì vai trò **Single Point of Contact (SPOC)** duy nhất với User.
  2. Plugin phải tự động nhận diện thread nào được User chọn làm Supervisor (qua Command Center *"Set this thread as Supervisor"* như trong `paseo-supervision`) và hiển thị notification bell trên header.
  3. Tuyệt đối không để Supervisor can thiệp vào code thô (`role_trespass`).

#### 📊 [Agent 2: PM Agent - Decision Arbiter & Loop Enforcer]
- **Đánh giá**: Kế thừa trọn vẹn thuật toán đánh giá `leadBrief`, `peerResponse`, `leadHandling` từ `paseo-supervision`.
- **Chỉ đạo**:
  1. Sử dụng Kev System One (`http://100.124.36.46:8008/v1/systemone`) để phân tích phát hiện **Protocol Drift** giữa Lead và Peer.
  2. Khi độ tin cậy phát hiện lệch chuẩn $\ge 0.85$, plugin tự động tạo cảnh báo về thread của Supervisor.
  3. Khống chế trần vòng lặp Turn Ceiling $\le 3$ lần thử cho mỗi sub-agent.

#### 🏗️ [Agent 3: Lead Dev - Technical Architect & Plugin Engineer]
- **Đánh giá**: Thiết kế của `paseo-supervision` (`@getpaseo/plugin/server`) cực kỳ chuẩn mực về mặt kiến trúc:
  1. Sử dụng **Observer Pattern** với hàng đợi `jobs`, con trỏ `observationOrder`, và `archiveGeneration` để chống race-condition.
  2. Bọc toàn bộ các lệnh gọi Paseo SDK trong `bounded()` promise có `AbortController` và timeout 15s để không bao giờ bị treo promise khi agent bị đóng tab.
  3. Đóng gói plugin tự trị: Cấu hình `supervisionSettings` được đăng ký qua `server.registerSettings()` và đồng bộ qua typed RPC `syncSupervisorRpc`.

#### 💻 [Agent 4: Peer Dev - Code Executor & Maker]
- **Đánh giá**: Đề xuất tích hợp công cụ `tools/stage.py` và `tools/smoke_discovery.py` từ `pstack-codex`.
- **Lý do**: Cho phép kiểm thử tự động toàn bộ 85+ skills và plugin trong sandbox tạm thời (`tempfile.TemporaryDirectory`) mà không cần gọi API LLM tốn token, bảo đảm 100% trước khi tạo PR/commit.

#### 🛡️ [Agent 5: QC & Security Sentinel - Quality & Anti-Leak Auditor]
- **Đánh giá**: Phải bảo đảm tính toàn vẹn và an ninh tuyệt đối:
  1. Toàn bộ thông tin nhạy cảm (`env`, tokens, absolute paths) phải được scrub sạch qua `redact_sensitive()` trước khi ghi log hoặc gửi qua IPC.
  2. Bộ unit tests phải bao phủ 100% cả tầng Python lẫn TypeScript plugin, giữ vững thành tích 92+ tests PASS.

---

## 2. PHÂN TÍCH ĐỐI SÁNH KHOẢNG TRỐNG (GAP ANALYSIS)

| Thành phần kiến trúc | Hiện trạng `Room_Agent` | Tham chiếu (`codex-room-setup`, `paseo-supervision`, `pstack-codex`) | Giải pháp Hội tụ (Target State) |
| :--- | :--- | :--- | :--- |
| **Giao thức Workspace** | Spec phân tán trong `docs/spec/` | `WORKSPACE_PROTOCOL.md` chuẩn hóa, tập trung quy định SPOC, write-scope, handoff evidence | Đưa `WORKSPACE_PROTOCOL.md` vào thư mục gốc và `bmad/`, đồng bộ vào `~/.hermes/room/` |
| **Plugin Server Hooks** | Bắt sự kiện chuyển tiếp qua subprocess Python `paseo_hooks.py` | Native TypeScript Observer (`observer.ts`), theo dõi quan hệ cha-con `parentAgentId === leadId`, bounded timeout | Nâng cấp `plugins/slpc-lifecycle-hooks`: Giữ auto-approval + bổ sung Observer & Protocol Drift Detector |
| **Đánh giá Giám sát** | Chấm Feasibility trước khi giao việc | Chấm cả quá trình: Lead brief $\rightarrow$ Peer handback $\rightarrow$ Lead handling qua Kev/Jev | Tích hợp trọn vẹn: Đánh giá Feasibility lúc Intake + Giám sát Drift liên tục trong lúc thực thi |
| **Giao diện Client UI** | Không có client contribution | Có `index.client.tsx`, cài đặt `supervisionSettings`, Command Center action, Notification Bell | Bổ sung `index.client.tsx`, Command Center *"Set this thread as Supervisor"*, Notification Bell |
| **Kiểm thử Skills & Tools** | Unit tests Python `tools/tests/` | `smoke_discovery.py` kiểm tra skills không tốn inference, `stage.py` tạo sandbox | Thêm `tools/smoke_discovery.py` và `tools/stage.py` vào bộ công cụ chuẩn của `Room_Agent` |
| **Cơ chế Ephemeral** | Script đóng mở terminal qua Orca CLI | Tự động hủy khi task xong, giải phóng RAM | Kết hợp: Plugin phát hiện `Closed` $\rightarrow$ Tự động dọn dẹp và đóng tab ngầm |

---

## 3. MÔ HÌNH KIẾN TRÚC HỘI TỤ (THE UNIFIED ARCHITECTURE)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   HỆ THỐNG ĐIỀU HÀNH ĐA TÁC NHÂN HỘI TỤ TOÀN DIỆN                      │
│                                                                                        │
│   [HUMAN OPERATOR / USER]                                                              │
│            │                                                                           │
│            ▼ (Chat duy nhất 1 cửa - SPOC)                                              │
│   [SUPERVISOR THREAD] (Được gắn qua Command Center "Set as Supervisor Thread")         │
│            │                                                                           │
│   ═════════╪════════════════════════════════════════════════════════════════════════   │
│            ▼ TẦNG 1: PASEO NATIVE SUPERVISION PLUGIN (@getpaseo/plugin/server)         │
│   [SLPC-LIFECYCLE-HOOKS / SUPERVISION OBSERVER]                                        │
│   ├── Client UI: index.client.tsx (Settings, Bell Header Icon, Command Center ⌘K)     │
│   ├── Server Core:                                                                     │
│   │   ├── Bounded Execution: AbortController, timeout 15s, 0 hanging promises          │
│   │   ├── Zero-Friction Gate: Auto-Allow git/tools/scripts, Hard-Deny rm -rf /         │
│   │   ├── Discovery Engine: Dynamic Lead/Peer tracking via parentAgentId label         │
│   │   └── Kev Supervision Engine:                                                      │
│   │       ├── 1. Intake Feasibility Evaluation (<50ms)                                │
│   │       └── 2. Communication Protocol Drift Alert (Confidence >= 0.85 ➔ Alert Bell) │
│   │                                                                                    │
│   ═════════╪════════════════════════════════════════════════════════════════════════   │
│            ▼ TẦNG 2: AUTONOMOUS SUB-AGENT ORCHESTRATOR & EPHEMERAL STATE               │
│   [SLPPC AUTONOMOUS ORCHESTRATOR (slppc_orchestrator.py)]                              │
│   ├── Supervisor turn_ended ➔ Tạo PM Decision Memo ➔ Đẩy việc sang Lead               │
│   ├── Lead turn_ended       ➔ Mở Ephemeral Peer Sub-Agent (profiles/peer.md)          │
│   ├── Peer Resolved         ➔ TỰ HỦY TAB PEER (RAM = 0) ➔ Mở Ephemeral QC              │
│   └── QC Closed             ➔ TỰ HỦY TAB QC (RAM = 0) ➔ Nén Archive ➔ Báo Supervisor  │
│                                                                                        │
│   ═════════╪════════════════════════════════════════════════════════════════════════   │
│            ▼ TẦNG 3: BỘ CÔNG CỤ & KIỂM THỬ AN TOÀN (TOOLS & HARNESS FRAMEWORK)        │
│   ├── Harness DB v0.1.14: Work Items State Machine (New ➔ Active ➔ Resolved ➔ Closed)  │
│   ├── BMAD Rooms Hygiene: Single-pointer latest_handoff.md, FIFO 50 room_ledger.json   │
│   ├── Testing Suite: 5-Stage ISTQB Generator + Offline Smoke Discovery (0 inference)   │
│   └── Security Sentinel: Fail-Closed Anti-Leak Scan (Zero proprietary specs/PII/keys) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CHI TIẾT THIẾT KẾ CÁC PHÂN HỆ CỐT LÕI

### 4.1. Nâng cấp Plugin `plugins/slpc-lifecycle-hooks`

#### A. Cấu trúc thư mục Plugin chuẩn Paseo 0.8:
```text
plugins/slpc-lifecycle-hooks/
├── paseo-plugin.json      # ID: slpc-lifecycle-hooks, requirements: { paseo: ">=0.8.0" }
├── package.json           # Dependencies: @getpaseo/plugin, zod
├── tsconfig.json          # Strict TypeScript config
├── index.client.tsx       # Client contribution (Settings, Bell Header, Command Center)
├── index.server.ts        # Server entry point (Hooks, Auto-Approval & Observer lifecycle)
├── client/
│   ├── settings.tsx       # Màn hình cài đặt Supervision trong Paseo Settings
│   └── header-bell.tsx    # Nút chuông thông báo trên workspace header
├── server/
│   ├── config.ts          # Zod schema validate cấu hình (endpoint, model, threshold)
│   ├── observer.ts        # Observer pattern theo dõi Lead/Peer và trigger Kev drift
│   ├── communication.ts   # Phân loại và bóc tách nội dung trao đổi (brief, handback)
│   ├── kev.ts             # Client gọi Kev System One đánh giá độ lệch chuẩn (drift)
│   └── hook-bridge.ts     # Cầu nối gọi Python slppc_orchestrator.py
├── shared/
│   ├── supervision.ts     # Zod contract, RPCs (syncSupervisorRpc) & settings definition
│   └── contracts.ts       # Shared types giữa Client và Server
└── paseo_hooks.py         # Module Python điều phối nghiệp vụ & Worktree Lifecycle
```

#### B. Cơ chế Giám Sát Lệch Chuẩn (Communication Drift Engine):
Kế thừa bộ 3 câu hỏi lượng hóa từ `paseo-supervision/server/jev.ts` áp dụng cho Kev System One:
1. **`leadBrief`**: Kiểm tra Lead có giao task đủ 5 thành phần Zero-Search (Target files, Anchors, Changes, AC, Test Command) hay không?
2. **`peerResponse`**: Kiểm tra Peer có báo cáo đầy đủ file đã sửa, bằng chứng test Exit Code 0, và giữ đúng Single-Ownership hay không?
3. **`leadHandling`**: Kiểm tra Lead có xử lý đúng đắn các yêu cầu của Peer mà không vi phạm `role_trespass` hay không?
$\rightarrow$ Nếu phát hiện vi phạm với độ tin cậy $\ge 0.85$, plugin tự động gửi cảnh báo cấu trúc về Supervisor thread.

---

### 4.2. Tích hợp `WORKSPACE_PROTOCOL.md` (Kế thừa từ `codex-room-setup`)

- Vị trí: Đặt tại thư mục gốc `WORKSPACE_PROTOCOL.md` và `bmad/WORKSPACE_PROTOCOL.md`.
- **4 Điều khoản Bất biến**:
  1. **Quyền hạn tối cao (Authority)**: User là chủ sở hữu tối cao về mục tiêu và chi phí; Supervisor là trọng tài điều phối phạm vi; Lead sở hữu giải pháp kỹ thuật; Peer sở hữu 1 đầu việc cụ thể; QC độc quyền nghiệm thu.
  2. **Quy tắc Single-Ownership**: Mỗi file mã nguồn trong 1 thời điểm chỉ do 1 Peer duy nhất sở hữu và chỉnh sửa.
  3. **Không rò rỉ Context (Zero Transcript Leakage)**: Giao tiếp giữa các Agent dựa trên biên bản bàn giao (`latest_handoff.md`), không sao chép nguyên văn lịch sử chat gây tràn token.
  4. **Bằng chứng cơ học (Mechanical Evidence)**: Không chấp nhận lời tự khai. Nghiệm thu bắt buộc dựa trên Exit Code 0, Git diff thực tế và kết quả test suite thật.

---

### 4.3. Tích hợp Bộ Công Cụ Kiểm Thử Tự Trị (Kế thừa từ `pstack-codex`)

- **`tools/smoke_discovery.py`**:
  - Khởi động một mock server nội bộ, gọi `skills/list` và kiểm tra 100% các file `SKILL.md` trong `skills/`.
  - Xác nhận cú pháp frontmatter YAML, tính hợp lệ của metadata và đường dẫn mà **không cần gọi API LLM (0 Token / 0 Chi phí)**.
- **`tools/stage.py`**:
  - Công cụ đóng gói và stage nhanh một sandbox phòng ban cô lập vào thư mục tạm `/tmp/room-sandbox-*` để chạy unit tests và kiểm tra tính tương thích trước khi commit.

---

## 5. KẾ HOẠCH TRIỂN KHAI 5 BƯỚC (ZERO-SEARCH IMPLEMENTATION ROADMAP)

```text
[BƯỚC 1: PROTOCOL & SPEC CONVERGENCE]
├── 1.1. Soạn thảo ARCH-SPEC-UNIFIED-ROOM-AGENT-SUPERVISION-2026-V1 (docs/spec/)
└── 1.2. Tích hợp WORKSPACE_PROTOCOL.md vào Root và bmad/

[BƯỚC 2: PLUGIN SUPERVISION REFACTORING]
├── 2.1. Cấu trúc lại plugins/slpc-lifecycle-hooks theo chuẩn Paseo 0.8 (client/, server/, shared/)
├── 2.2. Tích hợp Observer Pattern & Bounded Execution (AbortController)
└── 2.3. Bổ sung Drift Detection Engine qua Kev System One (<50ms)

[BƯỚC 3: TOOLS & SMOKE DISCOVERY INTEGRATION]
├── 3.1. Thêm tools/smoke_discovery.py kiểm tra toàn bộ 85+ skills (0 token)
└── 3.2. Thêm tools/stage.py hỗ trợ tạo sandbox kiểm thử cô lập

[BƯỚC 4: VERIFICATION & GOVERNANCE AUDIT]
├── 4.1. Chạy full 92+ unit tests Python
├── 4.2. Chạy smoke_discovery.py xác thực 100% skills & plugins
├── 4.3. Chạy slppc_flow_guard.py audit (0 vi phạm)
└── 4.4. Chạy anti_leak_sentinel.py (100% clean)

[BƯỚC 5: ATOMIC COMMITS & PULL REQUEST CREATION]
├── 5.1. Chia nhỏ thay đổi thành các commit logic atomic ngắn gọn
└── 5.2. Đẩy nhánh (git push) và tạo PR chính thức trên GitHub
```

---

## 6. TIÊU CHUẨN NGHIỆM THU ĐỊNH LƯỢNG (ACCEPTANCE CRITERIA)

- [ ] **AC-1 (Protocol Invariant)**: `WORKSPACE_PROTOCOL.md` tồn tại, phản ánh đúng 5 vai trò SLPPC, quy tắc SPOC và Single-Ownership.
- [ ] **AC-2 (Plugin Architecture)**: `plugins/slpc-lifecycle-hooks` đầy đủ `index.client.tsx`, `index.server.ts`, `server/observer.ts`, `server/kev.ts`, `shared/supervision.ts`, tích hợp Command Center *"Set this thread as Supervisor"*.
- [ ] **AC-3 (Auto-Approval & Security)**: Duy trì 100% auto-allow cho các lệnh an toàn (`git`, `tools/`, `scripts/`, `unittest`) và chặn đứng `rm -rf /`.
- [ ] **AC-4 (Ephemeral Orchestration)**: Peer tự hủy tab khi nộp `Resolved`; QC tự hủy tab khi duyệt `Closed`; đưa RAM nền về 0.
- [ ] **AC-5 (Smoke Discovery)**: Chạy `python3 tools/smoke_discovery.py` phát hiện chính xác toàn bộ skills/plugins mà không phát sinh lỗi cú pháp hay tốn token LLM.
- [ ] **AC-6 (Test & Governance Integrity)**: 100% unit tests PASS ($\ge 92$ tests), `slppc_flow_guard.py audit` đạt 0 vi phạm, `anti_leak_sentinel.py` đạt PASS tuyệt đối.
- [ ] **AC-7 (Clean Commits & PR)**: Commit theo các bước rõ ràng, không hardcode path cá nhân, sẵn sàng merge vào `main`.
