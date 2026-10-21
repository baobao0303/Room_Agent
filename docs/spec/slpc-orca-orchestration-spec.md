# ĐẶC TẢ KIẾN TRÚC ĐIỀU PHỐI ĐA TÁC NHÂN SLPC TRÊN NỀN TẢNG ORCA ORCHESTRATION
## (SLPC Multi-Agent Orchestration Architecture on Orca Runtime Engine)

> **Mã tài liệu**: `docs/spec/slpc-orca-orchestration-spec.md`  
> **Phiên bản**: 1.0.0 | **Ngày ban hành**: 2026-10-21  
> **Hệ thống áp dụng**: Orca IDE Runtime, Paseo Daemon, Harness State Engine (Floci DynamoDB) & BMAD Rooms  
> **Tác giả / Phê duyệt**: Lead Architect & SLPC System Team  

---

## 1. TỔNG QUAN & BỐI CẢNH (OVERVIEW & OBJECTIVES)

### 1.1 Mục tiêu
Hiện thực hóa mô hình phân quyền và luồng làm việc 4 tầng **SLPC** (`Supervisor - Lead - Peer - QC`) trên nền tảng **Orca Orchestration Engine** (`orca orchestration`), biến Orca từ một IDE đơn thuần thành môi trường điều phối đa tác nhân (Multi-Agent Runtime) trực quan, có kiểm soát và chống tràn Context Window.

### 1.2 Đánh giá mức độ đáp ứng của Orca với flow hiện tại
- **Mức độ tương thích**: **78% Native** + **22% Hybrid Bridge**.
- **Ưu thế vượt trội của Orca**:
  - Hỗ trợ native đa tác nhân chạy song song trên cùng một workspace/worktree (`orca orchestration worker-start` hỗ trợ Claude, Codex, Hermes, Antigravity...).
  - Hệ thống Event Bus liên agent (`send`, `reply`, `ask`, `inbox`) hỗ trợ phân loại tin nhắn (`handoff`, `question`, `worker_done`, `decision_gate`).
  - Giao diện trực quan (GUI sidebar): Xem trực tiếp danh sách agent, trạng thái (working/done), live terminal và diff thay đổi theo thời gian thực.
  - Cơ chế **Decision Gates** (`gate-create`, `gate-resolve`) tương thích hoàn hảo với vai trò Cổng kiểm thử độc lập của **QC**.
- **Điểm cần bù đắp bằng công cụ nội bộ (Hybrid Bridge)**:
  - Orca lưu trữ tiến trình cục bộ trong SQLite (`orchestration.db`); hệ thống dự án cần đồng bộ song song với **Harness DB** (Floci DynamoDB) để phục vụ dashboard Web và Jenkins CI.
  - Orca không có tri thức nghiệp vụ sâu về hệ thống Design System (TDS UI tokens, Angular 18 MFE) và bộ sinh kiểm thử tự động 5-Stage ISTQB (`qc_test_generator.py`).

---

## 2. ÁNH XẠ VAI TRÒ SLPC SANG ORCA PRIMITIVES (ROLE MAPPING MATRIX)

| Vai trò SLPC | Thực thể Orca tương ứng | Agent Runtime đề xuất | Quyền hạn & Nhiệm vụ cốt lõi |
| :--- | :--- | :--- | :--- |
| **Human / User** | **User / Primary Controller** | Người dùng | Đưa yêu cầu nghiệp vụ, nắm quyền phủ quyết tối cao (Veto), giải quyết các câu hỏi leo thang (Escalation). |
| **Supervisor** | **Run Coordinator / Root Owner** | `hermes` (Profile: `supervisor`) | - Tạo và sở hữu Orchestration Run (`run-create`).<br>- Là đầu mối giao tiếp duy nhất với User (SPOC).<br>- Giám sát tiến độ, kiểm soát scope, điều phối Lead. |
| **Lead** | **Supervised Dispatcher / PM** | `hermes` (Profile: `lead`) | - Phân rã mục tiêu thành các Task cụ thể (`task-create`).<br>- Thiết lập Decision Gates chặn nghiệm thu (`gate-create`).<br>- Dispatch công việc cho Peer Dev (`dispatch`).<br>- Trả lời các chất vấn kiến trúc từ Peer (`reply`). |
| **Peer Dev** | **Code Executor** | `hermes` (Profile: `peer`) | - Lập trình tính năng Angular 18 (Standalone, OnPush).<br>- Nhận design spec từ Peer Design để lắp ráp giao diện.<br>- Tự chạy unit test nội bộ.<br>- Báo cáo nộp code diff cho Lead Dev (`report-done`). |
| **Peer Design** | **UI/UX & Design Token Specialist** | `hermes` (Profile: `peer_design`) | - Bóc tách Figma Node, mockups giao diện.<br>- Ánh xạ sang component TDS UI và token `tds-color-*`.<br>- Xuất `bmad/rooms/tasks/<id>/design_spec.md`.<br>- Bàn giao spec cho Peer Dev (`report-design-done`). |
| **QC** | **Gatekeeper / Test Architect** | `hermes` (Profile: `qc`) | - Độc lập nghiệm thu sản phẩm của Peer.<br>- Sinh test suite 5-Stage ISTQB (`qc_test_generator.py`).<br>- Chỉ khi 100% tests PASS mới thực hiện mở cổng (`gate-resolve`) và đóng Task. |

