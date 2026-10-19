# Segmented

Bộ chọn phân đoạn (segmented control), tương tự tab nhưng compact hơn.

**Selector:** `tds-segmented`
**Import:** `import { TDSSegmentedModule } from 'tds-ui/segmented';`
**Export as:** `tdsSegmented`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsOptions` | `TDSSegmentedOptions` | `[]` | Danh sách options |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa toàn bộ |
| `tdsSize` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl' \| undefined` | `'md'` | Kích thước |
| `tdsBlock` | `boolean` | `false` | Full width |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |
| `tdsColor` | `'primary' \| 'secondary'` | `'primary'` | Màu chính |
| `tdsType` | `'default' \| 'outline'` | `'default'` | Kiểu button |
| `tdsIcon` | `boolean` | `false` | Chỉ hiển thị icon mode |
| `tdsLabelTemplate` | `TemplateRef<{ $implicit: TDSSegmentedOption; index: number }> | null` | `null` | Custom label template |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsValueChange` | `EventEmitter<number>` | Khi chọn option (emits index) |

## Type Definitions

```typescript
interface TDSSegmentedOption {
  label: string;
  value: string | number;
  icon?: string;        // tdsi-xxx class
  disabled?: boolean;
  useTemplate?: boolean;
  className?: string;
}

type TDSSegmentedOptions = Array<TDSSegmentedOption | string | number>;
```

## Usage

```html
<!-- Simple string options -->
<tds-segmented
  [tdsOptions]="['Ngày', 'Tuần', 'Tháng']"
  (tdsValueChange)="onPeriodChange($event)">
</tds-segmented>

<!-- Object options with values -->
<tds-segmented
  [tdsOptions]="viewOptions"
  (tdsValueChange)="onViewChange($event)">
</tds-segmented>

<!-- With icons -->
<tds-segmented
  [tdsOptions]="iconOptions"
  [tdsSize]="'lg'"
  (tdsValueChange)="onSelect($event)">
</tds-segmented>

<!-- Disabled and block mode -->
<tds-segmented
  [tdsOptions]="options"
  [tdsDisabled]="isDisabled"
  [tdsBlock]="true">
</tds-segmented>

<!-- Outline type -->
<tds-segmented
  [tdsOptions]="typeOptions"
  [tdsType]="'outline'"
  [tdsColor]="'secondary'">
</tds-segmented>

<!-- Icon only mode -->
<tds-segmented
  [tdsOptions]="iconOnlyOptions"
  [tdsIcon]="true">
</tds-segmented>

<!-- With form control -->
<tds-segmented
  [tdsOptions]="statusOptions"
  [formControl]="statusControl">
</tds-segmented>

<!-- Custom label template -->
<tds-segmented
  [tdsOptions]="options"
  [tdsLabelTemplate]="customLabelTemplate">
</tds-segmented>

<ng-template #customLabelTemplate let-option let-index="index">
  <span class="custom-label">{{ option.label }} ({{ index }})</span>
</ng-template>
```

```typescript
import { TDSSegmentedModule } from 'tds-ui/segmented';
import { TDSSegmentedOption } from 'tds-ui/segmented';
import { FormControl } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSSegmentedModule],
  template: `...`
})
export class MyComponent {
  viewOptions: TDSSegmentedOption[] = [
    { label: 'Danh sách', value: 'list', icon: 'tdsi-list-fill' },
    { label: 'Lưới', value: 'grid', icon: 'tdsi-grid-fill' },
  ];

  iconOptions: TDSSegmentedOption[] = [
    { label: 'Left', value: 'left', icon: 'tdsi-arrow-left-fill' },
    { label: 'Center', value: 'center', icon: 'tdsi-align-center-fill' },
    { label: 'Right', value: 'right', icon: 'tdsi-arrow-right-fill' },
  ];

  iconOnlyOptions: TDSSegmentedOptions = [
    'tdsi-bold-fill',
    'tdsi-italic-fill',
    'tdsi-underline-fill',
  ];

  statusControl = new FormControl(0);

  onPeriodChange(index: number) {
    console.log('Selected index:', index);
  }

  onViewChange(index: number) {
    const option = this.viewOptions[index];
    console.log('Selected option:', option);
  }
}
```

## Notes

- Segmented là ControlValueAccessor, có thể dùng với `formControl` hoặc `ngModel`
- Output `tdsValueChange` emits **index** của option được chọn, không phải value
- Để lấy actual value, access options array bằng index: `this.options[index]`
- String/number options tự động convert thành TDSSegmentedOption với `label = value`
- Icon classes phải là `tdsi-*` format từ icon system
- Component có thumb animation khi chuyển giữa các options
- Support RTL (right-to-left) direction
- `tdsIcon="true"` chỉ hiển thị icon: component dùng `label` làm icon class (render `<span [class]="item.label">`), **không dùng `icon` field**. Dùng string[] (vd: `['tdsi-bold-fill', ...]`) hoặc object có `label` là icon class. Text label bị ẩn
- `useTemplate="true"` trong option để sử dụng custom label template
