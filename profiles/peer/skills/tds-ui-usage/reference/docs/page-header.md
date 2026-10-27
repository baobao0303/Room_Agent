# Page Header

Header cho trang với title, subtitle, breadcrumb, back button, và các slot content tùy chỉnh. Tự động chuyển sang chế độ compact khi width < 768px.

**Selector:** `tds-page-header`
**Import:** `import { TDSPageHeaderModule } from 'tds-ui/page-header';`
**Export as:** `tdsPageHeader`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTitle` | `string \| TemplateRef<void>` | — | Tiêu đề chính |
| `tdsSubtitle` | `string \| TemplateRef<void>` | — | Phụ đề |
| `tdsBackIcon` | `string \| TemplateRef<void> \| null` | `null` | Icon nút back (null = không hiển thị) |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |
| `title` | `string \| TemplateRef<void>` | — | **DEPRECATED** — dùng `tdsTitle` thay thế |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsBack` | `EventEmitter<void>` | Emit khi click nút back |

## Content Directives

| Directive | Selector | Description |
|-----------|----------|-------------|
| `TDSPageHeaderTitleDirective` | `tds-page-header-title, [tds-page-header-title]` | Slot cho title tùy chỉnh |
| `TDSPageHeaderSubtitleDirective` | `tds-page-header-subtitle, [tds-page-header-subtitle]` | Slot cho subtitle tùy chỉnh |
| `TDSPageHeaderContentDirective` | `tds-page-header-content, [tds-page-header-content]` | Slot cho nội dung chính |
| `TDSPageHeaderTagsDirective` | `tds-page-header-tags, [tds-page-header-tags]` | Slot cho tags |
| `TDSPageHeaderExtraDirective` | `tds-page-header-extra, [tds-page-header-extra]` | Slot cho nội dung phụ (bên phải) |
| `TDSPageHeaderFooterDirective` | `tds-page-header-footer, [tds-page-header-footer]` | Slot cho footer |
| `TDSPageHeaderBreadcrumbDirective` | `tds-breadcrumb[tds-page-header-breadcrumb]` | Slot cho breadcrumb |
| `TDSPageHeaderAvatarDirective` | `tds-avatar[tds-page-header-avatar]` | Slot cho avatar |

## Usage

```html
<!-- Basic usage -->
<tds-page-header
  tdsTitle="User Profile"
  tdsSubtitle="Manage your account settings"
  [tdsBackIcon]="'tdsi-back-fill'"
  (tdsBack)="goBack()">
</tds-page-header>

<!-- With breadcrumb and extra -->
<tds-page-header tdsTitle="Products">
  <tds-breadcrumb tds-page-header-breadcrumb>
    <tds-breadcrumb-item>Home</tds-breadcrumb-item>
    <tds-breadcrumb-item>Catalog</tds-breadcrumb-item>
    <tds-breadcrumb-item>Products</tds-breadcrumb-item>
  </tds-breadcrumb>

  <div tds-page-header-extra>
    <button tds-button tdsType="outline">Filter</button>
    <button tds-button color="primary">Add New</button>
  </div>
</tds-page-header>

<!-- With avatar and custom title/subtitle -->
<tds-page-header [tdsBackIcon]="'tdsi-back-fill'">
  <tds-avatar tds-page-header-avatar
    tdsText="John Doe"
    color="primary">
  </tds-avatar>

  <div tds-page-header-title>John Doe</div>
  <div tds-page-header-subtitle>Administrator</div>

  <div tds-page-header-tags>
    <tds-tag color="success">Active</tds-tag>
    <tds-tag color="primary">Admin</tds-tag>
  </div>
</tds-page-header>

<!-- With content and footer -->
<tds-page-header tdsTitle="Dashboard">
  <div tds-page-header-content>
    <p>Welcome to your dashboard. Here you can view statistics and manage your account.</p>
  </div>

  <div tds-page-header-footer>
    <tds-statistic
      tdsTitle="Total Users"
      [tdsValue]="1234">
    </tds-statistic>
    <tds-statistic
      tdsTitle="Active Sessions"
      [tdsValue]="56">
    </tds-statistic>
  </div>
</tds-page-header>

<!-- Light theme -->
<tds-page-header
  tdsTitle="Settings"
  tdsTheme="light">
</tds-page-header>

<!-- Dark theme -->
<tds-page-header
  tdsTitle="Admin Panel"
  tdsTheme="dark">
</tds-page-header>
```

```typescript
import { TDSPageHeaderModule } from 'tds-ui/page-header';

@Component({
  standalone: true,
  imports: [TDSPageHeaderModule, TDSButtonModule, TDSBreadcrumbModule, ...],
})
export class MyComponent {
  goBack() {
    // Custom back logic
    console.log('Back clicked');
  }

  // Nếu không có (tdsBack) handler, sẽ tự động gọi location.back()
  // Cần import RouterModule hoặc đăng ký Location service
}
```

## Notes

- Input `title` đã bị deprecated từ v2.12.0 — hãy dùng `tdsTitle` thay thế
- Khi width < 768px, component tự động chuyển sang chế độ compact
- Nếu không cung cấp handler cho `(tdsBack)`, component sẽ tự động gọi `location.back()` (cần RouterModule hoặc Location)
- Icon back tự động đổi hướng theo RTL layout (`tdsi-back-fill` hoặc `tdsi-toward-fill`)
- Sử dụng `tdsBackIcon = null` để ẩn nút back
- Theme support: `default`, `light`, `dark`
- Tất cả content directives đều optional — dùng theo nhu cầu
- Component tự động quan sát resize để toggle compact mode
