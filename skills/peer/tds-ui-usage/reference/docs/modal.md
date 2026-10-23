# Modal

Dialog overlay. Dùng `TDSModalService` để mở programmatically, hoặc `tds-modal` component trong template.

**Selector:** `tds-modal`
**Import:** `import { TDSModalModule, TDSModalService } from 'tds-ui/modal';`
**Export as:** `tdsModal`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `visible` | `boolean` | `false` | Hiển thị/ẩn modal |
| `content` | `string \| TemplateRef \| Type<T>` | — | Nội dung modal |
| `title` | `string \| TemplateRef<{}>` | — | Tiêu đề |
| `footer` | `string \| TemplateRef<{}> \| Array<ModalButtonOptions<T>> \| null` | — | Footer tùy chỉnh (null = ẩn) |
| `closable` | `boolean` | `true` | Hiển thị nút X |
| `mask` | `boolean` | — | Hiển thị overlay |
| `maskClosable` | `boolean` | — | Đóng khi click mask |
| `closeOnNavigation` | `boolean` | — | Đóng khi navigate |
| `keyboard` | `boolean` | `true` | Đóng bằng ESC |
| `noAnimation` | `boolean` | `false` | Tắt animation |
| `centered` | `boolean` | `false` | Căn giữa modal |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| null` | `null` | Preset size (sm: 300px, md: 500px, lg: 800px, xl: 1140px) |
| `autoClose` | `boolean` | — | Tự đóng sau khi OK |
| `okText` | `string \| null` | — | Text nút xác nhận |
| `cancelText` | `string \| null` | — | Text nút hủy |
| `okType` | `'default' \| 'primary' \| 'dashed' \| 'danger' \| 'link' \| 'text' \| null` | `'primary'` | Loại button OK |
| `okDanger` | `boolean` | `false` | Highlight OK button đỏ |
| `okLoading` | `boolean` | `false` | Hiển thị loading trên nút OK |
| `okDisabled` | `boolean` | `false` | Vô hiệu hóa nút OK |
| `cancelLoading` | `boolean` | `false` | Hiển thị loading trên nút Hủy |
| `cancelDisabled` | `boolean` | `false` | Vô hiệu hóa nút Hủy |
| `closeIcon` | `string \| TemplateRef<void>` | `'close'` | Icon đóng |
| `iconType` | `string` | `'question-circle'` | Icon loại (Confirm Modal ONLY) |
| `modalType` | `'default' \| 'confirm'` | `'default'` | Loại modal |
| `autofocus` | `'ok' \| 'cancel' \| 'auto' \| null` | `null` | Tự động focus |
| `zindex` | `number` | `60` | Z-index của modal |
| `wrapClassName` | `string` | — | CSS class cho wrapper |
| `className` | `string` | — | CSS class cho modal |
| `style` | `object` | — | CSS style cho modal |
| `maskStyle` | `StyleObjectLike` | — | CSS style cho mask |
| `bodyStyle` | `StyleObjectLike` | — | CSS style cho body |
| `componentParams` | `T` | — | Params truyền vào component (deprecated) |
| `width` | `number \| string` | `500` | Chiều rộng modal |
| `confirmViewType` | `'default' \| 'compact'` | `'default'` | Kiểu hiển thị confirm modal |
| `confirmIcon` | `string \| TemplateRef<void>` | — | Icon tùy chỉnh cho confirm modal |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `onOk` | `EventEmitter<T> \| OnClickCallback<T>` | Khi nhấn OK |
| `onCancel` | `EventEmitter<T> \| OnClickCallback<T>` | Khi nhấn Hủy |
| `onAfterOpen` | `EventEmitter<void>` | Sau khi modal mở |
| `onAfterClose` | `EventEmitter<R>` | Sau khi modal đóng |
| `visibleChange` | `EventEmitter<boolean>` | Khi visible thay đổi |

## TDSModalService Methods

| Method | Description |
|--------|-------------|
| `create<T>(config: ModalOptions)` | Mở modal tùy chỉnh, trả về `TDSModalRef` |
| `confirm(options)` | Modal xác nhận |
| `info(options)` | Modal thông tin |
| `success(options)` | Modal thành công |
| `warning(options)` | Modal cảnh báo |
| `error(options)` | Modal lỗi |
| `closeAll()` | Đóng tất cả modal đang mở |

## TDSModalRef

```typescript
const ref = modalService.create({ ... });
ref.afterClose.subscribe(result => { /* result từ modal */ });
ref.afterOpen.subscribe(() => { /* ... */ });
ref.close(result);      // đóng và trả về result
ref.destroy(result);    // alias cho close(result)
ref.triggerOk();        // kích hoạt onOk callback
ref.triggerCancel();    // kích hoạt onCancel callback
ref.getContentComponent(); // lấy instance của content component
ref.updateConfig(newConfig); // cập nhật config
```

## Usage

### Confirm modal (info, success, error, warning)

```typescript
import { TDSModalService, TDSModalModule } from 'tds-ui/modal';

