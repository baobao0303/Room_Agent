---
name: lead-review
description: "Bộ kỹ năng rà soát mã nguồn (Code Review) và thẩm định kiến trúc dành riêng cho khối Quản lý (Lead Dev & Supervisor) trong mô hình SLPC."
version: 2.0.0
author: BaoLTB, Lead Architect
roles: [lead, supervisor]
---

# Kỹ Năng Code Review & Thẩm Định Kiến Trúc Dành Cho Quản Lý (SLPC Management Code Review)

Trong mô hình SLPC, **Quản lý (Supervisor & Lead) tuyệt đối KHÔNG viết code tính năng**, nhưng nắm quyền sinh sát về **Chất lượng, Ranh giới và Kiến trúc mã nguồn**.

Bộ kỹ năng này quy định quy chuẩn, danh mục kiểm tra (checklist) và công cụ tự động hóa để Quản lý thẩm định spec trước khi phân rã và thẩm định code của Dev trước khi chuyển giao cho QC.

---

## 0. Quy Trình Thẩm Định Đặc Tả Kiến Trúc Trước Khi Phân Rã (Pre-Decomposition Spec Review Gate)

Khi nhận spec từ Supervisor & PM ("giao spec cho leader để review rồi phân tích ok không, nếu không ok thì review spec lại chuẩn hết mới phân rã task cho peer"):

1. **Rà soát 4 trụ cột kiến trúc**:
   - **Decoupling & IoC**: Ưu tiên Template Projection / IoC TemplateRef Slots thay vì nhồi cờ boolean rẽ nhánh (Flag Bloat).
   - **Federation Compatibility**: Kiểm tra Module Federation exposes/remotes paths khớp chuẩn monorepo.
   - **Contract & Typing**: Bắt buộc 0% any/unknown, gắn `tdsTestId` directive theo BNF `<domain>-<component>-<element>-<state?>`.
   - **QC Regression Parity**: 100% tương thích ngược với các test cases hồi quy của QC.
2. **Quyết định thẩm định (Spec Verdict)**:
   - **CHƯA OK**: Chỉ rõ khiếm khuyết, gửi trả Supervisor & PM sửa spec trước khi bất kỳ ai được code.
   - **ĐÃ OK**: Phê duyệt và bóc tách task Zero-Search chuẩn 5 thành phần (Target Files, Anchors/Lines, Concrete Changes, ACs kèm tdsTestId, Test Command) giao cho Peer 1..4 và QC.
3. **Kỷ luật vai trò**: Nghiêm cấm Lead Dev tự ý code tính năng (`role_trespass`).

---

## 1. Phân Định Trách Nhiệm Review Giữa Supervisor và Lead

| Vai trò | Phạm vi Review (Review Scope) | Tiêu chí cốt lõi (Core Criteria) | Hành động khi vi phạm |
| :--- | :--- | :--- | :--- |
| **Supervisor** | **Intent & Scope Alignment** | - Code có giải quyết đúng bài toán của User không?<br>- Có phát sinh Scope Creep (tự ý thêm tính năng không ai yêu cầu) không?<br>- Có rủi ro xóa dữ liệu người dùng không? | Trả task về cho Lead bóc tách lại; khiển trách `scope_creep`. |
| **Lead Dev** | **Architecture & Code Standards** | - Tuân thủ Single-Ownership (chỉ sửa module được giao).<br>- Tuân thủ TDS UI Design Tokens (0% mã màu hex cứng).<br>- Angular 18 OnPush performance.<br>- Lazy Senior Dev / YAGNI (xóa trước thêm sau, không dead code). | Từ chối diff; chạy `tools/agent_reprimand.py --penalize` giáng task về `Active`. |

---

## 2. Checklist 9 Điểm Bắt Buộc Của Lead Dev (9-Point Review Gate)

Trước khi cho phép Task chuyển sang bước kiểm định độc lập của QC, Lead Dev bắt buộc phải đối soát qua 9 tiêu chí:

### A. Ranh giới Sở hữu Đơn nhất (Single-Ownership Invariant)
- **Quy tắc**: 100% file thay đổi phải nằm trọn trong module được giao (VD: Task CDP chỉ được sửa trong `apps/mfe-cdp/...`).
- **Vi phạm**: Sửa chéo sang `app-shell`, `libs/`, hoặc module khác ➔ **REJECT NGAY LẬP TỨC**.

