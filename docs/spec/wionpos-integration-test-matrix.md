# BỘ ĐẶC TẢ KIỂM ĐỊNH TÍCH HỢP CONTEXTS & PROVIDERS (ISTQB 5-STAGE PIPELINE)
## 6 Kịch Bản Kiểm Thử Tích Hợp Chuyên Sâu Cho Wi-MFES / WiOnPOS

> **Tiêu chuẩn áp dụng**: ISTQB Advanced Technical Test Analyst, ISO/IEC/IEEE 29119, SLPC Quality Gate.  
> **Căn cứ tài liệu**: `projects/wicx-crm-fe/docs/contexts/troubleshooting.md`, `contexts/automation.md`, `providers/troubleshooting.md`.  
> **Tác giả**: QC Verifier (Independent Quality Gate & Test Architect).  
> **Trạng thái**: Approved for Automated & Integration Verification.

---

## 1. TỔNG QUAN & NGUYÊN TẮC BẤT BIẾN (INVARIANTS)

Khi tích hợp Module Federation giữa Host Shell và các Micro-Frontend (Remote MFEs như Cashbook, Customer, Shop...), tầng Context (`@wi-mfes/context`, `@wi-mfes/perm`) và Providers đóng vai trò xương sống truyền tải định danh (`WI_SHOP_CONTEXT`), quyền hạn (`WI_PERMISSION_CONTEXT`), thông tin người dùng (`WI_USER_CONTEXT`) và trạng thái doanh nghiệp (`WI_BUSINESS_CONTEXT`).

### 5 Nguyên Tắc Bắt Buộc:
1. **Single Source of Truth**: `currentUser` (getter đồng bộ) và `user$` (observable bất đồng bộ) bắt buộc phải đọc cùng một Store/BehaviorSubject. Nghiêm cấm tạo 2 instance service hoặc đọc getter từ `localStorage` còn observable từ network.
2. **Replayability cho Subscriber Muộn**: Trạng thái context phải có khả năng replay (`BehaviorSubject`, `shareReplay({ bufferSize: 1, refCount: true })`, hoặc Angular 18 Signals). Subscriber vào muộn nhận ngay giá trị mới nhất mà không trigger API thừa.
3. **Phân Biệt Ba Trạng Thái Rõ Ràng**:
   - Chưa tải / Lỗi: `null` hoặc error state riêng.
   - Đang tải: `loading = true`.
   - Kết quả rỗng hợp lệ: `[]` (danh sách rỗng) hoặc empty DTO. Nghiêm cấm tạo mock user/tenant giả để che lỗi thiếu dữ liệu.
4. **Race-Condition Immunity**: Chuyển shop A -> B phải hủy request A (`switchMap` / `takeUntil`), vô hiệu hóa dữ liệu shop A lập tức và áp dụng Generation ID. Phản hồi của shop A về sau tuyệt đối không được ghi đè vào shop B.
5. **Stream Persistence**: Lỗi API (500, 503, 403, 401, timeout) không bao giờ được làm kết thúc vĩnh viễn Observable stream của context (`catchError` bắt lỗi và duy trì stream). Trạng thái lỗi phải bị xóa sạch khi retry thành công.

---

## 2. MA TRẬN 6 KỊCH BẢN KIỂM THỬ TÍCH HỢP (ISTQB 5-STAGE MATRIX)

| Mã KB | Tên Kịch Bản | Trọng Tâm Kỹ Thuật | Phương Pháp ISTQB | Số Testcases |
| :--- | :--- | :--- | :--- | :---: |
| **SC-01** | **F5 / Mở trực tiếp** (Direct Access & Reload) | Khởi tạo phiên, router guard, readiness check, khôi phục DTO thật | BVA, State Transition, Equivalence Partitioning | 4 TCs |
| **SC-02** | **Đổi shop A ➔ B khi request A còn chạy** | Race condition, `switchMap`, Generation ID, header isolation | Race Condition Analysis, Concurrency, BVA | 4 TCs |
| **SC-03** | **Đổi tài khoản cùng shop** | Privilege Escalation guard, re-fetch permissions, DTO mapping | Equivalence Partitioning, Security Matrix, BVA | 4 TCs |
| **SC-04** | **Logout / Login (Cùng tab & Khác tab)** | Context purge, storage event limitation, late response discard | Lifecycle Testing, Boundary State, Fault Injection | 4 TCs |
| **SC-05** | **API Lỗi / Retry** | Không dùng `forkJoin` mù quáng, stream survival, error reset | Fault Tolerance, Error Guessing, Resilience | 4 TCs |
| **SC-06** | **Subscriber vào muộn** (Late Subscriber) | Replay capability, snapshot delivery, zero duplicate HTTP calls | Timing & Concurrency, Memory Leak Verification | 4 TCs |
| **TỔNG** | **6 Kịch bản toàn diện** | **Độ bao phủ 100% 3 tài liệu đặc tả** | **ISTQB 5-Stage Framework** | **24 TCs** |

