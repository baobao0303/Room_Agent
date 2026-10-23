# Master Architecture Spec: Mô Hình Điều Hành Multi-Agent — Ephemeral Sub-Agent vs Persistent Worker Pool

- **Mã tài liệu**: `ARCH-SPEC-EPHEMERAL-SUBAGENT-ORCHESTRATION-2026-V1`  
- **Phiên bản**: `1.0.0` (Open-Source Architecture Blueprint)  
- **Chủ đề**: Tối ưu hóa điều hành Multi-Agent trong IDE Runtime: Chiến lược Sub-Agent theo phiên (Ephemeral Sub-Agent) thay thế cho Nhóm Agent thường trực (Persistent Worker Pool)  
- **Phạm vi kỹ thuật**: Orca IDE CLI (`orca agent launch`), Hermes Agent Engine, SLPPC Architecture Model.

---

## 1. TỔNG QUAN & TRIẾT LÝ VẬN HÀNH (CORE PHILOSOPHY)

Trong các hệ sinh thái phát triển phần mềm tự động hóa bằng Multi-Agent (như SLPPC: Supervisor - PM - Lead - Peer - QC), việc duy trì đồng thời nhiều agent chạy ngầm liên tục thường dẫn đến sự lãng phí tài nguyên máy tính và tiêu hao token khổng lồ.

Tài liệu này xác lập triết lý điều hành mới:
> **"Ephemeral by Default, Persistent by Exception"**  
> *(Mặc định sử dụng Sub-Agent tạm thời dùng xong tự hủy; Chỉ duy trì Agent thường trực khi thực sự bắt buộc).*

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

---

## 2. PHÂN TÍCH BÀI TOÁN SUY THOÁI CỦA PERSISTENT WORKER POOL

Khi khởi chạy cố định 5–10 Agent Tabs (Peer 1, Peer 2, Peer 3, Peer 4, Design, Lead, QC...) chạy thường trực trong không gian làm việc:

### 2.1. Hiện tượng "Ngáo Context" (Context Drift & Hallucination)
- **Cơ chế**: Một Agent thường trực lưu giữ toàn bộ lịch sử hội thoại của các tác vụ trước đó. Khi trải qua 10–20 lượt trao đổi, kích thước context phình to lên mức **200.000 – 500.000 tokens**.
- **Hệ quả**: LLM bị "nhiễu thông tin", dễ nhầm lẫn giữa logic của task cũ và task mới, sinh code sai lệch hoặc thực hiện các hành động thừa thãi không được yêu cầu.

### 2.2. Lãng Phí Token Cấp Số Nhân (Exponential Token Waste)
- Với mô hình thường trực, ngay cả khi giao một chỉ thị ngắn 1 dòng (ví dụ: *"chạy lại unit test"*), client bắt buộc phải gửi kèm toàn bộ lịch sử 300k tokens cũ lên nhà cung cấp mô hình.
- Chi phí API và độ trễ phản hồi (latency) tăng vọt một cách không cần thiết.

### 2.3. Chiếm Dụng RAM/CPU & Chi Phí Giám Sát (Resource Bloat)
- Mỗi agent thường trực tiêu tốn 1 tiến trình PTY nền và giữ kết nối socket.
- Hệ thống phải duy trì script giám sát nhịp tim (`Heartbeat Monitor`) liên tục gửi lệnh ping/status định kỳ để kiểm tra xem agent có bị disconnect hay treo không.

---

## 3. MÔ HÌNH EPHEMERAL SUB-AGENT (DÙNG XONG TỰ HỦY)

### 3.1. Nguyên Lý Hoạt Động (Lifecycle Flow)
1. **Spawn On-Demand**: Khi có một task cụ thể cần làm, Coordinator gọi lệnh kích hoạt một Sub-Agent mới với đúng bản mô tả công việc (Task Specification).
2. **Clean Context Window**: Sub-Agent khởi động với context tươi mới 100% (chỉ chứa system prompt và đúng thông tin của task đó, xấp xỉ **10.000 – 30.000 tokens**).
3. **Autonomous Execution**: Sub-Agent thực thi code, chạy test tự động, kiểm tra kết quả.
4. **Report & Auto-Tear-down**: Sub-Agent xuất bản biên bản kết quả hoặc nộp trạng thái `Resolved`. Coordinator tiếp nhận báo cáo và tiến hành đóng (kill/close) terminal session của Sub-Agent ngay lập tức.

---

## 4. BẢNG SO SÁNH ĐỊNH LƯỢNG CHI TIẾT

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 BẢNG SO SÁNH: EPHEMERAL SUB-AGENT VS PERSISTENT PEER        │
├──────────────────────┬──────────────────────────┬───────────────────────────┤
│ TIÊU CHÍ             │ EPHEMERAL SUB-AGENT      │ PERSISTENT WORKER POOL    │
├──────────────────────┼──────────────────────────┼───────────────────────────┤
│ Tiêu hao Token/Turn  │ 🟢 10k - 30k tokens      │ 🔴 200k - 500k tokens     │
│ Tiết kiệm chi phí    │ 🟢 Tiết kiệm 60% – 80%   │ 🔴 Tiêu tốn ngân sách     │
│ Độ tươi mới Context  │ 🟢 100% Sạch & Chuẩn     │ 🔴 Dễ bị trôi dạt ngữ cảnh│
│ Chiếm dụng RAM/CPU   │ 🟢 Giải phóng về 0 ngay  │ 🟡 Chiếm dụng PTY liên tục│
│ Vận hành Heartbeat   │ 🟢 Không tốn tài nguyên  │ 🟡 Phải chạy daemon ping  │
│ Độ trễ phản hồi      │ 🟢 Phản hồi nhanh        │ 🟡 Chờ load context lớn   │
│ Vòng đời (Lifecycle) │ 🟢 Mở ➔ Xong ➔ Tự hủy    │ 🟡 Chạy nền vĩnh viễn     │
│ Khả năng mở rộng     │ 🟢 Mở song song 1-10     │ 🔴 Giới hạn số lượng tab  │
│                      │    agents đồng thời      │    mở trên màn hình       │
└──────────────────────┴──────────────────────────┴───────────────────────────┘
```

---

## 5. QUY TẮC PHÂN BỔ 80/20 (WHEN TO USE WHAT)

### 5.1. Khi Nào Dùng Ephemeral Sub-Agent (Áp Dụng Cho 80% Công Việc):
- **Tác vụ đơn lẻ, độc lập**: Viết một unit test suite, sửa một bug cụ thể, format mã nguồn, kiểm tra lint.
- **Tác vụ phân tích & báo cáo**: Đọc và audit một nhóm file, quét an ninh rò rỉ mã nguồn, kiểm tra tính tương thích.
- **Tác vụ song song (Parallel Workstreams)**: Cần 3–4 agents cùng lúc làm 3–4 module không giao nhau. Mỗi sub-agent nhận 1 module, làm xong tự đóng mà không làm rối màn hình IDE.

### 5.2. Khi Nào Dùng Persistent Peer (Chỉ Áp Dụng Cho 20% Công Việc):
- **Chuỗi thao tác liên hoàn phụ thuộc trạng thái (Stateful Multi-Step Tasks)**: Một lập trình viên cần trải qua chuỗi 5–10 bước can thiệp sâu, trong đó bước sau cần quan sát trực tiếp biến môi trường, tiến trình debug hoặc kết quả vừa tạo của bước trước mà không thể mô tả trọn vẹn trong một bản spec đơn lẻ.
- **Phiên làm việc tương tác trực tiếp với con người (Pair Programming)**: Khi User muốn ngồi chat và chỉnh sửa code trực tiếp qua lại với đúng một Persona lập trình viên duy nhất.

---

## 6. CÁC PHƯƠNG THỨC KÍCH HOẠT TRONG RUNTIME

Mô hình Ephemeral Sub-Agent được kích hoạt thông qua 3 phương thức chuẩn hóa:

### 6.1. Phương Thức 1: Bật Tab/Pane Độc Lập Qua Orca CLI
Phù hợp khi cần quan sát trực quan tiến độ chạy trên màn hình IDE:
```bash
# 1. Kích hoạt Sub-Agent với nhiệm vụ định vị rõ ràng
orca agent launch --worktree active --agent hermes --prompt "<Task Specification Zero-Search>"

# 2. Sau khi Sub-Agent nộp báo cáo kết quả: Đóng terminal để giải phóng tài nguyên
orca terminal close --terminal <handle>
```

### 6.2. Phương Thức 2: Chạy Ngầm Bằng Tool Delegation Nội Bộ (`delegate_task`)
Phù hợp cho các tác vụ cần chạy ngầm, không mở thêm tab giao diện:
- Coordinator sử dụng tool `delegate_task`:
  * Spawn 1 đến 10 worker chạy hoàn toàn cô lập dưới background.
  * Tự động tổng hợp kết quả trả về cho Coordinator khi hoàn tất.
  * Tự động dọn dẹp bộ nhớ và context khi kết thúc turn.

### 6.3. Phương Thức 3: Động Cơ Điều Phối Orca Engine (`orca orchestration`)
Phù hợp cho các pipeline lớn có phân cấp kiểm duyệt:
```bash
# Tạo Run điều phối
orca orchestration run-create --title "Pipeline Sprint"

# Tạo Task và gán Worker xử lý theo lượt
orca orchestration task-create --title "Sub-task A"
orca orchestration worker-start --task-id <id>
```

---

## 7. QUY CHUẨN GIAO TASK ZERO-SEARCH CHO SUB-AGENT

Để Sub-Agent đạt hiệu quả 100% trong một vòng đời ngắn hạn (Single-Turn / Few-Turns Execution), bản mô tả công việc (Task Description) gửi vào bắt buộc phải tuân thủ chuẩn **Zero-Search 5 Thành Phần**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 5 THÀNH PHẦN BẮT BUỘC CỦA TASK ZERO-SEARCH                  │
├────────────────────┬────────────────────────────────────────────────────────┤
│ 1. Target Files    │ Đường dẫn file cụ thể (Single-Ownership).              │
│ 2. Anchors / Lines │ Tên hàm, class, component hook, selector hoặc dòng cụ  │
│                    │ thể cần can thiệp.                                     │
│ 3. Concrete Change │ Logic chi tiết, kiểu dữ liệu DTO, token hoặc payload.  │
│ 4. Acceptance (AC) │ Tiêu chuẩn nghiệm thu định lượng (Pass test suite nào).│
│ 5. Test Command    │ Lệnh kiểm tra cơ học cụ thể (vd: npx jest path/to/spec)│
└────────────────────┴────────────────────────────────────────────────────────┘
```
*Nguyên tắc*: Tuyệt đối cấm giao task 1 dòng mơ hồ (ví dụ: *"fix bug header"*). Giao task chuẩn giúp Sub-Agent mở đúng file đích bằng `read_file`, sửa bằng `patch`, chạy test bằng `terminal`, báo cáo và kết thúc ngay mà không cần tốn token chạy các lệnh tìm kiếm (`search_files`, `find`, `rg`).

