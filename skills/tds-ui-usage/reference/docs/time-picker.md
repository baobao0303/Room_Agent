# Time Picker

Component chọn giờ với hỗ trợ format, validation, và disabled options.

**Selector:** `tds-time-picker`
**Import:** `import { TDSTimePickerModule } from 'tds-ui/time-picker';`
**Export as:** `tdsTimePicker`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | `TDSTimeFormat` | `'HH:mm'` | Format hiển thị thời gian (HH:mm, HH:mm:ss) |
| `placeholder` | `string` | `'HH:mm'` | Placeholder cho input |
| `size` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `disabled` | `boolean` | `false` | Vô hiệu hóa component |
| `allowEmpty` | `boolean` | `true` | Cho phép xóa giá trị |
| `autoFocus` | `boolean` | `false` | Auto focus input |
| `hourStep` | `number` | `1` | Bước nhảy giờ |
| `minuteStep` | `number` | `1` | Bước nhảy phút |
| `secondStep` | `number` | `1` | Bước nhảy giây |
| `disabledHours` | `() => number[]` | — | Hàm trả về mảng giờ bị disable |
| `disabledMinutes` | `(hour: number) => number[]` | — | Hàm trả về mảng phút bị disable theo giờ |
| `disabledSeconds` | `(hour: number, minute: number) => number[]` | — | Hàm trả về mảng giây bị disable theo giờ, phút |
| `hideDisabledOptions` | `boolean` | `false` | Ẩn các option bị disable |
| `use12Hours` | `boolean` | `false` | Sử dụng định dạng 12 giờ (deprecated từ ver 2.7.0) |
| `defaultOpenValue` | `Date` | — | Giá trị mặc định khi mở picker |
| `popupClassName` | `string` | — | CSS class cho dropdown |
| `suffixIcon` | `string \| TemplateRef` | `'tdsi-time-line'` | Icon suffix |
| `addOn` | `TemplateRef<void>` | — | Template add-on bên dưới panel |
| `clearText` | `string` | `'clear'` | Text cho nút clear |
| `nowText` | `string` | — | Text cho nút Now |
| `okText` | `string` | — | Text cho nút OK |
| `backdrop` | `boolean` | `false` | Hiển thị backdrop |
| `isOpen` | `boolean` | `false` | Controlled open state |
| `tdsId` | `string \| null` | `null` | ID cho component |
| `id` | `string \| null` | `null` | ID cho component (alias, set trên host element) |
| `required` | `boolean` | `false` | Bắt buộc nhập (tích hợp với form-field validation) |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `openChange` | `EventEmitter<boolean>` | Khi picker mở/đóng |

## Usage

```html
<!-- Basic time picker -->
<tds-time-picker
  [(ngModel)]="selectedTime"
  format="HH:mm">
</tds-time-picker>

<!-- With seconds -->
<tds-time-picker
  [(ngModel)]="selectedTime"
  format="HH:mm:ss">
</tds-time-picker>

<!-- Disabled hours and minutes -->
<tds-time-picker
  [(ngModel)]="selectedTime"
  [disabledHours]="disabledHours"
  [disabledMinutes]="disabledMinutes">
</tds-time-picker>

<!-- Size variants -->
<tds-time-picker size="sm"></tds-time-picker>
<tds-time-picker size="md"></tds-time-picker>
<tds-time-picker size="lg"></tds-time-picker>

<!-- Disabled state -->
<tds-time-picker
  [(ngModel)]="selectedTime"
  [disabled]="true">
</tds-time-picker>

<!-- With custom steps -->
<tds-time-picker
  [(ngModel)]="selectedTime"
  [hourStep]="2"
  [minuteStep]="15"
  [secondStep]="30">
</tds-time-picker>

<!-- Reactive Form -->
<tds-time-picker
  [formControl]="timeCtrl">
</tds-time-picker>
```

```typescript
import { TDSTimePickerModule } from 'tds-ui/time-picker';
import { FormsModule, ReactiveFormsModule, FormControl } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSTimePickerModule, FormsModule, ReactiveFormsModule]
})
export class MyComponent {
  selectedTime: Date | null = null;
  timeCtrl = new FormControl(null);

  // Disable hours before 8 AM and after 8 PM
  disabledHours(): number[] {
    return [...Array(8).keys(), ...Array(4).keys().map(i => i + 20)];
  }

  // Disable minutes 0-29 for each hour
  disabledMinutes(hour: number): number[] {
    return [...Array(30).keys()];
  }
}
```

## Notes

- Component sử dụng `Date` type cho giá trị
- Input có mask tự động theo format (VD: `HH:mm` → `HH:mm`)
- Hỗ trợ keyboard navigation (Enter để xác nhận, Escape để hủy)
- `use12Hours` đã bị deprecated từ version 2.7.0
- Tự động đóng khi click outside
- Hỗ trợ RTL (right-to-left)
- Có thể dùng với `tds-form-field` để hiển thị error state
- Format tuân theo date-fns format
