# AGENTS.md - Global Workspace Directives & Multi-Agent Execution Protocols

> **QUY CHUẨN ĐỒNG BỘ TOÀN HỆ THỐNG**: Mọi Agent hoạt động trong workspace `/home/baoltb/Desktop/Paseo_Project` phải tuân thủ nghiêm ngặt các nguyên tắc, đường dẫn chuẩn và luồng phối hợp kế thừa từ **Obsidian Knowledge Base** (`/home/baoltb/Desktop/obsidian-obsidian`).

---

## 1. Workspace Identity & Canonical Paths

- **Root Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **BMAD Central Brain**: `/home/baoltb/Desktop/Paseo_Project/bmad` (Knowledge Graph, Architecture & Data Flows)
- **Paseo Daemon Plugins**: `/home/baoltb/Desktop/Paseo_Project/plugins` (Lifecycle hooks, environment & approval bridge)
- **Frontend Source Code**: `/home/baoltb/Desktop/Paseo_Project/projects/crm-fe` (Angular 18, Module Federation, Nx, UI-Lib)
- **REMOTE Docs Repository**: `/home/baoltb/Desktop/crm-doc` (REMOTE `_git/crm` branch `docs/base`)
- **Obsidian Knowledge Base**: `/home/baoltb/Desktop/obsidian-obsidian` (Specs, ADRs, Protocols, Beats, Metas)
- **Harness Cloud Storage**: Floci DynamoDB & S3 (`http://<FLOCI_HOST>:14566`, Web UI `http://<FLOCI_HOST>:4566`)
- **REMOTE Azure DevOps Server**: `https://remote.example.com/MainCollection/ACME` (via MCP `remote-crm`)

---

## 2. Team Multi-Agent Roles & Workflow Gates (SLPPC)

Mọi tác vụ phải tuân thủ nghiêm ngặt quy trình chuyển giao qua 5 cổng kiểm soát SLPPC:

```text
[Yêu cầu từ User]
       │
       ▼
1. Supervisor (Scope & Intent Guard) ──► Phân tích scope, tiếp nhận ý định User
       │
       ▼
2. PM Agent (Feasibility & Alignment) ─► Thẩm định Khả thi / Phù hợp qua Kev System One (<50ms)
       │
       ▼
3. Lead (Architect & Technical PM) ────► Thiết kế kiến trúc, tra cứu bài học cũ, phân rã Zero-Search
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

### Chi tiết vai trò SLPPC, Cố vấn PM & An ninh Sentinel:
1. **Supervisor (`supervisor`)**: Scope & Intent Guard. Tiếp nhận yêu cầu từ User, phân tích phạm vi, tạo Epic/Task/Story trên Harness DB (`--engine auto`), điều phối PM/Lead/Peer và kiểm soát chi phí/rủi ro.
2. **PM Agent (`pm`)**: Product Manager & Decision Arbiter (Kev System One Engine). Cố vấn định lượng ngầm cho Supervisor & Lead Dev: đánh giá mức độ **Khả thi (Feasibility)** và mức độ **Phù hợp (Alignment)**, tính điểm rủi ro và phân luồng sub-50ms trước khi phân rã task. Chặn đứng lỗi `pm_bypass`.
3. **Lead (`lead`)**: Technical Architect & PM. Phân tích tài liệu nghiệp vụ, tra cứu bài học kinh nghiệm qua `harness learn query`, thiết kế kiến trúc hệ thống, API Contract, duyệt giải pháp kỹ thuật và phân rã task Zero-Search cho Peer. Nghiêm cấm tự ý code (`role_trespass`).
4. **Peer (`peer`, `peer2`, `peer3`, `peer4`)**: Code Executor (Developer). Hiện thực hóa mã nguồn theo spec, tuân thủ Angular 18 + TDS UI Design System, viết unit test và chuyển task sang `Resolved`. Nghiêm cấm tự tiện đóng task (`premature_close`).
5. **QC (`qc`)**: Independent Quality Gate & Test Architect. Độc quyền quyền hạn chuyển trạng thái task sang `Closed`. Nghiệm thu độc lập, sinh testcase theo chuẩn ISTQB 5-Stage (`tools/qc_test_generator.py`), xác nhận Acceptance Criteria, ghi nhận bài học kinh nghiệm vào `harness learn record`, và chạy `tools/slppc_flow_guard.py audit` bảo đảm 100% tuân thủ quy trình trước khi đóng Epic.
6. **Security Sentinel (`security`)**: Continuous Anti-Leak Gatekeeper & Open-Source Auditor. Giám sát liên tục chống lộ API spec tính năng, luồng nghiệp vụ FE, địa chỉ công ty và secrets; sở hữu quyền VETO chặn đứng mọi commit/push vi phạm.

---

## 3. Available Tools & Skills Index

### A. Harness Manager Tool (`tools/harness_manager.py` / Skill `harness-ops`)
- **Lưu trữ**: Floci DynamoDB endpoint `http://<FLOCI_HOST>:14566` (tables `harness_work_items`, `harness_stories`, `harness_tools`, `harness_metadata`) và SQLite local (`harness.db`).
- **Engine**: Hỗ trợ cờ `--engine {auto,floci,rust,sqlite}` (mặc định: `auto`).
- **Lệnh thực thi**:
  - Xem ma trận kiểm thử: `./scripts/harness query matrix`
  - Xem backlog đa chiều: `./scripts/harness query backlog [--sprint <sprint>] [--source remote|local] [--top 25]`
  - Xem thống kê: `python3 tools/harness_manager.py [--engine auto] stats` | `./scripts/harness query stats`
  - Đồng bộ lại từ REMOTE: `./scripts/harness sync-remote`
  - Thêm mới / Cập nhật trạng thái: `python3 tools/harness_manager.py [--engine auto] add ...` | `python3 tools/harness_manager.py [--engine auto] update ...`

