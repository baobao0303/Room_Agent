# User Story: Xem chi tiết hồ sơ khách hàng dạng drawer

- Parent: Feature #123 (Resolved, spec xong)
- Spec nguồn: `docs/spec/wicx-crm-fe/design/customer-detail-drawer.md` (mục 6 AC, mục 7 câu hỏi mở, mục 9 kế hoạch)
- BA nguồn: `Phase 0.5_User_Stories/UC4.04 - Chi tiết hồ sơ khách hàng.md`, `UC4.01` (2.1-2.4)
- Figma: file `yOglVOGf6KdoroEulwFYcg`, node `1175:5513`, `1659:38575`
- Trạng thái: user đã chốt 4 điểm (mục "Quyết định của user"). Chưa tạo Harness item, chưa dispatch.

## Story

Là nhân viên chăm sóc khách hàng,
tôi muốn bấm vào tên khách ở danh sách Khách hàng để mở drawer hồ sơ,
để xem thông tin, lịch hẹn, ghi chú, lịch sử của khách và thao tác nhanh mà không rời danh sách.

## Quyết định của user (2026-10-14)

- D1. Tính năng chưa phát triển: bấm hiện message "Tính năng đang phát triển" (`TDSMessageService.info`), không mở gì. Áp dụng cho: tab "Ghi chú", tab "Lịch sử", nút "Ghi chú", nút "Tạo lịch hẹn", nút "Chỉnh sửa".
- D2. Token (Q6): tra lookup, token nào dùng được (exact) thì dùng class `tds-color-*`. Token ambiguous/missing thì làm như Figma (màu theo hex Figma, đặt trong 1 file hằng/biến cục bộ, comment `TODO(token)`), không tự chọn token.
- D3. Phần còn lại theo Figma (suy ra từ "còn lại như figma"; user chưa nêu riêng, nếu sai báo lại):
  - Q25: nhóm nút nằm trong summary card, cuộn theo, không sticky.
  - Q23: KHÔNG thêm nút "Nhận khách" và nút Sửa/Xóa trên card lịch hẹn (Figma không có).
  - Release 1 chỉ làm phần có node Figma.

## Phạm vi

Release 1 (dựng trên mock data):
- R1-A: Drawer shell, mở/đóng, deep link `?customerId=`, loading/404/lỗi.
- R1-B: Header (avatar, tên, Loại hồ sơ, Mã KH, Trạng thái KH) + nhóm nút theo Figma (Ghi chú, Tạo lịch hẹn, Chỉnh sửa: message D1; Xóa: popup xác nhận).
- R1-C: Tab "Thông tin" (Thông tin cá nhân, Thông tin mua hàng).
- R1-D: Tab "Lịch hẹn" (xem, rỗng).
- R1-E: Popup Xóa khách (theo BA; xóa trên mock).
- R1-F: Tab "Ghi chú" và "Lịch sử": chỉ nhận click, hiện message D1 và giữ nguyên tab hiện tại.

Release 2 (sau, khi Figma hết 429 và chốt Q20, Q15, Q18, Q19, Q24): nội dung tab Ghi chú, Lịch sử; modal Tạo lịch hẹn, Chỉnh sửa; Nhận khách; Sửa/Xóa lịch hẹn.

Ngoài phạm vi: Phase 1 (RBAC/ABAC, audit, segment), API thật (Q11), luật tự tính trạng thái khách (BE), responsive < 768px (Q7).

## Điều kiện/ phụ thuộc

- Contract API chưa có (Q11): dùng DTO + service mock, đổi sang HTTP sau không đổi UI.
- Token ambiguous/missing (Q6, Q8, Q15): theo D2, màu Figma + `TODO(token)`.

## Acceptance Criteria

Chi tiết Given/When/Then nằm ở spec mục 6. Bảng map để Lead tạo task và QC dựng test case.

