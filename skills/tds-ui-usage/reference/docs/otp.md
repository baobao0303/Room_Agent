# OTP Input

Input cho OTP (One-Time Password) với nhiều ô nhập liệu. Hỗ trợ auto-focus, paste, và validation.

**Selector:** `tds-otp-input`
**Import:** `import { TDSOtpInputModule } from 'tds-ui/otp';`
**Export as:** `tdsOtpInput`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsValue` | `string` | `''` | Giá trị OTP |
| `tdsAllowNumbersOnly` | `boolean` | `true` | Chỉ cho phép nhập số |
| `tdsIsPasswordInput` | `boolean` | `false` | Hiển thị dưới dạng password |
| `tdsPlaceholder` | `string` | `''` | Placeholder text |
| `tdsDisableAutoFocus` | `boolean` | `false` | Tắt auto-focus vào ô đầu tiên |
| `tdsOtpLength` | `number` | `6` | Số lượng ô nhập liệu |
| `tdsLetterCase` | `'upper' \| 'lower'` | `'upper'` | Viết hoa hay thường (khi không cho phép số only) |
| `tdsError` | `boolean` | `false` | Hiển thị trạng thái lỗi |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa input |
| `formCtrl` | `FormControl` | — | FormControl để bind với Reactive Forms |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsInputChange` | `EventEmitter<string>` | Emit khi giá trị OTP thay đổi |
| `tdsErrorChange` | `EventEmitter<boolean>` | Emit khi trạng thái lỗi thay đổi |

## Usage

```html
<!-- Basic OTP input -->
<tds-otp-input
  (tdsInputChange)="onOtpChange($event)"
  [tdsOtpLength]="6">
</tds-otp-input>

<!-- With form control -->
<tds-otp-input
  [formCtrl]="otpControl"
  [tdsOtpLength]="4"
  (tdsInputChange)="verifyOtp($event)">
</tds-otp-input>

<!-- Allow letters only -->
<tds-otp-input
  [tdsAllowNumbersOnly]="false"
  [tdsLetterCase]="'upper'"
  [tdsOtpLength]="4">
</tds-otp-input>

<!-- Password mode -->
<tds-otp-input
  [tdsIsPasswordInput]="true"
  [tdsOtpLength]="6">
</tds-otp-input>

<!-- With error state -->
<tds-otp-input
  [tdsError]="isInvalid"
  [tdsOtpLength]="6"
  (tdsInputChange)="validateOtp($event)">
</tds-otp-input>

<!-- Disabled -->
<tds-otp-input
  [tdsDisabled]="true"
  [tdsOtpLength]="6">
</tds-otp-input>
```

```typescript
import { TDSOtpInputModule } from 'tds-ui/otp';
import { FormControl } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSOtpInputModule],
})
export class MyComponent {
  otpControl = new FormControl('');

  onOtpChange(value: string) {
    console.log('OTP:', value);
    if (value.length === 6) {
      this.verifyOtp(value);
    }
  }

  verifyOtp(otp: string) {
    // Verify OTP logic
  }

  validateOtp(otp: string) {
    // Validation logic
  }
}
```

## Notes

- Component standalone, có thể import trực tiếp mà không cần module
- Auto-focus vào ô đầu tiên khi mount (có thể tắt bằng `tdsDisableAutoFocus`)
- Hỗ trợ paste OTP (Ctrl+V) - tự động điền vào các ô
- Hỗ trợ keyboard navigation:
  - Arrow keys: di chuyển giữa các ô
  - Backspace/Delete: xóa và quay lại ô trước
  - Spacebar: bị chặn
- Tự động chuyển sang ô tiếp theo sau khi nhập
- Tự động chuyển sang chữ hoa/thường khi `tdsAllowNumbersOnly = false`
- Validate số khi `tdsAllowNumbersOnly = true`
- Error state: hiển thị khi click outside mà chưa nhập đủ OTP
- Hỗ trợ Reactive Forms với `formCtrl`
- Hỗ trợ 3 theme: default, light, dark
- Input type tự động:
  - `password` khi `tdsIsPasswordInput = true`
  - `tel` khi `tdsAllowNumbersOnly = true` (tốt cho mobile)
  - `text` cho trường hợp khác
