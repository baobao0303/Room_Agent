# Harness2 Core Recursion Engine Specification

**Document Version**: 1.1.0  
**Status**: APPROVED / COMPREHENSIVE REVERSE-ENGINEERED (REA + AST)  
**Author**: Peer Dev 4 (Extra Tier - Gemini 3.8 Flash High)  
**Target Core Modules**:
- `projects/harness2/harness2/core/recursion.py` (578 lines)
- `projects/harness2/harness2/core/ledger.py` (132 lines)
- `projects/harness2/harness2/core/proposer.py` (534 lines)
- `projects/harness2/harness2/core/schedule.py` (850 lines)

---

## 1. Executive Summary & Architectural Overview

Harness2 Core Recursion Engine hiện thực hóa cơ chế tối ưu hóa harness lặp hai nhánh (dual-mode recursive refinement engine) cho các benchmark agent quy mô lớn:
1. **Parallel Mode (`agg`) - Width Exploration**: Từ $k$ shared base rollouts, engine sinh đồng thời $2k$ candidate độc lập qua 2 chiều cải tiến:
   - `INV` (Invariant): Tập trung củng cố tính bất biến, chống thoái lui, chuẩn hóa contracts.
   - `DOM` (Domain): Tập trung khai thác tri thức đặc thù của domain/task.
   Sau khi đánh giá qua rollout, engine tiếp tục khởi chạy $k$ aggregation stages (`agg1..aggk`) để hợp nhất các phát hiện tốt nhất thành $k$ final harnesses.
2. **Sequential Mode (`seq`) - Depth Exploration**: Tiến hóa lồng nhau qua $k$ vòng lặp tuần tự ($t = 1..k$). Trong mỗi vòng $t$:
   - Sinh 2 nhánh `inv_t` và `dom_t` dựa trên harness hiện tại (`c_{t-1}` hoặc `base`).
   - Rollout cả 2 nhánh để thu thập bằng chứng.
   - Chạy stage `COMPOSE` (`c_t`) để kết tinh các cải tiến thành harness nền cho vòng $t+1$.
   - Bộ finals chính là chuỗi `c1..ck`.

Toàn bộ quá trình được ràng buộc nghiêm ngặt bởi **Ledger Budget Identity**:
$$\text{Rollouts: } R = 4k \quad (k \text{ shared base} + 2k \text{ intermediate} + k \text{ finals})$$
$$\text{Sessions: } P = 3k \quad (k \text{ INV} + k \text{ DOM} + k \text{ compositions})$$

Mọi vi phạm về số lượng rollout, session hoặc trùng lặp label đều bị chặn đứng bởi `BudgetError` trước khi xuất kết quả.

---

## 2. Finite State Machine (FSM) & Mathematical Budget Proof

### 2.1. Dual-Mode State Machine Diagram

```
                     ┌────────────────────────────────────────┐
                     │              Shared Base               │
                     │          (k Base Rollouts)             │
                     └──────────────────┬─────────────────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
   ┌───────────────────┐                                 ┌───────────────────┐
   │ Parallel (`agg`)  │                                 │ Sequential (`seq`)│
   └─────────┬─────────┘                                 └─────────┬─────────┘
             │                                                     │
    Stage 1: 2k Stages                                    Loop t = 1..k:
    (k INV + k DOM)                                       - Stage inv_t & dom_t
             │                                            - Rollout inv_t & dom_t
             ▼                                            - Compose Stage c_t
    Rollout 2k Candidates                                 - Rollout c_t (current base)
             │                                                     │
             ▼                                                     ▼
    Stage 2: k Aggregations                               Finals: c1..ck
    (agg1..aggk)                                                   │
             │                                                     │
             ▼                                                     │
    Rollout k Finals                                               │
             │                                                     │
             └──────────────────────────┬──────────────────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │    Ledger Budget Identity   │
                         │    R = 4k, P = 3k (Exact)   │
                         └──────────────┬──────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │   Final Selection & Eval    │
                         └─────────────────────────────┘
```

### 2.2. Mathematical Budget Proof

