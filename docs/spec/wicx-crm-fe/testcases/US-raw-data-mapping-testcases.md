# Bộ Test Case Kiểm Thử 5 Giai Đoạn ISTQB: Phân Hệ Ánh Xạ Dữ Liệu Thô (Raw Data Mapping)

> **Mã tài liệu:** `TC-SPEC-CDP-RAW-DATA-MAPPING-01`  
> **Áp dụng theo:** Chuẩn 5 giai đoạn ISTQB (Requirement Analysis -> Test Point Extraction -> ISTQB Techniques -> Executable Test Design -> Quality Gate)  
> **Parent Stories:**  
> - US #266: Cấu hình chung và lấy mẫu dữ liệu thô (Step 1)  
> - US #267: Quản lý sự kiện hành vi & Drawer tạo sự kiện tùy biến (Step 2)  
> - US #268: Ma trận ánh xạ trường & Bộ chuẩn hóa (Step 3)  
> - US #269: Chạy thử nghiệm & Quản lý lịch sử phiên bản (Step 4)  
> **QC Tasks:** #278, #279, #280, #277  
> **Chế độ phát triển:** TDD (Test-Driven Development) — QC viết test trước, Peer Dev HOLD chưa code.

---

## 1. Ma Trận Phủ Yêu Cầu & Acceptance Criteria (AC Coverage Matrix)

| User Story | Acceptance Criteria | Mã Test Case (ISTQB) | Kỹ thuật áp dụng |
|---|---|---|---|
| **US #266** (Step 1) | `AC-NAV-01`: Điều hướng tab Mapping dữ liệu | `TC-MAP-001`, `TC-MAP-002` | State Transition |
| | `AC-SRC-01`: Tìm kiếm & Lọc kênh Pane trái (320px) | `TC-MAP-003`, `TC-MAP-004`, `TC-MAP-005` | Equivalence Partitioning |
| | `AC-WIZ-01`: Chọn Channel liên kết & Event type từ JSON | `TC-MAP-006`, `TC-MAP-007` | Decision Table |
| | `AC-WIZ-02`: Xem trước JSON mẫu & Nút Copy | `TC-MAP-008`, `TC-MAP-009` | Boundary Value Analysis |
| | `AC-WIZ-03`: Lấy mẫu dữ liệu thô & Bảng 12 cột | `TC-MAP-010`, `TC-MAP-011`, `TC-MAP-012` | Equivalence + Boundary (Limit: 500, 1000, 2000) |
| **US #267** (Step 2) | `AC-EVT-01`: Bật/tắt lưu 9 sự kiện hành vi vào timeline | `TC-MAP-013`, `TC-MAP-014` | Decision Table |
| | `AC-EVT-02`: Drawer 720px tạo sự kiện tự định nghĩa | `TC-MAP-015`, `TC-MAP-016`, `TC-MAP-017` | State Transition + Regex |
| **US #268** (Step 3) | `AC-MAP-01`: Ma trận ánh xạ trường 5 cột | `TC-MAP-018`, `TC-MAP-019`, `TC-MAP-020` | Equivalence Partitioning |
| | `AC-MAP-02`: Bộ chuẩn hóa `CH-SDT` (E.164) | `TC-MAP-021`, `TC-MAP-022`, `TC-MAP-023` | BVA + Format Validation |
| | `AC-MAP-02`: Bộ chuẩn hóa `CH-EMAIL` | `TC-MAP-024`, `TC-MAP-025` | RFC 5322 Regex |
| | `AC-MAP-02`: Bộ chuẩn hóa `CH-TEN` & Độ tin cậy | `TC-MAP-026`, `TC-MAP-027`, `TC-MAP-028` | Decision Table |
| **US #269** (Step 4) | `AC-TEST-01`: Chạy thử (Dry Run) Trước vs Sau | `TC-MAP-029`, `TC-MAP-030`, `TC-MAP-031` | State Transition |
| | `AC-VER-01`: Lưu phiên bản (v3 -> v4), Sổ cái & Rollback | `TC-MAP-032`, `TC-MAP-033`, `TC-MAP-034` | Audit Log & State Machine |

