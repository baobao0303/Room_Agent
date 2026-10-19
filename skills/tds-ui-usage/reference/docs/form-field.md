# Form Field

Container bọc input controls, cung cấp label, validation state, error messages, prefix/suffix và add-on.

**Selector:** `tds-form-field`
**Import:** `import { TDSFormFieldModule } from 'tds-ui/form-field';`
**Export as:** `taFormField`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | `InputColor` | `'default'` | Màu viền và trạng thái |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |
| `tdsClass` | `string` | `''` | CSS class thêm vào container |

## Type Definitions

```typescript
type InputColor = 'default' | 'success' | 'warning' | 'error' | 'dark';
type TDSTheme = 'default' | 'light' | 'dark';
type ButtonSize = 'sm' | 'md' | 'lg' | 'xl';
```

## Content Directives

| Directive | Selector | Description |
|-----------|----------|-------------|
| `TDSLabel` | `tds-label` | Label của field, tự thêm `*` nếu required |
| `TDSError` | `tds-error` | Hiển thị khi field có lỗi |
| `TDSSuccess` | `tds-success` | Hiển thị message thành công với icon |
| `TDSWarning` | `tds-warning` | Hiển thị message cảnh báo với icon |
| `TDSHelpMessage` | `tds-help-message` | Hiển thị help message với icon |
| `TDSPrefix` | `[tdsPrefix]` | Icon/text trước input |
| `TDSSuffix` | `[tdsSuffix]` | Icon/text sau input |
| `TDSAddOnLeft` | `[tdsAddOnLeft]` | Add-on ngoài cùng bên trái |
| `TDSAddOnRight` | `[tdsAddOnRight]` | Add-on ngoài cùng bên phải |
| `TDSFormFieldContainer` | `[tds-form-field-container]` | Directive cho form field container |

## Content Child Components

| Component | Type | Description |
|-----------|------|-------------|
| `_control` | `TDSFormFieldControl<any>` | Control bên trong form field (input, select, etc.) |
| `_labelChild` | `TDSLabel` | Label component |
| `_errorChildren` | `QueryList<TDSError>` | List of error messages |
| `_prefixChildren` | `QueryList<TDSPrefix>` | List of prefix elements |
| `_suffixChildren` | `QueryList<TDSSuffix>` | List of suffix elements |
| `_addOnLeftChildren` | `QueryList<TDSAddOnLeft>` | List of left add-ons |
| `_addOnRightChildren` | `QueryList<TDSAddOnRight>` | List of right add-ons |

## Methods

| Method | Return | Description |
|--------|--------|-------------|
| `getConnectedOverlayOrigin()` | `ElementRef` | ElementRef cho element positioning overlay |
| `getLabelId()` | `string \| null` | ID của label element |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `_labelId` | `string` | Unique ID cho label element |
| `_control` | `TDSFormFieldControl<any>` | Reference đến control bên trong |
| `hasRequired` | `boolean` | Kiểm tra field có required validator |

## TDSFormFieldControl Interface

```typescript
abstract class TDSFormFieldControl<T> {
  value: T | null;
  readonly stateChanges: Observable<void>;
  readonly id: string | null;
  readonly placeholder: string | string[];
  readonly ngControl: NgControl | null;
  readonly focused: boolean;
  readonly empty: boolean;
  readonly size: ButtonSize;
  readonly required: boolean;
  readonly disabled: boolean;
  readonly errorState: boolean;
  readonly controlType?: string;
  readonly autofilled?: boolean;
  readonly userAriaDescribedBy?: string;
  
  abstract setDescribedByIds(ids: string[]): void;
  abstract onContainerClick(event: MouseEvent): void;
}
```

## Host Classes

Form field tự động forward các state classes từ control:

