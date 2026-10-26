# AGENTS.md - Global Workspace Directives, Multi-Agent Architecture & Setup Guide

> **QUY CHUẨN ĐỒNG BỘ TOÀN HỆ THỐNG**: Mọi Agent hoạt động trong workspace `Room_Agent` phải tuân thủ nghiêm ngặt các nguyên tắc, đường dẫn chuẩn và luồng phối hợp kế thừa từ Master Architecture Spec:
> - `docs/spec/ephemeral-sub-agent-orchestration-spec.md` (ARCH-SPEC-EPHEMERAL-SUBAGENT-ORCHESTRATION-2026-V1)
> - `docs/spec/harness-cli-v0.1.14-upgrade-spec.md` (SLPPC Native Governance)

---

## 1. Workspace Identity & Canonical Paths

- **Root Workspace**: Đường dẫn thư mục gốc `Room_Agent`.
- **BMAD Central Brain**: `bmad/` (Đồ thị kiến trúc, luồng module, meeting rooms, violations log).
- **Canonical Skills**: `profiles/<role>/skills/` và `profiles/shared/skills/` (Phân quyền theo vai trò: `supervisor`, `lead`, `peer`, `qc`, `shared`).
- **Agent Profiles**: `profiles/<role>/PROFILE.md` (4 hồ sơ chuẩn: `supervisor`, `lead`, `peer`, `qc` kèm YAML frontmatter `permissions`).
- **Core CLI Tools**: `tools/` (21 Python CLI tools chuẩn hóa 6 nhóm nghiệp vụ).
- **Execution Scripts**: `scripts/` (Scripts cài đặt, khởi động phòng, cấu hình RTK proxy, CI guards).
- **Harness Cloud Storage**: Floci DynamoDB & S3 (`http://<FLOCI_HOST>:14566`, Web UI `http://<FLOCI_HOST>:4566`).
- **Subprojects (FE Source)**:
  - `projects/demo-crm-fe` (Angular 18, Nx, Rsbuild, Module Federation, TDS UI).
  - `projects/demo-pos-fe` (Angular 18, Nx, Rsbuild/Webpack, Module Federation).
- **Model Standard**: Bắt buộc toàn bộ Agent Profiles trong phòng sử dụng model `ag/gemini-3.8-flash-high`.

---

## 2. Multi-Agent Roles & 4-Role Governance Gate (SLPC Architecture)

Mọi tác vụ phải tuân thủ nghiêm ngặt quy trình chuyển giao qua 4 vai trò kiểm soát SLPC:

```text
[Yêu cầu từ User]
       │
       ▼
1. Supervisor (Scope & Intent Guard) ──► Tiếp nhận ý định, thẩm định Khả thi/Phù hợp qua Kev System One (<50ms), khống chế trần loop
       │
       ▼
2. Lead (Architect & Technical PM) ────► Thiết kế kiến trúc, tra cứu bẫy lỗi cũ, phân rã Zero-Search
       │
       ▼
3. Peer (Code Executor / Maker Pool) ──► Lập trình theo spec, tuân thủ Angular 18/TDS, nộp Resolved
       │
       ▼
4. QC (Quality Gate & Test Architect) ─► Sinh testcase ISTQB 5-Stage, độc quyền nghiệm thu & Closed
       │
       ▼
[Task CLOSED]
```