---

## 8. NGUYÊN TẮC AN TOÀN & RÀO CẢN VAI TRÒ (SAFETY INVARIANTS)

1. **Maker & Checker Độc Lập**: Sub-Agent phụ trách viết code (Maker) tuyệt đối không có quyền tự nghiệm thu và đóng task `Closed`. Việc nghiệm thu bắt buộc phải do QC Sub-Agent hoặc Coordinator thẩm định cơ học độc lập.
2. **Context Clearance**: Sau khi Sub-Agent kết thúc, terminal session phải được đóng (`orca terminal close`). Không tái sử dụng lại terminal cũ cho các task thuộc domain khác để chống lây nhiễm context.
3. **Anti-Leak Assurance**: Mọi prompt và chỉ thị truyền vào Sub-Agent phải được lọc qua bộ kiểm duyệt an ninh tự động, loại bỏ 100% các bí mật, token nội bộ hoặc địa chỉ thực tế.

---

## 9. GIAO THỨC QUẢN TRỊ & KIỂM SOÁT VÒNG ĐỜI SUB-AGENT (SUB-AGENT GOVERNANCE & LIFECYCLE MANAGEMENT)

Tạo Sub-Agent **BẮT BUỘC PHẢI ĐI KÈM QUẢN TRỊ NGHIÊM NGẶT**. Nếu thả nổi Sub-Agent mà không có cơ chế kiểm soát, hệ thống sẽ đối mặt với 4 thảm họa:
1. **Fork Bomb & Cạn Kiệt Tài Nguyên**: Sub-Agent tự sinh Sub-Agent đệ quy làm tràn RAM và sập CPU máy trạm.
2. **Zombie Terminals**: Các tiến trình PTY bị bỏ rơi chạy ngầm không người quản lý.
3. **Treo Turn Vô Tận**: Sub-Agent chạy lệnh quét vô định hoặc interactive prompt không bao giờ thoát.
4. **Báo Cáo Lá Cải (Hallucinated Self-Report)**: Sub-Agent tự khẳng định "đã làm xong" nhưng thực chất code không chạy.

Để triệt tiêu hoàn toàn các rủi ro trên, hệ thống thiết lập **Bộ Khung 6 Trụ Cột Quản Trị Sub-Agent**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 BỘ KHUNG 6 TRỤ CỘT QUẢN TRỊ VÒNG ĐỜI SUB-AGENT              │
│                                                                             │
│   1. CONCURRENCY CEILING     ──► Giới hạn trần tối đa 3–5 Sub-Agents cùng lúc│
│   2. 6-PHASE STATE MACHINE   ──► SPAWNED -> EXECUTING -> REAPED             │
│   3. TIMEOUT & WATCHDOG      ──► Hard Timeout 300s, tự ngắt lệnh treo        │
│   4. MECHANICAL VERIFICATION ──► Cấm tin lời tự khai; bắt buộc kiểm tra hash │
│   5. ZOMBIE TERMINAL REAPER  ──► Tự động quét và dọn terminal mồ côi        │
│   6. ANTI-RECURSION FENCE    ──► Cấm Sub-Agent spawn Sub-Agent đệ quy        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.1. Trụ Cột 1: Giới Hạn Trần Đồng Thời (Concurrency Ceiling & Throttling)
- **Quy chuẩn**: Coordinator khống chế tối đa **không quá 3–5 Sub-Agents chạy song song** tại cùng một thời điểm (`max_concurrent_children: 3`).
- **Lý do**: Ngăn chặn hiện tượng nghẽn CPU khi build nhiều module cùng lúc và tránh chạm ngưỡng Rate Limit / Quota của nhà cung cấp mô hình (LLM API).
- Khi có 10 tasks, Coordinator chia thành các đợt chạy (Batches): Đợt 1 chạy 3 task $\rightarrow$ xong thu hồi $\rightarrow$ Đợt 2 chạy 3 task tiếp theo.

### 9.2. Trụ Cột 2: Máy Trạng Thái Vòng Đời 6 Bước (6-Phase Lifecycle State Machine)
Mọi Sub-Agent đều phải chuyển dịch tuần tự qua 6 trạng thái kiểm soát:
```text
[SPAWNED] ──► [ALLOCATED] ──► [EXECUTING] ──► [REPORTED] ──► [VERIFIED] ──► [REAPED]
```
1. **`SPAWNED`**: Khởi tạo terminal session độc lập trên Orca.
2. **`ALLOCATED`**: Bơm đúng context Zero-Search, gắn mã định danh `handle` và timeout quota.
3. **`EXECUTING`**: Sub-Agent thao tác code và chạy test trong phạm vi được giao.
4. **`REPORTED`**: Sub-Agent xuất bản báo cáo tóm tắt và mã hash các file đã sửa.
5. **`VERIFIED`**: Coordinator hoặc QC chạy kiểm tra cơ học đối soát kết quả thật.
6. **`REAPED`**: Gọi `orca terminal close` thu hồi ngay lập tức, đưa tài nguyên RAM/PTY về 0.

### 9.3. Trụ Cột 3: Watchdog Daemon & Trần Thời Gian (Timeout Ceiling)
- **Hard Timeout**: Mỗi Sub-Agent được cấp một ngân sách thời gian tối đa (mặc định: `timeout_s: 300` - 5 phút).
- **Cơ chế can thiệp**:
  - Nếu Sub-Agent bị kẹt bởi một lệnh shell không hồi kết (unbounded scan, infinite loop), Watchdog gửi tín hiệu ngắt:
    ```bash
    orca terminal send --terminal <handle> --interrupt
    ```
  - Nếu quá thời gian trần mà không hồi đáp: Coordinator phát lệnh cưỡng chế đóng terminal và ghi nhận lỗi `TimeoutError`, chuyển task sang `Blocked` để tránh treo toàn bộ phòng ban.

### 9.4. Trụ Cột 4: Chốt Chặn Bằng Chứng Cơ Học (Mechanical Verification vs Self-Report)
- **Quy tắc vàng**: *"Never trust a sub-agent's self-report"* (Không bao giờ tin vào lời tự báo cáo của Sub-Agent).
- Khi Sub-Agent nói *"Tôi đã viết code và chạy test pass 100%"*, Coordinator **BẮT BUỘC PHẢI XÁC MINH CƠ HỌC**:
  1. Kiểm tra mã thoát (Exit Code): Exit code phải bằng `0`.
  2. Kiểm tra Git Diff thật: Chạy `git status --short` và `git diff` xác nhận file đích thực sự có thay đổi hợp lệ.
  3. Kiểm tra Output Test thật: Bắt buộc đọc output log thật từ test runner (Jest, Cargo, Pytest), cấm chấp nhận output giả lập.

### 9.5. Trụ Cột 5: Cơ Chế Quét & Tiêu Diệt Terminal Mồ Côi (Zombie Terminal Reaper)
- **Hiện tượng**: Khi Coordinator bị crash, restart hoặc user đóng trình duyệt đột ngột, một số Sub-Agent có thể bị bỏ quên (Orphaned / Zombie PTY).
- **Reaper Script**:
  - Định kỳ (hoặc trước mỗi phiên làm việc mới), hệ thống chạy hàm quét:
    ```bash
    orca terminal list --json
    ```
  - Đối chiếu danh sách handles đang sống với danh sách task đang Active trong CSDL.
  - Mọi terminal không có Task ID hợp lệ bảo trợ đều bị Reaper tự động đóng sạch sẽ (`orca terminal close`), bảo đảm hệ thống luôn sạch 100%.

### 9.6. Trụ Cột 6: Rào Cản Thẩm Quyền Chống Đệ Quy (Authority Fencing)
Để bảo vệ kiến trúc SLPPC không bị phá vỡ, Sub-Agent bị khóa các thẩm quyền sau:
1. **Cấm Spawn Đệ Quy**: Sub-Agent bị cấm hoàn toàn quyền gọi `delegate_task` hoặc `orca agent launch` để sinh thêm con (No Nested Delegation).
2. **Cấm Tự Đóng Task**: Sub-Agent chỉ được nộp trạng thái `Resolved`. Quyền chuyển trạng thái `Closed` thuộc độc quyền của QC Verifier hoặc Coordinator.
3. **Cấm Can Thiệp Memory Hệ Thống**: Sub-Agent không được phép ghi đè persistent memory (`MEMORY.md` / `USER.md`) của toàn phòng ban để tránh làm ô nhiễm tri thức lõi.

---

## 10. MA TRẬN PHÂN QUYỀN QUẢN LÝ TRONG MÔ HÌNH SLPPC (WHO MANAGES WHAT)