### 2.1 Ma Trận 3 Sub-Agents Chuyên Trách Review Chéo (Cross-Agent Audit Matrix)
Để không làm ô nhiễm context của các Agent chính (Lead/Peer/QC), 3 Sub-Agent chuyên trách được thiết kế hoạt động song song để review mọi thay đổi mã nguồn trước khi nghiệm thu:

```text
                           [Code Diff / Commit của Peer]
                                         │
             ┌───────────────────────────┼───────────────────────────┐
             ▼                           ▼                           ▼
   [gemini-codebase-analyzer]  [strategic-architect]       [slpc-qc-verifier]
   - Quét diện rộng 1M token   - Rà soát Lazy Senior Dev   - 100% Test suite PASS
   - Blast Radius & Imports    - Single-Ownership          - 17 Web UI Standards
   - Bắt Dead Code sau refactor- Không hardcode màu hex    - Edge cases & null data
```

| Sub-Agent | Model / CLI Nền tảng | Nhiệm vụ Review Chéo Cốt Lõi | Tiêu chuẩn Đánh giá (Pass/Fail) |
| :--- | :--- | :--- | :--- |
| **`gemini-codebase-analyzer`** | Gemini 1M+ Context (`gemini --all-files`) | - **Phạm vi ảnh hưởng (Blast Radius)**: Kiểm tra thay đổi có làm vỡ component cha/con hoặc MFE khác không.<br>- **Phát hiện Dead Code**: Tìm sạch các import rác, `@ViewChild` mồ côi, module cũ không còn sử dụng sau khi refactor. | **FAIL** nếu còn sót import không dùng hoặc vỡ interface liên module. |
| **`strategic-reasoning-architect`** | GPT-5 / Codex (`codex -m "gpt-5"`) | - **Tuân thủ Kiến trúc**: Đảm bảo tuân thủ nguyên tắc Lazy Senior Dev (xóa trước thêm sau, YAGNI, không sinh boilerplate).<br>- **Single-Ownership**: Đảm bảo 100% file sửa nằm trong module được phân quyền.<br>- **TDS Token Compliance**: 0% mã màu hex cứng (`#...`), 100% dùng token TDS UI, giữ `ChangeDetectionStrategy.OnPush`. | **FAIL** nếu phát hiện mã màu hex cứng hoặc vi phạm ranh giới sở hữu file. |
| **`slpc-qc-verifier`** | Test Engine (`qc_test_generator.py`) | - **Thực thi Kiểm thử Thực nghiệm**: Chạy Jest runner (`npx jest`), tỷ lệ pass đạt 100%.<br>- **Bao phủ 17 Web UI Categories**: Kiểm tra toàn diện checkbox select-all, sort, filter, empty states, pagination, drawer...<br>- **Kiểm tra ca biên (Boundary/Edge)**: Dữ liệu rỗng, null, undefined, số lượng item lớn. | **FAIL** nếu có bất kỳ test suite nào thất bại hoặc thiếu test cho ca biên. |

### 2.2 Rào Cản Thẩm Quyền Bất Khả Xâm Phạm: Quản Lý & Phát Triển (Strict Role Fencing)
Để loại trừ triệt để tình trạng chéo chân, lấn sân hoặc đùn đẩy trách nhiệm, hệ thống áp đặt **Rào cản thẩm quyền cứng (Hard Role Fence)** được kiểm tra và chặn tự động bằng code:

```text
 ┌───────────────────────────────────────────────┐
 │ KHỐI QUẢN LÝ (Supervisor & Lead)              │
 │ • Supervisor: Quản lý Intent & Scope          │
 │ • Lead: Quản lý Kiến trúc & Phân rã           │
 │ ⛔ CẤM TUYỆT ĐỐI: Không được sửa code feature │
 └───────────────────────┬───────────────────────┘
                         │ Giao việc 3 phần
                         ▼
 ┌───────────────────────────────────────────────┐
 │ KHỐI PHÁT TRIỂN / DEV (Peer)                  │
 │ • Lập trình tính năng (Angular 18 / TDS UI)   │
 │ • Tự chạy Unit Test nội bộ                    │
 │ ⛔ CẤM TUYỆT ĐỐI: Không được đóng Task Closed │
 │ ⛔ CẤM TUYỆT ĐỐI: Không được tự ý tạo Epic    │
 └───────────────────────┬───────────────────────┘
                         │ Nộp code diff (Resolved)
                         ▼
 ┌───────────────────────────────────────────────┐
 │ KHỐI KIỂM ĐỊNH ĐỘC LẬP (QC)                   │
 │ • Sinh test ISTQB 5-Stage & chạy runner       │
 │ • Mở Decision Gate và chuyển Task sang Closed │
 │ ⛔ CẤM TUYỆT ĐỐI: Không sửa code hộ Dev       │
 └───────────────────────────────────────────────┘
```

#### Ma Trận Rào Cản & Cơ Chế Chặn Tự Động (Enforcement Matrix):

