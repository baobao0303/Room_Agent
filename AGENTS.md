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

## 2. Team Multi-Agent Roles & Workflow Gates (SLPC)

Mọi tác vụ phải tuân thủ nghiêm ngặt quy trình chuyển giao qua 4 cổng kiểm soát SLPC:

```text
[Yêu cầu từ User]
       │
       ▼
1. Supervisor (Scope & Intent Guard) ──► Phân tích scope, tạo Epic/Task trên Harness DB
       │
       ▼
2. Lead (Architect & Technical PM) ────► Thiết kế kiến trúc, API contract, phân rã task
       │
       ▼
3. Peer (Code Executor / Dev) ────────► Lập trình tính năng (Angular 18/TDS), viết Unit Test
       │
       ▼
4. QC (Quality Gate & Test Architect) ─► Sinh testcase ISTQB 5-Stage, nghiệm thu độc lập
       │
       ▼
[Task CLOSED]
```

### Chi tiết 4 vai trò SLPC:
1. **Supervisor (`supervisor`)**: Scope & Intent Guard. Tiếp nhận yêu cầu từ User, phân tích phạm vi, tạo Epic/Task/Story trên Harness DB, điều phối Lead/Peer và kiểm soát chi phí/rủi ro.
2. **Lead (`lead`)**: Technical Architect & PM. Phân tích tài liệu nghiệp vụ, thiết kế kiến trúc hệ thống, API Contract, duyệt giải pháp kỹ thuật và phân rã task cho Peer.
3. **Peer (`peer`)**: Code Executor (Developer). Hiện thực hóa mã nguồn theo spec, tuân thủ Angular 18 + TDS UI Design System, viết unit test và chuyển task sang `Resolved`.
4. **QC (`qc`)**: Independent Quality Gate & Test Architect. Nghiệm thu độc lập, sinh testcase theo chuẩn ISTQB 5-Stage (`tools/qc_test_generator.py`), xác nhận Acceptance Criteria và đóng task (`Resolved ➔ Closed`).

---

## 3. Available Tools & Skills Index

### A. Harness Manager Tool (`tools/harness_manager.py` / Skill `harness-ops`)
- **Lưu trữ**: Floci DynamoDB endpoint `http://<FLOCI_HOST>:14566` (tables `harness_work_items`, `harness_stories`, `harness_tools`, `harness_metadata`).
- **Lệnh thực thi**:
  - Xem ma trận kiểm thử: `./scripts/harness query matrix`
  - Xem backlog đa chiều: `./scripts/harness query backlog [--sprint <sprint>] [--source remote|local] [--top 25]`
  - Xem thống kê: `./scripts/harness query stats`
  - Đồng bộ lại từ REMOTE: `./scripts/harness sync-remote`
  - Thêm mới / Cập nhật trạng thái: `python3 tools/harness_manager.py add ...` | `python3 tools/harness_manager.py update ...`

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
