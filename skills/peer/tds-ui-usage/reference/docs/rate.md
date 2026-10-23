# Rate

Component đánh giá bằng sao, hỗ trợ half-star và tùy chỉnh.

**Selector:** `tds-rate`
**Import:** `import { TDSRateModule } from 'tds-ui/rate';`
**Export as:** `tdsRate`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `allowClear` | `boolean` | `true` | Cho phép xóa đánh giá khi click lại |
| `allowHalf` | `boolean` | `false` | Cho phép đánh giá nửa sao |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `autoFocus` | `boolean` | `false` | Tự động focus khi init |
| `character` | `TemplateRef<{}>` | `undefined` | Template tùy chỉnh cho sao |
| `count` | `number` | `5` | Số lượng sao |
| `tooltips` | `string[]` | `[]` | Tooltip cho mỗi sao |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước |

## Key Outputs

Rate sử dụng `ControlValueAccessor`, dùng với `[(ngModel)]` hoặc `[formControl]`.

| Output | Type | Description |
|--------|------|-------------|
| `tdsOnBlur` | `EventEmitter<FocusEvent>` | Khi mất focus |
| `tdsOnFocus` | `EventEmitter<FocusEvent>` | Khi được focus |
| `tdsOnHoverChange` | `EventEmitter<number>` | Khi hover qua sao |
| `tdsOnKeyDown` | `EventEmitter<KeyboardEvent>` | Khi nhấn phím |

## Usage

```html
<!-- Cơ bản -->
<tds-rate [(ngModel)]="rating"></tds-rate>

<!-- Cho phép half-star -->
<tds-rate 
  [(ngModel)]="rating"
  [allowHalf]="true">
</tds-rate>

<!-- Với số sao tùy chỉnh -->
<tds-rate 
  [(ngModel)]="rating"
  [count]="10">
</tds-rate>

<!-- Với tooltips -->
<tds-rate 
  [(ngModel)]="rating"
  [tooltips]="['Rất tệ', 'Tệ', 'Bình thường', 'Tốt', 'Rất tốt']">
</tds-rate>

<!-- Không cho phép xóa -->
<tds-rate 
  [(ngModel)]="rating"
  [allowClear]="false">
</tds-rate>

<!-- Disabled -->
<tds-rate 
  [(ngModel)]="rating"
  [disabled]="true">
</tds-rate>

<!-- Với kích thước -->
<tds-rate 
  [(ngModel)]="rating"
  size="lg">
</tds-rate>
```

```typescript
import { TDSRateModule } from 'tds-ui/rate';
import { FormControl } from '@angular/forms';

rating = 3;

// Reactive form
ratingCtrl = new FormControl(0);
```

## Notes

- Dùng `[(ngModel)]` hoặc `[formControl]` để bind value
- Value là số (float nếu `allowHalf="true"`)
- `allowClear="true"` cho phép click lại để reset về 0
- `allowHalf="true"` cho phép đánh giá 0.5, 1.5, 2.5, etc.
- Hỗ trợ keyboard navigation (mũi tên trái/phải)
- Hỗ trợ RTL (right-to-left)
- `size` hỗ trợ `'xs'`, `'sm'`, `'md'`, `'lg'`, `'xl'`
- `tooltips` là mảng string với độ dài bằng `count`
- `character` cho phép custom icon/template thay vì sao mặc định
