# Icon

Hệ thống icon dùng CSS class `tdsi-*`. Không cần import — có sẵn qua stylesheet global.

**Import:** Không cần import component — dùng trực tiếp CSS class trong HTML.

## Icon Versions

Hệ thống icon có 3 phiên bản:
- **Version 01**: Icon cũ (đổi tên thành version 03)
- **Version 02**: Icon hiện tại
- **Version 03**: Icon mới với tên đã chuẩn hóa

## Usage

```html
<!-- Filled icon -->
<span class="tdsi-search-fill"></span>

<!-- Outline icon -->
<span class="tdsi-search-line"></span>

<!-- Với kích thước Tailwind -->
<span class="tdsi-bell-fill text-xl"></span>

<!-- Với màu tds-ui (hỗ trợ dark mode) -->
<span class="tdsi-bell-fill text-xl tds-color-icon-primary"></span>

<!-- Dùng trong component -->
<tds-badge [count]="5">
  <span class="tdsi-shopping-bag-fill text-2xl"></span>
</tds-badge>

<!-- Trong breadcrumb -->
<tds-breadcrumb [separator]="'tdsi-chevron-right-fill'">
  <!-- items -->
</tds-breadcrumb>

<!-- Trong button -->
<button tds-button tdsIcon="tdsi-search-fill">Tìm kiếm</button>
```

## Common Icons

### Navigation
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Chevron Down | `tdsi-chevron-down-fill` | — | Mũi tên xuống |
| Chevron Up | `tdsi-chevron-up-fill` | — | Mũi tên lên |
| Chevron Left | `tdsi-chevron-left-fill` | — | Mũi tên trái |
| Chevron Right | `tdsi-chevron-right-fill` | — | Mũi tên phải |
| Arrow Down | `tdsi-arrow-down-fill` | `tdsi-arrow-down-line` | Mũi tên xuống |
| Arrow Up | `tdsi-arrow-up-fill` | `tdsi-arrow-up-line` | Mũi tên lên |
| Arrow Left | `tdsi-arrow-left-fill` | `tdsi-arrow-left-line` | Mũi tên trái |
| Arrow Right | `tdsi-arrow-right-fill` | `tdsi-arrow-right-line` | Mũi tên phải |
| Double Arrow Left | — | `tdsi-double-arrow-left-line` | Mũi tên kép trái |
| Double Arrow Right | — | `tdsi-double-arrow-right-line` | Mũi tên kép phải |

### Actions
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Search | `tdsi-search-fill` | — | Tìm kiếm |
| Close | — | `tdsi-close-line` | Đóng/Hủy |
| Check | `tdsi-check-fill` | `tdsi-tick-fill` | Xác nhận |
| Edit | `tdsi-edit-square-fill` | `tdsi-edit-line` | Chỉnh sửa |
| Delete | — | — | Xóa |
| Add | — | — | Thêm |
| Refresh | `tdsi-refresh-fill` | `tdsi-reload-fill` | Làm mới |
| Sync | `tdsi-sync-fill` | — | Đồng bộ |
| Copy | `tdsi-paste-fill` | `tdsi-paste-line` | Copy |
| Save | — | — | Lưu |
| Clear | — | — | Xóa |

### Media
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Image | — | `tdsi-images-line` | Hình ảnh |
| Video | `tdsi-video-library-fill` | `tdsi-video-camera-line` | Video |
| Volume Up | `tdsi-volume-up-fill` | `tdsi-volume-1-fill` | Tăng âm lượng |
| Volume Down | `tdsi-volume-down-fill` | `tdsi-volume-2-fill` | Giảm âm lượng |

### Communication
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Bell | — | `tdsi-bell-line` | Thông báo |
| Comment | `tdsi-comment-fill` | `tdsi-message-line` | Bình luận |
| Chat | — | `tdsi-chat-line` | Chat |
| Call Incoming | — | `tdsi-call-incoming-line` | Cuộc gọi đến |
| Call Outgoing | — | `tdsi-call-outgoing-line` | Cuộc gọi đi |
| Call Missing | — | `tdsi-call-missing-line` | Cuộc gọi nhỡ |
| Video Call | — | `tdsi-video-call-line` | Video call |

### Status & Feedback
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Info | `tdsi-info-fill` | `tdsi-information-fill` | Thông tin |
| Warning | `tdsi-warning-fill` | `tdsi-warning-1-fill` | Cảnh báo |
| Error | — | — | Lỗi |
| Success | — | — | Thành công |
| Loading | `tdsi-loading-fill` | — | Đang tải |

