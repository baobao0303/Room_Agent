# App Shell với Layout (Sider + Menu + Router Outlet)

Pattern admin shell phổ biến: sidebar collapse + menu + header + vùng content render router-outlet.

## 1. Import

Standalone component cần `TDSLayoutModule`, `TDSMenuModule` từ `tds-ui`, và `RouterOutlet` từ `@angular/router`. Chi tiết import xem trong block Code bên dưới.

## 2. Code

```typescript
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TDSLayoutModule } from 'tds-ui/layout';
import { TDSMenuModule } from 'tds-ui/menu';
import { TDSMenuDTO } from 'tds-ui/menu';

@Component({
  standalone: true,
  imports: [TDSLayoutModule, TDSMenuModule, RouterOutlet],
  template: `
    <tds-layout>
      <tds-layout-sider
        [tdsWidth]="240"
        [tdsCollapsedWidth]="64"
        [tdsCollapsible]="true"
        [tdsCollapsed]="isCollapsed()"
        [tdsBreakpoint]="'lg'"
        [tdsTrigger]="customTrigger"
        (tdsCollapsedChange)="isCollapsed.set($event)">
        <ng-template #customTrigger>
          <span class="trigger-icon" tds-icon tds-icon-name="menu"></span>
        </ng-template>
        <tds-menu
          [data]="menuData"
          [mode]="'dark'"
          [matchRouter]="true">
        </tds-menu>
      </tds-layout-sider>

      <tds-layout-header>
        <span class="brand">My Admin</span>
      </tds-layout-header>

      <tds-layout-content>
        <router-outlet></router-outlet>
      </tds-layout-content>
    </tds-layout>
  `,
  styles: [`
    :host { display: block; height: 100vh; }
    .trigger-icon { display: inline-flex; padding: 0 12px; }
    .brand { font-weight: 600; }
  `],
})
export class AppShellComponent {
  isCollapsed = signal(false);
  menuData: TDSMenuDTO[] = [
    { name: 'Dashboard', icon: 'tdsi-dashboard', link: '/dashboard' },
    { name: 'Users', icon: 'tdsi-user', link: '/users' },
    {
      name: 'Settings',
      icon: 'tdsi-setting',
      listChild: [
        { name: 'Profile', link: '/settings/profile' },
        { name: 'Security', link: '/settings/security' },
      ],
    },
  ];
}
```

## 3. Giải thích

- Cấu trúc **flat**: `tds-layout` chứa `tds-layout-sider`, `tds-layout-header`, `tds-layout-content` ở cùng cấp. **Không nest `tds-layout`** — CSS `.tds-layout-has-sider > .tds-layout { width: 0 }` làm nested sập width.
- `tds-layout-content` có sẵn `tds-custom-scroll` và `flex-auto min-h-0` → fill phần còn lại, cuộn độc lập với sider.
- `tdsBreakpoint="'lg'"` → sider auto-collapse khi viewport ≤ 991.98px (theo `siderResponsiveMap`). `tdsCollapsedChange` đồng bộ lại state.
- `tds-menu` **data-driven**: bind `[data]` thành mảng `TDSMenuDTO`. Item có `link` → tự render `<a [routerLink]="[item.link]">`. Item có `listChild` → submenu. Không dùng `<tds-menu-item>` làm content child.
- `[mode]="'dark'"` là theme của menu (`dark | light | default`), không phải layout mode. Sider tự switch menu inline/popup khi collapse.
- `tdsTrigger` custom bắt buộc nếu muốn icon — default trigger template bị comment trong source (`sider-trigger.component.ts` lines 30–35). Icon dùng CSS class `<span tds-icon tds-icon-name="...">`, không cần import module icon.
- `[(tdsCollapsed)]` two-way binding cũng dùng được thay vì `(tdsCollapsedChange)` + signal.

## 4. Tips

- **Height chain bắt buộc:** `html, body` cần `height: 100%` (hoặc dùng `100vh` trên `:host`). Không có → `tds-layout-content` height 0 → không scroll.
- Sider auto-collapse menu inline khi `tdsCollapsedWidth !== 0` và menu có `mode` phù hợp. Set `tdsCollapsedWidth="0"` nếu muốn ẩn hẳn sider thay vì thu nhỏ.
- `[matchRouter]="true"` (default) tự active menu item theo route hiện tại. Dùng `[matchRouterExact]` cho match chính xác.
- Muốn submenu mở mặc định: set `isOpen: true` trên `TDSMenuDTO` cha. Muốn divider: `divider: true`. Xem đầy đủ `TDSMenuDTO` ở `reference/docs/menu.md`.
- Xem thêm: `reference/docs/layout.md`, `reference/docs/menu.md`.