---

## 3. CHI TIẾT CÁC TEST CASES THEO CHUẨN ISTQB

### ── KỊCH BẢN 1: F5 / MỞ TRỰC TIẾP (DIRECT ACCESS & RELOAD) ──

#### TC-INT-01-01: Khởi tạo context khi mở trực tiếp URL hợp lệ kèm shopId
- **Trace ID**: `TC-INT-01-01` | **Mức ưu tiên**: P0 (Blocker) | **Kỹ thuật**: State Transition
- **Mục tiêu**: Đảm bảo Host Shell chặn MFE render cho tới khi `WI_SHOP_CONTEXT` và `WI_USER_CONTEXT` tải xong từ backend thực tế.
- **Tiền điều kiện**: Trình duyệt truy cập trực tiếp URL `http://localhost:4200/#/1784471989/customers`. LocalStorage chưa có cache.
- **Các bước thực hiện**:
  1. Khởi động Host Shell và route guard.
  2. Giả lập backend phản hồi `currentUser` sau 300ms, `shopContext` sau 200ms.
  3. Quan sát trạng thái MFE loading và context injector.
- **Dữ liệu kiểm thử**: `shopId = 1784471989` (kiểu số nguyên hợp lệ), tenant UUID `01a03dc0-818f-71bb-a0a6-8b2bd8694474`.
- **Kết quả mong đợi**:
  - Route guard giữ trạng thái pending, hiển thị skeleton/loading của Host.
  - Không ném `NullInjectorError` cho các MFE components.
  - Khi API 200 OK: MFE nạp đúng `shopId = 1784471989`, `currentUser` có `userId` dạng chuỗi và tên thật. Không tồn tại dữ liệu mock.

#### TC-INT-01-02: F5 reload khi mạng chậm không dùng timeout giả lập
- **Trace ID**: `TC-INT-01-02` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Boundary Value Analysis
- **Mục tiêu**: Xác minh hệ thống không bị timeout giả lập 600ms ngắt quãng hoặc tự gán user giả khi mạng trễ.
- **Tiền điều kiện**: User đang ở trang nghiệp vụ, bấm F5. Mạng mô phỏng Slow 3G (trễ 2500ms).
- **Các bước thực hiện**:
  1. F5 trình duyệt.
  2. API context phản hồi sau 2500ms.
- **Kết quả mong đợi**:
  - Không có cờ timeout (như `setTimeout 600ms`) tự ý ép `ready = true`.
  - Không render giao diện lỗi trước khi API phản hồi.
  - Readiness check hoàn thành chính xác ở mốc 2500ms.

#### TC-INT-01-03: F5 với shopId không hợp lệ trong URL
- **Trace ID**: `TC-INT-01-03` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Equivalence Partitioning (Invalid)
- **Mục tiêu**: Xử lý an toàn khi URL chứa shopId sai định dạng (chuỗi UUID, số âm, NaN).
- **Tiền điều kiện**: Người dùng nhập URL `http://localhost:4200/#/invalid-shop-uuid/customers`.
- **Các bước thực hiện**:
  1. Route guard đọc `shopId` từ route param.
  2. Kiểm tra parser `WIShopIdentity`.
- **Kết quả mong đợi**:
  - `WIShopIdentity` từ chối parse chuỗi non-integer thành `shopId`.
  - Không tạo tenant rác hoặc tenant mặc định.
  - Chuyển hướng an toàn về màn hình Chọn cửa hàng (`/select-shop`) hoặc trang lỗi thân thiện.

#### TC-INT-01-04: Đồng bộ bản dịch i18n khi mở trực tiếp
- **Trace ID**: `TC-INT-01-04` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Equivalence Partitioning
- **Mục tiêu**: Đảm bảo JSON bản dịch tải thành công, không hiển thị raw key `CUSTOMER.*` hoặc `CDP.*`.
- **Tiền điều kiện**: Truy cập trực tiếp link MFE với locale `vi`.
- **Kết quả mong đợi**:
  - `assets/i18n/vi/*.json` tải đúng từ host/remote, không 404.
  - Toàn bộ nhãn hiển thị tiếng Việt chuẩn xác, 0 raw key lọt ra màn hình.

