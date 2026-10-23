# Input Password

Input password với nút toggle ẩn/hiện mật khẩu và nút xóa.

**Selector:** `tds-input-password`
**Import:** `import { TDSInputPasswordModule } from 'tds-ui/input-password';`
**Export as:** `tdsInputPassword`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsPrefix` | `string \| TemplateRef<void> \| undefined` | `undefined` | Nội dung prefix (text hoặc template) |
| `tdsSuffix` | `string \| TemplateRef<void> \| undefined` | `undefined` | Nội dung suffix (text hoặc template) |
| `tdsPrefixIcon` | `string \| null` | `null` | Icon prefix (tên icon từ TDS icon set) |
| `tdsSuffixIcon` | `string \| null` | `null` | Icon suffix (tên icon từ TDS icon set) |
| `tdsAllowClear` | `boolean` | `true` | Hiển thị nút xóa khi có nội dung |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa input |
| `tdsAutoFocus` | `boolean` | `false` | Tự động focus khi component được khởi tạo |
| `tdsShowPassword` | `boolean` | `false` | Hiện/ẩn mật khẩu (toggle) |
| `tdsSize` | `ButtonSize` (`'sm' \| 'md' \| 'lg' \| 'xl'`) | `'md'` | Kích thước input |
| `tdsPlaceHolder` | `string` | `'Tìm kiếm'` | Placeholder text |
| `tdsInputValue` | `string \| null` | `null` | Giá trị input (two-way binding) |
| `tdsInputDebounce` | `number` | `300` | Thời gian debounce (ms) khi nhập |
| `tdsInputEventName` | `string \| null` | `null` | Tên sự kiện custom để lắng nghe (ví dụ: `'change'`, `'keydown'`) |
| `tdsVariant` | `TDSInputVariant` (`'outline' \| 'fill' \| 'flat' \| 'underline'`) | `'outline'` | Kiểu hiển thị |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsInputValueChange` | `EventEmitter<string>` | Phát ra khi giá trị input thay đổi |
| `tdsInputEventTriggered` | `EventEmitter<TDSInputPasswordEventDTO>` | Phát ra khi sự kiện custom được kích hoạt ({ value, event }) |
| `tdsFocusChange` | `EventEmitter<boolean>` | Phát ra khi input thay đổi trạng thái focus |

## Usage

```html
<!-- Basic usage -->
<tds-input-password 
  [(ngModel)]="password"
  [tdsPlaceHolder]="'Nhập mật khẩu'">
</tds-input-password>

<!-- Với ReactiveForm -->
<tds-input-password 
  [formControl]="passwordCtrl"
  [tdsSize]="'lg'"
  [tdsVariant]="'fill'">
</tds-input-password>

<!-- Custom prefix/suffix -->
<tds-input-password 
  [(ngModel)]="password"
  [tdsPrefixIcon]="'tdsi-lock-fill'"
  [tdsAllowClear]="true">
</tds-input-password>

<!-- Disabled -->
<tds-input-password 
  [(ngModel)]="password"
  [tdsDisabled]="true">
</tds-input-password>

<!-- Auto focus -->
<tds-input-password 
  [(ngModel)]="password"
  [tdsAutoFocus]="true">
</tds-input-password>

<!-- Với custom event và debounce -->
<tds-input-password 
  [(ngModel)]="password"
  [tdsInputEventName]="'change'"
  [tdsInputDebounce]="500"
  (tdsInputEventTriggered)="handleCustomEvent($event)">
</tds-input-password>
```

```typescript
import { TDSInputPasswordModule } from 'tds-ui/input-password';

password = '';
passwordCtrl = new FormControl('');

// Xử lý custom event
handleCustomEvent(event: TDSInputPasswordEventDTO) {
  console.log('Value:', event.value);
  console.log('Event:', event.event);
}
```

## Notes

- Mặc định có icon mắt (eye/eye-off) để toggle hiện/ẩn mật khẩu
- Icon prefix mặc định là `tdsi-search-fill` nếu không có prefix/suffix nào được cung cấp
- Nút xóa (clear button) chỉ hiển thị khi có nội dung và `tdsAllowClear = true`
- Hỗ trợ debounce để tối ưu performance khi nhập
- Hỗ trợ nhiều biến thể: outline (mặc định), fill, flat, underline
- Hỗ trợ các kích thước: sm, md (mặc định), lg, xl
- Focus state được theo dõi và phát ra qua `tdsFocusChange`
- Component là standalone, có thể import trực tiếp mà không cần module
