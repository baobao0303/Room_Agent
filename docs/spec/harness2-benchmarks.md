# Harness2 Benchmark Suites, Runner Presets & Anti-Leak Architecture Specification

**Document Version**: 1.0.0  
**Status**: APPROVED / REVERSE-ENGINEERED (Task #3953)  
**Author**: Peer Dev 2 (Medium Tier)  
**Reviewer**: Lead Dev  
**Target Codebase Paths**:
- `projects/harness2/harness2/benchmarks/tasks.py`
- `projects/harness2/harness2/benchmarks/jobbench.py`
- `projects/harness2/harness2/benchmarks/workbuddy.py`
- `projects/harness2/harness2/benchmarks/lab.py`
- `projects/harness2/harness2/benchmarks/wb_render.py`
- `projects/harness2/harness2/benchmarks/jb_opencode_runner.py`
- `projects/harness2/third_party/wb_runner/configs/`
- `projects/harness2/scripts/split_tasks.py`

---

## 1. Executive Summary & Architecture Overview

Harness2 cung cấp lớp trừu tượng đồng nhất (Unified Benchmark Adapter Layer) kết nối giữa các Substrates thực thi mã nguồn (`OpenCode` - `oc`, `Codex CLI` - `cx`) và các bộ Benchmark tiêu chuẩn hàng đầu dành cho Agent:
1. **JobBench (`jb`)**: Đánh giá năng lực giải quyết công việc chuyên nghiệp xuyên suốt 10 ngành nghề (Office, Data, Tech, Finance...), chấm điểm qua ma trận Rubrics đa tiêu chí có trọng số.
2. **WorkBuddy-Bench (`wb`)**: Đánh giá năng lực tác vụ đa miền (Code diffs, Web apps, Office artifacts) chạy dưới cơ chế Harbor Batch với hệ thống Anti-Leak Guardrail nghiêm ngặt.
3. **Harvey LAB (`lab`)**: Đánh giá năng lực phân tích, thẩm định và soạn thảo văn kiện pháp lý phức tạp theo 4 Work Types và các Practice Areas chuyên sâu.

Lớp adapter bảo đảm:
- **Zero Evaluation Leakage**: Tách biệt hoàn toàn giữa artifacts do agent tạo ra và dữ liệu chấm điểm của verifier/judge.
- **Unified Score Representation**: Chuẩn hóa điểm số từ nhiều cơ chế chấm (Rule-based, Rubric-weighted, LLM Judge) về schema `{ n_passed, n_criteria, all_pass, ... }`.
- **Reproducible Dataset Partitioning**: Phân vùng tập dữ liệu (train/test) phân tầng theo miền (stratified by domain) với seed xác định.

---

## 2. Benchmark Suite Comparison Matrix

| Benchmark Suite | Subsets / Practice | Substrates | Primary Deliverable | Scoring Mechanism | Judge Model / Evaluator | Anti-Leak Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **JobBench (`jb`)** | 10 Professions (Management Analysts, Accountants, Developers...) | `oc`, `cx` | Tài liệu, bảng tính, code (`task_folder`) | Rubric-based Weighted / Unweighted fallback | Vertex AI / OpenAI-compatible (`JB_JUDGE_MODEL`) | Staging cô lập, chỉ đọc artifacts, bỏ qua verifier internals |
| **WorkBuddy (`wb`)** | `code`, `web`, `office` | `oc`, `cx` | Git patch, Web workspace tar, Office raw files | Precedence: `reward > overall > test_pass_rate > passed/total` | Rule-based (`code`), LLM Judge (`web`), Rubric (`office`) | `wb_render.py` Allowlist & Scanner chặn mọi verifier feedback |
| **Harvey LAB (`lab`)** | 4 Work Types (`analyze`, `review`, `draft`, `research`) | `oc`, `cx` | Legal instruments, research memos | Rubric criteria passing count | `evaluation.run_eval` (`LAB_JUDGE_MODEL`) | Stripped grading criteria trong task JSON |

---

## 3. Dataset Discovery & Stratified Split Architecture

### 3.1. Discovery Engine (`benchmarks/tasks.py`)

Cung cấp hàm `discover(bench: str, subset: str | None = None) -> dict[str, str]` trả về mapping `task_id -> domain`:
- **JobBench (`jb`)**:
  - Đường dẫn: `config.jb_repo() / "dataset" / "main"`.
  - Quét: Glob `*/*/task_folder/TASK_INSTRUCTIONS.txt`.
  - Task ID: `<profession>/<task_folder>` (ví dụ: `management_analysts/task_001`).
  - Domain: `parts[0]` (Tên ngành nghề / profession).
- **Harvey LAB (`lab`)**:
  - Đường dẫn: `config.lab_repo() / "tasks"`.
  - Quét: Glob `*/*/task.json`.
  - Task ID: `<practice_area>/<task_name>`.
  - Domain: `parts[0]` (Tên practice area).
- **WorkBuddy (`wb`)**:
  - Yêu cầu `subset` thuộc `("office", "web", "code")`.
  - Đường dẫn: `config.wb_repo() / "datasets" / f"wb-bench-{subset}-v1.0" / "tasks"`.
  - Quét: Glob `*/task.toml`. Đọc file bằng `tomllib`.
  - Lấy trường: `role` (đối với subset `code`) hoặc `category` (đối với `web` và `office`).
  - Ràng buộc: Bắt buộc tồn tại `instruction.md` trong cùng thư mục task.

### 3.2. Split Selection & Validation Engine (`select()`)

Hàm `select(tasks, split, path, *, benchmark)` kiểm soát phân chia dữ liệu:
- Chấp nhận 3 chế độ: `"all"`, `"train"`, `"test"`.
- Nếu `path is None`: Chỉ cho phép `split == "all"`. Ngược lại bắt buộc phải có `--split-file`.
- **Ràng buộc bất biến (Invariants)**:
  1. `data["benchmark"] == benchmark` (Không dùng nhầm split file của benchmark khác).
  2. `train` và `test` phải là danh sách task ID dạng string, không trùng lặp nội bộ.
  3. Tính rời rạc tuyệt đối: $\text{train} \cap \text{test} = \emptyset$.
  4. Toàn vẹn vũ trụ task: $(\text{train} \cup \text{test}) \subseteq \text{tasks.keys()}$.

### 3.3. Stratified Partitioning Generator (`scripts/split_tasks.py`)

Thực hiện phân vùng ngẫu nhiên nhưng bảo toàn phân bố của từng domain:
```python
# Stratified sampling per domain with deterministic seed
for domain, ids in sorted(by_domain.items()):
    random.Random(f"{seed}:{domain}").shuffle(ids)
    n = int(len(ids) * train_fraction)
    train.extend(ids[:n])
    test.extend(ids[n:])
```
- **Output JSON Schema**:
  ```json
  {
    "benchmark": "jb",
    "seed": 42,
    "train_fraction": 0.5,
    "train": ["accountants/task_01", "..."],
    "test": ["accountants/task_02", "..."]
  }
  ```

---

## 4. Runner Presets & Configuration Reverse Engineering

Hệ thống cấu hình tại `third_party/wb_runner/configs/` chịu trách nhiệm đóng gói, cấu hình môi trường bảo mật và cấp quyền cho agent khi thực thi tác vụ.

### 4.1. OpenCode Settings Preset (`v1_14.json`)

Đường dẫn: `configs/harnesses/opencode/presets/settings/v1_14.json`
```json
{
  "$schema": "https://opencode.ai/config.json",
  "autoupdate": false,
  "share": "disabled",
  "permission": {
    "*": "allow",
    "websearch": "deny",
    "codesearch": "deny",
    "question": "deny",
    "plan_exit": "deny"
  },
  "tools": {
    "websearch": false,
    "codesearch": false,
    "question": false,
    "plan_exit": false
  }
}
```

#### Phân tích bảo mật & REA Findings:
1. **Anti-Leak Deny List**: Chặn hoàn toàn 4 công cụ `websearch`, `codesearch`, `question`, `plan_exit`.
   - *Lý do*: Tránh việc Agent dùng công cụ tìm kiếm bên ngoài để tra cứu đề thi, rubrics hoặc solutions của benchmark đã được publish trên internet.
   - *Parity*: Đảm bảo tính công bằng (parity) tương tự danh sách deny của Claude Code và CodeBuddy Code.
2. **Telemetry & Privacy**: Vô hiệu hóa tính năng auto-update (`autoupdate: false`) và chia sẻ dữ liệu (`share: "disabled"`).
3. **Execution Guardrails**:
   - `OPENCODE_DISABLE_AUTOUPDATE=1`
   - `OPENCODE_TELEMETRY_DISABLED=1`
   - `OPENCODE_DISABLE_PROJECT_CONFIG=1` (Ngăn task repo ghi đè cấu hình hoặc tự bật lại tool bị cấm).

### 4.2. Harness Defaults & Version Bindings

#### A. OpenCode Family (`opencode` & `oc-harness`)
- **`opencode/_defaults.yaml`**:
  - Agent: `workbuddy_bench.agents.oc_agent:OcAgent`
  - Giao thức: `openai` (Chat Completions passthrough, không cần chuyển đổi a2o như Claude Code).
  - Mount Path: `/opt/opencode` (Dockerfile tại `docker/Dockerfile`).
  - Max Turns: `null` (OpenCode không hỗ trợ `--max-turns`; vòng lặp được giới hạn bởi ngân sách step/tool và Harbor trial timeout).
- **`oc-harness/_defaults.yaml`**:
  - Agent: `workbuddy_bench.agents.oc_harness_agent:OcHarnessAgent`.
  - Tái sử dụng Docker image và deny preset của `opencode` để đảm bảo binary và tool gate trùng khớp 100%.
  - Cơ chế nạp động (`_materialize_harness`):
    - Đọc từ biến môi trường `WB_HARNESS_WS`.
    - Đóng gói tar.gz gồm: `skills/` -> `.config/opencode/skill`, `scripts/` -> `harness_scripts`, `plugin/` -> `.config/opencode/plugin`, `sub_agents/*/AGENT.md` -> `.config/opencode/agent/<name>.md`.
    - Tự động inject danh sách plugins `./plugin/<name>.ts` vào cấu hình base64 `opencode.json`.

#### B. Codex Family (`codex-harness`)
- **`codex-harness/_defaults.yaml` & `0.144.6.yaml`**:
  - Agent: `workbuddy_bench.agents.codex_harness_agent:CodexHarnessAgent`.
  - Giao thức: `openai`.
  - Binary Mount: `/opt/codex` (phiên bản `0.144.6`).
  - Cơ chế nạp động (`_materialize_harness`):
    - Nạp các thư mục root: `AGENTS.md`, `.agents`, `scripts`, `.codex`.
    - Giải nén trực tiếp vào `/workspace` và thực hiện git commit trước khi agent bắt đầu (`commit pre-agent`).

---

## 5. Benchmark Adapters & Judge Metrics In-Depth

### 5.1. JobBench Adapter (`benchmarks/jobbench.py`)

#### A. Định danh và Quản lý Lưu trữ (Rollout Store)
- Địa chỉ hóa theo **LABEL**, không theo thư mục run:
  - Output: `<store>/<profession>/<taskN>/model_output/<label>`
  - Trajectory: `<store>/<profession>/<taskN>/model_traj/<label>`
- Seed Task an toàn: Sao chép input từ dataset vào store một lần duy nhất qua cơ chế khóa nguyên tử `_STORE_SEED_LOCK` và thư mục tạm `.task_folder.tmp.{pid}.{tid}`.

#### B. Trích xuất Deliverables
- Chạy qua driver subprocess `_EXTRACT_DRIVER` gọi module extractor nội bộ của `judge.py`:
  - `convert_file_to_text(f)`: Trích xuất nội dung văn bản (xlsx, docx, pdf...).
  - `extract_all_file_contents(run_dir)`: Flat representation phục vụ LLM selection / evaluation.
  - `collect_image_paths(run_dir)`: Danh sách ảnh cho Vision Judge.
- Fallback: `_raw_extract()` đọc trực tiếp text file với ngưỡng cắt `_MAX_CHARS_PER_FILE = 50,000` ký tự.

#### C. Chấm điểm & Xử lý Lỗi Judge
- Đọc từ candidate file theo thứ tự ưu tiên: `reporting` judge file -> `own` judge file (`eval_<label>/<model>_judge.json`).
- Parsing (`_parse_details()`):
  - Metric có trọng số (Weighted):
    $$\text{score} = \frac{\text{total\_score}}{\text{max\_score}}$$
    Trả về `{ "n_passed": total, "n_criteria": mx, "all_pass": (n_passed == n_criteria), "metric": "weighted" }`.
  - Metric không trọng số (Unweighted fallback): Khi `max_score == 0`, dùng tổng số tiêu chí đạt `n_p` trên tổng số tiêu chí `n_c`.
- Xử lý Agent không sinh output (`_no_output_score()`):
  - Phân tích `RUBRICS.json`, tính tổng trọng số tối đa và gán điểm $0.0$ thực tế (`"no_output": True`).
- Xử lý Judge gặp sự cố:
  - Nếu gặp lỗi transport hoặc chuỗi lỗi thuộc `_JUDGE_FAILURE_PREFIXES`, file bị cách ly đổi tên thành `.judge_failed` và trả về `None` (tuyệt đối không coi lỗi hạ tầng là điểm 0).

---

### 5.2. WorkBuddy-Bench Adapter & Anti-Leak Shield (`workbuddy.py`, `wb_render.py`)

#### A. Phân vùng Subsets & Tiêu chuẩn Deliverable
1. **`code`**:
   - Deliverable: Git patch duy nhất (`verifier/agent.patch`).
   - Scoring: Rule-based (chạy test suite thực tế).
2. **`web`**:
   - Deliverable: Workspace nén (`verifier/agent.workspace.tar.gz`).
   - Scoring: LLM Judge (`WB_WEB_JUDGE`).
3. **`office`**:
   - Deliverable: Raw files tại `verifier/raw_artifacts/**` hoặc patch.
   - Scoring: Rubric-based evaluation.

#### B. Tường lửa Chống Rò rỉ Thông tin Chấm điểm (`wb_render.py`)
Mọi dữ liệu mà model/agent đọc được đều BẮT BUỘC đi qua cổng kiểm duyệt `_admit()`:
- **ALLOWLIST Cực đoan**:
  ```python
  ALLOWLIST = {
      "office": ("verifier/raw_artifacts/**", "verifier/agent.patch"),
      "web": ("verifier/agent.workspace.tar.gz",),
      "code": ("verifier/agent.patch",),
      "sec": ("artifacts/logs/artifacts/**",),
  }
  ```
- **FORBIDDEN (Cấm tuyệt đối)**: Chặn mọi file do verifier sinh ra trong quá trình chấm (`score.json`, `reward.json`, `results.xml`, `test_output.txt`, `evidence/**`, `judge_evidence/**`).
- **Heuristic Scanner (`_is_verifier_authored`)**:
  - Quét 4000 ký tự đầu của file text.
  - Từ chối ngay nếu xuất hiện các dấu hiệu: `"verifier-owned"`, `"verifier-generated"`, `"judge rubric"`, `"pass_rate"`, `"failed_checks"`.

#### C. Thang điểm & Thứ tự Ưu tiên (Score Precedence)
Hàm `score_from_payload(payload: dict) -> float | None`:
$$\text{Priority}: \text{reward} \succ \text{overall} \succ \text{test\_pass\_rate} \succ \left(\frac{\text{tests\_passed}}{\text{tests\_total}}\right)$$
- Giá trị bắt buộc chuẩn hóa trong đoạn $[0.0, 1.0]$.
- Kết quả trả về cho hệ thống:
  ```python
  {
      "n_passed": round(sc * 100),
      "n_criteria": 100,
      "all_pass": sc >= 1.0,
      "raw_score": sc,
  }
  ```

---

### 5.3. Harvey LAB Adapter (`benchmarks/lab.py`)

#### A. Practice Areas & Work Types
- **4 Work Types**:
  - `analyze`: Phân tích rủi ro, đối chiếu sự thật pháp lý và đưa ra khuyến nghị thực thi.
  - `review`: So sánh baseline document và proposed text, đề xuất chấp nhận/từ chối/chỉnh sửa.
  - `draft`: Soạn thảo điều khoản, kiểm tra định nghĩa, điều kiện tiên quyết và tính hợp lệ.
  - `research`: Nghiên cứu thẩm quyền, tiền lệ pháp và áp dụng vào hồ sơ vụ việc.

#### B. Đánh giá Chấm điểm (Harvey Eval)
- Chạy module ngoài qua subprocess: `evaluation.run_eval` với Python môi trường riêng (`config.LAB_PYTHON`).
- Đọc kết quả từ `scores.json`:
  ```python
  {
      "n_passed": s.get("n_passed"),
      "n_criteria": s.get("n_criteria"),
      "all_pass": s.get("all_pass"),
  }
  ```
- Timeout subprocess là 3600s; lỗi judge trả về `None`, không ghi nhận 0.

---

## 6. Zero-Search Task Specification Summary

Nhằm tuân thủ Directive #5 trong `AGENTS.md`, các vị trí mã nguồn then chốt được định vị chính xác:

| Mục tiêu nghiệp vụ | Target File | Anchors / Symbols | Logic xử lý chính |
| :--- | :--- | :--- | :--- |
| **Discovery** | `harness2/benchmarks/tasks.py` | `def discover(...)` (L26-59) | Glob files theo cấu trúc thư mục đặc thù của 3 benchmark |
| **Splits Validation** | `harness2/benchmarks/tasks.py` | `def select(...)` (L62-88) | Kiểm tra tính rời rạc $train \cap test = \emptyset$ và toàn vẹn vũ trụ task |
| **Split Generator** | `scripts/split_tasks.py` | `def main(...)` (L29-65) | Phân tầng theo domain với seed ngẫu nhiên xác định |
| **OpenCode Preset** | `configs/harnesses/opencode/presets/settings/v1_14.json` | `permission`, `tools` (L5-17) | Deny `websearch`, `codesearch`, `question`, `plan_exit` |
| **Anti-Leak Filter** | `harness2/benchmarks/wb_render.py` | `_admit(...)` (L64-88) | Kiểm tra Allowlist và từ chối truy cập mọi Verifier metadata |
| **JobBench Scoring** | `harness2/benchmarks/jobbench.py` | `_parse_details(...)` (L592-620) | Weighted total/max score với unweighted fallback |
| **WorkBuddy Scoring** | `harness2/benchmarks/workbuddy.py` | `score_from_payload(...)` (L408-420) | Thứ tự ưu tiên `reward > overall > test_pass_rate > ratio` |
| **Harvey LAB Scoring** | `harness2/benchmarks/lab.py` | `def score(...)` (L961-1002) | Thực thi `evaluation.run_eval` và đọc `scores.json` |

---

## 7. Verification & Sign-Off Checklist (Lead Dev Gate)

- [x] Đọc và đối chiếu toàn bộ source code trong `projects/harness2/harness2/benchmarks/`.
- [x] Bóc tách toàn diện cấu trúc presets JSON và YAML tại `projects/harness2/third_party/wb_runner/configs/`.
- [x] Làm rõ cơ chế phân chia train/test stratified splits và invariants kiểm tra.
- [x] Phân tích chi tiết công thức và độ ưu tiên tính điểm của JobBench, WorkBuddy và Harvey LAB.
- [x] Xác lập ranh giới Anti-Leak bảo vệ tính khách quan của kỳ đánh giá benchmark.
- [x] Hoàn thiện tài liệu đặc tả chuẩn Markdown tại `docs/spec/harness2-benchmarks.md`.
- [ ] Lead Dev Review & Approval.
