# PRODUCT.md — Customer 360 Profile & Operational Hub

> **Product**: WiCX CRM & CDP Front-End  
> **Feature**: Hồ Sơ Khách Hàng 360 (Customer 360 Profile & Relationship Hub)  
> **Source Evidence**: Thiết kế Figma mockup, `DESIGN.md`, `private/open-design.md`, `private/ux-research.md`  
> **Platform**: Web Desktop (Angular 18, TDS UI, Tailwind CSS)  

---

## 1. Executive Summary & Problem Definition

### 1.1. Trải nghiệm cần tạo dựng (What experience are we trying to create?)
Một trung tâm dữ liệu và điều hành quan hệ khách hàng hợp nhất (**Customer 360 Operational Hub**). Nơi nhân viên kinh doanh (Sales), nhân viên chăm sóc khách hàng (CSKH) và quản lý cửa hàng có thể nắm bắt toàn bộ bối cảnh của một khách hàng trong vòng 5 giây:
1. **Định danh & Tổ chức**: Khách hàng là ai, đã định danh hay chưa, thuộc những doanh nghiệp nào, ai đang phụ trách.
2. **Giá trị thương mại (Commercial Value)**: Tổng giá trị chi tiêu, các gói giải pháp/phần mềm đã mua, gói nào sắp hết hạn cần gia hạn (upsell/cross-sell/renewal).
3. **Mức độ gắn kết đa kênh (Cross-channel Engagement Heatmap)**: Trực quan hóa tần suất tương tác trên ma trận tháng x kênh (Facebook, Zalo, Website, Tổng đài) và drill-down vào từng sự kiện cụ thể.
4. **Hành động & Kế hoạch (Actionable Collaboration)**: Lịch hẹn sắp tới và sổ ghi chú trao đổi nội bộ thời gian thực.

### 1.2. Vị trí trong hệ thống hiện tại (How it fits into existing product)
- **Điểm vào (Entrypoint)**: Từ màn hình **Danh sách Khách hàng** (`/customers` hoặc `/contact`), người dùng click vào tên khách hàng ở cột "Khách hàng" (đã được cấu hình `hover:tds-color-text-interactive hover:underline hover:font-semibold`).
- **Hình thức hiển thị (View Mode)**: Mở toàn màn hình hoặc trang chi tiết chuyên biệt `/customers/:id`, đồng bộ URL và hỗ trợ back/forward của trình duyệt.
- **Tương tác liên kết**:
  - Click "Tạo lịch hẹn" mở drawer `CreateAppointmentModalComponent`.
  - Click "Chỉnh sửa" mở modal `EditContactModalComponent`.
  - Click vào ô Heatmap tháng/kênh lọc nhật ký sự kiện tương ứng từ CDP Raw Event Pipeline.

---

## 2. User Journey & Flow Specifications

### 2.1. Hành trình người dùng chính (Primary User Journeys)

#### Journey 1: Nhân viên CSKH kiểm tra trước cuộc gọi chăm sóc (Pre-call Context Review)
1. CSKH nhận ticket hoặc có lịch hẹn "Demo Tpos Pro".
2. Truy cập hồ sơ khách hàng `Trần Thị Minh Ngọc`.
3. Nhìn lướt Cột 1: Nắm bắt số điện thoại `0901892384`, đơn vị công tác `Nhà Thuốc Long Châu`, phụ trách bởi `Minh Đạt`.
4. Nhìn lướt Cột 2 (Hero box): Tổng chi tiêu `12.000.000 đ`, có `1 gói đã hết hạn` (Landing Pro) và 3 gói còn hạn 117 ngày.
5. Nhìn Cột 2 (Heatmap): Thấy khách hàng vừa nhắn tin qua Zalo OA 4 lần trong Tháng 4, click ô Zalo Tháng 4 để đọc nội dung tin nhắn gần nhất.
6. Đọc Cột 3 (Notes feed): Thấy đồng nghiệp Hoàng Khôi ghi chú "Khách hàng bận thứ 2 gọi lại. Tư vấn dịch vụ".
7. Thực hiện cuộc gọi với đầy đủ thông tin bối cảnh mà không cần hỏi lại khách hàng những câu hỏi cơ bản.

#### Journey 2: Quản lý / CSKH tạo ghi chú nhanh sau tương tác
1. Sau khi kết thúc cuộc gọi/chat, người dùng đưa con trỏ chuột vào ô "Nhập ghi chú, Enter để thêm" ở Cột 3.
2. Gõ nội dung trao đổi: "Đã tư vấn gói gia hạn POS, khách đồng ý nhận báo giá qua email".
3. Nhấn phím `Enter`.
4. Ghi chú mới lập tức xuất hiện ở vị trí đầu tiên của Feed kèm avatar, tên tài khoản đăng nhập hiện tại và timestamp `dd/MM/yyyy HH:mm`.

---

## 3. Information Architecture & Screen Inventory

### 3.1. Bố cục 3 Cột (Information Architecture)

