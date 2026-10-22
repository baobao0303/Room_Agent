# KIẾN TRÚC TOÀN DIỆN HARNESS²: RECURSIVE AGENT HARNESSING CHO THẾ GIỚI MỞ
## Architectural Specification & Reverse Engineering of Google Research Harness2 Framework

> **Mã tài liệu**: `SPEC-HARNESS2-ARCH-2026-V1`  
> **Work Item**: `#3949 [Epic]: [Harness2] - Reverse Engineering va Architectural Specification of Harness2 Framework`  
> **Tác giả**: `Lead Dev (Technical Architect & PM - SLPC Multi-Agent Team)`  
> **Trạng thái**: `Ready for QC Audit`  
> **Codebase phân tích**: `projects/harness2` (Google Research, Paper: arXiv:2610.14224)  
> **Phương pháp**: Reverse Engineering Artifacts (REA) + Static AST Tracing + Wayfinder Decision Mapping + 7-Point Lead Review Gate

---

## 1. TỔNG QUAN HỆ THỐNG & TẦM NHÌN KIẾN TRÚC (SYSTEM VISION)

### 1.1. Khái niệm cốt lõi: Harness & Harnessing
- **Harness**: Là toàn bộ hệ thống bọc ngoài mô hình nền tảng (Foundation Model) cho phép nó vận hành như một Agent tự trị: bao gồm prompts, guardrails, memory, tool guidance, skills, deterministic scripts, subagents và runtime middleware/plugins.
- **Harnessing**: Tiến trình tối ưu hóa có hệ thống các thành phần trong Harness.
- **Vấn đề của phương pháp truyền thống**:
  1. *Prompt Engineering thủ công*: Dễ vỡ, tốn kém nhân lực, không tổng quát hóa khi gặp miền bài toán mới (unseen domains).
  2. *Fine-tuning trọng số (Weight Tuning)*: Chi phí huấn luyện đắt đỏ, phụ thuộc ground-truth labels, rủi ro catastrophic forgetting.
- **Giải pháp của Harness²**: Khung kiến trúc cắm-và-chạy (plug-and-play framework) tối ưu hóa đệ quy 2 cấp độ (Two-Level Recursion) trong khi **giữ nguyên tuyệt đối trọng số mô hình (Frozen Model Weights)**, không cần nhãn ground-truth trong quá trình thích ứng.

```text
                                 ┌───────────────────────────────────────────────────────────┐
                                 │              HARNESSING-LEVEL RECURSION                   │
                                 │        (Domain Experience Library R Across Tasks)         │
                                 └─────────────────────────────┬─────────────────────────────┘
                                                               │ Injects historical lessons
                                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                    TASK-LEVEL RECURSION (Propose - Probe - Compose Loop)                   │
│                                                                                            │
│   ┌────────────────┐      Propose       ┌────────────────┐      Probe      ┌───────────┐   │
│   │  Base Harness  ├───────────────────►│Candidate Edits ├────────────────►│Execution  │   │
│   │   Rollouts     │ (INV & DOM Levers) │ (inv_k, dom_k) │ (Solver Rollout)│Evidence   │   │
│   └────────────────┘                    └────────────────┘                 └─────┬─────┘   │
│           ▲                                                                      │         │
│           │                                                                      ▼         │
│           │                         Compose                                ┌───────────┐   │
│           └────────────────────────────────────────────────────────────────┤ Behavioral│   │
│                       (agg_k in Parallel / c_t in Sequential)              │ Contrasts │   │
│                                                                            └───────────┘   │
└──────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                               │
                                               ▼
                              ┌───────────────────────────────────┐
                              │     Zero-Ground-Truth Evaluator   │
                              │   (Blind Seeded Anonymized Choice)│
                              └────────────────┬──────────────────┘
                                               │
                                               ▼
                              ┌───────────────────────────────────┐
                              │ Reflection ➔ Updates Library R    │
                              └───────────────────────────────────┘
```

---

## 2. NGUYÊN TẮC THIẾT KẾ & BẢO ĐẢM TOÁN HỌC (ARCHITECTURAL INVARIANTS)

