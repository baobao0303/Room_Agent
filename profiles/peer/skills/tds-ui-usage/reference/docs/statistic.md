# Statistic

Component hiển thị số liệu thống kê với giá trị, prefix, suffix và title. Hỗ trợ countdown timer và custom value formatting.

**Selector:** `tds-statistic`
**Export as:** `tdsStatistic`
**Import:** `import { TDSStatisticModule } from 'tds-ui/statistic';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsPrefix` | `string \| TemplateRef<void>` | — | Prefix hiển thị trước giá trị |
| `tdsSuffix` | `string \| TemplateRef<void>` | — | Suffix hiển thị sau giá trị |
| `tdsTitle` | `string \| TemplateRef<void>` | — | Tiêu đề của statistic |
| `tdsValue` | `number \| string` | — | Giá trị hiển thị |
| `tdsValueStyle` | `NgStyleInterface` | `{}` | Custom style cho giá trị |
| `tdsValueTemplate` | `TemplateRef<{ $implicit: number \| string }>` | — | Custom template cho giá trị |

## Statistic Number

**Selector:** `tds-statistic-number`
**Export as:** `tdsStatisticNumber`

Component con hiển thị giá trị số với formatting tự động.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsValue` | `number \| string` | — | Giá trị hiển thị |
| `tdsValueTemplate` | `TemplateRef<{ $implicit: number \| string }>` | — | Custom template cho giá trị |

## Countdown

**Selector:** `tds-countdown`
**Export as:** `tdsCountdown`

Component đếm ngược thời gian. Kế thừa tất cả inputs từ `TDSStatisticComponent` (`tdsPrefix`, `tdsSuffix`, `tdsTitle`, `tdsValueStyle`, `tdsValueTemplate`) và thêm:

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsValue` | `number` | — | Timestamp target để đếm ngược (ms) |
| `tdsFormat` | `string` | `'HH:mm:ss'` | Format hiển thị thời gian |

**Output:**

| Output | Type | Description |
|--------|------|-------------|
| `tdsCountdownFinish` | `EventEmitter<void>` | Phát ra khi countdown kết thúc |

## Usage

```html
<!-- Basic statistic -->
<tds-statistic
  [tdsTitle]="'Active Users'"
  [tdsValue]="11280">
</tds-statistic>

<!-- With prefix and suffix -->
<tds-statistic
  [tdsTitle]="'Revenue'"
  [tdsPrefix]="'$'"
  [tdsSuffix]="'USD'"
  [tdsValue]="12500">
</tds-statistic>

<!-- With string value -->
<tds-statistic
  [tdsTitle]="'Account Balance'"
  [tdsPrefix]="'$'"
  [tdsValue]="'12,345.67'">
</tds-statistic>

<!-- With custom value style -->
<tds-statistic
  [tdsTitle]="'Growth Rate'"
  [tdsValue]="23.5"
  [tdsSuffix]="'%'"
  [tdsValueStyle]="{ color: '#3f8600' }">
</tds-statistic>

<!-- With custom value template -->
<tds-statistic
  [tdsTitle]="'Feedback'"
  [tdsValue]="feedbackCount"
  [tdsValueTemplate]="feedbackTemplate">
</tds-statistic>

<ng-template #feedbackTemplate let-value>
  <span class="feedback-value">
    {{ value }}
    <span class="icon">★</span>
  </span>
</ng-template>

<!-- Countdown -->
<tds-countdown
  [tdsTitle]="'Countdown'"
  [tdsValue]="targetTime"
  [tdsFormat]="'HH:mm:ss'">
</tds-countdown>

<!-- Countdown with custom format -->
<tds-countdown
  [tdsTitle]="'Sale Ends In'"
  [tdsValue]="saleEndTime"
  [tdsFormat]="'D days HH:mm:ss'">
</tds-countdown>

<!-- Countdown with finish event -->
<tds-countdown
  [tdsTitle]="'Event Countdown'"
  [tdsValue]="eventStartTime"
  (tdsCountdownFinish)="onCountdownFinish()">
</tds-countdown>

<!-- Multiple statistics -->
<div class="statistics-grid">
  <tds-statistic
    [tdsTitle]="'Total Users'"
    [tdsValue]="totalUsers">
  </tds-statistic>
  <tds-statistic
    [tdsTitle]="'Active Now'"
    [tdsValue]="activeUsers"
    [tdsValueStyle]="{ color: '#1890ff' }">
  </tds-statistic>
  <tds-statistic
    [tdsTitle]="'New Today'"
    [tdsValue]="newUsers"
    [tdsValueStyle]="{ color: '#52c41a' }">
  </tds-statistic>
</div>
```

```typescript
import { TDSStatisticModule } from 'tds-ui/statistic';

@Component({
  standalone: true,
  imports: [TDSStatisticModule]
})
export class MyComponent {
  totalUsers = 11280;
  activeUsers = 5432;
  newUsers = 128;
  feedbackCount = 4.5;

  // Target time for countdown (timestamp in milliseconds)
  targetTime = Date.now() + 86400000; // 24 hours from now
  saleEndTime = Date.now() + 172800000; // 48 hours from now
  eventStartTime = Date.now() + 3600000; // 1 hour from now

  onCountdownFinish() {
    console.log('Countdown finished!');
    // Handle countdown finish event
  }
}
```

