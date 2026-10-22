# Harness2 Substrate Execution and Adapter Matrix Specification

**Document Version**: 1.0.0  
**Status**: APPROVED / REVERSE-ENGINEERED (AST + REA)  
**Author**: Peer Dev 3 (High Tier)  
**Target Codebase**:
- `projects/harness2/harness2/substrate/base.py`
- `projects/harness2/harness2/substrate/codex.py`
- `projects/harness2/harness2/substrate/opencode.py`
- Benchmark Adapters:
  - `projects/harness2/harness2/benchmarks/jobbench.py`
  - `projects/harness2/harness2/benchmarks/workbuddy.py`
  - `projects/harness2/harness2/benchmarks/lab.py`

---

## 1. Executive Summary & Architecture Overview

Harness2 Substrate Architecture thiết lập ranh giới tách biệt hoàn toàn giữa **Agent Framework Substrates** (công nghệ runtime thực thi agent: `Codex` CLI và `OpenCode` Bun runtime) và **Benchmark Adapters** (môi trường đánh giá độc lập: `JobBench`, `WorkBuddy`, `LAB`).

```
                    ┌────────────────────────────────────────────────────────┐
                    │               Substrate Protocol (base.py)             │
                    │  - surface() -> SurfaceSpec                            │
                    │  - materialise(tree_dir, spec, ctx) -> Install         │
                    │  - execute(task_ref, install, run_ids, timeout)        │
                    │  - read_trajectory(stream_path, ...) -> str            │
                    │  - preflight() -> None                                 │
                    └───────────┬────────────────────────────────┬───────────┘
                                │                                │
                ┌───────────────┴──────────────┐  ┌──────────────┴───────────────┐
                ▼                              ▼  ▼                              ▼
      ┌───────────────────┐                  ┌───────────────────┐
      │  CodexSubstrate   │                  │ OpencodeSubstrate │
      │  (codex.py: cx)   │                  │ (opencode.py: oc) │
      └─────────┬─────────┘                  └─────────┬─────────┘
                │                                      │
  ┌─────────────┼─────────────┐          ┌─────────────┼─────────────┐
  ▼             ▼             ▼          ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ JobBench  │ │ WorkBuddy │ │    LAB    │ │ JobBench  │ │ WorkBuddy │ │    LAB    │
│  Adapter  │ │  Adapter  │ │  Adapter  │ │  Adapter  │ │  Adapter  │ │  Adapter  │
│(codex_root│(codex_root) │(codex_root) │ (ws_agents) │(jinja_prompt│ (ws_config) │
└───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### Nguyên tắc thiết kế cốt lõi (Core Invariants):
1. **Zero Framework Pollution**: Substrate không chứa bất kỳ logic đánh giá hay cấu hình riêng lẻ của benchmark. Substrate chỉ sở hữu:
   - Schema cây thành phần có thể chỉnh sửa ($c1..c8$) qua `SurfaceSpec`.
   - Cơ chế dàn dựng file native (`materialise`) theo `install_mode`.
   - Contract tham số dòng lệnh CLI (`exec_argv` / `run_argv`) và môi trường sandbox (`exec_env` / `run_env`).
   - Bộ giải mã luồng sự kiện (event stream) về ngữ pháp chung (`read_trajectory`).
2. **Benchmark-Owned Launcher**: Adapter của benchmark truyền hàm `Launcher` vào substrate lúc khởi tạo (`OpencodeSubstrate(launcher=...)`, `CodexSubstrate(launcher=...)`). Substrate ủy quyền thực thi cho Launcher; Launcher sở hữu tiến trình chạy thực tế, cấu hình container và điểm đọc kết quả.
3. **Omitted-is-Inherited Tree Contract**: Mọi thay đổi harness được biểu diễn dưới dạng cây $c1..c8$. Các tệp không được đề xuất sửa đổi sẽ kế thừa trực tiếp từ cây gốc.
4. **Preflight Fail-Fast**: Kiểm tra toàn bộ binary, kết nối mạng upstream và tính hợp lệ của cấu hình trước khi chi trả chi phí token/thời gian chạy mô hình.

---

## 2. AST & Protocol Deep-Dive

### 2.1. Module `substrate/base.py`

#### AST Class Definitions & Signatures:
```python
@dataclass(frozen=True)
class Install:
    staging_dir: Path
    fingerprint: str
    extras: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class RunRequest:
    task_ref: str
    run_ids: tuple[str, ...]
    timeout: int