---

### ── KỊCH BẢN 2: ĐỔI SHOP A ➔ B KHI REQUEST A CÒN CHẠY (RACE CONDITION) ──

#### TC-INT-02-01: Hủy hoặc vô hiệu hóa in-flight request của Shop A khi đổi sang Shop B
- **Trace ID**: `TC-INT-02-01` | **Mức ưu tiên**: P0 (Blocker) | **Kỹ thuật**: Concurrency / Race Condition
- **Mục tiêu**: Đảm bảo request của Shop A đang chạy bị hủy ngay khi người dùng chọn Shop B.
- **Tiền điều kiện**: Đang ở Shop A (`shopId: 101`), trigger API tải dữ liệu lớn (trễ 2000ms).
- **Các bước thực hiện**:
  1. Phát sự kiện đổi sang Shop B (`shopId: 102`) ở thời điểm 300ms.
  2. Quan sát HTTP traffic qua interceptor/network.
- **Kết quả mong đợi**:
  - Request Shop A bị cancel lập tức qua cơ chế `switchMap` / `takeUntil(shopChange$)`.
  - Dữ liệu Shop A trong context store bị reset về pending/null ngay lập tức.

#### TC-INT-02-02: Chặn phản hồi muộn của Shop A ghi đè lên Shop B
- **Trace ID**: `TC-INT-02-02` | **Mức ưu tiên**: P0 (Blocker) | **Kỹ thuật**: Timing / Fault Injection
- **Mục tiêu**: Giả lập Request Shop A không thể cancel (vẫn trả về sau 1500ms), trong khi Shop B đã nhận xong dữ liệu ở 500ms.
- **Tiền điều kiện**: Request A (Shop 101) trả về lúc t = 1500ms. Request B (Shop 102) trả về lúc t = 500ms.
- **Các bước thực hiện**:
  1. t = 0ms: Kích hoạt tải Shop A (Generation ID: gen-1).
  2. t = 100ms: Đổi sang Shop B (Generation ID: gen-2).
  3. t = 500ms: Response Shop B về. Store nhận gen-2.
  4. t = 1500ms: Response Shop A về muộn mang gen-1.
- **Kết quả mong đợi**:
  - Store kiểm tra Generation ID: `gen-1 !== currentGen (gen-2)`.
  - Response Shop A bị DROP hoàn toàn.
  - Giao diện và context giữ nguyên 100% dữ liệu của Shop B.

#### TC-INT-02-03: Header HTTP shopId đồng bộ tuyệt đối với Shop B
- **Trace ID**: `TC-INT-02-03` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Interceptor Verification
- **Mục tiêu**: Đảm bảo mọi request phát sinh sau khi đổi shop mang đúng header `shopId: 102`.
- **Tiền điều kiện**: Đổi shop A (`101`) -> Shop B (`102`). Event chọn shop phát trước khi URL router hoàn tất.
- **Các bước thực hiện**:
  1. Trigger event chọn shop.
  2. MFE gửi đồng thời 3 request nghiệp vụ.
  3. Interceptor inject header.
- **Kết quả mong đợi**:
  - 100% request mang header `shopId: 102`. Không request nào mang header `101`.

#### TC-INT-02-04: Đổi shop liên tục (Shop Toggling Stress Test)
- **Trace ID**: `TC-INT-02-04` | **Mức ưu tiên**: P2 | **Kỹ thuật**: Stress Testing / State Convergence
- **Mục tiêu**: Thao tác đổi shop liên tục A -> B -> A -> B trong 500ms.
- **Kết quả mong đợi**:
  - Trạng thái hội tụ chính xác về Shop B cuối cùng.
  - Không xảy ra deadlock hoặc memory leak.

---

### ── KỊCH BẢN 3: ĐỔI TÀI KHOẢN CÙNG SHOP (ACCOUNT SWITCH SAME SHOP) ──