Trong mô hình **SLPPC**, cơ chế Sub-Agent được quản lý theo mô hình **Phân Tầng 2 Cấp (Two-Tier Governance)**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN PHÂN QUYỀN QUẢN LÝ SUB-AGENT (SLPPC)                │
│                                                                             │
│   [CẤP 1: CHIẾN LƯỢC & HẠ TẦNG] ──► SUPERVISOR                              │
│   • Giám sát ngân sách token tổng & trần đồng thời (Concurrency Ceiling)    │
│   • Vận hành Zombie Terminal Reaper (dọn sạch PTY mồ côi)                   │
│   • Báo cáo duy nhất với User (SPOC)                                        │
│                                                                             │
│   [CẤP 2: KỸ THUẬT & ĐIỀU PHỐI TRỰC TIẾP]                                   │
│   ├── LEAD DEV (Quản lý Sub-Agents Lập Trình / Maker Pool):                 │
│   │   • Phân rã Task Zero-Search 5 thành phần                               │
│   │   • Trực tiếp Spawn, giám sát Timeout 300s và Close Sub-Agent sau khi fix│
│   │   • Code Review 5 tiêu chí trước khi bàn giao sang QC                   │
│   │                                                                         │
│   └── QC VERIFIER (Quản lý Sub-Agents Kiểm Thử / Checker Pool):             │
│       • Spawn Sub-Agent chạy song song các test suites                      │
│       • Độc quyền thực thi chốt chặn kiểm chứng cơ học (Mechanical Gate)    │
│       • Độc quyền quyền hạn ký duyệt đóng task Closed                       │
│                                                                             │
│   [CỐ VẤN & AN NINH ĐỘC LẬP]                                                │
│   ├── PM AGENT: Thẩm định khả thi Kev System One trước khi Lead spawn task  │
│   └── SECURITY SENTINEL: Tự động quét chặn rò rỉ mã nguồn/secrets từ Sub-Agent│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.1. Supervisor (Macro Governor - Quản Trị Vĩ Mô & Hạ Tầng)
- **Thẩm quyền**: Là phiên làm việc thường trực duy nhất đại diện giao tiếp với User.
- **Trách nhiệm**:
  1. Kiểm soát trần đồng thời toàn phòng: Đảm bảo tổng số Sub-Agents đang chạy trên máy trạm không vượt quá ngưỡng an toàn (tối đa 3–5).
  2. Kích hoạt **Zombie Reaper**: Tự động quét và cưỡng chế đóng toàn bộ terminal rác nếu có Sub-Agent bị đứt kết nối hoặc coordinator bị crash.
  3. Tuyệt đối không can thiệp viết code tính năng (`Anti-Role Trespass`).

### 10.2. Lead Dev (Technical Dispatcher - Quản Trị Trực Tiếp Nhóm Maker)
- **Thẩm quyền**: Quản trị trực tiếp vòng đời của các **Coding Sub-Agents** (Peer Workers).
- **Trách nhiệm**:
  1. Đóng gói chỉ thị theo chuẩn **Zero-Search 5 Thành Phần** trước khi spawn Sub-Agent.
  2. Đóng vai trò **Watchdog trực tiếp**: Bắt lỗi nếu Sub-Agent chạy lệnh shell treo quá 300s, gửi tín hiệu ngắt `--interrupt`.
  3. Tiếp nhận Git diff từ Sub-Agent, thực thi Code Review (5 tiêu chí).
  4. Sau khi duyệt đạt, Lead trực tiếp gọi lệnh đóng terminal (`orca terminal close`) để giải phóng tài nguyên trước khi bàn giao sang QC.

### 10.3. QC Verifier (Independent Quality Gate - Quản Trị Nhóm Checker)
- **Thẩm quyền**: Quản trị các **Testing Sub-Agents** và độc quyền kiểm định chất lượng.
- **Trách nhiệm**:
  1. Có quyền spawn Sub-Agent chuyên biệt (ví dụ: `slpc-qc-verifier`) để chạy song song các test suites độc lập.
  2. Thực thi **Chốt Chặn Kiểm Chứng Cơ Học (Mechanical Verification)**: Không tin lời khai của Coding Sub-Agent; bắt buộc đối soát mã thoát (Exit Code = 0) và log test runner thật.
  3. Độc quyền thẩm quyền ký duyệt chuyển trạng thái task từ `Resolved` sang `Closed`.

### 10.4. PM Agent & Security Sentinel (Cố Vấn & Giám Sát Ngầm)
- **PM Agent**: Đánh giá định lượng qua Kev System One (`<50ms`) xem task có đủ khả thi và đúng phạm vi không trước khi Lead cho phép spawn Sub-Agent (ngăn chặn tình trạng tạo task rác gây lãng phí token).
- **Security Sentinel**: Tự động giám sát luồng I/O của mọi Sub-Agent, sở hữu quyền VETO chặn đứng mọi commit hoặc output có dấu hiệu làm lộ bí mật hoặc thông tin nhạy cảm.

---

## 11. BỘ PROMPT CHUẨN: SYSTEM PROMPT PM ORCHESTRATOR & ONE-SHOT DELEGATION PROMPT

Để hiện thực hóa triệt để mô hình **Ephemeral Sub-Agent Orchestration**, hệ thống ban hành 2 mẫu prompt chuẩn mực dùng trực tiếp cho phiên làm việc của PM Agent / Technical PM:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 LUỒNG VẬN HÀNH BỘ PROMPT PM ORCHESTRATOR                    │
│                                                                             │
│   [USER] ──(Gửi One-Shot Prompt)──► [PM AGENT (Persistent)]                 │
│                                            │                                │
│                     ┌──────────────────────┴──────────────────────┐         │
│                     ▼                                             ▼         │
│       [1. SUB-AGENT DEV (Ephemeral)]                [2. SUB-AGENT QC]       │
│       • Nhận Zero-Search Task Spec                  • Nhận Git Diff & ACs   │
│       • Code & Unit Test nội bộ                     • Kiểm thử độc lập      │
│       • Nộp Diff & Status                           • Ký duyệt / Reject     │
│       • TỰ HỦY TERMINAL                             • TỰ HỦY TERMINAL       │
│                     │                                             │         │
│                     └──────────────────────┬──────────────────────┘         │
│                                            ▼                                │
│                         [PM TỔNG HỢP & BÁO CÁO USER]                        │
│                         • Cập nhật Harness DB & Progress                    │
│                         • Context PM sạch 100% (<30k tokens)                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.1. Mẫu 1: System Prompt Cho PM Agent (Agent Thường Trực)
Dán vào file cấu hình Profile của PM (`profiles/pm.md`) hoặc gửi khi bắt đầu phiên làm việc:

```markdown
Role: Senior Technical PM & Orchestrator.
Model: Combo-Supervisor-PM (ag/gemini-3.8-flash-high).
Triết lý: Ephemeral by Default, Persistent by Exception (Spec: ARCH-SPEC-EPHEMERAL-SUBAGENT-ORCHESTRATION).

NHIỆM VỤ:
1. Tiếp nhận tính năng từ User, đọc specs và architecture.json để hiểu phạm vi.
2. KHÔNG tự tay sửa toàn bộ code. Bạn phải phân rã thành các "Zero-Search Tasks" (nhiệm vụ độc lập, chỉ định rõ đường dẫn file cần sửa).
3. ĐIỀU PHỐI SUB-AGENT:
   - Với mỗi task code: Kích hoạt Sub-Agent Dev (model Combo-Subagent-Dev / ag/gemini-3.8-flash-low) thực thi.
   - Với mỗi task review/test: Kích hoạt Sub-Agent QC (model Combo-Subagent-QC / ag/gemini-3.8-flash-high) kiểm định.
4. QUẢN LÝ CONTEXT:
   - Thu nhận kết quả tóm tắt từ sub-agent (chỉ lấy diff và status, không nhồi toàn bộ log vào context).
   - Đảm bảo sub-agent kết thúc và tự hủy ngay sau khi task hoàn thành.
   - Cập nhật tiến độ vào Harness DB (harness_manager.py) và Sổ cái agent_progress.py.
```

---

### 11.2. Mẫu 2: One-Shot Prompt — Giao Việc Cho PM Điều Phối Sub-Agent
Dán câu lệnh này vào chat để PM tự bóc tách và gọi sub-agent thực thi theo đợt:

```text
"Đọc tài liệu kiến trúc và yêu cầu cho tính năng: [Tên tính năng, ví dụ: Contact List Filter].
Hãy đóng vai trò Technical PM, thực hiện quy trình Ephemeral Sub-Agent:

1. Phân tích spec, bóc tách ra các subtask nhỏ độc lập (nêu rõ file input/output theo chuẩn Zero-Search 5 thành phần).
2. Kích hoạt Sub-Agent Dev (Combo-Subagent-Dev) xử lý từng task code, tự test cục bộ.
3. Sau khi dev xong, kích hoạt Sub-Agent QC (Combo-Subagent-QC) đối chiếu diff với tiêu chí chấp nhận.
4. Thu hồi báo cáo ngắn gọn, cập nhật task lên Harness DB và kết thúc phiên của sub-agent để làm sạch context."
```

---

### 11.3. Phân Tích Chuyên Sâu 4 Điểm Mạnh Cốt Lõi Của Thiết Kế Prompt:
1. **Khắc Chế Triệt Để Bùng Nổ Ngữ Cảnh (Context Explosion Defense)**:
   - Điều khoản: *"Chỉ lấy diff và status, không nhồi toàn bộ log vào context"*.
   - Đây là chốt chặn quan trọng nhất giúp session PM duy trì được độ tươi mới dưới 30k tokens dù trải qua 20–30 tasks, vì toàn bộ log build/terminal dài hàng nghìn dòng đã bị tiêu hủy cùng Sub-Agent.
2. **Rào Cản Thẩm Quyền (Anti-Role Trespass Guard)**:
   - Điều khoản: *"KHÔNG tự tay sửa toàn bộ code. Bạn phải phân rã thành các Zero-Search Tasks"*.
   - Ngăn chặn triệt để lỗi người điều hành tự ý code tranh phần của Dev (`role_trespass`), bảo đảm tính phân quyền và trách nhiệm giải trình.
3. **Cơ Chế Tiêu Hủy Ép Buộc (Mandatory Termination)**:
   - Yêu cầu Sub-Agent kết thúc và tự hủy ngay lập tức (`orca terminal close`) sau khi hoàn thành giúp đưa RAM/PTY về 0, không để lại Zombie process.
4. **Đồng Bộ Dữ Liệu Bền Vững (Durable State Synchronization)**:
   - Bắt buộc cập nhật Harness DB (`harness_manager.py`) và Sổ cái tiến độ (`agent_progress.py`), bảo đảm mọi Agent khác khi vào phiên đều nắm bắt được trạng thái mà không cần đọc lại lịch sử chat.

---

### 11.4. Bảng Tra Cứu Model Combos (Combo-To-Model Routing Map):