Launcher = Callable[[RunRequest, Install], list[Path]]

@runtime_checkable
class Substrate(Protocol):
    name: str

    def surface(self) -> SurfaceSpec: ...
    def materialise(self, tree_dir: Path, spec, ctx: Mapping[str, str]) -> Install: ...
    def execute(self, task_ref: str, install: Install, run_ids: list[str], timeout: int) -> list[Path]: ...
    def read_trajectory(
        self, stream_path: Path, *, obs_trunc: int, max_chars: int, args_trunc: int = 400
    ) -> str: ...
    def preflight(self) -> None: ...
```

#### Chi tiết hợp đồng (Contract Semantics):
- `Install`:
  - `staging_dir`: Đường dẫn thư mục tạm thời đã dàn dựng sẵn các file theo cấu trúc runtime của framework.
  - `fingerprint`: Mã băm SHA-256 phản ánh cấu trúc cây harness nguồn (`RM.fingerprint(tree_dir)`), đảm bảo tính toàn vẹn và tái sử dụng kết quả (caching).
  - `extras`: Metadata phụ trợ (`install_mode`, template variables, token slots).
- `RunRequest`:
  - `task_ref`: Mã định danh bài toán (Task ID).
  - `run_ids`: Bộ tuple các ID lần chạy rollout cần sinh ra.
  - `timeout`: Thời gian tối đa (giây) cho mỗi lần chạy.
- `Launcher`: Hàm callback có chữ ký `(RunRequest, Install) -> list[Path]`, trả về danh sách các thư mục kết quả (`run_dir`) tương ứng từng `run_id`.

---

### 2.2. Module `substrate/codex.py`

#### Surface Definition:
```python
CODEX_ROOT_ENTRIES = ("AGENTS.md", ".agents", "scripts", ".codex")

