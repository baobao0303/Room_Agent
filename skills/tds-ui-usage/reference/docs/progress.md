# Progress

Thanh tiến trình.

**Selector:** `tds-progress`
**Import:** `import { TDSProgressModule } from 'tds-ui/progress';`
**Export as:** `tdsProgress`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `'line' \| 'circle' \| 'dashboard'` | `'line'` | Kiểu hiển thị |
| `percent` | `number` | `0` | Phần trăm (0-100) |
| `status` | `'success' \| 'exception' \| 'active' \| 'normal'` | — | Trạng thái |
| `showInfo` | `boolean` | `true` | Hiển thị text phần trăm |
| `strokeWidth` | `number` | — | Độ dày thanh (line: px, circle: %) |
| `width` | `number` | `132` | Kích thước vòng tròn (circle/dashboard) |
| `strokeColor` | `string \| TDSProgressColorGradient` | — | Màu gradient |
| `format` | `TDSProgressFormatter` | — | Custom text formatter |
| `size` | `'default' \| 'small'` | `'default'` | Kích thước |
| `successPercent` | `number` | — | Thành công phần trăm (đối với two-part progress) |
| `gapDegree` | `number` | — | Gap degree (circle/dashboard) |
| `gapPosition` | `'top' \| 'bottom' \| 'left' \| 'right'` | `'top'` | Vị trí gap |
| `strokeLinecap` | `'round' \| 'square'` | `'round'` | Kiểu đầu line |
| `steps` | `number` | `0` | Số steps (nếu > 0, hiển thị step progress) |

## Type Definitions

```typescript
// Gradient color types
type TDSProgressColorGradient = string | {
  from?: string;
  to?: string;
  direction?: string;
} | {
  [percent: string]: string;
};

// Formatter type
type TDSProgressFormatter = (percent: number) => string | TemplateRef<{ $implicit: number }>;
```

## Usage

```html
<!-- Line progress -->
<tds-progress [percent]="75"></tds-progress>

<!-- Circle progress -->
<tds-progress
  type="circle"
  [percent]="75">
</tds-progress>

<!-- Dashboard progress -->
<tds-progress
  type="dashboard"
  [percent]="60"
  [width]="200">
</tds-progress>

<!-- Custom format -->
<tds-progress
  [percent]="uploadPercent"
  [format]="formatProgress">
</tds-progress>

<!-- Gradient color (from/to) -->
<tds-progress
  [percent]="80"
  [strokeColor]="{ from: '#ff0000', to: '#00ff00' }">
</tds-progress>

<!-- Gradient color (percent-based) -->
<tds-progress
  [percent]="80"
  [strokeColor]="{ '0%': '#108ee9', '100%': '#87d068' }">
</tds-progress>

<!-- Step progress -->
<tds-progress
  [percent]="50"
  [steps]="5">
</tds-progress>

<!-- With success percent -->
<tds-progress
  [percent]="75"
  [successPercent]="30">
</tds-progress>

<!-- Different sizes -->
<tds-progress [percent]="50" size="small"></tds-progress>
<tds-progress [percent]="50" size="default"></tds-progress>

<!-- Status -->
<tds-progress [percent]="100" status="success"></tds-progress>
<tds-progress [percent]="50" status="exception"></tds-progress>
<tds-progress [percent]="70" status="active"></tds-progress>
```

```typescript
import { TDSProgressModule } from 'tds-ui/progress';

@Component({
  standalone: true,
  imports: [TDSProgressModule],
  template: `...`
})
export class MyComponent {
  uploadPercent = 65;

  formatProgress = (percent: number): string => {
    return `${percent} / 100`;
  };
}
```

## Notes

- Default type là `'line'`
- Default status tự động inferred:
  - `percent >= 100` → `success`
  - User có thể override với `status` input
- Format function nhận percent và trả về string
- Gradient color có thể là:
  - Object với `from` và `to` properties
  - Object với percent keys (`'0%'`, `'100%'`, etc.)
  - String color đơn
- `strokeWidth` default:
  - Line + default size: `8px`
  - Line + small size hoặc circle/dashboard: `6px`
- `gapDegree` default:
  - Circle: `0`
  - Dashboard: `75`
- Step progress tự động hiển thị khi `steps > 0`
- Component support RTL (right-to-left) direction
