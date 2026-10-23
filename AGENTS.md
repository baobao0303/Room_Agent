# AGENTS.md - Global Workspace Directives, Multi-Agent Architecture & Setup Guide

> **QUY CHUẨN ĐỒNG BỘ TOÀN HỆ THỐNG**: Mọi Agent hoạt động trong workspace `Room_Agent` phải tuân thủ nghiêm ngặt các nguyên tắc, đường dẫn chuẩn và luồng phối hợp kế thừa từ Master Architecture Spec:
> - `docs/spec/ephemeral-sub-agent-orchestration-spec.md` (ARCH-SPEC-EPHEMERAL-SUBAGENT-ORCHESTRATION-2026-V1)
> - `docs/spec/harness-cli-v0.1.14-upgrade-spec.md` (SLPPC Native Governance)

---

## 1. Workspace Identity & Canonical Paths

- **Root Workspace**: Đường dẫn thư mục gốc `Room_Agent`.
- **BMAD Central Brain**: `bmad/` (Đồ thị kiến trúc, luồng module, meeting rooms, violations log).
- **Canonical Skills**: `skills/` (Phân tầng 7 nhóm RBAC theo vai trò: `supervisor`, `pm`, `lead`, `peer`, `qc`, `security`, `shared`).
- **Agent Profiles**: `profiles/` (10 hồ sơ MD có YAML frontmatter `skills_dirs` và `permissions`).
- **Core CLI Tools**: `tools/` (21 Python CLI tools chuẩn hóa 6 nhóm nghiệp vụ).
- **Execution Scripts**: `scripts/` (Scripts cài đặt, khởi động phòng, cấu hình RTK proxy, CI guards).
- **Harness Cloud Storage**: Floci DynamoDB & S3 (`http://<FLOCI_HOST>:14566`, Web UI `http://<FLOCI_HOST>:4566`).
- **Subprojects (FE Source)**:
  - `projects/wicx-crm-fe` (Angular 18, Nx, Rsbuild, Module Federation, TDS UI).
  - `projects/wion_pos_fe` (Angular 18, Nx, Rsbuild/Webpack, Module Federation).
- **Model Standard**: Bắt buộc toàn bộ Agent Profiles trong phòng sử dụng model `ag/gemini-3.8-flash-high`.

---

## 2. Multi-Agent Roles & 5-Stage Governance Gate (SLPPC)

Mọi tác vụ phải tuân thủ nghiêm ngặt quy trình chuyển giao qua 5 cổng kiểm soát SLPPC:

```text
[Yêu cầu từ User]
       │
       ▼
1. Supervisor (Scope & Intent Guard) ──► Tiếp nhận ý định User, phân tích phạm vi, khống chế chi phí
       │
       ▼
2. PM Agent (Feasibility & Alignment) ─► Thẩm định Khả thi / Phù hợp qua Kev System One (<50ms) & Loop Gate
       │
       ▼
3. Lead (Architect & Technical PM) ────► Thiết kế kiến trúc, tra cứu bẫy lỗi cũ, phân rã Zero-Search
       │
       ▼
4. Peer (Code Executor / Dev 1..4) ───► Lập trình theo spec, tuân thủ Angular 18/TDS, nộp Resolved
       │
       ▼
5. QC (Quality Gate & Test Architect) ─► Sinh testcase ISTQB 5-Stage, độc quyền nghiệm thu & Closed
       │
       ▼
[Task CLOSED]
```