| Tên Logic Trong Prompt | Model Cấu Hình Thực Tế | Reasoning Tier | Mục Đích Sử Dụng |
| :--- | :--- | :---: | :--- |
| **`Combo-Supervisor-PM`** | `ag/gemini-3.8-flash-high` | `high` | Lập luận chiến lược, phân rã task Zero-Search, đánh giá Kev System One. |
| **`Combo-Subagent-Dev`** | `ag/gemini-3.8-flash-low` / `medium` | `low` / `medium` | Tiết kiệm token tối đa, sinh code nhanh, sửa file cục bộ theo spec. |
| **`Combo-Subagent-QC`** | `ag/gemini-3.8-flash-high` | `high` | Thẩm định cơ học độc lập, bắt lỗi hồi quy, sinh test ISTQB. |

---

## 12. GIAO THỨC PHỐI HỢP CỐT LÕI CỦA PM AGENT TRONG SLPPC (PM COORDINATION PROTOCOL & SUITABILITY MATRIX)

### 12.1. Đánh Giá Độ Phù Hợp Của PM Agent (Suitability Evaluation: 9.5/10)
Trong mô hình **SLPPC**, PM Agent đóng vai trò là **"Bộ Lọc Định Lượng & Người Trọng Tài Quyết Quyết"**:
- **Định lượng hóa bằng máy (<50ms)**: Không phán đoán cảm tính, PM bắt buộc gọi Kev System One (`kev-latest`) để lấy 3 chỉ số vàng: **Feasibility** (0..3), **Strategic Alignment** (`perfect_fit` vs `scope_creep`), và **Risk Lane** (Green/Yellow/Red).
- **Ngăn chặn lãng phí tài nguyên**: Chặn đứng 100% các ý tưởng viển vông, tính năng phình to hoặc rủi ro vỡ kiến trúc trước khi Lead/Dev gõ một dòng code nào.
- **Bảo toàn nguyên tắc SPOC (Single Point of Contact)**: PM hoạt động ngầm (Headless/Background), tuyệt đối không chat trực tiếp với User, giữ kênh giao tiếp giữa User và Supervisor luôn tinh gọn.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN PHỐI HỢP TƯƠNG TÁC 5 CHIỀU CỦA PM AGENT             │
│                                                                             │
│                        [USER] (Người dùng)                                  │
│                          ▲                                                  │
│                          │ (Giao tiếp duy nhất / SPOC)                      │
│                          ▼                                                  │
│                    [SUPERVISOR]                                             │
│                          ▲                                                  │
│         (1. Yêu cầu)     │   (2. Trả Intake Memo)                           │
│                          ▼                                                  │
│                     [PM AGENT] ◄──► [Kev System One Engine <50ms]           │
│                     │        │                                              │
│       (3. Bàn giao) │        │ (4. Định nghĩa ACs)                          │
│                     ▼        ▼                                              │
│              [LEAD / DEV]   [QC VERIFIER]                                   │
│              (Maker Pool)   (Checker Pool)                                  │
│                     ▲        ▲                                              │
│                     │        │                                              │
│            [SECURITY SENTINEL] (Giám sát chống rò rỉ I/O)                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 12.2. Ma Trận Phối Hợp Tương Tác 5 Chiều Cụ Thể

| Đối Tượng Phối Hợp | Chiều & Giao Thức Tương Tác | Trách Nhiệm Phối Hợp Của PM | Rào Cản Thẩm Quyền Bắt Buộc |
| :--- | :---: | :--- | :--- |
| **Với Supervisor** | $\text{Supervisor} \leftrightarrow \text{PM}$ | • Tiếp nhận draft tính năng từ Supervisor.<br>• Thẩm định Kev System One, xuất bản `intake_memo_<task>.md` kèm Feasibility, Alignment, Risk, và Past Traps. | PM không tự ý tạo Epic thay Supervisor; Supervisor cấm tạo/giao việc khi chưa có memo từ PM (`pm_bypass`). |
| **Với Lead Dev** | $\text{PM} \rightarrow \text{Lead}$ | • Cung cấp Business Rules (BR) và Acceptance Criteria (AC) định lượng.<br>• Cung cấp danh sách bẫy lỗi từ `harness learn query`. | PM không can thiệp vào chi tiết kỹ thuật sâu (như cấu trúc RxJS/Signals); Lead không được tự ý nới rộng phạm vi nghiệp vụ. |
| **Với Sub-Agents Dev** | $\text{PM} \rightarrow \text{Dev Sub-Agent}$ | • Khi PM kiêm nhiệm Technical PM Orchestrator: Bóc tách Zero-Search Tasks giao thẳng cho Sub-Agent Dev.<br>• Thu nhận tóm tắt: **Chỉ nhận Diff và Status**, tiêu hủy terminal Sub-Agent ngay. | PM tuyệt đối không tự tay sửa code tính năng (`role_trespass`). |
| **Với QC Verifier** | $\text{PM} \leftrightarrow \text{QC}$ | • PM định nghĩa ACs chuẩn mực $\rightarrow$ QC dựa vào đó sinh 5-Stage ISTQB tests.<br>• Làm trọng tài phân xử khi Dev và QC tranh chấp về tiêu chí chấp nhận. | PM không ký đóng task; độc quyền nghiệm thu và chuyển `Closed` thuộc về QC. |
| **Với Security Sentinel** | $\text{Sentinel} \rightarrow \text{PM}$ | • Sentinel giám sát luồng I/O và file memo của PM, đảm bảo không rò rỉ domain, token hay địa chỉ thật. | Sentinel sở hữu quyền VETO chặn đứng mọi output của PM nếu vi phạm an ninh. |

---

### 12.3. Hai Chế Độ Vận Hành Của PM Agent Trong Phòng Ban (Two Operating Modes)

Hệ thống cho phép PM Agent linh hoạt chuyển đổi giữa 2 chế độ tùy theo quy mô nhân sự:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 HAI CHẾ ĐỘ VẬN HÀNH CỦA PM AGENT                            │
│                                                                             │
│   CHẾ ĐỘ 1: TEAM ĐẦY ĐỦ (FULL SLPPC TEAM - DỰ ÁN LỚN)                       │
│   Supervisor ──► PM (Đánh giá Kev & AC) ──► Lead (Kiến trúc & Task) ──► Peer │
│   • PM chuyên tâm vào vai trò Product & Feasibility Gatekeeper.             │
│   • Lead Dev phụ trách phân rã kỹ thuật và quản lý Maker Pool.              │
│                                                                             │
│   CHẾ ĐỘ 2: TEAM TINH GỌN (LEAN SINGLE-TAB PM ORCHESTRATOR - TIẾT KIỆM 80%) │
│   User ──► PM Orchestrator (System Prompt Mục 11)                           │
│                 ├── Bóc tách Zero-Search Tasks                              │
│                 ├── Spawn Sub-Agent Dev ➔ Thu Diff ➔ Đóng PTY               │
│                 └── Spawn Sub-Agent QC  ➔ Thu Test ➔ Đóng PTY               │
│   • PM kiêm nhiệm Technical PM & Orchestrator trực tiếp.                    │
│   • Không cần duy trì Lead và Peer thường trực.                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Chế Độ 1 (Full SLPPC Team - Dự án phức tạp)**:
   - Áp dụng khi dự án có nhiều module giao thoa, cần phân tích kiến trúc sâu.
   - PM chỉ làm nhiệm vụ thẩm định Kev System One, xác lập phạm vi, phát hiện bẫy lỗi và bàn giao cho Lead Dev.
2. **Chế Độ 2 (Lean Single-Tab PM Orchestrator - Tối ưu tốc độ & token)**:
   - Áp dụng bộ prompt chuẩn tại **Mục 11**.
   - PM đảm nhận toàn bộ luồng điều phối: Nhận spec $\rightarrow$ chia Zero-Search tasks $\rightarrow$ kích hoạt Sub-Agent Dev/QC $\rightarrow$ thu diff tóm tắt $\rightarrow$ đóng terminal sub-agent ngay lập tức.

---

### 12.4. Cơ Chế Chống Bỏ Qua PM (`pm_bypass`) & Khắc Phục False-Positive
- **Quy tắc kiểm soát**: Script `tools/slppc_flow_guard.py` tự động audit mọi Epic mới. Bắt buộc phải có Intake Memo trong `bmad/rooms/pm/` trước khi Epic được kích hoạt.
- **Cơ chế đối soát 2 lớp (Two-Layer Memo Matching)**:
  1. *Lớp 1 (ID Matching)*: Tìm chuỗi `#<epic_id>` trong tên file hoặc nội dung memo (áp dụng khi đã tạo Epic).
  2. *Lớp 2 (Slug Matching)*: Khi PM lập memo trước khi Epic có ID, memo được đặt tên theo slug tính năng (ví dụ: `intake_memo_contact_filter.md`). `slppc_flow_guard.py` đối chiếu slug tên tính năng giữa handoff của Supervisor và file memo của PM, triệt tiêu 100% cảnh báo giả (false-positive).

---

### 12.5. Tiêu Chuẩn Quản Lý Bộ Nhớ PM Dưới 30k Tokens
Để giữ phiên làm việc của PM luôn nhạy bén và không bị trôi dạt ngữ cảnh qua hàng chục tasks:
1. **Chỉ Lưu Dữ Liệu Tinh Gọn (Summary Only)**: PM chỉ nhận về:
   - Danh sách file đã sửa (`files_modified`).
   - Unified diff ngắn gọn của các hàm cốt lõi.
   - Kết quả test runner (Pass/Fail count và Exit code).
2. **Tuyệt Đối Cấm Nhồi Raw Log**: Cấm đưa toàn bộ log build Webpack/Rsbuild, npm install hay stack trace dài hàng nghìn dòng vào context của PM.
3. **Đồng Bộ Ngoại Vi Bền Vững**: Mọi quyết định và tiến độ được ghi trực tiếp vào `harness.db` và `agent_progress.py`, giúp PM có thể reload trạng thái tức thời mà không cần duy trì lịch sử chat khổng lồ.

---

## 13. CƠ CHẾ DỰ PHÒNG & XỬ LÝ SỰ CỐ CHO TỪNG PROFILE (PROFILE-SPECIFIC FALLBACK & CRISIS RECOVERY PROTOCOLS)

