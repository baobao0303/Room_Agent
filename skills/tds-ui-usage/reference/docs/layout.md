# Layout

Hệ thống layout container hỗ trợ responsive design với các thành phần header, sider, content, footer. Tương tự Ant Design Layout.

**Selector:** `tds-layout`
**Import:** `import { TDSLayoutModule } from 'tds-ui/layout';`
**Export as:** `tdsLayout`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTheme` | `TDSTheme` | `'default'` | Theme của layout: `default`, `light`, `dark` |

## Layout Components

| Component | Selector | Export As | Description |
|-----------|----------|-----------|-------------|
| `TDSLayoutComponent` | `tds-layout` | `tdsLayout` | Container chính |
| `TDSLayoutHeaderComponent` | `tds-layout-header` | `tdsLayoutHeader` | Phần header. Tự thêm class `tds-layout-has-header` khi content-child là `TDSHeaderComponent` |
| `TDSLayoutContentComponent` | `tds-layout-content` | `tdsLayoutContent` | Vùng nội dung chính, host class `tds-custom-scroll` |
| `TDSLayoutFooterComponent` | `tds-layout-footer` | `tdsLayoutFooter` | Phần footer |
| `TDSLayoutSiderComponent` | `tds-layout-sider` | `tdsLayoutSider` | Sidebar collapse/expand được |
| `TDSLayoutDeviceComponent` | `tds-layout-device` | — | Render content theo device type |
| `TDSLayoutDeviceDirective` | `[tdsLayoutDevice]` | — | Structural directive `*tdsLayoutDevice` |
| `TDSLayoutDeviceContentDirective` | `[tdsLayoutDeviceContent]` | — | Template directive dùng bên trong `tds-layout-device` |

> `TDSLayoutSiderTriggerComponent` export với alias `ɵ...` (private). Không import trực tiếp.

## Sider Component Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsWidth` | `string \| number` | `256` | Chiều rộng sider khi mở rộng |
| `tdsCollapsedWidth` | `number` | `52` | Chiều rộng sider khi collapsed. `0` → zero-width trigger |
| `tdsCollapsed` | `boolean` | `false` | Trạng thái collapse (hỗ trợ two-way `[(tdsCollapsed)]`) |
| `tdsCollapsible` | `boolean` | `false` | Có hiển thị trigger collapse hay không |
| `tdsTheme` | `TDSTheme` | `'dark'` | Theme của sider |
| `tdsBreakpoint` | `TDSBreakpointKey \| null` | `null` | Breakpoint auto-collapse: `xs`, `sm`, `md`, `lg`, `xl`, `xxl`. Dùng `siderResponsiveMap` |
| `tdsReverseArrow` | `boolean` | `false` | Đảo hướng trigger |
| `tdsTrigger` | `TemplateRef<void> \| undefined \| null` | `undefined` | Custom trigger. `null` ẩn trigger |
| `tdsZeroTrigger` | `TemplateRef<void> \| null` | `null` | Custom trigger khi `tdsCollapsedWidth === 0` |

## Sider Component Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsCollapsedChange` | `EventEmitter<boolean>` | Emit khi `tdsCollapsed` thay đổi |

## Sider + Menu Integration

`TDSLayoutSiderComponent` query `ContentChild(TDSMenuComponent)`:

- Khi `tdsMenuDirective` tồn tại, `tdsMenuDirective.inlineCollapsed === false`, và `tdsCollapsedWidth !== 0` → sider tự gọi `menu.setInlineCollapsed(tdsCollapsed)`.
- Ngược lại (`tdsCollapsible && tdsTrigger != null`): sider ẩn footer menu (`menu.showFooter = false`).
- Ngược lại còn lại: menu drive collapse qua `onOpenChange`, emit `tdsCollapsedChange`.

## Device Component Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDevice` | `'mobile' \| 'tablet' \| 'desktop'` | `'desktop'` | Loại device. Dùng `tdsLayoutResponsiveMap` |

## Device Directive Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsLayoutDevice` | `'mobile' \| 'tablet' \| 'desktop'` | `'desktop'` | Structural directive, dùng `tdsLayoutResponsiveMap` |

## Responsive Breakpoints

Ba map khác nhau. Dùng đúng map cho API:

| API | Map |
|-----|-----|
| `tds-layout-sider[tdsBreakpoint]` | `siderResponsiveMap` |
| `tds-layout-device[tdsDevice]`, `*tdsLayoutDevice` | `tdsLayoutResponsiveMap` |
| (tham khảo) grid | `gridResponsiveMap` — không dùng cho layout |

### `siderResponsiveMap` (tdsBreakpoint)

| Key | Media query |
|-----|-------------|
| `xs` | `(max-width: 479.98px)` |
| `sm` | `(max-width: 575.98px)` |
| `md` | `(max-width: 767.98px)` |
| `lg` | `(max-width: 991.98px)` |
| `xl` | `(max-width: 1199.98px)` |
| `xxl` | `(max-width: 1599.98px)` |

### `tdsLayoutResponsiveMap` (tdsDevice / tdsLayoutDevice)

| Key | Media query |
|-----|-------------|
| `xs` | `(max-width: 375.98px)` |
| `sm` | `(min-width: 640px)` |
| `md` | `(min-width: 768px)` |
| `lg` | `(min-width: 1024px)` |
| `xl` | `(min-width: 1280px)` |
| `xxl` | `(min-width: 1536px)` |

### Device-type mapping

| `tdsDevice` / `tdsLayoutDevice` | Breakpoint keys |
|----------------------------------|-----------------|
| `mobile` | `xs`, `sm` |
| `tablet` | `md`, `lg` |
| `desktop` | `xl`, `xxl` (default) |

