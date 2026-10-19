# Những Case Test Cơ Bản Khi Kiểm Thử Website (17 Standard Web UI Categories)

Tài liệu chuẩn mực kiểm thử giao diện & luồng chức năng Web bắt buộc dành cho Agent QC (Test Architect & Independent Quality Gate).

---

## 1. Testcases for Textbox
- Kiểm tra các ký tự alpha hoặc ký tự chữ.
- Kiểm tra nhập giá trị số âm, số nguyên, số thập phân.
- Kiểm tra dữ liệu đầu vào là khoảng trắng (leading, trailing, whitespace-only).
- Kiểm tra dữ liệu đầu vào chứa ký tự đặc biệt (XSS/SQLi payload, emoji, ký tự lạ).
- Kiểm tra điều kiện bắt buộc cho textbox nếu được cung cấp.
- Kiểm tra textbox có được bỏ trống hay không theo quy định.
- Kiểm tra giới hạn ký tự Min – Max (Boundary Value Analysis).
- Kiểm tra có thể sao chép và dán (copy-paste) ký tự vào textbox.
- Kiểm tra nút “Tab” trên bàn phím có di chuyển qua các textbox tuần tự.
- Kiểm tra placeholder có phù hợp và đúng ngữ pháp không.
- Kiểm tra không thể chỉnh sửa khi textbox bị disabled/readonly.
- Kiểm tra khi textbox disabled thì chuyển sang màu xám (disabled style/cursor).

---

## 2. Testcases for Button
- Kiểm tra button có hiện trên trang web như bản design (Figma/Spec).
- Kiểm tra màu sắc, icon của button đúng chuẩn token và thiết kế.
- Kiểm tra kích thước của button (responsive, padding, min-width/height).
- Kiểm tra button có hoạt động khi click vào (trigger đúng event/action).
- Kiểm tra chức năng của button có đúng hay không.
- Kiểm tra các giá trị được lưu hoặc gửi có đúng khi click button.
- Kiểm tra click liên tục (rapid/duplicate click) có bị debounce hoặc vô hiệu hóa để tránh spam không.
- Kiểm tra khi nhấn các phím trên bàn phím (Enter, Space) có kích hoạt đúng chức năng của button.

---

## 3. Testcases for Search box
- Kiểm tra search box hiện trên trang web như bản design.
- Kiểm tra placeholder có đúng ngữ pháp và hợp lý hay không.
- Kiểm tra biểu tượng tìm kiếm có trên Search box.
- Kiểm tra con trỏ sẽ xuất hiện khi click vào thanh search (focus).
- Kiểm tra kết quả tìm kiếm khi nhập từ khóa tìm kiếm: từ đầu tiên, giữa, cuối.
- Kiểm tra các kết quả có đúng khi nhập vào 1 từ khóa tìm kiếm (exact match & partial match).
- Kiểm tra tìm kiếm hoạt động khi nhấn Enter.
- Kiểm tra tìm kiếm hoạt động khi click vào biểu tượng tìm kiếm.
- Kiểm tra xem người dùng có thể paste dữ liệu vào ô tìm kiếm không.
- Kiểm tra dữ liệu đầu vào là null hoặc space ở ô tìm kiếm.
- Kiểm tra xem thời gian load tìm kiếm thế nào (debounce, loading indicator).
- Kiểm tra tìm kiếm khi có phân trang (reset về trang 1 khi gõ từ khóa mới).
- Kiểm tra xóa từ khóa tìm kiếm thì trở về danh sách ban đầu.
- Kiểm tra số lượng kết quả tìm kiếm được hiển thị trong trang.
- Kiểm tra phân trang nên được bật khi kết quả số lượng tìm kiếm nhiều.
- Kiểm tra kết quả sắp xếp thứ tự tìm kiếm theo Alphabet hoặc độ phù hợp.
- Kiểm tra khi thêm dữ liệu ở danh mục thì khi tìm kiếm có hiển thị kết quả.
- Kiểm tra khi xóa dữ liệu ở danh mục thì khi tìm kiếm không hiện kết quả.

---

