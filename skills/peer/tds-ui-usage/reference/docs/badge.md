# Badge

Hiển thị số lượng hoặc trạng thái trên icon/avatar. Hỗ trợ standalone mode, status colors, và ribbon.

**Selector:** `tds-badge`
**Import:** `import { TDSBadgeModule } from 'tds-ui/badges';`
**Export as:** `tdsBadge`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `count` | `number \| TemplateRef<TDSSafeAny>` | — | Số hiển thị |
| `showZero` | `boolean` | `false` | Hiển thị khi count = 0 |
| `overflowCount` | `number` | `99` | Ngưỡng hiển thị `+` |
| `dot` | `boolean` | `false` | Chỉ hiển thị dot (không số) |
| `showDot` | `boolean` | `true` | Kiểm soát việc hiển thị dot |
| `status` | `TDSBadgeStatusType \| string` | — | Status badge (standalone, không cần con) |
| `text` | `string \| TemplateRef<void> \| null` | — | Text thay thế count (dùng với status) |
| `color` | `string` | `undefined` | Custom color (hoặc preset color) |
| `offset` | `[number, number]` | — | `[x, y]` offset từ vị trí mặc định |
| `title` | `string \| null \| undefined` | — | Title attribute |
| `standalone` | `boolean` | `false` | Badge độc lập (không bọc component con) |
| `size` | `ButtonSize` | `'md'` | Kích thước badge |
| `placement` | `'topLeft' \| 'topRight' \| 'bottomLeft' \| 'bottomRight'` | `'topRight'` | Vị trí badge |
| `tdsStyle` | `{ [key: string]: string } \| null` | `null` | Custom style object |
| `tdsClass` | `string` | `''` | Custom CSS class |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |

## TDSBadgeStatusType

```typescript
type TDSBadgeStatusType = 'primary' | 'secondary' | 'success' | 'info' | 'processing' | 'error' | 'warning';
```

## Preset Colors

Badges hỗ trợ các preset colors: `pink`, `red`, `yellow`, `orange`, `cyan`, `green`, `blue`, `purple`, `geekblue`, `magenta`, `volcano`, `gold`, `lime`.

## Usage

```html
<!-- Badge trên icon -->
<tds-badge [count]="5">
  <span class="tdsi-bell-fill text-xl"></span>
</tds-badge>

<!-- Badge với số lớn -->
<tds-badge [count]="150" [overflowCount]="99">
  <span class="tdsi-mail-fill"></span>
</tds-badge>

<!-- Chỉ hiển thị dot -->
<tds-badge [dot]="true">
  <span class="tdsi-notification-fill"></span>
</tds-badge>

<!-- Show zero -->
<tds-badge [count]="0" [showZero]="true">
  <span class="tdsi-shopping-bag-fill"></span>
</tds-badge>

<!-- Custom offset -->
<tds-badge [count]="5" [offset]="[10, 10]">
  <span class="tdsi-user-fill"></span>
</tds-badge>

<!-- Status badge standalone -->
<tds-badge 
  status="success" 
  text="Hoàn thành"
  [standalone]="true">
</tds-badge>

<tds-badge 
  status="error" 
  text="Lỗi"
  [standalone]="true">
</tds-badge>

<!-- Preset color -->
<tds-badge color="pink" [count]="10">
  <span class="tdsi-heart-fill"></span>
</tds-badge>

<!-- Custom color -->
<tds-badge [color]="'#f50'" [count]="5">
  <span class="tdsi-star-fill"></span>
</tds-badge>

<!-- Size variants -->
<tds-badge [count]="5" size="sm">Small</tds-badge>
<tds-badge [count]="5" size="md">Medium</tds-badge>
<tds-badge [count]="5" size="lg">Large</tds-badge>
<tds-badge [count]="5" size="xl">Extra Large</tds-badge>

<!-- Placement variants -->
<tds-badge [count]="5" placement="topLeft">Top Left</tds-badge>
<tds-badge [count]="5" placement="topRight">Top Right</tds-badge>
<tds-badge [count]="5" placement="bottomLeft">Bottom Left</tds-badge>
<tds-badge [count]="5" placement="bottomRight">Bottom Right</tds-badge>
```

```typescript
import { TDSBadgeModule } from 'tds-ui/badges';

@Component({
  standalone: true,
  imports: [TDSBadgeModule],
})
export class MyComponent {
  unreadCount = 5;
  notifications = 150;
  
  markAsRead() {
    this.unreadCount = 0;
  }
}
```

## Ribbon

**Selector:** `tds-ribbon`
**Export as:** `tdsRibbon`

Hiển thị ribbon góc trên card hoặc container.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `string \| TemplateRef<void>` | `null` | Text hiển thị trên ribbon |
| `color` | `string` | `undefined` | Màu ribbon (hoặc preset color) |
| `placement` | `'start' \| 'end'` | `'end'` | Vị trí ribbon (góc trái/phải) |

```html
<!-- Ribbon basic -->
<tds-ribbon text="SALE" color="red">
  <tds-card>
    <tds-card-content>Product content...</tds-card-content>
  </tds-card>
</tds-ribbon>

<!-- Ribbon placement -->
<tds-ribbon text="NEW" color="green" placement="start">
  <tds-card>
    <tds-card-content>New product...</tds-card-content>
  </tds-card>
</tds-ribbon>

<!-- Preset colors -->
<tds-ribbon text="HOT" color="pink">
  <tds-card>Content...</tds-card>
</tds-ribbon>
```

```typescript
import { TDSBadgeModule } from 'tds-ui/badges';

@Component({
  standalone: true,
  imports: [TDSBadgeModule],
})
export class MyComponent {}
```

## Badge Sup Component

**Selector:** `tds-badge-sup`
**Export as:** `tdsBadgeSup`

Internal component dùng để hiển thị badge count/number với animation.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `count` | `number \| TemplateRef<TDSSafeAny>` | — | Số hiển thị |
| `title` | `string \| null \| undefined` | — | Title attribute |
| `overflowCount` | `number` | `99` | Ngưỡng hiển thị `+` |
| `dot` | `boolean` | `false` | Chỉ hiển thị dot (không số) |
| `offset` | `[number, number]` | — | `[x, y]` offset từ vị trí mặc định |
| `standalone` | `boolean` | `false` | Badge độc lập |
| `size` | `ButtonSize` | `'md'` | Kích thước badge |
| `placement` | `'topLeft' \| 'topRight' \| 'bottomLeft' \| 'bottomRight'` | `'topRight'` | Vị trí badge |
| `tdsStyle` | `{ [key: string]: string } \| null` | `null` | Custom style object |
| `disableAnimation` | `boolean` | `false` | Tắt animation |
| `noAnimation` | `boolean` | `false` | Tắt animation |

## Notes

- Import path là `tds-ui/badges` (số nhiều), không phải `tds-ui/badge`
- `status` dùng khi không bọc component con — chỉ hiển thị dot + text
- `showDot` kiểm soát việc hiển thị dot khi có count
- `standalone = true` khi dùng badge như một component độc lập
- Status types có sẵn: `primary`, `secondary`, `success`, `info`, `processing`, `error`, `warning`
- Animation zoom tự động áp dụng khi count thay đổi
- RTL support tự động khi dùng với `Directionality`
- Ribbon chỉ hiển thị ở góc trên của container
- `ButtonSize` type: `'sm' | 'md' | 'lg' | 'xl'`
- `TDSTheme` type: `'default' | 'light' | 'dark'`