### User & People
| Name | Fill | Line | Description |
|------|------|------|-------------|
| User | — | — | Người dùng |
| User Add | `tdsi-user-add-fill` | `tdsi-addfriend-fill` | Thêm người dùng |
| User Remove | `tdsi-user-remove-fill` | `tdsi-unfriend-fill` | Xóa người dùng |
| User List | `tdsi-user-list-fill` | `tdsi-friend-fill` | Danh sách người dùng |
| Group | `tdsi-group-fill` | `tdsi-users-fill` | Nhóm |

### Files & Folders
| Name | Fill | Line | Description |
|------|------|------|-------------|
| File | `tdsi-file-fill` | `tdsi-file-line` | File |
| Folder | `tdsi-folder-fill` | — | Th mục |
| Folder Add | `tdsi-folder-add-fill` | — | Thêm thư mục |
| Folders | `tdsi-folders-fill` | — | Nhiều thư mục |

### Settings & Tools
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Settings | `tdsi-gear-fill` | `tdsi-gear-1-fill` | Cài đặt |
| Filter | `tdsi-filter-fill` | `tdsi-filter-1-fill` | Bộ lọc |
| Adjustments | — | `tdsi-ajustment-line` | Điều chỉnh |
| Theme | — | `tdsi-theme-line` | Chủ đề |
| Print | `tdsi-print-setting-fill` | — | In ấn |
| Wrench | `tdsi-wrench-fill` | — | Công cụ |

### E-commerce
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Shopping Bag | `tdsi-shopping-bag-fill` | `tdsi-bag-fill` | Giỏ hàng |
| Cart | `tdsi-cart-fill` | `tdsi-cart-fill-green-fill` | Giỏ hàng |
| ATM Card | `tdsi-atm-card-fill` | `tdsi-card-fill` | Thẻ ATM |
| Cash | `tdsi-cash-fill` | `tdsi-money-fill` | Tiền mặt |
| VND | `tdsi-vnd-fill` | — | Đồng Việt Nam |
| Barcode Scanner | `tdsi-barcode-scanner-fill` | — | Quét mã vạch |
| Truck | — | `tdsi-truck-line` | Vận chuyển |
| COD | — | `tdsi-cod-line` | COD |

### Data & Charts
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Pie Chart | `tdsi-pie-chart-fill` | `tdsi-chart-pie-line` | Biểu đồ tròn |
| Bar Chart | `tdsi-bar-chart-fill` | `tdsi-report-fill` | Biểu đồ cột |
| Trending Up | — | `tdsi-trending-up-line` | Xu hướng tăng |
| Trending Down | — | `tdsi-trending-down-line` | Xu hướng giảm |
| Database | `tdsi-database-fill` | `tdsi-module-fill` | Database |

### Organization
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Company Branch | `tdsi-company-branch-fill` | `tdsi-branch-fill` | Chi nhánh |
| Map | `tdsi-map-fill` | `tdsi-maps-fill` | Bản đồ |
| Storehouse | `tdsi-storehouse-fill` | `tdsi-supplier-fill` | Kho |

### UI Elements
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Menu | `tdsi-menu-fill` | `tdsi-menu-2-fill` | Menu |
| Grid View | `tdsi-grid-view-fill` | — | Chế độ lưới |
| List | — | — | Chế độ danh sách |
| Select All | `tdsi-select-all-fill` | `tdsi-select-all-line` | Chọn tất cả |
| Full Screen | `tdsi-full-screen-fill` | — | Toàn màn hình |
| Bookmark | `tdsi-bookmark-fill` | `tdsi-save-fill` | Bookmark |
| Star | `tdsi-star-fill` | `tdsi-star-1-fill` | Yêu thích |

### Alignment & Spacing
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Align Left | — | `tdsi-align-left-line` | Căn trái |
| Align Center | — | `tdsi-align-mid-line` | Căn giữa |
| Align Right | — | `tdsi-align-right-line` | Căn phải |
| Align Justify | — | `tdsi-two-side-align-line` | Căn đều |
| Vertical Spacing | — | `tdsi-vertical-spacing-line` | Khoảng cách dọc |
| Horizontal Spacing | — | `tdsi-horizontal-spacing-line-1` | Khoảng cách ngang |

### Text Formatting
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Text Align Left | — | `tdsi-text-align-left-line` | Căn trái |
| Text Align Center | — | `tdsi-text-align-center-line` | Căn giữa |
| Text Align Right | — | `tdsi-text-align-right-line` | Căn phải |
| Indent | — | `tdsi-indent-line` | Thụt đầu dòng |

