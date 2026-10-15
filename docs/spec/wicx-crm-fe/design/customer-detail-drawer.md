# UI Spec: Drawer "Hồ sơ khách hàng" (CRM - Khách hàng)

- Harness: Feature #123
- Figma: file `yOglVOGf6KdoroEulwFYcg` (WiCX CRM UI v1 - Copy), node `1175:5513` ("Drawer", 768x1080)
- Phạm vi: CHỈ spec. Chưa code.
- Theme preset: `orange` (project `wicx`, `.agents/skills/ui-lib-figma/references/config/tds-project-token-map.json`), mode `light`
- Rule: https://github.com/baobao0303/cursor_rule_angular2026 (Angular 18 standalone, strict TS, import `tds-ui/<sub-path>`, DTO suffix `Dto`)

## 1. Luồng click

Figma node là frame `Drawer` (có header, nội dung cuộn, footer) => mở dạng **drawer phải**, không phải route/modal.

1. User ở trang danh sách Khách hàng, click 1 item ở cột "Khách hàng".
2. Mở `TDSDrawerService.create` (placement `right`, width 768) với `TDS_DRAWER_DATA = { customerId }`.
3. Drawer hiện loading (skeleton) -> gọi API chi tiết theo `customerId` -> render nội dung / empty / error.
4. Đóng: nút X header, nút "Đóng" footer, ESC, click mask. Đóng không reload danh sách (trừ khi sau Chỉnh sửa/Xóa thành công).
5. Click item khác khi drawer đang mở: thay `customerId`, quay lại loading.

Đã chốt (Q1): drawer + sync `?customerId=<id>` lên query param. Mở drawer -> set param; đóng -> xóa param. Vào URL có param (refresh/chia sẻ link) -> tự mở drawer đúng khách hàng. Không dùng route riêng.

## 2. Layout (theo node)

```text
Drawer 768x1080 (bg white)
|-- Header #1175:5514  (_item/drawer header, padding 8/16)
|     |-- "Hồ sơ khách hàng" (Heading/heading-6, 18/24 semibold)
|     `-- Button close (tdsi-close-fill)
|-- Body #1175:5515  (padding 16, gap 16, bg #F2F5F8, scroll)
|     |-- Summary card #1175:5534 (padding 12, radius 8, viền trên 4px màu primary)
|     |     |-- Avatar 80 (chữ "Đ") + Tên (20/28 semibold) + Tag "Đã định danh" (success, có icon)
|     |     |     `-- "Mã KH: KH-4F7A2C" (mã màu info)
|     |     |-- Divider
|     |     `-- Hàng trạng thái #1659:24044
|     |           |-- "Trạng thái khách hàng:" + Tag "Đang tương tác" (success minimal)
|     |           `-- Actions (Figma 4 nút): Ghi chú | Tạo lịch hẹn | Chỉnh sửa (button info outline XS) | Xóa (icon button error). BA thêm "Nhận khách" + sticky (Q23, Q25)
|     |-- Segment tabs #1659:42418: Thông tin (active) | Ghi chú | Lịch sử | Lịch hẹn
|     |-- Card "Thông tin cá nhân" #1659:24188 (collapsible, chevron-up)
|     |     Giới tính, Ngày sinh, Số điện thoại (+Tag "SĐT Chính", "/" SĐT phụ),
|     |     Email, Địa chỉ, Doanh nghiệp (list thẻ DN + "Rút gọn thông tin"),
|     |     Người phụ trách (avatar 24 + tên), Kênh nguồn (tag WiPix, Facebook),
|     |     Ngày tạo, Ngày hoạt động cuối
|     `-- Card "Thông tin mua hàng" #1659:24348
|           Tổng đơn hàng ("3 đơn hàng - Tổng tiền: 18.400.000 đ"),
|           Sản phẩm đã mua (tên x SL + icon lịch "Ngày hết hạn: dd/MM/yyyy"; hoặc "Hết hạn" màu error),
|           Quan tâm nhiều nhất (list "Sản phẩm (Báo giá ...)")
`-- Footer #1175:5517 (padding 8/16, viền trên) : Button secondary "Đóng"
```

Hàng thông tin: label cột trái cố định (200px; riêng "Doanh nghiệp" 180px - lệch Figma, Q9), giá trị cột phải. Card: bg white, radius 6, shadow `0 1px 3px rgba(29,45,73,.1)`; header card padding 12/16; body padding 12/16 gap 12.

## 3. Map Figma -> tds-ui

