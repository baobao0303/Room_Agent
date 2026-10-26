# Tiêu Chuẩn Các Ca Kiểm Thử Website Cơ Bản (Web Component Test Matrix)

Tài liệu chuẩn hóa danh mục test case kiểm thử giao diện & thành phần web dành riêng cho Agent **QC** trong chu trình **SLPC Gate 4 (ISTQB 5-Stage Unit Test & Testcase Generation)**. Mọi file unit test (`*.spec.ts` / `test_*.py`) và work item `Testcase` khi sinh ra từ `tools/qc_test_generator.py` phải đối chiếu và bao phủ các trường hợp tương ứng với từng loại component.

---

## 1. Testcases for Textbox (Ô Nhập Liệu)
- Kiểm tra các ký tự alpha hoặc ký tự chữ.
- Kiểm tra nhập giá trị số âm, số nguyên, số thập phân.
- Kiểm tra dữ liệu đầu vào là khoảng trắng (space / whitespace trimming).
- Kiểm tra dữ liệu đầu vào chứa ký tự đặc biệt (!@#$%^&*...).
- Kiểm tra điều kiện bắt buộc (Required field) nếu được cung cấp.
- Kiểm tra textbox có được bỏ trống hay không theo quy định.
- Kiểm tra giới hạn ký tự Min – Max (Boundary Value Analysis - BVA).
- Kiểm tra có thể sao chép và dán (Copy / Paste) ký tự vào textbox.
- Kiểm tra nút “Tab” trên bàn phím có di chuyển qua các textbox theo đúng tab-index.
- Kiểm tra placeholder hiển thị đúng ngữ pháp, hợp lý và biến mất khi gõ.
- Kiểm tra không thể chỉnh sửa khi textbox bị disable / readonly.
- Kiểm tra khi textbox disable thì chuyển sang màu xám và con trỏ chuyển dạng `not-allowed`.

---

## 2. Testcases for Button (Nút Bấm)
- Kiểm tra button có hiện trên trang web đúng như bản design (Figma).
- Kiểm tra màu sắc, icon của button đúng chuẩn token (`tds-color-*`).
- Kiểm tra kích thước của button (sm, md, lg) và độ co giãn trên các thiết bị.
- Kiểm tra button có hoạt động khi click vào (trigger event handler).
- Kiểm tra chức năng của button có đúng nghiệp vụ hay không.
- Kiểm tra các giá trị được lưu hoặc gửi lên API có đúng payload khi click button.
- Kiểm tra click liên tục (Debounce / Double-click prevention) không bị gửi duplicate requests hoặc crash state.
- Kiểm tra khi nhấn các phím bàn phím tương ứng (Enter / Space) kích hoạt đúng chức năng của button.

---

## 3. Testcases for Search Box (Ô Tìm Kiếm)
- Kiểm tra search box hiện trên trang web như bản design.
- Kiểm tra placeholder có đúng ngữ pháp, ngữ cảnh và hợp lý hay không.
- Kiểm tra biểu tượng tìm kiếm (Search Icon) có hiển thị trên Search box.
- Kiểm tra con trỏ nhấp nháy sẽ xuất hiện khi click vào thanh search (Focus state).
- Kiểm tra kết quả tìm kiếm khi nhập từ khóa: từ đầu tiên, từ ở giữa, từ cuối cùng.
- Kiểm tra tính chính xác của kết quả khi nhập 1 từ khóa tìm kiếm.
- Kiểm tra tìm kiếm hoạt động khi nhấn phím Enter.
- Kiểm tra tìm kiếm hoạt động khi click vào biểu tượng tìm kiếm.
- Kiểm tra người dùng có thể paste dữ liệu vào ô tìm kiếm.
- Kiểm tra dữ liệu đầu vào là null hoặc chuỗi khoảng trắng (trả về danh sách mặc định).
- Kiểm tra thời gian load tìm kiếm và hiển thị skeleton / loading indicator.
- Kiểm tra tìm kiếm khi có phân trang (reset về trang 1 khi tìm từ khóa mới).
- Kiểm tra khi xóa từ khóa tìm kiếm (Clear button hoặc Backspace hết) thì trở về danh sách ban đầu.
- Kiểm tra số lượng kết quả tìm kiếm được hiển thị trong trang (Page size).
- Kiểm tra phân trang được bật khi kết quả số lượng tìm kiếm vượt quá page size.
- Kiểm tra kết quả sắp xếp thứ tự tìm kiếm theo Alphabet hoặc độ liên quan.
- Kiểm tra khi thêm mới dữ liệu ở danh mục thì khi tìm kiếm có hiển thị kết quả ngay.
- Kiểm tra khi xóa dữ liệu ở danh mục thì khi tìm kiếm không còn hiển thị kết quả.

---

## 4. Testcases for Combo Box & Dropdown List (Hộp Lựa Chọn)
- Kiểm tra tất cả các giá trị có được nạp đầy đủ vào danh sách dropdown hay không.
- Kiểm tra khi nhấp vào menu dropdown, nó mở menu hiển thị danh sách các options.
- Kiểm tra chức năng cuộn xuống (Scroll) khi số lượng options vượt chiều cao tối đa.
- Kiểm tra danh sách dropdown cuộn xuống / chuyển item bằng phím mũi tên lên/xuống (Arrow keys).
- Kiểm tra giá trị được chọn mặc định (Default selected value) hiển thị đúng khi mở màn hình.
- Kiểm tra menu dropdown không thể chỉnh sửa văn bản trực tiếp (nếu là dạng Select tĩnh).
- Kiểm tra không có bất kỳ giá trị trống hoặc `undefined`/`null` hiển thị rác trong danh sách.
- Kiểm tra hiển thị độ dài ký tự tối đa của option (text-overflow: ellipsis nếu quá dài).
- Kiểm tra con trỏ chuột khi hover chuyển từ con trỏ mũi tên sang bàn tay (pointer).
- **Với Combo Box (Searchable Dropdown)**:
  - Kiểm tra trường tìm kiếm có thể nhấp được (Clickable & Focusable).
  - Kiểm tra văn bản được nhập vào trường tìm kiếm từ bàn phím.
  - Kiểm tra người dùng có thể dán văn bản vào ô tìm kiếm bằng chuột.
  - Kiểm tra giá trị từ danh sách được chọn tự động nếu người dùng nhập từ khóa hợp lệ.
  - Kiểm tra dữ liệu hiển thị cập nhật lên ô Combo Box sau khi chọn.
  - Kiểm tra khi click vào dữ liệu sẽ kích hoạt emit event `selectionChange`.

---

## 5. Testcases for Upload File / Image (Tải Lên Tệp & Ảnh)
- Kiểm tra hiển thị nút hoặc liên kết tải lên tệp.
- Kiểm tra biểu tượng (Upload icon) căn chỉnh đúng thiết kế.
- Kiểm tra hiển thị dấu 3 chấm (`...`) khi tên tệp quá dài để không làm vỡ layout.
- Kiểm tra khi click vào nút, hộp thoại chọn tệp hệ thống (File Picker) được mở ra.
- Kiểm tra người dùng có thể chọn và tải lên nhiều tệp nếu hệ thống hỗ trợ multi-upload.
- Kiểm tra tải lên nhiều tệp cùng một lúc (Batch upload & Progress bar).
- Kiểm tra thứ tự hiển thị của các tệp tải lên giữ nguyên đúng thứ tự người dùng chọn.
- Kiểm tra tải lên hình ảnh với các phần mở rộng khác nhau (.png, .jpg, .jpeg, .webp, .svg).
- Kiểm tra tải lên hình ảnh có tên trùng lặp (xử lý đổi tên hoặc cảnh báo ghi đè).
- Kiểm tra tải lên tệp có dung lượng vượt quá giới hạn tối đa cho phép (Hiển thị thông báo lỗi rõ ràng).
- Kiểm tra tải lên tệp sai định dạng (ví dụ chọn .exe, .sh, .txt khi chỉ cho phép ảnh).
- Kiểm tra xác nhận thông báo lỗi định dạng không hợp lệ.
- Kiểm tra hộp thoại chọn tệp chỉ lọc hiển thị các tệp thuộc định dạng được hỗ trợ (`accept="image/*"`).
- Kiểm tra chất lượng hình ảnh sau khi tải lên không bị vỡ hoặc méo tỉ lệ.
- Kiểm tra người dùng có thể xem trước (Preview) hoặc xóa (Delete) tệp/ảnh đã tải lên.
- Kiểm tra tính năng kéo và thả (Drag and Drop) hoạt động mượt mà cho các loại tệp được phép.
- Kiểm tra thông báo lỗi nếu tệp tải lên là tệp rỗng (0 bytes).
- Kiểm tra các loại tập tin bị cấm không được phép kéo thả hoặc bypass qua script.

---

## 6. Testcases for Form (Biểu Mẫu)
- Kiểm tra vị trí và bố cục biểu mẫu trên trang web.
- Kiểm tra tiêu đề (Form Title) và mô tả form.
- Kiểm tra sự hiện diện và thứ tự của các trường trong form.
- Kiểm tra dấu hoa thị đỏ (`*`) hiển thị cạnh nhãn của các trường bắt buộc.
- Kiểm tra các nút hành động (Lưu, Hủy, Đặt lại) trong form.
- Kiểm tra thông báo lỗi validation hiển thị tức thì khi người dùng nhập sai hoặc bỏ trống trường bắt buộc.
- Kiểm tra điều hướng tuần tự giữa các trường bằng phím `Tab` và `Shift + Tab`.
- Kiểm tra ngăn chặn click liên tục vào nút Gửi (Prevent duplicate submit / disable submit button khi đang pending).
- Kiểm tra nút Gửi bị disable khi form ở trạng thái `INVALID` (nếu có yêu cầu).

---

## 7. Testcases for ListView / Data Table (Danh Sách & Bảng Dữ Liệu)
- Kiểm tra các cột, tiêu đề cột và các nút thao tác hiển thị đúng bản design.
- Kiểm tra tính năng chọn 1 dòng hoặc chọn tất cả (Select All Checkbox).
- Kiểm tra sắp xếp (Sorting) danh sách theo bảng chữ cái hoặc ngày tạo mới nhất/cũ nhất.
- Kiểm tra hiển thị thanh cuộn ngang (Horizontal scroll) và cuộn dọc khi bảng có nhiều cột hoặc dữ liệu dài.
- Kiểm tra phân trang (Pagination) hoạt động khi danh sách có số lượng bản ghi lớn.

---

## 8. Testcases for Checkbox (Hộp Kiểm)
- Kiểm tra UI: Nhãn (Label), khoảng cách và căn chỉnh của checkbox.
- Kiểm tra checkbox có thể tick chọn hoặc bỏ chọn được (Checked / Unchecked).
- Kiểm tra trạng thái đã chọn của checkbox được lưu lại chính xác trong form/model khi submit.
- Kiểm tra cho phép chọn nhiều checkbox độc lập trong cùng một nhóm.
- Kiểm tra hiển thị cảnh báo nếu checkbox là điều kiện bắt buộc (ví dụ: *Tôi đồng ý với điều khoản sử dụng*).
- Kiểm tra trạng thái mặc định của checkbox đúng theo tài liệu đặc tả.
- Kiểm tra trong quá trình tải trang/pending API, checkbox bị disable không cho click.
- Kiểm tra click vào chữ nhãn (Label) cũng làm thay đổi trạng thái checkbox.
- Kiểm tra chọn được checkbox bằng bàn phím (Phím `Tab` để focus, phím `Space` để toggle).
- **Trường hợp Checkbox "Ghi nhớ đăng nhập" (Remember Me)**:
  - Kiểm tra lưu token / username an toàn khi checkbox được chọn.
  - Kiểm tra khi người dùng quay lại trang, thông tin đăng nhập được tự động điền sẵn.
  - Kiểm tra người dùng vẫn đăng nhập bình thường nếu không chọn checkbox này.
  - Kiểm tra sau khi xóa cookie / storage trình duyệt thì form không còn nhớ thông tin.

---

## 9. Testcases for Radio Button (Nút Chọn Một)
- Kiểm tra radio button hiển thị đúng vị trí và kiểu dáng theo thiết kế.
- Kiểm tra có thể chọn được radio button.
- Kiểm tra khi nhấp vào nhãn (Label) thì radio button tương ứng được chọn.
- Kiểm tra lựa chọn mặc định của nhóm radio button đúng theo spec.
- Kiểm tra tính loại trừ lẫn nhau: Khi chọn option này thì option đã chọn trước đó tự động bị bỏ chọn.
- Kiểm tra dữ liệu gửi đi khớp chính xác với option đang được chọn.

---

## 10. Testcases for Header (Đầu Trang)
- Kiểm tra phần Header hiển thị đầy đủ trên trang web.
- Kiểm tra phần Header căn chỉnh đúng lề và chiều cao.
- Kiểm tra các biểu tượng (Icons) căn chỉnh thẳng hàng với văn bản.
- Kiểm tra các biểu tượng có ngữ nghĩa liên quan đúng với đường link.
- Kiểm tra văn bản liên kết rõ ràng, dễ đọc, độ tương phản cao.
- Kiểm tra Logo trang web hiển thị đúng vị trí và tỉ lệ.
- Kiểm tra Header được sử dụng nhất quán trên toàn bộ các trang con.
- Kiểm tra Header cố định (Sticky Header) khi cuộn trang nếu có yêu cầu.
- Kiểm tra tất cả các đường link trên Header đều có thể click được.
- Kiểm tra khi click vào link trên Header, điều hướng đến đúng trang đích.
- Kiểm tra click vào Logo luôn chuyển hướng về Trang chủ.
- Kiểm tra hiệu ứng đổi màu khi hover chuột vào các menu link.
- Kiểm tra menu đang active (Active State) được highlight để người dùng biết đang ở trang nào.
- Kiểm tra thanh tìm kiếm trên Header hoạt động bình thường.
- Kiểm tra phần Header có đường phân cách rõ ràng với phần Body.
- Kiểm tra menu thả xuống (Dropdown Menu) trên Header mở mượt mà khi click hoặc hover.

---

## 11. Testcases for Footer (Chân Trang)
- Kiểm tra Footer luôn nằm cố định ở đáy trang (Bottom of page).
- Kiểm tra không xuất hiện khoảng trắng thừa dưới đáy Footer ở màn hình độ phân giải cao (Sticky footer).
- Kiểm tra các cột và phần tử trong Footer căn chỉnh ngăn nắp, cân đối.
- Kiểm tra nội dung Footer hiển thị nhất quán trên mọi trang.
- Kiểm tra tất cả liên kết trong Footer (Chính sách, Điều khoản, Liên hệ) mở đúng trang.
- Kiểm tra các liên kết mạng xã hội (Facebook, Zalo, YouTube) có icon đúng và mở trong tab mới (`target="_blank"`).
- Kiểm tra phần bản quyền (Copyright © 2026) hiển thị chính xác.
- Kiểm tra Logo chân trang hiển thị sắc nét.

---

## 12. Testcases for Dialog / Modal (Hộp Thoại)
- Kiểm tra vị trí hiển thị (canh giữa màn hình), tiêu đề và nội dung Dialog đúng bản thiết kế.
- Kiểm tra lớp phủ nền mờ (Backdrop overlay) ngăn thao tác với trang bên dưới.
- Kiểm tra thông điệp hoặc dữ liệu trong Dialog hiển thị chính xác theo ngữ cảnh kích hoạt.
- Kiểm tra chức năng của các nút trong Dialog (Đồng ý, Xác nhận, Hủy bỏ).
- Kiểm tra nút Đóng (`X`) hoặc nút Hủy đóng được Dialog và dọn sạch DOM/Memory.
- Kiểm tra nhấn phím `ESC` trên bàn phím có đóng Dialog hay không (Accessibility).
- Kiểm tra Dialog hiển thị đồng nhất trên mọi module và trình duyệt.

---

## 13. Testcases for Links (Liên Kết Hyperlink)
- Kiểm tra link có thể click được.
- Kiểm tra liên kết nội bộ điều hướng mượt mà trong cùng tab (Angular Router navigation).
- Kiểm tra liên kết ngoài mở ra cửa sổ/tab mới với URL chính xác và thuộc tính bảo mật `rel="noopener noreferrer"`.
- Kiểm tra link không bị gãy hoặc chuyển hướng đến trang lỗi 404.
- Kiểm tra màu sắc liên kết thay đổi ở các trạng thái: normal, hover, active, visited.
- Kiểm tra con trỏ chuột chuyển thành hình bàn tay khi hover vào link.
- Kiểm tra thời gian tải trang khi click liên kết nội bộ.
- Kiểm tra liên kết luôn sử dụng giao thức bảo mật `https://`.

---

## 14. Testcases for Date Field (Trường Ngày Tháng)
- Kiểm tra khi click vào ô ngày tháng hoặc icon lịch, Datepicker widget mở ra.
- Kiểm tra kích thước của lịch hiển thị responsive trên các thiết bị.
- Kiểm tra người dùng có thể chọn ngày từ lịch và ngày được điền chính xác vào ô input.
- Kiểm tra mặc định hiển thị đúng tháng và năm hiện tại.
- Kiểm tra chuyển tháng trước / tháng sau bằng nút mũi tên trái / phải.
- Kiểm tra chọn nhanh tháng/năm qua dropdown selector.
- Kiểm tra cho phép nhập ngày thủ công bằng bàn phím theo đúng định dạng (ví dụ: `DD/MM/YYYY`).
- Kiểm tra kiểm tra định dạng ngày được hỗ trợ (DD/MM/YYYY, YYYY-MM-DD).
- Kiểm tra cho phép chỉnh sửa lại ngày đã chọn.
- Kiểm tra chặn nhập ký tự chữ cái hoặc ký tự không hợp lệ vào trường ngày.
- Kiểm tra validation báo lỗi khi nhập ngày không hợp lệ (ngày > 31, tháng > 12, ngày 29/02 năm không nhuận).
- Kiểm tra giới hạn ngày nhỏ nhất (Min Date) và ngày lớn nhất (Max Date) nếu có yêu cầu.

---

## 15. Testcases for Pop-up / Toast Messages (Thông Báo Nổi)
- Kiểm tra chính tả và ngữ nghĩa của thông báo lỗi, cảnh báo và thành công.
- Kiểm tra thông báo lỗi hiển thị khi bỏ trống trường bắt buộc.
- Kiểm tra thông báo lỗi hiển thị khi tải lên tệp rỗng hoặc sai định dạng.
- Kiểm tra thông báo lỗi hiển thị khi vượt quá ngưỡng ký tự tối đa hoặc không đạt ngưỡng tối thiểu.
- Kiểm tra thông báo lỗi hiển thị khi nhập URL hoặc Email sai định dạng.
- Kiểm tra tính nhất quán về phong cách trình bày thông báo (Title Case, Sentence Case).
- Kiểm tra vị trí hiển thị của Toast (Top-Right, Bottom-Right...) không che khuất thao tác quan trọng.
- Kiểm tra màu sắc chuẩn ngữ nghĩa: Đỏ (Error/Lỗi), Xanh lá (Success/Thành công), Vàng (Warning/Cảnh báo), Xanh dương (Info/Thông tin).
- Kiểm tra thời gian tự động biến mất (Auto-dismiss timeout: thường 3s - 5s) hoặc nút đóng thủ công (`X`).
- Kiểm tra số lượng thông báo hiển thị tối đa cùng lúc (Stacking limit, ví dụ: tối đa 3 toasts) để tránh ngập màn hình.

---

## 16. Testcases for Graphical Report & Charts (Báo Cáo & Đồ Thị)
- Kiểm tra hiển thị thông báo rỗng ("Không có dữ liệu") khi tập dữ liệu bằng 0.
- Kiểm tra hiển thị Progress Bar / Spinner trong lúc đang tải dữ liệu biểu đồ.
- Kiểm tra giá trị các cột/đường tương ứng chính xác với trục X và trục Y; tỉ lệ phần trăm của biểu đồ tròn khớp với dữ liệu gốc.
- Kiểm tra biểu đồ tự động cập nhật lại khi nguồn dữ liệu thay đổi hoặc khi chuyển kỳ báo cáo.
- Kiểm tra hiển thị biểu đồ khi áp dụng các bộ lọc khác nhau.
- Kiểm tra tooltip hiển thị chi tiết số liệu khi người dùng hover chuột vào từng điểm dữ liệu / cột.
- Kiểm tra phạm vi thang đo của trục X và Y tự co giãn hợp lý theo độ lớn của dữ liệu.
- Kiểm tra hiển thị biểu đồ với các giá trị cực trị (rất nhỏ gần 0 hoặc cực lớn hàng tỷ).
- Kiểm tra màu sắc các đường/cột tuân thủ đúng bảng màu token thiết kế.
- Kiểm tra không bị lỗi layout hoặc tràn khung khi phóng to / thu nhỏ màn hình.
- Kiểm tra tính năng Xuất dữ liệu (Export PNG / SVG / Excel) hoạt động chính xác.
- Kiểm tra file Excel xuất ra có số liệu và đồ thị khớp 100% với trên web.

---

## 17. Testcases for Filter (Bộ Lọc Dữ Liệu)
- Kiểm tra click vào nút hoặc dropdown bộ lọc sẽ mở rộng vùng lọc.
- Kiểm tra click ra ngoài hoặc click nút đóng sẽ thu gọn vùng lọc.
- Kiểm tra hiển thị đầy đủ các tiêu chí lọc trước khi thực hiện tìm kiếm.
- Kiểm tra các giá trị trong danh mục lọc khớp với danh mục dữ liệu thực tế từ backend.
- Kiểm tra kết quả hiển thị sau khi lọc khớp 100% với các tiêu chí đã chọn.
- Kiểm tra các bản ghi không thỏa mãn tiêu chí lọc bị loại bỏ hoàn toàn khỏi danh sách kết quả.
- Kiểm tra bộ lọc hiển thị responsive và hoạt động tốt trên Desktop, Tablet và Mobile.
- Kiểm tra người dùng có thể thay đổi hoặc kết hợp nhiều tiêu chí lọc cùng lúc (Multi-criteria filter).
- Kiểm tra nút "Xóa bộ lọc" (Reset filter) hoàn tác tất cả các tiêu chí về trạng thái ban đầu.
- Kiểm tra trạng thái bộ lọc được lưu trữ trên Query Params URL để khi F5 / chia sẻ link vẫn giữ nguyên kết quả lọc.
- Kiểm tra bộ lọc áp dụng đồng bộ trên tất cả các trang khi danh sách có phân trang.
- Kiểm tra xử lý mượt mà khi kết quả lọc không tìm thấy dữ liệu (Hiển thị empty state lịch sự).