## Nesting Rule

> **`tds-layout` không lồng `tds-layout`.** Dùng `tds-layout-content` cho vùng nội dung.

Lý do (CSS, `projects/tds-ui/assets/v2/scss/components/layout.component.scss`):

```scss
.tds-layout {
  @apply flex flex-auto flex-col min-h-0;
  &.tds-layout-has-sider {
    @apply flex-row;
    > .tds-layout,
    > .tds-layout-content {
      @apply w-0;  // width: 0px
    }
  }
}
```

Khi parent có sider, direct child `.tds-layout` bị `width: 0`. Mix sai flex context → collapse width/height → không render. Xem `troubleshooting.md`.

## Usage

```html
<!-- Basic: header + content + footer -->
<tds-layout>
  <tds-layout-header>
    <div class="logo">My App</div>
  </tds-layout-header>
  <tds-layout-content>
    <p>Main content goes here...</p>
  </tds-layout-content>
  <tds-layout-footer>
    <p>© 2024 My Company</p>
  </tds-layout-footer>
</tds-layout>
```

```html
<!-- Layout with sidebar (FLAT — không nest tds-layout) -->
<tds-layout>
  <tds-layout-sider
    [tdsCollapsed]="isCollapsed"
    [tdsWidth]="200"
    [tdsCollapsedWidth]="80"
    [tdsCollapsible]="true"
    (tdsCollapsedChange)="onCollapsedChange($event)">
    <tds-menu>
      <tds-menu-item>Item 1</tds-menu-item>
      <tds-menu-item>Item 2</tds-menu-item>
    </tds-menu>
  </tds-layout-sider>
  <tds-layout-header>Header</tds-layout-header>
  <tds-layout-content>Content</tds-layout-content>
</tds-layout>
```

```html
<!-- Sider with breakpoint auto-collapse -->
<tds-layout>
  <tds-layout-sider
    [tdsBreakpoint]="'lg'"
    [tdsCollapsible]="true"
    (tdsCollapsedChange)="isCollapsed = $event">
    <tds-menu>
      <tds-menu-item>Menu 1</tds-menu-item>
    </tds-menu>
  </tds-layout-sider>
  <tds-layout-content>Content</tds-layout-content>
</tds-layout>
```

```html
<!-- Responsive content theo device -->
<tds-layout>
  <tds-layout-device tdsDevice="mobile">
    <p>Mobile content</p>
  </tds-layout-device>
  <tds-layout-device tdsDevice="tablet">
    <p>Tablet content</p>
  </tds-layout-device>
  <tds-layout-device tdsDevice="desktop">
    <p>Desktop content</p>
  </tds-layout-device>
</tds-layout>

<!-- Hoặc structural directive -->
<div *tdsLayoutDevice="'mobile'">Mobile only</div>
<div *tdsLayoutDevice="'tablet'">Tablet only</div>
<div *tdsLayoutDevice="'desktop'">Desktop only</div>
```

```html
<!-- Theme -->
<tds-layout tdsTheme="dark">
  <tds-layout-sider tdsTheme="dark">
    <tds-menu>
      <tds-menu-item>Menu 1</tds-menu-item>
    </tds-menu>
  </tds-layout-sider>
  <tds-layout-content>Content</tds-layout-content>
</tds-layout>
```

```typescript
// Option 1: Import all via module
import { TDSLayoutModule } from 'tds-ui/layout';

// Option 2: Import standalone symbols riêng lẻ
import {
  TDSLayoutComponent,
  TDSLayoutHeaderComponent,
  TDSLayoutContentComponent,
  TDSLayoutFooterComponent,
  TDSLayoutSiderComponent,
  TDSLayoutDeviceComponent,
  TDSLayoutDeviceDirective,
  TDSLayoutDeviceContentDirective,
} from 'tds-ui/layout';

@Component({
  standalone: true,
  imports: [
    // Option 1
    TDSLayoutModule,
    // Option 2 — uncomment khi cần
    // TDSLayoutHeaderComponent,
    // TDSLayoutContentComponent,
    // TDSLayoutFooterComponent,
    // TDSLayoutSiderComponent,
    // TDSLayoutDeviceComponent,
    // TDSLayoutDeviceDirective,
    // TDSLayoutDeviceContentDirective,
  ],
})
export class MyComponent {
  isCollapsed = false;
  onCollapsedChange(collapsed: boolean) {
    this.isCollapsed = collapsed;
  }
}
```

## Notes

- `tds-layout-sider` auto-collapse theo `siderResponsiveMap` khi `tdsBreakpoint` được set.
- Khi có sider trong layout, layout thêm class `tds-layout-has-sider`.
- `tds-layout-content` có `tds-custom-scroll`. Scroll cần height chain từ root (`html`, `body`, `tds-layout`).
- `tds-layout-device` chỉ render content khi breakpoint khớp device type.
- Sider two-way binding: `[(tdsCollapsed)]`.
- Layout hỗ trợ RTL qua `Directionality` từ `@angular/cdk/bidi`.
- Default sider trigger template bị comment trong source (`sider-trigger.component.ts` lines 30–35). Muốn icon trigger → cung cấp `tdsTrigger` custom.

## See Also

- Recipe: `recipes/app-shell-layout.md`
- Troubleshooting: `../troubleshooting.md`
- Sider source: `projects/tds-ui/layout/sider.component.ts`
- Breakpoint source: `projects/tds-ui/core/services/breakpoint.ts`
