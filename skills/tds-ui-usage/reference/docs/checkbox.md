# Checkbox

Ô checkbox đơn. Hỗ trợ các kích thước khác nhau, trạng thái indeterminate, và theme options.

**Selector:** `tds-checkbox`
**Import:** `import { TDSCheckBoxModule } from 'tds-ui/tds-checkbox';`
**Export as:** `taCheckbox`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `checked` | `boolean` | `false` | Trạng thái checked |
| `indeterminate` | `boolean` | `false` | Trạng thái một phần (partial) |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `required` | `boolean` | `undefined` (code initializes `!` — potential bug: always truthy until explicitly set) | Bắt buộc chọn |
| `size` | `ButtonSize` | `'md'` | Kích thước: `sm`, `md`, `lg` |
| `value` | `string` | — | Giá trị của checkbox (dùng trong checkbox group) |
| `name` | `string \| null` | `null` | Tên field |
| `color` | `TDSThemePalette` | — | Màu sắc (kế thừa từ mixin) |
| `tabIndex` | `number` | `0` | Tab index (kế thừa từ mixin) |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |
| `id` | `string` | `tds-checkbox-{n}` | ID của checkbox |
| `aria-label` | `string` | `''` | ARIA label |
| `aria-labelledby` | `string \| null` | `null` | ARIA labelled by |
| `aria-describedby` | `string` | — | ARIA described by |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsChange` | `EventEmitter<TDSCheckboxChange>` | Khi checked thay đổi, trả về `{ checked: boolean, source: TDSCheckbox }` |
| `change` | `EventEmitter<TDSCheckboxChange>` | @deprecated từ version 2.1.0, dùng `tdsChange` thay thế |
| `indeterminateChange` | `EventEmitter<boolean>` | Khi indeterminate thay đổi |

## TDSCheckboxChange Interface

```typescript
class TDSCheckboxChange {
  source: TDSCheckbox;    // Checkbox phát ra event
  checked: boolean;       // Giá trị checked mới
}
```

## Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `toggle` | - | Đảo ngược trạng thái checked |
| `focus` | `origin?: FocusOrigin, options?: FocusOptions` | Focus vào checkbox |

## Usage

```html
<!-- Standalone checkbox -->
<tds-checkbox [(checked)]="isAgreed" (tdsChange)="onAgreeChange($event)">
  Tôi đồng ý với điều khoản
</tds-checkbox>

<!-- Với ngModel -->
<tds-checkbox [(ngModel)]="isActive">Kích hoạt</tds-checkbox>

<!-- Multiple checkboxes (checkbox group) -->
<div>
  <tds-checkbox [(ngModel)]="selectedValues" value="a">Option A</tds-checkbox>
  <tds-checkbox [(ngModel)]="selectedValues" value="b">Option B</tds-checkbox>
  <tds-checkbox [(ngModel)]="selectedValues" value="c">Option C</tds-checkbox>
</div>

<!-- Indeterminate (select-all) -->
<tds-checkbox 
  [checked]="allSelected" 
  [indeterminate]="someSelected"
  (tdsChange)="toggleAll($event)">
  Select All
</tds-checkbox>

<!-- Với kích thước -->
<tds-checkbox size="sm" [(ngModel)]="isChecked">Small</tds-checkbox>
<tds-checkbox size="md" [(ngModel)]="isChecked">Medium</tds-checkbox>
<tds-checkbox size="lg" [(ngModel)]="isChecked">Large</tds-checkbox>

<!-- Với theme -->
<tds-checkbox tdsTheme="light" [(ngModel)]="isChecked">Light theme</tds-checkbox>
<tds-checkbox tdsTheme="dark" [(ngModel)]="isChecked">Dark theme</tds-checkbox>

<!-- Disabled -->
<tds-checkbox [disabled]="true" [(ngModel)]="isChecked">Disabled</tds-checkbox>

<!-- Required -->
<tds-checkbox [required]="true" [(ngModel)]="isAccepted">
  Bắt buộc đồng ý
</tds-checkbox>

<!-- Reactive Form -->
<tds-checkbox [formControl]="agreeCtrl">
  Tôi đồng ý
</tds-checkbox>

<!-- Với ARIA -->
<tds-checkbox 
  aria-label="Điều khoản dịch vụ"
  aria-describedby="terms-desc"
  [(ngModel)]="isAgreed">
  Điều khoản dịch vụ
</tds-checkbox>
<span id="terms-desc">Đọc kỹ trước khi đồng ý</span>
```

```typescript
import { TDSCheckbox, TDSCheckboxChange } from 'tds-ui/tds-checkbox';
import { FormControl } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSCheckbox, FormsModule, ReactiveFormsModule]
})
export class MyComponent {
  isAgreed = false;
  isActive = true;
  selectedValues: any[] = [];
  agreeCtrl = new FormControl(false);
  
  allSelected = false;
  someSelected = false;
  
  onAgreeChange(event: TDSCheckboxChange) {
    console.log('Checked:', event.checked);
    console.log('Source:', event.source);
  }

  toggleAll(event: TDSCheckboxChange) {
    this.selectedValues = event.checked ? ['a', 'b', 'c'] : [];
  }
  
  // Indeterminate state
  updateSelectAll(items: any[]) {
    const selected = items.filter(i => i.selected);
    this.allSelected = selected.length === items.length;
    this.someSelected = selected.length > 0 && !this.allSelected;
  }
}
```

## Notes

- `indeterminate` dùng khi select-all nhưng chưa chọn hết (ví dụ: select trong table)
- Khi dùng multiple checkboxes với `[(ngModel)]`, tất cả phải bind vào cùng một array
- Mỗi checkbox cần `value` prop để xác định giá trị khi checked trong checkbox group
- `size` hỗ trợ `sm`, `md`, `lg`
- `tdsTheme` hỗ trợ `default`, `light`, `dark`
- `change` output đã deprecated từ version 2.1.0, dùng `tdsChange` thay thế
- `required` input dùng cho validation (cần validator để hoạt động đúng)
- Component tự động quản lý ARIA attributes cho accessibility
- `indeterminate` sẽ tự động reset về `false` khi user click vào checkbox
- `exportAs` là `taCheckbox` (tiền tố `ta` thay vì `tds` — khác với quy ước naming chung của TDS)
- `required` input có potential bug: `_required` được khai báo với `!` (definite assignment assertion) nhưng không có giá trị khởi tạo, nên giá trị mặc định thực tế là `undefined` (truthy) cho đến khi được set explicit
