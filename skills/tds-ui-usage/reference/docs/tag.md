# Tag

Nhãn hiển thị với nhiều mode (default, closeable, checkable), status colors và sizes. Hỗ trợ tag đa màu tùy chỉnh.

**Selectors:** `tds-tag`, `tds-tag-multi-color`
**Import:** `import { TDSTagModule, TDSTagColorModule } from 'tds-ui/tag';`
**Export as:** `tdsTag`, `tdsTagMultiColor`

## TDSTagModule (Regular Tag)

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `'default' \| 'closeable' \| 'checkable'` | `'default'` | Chế độ hoạt động của tag |
| `type` | `'default' \| 'outline'` | `'default'` | Kiểu hiển thị (solid hoặc outline) |
| `status` | `'primary' \| 'secondary' \| 'success' \| 'info' \| 'error' \| 'warning' \| 'neutral' \| 'default' \| string` | `'secondary'` | Trạng thái/màu sắc của tag |
| `checked` | `boolean` | `false` | Trạng thái checked (chỉ dùng với mode='checkable') |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước tag |
| `disabled` | `boolean` | `false` | Vô hiệu hóa tag (không tương tác) |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme màu sắc |
| `tdsStyle` | `NgStyleInterface` | — | CSS inline style tùy chỉnh |
| `rounded` | `string` | `null` | CSS class cho border radius (deprecated from v2.4.2) |

### Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `close` | `EventEmitter<MouseEvent>` | Emit khi nhấn nút X (mode='closeable') |
| `checkedChange` | `EventEmitter<boolean>` | Emit khi checked thay đổi (mode='checkable') |

## TDSTagColorModule (Multi-color Tag)

### Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsColor` | `string` | `''` | Màu base để generate palette (ví dụ: '#ff0000', 'red') |
| `tdsBgColor` | `'50' \| '100' \| '200' \| '300' \| '400' \| '500' \| '600' \| '700' \| '800' \| '900'` | `'100'` | Mức màu cho background |
| `tdsBorderColor` | `'50' \| '100' \| '200' \| '300' \| '400' \| '500' \| '600' \| '700' \| '800' \| '900'` | `'100'` | Mức màu cho border |
| `tdsIconColor` | `'50' \| '100' \| '200' \| '300' \| '400' \| '500' \| '600' \| '700' \| '800' \| '900'` | `'500'` | Mức màu cho icon |
| `tdsIcon` | `string` | — | Icon class (ví dụ: 'tdsi-check') |
| `tdsSize` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước tag |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme cho màu nền khi generate |

### Key Outputs

None (component không có outputs)

## Usage

### Regular Tag (TDSTagModule)

```html
<!-- Default tags với các status -->
<tds-tag>Mặc định</tds-tag>
<tds-tag status="primary">Primary</tds-tag>
<tds-tag status="success">Thành công</tds-tag>
<tds-tag status="info">Thông tin</tds-tag>
<tds-tag status="error">Lỗi</tds-tag>
<tds-tag status="warning">Cảnh báo</tds-tag>
<tds-tag status="neutral">Neutral</tds-tag>

<!-- Outline type -->
<tds-tag type="outline" status="primary">Outline Primary</tds-tag>
<tds-tag type="outline" status="success">Outline Success</tds-tag>

<!-- Different sizes -->
<tds-tag size="sm">Small</tds-tag>
<tds-tag size="md">Medium</tds-tag>
<tds-tag size="lg">Large</tds-tag>
<tds-tag size="xl">Extra Large</tds-tag>

<!-- Closeable mode -->
<tds-tag mode="closeable" (close)="removeTag($event)">
  Tag có thể đóng
</tds-tag>

<tds-tag mode="closeable" status="error" (close)="handleRemove($event)">
  Xóa được
</tds-tag>

<!-- Checkable mode -->
<tds-tag mode="checkable" [(checked)]="isChecked">
  Checkable
</tds-tag>

<tds-tag
  mode="checkable"
  [checked]="true"
  (checkedChange)="onCheckedChange($event)"
  status="success">
  Selected
</tds-tag>

<!-- Disabled -->
<tds-tag [disabled]="true">Vô hiệu hóa</tds-tag>
<tds-tag mode="closeable" [disabled]="true">Không thể đóng</tds-tag>
<tds-tag mode="checkable" [disabled]="true">Không thể check</tds-tag>

<!-- Custom style -->
<tds-tag [tdsStyle]="{'background': '#purple-500', 'color': 'white'}">
  Custom style
</tds-tag>

<!-- Theme variants -->
<tds-tag tdsTheme="light">Light theme</tds-tag>
<tds-tag tdsTheme="dark">Dark theme</tds-tag>

<!-- Rounded (deprecated) -->
<tds-tag rounded="rounded-full">Rounded full</tds-tag>
```