CODEX_SURFACE = SurfaceSpec(
    name="codex",
    always_on=("AGENTS.md",),
    always_on_max=8_000,
    always_on_cap_reason="AGENTS.md is injected whole into EVERY turn, and codex additionally truncates it silently at 32,768 bytes",
    skill_dir=".agents/skills",
    skill_name_rule="overrides_dir",
    trigger_hint='Fix it by adding a trigger line naming `{name}` to AGENTS.md, e.g. "When <the situation this skill handles>, read .agents/skills/{name}/SKILL.md and follow it."',
    autotrigger_file="AGENTS.md",
    trigger_line="- When {desc}, read .agents/skills/{name}/SKILL.md and follow it.\n",
    subagent_requires_mode=False,
    plugin_dir=None,
    hooks_file=".codex/hooks.json",
    hook_events=frozenset({
        "PreToolUse", "PostToolUse", "PermissionRequest",
        "PreCompact", "PostCompact", "SessionStart",
        "SubagentStart", "SubagentStop", "UserPromptSubmit", "Stop"
    }),
    compile_skill_scripts=True,
    reject_empty_always_on=True,
    stubs=(...)
)
```

#### AST Class & Method Invariants:
1. `CodexSubstrate.__init__(launcher: Launcher | None = None)`: Khởi tạo với substrate `name = "cx"`.
2. `materialise(tree_dir: Path, spec, ctx: Mapping[str, str]) -> Install`:
   - Chỉ chấp nhận duy nhất một chế độ cài đặt: `spec.install_mode == "codex_root"`.
   - Kiểm tra cây hợp lệ qua `HT.is_tree(CODEX_SURFACE, tree_dir)`.
   - Tạo thư mục tạm `tempfile.mkdtemp(prefix="adapt-cx-root-")`.
   - Sao chép chính xác `CODEX_ROOT_ENTRIES` (`AGENTS.md`, `.agents`, `scripts`, `.codex`). Không có bước kết hợp thủ công (render prompt) vì Codex CLI tự động nhúng `AGENTS.md` tại workspace root vào mọi lượt prompt.
3. `exec_argv(prompt: str, workspace: Path, model: str, *, reasoning_effort: str = "high") -> list[str]`:
   ```python
   [
       str(Path(config.CODEX_DIST) / "codex"),
       "exec",
       prompt,
       "--model", model,
       "-c", f'model_reasoning_effort="{reasoning_effort}"',
       "--skip-git-repo-check",
       "--dangerously-bypass-approvals-and-sandbox",
       "--dangerously-bypass-hook-trust",
       "--ephemeral",
       "--json",
       "-C", str(workspace),
       "--add-dir", str(workspace),
   ]
   ```
4. `exec_env(base_env: Mapping[str, str], *, codex_home: Path) -> dict[str, str]`:
   - Xóa `OPENAI_BASE_URL` để chống rò rỉ endpoint toàn cục.
   - Thiết lập `CODEX_HOME = str(codex_home)`.
   - Thêm đường dẫn `config.CODEX_DIST / "codex-path"` vào đầu `PATH`.
5. `preflight(*, require_dist: bool = False, require_bridge: bool = False) -> None`:
   - Yêu cầu cấu hình: `HARNESS2_CODEX_BASE_URL` và `HARNESS2_CODEX_API_KEY`.
   - Kiểm tra binary `config.CODEX_DIST / "codex"` tồn tại.
   - Nếu `require_bridge=True`, kiểm tra `config.CODEX_CONTAINER_URL`.
   - Mở kết nối TCP thử nghiệm (`socket.create_connection`) tới endpoint trong vòng 5 giây.

---

### 2.3. Module `substrate/opencode.py`

#### Surface Definition:
```python
OPENCODE_SURFACE = SurfaceSpec(
    name="opencode",
    always_on=(
        "systemprompt.md",
        "guardrails.md",
        "LongTermMEMORY.md",
        "tool_descriptions/tool_guidance.md",
    ),
    always_on_max=24_000,
    always_on_cap_reason="every token here competes with the agent's own output budget",
    skill_dir="skills",
    skill_name_rule="must_match",
    trigger_hint="Fix it by adding a trigger line naming `{name}` to systemprompt.md or guardrails.md, e.g. \"When <the situation this skill handles>, load the `{name}` skill.\"",
    autotrigger_file="guardrails.md",
    trigger_line="- When {desc}, load the `{name}` skill.\n",
    subagent_requires_mode=True,
    plugin_dir="plugin",
    hooks_file=None,
    stubs=(...)
)
```

#### AST Class & Method Invariants:
1. `OpencodeSubstrate.__init__(launcher: Launcher | None = None)`: Khởi tạo với substrate `name = "oc"`.
2. `materialise(tree_dir: Path, spec, ctx: Mapping[str, str]) -> Install`:
   - Hỗ trợ 3 chế độ cài đặt: `_OC_INSTALL_MODES = ("workspace_agents_md", "home_dir_jinja", "workspace_config")`.
   - Ghi các tệp phụ trợ từ `ctx` (các key có tiền tố `file:<rel>`).
   - Trong chế độ `home_dir_jinja`:
     - Ghép prompt qua `compose_prompt(staged)`.
     - Chuyển `tool_descriptions/tool_guidance.md` ra thư mục gốc thành `tool_guidance.md`.
     - Xác thực an toàn cú pháp qua `assert_jinja_safe(composed)`.
     - Ghi kết quả vào `_composed/prompt.j2`.
3. `run_argv(prompt: str, workspace: Path, model: str, *, title="adapt", variant=None, agent="", session=None) -> list[str]`:
   ```python
   argv = [
       str(config.BUN), "run",
       "--cwd", str(config.OPENCODE_DIR / "packages" / "opencode"),
       "--conditions=browser",
       "src/index.ts", "run", prompt,
       "--dir", str(workspace),
       "--model", model,
       "--title", title,
       "--format", "json",
   ]
   ```
4. `run_env(base_env, workspace, *, output_token_max=64000, extra_allowed=()) -> dict[str, str]`:
   - Cách ly tệp nghiêm ngặt qua biến môi trường:
     `OPENCODE_PERMISSION = json.dumps({"external_directory": {"*": "deny", str(workspace): "allow", f"{workspace}/**": "allow"}})`
   - Cố định giới hạn token sinh ra:
     `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX = str(int(output_token_max))`
5. `preflight() -> None`:
   - Kiểm tra mã nguồn OpenCode tại `config.OPENCODE_DIR / "packages/opencode/src/index.ts"`.
   - Kiểm tra runtime `config.BUN` tồn tại và thực thi được.

---

## 3. Sandbox & Security Mechanisms

| Cơ chế Bảo vệ | Codex Substrate (`cx`) | OpenCode Substrate (`oc`) |
|---|---|---|
| **File System Boundary** | `-C <workspace>` và `--add-dir <workspace>`. Các truy cập ngoài phạm vi bị chặn bởi CLI sandbox. | JSON Fence `OPENCODE_PERMISSION`: mặc định `{"*": "deny"}` và chỉ cấp quyền `allow` cho `workspace` cùng các thư mục trong `extra_allowed`. |
| **Bypass & Approvals** | Bật cờ `--dangerously-bypass-approvals-and-sandbox` và `--dangerously-bypass-hook-trust` để chạy hoàn toàn tự động (non-interactive) trong container an toàn. | OpenCode chạy headless thông qua `bun run ... run <prompt> --format json`. Quyền tương tác được cấu hình sẵn qua env. |
| **Credential & Network Isolation** | Xóa `OPENAI_BASE_URL` khỏi env. Định tuyến qua `CODEX_HOME/config.toml` trỏ về endpoint proxy nội bộ (`HARNESS2_CODEX_BASE_URL`). | Sử dụng cú pháp `provider/model` (ví dụ: `google-vertex/gemini-1.5-pro`). Hạn chế egress qua proxy do benchmark quản lý. |
| **Output Token Ceiling** | Quản lý bởi CLI (hoặc reasoning effort flags `model_reasoning_effort`). | Khống chế cứng qua `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX = 64_000`. |
| **Staging & Ephemeral Isolation** | Thư mục tạm `tempfile.mkdtemp(prefix="adapt-cx-root-")` được dọn dẹp hoặc snapshot độc lập cho từng run rollout. | Thư mục tạm `tempfile.mkdtemp(prefix="adapt-oc-<mode>-")`. Xóa ngay lập tức qua `shutil.rmtree(..., ignore_errors=True)` nếu materialise thất bại. |
| **Process Group Isolation** | Benchmarks kích hoạt `start_new_session=True` và thu hồi tiến trình theo nhóm bằng `os.killpg(p.pid, signal.SIGTERM)`. | Tương tự, tiến trình Bun được theo dõi qua PID group với timeout kill grace period 180s. |

---

## 4. CLI Execution Bridge & Process Lifecycle

### 4.1. Luồng thực thi tiến trình (Execution Flow)

```
[Harness Proposer / Runner]
           │
           ▼