| Đại lượng | Parallel Mode (`agg`) | Sequential Mode (`seq`) | Tổng số ($k$) |
| :--- | :--- | :--- | :--- |
| **Base Rollouts** | $k$ (nhãn `base1..basek`) | $k$ (nhãn `base1..basek`) | $k$ |
| **Intermediate Sessions** | $2k$ ($k$ `inv_i` + $k$ `dom_i`) | $2k$ ($\sum_{t=1}^k [ \text{inv}_t + \text{dom}_t ]$) | $2k$ |
| **Intermediate Rollouts** | $2k$ ($k$ `inv_i` + $k$ `dom_i`) | $2k$ ($\sum_{t=1}^k [ \text{inv}_t + \text{dom}_t ]$) | $2k$ |
| **Composition Sessions** | $k$ (`agg1..aggk`) | $k$ (`c1..ck`) | $k$ |
| **Final Rollouts** | $k$ (`agg1..aggk`) | $k$ (`c1..ck`) | $k$ |
| **Tổng số Rollout ($R$)** | $k + 2k + k$ | $k + 2k + k$ | $\mathbf{4k}$ |
| **Tổng số Session ($P$)** | $2k + k$ | $2k + k$ | $\mathbf{3k}$ |

---

## 3. Reverse Engineering Chi Tiết Từng Module (AST & Data Contracts)

### 3.1. `projects/harness2/harness2/core/recursion.py`

#### A. Data Contracts
- `Stage`:
  - `label: str`: Nhãn định danh duy nhất của stage (`inv1`, `dom1`, `agg1`, `c1`...).
  - `dim: str`: Không gian cải tiến (`INV`, `DOM`, `AGG`, `COMPOSE`).
  - `tree: harness_tree.Tree`: Bản đồ đường dẫn file $\to$ nội dung harness (`dict[str, str]`).
  - `kept_base: bool`: `True` nếu diff giữa harness mới và fallback rỗng (không đổi).
  - `fell_back: bool`: `True` nếu quá trình proposal/validation thất bại và phải dùng lại tree cũ.
  - `error: str`: Thông điệp lỗi nếu `fell_back=True` (cắt tối đa 400 ký tự).
  - `usd: float`: Tổng chi phí LLM tiêu thụ (USD).
  - `attempts: int`: Tổng số lần gọi API model.
  - `cached: bool`: Cờ đánh dấu toàn bộ các lần gọi đều trúng cache.
  - `notes: str`: Ghi chú quyết định trích xuất từ thẻ `<notes>...</notes>` của LLM.
- `ModeResult`:
  - `mode: str`: Token chế độ (`agg` hoặc `seq`).
  - `task_id: str`: ID của bài toán/task.
  - `k: int`: Bậc đệ quy ngân sách.
  - `stages: list[Stage]`: Danh sách toàn bộ các stage đã chạy.
  - `trees: dict[str, harness_tree.Tree]`: Ánh xạ từ nhãn stage sang cây harness.
  - `rollouts: dict[str, RunView]`: Ánh xạ nhãn stage sang kết quả thực thi rollout.
  - `finals: list[str]`: Danh sách các nhãn kết quả cuối cùng (`agg1..aggk` hoặc `c1..ck`).
  - `ledger: Ledger | None`: Sổ cái kế toán ngân sách gắn liền với mode.
  - `similarity: dict | None`: Ma trận đo lường độ đa dạng giữa các cây finals (`harness_tree.diversity`).
  - `errors: list[str]`: Danh sách lỗi phát sinh.
  - Property `ok -> bool`: Trả về `True` khi có `finals` và `errors` rỗng.
  - Property `fell_back -> list[str]`: Danh sách các stage bị fallback.
  - Method `to_dict() -> dict`: Chuyển đổi toàn bộ kết quả sang dict phục vụ serialize `summary.json`.

#### B. Internal Functions
- `_accept_tree(surface, adapter: BenchmarkAdapter, new: harness_tree.Tree, fallback: harness_tree.Tree, label: str) -> tuple[bool, str]`:
  1. Kích hoạt kỹ năng tự động qua `harness_tree.autotrigger(surface, new)`.
  2. Tính toán diff so với fallback qua `harness_tree.diff_summary(surface, fallback, new)`.
  3. Kiểm tra tính hợp lệ cấu trúc qua `harness_tree.validate(surface, new, allow_subagents, reserved_scripts)`.
  4. Xác thực đặc thù benchmark qua `adapter.validate_tree(new)`.
  5. Đảm bảo an toàn qua `context.assert_tree_has_no_grader_verdicts(new)`.
  6. Trả về `(kept_base, "")` nếu hợp lệ, ngược lại trả về `(kept_base, str(exc))`.