| AC | Nội dung | Spec mục 6 (Scenario) | Release |
|---|---|---|---|
| AC-01 | Click cột Khách hàng mở drawer 768px, có loading | Mở chi tiết từ cột Khách hàng | R1-A |
| AC-02 | `?customerId=<id>` mở đúng khách; đóng thì xóa param | Deep link qua query param | R1-A |
| AC-03 | Đóng bằng X, "Đóng", ESC, click mask; danh sách giữ cuộn/lọc | Đóng drawer | R1-A |
| AC-04 | Click khách khác khi drawer mở: loading rồi khách mới | Đổi khách hàng khi drawer đang mở | R1-A |
| AC-05 | 404: empty "Không tìm thấy khách hàng" | Khách hàng không tồn tại | R1-A |
| AC-06 | Lỗi 5xx/mạng: "Thử lại" gọi lại API | Lỗi tải chi tiết | R1-A |
| AC-07 | Header hiển thị avatar, tên, Loại hồ sơ, Mã KH, Trạng thái KH | Hiển thị dữ liệu khách hàng | R1-B |
| AC-08 | Nhóm nút theo Figma (Ghi chú, Tạo lịch hẹn, Chỉnh sửa, Xóa), nằm trong summary card, cuộn theo. Bấm Ghi chú/Tạo lịch hẹn/Chỉnh sửa: message "Tính năng đang phát triển" (D1). Không có nút Nhận khách (D3) | MỚI, xem dưới | R1-B |
| AC-09 | Thu gọn card "Thông tin cá nhân" bằng chevron | Thu gọn card | R1-C |
| AC-10 | Trường cá nhân rỗng thì ẨN dòng | Ẩn trường cá nhân rỗng | R1-C |
| AC-11 | SĐT/Email/DN/Sản phẩm: tối đa 3 + "Xem thêm"/"Rút gọn thông tin" | Giới hạn 3 mục và Xem thêm | R1-C |
| AC-12 | Mua hàng: chưa khớp đơn để trống, không dùng "-"; đã khớp chưa có đơn Completed hiện `0` | Thông tin mua hàng (2 scenario) | R1-C |
| AC-13 | Sản phẩm hết hạn hiện "Hết hạn" màu error | Sản phẩm hết hạn | R1-C |
| AC-14 | Chuyển tab: "Thông tin" và "Lịch hẹn" chuyển được; bấm "Ghi chú"/"Lịch sử" hiện message "Tính năng đang phát triển", giữ nguyên tab hiện tại (D1) | MỚI, xem dưới | R1-C/F |
| AC-15 | Tab Lịch hẹn: mới nhất trên cùng, gồm lịch đã qua, đủ trường, mô tả wrap | Tab Lịch hẹn | R1-D |
| AC-16 | Lịch hẹn rỗng: "Chưa có lịch hẹn nào." | Tab Lịch hẹn rỗng | R1-D |
| AC-17 | (HOÃN R2, D3) Xóa lịch hẹn | Xóa lịch hẹn | R2 |
| AC-18 | Lỗi một khối không chặn khối khác, có "Thử lại" | Lỗi theo khối | R1-A/D |
| AC-19 | (HOÃN R2, D1) Tạo lịch hẹn: Release 1 chỉ hiện message "Tính năng đang phát triển" | Tạo lịch hẹn | R2 |
| AC-20 | (HOÃN R2, D1) Chỉnh sửa: Release 1 chỉ hiện message "Tính năng đang phát triển" | Chỉnh sửa khách hàng | R2 |
| AC-21 | Xóa khách: popup đúng text, xác nhận xóa vĩnh viễn, Đóng thì không xóa | Xóa khách hàng | R1-E |
| AC-22 | Token exact dùng class `tds-color-*`; ambiguous/missing dùng màu Figma trong 1 file hằng kèm `TODO(token)` (D2) | Màu sắc theo token (sửa theo D2) | R1-ALL |
| AC-23 | (HOÃN R2) Nội dung tab Ghi chú | Tab Ghi chú (hiển thị), rỗng | R2 (CHẶN) |
| AC-24 | (HOÃN R2) Nội dung tab Lịch sử | Lịch sử tương tác theo kênh, Heatmap x3, Lịch sử lazy-load, Lịch sử cập nhật | R2 (CHẶN) |

AC mới (chưa có trong spec mục 6, cần thêm vào spec):