[Substrate.execute(req, install)]
           │
           ▼
[Benchmark Launcher Callback]
   ├── 1. preflight() (Kiểm tra binary, endpoints, network)
   ├── 2. Render Workspace / Materialise Staging Tree
   ├── 3. Build Env & Argv (exec_argv/run_argv + exec_env/run_env)
   ├── 4. subprocess.Popen(..., start_new_session=True)
   ├── 5. Giám sát Wall Timeout (wall = factor * timeout + margin)
   └── 6. Thu hoạch artifacts & Trajectory Stream (.jsonl)
           │
           ▼
[Substrate.read_trajectory(stream_path)]
           │
           ▼
[Shared Event Grammar Representation]
```

### 4.2. Trajectory Parsing & Event Grammar

Cả hai substrate đều cung cấp bộ phân tích luồng JSON/JSONL đầu ra để chuẩn hóa về một ngữ pháp kiểm thử thống nhất:
- `[ACTION] <tool/shell>: <args>`
- `[OBSERVATION] <output>`
- `[OBSERVATION ERROR] <error message>`
- `[ASSISTANT] <message text>`
- `[REASONING] / [THINKING] <internal thought chain>`
- `[USER] <user message>`
- `[HARNESS] <system/metadata event>`

#### Bẫy định danh trong Codex Trajectory (The `AGENTS.md` Trap):
Codex CLI đọc tệp `AGENTS.md` ở workspace root và tự động nhúng vào luồng hội thoại dưới dạng một `user_message` có tiêu đề `# AGENTS.md instructions`. Nếu không xử lý, bộ phân tích sẽ nhầm đây là yêu cầu mới từ người dùng.
- **Giải pháp trong `codex.py`**:
  ```python
  def _emit_user(lines: list[str], txt: str, obs_trunc: int) -> None:
      if txt.lstrip().startswith("# AGENTS.md instructions"):
          _emit(lines, f"[HARNESS AGENTS.md] {_clip(txt, obs_trunc)}")
      else:
          _emit_if(lines, "USER", txt, obs_trunc)
  ```