#### TC-INT-03-01: Tải lại toàn bộ User Context và Permissions khi đổi tài khoản cùng shopId
- **Trace ID**: `TC-INT-03-01` | **Mức ưu tiên**: P0 (Security Blocker) | **Kỹ thuật**: Equivalence Partitioning
- **Mục tiêu**: Chặn lỗi bỏ qua tải lại do deduplicate sai (`prevShopId === nextShopId`).
- **Tiền điều kiện**: User 1 (Admin, `userId: "usr_admin_01"`) đăng xuất, User 2 (Thu ngân, `userId: "usr_cashier_02"`) đăng nhập vào cùng Shop `1784471989`.
- **Các bước thực hiện**:
  1. Đổi token sang User 2.
  2. Kích hoạt luồng làm mới phiên của Host.
- **Kết quả mong đợi**:
  - Hệ thống nhận biết `userId` thay đổi, kích hoạt tải lại `WI_USER_CONTEXT` và `WI_PERMISSION_CONTEXT`.
  - `currentUser` và `user$` cập nhật đồng bộ sang `usr_cashier_02`.

#### TC-INT-03-02: Thu hồi quyền Admin ngay lập tức khi đổi sang tài khoản hạn chế
- **Trace ID**: `TC-INT-03-02` | **Mức ưu tiên**: P0 (Security Blocker) | **Kỹ thuật**: Security Matrix
- **Mục tiêu**: Đảm bảo quyền hạn cũ bị thu hồi 100%, không rò rỉ quyền Admin sang tài khoản Thu ngân.
- **Tiền điều kiện**: User 1 có quyền `CASHBOOK_DELETE`, User 2 chỉ có `CASHBOOK_VIEW`.
- **Kết quả mong đợi**:
  - `WI_PERMISSION_CONTEXT.check('CASHBOOK_DELETE')` trả về `false` ngay lập tức.
  - Các nút Xóa/Sửa trên giao diện MFE bị ẩn/disable đồng bộ.

#### TC-INT-03-03: Tách biệt tuyệt đối giữa ShopUserDto.id và ShopUserDto.userId
- **Trace ID**: `TC-INT-03-03` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Contract Verification
- **Mục tiêu**: Ngăn chặn lỗi ép kiểu `parseInt(userId)` hoặc nhầm lẫn giữa ID bản ghi nhân viên với ID tài khoản.
- **Dữ liệu kiểm thử**: `ShopUserDto.id = 852` (số nguyên), `ShopUserDto.userId = "usr_uuid_999"` (chuỗi).
- **Kết quả mong đợi**:
  - `currentUser.id` là số nguyên `852`.
  - `currentUser.userId` là chuỗi nguyên bản `"usr_uuid_999"`.
  - Không xuất hiện `NaN` trong bất kỳ trường dữ liệu nào.

#### TC-INT-03-04: Cập nhật danh sách nhân viên shopUserList$ khi đổi quyền
- **Trace ID**: `TC-INT-03-04` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Observable Verification
- **Kết quả mong đợi**:
  - `shopUserList$` phát danh sách nhân viên mới có chứa trường `shopUsers` và `totalUser` đầy đủ theo DTO thật.

---

### ── KỊCH BẢN 4: LOGOUT / LOGIN (SESSION LIFECYCLE & SYNC) ──

#### TC-INT-04-01: Đăng xuất cùng tab xóa sạch toàn bộ Context tức thì
- **Trace ID**: `TC-INT-04-01` | **Mức ưu tiên**: P0 (Blocker) | **Kỹ thuật**: State Transition
- **Mục tiêu**: Khắc phục hạn chế trình duyệt không phát event `storage` cho chính tab thực hiện ghi.
- **Tiền điều kiện**: Người dùng nhấn "Đăng xuất" tại Tab 1.
- **Các bước thực hiện**:
  1. Hàm `authService.logout()` được gọi.
  2. Kiểm tra trạng thái các providers trong Tab 1.
- **Kết quả mong đợi**:
  - Host kích hoạt trực tiếp hàm `clear()` trên toàn bộ Context Store mà không chờ `storage` event.
  - `WI_USER_CONTEXT`, `WI_SHOP_CONTEXT`, `WI_BUSINESS_CONTEXT`, `WI_PERMISSION_CONTEXT` đều chuyển về `null`.
  - Mọi request in-flight bị abort ngay lập tức.

#### TC-INT-04-02: Đồng bộ đăng xuất đa tab qua storage event
- **Trace ID**: `TC-INT-04-02` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Cross-Tab Synchronization
- **Mục tiêu**: Khi Tab 2 đăng xuất, Tab 1 phải tự động hủy session và điều hướng về trang Login.
- **Tiền điều kiện**: Mở 2 tab cùng đăng nhập một tài khoản.
- **Các bước thực hiện**:
  1. Bấm đăng xuất ở Tab 2.
  2. Tab 1 nhận event `window.addEventListener('storage')`.