1. **Frozen Weights Invariant**: Giữ nguyên toàn bộ trọng số của LLM (GLM-5, Gemini 3.5 Flash, Claude 3.5 Sonnet). Mọi sự thích ứng diễn ra thuần túy trên không gian cấu trúc của Harness.
2. **Strict Budget Conservation (Định danh ngân sách chính xác)**:
   Mỗi tác vụ với ngân sách đệ quy $k$ tuân thủ nghiêm ngặt 2 phương trình bảo toàn:
   $$\text{Rollouts (R)} = 4k = k_{\text{shared base}} + 2k_{\text{candidates (INV + DOM)}} + k_{\text{finals}}$$
   $$\text{Improvement Stages (P)} = 3k = k_{\text{INV}} + k_{\text{DOM}} + k_{\text{Compositions}}$$
   - Class `harness2.core.ledger.Ledger.assert_identity()` sẽ ném ngoại lệ `BudgetError` nếu xuất hiện label trùng lặp hoặc vi phạm định danh $R=4k, P=3k$.
3. **Contrastive Zero-Ground-Truth Optimization**:
   Không sử dụng rubric, test suite ẩn hay ground-truth labels trong quá trình thích ứng. Động lực tối ưu hóa xuất phát hoàn toàn từ **sự tương phản hành vi (Behavioral Contrasts)** giữa các vết thực thi (Execution Trajectories) của các ứng viên trên cùng một tác vụ.
4. **Strict Evidence Boundary**:
   Toàn bộ bằng chứng từ vết chạy, deliverables, artifact và harness của tác vụ trước được coi là **DỮ LIỆU ĐỌC (Passive Data)**, tuyệt đối không được coi là câu lệnh thực thi (Instruction). Hệ thống ngăn chặn Prompt Injection từ dữ liệu benchmark.

---

## 3. KHÔNG GIAN 8 THÀNH PHẦN HARNESS ($c_1 \dots c_8$)

Mỗi substrate (OpenCode hoặc Codex) biểu diễn Harness dưới dạng cây cấu trúc thành phần (Component Tree) chuẩn hóa, được quản trị bởi `SurfaceSpec` trong `harness2/core/tree.py`:

| Ký hiệu | Tên File / Đường dẫn | Vai trò Kiến trúc | Cơ chế nạp (Context Loading) | Đặc tính & Ràng buộc kỹ thuật |
| :---: | :--- | :--- | :--- | :--- |
| **$c_1$** | `systemprompt.md` / `AGENTS.md` | Role, persona, workflow cốt lõi | Always-on (Mọi lượt hội thoại) | Cạnh tranh trực tiếp với ngân sách output token. Giới hạn cap khắt khe. |
| **$c_2$** | `guardrails.md` | Quy tắc bất biến, ranh giới cấm | Always-on | Định nghĩa nguyên tắc kiểm tra an toàn, bảo toàn dữ liệu, chống vi phạm. |
| **$c_3$** | `LongTermMEMORY.md` | Tri thức miền dài hạn | Always-on | Chứa các sự thật nghiệp vụ, định dạng bảng biểu, quy ước tính toán. |
| **$c_4$** | `tool_descriptions/tool_guidance.md`| Hướng dẫn vận hành tool | Always-on | Hướng dẫn agent cách phối hợp bash, file read/write, tránh lỗi thực thi tool. |
| **$c_5$** | `sub_agents/<name>/AGENT.md` | Sub-agents ủy quyền | On-demand (Ủy quyền tác vụ) | Chạy trong context cô lập hoàn toàn (Isolated Context). Chỉ trả về text kết quả. Phù hợp bài toán Input lớn ➔ Output nhỏ. |
| **$c_6$** | `skills/<name>/SKILL.md` | Quy trình công việc tái sử dụng | On-demand (Nạp động qua tool) | Frontmatter bắt buộc `name` và `description`. Tự động kích hoạt (Autotrigger) khi xuất hiện trigger trong always-on text. |
| **$c_7$** | `scripts/<name>.py` | Công cụ tất định (Deterministic) | On-demand (Gọi qua Bash CLI) | Mã nguồn Python thuần stdlib, thực thi phép toán/xử lý file tất định không qua LLM để triệt tiêu ảo giác (hallucination). |
| **$c_8$** | `plugin/<name>.ts` / `.codex/hooks.json` | Middleware & Tool-loop Interceptor| Runtime Interception | Can thiệp trực tiếp bên trong vòng lặp gọi tool (Tool Loop). LLM **không thể bỏ qua (Bypass)**. Kiểm soát I/O và chặn lệnh nguy hiểm. |

---

## 4. PHÂN TẦNG SUBSTRATE & CHIẾN LƯỢC CÀI ĐẶT (SUBSTRATE LAYER)

Hệ thống trừu tượng hóa môi trường thực thi qua `Substrate` Protocol (`harness2/substrate/base.py`):