## 4. Testcases for Combo Box + Dropdown list
- Kiểm tra xem tất cả các giá trị có được thêm vào danh sách dropdown hay không.
- Kiểm tra khi nhấp vào menu dropdown, nó sẽ hiển thị một danh sách chứa các giá trị.
- Kiểm tra xem chức năng cuộn xuống có hoạt động trong danh sách dropdown hay không.
- Kiểm tra danh sách dropdown sẽ được cuộn xuống bằng cách nhấn phím mũi tên xuống trên bàn phím.
- Kiểm tra rằng giá trị được chọn theo mặc định có được hiển thị trên menu dropdown hay không.
- Kiểm tra rằng menu dropdown không thể chỉnh sửa được (đối với standard dropdown).
- Kiểm tra để đảm bảo rằng không có bất kỳ giá trị trống nào được hiển thị trong danh sách dropdown.
- Kiểm tra hiển thị độ dài ký tự tối đa trong dropdown (ellipsis, tooltip).
- Kiểm tra xem con trỏ chuột khi di chuột có thay đổi từ con trỏ sang bàn tay (pointer) hay không.

### Combo Box (Searchable Dropdown):
- Kiểm tra trường tìm kiếm có thể nhấp được hay không bằng cách nhấp vào trường tìm kiếm.
- Kiểm tra văn bản có được thêm vào trường tìm kiếm hay không từ thao tác nhập bằng bàn phím.
- Kiểm tra người dùng có thể dán văn bản vào trường tìm kiếm bằng chuột.
- Kiểm tra rằng giá trị từ danh sách sẽ được chọn nếu người dùng thêm một từ khóa hợp lệ.
- Kiểm tra hiển thị dữ liệu lên Combo Box.
- Kiểm tra khi click vào dữ liệu sẽ hiển thị lên Combo Box.

---

## 5. Testcases for Upload file / image
- Kiểm tra có nút hoặc link tệp tải lên.
- Kiểm tra biểu tượng được thêm vào với nút tải lên có trong thiết kế và có được căn chỉnh hay không.
- Kiểm tra dấu 3 chấm (...) nên được hiển thị trong trường hợp tên tệp quá dài và làm xáo trộn thiết kế.
- Kiểm tra khi nhấp vào cửa sổ nút Tải lên sẽ được mở để chọn tệp.
- Kiểm tra rằng người dùng có thể chọn và tải lên nhiều tệp nếu được yêu cầu.
- Kiểm tra rằng người dùng có thể tải lên nhiều tệp cùng một lúc.
- Kiểm tra thứ tự của tệp phải giống với các tệp được tải lên hoặc cả hai trường hợp lần lượt và nhiều tệp được tải lên.
- Kiểm tra chức năng tải lên hình ảnh với các tệp hình ảnh có các phần mở rộng khác nhau (png, jpg, jpeg, svg, webp).
- Kiểm tra tải lên hình ảnh tên trùng lặp.
- Kiểm tra tải lên hình ảnh với kích thước hình ảnh lớn hơn kích thước tối đa cho phép. Thông báo lỗi thích hợp sẽ được hiển thị.
- Kiểm tra chức năng tải lên hình ảnh với các loại tệp khác với hình ảnh (ví dụ: txt, doc, pdf, exe, v.v.).
- Kiểm tra xác nhận định dạng không hợp lệ.
- Kiểm tra xem hộp thoại chọn tệp chỉ hiển thị các tệp được hỗ trợ được liệt kê (accept attribute).
- Kiểm tra chất lượng hình ảnh sau khi tải lên. Chất lượng hình ảnh không được thay đổi sau khi tải lên.
- Kiểm tra xem người dùng có thể sử dụng / xem các hình ảnh đã tải lên hay không (preview, thumbnail).
- Chức năng kéo và thả (drag & drop) sẽ hoạt động bình thường cho các loại tệp được phép.
- Kiểm tra thông báo lỗi nếu tệp trống và không có nội dung (0-byte file).
- Kiểm tra các loại tập tin không được kéo thả và không tải lên.

---

## 6. Testcases for Form
- Kiểm tra vị trí biểu mẫu trên trang web đúng layout.
- Kiểm tra tiêu đề của form.
- Kiểm tra các trường của form hiển thị đầy đủ, đúng thứ tự.
- Dấu hoa thị (*) được hiển thị gần các trường bắt buộc.
- Kiểm tra các nút lưu và hủy trong form.
- Thông báo xác thực trên trường bắt buộc hoặc các giá trị không chính xác (validation error messages).
- Kiểm tra xem việc điều hướng giữa các trường có thành công hay không bằng cách sử dụng phím Tab.
- Không được phép nhấp nhiều lần vào quá trình gửi (disable submit button khi đang submitting).
- Có thể tắt nút gửi trước khi nhập các trường bắt buộc trong biểu mẫu.