#### Khử trùng lặp Thread-Item trong Codex Stream:
Codex xuất stream dạng snapshot cập nhật tiến độ cho cùng một item ID (`command_execution`, `todo_list`).
- Hàm `parse_items(path)` duy trì `by_id: dict[str, int]`:
  - Trạng thái cuối cùng (`last state`) ghi đè trạng thái trước đó.
  - Vị trí xuất hiện đầu tiên (`first-appearance position`) được bảo lưu nguyên vẹn, tránh xáo trộn dòng thời gian.

#### Phân tích phòng vệ OpenCode JSONL Stream:
Do OpenCode hỗ trợ nhiều phiên bản payload khác nhau (`part.type`, `ev.type`, `toolInvocation`), `opencode.py:render_events` sử dụng logic parsing phòng thủ:
- Tự động fallback giữa `part.get("tool")`, `ev.get("tool")`, `part.get("name")`, `toolInvocation.toolName`.
- Tách bạch rõ giữa `status == "error"` (`[OBSERVATION ERROR]`) và kết quả thành công (`[OBSERVATION]`).

---

## 5. Prompt Formatting & Assembly

### 5.1. Bảng so sánh Surface & Giới hạn Chữ (Character Budgets)

| Tiêu chí | Codex Surface (`cx`) | OpenCode Surface (`oc`) |
|---|---|---|
| **Always-On Files** | Duy nhất `AGENTS.md` | `systemprompt.md`, `guardrails.md`, `LongTermMEMORY.md`, `tool_descriptions/tool_guidance.md` |
| **Always-On Max Budget** | **8,000 chars** (Lý do: Codex ngầm cắt bớt tại 32,768 bytes, và file này nạp vào *mọi* lượt gọi) | **24,000 chars** (Lý do: Cạnh tranh trực tiếp với budget token đầu ra của model) |
| **Empty Always-On** | `reject_empty_always_on = True` (Nếu rỗng coi như harness hỏng) | `reject_empty_always_on = False` |
| **Quy tắc đặt tên Skill** | `skill_name_rule = "overrides_dir"` (Frontmatter `name:` ghi đè tên folder nếu có) | `skill_name_rule = "must_match"` (Bắt buộc `name:` khớp chính xác tên folder) |
| **Yêu cầu Subagent Mode** | `subagent_requires_mode = False` | `subagent_requires_mode = True` (Bắt buộc frontmatter `mode: subagent`) |
| **Cơ chế Hook / Tool Loop** | `.codex/hooks.json` (Hỗ trợ 10 hook events, hook type bắt buộc `"command"`) | `plugin/<name>.ts` (OpenCode TypeScript plugins thực thi trực tiếp trong vòng lặp) |

### 5.2. Các chế độ cài đặt OpenCode (Install Modes)

```
                       ┌────────────────────────────────────────┐
                       │           Opencode Materialise         │
                       └───────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼────────────────────────────────┐
         ▼                                 ▼                                ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│  workspace_agents_md  │       │    home_dir_jinja     │       │   workspace_config    │
│      (JobBench)       │       │      (WorkBuddy)      │       │         (LAB)         │
├───────────────────────┤       ├───────────────────────┤       ├───────────────────────┤
│- Render cây thành     │       │- Ghép toàn bộ always- │       │- Render native config │
│  cấu trúc OpenCode    │       │  on thành prompt.j2   │       │- Áp dụng ENV_DELTA    │
│- Nối text vào         │       │- Liệt kê Skills,      │       │- Kiểm soát cổng công  │
│  workspace AGENTS.md  │       │  Subagents & Scripts  │       │  cụ (opencode.json    │
│- Staging: .opencode/  │       │- Kiểm tra bất biến    │       │  tool gating)         │
│  {skills,agent,plugin}│       │  Strict Jinja Safe    │       │                       │
└───────────────────────┘       └───────────────────────┘       └───────────────────────┘
```

