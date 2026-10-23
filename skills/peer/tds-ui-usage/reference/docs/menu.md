# Menu

Menu điều hướng đa cấp với hỗ trợ icon, badge, tag, và divider. Component menu chính của hệ thống TDS UI.

**Selector:** `tds-menu`
**Import:** `import { TDSMenuModule } from 'tds-ui/menu';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `data` | `Array<any>` | `[]` | Dữ liệu menu (array của `TDSMenuDTO`) |
| `mode` | `TDSMenuMode` | `'dark'` | Theme: `dark`, `light`, `default` |
| `showIcon` | `boolean` | `true` | Hiển thị icon cho menu items |
| `showFooter` | `boolean` | `true` | Hiển thị footer menu |
| `showLogo` | `boolean` | `false` | Hiển thị logo |
| `inlineCollapsed` | `boolean` | `false` | Thu gọn menu (inline mode) |
| `matchRouter` | `boolean` | `true` | Tự động active menu item theo route |
| `matchRouterExact` | `boolean` | `false` | Match exact route |
| `tdsVariant` | `'secondary' \| 'primary' \| 'minimal'` | `'secondary'` | Variant style |
| `tdsHeader` | `TemplateRef<void> \| string \| null` | `null` | Template hoặc text header |
| `tdsFooter` | `TemplateRef<void> \| string \| null` | `null` | Template hoặc text footer |
| `tdsMenuFooter` | `TemplateRef<{ $implicit: boolean }>` | — | Template cho menu footer (nhận context `$implicit` = inlineCollapsed) |
| `options` | `TDSMenuOptionDTO` | `{...}` | @deprecated từ version 2.7.0 |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `onClickItem` | `EventEmitter<TDSMenuDTO>` | Khi click menu item |
| `onOpenChange` | `EventEmitter<boolean>` | Khi toggle inline collapsed |

## TDSMenuDTO Interface

```typescript
interface TDSMenuDTO {
  name: string;                    // Tên menu item
  icon?: string;                   // Icon class (tdsi-xxx)
  htmlIcon?: string;               // HTML string cho custom icon
  link?: any;                      // Router link
  disabled?: boolean;              // Vô hiệu hóa
  hidden?: boolean;                // Ẩn menu item
  isSelected?: boolean;            // Active state
  isOpen?: boolean;                // Expanded state (cho submenu)
  listChild?: Array<TDSMenuDTO>;   // Menu con
  groupTitle?: string;             // Title nhóm menu
  divider?: boolean;               // Hiển thị divider
  linkProps?: TDSMenuLinkPropsDTO; // Router link props
  badge?: TDSMenuBadgeDTO;         // Badge config
  tag?: TDSMenuTagDTO;             // Tag config
  dot?: TDSMenuDotDTO;             // Dot config (cho menu cha)
}
```

### TDSMenuLinkPropsDTO

```typescript
interface TDSMenuLinkPropsDTO {
  queryParams?: {[k: string]: any};
  fragment?: string;
  queryParamsHandling?: 'merge' | 'preserve' | '';
  preserveFragment?: boolean;
  skipLocationChange?: boolean;
  replaceUrl?: boolean;
  state?: {[k: string]: any};
  routerLinkActiveOptions?: IsActiveMatchOptions;
  routerLinkActive?: string | string[];
}
```

### TDSMenuBadgeDTO

```typescript
interface TDSMenuBadgeDTO {
  count: number;                   // Số hiển thị
  overflowCount?: number;          // Số max hiển thị (vd: 99+)
  tdsStyle?: { [key: string]: string }; // Custom style
}
```

### TDSMenuTagDTO

```typescript
interface TDSMenuTagDTO {
  text: string;                    // Text tag
  type?: 'default' | 'outline';    // Kiểu tag
  status?: TDSTagStatusType;       // Màu status
  rounded?: string;                // Border radius
}
```

### TDSMenuDotDTO

```typescript
interface TDSMenuDotDTO {
  status?: TDSTagStatusType;       // Màu dot
}
```

## Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `setInlineCollapsed` | `collapsed: boolean` | Set trạng thái inline collapsed |
| `updateInlineCollapse` | - | Cập nhật inline collapse state |

## Footer Directive

**Selector:** `[tdsMenuFooter]`
**Export as:** `tdsMenuFooter`
**Import:** `import { TDSMenuFooterDirective } from 'tds-ui/menu';`

Dùng attribute directive `tdsMenuFooter` trên `<ng-template>` để cung cấp footer template cho menu.

```html
<tds-menu [data]="menuData">
  <ng-template #footer tdsMenuFooter let-collapsed>
    <div class="footer">{{ collapsed ? 'Thu gọn' : 'Mở rộng' }}</div>
  </ng-template>
</tds-menu>
```

## Usage

```html
<tds-menu
  [data]="menuData"
  mode="dark"
  [showIcon]="true"
  [inlineCollapsed]="false"
  (onClickItem)="onMenuClick($event)"
  [tdsHeader]="headerTemplate"
  [tdsFooter]="footerTemplate">
</tds-menu>

<ng-template #headerTemplate>
  <div class="p-4">
    <h3>Application Name</h3>
  </div>
</ng-template>

<ng-template #footerTemplate>
  <div class="p-4 text-center">
    <small>Version 1.0.0</small>
  </div>
</ng-template>
```

```typescript
import { TDSMenuModule } from 'tds-ui/menu';

@Component({
  standalone: true,
  imports: [TDSMenuModule],
})
export class AppComponent {
  menuData = [
    {
      name: 'Dashboard',
      icon: 'tdsi-dashboard-fill',
      link: '/dashboard',
    },
    {
      name: 'Management',
      icon: 'tdsi-settings-fill',
      groupTitle: 'Management',
      listChild: [
        {
          name: 'Users',
          icon: 'tdsi-user-fill',
          link: '/users',
          badge: { count: 5, overflowCount: 99 }
        },
        {
          name: 'Roles',
          icon: 'tdsi-team-fill',
          link: '/roles',
          tag: { text: 'New', status: 'success' }
        }
      ]
    },
    {
      name: 'Reports',
      icon: 'tdsi-file-text-fill',
      link: '/reports',
      divider: true,
      dot: { status: 'error' } // Đỏ cho con chưa đọc
    }
  ];

  onMenuClick(item: TDSMenuDTO) {
    console.log('Menu clicked:', item);
  }
}
```

## Notes

- Component tự động quản lý trạng thái active/based trên `routerLink`
- Hỗ trợ multi-level submenu (nested)
- `groupTitle` dùng để chia menu thành các nhóm nhỏ
- `divider` hiển thị đường kẻ ngang giữa các menu items
- Hỗ trợ badge, tag, dot cho indicator trạng thái
- `inlineCollapsed` thu gọn menu thành icon only
- `tdsVariant` đổi style: `secondary` (mặc định), `primary` (màu primary), `minimal` (tối giản)
- Component tự động sync với router khi `matchRouter=true`