### B. Chuẩn Hóa Design Tokens TDS UI (No Raw Hex Codes)
- **Quy tắc**: Nghiêm cấm mã màu hex cứng dạng `#FF4E00`, `#2EB032`, `rgb(...)` trong template HTML và stylesheet SCSS.
- **Tiêu chuẩn**: Bắt buộc dùng class tiện ích Tailwind chuẩn TDS (`bg-white`, `border-neutral-200`) hoặc token CSS `var(--tds-color-...)`.

### C. Hiệu Năng Angular 18 Standalone & OnPush
- **Quy tắc**: Mọi component tạo mới hoặc refactor bắt buộc phải có:
  ```typescript
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  ```
- **Signals**: Ưu tiên Angular Signals (`signal()`, `computed()`, `input()`, `output()`) thay vì quản lý subscription thủ công.

### D. Tinh Gọn Mã Nguồn & YAGNI (Lazy Senior Dev)
- **Quy tắc**: "Code tốt nhất là code không cần viết".
- **Kiểm tra**:
  * Có tạo interface cho 1 implement duy nhất không? (Xóa).
  * Có viết file util chỉ dùng 1 lần không? (Chuyển thành inline/stdlib).
  * Diff có xóa code cũ trước khi thêm code mới không?

### E. Quét Sạch Dead Code & Import Rác
- **Quy tắc**: Khi refactor (VD: từ `tds-data-table` sang `tds-table`), bắt buộc phải dọn sạch:
  * Các import module cũ không còn sử dụng.
  * Các `@ViewChild` mồ côi không có lệnh gọi.
  * Các biến, hàm private không còn nơi nào invoke.

### F. Tái Sử Dụng Store & State Sẵn Có (Store Reuse Gate - Anti-Rogue HTTP Call)
- **Quy tắc**: Tuyệt đối KHÔNG inject raw API service (như `MemberService`, `AccountService`) để gọi lại server và viết hàm mapping thủ công khi **codebase đã có Signal Store / NgRx Store quản trị tập trung (như `MemberStore`, `AccountStore`)**.
- **Kiểm tra**:
  * Đã tra cứu xem feature/entity đó có store trong `libs/features/*/stores/` chưa?
  * Nếu đã có Store `{ providedIn: 'root' }`, BẮT BUỘC inject Store và tái sử dụng computed signals (`memberStore.employeeList()`, `memberStore.totalEmployees()`).
  * Cấm tạo các luồng tải mạng song song phân mảnh state của hệ thống.

### G. Chuẩn Hóa Kiểu Dữ Liệu Chặt Chẽ (Strict Typing Gate - Zero `any`, Zero `unknown`, Zero Sloppy Fallbacks `||`)
- **Quy tắc**: Khi DTO, Model, Interface đã tồn tại trong codebase:
  * **CẤM TUYỆT ĐỐI** dùng `any`, `unknown`, `as any` trong mã nguồn sản phẩm. Dù chỉ 1 dòng `any` cũng bị **REJECT NGAY LẬP TỨC**.
  * **CẤM** chuỗi fallback `||` không chắc chắn (như `emp.id || emp.shopUserId`, `displayName || name || ''`). Phải map tường minh đúng trường theo DTO contract (`emp.shopUserId`, `emp.accountUserId ?? String(emp.shopUserId)`).
  * **CẤM** dùng `new Optional()` trong `deps` cho các Store/Service cốt lõi đã `{ providedIn: 'root' }`. Phải inject trực tiếp bắt buộc.

### H. Cổng Chống Lộ Dữ Liệu Nhạy Cảm & Địa Chỉ Thực Tế (Anti-Leak & Sensitive Data Gate)
- **Quy tắc**: Tuyệt đối KHÔNG đưa thông tin nhạy cảm vào codebase, tài liệu spec, commit Git hoặc Pull Request:
  * **Tên công ty nội bộ, dự án khách hàng**: Không hardcode tên công ty, domain nội bộ (`tfs.*`, `*.dev.local`).
  * **Địa chỉ thực tế & địa danh cụ thể**: Tuyệt đối xóa sạch số nhà, tên đường, cụm/lô khu công nghiệp, quận huyện khỏi tài liệu/spec mẫu.
  * **Thông tin định danh cá nhân (PII)**: Số điện thoại, email cá nhân, mã số thuế nội bộ.
  * **Secret Keys & Env Files**: Không commit file `.env` chứa credential thật, private keys, API keys.
- **Kịch bản kiểm tra tự động (Automated Security Scan)**:
  * Bắt buộc tích hợp script quét regex (như `check-sensitive-info.py`, `git_pre_commit_guard.py`) hoặc GitHub Actions workflow (`security-scan.yml`) fail-closed trước khi merge.