### Chi tiết 6 vai trò SLPPC & An ninh Sentinel:
1. **Supervisor (`supervisor`)**: Scope & Intent Guard (Macro Governor). Tiếp nhận yêu cầu từ User, BẮT BUỘC kết nối PM Agent (`pm`) thẩm định Khả thi / Phù hợp trước khi tạo Epic/Task/Story trên Harness DB (`--engine auto`). Nghiêm cấm đào sâu đọc mã nguồn/debug chi tiết (`role_trespass`) hoặc bỏ qua cổng PM (`pm_bypass`). Quản trị trần đồng thời (Concurrency Ceiling max 3–5 workers), kích hoạt Zombie Reaper quét terminal mồ côi. Tuyệt đối không can thiệp code thô.
2. **PM Agent (`pm`)**: Product Manager, Decision Arbiter & Loop Enforcer (Issue #4). Thẩm định **Khả thi (Feasibility)** và **Phù hợp (Alignment)** qua Kev System One (<50ms). Sở hữu kỹ năng `loop-engineering`, thiết lập trần vòng lặp (**Turn Ceiling $\le$ 3–5 lần thử**) và kiểm tra Mechanical Stop Gate trước khi giao task. Chặn đứng lỗi `pm_bypass`.
3. **Lead (`lead`)**: Technical Architect & Sub-Agent Dispatcher. Tra cứu bài học kinh nghiệm qua `scripts/bin/harness-cli learn query`, thiết kế API Contract / DTO, duyệt giải pháp kỹ thuật và phân rã task Zero-Search 5 thành phần cho Peer. Nghiêm cấm tự ý code (`role_trespass`).
4. **Peer (`peer`, `peer2`, `peer3`, `peer4`, `peer_design`)**: Ephemeral Coding Sub-Agents (Maker Pool). Hoạt động trên Context Window tươi mới (<30k tokens), chỉ chạm vào file được chỉ định (Single-Ownership), thực thi code, chạy test tự động cục bộ và nộp trạng thái `Resolved`. Nghiêm cấm tự tiện đóng task (`premature_close`).
5. **QC (`qc`)**: Independent Quality Gate & Test Architect (Checker Pool). Độc quyền thẩm quyền chuyển trạng thái task sang `Closed`. Sinh test matrix và file spec theo chuẩn ISTQB 5-Stage (`tools/qc_test_generator.py`), xác nhận Acceptance Criteria, ghi nhận bài học kinh nghiệm vào Harness Learn Store, và chạy `tools/slppc_flow_guard.py audit` bảo đảm 100% tuân thủ quy trình.
6. **Security Sentinel (`security_sentinel`)**: Continuous Anti-Leak Gatekeeper & Open-Source Cleanliness Auditor. Giám sát liên tục chống lộ API spec nghiệp vụ, địa chỉ thực tế, domain nội bộ và secrets; sở hữu quyền VETO chặn đứng mọi commit/push vi phạm (`scripts/anti_leak_sentinel.py`).

---

## 3. Ephemeral Sub-Agent Architecture ("Ephemeral by Default, Persistent by Exception")

Hệ sinh thái chuyển dịch từ nhóm Agent thường trực (Persistent Worker Pool) sang mô hình Sub-Agent tạm thời dùng xong tự hủy:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MÔ HÌNH ĐIỀU HÀNH EPHEMERAL SUB-AGENT TỔNG QUAN              │
│                                                                             │
│   [COORDINATOR / SUPERVISOR] (Single Persistent Session)                    │
│   ├── Tiếp nhận yêu cầu từ User / Backlog                                   │
│   ├── Phân tích phạm vi, rủi ro và chia nhỏ thành Task Zero-Search          │
│   │                                                                         │
│   ├── 🚀 KÍCH HOẠT THEO YÊU CẦU (ON-DEMAND DISPATCH):                       │
│   │   ├── Task A: Sinh Sub-Agent A (Context sạch 10k) ➔ Xong việc ➔ TỰ HỦY  │
│   │   ├── Task B: Sinh Sub-Agent B (Context sạch 15k) ➔ Xong việc ➔ TỰ HỦY  │
│   │   └── Task C: Sinh Sub-Agent C (Context sạch 20k) ➔ Xong việc ➔ TỰ HỦY  │
│   │                                                                         │
│   └── 📊 Thu thập kết quả báo cáo ➔ Kiểm định độc lập ➔ Trả lời User       │
│                                                                             │
│   KẾT QUẢ: Token tiêu hao giảm 70%, RAM nền về 0, Triệt tiêu 100% "Ngáo"     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Bộ Khung 6 Trụ Cột Quản Trị Sub-Agent:
1. **Concurrency Ceiling (Giới hạn trần đồng thời)**: Khống chế tối đa **không quá 3–5 Sub-Agents chạy song song** cùng thời điểm để tránh nghẽn CPU và chạm rate-limit API.
2. **6-Phase State Machine**: Mọi Sub-Agent chuyển dịch tuần tự: `SPAWNED` ➔ `ALLOCATED` ➔ `EXECUTING` ➔ `REPORTED` ➔ `VERIFIED` ➔ `REAPED`.
3. **Watchdog Daemon & Timeout Ceiling**: Hard timeout tối đa **300 giây (5 phút)**. Tự động gửi ngắt (`orca terminal send --interrupt`) hoặc cưỡng chế đóng terminal khi bị treo.
4. **Mechanical Verification**: Tuyệt đối không tin lời tự khai ("Never let the AI verify its own done"). Bắt buộc kiểm tra Exit Code 0, Git Diff thật và Output Test Runner thật trước khi chấp nhận nghiệm thu.
5. **Zombie Terminal Reaper (`tools/zombie_reaper.py`)**: Định kỳ quét đối chiếu terminals đang mở với danh sách task Active trong Harness DB; tự động đóng các PTY mồ côi để đưa RAM nền về 0.
6. **Authority Fencing (Rào cản thẩm quyền)**: Cấm Sub-Agent spawn đệ quy (No nested delegation), cấm tự đóng task, cấm ghi đè bộ nhớ hệ thống.

---

## 4. RTK (Rust Token Killer) CLI Proxy (Issue #5)

Dự án tích hợp bộ proxy hiệu năng cao viết bằng Rust thuần (`rtk`) đánh chặn các lệnh CLI phổ biến, nén từ **60% đến 90% output** trước khi nạp vào context LLM:

- **Bộ biến môi trường bắt buộc**:
  ```bash
  export RTK_TELEMETRY_DISABLED=1
  export RTK_COMPACT_MODE=1
  export RTK_TEST_FAILURES_ONLY=1
  ```
- **Ma trận Alias Per-Profile (`scripts/rtk_profile_env.sh`)**:
  - `supervisor`: `git` ➔ `rtk git`, `log` ➔ `rtk git log -n 5`, `gain` ➔ `rtk gain`.
  - `pm`: `diff` ➔ `rtk diff`, `find` ➔ `rtk find`.
  - `lead`: `git` ➔ `rtk git`, `diff` ➔ `rtk git diff`, `tsc` ➔ `rtk tsc`.
  - `peer 1..4`: `jest` ➔ `rtk jest`, `tsc` ➔ `rtk tsc`, `cat` ➔ `rtk read -l aggressive`, `git` ➔ `rtk git`.
  - `peer_design`: `diff` ➔ `rtk diff`, `cat` ➔ `rtk read`.
  - `qc`: `jest` ➔ `rtk jest` (failures only), `playwright` ➔ `rtk test`, `err` ➔ `rtk err`.
  - `security_sentinel`: `grep` ➔ `rtk grep`, `diff` ➔ `rtk diff`.

---

## 5. Profile-Based Skills Taxonomy & RBAC Matrix

Kho kỹ năng được tái cấu trúc thành 7 nhóm phân tầng theo vai trò chuyên biệt, loại bỏ cấu trúc phẳng:

```text
skills/
├── supervisor/       # slpc-role-governance, chief-of-staff, handoff, workflow-launch-exec...
├── pm/               # pm-decision-governance, systemone, loop-engineering, ba, to-spec...
├── lead/             # lead-review, codebase-design, code-review, improve-codebase-architecture...
├── peer/             # rsbuild-angular, mfe-angular-build, tds-ui-usage, tds-ui-figma, debug...
├── qc/               # qc, a11y-debugging, chrome-devtools, tdd...
├── security/         # fewer-permission-prompts, permissioned-github...
└── shared/           # Tiện ích nền tảng: git, research, terminal, query-read...
```

- **Khóa phạm vi trong hồ sơ (`profiles/<name>.md`)**:
  - Mỗi profile chỉ nạp danh mục `skills_dirs` tương ứng: `skills/<profile>` và `skills/shared`.
  - Lập trình viên không thể gọi tool của quản lý; người quản lý không thể dùng tool can thiệp code thô.

---

## 6. Hướng Dẫn Cài Đặt & Khởi Động Lại Phòng (Setup & Room Launch Guide)

Sau khi clone hoặc merge mã nguồn mới, thực hiện quy trình cài đặt và kích hoạt lại toàn bộ phòng ban:

### Bước 1: Chuẩn Bị Môi Trường & Công Cụ Cơ Sở
- Cài đặt công cụ bắt buộc: `git`, `python3` ($\ge 3.11$).
- Cài đặt Rust Token Killer (RTK):
  ```bash
  curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  rtk --version  # Xác nhận phiên bản (vd: rtk 1.0.1)
  ```
- Nếu dùng Orca IDE: Đảm bảo lệnh `orca` có trong PATH (`~/.config/orca/linux-orca-cli-shim` hoặc Orca Desktop AppImage).

### Bước 2: Khởi Tạo File Cấu Hình `.env`
```bash
cp .env.example .env
# Kiểm tra FLOCI_ENDPOINT (mặc định: http://<FLOCI_HOST>:14566)
```

### Bước 3: Chạy Script Cài Đặt Tự Động 1 Bước (`setup.sh`)
Script thực hiện toàn bộ 6 khâu cài đặt:
```bash
./setup.sh
```
- Khởi tạo thư mục và liên kết Skills vào `~/.hermes/skills/`.
- Cấu hình Git Pre-commit Guard (`.git/hooks/pre-commit`) chặn hardcoded hex và vi phạm vai trò.
- Đồng bộ các Profile SLPPC vào `~/.paseo/config.json` qua `patch_paseo.py`.
- Kiểm tra kết nối và cấu trúc dữ liệu Harness Database (Floci DynamoDB).

### Bước 4: Khởi Chạy Các Agent Tabs Thường Trực Trong Phòng Ban
```bash
# Khởi chạy 2 Agent Tabs thường trực (PM, Lead). Supervisor là tab hiện hành.
# Peer 1..4, Design, QC là Ephemeral Sub-Agents kích hoạt on-demand khi có task.
./scripts/launch_room.sh

# Hoặc vừa setup vừa launch:
./setup.sh --launch
```

### Bước 5: Kiểm Tra & Giám Sát Sức Khỏe Phòng Ban
```bash
# 1. Kiểm tra an ninh chống rò rỉ (phải đạt PASS 100%)
python3 scripts/anti_leak_sentinel.py

# 2. Chạy toàn bộ 26 unit tests của công cụ
python3 -m unittest discover -s tools/tests

# 3. Quét Zombie Terminals mồ côi và Watchdog timeout
python3 tools/zombie_reaper.py --dry-run

# 4. Kiểm tra trạng thái Backlog & Work Items
python3 tools/harness_manager.py stats
./scripts/harness query backlog

# 5. Kiểm tra nhịp tim các Agent
python3 tools/agent_heartbeat.py status
```

---

## 7. Quy Chuẩn Lập Trình & Kiểm Soát Chất Lượng (Quality Gates)

1. **Lazy Senior Developer Philosophy**:
   - Stdlib & Native Platform trước tiên.
   - Diff ngắn gọn, giữ nguyên code style hiện tại, không thêm boilerplate thừa.
2. **Path Integrity**:
   - Luôn sử dụng đường dẫn tuyệt đối khi thao tác file.
3. **Session Continuity & Handoff Rule**:
   - Khi User yêu cầu *"làm tiếp"* hoặc *"báo cáo tiến độ"*, Agent bắt buộc đọc `docs/AGENT_PROGRESS.md` (hoặc chạy `python3 tools/agent_progress.py status`) trước tiên.
   - Trước khi kết thúc phiên hoặc dừng chờ User, Agent bắt buộc cập nhật tiến độ qua `python3 tools/agent_progress.py log ...`.
4. **Zero-Search Task Specification Standard (5 Thành Phần Bắt Buộc)**:
   Khi Supervisor/Lead giao việc cho Peer, task BẮT BUỘC phải đủ 5 thông tin định danh, nghiêm cấm mô tả 1 dòng mơ hồ:
   1. `Target Files`: Đường dẫn file cụ thể (Single-Ownership).
   2. `Anchors / Line Numbers`: Tên hàm, class, selector, hoặc block code cần can thiệp.
   3. `Concrete Changes`: Logic chi tiết, kiểu dữ liệu, token TDS hoặc payload JSON cụ thể.
   4. `Acceptance Criteria (AC)`: Tiêu chuẩn nghiệm thu định lượng (pass test suite nào).
   5. `Test Command`: Lệnh kiểm tra cơ học cụ thể (vd: `npx jest path/to/spec`).
5. **Strict Typing Gate: Zero `any`, Zero `unknown`, Zero Sloppy Fallbacks (`||`)**:
   - Cấm dùng `any`, `unknown`, `as any` hoặc chuỗi fallback `||` chắp vá trong mã nguồn FE.
   - QC bắt buộc chạy `python3 tools/strict_typing_scanner.py <path>` rà soát diff; nếu phát hiện vi phạm, lập tức REJECT task.
6. **Anti-Leak & Sensitive Data Gate**:
   - Tuyệt đối cấm đưa tên công ty nội bộ, địa chỉ thực tế, số điện thoại, email cá nhân, mã số thuế hoặc API token vào mã nguồn, commit Git hoặc PR công khai.
   - Bắt buộc chạy `python3 scripts/anti_leak_sentinel.py` fail-closed trước khi commit/push.
7. **TDS Test ID & Testing Contract Gate**:
   - 100% component FE có tương tác phải gắn directive `tdsTestId` từ `@wicx/core`.
   - Naming convention: `<domain>-<component>-<element>-<state?>` (100% tiếng Anh, kebab-case).
   - QC thẩm tra bằng `[tds-test-id="..."]` hoặc helper `getByTdsTestId()`, nghiêm cấm `getByText()` hay class CSS.
