# Spin

Wrapper component để hiển thị loading state cho nội dung bên trong. Có thể hiển thị spinner với optional text.

**Selector:** `tds-spin`
**Import:** `import { TDSSpinnerModule } from 'tds-ui/progress-spinner';`
**Export as:** `tdsSpin`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `spinning` | `boolean` | `true` | Hiển thị spinner |
| `indicator` | `TemplateRef<any> \| null` | `null` | Custom template cho loading indicator |
| `size` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `tip` | `string \| null` | `null` | Text hiển thị dưới spinner |
| `delay` | `number` | `0` | Delay (ms) trước khi hiển thị spinner |
| `simple` | `boolean` | `false` | Chỉ hiển thị spinner, không blur content |
| `color` | `TDSThemePalette` | `'primary'` | Màu sắc của spinner |

## Usage

```html
<!-- Basic spin wrapper -->
<tds-spin [spinning]="isLoading">
  <div class="content">
    Nội dung sẽ được blur khi loading
  </div>
</tds-spin>

<!-- With tip text -->
<tds-spin [spinning]="isLoading" tip="Đang tải...">
  <div class="content">Content</div>
</tds-spin>

<!-- Custom size -->
<tds-spin [spinning]="isLoading" size="lg">
  <div class="content">Content</div>
</tds-spin>

<!-- With delay -->
<tds-spin [spinning]="isLoading" [delay]="500">
  <div class="content">Content</div>
</tds-spin>

<!-- Simple mode (không blur content) -->
<tds-spin [spinning]="isLoading" [simple]="true">
  <div class="content">Content</div>
</tds-spin>

<!-- Custom indicator -->
<ng-template #customIndicator>
  <div class="custom-loader">Loading...</div>
</ng-template>
<tds-spin [spinning]="isLoading" [indicator]="customIndicator">
  <div class="content">Content</div>
</tds-spin>

<!-- Custom color -->
<tds-spin [spinning]="isLoading" color="secondary">
  <div class="content">Content</div>
</tds-spin>
```

```typescript
import { TDSSpinModule } from 'tds-ui/progress-spinner';

@Component({
  standalone: true,
  imports: [TDSSpinModule],
})
export class MyComponent {
  isLoading = false;

  loadData() {
    this.isLoading = true;
    // Fetch data...
    this.isLoading = false;
  }
}
```

## Notes

- Component standalone, có thể import trực tiếp mà không cần module
- Khi `spinning = true`, content bên trong sẽ bị blur
- `simple = true` chỉ hiển thị spinner mà không blur content
- `delay` hữu ích để tránh hiển thị spinner cho các tác vụ rất nhanh
- Hỗ trợ RTL (right-to-left)
- Mặc định sử dụng `TDSProgressSpinnerModule` làm indicator
- Có thể hoàn toàn customize indicator với `indicator` input
- `tip` hiển thị text bên dưới spinner (nếu có)
- Export cùng với `TDSProgressSpinnerModule` từ `tds-ui/progress-spinner`
