# Drawer

Slide-in panel từ cạnh màn hình. Dùng `TDSDrawerService` hoặc component `tds-drawer`.

**Selector:** `tds-drawer`
**Import:** `import { TDSDrawerModule, TDSDrawerService, TDSDrawerRef, TDSDrawerOptions, TDS_DRAWER_DATA } from 'tds-ui/drawer';`
**Export as:** `tdsDrawer`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `visible` | `boolean` | `false` | Hiển thị/ẩn drawer |
| `content` | `TemplateRef<{ $implicit: D; drawerRef: TDSDrawerRef<R> }> \| Type<T>` | — | Nội dung drawer |
| `title` | `string \| TemplateRef<{}>` | — | Tiêu đề |
| `footer` | `string \| TemplateRef<{}>` | — | Footer template |
| `placement` | `TDSDrawerPlacement` | `'right'` | Vị trí hiển thị |
| `size` | `TDSDrawerSize` | `null` | Preset size (sm: 320px, md: 400px, lg: 640px, xl: 780px) |
| `width` | `number \| string \| null` | — | Chiều rộng (placement left/right) |
| `height` | `number \| string \| null` | — | Chiều cao (placement top/bottom) |
| `closable` | `boolean` | `true` | Hiển thị nút đóng |
| `maskClosable` | `boolean` | `true` | Đóng khi click mask |
| `mask` | `boolean` | `true` | Hiển thị mask overlay |
| `keyboard` | `boolean` | `true` | Đóng bằng ESC |
| `closeOnNavigation` | `boolean` | `true` | Đóng khi navigate |
| `noAnimation` | `boolean` | `false` | Tắt animation |
| `closeIcon` | `string \| TemplateRef<void>` | `'close'` | Icon đóng |
| `maskStyle` | `NgStyleInterface` | `{}` | CSS style cho mask |
| `bodyStyle` | `NgStyleInterface` | `{}` | CSS style cho body |
| `wrapClassName` | `string` | — | CSS class cho wrapper |
| `zIndex` | `number` | `1000` | Z-index của drawer |
| `offsetX` | `number` | `0` | X offset |
| `offsetY` | `number` | `0` | Y offset |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `onViewInit` | `EventEmitter<void>` | Khi view init |
| `onClose` | `EventEmitter<MouseEvent>` | Khi drawer đóng |
| `visibleChange` | `EventEmitter<boolean>` | Khi visible thay đổi |

## Observable Outputs (via TDSDrawerRef)

| Output | Type | Description |
|--------|------|-------------|
| `afterOpen` | `Observable<void>` | Khi drawer mở xong (sau animation) |
| `afterClose` | `Observable<R \| undefined>` | Khi drawer đóng xong (sau animation) |

## Type Definitions

```typescript
type TDSDrawerPlacement = 'left' | 'right' | 'top' | 'bottom';
type TDSDrawerSize = 'sm' | 'md' | 'lg' | 'xl' | null;

interface TDSDrawerOptionsOfComponent<T = TDSSafeAny, D = TDSSafeAny> {
  closable?: boolean;
  maskClosable?: boolean;
  closeOnNavigation?: boolean;
  direction?: Direction;
  mask?: boolean;
  keyboard?: boolean;
  noAnimation?: boolean;
  title?: string | TemplateRef<{}>;
  footer?: string | TemplateRef<{}>;
  content?: TemplateRef<{ $implicit: D; drawerRef: TDSDrawerRef }> | Type<T>;
  contentParams?: D; // @Deprecated
  tdsData?: D;
  maskStyle?: object;
  bodyStyle?: object;
  wrapClassName?: string;
  width?: number | string | null;
  height?: number | string | null;
  placement?: TDSDrawerPlacement;
  zIndex?: number;
  offsetX?: number;
  offsetY?: number;
}

interface TDSDrawerOptions<T = TDSSafeAny, D = TDSSafeAny> extends TDSDrawerOptionsOfComponent<T, D> {
  onCancel?(): Promise<any>;
}
```

## TDSDrawerService Methods

| Method | Description |
|--------|-------------|
| `create<T>(options: TDSDrawerOptions)` | Mở drawer, trả về `TDSDrawerRef` |

## TDSDrawerRef Methods