@Component({ standalone: true, imports: [TDSModalModule] })
export class MyComponent {
  constructor(private modal: TDSModalService) {}

  showInfo() {
    this.modal.info({
      title: 'Thông báo',
      content: 'Dữ liệu đã được lưu thành công.',
      okText: 'Đã hiểu',
      onOk: () => console.log('OK'),
    });
  }

  showError() {
    this.modal.error({
      title: 'Lỗi',
      content: 'Không thể kết nối đến server.',
      okText: 'Thử lại',
      onOk: () => this.retry(),
    });
  }

  showWarning() {
    this.modal.warning({
      title: 'Cảnh báo',
      content: 'Phiên bản này đã bị khóa.',
      okText: 'Đóng',
    });
  }

  showSuccess() {
    this.modal.success({
      title: 'Thành công',
      content: 'Đã cập nhật thông tin.',
      okText: 'OK',
    });
  }

  // Xác nhận với 2 nút (OK + Hủy)
  showConfirm() {
    this.modal.confirm({
      title: 'Xác nhận xóa',
      content: 'Bạn có chắc muốn xóa mục này?',
      okText: 'Xóa',
      cancelText: 'Hủy',
      onOk: () => this.deleteItem(),
    });
  }
}
```

### Confirm compact view

Thêm `confirmViewType: 'compact'` để hiển thị confirm nhỏ gọn hơn:

```typescript
this.modal.info({
  title: 'Thông báo',
  content: 'Dữ liệu đã được cập nhật.',
  okText: 'Đã hiểu',
  cancelText: 'Hủy',
  confirmViewType: 'compact',
});
```

### Confirm với custom icon

Dùng `confirmIcon` để thay icon mặc định. Hỗ trợ string (CSS class) hoặc TemplateRef:

```typescript
// Dùng icon class
this.modal.error({
  title: 'Lỗi xác thực',
  content: 'Token đã hết hạn.',
  confirmIcon: 'tdsi-lock-fill',
});

// Dùng template (SVG, icon phức tạp)
@ViewChild('customIcon') customIcon!: TemplateRef<void>;

this.modal.success({
  title: 'Thành công',
  content: 'Đã hoàn tất.',
  confirmIcon: this.customIcon,
});
```

```html
<ng-template #customIcon>
  <i class="tdsi-check-circle-fill tds-color-text-success"></i>
</ng-template>
```

### Custom modal (component content)

```typescript
openCustomModal() {
  const ref = this.modal.create({
    content: MyCustomComponent,
    title: 'Tiêu đề',
    width: 600,
    tdsData: { id: 123 },
    footer: null,
  });
  ref.afterClose.subscribe(result => console.log(result));
}
```
```

Template usage:
```html
<tds-modal
  [(visible)]="isVisible"
  title="Tiêu đề"
  (onCancel)="handleCancel()"
  (onOk)="handleOk()">
  <ng-container *tdsModalContent>
    <p>Nội dung modal</p>
  </ng-container>
</tds-modal>
```

In content component, receive data via injection:
```typescript
import { TDS_MODAL_DATA, TDSModalRef } from 'tds-ui/modal';
import { inject } from '@angular/core';

@Component({ standalone: true })
export class MyCustomComponent {
  data = inject(TDS_MODAL_DATA) as { id: number };
  modalRef = inject(TDSModalRef);

  close() { this.modalRef.close({ saved: true }); }
}
```

## Notes

- `TDSModalService` KHÔNG có `providedIn: 'root'` — bắt buộc import `TDSModalModule` vào `imports: []` để inject service
- Dùng `footer: null` để ẩn footer mặc định và tự xây dựng footer trong content component
- `size` preset: sm (300px), md (500px), lg (800px), xl (1140px)
- `modalType: 'confirm'` cho confirm dialog với icon
- Confirm modal mặc định dùng locale tiếng Việt: nút OK = "Đồng ý", nút Hủy = "Hủy"
- `info()`, `success()`, `error()`, `warning()` tự ẩn nút Hủy (set `cancelText = null`). `confirm()` hiện cả 2 nút
- Confirm modal hỗ trợ `footer` (string/template/array) để tùy chỉnh buttons