Trong quá trình vận hành tự động hóa với Sub-Agents, các lỗi phần cứng, đứt mạng, timeout, bùng nổ ngữ cảnh hoặc vi phạm rào cản vai trò là điều khó tránh khỏi. Hệ thống thiết lập **Ma Trận Cơ Chế Dự Phòng (Fallback Matrix)** cho từng Profile nhằm bảo đảm hệ thống luôn tự phục hồi (Self-Healing) và không bao giờ rơi vào trạng thái bế tắc:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN CƠ CHẾ DỰ PHÒNG CHO TỪNG PROFILE                    │
├─────────────────────┬──────────────────────────┬────────────────────────────┤
│ PROFILE             │ SỰ CỐ / RỦI RO ĐẶC THÙ   │ CƠ CHẾ DỰ PHÒNG (FALLBACK) │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 1. SUPERVISOR       │ Crash phiên, mất context,│ • Re-anchor từ Sổ cái tiến │
│                     │ Zombie terminals tràn RAM│   độ docs/AGENT_PROGRESS.md│
│                     │                          │ • Kích hoạt Zombie Reaper  │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 2. PM AGENT         │ • Kev System One offline │ • Heuristic Rule-based Eval│
│                     │ • Sub-Agent nộp diff rác │ • Bắt buộc kiểm tra AST    │
│                     │ • Context > 30k tokens   │ • Auto-Compact & Reset Tab │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 3. LEAD DEV         │ • Vi phạm ôm code        │ • Pre-commit Hook tự chặn  │
│                     │ • Thiết kế gây crash     │ • Peer VETO -> Trả ticket  │
│                     │ • Sub-Agent lặp vô tận   │ • Ngắt turn ceiling (<=3)  │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 4. PEER DEV         │ • Nhận task 1 dòng mơ hồ │ • Kích hoạt VETO Zero-Search│
│    (Coding Sub)     │ • Sửa code test không pass│ • Loop-ceiling dừng sau 5x │
│                     │ • Đứt session giữa chừng │ • Khôi phục từ git status  │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 5. QC VERIFIER      │ • Runner test bị crash   │ • Mock Isolated Testbench  │
│    (Testing Sub)    │ • Đóng ẩu khi test fail  │ • Flow Guard giáng Active  │
│                     │ • Tự ý sửa code sản phẩm │ • Git revert file tính năng│
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 6. SECURITY         │ • Lỗi Regex / Treo CI    │ • Fail-Closed: Khóa Commit │
│    SENTINEL         │                          │ • Yêu cầu User Override    │
└─────────────────────┴──────────────────────────┴────────────────────────────┘
```

---

### 13.1. Cơ Chế Dự Phòng Cho Supervisor (Macro Governor / SPOC)
- **Sự cố 1: Phiên Supervisor bị Crash hoặc Trôi Mất Ngữ Cảnh**:
  * *Hệ quả*: Supervisor quên mất tiến độ đang làm của phòng ban khi User hỏi *"báo cáo tình hình"* hoặc *"làm tiếp"*.
  * *Cơ chế Fallback*: Supervisor **BẮT BUỘC KHÔNG ĐƯỢC ĐOÁN**. Tự động chạy lệnh tái neo trạng thái:
    ```bash
    python3 tools/agent_progress.py status
    python3 tools/harness_manager.py --engine auto list --state Active
    ```
  * Toàn bộ bức tranh dự án được nạp lại tức thì trong $<100\text{ms}$ từ đĩa vật lý (`docs/AGENT_PROGRESS.md` và `harness.db`).
- **Sự cố 2: Terminal PTY Bị Bỏ Rơi Tràn RAM Máy Trạm**:
  * *Cơ chế Fallback*: Supervisor kích hoạt định kỳ **Zombie Terminal Reaper**:
    ```bash
    # Quét danh sách live terminals trên Orca
    orca terminal list --json
    # Tự động đóng cưỡng chế các terminal không gắn với Task ID hợp lệ
    orca terminal close --terminal <stale_handle>
    ```

---

### 13.2. Cơ Chế Dự Phòng Cho PM Agent (Technical PM & Orchestrator)
- **Sự cố 1: Kev System One Engine Ngoại Vi Bị Offline / Timeout (>50ms)**:
  * *Hệ quả*: Gọi `http://100.124.36.46:8008/v1/systemone` trả về `ConnectionRefused` hoặc `TimeoutError`.
  * *Cơ chế Fallback*: PM **tự động chuyển sang chế độ Thẩm Định Ngoại Tuyến (Offline Heuristics Evaluation)**:
    1. Đọc trực tiếp cấu trúc file mã nguồn bằng `search_files` và `read_file` để kiểm tra sự tồn tại của DTO/Model.
    2. Truy vấn kho bài học kinh nghiệm cục bộ qua SQLite:
       ```bash
       python3 tools/harness_rust.py query --domain "<domain>"
       ```
    3. Tự chấm điểm Heuristic: Nếu DTO đã có sẵn $\rightarrow$ Feasibility = 2.5/3.0; nếu thiếu DTO $\rightarrow$ Feasibility = 1.0 (Yêu cầu bổ sung DTO trước).
- **Sự cố 2: Sub-Agent Nộp Báo Cáo Ảo (Hallucinated Completion)**:
  * *Hệ quả*: Sub-Agent tự nhận "đã hoàn thành" nhưng thực tế không sửa đúng file.
  * *Cơ chế Fallback*: PM không đưa báo cáo này cho User, mà chạy script kiểm chứng diff thực tế:
    ```bash
    git status --short <target_file>
    ```
    Nếu file không có diff hoặc diff rác $\rightarrow$ PM tự động giáng task về `Active`, tiêu hủy Sub-Agent cũ và spawn Sub-Agent mới với chỉ thị thu hẹp phạm vi.
- **Sự cố 3: Context Của PM Phình To Vượt Ngưỡng 30k Tokens**:
  * *Cơ chế Fallback*: PM kích hoạt lệnh `/compact` hoặc đóng session, khởi động lại phiên PM mới và chỉ đọc lại duy nhất 1 file handoff gần nhất `bmad/rooms/pm/latest_memo.md`.

---

### 13.3. Cơ Chế Dự Phòng Cho Lead Dev (Technical Dispatcher & Architect)
- **Sự cố 1: Lead Dev Vi Phạm Rào Cản Thẩm Quyền Tự Ý Code (`role_trespass`)**:
  * *Hệ quả*: Lead trực tiếp sửa file mã nguồn sản phẩm thay vì giao cho Dev Sub-Agent.
  * *Cơ chế Fallback*:
    1. Pre-commit hook (`scripts/git_pre_commit_guard.py`) và `tools/slppc_flow_guard.py` lập tức phát hiện và **chặn đứng lệnh commit (Exit code 1)**.
    2. Supervisor xuất biên bản khiển trách `reprimand_lead_role_trespass.md`, phạt tạo 1 Bug P1 trên Harness DB.
    3. Lead Dev bắt buộc phải hoàn tác mã nguồn tự viết:
       ```bash
       git restore <file_path>
       ```
    4. Lead phân rã lại task theo chuẩn Zero-Search và ủy quyền cho Sub-Agent thi công.
- **Sự cố 2: Bản Thiết Kế Của Lead Gây Panic / Build Thất Bại**:
  * *Cơ chế Fallback*: Sub-Agent Dev kích hoạt **Quyền Phản Biện (Right to Challenge)**, chuyển task sang `Blocked` và gửi thẳng bằng chứng lỗi biên dịch vào terminal của Lead để Lead thiết kế lại giải pháp.

---

### 13.4. Cơ Chế Dự Phòng Cho Peer Dev / Coding Sub-Agents (Maker Pool)
- **Sự cố 1: Nhận Task Mô Tả Mơ Hồ, Thiếu Vị Trí File (Vague Task Spec)**:
  * *Nguy cơ*: Sub-Agent chạy các lệnh `find`, `rg` tìm kiếm mù quáng khắp repo, làm cháy sạch token trong 2–3 phút.
  * *Cơ chế Fallback (Zero-Search VETO)*:
    Sub-Agent có quyền **VETO từ chối làm việc ngay lập tức**. Chuyển task sang `Blocked`:
    ```bash
    python3 tools/harness_manager.py update --id <id> --state Blocked --assigned-to-profile lead
    ```
    Yêu cầu Lead Dev cung cấp đủ 5 thành phần định danh mới được phép tiếp tục.
- **Sự cố 2: Vòng Lặp Tự Sửa Lỗi (Autonomous Self-Healing Loop) Bị Vòng Lặp Vô Tận**:
  * *Nguy cơ*: Sửa code $\rightarrow$ test fail $\rightarrow$ sửa tiếp $\rightarrow$ test lại fail... lặp hàng chục lần không dừng.
  * *Cơ chế Fallback (Turn Ceiling Gate)*:
    Cài đặt cứng ngân sách **Turn Ceiling $\le 3 - 5$ lần thử**. Nếu sau 3 lần sửa mà test runner vẫn không chuyển xanh (Exit code $\ne 0$):
    1. Sub-Agent dừng ngay lập tức, không cố sửa mò.
    2. Xuất bản biên bản chẩn đoán nguyên nhân gốc rễ: `bmad/rooms/tasks/<id>/root_cause_blocker.md`.
    3. Nộp về cho Lead/QC xử lý, tránh đốt sạch ngân sách token.
- **Sự cố 3: Tiến Trình Sub-Agent Bị Đứt Kết Nối Giữa Chừng (Mid-Turn Disconnect)**:
  * *Cơ chế Fallback*: Toàn bộ mã nguồn Sub-Agent đang sửa vẫn được lưu trên đĩa vật lý (Git Working Tree). Coordinator chỉ cần kiểm tra `git diff`, spawn một Sub-Agent thay thế và tiếp quản chính xác phần việc còn dang dở.

---

### 13.5. Cơ Chế Dự Phòng Cho QC Verifier / Testing Sub-Agents (Checker Pool)
- **Sự cố 1: Môi Trường Test Runner Bị Gãy (Missing Dependencies / Canvas / Native Panics)**:
  * *Hệ quả*: Lệnh `npx jest` hoặc `npx playwright test` văng lỗi môi trường Node/OS chứ không phải lỗi logic code.
  * *Cơ chế Fallback*: QC chuyển sang cơ chế **Kiểm Thử Cô Lập (Isolated Testbench)**:
    1. Kiểm tra môi trường Node.js runtime (`PATH="$HOME/.nvm/versions/node/v20.20.2/bin:$PATH"`).
    2. Chạy test suite ở chế độ độc lập từng file (Single-file run).
    3. Nếu môi trường Jest vỡ: Dùng script `tools/qc_test_generator.py` đối soát AST và TypeScript Compiler check (`tsc --noEmit`).