---

## 7. Testcases for ListView / Table
- Kiểm tra các cột, button được hiển thị trên danh sách giống với bản design.
- Kiểm tra chọn được 1 hoặc tất cả các đối tượng trong danh sách (single / select-all checkbox).
- Kiểm tra danh sách được sắp xếp theo bảng chữ cái hoặc ngày tạo gần nhất (sort order).
- Kiểm tra hiển thị scroll bar ngang và dọc để có thể xem hết được nội dung (sử dụng chuẩn tds-panel-scroll).
- Kiểm tra có phân trang trên danh sách khi dữ liệu quá nhiều (pagination controls).

---

## 8. Testcases for Checkbox
- Kiểm tra UI: label, căn chỉnh của checkbox.
- Kiểm tra xem checkbox có thể chọn được (checked/unchecked) hay không.
- Kiểm tra xem checkbox đã được chọn và nhấn gửi có lưu lại theo lựa chọn của mình không.
- Kiểm tra xem có thể chọn nhiều checkbox không (multi-selection).
- Kiểm tra thông báo, cảnh báo thích hợp có hiển thị hay không nếu đó là trường bắt buộc khi người dùng click nút gửi.
- Kiểm tra trạng thái mặc định của các checkbox phải theo tài liệu yêu cầu.
- Kiểm tra trong quá trình tải trang, checkbox không được nhấp vào.
- Kiểm tra xem checkbox đã được chọn hay chưa bằng cách nhấp vào label.
- Kiểm tra hộp kiểm có thể chọn được bằng bàn phím (Tab + Space/Enter).

### Checkbox Remember Me:
- Chọn Checkbox Remember Me nếu người dùng nhấp vào nút đăng nhập hoặc gửi và tên người dùng/mật khẩu được lưu trong cookie/storage của trình duyệt.
- Kiểm tra xem người dùng khi truy cập lại trang đăng nhập, sau đó tên người dùng và mật khẩu hiển thị trong trường tương ứng.
- Kiểm tra xem người dùng có thể đăng nhập mà không cần chọn hộp kiểm Remember Me hay không.
- Truy cập lại trang và kiểm tra các trường sau khi xóa cookie/storage của trình duyệt (phải reset về trống).

---

## 9. Testcases for Radio Button
- Kiểm tra xem radio button có được trình bày trên trang web theo thiết kế hay không.
- Kiểm tra xem các nút radio có thể chọn được hay không chọn được.
- Kiểm tra khi nhấp vào nhãn và kiểm tra xem nút radio đã được chọn hay chưa.
- Kiểm tra lựa chọn mặc định của nút radio theo tài liệu.
- Kiểm tra chức năng của nút radio trên một lựa chọn (mutual exclusivity - chọn option A thì option B tự bỏ chọn).
- Kiểm tra chức năng của nút radio mà không cần lựa chọn (nếu là trường không bắt buộc).
- Kiểm tra dữ liệu được chọn khi nhấn nút gửi khớp với nhau.

---

## 10. Testcases for Header and Footer
### Testcases for Header:
- Kiểm tra phần tiêu đề được thêm vào trang web.
- Kiểm tra phần tiêu đề được căn chỉnh đúng (height, alignment).
- Kiểm tra các biểu tượng được căn chỉnh với văn bản nếu được thêm vào tiêu đề.
- Kiểm tra các biểu tượng được thêm vào có liên quan đến văn bản link.
- Kiểm tra xem văn bản link có thể đọc được hay không.
- Kiểm tra logo của trang web được thêm vào tiêu đề có được căn chỉnh hay không.
- Kiểm tra cùng một tiêu đề được sử dụng nhất quán trên toàn bộ trang web.
- Kiểm tra tiêu đề có dính (sticky) trên toàn bộ trang hoặc cố định theo yêu cầu và thiết kế.
- Kiểm tra xem tất cả các link có nên được mở trên tiêu đề hay không.
- Kiểm tra khi nhấp vào link trên tiêu đề, trang chính xác sẽ được mở (routing).
- Kiểm tra trang chủ nên được mở khi nhấp vào logo trên tất cả các trang.
- Kiểm tra trên chuột di chuột thay đổi màu sắc (hover state) cho link được thêm vào menu tiêu đề.
- Kiểm tra rằng các link tiêu đề đã chọn sẽ vẫn ở trạng thái active để thông báo cho người dùng về màn hình/trang đã nhấp.
- Kiểm tra rằng thanh tìm kiếm có được thêm vào menu tiêu đề hay không.
- Kiểm tra phần tiêu đề và phần nội dung không giống nhau, có đường phân định rõ ràng (border/shadow).
- Kiểm tra màu biểu tượng cũng sẽ thay đổi khi di chuột vào tiêu đề nếu các biểu tượng được thêm vào.
- Kiểm tra các tùy chọn thả xuống được thêm vào tiêu đề hiển thị khi di chuột hoặc nhấp chuột.