| Nhóm Vai Trò | Quyền Hạn Cho Phép (Allowed) | Rào Cản Cấm Thực Hiện (Strictly Forbidden) | Cơ Chế Chặn Bằng Code / Tool |
| :--- | :--- | :--- | :--- |
| **Supervisor** *(Quản lý Scope)* | Giao tiếp với User, tạo Epic trên Harness, theo dõi Board, điều phối Lead. | **CẤM sửa code production**, cấm can thiệp chi tiết kỹ thuật. | Bị phạt `role_trespass` nếu sửa file trong `projects/`. |
| **Lead** *(Quản lý Kỹ thuật)* | Bóc tách Task, thiết kế kiến trúc, lập Gate, review diff, giải quyết phản biện. | **CẤM viết code production**, cấm làm thay việc của Dev. | Bị phạt `role_trespass` nếu commit vào source code component. |
| **Peer** *(Phát triển / Dev)* | Viết mã nguồn tính năng, viết style SCSS, tự chạy test, phản biện Lead (`ask`). | **CẤM đóng Task sang `Closed`**, cấm tạo Epic, cấm sửa ngoài scope được giao. | `tools/harness_manager.py` tự động ném ngoại lệ `PermissionError` chặn đứng lệnh đóng task. |
| **QC** *(Kiểm định Độc lập)* | Sinh testcase, chạy automated test, mở Decision Gate, đóng Task `Closed`. | **CẤM sửa code tính năng cho Dev** (No silent patching). | Nếu test fail, bắt buộc giáng task về `Active` trả cho Peer. |

### 2.3 Luồng Phối Hợp Kép Giữa Peer Design Và Peer Dev (Dual-Peer Execution Pipeline)
Đối với các tính năng có giao diện (UI) hoặc yêu cầu thiết kế Figma, hệ thống kích hoạt luồng phối hợp chuyên môn hóa cao giữa 2 Peer:

```text
[Yêu cầu giao diện / Figma từ User]
                 │
                 ▼
          [1. Supervisor] ──► Tạo Epic trên Harness DB
                 │
                 ▼
            [2. Lead Dev] ──► Bóc tách Task & lập QC Decision Gate
                 │
                 ▼ (python3 tools/orca_slpc_bridge.py dispatch-design --figma-node <id>)
         [3a. Peer Design] ──► Chuyên trách UI/UX & Design Tokens
         - Tra cứu Figma Node geometries, typography, spacing
         - Tra cứu component TDS tương ứng (`tools/tds_search.py`)
         - Xuất bản tài liệu: `bmad/rooms/tasks/<id>/design_spec.md`
                 │
                 ▼ (python3 tools/orca_slpc_bridge.py report-design-done)
          [3b. Peer Dev]   ──► Chuyên trách Code & Logic
         - Đọc `design_spec.md` của Peer Design để lắp ráp HTML/SCSS
         - Đảm bảo 100% OnPush và không cần tự mò mẫm style
         - Tự chạy Jest test runner nội bộ
                 │
                 ▼ (python3 tools/orca_slpc_bridge.py report-done)
          [4. Lead Dev Review] ──► Thẩm định kiến trúc & đối soát token của Design
                 │
                 ▼ (APPROVED ➔ Báo cáo Supervisor)
          [5. QC Verifier]     ──► Nghiệm thu độc lập 17 Web Categories ➔ Closed!
```

---

## 3. GIAO THỨC TRUYỀN TIN LIÊN TÁC NHÂN (INTER-AGENT MESSAGE PROTOCOL)

Hệ thống sử dụng lệnh `orca orchestration send` làm trục truyền tin chính, kết hợp với metadata chuẩn hóa:

```text
[Supervisor] ──(dispatch / task-create)──▶ [Lead]
                                             │
                                     (dispatch / task)
                                             ▼
[Lead] ◀────(ask: Evidence Challenge)──── [Peer]
   │                                         │
(reply)                                      │ (worker_done + git diff)
   ▼                                         ▼
[Peer] ───────────────────────────────────▶ [QC] ──(gate-resolve)──▶ [Closed]
```

### 3.1 Bảng mã Message Type trong Orca
1. **`dispatch`**:
   - Dùng khi: Supervisor giao Epic cho Lead, hoặc Lead giao Subtask cho Peer/QC.
   - Tham số bắt buộc: `--task-id <id> --to <dispatch:id|agent>`
2. **`handoff`**:
   - Dùng khi: Chuyển giao ngữ cảnh kèm đường dẫn biên bản tại `bmad/rooms/<role>/latest_handoff.md`.
   - Payload: Đường dẫn file handoff, danh sách module bị ảnh hưởng.
3. **`ask` & `reply` (Blocking Evidence-backed Challenge)**:
   - Dùng khi: Peer phát hiện kiến trúc của Lead sai thực tế (build panic, token không tồn tại, xung đột thư viện).
   - Peer gọi: `orca orchestration ask --subject "Kien truc loi" --body "Kem log loi thuc te"`. Lệnh này **chặn (block)** tiến trình của Peer cho đến khi Lead trả lời qua `orca orchestration reply`.
4. **`worker_done`**:
   - Dùng khi: Peer hoàn tất code và tự test nội bộ; hoặc QC hoàn tất chạy bộ test ISTQB.
   - Tham số bắt buộc: `--outcome succeeded|failed --files-modified <csv> --task-id <id>`.
5. **`decision_gate`**:
   - Dùng khi: Lead dựng rào cản chất lượng (`gate-create --name "QC-Approval-WI-xxx"`). Task không thể hoàn tất nếu QC chưa giải phóng gate này qua `gate-resolve`.
6. **`escalation`**:
   - Dùng khi: Bế tắc kỹ thuật, phát sinh rủi ro xóa dữ liệu hoặc vượt ngoài budget/scope. Báo trực tiếp về Supervisor để hỏi ý kiến User.
7. **`heartbeat`**:
   - Dùng khi: Agent báo cáo nhịp tim định kỳ (trạng thái: `working`/`idle`/`blocked`, Task ID, hành động hiện tại).
   - Tool quản lý: `tools/agent_heartbeat.py ping|status|broadcast`.
   - Lưu trữ tập trung: `bmad/rooms/heartbeats.json`.
   - Giám sát sức khỏe: 🟢 ONLINE (< 3 phút), 🟡 WARNING (3-5 phút), 🔴 OFFLINE / TREO (> 5 phút).