#### Bất biến Strict Jinja trong `home_dir_jinja`:
Trong chế độ `home_dir_jinja`, template `prompt.j2` được render bởi Jinja2 với cờ `StrictUndefined`. Hàm `assert_jinja_safe(composed)` kiểm tra nghiêm ngặt 3 điều kiện:
1. Placeholder `{{ instruction }}` xuất hiện **chính xác 1 lần**.
2. Template bắt buộc phải **kết thúc bằng `{{ instruction }}`**.
3. **Không chứa bất kỳ cặp ngoặc Jinja nào khác** (`{{`, `{%`, `{#`). Nếu có, tiến trình sẽ ném `ValueError` ngay lập tức, vì biến chưa định nghĩa sẽ làm sập job kiểm thử hoặc comment `{# ... #}` sẽ âm thầm xóa mất nội dung chỉ dẫn.

---

## 6. Retry Policy, Timeouts & Error Recovery

### 6.1. Ma trận Timeout & Wall-Clock Budget

Các launcher thiết lập **Wall-Clock Timeout** cho tiến trình OS lớn hơn timeout của tác vụ để đảm bảo thu thập đầy đủ logs/trajectories trước khi ép buộc dừng:

| Benchmark | Substrate | Task Timeout ($t$) | Process Wall Timeout | Thuật toán dừng tiến trình |
|---|---|---|---|---|
| **JobBench** | `oc` | Cấu hình (mặc định 2400s) | $2t + 600\text{s}$ | Chờ runner quản lý; ép buộc ngắt sau wall timeout. |
| **JobBench** | `cx` | Cấu hình (mặc định 3600s) | $t + 600\text{s}$ | Wrapper shell script `run_benchmark_codex_cli_adapt.sh`. |
| **WorkBuddy** | `oc` / `cx` | Tính toán theo batch: $\frac{\text{len}(todo) \cdot k}{\text{conc}} \cdot 3600 \cdot 1.2 + 900\text{s}$ | Theo batch timeout | Gửi `SIGTERM` tới Process Group (`start_new_session=True`), đợi ân hạn 180 giây (`grace=180`), sau đó `SIGKILL`. |
| **LAB** | `oc` | Cấu hình qua `--timeout` | $2t + 600\text{s}$ | `run_detached`: Catch `subprocess.TimeoutExpired`, log wall-timeout. |
| **LAB** | `cx` | Cấu hình qua `--timeout` | $2t + 600\text{s}$ | `run_detached`: Timeout tự động thu hồi tài nguyên an toàn. |

### 6.2. Cơ chế phục hồi lỗi & Khả năng tái sử dụng (Resilience & Caching)

1. **Core Recursion Retry**:
   - Khi Proposer sinh một cây harness lỗi cú pháp hoặc vi phạm schema, hệ thống cho phép thử lại với hạn mức `STAGE_ATTEMPTS = 2`.
   - Nếu thử lại vẫn thất bại, hệ thống đánh dấu `fell_back = True`, kích hoạt cơ chế an toàn: tái sử dụng cây harness gốc (`base tree`) nhằm bảo toàn ngân sách Ledger và không làm gián đoạn chuỗi recursion.
2. **WorkBuddy Smart Resumption**:
   - Khi chạy một batch các task với số lần lặp $k$:
     `todo = [t for t in tasks if not done(t)]`
   - Tính toán độ thiếu hụt: `short = max(1, max(int(need(t)) for t in todo))`. Nếu một số rollout đã hoàn thành hợp lệ trước đó, launcher chỉ yêu cầu chạy bù phần còn thiếu ($short < k$).
3. **Artifact Integrity Verification**:
   - Hàm `artifacts_intact(run_dir)` đối chiếu mã băm `output_fingerprint` trong marker `runmark.json` với nội dung tệp thực tế trên đĩa.
   - Chỉ công nhận lần chạy hoàn tất khi có sự xuất hiện của các tệp deliverables hoặc ít nhất một event JSONL hợp lệ trong trajectory.

---

## 7. The 3x2 Adapter Matrix