---

## 11. Testcases for Footer
- Kiểm tra footer được căn chỉnh ở cuối trang.
- Kiểm tra rằng không được có thêm khoảng trắng ở cuối chân trang ở độ phân giải màn hình cao (sticky footer).
- Kiểm tra phần tử được căn chỉnh ở phần footer hay không.
- Kiểm tra phần footer phải giống nhau cho tất cả các trang.
- Kiểm tra khi nhấp vào link các trang chính xác sẽ được tải.
- Kiểm tra tất cả các link mạng xã hội với các biểu tượng được thêm vào chân trang (target="_blank", rel="noopener noreferrer").
- Kiểm tra phần bản quyền (copyright) có được thêm vào chân trang hay không.
- Kiểm tra logo hiển thị ở footer nếu có.

---

## 12. Testcases for Dialog / Modal
- Kiểm tra UI: vị trí (căn giữa hoặc theo spec), title, content của hộp thoại hiển thị trên trang web có giống bản design.
- Kiểm tra thông báo hoặc thông tin đang hiển thị theo yêu cầu.
- Kiểm tra chức năng của các nút trong dialog nếu có (Save, Cancel, Action).
- Kiểm tra xem dialog có nút hủy hoặc đóng (icon X, button Đóng) hay không.
- Kiểm tra backdrop che mờ bên dưới và bấm ESC hoặc click outside (nếu cho phép) để đóng dialog.
- Kiểm tra dialog hiển thị cùng một vị trí trong tất cả các module của trình duyệt.

---

## 13. Testcases for Links
- Kiểm tra xem link được thêm vào trang có thể nhấp được hay không bằng cách nhấp vào link.
- Kiểm tra các link nội bộ đã chuyển hướng người dùng đến trang được link (Angular Router).
- Kiểm tra xem tất cả các link bên ngoài có đang mở trong cửa sổ hoặc tab mới với URL thích hợp hay không (target="_blank", rel="noopener noreferrer").
- Kiểm tra xem trang có chuyển hướng đến trang hợp lệ hay không khi người dùng nhấp vào link.
- Kiểm tra các link đang mở tất cả các trình duyệt và hệ điều hành khác nhau.
- Kiểm tra xem màu của link đã truy cập (visited) có bị thay đổi hay theo thiết kế không.
- Kiểm tra khi di chuột vào link con trỏ chuột có được thay đổi thành biểu tượng bàn tay (pointer) hay không.
- Kiểm tra thời gian tải cho các link nội bộ theo yêu cầu.
- Kiểm tra xem một link được chia sẻ thì link đó có được chia sẻ đúng với địa chỉ chính xác hay không.
- Kiểm tra link được chia sẻ đang được mở đúng cách.
- Kiểm tra xem trang có link không hợp lệ hay không (nó sẽ chuyển hướng người dùng đến trang lỗi 404).
- Kiểm tra xem link có được thêm vào với đúng giao thức truyền siêu văn bản HTTPS:// hoặc HTTP:// hay không.

---