| Vùng / Figma evidence | tds-ui | Import | Ghi chú | Tin cậy |
|---|---|---|---|---|
| Drawer, header "Hồ sơ khách hàng", close (`_item/drawer header` 1175:5296, `Button close` 13:1818) | `TDSDrawerService` / `tds-drawer` (`title`, `closable`, `footer`) | `tds-ui/drawer` | `width=768` (preset max `xl`=780 không khớp), `placement='right'`, `maskClosable`, `keyboard` | high |
| Footer "Đóng" (`Button secondary` 13:4044, Style outline white/border) | `button tds-button-outline color="secondary"` | `tds-ui/button` | Đặt trong `footer` template | high |
| Avatar 80 chữ cái (`Avatar` 13:4661 Size=XL Circle; `_item/avatar style`) | `tds-avatar` `[text]` `[size]="80"` | `tds-ui/avatar` | Màu nền chữ theo style 7 (vàng) / style 4 (hồng, size 24): Q8 | medium |
| Tag "Đã định danh" (Flat, Success, có icon) | `tds-tag status="success"` | `tds-ui/tag` | icon leading `tdsi-*` check: Q8 | medium |
| Tag "Đang tương tác" (Flat Success minimal) | `tds-tag status="success"` `size="md"` | `tds-ui/tag` | | medium |
| Tag "SĐT Chính" (Without-o, Primary, size S) | `tds-tag status="primary" size="sm"` | `tds-ui/tag` | | medium |
| Tag kênh nguồn "WiPix", "Facebook" (Outline, Default) | `tds-tag type="outline" status="default"` | `tds-ui/tag` | | high |
| Ghi chú / Tạo lịch hẹn / Chỉnh sửa (`Button info` 87:2101, Outline XS, prefix icon) | `button tds-button-outline` size `xs`/`sm` + `tdsPrefixIcon` | `tds-ui/button` | Màu info; `ButtonSize` có `xs` (button.md) | medium |
| Xóa (`Button icon error` 276:3221, Outline XS) | `button tds-button-outline color="error"` icon-only `tdsi-trash-line` | `tds-ui/button` | Xác nhận xóa bằng popconfirm/modal: Q4 | medium |
| Segment Thông tin/Ghi chú/Lịch sử/Lịch hẹn (`_item/segment text item` 1659:24625) | `tds-segmented` `[tdsOptions]` `tdsBlock` `tdsColor="primary"` | `tds-ui/segmented` | Emit `tdsValueChange` (index). Nội dung 3 tab sau ngoài Figma: Q3 | high |
| Card "Thông tin cá nhân/mua hàng" (`_item/card view` 1175:5721 + `_item/card title group`) | `tds-card-view` (`tdsTitle` template, `tdsExtra` cho chevron) | `tds-ui/card-view` | Collapse bằng `tds-card-view` + state cục bộ, hoặc `tds-collapse`. Chốt khi code: Q5 | medium |
| Chevron thu gọn (`Button icon secondary` 13:559 Flat S) | `button tds-button` flat icon `tdsi-chevron-up-fill` | `tds-ui/button` | Xoay icon khi collapse | medium |
| "Rút gọn thông tin" (`Button text no spacing` 13:2514) | `button tds-button-text` + `tdsSuffixIcon="tdsi-chevron-up-fill"` | `tds-ui/button` | Toggle danh sách (tối đa 3 + "Xem thêm", BA A.3: Q22) | medium |
| Divider dưới summary | `tds-divider` | `tds-ui/divider` | | high |
| Icon `tdsi-*` (close-fill, edit-line, edit-file-line, calendar-check-line, calendar-line, trash-line, chevron-up-fill, user-fill, product-fill) | class `tdsi-*` | không import module (chỉ class CSS) | KHÔNG tải SVG. Xác nhận tên trong `node_modules/tds-ui/icon/list-icon.js` khi code | high |
| Loading | `tds-skeleton` | `tds-ui/skeleton` | | high |
| Empty | `tds-empty` | `tds-ui/empty` | | high |
| Error/Retry | `tds-empty` (`notFoundFooter` = nút "Thử lại") hoặc `TDSMessageService` (toast) | `tds-ui/empty`, `tds-ui/message` | Không có trong Figma: Q2 | low |
| Khối doanh nghiệp (nền #F5F8FB, radius 6, padding 8) | wrapper cục bộ `div` Tailwind | - | Không có component tds-ui tương đương, thuần cấu trúc | n/a |

Typography (class `tds-` prefix, không gộp weight): tiêu đề `tds-heading-6`; tên KH 20/28 semibold (kiểm tra có class; nếu không: Q8); label/giá trị `tds-body-2` (+ `font-semibold` cho giá trị); tag `tds-body-3 font-semibold`; tiêu đề card `tds-body-1 font-semibold`; nút caption `tds-caption-1 font-semibold`. Đặt `tds-body-2 tds-color-text-primary` một lần ở container body.

## 3b. Tab "Lịch hẹn" (node `1659:38575`, Drawer 768x1080)

Cùng khung header/summary/footer với node `1175:5513`; khác phần body: segment `Lịch hẹn` active (item cuối, bo phải 6, nền primary-500), bên dưới 1 card.

```text
Card view (white, radius 6, shadow s)
|-- Header: icon tdsi-calendar-check-line (20) + "Lịch sử lịch hẹn" (body-1 semibold)
`-- Body (padding 12/16, gap 12): danh sách item lịch hẹn (4 item mẫu)
      Item (nền neutral-lighten, radius 6, padding 8, gap 8)
      |-- Hàng 1: "Demo Tpos Pro" (body-1 semibold) + Tag "Ưu tiên cao" (primary, size S) ...... "12/03/2027 11:09" (body-3 regular, text-secondary)
      |-- "Dịch vụ: Tư vấn sản phẩm"
      |-- "Mô tả: <văn bản dài, wrap nhiều dòng>"
      `-- "Người phụ trách:" + avatar 24 (chữ "Đ", style 4 hồng) + "Minh Đạt"
```

Map: giống mục 3 (card `tds-card-view`, tag `tds-tag status="primary" size="sm"`, `tds-avatar size="24"`, icon `tdsi-calendar-check-line`). Item là wrapper cục bộ (không có component tds-ui). Danh sách không phân trang trong Figma (Q14).

## 3c. Item lịch sử tương tác theo kênh (nodes `1659:45163` Zalo, `1659:45205` Website, `1659:45247` Tổng đài)

Dùng cho tab "Lịch sử" (khớp ảnh export: danh sách dưới heatmap, có thêm kênh Facebook, màu Facebook chưa có: Q15). Node tab chưa đọc bằng API (429), xem 3d.

```text
List (704px, nền #F2F5F8, radius 4, padding 8, gap 8, vùng cuộn cao ~168px, scrollbar 4px bên phải)
|-- Row: [thanh dọc 4x40 màu kênh] + cột (gap 4)
|       |-- Hàng 1: Tên kênh (body-3 semibold, màu kênh) + thời gian "12/03/2027 11:09" (body-3 regular, #535A67)
|       `-- Nội dung (body-2 regular, đen), ví dụ "Thả cảm xúc lên bài viết của Page"
|-- Divider 1px
`-- ... lặp, 3 row hiển thị rồi cuộn
```

| Kênh | Màu thanh + tên kênh |
|---|---|
| Zalo | `#0569FA` |
| Website | `#FF4E00` |
| Tổng đài | `#1D8A24` |

Map: không có component tds-ui tương đương -> wrapper cục bộ Tailwind + `tds-divider` (`tds-ui/divider`); vùng cuộn dùng class `tds-panel-scroll` (4px, panel nội bộ) (xem `reference/css-utilities.md`, Figma dùng component `Scroll bar` 13:2035 Vertical Small). Màu kênh theo map động: `channel -> class` trong code, không hardcode hex (Q15).

## 3d. Tab "Ghi chú" và "Lịch sử" (nodes `1659:42786`, `1659:25223`) và node `1659:37648`

Nguồn: 5 ảnh export user gửi, đọc bằng OCR cục bộ (chỉ lấy TEXT + thứ tự; KHÔNG có màu, spacing, tên icon, kích thước). Figma API vẫn 429 nên chưa có node data. Mức tin cậy: text cao, layout trung bình, icon/màu thấp. Cần xác nhận lại bằng node data khi hết limit.

### Tab "Ghi chú" (`1659:42786`)

```text
Card view "Ghi chú" (icon + tiêu đề)
|-- Input "Nhập ghi chú, Enter để thêm" (icon gửi ở cuối; Enter = thêm)
`-- Danh sách ghi chú (mới nhất trên cùng, giả định)
      Item: avatar chữ cái + "Tên - Chức danh" + cụm icon thao tác bên phải (không đọc được: Q17)
            nội dung ghi chú (wrap)
            icon đồng hồ + "dd/MM/yyyy HH:mm"
```

Dữ liệu mẫu: "Hoàng Khôi - Nhân viên chăm sóc khách hàng", "Trần Minh Đạt - Quản lý cửa hàng", "Nguyễn Thanh Lam - Nhân viên chăm sóc khách hàng"; nội dung "Khách hàng bận thứ 2 gọi lại. Tư vấn dịch vụ", "Gia hạn gói TPOS". Danh sách dài, cuộn trong drawer.

Map: `tds-card-view`, `input[tdsInput]` (`tds-ui/tds-input`, trong `tds-form-field` `tds-ui/form-field`) + suffix icon `tdsi-*`, `tds-avatar size="24"` hoặc 32 (Q17). Item là wrapper cục bộ.

### Tab "Lịch sử" (`1659:25223`, `1659:37648` giả định là heatmap/phần bổ trợ, Q13)

```text
Card view "Lịch sử hoạt động" (icon) + gợi ý "Bấm vào các ô để xem lịch sử" (icon info)
|-- Heatmap: cột = tháng (OCR thấy Tháng 11 ... Tháng 06; BA chốt 6 tháng gần nhất, Q18; cuộn ngang)
|            hàng = Facebook | Zalo | Website | Tổng đài (BA thêm WiKaizen, Q15; chỉ lập dòng kênh có sự kiện)
|            ô = số lượng tương tác (ô trống nếu 0); click ô -> lọc danh sách bên dưới
`-- Danh sách tương tác của ô đang chọn (mục 3c): "Kênh  dd/MM/yyyy HH:mm" + nội dung
Card view "Lịch sử chỉnh sửa thông tin" (icon)
`-- Nhóm theo ngày: header "Hôm nay" + chevron (thu gọn/mở)
      Item: icon + "Cập nhật thông tin khách hàng" + thời gian "dd/MM/yyyy HH:mm"
            diff từng trường: "Giới tính: Nam -> Khác", "Đường: Nguyễn Trãi -> Lê Hồng Phong"
            link "Xem thêm" (mở rộng nếu nhiều trường)
            avatar 24 + tên người sửa ("Minh Đạt")
```

Map: heatmap KHÔNG có tds-ui tương đương -> wrapper cục bộ (grid Tailwind + `<button>` ô, có `aria-label` "<Kênh> <Tháng>: <n> tương tác"); cường độ màu ô theo số lượng: Q18. Nhóm ngày: `tds-collapse` hoặc card + state cục bộ (Q5). Diff: giá trị cũ gạch/mờ, giá trị mới nổi bật (chưa rõ từ ảnh: Q19).

### Cập nhật từ ảnh tab "Thông tin" (2.png, 3.png)

- Doanh nghiệp (Figma ảnh): thu gọn hiển thị 1 DN + "Xem thêm"; mở rộng tất cả DN; BA chốt tối đa 3 (Q22) + "Rút gọn thông tin" (chevron-up). Mỗi DN: tên, "Chức vụ / SĐT", địa chỉ.
- "Sản phẩm đã mua" có 3 dòng mẫu, dòng thứ 3 "WiOn.com - Gói Năm x 1" + "Hết hạn".
- "Quan tâm nhiều nhất": `TPOS.com (Báo giá bán hàng)`, `WiPix.com (Báo giá WiPix)`.

## 3e. Đối chiếu BA (vault Obsidian `/home/baoltb/Desktop/obsidian-obsidian/documents/BA/`)

Nguồn: `implementation-artifacts/stories/Phase 0.5_User_Stories/` -> `UC4.04 - Chi tiết hồ sơ khách hàng.md` (BR4.04-1..28, màn A.1-A.5, B.1-B.2), `UC4.02 - Hồ sơ khách hàng 360° (2 tab).md`, `UC4.01 - Danh sách contact, bộ lọc & Thao tác.md` (mục 2.1-2.4). Figma khớp Phase 0.5 (không phải Phase 1 "4 khối"). Đọc trực tiếp file (MCP obsidian không có trong phiên).

### Map tab Figma -> BA

| Tab Figma | BA |
|---|---|
| Thông tin | Tab Tổng quan: Khối Thông tin cá nhân (12 dòng) + Thông tin mua hàng (3 dòng) |
| Ghi chú | Khối Công việc, phần Ghi chú (A.5) |
| Lịch hẹn | Khối Công việc, phần Lịch sử lịch hẹn (A.5, A.5.1) |
| Lịch sử | Tab Hoạt động: tab con Lịch sử hoạt động (Hành trình B.1.1 + Lịch sử B.1.2) và Lịch sử cập nhật (B.2) |

### Rule chốt từ BA (áp vào spec)

- Header: nhãn Loại hồ sơ ("Đã định danh"/"Chưa định danh") + Trạng thái KH tự tính, user không đặt: Mới, Đang tương tác, Trễ hẹn chăm, Đã chốt, Đang nuôi dưỡng (BR4.04-13). Tag "Đang tương tác" trong Figma = 1 trong 5. Tag status map màu theo trạng thái: chưa có màu 4 trạng thái còn lại (Q21).
- Nhóm thao tác BA có 5 nút: Nhận khách, Chỉnh sửa, Ghi chú, Tạo lịch hẹn, Xóa; sticky, cả 2 tab. Figma chỉ có 4 (thiếu Nhận khách; BA: chỉ bấm được khi trạng thái "Mới", disable khi đã có người phụ trách). Mở modal Chỉnh sửa -> disable cả nhóm (BR4.04-12). Q4 phần lớn đã chốt (bảng dưới).
- Thông tin cá nhân chỉ hiển thị (không inline edit). Trường trống -> ẨN dòng (mục 5 cùng quy tắc). Thông tin mua hàng: giữ đủ 3 dòng, chưa khớp đơn -> để trống (KHÔNG dùng "-"); đã khớp chưa có đơn Completed -> hiện 0.
- SĐT/Email/Doanh nghiệp/Sản phẩm đã mua: hiển thị tối đa 3, còn nữa -> "Xem thêm". (Spec cũ ghi DN hiện 2 / Figma 1: Q22.) Nhãn "SĐT chính" chỉ ở SĐT, email không nhãn. Sản phẩm sort theo mua gần nhất giảm dần, gồm cả hết hạn.
- Ghi chú: mới nhất trên cùng, mặc định 5 dòng + "Xem thêm"/"Thu gọn"; mỗi dòng nội dung + người ghi + thời gian; rỗng: "Chưa có ghi chú.". Form Ghi chú (UC4.01 2.3): popover, textarea placeholder "Nhập mô tả ghi chú", tối đa 500 ký tự + bộ đếm, quá 500 -> bộ đếm đỏ + disable Lưu, Hủy khi đã nhập -> popup "Ghi chú chưa hoàn tất, bạn có muốn rời mà chưa hoàn tất không?" (Đóng/Rời khỏi). Figma tab Ghi chú có ô inline "Nhập ghi chú, Enter để thêm": LỆCH BA (Q20).
- Lịch hẹn: nhiều card/hồ sơ, mới nhất trên cùng, gồm cả lịch đã qua; card gồm Chủ đề, Ưu tiên (Thấp/Trung bình/Cao), ngày+giờ, Dịch vụ, Mô tả, Người phụ trách; mỗi card có nút Chỉnh sửa + Xóa (Xóa qua popup: "Thao tác này sẽ xóa lịch hẹn [<Chủ đề>] ra khỏi Lịch sử lịch hẹn? Xóa xong không khôi phục được." Xác nhận/Đóng). Rỗng: "Chưa có lịch hẹn nào.". Xóa lịch quá hạn cuối cùng -> trạng thái về Đang tương tác. Nút Chỉnh sửa/Xóa trên card không thấy trong dữ liệu Figma/OCR (Q23).
- Form Tạo lịch hẹn (UC4.01 2.4): Chủ đề (<=100, bắt buộc, có chữ cái), Dịch vụ (select, bắt buộc), Nhân viên liên hệ (select, bắt buộc, mặc định người tạo), Ưu tiên (radio Thấp/Trung bình/Cao, mặc định Thấp), Ngày hẹn (dd/MM/yyyy, > hôm nay), Giờ hẹn (select, theo khung trống của nhân viên), Mô tả (<=200). Nút Tạo disable khi Chủ đề/Dịch vụ/Ngày/Giờ trống. Form/modal này ngoài node Figma đã đọc (Q4 còn lại: có node Figma?).
- Xóa khách: popup "Xóa vĩnh viễn hồ sơ [mã KH] [tên khách] ra khỏi doanh nghiệp?" + Xác nhận (xóa hẳn, nhả định danh, về danh sách) / Đóng. Dùng `tds-modal`/popconfirm tùy Q4.
- Hành trình (heatmap): 6 tháng gần nhất (tháng hiện tại ngoài cùng phải, mặc định cuộn hết phải, cuộn ngang), chỉ lập dòng kênh có sự kiện (Facebook, Zalo, Website, Tổng đài, WiKaizen), ô trống không tương tác. Hover ô: menu tóm tắt "<Kênh> · Tháng N · X sự kiện" + từng loại sự kiện kèm số, giảm dần. Click ô: lọc Lịch sử theo kênh + tháng; hành động nội bộ vẫn giữ; hết dòng khách -> "Không có hoạt động khách ở kênh đã chọn". Lọc chỉ cho lần xem đó. Chưa có sự kiện: "Chưa có hoạt động".
- Lịch sử (B.1.2): mỗi dòng = thời gian dd/MM/yyyy HH:mm + nguồn (badge kênh có màu; hành động nội bộ = avatar + tên, không màu) + nội dung 1 dòng (<=120 ký tự). Dòng mới nhất đậm hơn. Lazy-load 100 dòng/trang. Cuộn reset khi đổi khách hoặc đổi tab.
- Lịch sử cập nhật (B.2): chỉ hành động của thành viên; tiêu đề cố định: "Cập nhật thông tin khách hàng", "Tạo lịch hẹn khách hàng", "Cập nhật ghi chú khách hàng", "Nhận khách hàng"; gom nhóm theo ngày ("Hôm nay", "Hôm qua", dd/MM/yyyy), mặc định mở nhóm gần nhất, nhóm khác gập; chi tiết `Nhãn: cũ -> mới` (chỉ trường đổi); >3 dòng -> 3 dòng + "Xem thêm"/"Thu gọn"; cuối card: người thực hiện + thời gian; lazy-load 20 card/lần. Trả lời Q19.
- Chỉnh sửa lưu chỉ ghi tại CRM, không ghi ngược nguồn. Tên trống để trống (không bù SĐT/email); avatar trống -> chữ cái đầu. Loading/lỗi: "đang tải" + nút "Thử lại" theo từng khối, khối đã có dữ liệu vẫn hiện (khớp mục 5; nên chia state theo khối).
- Hết hạn: không có RBAC/mask ở P0.5 (SĐT/email hiện nguyên văn).

### Mâu thuẫn BA vs Figma/spec

- BA (A.1) mô tả TRANG riêng + breadcrumb "Khách hàng -> Mã KH + Tên"; Figma là drawer; Q1 đã chốt drawer + `?customerId=`. Không phải lỗi, ghi nhận để BA đồng bộ (Q20b).
- BA tiêu đề tab: "Tổng quan/Hoạt động"; Figma: "Thông tin/Ghi chú/Lịch sử/Lịch hẹn". Theo Figma.

## 4. Token màu (tds-color), preset `orange`, light

Tra bằng `node .agents/skills/ui-lib-figma/scripts/tds-token-lookup.js <hex> <role> wicx orange light`.

| Dùng cho | Hex Figma | Role | Kết quả | Status |
|---|---|---|---|---|
| Text chính (tên, giá trị, tiêu đề) | `#0C1014` | text | `tds-color-text-primary` | exact |
| Thanh kênh + tên kênh Zalo / Website | `#0569FA` / `#FF4E00` | background / text | không có token | **missing** (Q15) |
| Thanh kênh + tên kênh Tổng đài | `#1D8A24` | text / background | `text-tds-color-green-600-light dark:text-tds-color-green-600-dark` / ambiguous (`background-success-subtle-hover`/`-pressed`) | exact (text) / **ambiguous** (bg) |
| Nội dung lịch sử | `#000000` | text | `text-tds-color-black-light dark:text-tds-color-black-dark` (khác `#0C1014` primary, Q16) | exact |
| Label cột trái, "Ngày hết hạn" giá trị | `#535A67` | text | `tds-color-text-quaternary` | exact |
| Tab chưa chọn, dấu "/" | `#7E8796` | text | `tds-color-text-secondary` | exact |
| "Ngày hết hạn:" label, tag channel text | `#656D7C` | text | `tds-color-text-placeholder` / `-inactive` / `-tertiary` | **ambiguous** (Q6) |
| Mã KH, chữ nút info | `#2A92FF` | text | `tds-color-text-info` / `tds-color-text-interactive` | **ambiguous** (Q6) |
| "Hết hạn" | `#EA2733` | text | `tds-color-text-error` | exact |
| Tag success text | `#2EB032` | text | `tds-color-text-success` | exact |
| Nền drawer, card, nút | `#FFFFFF` | background | `tds-color-background-white` | exact |
| Nền body drawer | `#F2F5F8` | background | `tds-color-background-neutral-minimalist` / `-disable` | **ambiguous** (Q6) |
| Nền khối doanh nghiệp | `#F5F8FB` | background | `tds-color-background-neutral-lighten` | exact |
| Viền trên summary card, tab active (nền) | `#F35431` | background / border | `bg-tds-color-primary-500-light dark:bg-tds-color-primary-500-dark` / `border-tds-color-primary-500-light dark:border-tds-color-primary-500-dark` | exact |
| Tag "SĐT Chính" nền | `#FFEBE5` | background | `bg-tds-color-primary-100-light dark:bg-tds-color-primary-100-dark` | exact |
| Tag "Đang tương tác" nền | `#DEF5D9` | background | `tds-color-background-success-minimal` | exact |
| Tag "Đã định danh" nền/viền | `#2EB032` | bg / border | `tds-color-background-success-subtle` / `tds-color-border-success` | exact |
| Viền nút info | `#2A92FF` | border | `tds-color-border-info` | exact |
| Viền nút xóa | `#EA2733` | border | `tds-color-border-error` | exact |
| Viền card/segment/divider/footer | `#DBE0E6` | border | `tds-color-border-primary` / `tds-color-border-disable` | **ambiguous** (Q6) |

Avatar style (đã tra): `#FFD6E7` bg -> `bg-tds-color-pink-100-light dark:bg-tds-color-pink-100-dark` (exact); `#C41D7C` text -> `text-tds-color-pink-600-light dark:text-tds-color-pink-600-dark` (exact); `#AD6800` text -> `text-tds-color-amber-700-light dark:text-tds-color-amber-700-dark` (exact); `#FFE58F` bg -> ambiguous (`tds-color-background-warning-minimal-hover`/`-pressed`) -> Q8. Cấm hardcode hex trong code. Alias render trực tiếp, không prefix `text-`/`bg-`/`border-`.

## 5. State

State theo KHỐI (header, Thông tin cá nhân, Thông tin mua hàng, Ghi chú, Lịch hẹn, Lịch sử hoạt động, Lịch sử cập nhật). Lỗi 1 khối không chặn khối khác (BA Exception Flow 2).

| State | Hiển thị | Nguồn |
|---|---|---|
| Loading lần đầu | Header + footer giữ nguyên; body `tds-skeleton` (avatar + title + 3 card). Nhóm nút thao tác disabled | Đề xuất (Q2) |
| Loading theo khối/tab | "Đang tải" (`tds-skeleton`) trong card của khối đó | BA + đề xuất |
| Loaded | Như Figma | Figma |
| Không tìm thấy (404) | `tds-empty` "Không tìm thấy khách hàng" + nút "Đóng" | Đề xuất |
| Lỗi tải từng khối | Khối lỗi hiện "Thử lại"; các khối khác giữ nguyên dữ liệu | BA |
| Lỗi tải header/chi tiết chính | `tds-empty` toàn drawer + "Thử lại" | Đề xuất |
| Lỗi thao tác (xóa/lưu/nhận khách) | Toast `TDSMessageService.error`, giữ nguyên form/popup | Đề xuất |
| Trường cá nhân rỗng | ẨN dòng (BR4.04-2). Không hiển thị "-" | BA |
| Thông tin mua hàng, chưa khớp đơn | Giữ đủ 3 dòng, giá trị để trống, KHÔNG dùng "-" (BR4.04-3) | BA |
| Thông tin mua hàng, đã khớp nhưng chưa có đơn Completed | Hiện `0` | BA |
| Chưa có ghi chú | "Chưa có ghi chú." | BA |
| Chưa có lịch hẹn | "Chưa có lịch hẹn nào." | BA |
| Chưa có hoạt động | "Chưa có hoạt động" | BA |
| Lọc heatmap không có dòng khách | "Không có hoạt động khách ở kênh đã chọn" | BA |
| Chưa có lịch sử cập nhật | Chưa có text BA | Q24 |
| Sản phẩm hết hạn | Thay "Ngày hết hạn" bằng "Hết hạn" `tds-color-text-error` | Figma |

Responsive: Figma chỉ có 768px; đề xuất `width: min(768px, 100vw)` (Q7).

## 6. Acceptance Criteria (BDD)

```gherkin
Feature: Chi tiết khách hàng dạng drawer

  Scenario: Mở chi tiết từ cột Khách hàng
    Given tôi đang ở trang danh sách Khách hàng
    When tôi click vào 1 khách hàng ở cột "Khách hàng"
    Then drawer "Hồ sơ khách hàng" mở từ bên phải, rộng 768px
    And drawer hiển thị loading cho đến khi dữ liệu trả về

  Scenario: Deep link qua query param
    When tôi mở URL danh sách Khách hàng kèm "?customerId=<id>" hoặc refresh khi drawer đang mở
    Then drawer tự mở đúng khách hàng đó
    When tôi đóng drawer
    Then "customerId" bị xóa khỏi URL

  Scenario: Hiển thị dữ liệu khách hàng
    Given API chi tiết trả dữ liệu hợp lệ
    Then tôi thấy avatar, tên, tag Loại hồ sơ, "Mã KH", "Trạng thái khách hàng"
    And tab "Thông tin" đang được chọn
    And card "Thông tin cá nhân" và "Thông tin mua hàng" hiển thị đúng trường như Figma

  Scenario: Đóng drawer
    Given drawer đang mở
    When tôi bấm nút X, nút "Đóng", phím ESC hoặc click mask
    Then drawer đóng và danh sách giữ nguyên vị trí cuộn và bộ lọc

  Scenario: Đổi khách hàng khi drawer đang mở
    Given drawer đang mở cho khách hàng A
    When tôi click khách hàng B ở danh sách
    Then drawer về loading rồi hiển thị khách hàng B

  Scenario: Thu gọn card
    Given card "Thông tin cá nhân" đang mở
    When tôi bấm chevron ở header card
    Then phần body ẩn và icon xoay

  Scenario: Ẩn trường cá nhân rỗng
    Given khách hàng không có "Ngày sinh"
    When drawer hiển thị
    Then dòng "Ngày sinh" không xuất hiện trong card "Thông tin cá nhân"

  Scenario: Giới hạn 3 mục và Xem thêm
    Given khách hàng có 5 SĐT (áp dụng tương tự Email, Doanh nghiệp, Sản phẩm đã mua)
    When drawer hiển thị
    Then hiển thị tối đa 3 mục kèm link "Xem thêm"
    When tôi bấm "Xem thêm"
    Then hiển thị tất cả mục và link đổi thành "Rút gọn thông tin"

  Scenario: Thông tin mua hàng, chưa khớp đơn
    Given khách chưa khớp đơn hàng nào
    When drawer hiển thị
    Then card "Thông tin mua hàng" giữ đủ 3 dòng với giá trị để trống và không dùng "-"

  Scenario: Thông tin mua hàng, đã khớp nhưng chưa có đơn Completed
    Given khách đã khớp nhưng không có đơn Completed
    When drawer hiển thị
    Then "Tổng đơn hàng" hiển thị 0

  Scenario: Sản phẩm hết hạn
    Given sản phẩm đã mua có ngày hết hạn nhỏ hơn hôm nay
    When card "Thông tin mua hàng" hiển thị
    Then dòng sản phẩm hiển thị "Hết hạn" màu error thay ngày hết hạn

  Scenario: Chuyển tab
    Given drawer đang mở tab "Thông tin"
    When tôi chọn tab "Ghi chú", "Lịch sử" hoặc "Lịch hẹn"
    Then nội dung tab tương ứng hiển thị

  Scenario: Tab Lịch hẹn
    Given khách có lịch hẹn
    When tôi chọn tab "Lịch hẹn"
    Then tab "Lịch hẹn" ở trạng thái active
    And card "Lịch sử lịch hẹn" liệt kê lịch hẹn mới nhất trên cùng, gồm cả lịch đã qua
    And mỗi lịch hẹn có tiêu đề, tag Ưu tiên, thời gian, dịch vụ, mô tả, người phụ trách
    And mô tả dài wrap nhiều dòng, không cắt

  Scenario: Tab Lịch hẹn rỗng
    Given khách chưa có lịch hẹn
    When tôi chọn tab "Lịch hẹn"
    Then hiển thị "Chưa có lịch hẹn nào."

  Scenario: Xóa lịch hẹn
    Given tab "Lịch hẹn" có lịch hẹn "Demo Tpos Pro"
    When tôi bấm "Xóa" ở card lịch hẹn đó
    Then popup hiển thị "Thao tác này sẽ xóa lịch hẹn [Demo Tpos Pro] ra khỏi Lịch sử lịch hẹn? Xóa xong không khôi phục được."
    When tôi bấm "Xác nhận"
    Then card bị xóa
    And nếu là lịch quá hạn cuối cùng thì trạng thái khách về "Đang tương tác"

  Scenario: Tạo lịch hẹn
    Given drawer đang mở
    When tôi bấm "Tạo lịch hẹn"
    Then modal form mở với Ưu tiên mặc định "Thấp" và Nhân viên liên hệ mặc định là tôi
    And nút "Tạo" disabled khi thiếu Chủ đề, Dịch vụ, Ngày hẹn hoặc Giờ hẹn
    And Ngày hẹn phải sau hôm nay, Chủ đề tối đa 100 ký tự và có chữ cái, Mô tả tối đa 200 ký tự
    When tôi tạo thành công
    Then lịch hẹn mới xuất hiện đầu danh sách tab "Lịch hẹn"

  Scenario: Nhận khách
    Given trạng thái khách là "Mới" và chưa có người phụ trách
    When drawer hiển thị
    Then nút "Nhận khách" bật
    When tôi bấm "Nhận khách"
    Then khách gán cho tôi, nút "Nhận khách" disabled
    And Lịch sử cập nhật có mục "Nhận khách hàng"

  Scenario: Nhận khách bị khóa
    Given khách đã có người phụ trách hoặc trạng thái "Đã chốt"
    When drawer hiển thị
    Then nút "Nhận khách" disabled

  Scenario: Chỉnh sửa khách hàng
    Given drawer đang mở
    When tôi bấm "Chỉnh sửa"
    Then modal chỉnh sửa mở và cả nhóm nút thao tác disabled cho đến khi đóng modal
    When tôi lưu thành công
    Then drawer tải lại dữ liệu
    And Lịch sử cập nhật có mục "Cập nhật thông tin khách hàng"

  Scenario: Xóa khách hàng
    Given drawer đang mở cho khách "KH-4F7A2C Nguyễn Văn A"
    When tôi bấm nút "Xóa"
    Then popup hiển thị "Xóa vĩnh viễn hồ sơ KH-4F7A2C Nguyễn Văn A ra khỏi doanh nghiệp?"
    When tôi bấm "Xác nhận"
    Then hồ sơ bị xóa, drawer đóng, danh sách tải lại
    When tôi bấm "Đóng" thay vì "Xác nhận"
    Then popup đóng, hồ sơ không bị xóa

  Scenario: Lịch sử tương tác theo kênh
    Given khách có tương tác qua Zalo, Website, Tổng đài
    When tôi chọn tab "Lịch sử"
    Then mỗi dòng hiển thị thanh dọc màu theo kênh, tên kênh, thời gian dd/MM/yyyy HH:mm, nội dung tối đa 120 ký tự
    And dòng mới nhất đậm hơn
    And các dòng ngăn cách bằng divider
    And vùng danh sách cuộn dọc khi vượt chiều cao

  Scenario: Heatmap hover
    Given heatmap có ô Zalo, Tháng 3 với 5 sự kiện
    When tôi hover ô đó
    Then hiển thị tóm tắt "Zalo · Tháng 3 · 5 sự kiện" kèm từng loại sự kiện giảm dần

  Scenario: Heatmap lọc
    Given heatmap có ô có số lượng
    When tôi click 1 ô có số lượng
    Then danh sách bên dưới chỉ hiển thị tương tác của kênh và tháng đó
    And ô không có sự kiện không click được
    And bộ lọc không còn khi tôi đổi khách hoặc đổi tab

  Scenario: Heatmap lọc không có dòng khách
    Given ô được chọn chỉ có hành động nội bộ
    When danh sách lọc
    Then hiển thị "Không có hoạt động khách ở kênh đã chọn"

  Scenario: Lịch sử lazy-load
    Given có hơn 100 dòng lịch sử hoạt động
    When tôi cuộn tới cuối danh sách
    Then tải thêm 100 dòng kế tiếp

  Scenario: Lịch sử cập nhật
    Given khách có thay đổi thông tin
    When tôi chọn tab "Lịch sử"
    Then card "Lịch sử chỉnh sửa thông tin" gom theo ngày ("Hôm nay", "Hôm qua", dd/MM/yyyy)
    And nhóm gần nhất mở sẵn, nhóm khác gập
    And mỗi mục có tiêu đề cố định ("Cập nhật thông tin khách hàng", "Tạo lịch hẹn khách hàng", "Cập nhật ghi chú khách hàng", "Nhận khách hàng"), chi tiết "Nhãn: cũ -> mới", người thực hiện, thời gian
    And chi tiết dài hơn 3 dòng thì hiện 3 dòng kèm "Xem thêm"

  Scenario: Tab Ghi chú (hiển thị)
    Given khách có ghi chú
    When tôi chọn tab "Ghi chú"
    Then ghi chú mới nhất trên cùng, mỗi ghi chú có avatar, tên, nội dung, thời gian dd/MM/yyyy HH:mm
    And mặc định hiển thị 5 ghi chú kèm "Xem thêm", mở rộng thì có "Thu gọn"

  Scenario: Tab Ghi chú rỗng
    Given khách chưa có ghi chú
    When tôi chọn tab "Ghi chú"
    Then hiển thị "Chưa có ghi chú."

  Scenario: Lỗi theo khối
    Given API tab "Lịch hẹn" lỗi, các khối khác thành công
    When tôi mở tab "Lịch hẹn"
    Then chỉ khối Lịch hẹn hiển thị "Thử lại"
    And các khối khác vẫn hiển thị dữ liệu

  Scenario: Khách hàng không tồn tại
    Given API trả 404
    When drawer tải dữ liệu
    Then drawer hiển thị empty "Không tìm thấy khách hàng"

  Scenario: Lỗi tải chi tiết
    Given API chi tiết lỗi 5xx hoặc mất mạng
    When drawer tải dữ liệu
    Then drawer hiển thị lỗi với nút "Thử lại"
    When tôi bấm "Thử lại"
    Then hệ thống gọi lại API và hiển thị loading

  Scenario: Tính năng chưa phát triển (tab)
    Given drawer đang mở tab "Thông tin"
    When tôi bấm tab "Ghi chú" hoặc "Lịch sử"
    Then hiển thị message "Tính năng đang phát triển"
    And tab hiện tại giữ nguyên

  Scenario: Tính năng chưa phát triển (nút)
    Given drawer đang mở
    When tôi bấm nút "Ghi chú", "Tạo lịch hẹn" hoặc "Chỉnh sửa"
    Then hiển thị message "Tính năng đang phát triển"
    And không có modal hay popup nào mở

  Scenario: Nhóm nút theo Figma
    When drawer hiển thị
    Then nhóm nút nằm trong summary card và cuộn cùng nội dung
    And chỉ có 4 nút: Ghi chú, Tạo lịch hẹn, Chỉnh sửa, Xóa

  Scenario: Màu sắc theo token
    When tôi kiểm tra style
    Then màu có token exact dùng class tds-color
    And màu ambiguous hoặc missing dùng màu Figma trong 1 file hằng kèm TODO(token)
```

Cách nhập ghi chú (inline hay popover) CHƯA chốt, nên không có AC nhập ghi chú; xem Q20.

## 7. Câu hỏi mở / Quyết định

### Quyết định của user (2026-10-14)

- D1. Tính năng chưa phát triển (tab Ghi chú, tab Lịch sử, nút Ghi chú, Tạo lịch hẹn, Chỉnh sửa): bấm hiện `TDSMessageService.info` "Tính năng đang phát triển", không mở gì.
- D2. Token: có token exact thì dùng class `tds-color-*`; ambiguous/missing thì dùng màu Figma, đặt trong 1 file hằng, `TODO(token)`. Thay thế mọi "ĐỀ XUẤT" token trong Q6, Q8, Q15, Q18, Q21.
- D3. "Còn lại như Figma": Q23 = không thêm Nhận khách và Sửa/Xóa card lịch hẹn; Q25 = nhóm nút trong summary card, cuộn theo; AC Nhận khách, Tạo lịch hẹn, Chỉnh sửa, Xóa lịch hẹn, tab Ghi chú/Lịch sử nội dung: HOÃN Release 2. (D3 suy ra từ lời user; chưa xác nhận riêng.)

Các scenario Nhận khách, Chỉnh sửa, Tạo lịch hẹn, Xóa lịch hẹn, tab Ghi chú rỗng/hiển thị, Lịch sử ở mục 6 là Release 2, KHÔNG làm ở Release 1.

Ký hiệu: CHỐT = có căn cứ (user hoặc BA hoặc tài liệu tds-ui). MỞ = chưa có căn cứ, cần user/designer/BE/BA. ĐỀ XUẤT = ý Lead, chưa duyệt.

### Đã chốt

- Q1. CHỐT (user): drawer + `?customerId=`.
- Q2. CHỐT: state theo khối ở mục 5 (loading/empty/error không có trong Figma, đề xuất của Lead). User duyệt mục 5 là coi như chốt.
- Q3. CHỐT: 4 tab (Thông tin, Ghi chú, Lịch sử, Lịch hẹn) theo Figma. Tab Ghi chú/Lịch sử chỉ ở mức text (OCR).
- Q4. CHỐT hành vi theo BA: Xóa = xóa vĩnh viễn + popup xác nhận; Chỉnh sửa = modal UC4.01 2.2, disable nhóm nút khi mở; Tạo lịch hẹn = modal form UC4.01 2.4. Component: `tds-ui/modal` + `tds-ui/form-field` + `tds-ui/tds-input`. MỞ: layout form chưa có node Figma.
- Q5. CHỐT: `tds-card-view` + signal cục bộ cho collapse "Thông tin cá nhân" (có chevron trong Figma); "Thông tin mua hàng" không collapse.
- Q9. CHỐT: label width 200px. 180px ở hàng "Doanh nghiệp" coi là lỗi design.
- Q10. CHỐT: `ButtonSize` hỗ trợ `xs` (`reference/docs/button.md`). Nút info outline dùng `xs` như Figma.
- Q12. CHỐT: lỗi `\\(` trong text "Quan tâm nhiều nhất" là artifact export, hiển thị `(`.
- Q16. CHỐT: nội dung lịch sử dùng `tds-color-text-primary` thay `#000000` (giống mọi text chính).
- Q22. CHỐT theo BA (BR4.04 màn A.3): tối đa 3 mục + "Xem thêm"/"Rút gọn thông tin" cho SĐT/Email/Doanh nghiệp/Sản phẩm đã mua. Figma chỉ minh họa 1-2 mục.

### Còn mở (cần người quyết, không tự chốt)

- Q6. Token ambiguous (lookup `orange`/`light`): `#656D7C` text (`placeholder`/`inactive`/`tertiary`), `#2A92FF` text (`info`/`interactive`), `#F2F5F8` nền (`neutral-minimalist`/`disable`), `#DBE0E6` viền (`primary`/`disable`). ĐỀ XUẤT: `tds-color-text-tertiary`, `tds-color-text-info`, `tds-color-background-neutral-minimalist`, `tds-color-border-primary`. Cần designer xác nhận variable name.
- Q7. Hành vi < 768px. ĐỀ XUẤT: `width: min(768px, 100vw)`.
- Q8. Avatar chữ cái: nền/chữ theo hash tên hay cố định? `#FFE58F` nền: lookup ambiguous (`tds-color-background-warning-minimal-hover`/`-pressed`); `#FFF1B8` mới là `tds-color-background-warning-minimal`. Cần designer chốt. Còn: class typography tên KH 20/28 semibold, icon tag "Đã định danh".
- Q11. Contract API chi tiết khách hàng (endpoint, `CustomerDetailDto`, phân trang tab, format). Chưa có contract BE. Mục 9 dùng interface mock, đổi theo BE khi có.
- Q13. `1659:37648` chưa rõ là phần nào (giả định heatmap). Kiểm khi Figma hết 429.
- Q14. Tab Lịch hẹn: BA chốt mới nhất trên cùng + gồm lịch đã qua + 3 mức Ưu tiên (Thấp/Trung bình/Cao). BA/Figma chưa nêu phân trang, màu tag Thấp/Trung bình (Figma chỉ "Ưu tiên cao" = primary), card có click không.
- Q15. Màu kênh: `#0569FA` (Zalo), `#FF4E00` (Website) lookup `missing`; `#1D8A24` bg ambiguous (`success-subtle-hover`/`-pressed`); Facebook chưa có màu; WiKaizen (BA có) chưa có trong Figma. Không hardcode hex; chờ designer cho token hoặc cho phép màu cục bộ.
- Q17. Tab Ghi chú: icon thao tác bên phải mỗi ghi chú (BA không có sửa/xóa ghi chú); chức danh người ghi "Nhân viên chăm sóc khách hàng" (BA chỉ nêu avatar + tên); avatar size.
- Q18. Heatmap: BA chốt 6 tháng gần nhất, cuộn ngang, hover menu, click lọc. Còn mở: thang màu ô theo số lượng ("designer chốt"), click lại ô có bỏ lọc không. OCR Figma có 8 cột nhưng BA thắng (6).
- Q19. Lịch sử cập nhật: kiểu hiển thị giá trị cũ/mới (BA không nêu; Figma ảnh không rõ màu).
- Q20. Ghi chú: Figma có ô inline "Nhập ghi chú, Enter để thêm"; BA UC4.01 2.3 là popover textarea (500 ký tự, Lưu/Hủy, popup "Ghi chú chưa hoàn tất, bạn có muốn rời mà chưa hoàn tất không?" Đóng/Rời khỏi). Chọn Figma, BA, hoặc kết hợp? Nút "Ghi chú" ở nhóm nút làm gì (Figma không có footer Ghi chú)? Q20b: BA mô tả TRANG + breadcrumb, Figma là drawer: BA cần cập nhật.
- Q21. Màu tag 5 Trạng thái KH (Mới, Đang tương tác, Trễ hẹn chăm, Đã chốt, Đang nuôi dưỡng) và Loại hồ sơ (Đã định danh / Chưa định danh). Figma chỉ có "Đang tương tác" (success minimal) và "Đã định danh" (success).
- Q23. Card lịch hẹn: BA có nút Chỉnh sửa + Xóa mỗi card, Figma không thấy. Nút "Nhận khách" (BA) vắng ở Figma: thiếu hay cố ý? Form Tạo lịch hẹn/Chỉnh sửa/Xóa chưa có node Figma.
- Q24. Trạng thái trống của "Lịch sử cập nhật": BA không nêu text.
- Q25. ĐÃ CHỐT (D3): theo Figma, nhóm nút trong summary card, cuộn theo. BA BR4.04-9 yêu cầu sticky: BA cần đồng bộ.

### Ghi chú về phạm vi

- Luật tự tính 5 trạng thái khách (BR4.04-13, UC4.05) là logic BE; FE chỉ hiển thị `status` nhận từ API.
- Link Figma cũ (`uHeLU9Im5mK4BVcAxUDVtj`) 429, thay bằng bản copy `yOglVOGf6KdoroEulwFYcg`. Cần user xác nhận copy = bản gốc.

## 8. Evidence / gap

- `get_figma_data` node `1175:5513`, `1659:38575`, `1659:45163`, `1659:45205`, `1659:45247`: OK. Không tải ảnh (icon là `tdsi-*`).
- Node `1659:42786`, `1659:25223`, `1659:37648`: 429 (starter plan, retry-after ~399.000s, đổi token không giúp). Tab Ghi chú/Lịch sử lấy từ 5 ảnh export + OCR `tesseract.js` (chỉ text/thứ tự, có lỗi dấu).
- BA đọc trực tiếp vault Obsidian (MCP không khả dụng); mục 3e.
- Token lookup `orange`/`light`: ambiguous và missing như mục 4 và Q6/Q8/Q15.
- Chưa chụp screenshot; chưa so khớp pixel. Chưa có `projects/wicx-crm-fe/spec.md`.

## 9. Kế hoạch triển khai (mock data trước, UI sau)

Mục đích: dựng UI chạy được trên mock, BE khớp sau. Đường dẫn file do Peer chọn theo cấu trúc app (chưa có app trong repo này).

1. Mock data (làm trước)
   - `CustomerDetailDto`, `CustomerAppointmentDto`, `CustomerNoteDto`, `CustomerActivityDto`, `CustomerChangeLogDto` trong 1 file `*.dto.ts` (interface, suffix `Dto`, strict, không `any`). Contract là TẠM (Q11).
   - Fixture + service mock trả `Observable` có độ trễ giả (`delay`) để thấy loading. Service có interface để đổi sang HTTP không đổi UI.
   - Ca fixture bắt buộc: đủ dữ liệu; thiếu trường (ẩn dòng); chưa khớp đơn (để trống); đã khớp 0 đơn (`0`); sản phẩm hết hạn; >3 SĐT/Email/DN/Sản phẩm (Xem thêm); 404; lỗi 5xx; lịch hẹn rỗng; ghi chú rỗng (và >5); hoạt động rỗng; heatmap 6 tháng.
2. UI theo thứ tự
   - 2a. Drawer shell + `?customerId=` + loading/404/error (mục 1, 5).
   - 2b. Header + trạng thái + nhóm nút (cần Q20, Q21, Q23, Q25 để chốt nút/màu; dựng theo Figma, nút Nhận khách theo BA, bật/tắt theo status).
   - 2c. Tab "Thông tin" (đủ node Figma, token mục 4; ambiguous dùng đề xuất Q6 và đánh dấu TODO).
   - 2d. Tab "Lịch hẹn" (node `1659:38575`).
   - 2e. Modal Tạo lịch hẹn/Chỉnh sửa/popup Xóa (theo BA; layout chờ Q4).
   - 2f. Tab "Ghi chú" và "Lịch sử": CHẶN bởi Figma 429 và Q15, Q17, Q18, Q19, Q20.
3. Kiểm tra: `npx tsc -p tsconfig.json --noEmit`; mở drawer trong trình duyệt với từng ca fixture; kiểm tra không hardcode hex (grep `#[0-9A-Fa-f]{6}` trong feature).

### Cập nhật 2026-10-14 (đợt 5, sau review)

- Review song song (Standards + Spec): đã vá các lỗi hard (import path, token, mâu thuẫn, luật rỗng/0, "Nhận khách", WiKaizen, popup text). Các quyết định không có căn cứ (Q11, Q14, Q15, Q17-Q21, Q23, màu heatmap/tag) trả về MỞ kèm ĐỀ XUẤT.
