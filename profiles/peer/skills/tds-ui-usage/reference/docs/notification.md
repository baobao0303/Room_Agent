# Notification

Thông báo góc màn hình (toast). Sử dụng `TDSNotificationService` để hiển thị notification.

**Import:** `import { TDSNotificationService, TDSNotificationModule } from 'tds-ui/notification';`

## TDSNotificationService Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `success` | `success(title: string, content: string, options?: TDSNotificationDataOptions): TDSNotificationRef` | Notification thành công |
| `error` | `error(title: string, content: string, options?: TDSNotificationDataOptions): TDSNotificationRef` | Notification lỗi |
| `info` | `info(title: string, content: string, options?: TDSNotificationDataOptions): TDSNotificationRef` | Notification thông tin |
| `warning` | `warning(title: string, content: string, options?: TDSNotificationDataOptions): TDSNotificationRef` | Notification cảnh báo |
| `blank` | `blank(title: string, content: string, options?: TDSNotificationDataOptions): TDSNotificationRef` | Notification không icon |
| `create` | `create(type: string, title: string, content: string, options?: TDSNotificationDataOptions): TDSNotificationRef` | Tạo notification tuỳ chỉnh |
| `template` | `template(template: TemplateRef<{}>, options?: TDSNotificationDataOptions): TDSNotificationRef` | Notification dùng template |
| `remove` | `remove(id?: string): void` | Đóng notification theo ID hoặc tất cả |

## TDSNotificationRef

```typescript
const ref = notificationService.success('Tiêu đề', 'Nội dung');

ref.messageId;                          // ID dùng để remove: service.remove(ref.messageId)
ref.onClose.subscribe(byUser => {});    // Observable — phát khi notification đóng
ref.onClick.subscribe(event => {});     // Observable — phát khi click vào notification
```

- Gọi `service.remove(ref.messageId)` để đóng notification programmatically

## TDSNotificationDataOptions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `placement` | `'topLeft' \| 'topRight' \| 'bottomLeft' \| 'bottomRight'` | `'topRight'` | Vị trí hiển thị |
| `duration` | `number` | `4500` | Thời gian tự đóng (ms) |
| `animate` | `boolean` | `true` | Hiệu ứng animation |
| `pauseOnHover` | `boolean` | `true` | Dừng timer khi hover |
| `key` | `string` | — | Key unique để nhóm notification |
| `style` | `NgStyleInterface` | — | CSS inline |
| `clss` | `NgClassInterface \| string` | — | CSS classes |
| `closeIcon` | `TemplateRef<void> \| string` | — | Icon close tùy chỉnh |
| `data` | `T` | — | Data tùy chỉnh |

## Usage

```typescript
import { TDSNotificationService } from 'tds-ui/notification';
import { Component } from '@angular/core';

@Component({
  selector: 'app-notification-demo',
  standalone: true,
  template: `
    <button (click)="showSuccess()">Success</button>
    <button (click)="showError()">Error</button>
    <button (click)="showCustom()">Custom</button>
  `
})
export class NotificationDemoComponent {
  constructor(private notification: TDSNotificationService) {}

  showSuccess() {
    this.notification.success(
      'Thành công',
      'Dữ liệu đã được lưu thành công!',
      { placement: 'topRight', duration: 3000 }
    );
  }

  showError() {
    this.notification.error(
      'Lỗi',
      'Không thể kết nối đến máy chủ'
    );
  }

  showCustom() {
    this.notification.create(
      'custom',
      'Tuỳ chỉnh',
      'Notification tuỳ chỉnh',
      { 
        placement: 'bottomLeft',
        duration: 5000,
        animate: true,
        pauseOnHover: true
      }
    );
  }
}
```

## Notes

- `TDSNotificationService` được inject tự động (providedIn: 'root')
- Notification hiển thị ở góc màn hình, không che phủ toàn trang (khác với Alert)
- `placement` xác định góc hiển thị (top/bottom, left/right)
- Không set `duration` sẽ sử dụng giá trị mặc định từ container (4500ms)
- Sử dụng `key` option để merge notification cùng loại
- Component hỗ trợ RTL (right-to-left) khi dùng với Directionality
