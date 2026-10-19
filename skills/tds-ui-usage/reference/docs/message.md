# Message

Thông báo nhỏ ở đầu trang. Sử dụng `TDSMessageService` để hiển thị message.

**Import:** `import { TDSMessageService, TDSMessageModule } from 'tds-ui/message';`

## TDSMessageService Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `success` | `success(content: string \| TemplateRef<void>, options?: TDSMessageDataOptions): TDSMessageRef` | Message thành công |
| `error` | `error(content: string \| TemplateRef<void>, options?: TDSMessageDataOptions): TDSMessageRef` | Message lỗi |
| `info` | `info(content: string \| TemplateRef<void>, options?: TDSMessageDataOptions): TDSMessageRef` | Message thông tin |
| `warning` | `warning(content: string \| TemplateRef<void>, options?: TDSMessageDataOptions): TDSMessageRef` | Message cảnh báo |
| `loading` | `loading(content: string \| TemplateRef<void>, options?: TDSMessageDataOptions): TDSMessageRef` | Message loading |
| `create` | `create(type: string, content: string \| TemplateRef<void>, options?: TDSMessageDataOptions): TDSMessageRef` | Tạo message tuỳ chỉnh |
| `remove` | `remove(id?: string): void` | Đóng message theo ID hoặc tất cả |

## TDSMessageRef

```typescript
const ref = messageService.success('Thành công!');

ref.messageId;                      // ID dùng để remove: service.remove(ref.messageId)
ref.onClose.subscribe(closed => {}); // Observable — phát khi message đóng
```

- Gọi `service.remove(ref.messageId)` để đóng message programmatically

## TDSMessageDataOptions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `duration` | `number` | `3000` | Thời gian tự đóng (ms) |
| `animate` | `boolean` | `true` | Hiệu ứng animation |
| `pauseOnHover` | `boolean` | `true` | Dừng timer khi hover |

## Usage

```typescript
import { TDSMessageService } from 'tds-ui/message';
import { Component } from '@angular/core';

@Component({
  selector: 'app-message-demo',
  standalone: true,
  template: `
    <button (click)="showSuccess()">Success</button>
    <button (click)="showError()">Error</button>
    <button (click)="showLoading()">Loading</button>
    <button (click)="showCustom()">Custom Duration</button>
  `
})
export class MessageDemoComponent {
  constructor(private message: TDSMessageService) {}

  showSuccess() {
    this.message.success('Lưu thành công!');
  }

  showError() {
    this.message.error('Có lỗi xảy ra, vui lòng thử lại.');
  }

  showLoading() {
    // Persistent loading (passes duration: 0)
    const ref = this.message.loading('Đang tải...', { duration: 0 });
    // Close it manually:
    this.message.remove(ref.messageId);
    // Subscribe to know when it closes:
    ref.onClose.subscribe(closed => console.log('closed'));
  }

  showCustom() {
    this.message.success('Hoàn thành!', { duration: 5000 });
  }
}
```

## Notes

- Message hiển thị ở đầu trang (top-center), ngắn gọn và nhanh chóng
- `loading()` auto-closes sau 3000ms theo mặc định — để persistent, truyền `{ duration: 0 }` và gọi `this.message.remove(ref.messageId)` để đóng thủ công
- Mặc định message hiển thị 3000ms rồi tự đóng
- `pauseOnHover` mặc định `true` — timer tạm dừng khi hover
- Message khác Notification: Message ở top-center, Notification ở góc — chọn theo UX context
- `content` hỗ trợ cả string và TemplateRef<void>
- Service được inject tự động (providedIn: 'root')
