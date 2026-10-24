# Workspace Protocol: SLPPC Multi-Agent Architecture

> **Mã quy chuẩn**: `bmad/WORKSPACE_PROTOCOL.md`  
> **Tham chiếu**: `ARCH-SPEC-UNIFIED-ROOM-AGENT-SUPERVISION-2026-V1` | `codex-room-setup` | `paseo-supervision` | `pstack-codex`

Đây là bản giao ước bất biến (Shared Contract) bắt buộc cho mọi Agent hoạt động trong phòng điều hành `Room_Agent`. Quyết định của Người điều hành (Human) là thẩm quyền cao nhất. Mọi Agent đọc tài liệu này trước khi tiếp nhận công việc.

---

## 1. Phân định Thẩm quyền (Authority & Governance)

- **Human Operator (User)**: Chủ sở hữu tối cao về mục tiêu sản phẩm, độ ưu tiên, chi phí token/API, và các quyết định rủi ro không thể đảo ngược.
- **Supervisor (Scope & Intent Guard)**: Trọng tài quản trị phạm vi, **Single Point of Contact (SPOC)** duy nhất với User. Quan sát, định tuyến ý định của Human, quản lý trần đồng thời (Concurrency Ceiling 3–5 workers). Nghiêm cấm trực tiếp can thiệp mã nguồn (`role_trespass`).
- **PM Agent (Decision Arbiter & Loop Enforcer)**: Thẩm định Khả thi (Feasibility 0..3) và Phù hợp (Alignment) qua Kev System One (<50ms). Khống chế trần vòng lặp (Turn Ceiling $\le 3$ attempts). Chặn đứng lỗi `pm_bypass`.
- **Lead Dev (Technical Architect & Technical PM)**: Thiết kế giải pháp kỹ thuật, phân rã task chuẩn Zero-Search 5 thành phần, phê duyệt giải pháp và giao cho Peer. Nghiêm cấm tự ý code sản phẩm (`role_trespass`).
- **Peer Devs (Ephemeral Code Executors 1..4)**: Nhận ủy quyền 1 đầu việc cụ thể từ Lead. Code theo spec, tuân thủ Strict Typing, tự chạy test cơ học cục bộ và nộp trạng thái `Resolved`. Tự hủy tab khi hoàn thành.
- **QC (Quality Gate & Test Architect)**: Độc quyền thẩm quyền chuyển trạng thái task sang `Closed` sau khi xác thực 5-Stage ISTQB, kiểm tra Exit Code 0 cơ học, và xác nhận 100% không có lỗi hồi quy.
- **Security Sentinel**: Quyền VETO bảo vệ an ninh chống rò rỉ (Fail-Closed). Chặn đứng commit/push nếu phát hiện secret, PII hoặc domain nội bộ.

---

## 2. Ranh giới Sở hữu & Phân bổ Công việc (Ownership & Single-Scope)

1. **Quy tắc Single-Ownership**:
   - Mỗi file mã nguồn trong cùng một thời điểm chỉ được phép do **1 Peer Dev duy nhất sở hữu và chỉnh sửa**.
   - Cấm 2 Peer cùng chỉnh sửa 1 file gây xung đột merge (merge conflict).
2. **Biên bản Tự Chứa (Self-Contained Briefs)**:
   - Chỉ thị giao việc từ Lead cho Peer phải chứa đầy đủ mục tiêu, ràng buộc, file can thiệp, và lệnh test.
   - Không chuyển giao nguyên văn lịch sử chat cá nhân nhằm chống tràn Context Window.
3. **Quyền Khiếu Nại Kỹ Thuật (Right to Challenge)**:
   - Peer có quyền phát tín hiệu `REOPEN_REQUEST` (khi tiền đề sai), `DEPENDENCY_REQUEST` (khi thiếu phụ thuộc), hoặc `BLOCKED` (khi không an toàn).
   - Mọi khiếu nại phải đi kèm bằng chứng thực nghiệm (compiler log, test failure, benchmark).

---

## 3. Quản trị Trạng thái & Cơ chế Tự Hủy (Ephemeral State Lifecycle)

Hệ sinh thái vận hành theo nguyên lý **"Ephemeral by Default, Persistent by Exception"**:
- **Persistent Tabs**: Duy trì thường trực tối đa 2–3 tabs điều phối (`Supervisor`, `PM`, `Lead Dev`).
- **Ephemeral Sub-Agents**: `Peer Dev` và `QC` chỉ được kích hoạt theo nhu cầu (on-demand) khi có task:
  - Khi Peer hoàn tất mã nguồn $\rightarrow$ nộp `Resolved` $\rightarrow$ **Cưỡng chế đóng tab Peer ngay lập tức** (đưa RAM nền về 0).
  - Khi QC hoàn tất kiểm thử $\rightarrow$ nộp `Closed` $\rightarrow$ **Cưỡng chế đóng tab QC ngay lập tức** $\rightarrow$ Nén dọn dẹp thư mục tạm `bmad/rooms/tasks/<id>/` vào `bmad/rooms/archive/task_<id>.tar.gz`.

---

## 4. Bằng chứng Cơ học & Nghiệm thu (Mechanical Evidence)

- **Không chấp nhận lời tự khai**: "Never let the AI verify its own done".
- **Tiêu chuẩn nghiệm thu định lượng**:
  1. Exit Code 0 từ test runner thực tế (`pytest`, `npm test`, `python3 -m unittest`).
  2. Git diff thực tế không chứa `any`, `unknown` hoặc fallback chắp vá (`||`).
  3. Kiểm tra Flow Guard: `python3 tools/slppc_flow_guard.py audit` đạt 0 vi phạm.
  4. Quét Anti-Leak: `python3 scripts/anti_leak_sentinel.py` đạt PASS 100%.

---

## 5. Lưu trữ Biên bản Bàn giao (Room Hygiene Standard)

1. Mỗi phòng ban (`bmad/rooms/{supervisor,pm,lead,peer,qc}`) chỉ duy trì duy nhất một file **`latest_handoff.md`** (atomic overwrite in-place, $\le 150$ dòng).
2. Toàn bộ lịch sử chuyển giao được lưu tập trung tại **`bmad/rooms/room_ledger.json`** theo cơ chế xoay vòng rolling FIFO 50 bản ghi, kích thước trần $< 50$ KB.
3. Nghiêm cấm sinh file có hậu tố timestamp (`handoff_YYYYMMDD_HHMMSS.md`) gây bùng nổ file rác.
