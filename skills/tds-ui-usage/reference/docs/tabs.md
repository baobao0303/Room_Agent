# Tabs

Điều hướng nội dung theo tab.

**Selector:** `tds-tabset` (container), `tds-tab` (individual tab)
**Import:** `import { TDSTabsModule } from 'tds-ui/tabs';`
**Export as:** `tdsTabset`, `tdsTab`

## tds-tabset Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `selectedIndex` | `number \| null` | `null` | Tab đang active (index) |
| `tabPosition` | `'top' \| 'bottom' \| 'left' \| 'right'` | `'top'` | Vị trí tab bar |
| `tdsType` | `'line' \| 'card' \| 'editable-card' \| 'pill' \| 'pill-outline'` | `'line'` | Kiểu tab |
| `tdsSize` | `'default' \| 'small'` | `'default'` | Kích thước tab |
| `animated` | `TDSAnimatedInterface \| boolean` | `false` | Animation khi chuyển tab |
| `tabBarExtraContent` | `TemplateRef<void>` | `undefined` | Nội dung thêm phía phải tab bar |
| `tabBarGutter` | `number` | `8` | Khoảng cách giữa các tab |
| `tabBarStyle` | `{ [key: string]: string } \| null` | `null` | Custom style cho tab bar |
| `centered` | `boolean` | `false` | Center tab bar |
| `hideAdd` | `boolean` | `false` | Ẩn nút add (editable-card) |
| `hideAll` | `boolean` | `false` | Ẩn tất cả |
| `hidenNextBtn` | `boolean` | `false` | Ẩn nút next/prev |
| `linkRouter` | `boolean` | `false` | Liên kết với route |
| `linkExact` | `boolean` | `true` | Match exact route |
| `tdsBorderless` | `boolean` | `false` | Không border |
| `tdsAddable` | `boolean` | `false` | Cho phép thêm tab |
| `tdsHideBar` | `boolean \| undefined` | `undefined` | Ẩn tab bar |
| `clsTab` | `string` | `''` | Custom class cho tab |
| `addIcon` | `string \| TemplateRef<any>` | `'tdsi-plus-circle-fill'` | Icon nút add |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |
| `onCanDeactivate` | `(fromIndex: number, toIndex: number) => Observable<boolean> \| Promise<boolean> \| boolean` | `null` | Guard kiểm tra có thể rời tab không |

## tds-tabset Outputs

| Output | Type | Description |
|--------|------|-------------|
| `selectedIndexChange` | `EventEmitter<number>` | Khi đổi tab |
| `selectChange` | `EventEmitter<TDSTabChangeEvent>` | Chi tiết tab thay đổi |
| `tabListScroll` | `EventEmitter<TDSTabScrollEvent>` | Khi scroll tab list |
| `close` | `EventEmitter<{ index: number }>` | Khi đóng tab (editable) |
| `add` | `EventEmitter<void>` | Khi click nút add |

## tds-tab Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `string \| TemplateRef<TabTemplateContext>` | `''` | Tiêu đề tab |
| `disabled` | `boolean` | `false` | Vô hiệu hóa tab |
| `forceRender` | `boolean` | `false` | Render nội dung dù tab chưa active |
| `closable` | `boolean` | `false` | Có nút close (editable-card) |
| `clsContent` | `string` | `'p-4 w-full h-full'` | CSS class nội dung tab |
| `closeIcon` | `string \| TemplateRef<any> \| null` | `'tdsi-close-fill'` | Icon nút đóng |

## tds-tab Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tabSelect` | `EventEmitter<void>` | Khi tab được active |
| `tabDeselect` | `EventEmitter<void>` | Khi tab bị deactive |
| `tabClick` | `EventEmitter<void>` | Khi click tab |
| `tabContextmenu` | `EventEmitter<MouseEvent>` | Khi right-click tab |

## Interfaces

### TDSTabChangeEvent

```typescript
class TDSTabChangeEvent {
  index?: number;
  tab: any;
}
```

### TDSTabScrollEvent

