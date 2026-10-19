# Collapse

Panel thu gọn/mở rộng (accordion).

**Selector:** `tds-collapse`, `tds-collapse-panel`
**Import:** `import { TDSCollapseModule } from 'tds-ui/collapse';`
**Export as:** `tdsCollapse`, `tdsCollapsePanel`

## tds-collapse Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `accordion` | `boolean` | `false` | Chế độ accordion (chỉ một panel mở) |
| `bordered` | `boolean` | `true` | Hiển thị border |
| `ghost` | `boolean` | `false` | Chế độ ghost (bỏ background) |
| `expandIconPosition` | `'left' \| 'right'` | `'left'` | Vị trí mũi tên expand |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |

## tds-collapse-panel Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `active` | `boolean` | `false` | Mở panel |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `showArrow` | `boolean` | `true` | Hiển thị mũi tên |
| `extra` | `string \| TemplateRef<void>` | — | Nội dung phụ bên phải header |
| `header` | `string \| TemplateRef<void>` | — | Tiêu đề panel |
| `expandedIcon` | `string \| TemplateRef<void>` | `'tdsi-chevron-right-fill'` | Custom expand icon |
| `tdsClass` | `string` | `""` | Custom class cho content |
| `tdsHeaderClass` | `string` | `""` | Custom class cho header |

## tds-collapse-panel Outputs

| Output | Type | Description |
|--------|------|-------------|
| `activeChange` | `EventEmitter<boolean>` | Khi panel mở/đóng |

## Usage

```html
<!-- Basic collapse -->
<tds-collapse>
  <tds-collapse-panel header="Panel 1">
    Nội dung panel 1
  </tds-collapse-panel>
  <tds-collapse-panel header="Panel 2">
    Nội dung panel 2
  </tds-collapse-panel>
</tds-collapse>

<!-- Accordion mode -->
<tds-collapse [accordion]="true">
  <tds-collapse-panel header="Section A" [active]="true">
    Content A
  </tds-collapse-panel>
  <tds-collapse-panel header="Section B">
    Content B
  </tds-collapse-panel>
</tds-collapse>

<!-- Custom header template -->
<tds-collapse>
  <tds-collapse-panel [header]="headerTpl">
    Content here
  </tds-collapse-panel>
</tds-collapse>

<ng-template #headerTpl>
  <span>Custom Header</span>
  <span class="tdsi-info-fill text-primary-500"></span>
</ng-template>

<!-- With extra content -->
<tds-collapse>
  <tds-collapse-panel
    header="Settings"
    [extra]="extraTpl">
    Panel content
  </tds-collapse-panel>
</tds-collapse>

<ng-template #extraTpl>
  <button>Delete</button>
</ng-template>

<!-- Ghost mode -->
<tds-collapse [ghost]="true">
  <tds-collapse-panel header="Panel 1">Content 1</tds-collapse-panel>
</tds-collapse>

<!-- Custom expand icon position -->
<tds-collapse expandIconPosition="right">
  <tds-collapse-panel header="Panel 1">Content 1</tds-collapse-panel>
</tds-collapse>
```

```typescript
import { TDSCollapseModule } from 'tds-ui/collapse';

@Component({
  standalone: true,
  imports: [TDSCollapseModule]
})
export class MyComponent {}
```

## Notes

- `accordion` mode: chỉ một panel có thể mở tại một lúc
- Mũi tên mặc định là `tdsi-chevron-right-fill` (khi closed) và `tdsi-chevron-down-fill` (khi open)
- Khi `expandIconPosition="left"`: icon `tdsi-chevron-right-fill` (closed) -> `tdsi-chevron-down-fill` (open)
- Khi `expandIconPosition="right"`: icon `tdsi-chevron-down-fill` (closed) -> `tdsi-chevron-up-fill` (open)
- `activeChange` event phát ra boolean giá trị của active state
- Header có thể là string hoặc TemplateRef
- `tdsClass` áp dụng class custom cho content box
- `tdsHeaderClass` áp dụng class custom cho header element
- `TDSCollapsePanelModule` không tồn tại — chỉ cần import `TDSCollapseModule`, nó đã export cả `TDSCollapsePanelComponent`