| Class | Condition |
|-------|-----------|
| `tds-form-field-default` | `color === 'default' || color === 'dark'` |
| `tds-form-field-success` | `color === 'success'` |
| `tds-form-field-warning` | `color === 'warning'` |
| `tds-form-field-error` | `color === 'error' || _control.errorState` |
| `tds-form-field-focused` | `_control.focused && !_control.disabled` |
| `tds-form-field-invalid` | `_control.errorState` |
| `tds-form-field-disabled` | `_control.disabled` |
| `tds-form-field-autofilled` | `_control.autofilled` |
| `tds-form-field-has-add-on-left` | `_addOnLeftChildren.length > 0` |
| `tds-form-field-has-add-on-right` | `_addOnRightChildren.length > 0` |
| `tds-form-field-has-prefix` | `_prefixChildren.length > 0` |
| `tds-form-field-has-suffix` | `_suffixChildren.length > 0` |
| `tds-form-field-sm` | `size === 'sm'` |
| `tds-form-field-md` | `size === 'md'` |
| `tds-form-field-lg` | `size === 'lg'` |
| `tds-form-field-xl` | `size === 'xl'` |
| `tds-form-field-theme-default` | `tdsTheme === 'default'` |
| `tds-form-field-theme-light` | `tdsTheme === 'light'` |
| `tds-form-field-theme-dark` | `tdsTheme === 'dark'` |
| `ng-untouched` | `_shouldForward('untouched')` |
| `ng-touched` | `_shouldForward('touched')` |
| `ng-pristine` | `_shouldForward('pristine')` |
| `ng-dirty` | `_shouldForward('dirty')` |
| `ng-valid` | `_shouldForward('valid')` |
| `ng-invalid` | `_shouldForward('invalid')` |
| `ng-pending` | `_shouldForward('pending')` |

## Usage

```html
<tds-form-field>
  <tds-label>Tên người dùng</tds-label>
  <span tdsPrefix class="tdsi-user-fill text-gray-400"></span>
  <input tdsInput placeholder="Nhập tên" [formControl]="nameCtrl" />
  @if (nameCtrl.hasError('required')) {
    <tds-error>Bắt buộc</tds-error>
  }
  @if (nameCtrl.hasError('minlength')) {
    <tds-error>Tối thiểu 3 ký tự</tds-error>
  }
</tds-form-field>

<!-- Với add-on -->
<tds-form-field>
  <span tdsAddOnLeft>https://</span>
  <input tdsInput placeholder="example.com" />
  <span tdsAddOnRight>.vn</span>
</tds-form-field>

<!-- Với suffix -->
<tds-form-field>
  <tds-label>Số tiền</tds-label>
  <input tdsInput type="number" />
  <span tdsSuffix>VNĐ</span>
</tds-form-field>

<!-- Với theme -->
<tds-form-field tdsTheme="dark">
  <tds-label>Dark theme</tds-label>
  <input tdsInput />
</tds-form-field>

<!-- Với color state -->
<tds-form-field color="success">
  <tds-label>Success</tds-label>
  <input tdsInput />
</tds-form-field>

<!-- Với multiple errors -->
<tds-form-field>
  <tds-label>Email</tds-label>
  <input tdsInput type="email" [formControl]="emailCtrl" />
  @if (emailCtrl.hasError('required')) {
    <tds-error>Email là bắt buộc</tds-error>
  }
  @if (emailCtrl.hasError('email')) {
    <tds-error>Email không hợp lệ</tds-error>
  }
</tds-form-field>

<!-- Với size -->
<tds-form-field size="lg">
  <tds-label>Large input</tds-label>
  <input tdsInput />
</tds-form-field>
```

```typescript
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSInputModule } from 'tds-ui/tds-input';
import { FormControl, Validators } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSFormFieldModule, TDSInputModule],
})
export class MyComponent {
  nameCtrl = new FormControl('', [Validators.required, Validators.minLength(3)]);
  emailCtrl = new FormControl('', [Validators.required, Validators.email]);
}
```

## Form Field Container Directive

**Selector:** `[tds-form-field-container]`

Directive để đánh dấu container cho form field.

```html
<div tds-form-field-container>
  <tds-form-field>
    <tds-label>Field</tds-label>
    <input tdsInput />
  </tds-form-field>
</div>
```

## Add-On Directives

**Selector:** `[tdsAddOnLeft]`, `[tdsAddOnRight]`

Dùng để thêm add-on ở hai bên ngoài cùng của input.