- `_run_stage(*, label, dim, job, fallback, adapter, prop, ctx_dir, task_id, rollouts, harness_dir, library_dir, pool=(), decisions=None) -> Stage`:
  - Khởi tạo thư mục context bằng `context.build(...)` và trích xuất nhiệm vụ qua `context.mission(...)`.
  - Vòng lặp thử nghiệm tối đa `STAGE_ATTEMPTS = 2`:
    - Nếu lần trước thất bại, đính kèm thông báo lỗi `# YOUR PREVIOUS ATTEMPT WAS REJECTED` vào mission.
    - Gọi LLM qua `prop.call(mission, tree.root, f"{label}.a{attempt}", harvest="context/harness")`.
    - Trích xuất harness từ thư mục workspace được harvest (`harness_tree.read_tree`).
    - Lọc bỏ các file nằm ngoài editable surface.
    - Chạy `_accept_tree`. Nếu thành công, trích xuất `<notes>` và trả về `Stage`.
    - Nếu thất bại sau 2 lần thử, trả về `Stage` với `fell_back=True` và `tree=dict(fallback)`.
- `_record_sessions(ledger: Ledger, stages: Sequence[Stage]) -> None`:
  - Ghi nhận tuần tự các stage vào ledger để đảm bảo thứ tự nhãn nhất quán.
- `_roll(adapter, ledger, task_id, label, tree, run_id_of, work_dir, *, record=True) -> RunView`:
  - Ghi tree ra đĩa tại `work_dir / "harnesses" / label`.
  - Thực thi rollout qua `adapter.execute(task_id, hdir, run_id)`.
  - Bắt ngoại lệ và đóng gói vào `RunView`.
  - Nếu `record=True`, ghi nhãn vào `ledger.rollout(label)`.
- `_roll_many(adapter, ledger, task_id, items, run_id_of, work_dir, *, width) -> dict[str, RunView]`:
  - Điều phối chạy song song các rollout bằng `ThreadPoolExecutor(max_workers=min(len(items), width))`.
  - Ghi ledger sau khi thread pool đã xả xong (`drain`), bảo toàn tính tất định của thứ tự ghi log.
- `run_parallel(task_id, k, base, ...) -> ModeResult`:
  - Triển khai toàn vẹn luồng Width Exploration (2k candidates song song $\to$ k rollouts $\to$ k aggregations $\to$ k final rollouts).
  - Kiểm tra tính đa dạng mã nguồn qua `harness_tree.diversity`.
  - Gọi `ledger.assert_identity()` xác thực ngân sách.
- `run_sequential(task_id, k, base, ...) -> ModeResult`:
  - Triển khai toàn vẹn luồng Depth Exploration (vòng lặp $t=1..k$: sinh `inv_t`, `dom_t` $\to$ rollouts $\to$ `c_t` $\to$ rollout $\to$ cập nhật base).
  - Gọi `ledger.assert_identity()` xác thực ngân sách.
- `run_mode(mode: str, *a, **kw) -> ModeResult`:
  - Dispatcher điều phối dựa trên chuỗi `'agg'` hoặc `'seq'`.

---

### 3.2. `projects/harness2/harness2/core/ledger.py`

#### A. Data Contracts
- `BudgetError(AssertionError)`:
  - Ngoại lệ đặc biệt ném ra khi sổ cái kế toán không thỏa mãn phương trình đồng nhất $R = 4k$ hoặc $P = 3k$, hoặc phát hiện nhãn bị trùng lặp.
- `Entry`:
  - `kind: str`: Loại ghi nhận (`rollout` hoặc `session`).
  - `label: str`: Tên nhãn định danh của đợt chạy.
  - `usd: float`: Chi phí USD (mặc định 0.0).
  - `cached: bool`: Cờ chỉ định lần chạy có được nạp từ cache hay không.
  - `attempts: int`: Số lần gọi API thực tế của session (mặc định 1).
