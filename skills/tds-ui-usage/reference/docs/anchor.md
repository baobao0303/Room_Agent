# Anchor

Hiển thị danh sách neo trang để điều hướng nhanh đến các phần nội dung.

**Selector:** `tds-anchor`, `tds-link`
**Export as:** `tdsAnchor`, `tdsLink`
**Import:** `import { TDSAnchorModule } from 'tds-ui/anchor';`

## Key Inputs

### TDSAnchorModule

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsAffix` | `boolean` | `true` | Sử dụng affix cho anchor |
| `tdsShowInkInFixed` | `boolean` | `false` | Hiển thị ink ball khi fixed |
| `tdsBounds` | `number` | `5` | Khoảng cách bounds để kích hoạt active |
| `tdsOffsetTop` | `number` | `undefined` | Offset từ trên cùng |
| `tdsTargetOffset` | `number` | `undefined` | Offset cho target scroll |
| `tdsContainer` | `string \| HTMLElement` | `undefined` | Container để scroll |
| `tdsCurrentAnchor` | `string` | `undefined` | Anchor hiện tại (được control) |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Chủ đề màu |

### TDSAnchorLinkComponent

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsHref` | `string` | `'#'` | Href của link (đến target section) |
| `tdsTarget` | `string` | `undefined` | Target attribute của link |
| `tdsTitle` | `string \| TemplateRef<void>` | `null` | Tiêu đề của link |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Chủ đề màu |
| `isGroup` | `boolean` | `false` | Đánh dấu là group title |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsClick` | `EventEmitter<string>` | Khi click vào link |
| `tdsChange` | `EventEmitter<string>` | Khi anchor active thay đổi |
| `tdsScroll` | `EventEmitter<TDSAnchorLinkComponent>` | Khi scroll event xảy ra |

## Usage

```html
<!-- Basic anchor -->
<tds-anchor [tdsOffsetTop]="120">
  <tds-link tdsHref="#section1" tdsTitle="Section 1"></tds-link>
  <tds-link tdsHref="#section2" tdsTitle="Section 2"></tds-link>
  <tds-link tdsHref="#section3" tdsTitle="Section 3"></tds-link>
</tds-anchor>

<!-- Anchor with nested links -->
<tds-anchor [tdsOffsetTop]="120">
  <tds-link tdsHref="#overview" tdsTitle="Overview"></tds-link>
  
  <tds-link tdsHref="#features" tdsTitle="Features" [isGroup]="true">
    <tds-link tdsHref="#feature1" tdsTitle="Feature 1"></tds-link>
    <tds-link tdsHref="#feature2" tdsTitle="Feature 2"></tds-link>
  </tds-link>
  
  <tds-link tdsHref="#pricing" tdsTitle="Pricing"></tds-link>
</tds-anchor>

<!-- Anchor without affix -->
<tds-anchor [tdsAffix]="false">
  <tds-link tdsHref="#start" tdsTitle="Start"></tds-link>
  <tds-link tdsHref="#end" tdsTitle="End"></tds-link>
</tds-anchor>

<!-- Anchor with events -->
<tds-anchor
  [tdsOffsetTop]="120"
  (tdsClick)="onAnchorClick($event)"
  (tdsChange)="onAnchorChange($event)">
  <tds-link tdsHref="#section1" tdsTitle="Section 1"></tds-link>
  <tds-link tdsHref="#section2" tdsTitle="Section 2"></tds-link>
</tds-anchor>
```

```typescript
import { TDSAnchorModule } from 'tds-ui/anchor';
import { Component } from '@angular/core';

@Component({
  selector: 'app-anchor-demo',
  standalone: true,
  imports: [TDSAnchorModule],
  template: `
    <div class="container">
      <tds-anchor [tdsOffsetTop]="120" (tdsChange)="currentSection = $event">
        <tds-link tdsHref="#introduction" tdsTitle="Introduction"></tds-link>
        <tds-link tdsHref="#getting-started" tdsTitle="Getting Started"></tds-link>
        
        <tds-link tdsHref="#components" tdsTitle="Components" [isGroup]="true">
          <tds-link tdsHref="#buttons" tdsTitle="Buttons"></tds-link>
          <tds-link tdsHref="#inputs" tdsTitle="Inputs"></tds-link>
          <tds-link tdsHref="#forms" tdsTitle="Forms"></tds-link>
        </tds-link>
        
        <tds-link tdsHref="#api" tdsTitle="API Reference"></tds-link>
      </tds-anchor>
      
      <div class="content">
        <section id="introduction">...</section>
        <section id="getting-started">...</section>
        <section id="components">...</section>
        <section id="api">...</section>
      </div>
    </div>
  `
})
export class AnchorDemoComponent {
  currentSection = '';

  onAnchorClick(href: string) {
    console.log('Clicked anchor:', href);
  }

  onAnchorChange(href: string) {
    console.log('Active anchor changed:', href);
  }
}
```

## Notes

- `tdsHref` phải khớp với `id` của section muốn điều hướng đến (có bao gồm `#`)
- Hỗ trợ nested links với `isGroup="true"` để tạo hierarchical navigation
- Ink ball tự động di chuyển đến link đang active
- Mặc định sử dụng affix để giữ anchor cố định khi scroll
- `tdsOffsetTop` dùng để set vị trí top của anchor khi scroll
- `tdsBounds` dùng để điều khiển độ nhạy khi kích hoạt active state
- Hỗ trợ 3 theme: default, light, dark
- Scroll animation mượt mà khi click vào link
