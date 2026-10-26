# Form với Validation

## Use case
Tạo form có validate dữ liệu, hiện error message khi nhập sai, disable button khi đang submit.

## Components cần import
```typescript
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSButtonModule } from 'tds-ui/button';
import { TDSInputModule } from 'tds-ui/tds-input';
```

## Code example

### Template
```html
<form [formGroup]="form" (ngSubmit)="onSubmit()">
  <tds-form-field>
    <tds-label>Tên</tds-label>
    <input tdsInput formControlName="name" placeholder="Nhập tên" />
    @if (form.get('name')?.hasError('required')) {
      <tds-error>Tên là bắt buộc</tds-error>
    }
    @if (form.get('name')?.hasError('minlength')) {
      <tds-error>Tên ít nhất 3 ký tự</tds-error>
    }
  </tds-form-field>

  <tds-form-field>
    <tds-label>Email</tds-label>
    <input tdsInput formControlName="email" placeholder="Nhập email" />
    @if (form.get('email')?.hasError('required')) {
      <tds-error>Email là bắt buộc</tds-error>
    }
    @if (form.get('email')?.hasError('email')) {
      <tds-error>Email không hợp lệ</tds-error>
    }
  </tds-form-field>

  <button tds-button color="primary" type="submit" [disabled]="form.invalid || submitting">
    {{ submitting ? 'Đang lưu...' : 'Lưu' }}
  </button>
</form>
```

### TypeScript
```typescript
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSButtonModule } from 'tds-ui/button';
import { TDSInputModule } from 'tds-ui/tds-input';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, TDSFormFieldModule, TDSButtonModule, TDSInputModule],
  templateUrl: './my-form.component.html'
})
export class MyFormComponent {
  form: FormGroup;
  submitting = false;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
    });
  }

  onSubmit() {
    if (this.form.invalid) return;
    this.submitting = true;
    // Call API...
    this.submitting = false;
  }
}
```

## Tips
- `tds-form-field` tự động hiển thị error khi dùng với reactive forms
- Dùng `tds-help-message` thay `tds-error` cho hint text không phải error
- Xem thêm: `reference/docs/form-field.md`, `reference/docs/button.md`