- **Quy chuẩn Format Rust / TypeScript**:
  * Với dự án Rust: Bắt buộc chạy `cargo fmt --check` và `cargo check` trước khi commit/push để tránh gãy release pipeline.
  * Với dự án Angular/TS: Chạy lint và typecheck (`tsc --noEmit`) trước khi bàn giao.

### I. Chuẩn Hóa Định Danh Kiểm Thử Bất Biến (TDS Test ID & Testing Contract Gate)
- **Quy tắc bắt buộc**: 100% component FE có tương tác (button, input, select, form, modal, table row) phải gắn directive `tdsTestId` từ `@demo/core`.
- **Cú pháp định danh**: `<domain>-<component>-<element>-<state?>` (100% tiếng Anh, kebab-case).
- **Quy định Zero-Search Task**: Mọi Task giao cho Peer bắt buộc trường `--ac` và `--description` phải chỉ định rõ danh sách `tdsTestId` cụ thể.
- **Quyền VETO / REJECT NGAY LẬP TỨC**:
  * ❌ Hardcode thuộc tính DOM tĩnh `tds-test-id="..."` trực tiếp trên template (bắt buộc dùng directive `tdsTestId`).
  * ❌ Dùng `data-testid` hoặc class CSS/XPath để phục vụ test.
  * ❌ Dùng array index cho danh sách/bảng: `[tdsTestId]="'row-' + index"` (bắt buộc dùng entity ID: `[tdsTestId]="'customer-row-' + item.id"`).
  * ❌ Dùng tiếng Việt không dấu hoặc đưa chi tiết CSS/màu sắc vào ID (`red-btn`, `xoa-btn`).

---

## 3. Quy Trình & Công Cụ Review Tự Động Hóa

### Bước 1: Quét Tự Động Bằng Tool
Lead Dev chạy công cụ thẩm định tự động:
```bash
python3 tools/lead_code_review.py --repo-dir projects/demo-crm-fe --task-id <id>
```
- Công cụ tự động quét Git Diff (cả staged và unstaged).
- Kiểm tra mã màu hex, OnPush, single-ownership.
- Xuất báo cáo tại: `bmad/rooms/lead/latest_review.md`.

### Bước 2: Huy Động Sub-Agents Hỗ Trợ Review Sâu
- Khi diff phức tạp, Lead gọi Sub-agent:
  * `gemini-codebase-analyzer`: Quét 1M+ token để kiểm tra blast radius và import rác.
  * `strategic-reasoning-architect`: Phân tích xem giải pháp của Peer có tối ưu không.

### Bước 3: Đưa Ra Quyết Định (Verdict)

#### Trường hợp 1: APPROVED (Đạt chuẩn 100%)
Lead ký duyệt biên bản và bàn giao việc sang phòng QC:
```bash
# Cập nhật handoff cho QC
python3 tools/agent_progress.py log \
  --agent "Lead" \
  --summary "Code review APPROVED Task #<id>, chuyển giao cho QC" \
  --files "<files>"

# Chuyển trạng thái trên Harness DB
python3 tools/harness_manager.py update --id <id> --state Resolved --assigned-to-profile qc
```

#### Trường hợp 2: REJECTED (Phát hiện lỗi vi phạm ➔ TỰ ĐỘNG TẠO BUG)
Lead không bao giờ sửa code hộ Dev. Thay vào đó, Lead lập tức kích hoạt công cụ xử phạt:
```bash
python3 tools/agent_reprimand.py \
  --from-role Lead \
  --to-role Peer \
  --violation hardcoded_hex \
  --evidence "<dòng code vi phạm trích từ git diff>" \
  --message "Yêu cầu xóa sạch mã màu hex cứng và thay bằng token chuẩn TDS trước khi nộp lại!" \
  --task-id <id> \
  --penalize
```
**Hệ thống tự động kích hoạt**:
1. **Tạo Ticket dạng `Bug` trên Harness DB**: Sinh Bug `[Review]: Phat hien <violation> when reviewed by Lead`, độ ưu tiên `P1`, gán đích danh cho `peer` kèm bằng chứng thực tế.
2. **Giáng cấp Task**: Task chính bị giật ngược từ `Resolved` về `Active`.
3. **Bắn thông báo qua Orca**: Gửi escalation cảnh cáo vào terminal của Peer Dev. Dev bắt buộc phải fix xong Bug này mới được nộp lại cho QC!