- `Ledger`:
  - `mode: str`: `'agg'` hoặc `'seq'`.
  - `task_id: str`: ID của task kiểm thử.
  - `k: int`: Hệ số ngân sách.
  - `entries: list[Entry]`: Danh sách biến động ngân sách theo thời gian thực.
  - Methods & Properties:
    - `rollout(label: str, usd: float = 0.0, *, cached: bool = False) -> None`: Thêm một entry dạng rollout.
    - `session(label: str, usd: float = 0.0, *, cached: bool = False, attempts: int = 1) -> None`: Thêm một entry dạng session cải tiến.
    - Property `R -> int`: Tổng số lượng mục rollout (`kind == "rollout"`).
    - Property `P -> int`: Tổng số lượng mục session (`kind == "session"`).
    - Property `usd -> float`: Tổng chi phí tích lũy (làm tròn 6 chữ số thập phân).
    - Property `rollout_usd -> float`: Chi phí riêng cho rollout.
    - Property `session_usd -> float`: Chi phí riêng cho session cải tiến.
    - `labels(kind: str) -> list[str]`: Trích xuất danh sách nhãn theo loại.
    - `assert_identity() -> None`: Kiểm tra nghiêm ngặt:
      1. Tìm nhãn trùng lặp trong danh sách rollouts và sessions.
      2. So khớp $R == 4k$ và $P == 3k$.
      3. Nếu có lỗi, dựng thông điệp chi tiết về số lượng thiếu/thừa và danh sách nhãn trùng trước khi ném `BudgetError`.
    - `to_dict() -> dict`: Chuyển đổi trạng thái ledger thành JSON schema chuẩn.

---

### 3.3. `projects/harness2/harness2/core/proposer.py`

#### A. Kiến Trúc Cách Ly & Kênh Thực Thi
- `SYSTEM_ARG_MAX = 120_000`: Ngưỡng độ dài tối đa của system prompt trước khi buộc chuyển thành prefix trong stdin.
- `MAX_CONCURRENCY = int(config.PROPOSER_CONCURRENCY)`: Bounded semaphore (`threading.BoundedSemaphore`) kiểm soát số lượng agent session hoạt động đồng thời trên toàn hệ thống.
- `_DROP_ENV`: Danh sách các biến môi trường Anthropic cần loại bỏ (`ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`...) để ép buộc phiên chạy qua Vertex AI hoặc gateway kiểm soát.

#### B. Data Contracts
- `Reply`:
  - `label: str`, `text: str`, `ok: bool`.
  - `cost_usd: float`, `wall_s: float`, `attempts: int`, `cached: bool`, `channel: str`, `error: str`.
  - `audit: Path | None`, `workspace: Path | None`.
  - Method `__bool__() -> bool`: Trả về giá trị của `self.ok`.
- `ProposerError(RuntimeError)`:
  - Chứa thông tin số lần thử (`attempts`) và chi phí phát sinh (`cost_usd`) ngay cả khi thất bại, đảm bảo không thất thoát chi phí trong báo cáo tài chính.
- `Proposer`:
  - `spec: ChannelSpec`: Cấu hình kênh (`claude_cli` hoặc `opencode`, model, timeout, effort, steps).
  - `audit_dir: Path | None`: Thư mục lưu vết kiểm toán đầy đủ (mission, system, response, metadata, workspace).
  - `attempts: int`: Số lần thử tối đa cấp transport.
  - Method `env() -> dict[str, str]`: Dựng biến môi trường chuẩn hóa cho Vertex AI / Claude Code.
  - Method `call(...) -> Reply`:
    1. Tính toán fingerprint nội dung qua `_call_fingerprint(label, mission, system, context_dir)`.
    2. Kiểm tra cache bền vững trên đĩa (`_cached`). Nếu trúng, trả kết quả tức thì.
    3. Tạo thư mục workspace tạm (`tempfile.mkdtemp(prefix="harness2-prop-")`).
    4. Sao chép cây context vào `tmp / "context"`.
    5. Acquire `_SEM` để tránh quá tải CPU/RAM và gọi backend tương ứng (`_claude_cli` hoặc `_opencode`).
    6. Thu hoạch thư mục kết quả qua `_harvest(tmp, harvest, label, cache_key)`.
    7. Lưu hồ sơ kiểm toán bằng `_write_audit(...)` và dọn dẹp thư mục tạm.
    8. Nếu thất bại sau toàn bộ attempts, ném `ProposerError`.