### A2. SLPPC Flow Guard & Automated Violation Auditor (`tools/slppc_flow_guard.py`)
- **Mục đích**: Canh gác tự động rào cản thẩm quyền 5 vai trò SLPPC, ngăn chặn `role_trespass` (Lead ôm code), `pm_bypass` (bỏ qua cổng PM), `premature_close` (Dev tự đóng task), `vague_specs` (giao task cẩu thả).
- **Biên bản vi phạm**: Lưu tự động và vĩnh viễn tại `bmad/rooms/violations/violation_<task_id>_<from>_to_<to>_<timestamp>.md`.
- **Lệnh thực thi**: `python3 tools/slppc_flow_guard.py audit [--json]`

### A3. Harness Native Rust Bridge (`tools/harness_rust.py`)
- **Mục đích**: Cầu nối Python gọi trực tiếp binary Rust native v0.1.14 (`scripts/bin/harness-cli`) và mô hình quyết định Kev System One.
- **Hàm cốt lõi**: `supervise_task(text)` (sub-50ms routing), `record_lesson(...)` (ghi đồng thời SQLite + DynamoDB), `query_lessons(domain)` (truy vấn bẫy lỗi).

### B. REMOTE ACME MCP Server (`tools/remote_mcp_server.py`)
- **Server**: `remote-crm` (cấu hình trong `~/.gemini/config/mcp_config.json`).
- **Tools**: `remote_list_work_items`, `remote_get_work_item`, `remote_query_wiql`, `remote_list_repositories`, `remote_list_pull_requests`, `remote_search_use_cases`, `remote_get_use_case`, `remote_sync_docs`, `remote_list_doc_tree`, `remote_git_status`, `remote_git_log`.

### C. Query Reader Tool (`tools/query_reader.py` / Skill `query-read`)
- **Mục đích**: Duyệt cấu trúc thư mục chống lỗi `EISDIR`, tìm kiếm ngữ cảnh chính xác cao bằng thuật toán BM25.
- **Lệnh thực thi**: `python3 tools/query_reader.py <folder_path> ["<từ_khóa>"]`

### D. TDS UI & Figma Tools (`tools/tds_search.py`, Skill `tds-ui-usage`, `tds-ui-figma`)
- **`tds-ui-figma`**: Token lookup, chuyển đổi Figma node sang TDS Angular component và tokens `tds-color-*`.
- **`tds-ui-usage`**: Danh mục gần 80 components UI Lib, recipes, troubleshooting.
- **`tools/tds_search.py`**: Tra cứu API, selectors, component TDS offline nhanh chóng.