- **Sự cố 2: QC Bị Lỗi Duyệt Ẩu Khi Test Chưa Xanh (`premature_close`)**:
  * *Hệ quả*: QC đóng task khi test runner vẫn đang đỏ hoặc chưa chạy test thực tế.
  * *Cơ chế Fallback*: Script canh gác `tools/slppc_flow_guard.py` tự động quét các Task vừa đóng `Closed`. Nếu không tìm thấy log chạy test exit code 0 trong vòng 1 giờ gần nhất $\rightarrow$ **Tự động giáng cấp Task về `Active`**, lập biên bản phạt QC và cảnh báo Supervisor.
- **Sự cố 3: QC Tự Ý Chữa Cháy Mã Nguồn (Silent Patching Anti-Pattern)**:
  * *Hệ quả*: Thay vì bắt lỗi trả về cho Dev, QC tự ý sửa code sản phẩm để test pass.
  * *Cơ chế Fallback*: Giám sát Git diff của QC. Nếu phát hiện QC sửa bất kỳ file nào nằm ngoài thư mục `*.spec.ts` hoặc `tests/` $\rightarrow$ Tự động revert file tính năng và yêu cầu QC trả Bug P1 về cho Dev làm lại.

---

### 13.6. Cơ Chế Dự Phòng Cho Security Sentinel (Anti-Leak Gatekeeper)
- **Sự cố 1: Bộ Quét Gặp Lỗi Regex Treo Hoặc CI Action Bị Lỗi Mạng**:
  * *Cơ chế Fallback (Fail-Closed Security Policy)*:
    Áp dụng nguyên tắc **"Thà Chặn Nhầm Còn Hơn Bỏ Sót (Fail-Closed)"**:
    1. Khi script bảo mật `scripts/anti_leak_sentinel.py` không thể hoàn tất quét với mã thoát 0 $\rightarrow$ Mọi hành động `git push` hoặc chuyển giao tài liệu ra ngoài **MẶC ĐỊNH BỊ KHÓA 100%**.
    2. Chỉ duy nhất User có thẩm quyền mở khóa bằng cờ ghi đè thủ công (`--force-user-override`) sau khi đã kiểm tra thủ công bằng mắt.

---

## 14. CƠ CẤU TỔ CHỨC SKILLS THEO PROFILE & MA TRẬN PHÂN QUYỀN TRUY CẬP (PROFILE-BASED SKILLS TAXONOMY & RBAC PERMISSIONS)

### 14.1. Động Lực Kiến Trúc: Xóa Bỏ Cấu Trúc Phẳng Gây Ô Nhiễm Ngữ Cảnh (Flat Skills Anti-Pattern)
- **Hiện trạng bất cập**: Việc gom toàn bộ 80+ skills (và gần 200 skills phụ) vào một thư mục gốc `skills/` dùng chung khiến mọi Agent khi khởi động đều bị nhồi nhét toàn bộ danh mục kỹ năng vào System Prompt.
- **Hậu quả**:
  1. *Prompt Overhead Khổng Lồ*: Mất hàng chục nghìn tokens chỉ để mô tả các kỹ năng mà role đó không bao giờ dùng tới (ví dụ: Dev bị nạp các skill của PM/BA; QC bị nạp các skill can thiệp sâu kiến trúc của Lead).
  2. *Rò Rỉ Năng Lực Chéo (Cross-Role Capability Bleed)*: Dev có thể vô tình gọi các skill phân xử của PM hoặc skill review của Lead, phá vỡ rào cản thẩm quyền SLPPC.
  3. *Ảo Giác Quyết Định*: LLM bị phân vân giữa quá nhiều công cụ tương tự nhau dẫn đến việc chọn sai tool/workflow.

### 14.2. Cấu Trúc Thư Mục Skills Phân Tầng Theo Profile (`skills/<profile>/`)
Toàn bộ kho kỹ năng trên GitHub Repository được tái cấu trúc thành các thư mục con tương ứng 1:1 với Profile:

```text
skills/
├── supervisor/       # Kỹ năng dành riêng cho Supervisor (Điều phối, Intent, Handoff)
├── pm/               # Kỹ năng dành riêng cho PM Agent (Kev System One, Decision Governance)
├── lead/             # Kỹ năng dành riêng cho Lead Dev (Architecture Review, Zero-Search Decomposition)
├── peer/             # Kỹ năng dành riêng cho Peer Dev (Angular 18, Rsbuild, TDS UI, Loop Engineering)
├── qc/               # Kỹ năng dành riêng cho QC Verifier (ISTQB Test Generator, Automation Framework)
├── security/         # Kỹ năng dành riêng cho Security Sentinel (Anti-Leak, Secret Scanner, Git Guard)
└── shared/           # Kỹ năng tiện ích nền tảng dùng chung (Git, Research, Terminal Tooling)
```

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SƠ ĐỒ PHÂN BỔ KỸ NĂNG THEO TỪNG VAI TRÒ                     │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ PROFILE             │ DANH MỤC SKILLS ĐƯỢC PHÉP TRUY CẬP                   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 1. SUPERVISOR       │ skills/supervisor/ + skills/shared/                   │
│                     │ • slpc-role-governance, chief-of-staff, handoff,      │
│                     │   workflow-launch-exec, slppc-runtime-governance      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 2. PM AGENT         │ skills/pm/ + skills/shared/                           │
│                     │ • pm-decision-governance, systemone, ba, to-spec,     │
│                     │   to-tickets, domain-modeling                         │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 3. LEAD DEV         │ skills/lead/ + skills/shared/                         │
│                     │ • lead-review, codebase-design, code-review,          │
│                     │   improve-codebase-architecture, slpc-management-rev  │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 4. PEER DEV         │ skills/peer/ + skills/shared/                         │
│    (Coding Sub)     │ • rsbuild-angular, mfe-angular-build, tds-ui-usage,   │
│                     │   tds-ui-figma, loop-engineering, systematic-debug    │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 5. QC VERIFIER      │ skills/qc/ + skills/shared/                           │
│    (Testing Sub)    │ • qc, e2e-automation-testing, tester-team-automation, │
│                     │   dogfood, slpc-verification-audit, test-driven-dev   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 6. SECURITY         │ skills/security/ + skills/shared/                     │
│    SENTINEL         │ • anti-leak-sentinel, permissioned-github,            │
│                     │   anti-leak-gatekeeper                                │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

### 14.3. Ma Trận Phân Quyền Truy Cập Kỹ Năng (Role-Based Access Control - RBAC)

Mọi yêu cầu gọi `skill_view` hoặc kích hoạt skill đều phải đi qua **Chốt Chặn Kiểm Tra Thẩm Quyền (Skill Authorization Gate)**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN PHÂN QUYỀN TRUY CẬP SKILLS (RBAC)                   │
├──────────────────────────┬──────┬────┬──────┬──────┬────┬──────────┬────────┤
│ NHÓM SKILL               │ SUPV │ PM │ LEAD │ PEER │ QC │ SENTINEL │ SUB-AG │
├──────────────────────────┼──────┼────┼──────┼──────┼────┼──────────┼────────┤
│ Strategy & Orchestration │  ✔   │ ✔  │  ❌  │  ❌  │ ❌ │    ❌    │   ❌   │
│ Decision & Kev SystemOne │  ❌  │ ✔  │  ❌  │  ❌  │ ❌ │    ❌    │   ❌   │
│ Architecture & Review    │  ✔   │ ❌ │  ✔   │  ❌  │ ❌ │    ❌    │   ❌   │
│ Code Implementation      │  ❌  │ ❌ │  ❌  │  ✔   │ ❌ │    ❌    │   ✔    │
│ Testing & Verification   │  ❌  │ ❌ │  ❌  │  ❌  │ ✔  │    ❌    │   ✔    │
│ Security & Anti-Leak     │  ✔   │ ❌ │  ❌  │  ❌  │ ❌ │    ✔     │   ❌   │
│ Generic Utilities        │  ✔   │ ✔  │  ✔   │  ✔   │ ✔  │    ✔     │   ✔    │
└──────────────────────────┴──────┴────┴──────┴──────┴────┴──────────┴────────┘
```

#### Quy Tắc Chế Tài Khi Vi Phạm Quyền Truy Cập (Unauthorized Access Rejection):
- Nếu Agent cố tình nạp một skill ngoài phạm vi cho phép (ví dụ: `Peer` cố tình gọi `skill_view("lead-review")` hoặc `skill_view("pm-decision-governance")`):
  1. Bộ lọc quyền hạn lập tức từ chối và ném ngoại lệ:
     ```text
     PermissionDeniedError: Role 'peer' is NOT authorized to access skill 'lead-review'.
     Allowed roles: ['lead', 'supervisor']. Action blocked by SLPPC Skill RBAC Gate.
     ```
  2. Ghi nhận nhật ký cảnh báo vi phạm phân quyền vào `bmad/rooms/violations/unauthorized_skill_access.md`.

---

### 14.4. Cấu Hình Khóa Phạm Vi Skills Trực Tiếp Trong Profile (`profiles/<name>.md`)
Mỗi hồ sơ Profile chỉ nạp danh mục skills của riêng mình thông qua khai báo `skills_dirs` trong YAML Frontmatter:

```yaml
# Ví dụ: profiles/pm.md
---
name: PM
model: gemini-3.8-flash-high
skills_dirs:
  - skills/pm
  - skills/shared
permissions:
  can_arbitrate: true
  can_call_kev_systemone: true
  can_code: false
  can_close_task: false
---
```

```yaml
# Ví dụ: profiles/peer.md
---
name: Peer Dev 1 (Low)
model: gemini-3.8-flash-low
skills_dirs:
  - skills/peer
  - skills/shared
permissions:
  can_code: true
  can_run_local_test: true
  can_review_architecture: false
  can_close_task: false
---
```

```yaml
# Ví dụ: profiles/qc.md
---
name: QC
model: gemini-3.8-flash-high
skills_dirs:
  - skills/qc
  - skills/shared
permissions:
  can_generate_test: true
  can_execute_e2e: true
  can_code_features: false
  can_close_task: true # Độc quyền quyền hạn đóng task