### Chi tiết 4 vai trò SLPC & An ninh Sentinel:
1. **Supervisor (`supervisor`)**: Scope & Intent Guard (Macro Governor & Product Decision Arbiter — sáp nhập PM). Tiếp nhận yêu cầu từ User, thẩm định Khả thi (Feasibility 0..3) và Phù hợp (Alignment) qua Kev System One (<50ms), khống chế trần vòng lặp (Turn Ceiling $\le$ 3) trước khi tạo Epic/Task/Story trên Harness DB (`--engine auto`). Nghiêm cấm đào sâu đọc mã nguồn/debug chi tiết (`role_trespass`). Quản trị trần đồng thời (Concurrency Ceiling max 3–5 workers), kích hoạt Zombie Reaper quét terminal mồ côi. Tuyệt đối không can thiệp code thô.
2. **Lead (`lead`)**: Technical Architect & Sub-Agent Dispatcher. Tra cứu bài học kinh nghiệm qua `scripts/bin/harness-cli learn query`, thiết kế API Contract / DTO, duyệt giải pháp kỹ thuật và phân rã task Zero-Search 5 thành phần cho Peer. Nghiêm cấm tự ý code (`role_trespass`).
3. **Peer (`peer`, `peer2`, `peer3`, `peer4`, `peer_design`)**: Ephemeral Coding Sub-Agents (Maker Pool). Hoạt động trên Context Window tươi mới (<30k tokens), chỉ chạm vào file được chỉ định (Single-Ownership), thực thi code, chạy test tự động cục bộ và nộp trạng thái `Resolved`. Nghiêm cấm tự tiện đóng task (`premature_close`).
4. **QC (`qc`)**: Independent Quality Gate & Test Architect (Checker Pool). Độc quyền thẩm quyền chuyển trạng thái task sang `Closed`. Sinh test matrix và file spec theo chuẩn ISTQB 5-Stage (`tools/qc_test_generator.py`), xác nhận Acceptance Criteria, ghi nhận bài học kinh nghiệm vào Harness Learn Store, và chạy `tools/slppc_flow_guard.py audit` bảo đảm 100% tuân thủ quy trình.
5. **Security Sentinel (`security_sentinel`)**: Continuous Anti-Leak Gatekeeper & Open-Source Cleanliness Auditor. Giám sát liên tục chống lộ API spec nghiệp vụ, địa chỉ thực tế, domain nội bộ và secrets; sở hữu quyền VETO chặn đứng mọi commit/push vi phạm (`scripts/anti_leak_sentinel.py`).

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

### 3.1. Điều Phối Tự Hành Qua Plugin Hooks (`plugins/slpc-lifecycle-hooks/slppc_orchestrator.py`):
Toàn bộ luồng điều phối chuyển giao giữa các Agent được tự động hóa thông qua chốt chặn vòng đời plugin:
- **Supervisor `agent.turn_ended`**: Tự động gọi Kev System One (<50ms) đánh giá Feasibility & Alignment, xuất `bmad/rooms/supervisor/decision_memo.md`, cập nhật task và đẩy thông báo sang Lead Dev.
- **Lead `agent.turn_ended`**: Phát hiện Zero-Search Task mới, tự động spawn Ephemeral Peer Sub-Agent tab gắn `profiles/peer/PROFILE.md` với đầy đủ AC và test command.
- **Peer `agent.turn_ended` (Resolved)**: Cưỡng chế đóng tab Peer Dev (`orca terminal close` đưa RAM về 0) và tự động spawn Ephemeral QC Sub-Agent tab gắn `profiles/qc/PROFILE.md`.
- **QC `agent.turn_ended` (Closed)**: Cưỡng chế đóng tab QC, nén dọn artifacts vào `bmad/rooms/archive/task_<id>.tar.gz` và bắn thông báo nghiệm thu thành công về tab Supervisor.

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
  - `lead`: `git` ➔ `rtk git`, `diff` ➔ `rtk git diff`, `tsc` ➔ `rtk tsc`.
  - `peer 1..4`: `jest` ➔ `rtk jest`, `tsc` ➔ `rtk tsc`, `cat` ➔ `rtk read -l aggressive`, `git` ➔ `rtk git`.
  - `peer_design`: `diff` ➔ `rtk diff`, `cat` ➔ `rtk read`.
  - `qc`: `jest` ➔ `rtk jest` (failures only), `playwright` ➔ `rtk test`, `err` ➔ `rtk err`.
  - `security_sentinel`: `grep` ➔ `rtk grep`, `diff` ➔ `rtk diff`.

---

## 5. Profile-Based Skills Taxonomy & RBAC Matrix

Kho kỹ năng được cấu trúc trực tiếp theo hồ sơ từng vai trò trong `profiles/<role>/skills/`:

```text
profiles/
├── supervisor/skills/   # slpc-role-governance, systemone, loop-engineering, handoff...
├── lead/skills/         # lead-review, codebase-design, code-review, improve-codebase-architecture...
├── peer/skills/         # rsbuild-angular, mfe-angular-build, tds-ui-usage, tds-ui-figma, debug...
├── qc/skills/           # qc, a11y-debugging, chrome-devtools, tdd...
└── shared/skills/       # Tiện ích nền tảng: git, research, query-read, rtk, harness...
```