### E. Agent Progress & Handoff Ledger (`tools/agent_progress.py` & `docs/AGENT_PROGRESS.md`)
- **Mục đích**: Nơi lưu trữ tập trung toàn bộ những gì các Agent đã làm, những hạng mục còn thiếu, và bước tiếp theo cần thực hiện để khi User yêu cầu **"làm tiếp"** / **"báo cáo tiến độ"**, bất kỳ Agent nào vào cũng nắm bắt và báo cáo được ngay.
- **Lệnh thực thi**:
  - Xem nhanh trạng thái để báo cáo User khi được yêu cầu *"làm tiếp"*: `python3 tools/agent_progress.py status` (hoặc đọc `docs/AGENT_PROGRESS.md`)
  - Ghi nhận công việc sau khi hoàn thành một bước: `python3 tools/agent_progress.py log --agent "<Role>" --summary "<Tóm tắt>" --done "<Việc đã xong>" --missing "<Việc còn thiếu>" --next "<Bước kế tiếp>" --files "<File đã sửa>"`

### F. Claude Code & Codex Sub-Agents (`031_claude_code_sub_agents` / Skill `claude-code-sub-agents`)
- **Đường dẫn cài đặt**: `.claude/agents/*.md`, `~/.paseo/claude-config/agents/*.md`, `.agents/skills/claude-code-sub-agents/SKILL.md`, và `~/.codex/skills/claude-code-sub-agents/SKILL.md`.
- **3 Sub-Agents chuyên biệt cho 4 Role (`Supervisor - Lead - Peer - QC`)**:
  1. `gemini-codebase-analyzer`: Phân tích toàn cảnh codebase quy mô lớn với Context Window 1M+ tokens (`gemini --prompt "..." --all-files`).
  2. `strategic-reasoning-architect`: Suy luận chiến lược, đánh giá kiến trúc và tìm Root Cause phức tạp (`codex -m "gpt-5" "..."`).
  3. `slpc-qc-verifier`: Sub-agent chuyên trách Role thứ 4 (`QC`) thực thi quy trình 5-Stage ISTQB Pipeline (`python3 tools/qc_test_generator.py`) và nghiệm thu độc lập.

### G. BMAD Central Brain (`/home/baoltb/Desktop/Paseo_Project/bmad`)
- **Bản chất**: "Bộ não" lưu trữ đồ thị tri thức kiến trúc, ranh giới module và luồng nghiệp vụ tập trung, giải quyết triệt để vấn đề Context Overflow (tránh nạp 248.000 file source thô vào LLM context).
- **Tương thích Understand-Anything**: Tích hợp với `understand-anything` để trực quan hóa đồ thị kiến trúc:
  - `bmad/architecture.json`: Đồ thị Nodes (App Shell Host, Remote MFEs `mfe-cdp`, `mfe-crm`, `mfe-account`, thư viện dùng chung `tds-ui`) kèm port dev (4200, 4204, 4203...), router mapping (`/:shopId/customers`, `/:shopId/data-raw`...) và dependencies.
  - `bmad/modules/`: Tóm tắt vai trò, API contracts và công nghệ (Rsbuild Module Federation 2.0, Angular 18 Signals, Tailwind CSS).
  - `bmad/flows/`: Đồ thị luồng tương tác và luồng dữ liệu người dùng (ví dụ: `customer-360-flow.md`).
- **Quy tắc bắt buộc**: Trước khi Lead/Peer lập trình hoặc BA bóc tách spec, **Agent PHẢI đọc `bmad/architecture.json`** và các file module liên quan để nắm trọn vẹn điểm chạm hệ thống.

### H. Paseo Lifecycle Plugins (`/home/baoltb/Desktop/Paseo_Project/plugins`)
- **Vị trí**: `/home/baoltb/Desktop/Paseo_Project/plugins/slpc-lifecycle-hooks`
- **Mục đích**: Plugin chính thức chạy trên server Paseo Daemon (`@getpaseo/plugin/server`, port `:6767`), đăng ký 11 lifecycle hooks (`workspace.create`, `agent.create`, `session.open`, `tool.execute`, `subagent.spawn`...).
- **Chức năng tự động hóa**:
  1. **Inject môi trường SLPC**: Tự động cấp các biến môi trường `PASEO_SLPC_HOOK_ACTIVE=1`, `PASEO_HOOK_TOOL`, `PASEO_RESEARCH_GEN_TOOL` cho mọi agent session.
  2. **Tự động phê duyệt an toàn**: Regex `SAFE_AUTO_APPROVE_PATTERN` tự duyệt các lệnh đọc git và scripts trong `tools/` mà không hỏi prompt thủ công.
  3. **Ép cổng Research & Gen Gate**: Kích hoạt `tools/profile_research_gen.py` đồng bộ tri thức trước khi agent thực thi.