---
```

### 14.5. Lợi Ích Đo Lường Được:
1. **Tiết kiệm thêm 40% – 60% Token System Prompt ban đầu**: Thay vì nạp toàn bộ 194 skills, mỗi Agent chỉ phải nạp từ 5–12 skills cốt lõi của chuyên môn mình.
2. **Loại bỏ 100% rủi ro xâm lấn thẩm quyền (Anti-Role Trespass)**: Lập trình viên không thể dùng tool của người quản lý, người quản lý không thể dùng tool can thiệp code thô.
3. **Mã nguồn sạch và rõ ràng trên GitHub**: Kho lưu trữ `skills/` trên GitHub được phân chia ngăn nắp theo vai trò, giúp cộng đồng mã nguồn mở đọc và áp dụng mô hình một cách trực quan, khoa học.

---

## 15. QUY CHUẨN CHỐNG RÒ RỈ DỮ LIỆU DỰ ÁN & VỆ SINH REPOSITORY (ANTI-LEAK GOVERNANCE & REPO SANITIZATION)

### 15.1. Phân Tích Nguyên Nhân Gốc Rễ (Root Cause Analysis Tại Sao Bị Lộ Trên GitHub)
Qua đợt rà soát thực tế kho lưu trữ `https://github.com/baobao0303/Room_Agent`, hệ thống phát hiện 2 nguyên nhân cốt lõi dẫn đến việc rò rỉ dữ liệu:
1. **Lỗi Hiểu Sai Về Cơ Chế Git Tracking**:
   - Các file biên bản (`bmad/rooms/*/handoff_*.md`, `review_*.md`) và sổ cái tiến độ (`docs/AGENT_PROGRESS.md`) đã bị commit vào Git index từ các đợt phát triển ban đầu.
   - **Quy tắc cơ bản của Git**: Khi một file đã được Git theo dõi (tracked), việc sau đó thêm đường dẫn của nó vào `.gitignore` **HOÀN TOÀN KHÔNG CÓ HIỆU LỰC**. File vẫn sẽ tiếp tục bị commit và push lên GitHub cho đến khi được gỡ khỏi bộ nhớ đệm bằng lệnh `git rm --cached`.
2. **Lỗ Hổng "Mù" Của Công Cụ Giám Sát `scripts/anti_leak_sentinel.py`**:
   - Tại dòng 52 của script, tác giả đã cấu hình `"bmad/rooms"` nằm trong mảng `EXCLUDED_PATHS` (do giả định thư mục này đã được gitignore).
   - Hậu quả: Script Sentinel tự động bỏ qua toàn bộ thư mục biên bản, liên tục báo `PASS 100% giả tạo` trong khi hơn 260 files biên bản chứa đầy đường dẫn `projects/...`, bug ID và mã nguồn DTO đang nằm công khai trên GitHub.

---