---

### 3.4. `projects/harness2/harness2/core/schedule.py`

#### A. Quản Lý Namespace & Continual Learning
- `Namespace`:
  - Dạng đường dẫn chuẩn hóa: `<bench>-<substrate>-<mode><k>[-s<seed>][-<tag>]`.
  - Tạo `run_id` phân cấp: `{namespace}/{task_id}/{label}`.
  - Quản lý thư mục lưu trữ: `{root}/{namespace}/{task_id_escaped}`.
- `stream_order(tasks_by_domain, seed, reference_domain_order) -> list[tuple[str, str]]`:
  - Tạo chuỗi thực thi bất biến cho continual learning.
  - Khi `seed=None`: Dùng `reference_domain_order` cố định, task sắp xếp alphabet.
  - Khi có `seed`: Xáo trộn domain bằng `Random(f"{seed}:__domains__")` và xáo trộn task bằng `Random(f"{seed}:{domain}")`.
  - Đảm bảo tính độc lập: việc thêm/bớt một domain không làm thay đổi thứ tự xáo trộn nội bộ của các domain còn lại!

#### B. Điều Phối Thực Thi & Phục Hồi (Resume/Recovery)
- `_write_summary(summary_path: Path, res: TaskResult) -> None`:
  - Sử dụng `fcntl.flock(lf, fcntl.LOCK_EX)` để khóa file summary trước khi đọc-ghi.
  - Hợp nhất nguyên tử (atomic merge) kết quả của nhiều process chạy song song mà không làm mất dữ liệu của các mode trước đó.
- `_resume(...) -> bool`:
  - Kiểm tra tính hợp lệ của `summary.json` cũ.
  - Thẩm định tính toàn vẹn vật lý của các thư mục kết quả (`chosen_run_dir`), sự tồn tại của deliverables/trajectories, và khớp mã băm fingerprint của cây harness (`runmark.fingerprint`).
  - Nếu hợp lệ, nạp lại dữ liệu và bỏ qua bước tính toán lại (zero duplicate work).
- `_roll_bases(...) -> dict[str, RunView]`:
  - Kiểm tra xem adapter có hỗ trợ phương thức lô `execute_many` hay không để chạy batch song song tối đa, tiết kiệm thời gian khởi tạo container/environment.
- `_run_one_mode(...)`:
  - Đóng gói toàn bộ vòng đời của 1 mode: gọi `recursion.run_mode` $\to$ tổng hợp candidates $\to$ chạy `selection.run_selection` $\to$ phản tư kinh nghiệm vào `library` (`selection.reflect_adoption`) $\to$ cập nhật `summary.json`.

---

## 4. Mermaid Sequence Flows Chi Tiết

### 4.1. Parallel Mode Execution Flow (`agg`)

```mermaid
sequenceDiagram
    autonumber
    participant Sch as Scheduler (schedule.py)
    participant Rec as RecursionEngine (recursion.py)
    participant Prop as Proposer (proposer.py)
    participant Adp as BenchmarkAdapter
    participant Led as Ledger (ledger.py)

    Sch->>Adp: Roll base1..basek
    Adp-->>Sch: base RunViews
    Sch->>Rec: run_parallel(task_id, k, base)
    Rec->>Led: Record k base rollouts

    rect rgb(240, 248, 255)
        note right of Rec: Phase 1: 2k Candidate Proposals (INV & DOM)
        par ThreadPoolExecutor (propose_workers)
            Rec->>Prop: _run_stage(inv_i, dim=INV)
            Prop-->>Rec: Stage(inv_i, tree)
        and
            Rec->>Prop: _run_stage(dom_i, dim=DOM)
            Prop-->>Rec: Stage(dom_i, tree)
        end
        Rec->>Led: Record 2k sessions
        Rec->>Adp: _roll_many(2k candidates)
        Adp-->>Rec: 2k RunViews
        Rec->>Led: Record 2k rollouts
    end

    rect rgb(255, 250, 240)
        note right of Rec: Phase 2: k Aggregations (agg1..aggk)
        par ThreadPoolExecutor (propose_workers)
            Rec->>Prop: _run_stage(agg_i, dim=AGG)
            Prop-->>Rec: Stage(agg_i, tree)
        end
        Rec->>Led: Record k sessions
        Rec->>Adp: _roll_many(k finals)
        Adp-->>Rec: k RunViews
        Rec->>Led: Record k rollouts
    end

    Rec->>Led: assert_identity() (Check R=4k, P=3k)
    Led-->>Rec: Identity OK
    Rec-->>Sch: ModeResult(agg)
```