```gherkin
  Scenario: Tính năng chưa phát triển
    Given drawer đang mở tab "Thông tin"
    When tôi bấm tab "Ghi chú" hoặc "Lịch sử"
    Then hiển thị message "Tính năng đang phát triển"
    And tab hiện tại giữ nguyên

  Scenario: Nút chưa phát triển
    Given drawer đang mở
    When tôi bấm nút "Ghi chú", "Tạo lịch hẹn" hoặc "Chỉnh sửa"
    Then hiển thị message "Tính năng đang phát triển"
    And không có modal hay popup nào mở

  Scenario: Nhóm nút theo Figma
    When drawer hiển thị
    Then nhóm nút nằm trong summary card và cuộn cùng nội dung
    And chỉ có 4 nút: Ghi chú, Tạo lịch hẹn, Chỉnh sửa, Xóa
```

Phi chức năng: Angular 18 standalone, strict TS, không `any`, DTO hậu tố `Dto`, import `tds-ui/<sub-path>`, màu bằng class `tds-color-*`.

## Gợi ý chia task cho Lead (Technical Story/Task)

Lead quyết định cuối cùng. Chỉ Release 1.

| # | Task | Assignee | Phụ thuộc | AC |
|---|---|---|---|---|
| T1 | DTO + fixture + mock service (fixture F1..F12) | Peer | - | nền cho mọi AC |
| T2 | Drawer shell, deep link, loading/404/lỗi | Peer | T1 | AC-01..06, 18 |
| T3 | Header + nhóm nút (Xóa popup, 3 nút còn lại message D1) | Peer | T2 | AC-07, 08, 21 |
| T4 | Tab Thông tin + chuyển tab (Ghi chú/Lịch sử message D1) | Peer | T2 | AC-09..14 |
| T5 | Tab Lịch hẹn (xem, rỗng) | Peer | T2 | AC-15, 16 |
| T6 | Token: tra lookup, class exact; ambiguous theo Figma trong file hằng + TODO(token); rà hex | Peer, QC kiểm | T3..T5 | AC-22 |

Hoãn Release 2: AC-17, 19, 20, 23, 24 và Nhận khách (cần Q20, Q15, Q18, Q19, Q24, Figma hết 429).

## Hand-off cho QC (tạo test case)

Test case tạo từ AC ở trên, không đọc code. Mỗi test case ghi: ID, AC, kỹ thuật (phân vùng tương đương / giá trị biên / bảng quyết định / chuyển trạng thái), dữ liệu fixture, bước, kết quả mong đợi.

Dữ liệu fixture bắt buộc (dùng cùng bộ với T1):

| Fixture | Dùng cho AC |
|---|---|
| F1 đủ dữ liệu | AC-07, 09, 14 |
| F2 thiếu trường (ngày sinh, email...) | AC-10 |
| F3 chưa khớp đơn | AC-12 |
| F4 đã khớp, 0 đơn Completed | AC-12 |
| F5 sản phẩm hết hạn | AC-13 |
| F6 5 SĐT, 5 email, 5 DN, 5 sản phẩm (biên: đúng 3 và 4 mục) | AC-11 |
| F7 trạng thái "Mới" | AC-07 (hiển thị tag trạng thái) |
| F8 trạng thái "Đã chốt", "Trễ hẹn chăm", "Đang nuôi dưỡng" | AC-07 |
| F9 không có lịch hẹn | AC-16 |
| F10 nhiều lịch hẹn, có lịch quá hạn | AC-15 |
| F11 API 404 | AC-05 |
| F12 API 5xx, riêng lịch hẹn lỗi | AC-06, 18 |

Biên cần có: đúng 3/4 mục (Xem thêm), tên khách rất dài, mô tả lịch hẹn rất dài.

Kiểm tra phi chức năng: hex chỉ xuất hiện trong file hằng token (kèm `TODO(token)`), ngoài ra = 0; `tsc --noEmit` pass.

Test case cho AC hoãn (AC-17, 19, 20, 23, 24) để trạng thái "Blocked" cho tới Release 2.

## Việc sau khi user duyệt

```bash
python3 tools/harness_manager.py add --type "User Story" --title "<tiêu đề story>" --parent-id 123 --priority P1 --ac "AC-01..AC-16, AC-18, AC-21, AC-22 và 3 scenario mới (docs/spec/wicx-crm-fe/stories/US-customer-detail-drawer.md)" --created-by-profile Supervisor --assigned-to-profile Lead --dispatch
```

Lead tạo Task T1..T6 và gắn `--parent-id` là story. QC tạo Testcase từ bảng AC (`tools/qc_test_generator.py --task-id <id> --sync-harness` khi có code).