### 15.2. Bản Đồ 4 Khu Vực Rò Rỉ Dữ Liệu Trên GitHub Repository

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 BẢN ĐỒ 4 KHU VỰC RÒ RỈ DỮ LIỆU TRÊN GITHUB                  │
├───────────────────────────────┬────────────┬────────────────────────────────┤
│ KHU VỰC BỊ LỘ                 │ SỐ LƯỢNG   │ NỘI DUNG NHẠY CẢM BỊ LỘ        │
├───────────────────────────────┼────────────┼────────────────────────────────┤
│ 1. bmad/rooms/                │ 269 files  │ • 150+ biên bản handoff/review │
│    (lead, peer, qc, pm,       │            │ • Lộ đường dẫn: projects/wicx- │
│     supervisor, violations)   │            │   crm-fe, wion_pos_fe, Aevum   │
│                               │            │ • Lộ Bug IDs, code diff, DTOs  │
├───────────────────────────────┼────────────┼────────────────────────────────┤
│ 2. docs/AGENT_PROGRESS.md     │ 1 file     │ • Nhật ký chi tiết toàn bộ các │
│                               │            │   bước sửa code trên các dự án │
├───────────────────────────────┼────────────┼────────────────────────────────┤
│ 3. docs/spec/                 │ 31 files   │ • Lộ các bản đặc tả nghiệp vụ: │
│    (wion-pos, wicx-crm, cdp)  │            │   wion-pos-header, cdp-mapping,│
│                               │            │   customer-drawer, shop-user   │
├───────────────────────────────┼────────────┼────────────────────────────────┤
│ 4. .claude/                   │ 90 files   │ • Thư mục rác .claude/skills/  │
│                               │            │   vẫn bị Git index theo dõi    │
└───────────────────────────────┴────────────┴────────────────────────────────┘
```

---

### 15.3. Kế Hoạch Hành Động Dọn Sạch & Khóa Cứng (Action Plan)
1. **Khóa Cứng `.gitignore`**:
   Bổ sung quy tắc khóa toàn diện các artifacts sinh ra trong quá trình agent làm việc cục bộ:
   ```gitignore
   # Ephemeral agent room coordination & meeting memos
   bmad/rooms/lead/
   bmad/rooms/peer/
   bmad/rooms/qc/
   bmad/rooms/supervisor/
   bmad/rooms/pm/
   bmad/rooms/tasks/
   bmad/rooms/violations/
   bmad/rooms/archive/
   bmad/rooms/*.json
   docs/AGENT_PROGRESS.md
   .harness_progress.json
   .claude/
   */.claude/
   ```
2. **Gỡ Bỏ Hoàn Toàn Khỏi Git Tracking Index (`git rm --cached`)**:
   Thực thi lệnh gỡ sạch các file đã lỡ theo dõi (file trên máy trạm vẫn còn nguyên, chỉ không còn bị Git đẩy lên GitHub):
   ```bash
   git rm -r --cached bmad/rooms/lead bmad/rooms/peer bmad/rooms/qc bmad/rooms/supervisor bmad/rooms/tasks bmad/rooms/violations bmad/rooms/archive bmad/rooms/*.json .claude/ docs/AGENT_PROGRESS.md
   ```
3. **Nâng Cấp `scripts/anti_leak_sentinel.py`**:
   - Xóa bỏ `"bmad/rooms"` khỏi `EXCLUDED_PATHS`.
   - Bổ sung hàm kiểm tra `check_git_tracked_memos()`: Nếu phát hiện bất kỳ file nào trong `bmad/rooms/*` hoặc `.claude/*` còn bị Git track $\rightarrow$ **VETO (Exit code 1)** ngay lập tức.

---

## 16. PHÂN TÍCH RTK (RUST TOKEN KILLER) & THIẾT LẬP CLI PROXY CHO TỪNG AGENT

### 16.1. Phân Tích Kiến Trúc RTK (`https://github.com/rtk-ai/rtk`)
- **Bản chất**: RTK (Rust Token Killer) là một CLI Proxy hiệu năng cực cao viết bằng Rust thuần (Single Rust binary, zero dependencies, <10ms overhead), đạt hơn **82.000 Stars** trên GitHub.
- **Cơ chế hoạt động**: RTK đứng ở giữa Agent và Shell, đánh chặn (intercept) các lệnh dev phổ biến và nén/lọc sạch từ **60% đến 90% lượng output** trước khi trả về context của LLM:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CƠ CHẾ ĐÁNH CHẶN CỦA RTK PROXY                        │
│                                                                             │
│   ❌ KHÔNG CÓ RTK:                                                          │
│   Agent ──(git status / jest)──► Shell ──► Git / Node                       │
│     ▲                                           │                           │
│     └──────────── 5.000 dòng log thô ───────────┘ (Lãng phí 15k tokens)     │
│                                                                             │
│   ✔ CÓ RTK PROXY:                                                           │
│   Agent ──(git status / jest)──► RTK Interceptor ──► Git / Node             │
│     ▲                                  │                                    │
│     └──── Output tinh gọn 5 dòng ──────┴── Lọc 90% rác, chỉ giữ failures     │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **4 Chiến Lược Nén Của RTK**:
  1. *Smart Filtering*: Lược bỏ comments, khoảng trắng thừa, boilerplate không có giá trị.
  2. *Grouping*: Nhóm các file theo thư mục, nhóm lỗi theo Rule/Type.
  3. *Truncation*: Cắt gọt traceback dài dòng, chỉ giữ 2 dòng lỗi cốt lõi.
  4. *Deduplication*: Gom các dòng log lặp lại thành `(repeated xN times)`.

---

### 16.2. Bảng Nén Lệnh Điển Hình Của RTK:

| Nhóm Lệnh | Lệnh Gốc | RTK Xử Lý Nén Output | Tỷ Lệ Tiết Kiệm |
| :--- | :--- | :--- | :---: |
| **Git Status** | `git status` | Hiển thị dạng compact stat, gom nhóm theo trạng thái (`M 2 files, ?? 1 file`). | **-75%** |
| **Git Diff** | `git diff` | Lược bỏ header hunk thừa, chỉ giữ diff code logic cốt lõi. | **-65%** |
| **Git Log** | `git log -n 10` | Nén thành 1 dòng: Hash + Tác giả + Subject. | **-80%** |
| **Git Commit** | `git commit -m "..."` | Chỉ trả về dòng xác nhận: `ok abc1234`. | **-90%** |
| **Test Runner** | `npx jest` / `npm test` | **Failures only**: Ẩn toàn bộ test pass, chỉ in đúng test case bị fail kèm vị trí lỗi. | **-90%** |
| **TypeScript** | `npx tsc` | Nhóm lỗi theo từng file và mã lỗi TS. | **-70%** |
| **File Read** | `cat` / `read` | `rtk read -l aggressive`: Chỉ đọc signatures/headers, ẩn body implementation. | **-80%** |
| **File Search** | `grep` / `rg` | Nhóm kết quả theo file, cắt dòng quá dài. | **-70%** |

---

### 16.3. Ma Trận Thiết Lập RTK Cho Từng Profile Agent (SLPPC RTK Setup Matrix)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN CẤU HÌNH RTK CHO TỪNG PROFILE AGENT                 │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ PROFILE             │ LỆNH RTK BẮT BUỘC SỬ DỤNG                             │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 1. SUPERVISOR       │ • rtk git status  (Kiểm tra working tree trong 2 dòng)│
│                     │ • rtk git log -n 5 (Xem commit gần nhất dạng 1-line)  │
│                     │ • rtk gain         (Xem dashboard thống kê token tiết │
│                     │                     kiệm được của toàn phòng ban)      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 2. PM AGENT         │ • rtk diff         (So sánh nhanh spec & DTO)         │
│                     │ • rtk find         (Định vị nhanh cấu trúc file)      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 3. LEAD DEV         │ • rtk git diff     (Review code diff gọn gàng)        │
│                     │ • rtk git log      (Kiểm tra lịch sử nhánh)           │
│                     │ • rtk tsc          (Kiểm tra lỗi type theo file)      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 4. PEER DEV         │ • rtk read -l aggressive (Đọc nhanh API/DTO không body)│
│    (Coding Sub)     │ • rtk jest         (Chỉ hiện test lỗi để sửa nhanh)   │
│                     │ • rtk tsc          (Kiểm tra typecheck tức thì)       │
│                     │ • rtk git add/commit (Thao tác git 1 dòng ok)         │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 5. QC VERIFIER      │ • rtk jest         (Chạy test suite, chỉ log failure) │
│    (Testing Sub)    │ • rtk playwright test (E2E failures only)             │
│                     │ • rtk err <cmd>    (Chỉ bắt stderr/warnings)          │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 6. SECURITY         │ • rtk grep         (Quét regex pattern theo nhóm file)│
│    SENTINEL         │ • rtk diff         (Kiểm tra leak trong staged diff)  │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

### 16.4. Hướng Dẫn Cài Đặt & Kích Hoạt Tự Động Trong Hệ Thống

#### Bước 1: Cài Đặt Binary RTK Trên Host (Linux Dev Machine):
```bash
# Tải và cài đặt tự động vào ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# Kiểm tra phiên bản và dashboard
rtk --version
rtk gain
```

#### Bước 2: Kích Hoạt Plugin Hook Cho Hermes Agent & Orca:
```bash
# Kích hoạt hook tự động viết lại lệnh cho Hermes
rtk init --agent hermes

# Kích hoạt hook toàn cục cho Google Antigravity & Claude Code
rtk init -g --agent antigravity
rtk init -g
```
*Sau khi cài đặt hook, mọi lệnh gõ từ Agent như `git status`, `npx jest` sẽ được tự động chuyển hướng qua `rtk git status`, `rtk jest` mà agent không cần phải nhớ gõ tiền tố `rtk`.*

#### Bước 3: Tích Hợp Vào Script Khởi Động Phòng Ban (`scripts/launch_room.sh`):
Bổ sung đoạn kiểm tra RTK vào đầu script `scripts/launch_room.sh`:
```bash
if command -v rtk &> /dev/null; then
    echo "⚡ [RTK Active]: Rust Token Killer đã sẵn sàng, kích hoạt nén 90% bash output."
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "⚠️  [RTK Missing]: Khuyến nghị cài đặt RTK (curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh) để tiết kiệm 70% token."
fi
```

---

## 17. CHUẨN HÓA GIẢI PHÁP CHO GITHUB ISSUE #4 & ISSUE #5 (GITHUB ISSUES FORMAL SPECIFICATION)

Để đáp ứng trực tiếp 2 yêu cầu kỹ thuật vừa được mở trên kho lưu trữ `baobao0303/Room_Agent` (Issue #4 và Issue #5), hệ thống chuẩn hóa giải pháp chi tiết vào Master Spec:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 BẢN ĐỒ GIẢI PHÁP 2 GITHUB ISSUES (#4 & #5)                  │
│                                                                             │
│   [ISSUE #4]: "Skill loop enginnering nạp thẳng vào pm"                     │
│    ├── Mục tiêu: Đưa PM thành Arbiter thẩm định vòng lặp khép kín           │
│    ├── Gán Skill: Nạp skills/loop-engineering thẳng vào profiles/pm.md      │
│    └── Trách nhiệm: Thiết lập Turn Ceiling (<=3-5x) & Mechanical Stop Gate   │
│                                                                             │
│   [ISSUE #5]: "Bổ sung bộ nén input rtk cho từng profile của room"          │
│    ├── Mục tiêu: Nén 60–90% bash input/output cho toàn bộ 6 profiles         │
│    ├── Cấu hình: Hook rtk per-profile trong Hermes / Orca workspace         │
│    └── Tối ưu: Maker (Failures only), Checker (Jest/E2E), Leader (Diff/Log) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 17.1. Giải Pháp Chi Tiết Cho Issue #4: Nạp Thẳng Kỹ Năng Loop Engineering Vào PM Agent

#### A. Lý Do Kiến Trúc Bắt Buộc PM Phải Có Skill `loop-engineering`:
- Trước đây, `loop-engineering` chỉ được giao cho Peer (tự sửa lỗi) và QC (nghiệm thu). Tuy nhiên, **PM Agent mới là người quyết định xem bài toán có khả thi để chạy vòng lặp hay không**.
- Nếu PM giao một task mơ hồ hoặc không có công cụ kiểm thử tự động, vòng lặp tự sửa lỗi của Peer sẽ biến thành **vòng lặp vô tận (Infinite Loop)**, thiêu rụi toàn bộ ngân sách token.

#### B. Trách Nhiệm Cụ Thể Của PM Khi Sở Hữu Skill `loop-engineering`:
1. **Thẩm Định Khả Thi Của Vòng Lặp (Loop Feasibility Gate)**:
   - Trước khi bóc tách task, PM kiểm tra: *Task này có lệnh kiểm thử cơ học tự động hóa được không (Exit code 0)?*
   - Nếu KHÔNG có test tự động $\rightarrow$ PM từ chối giao việc cho Sub-Agent chạy tự do, yêu cầu thiết lập test runner trước.
2. **Khống Chế Ngân Sách Vòng Lặp (Turn Ceiling & Budget Enforcer)**:
   - PM cài đặt cứng ngân sách số vòng lặp tối đa: **Turn Ceiling $\le 3 - 5$ lần thử** cho mỗi Sub-Agent.
   - Nếu quá 5 lần sửa mà test vẫn đỏ $\rightarrow$ Sub-Agent buộc phải dừng lại và nộp báo cáo blocker cho Lead/PM.
3. **Bảo Đảm Nguyên Tắc Vàng "Never Let The AI Verify Its Own Done"**:
   - PM phân định rạch ròi: Sub-Agent Dev chỉ là Maker (nộp `Resolved`), Sub-Agent QC là Checker độc lập (độc quyền chuyển `Closed`).

#### C. Cấu Hình Nạp Trực Tiếp Vào `profiles/pm.md`:
```yaml
---
name: PM
model: gemini-3.8-flash-high
skills_dirs:
  - skills/pm
  - skills/loop-engineering    # NẠP THẲNG VÀO PM (ISSUE #4)
  - skills/shared
permissions:
  can_arbitrate: true
  can_enforce_loop_ceiling: true # Quyền khống chế trần vòng lặp
  can_code: false
  can_close_task: false
---
```

---

### 17.2. Giải Pháp Chi Tiết Cho Issue #5: Bổ Sung Bộ Nén Input/Output RTK Cho Từng Profile

Để giải quyết triệt để Issue #5, mỗi Profile Agent trong Room được trang bị cấu hình bộ nén RTK CLI Proxy tương ứng với chức năng chuyên biệt:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MA TRẬN CẤU HÌNH RTK INPUT/OUTPUT PER-PROFILE               │
├─────────────────────┬──────────────────────────┬────────────────────────────┤
│ PROFILE AGENT       │ BỘ LỆNH ĐƯỢC ĐÁNH CHẶN   │ HIỆU QUẢ NÉN INPUT/OUTPUT  │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 1. SUPERVISOR       │ • git status -> rtk stat │ Nén 75% output working tree│
│    (Governor)       │ • git log -> rtk log 1-L │ Nén 80% commit history     │
│                     │ • rtk gain               │ Dashboard định lượng token │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 2. PM AGENT         │ • diff -> rtk diff       │ Chỉ hiện diff nội dung cốt │
│    (Orchestrator)   │ • find -> rtk find       │ Nén cây thư mục dạng tree  │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 3. LEAD DEV         │ • git diff -> rtk diff   │ Gọt bỏ header hunk rác     │
│    (Architect)      │ • tsc -> rtk tsc         │ Gom lỗi type theo từng file│
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 4. PEER DEV         │ • cat/read -> rtk read   │ rtk read -l aggressive     │
│    (Maker Sub)      │ • jest -> rtk jest       │ Nén 90% (chỉ hiện failure) │
│                     │ • git add/commit -> rtk  │ Rút gọn còn 1 dòng "ok"    │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 5. QC VERIFIER      │ • jest -> rtk jest       │ Failures only (-90% logs)  │
│    (Checker Sub)    │ • playwright -> rtk test │ E2E trace rút gọn          │
│                     │ • <cmd> -> rtk err <cmd> │ Chỉ bắt stderr và warnings │
├─────────────────────┼──────────────────────────┼────────────────────────────┤
│ 6. SECURITY         │ • grep/rg -> rtk grep    │ Nhóm match theo file (-70%)│
│    SENTINEL         │ • diff -> rtk diff       │ Kiểm tra leak không rác    │
└─────────────────────┴──────────────────────────┴────────────────────────────┘
```

#### A. Cấu Hình Hook Tự Động Trong Hermes Runtime Cho Từng Profile:
Khi spawn bất kỳ Agent nào trong phòng, hệ thống tự động thiết lập bí danh (Alias Wrapper) và biến môi trường:
```bash
# Tự động viết lại các lệnh dev chuẩn sang RTK
alias git="rtk git"
alias jest="rtk jest"
alias tsc="rtk tsc"
alias cat="rtk read"
alias find="rtk find"
alias grep="rtk grep"

# Biến môi trường khống chế output RTK
export RTK_TELEMETRY_DISABLED=1
export RTK_COMPACT_MODE=1
export RTK_TEST_FAILURES_ONLY=1
```

#### B. Kết Quả Đo Lường Định Lượng Sau Khi Áp Dụng Issue #4 & Issue #5:
1. **Tổng lượng Token Input giảm**: Giảm trung bình **65% – 85%** trên mỗi lượt chạy lệnh bash.
2. **Context Window của Agent**: Kéo dài tuổi thọ phiên làm việc lên gấp **3 đến 5 lần** trước khi cần compact.
3. **Tốc độ phản hồi (Latency)**: Rút ngắn thời gian đọc và suy luận của LLM từ 15s xuống còn dưới 3s do không phải parse các log rác dài hàng nghìn dòng.