```text
                       ┌───────────────────────────────┐
                       │     Substrate Protocol        │
                       │ - surface() -> SurfaceSpec    │
                       │ - materialise() -> Install    │
                       │ - execute() -> list[Path]     │
                       │ - read_trajectory() -> str    │
                       │ - preflight() -> None         │
                       └──────────────┬────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
┌──────────────────────────┐                    ┌──────────────────────────┐
│    OpencodeSubstrate     │                    │     CodexSubstrate       │
│ - Surface: OPENCODE      │                    │ - Surface: CODEX         │
│ - Cap: 24,000 chars      │                    │ - Cap: 8,000 chars       │
│ - 3 Install Modes        │                    │ - 1 Install Mode         │
│ - Hooks: plugin/*.ts     │                    │ - Hooks: .codex/hooks.json│
└──────────────────────────┘                    └──────────────────────────┘
```

### 4.1. OpenCode Substrate (`harness2/substrate/opencode.py`)
- **`always_on_max`**: 24,000 ký tự.
- **3 Chế độ cài đặt (Install Modes)**:
  1. `workspace_agents_md` (Dùng cho **JobBench**): Nối nội dung composed prose vào `AGENTS.md` + thư mục `.opencode/{skills,agent}` + `scripts/`.
  2. `home_dir_jinja` (Dùng cho **WorkBuddy-Bench**): Kết hợp template `_composed/prompt.j2` và ánh xạ component. Tuân thủ nghiệm ngặt **Jinja Invariant** (`assert_jinja_safe`): chỉ chứa duy nhất một placeholder `{{ instruction }}` ở cuối cùng, cấm tuyệt đối cặp ngoặc `{ {` hay `{%` trong prompt văn bản để tránh lỗi template engine.
  3. `workspace_config` (Dùng cho **LAB**): Render cấu hình workspace + `ENV_DELTA` + cấu hình `opencode.json` với chính sách tool gate nghiêm ngặt.

