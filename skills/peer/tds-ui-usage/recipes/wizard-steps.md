## Wizard với Steps

**Use case:** Tạo form nhiều bước (wizard/stepper) sử dụng `tds-steps` để hiển thị tiến trình và điều khiển bước.

**Components cần import:**
```typescript
import { TDSStepsModule } from 'tds-ui/step';
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSInputModule } from 'tds-ui/tds-input';
import { TDSButtonModule } from 'tds-ui/button';
import { ReactiveFormsModule } from '@angular/forms';
```

---

### Wizard form đa bước

```html
<!-- Steps indicator -->
<tds-steps [current]="currentStep" mode="default" labelPlacement="horizontal">
  <tds-step tdsTitle="Thông tin cơ bản" description="Nhập thông tin"></tds-step>
  <tds-step tdsTitle="Liên hệ" description="Địa chỉ và SĐT"></tds-step>
  <tds-step tdsTitle="Xác nhận" description="Kiểm tra lại"></tds-step>
</tds-steps>

<!-- Step content -->
<div class="mt-6">
  <!-- Step 1 -->
  @if (currentStep === 0) {
    <form [formGroup]="form">
      <tds-form-field>
        <tds-label>Họ tên</tds-label>
        <input tdsInput formControlName="name" placeholder="Nhập họ tên" />
        @if (form.get('name')?.hasError('required')) {
          <tds-error>Họ tên là bắt buộc</tds-error>
        }
      </tds-form-field>

      <tds-form-field class="mt-4">
        <tds-label>Email</tds-label>
        <input tdsInput formControlName="email" placeholder="Nhập email" />
        @if (form.get('email')?.hasError('required')) {
          <tds-error>Email là bắt buộc</tds-error>
        }
      </tds-form-field>
    </form>
  }

  <!-- Step 2 -->
  @if (currentStep === 1) {
    <form [formGroup]="form">
      <tds-form-field>
        <tds-label>Số điện thoại</tds-label>
        <input tdsInput formControlName="phone" placeholder="Nhập SĐT" />
      </tds-form-field>

      <tds-form-field class="mt-4">
        <tds-label>Địa chỉ</tds-label>
        <input tdsInput formControlName="address" placeholder="Nhập địa chỉ" />
      </tds-form-field>
    </form>
  }

  <!-- Step 3 -->
  @if (currentStep === 2) {
    <div class="space-y-2">
      <p><strong>Họ tên:</strong> {{ form.get('name')?.value }}</p>
      <p><strong>Email:</strong> {{ form.get('email')?.value }}</p>
      <p><strong>SĐT:</strong> {{ form.get('phone')?.value }}</p>
      <p><strong>Địa chỉ:</strong> {{ form.get('address')?.value }}</p>
    </div>
  }
</div>

<!-- Navigation buttons -->
<div class="flex justify-between mt-8">
  @if (currentStep > 0) {
    <button tds-button color="secondary" (click)="prev()">
      Quay lại
    </button>
  }
  <div></div>
  @if (currentStep < totalSteps - 1) {
    <button tds-button color="primary"
      (click)="next()" [disabled]="!isStepValid()">
      Tiếp theo
    </button>
  }
  @if (currentStep === totalSteps - 1) {
    <button tds-button color="success"
      (click)="submit()" [disabled]="form.invalid">
      Hoàn thành
    </button>
  }
</div>
```

```typescript
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-wizard-form',
  templateUrl: './wizard-form.component.html'
})
export class WizardFormComponent {
  currentStep = 0;
  totalSteps = 3;
  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      address: [''],
    });
  }

  isStepValid(): boolean {
    switch (this.currentStep) {
      case 0:
        return !!(this.form.get('name')?.valid && this.form.get('email')?.valid);
      case 1:
        return true;
      default:
        return this.form.valid;
    }
  }

  next(): void {
    if (this.currentStep < this.totalSteps - 1) {
      this.currentStep++;
    }
  }

  prev(): void {
    if (this.currentStep > 0) {
      this.currentStep--;
    }
  }

  submit(): void {
    if (this.form.invalid) return;
    console.log('Submit:', this.form.value);
  }
}
```

---

### Bar mode (thanh tiến trình)

```html
<tds-steps [current]="currentStep" mode="bar" (indexChange)="onStepClick($event)">
  <tds-step tdsTitle="Bước 1"></tds-step>
  <tds-step tdsTitle="Bước 2"></tds-step>
  <tds-step tdsTitle="Bước 3"></tds-step>
</tds-steps>
```

---

**Tips:**
- `[current]` — step hiện tại, bắt đầu từ 0
- `mode`: `"default"` (tròn có icon/số) | `"bar"` (thanh ngang)
- `direction`: `"horizontal"` (mặc định) | `"vertical"` — chiều hiển thị
- `labelPlacement`: `"horizontal"` | `"vertical"` — vị trí label
- `(indexChange)` — event khi click vào step (cho phép navigate bằng click)
- `[status]` trên `tds-step`: `"wait"` | `"process"` | `"finish"` | `"error"` — ghi đè status tự động
- `[showStep]="true"` — hiện số thứ tự step
- Dùng `@if (currentStep === N)` để ẩn/hiện nội dung từng bước
- Validate từng bước trong `isStepValid()` trước khi cho next
