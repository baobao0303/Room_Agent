# Popconfirm

Hộp thoại xác nhận nhỏ gọn hiển thị khi click vào element. Kế thừa từ `TDSTooltipBaseDirective`, hỗ trợ đầy đủ tính năng tooltip với thêm nút OK/Cancel.

**Selector:** `[tds-popconfirm]`
**Import:** `import { TDSPopconfirmDirective, TDSPopconfirmModule } from 'tds-ui/popconfirm';`
**Export as:** `tdsPopconfirm`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsPopconfirmTitle` | `string \| TemplateRef` | — | Tiêu đề popconfirm |
| `tdsPopconfirmTitleContext` | `object \| null` | `null` | Context cho template title |
| `tdsPopconfirmContent` | `string \| TemplateRef` | — | Nội dung mô tả |
| `tdsPopconfirmContentContext` | `object \| null` | `null` | Context cho template content |
| `tdsPopconfirmTrigger` | `'click' \| 'hover' \| 'focus'` | `'click'` | Cách kích hoạt |
| `tdsPopconfirmPlacement` | `string \| string[]` | `'top'` | Vị trí hiển thị |
| `tdsPopconfirmVisible` | `boolean` | — | Điều khiển hiển thị |
| `tdsPopconfirmAutoClose` | `boolean` | `true` | Tự đóng khi click outside |
| `tdsPopconfirmEnableToggle` | `boolean` | `true` | Cho phép toggle |
| `tdsOkText` | `string \| null` | — | Text nút OK (null = dùng i18n) |
| `tdsCancelText` | `string \| null` | — | Text nút Cancel (null = dùng i18n) |
| `tdsOkType` | `string` | `'primary'` | Loại button OK |
| `tdsOkButtonProps` | `TDSPopConfirmButtonProps \| null` | — | Props tùy chỉnh cho nút OK |
| `tdsCancelButtonProps` | `TDSPopConfirmButtonProps \| null` | — | Props tùy chỉnh cho nút Cancel |
| `tdsBeforeConfirm` | `() => Observable<boolean> \| Promise<boolean> \| boolean` | — | Async validation trước khi confirm |
| `tdsCondition` | `boolean` | `false` | Nếu true, skip popconfirm và confirm trực tiếp |
| `tdsPopconfirmIcon` | `string \| TemplateRef` | `'tdsi-warning-1-fill'` | Icon hiển thị |
| `tdsPopconfirmShowArrow` | `boolean` | `true` | Hiển thị mũi tên |
| `tdsPopconfirmBackdrop` | `boolean` | `false` | Hiển thị backdrop overlay |
| `tdsAutofocus` | `null \| 'ok' \| 'cancel'` | `null` | Focus tự động vào nút |
| `tdsPopconfirmOverlayClassName` | `string` | — | Class tùy chỉnh cho overlay |
| `tdsPopconfirmOverlayStyle` | `NgStyleInterface` | — | Style tùy chỉnh cho overlay |
| `tdsPopconfirmMouseEnterDelay` | `number` | — | Delay khi hover (ms) |
| `tdsPopconfirmMouseLeaveDelay` | `number` | — | Delay khi leave (ms) |
| `tdsPopconfirmOrigin` | `ElementRef<HTMLElement>` | — | Origin element tùy chỉnh |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsPopconfirmVisibleChange` | `EventEmitter<boolean>` | Emit khi trạng thái hiển thị thay đổi |
| `tdsOnConfirm` | `EventEmitter<void>` | Emit khi nhấn nút OK |
| `tdsOnCancel` | `EventEmitter<void>` | Emit khi nhấn nút Cancel |

## Usage

```html
<!-- Basic usage -->
<button tds-popconfirm
  tdsPopconfirmTitle="Xác nhận xóa"
  tdsPopconfirmContent="Bạn có chắc muốn xóa mục này?"
  (tdsOnConfirm)="deleteItem()">
  Xóa
</button>

<!-- Custom buttons text -->
<button tds-popconfirm
  tdsPopconfirmTitle="Export data"
  tdsPopconfirmContent="This will export all data to CSV"
  [tdsOkText]="'Export'"
  [tdsCancelText]="'Cancel'"
  (tdsOnConfirm)="exportData()">
  Export
</button>

<!-- Async confirmation -->
<button tds-popconfirm
  tdsPopconfirmTitle="Submit approval"
  tdsPopconfirmContent="This action cannot be undone"
  [tdsBeforeConfirm]="checkBeforeSubmit"
  [tdsOkButtonProps]="{ loading: isSubmitting }"
  (tdsOnConfirm)="submitApproval()">
  Submit
</button>

<!-- Custom icon và arrow -->
<button tds-popconfirm
  tdsPopconfirmTitle="Warning"
  tdsPopconfirmContent="Please read carefully"
  [tdsPopconfirmIcon]="'tdsi-error-warning-fill'"
  [tdsPopconfirmShowArrow]="false">
  Show Warning
</button>

<!-- With backdrop -->
<button tds-popconfirm
  tdsPopconfirmTitle="Critical action"
  tdsPopconfirmContent="This will affect all users"
  [tdsPopconfirmBackdrop]="true"
  (tdsOnConfirm)="executeCriticalAction()">
  Execute
</button>

<!-- Auto focus OK button -->
<button tds-popconfirm
  tdsPopconfirmTitle="Confirm"
  tdsPopconfirmContent="Are you sure?"
  [tdsAutofocus]="'ok'">
  Focus OK
</button>

<!-- Skip popconfirm conditionally -->
<button tds-popconfirm
  tdsPopconfirmTitle="Delete"
  [tdsCondition]="!isProtected"
  (tdsOnConfirm)="deleteItem()">
  Delete
</button>
```

```typescript
import { TDSPopconfirmDirective, TDSPopconfirmModule } from 'tds-ui/popconfirm';
import { wrapIntoObservable } from 'tds-ui/core/util';

@Component({
  standalone: true,
  imports: [TDSPopconfirmModule],
})
export class MyComponent {
  isSubmitting = false;
  isProtected = false;

  deleteItem() {
    console.log('Item deleted');
  }

  checkBeforeConfirm(): Observable<boolean> {
    // Async validation logic
    return this.service.validate().pipe(
      map(result => result.isValid)
    );
  }

  checkBeforeSubmit() {
    // Can return Observable, Promise, or boolean
    return this.service.canSubmit();
  }

  exportData() {
    console.log('Exporting data...');
  }
}
```

## Notes

- Kế thừa tất cả tính năng từ `TDSTooltipBaseDirective`: placement, trigger, visible control, etc.
- Dùng `tdsBeforeConfirm` cho async validation (API call, form validation, etc.)
- `tdsCondition` hữu ích để tắt popconfirm cho các action an toàn (như item protected)
- `TDSPopConfirmButtonProps` là `Partial<TDSButtonProps>` — có thể truyền bất kỳ props nào của TDS button
- Text mặc định cho buttons lấy từ i18n (`Popconfirm.okText`, `Popconfirm.cancelText`)
- Khi `tdsBeforeConfirm` trả về `false`, popconfirm không đóng
- Focus tự động trả về element trước khi mở popconfirm khi đóng
- Hỗ trợ RTL layout