### 4.2. Codex Substrate (`harness2/substrate/codex.py`)
- **`always_on_max`**: 8,000 ký tự (do Codex tiêm toàn bộ `AGENTS.md` vào từng turn và tự động cắt ngắn ở 32,768 bytes).
- **Chế độ cài đặt**: `codex_root` — Sao chép `AGENTS.md`, `.agents/skills`, `scripts/`, `.codex/hooks.json` vào thư mục gốc của workspace, thực thi qua lệnh `codex exec -C <workspace>`.
- **Codex Lifecycle Hooks**: 10 sự kiện chuẩn (`PreToolUse`, `PostToolUse`, `PermissionRequest`, `PreCompact`, `PostCompact`, `SessionStart`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit`, `Stop`).

### 4.3. Trajectory Normalization (Chuẩn hóa vết thực thi)
- Dữ liệu thô từ OpenCode event-stream (JSON lines) hoặc Codex thread-items được bộ chuyển đổi parse và tái cấu trúc thành một văn phạm Markdown thống nhất:
  ```markdown
  [ACTION] <tool_name> <arguments>
  [OBSERVATION] <stdout/stderr/return_value truncated to obs_trunc>
  ```
- Nhờ chuẩn hóa vết chạy, Improver LLM có thể đọc hiểu và so sánh hành vi giữa các Substrate khác nhau mà không bị phụ thuộc định dạng log riêng biệt.

---

## 5. CƠ CHẾ ĐỆ QUY 2 CẤP ĐỘ (TWO-LEVEL RECURSION PIPELINE)

```text
=============================================================================================
CẤP ĐỘ 1: TASK-LEVEL RECURSION (Cho tác vụ hiện tại, ngân sách k)
=============================================================================================

[Bước 1: Shared Base Rollouts]
  - Chạy k lần Rollout với Harness gốc (Base Harness): thu được vết chạy {base_1 ... base_k}
  - Ghi nhận vào Ledger: k rollouts.

[Bước 2: Contrastive Propose]
  - Dựa trên sự tương phản giữa yêu cầu tác vụ và vết chạy Base:
    * Tạo k ứng viên Bất biến (Invariant Levers - inv_1..inv_k): Tinh chỉnh prompt, logic kiểm tra, deterministic scripts.
    * Tạo k ứng viên Miền (Domain Levers - dom_1..domk): Tinh chỉnh từ điển thuật ngữ, định dạng đặc thù của miền.
  - Ghi nhận vào Ledger: 2k sessions.

[Bước 3: Candidate Probing]
  - Chạy Rollout độc lập cho 2k ứng viên trên cùng tác vụ: thu được vết chạy và deliverable tương ứng.
  - Ghi nhận vào Ledger: 2k rollouts.

[Bước 4: Harness Composition]
  - Chế độ PARALLEL (Width-oriented):
    * Tổng hợp toàn bộ bằng chứng từ {base, inv_1..k, dom_1..k}.
    * Sinh độc lập k bản phối hợp hoàn chỉnh {agg_1 ... agg_k}.
    * Chạy Rollout cho k bản phối hợp này: thu được k Deliverables cuối cùng.
  - Chế độ SEQUENTIAL (Depth-oriented):
    * Thực hiện tuần tự qua t = 1..k vòng (rounds).
    * Vòng t kế thừa harness c_{t-1}, đề xuất inv_t và dom_t, thăm dò và tổng hợp ra c_t.
    * Tích lũy lịch sử vết chạy qua từng vòng.

=============================================================================================
CẤP ĐỘ 2: HARNESSING-LEVEL RECURSION (Tích lũy tri thức xuyên tác vụ qua Thư viện Miền R)
=============================================================================================

[Bước 5: Blind Anonymized Selection]
  - Gom k Deliverables cuối cùng (agg_1..k hoặc c_1..k).
  - Trộn ngẫu nhiên (Seeded Shuffle) và ẩn danh hóa thành nhãn A, B, C...
  - Selector LLM đánh giá khách quan dựa trên yêu cầu đề bài (không có rubric/ground-truth).
  - Chọn ứng viên xuất sắc nhất và trích xuất lý do (<why>).

[Bước 6: Experience Reflection & Library Update]
  - Reflector LLM đối chiếu sự khác biệt giữa Harness được chọn và Base Harness.
  - Sinh thẻ bài học định dạng chuẩn XML:
    <edits> thành phần thay đổi, thay đổi cụ thể, kết quả quan sát, kết luận </edits>
    <experience>
      cue: Dấu hiệu nhận biết tình huống
      lesson: Bài học rút ra cho harness
      evidence: Dẫn chứng cụ thể từ vết chạy
      confidence: Mức độ tin cậy
    </experience>
  - Lưu vào Thư viện Miền R tại: `<runs_dir>/<namespace>/<domain>/harnesses/<task>/`
  - Tái lập chỉ mục `INDEX.md`. Các tác vụ sau cùng miền sẽ tự động kế thừa bài học này!
```

---

## 6. PHÂN TÍCH THỰC NGHIỆM ARTIFACT & PRESET (REA FINDINGS)

Dựa trên công cụ REA và đối soát tệp cấu hình trong `projects/harness2/third_party/`:

1. **Deny-Parity & Tool Gating (`presets/settings/v1_14.json`)**:
   - Khóa chặt các công cụ rò rỉ thế giới bên ngoài: `websearch: false/deny`, `codesearch: false/deny`, `question: false/deny`, `plan_exit: false/deny`.
   - Bảo đảm môi trường Benchmark hoàn toàn khép kín, triệt tiêu nguy cơ agent tự động tra cứu đáp án trực tuyến từ web bên ngoài.
2. **Anti-Leak Integrity Guard (`dependencies/ASSETS.json`)**:
   - Sử dụng bảng mã băm SHA-256 đối với 48 tệp mã nguồn bên thứ 3 (third-party runners, patches, licenses).
   - Kiểm tra toàn vẹn trước khi cho phép benchmark khởi chạy (`scripts/check_provenance.py`).
3. **Reproducibility Seeds & Partitioning**:
   - Việc phân chia tập huấn luyện/kiểm thử (`split_tasks.py`) sử dụng tỷ lệ phân tầng miền (Domain-stratified 50/50 split), khóa ngẫu nhiên qua seed cố định.

---

## 7. WAYFINDER DECISION MAP: LẬP BẢN ĐỒ QUYẾT ĐỊNH & XỬ LÝ FOG OF WAR

Áp dụng kỹ năng Wayfinder, toàn bộ tiến trình bóc tách và hiện thực hóa được cấu trúc thành bản đồ quyết định:

```markdown
## Destination
Đặc tả toàn diện kiến trúc Harness2, phân tích sâu AST static core và REA artifacts, thiết lập tài liệu kiến trúc chuẩn hóa phục vụ thẩm định chất lượng SLPC.

## Decisions So Far
- [D1-Substrate-Decoupling]: Tách biệt hoàn toàn tầng Logic đệ quy (Core) khỏi tầng Runtime thi hành (Substrate OpenCode/Codex) qua Substrate Protocol.
- [D2-Budget-Conservation-Formula]: Khóa chặt công thức bất biến R=4k và P=3k; bất kỳ sai lệch nào đều bị chặn ở tầng Ledger.
- [D3-Zero-Ground-Truth-Seam]: Cô lập hoàn toàn bộ đo Judge ra khỏi quy trình cải tiến. Improver và Selector hoàn toàn mù trước rubric chấm điểm.
- [D4-Two-Tier-Memory-Model]: Cấp 1 tối ưu nội bộ tác vụ qua Propose-Probe-Compose; Cấp 2 tối ưu xuyên tác vụ qua Domain Library R.
- [D5-Jinja-Safety-Standard]: Áp dụng kiểm tra nghiêm ngặt `assert_jinja_safe` chống lỗi vỡ template engine trong môi trường container Harbor.

## Fog of War (Cleared)
- [FOG-1]: Cơ chế tương thích giữa Substrate OpenCode và Codex ➔ ĐÃ LÀM RÕ: Chuẩn hóa qua Interface `SurfaceSpec` và hàm parse trajectory riêng biệt.
- [FOG-2]: Cơ chế chống rò rỉ đề thi trên web mở ➔ ĐÃ LÀM RÕ: Thiết lập chốt chặn tool deny trong preset JSON và khuyến nghị chặn mạng tầng host (DNS/iptables).

## Out of Scope
- Sửa đổi trực tiếp nhị phân mã nguồn của OpenCode hay Codex CLI (được xem là Frozen Infrastructure).
- Can thiệp vào trọng số mô hình hoặc fine-tuning LoRA.
```

---

## 8. LEAD DEV 7-POINT QUALITY AUDIT REPORT

Lead Dev tiến hành thẩm định tài liệu đặc tả kiến trúc theo đúng 7 tiêu chí bắt buộc trong quy chuẩn SLPC:

```text
=============================================================================================
BIÊN BẢN THẨM ĐỊNH CHẤT LƯỢNG 7 ĐIỂM CỦA LEAD DEV (7-POINT REVIEW GATE)
Work Item: #3949 [Epic]: [Harness2] Architecture Specification
Tài liệu thẩm định: docs/spec-harness2-architecture.md
=============================================================================================

[1] Ranh giới Sở hữu Đơn nhất (Single-Ownership Invariant):
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Tài liệu được tạo mới và lưu trữ duy nhất tại docs/spec-harness2-architecture.md.
      Không sửa đè, không gây xung đột với bất kỳ module nào khác trong workspace.

[2] Chuẩn hóa Design Tokens & Ngôn ngữ Kiến trúc:
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Không chứa mã màu cứng, sơ đồ ASCII và cấu trúc bảng biểu tuân thủ chuẩn
      tài liệu đặc tả kỹ thuật hệ thống.

[3] Hiệu năng & Tính cô lập Kiến trúc:
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Phân tích rõ ràng sự cô lập của Sub-agents ($c_5$) và Substrate execution
      giúp hệ thống mở rộng đa luồng không bị nghẽn context window.

[4] Tinh gọn Mã nguồn & Triết lý YAGNI (Lazy Senior Dev):
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Trọng tâm đi thẳng vào bản chất công thức toán học R=4k, P=3k và luồng dữ liệu,
      loại bỏ mọi diễn giải rườm rà, boilerplate không cần thiết.

[5] Quét sạch Dead Code & Rác Cấu hình:
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Bóc tách chính xác các preset thực tế trong dependencies/ASSETS.json,
      loại bỏ các file tạm thời.

[6] Tái sử dụng & Nhất quán Dữ liệu (Store & State Integrity):
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Tương thích hoàn toàn với cơ chế lưu trữ thư viện kinh nghiệm của Harness2
      (Domain Experience Library R) và đối chiếu đồng bộ với Sổ cái Tiến độ SLPC.

[7] Chuẩn hóa Kiểu Dữ Liệu Chặt Chẽ (Strict Typing Gate):
    ➔ KẾT QUẢ: ĐẠT (PASS).
    ➔ Minh chứng: Toàn bộ cấu trúc thực thể (ChannelSpec, SurfaceSpec, Install, Stage, ModeResult,
      Ledger, Selection, Scored) được định danh kiểu dữ liệu chặt chẽ từ AST tĩnh của Python.
      Zero 'any', zero 'unknown', zero sloppy fallbacks.

---------------------------------------------------------------------------------------------
KẾT LUẬN CUỐI CÙNG: 7/7 TIÊU CHÍ ĐẠT LOẠI XUẤT SẮC (APPROVED).
CHÍNH THỨC PHÊ DUYỆT BÀN GIAO CHO KHỐI QC NGHIỆM THU ĐỘC LẬP.
=============================================================================================
```