- **Quản lý & Kiểm tra trạng thái**:
  ```bash
  python3 /home/baoltb/Desktop/Paseo_Project/tools/paseo_hooks.py status
  ```

### I. Skill Manager & Inverted Index DB Search (`tools/skill_manager.py`)
- **Lưu trữ**: Floci DynamoDB endpoint `http://<FLOCI_HOST>:14566` (bảng `harness_skills` và chỉ mục ngược `harness_skills_index`).
- **Mục đích**: Quản lý Master Registry 80+ skills, đồng bộ đa phòng và tìm kiếm cực nhanh qua Inverted Index (**truy vấn phân vùng $O(1)$, tuyệt đối không ScanAll toàn bảng**).
- **Lệnh thực thi**:
  - Tìm kiếm skill theo từ khóa: `python3 tools/skill_manager.py search "<từ_khóa>" [--limit 10] [--json]` (hoặc `query`)
  - Đồng bộ và lập chỉ mục DB: `python3 tools/skill_manager.py sync-db` | `python3 tools/skill_manager.py sync`
  - Liệt kê toàn bộ: `python3 tools/skill_manager.py list [--json]`

### J. Loop Engineering & Mechanical Verification Gate (Skill `loop-engineering`)
- **Triết lý**: Xây dựng hệ thống tự động hóa vòng lặp khép kín (Automatic + Closed Loop) thay thế cho luồng viết -> chờ -> prompt thủ công.
- **Nguyên tắc bất biến ("Never let the AI verify its own done")**: Maker (Dev viết code) và Checker (Cổng nghiệm thu kiểm thử) bắt buộc phải tách biệt độc lập 100%. Cấm tuyệt đối Dev tự tin vào chữ "done" của chính mình (`premature_close`). Cổng kiểm soát phải là cơ học (mechanical Stop gate - exit code test/build/lint) hoặc QC độc lập.
- **Vòng lặp tự sửa lỗi (Autonomous Self-Healing Loop)**: Khi nhận task, Peer Dev tự động lặp (code -> test -> fix -> test) trong giới hạn lượt chạy (turn ceiling) cho đến khi toàn bộ test xanh 100% trước khi nộp `Resolved`.
- **Nghiệm thu đóng task**: QC kích hoạt 5-Stage ISTQB pipeline thẩm tra độc lập để đóng `Closed`.

---

## 4. Coding & Operation Rules
1. **Lazy Senior Developer Philosophy**:
   - Stdlib & Native Platform trước tiên.
   - Đọc kỹ source code và specs trước khi chỉnh sửa.
   - Diff ngắn gọn, giữ nguyên code style hiện tại, không thêm boilerplate thừa.
2. **Path Integrity**:
   - Luôn sử dụng đường dẫn tuyệt đối khi thao tác file.
   - Mã nguồn FE luôn trỏ về `/home/baoltb/Desktop/Paseo_Project/projects/crm-fe`.
3. **No Raw HTML in Data**:
   - Dữ liệu bóc tách từ REMOTE hoặc nạp vào DynamoDB/Harness bắt buộc phải được làm sạch qua `clean_html()` để loại bỏ thẻ HTML.
4. **Session Continuity & Handoff Rule**:
   - Khi User yêu cầu *"làm tiếp"* hoặc *"báo cáo những gì đã làm"*, Agent bắt buộc đọc `docs/AGENT_PROGRESS.md` (hoặc chạy `python3 tools/agent_progress.py status`) trước tiên.
   - Trước khi kết thúc phiên hoặc dừng chờ User, Agent bắt buộc cập nhật tiến độ vào `docs/AGENT_PROGRESS.md` qua `python3 tools/agent_progress.py log ...`.