- **Kết quả mong đợi**:
  - Tab 1 lập tức purge sạch memory context.
  - Chuyển hướng an toàn về màn hình đăng nhập, không lưu vết token.

#### TC-INT-04-03: Chặn response đến sau thời điểm logout khôi phục phiên
- **Trace ID**: `TC-INT-04-03` | **Mức ưu tiên**: P0 (Security) | **Kỹ thuật**: Timing / Fault Injection
- **Tiền điều kiện**: Request API thông tin người dùng gửi lúc t = 0. Bấm logout lúc t = 100ms. Response 200 trả về lúc t = 400ms.
- **Kết quả mong đợi**:
  - Cờ phiên `isLoggedOut = true` chặn không cho response t = 400ms ghi dữ liệu vào store.
  - Context giữ nguyên trạng thái `null`.

#### TC-INT-04-04: Đăng nhập lại tạo phiên mới tinh (Clean Slate)
- **Trace ID**: `TC-INT-04-04` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Lifecycle Testing
- **Kết quả mong đợi**:
  - Đăng nhập thành công tạo Generation ID mới.
  - Toàn bộ dữ liệu tải mới 100%, không bị ảnh hưởng bởi session cũ.

---

### ── KỊCH BẢN 5: API LỖI / RETRY (FAULT RESILIENCE & STREAM SURVIVAL) ──

#### TC-INT-05-01: Lỗi API phụ không được làm chết giao diện chính (Tránh bẫy forkJoin)
- **Trace ID**: `TC-INT-05-01` | **Mức ưu tiên**: P0 (Reliability) | **Kỹ thuật**: Fault Tolerance
- **Mục tiêu**: Kiểm tra màn hình tải nhiều API đồng thời (ví dụ: `receipts/search-filter` 200 OK, nhưng `receipts/summary` trả về HTTP 500).
- **Tiền điều kiện**: Mock endpoint danh sách trả về 200 OK (20 bản ghi), endpoint thống kê trả về 500 Internal Error.
- **Các bước thực hiện**:
  1. Mở màn hình danh sách.
  2. Component gọi các API phụ thuộc.
- **Kết quả mong đợi**:
  - Danh sách chính vẫn hiển thị đầy đủ 20 bản ghi.
  - Chỉ riêng khối thống kê hiển thị thông báo lỗi cục bộ hoặc fallback `--`.
  - Tuyệt đối không dùng `forkJoin` trần khiến toàn bộ màn hình bị trắng xoá.

#### TC-INT-05-02: Observable Context sống sót qua lỗi HTTP 500
- **Trace ID**: `TC-INT-05-02` | **Mức ưu tiên**: P0 (Architecture) | **Kỹ thuật**: Stream Resilience
- **Mục tiêu**: Đảm bảo observable `user$` hoặc `changes$` không bị `complete()` hay `error()` vĩnh viễn khi API lỗi.
- **Tiền điều kiện**: API `currentUser` trả về HTTP 500 lần đầu.
- **Các bước thực hiện**:
  1. Lần 1: API lỗi 500 -> Observable phát trạng thái error hoặc fallback an toàn qua `catchError`.
  2. Lần 2: Người dùng bấm Thử lại (Retry) -> API trả về 200 OK.
- **Kết quả mong đợi**:
  - Observable stream vẫn mở và tiếp tục phát giá trị mới khi retry thành công.
  - Subscriber không bị ngắt kết nối.

#### TC-INT-05-03: Xóa cờ lỗi giao diện sau khi Retry thành công
- **Trace ID**: `TC-INT-05-03` | **Mức ưu tiên**: P1 | **Kỹ thuật**: State Transition
- **Mục tiêu**: Ngăn chặn lỗi "API đã phục hồi nhưng màn hình lỗi vẫn hiện do quên reset `errorStatus`".
- **Kết quả mong đợi**:
  - Khi API retry trả về 200: Cờ `errorStatus` lập tức chuyển thành `false`, lớp overlay báo lỗi biến mất, hiển thị giao diện dữ liệu bình thường.

#### TC-INT-05-04: Xử lý lỗi 401 Unauthorized và 403 Forbidden chuẩn mực
- **Trace ID**: `TC-INT-05-04` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Boundary & Security
- **Kết quả mong đợi**:
  - 401: Kích hoạt luồng refresh token của Host Shell; nếu refresh thất bại mới chuyển về login.
  - 403: Không tự ý sinh quyền giả lập để bypass; hiển thị đúng thông báo "Không có quyền truy cập".

