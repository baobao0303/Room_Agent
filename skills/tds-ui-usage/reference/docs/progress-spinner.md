# Progress Spinner

Spinner loading animation với nhiều màu sắc. Hiển thị trạng thái đang tải.

**Selector:** `tds-spinner`
**Import:** `import { TDSSpinnerModule } from 'tds-ui/progress-spinner';`
**Export as:** `tdsSpinner`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | `TDSThemePalette` | `'primary'` | Màu sắc: `primary`, `secondary`, `success`, `error`, `warning`, `info`, `black`, `white`, `red`, `yellow`, `green`, `blue`, `indigo`, `purple`, `pink`, `amber`, `sky`, `lime`, `teal`, `orange` |
| `tdsTemplate` | `TemplateRef<any> \| null` | `null` | Custom template cho spinner |

## Usage

```html
<!-- Basic spinner -->
<tds-spinner></tds-spinner>

<!-- Custom color -->
<tds-spinner color="secondary"></tds-spinner>

<!-- Custom template -->
<ng-template #customSpinner>
  <div class="my-custom-spinner">...</div>
</ng-template>
<tds-spinner [tdsTemplate]="customSpinner"></tds-spinner>
```

```typescript
import { TDSSpinnerModule } from 'tds-ui/progress-spinner';

@Component({
  standalone: true,
  imports: [TDSSpinnerModule],
})
export class MyComponent {
  // Component logic
}
```

## tds-spin Wrapper Component

`tds-spin` là wrapper component bao spinner với content slot, dùng cho loading overlay.

**Selector:** `tds-spin`
**Export as:** `tdsSpin`

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `spinning` | `boolean` | `true` | Trạng thái spinning |
| `indicator` | `TemplateRef<any> \| null` | `null` | Custom spinner template |
| `size` | `ButtonSize` | `'md'` | Kích thước: `sm`, `md`, `lg`, `xl` |
| `tip` | `string \| null` | `null` | Text hiển thị bên dưới spinner |
| `delay` | `number` | `0` | Delay trước khi hiển thị spinner (ms) |
| `simple` | `boolean` | `false` | Chỉ hiển thị spinner, không wrap content |
| `color` | `TDSThemePalette` | `'primary'` | Màu spinner |

```html
<!-- Spin wrapper với content -->
<tds-spin [spinning]="isLoading" tip="Đang tải...">
  <div>Content được hiển thị khi không loading</div>
</tds-spin>

<!-- Simple spinner (no content wrapper) -->
<tds-spin [simple]="true" [spinning]="true"></tds-spin>
```

## Notes

- Component standalone, có thể import trực tiếp mà không cần module
- Module name là `TDSSpinnerModule` (không phải `TDSProgressSpinnerModule`)
- Tự động render SVG spinner animation
- Hỗ trợ RTL (right-to-left)
- Có thể customize template hoàn toàn
- Mặc định màu primary
