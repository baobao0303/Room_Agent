# Slider

Thanh trượt để chọn giá trị trong một khoảng số, hỗ trợ single hoặc range.

**Selector:** `tds-slider`
**Import:** `import { TDSSliderModule } from 'tds-ui/slider';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa slider |
| `tdsDots` | `boolean` | `false` | Hiển thị dots tại các step |
| `tdsIncluded` | `boolean` | `true` | Hiển thị track giữa các handle |
| `tdsRange` | `boolean` | `false` | Mode range (2 handles) |
| `tdsVertical` | `boolean` | `false` | Hiển thị dọc |
| `tdsReverse` | `boolean` | `false` | Đảo ngược hướng |
| `tdsDefaultValue` | `number \| number[]` | `undefined` | Giá trị mặc định |
| `tdsMarks` | `TDSMarks` | `null` | Các mốc đánh dấu |
| `tdsMax` | `number` | `100` | Giá trị tối đa |
| `tdsMin` | `number` | `0` | Giá trị tối thiểu |
| `tdsStep` | `number` | `1` | Bước nhảy |
| `tdsTooltipVisible` | `'always' \| 'never' \| 'default'` | `'default'` | Khi nào hiển thị tooltip |
| `tdsTooltipPlacement` | `string` | `'top'` | Vị trí tooltip |
| `tdsTipFormatter` | `(value: number) => string` | `null` | Format tooltip content |

## Key Outputs

Slider sử dụng `ControlValueAccessor`, dùng với `[(ngModel)]` hoặc `[formControl]`.

| Output | Type | Description |
|--------|------|-------------|
| `tdsOnAfterChange` | `EventEmitter<TDSSliderValue>` | Phát sinh khi kết thúc drag/slide |

## Usage

```html
<!-- Cơ bản -->
<tds-slider [(ngModel)]="value"></tds-slider>

<!-- Với min, max, step -->
<tds-slider 
  [(ngModel)]="value"
  [tdsMin]="0"
  [tdsMax]="100"
  [tdsStep]="5">
</tds-slider>

<!-- Range slider -->
<tds-slider 
  [(ngModel)]="rangeValue"
  [tdsRange]="true">
</tds-slider>

<!-- Với marks -->
<tds-slider 
  [(ngModel)]="value"
  [tdsMarks]="marks">
</tds-slider>

<!-- Vertical -->
<tds-slider 
  [(ngModel)]="value"
  [tdsVertical]="true">
</tds-slider>

<!-- Với tooltip formatter -->
<tds-slider 
  [(ngModel)]="value"
  [tdsTipFormatter]="formatTooltip">
</tds-slider>
```

```typescript
import { TDSSliderModule } from 'tds-ui/slider';
import { FormControl } from '@angular/forms';

value = 50;
rangeValue = [20, 80];
marks = {
  0: '0%',
  25: '25%',
  50: '50%',
  75: '75%',
  100: '100%'
};

formatTooltip(value: number): string {
  return `${value}%`;
}
```

## Notes

- Dùng `[(ngModel)]` hoặc `[formControl]` để bind value
- `tdsRange="true"` cho phép chọn khoảng giá trị (2 handles)
- `tdsMarks` là object với key là số (position) và value là string (label) hoặc object `{ style, label }`
- `tdsTooltipVisible`:
  - `'default'`: Hiển thị khi hover/drag
  - `'always'`: Luôn hiển thị
  - `'never'`: Không hiển thị
- Hỗ trợ keyboard navigation (mũi tên trái/phải hoặc lên/xuống)
- Hỗ trợ RTL (right-to-left)
- `tdsDots="true"` hiển thị dots tại mỗi step