## 14. Testcases for Date field
- Kiểm tra rằng khi nhấp vào trường ngày, một tiện ích lịch (datepicker widget) sẽ mở ra.
- Kiểm tra rằng kích thước của tiện ích lịch phải đáp ứng theo kích thước màn hình và thiết bị (responsive).
- Kiểm tra rằng người dùng có thể chọn ngày trong lịch và sau khi chọn ngày, ngày đó sẽ được hiển thị trong trường ngày.
- Kiểm tra rằng theo mặc định, lịch của tháng hiện tại sẽ được hiển thị.
- Kiểm tra rằng người dùng có thể chuyển sang lịch của tháng trước và tháng sau bằng cách chọn biểu tượng trái và phải trên lịch.
- Kiểm tra rằng người dùng có thể kiểm tra lịch của một tháng cụ thể trong năm bất kỳ (month/year picker).
- Kiểm tra rằng người dùng có thể nhập ngày theo cách thủ công vào ngày theo định dạng ngày.
- Kiểm tra định dạng ngày được lịch hỗ trợ, ví dụ – dd/mm/yyyy, mm/dd/yyyy, v.v.
- Kiểm tra rằng người dùng cũng có thể chỉnh sửa ngày đã được đặt trong lịch.
- Kiểm tra rằng các giá trị không phải là số không được phép trong trường ngày (ngoài các ký tự được sử dụng trong định dạng ngày như '/' hoặc '-').
- Kiểm tra rằng ngày không hợp lệ không được phép trong trường ngày (như giá trị ngày vượt quá 31, giá trị tháng vượt quá 12, năm nhuận, v.v.).
- Kiểm tra ngày cũ nhất và mới nhất có thể được đặt trên lịch (minDate / maxDate).
- Kiểm tra giao diện người dùng của tiện ích lịch trên kích thước màn hình cực nhỏ và cực lớn.

---

## 15. Testcases for Pop-up / Toast Message
- Kiểm tra xem chính tả cho thông báo lỗi có đúng hay không.
- Kiểm tra thông báo lỗi cho đầu vào trống được hiển thị.
- Kiểm tra thông báo lỗi tải lên một tệp trống có được hiển thị hay không.
- Kiểm tra thông báo lỗi sẽ được hiển thị cho giới hạn tối đa hoặc giới hạn trên.
- Kiểm tra xem thông báo lỗi có hiển thị cho đầu vào trống hoặc giới hạn sau thông báo mà người dùng có thể nhấp và tương tác với phần mềm hay không.
- Kiểm tra một thông báo lỗi sẽ được hiển thị trong trường hợp người dùng thêm các từ hoặc nội dung tối thiểu hơn giới hạn cho phép.
- Kiểm tra thông báo lỗi sẽ được hiển thị cho URL không hợp lệ.
- Kiểm tra xem có nên sử dụng cùng một định dạng để hiển thị tất cả các thông báo lỗi không (chữ hoa, chữ thường hoặc chữ hoa đầu câu).
- Kiểm tra vị trí thông báo lỗi phải được căn chỉnh (top-right, bottom-right...).
- Kiểm tra trang thông báo lỗi 500 sẽ được hiển thị cho người dùng khi backend lỗi.
- Kiểm tra màu đỏ (danger) được sử dụng để hiển thị thông báo lỗi cho người dùng.
- Kiểm tra thông tin (info) và xác nhận (success) rằng màu xanh lam hoặc xanh lá cây có thể được sử dụng.
- Kiểm tra khoảng thời gian cho thông báo lỗi được hiển thị (auto-dismiss sau 3-5 giây).
- Kiểm tra được phép hiện tối đa bao nhiêu thông báo lỗi xếp chồng (stacking limit).

---

