# NavBar

Thanh điều hướng hỗ trợ vertical, horizontal, và inline modes. Navbar linh hoạt với nested submenus.

**Selectors:**
- `[tds-navbar]` - Container directive
- `[tds-navbar-item]` - Menu item directive
- `[tds-navbar-group]` - Group items với title
- `[tds-navbar-divider]` - Divider giữa items

**Import:** `import { TDSNavBarModule } from 'tds-ui/nav-bar';`

## [tds-navbar] Directive

**Export as:** `tdsNavBar`

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsMode` | `TDSNavBarModeType` | `'vertical'` | Mode: `vertical`, `horizontal`, `inline` |
| `tdsTheme` | `TDSNavBarThemeType` | `'light'` | Theme: `light`, `dark` |
| `tdsInlineCollapsed` | `boolean` | `false` | Thu gọn (inline mode) |
| `tdsInlineIndent` | `number` | `24` | Indent level cho submenu (px) |
| `tdsSelectable` | `boolean` | `true` (dropdown: `false`) | Cho phép select item |

### Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsClick` | `EventEmitter<TDSNavBarItemDirective>` | Khi click item |

### Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `setInlineCollapsed` | `collapsed: boolean` | Set trạng thái inline collapsed |
| `updateInlineCollapse` | - | Cập nhật inline collapse state |

## [tds-navbar-item] Directive

**Export as:** `tdsNavBarItem`

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa item |
| `tdsSelected` | `boolean` | `false` | Active state |
| `tdsDanger` | `boolean` | `false` | Danger style (red) |
| `tdsMatchRouter` | `boolean` | `false` | Auto-active theo route |
| `tdsMatchRouterExact` | `boolean` | `false` | Exact route match |
| `tdsMatchOptions` | `IsActiveMatchOptions` | `{paths: 'exact', ...}` | Router match options |
| `tdsPaddingLeft` | `number` | `undefined` | Custom left padding |

### Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `setSelectedState` | `value: boolean` | Set selected state |

## [tds-navbar-group] Directive

**Export as:** `tdsNavBarGroup`

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTitle` | `string \| TemplateRef<void>` | `undefined` | Title nhóm |

## Sub-navbar Component

**Selector:** `[tds-subnavbar]`
**Export as:** `tdsSubNavBar`

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsNavBarClassName` | `string` | `''` | Custom CSS class cho sub-navbar container |
| `tdsPaddingLeft` | `number \| null` | `null` | Custom left padding |
| `tdsTitle` | `string \| TemplateRef<void> \| null` | `null` | Tiêu đề sub-navbar |
| `tdsIcon` | `string \| null` | `null` | Icon (class name) |
| `tdsHtmlIcon` | `string \| null` | `null` | HTML icon tùy chỉnh |
| `tdsOpen` | `boolean` | `false` | Expanded state |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa |
| `tdsPlacement` | `'bottomLeft' \| 'bottomRight' \| ...` | `'bottomLeft'` | Vị trí popup (horizontal mode) |

### Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsOpenChange` | `EventEmitter<boolean>` | Phát ra khi open state thay đổi |

### Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `setOpenStateWithoutDebounce` | `value: boolean` | Set open state (no debounce) |

## Usage

```html
<nav tds-navbar
  [tdsMode]="'vertical'"
  [tdsTheme]="'light'"
  [tdsInlineCollapsed]="false"
  (tdsClick)="onNavClick($event)">

  <a tds-navbar-item [routerLink]="['/dashboard']">
    <i class="tdsi-dashboard-fill"></i>
    <span>Dashboard</span>
  </a>

  <div tds-navbar-group [tdsTitle]="'Management'">
    <a tds-navbar-item [routerLink]="['/users']">
      <i class="tdsi-user-fill"></i>
      <span>Users</span>
    </a>
    <a tds-navbar-item [routerLink]="['/roles']">
      <i class="tdsi-team-fill"></i>
      <span>Roles</span>
    </a>
  </div>

  <div tds-subnavbar
    [tdsTitle]="'Reports'"
    [tdsOpen]="true"
    [tdsIcon]="'tdsi-file-text-fill'"
    (tdsOpenChange)="onSubNavOpenChange($event)">
    <a tds-navbar-item [routerLink]="['/reports/daily']">Daily</a>
    <a tds-navbar-item [routerLink]="['/reports/monthly']">Monthly</a>
  </div>

  <div tds-navbar-divider></div>

  <a tds-navbar-item [tdsDanger]="true" (click)="logout()">
    <i class="tdsi-logout-fill"></i>
    <span>Logout</span>
  </a>
</nav>
```

```typescript
import { TDSNavBarModule } from 'tds-ui/nav-bar';
import { TDSNavBarItemDirective } from 'tds-ui/nav-bar';

@Component({
  standalone: true,
  imports: [TDSNavBarModule, RouterModule],
})
export class AppComponent {
  onNavClick(item: TDSNavBarItemDirective) {
    console.log('Nav item clicked:', item);
  }

  onSubNavOpenChange(open: boolean) {
    console.log('Sub-nav open state:', open);
  }

  logout() {
    // Handle logout
  }
}
```

```html
<!-- Horizontal navbar -->
<nav tds-navbar [tdsMode]="'horizontal'" [tdsTheme]="'dark'">
  <a tds-navbar-item [routerLink]="['/home']">Home</a>
  <a tds-navbar-item [routerLink]="['/about']">About</a>
  <a tds-navbar-item [routerLink]="['/contact']">Contact</a>
</nav>
```

```html
<!-- Inline collapsed navbar -->
<nav tds-navbar
  [tdsMode]="'inline'"
  [tdsInlineCollapsed]="true"
  [tdsInlineIndent]="32">
  <!-- Items tự động thu gọn thành icon only -->
</nav>
```

## Notes

- `tdsMode`:
  - `vertical`: Menu dọc (mặc định)
  - `horizontal`: Menu ngang
  - `inline`: Inline với expand/collapse
- `tdsInlineCollapsed` chỉ có hiệu quả trong `inline` mode
- Component tự động tính padding cho nested items dựa trên `level * tdsInlineIndent`
- Hỗ trợ RTL (right-to-left) tự động
- `tdsMatchRouter=true` tự active item dựa trên current route
- `tdsDanger` dùng cho các action nguy hiểm (logout, delete, v.v.)
- Submenu hỗ trợ nested unlimited levels
- Có thể dùng `routerLink` trực tiếp trên `tds-navbar-item` để auto-active