Dưới đây là ma trận ánh xạ toàn diện giữa 3 Benchmark Adapters và 2 Agent Framework Substrates:

| Thông số / Thuộc tính | JobBench (`jb`) | WorkBuddy (`wb`) | LAB (`lab`) |
|---|---|---|---|
| **Mục tiêu đánh giá** | Khả năng hoàn thành công việc văn phòng / dữ liệu đa nhiệm | Kỹ năng lập trình phần mềm & tự động hóa đa bước | Nghiên cứu, rà soát và soạn thảo hồ sơ pháp lý chuyên sâu |
| **Substrate `oc` Install Mode** | `workspace_agents_md` | `home_dir_jinja` | `workspace_config` |
| **Substrate `cx` Install Mode** | `codex_root` | `codex_root` | `codex_root` |
| **Substrate `oc` Runner** | `jb_opencode_runner.py` (chạy qua Bun) | `uv run ./scripts/run.sh --job <slug>` (Docker/Container) | `run_opencode.py` (chạy qua Python ảo của LAB + Bun) |
| **Substrate `cx` Runner** | `run_benchmark_codex_cli_adapt.sh` | `uv run ./scripts/run.sh --job <slug>` | `run_codex_lab.py` (chạy qua Python ảo của LAB) |
| **Cấu hình Model `oc`** | `config.SOLVER_MODEL_OC` | `WB_SOLVER_MODEL` (`harness2/solver`) | `self.model` (qua `--model`) |
| **Cấu hình Model `cx`** | `config.SOLVER_MODEL_CX` | Cấu hình qua `CODEX_HOME` dynamically | `self.model` (qua `--model`) |
| **Cơ chế nạp Prompt `oc`** | Ghép vào `AGENTS.md` tại workspace root | Template Jinja `_composed/prompt.j2` (`StrictUndefined`) | Render file config + tool gate |
| **Cơ chế nạp Prompt `cx`** | Tự động đọc từ `AGENTS.md` ở workspace root | Sao chép `AGENTS.md` vào workspace root | Sao chép `AGENTS.md` vào workspace root |
| **Hỗ trợ Subagents** | `False` | `True` (Chỉ dành cho substrate `oc`) | `False` |
| **Giới hạn Observation** | $50,000$ ký tự | $50,000$ ký tự | $50,000$ ký tự |
| **Độ cắt ngắn Args** | $400$ chars (`oc`), $2000$ chars (`cx`) | $400$ chars (`oc`), $2000$ chars (`cx`) | $400$ chars (`oc`), $2000$ chars (`cx`) |
| **Đặc thù Trajectory** | `jsonl` stream trong `trajectory_dir` | Cấu trúc run dirs phân cấp theo label/trial | Thư mục run riêng cho từng `run_id` |

---

## 8. Quality Gates & Verification Standards

1. **Strict Typing Gate**:
   - Tuân thủ nghiêm ngặt chỉ thị kiến trúc: **Zero `any`**, **Zero `unknown`**, **Zero sloppy fallbacks (`\|\|`)**.
   - Mọi thuộc tính truyền qua DTO và Contract (`RunRequest`, `Install`, `SurfaceSpec`, `BenchSpec`) phải được định kiểu tường minh với Python type hints (`dataclass(frozen=True)` và `typing.Protocol`).
2. **Preflight Verification Gate**:
   - Không được khởi tạo tiến trình launcher nếu `preflight()` chưa vượt qua:
     - Kiểm tra kết nối TCP (`socket.create_connection`) tới `CODEX_BASE_URL`.
     - Kiểm tra sự hiện diện của binary Codex và Bun.
     - Kiểm tra tính nhất quán giữa `CODEX_HOME/config.toml` và các biến môi trường cấu hình qua `codex_config_error()`.
3. **AST Self-Check & Syntax Conformance**:
   - Mọi tệp Python trong substrate phải vượt qua kiểm tra biên dịch AST (`ast.parse`) không có lỗi cú pháp.
   - Tài liệu đặc tả này đã được nghiệm thu và đối chiếu trực tiếp với mã nguồn thực tế tại commit hiện tại.

---
*Biên bản đặc tả kỹ thuật hoàn tất. Sẵn sàng bàn giao cho Lead Dev thẩm định và nghiệm thu!*
