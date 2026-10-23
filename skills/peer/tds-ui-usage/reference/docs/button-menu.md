# Button Menu

Menu dropdown được trigger bởi button, với hỗ trợ positioning và nested menu.

**Selector:** `tbutton-menu`, `[tdsbutton-menu-trigger-for]`, `[tdsbuttonMenuTriggerFor]`
**Import:** `import { TDSButtonMenuModule } from 'tds-ui/button-menu';`
**Export as:** `TDSButtonMenu`, `TDSButtonMenuTrigger`, `TDSButtonMenuItem`

## Key Inputs

### TDSButtonMenu (tbutton-menu)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `xPosition` | `'before' \| 'after'` | `'before'` | Vị trí menu theo chiều ngang: `before` (trái trigger), `after` (phải trigger) |
| `yPosition` | `'above' \| 'below'` | `'below'` | Vị trí menu theo chiều dọc: `above` (trên trigger), `below` (dưới trigger) |
| `overlapTrigger` | `boolean` | `false` | Menu có overlap với trigger hay không |
| `hasBackdrop` | `boolean` | `undefined` | Hiển thị backdrop phía sau menu |
| `backdropClass` | `string` | `'cdk-overlay-transparent-backdrop'` | Class CSS cho backdrop |
| `overlayPanelClass` | `string \| string[]` | `''` | Class hoặc list class cho overlay panel (set via default options, not `@Input`). Use `panelClass` (`@Input('class')`) to set classes from template |
| `aria-label` | `string` | - | ARIA label cho menu panel |
| `aria-labelledby` | `string` | - | ARIA labelled by |
| `aria-describedby` | `string` | - | ARIA described by |

### TDSButtonMenuTrigger

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsbuttonMenuTriggerFor` | `TDSButtonMenuPanel` | - | Reference đến menu instance |
| `menuData` | `any` | - | Data truyền vào lazy-rendered content |
| `restoreFocus` | `boolean` | `true` | Restore focus vào trigger khi đóng menu |

### TDSButtonMenuItem ([tds-button-menu-item])

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `disabled` | `boolean` | `false` | Vô hiệu hóa menu item |
| `role` | `'menuitem' \| 'menuitemradio' \| 'menuitemcheckbox'` | `'menuitem'` | ARIA role cho menu item |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước menu item |

## Key Outputs

### TDSButtonMenu

| Output | Type | Description |
|--------|------|-------------|
| `closed` | `EventEmitter<MenuCloseReason>` | Emit khi menu đóng với reason: `void`, `'click'`, `'keydown'`, `'tab'` |
| `close` | `EventEmitter<MenuCloseReason>` | @deprecated Dùng `closed` thay thế |

### TDSButtonMenuTrigger

| Output | Type | Description |
|--------|------|-------------|
| `menuOpened` | `EventEmitter<void>` | Emit khi menu mở |
| `menuClosed` | `EventEmitter<void>` | Emit khi menu đóng |

## Key Methods

### TDSButtonMenu

| Method | Parameters | Description |
|--------|-----------|-------------|
| `focusFirstItem` | `origin?: FocusOrigin` | Focus vào item đầu tiên của menu |
| `resetActiveItem` | - | Reset active item về trạng thái ban đầu |
| `setElevation` | `depth: number` | Set elevation cho menu panel dựa trên depth |

### TDSButtonMenuTrigger

| Method | Parameters | Description |
|--------|-----------|-------------|
| `toggleMenu` | - | Toggle menu giữa open/close |
| `openMenu` | - | Mở menu |
| `closeMenu` | - | Đóng menu |
| `focus` | `origin?: FocusOrigin, options?: FocusOptions` | Focus vào trigger element |
| `updatePosition` | - | Cập nhật vị trí menu |

## Usage

```html
<!-- Basic button menu -->
<button [tdsbuttonMenuTriggerFor]="menu" tds-button>
  Options
</button>

<tbutton-menu #menu="TDSButtonMenu" xPosition="after" yPosition="below">
  <div tds-button-menu-item (click)="onEdit()">Edit</div>
  <div tds-button-menu-item (click)="onDelete()">Delete</div>
  <div tds-button-menu-item [disabled]="true">Disabled</div>
</tbutton-menu>

<!-- Nested menu -->
<button [tdsbuttonMenuTriggerFor]="parentMenu" tds-button>
  File
</button>

<tbutton-menu #parentMenu="TDSButtonMenu">
  <div tds-button-menu-item [tdsbuttonMenuTriggerFor]="subMenu">
    New > 
  </div>
  <div tds-button-menu-item>Open</div>
  <div tds-button-menu-item>Save</div>
</tbutton-menu>

<tbutton-menu #subMenu="TDSButtonMenu">
  <div tds-button-menu-item>Document</div>
  <div tds-button-menu-item>Folder</div>
</tbutton-menu>

<!-- With positioning -->
<button [tdsbuttonMenuTriggerFor]="topMenu" tds-button>
  Top Menu
</button>

<tbutton-menu #topMenu="TDSButtonMenu" 
              xPosition="before" 
              yPosition="above"
              [overlapTrigger]="false">
  <div tds-button-menu-item>Item 1</div>
  <div tds-button-menu-item>Item 2</div>
</tbutton-menu>

<!-- With sizes -->
<button [tdsbuttonMenuTriggerFor]="sizeMenu" tds-button>
  Size Menu
</button>

<tbutton-menu #sizeMenu="TDSButtonMenu">
  <div tds-button-menu-item size="sm">Small Item</div>
  <div tds-button-menu-item size="md">Medium Item</div>
  <div tds-button-menu-item size="lg">Large Item</div>
</tbutton-menu>
```

```typescript
import { TDSButtonMenu, TDSButtonMenuTrigger, TDSButtonMenuItem } from 'tds-ui/button-menu';
import { TDSButtonModule } from 'tds-ui/button';

@Component({
  standalone: true,
  imports: [
    TDSButtonMenu, 
    TDSButtonMenuTrigger, 
    TDSButtonMenuItem,
    TDSButtonModule
  ],
})
export class MyComponent {
  onEdit() {
    console.log('Edit clicked');
  }

  onDelete() {
    console.log('Delete clicked');
  }
}
```

## Notes

- Component tự động positioning để đảm bảo menu không bị viewport cắt
- Hỗ trợ nested menu (menu trong menu) với `tdsbuttonMenuTriggerFor` trên `tds-button-menu-item`
- Keyboard navigation: Arrow keys để navigate, Enter/Space để select, Escape để đóng
- `overlapTrigger=false` sẽ đặt menu ngay cạnh trigger thay vì overlap
- `xPosition` và `yPosition` có thể auto-flip khi không đủ không gian
- `restoreFocus` option có thể disable nếu muốn custom focus behavior
- Menu items có thể be disabled với input `disabled`
- Hỗ trợ các roles khác nhau: `menuitem`, `menuitemradio`, `menuitemcheckbox`
- Size options cho menu items: `xs`, `sm`, `md` (default), `lg`, `xl`
- Component tự động quản lý accessibility với proper ARIA attributes
