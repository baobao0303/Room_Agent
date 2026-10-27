# Date Picker

Chọn ngày, tháng, năm hoặc range.

**Import:** `import { TDSDatePickerModule } from 'tds-ui/date-picker';`
**Export as:** `tdsDatePicker`

## Components

Tất cả variant đều dùng chung `TDSDatePickerModule` (duy nhất). Mỗi variant là một Directive wrapper đặt `isRange` hoặc `mode` lên host `TDSDatePickerComponent`.

| Selector | Directive | Mô tả |
|----------|-----------|-------|
| `tds-date-picker` | `TDSDatePickerComponent` | Chọn một ngày |
| `tds-range-picker` | `TDSRangePickerComponent` (set `isRange = true`) | Chọn khoảng ngày |
| `tds-month-picker` | `TDSMonthPickerComponent` (set `mode = 'month'`) | Chọn tháng |
| `tds-week-picker` | `TDSWeekPickerComponent` (set `mode = 'week'`) | Chọn tuần |
| `tds-year-picker` | `TDSYearPickerComponent` (set `mode = 'year'`) | Chọn năm |

Vì tất cả variant là directive wrapper, inputs/outputs đều thuộc host `TDSDatePickerComponent`.

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | `string` | — | Format hiển thị (defaults to locale format when not set) |
| `placeholder` | `string \| string[]` | `''` | Placeholder. Range mode dùng `string[]` 2 phần tử `['Bắt đầu', 'Kết thúc']` |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `allowClear` | `boolean` | `true` | Cho phép xóa |
| `disabledDate` | `DisabledDateFn` | — | Hàm disable ngày |
| `disabledTime` | `DisabledTimeFn` | — | Hàm disable giờ (khi showTime=true) |
| `size` | `ButtonSize` (`'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`) | `'md'` | Kích thước |
| `showToday` | `boolean` | `true` | Hiển thị "Today" button |
| `showNow` | `boolean` | `true` | Hiển thị "Now" button (khi showTime=true) |
| `mode` | `TDSDateMode` (`'date' \| 'month' \| 'year' \| 'decade' \| 'week' \| 'time'`) | `'date'` | Chế độ picker |
| `showTime` | `boolean \| SupportTimeOptions` | `false` | Hiển thị time picker |
| `showWeekNumber` | `boolean` | `false` | Hiển thị số tuần |
| `inline` | `boolean` | `false` | Luôn hiển thị calendar (không popup) |
| `borderless` | `boolean` | `false` | Không hiển thị border input |
| `inputReadOnly` | `boolean` | `false` | Input readonly |
| `autoFocus` | `boolean` | `false` | Auto focus input |
| `tdsShowInput` | `boolean` | `true` | **Range-only.** Ẩn input khi `false`, hiển thị chỉ calendar |
| `suffixIcon` | `string \| TemplateRef` | `'tdsi-calendar-fill'` | Icon suffix |
| `prefixIcon` | `string \| TemplateRef \| null` | `null` | Icon prefix |
| `backdrop` | `boolean` | `false` | Hiển thị backdrop |
| `isOpen` | `boolean \| undefined` | `undefined` | Controlled open state |
| `dropdownClassName` | `string` | — | CSS class cho dropdown |
| `popupStyle` | `object` | — | Inline style cho popup |
| `ranges` | `PresetRanges` | — | Preset ranges (date picker) |
| `monthRanges` | `PresetRanges` | — | Preset month ranges |
| `yearRanges` | `PresetRanges` | — | Preset year ranges |
| `defaultPickerValue` | `CompatibleDate \| null` | `null` | Default value khi mở picker |
| `separator` | `string` | — | **Range-only.** Separator giữa start và end (e.g., `' ~ '`) |
| `renderExtraFooter` | `TemplateRef \| string \| FunctionProp` | — | Custom footer |
| `tdsValidateRangeTime` | `ValidateRangeTimeFn` | — | **Range-only** (khi `tdsShowInput = false`). Validate range time |
| `locale` | `TDSDatePickerI18nInterface` | — | i18n locale |
| `dateRender` | `TemplateRef \| string \| FunctionProp` | — | Custom date cell |
| `required` | `boolean` | `false` | Bắt buộc nhập |
| `id` | `string \| null` | `null` | ID cho component |
| `tdsClass` | `string` | `''` | **@deprecated 2.6.0** — CSS class thêm vào container. Sẽ bị xóa trong phiên bản tới |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `openChange` | `EventEmitter<boolean>` | Khi picker mở/đóng |
| `panelChange` | `EventEmitter<TDSDateMode \| TDSDateMode[] \| string \| string[]>` | Khi chế độ panel thay đổi |
| `calendarChange` | `EventEmitter<Array<Date \| null>>` | Khi giá trị calendar thay đổi |
| `ok` | `EventEmitter<CompatibleDate \| null>` | Khi nhấn OK button |

## Types