---

### ── KỊCH BẢN 6: SUBSCRIBER VÀO MUỘN (LATE SUBSCRIBER & REPLAY) ──

#### TC-INT-06-01: Late Subscriber nhận ngay giá trị mới nhất qua BehaviorSubject/shareReplay
- **Trace ID**: `TC-INT-06-01` | **Mức ưu tiên**: P0 (Architecture) | **Kỹ thuật**: Timing & Concurrency
- **Mục tiêu**: Đảm bảo MFE con tải lazy sau 5 giây vẫn nhận ngay context hiện tại mà không phải gọi lại API.
- **Tiền điều kiện**: Host Shell đã nạp xong context lúc t = 500ms.
- **Các bước thực hiện**:
  1. t = 5000ms: Lazy route MFE mount và subscribe vào `WI_USER_CONTEXT.user$`.
  2. Đo đạc thời gian nhận dữ liệu và số lượng network request phát sinh.
- **Kết quả mong đợi**:
  - MFE nhận dữ liệu ngay lập tức (< 10ms) qua cơ chế Replay.
  - Số lượng network request phát sinh thêm = 0.

#### TC-INT-06-02: Phân biệt chính xác giữa danh sách rỗng hợp lệ và trạng thái chưa tải
- **Trace ID**: `TC-INT-06-02` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Boundary Value Analysis
- **Mục tiêu**: Đảm bảo `shopUserList$` phát mảng rỗng `[]` khi shop chưa có nhân viên, và late subscriber không bị treo loading.
- **Dữ liệu kiểm thử**: API trả về `{ shopUsers: [], totalUser: 0 }`.
- **Kết quả mong đợi**:
  - Late subscriber nhận mảng rỗng `[]`, hiển thị empty-state "Chưa có nhân viên".
  - Không bị nhầm sang `null` (loading vô tận).

#### TC-INT-06-03: Đồng bộ giá trị giữa getter đồng bộ và observable cho Late Subscriber
- **Trace ID**: `TC-INT-06-03` | **Mức ưu tiên**: P1 | **Kỹ thuật**: Consistency Check
- **Mục tiêu**: Đảm bảo `WI_USER_CONTEXT.currentUser` và giá trị emit từ `user$` cho late subscriber là đồng nhất 100%.
- **Kết quả mong đợi**:
  - `expect(currentUser).toEqual(emittedUser)`. Không có độ lệch trường hay giá trị.

#### TC-INT-06-04: Giải phóng subscription khi component/modal bị destroy
- **Trace ID**: `TC-INT-06-04` | **Mức ưu tiên**: P2 | **Kỹ thuật**: Memory Leak Prevention
- **Mục tiêu**: Ngăn chặn rò rỉ bộ nhớ khi mở/đóng modal MFE nhiều lần.
- **Kết quả mong đợi**:
  - Sử dụng `takeUntilDestroyed()` hoặc `Subscription.unsubscribe()`.
  - Số lượng active subscriber của context store trở về trạng thái ban đầu sau khi destroy.

---

## 4. QUY TRÌNH THỰC THI & NGHIỆM THU TỰ ĐỘNG (AUTOMATED TEST HARNESS)

### Lệnh chạy kiểm thử đơn vị & tích hợp Jest:
```bash
# Kiểm thử toàn bộ context và providers suite
cd /home/baoltb/Desktop/Room_Agent/projects/wicx-crm-fe
npx jest --config apps/app-shell/jest.config.ts --testPathPattern="context|provider"

# Kiểm thử độc lập MFE CDP Data Raw
npx jest --config apps/mfe-cdp/jest.config.ts apps/mfe-cdp/src/app/pages/data-raw/raw-event-list.component.spec.ts
```

### Tiêu chí đóng cổng chất lượng (Decision Gate Closure Criteria):
- [x] **100% Pass**: Tất cả 24 Testcases thuộc 6 kịch bản kiểm thử tích hợp phải đạt trạng thái PASS.
- [x] **0 Hardcoded Mocks**: Không tồn tại cờ mock allow-all quyền hoặc user giả trong code nghiệm thu.
- [x] **Zero Memory Leaks**: Xác minh 100% subscription được dọn dẹp khi đổi scope.
- [x] **Harness Work Items Sync**: 24 Testcase items được đồng bộ và đóng trên Floci DynamoDB.