- **Khóa phạm vi trong hồ sơ (`profiles/<role>/PROFILE.md`)**:
  - Mỗi profile chỉ nạp danh mục `skills_dirs` tương ứng trong thư mục của mình và `profiles/shared/skills`.
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
`./setup.sh` tự động khởi tạo file `.env` chuẩn với model `ag/gemini-3.8-flash-high` và backend auto-detect nếu file chưa tồn tại.

### Bước 3: Chạy Script Cài Đặt Tự Động 1 Bước (`setup.sh`)
Script thực hiện toàn bộ 6 khâu cài đặt:
```bash
./setup.sh
```
- Khởi tạo thư mục và liên kết Skills vào `~/.hermes/skills/`.
- Cấu hình Git Pre-commit Guard (`.git/hooks/pre-commit`) chặn hardcoded hex và vi phạm vai trò.
- Đồng bộ các Profile SLPPC vào `~/.paseo/config.json` qua `patch_paseo.py`.
- Kiểm tra kết nối và cấu trúc dữ liệu Harness Database (Floci DynamoDB / Local Fallback).

### Bước 4: Khởi Chạy & Quản Trị Agent Tabs (`./cli/agent-start`)
```bash
# Khởi chạy Agent Controller (Supervisor là phiên chính, Lead/Peer/QC chạy ephemeral on-demand):
./cli/agent-start

# Xem trạng thái chi tiết tất cả Agent và nhịp tim:
./cli/agent-start status

# Khởi chạy toàn bộ hoặc một agent cụ thể on-demand:
./cli/agent-start --all
./cli/agent-start peer
```