### 3.2 Giao Thức Thảo Luận & Lập Biên Bản (Discussion Minutes & ADR Protocol)
Khi có sự bất đồng hoặc tương tác hai chiều (Peer ⟷ Lead hoặc thảo luận đa bên), **bắt buộc phải lập biên bản kết luận (Minutes)** thay vì để trôi mất trong log terminal:

1. **Vị trí lưu trữ**: `bmad/rooms/discussions/`
2. **Quy chuẩn đặt tên**: `minutes_<task_id>_<topic_slug>_<timestamp>.md`
3. **Cấu trúc biên bản thảo luận bắt buộc**:
   - **Vấn đề / Bất đồng (Conflict / Issue)**: Mô tả xung đột (VD: Peer chứng minh directive của Lead gây lỗi Rspack compile).
   - **Ý kiến & Bằng chứng các bên**:
     * *Phía Peer*: Log lỗi thực nghiệm, benchmark, test thất bại.
     * *Phía Lead*: Ràng buộc kiến trúc, ranh giới module, tiêu chuẩn TDS.
   - **Đồng thuận / Quyết định cuối (Consensus / Resolution)**: Phương án kỹ thuật được chốt.
   - **Hành động tiếp theo (Action Items)**: Danh sách file cần sửa, người chịu trách nhiệm, cập nhật task.
4. **Công cụ tự động hóa**:
   - Agent tham gia cuộc họp/thảo luận gọi script:
     ```bash
     python3 tools/record_discussion.py \
       --task-id <id> \
       --topic "Xu ly loi Rspack cache panic khi doi directive" \
       --parties "Peer Dev, Lead Dev" \
       --conflict "Lead yeu cau dung flex-order, Peer gap loi compile" \
       --consensus "Chuyen sang dung ng-template va CSS grid" \
       --actions "Peer sua raw-event-list.component.ts; Lead cap nhat spec"
     ```
   - Biên bản sau khi ghi nhận sẽ tự động gửi thông báo qua `orca orchestration send --type handoff --subject "Bien ban thao luan #<id>"`.

### 3.3 Giao Thức Khiển Trách & Xử Phạt Kỹ Thuật (Agent Reprimand & Sanction Protocol)
Để đảm bảo kỷ luật tuyệt đối và ngăn chặn việc agent làm ẩu, làm sai quy tắc của User, hệ thống cung cấp công cụ `tools/agent_reprimand.py` trao quyền cho các vai trò tương ứng **khiển trách ("chửi") chính thức** agent vi phạm:

```text
               [Ma Trận Quyền Khiển Trách & Phản Biện]
  ┌─────────────────────────────────────────────────────────────┐
  │ • Supervisor ──(scope_creep / premature_close)──► Lead / QC │
  │ • Lead       ──(hardcoded_hex / dead_code)    ──► Peer      │
  │ • Peer       ──(flawed_architecture)          ──► Lead      │
  │ • QC         ──(untested_code / 17 UI gaps)   ──► Peer      │
  │ • Sub-Agents ──(audit failure / dead code)    ──► Peer/Lead │
  └─────────────────────────────────────────────────────────────┘
```

#### 9 Nhóm Vi Phạm Chuẩn Hóa:
1. `hardcoded_hex`: Chứa mã màu hex cứng `#...` thay vì dùng TDS Design Tokens.
2. `broken_ownership`: Sửa chéo sang file/module khác ngoài phạm vi được giao.
3. `dead_code`: Để lại import rác, `@ViewChild` mồ côi hoặc biến thừa sau refactor.
4. `untested_code`: Nộp code lên `Resolved` mà chưa tự test hoặc test suite thất bại.
5. `flawed_architecture`: Thiết kế lý thuyết suông, gây build panic hoặc crash thực tế.
6. `vague_specs`: Giao đề bài mơ hồ, thiếu Acceptance Criteria (BDD) hoặc thiếu Anchor.
7. `scope_creep`: Tự ý làm thêm tính năng ngoài phạm vi Epic/Task được giao.
8. `premature_close`: Tự tiện đóng Task khi chưa có xác nhận nghiệm thu 100% từ QC.
9. `context_pollution`: Ghi đè file handoff hoặc nạp bừa context của task khác.

#### Cơ Chế Thực Thi & Chế Tài:
- Khi một Agent phát hiện vi phạm, gọi tool:
  ```bash
  python3 tools/agent_reprimand.py \
    --from-role Lead \
    --to-role Peer \
    --violation hardcoded_hex \
    --evidence "raw-event-list.component.scss: line 15 chứa color: #FF4E00" \
    --message "Nghiêm cấm dùng mã màu hex cứng! Phải dùng token tds-color-text-danger." \
    --task-id 1174 \
    --penalize
  ```
