# Step

Thanh điều hướng các bước (stepper) với nhiều kiểu hiển thị. Hỗ trợ cả ngang và dọc, có thể dùng dạng icon hoặc dạng thanh (bar).

**Selector:** `tds-steps`, `tds-step`
**Import:** `import { TDSStepsModule } from 'tds-ui/step';`
**Export as:** `tdsSteps`, `tdsStep`

## Key Inputs

### TDSStepsModule (tds-steps)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `current` | `number` | `0` | Index của step hiện tại |
| `direction` | `'horizontal' \| 'vertical'` | `'horizontal'` | Hướng hiển thị |
| `labelPlacement` | `'horizontal' \| 'vertical'` | `'horizontal'` | Vị trí label |
| `mode` | `'default' \| 'bar'` | `'default'` | Chế độ hiển thị |
| `size` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `startIndex` | `number` | `0` | Index bắt đầu |
| `status` | `TDSStatusType` | `'process'` | Trạng thái: `wait`, `process`, `finish`, `error` |
| `showStep` | `boolean` | `false` | Hiển thị số thứ tự step |
| `borderStyle` | `string` | `'border-solid'` | Style viền |
| `progressDot` | `boolean \| TemplateRef` | `false` | Hiển thị dạng dot hoặc custom template |

### TDSStepModule (tds-step)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTitle` | `string \| TemplateRef` | `undefined` | Tiêu đề step |
| `subtitle` | `string \| TemplateRef` | `undefined` | Tiêu đề phụ |
| `description` | `string \| TemplateRef` | `undefined` | Mô tả |
| `disabled` | `boolean` | `false` | Vô hiệu hóa step |
| `status` | `string` | `'wait'` | Trạng thái: `wait`, `process`, `finish`, `error` |
| `icon` | `NgClassType \| TemplateRef` | `undefined` | Icon hoặc class icon |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `indexChange` | `EventEmitter<number>` | Emit khi index thay đổi (chỉ emit khi step clickable) |

## Usage

```html
<!-- Basic steps -->
<tds-steps [current]="currentStep" (indexChange)="onIndexChange($event)">
  <tds-step [tdsTitle]="'Bước 1'" [description]="'Mô tả bước 1'"></tds-step>
  <tds-step [tdsTitle]="'Bước 2'" [description]="'Mô tả bước 2'"></tds-step>
  <tds-step [tdsTitle]="'Bước 3'" [description]="'Mô tả bước 3'"></tds-step>
</tds-steps>

<!-- Vertical steps -->
<tds-steps direction="vertical" [current]="2">
  <tds-step [tdsTitle]="'Login'"></tds-step>
  <tds-step [tdsTitle]="'Verify'"></tds-step>
  <tds-step [tdsTitle]="'Complete'"></tds-step>
</tds-steps>

<!-- Progress dot mode -->
<tds-steps [current]="1" [progressDot]="true">
  <tds-step [tdsTitle]="'Step 1'"></tds-step>
  <tds-step [tdsTitle]="'Step 2'"></tds-step>
  <tds-step [tdsTitle]="'Step 3'"></tds-step>
</tds-steps>

<!-- Bar mode -->
<tds-steps mode="bar" [current]="1" size="lg">
  <tds-step [tdsTitle]="'In Progress'" status="process"></tds-step>
  <tds-step [tdsTitle]="'Waiting'" status="wait"></tds-step>
  <tds-step [tdsTitle]="'Finished'" status="finish"></tds-step>
</tds-steps>

<!-- With icons -->
<tds-steps [current]="1">
  <tds-step [tdsTitle]="'Upload'" [icon]="'tdsi-upload-fill'"></tds-step>
  <tds-step [tdsTitle]="'Process'" [icon]="'tdsi-loading-fill'"></tds-step>
  <tds-step [tdsTitle]="'Done'" [icon]="'tdsi-check-fill'"></tds-step>
</tds-steps>
```

```typescript
import { TDSStepsModule, TDSStepModule } from 'tds-ui/step';

@Component({
  standalone: true,
  imports: [TDSStepsModule, TDSStepModule],
})
export class MyComponent {
  currentStep = 1;

  onIndexChange(index: number) {
    this.currentStep = index;
  }
}
```

## Notes

- Dùng `(indexChange)` để xử lý khi người dùng click vào step
- Status được auto-calculate dựa trên `current` nếu không set manually
- `progressDot` có thể nhận `boolean` hoặc `TemplateRef` để custom
- `mode="bar"` hiển thị dạng thanh tiến trình ngang gọn nhẹ hơn
- `showStep="true"` hiển thị số thứ tự trong icon
- Support RTL (right-to-left) với Directionality
- Các size: `xs`, `sm`, `md`, `lg`, `xl` (default: `md`)
