# Input Number

Input số với điều khiển tăng/giảm, format số tự động theo locale.

**Selector:** `tds-input-number`
**Import:** `import { TDSInputNumberModule } from 'tds-ui/input-number';`
**Export as:** `tdsInputNumber`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `min` | `number` | `-Infinity` | Giá trị tối thiểu |
| `max` | `number` | `Infinity` | Giá trị tối đa |
| `step` | `number` | `1` | Bước nhảy khi click tăng/giảm |
| `precision` | `number` | `2` | Số chữ số thập phân |
| `size` | `ButtonSize` (`'sm' \| 'md' \| 'lg' \| 'xl'`) | `'md'` | Kích thước |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `placeholder` | `string` | `''` | Placeholder text |
| `defaultValue` | `number \| null` | `null` | Giá trị mặc định khi rỗng |
| `required` | `boolean` | `false` | Bắt buộc nhập |
| `tdsTextAlign` | `'left' \| 'right' \| 'center'` | `'left'` | Căn chỉnh text |
| `tdsBorderless` | `boolean` | `false` | Ẩn viền |
| `hiddenIcon` | `boolean` | `false` | Ẩn icon tăng/giảm |
| `tdsTheme` | `TDSTheme` (`'default' \| 'light' \| 'dark'`) | `'default'` | Theme |
| `decimal` | `TDSDecimal` (`'not-zero' \| 'always' \| 'never'`) | `'not-zero'` | Hiển thị thập phân: `not-zero` (chỉ khi có), `always` (luôn hiển thị), `never` (không hiển thị) |
| `id` | `string \| null` | `null` | HTML id attribute |
| `autoFocus` | `boolean` | `false` | Tự động focus khi component được khởi tạo |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsBlur` | `EventEmitter` | Khi input mất focus |
| `tdsFocus` | `EventEmitter` | Khi input nhận focus |

## Usage

```html
<!-- Basic usage -->
<tds-input-number 
  [(ngModel)]="amount" 
  [min]="0" 
  [max]="1000"
  [step]="10">
</tds-input-number>

<!-- Với ReactiveForm -->
<tds-input-number 
  [formControl]="priceCtrl"
  [min]="0"
  [precision]="2"
  size="lg">
</tds-input-number>

<!-- Decimal handling -->
<tds-input-number 
  [(ngModel)]="price"
  [decimal]="'always'"
  [precision]="2"
  [step]="0.01">
</tds-input-number>

<!-- Borderless, right aligned -->
<tds-input-number 
  [(ngModel)]="quantity"
  [tdsBorderless]="true"
  [tdsTextAlign]="'right'"
  [hiddenIcon]="true">
</tds-input-number>

<!-- Với form-field -->
<tds-form-field>
  <tds-label>Số tiền</tds-label>
  <tds-input-number [(ngModel)]="amount" [min]="0" [precision]="2" />
  <tds-error>Giá trị không hợp lệ</tds-error>
</tds-form-field>
```

```typescript
import { TDSInputNumberModule } from 'tds-ui/input-number';

amount = 0;
priceCtrl = new FormControl(0);

// Keyboard shortcuts
// - Up/Down arrow: tăng/giảm theo step
// - Ctrl/Cmd + Up/Down: tăng/giảm 0.1x step
// - Shift + Up/Down: tăng/giảm 10x step
```

## Notes

- Tự động format số theo locale (đúng thousand separator, decimal separator)
- Hỗ trợ nhập âm nếu `min < 0`
- Validation tự động: không cho nhập giá trị ngoài `min`/`max`
- `decimal='always'`: luôn hiển thị số thập phân (ví dụ: `100.00`)
- `decimal='not-zero'`: chỉ hiển thị khi có phần thập phân (ví dụ: `100.5`, `100`)
- `decimal='never'`: chỉ số nguyên, không cho nhập thập phân
- Trên iOS, tự động đổi `inputMode` thành `'text'` nếu cho phép số âm để hiển thị dấu `-`
- Khi input rỗng và có `min`, giá trị sẽ mặc định là `defaultValue` hoặc `min`
