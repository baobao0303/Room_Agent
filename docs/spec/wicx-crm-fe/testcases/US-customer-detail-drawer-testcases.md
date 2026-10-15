# Test case: Chi tiết khách hàng dạng drawer (Story #127)

- Nguồn: `docs/spec/wicx-crm-fe/stories/US-customer-detail-drawer.md`, `docs/spec/wicx-crm-fe/design/customer-detail-drawer.md` mục 6. Không đọc code.
- Tổng: 81 test case. Ready: 72. Blocked (Release 2): 9.
- Harness: item type Testcase, parent #127, created-by QC. Cột `Harness` là id item.
- Message chuẩn: "Tính năng đang phát triển" (D1).
- Giả định: F1 chứa khách "KH-4F7A2C Nguyễn Văn A" (dùng cho AC-21); F6 có biến thể đúng 3, 4, 1 mục; F8 gồm 3 khách (Đã chốt, Trễ hẹn chăm, Đang nuôi dưỡng). Lead/Peer xác nhận khi dựng fixture T1.
- Blocked: trạng thái Testcase của Harness không cho chuyển New sang Blocked, nên Blocked ghi trong description và bảng này; giữ state New.

## Ma trận phủ AC

| AC | Test case |
|---|---|
| AC-01 | 001, 002, 003 |
| AC-02 | 004, 005, 006, 007 |
| AC-03 | 008, 009, 010, 011, 012 |
| AC-04 | 013, 014 |
| AC-05 | 015 |
| AC-06 | 016, 017, 018, 019 |
| AC-07 | 020, 021, 022, 023, 024 |
| AC-08 | 025, 026, 027, 028, 029 |
| AC-09 | 030, 031 |
| AC-10 | 032, 033, 034 |
| AC-11 | 035, 036, 037, 038, 039, 040, 041, 042 |
| AC-12 | 043, 044, 045 |
| AC-13 | 046, 047, 048, 049 |
| AC-14 | 050, 051, 052, 053, 054 |
| AC-15 | 055, 056, 057, 058, 059, 060 |
| AC-16 | 061 |
| AC-18 | 062, 063, 064 |
| AC-21 | 065, 066, 067, 068 |
| AC-22 | 069, 070, 071, 072 |
| AC-17 | 073 |
| AC-19 | 074 |
| AC-20 | 075 |
| AC-23 | 076, 077 |
| AC-24 | 078, 079, 080, 081 |
| 3 scenario mới | Tab: TC cùng AC-14 (Ghi chú/Lịch sử). Nút: TC cùng AC-08 (3 nút message). Nhóm nút: TC cùng AC-08 (4 nút, summary card, cuộn theo) |

## Bảng test case