```text
[Header Toàn Cục: Breadcrumb / Khách hàng / Chi tiết [NV0015-21] / Nút Quay lại]
───────────────────────────────────────────────────────────────────────────────────
CỘT TRÁI (340px - 360px)        CỘT GIỮA (Flex-1)                 CỘT PHẢI (360px - 400px)
├─ Khối 1: Identity & Meta      ├─ Khối 3: Purchase & Subscriptions├─ Khối 5: Upcoming Appointments
│  • Avatar + Định danh         │  • Hero KPI Card (Cam TDS)      │  • Header + Nút Tạo lịch hẹn
│  • Tên, Mã KH, Sửa, Xóa       │  • Grid thẻ dịch vụ đã mua      │  • List thẻ cuộc hẹn có tag priority
│  • Bảng 8 trường thuộc tính   │                                 │
├─ Khối 2: Doanh nghiệp (Org)   ├─ Khối 4: Heatmap & Activity Log ├─ Khối 6: Notes Feed
│  • List công ty liên kết      │  • Tabs Hoạt động / Chỉnh sửa   │  • Input thêm nhanh (Enter)
│  • Chức vụ, Hotline, Địa chỉ  │  • Ma trận Tháng x Kênh         │  • Dòng thời gian trao đổi nội bộ
│                               │  • Chi tiết nhật ký bên dưới    │
```

### 3.2. Bảng kê trạng thái màn hình (Screen & State Inventory)

| Khối / Thành phần | Trạng thái hiển thị (States) | Quy tắc xử lý giao diện |
|---|---|---|
| **Khối 1: Summary** | Normal / Editing / Unidentified | Hiện tag xanh "Đã định danh" hoặc xám "Chưa định danh". Nút Chỉnh sửa mở modal edit. |
| **Khối 2: Doanh nghiệp** | Has Data / Empty / Loading | Khi không có DN liên kết: Hiển thị Empty state gọn nhẹ với nút "+ Liên kết doanh nghiệp". |
| **Khối 3: Mua hàng** | Active / Expired Packages | Hero card chuyển màu cam cảnh báo nếu có gói hết hạn. Badge "Đã hết hạn" (đỏ) hoặc "Còn X ngày" (xanh lá). |
| **Khối 4: Heatmap** | Default Cell / Hover / Selected | Hover hiện tooltip `[Kênh] • [Tháng] • [Số lượng]`. Click ô có sự kiện: Highlight viền xanh `#0068FF` và reload log bên dưới. |
| **Khối 5: Lịch hẹn** | List / Empty / Create New | Hiển thị thẻ cuộc hẹn sắp tới. Bấm "+ Tạo lịch hẹn" mở drawer `CreateAppointmentModal`. |
| **Khối 6: Ghi chú** | Typing / Submitting / Feed | Nhấn Enter gửi ghi chú ngay lập tức (optimistic UI update), xử lý loading spinner tại icon Enter nếu mạng chậm. |

---

## 4. UX Pattern Evidence & Reference Mapping

Theo tiêu chuẩn phân tích từ Mobbin (`private/ux-research.md`) và các hệ thống CRM hàng đầu (HubSpot 360, Salesforce Lightning, Stripe Customer Dashboard):

1. **Split-Screen Contextual Triage (3-Column Layout)**:
   - *Evidence*: HubSpot Customer Record & Stripe Dashboard chia 3 cột cố định: Identity (Trái) — Core Insights/Timeline (Giữa) — Next Steps/Actions (Phải). Giúp người dùng không phải chuyển tab để vừa đọc hồ sơ vừa tạo ghi chú.
2. **Activity Density Matrix (GitHub/Linear-style Heatmap)**:
   - *Evidence*: Khác với danh sách nhật ký sự kiện cuộn dài bất tận, ma trận tháng x kênh giúp người dùng phát hiện ngay quy luật tương tác (khách hàng chuộng kênh nào nhất, tháng nào tương tác đột biến) chỉ trong 1 ánh nhìn.
3. **Inline Quick-Add (Slack / Notion Notes Pattern)**:
   - *Evidence*: Không bắt người dùng mở modal/popup để ghi một dòng note ngắn. Input 1 dòng nhấn Enter giúp tăng 300% tỷ lệ nhân viên chịu cập nhật nhật ký sau cuộc gọi.

---

## 5. Design Decisions & Assumptions

### 5.1. Quyết định thiết kế đã chốt (Decisions)
- **Hệ thống Design System**: Tuân thủ 100% token của TDS UI và bản đặc tả `DESIGN.md` (Theme preset `orange` `#F35431`, font `SF Pro Text`, icon font `tdsi-*`).
- **Heatmap Interaction**: Ô không có sự kiện để mờ (`opacity-40` hoặc nền xám nhạt), không cho click. Ô có sự kiện hiển thị số lượng rõ ràng, hover có tooltip và click có border highlight xanh.
- **Tiền tệ & Ngày tháng**: Định dạng tiền tệ VND (`12.000.000 đ`), định dạng ngày chuẩn Việt Nam `dd/MM/yyyy` và thời gian `HH:mm`.

### 5.2. Giả định & Câu hỏi mở (Assumptions & Open Questions)
- *Giả định 1*: Dữ liệu sự kiện trong Heatmap lấy từ nguồn CDP Raw Event Data đã được đồng bộ qua Kafka/MinIO.
- *Giả định 2*: Khách hàng có thể thuộc nhiều Doanh nghiệp (quan hệ n-n), mỗi liên kết có vai trò (Role) và số hotline riêng.
- *Câu hỏi mở cho BA*: Khi bấm vào nút "Xóa" cạnh nút "Chỉnh sửa" ở góc trên bên trái, hệ thống hiển thị confirm dialog xóa mềm (soft delete) hay chuyển trạng thái về `inactive`? (Hiện tại mockup hiển thị icon thùng rác viền đỏ).
