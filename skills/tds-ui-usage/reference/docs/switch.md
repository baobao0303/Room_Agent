# Switch

Toggle switch on/off, tương tự checkbox nhưng dạng slide. Hỗ trợ các kích thước khác nhau, loading state, và theme options.

**Selector:** `tds-switch`
**Import:** `import { TDSSwitchModule } from 'tds-ui/switch';`
**Export as:** `tdsSwitch`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsCheckedChildren` | `string \| TemplateRef<void> \| null` | `null` | Label/text khi ON (checked) |
| `tdsUnCheckedChildren` | `string \| TemplateRef<void> \| null` | `null` | Label/text khi OFF (unchecked) |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa |
| `tdsLoading` | `boolean` | `false` | Trạng thái loading (hiển thị spinner) |
| `tdsControl` | `boolean` | `false` | Kiểm soát hoàn toàn bằng code (không click) |
| `tdsSize` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `tdsId` | `string \| null` | `null` | ID của switch |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |

## Key Outputs

Switch sử dụng `ControlValueAccessor`, dùng với `[(ngModel)]` hoặc `[formControl]`. Không có explicit `@Output` events — value changes được propagated qua `ngModelChange` hoặc `formControl`.

| Output | Type | Description |
|--------|------|-------------|
| `ngModelChange` | `EventEmitter<boolean>` | Tự động với `[(ngModel)]` |

## Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `focus` | - | Focus vào switch |
| `blur` | - | Blur switch |
| `updateValue` | `value: boolean` | Cập nhật giá trị checked |

## Usage

```html
<!-- Cơ bản -->
<tds-switch [(ngModel)]="isActive"></tds-switch>

<!-- Với label -->
<tds-switch 
  [(ngModel)]="isEnabled"
  tdsCheckedChildren="Bật"
  tdsUnCheckedChildren="Tắt">
</tds-switch>

<!-- Với template label -->
<ng-template #checkedTemplate>BẬT</ng-template>
<ng-template #uncheckedTemplate>TẮT</ng-template>
<tds-switch 
  [(ngModel)]="isEnabled"
  [tdsCheckedChildren]="checkedTemplate"
  [tdsUnCheckedChildren]="uncheckedTemplate">
</tds-switch>

<!-- Với kích thước -->
<tds-switch [(ngModel)]="isActive" tdsSize="xs">Extra Small</tds-switch>
<tds-switch [(ngModel)]="isActive" tdsSize="sm">Small</tds-switch>
<tds-switch [(ngModel)]="isActive" tdsSize="md">Medium</tds-switch>
<tds-switch [(ngModel)]="isActive" tdsSize="lg">Large</tds-switch>
<tds-switch [(ngModel)]="isActive" tdsSize="xl">Extra Large</tds-switch>

<!-- Reactive Form -->
<tds-switch [formControl]="activeCtrl"></tds-switch>

<!-- Loading state -->
<tds-switch [(ngModel)]="isActive" [tdsLoading]="isLoading"></tds-switch>

<!-- Disabled -->
<tds-switch [(ngModel)]="isActive" [tdsDisabled]="true"></tds-switch>

<!-- Control mode (chỉ thay đổi từ code) -->
<tds-switch 
  [(ngModel)]="isActive" 
  [tdsControl]="true">
</tds-switch>

<!-- Với theme -->
<tds-switch tdsTheme="light" [(ngModel)]="isActive">Light theme</tds-switch>
<tds-switch tdsTheme="dark" [(ngModel)]="isActive">Dark theme</tds-switch>

<!-- Với ID -->
<tds-switch tdsId="notification-switch" [(ngModel)]="notifications">
  Enable notifications
</tds-switch>

<!-- Full example với label -->
<div class="flex items-center gap-2">
  <tds-switch 
    [(ngModel)]="emailNotifications"
    tdsCheckedChildren="Email ON"
    tdsUnCheckedChildren="Email OFF">
  </tds-switch>
  <span>Email notifications</span>
</div>
```

```typescript
import { TDSSwitchModule } from 'tds-ui/switch';
import { FormControl } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSSwitchModule, FormsModule, ReactiveFormsModule]
})
export class MyComponent {
  isActive = false;
  isEnabled = false;
  isLoading = false;
  notifications = true;
  emailNotifications = false;
  activeCtrl = new FormControl(false);
  
  // Control mode example
  @ViewChild('mySwitch') mySwitch!: TDSSwitchModule;
  
  programmaticToggle() {
    // Chỉ thay đổi từ code, user không thể click
    this.mySwitch.updateValue(!this.isActive);
  }
  
  // Async toggle with loading
  async toggleWithLoading() {
    this.isLoading = true;
    try {
      await someAsyncOperation();
      this.isActive = !this.isActive;
    } finally {
      this.isLoading = false;
    }
  }
}
```

## Notes

- Dùng `[(ngModel)]` hoặc `[formControl]` để bind value
- `tdsSize` hỗ trợ `xs`, `sm`, `md`, `lg`, `xl`
- `tdsLoading="true"` hiển thị spinner và vô hiệu hóa tương tác
- `tdsControl="true"` khi chỉ muốn thay đổi từ code (vô hiệu hóa click)
- `tdsTheme` hỗ trợ `default`, `light`, `dark`
- Switch hỗ trợ RTL (right-to-left) layout
- Component tự động quản lý accessibility với keyboard navigation (arrow keys, space, enter)
- `tdsCheckedChildren` và `tdsUnCheckedChildren` có thể là string hoặc TemplateRef
- Khi `tdsControl="true"`, switch vẫn nhận focus nhưng không thay đổi giá trị khi click
- Focus monitor được tự động setup để track focus state