- **Hệ thống tự động kích hoạt 4 chế tài bắt buộc**:
  1. **Tự động tạo Ticket dạng `Bug` trên Harness DB**: Hệ thống lập tức sinh một Work Item loại `Bug` (`[Review]: Phat hien <violation> when reviewed by <Role>`), độ ưu tiên `P1`, gắn `--parent-id <task_id>` và gán đích danh cho `peer` giải quyết.
  2. **Ký thác biên bản xử phạt**: Xuất file `bmad/rooms/violations/reprimand_<task_id>_<from>_to_<to>_<timestamp>.md` và ghim vào `tasks/<task_id>/latest_violation.md`.
  3. **Giáng cấp trạng thái Harness DB**: Task bị giáng từ `Resolved` ngược về `Active` (Dev phải làm lại từ đầu) hoặc từ `Active` sang `Blocked`.
  4. **Bắn thông báo cảnh cáo qua Orca Event Bus**: Gửi thông điệp khẩn cấp (`type: escalation`) tới thẳng hộp thư `@<target>` trên Orca. Dev phải giải quyết xong Bug ticket mới được nộp lại nghiệm thu.

---

## 4. KIẾN TRÚC HYBRID BRIDGE & CHUẨN HÓA HARNESS ⟷ ORCA WORKSPACE BOARD

### 4.1 Bảng Chuẩn Hóa Thực Thể (Entity Standardization Matrix)
Để đồng bộ mượt mà giữa Harness DB (Floci Cloud DynamoDB) và Orca Workspace Board (Kanban UI):

| Thực thể Harness DB | Thực thể Orca Runtime | Vai trò trên UI Board | Cơ chế ánh xạ kỹ thuật |
| :--- | :--- | :--- | :--- |
| **Epic / Feature lớn** | **Orca Worktree** | 1 Thẻ (Card) lớn trên Kanban Board | `orca worktree create --name "WI-<id>-<slug>"` |
| **Subtask / Bug** | **Orchestration Task** | Mục con trong danh sách `N agents` của Card | `orca orchestration task-create --parent <parent_id>` |
| **Lead / Peer / QC Profile** | **Worker Dispatch / Sub-agent** | 1 dòng tiến trình (thread) có avatar & trạng thái | `orca orchestration worker-start --agent antigravity` |
| **Testcase / ISTQB Matrix** | **Decision Gate** | Rào cản chặn cột `In review` ➔ `Done` | `orca orchestration gate-create --name "QC-Gate"` |

### 4.2 Chuẩn Hóa Trạng Thái 1:1 Bao Gồm Trạng Thái `Removed` (5-State Full Synchronization)
Orca Workspace Board hỗ trợ 4 cột mặc định: `todo`, `in-progress`, `in-review`, `completed`. Chu trình làm việc thực tế của Harness DB bao gồm 5 trạng thái: `New`, `Active`, `Resolved`, `Closed`, và `Removed` (Hủy bỏ / Gỡ khỏi backlog):

```text
  [Harness DB (5 States)]           [Orca Workspace Board & Runtime Actions]
 ┌──────────────────────┐         ┌──────────────────────────────────────────────┐
 │         New          │ ◄─────► │ Todo (0) - Hàng đợi công việc                │
 ├──────────────────────┤         ├──────────────────────────────────────────────┤
 │        Active        │ ◄─────► │ In progress (2) - Đang lập trình             │
 ├──────────────────────┤         ├──────────────────────────────────────────────┤
 │       Resolved       │ ◄─────► │ In review (0) - Chờ QC nghiệm thu độc lập    │
 ├──────────────────────┤         ├──────────────────────────────────────────────┤
 │        Closed        │ ◄─────► │ Done / Completed (0) - Nghiệm thu hoàn tất   │
 ├──────────────────────┤         ├──────────────────────────────────────────────┤
 │       Removed        │ ◄─────► │ Purged / Evicted - Gỡ bỏ khỏi Board & Dừng   │
 └──────────────────────┘         └──────────────────────────────────────────────┘
```

#### Quy tắc xử lý chi tiết từng trạng thái:
1. **`New` ➔ `Todo`**: Thẻ nằm ở cột chờ, agent chưa tiêu tốn tài nguyên GPU/CPU.
2. **`Active` ➔ `In progress`**: Thẻ chuyển sang cột đang làm (`orca worktree set --workspace-status in-progress`).
3. **`Resolved` ➔ `In review`**: Peer hoàn thành code, thẻ tự động chuyển sang `In review` để báo hiệu cho QC.
4. **`Closed` ➔ `Done / Completed`**: QC nghiệm thu pass 100%, chuyển thẻ sang `Done` (`workspace-status completed`), kích hoạt Cổng 5 di chuyển file sang `bmad/rooms/archive/task_<id>/`.
5. **`Removed` ➔ `Gỡ bỏ khỏi Board (Evicted / Resource Release)`**:
   - Khi một Task bị hủy bỏ, trùng lặp hoặc out of scope (`state == 'Removed'`):
     * **Nếu là Worktree độc lập**: Tự động gỡ sạch thẻ khỏi Board qua lệnh `orca worktree rm --worktree <selector> --force` (không để rác chiếm chỗ trên UI).
     * **Nếu là Agent thread trong `main`**: Tự động đóng terminal agent (`orca terminal close`), hủy bỏ worker dispatch (`orca orchestration worker-abandon` / `worker-release`) để dừng ngay việc hao phí token và quota Antigravity/Claude.
     * **Đánh dấu ngữ cảnh**: Thư mục `bmad/rooms/tasks/<task_id>/` được chuyển sang `archive/task_<task_id>_removed/` kèm lý do gỡ bỏ.

### 4.3 Giải Quyết Bài Toán "Orca Không Tạo Được Sub-Agent"
Trong giao diện người dùng đơn thuần, Orca không có nút click thủ công để sinh sub-agent. **Tuy nhiên, qua tầng Orchestration Engine, Orca hỗ trợ mô hình Sub-Agent phân cấp (Hierarchical Sub-Agents) cực mạnh**:

1. **Cơ chế Cha - Con (Parent-Child Task Lineage)**:
   - Agent cấp trên (Lead) đóng vai trò điều phối, gọi lệnh tạo sub-agent cấp dưới (Peer hoặc QC) thông qua cờ `--parent`:
     ```bash
     # Lead tạo Task cha
     LEAD_TASK=$(orca orchestration task-create --title "[Lead] Kien truc WI-3623" --json | jq -r '.result.taskId')

     # Lead sinh Sub-agent Peer Dev để viết code
     orca orchestration worker-start \
       --parent "$LEAD_TASK" \
       --agent antigravity \
       --task-title "[Sub-agent Peer] Sửa CSS sidebar color" \
       --spec "Thực thi đổi màu active theo docs/spec/..."
     ```
2. **Hiển thị trực quan trên Workspace Board**:
   - Các Sub-Agent khi sinh ra sẽ tự động gom nhóm dưới Card của Workspace tương ứng (như danh sách `8 agents` xổ xuống trong Card `main` trên ảnh).
   - Agent cha theo dõi kết quả của sub-agent qua `orca orchestration worker-read --source auto` mà không bị nghẽn giao tiếp.
3. **Cơ chế Điều Hướng Trực Tiếp (Direct Terminal Dispatch)**:
   - Thay vì liên tục mở thêm tab mới làm rác Workspace Board, bộ công cụ tự động dò tìm tab terminal của role tương ứng (`[Lead]`, `[Peer]`, `[QC]`):
     * Nếu tab đã mở: Bắn lệnh trực tiếp qua `orca terminal send --terminal <handle> --text "<task_body>" --enter`.
     * Nếu tab chưa mở: Khởi chạy mới bằng `orca agent launch --worktree active --agent hermes --prompt "..."`.
   - Cập nhật tức thời trạng thái spinner (vàng: đang chạy; tích xanh: đã xong) trên Kanban Board.

---

## 5. QUY TRÌNH THỰC THI 5 BƯỚC CHI TIẾT (E2E WORKFLOW PIPELINE)

### Bước 1: Supervisor khởi tạo phiên điều phối (Run Initialization)
Khi User đưa yêu cầu:
```bash
# 1. Khởi tạo Run điều phối trên Orca
orca orchestration run-create --name "Fix-CDP-Drawer-EmptyState"

# 2. Tạo Work Item trên Harness DB
python3 tools/harness_manager.py add --type Task --title "[CDP] - Fix empty state drawer" --source bot --created-by-profile supervisor --assigned-to-profile lead

# 3. Tạo Task trong Orca Orchestration
orca orchestration task-create --title "Kien truc & Phan ra Task CDP Drawer"
```

### Bước 2: Lead thiết kế kiến trúc & thiết lập Cổng QC (Design & Gate Setup)
Lead phân tích codebase, xác định file cần chỉnh sửa:
```bash
# 1. Tạo Decision Gate chặn việc đóng task tùy tiện
GATE_ID=$(orca orchestration gate-create --name "QC-ISTQB-Verification" --task <task_id> --json | jq -r '.result.gateId')

# 2. Tạo subtask cho Peer Dev và Dispatch vào terminal Peer Hermes
orca terminal send --terminal <peer_handle> --text "Sửa file apps/mfe-cdp/... tuân thủ TDS UI tokens, không nạp thêm lib thừa." --enter
```

### Bước 3: Peer thực thi & Phản biện kỹ thuật (Execution & Challenge)
Peer làm việc trong worktree/terminal được cấp:
- **Trường hợp thuận lợi**: Sửa code, chạy unit test nội bộ, kiểm tra build ➔ Báo cáo nộp cho **Lead Dev**:
  ```bash
  python3 tools/orca_slpc_bridge.py report-done --task-id <task_id> --files "raw-event-list.component.ts"
  ```
- **Trường hợp kiến trúc đề xuất bị lỗi thực tế (Challenge)**:
  ```bash
  orca orchestration ask \
    --to @lead \
    --subject "Kiến trúc flex-order xung đột cấu trúc DOM" \
    --body "Log lỗi Rspack cache panic khi đổi directive. Đề xuất: dùng ng-template thay thế."
  ```

### Bước 4: Lead Dev Thẩm Định Kiến Trúc (Continuous Code Review Gate)
Lead Dev bắt buộc phải rà soát code của Peer trước khi cho phép chuyển sang QC:
```bash
python3 tools/orca_slpc_bridge.py lead-review --task-id <task_id>
```
- **Tiêu chuẩn kiểm tra**: Áp dụng checklist 5 điểm (Single-Ownership, 0% mã hex, Angular 18 OnPush, YAGNI, Dead Code).
- **Nếu FAIL**: Tự động tạo Bug P1 (`agent_reprimand.py --penalize`), giáng task về `Active` bắt Peer sửa lại.
- **Nếu APPROVED**: Chuyển Task sang `Resolved`, ký biên bản bàn giao và bắn lệnh sang terminal QC!

### Bước 5: 3 Sub-Agents Review Chéo & QC Mở Cổng Nghiệm Thu (Cross-Agent Audit & Gate Clearance)
Khi Peer gửi tín hiệu `worker_done`, hệ thống kích hoạt đồng thời 3 Sub-Agents thực thi rà soát độc lập trước khi mở Decision Gate:

1. **Sub-agent 1: `gemini-codebase-analyzer` (Quét Dead Code & Blast Radius)**:
   - Rà soát toàn bộ diff: Phát hiện và dọn sạch các import không dùng (như `TDSDataTableModule` sau khi chuyển `tds-table`), các `@ViewChild` mồ côi.
2. **Sub-agent 2: `strategic-reasoning-architect` (Rà soát Tiêu chuẩn Kiến trúc)**:
   - Thẩm định 100% file thay đổi tuân thủ Single-Ownership.
   - Thẩm định 0% mã màu hex cứng, 100% token chuẩn `tds-color-*` và giữ `OnPush`.
3. **Sub-agent 3: `slpc-qc-verifier` (Nghiệm thu Thực nghiệm 5-Stage ISTQB)**:
   ```bash
   # 1. Sinh bổ sung testcase theo 17 Web Standard Categories
   python3 tools/qc_test_generator.py \
     --source "projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.ts" \
     --sync-harness

   # 2. Chạy test suite thực nghiệm
   npm test -- projects/wicx-crm-fe/apps/mfe-cdp
   ```

4. **Mở Decision Gate & Cập nhật Board / Harness DB**:
   - Khi cả 3 Sub-Agent đều xác nhận **APPROVED** và 100% unit tests PASS:
     ```bash
     # Mở Decision Gate trên Orca
     orca orchestration gate-resolve --gate $GATE_ID --status passed

     # Đồng bộ trạng thái Closed lên Harness DB và chuyển cột Kanban sang Completed
     python3 tools/orca_harness_bridge.py sync-status --task-id <task_id> --state Closed
     python3 tools/harness_manager.py update --id <task_id> --state Closed
     ```

### Bước 5: Supervisor báo cáo User & Thu dọn phiên làm việc
Supervisor kiểm tra inbox toàn hệ thống (`orca orchestration inbox`), xác nhận tất cả task và gates đã xử lý xong, báo cáo cho User một thông điệp ngắn gọn và giải phóng tài nguyên:
```bash
orca orchestration worker-release --all
```

---

## 6. QUẢN LÝ PHÌNH TO, CHỐNG LOẠN CONTEXT & THU GOM RÁC BMAD (CONTEXT ISOLATION & SAFE GARBAGE COLLECTION)

### 6.1 Phân tích lỗi gốc gây Loạn Context (Root Cause of Context Collision)
Trong môi trường nhiều agent chạy đồng thời (như 8 agent trong Orca IDE):
1. **Lỗi con trỏ dùng chung (Shared Mutable Pointer Antipattern)**:
   - File `bmad/rooms/<role>/latest_handoff.md` là một biến toàn cục dùng chung.
   - Khi Agent A đang xử lý Task #889 (Table) và Agent B bắt đầu Task #3623 (Color), Agent B ghi đè lên `latest_handoff.md`.
   - Khi QC hoặc Lead vào kiểm thử Task #889, họ nạp nhầm context của Task #3623 ➔ Sửa sai file, gãy luồng, sinh bug.
2. **Lỗi xóa sớm khi chưa nghiệm thu (Premature Cleanup Antipattern)**:
   - Task đang code (`Active`) hoặc đang chờ kiểm thử (`Resolved`) nhưng chưa `Closed` mà bị script dọn dẹp xóa mất file handoff / biên bản thảo luận ➔ Mất sạch ngữ cảnh kiểm thử, khiến QC không biết Acceptance Criteria để verify.

### 6.2 Kiến trúc Cô Lập Ngữ Cảnh Theo Task (Task Namespace Isolation)
**Tuyệt đối loại bỏ việc phụ thuộc vào con trỏ toàn cục `latest_handoff.md` khi chạy song song.**  
Mọi ngữ cảnh trao đổi giữa các Agent phải được đóng gói độc lập theo Task ID:

```text
bmad/rooms/
├── tasks/                               # VÙNG CÔ LẬP THEO WORK ITEM (TASK SANDBOX)
│   ├── 889/                             # Không gian riêng của Task #889
│   │   ├── handoff_supervisor.md        # Yêu cầu gốc & Acceptance Criteria
│   │   ├── handoff_lead.md              # Thiết kế kiến trúc & phân rã của Lead
│   │   ├── handoff_peer.md              # Báo cáo code diff & kết quả tự test
│   │   ├── handoff_qc.md                # Báo cáo 5-Stage ISTQB test
│   │   └── discussion.md                # Biên bản thảo luận & đồng thuận
│   └── 3623/                            # Hoàn toàn độc lập với Task #889
│       ├── handoff_supervisor.md
│       └── handoff_peer.md
│
├── archive/                             # VÙNG LƯU TRỮ LỊCH SỬ KHI TASK ĐÃ CLOSED
│   └── task_889/                        # Toàn bộ folder tasks/889/ được dời về đây
│
└── adrs/                                # CÁC QUYẾT ĐỊNH KIẾN TRÚC BỀN VỮNG (O(1))
    └── ADR-889-ng-template-refactor.md
```

- **Quy tắc đọc context**: Agent được dispatch với tham số `--item-id <id>` **CHỈ ĐƯỢC PHÉP** đọc các file trong `bmad/rooms/tasks/<id>/`. Tuyệt đối không đọc chéo sang task khác.