```typescript
type TDSTabScrollEvent = TDSTabTouchScrollEvent | TDSTabWheelScrollEvent;

interface TDSTabWheelScrollEvent {
  type: 'wheel';
  event: WheelEvent;
}

interface TDSTabTouchScrollEvent {
  type: 'touchstart' | 'touchmove' | 'touchend';
  event: TouchEvent;
}
```

### TabTemplateContext

```typescript
interface TabTemplateContext {
  visible: boolean;
  active: boolean;
}
```

### TDSAnimatedInterface

```typescript
interface TDSAnimatedInterface {
  inkBar: boolean;
  tabPane: boolean;
}
```

## Usage

```html
<tds-tabset [(selectedIndex)]="activeTab">
  <tds-tab title="Thông tin">
    <p>Nội dung tab 1</p>
  </tds-tab>
  <tds-tab title="Lịch sử">
    <p>Nội dung tab 2</p>
  </tds-tab>
  <tds-tab title="Cài đặt" [disabled]="true">
    <p>Nội dung tab 3</p>
  </tds-tab>
</tds-tabset>
```

```html
<!-- Custom tab title via template ref -->
<ng-template #customTitle let-active="active" let-visible="visible">
  <span>Tab 1 - <strong>Custom</strong></span>
  @if (active) {
    <span class="badge">Active</span>
  }
</ng-template>

<tds-tabset [(selectedIndex)]="activeTab" tdsType="card">
  <tds-tab [title]="customTitle">
    <p>Nội dung tab 1</p>
  </tds-tab>

  <tds-tab title="Tab 2">
    <p>Nội dung tab 2</p>
  </tds-tab>
</tds-tabset>
```

```html
<!-- Editable card type with add/close -->
<tds-tabset
  tdsType="editable-card"
  [(selectedIndex)]="activeTab"
  (add)="onAddTab()"
  (close)="onCloseTab($event)">
  <tds-tab title="Tab 1" [closable]="true">
    <p>Nội dung tab 1</p>
  </tds-tab>
  <tds-tab title="Tab 2" [closable]="true">
    <p>Nội dung tab 2</p>
  </tds-tab>
</tds-tabset>
```

```html
<!-- Router integration -->
<tds-tabset
  [linkRouter]="true"
  [linkExact]="true">
  <tds-tab title="Dashboard">
    <a [routerLink]="['/dashboard']" tds-tab-link>Dashboard</a>
  </tds-tab>
  <tds-tab title="Users">
    <a [routerLink]="['/users']" tds-tab-link>Users</a>
  </tds-tab>
</tds-tabset>
```

```typescript
import { TDSTabsModule } from 'tds-ui/tabs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-detail',
  standalone: true,
  imports: [TDSTabsModule, CommonModule]
})
export class DetailComponent {
  activeTab = 0;

  onTabChange(index: number) {
    console.log('Tab changed to:', index);
  }

  onAddTab() {
    console.log('Add new tab');
  }

  onCloseTab(event: { index: number }) {
    console.log('Close tab:', event.index);
  }
}
```

## Notes

- Nội dung tab lazy-rendered mặc định (chỉ render khi active)
- Dùng `[forceRender]="true"` để pre-render tab (cần thiết khi tab chứa form validators)
- `tdsType='editable-card'` cho phép thêm/xóa tab với `(add)` và `(close)` events
- `tdsAddable=true` enable addable mode cho bất kỳ tab type nào
- Khi dùng `linkRouter=true`, component sẽ tự động select tab dựa trên current route
- `selectedIndex` có thể là `null`, giúp quản lý trạng thái "không tab nào active"
- `tabBarExtraContent` thêm nội dung vào phía phải tab bar (vd: button action)
- `onCanDeactivate` guard function để prevent离开 tab khi có unsaved changes
- `animated` có thể là boolean hoặc object để control riêng inkBar và tabPane animation
- `clsContent` custom class cho content area của mỗi tab
- `tabPosition='left'` hoặc `'right'` hiển thị vertical tabs