```typescript
abstract class TDSDrawerRef<T = TDSSafeAny, R = TDSSafeAny> {
  abstract afterOpen: Observable<void>;
  abstract afterClose: Observable<R | undefined>;
  abstract close(result?: R): void;
  abstract open(): void;
  abstract getContentComponent(): T | null;
  
  abstract closable?: boolean;
  abstract noAnimation?: boolean;
  abstract maskClosable?: boolean;
  abstract keyboard?: boolean;
  abstract mask?: boolean;
  abstract title?: string | TemplateRef<{}>;
  abstract placement?: TDSDrawerPlacement;
  abstract maskStyle?: object;
  abstract bodyStyle?: object;
  abstract wrapClassName?: string;
  abstract width?: number | string | null;
  abstract height?: number | string | null;
  abstract zIndex?: number | string;
  abstract offsetX?: number | string;
  abstract offsetY?: number | string;
}
```

## Usage

```typescript
import { TDSDrawerService, TDSDrawerModule, TDSDrawerRef, TDS_DRAWER_DATA } from 'tds-ui/drawer';
import { inject } from '@angular/core';

@Component({ standalone: true, imports: [TDSDrawerModule] })
export class MyComponent {
  isVisible = false;
  
  constructor(private drawer: TDSDrawerService) {}

  openDrawer() {
    const ref = this.drawer.create({
      content: DetailComponent,
      title: 'Chi tiết',
      width: 500,
      tdsData: { id: 456 },
    });
    ref.afterClose.subscribe(result => { /* handle result */ });
  }
  
  openFromTemplate() {
    this.isVisible = true;
  }
  
  closeDrawer() {
    this.isVisible = false;
  }
}
```

Template usage:
```html
<tds-drawer
  [visible]="isVisible"
  title="Drawer Title"
  placement="right"
  (onClose)="closeDrawer()"
  [footer]="footerTpl">
  <ng-container *tdsDrawerContent>
    <p>Drawer content goes here.</p>
  </ng-container>

  <ng-template #footerTpl>
    <div class="flex justify-end w-full">
      <button tds-button color="secondary" class="mr-2" (click)="closeDrawer()">Cancel</button>
      <button tds-button (click)="closeDrawer()">Submit</button>
    </div>
  </ng-template>
</tds-drawer>
```

In content component:
```typescript
import { TDS_DRAWER_DATA, TDSDrawerRef } from 'tds-ui/drawer';
import { inject } from '@angular/core';

@Component({ standalone: true })
export class DetailComponent {
  data = inject(TDS_DRAWER_DATA) as { id: number };
  drawerRef = inject(TDSDrawerRef);

  closeDrawer(result?: any) { 
    this.drawerRef.close(result); 
  }
}
```

## Drawer Content Directive

**Selector:** `[tdsDrawerContent]`
**Export as:** `tdsDrawerContent`

Directive để đánh dấu content template của drawer khi dùng declarative approach.

```html
<tds-drawer [visible]="isVisible">
  <ng-container *tdsDrawerContent>
    <p>Content here</p>
  </ng-container>
</tds-drawer>
```

## Size Presets

| Size | Width/Height |
|------|--------------|
| `sm` | 320px |
| `md` | 400px (default) |
| `lg` | 640px |
| `xl` | 780px |

## Placement Options

| Placement | Description |
|-----------|-------------|
| `right` | Slide từ phải (default) |
| `left` | Slide từ trái |
| `top` | Slide từ trên |
| `bottom` | Slide từ dưới |

## Notes

- Inject `TDSDrawerService` as a regular service — no `providers` needed in component
- Dùng `TDS_DRAWER_DATA` token để nhận data trong content component
- `placement: 'right'` là mặc định — phù hợp cho sidebar/detail panel
- Dùng `footer` template để thêm action buttons ở cuối drawer
- `size` preset: sm (320px), md (400px), lg (640px), xl (780px)
- Animation duration: 300ms (có thể tắt bằng `noAnimation`)
- `offsetX` và `offsetY` dùng để điều chỉnh vị trí drawer từ vị trí mặc định
- `closeOnNavigation = true` tự động đóng khi user navigate đến route khác
- `maskClosable` kiểm soát việc đóng drawer khi click vào mask overlay
- `keyboard` kiểm soát việc đóng drawer khi nhấn ESC
- `contentParams` là @deprecated, dùng `tdsData` thay thế
- Drawer tự động focus trap khi mở và restore focus khi đóng
- Support RTL (right-to-left) layout
- Drawer component standalone, không cần import module