```html
<tds-form-field>
  <span tdsAddOnLeft>http://</span>
  <input tdsInput />
  <span tdsAddOnRight>.com</span>
</tds-form-field>
```

## Prefix/Suffix Directives

**Selector:** `[tdsPrefix]`, `[tdsSuffix]`

Dùng để thêm icon/text ngay bên trong input (sát với border).

```html
<tds-form-field>
  <span tdsPrefix class="tdsi-search-fill"></span>
  <input tdsInput placeholder="Search..." />
  <span tdsSuffix class="tdsi-close-fill"></span>
</tds-form-field>
```

## Label Directive

**Selector:** `tds-label`

Label cho form field, tự động hiển thị `*` khi field required.

```html
<tds-form-field>
  <tds-label>Username</tds-label>
  <input tdsInput [formControl]="usernameCtrl" />
</tds-form-field>
```

Label component có method `updateRequired(required: boolean)` để cập nhật trạng thái required.

## Error Directive

**Selector:** `tds-error`

Hiển thị error message khi field có lỗi.

```html
<tds-form-field>
  <tds-label>Email</tds-label>
  <input tdsInput [formControl]="emailCtrl" />
  @if (emailCtrl.hasError('required')) {
    <tds-error>Email is required</tds-error>
  }
  @if (emailCtrl.hasError('email')) {
    <tds-error>Invalid email format</tds-error>
  }
</tds-form-field>
```

## Success Component

**Selector:** `tds-success`

Hiển thị success message với icon bên dưới form field.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `string` | auto-generated | ID cho element |
| `icon` | `string \| null` | `'tdsi-success-fill'` | Icon class |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |

```html
<tds-form-field>
  <tds-label>Username</tds-label>
  <input tdsInput [formControl]="usernameCtrl" />
  @if (usernameCtrl.valid && usernameCtrl.value) {
    <tds-success>Username hợp lệ</tds-success>
  }
</tds-form-field>
```

## Warning Component

**Selector:** `tds-warning`

Hiển thị warning message với icon bên dưới form field.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `string` | auto-generated | ID cho element |
| `icon` | `string` | `'tdsi-warning-fill'` | Icon class |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |

```html
<tds-form-field>
  <tds-label>Password</tds-label>
  <input tdsInput type="password" [formControl]="passwordCtrl" />
  @if (passwordCtrl.value && passwordCtrl.value.length < 8) {
    <tds-warning>Mật khẩu nên có ít nhất 8 ký tự</tds-warning>
  }
</tds-form-field>
```

## Help Message Component

**Selector:** `tds-help-message`

Hiển thị help/hint message với icon bên dưới form field.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `string` | auto-generated | ID cho element |
| `icon` | `string \| null` | `'tdsi-info-line'` | Icon class |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |

```html
<tds-form-field>
  <tds-label>API Key</tds-label>
  <input tdsInput [formControl]="apiKeyCtrl" />
  <tds-help-message>API key được tìm thấy trong Settings > Developer</tds-help-message>
</tds-form-field>
```

## Notes

- `tds-form-field` cần có một child thực thi `TDSFormFieldControl` — thường là `tdsInput`, `tds-select`, `tds-date-picker`
- Error chỉ hiển thị khi control ở trạng thái invalid VÀ touched/dirty
- `color="error"` force hiển thị error state mà không cần validator
- Label tự động thêm `*` nếu field required (detect từ Validators)
- Hỗ trợ RTL (right-to-left)
- Hỗ trợ multiple labels
- Hỗ trợ multiple errors
- Forward control state classes đến host element: `ng-untouched`, `ng-touched`, `ng-pristine`, `ng-dirty`, `ng-valid`, `ng-invalid`, `ng-pending`
- `tdsClass` cho phép thêm custom CSS classes
- Import Module vào `imports: []` của standalone component
- Kích thước (`size`) tự động lấy từ control nếu có, mặc định `md`
- `hasRequired` property kiểm tra field có required validator (bao gồm cả custom validators)
- Form field tự động sync aria-describedby với error messages
- Support multiple form fields trong cùng một form
- Support reactive forms và template-driven forms
- Support custom controls implement `TDSFormFieldControl` interface