| ID | Harness | AC | Kỹ thuật | Fixture | Tên | Bước | Kết quả mong đợi | Trạng thái | Ưu tiên |
|---|---|---|---|---|---|---|---|---|---|
| TC-DRW-001 | #134 | AC-01 | Phân vùng tương đương | F1 | Drawer mở rộng 768px từ bên phải khi click tên khách ở cột Khách hàng | 1. Vào danh sách Khách hàng. 2. Click tên khách (F1) ở cột Khách hàng. | Drawer "Hồ sơ khách hàng" mở từ bên phải, rộng 768px. | Ready | P1 |
| TC-DRW-002 | #135 | AC-01 | Chuyển trạng thái | F1 | Drawer hiển thị loading rồi dữ liệu khi API trả chậm | 1. Mock API chi tiết trễ 2s. 2. Click tên khách (F1). 3. Quan sát trong 2s. 4. Chờ API trả. | Trong 2s: drawer mở, hiện loading, chưa hiện dữ liệu. Sau đó: loading ẩn, hiện header và tab Thông tin. | Ready | P1 |
| TC-DRW-003 | #136 | AC-01 | Phân vùng tương đương | F1 | Chỉ click vùng cột Khách hàng mở drawer, cột khác không mở khi click ô ngoài tên | 1. Click các ô cột khác của cùng dòng (không phải tên khách). | Drawer không mở. | Ready | P2 |
| TC-DRW-004 | #137 | AC-02 | Phân vùng tương đương | F1 | Drawer tự mở đúng khách khi mở URL kèm ?customerId hợp lệ | 1. Mở URL danh sách kèm ?customerId=<id F1>. | Drawer tự mở, hiển thị đúng khách có id đó (tên/Mã KH khớp F1). | Ready | P1 |
| TC-DRW-005 | #138 | AC-02 | Chuyển trạng thái | F1 | Drawer giữ nguyên khách khi refresh lúc drawer đang mở | 1. Mở drawer khách F1 (URL có customerId). 2. Refresh trình duyệt. | Drawer mở lại, đúng khách F1. | Ready | P1 |
| TC-DRW-006 | #139 | AC-02 | Giá trị biên | F1 | customerId bị xóa khỏi URL và giữ param khác khi đóng drawer | 1. Mở URL ?customerId=<id F1>&page=2 (hoặc param lọc khác). 2. Đóng drawer. | customerId biến mất khỏi URL; param còn lại (page/lọc) giữ nguyên. | Ready | P1 |
| TC-DRW-007 | #140 | AC-02 | Phân vùng tương đương | F11 | Drawer hiển thị không tìm thấy khi customerId không tồn tại trong URL | 1. Mở URL ?customerId=<id không tồn tại> (F11). | Drawer mở, hiển thị trạng thái 404 (xem AC-05), không crash, danh sách phía sau vẫn dùng được. | Ready | P2 |
| TC-DRW-008 | #141 | AC-03 | Bảng quyết định | F1 | Drawer đóng khi bấm nút X | 1. Mở drawer F1. 2. Bấm X. | Drawer đóng. | Ready | P1 |
| TC-DRW-009 | #142 | AC-03 | Bảng quyết định | F1 | Drawer đóng khi bấm nút Đóng | 1. Mở drawer F1. 2. Bấm nút "Đóng". | Drawer đóng. | Ready | P1 |
| TC-DRW-010 | #143 | AC-03 | Bảng quyết định | F1 | Drawer đóng khi bấm phím ESC | 1. Mở drawer F1. 2. Nhấn ESC. | Drawer đóng. | Ready | P1 |
| TC-DRW-011 | #144 | AC-03 | Bảng quyết định | F1 | Drawer đóng khi click mask | 1. Mở drawer F1. 2. Click vùng mask ngoài drawer. | Drawer đóng. | Ready | P1 |
| TC-DRW-012 | #145 | AC-03 | Phân vùng tương đương | F1 | Danh sách giữ vị trí cuộn và bộ lọc khi đóng drawer | 1. Áp bộ lọc, cuộn danh sách xuống giữa. 2. Mở drawer. 3. Đóng bằng từng cách (X, Đóng, ESC, mask). | Mỗi lần đóng: vị trí cuộn và bộ lọc giữ nguyên, danh sách không tải lại về đầu. | Ready | P1 |
| TC-DRW-013 | #146 | AC-04 | Chuyển trạng thái | F1,F8 | Drawer loading rồi hiển thị khách B khi click khách B lúc đang mở khách A | 1. Mở drawer khách A. 2. Click khách B ở danh sách (mask/danh sách còn click được). 3. Quan sát. | Drawer về loading, sau đó hiển thị dữ liệu khách B; không còn dữ liệu A. | Ready | P1 |
| TC-DRW-014 | #147 | AC-04 | Giá trị biên | F1,F8 | Drawer hiển thị khách cuối khi click liên tiếp A, B, C nhanh | 1. Mock API B trả chậm hơn C. 2. Click A, B, C liên tiếp. 3. Chờ mọi API xong. | Drawer hiển thị khách C; dữ liệu B trả muộn không ghi đè. | Ready | P2 |
| TC-DRW-015 | #148 | AC-05 | Phân vùng tương đương | F11 | Drawer hiển thị Không tìm thấy khách hàng khi API trả 404 | 1. Mock API chi tiết trả 404 (F11). 2. Click khách / mở deep link. | Drawer hiển thị empty "Không tìm thấy khách hàng"; không hiện lỗi 5xx, không hiện nút Thử lại. | Ready | P1 |
| TC-DRW-016 | #149 | AC-06 | Phân vùng tương đương | F12 | Drawer hiển thị lỗi và nút Thử lại khi API chi tiết trả 5xx | 1. Mock API chi tiết trả 500 (F12). 2. Mở drawer. | Drawer hiển thị lỗi kèm nút "Thử lại". | Ready | P1 |
| TC-DRW-017 | #150 | AC-06 | Phân vùng tương đương | F12 | Drawer hiển thị lỗi và nút Thử lại khi mất mạng | 1. Mock lỗi mạng (request fail). 2. Mở drawer. | Drawer hiển thị lỗi kèm nút "Thử lại". | Ready | P1 |
| TC-DRW-018 | #151 | AC-06 | Chuyển trạng thái | F12,F1 | Hệ thống gọi lại API và hiện loading khi bấm Thử lại | 1. Gây lỗi 5xx, drawer hiện lỗi. 2. Đổi mock trả F1. 3. Bấm "Thử lại". | API được gọi lại đúng 1 lần; drawer hiện loading; sau đó hiển thị dữ liệu F1. | Ready | P1 |
| TC-DRW-019 | #152 | AC-06 | Chuyển trạng thái | F12 | Drawer quay lại lỗi khi Thử lại tiếp tục thất bại | 1. Lỗi 5xx. 2. Bấm "Thử lại" khi mock vẫn lỗi. | Loading rồi hiện lại lỗi + nút "Thử lại"; có thể bấm tiếp. | Ready | P2 |
| TC-DRW-020 | #153 | AC-07 | Phân vùng tương đương | F1 | Header hiển thị avatar, tên, Loại hồ sơ, Mã KH, Trạng thái KH khi khách đủ dữ liệu | 1. Mở drawer F1. | Thấy avatar, tên, tag Loại hồ sơ, "Mã KH", "Trạng thái khách hàng"; tab "Thông tin" đang được chọn. | Ready | P1 |
| TC-DRW-021 | #154 | AC-07 | Phân vùng tương đương | F7 | Header hiển thị tag trạng thái Mới khi khách ở trạng thái Mới | 1. Mở drawer F7. | Tag trạng thái hiển thị "Mới". | Ready | P1 |
| TC-DRW-022 | #155 | AC-07 | Phân vùng tương đương | F8 | Header hiển thị đúng tag cho từng trạng thái Đã chốt, Trễ hẹn chăm, Đang nuôi dưỡng | 1. Mở lần lượt 3 khách của F8 (Đã chốt, Trễ hẹn chăm, Đang nuôi dưỡng). | Mỗi khách hiển thị đúng tên trạng thái của mình, không lẫn trạng thái khác. | Ready | P1 |
| TC-DRW-023 | #156 | AC-07 | Giá trị biên | F1 | Header không vỡ layout khi tên khách rất dài | 1. Mở drawer khách có tên 100+ ký tự (biên tên dài). | Tên wrap hoặc cắt gọn có ellipsis; không tràn ra ngoài drawer, không che nút X, không đẩy lệch avatar/tag. | Ready | P2 |
| TC-DRW-024 | #157 | AC-07 | Phân vùng tương đương | F1 | Card Thông tin cá nhân và Thông tin mua hàng hiển thị đúng trường như Figma | 1. Mở drawer F1. 2. Đối chiếu từng nhãn/giá trị trong 2 card với Figma node 1175:5513. | Hai card hiển thị đủ trường, đúng nhãn, đúng thứ tự như Figma. | Ready | P1 |
| TC-DRW-025 | #158 | AC-08 | Phân vùng tương đương | F1 | Nhóm nút chỉ có 4 nút Ghi chú, Tạo lịch hẹn, Chỉnh sửa, Xóa khi drawer hiển thị | 1. Mở drawer F1. 2. Liệt kê các nút thao tác khách. | Đúng 4 nút theo thứ tự Figma: Ghi chú, Tạo lịch hẹn, Chỉnh sửa, Xóa. Không có nút "Nhận khách". | Ready | P1 |
| TC-DRW-026 | #159 | AC-08 | Phân vùng tương đương | F1 | Nhóm nút nằm trong summary card và cuộn cùng nội dung khi cuộn drawer | 1. Mở drawer F1 (nội dung dài hơn chiều cao). 2. Cuộn xuống. | Nhóm nút thuộc summary card, cuộn lên cùng nội dung, không sticky/cố định. | Ready | P1 |
| TC-DRW-027 | #160 | AC-08 | Bảng quyết định | F1 | Hiện message khi bấm nút Ghi chú | 1. Mở drawer F1. 2. Bấm nút "Ghi chú". | Hiện message "Tính năng đang phát triển"; không modal, không popup, không đổi tab. | Ready | P1 |
| TC-DRW-028 | #161 | AC-08 | Bảng quyết định | F1 | Hiện message khi bấm nút Tạo lịch hẹn | 1. Mở drawer F1. 2. Bấm nút "Tạo lịch hẹn". | Hiện message "Tính năng đang phát triển"; không modal, không popup. | Ready | P1 |
| TC-DRW-029 | #162 | AC-08 | Bảng quyết định | F1 | Hiện message khi bấm nút Chỉnh sửa | 1. Mở drawer F1. 2. Bấm nút "Chỉnh sửa". | Hiện message "Tính năng đang phát triển"; không modal, không popup; nút Xóa vẫn dùng được. | Ready | P1 |
| TC-DRW-030 | #163 | AC-09 | Chuyển trạng thái | F1 | Body ẩn và icon xoay khi bấm chevron thu gọn card Thông tin cá nhân | 1. Mở drawer F1, card đang mở. 2. Bấm chevron ở header card. | Body card ẩn, icon chevron xoay. | Ready | P1 |
| TC-DRW-031 | #164 | AC-09 | Chuyển trạng thái | F1 | Body hiện lại và icon xoay về khi bấm chevron lần 2 | 1. Thu gọn card. 2. Bấm chevron lần nữa. | Body hiện lại đủ trường; icon về vị trí ban đầu. | Ready | P2 |
| TC-DRW-032 | #165 | AC-10 | Phân vùng tương đương | F2 | Dòng Ngày sinh bị ẩn khi khách không có ngày sinh | 1. Mở drawer F2 (thiếu ngày sinh). | Dòng "Ngày sinh" (nhãn + giá trị) không xuất hiện trong card Thông tin cá nhân. | Ready | P1 |
| TC-DRW-033 | #166 | AC-10 | Phân vùng tương đương | F2 | Mọi dòng rỗng bị ẩn và không dùng dấu - khi khách thiếu nhiều trường | 1. Mở drawer F2 (thiếu ngày sinh, email...). | Các dòng thiếu dữ liệu đều ẩn; dòng có dữ liệu vẫn hiện; không có giá trị "-". | Ready | P1 |
| TC-DRW-034 | #167 | AC-10 | Phân vùng tương đương | F2 | Dòng bị ẩn với cả giá trị null, chuỗi rỗng và chuỗi chỉ có khoảng trắng | 1. Mock 3 khách: trường = null / "" / "   ". 2. Mở từng khách. | Cả 3 trường hợp: dòng ẩn. | Ready | P2 |
| TC-DRW-035 | #168 | AC-11 | Phân vùng tương đương | F6 | Hiển thị 3 SĐT kèm Xem thêm khi khách có 5 SĐT | 1. Mở drawer F6. | Mục SĐT hiển thị đúng 3 giá trị + link "Xem thêm". | Ready | P1 |
| TC-DRW-036 | #169 | AC-11 | Chuyển trạng thái | F6 | Hiện đủ mục và link đổi thành Rút gọn thông tin khi bấm Xem thêm | 1. Mở F6. 2. Bấm "Xem thêm" ở SĐT. | Hiện đủ 5 SĐT; link đổi thành "Rút gọn thông tin". | Ready | P1 |
| TC-DRW-037 | #170 | AC-11 | Chuyển trạng thái | F6 | Về 3 mục và link Xem thêm khi bấm Rút gọn thông tin | 1. Mở rộng SĐT. 2. Bấm "Rút gọn thông tin". | Về 3 SĐT; link "Xem thêm" trở lại. | Ready | P2 |
| TC-DRW-038 | #171 | AC-11 | Giá trị biên | F6 | Không hiện Xem thêm khi khách có đúng 3 mục | 1. Mở khách F6 biến thể đúng 3 mục SĐT/Email/DN/Sản phẩm. | Hiển thị đủ 3 mục; không có link "Xem thêm". | Ready | P1 |
| TC-DRW-039 | #172 | AC-11 | Giá trị biên | F6 | Hiện 3 mục và Xem thêm khi khách có đúng 4 mục | 1. Mở khách F6 biến thể đúng 4 mục. 2. Bấm "Xem thêm". | Ban đầu 3 mục + "Xem thêm"; mở rộng thấy đủ 4 mục + "Rút gọn thông tin". | Ready | P1 |
| TC-DRW-040 | #173 | AC-11 | Giá trị biên | F6 | Không hiện Xem thêm khi khách có 1 mục | 1. Mở khách có 1 SĐT, 1 Email, 1 DN, 1 Sản phẩm. | Hiển thị 1 mục mỗi trường; không có "Xem thêm". | Ready | P3 |
| TC-DRW-041 | #174 | AC-11 | Phân vùng tương đương | F6 | Quy tắc 3 mục áp dụng cho Email, Doanh nghiệp và Sản phẩm đã mua | 1. Mở F6 (5 SĐT, 5 Email, 5 DN, 5 Sản phẩm). 2. Kiểm từng trường; bấm Xem thêm / Rút gọn. | Mỗi trường: 3 mục + "Xem thêm" → đủ 5 + "Rút gọn thông tin" → về 3. | Ready | P1 |
| TC-DRW-042 | #175 | AC-11 | Phân vùng tương đương | F6 | Xem thêm của trường này không mở rộng trường khác | 1. Mở F6. 2. Bấm "Xem thêm" ở SĐT. | Chỉ SĐT mở rộng; Email, DN, Sản phẩm vẫn 3 mục. | Ready | P2 |
| TC-DRW-043 | #176 | AC-12 | Phân vùng tương đương | F3 | Card Thông tin mua hàng giữ 3 dòng giá trị trống khi khách chưa khớp đơn | 1. Mở drawer F3. | Card giữ đủ 3 dòng, giá trị để trống, không có "-". | Ready | P1 |
| TC-DRW-044 | #177 | AC-12 | Phân vùng tương đương | F4 | Tổng đơn hàng hiện 0 khi khách đã khớp nhưng không có đơn Completed | 1. Mở drawer F4. | "Tổng đơn hàng" hiển thị 0 (không trống, không "-"). | Ready | P1 |
| TC-DRW-045 | #178 | AC-12 | Bảng quyết định | F3,F4,F1 | Phân biệt đúng chưa khớp, đã khớp 0 đơn, đã khớp có đơn khi tổ hợp điều kiện khớp và số đơn Completed | Bảng: (chưa khớp, -) → trống; (đã khớp, 0 đơn Completed) → 0; (đã khớp, >0 đơn Completed) → số đơn đúng. Mở lần lượt F3, F4, F1. | Đúng 3 kết quả như bảng; không lẫn trống với 0. | Ready | P1 |
| TC-DRW-046 | #179 | AC-13 | Phân vùng tương đương | F5 | Dòng sản phẩm hiện Hết hạn màu error khi ngày hết hạn nhỏ hơn hôm nay | 1. Mở drawer F5. | Dòng sản phẩm hết hạn hiển thị "Hết hạn" màu error thay ngày hết hạn. | Ready | P1 |
| TC-DRW-047 | #180 | AC-13 | Giá trị biên | F5 | Sản phẩm hiện ngày bình thường khi ngày hết hạn đúng bằng hôm nay | 1. Mock sản phẩm hết hạn = hôm nay. 2. Mở drawer. | Hiển thị ngày hết hạn; không có "Hết hạn". | Ready | P1 |
| TC-DRW-048 | #181 | AC-13 | Giá trị biên | F5 | Sản phẩm hiện Hết hạn khi ngày hết hạn là hôm qua | 1. Mock sản phẩm hết hạn = hôm qua. 2. Mở drawer. | Hiển thị "Hết hạn" màu error. | Ready | P1 |
| TC-DRW-049 | #182 | AC-13 | Phân vùng tương đương | F5 | Chỉ dòng hết hạn đổi trạng thái khi danh sách có cả sản phẩm còn hạn | 1. Mock 1 sản phẩm hết hạn + 1 còn hạn. 2. Mở drawer. | Dòng hết hạn hiện "Hết hạn"; dòng còn hạn hiện ngày. | Ready | P2 |
| TC-DRW-050 | #183 | AC-14 | Chuyển trạng thái | F1,F10 | Tab Lịch hẹn active và nội dung hiển thị khi chuyển từ Thông tin sang Lịch hẹn | 1. Mở drawer F10 (tab Thông tin). 2. Bấm tab "Lịch hẹn". | Tab "Lịch hẹn" active, hiện nội dung lịch hẹn. | Ready | P1 |
| TC-DRW-051 | #184 | AC-14 | Chuyển trạng thái | F10 | Tab Thông tin hiển thị lại khi chuyển từ Lịch hẹn về Thông tin | 1. Ở tab Lịch hẹn. 2. Bấm tab "Thông tin". | Tab "Thông tin" active, hiện 2 card. | Ready | P1 |
| TC-DRW-052 | #185 | AC-14 | Bảng quyết định | F1 | Hiện message và giữ tab Thông tin khi bấm tab Ghi chú | 1. Mở F1 (tab Thông tin). 2. Bấm tab "Ghi chú". | Hiện message "Tính năng đang phát triển"; tab hiện tại vẫn "Thông tin"; nội dung không đổi. | Ready | P1 |
| TC-DRW-053 | #186 | AC-14 | Bảng quyết định | F1 | Hiện message và giữ tab Thông tin khi bấm tab Lịch sử | 1. Mở F1 (tab Thông tin). 2. Bấm tab "Lịch sử". | Hiện message "Tính năng đang phát triển"; tab hiện tại vẫn "Thông tin". | Ready | P1 |
| TC-DRW-054 | #187 | AC-14 | Chuyển trạng thái | F10 | Giữ tab Lịch hẹn khi bấm tab Ghi chú hoặc Lịch sử từ tab Lịch hẹn | 1. Ở tab Lịch hẹn. 2. Bấm "Ghi chú", rồi "Lịch sử". | Mỗi lần hiện message "Tính năng đang phát triển"; tab vẫn "Lịch hẹn". | Ready | P2 |
| TC-DRW-055 | #188 | AC-15 | Phân vùng tương đương | F10 | Lịch hẹn mới nhất nằm trên cùng khi khách có nhiều lịch hẹn | 1. Mở F10, tab Lịch hẹn. | Card "Lịch sử lịch hẹn" xếp theo thời gian giảm dần, mới nhất trên cùng. | Ready | P1 |
| TC-DRW-056 | #189 | AC-15 | Phân vùng tương đương | F10 | Danh sách gồm cả lịch hẹn đã qua và quá hạn | 1. Mở F10 (có lịch quá hạn), tab Lịch hẹn. | Lịch đã qua/quá hạn hiển thị cùng danh sách, đúng vị trí theo thời gian. | Ready | P1 |
| TC-DRW-057 | #190 | AC-15 | Phân vùng tương đương | F10 | Mỗi lịch hẹn có đủ tiêu đề, tag Ưu tiên, thời gian, dịch vụ, mô tả, người phụ trách | 1. Mở F10, tab Lịch hẹn. 2. Kiểm từng card. | Mỗi card có đủ 6 trường; không card nào thiếu trường. | Ready | P1 |
| TC-DRW-058 | #191 | AC-15 | Giá trị biên | F10 | Mô tả wrap nhiều dòng và không bị cắt khi mô tả rất dài | 1. Mock lịch hẹn mô tả rất dài (200 ký tự, có chuỗi không khoảng trắng). 2. Mở tab Lịch hẹn. | Mô tả wrap nhiều dòng, đọc đủ nội dung; không ellipsis, không tràn card. | Ready | P1 |
| TC-DRW-059 | #192 | AC-15 | Giá trị biên | F10 | Hiển thị đúng khi khách chỉ có 1 lịch hẹn | 1. Mock khách có đúng 1 lịch hẹn. | 1 card hiển thị đủ trường; không hiện empty state. | Ready | P3 |
| TC-DRW-060 | #193 | AC-15 | Phân vùng tương đương | F10 | Card lịch hẹn không có nút Sửa và Xóa khi xem tab Lịch hẹn | 1. Mở F10, tab Lịch hẹn. 2. Rà các nút trên card. | Không có nút Sửa/Xóa trên card (D3, theo Figma). | Ready | P2 |
| TC-DRW-061 | #194 | AC-16 | Phân vùng tương đương | F9 | Hiện Chưa có lịch hẹn nào khi khách không có lịch hẹn | 1. Mở F9, tab Lịch hẹn. | Hiển thị "Chưa có lịch hẹn nào."; không hiện lỗi/Thử lại. | Ready | P1 |
| TC-DRW-062 | #195 | AC-18 | Phân vùng tương đương | F12 | Chỉ khối Lịch hẹn hiện Thử lại khi API lịch hẹn lỗi và các khối khác thành công | 1. Mock API lịch hẹn 5xx, các API khác OK (F12). 2. Mở drawer. 3. Bấm tab Lịch hẹn. | Khối Lịch hẹn hiện lỗi + "Thử lại"; header và card tab Thông tin vẫn đủ dữ liệu. | Ready | P1 |
| TC-DRW-063 | #196 | AC-18 | Phân vùng tương đương | F12 | Tab Thông tin vẫn đủ dữ liệu khi khối Lịch hẹn lỗi | 1. Như TC trước. 2. Chuyển về tab Thông tin. | Tab Thông tin đủ dữ liệu, không lỗi. | Ready | P2 |
| TC-DRW-064 | #197 | AC-18 | Chuyển trạng thái | F12,F10 | Chỉ gọi lại API lịch hẹn và hiện dữ liệu khi bấm Thử lại ở khối Lịch hẹn | 1. Khối Lịch hẹn lỗi. 2. Đổi mock trả F10. 3. Bấm "Thử lại" trong khối. | Chỉ API lịch hẹn gọi lại (API chi tiết không gọi lại, header không loading); khối hiện danh sách lịch hẹn. | Ready | P1 |
| TC-DRW-065 | #198 | AC-21 | Phân vùng tương đương | F1 | Popup hiện đúng text xác nhận xóa vĩnh viễn khi bấm Xóa | 1. Mở drawer khách "KH-4F7A2C Nguyễn Văn A" (F1). 2. Bấm "Xóa". | Popup hiện đúng: "Xóa vĩnh viễn hồ sơ KH-4F7A2C Nguyễn Văn A ra khỏi doanh nghiệp?" kèm nút "Xác nhận" và "Đóng". | Ready | P1 |
| TC-DRW-066 | #199 | AC-21 | Chuyển trạng thái | F1 | Hồ sơ bị xóa, drawer đóng, danh sách tải lại khi bấm Xác nhận | 1. Bấm Xóa. 2. Bấm "Xác nhận". | Mock xóa khách; drawer đóng; danh sách tải lại, khách không còn; customerId bị xóa khỏi URL. | Ready | P1 |
| TC-DRW-067 | #200 | AC-21 | Chuyển trạng thái | F1 | Popup đóng và hồ sơ không bị xóa khi bấm Đóng | 1. Bấm Xóa. 2. Bấm "Đóng" trong popup. | Popup đóng; drawer vẫn mở; khách vẫn còn trong mock và danh sách. | Ready | P1 |
| TC-DRW-068 | #201 | AC-21 | Giá trị biên | F1 | Popup hiển thị đúng text khi tên khách rất dài hoặc có ký tự đặc biệt | 1. Mock khách tên 100+ ký tự, có dấu và ký tự đặc biệt (&, <, "). 2. Bấm Xóa. | Text chứa nguyên tên, không lỗi escape/HTML, popup không vỡ layout. | Ready | P2 |
| TC-DRW-069 | #202 | AC-22 | Phân vùng tương đương | - | Màu có token exact dùng class tds-color khi kiểm style | 1. Chạy tra token lookup cho các màu Figma của feature. 2. Với màu exact, kiểm DOM/template. | Mọi màu exact dùng class tds-color-*; không hard-code hex cho màu đó. | Ready | P1 |
| TC-DRW-070 | #203 | AC-22 | Phân vùng tương đương | - | Hex chỉ xuất hiện trong 1 file hằng và mỗi hex kèm TODO(token) khi rà soát toàn feature | 1. grep -rE '#[0-9A-Fa-f]{6}' trong thư mục feature. 2. Đếm file chứa hex. 3. Kiểm từng hex có comment TODO(token). | Hex chỉ ở đúng 1 file hằng; ngoài file đó = 0; mỗi hex kèm TODO(token). | Ready | P1 |
| TC-DRW-071 | #204 | AC-22 | Phân vùng tương đương | - | tsc --noEmit pass khi kiểm phi chức năng | 1. Chạy tsc --noEmit cho project. | Exit code 0, 0 lỗi. | Ready | P1 |
| TC-DRW-072 | #205 | AC-22 | Phân vùng tương đương | - | Không có any, DTO hậu tố Dto, import tds-ui sub-path, standalone khi rà phi chức năng | 1. Grep ': any\|as any\|<any>' trong feature. 2. Kiểm tên DTO. 3. Kiểm import tds-ui. 4. Kiểm component standalone. | 0 any; DTO kết thúc bằng Dto; import dạng tds-ui/<sub-path>; component standalone. | Ready | P2 |
| TC-DRW-073 | #206 | AC-17 | Chuyển trạng thái | F10 | [R2] Xóa lịch hẹn: popup, xác nhận, trạng thái khách về Đang tương tác | 1. Tab Lịch hẹn có "Demo Tpos Pro". 2. Bấm Xóa ở card. 3. Xác nhận. | Popup "Thao tác này sẽ xóa lịch hẹn [Demo Tpos Pro] ra khỏi Lịch sử lịch hẹn? Xóa xong không khôi phục được."; xác nhận: card bị xóa; nếu là lịch quá hạn cuối thì trạng thái khách về "Đang tương tác". Chặn: D3, cần Q15/Q18. | Blocked | P3 |
| TC-DRW-074 | #207 | AC-19 | Bảng quyết định | F1 | [R2] Modal Tạo lịch hẹn: mặc định, validate, tạo thành công | 1. Bấm Tạo lịch hẹn. 2. Kiểm mặc định, nút Tạo disabled khi thiếu Chủ đề/Dịch vụ/Ngày/Giờ. 3. Biên: Chủ đề 100/101 ký tự, Mô tả 200/201, Ngày = hôm nay/ngày mai. 4. Tạo. | Ưu tiên mặc định Thấp; Nhân viên mặc định là tôi; biên đúng spec; lịch mới ở đầu danh sách. Chặn: D1, R1 chỉ hiện message. | Blocked | P3 |
| TC-DRW-075 | #208 | AC-20 | Chuyển trạng thái | F1 | [R2] Modal Chỉnh sửa: nhóm nút disabled khi mở, tải lại khi lưu | 1. Bấm Chỉnh sửa. 2. Kiểm nhóm nút. 3. Lưu. | Modal mở, nhóm nút disabled tới khi đóng; lưu xong drawer tải lại; Lịch sử cập nhật có mục "Cập nhật thông tin khách hàng". Chặn: D1. | Blocked | P3 |
| TC-DRW-076 | #209 | AC-23 | Phân vùng tương đương | - | [R2] Tab Ghi chú hiển thị: mới nhất trên cùng, 5 ghi chú + Xem thêm | 1. Mở tab Ghi chú khách có >5 ghi chú. | Mới nhất trên cùng; avatar, tên, nội dung, thời gian dd/MM/yyyy HH:mm; 5 ghi chú + "Xem thêm" / "Thu gọn". Chặn: Q20, Figma 429. | Blocked | P3 |
| TC-DRW-077 | #210 | AC-23 | Phân vùng tương đương | - | [R2] Tab Ghi chú rỗng hiện Chưa có ghi chú | 1. Mở tab Ghi chú khách chưa có ghi chú. | Hiển thị "Chưa có ghi chú.". Chặn: Q20, Figma 429. | Blocked | P3 |
| TC-DRW-078 | #211 | AC-24 | Phân vùng tương đương | - | [R2] Tab Lịch sử: tương tác theo kênh Zalo, Website, Tổng đài | 1. Mở tab Lịch sử khách có 3 kênh. | Thanh dọc màu theo kênh, tên kênh, thời gian dd/MM/yyyy HH:mm, nội dung tối đa 120 ký tự, dòng mới đậm hơn, divider, cuộn dọc. Chặn: Q24. | Blocked | P3 |
| TC-DRW-079 | #212 | AC-24 | Chuyển trạng thái | - | [R2] Heatmap: hover tóm tắt, click lọc, ô rỗng không click, lọc reset khi đổi khách/tab, rỗng khách | 1. Hover ô Zalo-Tháng 3 (5 sự kiện). 2. Click ô có số. 3. Click ô 0. 4. Đổi khách/tab. 5. Chọn ô chỉ có hành động nội bộ. | Tóm tắt "Zalo · Tháng 3 · 5 sự kiện"; danh sách lọc theo kênh/tháng; ô 0 không click; lọc reset; ô nội bộ hiện "Không có hoạt động khách ở kênh đã chọn". Chặn: Q24. | Blocked | P3 |
| TC-DRW-080 | #213 | AC-24 | Giá trị biên | - | [R2] Lịch sử lazy-load 100 dòng khi cuộn tới cuối | 1. Mock 100, 101, 200 dòng. 2. Cuộn tới cuối. | Tải thêm 100 dòng kế; 100 dòng thì không tải thêm. Chặn: Q24. | Blocked | P3 |
| TC-DRW-081 | #214 | AC-24 | Phân vùng tương đương | - | [R2] Lịch sử chỉnh sửa gom theo ngày, nhóm gần nhất mở sẵn, chi tiết >3 dòng có Xem thêm | 1. Mở tab Lịch sử khách có thay đổi nhiều ngày. | Nhóm Hôm nay/Hôm qua/dd/MM/yyyy; nhóm gần nhất mở, còn lại gập; tiêu đề cố định; chi tiết "Nhãn: cũ -> mới"; >3 dòng cắt 3 + "Xem thêm". Chặn: Q24. | Blocked | P3 |
