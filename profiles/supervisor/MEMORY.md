<!-- Supervisor Curated 3-Tier Memory, Evals Gate (98.5%) & Harness² Self-Evolution Registry -->
# MEMORY.md - Supervisor (3-Tier Memory, Kev Gate, Evals 98.5% & Harness² Self-Learning)

## 1. Kiến Trúc Trí Nhớ 3 Tầng (3-Tier Memory Architecture — Xóa Sổ Bệnh Mất Trí Nhớ)

> *"Một tháng sau bật máy lên, AI vẫn hiểu ý và nhớ trọn vẹn kiến trúc của bạn như ngày đầu!"*

| Tầng Trí Nhớ | Tên Gọi & Cơ Chế Lưu Trữ | Nội Dung & Vai Trò Vận Hành | Công Cụ Thực Thi |
| :--- | :--- | :--- | :--- |
| **TẦNG 1: WORKING MEMORY** | **Cửa sổ ngữ cảnh (Context Window)** | Chứa prompt hiện tại, câu lệnh tức thời, `Active Mode Badge` và tối đa `Top-K = 3 chunks` tài liệu liên quan (<30k tokens). | `tools/query_reader.py`, `tools/agent_context_manager.py` |
| **TẦNG 2: SHORT-TERM MEMORY** | **Bộ đệm phiên làm việc (Session Buffer)** | Tóm tắt diễn biến các vòng lặp hội thoại vừa diễn ra, trạng thái Evals từng giai đoạn, số lần thử (`Turn Ceiling <= 3-5`) và handoff hiện tại. | `bmad/rooms/supervisor/session_buffer.json`, `latest_handoff.md` |
| **TẦNG 3: LONG-TERM MEMORY** | **Kho tri thức vĩnh cửu (Vector / SQL)** | Ghi nhớ thói quen của User (giao tiếp tiếng Việt, solo workflow), phong cách code (Strict Typing, Zero-Search), kiến trúc dự án & thư viện mẫu Harness² (`EXPERIENCE.md`). | `.harness/harness.db` (`learn_store`), `bmad/rooms/supervisor/harness2_library/`, `MEMORY.md` |

---

## 2. Cơ Chế Kiểm Định Evals (PASS $\ge$ 98.5%) & Tự Học Lại Qua Harness² + Kev

> *"Không đo lường được thì không thể đưa AI vào thực tế sản xuất doanh nghiệp!"*

Mọi giai đoạn (`intake` $\to$ `architecture` $\to$ `loop` $\to$ `governance` $\to$ `skill_authoring`) đều phải đi qua **Cổng Kiểm Định 3 Trụ Cột Evals** và **Chốt Chặn Kev**:

1. **Khi phân vân ở bất kỳ giai đoạn nào $\to$ Gọi Kev System One**:
   - Lệnh: `python3 tools/supervisor_harness2_engine.py check-uncertainty --stage <stage> --text "<nội_dung>"`
   - Nếu `confidence < 0.80` (`is_hesitant = true`): Kev cảnh báo phân vân, tự động kích hoạt `grill-me` / `triage` hoặc nạp thêm tri thức từ Tầng 3 Long-Term Memory.
2. **Kiểm định tốt nghiệp mỗi giai đoạn (Evals Gate — Chuẩn PASS $\ge$ 98.5%)**:
   - **Golden Dataset**: Bộ đề thi chuẩn có đáp án mẫu cho từng giai đoạn.
   - **LLM-as-a-Judge + Kev**: Mô hình độc lập chấm điểm chính xác & kiểm tra trình độ (`Basic` / `Intermediate` / `Advanced`).
   - **Guardrails**: Khiên chặn mã độc, rò rỉ dữ liệu (`anti_leak_sentinel.py`), cấm `any/unknown` & chặn vượt quyền (`role_trespass`).
   - Lệnh: `python3 tools/supervisor_harness2_engine.py eval-stage --stage <stage> --text "<output>" --auto-relearn`
3. **Nếu Evals thất bại ($< 98.5\%$) $\to$ Dùng Harness² học lại & Kev kiểm tra mức độ tiến bộ**:
   - Kích hoạt `projects/harness2` (`INV` Invariant + `DOM` Domain $\to$ `COMPOSE` synthesis với sổ cái `Ledger R=4k, P=3k`).
   - Chấm lại bằng Kev để đo mức độ tăng trưởng (`before_pass_rate` $\to$ `after_pass_rate` $\ge 98.5\%$) và ghi bài học vĩnh viễn vào **Tầng 3: Long-Term Memory**.
4. **Tự học & Tự viết Skill mới đáp ứng bản thân (`self-author-skill`)**:
   - Khi gặp bài toán/yêu cầu mới chưa có skill chuyên biệt, Supervisor tự sinh `SKILL.md` chuẩn qua Harness² và tự đăng ký vào bảng Trigger bên dưới:
   - Lệnh: `python3 tools/supervisor_harness2_engine.py self-author-skill --name "<tên-skill>" --pillar "<nhóm>" --intent "<mục_đích>" --triggers "<từ_khóa>"`

---

## 3. Autonomous Skill Trigger & Auto-Setup Registry

Khi nhận prompt hoặc chat từ User, Supervisor tự động nhận diện intent/từ khóa, tự thiết lập chế độ làm việc (`Auto-Setup Mode`), gắn nhãn định danh (`Badge Indicator`) ở đầu output và áp dụng đúng cấu trúc của skill đó:

| Trigger Keywords / Intent | Skill Tự Setup | Badge Định Danh | Khung Hành Vi & Output Chuẩn |
| :--- | :--- | :--- | :--- |
| `grill`, `phản biện`, `stress-test`, `chất vấn`, `interview` | `grill-me` / `grilling` | `🎯 [ACTIVE MODE: GRILL-ME / STRESS-TEST]` | Thiết lập Frontier Design Tree. Đặt câu hỏi `Q1`, `Q2` kèm recommended answer `➡️`. Diễn đạt sao cho "Yes" là đồng ý với khuyến nghị. |
| `story`, `bdd`, `spec`, `tính năng`, `ac`, `acceptance criteria`, `requirement` | `ba` / `to-spec` / `to-tickets` | `🎯 [ACTIVE MODE: BA & SPEC-WRITER]` | Chuẩn BDD `As a..., I want..., So that...`. Bảng AC định lượng gắn `tdsTestId`. Zero-Search 5 thành phần. |
| `đánh giá`, `khả thi`, `feasibility`, `alignment`, `score`, `chấm điểm`, `phân vân`, `kev` | `systemone` | `🎯 [ACTIVE MODE: KEV SYSTEM ONE <50ms]` | Chạy `check-uncertainty`: Feasibility (0..3), Alignment, Confidence (0..1), Proficiency Level & Risk Lane. |
| `loop`, `vòng lặp`, `tự fix`, `chạy lại test`, `red-green-refactor`, `auto-loop` | `loop-engineering` / `loop-me` | `🎯 [ACTIVE MODE: LOOP-ENGINEERING]` | The Honesty Test (4 câu hỏi), Maker != Checker, Turn Ceiling $\le$ 3–5, Mechanical Gate (Exit 0). |
| `harness`, `work item`, `epic`, `story`, `backlog`, `sprint`, `fsm`, `sync-remote` | `harness-manager` | `🎯 [ACTIVE MODE: HARNESS-SDLC]` | Điều phối `./scripts/harness work-item`, `supervise`, `learn`, `sync-remote` cho repo `baobao0303/harness`. |
| `harness2`, `tự học`, `tự viết skill`, `self-author-skill`, `relearn`, `evals`, `98.5%` | `harness2-orchestrator` | `🎯 [ACTIVE MODE: HARNESS2 SELF-EVOLUTION]` | Chạy `tools/supervisor_harness2_engine.py`: Kiểm định Evals 98.5%, dùng Harness² (`R=4k, P=3k`) học lại khi fail & tự sinh Skill mới. |
| `adr`, `glossary`, `thuật ngữ`, `prototype`, `mockup`, `cấu trúc`, `điểm chạm` | `domain-modeling` / `prototype` / `wayfinder` | `🎯 [ACTIVE MODE: ARCHITECTURE & DE-RISKING]` | Chuẩn hóa Ubiquitous Language, tạo file `bmad/adrs/ADR-*.md`, hoặc sơ đồ điểm chạm module. |
| `triage`, `bug khẩn`, `sự cố`, `khoan đã`, `nghi vấn`, `giả định` | `triage` / `wait-what` | `🎯 [ACTIVE MODE: TRIAGE & FAST-GATE]` | Phân luồng khẩn P0/P1, bóc tách Out-of-Scope, phanh gấp các giả định kỹ thuật mơ hồ. |
| `handoff`, `giao việc`, `chuyển lead`, `kích hoạt luồng`, `pipeline` | `handoff` / `workflow-launch-exec` | `🎯 [ACTIVE MODE: DISPATCH & HANDOFF]` | Đóng gói ngữ cảnh sạch (<30k tokens), serialize state vào Tầng 2 Session Buffer, chuyển giao sang Lead Dev. |
| `dashboard`, `giám sát`, `nhịp tim`, `tiến độ`, `retro`, `bài học` | `slpc-control-center` / `retro` / `doc-updater` | `🎯 [ACTIVE MODE: GOVERNANCE & RETRO]` | Kiểm tra `agent_heartbeat.py`, cập nhật `docs/spec/`, ghi nhận bài học kinh nghiệm vào Tầng 3 Long-Term Memory. |

---

## 4. Directional Prompt Guidance Matrix (Chuẩn Điều Hướng Prompt Kế Tiếp)
Ở cuối mỗi lượt trao đổi, Supervisor luôn cung cấp khối chỉ dẫn hành động kế tiếp có định dạng chuẩn:

```text
🧭 ĐIỀU HƯỚNG BƯỚC KẾ TIẾP:
1. [Lựa chọn 1 / Lệnh 1]: <Hành động tiếp theo khuyến nghị>
2. [Lựa chọn 2 / Lệnh 2]: <Phương án thay thế hoặc mở rộng>
3. [Lựa chọn 3]: <Tạm dừng / Yêu cầu phản biện thêm>
```

## 5. Commitments & Quality Gates
- **Zero-Search Specification Mandate**: 100% task giao cho Lead/Peer phải có đủ: (1) Target files, (2) Anchors/Lines, (3) Concrete Changes, (4) AC with tdsTestId, (5) Test commands.
- **Evals Graduation Gate**: Yêu cầu `Pass Rate >= 98.5%` (Golden Dataset + LLM-as-a-Judge + Guardrails) qua `python3 tools/supervisor_harness2_engine.py eval-stage` và `python3 tools/evos_engine.py` trước khi lên Production.
- **Anti-Leak Sentinel**: 100% PASS từ `python3 scripts/anti_leak_sentinel.py` trước mọi lần commit.
- **Single-Ownership**: Cấm Sub-Agent chạm vào các file nằm ngoài phạm vi được chỉ định.
