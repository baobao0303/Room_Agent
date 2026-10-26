# CHỈ THỊ & ĐẶC TẢ HÀNH ĐỘNG NẠP CHO TOÀN BỘ AGENT (SLPPC AGENT ACTION SPEC)
## TRIỂN KHAI QUY CHUẨN ĐỊNH DANH KIỂM THỬ BẤT BIẾN: TDS TEST ID & TESTING CONTRACT

**Mã tài liệu**: `ACTION-SPEC-TDS-TEST-ID-2026-V1`  
**Ngày ban hành**: `2026-10-23`  
**Cơ quan ban hành**: Supervisor & PM Agent  
**Căn cứ kỹ thuật**: `docs/spec/tds-test-id-guideline-spec.md` (v2.2.0 Enterprise) & Outline Guideline  
**Phạm vi áp dụng**: 100% Agent trong phòng ban SLPPC (`Supervisor`, `PM`, `Lead`, `Peer 1..4`, `Design`, `QC`)  

---

## 1. PHÂN CÔNG HÀNH ĐỘNG CỤ THỂ CHO TỪNG AGENT

### 1.1. Dành Cho LEAD DEV (`profiles/lead.md`)
- **Nhiệm vụ cốt lõi**:
  1. Khi phân rã bất kỳ User Story / Task nào liên quan đến UI/UX, trường `--description` (Zero-Search 5 thành phần) và `--ac` BẮT BUỘC phải chứa yêu cầu gắn `tdsTestId`.
  2. Bắt buộc kiểm soát naming convention theo chuẩn:
     $$\mathbf{\langle domain \rangle\text{-}\langle component \rangle\text{-}\langle element \rangle\text{-}\langle state? \rangle}$$
  3. Cấm duyệt các PR của Peer nếu phát hiện:
     - Hardcode trực tiếp DOM attribute `tds-test-id="..."`.
     - Dùng `data-testid` hoặc CSS class để phục vụ test.
     - Dùng array index `[tdsTestId]="'row-' + index"`.
  4. Đưa `tools/strict_typing_scanner.py` và quy chuẩn Test ID vào 7-Point Review Gate.

---

### 1.2. Dành Cho PEER DEVS (`profiles/peer.md` - Peer 1, Peer 2, Peer 3, Peer 4, Design)
- **Nhiệm vụ cốt lõi**:
  1. **Import Directive**: Mọi Component Standalone khi render giao diện phải import `TdsTestIdDirective` từ `@demo/core`:
     ```typescript
     import { TdsTestIdDirective } from '@demo/core';

     @Component({
       standalone: true,
       imports: [CommonModule, TdsTestIdDirective, ...],
       ...
     })
     ```
  2. **Gắn ID bắt buộc cho**:
     - Tất cả các nút bấm (`*-btn`).
     - Tất cả các ô nhập liệu, select, checkbox, radio (`*-input`, `*-select`, `*-checkbox`).
     - Tất cả các form (`*-form`), modal (`*-modal`), drawer (`*-drawer`), toast/alert (`*-toast`, `*-alert`).
     - Tất cả các dòng trong bảng hoặc card trong danh sách: Phải dùng ID nghiệp vụ (`[tdsTestId]="'customer-row-' + item.id"`).
  3. **Quy tắc cấm tuyệt đối**:
     - ❌ CẤM hardcode `tds-test-id="..."` (phải dùng directive `tdsTestId`).
     - ❌ CẤM dùng tiếng Việt không dấu (ví dụ: cấm `xoa-btn`).
     - ❌ CẤM đưa chi tiết CSS/màu sắc vào test ID (cấm `red-btn`, `btn-primary`).

---

### 1.3. Dành Cho QC VERIFIER (`profiles/qc.md` - BẮT BUỘC BỔ SUNG UNIT TEST)
- **Nhiệm vụ cốt lõi**:
  1. **BỔ SUNG UNIT TEST NGAY LẬP TỨC CHO DIRECTIVE**:
     - File đích: `projects/demo-crm-fe/libs/demo-core/src/directives/tds-test-id.directive.spec.ts`.
     - Kịch bản kiểm thử bắt buộc:
       * `[TC-01]`: Gán tĩnh (`tdsTestId="auth-login-submit-btn"`) $\rightarrow$ Render đúng `tds-test-id="auth-login-submit-btn"`.
       * `[TC-02]`: Gán động (`[tdsTestId]="'customer-row-' + id"`) $\rightarrow$ Render đúng ID động khi input thay đổi.
       * `[TC-03]`: Truyền `null` hoặc `undefined` $\rightarrow$ DOM không render attribute rác.
       * `[TC-04]`: Truyền chuỗi rỗng hoặc khoảng trắng (`"   "`) $\rightarrow$ Tự động trim và không render attribute rác.
       * `[TC-05]`: Truyền kiểu số (`[tdsTestId]="12345"`) $\rightarrow$ Tự động ép kiểu chuỗi `"12345"`.
     - Tiêu chuẩn: **Pass 100%, 0 warnings, strict typing 100%**.
  2. **Thực thi Auto-Test Automation**:
     - 100% test Playwright/Cypress/Jest phải query qua helper `getByTdsTestId(page, id)` hoặc selector `[tds-test-id="..."]`.
     - ❌ TUYỆT ĐỐI CẤM query qua `getByText()`, `.className`, `nth-child`, hoặc XPath phân cấp.
  3. **Quyền VETO nghiệm thu**:
     - QC có quyền REJECT và từ chối đóng `Closed` bất kỳ task nào nếu phát hiện màn hình thiếu `tdsTestId` trên các button/input tương tác.

---

### 1.4. Dành Cho PM AGENT (`profiles/pm.md`)
- **Nhiệm vụ cốt lõi**:
  1. Giữ chốt chặn **Definition of Done (DoD)** 4 tiêu chuẩn: UI xong + Logic đúng + `tdsTestId` đủ + Auto-test pass.
  2. Thẩm định mọi đề xuất bổ sung Domain mới trước khi đưa vào codebase.
  3. Duy trì quy trình Change Management 4 bước khi có yêu cầu đổi tên `testId` để bảo vệ hệ thống CI/CD.

---

## 2. TỔNG KẾT HÀNH ĐỘNG CẦN KÍCH HOẠT NGAY

1. **Giai đoạn 1**: Peer Dev 1 tạo file `tds-test-id.directive.ts` và QA helper trong `libs/demo-core`.
2. **Giai đoạn 2**: **QC Verifier viết bộ unit test suite `tds-test-id.directive.spec.ts`** và chạy lệnh test pass 100%.
3. **Giai đoạn 3**: Peer Dev 2 áp dụng thí điểm cho màn hình Login (`app-shell`) và Customer List (`mfe-crm`).
4. **Giai đoạn 4**: QC nghiệm thu độc lập và đóng task.
