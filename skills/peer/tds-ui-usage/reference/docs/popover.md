# Popover

Overlay với title, content và footer — phức tạp hơn tooltip, hỗ trợ backdrop và footer.

**Selector:** `[tds-popover]`, `tds-popover`
**Import:** `import { TDSPopoverDirective, TDSPopoverModule } from 'tds-ui/popover';`
**Export as:** `tdsPopover`, `tdsPopoverComponent`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `popoverTitle` | `string \| TemplateRef` | — | Tiêu đề popover |
| `popoverContent` | `string \| TemplateRef` | — | Nội dung chính popover |
| `popoverFooter` | `string \| TemplateRef` | — | Footer popover (thường chứa actions) |
| `tds-popover` | `string \| TemplateRef` | — | Alias của popoverTitle |
| `popoverTrigger` | `'hover' \| 'focus' \| 'click' \| null` | `'hover'` | Cách kích hoạt popover |
| `popoverPlacement` | `string \| string[]` | `'top'` | Vị trí: `top`, `bottom`, `left`, `right`, `topLeft`, `topRight`, `bottomLeft`, `bottomRight`, `leftTop`, `leftBottom`, `rightTop`, `rightBottom` |
| `popoverOrigin` | `ElementRef<HTMLElement>` | — | Element gốc để định vị (mặc định là element có directive) |
| `popoverVisible` | `boolean` | — | Controlled visibility |
| `popoverMouseEnterDelay` | `number` | `0.15` | Delay khi hover vào (giây) |
| `popoverMouseLeaveDelay` | `number` | `0.1` | Delay khi hover ra (giây) |
| `popoverOverlayClassName` | `string` | — | CSS class cho overlay popover |
| `popoverOverlayStyle` | `NgStyleInterface` | — | Inline style cho overlay popover |
| `popoverBackdrop` | `boolean` | `false` | Hiển thị backdrop (chỉ hoạt động với trigger='click') |
| `popoverAutoClose` | `boolean` | `true` | Tự động đóng khi click outside |
| `popoverOverlayClickable` | `boolean` | `true` | Cho phép click vào overlay |
| `popoverEnableToggle` | `boolean` | `true` | Bật tính năng toggle khi click (chỉ với trigger='click') |
| `popoverArrowPointAtCenter` | `boolean` | — | Arrow chỉ vào giữa element gốc |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `popoverVisibleChange` | `EventEmitter<boolean>` | Emit khi popover mở/đóng |

## Usage

```html
<!-- Basic popover với string content -->
<button tds-popover
  popoverTitle="Thông tin"
  popoverContent="Nội dung chi tiết về popover"
  popoverTrigger="click">
  Xem chi tiết
</button>

<!-- Popover với template content và footer -->
<button tds-popover
  [popoverTitle]="titleTpl"
  [popoverContent]="contentTpl"
  [popoverFooter]="footerTpl"
  popoverTrigger="click"
  popoverPlacement="bottom">
  Menu Actions
</button>

<ng-template #titleTpl>
  <h3>Tiêu đề tùy chỉnh</h3>
</ng-template>

<ng-template #contentTpl>
  <div class="p-2">
    <p>Nội dung popover với HTML</p>
    <ul>
      <li>Item 1</li>
      <li>Item 2</li>
    </ul>
  </div>
</ng-template>

<ng-template #footerTpl>
  <div class="flex gap-2 justify-end">
    <button class="btn-secondary">Hủy</button>
    <button class="btn-primary">Xác nhận</button>
  </div>
</ng-template>

<!-- Popover với backdrop (modal-like) -->
<button tds-popover
  popoverTitle="Xác nhận xóa"
  popoverContent="Bạn có chắc muốn xóa item này không?"
  [popoverBackdrop]="true"
  [popoverAutoClose]="true"
  popoverTrigger="click">
  Xóa
</button>

<!-- Hover popover -->
<span tds-popover
  popoverTitle="Gợi ý"
  popoverContent="Di chuột vào để xem thông tin"
  popoverPlacement="top"
  popoverTrigger="hover">
  Hover me
</span>

<!-- Multiple placements -->
<button tds-popover
  popoverContent="Nội dung"
  [popoverPlacement]="['top', 'bottom', 'left', 'right']">
  Auto position
</button>

<!-- Controlled visibility -->
<button (click)="showPopover = !showPopover">Toggle</button>
<div tds-popover
  [popoverVisible]="showPopover"
  (popoverVisibleChange)="showPopover = $event"
  popoverContent="Controlled popover">
  Target
</div>
```

```typescript
import { TDSPopoverDirective, TDSPopoverModule } from 'tds-ui/popover';

@Component({
  standalone: true,
  imports: [TDSPopoverDirective, TDSPopoverModule],
})
export class MyComponent {
  showPopover = false;
}
```

## Notes

- **Popover vs Tooltip**: Popover phù hợp cho nội dung phức tạp, form, menu actions. Tooltip chỉ cho text ngắn.
- **Backdrop**: Chỉ hoạt động khi `popoverTrigger="click"`, tạo hiệu ứng modal.
- **Footer**: Thường dùng để chứa các action buttons (Confirm, Cancel, etc.)
- **Auto close**: Mặc định `true` — đóng khi click outside. Set `false` để giữ mở.
- **Toggle**: Với `trigger="click"` + `enableToggle="true"`, click lại để đóng.
- **Placement**: Hỗ trợ auto-adjust nếu không đủ không gian.
- **Standalone**: Cả directive và component đều standalone, không cần import module.
- **Delay defaults**: `popoverMouseEnterDelay` and `popoverMouseLeaveDelay` inherit from the base tooltip directive defaults (`0.15` and `0.1` seconds respectively) when not explicitly set.