```typescript
type TDSDateMode = 'decade' | 'year' | 'month' | 'week' | 'date' | 'time';
type CompatibleDate = Date | Date[];

type DisabledDateFn = (d: Date, start?: Date, end?: Date) => boolean;

type DisabledTimeFn = (
  current: Date | Date[], 
  partial?: 'start' | 'end'
) => DisabledTimeConfig | undefined;

interface DisabledTimeConfig {
  disabledHours(): number[];
  disabledMinutes(hour: number): number[];
  disabledSeconds(hour: number, minute: number): number[];
}

interface SupportTimeOptions {
  format?: string;
  hourStep?: number;
  minuteStep?: number;
  secondStep?: number;
  disabledHours?(): number[];
  disabledMinutes?(hour: number): number[];
  disabledSeconds?(hour: number, minute: number): number[];
  hideDisabledOptions?: boolean;
  defaultOpenValue?: Date;
  addOn?: TemplateRef<void>;
  use12Hours?: boolean;
}

interface PresetRanges {
  [key: string]: Date[] | (() => Date[]);
}

type ValidateRangeTimeFn = (start: Date, end: Date) => string | undefined;
```

## Usage

```html
<!-- Single date -->
<tds-date-picker
  [(ngModel)]="selectedDate"
  format="dd/MM/yyyy"
  placeholder="Chọn ngày">
</tds-date-picker>

<!-- With disabled dates -->
<tds-date-picker
  [(ngModel)]="selectedDate"
  [disabledDate]="disableBeforeToday">
</tds-date-picker>

<!-- Range picker -->
<tds-range-picker
  [(ngModel)]="dateRange"
  format="dd/MM/yyyy">
</tds-range-picker>

<!-- Range picker với placeholder tùy chỉnh -->
<tds-range-picker
  [(ngModel)]="dateRange"
  format="dd/MM/yyyy"
  [placeholder]="['Ngày bắt đầu', 'Ngày kết thúc']">
</tds-range-picker>

<!-- With time picker -->
<tds-date-picker
  [(ngModel)]="selectedDateTime"
  [showTime]="true"
  format="dd/MM/yyyy HH:mm:ss">
</tds-date-picker>

<!-- Month picker -->
<tds-month-picker
  [(ngModel)]="selectedMonth"
  format="MM/yyyy">
</tds-month-picker>

<!-- Year picker -->
<tds-year-picker
  [(ngModel)]="selectedYear"
  format="yyyy">
</tds-year-picker>

<!-- Inline (always open) -->
<tds-date-picker
  [(ngModel)]="selectedDate"
  [inline]="true">
</tds-date-picker>

<!-- Week picker -->
<tds-week-picker
  [(ngModel)]="selectedWeek">
</tds-week-picker>

<!-- Reactive Form -->
<tds-date-picker 
  [formControl]="dateCtrl">
</tds-date-picker>

<!-- With custom ranges -->
<tds-range-picker
  [(ngModel)]="dateRange"
  [ranges]="customRanges">
</tds-range-picker>
```

```typescript
import { TDSDatePickerModule } from 'tds-ui/date-picker';
import { FormsModule, ReactiveFormsModule, FormControl } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSDatePickerModule, FormsModule, ReactiveFormsModule]
})
export class MyComponent {
  selectedDate: Date | null = null;
  selectedDateTime: Date | null = null;
  dateRange: [Date | null, Date | null] = [null, null];
  selectedMonth: Date | null = null;
  selectedYear: Date | null = null;
  selectedWeek: Date | null = null;
  dateCtrl = new FormControl(null);
  
  disableBeforeToday = (date: Date) => {
    const today = new Date();
    return date < today;
  };

  customRanges = {
    'Hôm nay': [new Date(), new Date()],
    '7 ngày qua': [
      new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      new Date()
    ],
    '30 ngày qua': [
      new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      new Date()
    ]
  };
}
```

## Notes

- `format` tuân theo Angular DatePipe format (e.g., `dd/MM/yyyy`, `yyyy-MM-dd`, `dd/MM/yyyy HH:mm`)
- `inline="true"` để luôn hiển thị calendar mà không cần popup
- `showTime=true` để chọn cả giờ phút giây
- `showTime` có thể nhận object `SupportTimeOptions` để cấu hình chi tiết
- Range picker tự động nhận mảng `[startDate, endDate]`. Type: `[Date | null, Date | null]`
- `suffixIcon` có thể là icon name hoặc TemplateRef
- Các preset ranges (`ranges`, `monthRanges`, `yearRanges`) giúp chọn nhanh
- `disabledDate` nhận function trả về `true` để disable ngày
- `disabledTime` dùng để disable giờ/phút/giây cụ thể
- `tdsValidateRangeTime` để custom validation cho range time
- `tdsShowInput="false"` để ẩn input trong range picker mode
- `separator` để custom separator giữa start và end date
- `dateRender` để custom render date cell
- Import Module vào `imports: []` của standalone component
- Hỗ trợ Reactive Forms và Template-driven Forms
- Dùng bên trong `tds-form-field` cho layout đồng bộ