### View & Display
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Eye | `tdsi-eye-fill` | `tdsi-eye-open-fill` | Hiển thị |
| Eye Off | `tdsi-eye-off-fill` | `tdsi-eye-close-fill` | Ẩn |
| Contrast | `tdsi-contrast-fill` | `tdsi-half-fill` | Độ tương phản |
| Blur On | `tdsi-blur-on-fill` | `tdsi-blur-fill` | Làm mờ |
| Zoom In | `tdsi-zoom-in-fill` | `tdsi-zoom-in-line` | Phóng to |
| Zoom Out | `tdsi-zoom-out-fill` | `tdsi-zoom-out-line` | Thu nhỏ |

### Miscellaneous
| Name | Fill | Line | Description |
|------|------|------|-------------|
| Home | — | — | Trang chủ |
| Calendar | — | — | Lịch |
| Clock | — | — | Đồng hồ |
| Link | — | `tdsi-link-line` | Link |
| Embed | — | `tdsi-embed-link-line` | Nhúng |
| Tag | `tdsi-tag-simple-fill` | `tdsi-tag-2-fill` | Thẻ |
| Share | `tdsi-share-forward-fill` | `tdsi-share-fill` | Chia sẻ |
| Attach File | `tdsi-attach-file-fill` | `tdsi-attached-file-fill` | Đính kèm |
| Support | `tdsi-support-fill` | — | Hỗ trợ |
| Send | — | `tdsi-send-line` | Gửi |
| Help | — | `tdsi-live-help-fill` | Trợ giúp |
| Expand | `tdsi-expand-fill` | — | Mở rộng |

## Size Classes (Tailwind)

```html
<span class="tdsi-search-fill text-xs"></span>      <!-- Rất nhỏ -->
<span class="tdsi-search-fill text-sm"></span>      <!-- Nhỏ -->
<span class="tdsi-search-fill text-base"></span>    <!-- Bình thường (mặc định) -->
<span class="tdsi-search-fill text-lg"></span>      <!-- Lớn -->
<span class="tdsi-search-fill text-xl"></span>      <!-- Rất lớn -->
<span class="tdsi-search-fill text-2xl"></span>     <!-- Cực lớn -->
<span class="tdsi-search-fill text-3xl"></span>     <!-- Siêu lớn -->
```

## Color Classes

Ưu tiên dùng `tds-color-icon-*` từ tds-ui (hỗ trợ dark mode tự động):

```html
<span class="tdsi-check-fill tds-color-icon-success"></span>    <!-- Success -->
<span class="tdsi-info-fill tds-color-icon-info"></span>        <!-- Info -->
<span class="tdsi-warning-fill tds-color-icon-warning"></span>  <!-- Warning -->
<span class="tdsi-close-line tds-color-icon-error"></span>      <!-- Error -->
<span class="tdsi-search-fill tds-color-icon-primary"></span>   <!-- Primary -->
<span class="tdsi-search-fill tds-color-icon-secondary"></span> <!-- Secondary -->
<span class="tdsi-search-fill tds-color-icon-disable"></span>   <!-- Disabled -->
<span class="tdsi-search-fill tds-color-icon-white"></span>     <!-- White -->
```

Semantic values: `primary`, `secondary`, `tertiary`, `quaternary`, `inactive`, `success`, `info`, `warning`, `error`, `accent-1`, `disable`, `white`, `interactive`

## Icon Naming Convention

- **Fill icons**: `tdsi-{name}-fill` (icon đặc/nền)
- **Line icons**: `tdsi-{name}-line` (icon viền/outline)
- **Version migration**: Một số icon từ v01 đã được đổi tên trong v03

## Notes

- Pattern: `tdsi-{name}-fill` (filled) hoặc `tdsi-{name}-line` (outline)
- Kích thước dùng Tailwind text classes: `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-3xl`
- Màu dùng `tds-color-icon-*` classes (ưu tiên, hỗ trợ dark mode tự động): `tds-color-icon-success`, `tds-color-icon-error`, `tds-color-icon-warning`, `tds-color-icon-info`, v.v.
- Khi dùng Tailwind text color phải khai báo đủ light + dark: `text-red-500 dark:text-red-400`
- Không dùng `<mat-icon>` hay `<fa-icon>` — chỉ dùng `<span class="tdsi-...">` hoặc `<i class="tdsi-...">`
- Icon classes có sẵn từ stylesheet global, không cần thêm import component
- Có thể dùng trong các component khác thông qua `tdsIcon` input (ví dụ: `tds-button`)
- Hệ thống icon được load từ CSS, không phải từ component Angular