5. **Zero-Search Task Specification Standard (Quy chuẩn Mô tả Task Zero-Search)**:
   - Khi Supervisor tạo Epic/Task hoặc Lead phân rã Task cho Peer Dev / Peer Design, trường `description` và biên bản bàn giao BẮT BUỘC phải đủ 5 thông tin định danh, tuyệt đối cấm mô tả 1 dòng mơ hồ khiến Peer phải chạy bộ công cụ tìm kiếm (`search_files`, `rg`, `find`):
     1. **Target Files**: Đường dẫn file cụ thể (Single-Ownership).
     2. **Anchors / Line Numbers**: Tên hàm, class, selector, hoặc block code cần can thiệp.
     3. **Concrete Changes**: Logic chi tiết, kiểu dữ liệu, token TDS hoặc payload JSON cụ thể.
     4. **Acceptance Criteria (AC)**: Tiêu chuẩn nghiệm thu định lượng (pass test suite nào, verify điều kiện gì).
     5. **Zero-Search Mandate**: Peer chỉ việc mở đúng file đích bằng `read_file`, chỉnh sửa bằng `patch`, và chạy test bằng `terminal`. Peer có quyền VETO từ chối task nếu mô tả thiếu thông tin định vị.
6. **Strict Typing Gate: Zero `any`, Zero `unknown`, Zero Sloppy Fallbacks (`||`)**:
   - Khi DTO và Model đã có sẵn trong codebase (như `Employee`, `ShopUserDto`), cấm tuyệt đối việc Peer dùng `any`, `unknown`, `as any` hoặc lạm dụng chuỗi fallback `||` không chắc chắn (ví dụ: `a || b || c`).
   - Phải map tường minh từng thuộc tính theo đúng schema DTO đã khai báo (`item.shopUserId`, `item.accountUserId ?? String(item.shopUserId)`, `item.name`).
   - Cấm dùng `new Optional()` cho các Service/Store cốt lõi đã `{ providedIn: 'root' }` (như `MemberStore`). Dependency bắt buộc phải inject trực tiếp vào `deps`.
   - **Quality Gate của QC**: QC BẮT BUỘC phải rà soát diff của Peer. Nếu phát hiện dù chỉ 1 chữ `any`, `unknown` hoặc fallback chắp vá, QC lập tức REJECT nộp lại cho Peer sửa, cấm duyệt đóng task.
7. **Anti-Leak & Sensitive Data Gate (Quy chuẩn Chống Lộ Dữ Liệu Nhạy Cảm & Địa Chỉ Thực Tế)**:
   - Tuyệt đối cấm đưa tên công ty nội bộ, địa chỉ thực tế (số nhà, tên đường, cụm/lô khu công nghiệp, quận huyện), số điện thoại, email cá nhân, mã số thuế hoặc API token vào mã nguồn, tài liệu spec mẫu, commit Git hoặc Pull Request công khai.
   - Bắt buộc tích hợp và kích hoạt script quét tự động (`scripts/check-sensitive-info.py` hoặc CI Action `security-scan.yml`) fail-closed trước khi merge.
   - Với các dự án Rust: Bắt buộc chạy `cargo fmt --check` trước khi push để đảm bảo release pipeline không bị gãy format.
8. **TDS Test ID & Testing Contract Gate (Quy chuẩn Định danh Kiểm thử Bất biến FE ↔ QA)**:
   - Bắt buộc 100% component FE có tương tác (button, input, form, modal, table row) phải gắn directive `tdsTestId` từ `@wicx/core`.
   - Naming convention bắt buộc: `<domain>-<component>-<element>-<state?>` (100% tiếng Anh, kebab-case).
   - Tuyệt đối cấm: Hardcode `tds-test-id="..."`, dùng class CSS, dùng array index mảng `index` cho danh sách, rò rỉ visual styles (`red`, `hidden`) vào ID.
   - QC bắt buộc: Bổ sung unit test cho directive (`tds-test-id.directive.spec.ts`), viết auto-test query bằng `[tds-test-id="..."]` hoặc helper `getByTdsTestId()`, nghiêm cấm `getByText()`, class CSS hay XPath. QC có quyền VETO nếu thiếu test ID.
