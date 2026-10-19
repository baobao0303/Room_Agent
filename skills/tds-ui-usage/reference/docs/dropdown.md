# Dropdown

Hiển thị menu khi click hoặc hover vào trigger element.

**Selector:** `[tds-dropdown]` (on trigger element), `tds-dropdown-menu` (menu container)
**Import:** `import { TDSDropDownModule } from 'tds-ui/dropdown';`
**Export as:** `tdsDropdown`, `tdsDropdownMenu`

## Key Inputs (on trigger element `[tds-dropdown]`)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDropdownMenu` | `TDSDropdownMenuComponent \| null` | — | Ref đến `<tds-dropdown-menu>` dropdown |
| `trigger` | `'click' \| 'hover'` | `'hover'` | Cách mở dropdown |
| `placement` | `'bottomLeft' \| 'bottomCenter' \| 'bottomRight' \| 'topLeft' \| 'topCenter' \| 'topRight'` | `'bottomLeft'` | Vị trí dropdown |
| `disabled` | `boolean` | `false` | Vô hiệu hóa dropdown |
| `visible` | `boolean` | `false` | Controlled visibility |
| `matchWidthElement` | `ElementRef \| null` | `null` | Element để match width |
| `backdrop` | `boolean` | `false` | ⚠️ Deprecated — Hiển thị backdrop |
| `clickHide` | `boolean` | `true` | Tự đóng khi click menu item |
| `autoClose` | `boolean` | `true` | Tự đóng khi click outside |
| `overlayClassName` | `string` | `''` | CSS class cho overlay |
| `overlayStyle` | `IndexableObject` | `{}` | CSS style cho overlay |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `visibleChange` | `EventEmitter<boolean>` | Khi dropdown mở/đóng |
| `tdsDropdownOutsideClick` | `EventEmitter<MouseEvent>` | Khi click outside |

## TDSDropdownMenuItem Directive

Individual menu item directive.

**Selector:** `[tds-dropdown-item]`
**Export as:** `tdsDropdownItem`

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `disabled` | `boolean` | `false` | Vô hiệu hóa item |
| `selected` | `boolean` | `false` | Item được chọn |
| `tdsSize` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước item |

## Usage

```html
<button
  tds-button
  color="secondary"
  tds-dropdown
  trigger="click"
  tdsSuffixIcon="tdsi-arrow-down-fill"
  [tdsDropdownMenu]="menu">
  Tùy chọn
</button>

<tds-dropdown-menu #menu="tdsDropdownMenu">
  <div class="w-full">
    <div tds-dropdown-item (click)="onEdit()">Chỉnh sửa</div>
    <div tds-dropdown-item (click)="onDelete()">Xóa</div>
  </div>
</tds-dropdown-menu>
```

```typescript
import { TDSDropDownModule } from 'tds-ui/dropdown';

@Component({
  standalone: true,
  imports: [TDSDropDownModule]
})
export class MyComponent {
  onEdit() { console.log('Edit clicked'); }
  onDelete() { console.log('Delete clicked'); }
}
```

Programmatic control:
```html
<button tds-button tds-dropdown [(visible)]="isDropdownOpen" [tdsDropdownMenu]="menu">
  Dropdown
</button>

<tds-dropdown-menu #menu="tdsDropdownMenu">
  <!-- menu content -->
</tds-dropdown-menu>
```

## Notes

- `tds-dropdown` is a STATIC attribute (directive selector) — do NOT bind it with `[tds-dropdown]`
- `[tdsDropdownMenu]="ref"` is the INPUT that connects trigger to the dropdown menu
- `#ref="tdsDropdownMenu"` is the exportAs on `<tds-dropdown-menu>`
- Import `TDSMenuModule` from `tds-ui/menu` only when using `<ul tds-menu>/<li tds-menu-item>` syntax
- `tds-dropdown-item` directive works without TDSMenuModule
- `clickHide: true` sẽ tự động đóng dropdown khi click trên menu item
- `trigger: 'click'` phù hợp cho action buttons, `trigger: 'hover'` phù hợp cho desktop menus
- `placement` supports: bottomLeft, bottomCenter, bottomRight, topLeft, topCenter, topRight
- Không dùng native `<select>` cho dropdown chứa actions — dùng `tds-select` cho select data
