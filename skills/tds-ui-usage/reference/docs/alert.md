# Alert

Thông báo dạng banner cố định trên trang với hỗ trợ icon, mô tả và đóng.

**Selector:** `tds-alert`
**Export as:** `tdsAlert`
**Import:** `import { TDSAlertModule } from 'tds-ui/alert';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `'success' \| 'info' \| 'warning' \| 'error'` | `'info'` | Loại alert |
| `message` | `string \| TemplateRef<void> \| null` | `null` | Nội dung chính |
| `description` | `string \| TemplateRef<void> \| null` | `null` | Mô tả phụ (optional) |
| `footer` | `string \| TemplateRef<void> \| null` | `null` | Nội dung footer |
| `closeText` | `string \| TemplateRef<void> \| null` | `null` | Text hoặc template nút đóng |
| `closeable` | `boolean` | `false` | Hiển thị nút đóng |
| `showIcon` | `boolean` | `false` | Hiển thị icon loại |
| `banner` | `boolean` | `false` | Dạng banner (không border-radius, tự set type/showIcon) |
| `noAnimation` | `boolean` | `false` | Tắt animation |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Chủ đề màu |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `close` | `EventEmitter<boolean>` | Khi đóng alert hoàn tất |

## Usage

```html
<!-- Basic alert -->
<tds-alert 
  type="success"
  message="Thành công!"
  [showIcon]="true">
</tds-alert>

<!-- Alert with description -->
<tds-alert
  type="warning"
  message="Phiên sắp hết hạn"
  description="Vui lòng lưu công việc trước khi thoát"
  [showIcon]="true"
  [closeable]="true"
  (close)="onDismiss()">
</tds-alert>

<!-- Error alert -->
<tds-alert
  type="error"
  message="Lỗi"
  description="Không thể kết nối đến máy chủ"
  [showIcon]="true">
</tds-alert>

<!-- Banner style -->
<tds-alert
  banner="true"
  message="Hệ thống đang bảo trì">
</tds-alert>

<!-- Custom close text -->
<tds-alert
  type="info"
  message="Thông tin"
  [closeable]="true"
  closeText="Bỏ qua"
  (close)="handleClose()">
</tds-alert>
```

```typescript
import { TDSAlertModule } from 'tds-ui/alert';
import { Component } from '@angular/core';

@Component({
  selector: 'app-alert-demo',
  standalone: true,
  imports: [TDSAlertModule],
  template: `
    <tds-alert
      type="warning"
      message="Cảnh báo"
      description="Vui lòng xác nhận thao tác"
      [showIcon]="true"
      [closeable]="true"
      (close)="onClose()">
    </tds-alert>
  `
})
export class AlertDemoComponent {
  onClose() {
    console.log('Alert closed');
  }
}
```

## Notes

- Khi `description` có nội dung, alert sẽ được layout rộng hơn với icon outline
- `banner="true"` tự set `type="warning"` và `showIcon="true"` nếu chưa được set
- `message`, `description`, `footer`, `closeText` hỗ trợ cả string và TemplateRef
- Animation có thể tắt với `noAnimation="true"`
- Component hỗ trợ RTL (right-to-left) khi dùng với Directionality
