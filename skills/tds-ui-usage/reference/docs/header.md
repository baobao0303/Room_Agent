# Header

Component header với logo, avatar, search, và các toolbar sections. Hỗ trợ các theme khác nhau và có thể customize.

**Selector:** `tds-header`
**Import:** `import { TDSHeaderModule } from 'tds-ui/header';`
**Export as:** `tdsHeader`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTheme` | `TDSTheme` | `'default'` | Theme của header: 'default', 'dark', hoặc 'light' |
| `urlAvatar` | `string \| null` | `null` | URL hình ảnh avatar |
| `urlLogo` | `string \| null` | `null` | URL hình ảnh logo chính |
| `urlLogoText` | `string \| null` | `null` | URL hình ảnh logo text |
| `tdsLogoTemplate` | `TemplateRef<any> \| null` | `null` | Custom template cho logo |
| `tdsLogoTextTemplate` | `TemplateRef<any> \| null` | `null` | Custom template cho logo text |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `onToggle` | `EventEmitter<boolean>` | Phát sinh khi toggle button được click. **Note:** emits without argument (`this.onToggle.emit()`) despite the `boolean` type signature |
| `clickLogo` | `EventEmitter<MouseEvent>` | Phát sinh khi logo được click |
| `tdsClkBtnSearch` | `EventEmitter<MouseEvent>` | Phát sinh khi search button được click |

## Content Sections

Header component hỗ trợ 3 content sections sử dụng CSS classes:

- **Left toolbar**: `.tds-header-toolbar-left`
- **Center toolbar**: `.tds-header-toolbar-center`
- **Right toolbar**: `.tds-header-toolbar-right`

## Supported Child Components

- `<tds-select>` - Select component ở right section
- `<tds-form-field>` - Form field với search input ở left section

## Custom Template

Sử dụng directive `[tds-header-tmp]` để cung cấp custom template:

```html
<ng-template #customHeader let-onToggle="onToggle">
  <!-- Custom header content -->
</ng-template>
```

## Usage

```html
<!-- Basic header with logo and avatar -->
<tds-header
  [urlLogo]="'https://example.com/logo.png'"
  [urlAvatar]="'https://example.com/avatar.jpg'"
  (clickLogo)="onLogoClick($event)">
</tds-header>

<!-- Header with dark theme -->
<tds-header
  tdsTheme="dark"
  [urlLogoText]="'https://example.com/logo-text.png'"
  [urlAvatar]="'https://example.com/avatar.jpg'">
</tds-header>

<!-- Header with search functionality -->
<tds-header
  [urlLogo]="'https://example.com/logo.png'"
  (tdsClkBtnSearch)="onSearch($event)">
  <tds-form-field class="tds-header-toolbar-left">
    <input tdsInput placeholder="Search..." />
  </tds-form-field>
</tds-header>

<!-- Header with toggle button (mobile menu) -->
<tds-header
  [urlLogo]="'https://example.com/logo.png'"
  (onToggle)="toggleSidebar()">
</tds-header>

<!-- Header with custom toolbar sections -->
<tds-header [urlLogo]="'https://example.com/logo.png'">
  <!-- Left toolbar -->
  <div class="tds-header-toolbar-left">
    <button tds-button color="primary">Left Action</button>
  </div>

  <!-- Center toolbar -->
  <div class="tds-header-toolbar-center">
    <span>Center Content</span>
  </div>

  <!-- Right toolbar -->
  <div class="tds-header-toolbar-right">
    <button tds-button color="secondary">Right Action</button>
  </div>
</tds-header>

<!-- Header with select dropdown -->
<tds-header [urlLogo]="'https://example.com/logo.png'">
  <tds-select [(ngModel)]="selectedOption" placeholder="Select option">
    @for (option of options; track option.value) {
      <tds-option [tdsValue]="option.value">{{ option.label }}</tds-option>
    }
  </tds-select>
</tds-header>

<!-- Header with custom logo templates -->
<tds-header>
  <ng-template #logoTemplate>
    <div class="custom-logo">
      <i class="tdsi-logo"></i>
      <span>My Brand</span>
    </div>
  </ng-template>
  <ng-template [tdsLogoTemplate]="logoTemplate"></ng-template>
</tds-header>

<!-- Header with completely custom template -->
<tds-header>
  <ng-template #customHeader>
    <div class="custom-header">
      <h1>Custom Header</h1>
      <nav>
        <a href="#">Home</a>
        <a href="#">About</a>
      </nav>
    </div>
  </ng-template>
  <ng-template [tds-header-tmp]="customHeader"></ng-template>
</tds-header>
```

```typescript
import { TDSHeaderModule } from 'tds-ui/header';

@Component({
  standalone: true,
  imports: [TDSHeaderModule, TDSInputModule, TDSSelectModule, TDSFormFieldModule],
})
export class MyComponent {
  selectedOption: string | null = null;
  options = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ];

  onLogoClick(event: MouseEvent) {
    console.log('Logo clicked', event);
    // Navigate to home page
  }

  onSearch(event: MouseEvent) {
    console.log('Search clicked', event);
    // Open search dialog or focus search input
  }

  toggleSidebar() {
    console.log('Toggle sidebar');
    // Toggle mobile sidebar/menu
  }
}
```

## Responsive Layout Example

```html
<tds-header
  [urlLogo]="'https://example.com/logo.png'"
  [urlAvatar]="'https://example.com/avatar.jpg'"
  [urlLogoText]="'https://example.com/logo-text.png'"
  (onToggle)="toggleMobileMenu()">
</tds-header>
```

## Header with Multiple Features

```html
<tds-header
  tdsTheme="dark"
  [urlLogo]="'https://example.com/logo.png'"
  [urlAvatar]="'https://example.com/avatar.jpg'"
  (clickLogo)="goHome()"
  (onToggle)="toggleSidebar()"
  (tdsClkBtnSearch)="openSearchModal()">
  
  <!-- Search form field -->
  <tds-form-field class="tds-header-toolbar-left">
    <input tdsInput [formControl]="searchControl" placeholder="Search..." />
  </tds-form-field>

  <!-- Center content -->
  <div class="tds-header-toolbar-center">
    <span class="text-white">{{ pageTitle }}</span>
  </div>

  <!-- Right toolbar -->
  <div class="tds-header-toolbar-right">
    <button tds-button tdsSize="sm" color="secondary">Notifications</button>
  </div>

  <!-- Language selector -->
  <tds-select [(ngModel)]="currentLanguage">
    @for (lang of languages; track lang.code) {
      <tds-option [tdsValue]="lang.code">{{ lang.name }}</tds-option>
    }
  </tds-select>
</tds-header>
```

## Notes

- Header tự động chia layout thành 3 phần: left, center, right
- Toggle button chỉ hiển thị khi cần (thường cho mobile menu)
- Avatar hiển thị ở bên phải của header
- Search button hiển thị khi có `<tds-form-field>` child component
- Select component tự động được đặt ở bên phải với width cố định
- Theme classes: `tds-header-default`, `tds-header-dark`, `tds-header-light`
- Custom template hoàn toàn có thể thay thế default header template
- Responsive: Left section thường chứa toggle button (mobile), logo, và search
- Content sections sử dụng CSS classes để định vị: `tds-header-toolbar-left`, `tds-header-toolbar-center`, `tds-header-toolbar-right`
- Logo và logo text có thể sử dụng URL hoặc custom template
- Avatar component tự động áp dụng theme từ header