---

## 2. Chi Tiết Test Cases Kiểm Thử 5 Giai Đoạn ISTQB

### Giai đoạn 1: Kiểm thử Bước 1 - Cấu hình chung & Lấy mẫu (Task #278 / US #266)

#### `TC-MAP-001` - [State Transition] Chuyển đổi giữa tab Dữ liệu thô và Mapping dữ liệu
- **Given:** Người dùng đang ở màn hình `/cdp/data-raw` (mặc định tab "Dữ liệu thô").
- **When:** Người dùng click vào tab "Mapping dữ liệu".
- **Then:** Tab "Mapping dữ liệu" chuyển sang active (viền dưới màu cam thương hiệu `#E05206`), URL cập nhật query param `?tab=mapping`, hiển thị Stepper 4 bước với Bước 1 "Cấu hình chung" đang active.

#### `TC-MAP-002` - [Edge Case] Truy cập trực tiếp link kèm query param
- **Given:** Người dùng mở trình duyệt vào URL `/cdp/data-raw?tab=mapping`.
- **When:** Component khởi tạo hoàn tất.
- **Then:** Hệ thống tự động active tab "Mapping dữ liệu" và render Pane trái với danh sách connector.

#### `TC-MAP-003` - [Equivalence Partitioning] Tìm kiếm kênh trên Pane trái theo tên hợp lệ
- **Given:** Danh sách kênh Pane trái có 7 connector (TPOS VN #01, HCM #02, ĐN #03, Facebook, Zalo, Partner A, Partner B).
- **When:** Người dùng nhập từ khóa `"Facebook"` vào ô tìm kiếm.
- **Then:** Danh sách chỉ hiển thị đúng 1 card kênh `Facebook`, các kênh khác bị ẩn.

#### `TC-MAP-004` - [Boundary Value] Tìm kiếm kênh không có kết quả
- **Given:** Danh sách kênh Pane trái.
- **When:** Người dùng nhập `"Tiki_NonExistent"`.
- **Then:** Danh sách hiển thị empty state `"Không tìm thấy kênh liên kết phù hợp"`.

#### `TC-MAP-005` - [State Transition] Chọn kênh trên Pane trái cập nhật chi tiết Pane phải
- **Given:** Kênh `TPOS - Store VN #01` đang được chọn.
- **When:** Người dùng click vào card `Facebook`.
- **Then:** Card `Facebook` chuyển sang trạng thái active (viền/nền primary minimalist), Header Pane phải cập nhật tên `Facebook`, loại `Social - Facebook`, endpoint và khung JSON mẫu tương ứng của Facebook.

#### `TC-MAP-006` - [Decision Table] Validate các trường bắt buộc của Bước 1
- **Given:** Người dùng đang ở Bước 1.
- **When:** Người dùng chưa chọn `Channel liên kết *` hoặc `Channel event type *` mà bấm "Lưu cấu hình".
- **Then:** Hệ thống ngăn lưu, viền đỏ các trường thiếu và hiển thị thông báo lỗi `TDSMessageService.error("Vui lòng chọn đầy đủ các trường khóa bắt buộc")`.

#### `TC-MAP-007` - [Equivalence Partitioning] Dropdown khóa tự động nạp từ JSON mẫu
- **Given:** Khung JSON mẫu có các trường `site_id`, `site`, `data.system_event_type`, `user_id`.
- **When:** Người dùng mở dropdown `Channel liên kết *`.
- **Then:** Danh sách tùy chọn hiển thị đầy đủ các key quét được từ JSON: `site_id`, `site`, `domain...`.

#### `TC-MAP-008` - [UI/UX] Khung xem trước JSON mẫu đánh số dòng chính xác
- **Given:** Pane phải hiển thị khung "Xem trước dữ liệu JSON (mẫu)".
- **When:** Payload JSON được tải.
- **Then:** Khung hiển thị code có số dòng từ 1 đến 14, format chuẩn thụt lề 2 spaces.

#### `TC-MAP-009` - [Functional] Sao chép JSON mẫu vào Clipboard
- **Given:** Khung JSON mẫu đang hiển thị.
- **When:** Người dùng click icon Copy `tdsi-copy-line`.
- **Then:** Chuỗi JSON được copy vào `navigator.clipboard` và hiển thị toast `TDSMessageService.success("Đã sao chép dữ liệu JSON mẫu vào clipboard")`.

#### `TC-MAP-010` - [Boundary Value Analysis] Giới hạn số lượng bản ghi lấy mẫu
- **Given:** Nhóm nút segmented: `500`, `1.000` (mặc định), `2.000`, `Tùy chỉnh`.
- **When:** Người dùng click chọn `2.000`.
- **Then:** Nút `2.000` chuyển màu cam `#E05206`, biến `recordLimit` cập nhật thành 2000.
- **When:** Người dùng chọn "Tùy chỉnh" và nhập `2.500`.
- **Then:** Hệ thống tự động giới hạn về trần tối đa `2.000` bản ghi/lần lấy và hiện tooltip cảnh báo.

#### `TC-MAP-011` - [State Transition] Lấy dữ liệu mẫu thành công nạp bảng phẳng 12 cột
- **Given:** Đã chọn khoảng thời gian và giới hạn bản ghi 1.000.
- **When:** Người dùng click "Lấy dữ liệu mẫu".
- **Then:** Nút hiển thị spinner loading; sau khi API trả về, hiển thị Tag `Đã tải thành công` màu xanh lá, text `Tổng: 1.000 bản ghi | 12 field`, và render TDS Data Table với đúng 12 cột (`#`, `event_id`, `site_id`, `site`, `data.system_event_type`, `user_id`, `page_url`, `form_id`, `form_value`, `created_at`, `...`).

#### `TC-MAP-012` - [Error Handling] Lỗi mạng khi lấy dữ liệu mẫu
- **Given:** Mạng ngắt kết nối hoặc Backend trả lỗi HTTP 500.
- **When:** Người dùng click "Lấy dữ liệu mẫu".
- **Then:** Tắt spinner loading, hiển thị `TDSMessageService.error("Không thể tải dữ liệu mẫu. Vui lòng thử lại sau.")` và giữ nguyên bảng rỗng.

---

### Giai đoạn 2: Kiểm thử Bước 2 - Quản lý sự kiện hành vi & Custom Event (Task #279 / US #267)

#### `TC-MAP-013` - [Decision Table] Bật/tắt lưu sự kiện hành vi vào dòng thời gian khách hàng
- **Given:** Danh sách 9 sự kiện hành vi (`form_submit`, `page_view`, `scroll`, `click`, ...).
- **When:** Người dùng gạt toggle "Lưu vào CDP" của sự kiện `scroll` sang `OFF`.
- **Then:** Trạng thái sự kiện `scroll` chuyển sang không lưu; các sự kiện `scroll` gửi về trong tương lai sẽ bị bỏ qua không ghi vào Timeline của Contact.

#### `TC-MAP-014` - [Equivalence Partitioning] Phân loại nguồn gốc sự kiện (Tracker vs Tự tạo)
- **Given:** Bảng sự kiện có 4 sự kiện từ Tracker và 5 sự kiện tự tạo.
- **When:** Người dùng bấm nút bộ lọc `"Tracker gửi về (4)"`.
- **Then:** Bảng lọc và chỉ hiển thị đúng 4 sự kiện có tag nguồn gốc `Tracker`.

#### `TC-MAP-015` - [State Transition] Mở Drawer tạo sự kiện tự định nghĩa
- **Given:** Tab Sự kiện hành vi.
- **When:** Người dùng click nút `+ Tạo sự kiện`.
- **Then:** Drawer chiều rộng `720px` slide-over từ phải sang, tiêu đề "Tạo sự kiện", backdrop mờ hiển thị.

#### `TC-MAP-016` - [Validation & Regex] Validate form tạo sự kiện trong Drawer
- **Given:** Drawer tạo sự kiện đang mở.
- **When:** Người dùng nhập Tên chuẩn CDP có khoảng trắng hoặc ký tự hoa (e.g. `View Pricing Table`).
- **Then:** Hệ thống tự động chuẩn hóa sang định dạng snake_case `view_pricing_table` và báo lỗi nếu có ký tự đặc biệt không hợp lệ.

#### `TC-MAP-017` - [Decision Table] Thiết lập điều kiện kích hoạt sự kiện (Trigger Rules)
- **Given:** Drawer tạo sự kiện.
- **When:** Người dùng chọn điều kiện: Trường `URL` + Toán tử `chứa` + Giá trị `/bang-gia`.
- **And:** Click "Lưu sự kiện".
- **Then:** Sự kiện mới được thêm vào danh sách sự kiện tự tạo của kênh với tag `Tự tạo`, đóng Drawer và hiển thị toast thành công.

---

### Giai đoạn 3: Kiểm thử Bước 3 - Ma trận Ánh xạ Trường & Chuẩn hóa (Task #280 / US #268)

#### `TC-MAP-018` - [Equivalence Partitioning] Hiển thị ma trận ánh xạ 5 cột
- **Given:** Đã lấy mẫu form `/dang-ky` có 4 trường input nguồn.
- **When:** Người dùng chuyển sang Bước 3 "Mapping field".
- **Then:** Bảng ma trận hiển thị 5 cột: `Trường dữ liệu nguồn`, `Giá trị mẫu gần nhất`, `Trường CDP`, `Quy tắc chuẩn hóa`, `Mức tin cậy`.

#### `TC-MAP-019` - [Decision Table] Ánh xạ trường nguồn sang trường CDP đích
- **Given:** Dòng trường nguồn `form.tds-input-1` có giá trị mẫu `"0969733325"`.
- **When:** Người dùng chọn dropdown `Trường CDP` là `phone`.
- **Then:** Hệ thống tự động gợi ý quy tắc chuẩn hóa tương ứng là `CH-SDT` và mức tin cậy `Cao`.

#### `TC-MAP-020` - [Equivalence Partitioning] Tùy chọn "Không lưu" trường nhạy cảm/rác
- **Given:** Trường nguồn `form.captcha_token`.
- **When:** Người dùng chọn trường CDP là `Không lưu`.
- **Then:** Dropdown Quy tắc chuẩn hóa bị disabled và trường này sẽ bị bỏ qua trong pipeline trích xuất.

#### `TC-MAP-021` - [BVA & Normalization] Chuẩn hóa số điện thoại VN sang chuẩn E.164 (`CH-SDT`)
- **Given:** Các giá trị số điện thoại đầu vào đa dạng.
- **Test Matrix:**
  * Đầu vào `"0969733325"` -> Kết quả kỳ vọng: `"+84969733325"`.
  * Đầu vào `"038 123 4567"` (có khoảng trắng) -> Kết quả: `"+84381234567"`.
  * Đầu vào `"84912345678"` (thiếu dấu +) -> Kết quả: `"+84912345678"`.
  * Đầu vào `"+84988776655"` (đã chuẩn) -> Kết quả giữ nguyên: `"+84988776655"`.
  * Đầu vào `"12345"` (không đủ độ dài SĐT) -> Kết quả: `null` (Báo lỗi validate).

#### `TC-MAP-022` - [Normalization] Chuẩn hóa Email (`CH-EMAIL`)
- **Given:** Các chuỗi email đầu vào.
- **Test Matrix:**
  * Đầu vào `"  Tan.Nguyen@Example.COM  "` -> Kết quả: `"tan.nguyen@example.com"`.
  * Đầu vào `"invalid-email.com"` -> Kết quả: `null` (Báo lỗi RFC 5322).

#### `TC-MAP-023` - [Normalization] Chuẩn hóa Họ tên (`CH-TEN`)
- **Given:** Chuỗi họ tên nhiều khoảng trắng thừa và viết lộn xộn.
- **Test Matrix:**
  * Đầu vào `"  nguyễn   văn   A  "` -> Kết quả: `"Nguyễn Văn A"`.
  * Đầu vào `"TRẦN ĐẠI PHÁT"` -> Kết quả: `"Trần Đại Phát"`.

#### `TC-MAP-024` - [Decision Table] Phân cấp độ tin cậy định danh (Confidence Levels)
- **Given:** Trường ánh xạ `phone`.
- **When:** Người dùng chọn mức tin cậy:
  * `Cao`: Ghi đè hoặc gộp hồ sơ ngay khi khớp SĐT.
  * `Trung bình`: Chỉ cập nhật nếu hồ sơ khách hiện tại chưa có SĐT.
  * `Thấp`: Lưu vào thuộc tính mở rộng, không kích hoạt merge định danh.

---

### Giai đoạn 4: Kiểm thử Bước 4 - Chạy thử (Dry Run) & Sổ cái Phiên bản (Task #277 / US #269)

#### `TC-MAP-025` - [State Transition] Chạy thử quy tắc ánh xạ trên bản ghi thực tế (Dry Run)
- **Given:** Đã cấu hình ma trận mapping ở Bước 3.
- **When:** Người dùng chuyển sang Bước 4 và click "Chạy thử".
- **Then:** Hệ thống hiển thị bảng đối chiếu Trước (Nguồn) vs Sau (CDP Target):
  * `form.tds-input-1 = "0969733325"` -> `phone = "+84969733325"`.
  * Tag xanh `Khớp chuẩn E.164, liên kết Hồ sơ KH #KH-09823`.

#### `TC-MAP-026` - [Audit & Versioning] Tự động tăng phiên bản khi Lưu cấu hình
- **Given:** Mapping hiện tại ở `Phiên bản 3`.
- **When:** Người dùng thay đổi 1 quy tắc ánh xạ và click "Lưu thay đổi".
- **Then:** Phiên bản tự động nâng lên `Phiên bản 4`, banner thông báo: *"Đã lưu thành phiên bản 4. Mapping mới áp dụng ngay cho dữ liệu nhận từ bây giờ."*

#### `TC-MAP-027` - [Audit Trail] Xem lịch sử thay đổi phiên bản (Review & Diff)
- **Given:** Có lịch sử 4 phiên bản (v1, v2, v3, v4).
- **When:** Người dùng truy cập màn hình "Lịch sử thay đổi" (`Review.dc.html`).
- **Then:** Danh sách hiển thị chi tiết từng phiên bản kèm thời gian, người thực hiện, và diff so sánh các trường bị thay đổi.

#### `TC-MAP-028` - [State Transition] Khôi phục (Rollback) về phiên bản cũ
- **Given:** Đang ở phiên bản 4.
- **When:** Người dùng chọn phiên bản 2 và click "Khôi phục phiên bản này".
- **Then:** Toàn bộ ma trận mapping của phiên bản 2 được nạp lại, sinh ra phiên bản 5 kế thừa từ bản 2 và hiển thị toast xác nhận.

---

## 3. Tiêu Chí Nghiệm Thu Độc Lập Cho QC Gate (Quality Gate Checklist)

Trước khi chuyển bất kỳ Task nào sang `Closed`:
1. [ ] 100% các Test Case (`TC-MAP-001` đến `TC-MAP-028`) có assertion rõ ràng, không được dùng `expect(true).toBe(true)`.
2. [ ] Unit test cho bộ chuẩn hóa regex (`CH-SDT`, `CH-EMAIL`, `CH-TEN`) chạy pass 100% trên `Vitest` / `Jest`.
3. [ ] Component specs mô phỏng đầy đủ hành vi click, select, input và error toast qua mock `TDSMessageService`.
4. [ ] Không có memory leak hoặc unhandled Observable subscription khi unmount component.