## 16. Testcases for Graphical report & Charts
- Đảm bảo có thông báo khi không có dữ liệu để hiển thị lên đồ thị (empty state).
- Kiểm tra hiển thị Progress bar / Skeleton / Spinner khi đang load biểu đồ.
- Các giá trị hiển thị tương ứng trên trục X và Y đối với biểu đồ cột và đường, tỉ lệ phần trăm của đường tròn đối với biểu đồ tròn có đúng với dữ liệu gốc.
- Kiểm tra sự thay đổi của đồ thị khi dữ liệu thay đổi (reactivity).
- Kiểm tra với tất cả các cách kết hợp dữ liệu có thể.
- Kiểm tra hiển thị của đồ thị ở các bộ lọc khác nhau.
- Đồ thị có hiển thị rõ thông tin cơ bản về giá trị của từng thành phần (tooltip on hover).
- Phạm vi của biểu đồ có hợp lý (độ lớn trục X và Y tự động scale phù hợp với giá trị biểu diễn).
- Kiểm tra đồ thị với dữ liệu có giá trị rất nhỏ (0, cận 0) hoặc rất lớn (extreme values).
- Đảm bảo biểu đồ hiển thị chính xác dữ liệu của các kỳ khác nhau.
- Nếu Title đồ thị là một Hyperlink, khi click vào link có điều hướng đến trang tương ứng.
- Màu sắc hiển thị có chuẩn theo spec / Design System token palette.
- Kiểm tra thanh cuộn để xem đối với đồ thị kích thước lớn hay khi phóng to.
- Đảm bảo không bị lỗi UI khi phóng to hoặc thu nhỏ đồ thị (zoom / resize).
- Đảm bảo biểu đồ hiển thị chính xác với tất cả các trình duyệt.
- Kiểm tra Font chữ, cỡ chữ, chính tả với các thành phần của biểu đồ.
- Đảm bảo tên biểu đồ hiển thị chính xác.
- Đảm bảo đồ thị hiển thị đúng yêu cầu khi người dùng trỏ chuột vào (hover highlights).
- Kiểm tra chức năng Export (PNG, SVG, Excel, PDF).
- Kiểm tra chức năng in khi điều kiện không cho phép (ví dụ: chưa kết nối máy in).
- Đảm bảo đồ thị khi in rõ nét và chính xác.
- Nếu có chức năng download: Kiểm tra chức năng download khi điều kiện không cho phép (ví dụ: mất mạng).
- Đảm bảo file download về có định dạng đúng theo Spec.
- Nếu export ra file Excel: Đảm bảo đồ thị hiển thị rõ ràng, chính xác trên file Excel; có thể chỉnh sửa đồ thị bằng các công cụ của Excel.

---

## 17. Testcases for Filter
- Xác minh rằng việc nhấp vào trình đơn thả xuống bộ lọc sẽ mở rộng bộ lọc (expand on click).
- Xác minh việc bỏ chọn vùng bộ lọc sẽ thu gọn bộ lọc (collapse).
- Đảm bảo ứng dụng cho phép hiển thị các tùy chọn bộ lọc trước khi tìm kiếm.
- Xác minh kết quả tìm kiếm trước khi áp dụng bộ lọc là chính xác và đầy đủ.
- Lọc xác thực là tùy chọn và không bắt buộc.
- Xác minh chức năng bộ lọc được hiển thị phù hợp theo yêu cầu kinh doanh (lọc phía server hoặc lọc phía client).
- Kiểm tra xem bộ lọc có hiển thị khi lỗi cơ sở dữ liệu được đưa vào kết quả tìm kiếm hay không.
- Xác minh các giá trị trong bộ lọc khớp với danh sách đầy đủ có sẵn trên cơ sở dữ liệu / catalog.
- Xác minh độ dài văn bản tối đa trong cơ sở dữ liệu có thể được hiển thị trong vùng bộ lọc (không bị tràn text).
- Xác thực việc chọn bộ lọc trả về kết quả khớp với bộ lọc đã chọn (exact match filtering).
- Xác minh kết quả bên ngoài bộ lọc đã chọn không được trả lại (exclusion of non-matching).
- Đảm bảo bộ lọc phản hồi nhanh trên máy tính để bàn, máy tính xách tay, máy tính bảng và điện thoại di động (responsive).
- Đảm bảo giao diện người dùng bộ lọc hoạt động bình thường trên tất cả các trình duyệt.
- Xác minh xem có thể thay đổi các tùy chọn lọc sau khi thực hiện lựa chọn hay không.
- Xác minh rằng bộ lọc đã chọn có thể bị xóa (clear / reset filter button).
- Tùy thuộc vào yêu cầu kinh doanh, hãy xác minh xem có thể áp dụng bộ lọc tiêu chí tùy chỉnh (custom filter) hay không.
- Xác thực các tùy chọn bộ lọc được duy trì từ phiên này sang phiên khác – tùy thuộc vào yêu cầu kinh doanh (sync URL query params hoặc storage).
- Xác minh rằng các kết quả trả về có thể được sắp xếp theo mức độ liên quan.
- Xác minh rằng kết quả trả về có thể được sắp xếp theo từ khóa.
- Kiểm tra các tùy chọn bộ lọc có thể được ẩn đi nếu người dùng mong muốn.
- Xác thực nếu các tùy chọn bộ lọc có thể được áp dụng mà không cần nhập bất kỳ truy vấn tìm kiếm nào.
- Đảm bảo bộ lọc được bao gồm trên tất cả các trang khi kết quả có phân trang.
