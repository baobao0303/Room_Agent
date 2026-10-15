# Đặc Tả Kỹ Thuật & Giao Diện: Hồ Sơ Khách Hàng 360 (Customer 360 Profile)

> **Mã phân hệ:** `CDP / CRM Customer 360`  
> **Tài liệu tham chiếu:**  
> - `projects/wicx-crm-fe/DESIGN.md` (Hệ thống màu, typography, khoảng cách TDS UI)  
> - `private/open-design.md` & `private/ux-research.md` (Cấu trúc trải nghiệm UX & xác thực prototype)  
> - `tds-ui-usage` (`@tmt-co/tds-ui` - Angular 18 Standalone, Signals)  
> **Theme:** `orange` (Primary Brand `#F35431`), Mode `light`  

---

## 1. Tổng Quan Kiến Trúc & Bố Cục (Layout Architecture)

Màn hình Hồ sơ Khách hàng 360 được thiết kế dạng **Dashboard 3 Cột (3-Column Responsive Grid)** trên nền canvas xám nhạt `tds-color-background-neutral-minimalist` (`#F2F5F8`), khoảng cách giữa các khối `gap-4`:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  CUSTOMER 360 DASHBOARD                                                                                          │
├─────────────────────────┬──────────────────────────────────────────────────────────────┬─────────────────────────┤
│ CỘT 1: PROFILE & ORG    │ CỘT 2: PURCHASES & ACTIVITY HEATMAP                          │ CỘT 3: APPOINTMENT & NOTE│
│ (W: 340px - 360px)      │ (Flex: 1, min-w-0)                                           │ (W: 360px - 400px)      │
├─────────────────────────┼──────────────────────────────────────────────────────────────┼─────────────────────────┤
│ [Khối 1: Thông tin cá   │ [Khối 3: Thông tin mua hàng]                                 │ [Khối 5: Lịch hẹn sắp   │
│  nhân & Định danh]      │ ┌───────────────────┬──────────────────────────────────────┐ │  tới (Appointments)]    │
│ • Avatar 80px + Tag     │ │ KPI Tổng giá trị  │ Grid 4 Gói dịch vụ đã mua            │ │ • Header + Nút Tạo hẹn │
│ • Tên + Giới tính       │ │ đã mua:           │ • wìpìx Landing Pro (Đã hết hạn)     │ │ • List Card hẹn:      │
│ • Mã KH [NV0015-21]     │ │ 12.000.000 đ      │ • tpcs POS Nâng cao (Còn 117 ngày)   │ │   - Tên lịch hẹn      │
│ • Nút Chỉnh sửa / Xóa   │ │                   │ • wion Gói Năm (Còn 117 ngày)        │ │   - Tag Ưu tiên       │
│ • Metadata: Trạng thái, │ │ Đã hết hạn: 1 gói │ • wìpìx Landing Pro (Còn 117 ngày)   │ │   - Dịch vụ tư vấn    │
│   SĐT, Email, Địa chỉ,  │ └───────────────────┴──────────────────────────────────────┘ │   - Ghi chú hỗ trợ    │
│   Nguồn, Người phụ trách│                                                              │   - Người phụ trách   │
├─────────────────────────┼──────────────────────────────────────────────────────────────┼─────────────────────────┤
│ [Khối 2: Doanh nghiệp   │ [Khối 4: Heatmap Ma trận Hoạt động & Timeline]               │ [Khối 6: Ghi chú        │
│  liên kết (Companies)]  │ • Tab: Lịch sử hoạt động | Lịch sử chỉnh sửa                 │  nội bộ (Notes Feed)]   │
│ • Danh sách thẻ DN con: │ • Gợi ý: "(i) Bấm vào các ô để xem lịch sử"                  │ • Input + Phím Enter    │
│   - Nhà Thuốc Long Châu │ • Bảng ma trận Tháng 11 .. Tháng 06 theo 4 kênh:             │ • Danh sách ghi chú     │
│   - Nhà Thuốc Minh Châu │   Facebook, Zalo, Website, Tổng đài                          │   theo thời gian kèm    │
│   - Chức danh, Hotline  │ • Tooltip chi tiết khi hover từng ô số                       │   Avatar & vai trò nhân │
│   - Địa chỉ chi nhánh   │ • Danh sách nhật ký sự kiện chi tiết bên dưới ô được chọn    │   viên chăm sóc         │
└─────────────────────────┴──────────────────────────────────────────────────────────────┴─────────────────────────┘
```

---

## 2. Chi Tiết Từng Khối Giao Diện & TDS UI Mapping

### 2.1. Cột 1 — Trái: Hồ Sơ Cá Nhân & Doanh Nghiệp Liên Kết

#### Khối 1: Thông tin cá nhân & Định danh (`CustomerSummaryCardComponent`)
- **TDS Components & Directives:**
  - `tds-card` hoặc container `rounded-xl border tds-color-border-secondary tds-color-surface-lowest p-5 shadow-xs`.
  - `TDSAvatarModule` (`tds-avatar`): Ảnh đại diện tròn `size-20` (80px), viền trắng `border-2`.
  - `TDSTagModule` (`tds-tag`):
    - Tag định danh: `color="success"` (`tds-tag-success`), icon `tdsi-check-circle-fill`, text "Đã định danh".
    - Tag trạng thái: `color="success"` variant minimalist (`bg-[#E8F8F0] text-[#0E9347]`), text "Đang tương tác".
    - Tag kênh nguồn: `color="secondary"` (`WiPix`, `Facebook`).
  - `TDSButtonModule`:
    - Nút Chỉnh sửa: `button[tds-button-outline]` `color="secondary"` `size="sm"` `tdsPrefixIcon="tdsi-edit-line"`.
    - Nút Xóa: `button[tds-button-outline]` `color="error"` `size="sm"` `tdsPrefixIcon="tdsi-trash-line"`.
- **Thông tin hiển thị:**
  - Tên khách hàng: `tds-heading-5 font-bold tds-color-text-primary` (`Trần Thị Minh Ngọc`) kèm biểu tượng giới tính nữ `♀` (`#F43F5E`).
  - Mã khách hàng: Badge font mono `tds-caption-1 font-semibold tds-color-text-interactive` (`[NV0015-21]`).
  - Danh sách trường chi tiết (Label `tds-body-2 tds-color-text-secondary w-36`, Value `tds-body-2 font-medium tds-color-text-primary`):
    - Người phụ trách: Avatar chữ tròn mini 20px (Màu hồng `Đ`) + text "Minh Đạt".
    - Số điện thoại: `0901892384` (copyable).
    - Ngày sinh: `12/12/1999`.
    - Email: `nguyenvana1234@gmail.com`.
    - Địa chỉ: `12 Nguyễn Huệ, P. Bến Nghé, Hồ Chí Minh`.
    - Ngày tạo: `10/10/2026`.
    - Ngày hoạt động cuối: `18/10/2026`.

#### Khối 2: Doanh nghiệp liên kết (`CustomerOrganizationsCardComponent`)
- **Header:** Biểu tượng cờ `tdsi-flag-line`, tiêu đề `Doanh nghiệp (2)`.
- **Danh sách thẻ:**
  - Card con nền phẳng `tds-color-background-neutral-minimalist rounded-lg p-3.5 border border-dashed tds-color-border-secondary flex flex-col gap-1`:
    - Tên doanh nghiệp: `tds-body-2 font-semibold tds-color-text-primary` (`Nhà Thuốc Long Châu`, `Nhà Thuốc Minh Châu`).
    - Vai trò & Hotline: `tds-caption-1 tds-color-text-secondary` (`Giám đốc kinh doanh / +84 28 382 1100`).
    - Địa chỉ trụ sở: `tds-caption-1 tds-color-text-tertiary truncate`.

---

### 2.2. Cột 2 — Giữa: Thông Tin Mua Hàng & Ma Trận Hoạt Động (Heatmap)

#### Khối 3: Thông tin mua hàng (`CustomerPurchaseInfoComponent`)
- **Container chung:** `rounded-xl border tds-color-border-secondary tds-color-surface-lowest p-4 flex gap-4`.
- **Thẻ KPI bên trái (Hero Box):**
  - Kích thước: `w-56 shrink-0 rounded-lg p-4 flex flex-col justify-between text-white shadow-sm`.
  - Gradient nền: `bg-gradient-to-br from-[#FF6B4A] to-[#F35431]` (TDS Orange Brand).
  - Nội dung:
    - Nhãn trên: `tds-caption-1 font-semibold uppercase tracking-wider opacity-90` ("Thông tin mua hàng").
    - Giữa: Nhãn nhỏ "Tổng giá trị đã mua" + Giá trị lớn `text-2xl font-extrabold tracking-tight` (`12.000.000 đ`).
    - Footer pill: `inline-block bg-black/20 backdrop-blur-xs px-2.5 py-1 rounded text-xs font-medium` ("Đã hết hạn: 1 gói").
- **Grid gói dịch vụ đã mua (Bên phải):**
  - Layout: `grid grid-cols-2 gap-3 flex-1`.
  - Từng thẻ gói:
    - Nền trắng `border tds-color-border-secondary rounded-lg p-3 flex flex-col justify-between`.
    - Dòng 1: Logo/Tên brand (`wipix`, `tpos`, `wion`) + Tên gói (`Landing Pro x 1`, `POS Nâng cao x 3`) + Link domain (`WiPix.com`).
    - Dòng 2: Giá trị gói `tds-heading-6 font-bold tds-color-text-primary` (`2.000.000 đ`, `6.000.000 đ`).
    - Dòng 3 (Footer status): Hạn sử dụng (`Hết hạn: 01/10/2026` hoặc `12/10/2027`) kèm Badge trạng thái:
      - Đỏ: `tds-tag` / text đỏ `Đã hết hạn`.
      - Xanh lá: `tds-tag` / text xanh lá `Còn 117 ngày`.

#### Khối 4: Heatmap Ma trận Hoạt động & Timeline (`CustomerActivityHeatmapComponent`)
- **TDS Tabs:** `tds-tabs` với 2 tab:
  - `Lịch sử hoạt động` (Active, gạch chân cam `#F35431`).
  - `Lịch sử chỉnh sửa`.
- **Gợi ý:** Icon thông tin `tdsi-info-circle-line text-sm tds-color-text-info` + "Bấm vào các ô để xem lịch sử".
- **Bảng ma trận Heatmap:**
  - Header tháng: `Tháng 11`, `Tháng 12`, `Tháng 01`, `Tháng 02`, `Tháng 03`, `Tháng 04`, `Tháng 05`, `Tháng 06`.
  - Cột bên trái (4 Kênh liên kết có viền màu nhận diện bên trái):
    - `Facebook` (Viền xanh dương `#1877F2`).
    - `Zalo` (Viền xanh lam `#0068FF`).
    - `Website` (Viền cam `#FF7A00`).
    - `Tổng đài` (Viền xanh lá `#10B981`).
  - Các ô số (Cells):
    - Trống: Ô nền xám nhạt `tds-color-background-neutral-minimalist` bo góc 4px.
    - Có sự kiện: Ô nền xanh nhạt hoặc viền highlight, hiển thị số lượt sự kiện (VD: 12, 2, 1, 4, 6, 7, 10, 5, 9, 3, 11).
    - Trạng thái Active / Hover: Viền xanh đậm `border-2 border-[#0068FF]`, con trỏ bàn tay `cursor-pointer`.
    - Tooltip (TDS Tooltip): Khi hover ô Zalo Tháng 4 -> Hiện popup đen `Zalo • Tháng 4 • 4 sự kiện`.
- **Nhật ký chi tiết bên dưới ô được chọn (`EventLogSubListComponent`):**
  - Khối danh sách các sự kiện tương ứng ô đã chọn (VD: Zalo Tháng 4 có 4 sự kiện):
    - Sự kiện 1: `Zalo 28/04/2026 11:09` — *Nhắn tin qua Zalo OA* (Viền trái xanh lam).
    - Sự kiện 2: `Zalo 24/04/2026 08:30` — *Nhắn tin qua Zalo OA*.
    - Sự kiện 3: `Zalo 12/04/2027 16:00` — *Nhắn tin qua Zalo OA*.
    - Sự kiện 4: `Zalo 01/04/2027 00:09` — *Theo dõi Zalo OA*.

---

### 2.3. Cột 3 — Phải: Lịch Hẹn & Ghi Chú Nội Bộ

#### Khối 5: Lịch hẹn sắp tới (`CustomerUpcomingAppointmentsComponent`)
- **Header:**
  - Icon lịch `tdsi-calendar-line text-base tds-color-text-secondary`.
  - Tiêu đề: `tds-body-1 font-semibold tds-color-text-primary` ("Lịch hẹn sắp tới (4 lịch hẹn)").
  - Nút: `button[tds-button-outline]` `color="primary"` `size="xs"` `tdsPrefixIcon="tdsi-plus-line"` ("Tạo lịch hẹn").
- **Danh sách thẻ lịch hẹn:**
  - Container: `border tds-color-border-secondary rounded-lg p-3.5 mb-3 flex flex-col gap-2 bg-white hover:shadow-xs transition-shadow`.
  - Dòng 1: Tiêu đề cuộc hẹn `tds-body-2 font-bold tds-color-text-primary` (`Demo Tpos Pro`) + Tag `Ưu tiên cao` (màu cam nhạt `bg-[#FFF0EB] text-[#F35431] font-semibold text-xs px-2 py-0.5 rounded`) + Action icons (Sửa `tdsi-edit-line`, Xóa `tdsi-trash-line`).
  - Dòng 2: Phân loại dịch vụ: `Dịch vụ: Tư vấn sản phẩm` (`tds-caption-1 font-medium tds-color-text-secondary`).
  - Dòng 3: Nội dung ghi chú chi tiết (`tds-caption-1 tds-color-text-secondary leading-relaxed bg-[#F8FAFC] p-2 rounded`).
  - Dòng 4 (Footer card): Người phụ trách (Avatar initial `Đ` `Minh Đạt`) + Thời gian hẹn (Icon đồng hồ `tdsi-time-line` `12/03/2027 11:09`).

#### Khối 6: Ghi chú nội bộ (`CustomerNotesFeedComponent`)
- **Header:** Icon ghi chú `tdsi-file-text-line` + `Ghi chú`.
- **Ô nhập nhanh:**
  - `tds-form-field` + `<input tdsInput placeholder="Nhập ghi chú, Enter để thêm">`.
  - Icon phím Enter `tdsi-corner-down-left-line` bên phải input.
- **Dòng thời gian ghi chú (Feed):**
  - Item ghi chú:
    - Avatar nhân viên: Avatar ảnh tròn hoặc Avatar initial (VD: `Hoàng Khôi`, `Trần Minh Đạt`, `Nguyễn Thanh Lam`).
    - Tiêu đề: Tên nhân viên `font-semibold` • Vai trò (`Nhân viên chăm sóc khách hàng`, `Quản lý cửa hàng`).
    - Nội dung ghi chú: `tds-body-2 tds-color-text-primary mt-1` (`Khách hàng bận thứ 2 gọi lại. Tư vấn dịch vụ`, `Gia hạn gói TPOS`).
    - Thời gian: Icon đồng hồ `tdsi-time-line` `12/03/2027 11:09` (`tds-caption-1 tds-color-text-tertiary`).

---

## 3. Data Transfer Objects (DTOs)

```typescript
export interface Customer360DetailDto {
  id: string;
  customerCode: string; // NV0015-21
  fullName: string;
  gender: 'male' | 'female' | 'other';
  avatarUrl?: string;
  isIdentified: boolean;
  status: 'active' | 'inactive' | 'lead';
  statusLabel: string; // Đang tương tác
  assignee: {
    id: string;
    name: string;
    avatarUrl?: string;
  };
  phone: string;
  dateOfBirth?: string;
  email?: string;
  address?: string;
  sourceChannels: string[]; // WiPix, Facebook
  createdAt: string;
  lastActiveAt: string;
  organizations: CustomerOrganizationDto[];
  purchaseSummary: CustomerPurchaseSummaryDto;
  activityHeatmap: CustomerActivityHeatmapDto;
  upcomingAppointments: CustomerAppointmentDto[];
  notes: CustomerNoteDto[];
}

export interface CustomerOrganizationDto {
  id: string;
  name: string;
  roleTitle: string;
  phone: string;
  address: string;
}

export interface CustomerPurchaseSummaryDto {
  totalAmount: number; // 12000000
  currency: string; // đ
  expiredCount: number; // 1
  packages: Array<{
    id: string;
    provider: string; // WiPix, TPOS, WiOn
    packageName: string; // Landing Pro x 1
    domainUrl: string;
    price: number;
    expiredAt: string;
    isExpired: boolean;
    remainingDays?: number;
  }>;
}

export interface CustomerActivityHeatmapDto {
  months: string[]; // ['Tháng 11', 'Tháng 12', ..., 'Tháng 06']
  channels: Array<{
    channelCode: 'facebook' | 'zalo' | 'website' | 'call_center';
    channelName: string;
    colorIndicator: string;
    monthlyCounts: number[]; // Số lượng sự kiện từng tháng
  }>;
  selectedCellEvents?: Array<{
    id: string;
    channelCode: string;
    timestamp: string;
    title: string;
  }>;
}

export interface CustomerAppointmentDto {
  id: string;
  title: string;
  priority: 'high' | 'medium' | 'low';
  serviceType: string;
  note: string;
  assigneeName: string;
  scheduledTime: string;
}

export interface CustomerNoteDto {
  id: string;
  authorName: string;
  authorRole: string;
  authorAvatar?: string;
  content: string;
  createdAt: string;
}
```

---

## 4. Tiêu Chí Chấp Nhận (Acceptance Criteria - AC)

- **AC-1 (Bố cục 3 cột):** Màn hình hiển thị đầy đủ 3 cột theo tỷ lệ chuẩn desktop, cuộn độc lập hoặc cuộn toàn trang mượt mà không vỡ layout ở độ phân giải từ 1280px đến 1920px+.
- **AC-2 (Hồ sơ & Định danh):** Hiển thị đúng Avatar, Huy hiệu "Đã định danh", Badge trạng thái, mã khách hàng `[NV0015-21]`, đầy đủ 8 trường thông tin và danh sách Doanh nghiệp liên kết.
- **AC-3 (Thẻ Hero mua hàng):** Thẻ KPI tổng tiền mua hàng dùng gradient cam thương hiệu `#FF6B4A` -> `#F35431`, định dạng số tiền VND chuẩn `12.000.000 đ`, 4 thẻ gói dịch vụ hiển thị chuẩn badge "Đã hết hạn" hoặc "Còn X ngày".
- **AC-4 (Ma trận Heatmap tương tác):** Hover vào từng ô số hiện Tooltip `[Kênh] • [Tháng] • [X sự kiện]`. Khi click vào ô, danh sách nhật ký bên dưới lập tức lọc và hiển thị danh sách các sự kiện tương ứng của ô đó.
- **AC-5 (Lịch hẹn & Ghi chú nhanh):** Thêm mới ghi chú bằng cách gõ phím Enter trên ô input, ghi chú mới đẩy lên đầu feed. Bấm "Tạo lịch hẹn" mở drawer/modal tạo lịch hẹn chuẩn TDS UI.
- **AC-6 (Chuẩn TDS UI & Design Tokens):** 100% sử dụng token từ `DESIGN.md`, font SF Pro Text / Inter, icon `tdsi-*`, không sử dụng màu tùy tiện ngoài bảng màu Semantic Tokens.