### Multi-color Tag (TDSTagColorModule)

```html
<!-- Basic multi-color tag -->
<tds-tag-multi-color tdsColor="#ff0000">
  Custom Red Tag
</tds-tag-multi-color>

<!-- Với color name -->
<tds-tag-multi-color tdsColor="purple">
  Purple Tag
</tds-tag-multi-color>

<!-- Tùy chỉnh màu sắc cho từng phần -->
<tds-tag-multi-color
  tdsColor="#3b82f6"
  tdsBgColor="100"
  tdsBorderColor="200"
  tdsIconColor="500">
  Blue Tag
</tds-tag-multi-color>

<!-- Với icon -->
<tds-tag-multi-color
  tdsColor="#10b981"
  tdsIcon="tdsi-check-fill"
  tdsBgColor="100"
  tdsIconColor="500">
  Verified
</tds-tag-multi-color>

<!-- Different sizes -->
<tds-tag-multi-color tdsColor="#f59e0b" tdsSize="sm">Small</tds-tag-multi-color>
<tds-tag-multi-color tdsColor="#f59e0b" tdsSize="md">Medium</tds-tag-multi-color>
<tds-tag-multi-color tdsColor="#f59e0b" tdsSize="lg">Large</tds-tag-multi-color>
<tds-tag-multi-color tdsColor="#f59e0b" tdsSize="xl">XL</tds-tag-multi-color>

<!-- Theme variants -->
<tds-tag-multi-color
  tdsColor="#8b5cf6"
  tdsTheme="dark"
  tdsBgColor="600">
  Dark Theme
</tds-tag-multi-color>

<!-- Mức màu khác nhau -->
<tds-tag-multi-color
  tdsColor="#ec4899"
  tdsBgColor="50"
  tdsBorderColor="500"
  tdsIconColor="700">
  Subtle Pink
</tds-tag-multi-color>
```

### TypeScript Examples

```typescript
import { TDSTagModule, TDSTagColorModule } from 'tds-ui/tag';
import { Component } from '@angular/core';

@Component({
  selector: 'app-tag-demo',
  standalone: true,
  imports: [TDSTagModule, TDSTagColorModule],
  template: `
    <!-- Regular tags -->
    <tds-tag
      mode="closeable"
      status="success"
      (close)="handleClose($event)">
      Đóng được
    </tds-tag>

    <!-- Checkable with two-way binding -->
    <tds-tag
      mode="checkable"
      [(checked)]="isSelected"
      (checkedChange)="onCheckChange($event)">
      Chọn được
    </tds-tag>

    <!-- Multi-color tags -->
    <tds-tag-multi-color
      tdsColor="#ff6b6b"
      tdsIcon="tdsi-heart-fill"
      tdsBgColor="100"
      tdsIconColor="500">
      Custom Color
    </tds-tag-multi-color>
  `
})
export class TagDemoComponent {
  isSelected = false;

  handleClose(event: MouseEvent) {
    console.log('Tag closed', event);
    // Xử lý logic khi đóng tag
  }

  onCheckChange(checked: boolean) {
    console.log('Tag checked:', checked);
    // Xử lý logic khi checked thay đổi
  }
}
```

## Notes

### Regular Tag (TDSTagModule)
- **Modes**:
  - `default`: Chỉ hiển thị, không có tương tác
  - `closeable`: Hiển thị nút X, emit event `close` khi click
  - `checkable`: Click vào tag để toggle checked state
- **Type**: `default` (nền solid), `outline` (chỉ viền)
- **Status**: Xác định màu sắc (primary, secondary, success, info, error, warning, neutral)
- **Sizes**: `sm` (nhỏ nhất), `md` (mặc định), `lg`, `xl` (lớn nhất)
- **Disabled**: Tag disabled không emit events và không thay đổi checked state
- **Standalone**: Component standalone, không cần import module

### Multi-color Tag (TDSTagColorModule)
- **Color generation**: Tự động generate palette từ màu base (50-900)
- **Mức màu**: `50` (nhất) → `900` (đậm nhất)
- **Auto text color**: Tự động chọn text màu trắng hoặc đen dựa trên brightness của background
- **Icon support**: Hiển thị icon với màu tùy chỉnh
- **Theme**: `default`, `light`, `dark` ảnh hưởng đến màu nền khi generate
- **Responsive với config**: Component phản hồi với `TDSConfigService` thay đổi
- **Standalone**: Component standalone, không cần import module

### Khi nào dùng component nào?
- **TDSTagModule**: Tag thông thường với status colors preset, cần closeable/checkable
- **TDSTagColorModule**: Cần màu sắc custom brand colors, palette tự generate