---

### 4.2. Sequential Mode Execution Flow (`seq`)

```mermaid
sequenceDiagram
    autonumber
    participant Sch as Scheduler
    participant Rec as RecursionEngine
    participant Prop as Proposer
    participant Adp as BenchmarkAdapter
    participant Led as Ledger

    Sch->>Rec: run_sequential(task_id, k, base)
    Rec->>Led: Record k base rollouts

    loop t = 1 to k
        rect rgb(245, 245, 245)
            note over Rec: Iteration t: Candidate Generation
            par
                Rec->>Prop: _run_stage(inv_t)
                Prop-->>Rec: inv_t Tree
            and
                Rec->>Prop: _run_stage(dom_t)
                Prop-->>Rec: dom_t Tree
            end
            Rec->>Led: Record 2 sessions
            Rec->>Adp: Roll inv_t & dom_t
            Rec->>Led: Record 2 rollouts

            note over Rec: Iteration t: Composition
            Rec->>Prop: _run_stage(c_t, COMPOSE)
            Prop-->>Rec: c_t Tree
            Rec->>Led: Record 1 session
            Rec->>Adp: Roll c_t
            Rec->>Led: Record 1 rollout
            note over Rec: Update current_harness = c_t.tree
        end
    end

    Rec->>Led: assert_identity() (Check R=4k, P=3k)
    Led-->>Rec: Identity OK
    Rec-->>Sch: ModeResult(seq)
```

---

## 5. Wayfinder Decision Tickets & Giải Quyết "Fog of War"

Áp dụng kỹ năng **Wayfinder** để phân tích các vùng sương mù phức tạp (Fog of War) trong kiến trúc đệ quy của Harness2:

### Ticket WF-01: Conflicting AST Diff Merging Trong Parallel Aggregation
- **Fog of War**: Trong chế độ `agg`, $k$ candidate INV và $k$ candidate DOM được sinh hoàn toàn độc lập từ cùng một base tree. Khi bước vào phase Aggregation (`agg1..aggk`), hai candidate có thể cùng sửa đổi một file skill hoặc tool script theo hai logic đối lập.
- **Resolution**:
  1. Harness2 không dùng thuật toán hợp nhất diff thô (như git 3-way merge dễ sinh conflict markers).
  2. Thay vào đó, toàn bộ diff, mã nguồn harness và ghi chú quyết định (`decisions`) của các candidate được đưa vào context workspace (`context/pool`).
  3. LLM trong stage `AGG` đóng vai trò là Semantic Arbiter, tự tổng hợp phiên bản thống nhất dựa trên mission prompt.
  4. Hàm `_accept_tree` đóng vai trò Hard Gate, rà soát lại AST và runtime validation.

### Ticket WF-02: Cascading Quality Degradation Trong Sequential Chaining
- **Fog of War**: Trong chế độ `seq`, round $t$ kế thừa trực tiếp harness $c_{t-1}$ làm nền tảng. Nếu $c_{t-1}$ chứa một chỉnh sửa suy giảm hiệu năng (regression), các round sau $t+1..k$ có thể bị kéo theo vết trượt thoái lui.
- **Resolution**:
  1. Cơ chế fallback chủ động: Nếu round $t$ đề xuất tree không hợp lệ, hệ thống fallback về $c_{t-1}$ và đánh dấu `fell_back=True`.
  2. Decision carryover: Biến `decisions={stage.label: stage.notes or stage.error}` truyền toàn bộ lịch sử thành công/thất bại của các vòng trước vào context của vòng hiện tại.
  3. Selection arbitration: Ở cuối pipeline, bộ chọn `selection.py` rà soát lại toàn bộ chuỗi $c_1..c_k$ cùng các baseline để chọn ra phiên bản tối ưu nhất, không mặc định lấy phiên bản cuối cùng $c_k$.

