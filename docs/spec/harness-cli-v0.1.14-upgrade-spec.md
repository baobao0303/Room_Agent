# Đặc Tả Nâng Cấp Hệ Thống: Tích Hợp Harness CLI v0.1.14 Vào Room_Agent

**Tài liệu**: Technical Specification & Migration Architecture for Harness Framework Upgrade  
**Phiên bản tài liệu**: 1.0.0  
**Ngày lập**: 2026-10-22  
**Nhánh triển khai**: `feat/upgrade-harness-cli-v0.1.14`  
**Phiên bản phát hành mục tiêu**: [Harness CLI v0.1.14](https://github.com/baobao0303/harness/releases/tag/harness-cli-v0.1.14)  
**Tác giả**: Supervisor & SLPC Architecture Team  
**Người duyệt (Reviewer)**: User  

---

## 1. Bối Cảnh & Động Lực (Executive Summary & Background)

Framework quản trị phát triển phần mềm **Harness** (`baobao0303/harness`) vừa chính thức phát hành phiên bản **v0.1.14** với các đột phá kiến trúc quan trọng:
1. **Động cơ Rust CLI Đơn Nhất (`harness-cli`)**: Binary native siêu nhẹ (~7.1MB trên Linux x64), khởi động tức thì, tối ưu hóa triệt để tài nguyên so với các runtime script Python.
2. **Kev System One Decision Engine (`harness supervise`)**: Tích hợp mô hình quyết định nhỏ gọn Kev (prefill-only, non-autoregressive) qua giao thức TypeSafe System One (`http://100.124.36.46:8008/v1/systemone`, model `kev-latest`), phân luồng rủi ro siêu tốc **sub-50ms**.
3. **Thư viện Tự Học & Chuyển Giao Thích Ứng (`harness learn`)**: Kế thừa kiến trúc Recursive Harnessing của Google Research Harness² (`harness2`), tự động tích lũy kinh nghiệm, bài học và tự động kích hoạt checklist phòng ngừa lỗi khi chuyển giao trạng thái FSM (`New -> Active -> Resolved -> Closed`).
4. **Cơ sở Dữ liệu Bền Vững SQLite (Schema Migration 007)**: Bổ sung bảng `harness_experience` quản lý kinh nghiệm tự học với chỉ mục phân vùng tối ưu.
5. **Zero-Config Mặc Định**: Đã gỡ bỏ file `.env` rườm rà, nhúng trực tiếp cấu hình endpoint nội bộ Tailscale.

**Mục tiêu của nâng cấp này**:
Hiện đại hóa toàn bộ lớp điều phối công việc trong `Room_Agent`, nâng cấp từ cơ chế script Python truyền thống sang kiến trúc lai hiệu năng cao (Hybrid Dual-Engine Architecture), trang bị năng lực tự học và phân luồng rủi ro tự động cho đội ngũ 8 agents SLPC.

---

## 2. Phân Tích Thực Trạng & Kiến Trúc Mục Tiêu (Gap Analysis)

```text
HIỆN TẠI (Legacy Python Architecture)            MỤC TIÊU NÂNG CẤP (Hybrid v0.1.14 Architecture)
┌──────────────────────────────────────┐        ┌────────────────────────────────────────────────────────┐
│ Room_Agent Orchestrator              │        │ Room_Agent Multi-Agent Orchestrator                    │
│                                      │        │  (Supervisor, Lead Dev, 4 Peers, Design, QC)           │
│  tools/harness_manager.py (Python)   │        └───────────────────────────┬────────────────────────────┘
│  scripts/harness (Python wrapper)    │                                    │
│                 │                    │                 ┌──────────────────┴──────────────────┐
│                 ▼                    │                 ▼                                     ▼
│  Floci Cloud DynamoDB & S3           │     ┌───────────────────────┐             ┌─────────────────────┐
│  (100.124.36.46:14566)               │     │ Native Rust CLI       │             │ Floci Cloud Storage │
│                                      │     │ (scripts/bin/         │             │ (DynamoDB & S3)     │
│  - Không có module tự học            │     │  harness-cli v0.1.14) │             │ (100.124.36.46:     │
│  - Không có mô hình quyết định Kev   │     │                       │             │  14566)             │
│  - State machine chạy thủ công       │     │ • harness supervise   │             │                     │
│  - Tốn thời gian duyệt task nhỏ      │     │   (Kev System One)    │             │ • Global Backlog    │
└──────────────────────────────────────┘     │ • harness learn       │◄───────────►│ • Multi-Room Sync   │
                                             │   (Self-Learning)     │  Dual-Sync  │ • Team Progress     │
                                             │ • harness work-item   │   Bridge    │ • Audit Artifacts   │
                                             │ • harness.db (SQLite) │             └─────────────────────┘
                                             └───────────────────────┘
```

### Bảng Đối Chiếu Tính Năng (Feature Parity & Enhancement)

| Hạng mục chức năng | Hiện tại trong `Room_Agent` | Sau khi nâng cấp lên `v0.1.14` |
| :--- | :--- | :--- |
| **Runtime Engine** | Python (`floci_client.py` + `boto3`) | **Native Rust Binary** (`harness-cli`) kết hợp Python Bridge. |
| **Phân luồng Rủi ro Task** | Supervisor LLM đọc prompt (1-3s, tốn token) | **Kev System One Fast-Path** (<50ms, Zero LLM Token overhead). |
| **Kinh nghiệm Tự học** | Ghi log phân tán tại `AGENT_PROGRESS.md` | **SQLite `harness_experience`** + truy vấn tự động qua `harness learn`. |
| **Ngăn ngừa Lỗi Lặp lại** | Dựa vào trí nhớ agent (dễ quên sau context compression) | **Adaptive Transition Rules**: tự động inject bài học cũ vào context task mới. |
| **Tốc độ Khởi động CLI** | ~350ms - 500ms (nạp interpreter + boto3) | **<10ms** (Compiled native x86_64 Rust binary). |
| **Bảo vệ Bảo mật** | Quét thủ công qua `git_pre_commit_guard.py` | **Tích hợp thêm CI Security Scanner** chuẩn hóa từ `harness`. |

---

## 3. Thiết Kế Chi Tiết Các Khối Nâng Cấp (Technical Components)

### 3.1. Khối 1: Triển Khai Native Rust Binary (`scripts/bin/harness-cli`)
- Tải trực tiếp binary release Linux x64 chính thức từ GitHub:
  `https://github.com/baobao0303/harness/releases/download/harness-cli-v0.1.14/harness-cli-linux-x64`
- Đặt tại đường dẫn chuẩn: `Room_Agent/scripts/bin/harness-cli` (cấp quyền `chmod +x`).
- Xác thực tính toàn vẹn qua checksum SHA-256 (`harness-cli-linux-x64.sha256`).

### 3.2. Khối 2: PM Agent - Cố Vấn Quyết Định Ngầm Đánh Giá Khả Thi & Phù Hợp

PM Agent đóng vai trò là "bộ não cố vấn định lượng" cho Supervisor và Lead Dev, sử dụng động cơ Kev System One (`http://100.124.36.46:8008/v1/systemone`) để đánh giá 2 trụ cột sống còn trước khi công việc bắt đầu:

#### A. Trụ Cột 1: Đánh Giá Mức Độ Khả Thi Kỹ Thuật (Feasibility Assessment)
- **Câu hỏi Kev**: `feasibility_rating` (`score` 0..3)
  - Mốc 0: *Bất khả thi / Thiếu điều kiện tiên quyết (Blocked)*
  - Mốc 1: *Khả thi thấp / Rủi ro phụ thuộc bên thứ ba quá lớn*
  - Mốc 2: *Khả thi có điều kiện / Cần làm bản mẫu spike hoặc nghiên cứu thêm*
  - Mốc 3: *Hoàn toàn khả thi / Codebase, DTOs, APIs đã sẵn sàng 100%*
- **Ý nghĩa**: Ngăn chặn việc giao việc mò mẫm, ép phải có đủ tài liệu/API trước khi code.

#### B. Trụ Cột 2: Đánh Giá Mức Độ Phù Hợp Chiến Lược (Alignment Assessment)
- **Câu hỏi Kev**: `strategic_alignment` (`choice`)
  - `perfect_fit`: Khớp 100% mục tiêu của User và triết lý kiến trúc (DDD, TDS UI, Strict Typing).
  - `minor_drift`: Có điểm lệch nhẹ cần Supervisor uốn nắn.
  - `scope_creep`: Phát sinh tính năng dư thừa không ai yêu cầu (YAGNI violation).
  - `architectural_violation`: Vi phạm ranh giới hệ thống hoặc tiêu chuẩn bảo mật.
- **Ý nghĩa**: Ngăn chặn Scope Creep và tình trạng "vẽ voi", bảo vệ tuyệt đối ý đồ ban đầu của User.

#### C. Biên Bản Quyết Định Của PM (Intake Decision Memo) & Quy Tắc Phân Luồng
- Khi Supervisor tiếp nhận yêu cầu từ User, PM Agent xuất bản biên bản trong **<50ms**:
  ```text
  [PM INTAKE DECISION MEMO]
  - WorkItem Type : [User Story / Bug / Tech Story]
  - Priority       : [P0 / P1 / P2 / P3] | Urgency: [0.0 - 3.0]
  - Khả thi        : [Cao (Score 2.9/3.0) - Đủ DTO và Stores]
  - Phù hợp        : [100% Khớp mục tiêu, 0% Scope Creep]
  - Risk Lane      : [Green / Yellow / Red] (Confidence: XX%)
  - BDD Story      : As a..., I want..., So that...
  - AC Definition  : AC 1, AC 2, AC 3
  - Traps to Avoid : Past lessons from harness learn
  ```
- **Quy tắc điều phối 3 luồng**:
  1. **Fast-Path Route (`automated_worker`)**:
     - Điều kiện: `Khả thi >= 2.5` VÀ `Phù hợp == perfect_fit` VÀ `Risk == Green` VÀ `Confidence >= 0.85`.
     - Hành động: Giao thẳng cho Peer Dev thực thi tự động, bỏ qua thủ tục review rườm rà.
  2. **Review-Path Route (`peer_review_queue`)**:
     - Điều kiện: `Khả thi trung bình` HOẶC `Risk == Yellow`.
     - Hành động: Giao Peer Dev làm, chuyển Lead Dev review qua 7-Point Gate.
  3. **Slow-Path Route (`human_supervisor_approval`)**:
     - Điều kiện: `Risk == Red` HOẶC `Phù hợp == scope_creep` HOẶC `Khả thi < 1.0`.
     - Hành động: Dừng lại, xin ý kiến chấp thuận của User tại chat trước khi can thiệp.

### 3.3. Khối 3: Giao Thức Tự Học Khép Kín Đa Tầng (Closed-Loop Multi-Tier Self-Learning Protocol: Harness + Hermes)

Cả **Harness** và **Hermes** đều sở hữu năng lực tự học hỏi mạnh mẽ nhưng hoạt động ở 2 cấp độ bổ trợ nhau:
- **Harness Learn Engine**: Lưu trữ tri thức cấu trúc dạng bảng (`harness_experience`) theo mô hình Recursive Agent Harnessing (Google Research Harness²), gồm: `domain`, `cue`, `lesson`, `evidence`, `confidence`, `pattern_hash`, `failure_trajectories`.
- **Hermes Persistent Skill Engine**: Lưu trữ quy trình thực thi thủ tục (Procedural Memory) qua các file `SKILL.md` và `memory`, được nạp tự động vào ngữ cảnh của Agent theo từng loại tác vụ.

Hệ thống thiết lập **Vòng lặp học tập khép kín 2 chiều** để đảm bảo: **Mỗi khi User hoặc QC phát hiện lỗi, PM Agent lập tức bóc tách bài học để toàn bộ đội ngũ "khôn hơn trước", triệt tiêu 100% việc lặp lại sai phạm cũ**.

```text
                  ┌─────────────────────────────────────────┐
                  │          USER PHẢN HỒI LỖI              │
                  │  (Ví dụ: "video icon không ăn",         │
                  │   "sao chỗ này lại đi dùng any...")     │
                  └────────────────────┬────────────────────┘
                                       │ 1. Báo trực tiếp tại Chat
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │            SUPERVISOR AGENT             │
                  │       (Tiếp nhận phản hồi từ User)      │
                  └────────────────────┬────────────────────┘
                                       │ 2. Chuyển context cho PM Agent
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │                PM AGENT                 │
                  │   (Phân tích Root Cause & Đề xuất)      │
                  │ • Bóc tách: Domain, Cue, Lesson, Trap   │
                  │ • Đánh giá mức độ vi phạm & giải pháp   │
                  └────────────────────┬────────────────────┘
                                       │ 3. Phân phối tri thức đa tầng
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     TẦNG 1: HARNESS LEARN     │               │     TẦNG 2: HERMES SKILLS     │
│   (SQLite & Floci DynamoDB)   │               │   (skills/<domain>/SKILL.md)  │
│  Lưu bản ghi kinh nghiệm      │               │  Cập nhật checklist / rule    │
│  harness learn record         │               │  bắt buộc vào file kỹ năng    │
└───────────────┬───────────────┘               └───────────────┬───────────────┘
                │                                               │
                └───────────────────────┬───────────────────────┘
                                        │ 4. Tự động "nhắc bài" ở task sau
                                        ▼
                  ┌─────────────────────────────────────────┐
                  │             LEAD DEV AGENT              │
                  │   Tra cứu `harness learn query`         │
                  │   ➔ Inject vào Zero-Search Task Spec:   │
                  │   "## BẪY LỖI CŨ CẦN TRÁNH (USER NOTE)" │
                  └────────────────────┬────────────────────┘
                                       │ 5. Giao việc có rào chắn
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │                PEER DEV                 │
                  │  Bắt buộc đọc bẫy lỗi và tuân thủ       │
                  │  100% Strict Typing, Zero Recurrence    │
                  └────────────────────┬────────────────────┘
                                       │ 6. Nghiệm thu đối soát
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │               QC VERIFIER               │
                  │  Kiểm tra xem Peer có lặp lại lỗi cũ?   │
                  │  - Tái phạm ➔ REJECT ngay lập tức       │
                  │  - Vượt qua ➔ Nghiệm thu & đóng task    │
                  └─────────────────────────────────────────┘
```

#### A. Quy Trình Xử Lý Khi User Kiểm Tra Lại Phát Hiện Lỗi (Human Feedback Loop)
1. **Bước 1 (User Signal)**: User phát hiện lỗi thực tế và phản ánh với Supervisor trong chat (ví dụ: *"video icon không ăn"*, *"chỗ này sót DTO"*).
2. **Bước 2 (PM Root Cause Analysis)**: Supervisor chuyển nguyên văn phản hồi sang PM Agent. PM Agent lập tức trích xuất:
   - `Domain`: Phân hệ chức năng bị lỗi (ví dụ: `media_video`, `angular_fe`, `context_provider`).
   - `Cue`: Hoàn cảnh / dấu hiệu kích hoạt lỗi (ví dụ: `truetype_font_missing_glyph`, `member_store_bypass`).
   - `Lesson`: Quy tắc khắc phục bắt buộc (ví dụ: `Vẽ icon vector thuần bằng hình học PIL thay vì unicode emoji`, `Inject trực tiếp MemberStore, cấm gọi thô`).
   - `Evidence`: Lỗi thực tế User chụp/báo.
   - `Confidence`: Luôn đặt mức `high` (vì là phản hồi từ User).
3. **Bước 3 (Dual-Store & Skill Ingestion)**:
   - **Ghi vào Harness Learn**: Gọi `./scripts/bin/harness-cli learn record --domain "<domain>" --cue "<cue>" --lesson "<lesson>" --evidence "<evidence>" --confidence high`. Bản ghi được đồng bộ vào cả SQLite và Floci DynamoDB.
   - **Ghi vào Hermes Skill**: Cập nhật trực tiếp bài học vào `skills/<domain>/SKILL.md` (hoặc `lead-review`, `qc`) để các phiên làm việc sau tự động nạp vào system prompt.

#### B. Quy Trình Phòng Ngừa Chủ Động Ở Tác Vụ Tiếp Theo (Next-Task Prevention)
1. **PM & Lead Pre-flight Injection**: Khi phát sinh bất kỳ task mới nào thuộc `domain` đã có bài học, hệ thống tự động chạy `./scripts/bin/harness-cli learn query --domain "<domain>"`.
2. **Zero-Search Mandate Enforcement**: Lead Dev bắt buộc chèn khối sau vào bản giao việc cho Peer:
   ```markdown
   ## ⚠️ BẪY LỖI CŨ CẦN TRÁNH (LESSONS LEARNED FROM USER/QC):
   - [Bài học 1]: <Nội dung bài học cũ trích từ DB>
   - [Quy tắc cấm]: Tuyệt đối không lặp lại lỗi <Cue>!
   ```
3. **Cổng Phạt Tái Phạm Của QC**: QC khi nghiệm thu đối soát bắt buộc phải kiểm tra hạng mục này. Nếu Peer tái phạm lỗi cũ đã được cảnh báo trong `harness learn`, QC kích hoạt `tools/agent_reprimand.py --penalize` giáng task về `Active` và phạt nặng lập tức.

### 3.4. Khối 4: Cầu Nối Đồng Bộ Kép (Dual-Sync Bridge Engine)
- Nâng cấp `tools/harness_manager.py`:
  - Thêm cờ `--engine <rust|floci|auto>`: Mặc định `auto` tự động tận dụng binary Rust `harness-cli` cho các tác vụ tính toán nhanh (supervise, learn, validate syntax) và đồng bộ trạng thái lên Floci DynamoDB.
  - Đảm bảo tương thích ngược 100% với toàn bộ scripts hiện hữu (`agent_heartbeat.py`, `orca_slpc_bridge.py`, `agent_progress.py`).

### 3.5. Khối 5: Khảo Sát & Thiết Kế Bảng Lưu Trữ Học Tập (Learning Database Architecture)

#### A. Kết Quả Khảo Sát Thực Tế Các Bảng Hiện Hữu
Đã thực thi truy vấn trực tiếp trên endpoint Floci DynamoDB (`http://100.124.36.46:14566`):
```text
=== FLOCI DYNAMODB TABLES SURVEY ===
1. harness_work_items   : 4044 items (Keys: ['id'])
2. harness_stories      : 70 items   (Keys: ['id'])
3. harness_tools        : 4 items    (Keys: ['name'])
4. harness_skills       : 85 items   (Keys: ['name'])
5. harness_skills_index : 1744 items (Keys: ['token', 'skill_name'])
6. harness_metadata     : 1 item     (Keys: ['key'])
7. agproxy_*            : 6 bảng phụ trợ proxy
```
*Kết luận khảo sát*: Hiện tại trên Floci DynamoDB **CHƯA CÓ bảng lưu trữ bài học tự học**. Toàn bộ tri thức kinh nghiệm chỉ đang được lưu cục bộ trong SQLite `harness_experience` (migration 007 của `projects/harness`).

#### B. Thiết Kế Schema Bảng `harness_experience` Trên Floci DynamoDB
Nhằm chia sẻ tri thức tự học cho toàn bộ 8 agent SLPC hoạt động song song ở bất kỳ phiên làm việc nào, hệ thống thiết kế bảng DynamoDB mới:
- **Tên bảng**: `harness_experience`
- **Partition Key (PK)**: `id` (String: định dạng `exp_<timestamp>_<uuid>`)
- **Global Secondary Index 1 (GSI_Domain)**:
  - Partition Key: `domain` (String - ví dụ: `angular_fe`, `rust_cli`, `context_provider`)
  - Sort Key: `created_at` (String ISO-8601)
  - Projection: `ALL` (Hỗ trợ truy vấn danh sách bài học theo domain đạt độ phức tạp $O(1)$)
- **Global Secondary Index 2 (GSI_WorkItem)**:
  - Partition Key: `work_item_id` (Number)
  - Projection: `ALL` (Truy vết bài học gắn với từng Task/Bug)
- **Thuộc tính chi tiết (Attributes)**:
  - `cue` (String): Tín hiệu/hoàn cảnh phát sinh vấn đề (ví dụ: `any_unknown_violation`, `missing_dto`).
  - `lesson` (String): Bài học rút ra cần áp dụng.
  - `evidence` (String): Lệnh kiểm thử hoặc log chứng minh.
  - `confidence` (String: `low` | `medium` | `high`): Mức độ tin cậy.
  - `pattern_hash` (String): Mã băm đặc trưng lỗi.
  - `harness_patch` (String, optional): Nội dung diff hoặc cấu hình tối ưu.
  - `created_at` (String): Thời điểm ghi nhận.

#### C. Cơ Chế Lưu Trữ & Đồng Bộ Kép (Dual-Store Strategy)
1. **Local SQLite (`harness.db`)**: Phục vụ truy vấn siêu tốc ($<2\text{ms}$) cho native CLI `harness-cli learn`.
2. **Cloud DynamoDB (`harness_experience`)**: Phục vụ chia sẻ tri thức tập trung giữa các agent, đồng bộ qua `tools/floci_client.py`.

---

### 3.6. Khối 6: Kế Hoạch Loại Bỏ Triệt Để `harness-ui` (Decommissioning & Clean Architecture)

#### A. Lý Do Loại Bỏ (Why Decommission?)
- Thư mục `harness-ui/` (dự án Astro cũ tại root) ban đầu được thiết kế để render web dashboard cho Harness. Tuy nhiên hiện tại hệ thống đã chuyển dịch toàn diện sang:
  1. **Orca Board Live Workspace** (giám sát đa terminal agent).
  2. **Aevum BlockSuite Real-time Kanban** (bảng Kanban kéo thả trực quan).
  3. **Stitch Obsidian Cyber-Matrix** (dashboard tĩnh tốc độ cao).
- Việc duy trì `harness-ui` đem lại nhiều rủi ro kỹ thuật:
  - Làm phình to dung lượng repo (`package-lock.json` 233KB, Dockerfile, Nginx templates).
  - Workflow `.github/workflows/docker-harness-ui.yml` và pipeline `Jenkinsfile` thường xuyên bị fail hoặc ngốn tài nguyên CI/CD không cần thiết.
  - Dễ gây lỗi drift dependency khi nâng cấp Node/NPM.

#### B. Danh Sách Các Hạng Mục Xóa Bỏ & Điều Chỉnh (Decommissioning Matrix)
1. **Xóa toàn bộ thư mục `harness-ui/`**:
   - `harness-ui/astro.config.mjs`, `harness-ui/package.json`, `harness-ui/package-lock.json`
   - `harness-ui/Dockerfile`, `harness-ui/nginx.conf.template`, `harness-ui/.dockerignore`
   - `harness-ui/src/`, `harness-ui/public/`, `harness-ui/DESIGN.md`, `harness-ui/tsconfig.json`
2. **Xóa CI Workflow thừa**:
   - Gỡ bỏ `.github/workflows/docker-harness-ui.yml`.
3. **Cập nhật `Jenkinsfile`**:
   - Xóa các Stage: `Deploy Harness UI Container`, `Deploy Static to Workspace`, và các biến môi trường `GHCR_IMAGE`, `CONTAINER_NAME`.
4. **Cập nhật `tools/harness_doctor.py`**:
   - Xóa bỏ hàm `check_frontend_bundle()` kiểm tra `harness-ui/dist/index.html` để tránh báo lỗi `warn/error` giả khi chạy healthcheck.
5. **Cập nhật Tài liệu & Sơ đồ Tri thức**:
   - Gỡ bỏ node `harness-ui` trong `bmad/architecture.json` và `bmad/README.md`.
   - Lưu trữ / đánh dấu deprecated tài liệu `docs/spec/astro-jenkins-harness-ui-spec.md`.

---

### 3.7. Khối 7: Chỉ Thị Kỹ Thuật & Đóng Góp Từ Supervisor & Lead Architect (SLPC Governance Directives)

Nhằm đảm bảo quá trình nâng cấp không làm đứt gãy luồng vận hành của 8 agent và bảo vệ tính toàn vẹn hệ sinh thái, Supervisor và Lead Architect đã thẩm định và ban hành các chỉ thị kỹ thuật mang tính pháp lệnh:

#### A. Chỉ Thị Từ Supervisor (Scope & Intent Guard)
1. **Bảo Toàn Kênh Giao Tiếp Đơn Nhất Của User**:
   - User chỉ trao đổi duy nhất tại cửa sổ chat này với Supervisor.
   - PM Agent hoạt động như một động cơ quyết định ngầm (Silent Quantitative Decision Copilot), không mở luồng hội thoại độc lập gây loãng bối cảnh hay phiền hà cho User.
2. **Phân Luồng Rủi Ro Hai Cấp (Two-Tier Risk Gate)**:
   - Các tác vụ an toàn (Green, điểm tự tin $\ge 85\%$, sửa docs, format, test read-only): Kích hoạt Fast-Path Lambda thực thi sub-50ms.
   - Các tác vụ nguy hiểm (Red: xóa bảng DB, auth, lộ secret): Bắt buộc chặn đứng lập tức để báo cáo xin lệnh trực tiếp từ User.
3. **Quy Chuẩn Zero-Search 5 Thành Phần Bắt Buộc**:
   - Mọi task kỹ thuật phân rã từ bản đặc tả này (Phase 1 đến Phase 4) bắt buộc phải đủ 5 trường định danh (Target Files, Anchors/Lines, Concrete Changes, AC định lượng, Lệnh Test). Cấm giao task 1 dòng mơ hồ.
4. **Kỷ Luật Git & Chống Rò Rỉ Tuyệt Đối (Anti-Leak Protocol)**:
   - Toàn bộ thư mục `projects/` và các file database runtime SQLite (`harness.db*`) phải nằm trọn trong `.gitignore`.
   - Giữ nguyên toàn bộ mã nguồn trên nhánh `feat/upgrade-harness-cli-v0.1.14`, tuyệt đối cấm commit tự ý lên `main`.

#### B. Chỉ Thị Kỹ Thuật Từ Lead Architect (Theo Báo Cáo Thẩm Định /lead-review)
1. **Dọn Sạch harness-ui Đến Tận Gốc (Zero-Orphan Cleanliness)**:
   - Không chỉ xóa thư mục mã nguồn `harness-ui/`, Lead Dev yêu cầu dọn sạch 100% các tàn dư: gỡ bỏ workflow CI `docker-harness-ui.yml`, gỡ bỏ các stage deploy trong `Jenkinsfile`, sửa `tools/harness_doctor.py` gỡ bỏ hàm `check_frontend_bundle()` và xóa node `harness-ui` trong `bmad/architecture.json`.
2. **Chuẩn Hóa Strict Typing Tuyệt Đối (Zero `any`, Zero `unknown`)**:
   - Binary Rust v0.1.14 đã loại bỏ hoàn toàn `unwrap()` bừa bãi và đạt 44/44 tests.
   - Lớp bridge Python (`tools/harness_rust.py`): Bắt buộc định nghĩa `@dataclass` có type hint tường minh (`SupervisionEvaluationResult`, `ExperienceRecordDto`), nghiêm cấm trả về dictionary vô danh `dict[Any, Any]`.
3. **Bảo Toàn Kho Dữ Liệu Floci DynamoDB & Tối Ưu Hóa GSI**:
   - Nghiêm cấm mọi hành vi reset hay xóa bảng `harness_work_items` (đang lưu trữ 4,044 work items) và `harness_skills` (85 skills).
   - Thiết kế bảng mới `harness_experience` trên DynamoDB với Global Secondary Index `domain` để bảo đảm tốc độ truy vấn $O(1)$ theo phân vùng, nghiêm cấm dùng `ScanAll` gây nghẽn database.
4. **Cơ Chế Graceful Fallback An Toàn Khi Mất Mạng**:
   - Nếu mạng Tailscale tạm thời nghẽn hoặc endpoint Kev không phản hồi, bridge `tools/harness_rust.py` phải tự động chuyển sang chế độ heuristic an toàn (gán nhãn Yellow/Red) mà không làm crash agent session.
5. **Xác Thực Mã Băm Binary SHA-256 (Checksum Verification Gate)**:
   - Khi tải binary `harness-cli-linux-x64` từ GitHub Release, bắt buộc phải có bước kiểm tra hash SHA-256 đối chiếu với file `.sha256` chính thức trước khi cấp quyền `chmod +x`.

---

### 3.8. Khối 8: Bộ Quy Tắc Tự Học Bắt Buộc Theo Từng Vai Trò & Công Cụ Thẩm Định Tri Thức (Anti-Trivial Quality Guard)

Để đảm bảo các bài học tự học được áp dụng thực chất, không hình thức và **tuyệt đối không nạp các bài học "tào lao", vô nghĩa hoặc ảo giác** vào kho tri thức, hệ thống ban hành quy chuẩn bắt buộc theo từng vai trò cùng công cụ kiểm soát định kỳ:

#### A. Bộ Quy Tắc Tự Học Bắt Buộc Cho Từng Agent (Mandatory Agent Learning Rules)
1. **Peer Devs (1, 2, 3, 4)**:
   - **Quy tắc Trước Khi Code**: Bắt buộc phải đọc khối `## BẪY LỖI CŨ CẦN TRÁNH` trong spec task giao và tự tra cứu `python3 tools/harness_learning_search.py search --domain <domain>`.
   - **Cam kết Không Tái Phạm**: Nếu tái phạm lỗi cũ đã có bài học trong DB (như `any/unknown`, fallback `||`, thiếu DTO, bypass store), Peer chịu hình thức phạt kỷ luật lập tức.
   - **Khi Nộp Code**: Bắt buộc giải trình trong handoff memo bài học nào đã được áp dụng để bảo đảm code sạch.
2. **QC Verifier**:
   - **Đối Soát Độc Lập**: Trong quy trình 5-Stage ISTQB, QC bắt buộc đối chiếu diff của Peer với cơ sở dữ liệu `harness learn`. Tái phạm = REJECT lập tức không cần bàn cãi.
   - **Quy Chuẩn Khi Ghi Bài Học**: Khi đóng Bug, QC ghi bài học qua `harness-cli learn record` hoặc `tools/harness_learning_search.py` với tiêu chuẩn: độ dài `lesson` $\ge 20$ ký tự, `cue` $\ge 6$ ký tự, `evidence` $\ge 10$ ký tự, phải có quy tắc hành động rõ ràng (`cấm`, `phải`, `tránh`, `never`, `must`). Tuyệt đối cấm ghi tắt ngắn ngủn hoặc vô nghĩa.
3. **Lead Dev**:
   - **Rào Chắn Khi Giao Task**: Khi phân rã Zero-Search Task, Lead bắt buộc tra cứu bài học cũ và nhúng trực tiếp danh mục bẫy lỗi cần tránh vào spec bàn giao.
   - **Kiểm Duyệt Trước Khi Duyệt**: Kiểm tra code của Peer qua 8-Point Gate xem đã khắc phục triệt để các bài học cũ chưa.
4. **PM Agent**:
   - **Thẩm Định & Lọc Rác**: PM Agent định kỳ chạy công cụ kiểm soát `tools/harness_learning_search.py audit` để quét sạch toàn bộ kho tri thức, chấm điểm từng bài học và tự động thanh trừng (`--prune`) những bài học có điểm chất lượng thấp ($< 0.40$).
5. **Supervisor Agent**:
   - **Giám Sát Định Kỳ Qua Heartbeat**: Supervisor theo dõi chỉ số sức khỏe tri thức hiển thị tự động trên bảng Heartbeat Monitor (`python3 tools/agent_heartbeat.py status`). Nếu phát hiện tỉ lệ sức khỏe giảm hoặc có bài học nghi vấn, Supervisor lập tức chỉ đạo PM và Lead xử lý.

#### B. Công Cụ Tra Cứu & Thẩm Định Tri Thức (`tools/harness_learning_search.py`)
Hệ thống trang bị công cụ dòng lệnh chuyên dụng:
```bash
# 1. Tra cứu bài học kinh nghiệm đa chiều (hỗ trợ PM, Lead, Peer)
python3 tools/harness_learning_search.py search "strict_typing" --domain angular_fe
python3 tools/harness_learning_search.py search --confidence high --limit 10

# 2. Thẩm định chất lượng kho tri thức (PM & Supervisor Audit)
python3 tools/harness_learning_search.py audit

# 3. Tự động thanh trừng bài học rác / tào lao không đạt chuẩn
python3 tools/harness_learning_search.py audit --prune --threshold 0.60
```
- **Thuật toán Chấm Điểm Chất Lượng Bài Học (0.0 - 1.0)**:
  - Trừ điểm nếu `cue` $<6$ ký tự (-0.25), `lesson` $<20$ ký tự (-0.35), `evidence` $<10$ ký tự (-0.20).
  - Trừ nặng (-0.50) nếu chứa các từ ngữ rác/tào lao: `test`, `demo`, `abc`, `tào lao`, `vớ vẩn`, `asdf`, `chưa nghĩ ra`, `lorem ipsum`.
  - Trừ điểm (-0.20) nếu thiếu từ khóa hành động mang tính rào chắn (`cấm`, `phải`, `never`, `must`, `avoid`, `always`).

#### C. Tích Hợp Giám Sát Sức Khỏe Tri Thức Vào Heartbeat Định Kỳ
- Khi chạy `python3 tools/agent_heartbeat.py status`, hệ thống tự động quét và in dòng trạng thái tri thức thời gian thực:
  ```text
  📚 TRI THỨC TỰ HỌC: 2 bài học | 🟢 Sức khỏe: 100.0% | Nghi vấn tào lao: 0
  ```
- Nếu xuất hiện bài học rác, trạng thái tự động chuyển sang `🟡 Cảnh báo` để Quản lý can thiệp kịp thời.

---

### 3.9. Khối 9: Security Sentinel Agent - Giám Sát Liên Tục Chống Lộ Dữ Liệu Dự Án Dev & Chuẩn Bị Mở Public (Open-Source Readiness)

User định hướng sẽ **mở mã nguồn công khai (Open-Source / Public Repository)** cho `Room_Agent`. Do đó, hệ thống bắt buộc phải thiết lập chốt chặn an ninh tối thượng nhằm ngăn ngừa tuyệt đối mọi rủi ro lộ bí mật kinh doanh và nghiệp vụ:

#### A. Các Vùng Dữ Liệu Cấm Tuyệt Đối (Zero-Leak Boundary)
1. **API Specs Tính Năng Của Dự Án Đang Dev**:
   - Nghiêm cấm đưa vào commit/push bất kỳ file spec nào chứa API endpoints nội bộ của các dự án con đang phát triển (`projects/wicx-crm-fe`, WiOnPOS customer API, multi-tenant shop APIs, CRM gateway endpoints).
2. **Nghiệp Vụ & Luồng Frontend (Frontend Business Flows)**:
   - Nghiêm cấm lộ các tài liệu mô tả chi tiết logic thanh toán khách hàng, sơ đồ luồng dữ liệu nghiệp vụ (Customer 360 flows, thẻ thành viên, chương trình khuyến mãi riêng tư của khách hàng).
3. **Danh Tính Doanh Nghiệp & Địa Chỉ Thực Tế**:
   - Zero địa chỉ thực tế (tên đường, quận huyện, lô khu công nghiệp), zero mã số thuế, email nhân sự, domain nội bộ (`*.dev.example.com`, `tfs.*`).
4. **Mã Nguồn Các Dự Án Con (Sub-Projects Isolation)**:
   - Thư mục `projects/` (`wicx-crm-fe`, `Aevum`, `harness2`, `harness`) là các repo độc lập, BẮT BUỘC duy trì trong `.gitignore`, cấm `git add` vào `Room_Agent`.

#### B. Cơ Chế Hoạt Động Của Security Sentinel Agent (`profiles/security_sentinel.md`)
- **Vai trò**: Cảnh vệ an ninh độc lập có quyền **VETO tuyệt đối** (chặn đứng mọi hành vi commit/push).
- **Công cụ quét tự động liên tục**: `scripts/anti_leak_sentinel.py`
  - Tự động kiểm tra trước mọi commit và hook vào CI/CD:
    1. Quét git index: Báo động nếu phát hiện bất kỳ file nào trong `projects/` bị track.
    2. Quét nội dung: Tìm kiếm regex các pattern API riêng tư, domain nội bộ, địa chỉ thực tế, private keys.
    3. Tự động unstage (`git restore --staged`) và kích hoạt vi phạm `tools/agent_reprimand.py --violation security_leak`.

---

### 3.10. Khối 10: Quy Chuẩn Tập Trung Thư Mục Skills Duy Nhất (Single Canonical Skills Directory)

Khắc phục triệt để tình trạng các công cụ tự động copy/rải rác thư mục skills sang nhiều nơi gây hỗn loạn:

#### A. Nguyên Tắc Cấu Trúc Duy Nhất (Single Source of Truth)
- **Vị trí chuẩn duy nhất**: Toàn bộ kỹ năng bắt buộc phải nằm tại thư mục gốc:
  ```text
  /home/baoltb/Desktop/Room_Agent/skills/<tên-kỹ-năng>/SKILL.md
  ```
- **Quy chuẩn Định dạng**:
  - Mỗi kỹ năng BẮT BUỘC là **một thư mục riêng** chứa file `SKILL.md` (kèm các thư mục con `references/`, `scripts/` nếu có).
  - **Nghiêm cấm tạo file đơn lẻ dạng `<tên>.skill` hay file markdown mồ côi nằm trực tiếp tại thư mục `skills/`**.

#### B. Biện Pháp Ngăn Chặn Phân Mảnh Rải Rác
1. **Xóa sạch toàn bộ thư mục `.claude/skills` mồ côi**:
   - Đã dọn dẹp và xóa bỏ các thư mục rác từng bị phát sinh trong `bmad/rooms/*/.claude/` và `.claude/skills/`.
2. **Khóa Chặn Trên Git**:
   - Thêm `.claude/` và `*/.claude/` vào `.gitignore` để đảm bảo không bao giờ bị track vào Git repository.
3. **Cải tiến `tools/skill_manager.py`**:
   - Vô hiệu hóa tính năng tự động sao chép skills sang các thư mục con `bmad/rooms/*/`. Toàn bộ hệ thống chỉ tham chiếu tập trung về Master Registry tại `skills/`.
4. **Cơ chế nạp cho Hermes**:
   - Chỉ tạo duy nhất một symlink từ `skills/<tên>` sang `~/.hermes/skills/<tên>` để phục vụ `skill_view`, không nhân bản file.

---

### 3.11. Khối 11: Mô Hình Điều Hành SLPPC & Watchdog Tự Động Lập Biên Bản Vi Phạm (Flow Guard & Reprimand Ledger)

Nâng cấp chính thức mô hình điều hành từ **SLPC** lên **SLPPC** (Supervisor - Lead - PM - Peer - QC):

```text
               ┌──────────────────────────────────────────────┐
               │              USER (PRODUCT OWNER)            │
               └──────────────────────┬───────────────────────┘
                                      │ Yêu cầu nghiệp vụ
                                      ▼
               ┌──────────────────────────────────────────────┐
               │             SUPERVISOR (S)                   │
               │   • Scope & Intent Guard                     │
               │   • Cấm trực tiếp viết code tính năng        │
               └──────────────────────┬───────────────────────┘
                                      │ Chuyển bối cảnh
                                      ▼
               ┌──────────────────────────────────────────────┐
               │               PM AGENT (P)                   │
               │   • Feasibility Score (0..3) & Alignment     │
               │   • Đánh giá rủi ro sub-50ms qua Kev System 1│
               └──────────────────────┬───────────────────────┘
                                      │ Bàn giao spec đã duyệt
                                      ▼
               ┌──────────────────────────────────────────────┐
               │               LEAD DEV (L)                   │
               │   • Technical Architect & PM Phân Rã         │
               │   • CẤM TỰ Ý CODE (Role Trespass)            │
               │   • Bắt buộc bóc tách Zero-Search cho Peer   │
               └──────────────────────┬───────────────────────┘
                                      │ Giao task định lượng (5 mục)
                                      ▼
               ┌──────────────────────────────────────────────┐
               │             PEER DEVS (P1 - P4)              │
               │   • Code Executors (4 bậc tiết kiệm token)   │
               │   • Bắt buộc kiểm tra bẫy lỗi cũ             │
               │   • CẤM TỰ TIỆN ĐÓNG TASK (Premature Close)  │
               └──────────────────────┬───────────────────────┘
                                      │ Nộp code (Resolved)
                                      ▼
               ┌──────────────────────────────────────────────┐
               │               QC VERIFIER (C)                │
               │   • Independent Quality Gate (5-Stage ISTQB) │
               │   • Độc quyền quyền hạn đóng task (Closed)   │
               └──────────────────────────────────────────────┘
```

#### A. Thư Mục Lưu Trữ Biên Bản Vi Phạm Chính Thức (`bmad/rooms/violations/`)
- Mọi biên bản xử phạt kỷ luật được lưu trữ tập trung và bất biến tại:
  ```text
  /home/baoltb/Desktop/Room_Agent/bmad/rooms/violations/
  ```
- Định dạng biên bản: `violation_<task_id>_<from_role>_to_<to_role>_<YYYYMMDD_HHMMSS>.md` ghi rõ: Mã biên bản, đối tượng vi phạm, bằng chứng thực nghiệm (diff, log), nguyên tắc bị phá vỡ và chế tài xử phạt.

#### B. Cơ Chế Watchdog Giám Sát Tự Động (`tools/slppc_flow_guard.py`)
Tự động kích hoạt qua Heartbeat hoặc Cron định kỳ nhằm ngăn chặn tình trạng sai lệch quy trình:
1. **Chặn Lead ôm code (`role_trespass`)**:
   - Khi Lead Dev tự ý gõ code sửa mã nguồn sản phẩm (`projects/wicx-crm-fe`, `crates/harness-cli/src`) thay vì phân rã giao cho Peer:
   - Hệ thống lập tức tự động lập biên bản kỷ luật trong `bmad/rooms/violations/` và gửi cảnh báo tới Supervisor.
2. **Chặn bỏ qua cổng PM (`pm_bypass`)**:
   - Phát hiện task được kích hoạt mà chưa qua đánh giá Feasibility / Alignment của PM Agent.
3. **Chặn Dev tự đóng task (`premature_close`)**:
   - Bắt buộc task chỉ được đóng (`Closed`) sau khi có chữ ký nghiệm thu độc lập của QC.
4. **Chặn giao việc cẩu thả (`vague_specs`)**:
   - Quét các task mới: nếu thiếu 5 thành phần Zero-Search bắt buộc, lập tức giáng về `Active` và phạt Lead Dev.

---

### 3.12. Khối 12: Pipeline CI/CD GitHub Actions Kiểm Soát Tuân Thủ (`.github/workflows/slppc-governance-guard.yml`)

Để bảo đảm an toàn tuyệt đối khi public repository, GitHub Actions được thiết lập tự động kiểm tra trên mọi Pull Request và Push:
1. **Job `governance-and-security-audit`**:
   - **Bước 1: Open-Source Anti-Leak Sentinel**: Chạy `python3 scripts/anti_leak_sentinel.py` kiểm tra zero API contracts nội bộ, zero business flows, zero địa chỉ công ty và zero file rò rỉ từ `projects/`.
   - **Bước 2: SLPPC Flow & Role Trespass Guard**: Chạy `python3 tools/slppc_flow_guard.py` bảo đảm không có vi phạm rào cản thẩm quyền điều hành.
   - **Bước 3: Learning Quality Audit**: Chạy `python3 tools/harness_learning_search.py audit --threshold 0.60` bảo đảm không có bài học tào lao lọt vào kho tri thức.

---

## 4. Kế Hoạch Triển Khai Từng Bước (Migration Roadmap)

Quá trình chuyển đổi diễn ra qua 4 giai đoạn độc lập, kiểm định chặt chẽ trước khi merge vào nhánh chính:

```text
Giai đoạn 1: Decommission UI & Binary  Giai đoạn 2: Cloud DB & Bridge     Giai đoạn 3: Tích Hợp Cổng SLPC      Giai đoạn 4: E2E Quality Gate
┌─────────────────────────────────┐  ┌───────────────────────────────┐  ┌─────────────────────────────────┐  ┌────────────────────────────┐
│ • Xóa triệt để harness-ui/      │  │ • Tạo bảng harness_experience │  │ • Cập nhật profiles/supervisor  │  │ • Chạy 44 unit tests Rust  │
│ • Xóa docker-harness-ui.yml     │  │   trên Floci DynamoDB         │  │ • Cập nhật profiles/lead & qc   │  │ • Chạy 73 e2e tests Python │
│ • Sửa Jenkinsfile & doctor.py   │─►│ • Viết tools/harness_rust.py  │─►│ • Gắn hook learn & supervise    │─►│ • Nghiệm thu QC độc lập    │
│ • Tải harness-cli-v0.1.14       │  │ • Mở rộng harness_manager.py  │  │ • Thẩm định zero-leak Git       │  │ • Đóng Epic nâng cấp       │
│ • Kiểm tra SHA256 checksum      │  │ • Test gọi Kev live sub-50ms  │  │                                 │  │                            │
└─────────────────────────────────┘  └───────────────────────────────┘  └─────────────────────────────────┘  └────────────────────────────┘
```

### Bước 1: Loại Bỏ `harness-ui` & Chuẩn Bị Binary (Phase 1)
1. **Dọn sạch `harness-ui`**:
   - Chạy `git rm -r harness-ui` xóa toàn bộ mã nguồn Astro, Dockerfile, Nginx config.
   - Chạy `git rm .github/workflows/docker-harness-ui.yml` gỡ workflow CI thừa.
   - Sửa `Jenkinsfile` gỡ các stage deploy UI.
   - Sửa `tools/harness_doctor.py` gỡ bỏ bước kiểm tra frontend bundle `harness-ui/dist`.
   - Cập nhật `bmad/architecture.json` gỡ bỏ node `harness-ui`.
2. **Nạp Binary Native v0.1.14**:
   - Viết script `scripts/setup_harness_v0114.py` tự động tải binary `harness-cli-linux-x64` từ GitHub Releases (hoặc copy từ `projects/harness/target/release/harness-cli`).
   - Cấp quyền `chmod +x scripts/bin/harness-cli` và kiểm tra `harness-cli --version` xác nhận `0.1.14`.

### Bước 2: Tạo Bảng Học Tập DynamoDB & Xây Dựng Cầu Nối Bridge (Phase 2)
1. **Tạo Bảng `harness_experience` Trên Floci DynamoDB**:
   - Cập nhật `tools/floci_client.py` bổ sung phương thức `init_experience_table()`:
     - PK: `id` (String)
     - GSI: `domain` (String) + `created_at` (String)
   - Viết các hàm: `put_experience(exp)`, `query_experiences(domain, limit)`.
2. **Xây dựng Lớp Giao Tiếp `tools/harness_rust.py`**:
   - Wrapper gọi binary Rust `harness-cli`, cung cấp:
     - `supervise_task(text: str) -> dict`: Gọi Kev System One (<50ms).
     - `record_lesson(domain: str, cue: str, lesson: str, evidence: str) -> int`: Ghi đồng thời vào SQLite và DynamoDB.
     - `query_lessons(domain: str) -> list`: Truy vấn bài học kết hợp local/cloud.
   - Nâng cấp `tools/harness_manager.py` tích hợp tự động cờ `--engine auto`.

### Bước 3: Cập Nhật Quy Trình & Prompt Profiles (Phase 3)
- Bổ sung quy định vào `AGENTS.md` (Mục 3.A và Mục 2).
- Cập nhật hồ sơ vai trò:
  - `profiles/supervisor.md`: Tự động gọi Kev System One phân luồng Fast-Path Lambda / Worker trước khi dispatch.
  - `profiles/lead.md`: Bắt buộc tra cứu `harness learn` trước khi giao task để đính kèm bài học kinh nghiệm vào spec.
  - `profiles/qc.md`: Bắt buộc ghi nhận `harness learn record` khi đóng bug.

### Bước 4: Kiểm Thử Toàn Diện & Nghiệm Thu Độc Lập (Phase 4)
- Chạy kiểm thử đối chiếu: đảm bảo mọi lệnh CRUD work item trên DynamoDB và SQLite đều đồng nhất.
- Đánh giá độ trễ: khẳng định thời gian phản hồi phân luồng task của Kev đạt $<50\text{ms}$.
- Chạy toàn bộ test suites của `Room_Agent` và đóng task nâng cấp.

---

## 5. Tiêu Chuẩn Nghiệm Thu Định Lượng (Acceptance Criteria)

1. **AC-1 (Binary Integrity)**: Binary `scripts/bin/harness-cli` thực thi thành công trên môi trường Linux Ubuntu x64, trả về version `0.1.14`.
2. **AC-2 (Sub-50ms Supervision)**: Lệnh `supervise evaluate` qua Tailscale tới `http://100.124.36.46:8008/v1/systemone` trả về kết quả traffic-light hợp lệ với model `kev-latest`.
3. **AC-3 (Closed-Loop Learning)**: Bản ghi bài học được lưu thành công vào SQLite `harness_experience` và đồng bộ lên Floci DynamoDB `harness_experience`, truy vấn $O(1)$ qua domain.
4. **AC-4 (Complete Decommissioning of `harness-ui`)**: Thư mục `harness-ui/`, workflow `.github/workflows/docker-harness-ui.yml` được xóa bỏ sạch sẽ 100%, Jenkinsfile và `harness_doctor.py` không còn code thừa.
5. **AC-5 (Zero Regression)**: Toàn bộ hệ thống quản trị hiện tại (Floci DynamoDB, 8 agent terminals trên Orca, Aevum Kanban) hoạt động ổn định, không bị đứt gãy kết nối.
6. **AC-6 (Zero Git Leak)**: Thư mục `projects/` và các database runtime tiếp tục được bảo vệ tuyệt đối trong `.gitignore`, không rò rỉ mã nguồn hay bí mật hệ thống.
7. **AC-7 (Anti-Trivial Learning Quality Gate)**: Công cụ `tools/harness_learning_search.py` thẩm định chất lượng bài học đạt $\ge 90\%$ sức khỏe tri thức, tự động lọc sạch các bài học tào lao (< 0.40 điểm) và hiển thị trực quan cảnh báo trên bảng Heartbeat Monitor.
8. **AC-8 (Open-Source Leak-Free Gate)**: Chạy `python3 scripts/anti_leak_sentinel.py` đạt PASS 100%, bảo đảm 0 rò rỉ API endpoints riêng tư, 0 luồng nghiệp vụ FE, 0 địa chỉ công ty trước khi mở public repo.
9. **AC-9 (Single Canonical Skills Integrity)**: Toàn bộ 85 skills nằm tập trung duy nhất tại `skills/<name>/SKILL.md`, triệt tiêu 100% các bản copy rải rác trong `.claude/` và `bmad/rooms/`.
10. **AC-10 (SLPPC Flow Guard & Violations Ledger)**: Tự động phát hiện vi phạm rào cản thẩm quyền điều hành (Lead ôm code, bypass PM, dev tự đóng việc) và lập biên bản chuẩn hóa tại `bmad/rooms/violations/`.
11. **AC-11 (GitHub Actions Governance CI)**: Workflow `.github/workflows/slppc-governance-guard.yml` thực thi xanh 100% trên PR, tự động chặn mọi vi phạm bảo mật và sai lệch quy trình trước khi merge.

---

## 6. Trạng Thái Hiện Tại & Đề Xuất Phê Duyệt

- **Nhánh Git hiện tại**: `feat/upgrade-harness-cli-v0.1.14` (đã tách nhánh sạch từ `main`).
- **Tài liệu đặc tả**: Lưu trữ tại `docs/spec/harness-cli-v0.1.14-upgrade-spec.md`.
- **Hành động tiếp theo**: Kính mời User xem xét, phản biện hoặc duyệt thông qua bản đặc tả trên. Ngay khi User phê duyệt, Supervisor sẽ lập tức điều phối Lead Dev và các Peers bắt đầu thi công từng giai đoạn.