### Bước 5: Kiểm Tra & Giám Sát Sức Khỏe Phòng Ban
```bash
# 1. Kiểm tra an ninh chống rò rỉ (phải đạt PASS 100%)
python3 scripts/anti_leak_sentinel.py

# 2. Chạy toàn bộ 322+ unit tests của công cụ (yêu cầu spec >= 190+)
python3 -m unittest discover -s tools/tests

# 3. Kiểm tra chốt chặn phân luồng SLPPC & vệ sinh phòng ban
python3 tools/slppc_flow_guard.py audit

# 4. Kiểm tra trạng thái 3 tầng Lifecycle Hooks
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py status

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
   - 100% component FE có tương tác phải gắn directive `tdsTestId` từ `@demo/core`.
   - Naming convention: `<domain>-<component>-<element>-<state?>` (100% tiếng Anh, kebab-case).
   - QC thẩm tra bằng `[tds-test-id="..."]` hoặc helper `getByTdsTestId()`, nghiêm cấm `getByText()` hay class CSS.

---

## 8. Sub-Agent Dispatch Directives & Autonomous Prompt Triggers

Nhằm bảo đảm việc điều phối sub-agent diễn ra mượt mà và tự động trên cả hai môi trường **Orca** (Visual Workspace) và **Paseo** (Headless Daemon), quy chuẩn dưới đây xác lập bản đồ gọi Sub-Agent và các mẫu câu Prompt tự kích hoạt.

### 8.1. Ma Trận Phân Bổ Sub-Agent Theo Vai Trò (Role-to-SubAgent Mapping)

| Vai trò gọi | Sub-Agent cần gọi | Model & Khả năng | Khi nào kích hoạt? | Lệnh thực thi trực tiếp |
| :--- | :--- | :--- | :--- | :--- |
| **Supervisor** | `strategic-reasoning-architect` | `gpt-5` / `gemini-3.8-flash-high` (Codex reasoning) | Thẩm định phạm vi vĩ mô, đánh giá rủi ro hệ thống, chấm điểm Feasibility & Alignment (<50ms) qua Kev System One. | `codex -m "gpt-5" "<nội_dung>"` hoặc `/paseo-advisor` |
| **Lead Dev** | `gemini-codebase-analyzer` | `gemini-3.8-flash-high` (1M+ context) | Quét toàn bộ monorepo tìm điểm chạm, mapping import/DTO trước khi bóc tách Zero-Search. | `gemini --prompt "<yêu_cầu>" --all-files` |
| **Lead Dev** | `strategic-reasoning-architect` | `gpt-5` (Codex reasoning) | Chốt API contract, giải quyết tranh luận kiến trúc khi Peer khiếu nại (Peer Challenge). | `/paseo-advisor` |
| **Lead Dev** | `slpc-qc-verifier` | `gemini-3.8-flash-high` + ISTQB tools | Chuyển giao nghiệm thu khi Peer nộp `Resolved`. | `python3 tools/call_agent.py --profile QC --prompt "Verify Task #<id>"` |
| **Peer Dev** | `gemini-codebase-analyzer` | `gemini-3.8-flash-high` (1M+ context) | Tra cứu nhanh cách dùng component TDS, DTO mẫu mà không làm tràn context chính. | `gemini --prompt "<tìm_kiếm>" --include-directories projects/` |
| **Peer Design** | `tds-ui-usage` / `tds_search.py` | CLI Tool + Vector/BM25 Index | Tra cứu SCSS token, màu sắc, font, spacing TDS UI. | `python3 tools/tds_search.py "<token_hoặc_component>"` |
| **QC Verifier** | `slpc-qc-verifier` | `gemini-3.8-flash-high` + 5-Stage ISTQB | Độc quyền sinh Unit Test, kiểm tra cơ học (Exit 0) và đóng task (`Closed`). | `python3 tools/qc_test_generator.py --source <file> --task-id <id> --run` |

---

### 8.2. So Sánh Cơ Chế Kích Hoạt & Bộ Hook Điều Phối Hai Môi Trường (Orca vs Paseo)

Hệ thống tích hợp **Universal Dual-IDE Hook Router** (`tools/dual_ide_hook.py` & `.claude/hooks/dual_ide_prompt_hook.sh`) tự động đánh chặn prompt tại cả hai IDE:

```text
┌───────────────────────────────────────┬───────────────────────────────────────┐
│       ORCA (Visual Workspace PTY)     │       PASEO (Headless Daemon CLI)     │
├───────────────────────────────────────┼───────────────────────────────────────┤
│ • Giao diện: Tab/Pane trực quan       │ • Giao diện: Chạy ngầm background     │
│ • Cơ chế: On-demand PTY tab launch    │ • Cơ chế: Fork process / subagent     │
│ • Đổi tên: `orca terminal rename`     │ • Đổi tên: `paseo run -d --title`     │
│ • Vòng đời: Tự đóng tab khi `Resolved`│ • Vòng đời: Tự exit(0) giải phóng RAM │
│   và `Closed` đưa RAM nền về 0        │   ngay khi tiến trình kết thúc        │
│ • Đồng bộ: Ghi nhận handle vào        │ • Đồng bộ: Ghi handoff vào            │
│   `bmad/rooms/agent_terminals.json`   │   `bmad/rooms/<role>/latest_handoff`  │
│ • Hook: `.claude/hooks/` + PTY Bridge │ • Hook: `UserPromptSubmit` + Plugin   │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

**Cơ chế hoạt động của Dual-IDE Hook (`tools/dual_ide_hook.py`)**:
1. Nhận diện runtime đang chạy: Nếu có Orca Runtime ➔ Route lệnh sang Orca PTY và Workspace Board; Nếu chạy CLI/Headless ➔ Route sang Paseo Daemon.
2. Tự động quét tiền tố (`[THUẬN]`, `[NGHỊCH]`, `[THẢO-LUẬN]`, `[TÍNH-NĂNG]`, `[FIX-BUG]`, `[BẪY-LỖI]`, `[REFACTOR]`, `[REVIEW]`, `[QUÉT]`, `[TEST]`).
3. Tự động bơm khối `CHỈ THỊ BẮT BUỘC TRONG KHỐI THINKING` vào context của mô hình trước khi suy luận.


---

### 8.3. Mẫu Prompt Tự Kích Hoạt Trong Chat (Prompt Trigger Templates)

Chỉ cần sao chép các mẫu prompt dưới đây và dán vào phiên chat với Supervisor để hệ thống tự động nhận diện và kích hoạt đúng luồng:

#### Mẫu 1: Kích hoạt toàn bộ luồng SLPC 4 cổng tự hành (Full Autonomous Flow)
```text
Kích hoạt flow: [Tên tính năng hoặc yêu cầu nghiệp vụ]
- Target Module: [projects/demo-crm-fe hoặc tools/]
- Mô tả chi tiết: [Mô tả cụ thể hành vi cần làm]
- Tiêu chí nghiệm thu: [Các điều kiện hoàn thành bắt buộc]
```
> **Hệ thống tự động**: Chạy qua Supervisor (Kev System One) ➔ Lead bóc tách Zero-Search ➔ Mở tab Peer thi công ➔ Đóng tab Peer, mở tab QC kiểm thử ISTQB 5-Stage ➔ Đóng tab QC và báo cáo hoàn tất cho Supervisor.

#### Mẫu 2: Phân tích kiến trúc & Đánh đổi kỹ thuật (Gọi `strategic-reasoning-architect`)
```text
/paseo-advisor [Vấn đề kiến trúc hoặc băn khoăn về giải pháp kỹ thuật cần second opinion]
```
hoặc:
```text
Tư vấn kiến trúc: Cần đánh giá trade-off giữa [Phương án A] và [Phương án B] cho module [Tên module].
```

#### Mẫu 3: Quét toàn bộ Codebase & Tìm điểm chạm (Gọi `gemini-codebase-analyzer`)
```text
Quét codebase: Tìm toàn bộ điểm chạm và luồng dữ liệu liên quan đến [Tên Service/Component/API].
```

#### Mẫu 4: Nghiệm thu chất lượng & Sinh Unit Test độc lập (Gọi `slpc-qc-verifier`)
```text
QC verify: Nghiệm thu Task #[ID] tại file [đường_dẫn_source_code] theo chuẩn ISTQB 5-Stage.
```

---

### 8.4. Lệnh Kích Hoạt 1 Chạm Từ Terminal CLI

Ngoài việc ra lệnh trong chat, bạn có thể chạy trực tiếp từ terminal máy trạm:

```bash
# 1. Kích hoạt toàn bộ chu trình 4 vai trò tự hành (Supervisor ➔ Lead ➔ Peer ➔ QC):
./cli/trigger-flow "Nâng cấp tính năng X trên module Y"

# 2. Hoặc dùng script chi tiết với tùy chọn test:
python3 scripts/run_pipeline.py "Nâng cấp tính năng X" --test-cmd "pytest ..."

# 3. Kích hoạt riêng một vai trò Sub-Agent trong Orca / Paseo:
python3 tools/call_agent.py --profile Lead --prompt "Thiết kế API contract cho tính năng X"
python3 tools/call_agent.py --profile Peer --prompt "Thi công code tính năng X theo spec" --item-id <id>
python3 tools/call_agent.py --profile QC --prompt "Nghiệm thu Task #<id> với ISTQB 5-Stage" --item-id <id>
```

---

### 8.5. Tiền Tố Định Hướng Tư Duy Thuận - Nghịch (Dual-Anchor Thinking Prefixes)

Để Agent và Sub-Agent suy luận đúng trọng tâm cho cả trường hợp thuận (Happy Path) và trường hợp nghịch (Adversarial/Edge Cases), hệ thống tích hợp bộ bóc tách tiền tố tự động:

| Tiền tố (Prefix) | Ý nghĩa nghiệp vụ | Hành vi tư duy của Agent (Thinking Directive) |
| :--- | :--- | :--- |
| **`[THUẬN]`**<br>`[FORWARD]`<br>`[HAPPY-PATH]` | **Luồng Thuận (Happy Path / Golden Flow)** | Tập trung hoàn thiện nhanh luồng chạy chuẩn: input hợp lệ, kết quả mong đợi, DTO chuẩn, tối ưu diff theo triết lý Lazy Senior Dev / YAGNI, không over-engineering. |
| **`[NGHỊCH]`**<br>`[REVERSE]`<br>`[EDGE-CASE]`<br>`[ADVERSARIAL]` | **Luồng Nghịch (Adversarial / Edge-Cases / Negative)** | Tập trung truy quét kịch bản biên và bẫy lỗi: dữ liệu rỗng/null/undefined, boundary values (BVA), timeout mạng, race condition, fail-safe degradation, rollback và cơ chế chống crash. |
| **`[THẢO-LUẬN]`**<br>`[THẢO LUẬN]`<br>`[DISCUSS]` | **Luồng Thảo Luận Kiến Trúc (Architectural ADR)** | **KHÔNG viết code**. Supervisor thẩm định tính khả thi (<50ms) ➔ Lead Dev & Sub-Agents phân tích đánh đổi (trade-offs) ➔ Tự động chốt giải pháp đồng thuận và lưu biên bản ADR vĩnh viễn tại `bmad/rooms/discussions/` & `bmad/adrs/`. |
| **`[LƯỠNG-DIỆN]`**<br>`[DUAL]`<br>`[BOTH]`<br>*(Mặc định)* | **Lưỡng Diện (Dual-Anchor Thinking)** | BẮT BUỘC Agent tư duy 2 mặt song song trong khối Thinking:<br>1. `[THUẬN]`: Mặt thuận đáp ứng spec cốt lõi, hoàn tất AC.<br>2. `[NGHỊCH]`: Mặt nghịch bao phủ các bẫy lỗi và rủi ro phá vỡ kiến trúc. |

**Ví dụ thực tế**:
- Luồng Thuận: `./cli/trigger-flow "[THUẬN] Tạo modal xác nhận xóa đơn hàng"`
- Luồng Nghịch: `./cli/trigger-flow "[NGHỊCH] Kiểm thử race condition khi 2 user cùng bấm thanh toán đơn hàng #123"`
- Luồng Thảo Luận: `./cli/trigger-flow "[THẢO LUẬN] Đánh giá phương án xác thực JWT vs HttpOnly Cookie"`
- Luồng Lưỡng Diện: `./cli/trigger-flow "[LƯỠNG-DIỆN] Refactor module auth token sang HttpOnly cookie"`

---

### 8.6. Quy Tắc Vệ Sinh Context & Lệnh Dọn Dẹp Sub-Agent (Anti-Context Bloat)

Việc duy trì Sub-Agent chạy lâu dài qua nhiều task sẽ khiến **Context Window phình to (200k–500k tokens)**, làm tăng chi phí token gấp 5–10 lần, kéo dài độ trễ phản hồi (từ 2s lên 30s+) và sinh lỗi ảo giác ("ngáo" do nhiễm chéo biến/import của task cũ).

**4 Cơ Chế Chống Phình To Context (Anti-Bloat Protocol)**:
1. **Tự Hủy Ephemeral Sub-Agent (Single-Task Lifespan)**:
   - `Peer Dev` nộp `Resolved` ➔ Tự động đóng tab Orca (`orca terminal close`) đưa RAM và Context về 0.
   - `QC Verifier` duyệt `Closed` ➔ Tự động đóng tab Orca đưa RAM và Context về 0.
   - Mọi task Zero-Search mới mở ra đều bắt đầu trên một **Context Window tinh khôi (<15k tokens)**.
2. **Tự Động Nén Context Cho Vai Trò Thường Trực (`Supervisor`, `Lead`)**:
   - `tools/agent_context_manager.py` theo dõi token ngầm với ngưỡng trần theo vai trò (Peer/QC $\le$ 30k, Lead $\le$ 60k, Supervisor $\le$ 100k).
   - Khi vượt ngưỡng, tự động gửi lệnh `/compact` vào terminal, gọt tỉa 60%–70% token lịch sử thừa nhưng vẫn bảo toàn trạng thái trên đĩa cứng (`.harness_progress.json`).
3. **Lệnh Dọn Dẹp Tức Thì 1 Chạm (Manual Context Purge)**:
   ```bash
   ./cli/agent-start clear    # Đóng toàn bộ tab Sub-Agent (Peer, QC, Design), giữ lại Lead
   ./cli/agent-start stop --all # Đóng sạch toàn bộ
   ```
4. **Zombie Terminal Reaper (`tools/zombie_reaper.py`)**:
   - Khống chế trần thời gian tối đa **300 giây (5 phút)**. Tự động thu hồi các terminal mồ côi không có task Active bảo trợ.



