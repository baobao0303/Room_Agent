# Calendar

Component lịch đa chế độ (ngày, tuần, tháng, năm) với hỗ trợ sự kiện.

**Selector:** `tds-calendar`
**Export as:** `tdsCalendar`
**Import:** `import { TDSCalendarModule } from 'tds-ui/calendar';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsMode` | `'date' \| 'week' \| 'month' \| 'year'` | `'month'` | Chế độ hiển thị |
| `tdsValue` | `Date` | `undefined` | Ngày được chọn |
| `tdsDisabledDate` | `(date: Date) => boolean` | `undefined` | Disable ngày cụ thể |
| `locale` | `TDSCalendarI18nInterface` | - | Cấu hình ngôn ngữ |
| `tdsFullscreen` | `boolean` | `true` | Hiển thị fullscreen |
| `weekStartsOn` | `WeekDayIndex` | `1` | Ngày bắt đầu tuần (0=Chủ nhật, 1=Thứ 2) |
| **Date Mode** | | | |
| `tdsTypeArrange` | `'stack' \| 'timeline'` | `'stack'` | Kiểu sắp xếp |
| `tdsTypeGroup` | `'personal' \| 'group'` | `'personal'` | Loại nhóm |
| `tdsTimeDirection` | `'horizontal' \| 'vertical'` | `'vertical'` | Hướng thời gian |
| `tdsDayStartHour` | `number` | `8` | Giờ bắt đầu (0-23) |
| `tdsDayStartMinute` | `number` | `0` | Phút bắt đầu (0-59) |
| `tdsDayEndHour` | `number` | `17` | Giờ kết thúc (0-23) |
| `tdsDayEndMinute` | `number` | `30` | Phút kết thúc (0-59) |
| `tdsHourSegments` | `number` | `4` | Số segment mỗi giờ |
| `tdsHourSegmentHeight` | `number` | `30` | Chiều cao mỗi segment (px) |
| `tdsHourSegmentWidth` | `number` | `200` | Chiều rộng mỗi segment (px) |
| `tdsHourDuration` | `number` | `60` | Thời lượng mỗi segment (phút) |
| `tdsWidthColTime` | `number` | `64` | Chiều rộng cột thời gian (px) |
| `tdsMinimumEventHeight` | `number` | `100` | Chiều cao tối thiểu sự kiện (px) |
| `tdsCurrentTimeMarkerTemplate` | `TemplateRef<any>` | - | Template marker thời gian hiện tại |
| **Templates** | | | |
| `tdsDateCell` | `TemplateRef<Date>` | - | Template cell ngày |
| `tdsDateFullCell` | `TemplateRef<Date>` | - | Template full cell ngày |
| `tdsMonthCell` | `TemplateRef<Date>` | - | Template cell tháng |
| `tdsMonthFullCell` | `TemplateRef<Date>` | - | Template full cell tháng |

## Key Outputs

Calendar sử dụng `ControlValueAccessor`, dùng với `[(ngModel)]` hoặc `[formControl]`.

| Output | Type | Description |
|--------|------|-------------|
| `tdsModeChange` | `EventEmitter<TDSCalendarMode>` | Khi thay đổi chế độ |
| `tdsPanelChange` | `EventEmitter<{ date: Date; mode: TDSCalendarMode }>` | Khi panel thay đổi |
| `tdsSelectChange` | `EventEmitter<Date>` | Khi chọn ngày |
| `tdsValueChange` | `EventEmitter<Date>` | Khi value thay đổi |
| `tdsSelectHour` | `EventEmitter<WeekViewHourSegment>` | Khi chọn segment giờ |

## Usage

```html
<!-- Cơ bản - Month mode -->
<tds-calendar 
  [(ngModel)]="selectedDate"
  [locale]="locale">
</tds-calendar>

<!-- Week mode -->
<tds-calendar 
  [(ngModel)]="selectedDate"
  tdsMode="week"
  [locale]="locale">
</tds-calendar>

<!-- Day mode với events -->
<tds-calendar 
  [(ngModel)]="selectedDate"
  tdsMode="date"
  [tdsDayStartHour]="8"
  [tdsDayEndHour]="18"
  [tdsHourSegments]="4"
  [locale]="locale">
  <tds-calendar-event 
    [tdsStartDate]="eventStart"
    [tdsEndDate]="eventEnd"
    [tdsData]="eventData">
  </tds-calendar-event>
</tds-calendar>

<!-- Year mode -->
<tds-calendar 
  [(ngModel)]="selectedDate"
  tdsMode="year"
  [locale]="locale">
</tds-calendar>

<!-- Với custom template -->
<tds-calendar 
  [(ngModel)]="selectedDate"
  [locale]="locale">
  <ng-template #dateCell let-date>
    <div class="custom-date">{{ date | date:'d' }}</div>
  </ng-template>
</tds-calendar>
```

```typescript
import { TDSCalendarModule } from 'tds-ui/calendar';
import { TDSCalendarI18nInterface } from 'tds-ui/i18n';
import { FormControl } from '@angular/forms';

selectedDate = new Date();

// Cấu hình locale
locale: TDSCalendarI18nInterface = {
  // Cấu hình ngôn ngữ theo yêu cầu
};

// Event data
eventStart = new Date('2026-04-15T10:00:00');
eventEnd = new Date('2026-04-15T11:30:00');
eventData = { title: 'Meeting', type: 'work' };

// Reactive form
dateCtrl = new FormControl(new Date());
```

## Notes

- Dùng `[(ngModel)]` hoặc `[formControl]` để bind value
- `tdsMode`:
  - `'date'`: Lịch ngày với timeline và events
  - `'week'`: Lịch tuần
  - `'month'`: Lịch tháng (mặc định)
  - `'year'`: Lịch năm
- `weekStartsOn`: 0 = Chủ nhật, 1 = Thứ 2, ..., 6 = Thứ 7
- Date mode (`tdsMode="date"`) hỗ trợ:
  - Custom giờ bắt đầu/kết thúc ngày
  - Custom số segment mỗi giờ
  - Custom chiều cao/rộng segment
  - Hiển thị events trong ngày
- Sử dụng `<tds-calendar-event>` để thêm events vào calendar
- Hỗ trợ RTL (right-to-left)
- Có thể custom cell templates cho các mode khác nhau
- `tdsFullscreen`="false" cho hiển thị mini