### 6.3 Khóa An Toàn Trạng Thái Harness DB (Strict State Lock Guard)
Để đảm bảo **không bao giờ xóa nhầm dữ liệu đang làm dở**:
- Công cụ `tools/room_cleanup.py` bắt buộc phải query trạng thái thời gian thực từ Floci DynamoDB (`tools/floci_client.py`).
- **Điều kiện tiên quyết**: Chỉ Work Item có `state == 'Closed'` mới được phép dọn dẹp.
- **Cơ chế phòng vệ (Hard Abort)**: Nếu task ở trạng thái `New`, `Active`, `Resolved`, `Blocked`, hoặc PR đang chờ review ➔ **Hệ thống từ chối dọn dẹp ngay lập tức**, in cảnh báo và hủy lệnh.

### 6.4 Chính sách Archive (Lưu Trữ An Toàn) Thay Vì Delete (Xóa Trắng)
Không xóa mù quáng bằng lệnh `rm` hay `unlink()`. Khi một task đạt `Closed`:
1. **Di chuyển nguyên vẹn (Atomic Move)**: Thư mục `bmad/rooms/tasks/<task_id>/` được di chuyển sang `bmad/rooms/archive/task_<task_id>/`.
2. **Chắt lọc ADR vĩnh viễn**: Nếu task có thay đổi kiến trúc hệ thống, Lead chắt lọc 1 bản ghi ADR duy nhất vào `bmad/adrs/ADR-<id>.md` (dưới 30 dòng).
3. **Bảo toàn khả năng truy vết (Auditability)**: Khi phát sinh lỗi hồi quy (regression) sau 1 tháng, Developer chỉ cần mở `archive/task_<id>/` để xem chính xác Peer nào đã sửa, test case nào đã pass mà không sợ bị mất dữ liệu.

---

## 7. KỊCH BẢN THỰC THI THỬ NGHIỆM (PILOT EXECUTION SCRIPT)

Để tự động hóa luồng trên chỉ bằng một dòng lệnh điều phối, xây dựng script wrapper `tools/orca_slpc.sh`:

```bash
#!/usr/bin/env bash
# tools/orca_slpc.sh - Khởi chạy nhanh luồng phối hợp SLPC trên Orca
set -euo pipefail

TASK_TITLE="${1:-"[Feature] Cap nhat module"}"
TASK_SPEC="${2:-"Kiem tra va thuc hien theo spec"}"

echo "=== [1/4] KHOI TAO ORCA RUN BOI SUPERVISOR ==="
RUN_JSON=$(orca orchestration run-create --name "SLPC-$(date +%s)" --json)
RUN_ID=$(echo "$RUN_JSON" | jq -r '.result.runId')
echo "Run ID: $RUN_ID"

echo "=== [2/4] TAO DECISION GATE BOI LEAD ==="
TASK_JSON=$(orca orchestration task-create --title "$TASK_TITLE" --run "$RUN_ID" --json)
TASK_ID=$(echo "$TASK_JSON" | jq -r '.result.taskId')
GATE_JSON=$(orca orchestration gate-create --name "QC-Signoff" --task "$TASK_ID" --run "$RUN_ID" --json)
GATE_ID=$(echo "$GATE_JSON" | jq -r '.result.gateId')

echo "Task ID: $TASK_ID | Gate ID: $GATE_ID"

echo "=== [3/4] DISPATCH CHO PEER WORKER ==="
orca orchestration worker-start \
  --worktree current \
  --agent hermes \
  --task "$TASK_ID" \
  --spec "$TASK_SPEC"

echo "=== [4/4] HE THONG SAN SANG LANG NGHE VA DIEU PHOI ==="
```

---

## 8. KẾT QUẢ TRIỂN KHAI & NGHIỆM THU (IMPLEMENTATION & VERIFICATION STATUS)

Toàn bộ đặc tả đã được hiện thực hóa 100% bằng mã nguồn thực tế và kiểm thử thành công:

1. **Giai đoạn 1 (Bộ Điều Phối Master & Shell Wrapper)**:
   - File: `tools/orca_slpc_bridge.py` và `tools/orca_slpc.sh`.
   - Trạng thái: **HOÀN THÀNH 100%**. Hỗ trợ `init-run`, `create-task`, `dispatch-peer`, `report-done`, `qc-verify`, `sync-board`.
2. **Giai đoạn 2 (Chuẩn Hóa 5-State & Đồng Bộ Workspace Board)**:
   - File: `tools/orca_harness_bridge.py` và hook trong `tools/harness_manager.py`.
   - Trạng thái: **HOÀN THÀNH 100%**. Đồng bộ thời gian thực `New`, `Active`, `Resolved`, `Closed`, `Removed`.
3. **Giai đoạn 3 (Cô Lập Context & Thu Gom Rác An Toàn)**:
   - File: `tools/room_cleanup.py` và `bmad/rooms/tasks/<id>/`.
   - Trạng thái: **HOÀN THÀNH 100%**. Cấm xóa task chưa Closed; di chuyển vào `archive/` bảo tồn truy vết.
4. **Giai đoạn 4 (Bộ Công Cụ Xử Phạt Kỹ Thuật & Thảo Luận)**:
   - File: `tools/agent_reprimand.py` và `tools/record_discussion.py`.
   - Trạng thái: **HOÀN THÀNH 100%**. Xử lý 9 loại lỗi vi phạm, tự giáng cấp task trên Harness DB và lưu ADR.
5. **Giai đoạn 5 (Vận Hành 4 Agent Thuần Hermes)**:
   - Runtime: 100% Agent (`Supervisor`, `Lead`, `Peer`, `QC`) chạy Hermes trên model `gemini-3.8-flash-high`.
   - Trạng thái: **HOÀN THÀNH 100%**. Cơ chế Direct Terminal Dispatch điều hướng trực tiếp vào tab có sẵn.