## Custom Value Formatting

```html
<!-- Decimal places -->
<tds-statistic
  [tdsTitle]="'Precision'"
  [tdsValue]="3.14159265">
</tds-statistic>
<!-- Displays: 3.14159265 -->

<!-- Using string for custom formatting -->
<tds-statistic
  [tdsTitle]="'Custom Format'"
  [tdsValue]="'1,234,567.89'">
</tds-statistic>
<!-- Displays: 1,234,567.89 -->

<!-- With prefix/suffix templates -->
<tds-statistic
  [tdsTitle]="'Price'"
  [tdsValue]="99.99"
  [tdsPrefix]="prefixTemplate"
  [tdsSuffix]="suffixTemplate">
</tds-statistic>

<ng-template #prefixTemplate>
  <span class="currency-symbol">$</span>
</ng-template>

<ng-template #suffixTemplate>
  <span class="currency-code">USD</span>
</ng-template>
```

## Countdown Examples

```html
<!-- Basic countdown to specific date -->
<tds-countdown
  [tdsTitle]="'New Year Countdown'"
  [tdsValue]="newYearTime">
</tds-countdown>

<!-- Countdown with days -->
<tds-countdown
  [tdsTitle]="'Offer Expires In'"
  [tdsValue]="offerExpiry"
  [tdsFormat]="'D days HH hours mm minutes'">
</tds-countdown>

<!-- Short format -->
<tds-countdown
  [tdsTitle]="'Quick Timer'"
  [tdsValue]="timerEnd"
  [tdsFormat]="'mm:ss'">
</tds-countdown>

<!-- Countdown with action on finish -->
<tds-countdown
  [tdsTitle]="'Flash Sale'"
  [tdsValue]="flashSaleEnd"
  (tdsCountdownFinish)="redirectToList()">
</tds-countdown>
```

```typescript
@Component({
  // ...
})
export class SaleComponent {
  newYearTime = new Date('2025-01-01T00:00:00').getTime();
  offerExpiry = Date.now() + 7 * 24 * 60 * 60 * 1000; // 7 days
  timerEnd = Date.now() + 5 * 60 * 1000; // 5 minutes
  flashSaleEnd = Date.now() + 60 * 60 * 1000; // 1 hour

  redirectToList() {
    // Redirect to sale list page
    this.router.navigate(['/sales']);
  }
}
```

## Statistic Card Integration

```html
<tds-card [tdsBordered]="true">
  <tds-card-content>
    <tds-row [tdsGutter]="16">
      <tds-col [tdsSpan]="6">
        <tds-statistic
          [tdsTitle]="'Total Revenue'"
          [tdsPrefix]="'$'"
          [tdsValue]="totalRevenue">
        </tds-statistic>
      </tds-col>
      <tds-col [tdsSpan]="6">
        <tds-statistic
          [tdsTitle]="'Orders'"
          [tdsValue]="totalOrders">
        </tds-statistic>
      </tds-col>
      <tds-col [tdsSpan]="6">
        <tds-statistic
          [tdsTitle]="'Conversion Rate'"
          [tdsValue]="conversionRate"
          [tdsSuffix]="'%'"
          [tdsValueStyle]="{ color: '#cf1322' }">
        </tds-statistic>
      </tds-col>
      <tds-col [tdsSpan]="6">
        <tds-statistic
          [tdsTitle]="'Time Remaining'"
          [tdsValue]="countdownTime"
          [tdsValueTemplate]="countdownTemplate">
        </tds-statistic>
      </tds-col>
    </tds-row>
  </tds-card-content>
</tds-card>

<ng-template #countdownTemplate let-value>
  <tds-countdown [tdsValue]="value"></tds-countdown>
</ng-template>
```

## Notes

- `tdsValue` có thể là `number` hoặc `string`
- Khi `tdsValue` là `number`, component tự động tách phần nguyên và thập phân
- Khi `tdsValue` là `string`, component sử dụng locale decimal separator để tách phần
- `tdsValueStyle` cho phép custom CSS style cho giá trị (màu sắc, font size, etc.)
- `tdsValueTemplate` cho phép hoàn toàn custom cách hiển thị giá trị
- `tdsPrefix` và `tdsSuffix` có thể là string hoặc TemplateRef
- Countdown component tự động update mỗi ~33ms (30fps)
- Countdown tự động dừng khi đạt target time và phát `tdsCountdownFinish` event
- Countdown format hỗ trợ: `H` (hours), `m` (minutes), `s` (seconds), `S` (milliseconds)
- `tdsFormat` trong countdown sử dụng pipe `tdsTimeRange` để format thời gian
- Component hỗ trợ RTL (right-to-left)
- Countdown chỉ chạy trên browser (kiểm tra `platform.isBrowser`)
- Countdown sử dụng `ngZone.runOutsideAngular` để optimize performance

## Value Display

Giá trị số được tự động chia thành 2 phần:
- **Int part**: Phần nguyên số
- **Decimal part**: Phần thập phân (nếu có)

Ví dụ:
- `12345.67` → Int: `12345`, Decimal: `.67`
- `12345` → Int: `12345`, Decimal: `` (rỗng)

Điều này cho phép styling riêng cho phần nguyên và thập phân nếu cần.