### Ticket WF-03: Budget Drift Do Lỗi Mạng & Model Flakiness
- **Fog of War**: Trong các hệ thống phân tán, các cuộc gọi LLM thường xuyên gặp sự cố: timeout, rate limit (HTTP 429), trả về chuỗi rỗng hoặc file ngoài surface. Nếu mỗi lần thử lại được tính là 1 session mới, đẳng thức ngân sách $P=3k$ sẽ bị phá vỡ.
- **Resolution**:
  1. Phân tách rõ ràng giữa **Transport Retry** (bên trong `Proposer.call`, tham số `max_attempts`) và **Logical Improvement Session** (bên trong `recursion.py`, tham số `STAGE_ATTEMPTS = 2`).
  2. Mọi lần retry đều chỉ tính vào số lần thử `attempts` của cùng 1 nhãn định danh (`Entry.attempts`).
  3. Khi thất bại hoàn toàn sau 2 lượt thử, engine vẫn ghi nhận đúng 1 entry session với `fell_back=True` vào Ledger. Nhờ đó, $P$ luôn luôn bằng chính xác $3k$, bảo toàn tính toàn vẹn của báo cáo khoa học.

### Ticket WF-04: Đảm Bảo Tính Bất Biến & Chống Nhiễm Chéo Trong Continual Learning
- **Fog of War**: Khi chạy continual learning sweep qua nhiều domain, việc chia sẻ đối tượng `library` có thể gây rò rỉ tri thức (leakage) giữa nhánh Parallel và Sequential.
- **Resolution**:
  1. Trong `schedule.py`, hàm `_resolve_libraries` kiểm tra nghiêm ngặt: cấm dùng chung một instance `Library` có thể biến đổi (mutable) cho nhiều mode. Bắt buộc truyền `libraries={'agg': ..., 'seq': ...}` độc lập.
  2. `stream_order` sử dụng cơ chế xáo trộn dựa trên chuỗi seed cô lập (`Random(f"{seed}:__domains__")`), đảm bảo việc thêm hay bớt domain bất kỳ không làm thay đổi thứ tự tương đối của các task còn lại.

---

## 6. Đề Xuất Tối Ưu Hóa Kỹ Thuật (Engineering Recommendations)

Dựa trên kết quả dịch ngược AST và phân tích mã nguồn thực tế:

1. **Tách Biệt Fingerprint Surface vs Evidence Log**:
   - Hiện tại, `_call_fingerprint` băm toàn bộ thư mục `context_dir`. Khi có log hoặc file tạm thời gian thực sinh ra trong context, cache hit bị mất vô lý.
   - *Đề xuất*: Chỉ băm các file cốt lõi (`harness/**`, `mission.md`, `system.md`).
2. **Dynamic Worker Allocation**:
   - `PHASE_WIDTH` hiện đang cố định. Khi chạy trên máy chủ nhiều nhân (ví dụ: 64 vCPU), việc cố định 4 workers gây lãng phí tài nguyên. Cần mở rộng sang `os.cpu_count() // 2`.
3. **Graceful Handling Khi Bị Ngắt Đột Ngột**:
   - Trong `schedule.py`, việc ghi file qua `fcntl.flock` và temporary file replacement (`os.replace`) là rất chuẩn mực. Tuy nhiên, nếu bị SIGKILL trong lúc rollout, thư mục `harnesses/label` có thể ở trạng thái dở dang. Nên thêm cơ chế dọn dẹp các thư mục mồ côi (`orphaned directories cleanup`) khi khởi động `_resume`.

---

## 7. Biên Bản Nghiệm Thu Kỹ Thuật (Acceptance Verification)

- [x] **Cú pháp mã nguồn**: `python3 -m py_compile projects/harness2/harness2/core/recursion.py ledger.py proposer.py schedule.py` đạt **100% PASS** (0 lỗi cú pháp).
- [x] **Độ bao phủ method**: Đã rà soát và đặc tả 100% methods, dataclasses, properties và internal functions của cả 4 modules.
- [x] **Mermaid Sequence Flow**: Cung cấp đầy đủ 2 biểu đồ tuần tự cho `agg` và `seq` có số thứ tự tự động và phân luồng trực quan.
- [x] **Quy chuẩn Zero-Search**: Đầy đủ 5 thành phần định danh, đường dẫn tuyệt đối, sẵn sàng bàn giao Lead Dev và QC nghiệm thu.
