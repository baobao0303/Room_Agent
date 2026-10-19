# tds-ui Component Index

Quick reference for all tds-ui components. Use this to find the right component for your use case.

## Legend

- **Module**: Import this into your `imports: []`
- **Selector**: Use this in HTML templates
- **Import Path**: Use this in TypeScript `import` statements

## Components

| Component | Module | Selector | Import Path | Description |
|-----------|--------|----------|-------------|-------------|
| Affix | `TDSAffixModule` | `tds-affix` | `tds-ui/affix` | Cố định element khi scroll |
| Alert | `TDSAlertModule` | `tds-alert` | `tds-ui/alert` | Thông báo cảnh báo, thành công, lỗi |
| Anchor | `TDSAnchorModule` | `tds-anchor`, `tds-link` | `tds-ui/anchor` | Navigation anchor link |
| Auto Complete | `TDSAutocompleteModule` | `tds-autocomplete`, `tds-auto-option`, `input[tdsAutocomplete]` | `tds-ui/auto-complete` | Input với gợi ý tự động |
| Avatar | `TDSAvatarModule` | `tds-avatar`, `tds-avatar-group` | `tds-ui/avatar` | Hiển thị ảnh đại diện |
| Back Top | `TDSBackTopModule` | `tds-back-top` | `tds-ui/back-top` | Nút cuộn lên đầu trang |
| Badge | `TDSBadgeModule` | `tds-badge`, `tds-badge-sup`, `tds-ribbon` | `tds-ui/badges` | Hiển thị số thông báo, chấm đỏ |
| Breadcrumb | `TDSBreadCrumbModule` | `tds-breadcrumb`, `tds-breadcrumb-item` | `tds-ui/breadcrumb` | Navigation breadcrumb |
| Button | `TDSButtonModule` | `button[tds-button]`, `a[tds-button]` | `tds-ui/button` | Nút hành động, nhiều type/color |
| Button Menu | `TDSButtonMenuModule` | `tbutton-menu`, `[tdsbuttonMenuTriggerFor]` | `tds-ui/button-menu` | Menu dropdown từ button |
| Button Split | `TDSButtonSpitModule` | `tds-button-split` | `tds-ui/buttton-split` | Button chia tách hành động |
| Calendar | `TDSCalendarModule` | `tds-calendar` | `tds-ui/calendar` | Lịch hiển thị, chọn ngày |
| Card | `TDSCardModule` | `tds-card`, `tds-card-header`, `tds-card-content` | `tds-ui/card` | Container dạng thẻ |
| Card View | `TDSCardViewModule` | `tds-card-view` | `tds-ui/card-view` | Hiển thị dữ liệu dạng card grid |
| Carousel | `TDSCarouselModule` | `tds-carousel`, `[tds-carousel-content]` | `tds-ui/carousel` | Slider nội dung chuyển động |
| Cascader | `TDSCascaderModule` | `tds-cascader` | `tds-ui/cascader` | Dropdown chọn nhiều cấp |
| Checkbox | `TDSCheckBoxModule` | `tds-checkbox` | `tds-ui/tds-checkbox` | Checkbox chọn/bỏ chọn |
| Collapse | `TDSCollapseModule` | `tds-collapse`, `tds-collapse-panel` | `tds-ui/collapse` | Nội dung thu gọn/mở rộng |
| Color Picker | `TDSColorPickerModule` | `tds-color-picker` | `tds-ui/color-picker` | Chọn màu |
| Column Settings | `TDSColumnSettingsModule` | `tds-column-settings` | `tds-ui/column-settings` | Cài đặt cột hiển thị |
| Data List | `TDSDataListPanelModule` | `tds-data-list-panel` | `tds-ui/data-list` | Panel danh sách dữ liệu |
| Data Table | `TDSDataTableModule` | `tds-data-table`, `tds-data-table-column` | `tds-ui/data-table` | Bảng dữ liệu nâng cao |
| Date Picker | `TDSDatePickerModule` | `tds-date-picker`, `tds-range-picker`, `tds-month-picker`, `tds-week-picker`, `tds-year-picker` | `tds-ui/date-picker` | Chọn ngày, khoảng ngày |
| Divider | `TDSDividerModule` | `tds-divider` | `tds-ui/divider` | Đường phân cách nội dung |
| Drawer | `TDSDrawerModule` | `tds-drawer` | `tds-ui/drawer` | Panel trượt từ cạnh màn hình |
| Dropdown | `TDSDropDownModule` | `[tds-dropdown-trigger]`, `tds-dropdown-menu-item` | `tds-ui/dropdown` | Menu dropdown |
| Empty | `TDSEmptyModule` | `tds-empty` | `tds-ui/empty` | Trạng thái rỗng placeholder |
| Filter Result | `TDSFilterResultModule` | `tds-filter-result` | `tds-ui/filter-result` | Hiển thị kết quả lọc |
| Filter Status | `TDSFilterStatusModule` | `tds-filter-status`, `tds-filter-status-item` | `tds-ui/filter-status` | Bộ lọc theo trạng thái |
| Float Button | `TDSFloatButtonModule` | `tds-float-button` | `tds-ui/float-button` | Nút nổi (FAB) |
| Form Field | `TDSFormFieldModule` | `tds-form-field`, `tds-label`, `tds-error`, `tds-help-message` | `tds-ui/form-field` | Wrapper cho form input + label + error |
| Gradient Picker | `TDSGradientPickerModule` | `tds-gradient-color-picker` | `tds-ui/gradient-picker` | Chọn gradient màu |
| Grid View | `TDSGridViewModule` | `tds-grid-view` | `tds-ui/grid-view` | Hiển thị dữ liệu dạng grid |
| Header | `TDSHeaderModule` | `tds-header` | `tds-ui/header` | Header section |
| Illustration | `TDSIllustrationModule` | `tds-illustration` | `tds-ui/illustration` | Hình minh họa |
| Image | `TDSImageModule` | `img[tds-image]`, `tds-image-preview` | `tds-ui/image` | Hiển thị ảnh với preview |
| IMask | `TDSIMaskModule` | `[imask]` | `tds-ui/imask` | Input mask formatting |
| Input (tdsInput) | `TDSInputModule` | `input[tdsInput]`, `textarea[tdsInput]` | `tds-ui/tds-input` | Directive bọc input/textarea cho tds-form-field |
| Input Number | `TDSInputNumberModule` | `tds-input-number` | `tds-ui/input-number` | Nhập số có step up/down |
| Input Password | `TDSInputPasswordModule` | `tds-input-password` | `tds-ui/input-password` | Nhập mật khẩu có show/hide |
| Input Search | `TDSInputSearchModule` | `tds-input-search` | `tds-ui/input-search` | Input tìm kiếm |
| Layout | `TDSLayoutModule` | `tds-layout`, `tds-layout-header`, `tds-layout-content`, `tds-layout-footer`, `tds-layout-sider`, `tds-layout-device`, `[tdsLayoutDevice]`, `[tdsLayoutDeviceContent]` | `tds-ui/layout` | Bố cục trang (header, content, sider, footer, responsive device) |
| List | `TDSListModule` | `tds-list`, `tds-list-item` | `tds-ui/list` | Danh sách dữ liệu |
| Menu | `TDSMenuModule` | `tds-menu`, `tds-menu-item` | `tds-ui/menu` | Menu navigation |
| Message | `TDSMessageModule` | service only | `tds-ui/message` | Thông báo ngắn (toast) — service `TDSMessageService` |
| Modal | `TDSModalModule` | `tds-modal` | `tds-ui/modal` | Hộp thoại modal — service `TDSModalService` |
| Nav Bar | `TDSNavBarModule` | `[tds-navbar]`, `[tds-navbar-item]` | `tds-ui/nav-bar` | Thanh navigation |
| Notification | `TDSNotificationModule` | service only | `tds-ui/notification` | Thông báo góc màn hình |
| OTP Input | `TDSOtpInputModule` | `tds-otp-input` | `tds-ui/otp` | Nhập mã OTP |
| Page Header | `TDSPageHeaderModule` | `tds-page-header` | `tds-ui/page-header` | Tiêu đề trang |
| Pagination | `TDSPaginationModule` | `tds-pagination` | `tds-ui/pagination` | Phân trang |
| Pipes | `TDSPipesModule`, `TDSFilterPipeModule`, `TDSKeysPipeModule`, `TDSMapperPipeModule` | `tdsFilter`, `tdsKeys`, `tdsMapper`, `tdsToCssUnit`, `tdsSafeNull`, `tdsSanitizer`, `tdsTrim`, `tdsBytes`, `tdsAggregate`, `tdsEllipsis`, `tdsTimeRange`, `tdsFormatNumber` | `tds-ui/core/pipes`, `tds-ui/cdk/pipes/*` | Pipes tiện ích |
| Popconfirm | `TDSPopconfirmModule` | `[tds-popconfirm]` | `tds-ui/popconfirm` | Xác nhận bằng popup nhỏ |
| Popover | `TDSPopoverModule` | `[tds-popover]` | `tds-ui/popover` | Popup nội dung hover/click |
| Progress | `TDSProgressModule` | `tds-progress` | `tds-ui/progress` | Thanh tiến trình |
| Progress Spinner | `TDSSpinnerModule` | `tds-spinner` | `tds-ui/progress-spinner` | Loading spinner |
| QR Code | `TDSQRCodeModule` | `tds-qrcode` | `tds-ui/qr-code` | Tạo mã QR |
| Radio | `TDSRadioModule` | `tds-radio-group`, `[tds-radio]`, `[tds-radio-button]` | `tds-ui/radio` | Chọn một trong nhiều |
| Rate | `TDSRateModule` | `tds-rate` | `tds-ui/rate` | Đánh giá sao |
| Resizable | `TDSResizableModule` | `tds-resize` | `tds-ui/resizable` | Thay đổi kích thước element |
| Scroll Into View | `TDSScrollIntoViewModule` | `tds-scroll-into-view` | `tds-ui/scroll-into-view` | Cuộn đến element |
| Segmented | `TDSSegmentedModule` | `tds-segmented` | `tds-ui/segmented` | Chọn phân đoạn |
| Select | `TDSSelectModule` | `tds-select` | `tds-ui/select` | Dropdown chọn giá trị, hỗ trợ search, multiple |
| Skeleton | `TDSSkeletonModule` | `tdskeleton` | `tds-ui/skeleton` | Placeholder loading skeleton |
| Slider | `TDSSliderModule` | `tds-slider` | `tds-ui/slider` | Thanh trượt chọn giá trị |
| Statistic | `TDSStatisticModule` | `tds-statistic`, `tds-countdown` | `tds-ui/statistic` | Hiển thị số liệu thống kê |
| Step | `TDSStepsModule` | `tds-steps`, `tds-step` | `tds-ui/step` | Stepper wizard |
| Switch | `TDSSwitchModule` | `tds-switch` | `tds-ui/switch` | Công tắc bật/tắt |
| Table | `TDSTableModule` | `tds-table` | `tds-ui/table` | Bảng dữ liệu cơ bản |
| Tabs | `TDSTabsModule` | `tds-tabset`, `tds-tab` | `tds-ui/tabs` | Tab navigation |
| Tag | `TDSTagModule` | `tds-tag` | `tds-ui/tag` | Nhãn dán, tag |
| Timeline | `TDSTimelineModule` | `tds-timeline`, `tds-timeline-item` | `tds-ui/timeline` | Dòng thời gian |
| Time Picker | `TDSTimePickerModule` | `tds-time-picker` | `tds-ui/time-picker` | Chọn giờ |
| Tooltip | `TDSToolTipModule` | `tds-tooltip` | `tds-ui/tooltip` | Gợi ý khi hover |
| Tour | `TDSTourModule` | `tds-tour`, `[tds-tour-anchor]` | `tds-ui/tour` | Hướng dẫn sử dụng từng bước |
| Transfer | `TDSTransferModule` | `tds-transfer` | `tds-ui/transfer` | Chuyển đổi giữa 2 danh sách |
| Tree | `TDSTreeModule` | `tds-tree` | `tds-ui/tree` | Cây dữ liệu phân cấp |
| Tree Select | `TDSTreeSelectModule` | `tds-tree-select` | `tds-ui/tree-select` | Dropdown chọn dạng cây |
| Typography | `TDSTypographyModule` | `tds-typography` | `tds-ui/typography` | Văn bản typography |
| Upload | `TDSUploadModule` | `tds-upload` | `tds-ui/upload` | Upload file |
| Zoom Box | `TDSZoomBoxModule` | `tds-zoombox` | `tds-ui/zoom-box` | Phóng to nội dung |

## Notes

- Import **Module** vào `imports: []`, không import component trực tiếp
- Service-only components (Message, Notification): inject service trực tiếp
- Một số import path đặc biệt: `tds-ui/tds-input`, `tds-ui/tds-checkbox`
- Xem chi tiết từng component tại `reference/docs/{component-name}.md`
