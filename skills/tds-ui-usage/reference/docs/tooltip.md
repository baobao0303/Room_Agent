# Tooltip

Hiển thị text tooltip khi hover/focus/click. Hỗ trợ màu sắc và kích thước tùy chỉnh.

**Selector:** `[tds-tooltip]`, `tds-tooltip`
**Import:** `import { TDSTooltipDirective, TDSToolTipModule } from 'tds-ui/tooltip';`
**Export as:** `tdsTooltip`, `TDSTooltipModule`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tooltipTitle` | `string \| TemplateRef` | — | Nội dung tooltip |
| `tds-tooltip` | `string \| TemplateRef` | — | Alias của tooltipTitle |
| `tooltipTrigger` | `'hover' \| 'focus' \| 'click' \| null` | `'hover'` | Cách kích hoạt tooltip |
| `tooltipPlacement` | `string \| string[]` | `'top'` | Vị trí: `top`, `bottom`, `left`, `right`, `topLeft`, `topRight`, `bottomLeft`, `bottomRight`, `leftTop`, `leftBottom`, `rightTop`, `rightBottom` |
| `tooltipOrigin` | `ElementRef<HTMLElement>` | — | Element gốc để định vị (mặc định là element có directive) |
| `tooltipVisible` | `boolean` | — | Controlled visibility |
| `tooltipMouseEnterDelay` | `number` | `0.15` | Delay khi hover vào (giây) |
| `tooltipMouseLeaveDelay` | `number` | `0.1` | Delay khi hover ra (giây) |
| `tooltipOverlayClassName` | `string` | — | CSS class cho overlay tooltip |
| `tooltipOverlayStyle` | `NgStyleInterface` | — | Inline style cho overlay tooltip |
| `tooltipColor` | `'info' \| 'success' \| 'error' \| 'warning'` | — | Màu sắc preset cho tooltip |
| `tooltipContentCss` | `NgClassInterface \| string` | — | CSS class tùy chỉnh cho content area |
| `tooltipArrowCss` | `NgClassInterface \| string` | — | CSS class tùy chỉnh cho arrow |
| `tooltipSize` | `'sm' \| 'md'` | `'md'` | Kích thước tooltip |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tooltipVisibleChange` | `EventEmitter<boolean>` | Emit khi tooltip mở/đóng |

## Usage

```html
<!-- Basic tooltip với string -->
<button [tds-tooltip]="'Lưu thay đổi'">Lưu</button>

<!-- Tooltip với template content -->
<span [tds-tooltip]="tipTpl">Hover me</span>
<ng-template #tipTpl>
  <div>
    <b>Chi tiết</b> hướng dẫn sử dụng
    <br>
    <small>Xem thêm tại docs</small>
  </div>
</ng-template>

<!-- Click trigger với màu sắc -->
<button tds-tooltip
  tooltipTitle="Thông tin chi tiết"
  tooltipTrigger="click"
  tooltipColor="info"
  tooltipPlacement="bottom">
  Thông tin
</button>

<!-- Tooltip với các màu sắc khác nhau -->
<button tds-tooltip tooltipTitle="Thành công" tooltipColor="success">Success</button>
<button tds-tooltip tooltipTitle="Lỗi" tooltipColor="error">Error</button>
<button tds-tooltip tooltipTitle="Cảnh báo" tooltipColor="warning">Warning</button>

<!-- Small size cho compact UI -->
<button tds-tooltip
  tooltipTitle="Xóa"
  tooltipSize="sm"
  tooltipColor="error">
  <span class="icon-delete"></span>
</button>

<!-- Custom style với contentCss và arrowCss -->
<button tds-tooltip
  tooltipTitle="Custom styled"
  tooltipContentCss="{'bg-purple-100': true, 'text-purple-800': true}"
  tooltipArrowCss="{'border-purple-100': true}">
  Custom
</button>

<!-- Multiple placements (auto-adjust) -->
<button tds-tooltip
  tooltipTitle="Auto position"
  [tooltipPlacement]="['top', 'bottom', 'left', 'right']">
  Auto
</button>

<!-- Focus trigger (cho form inputs) -->
<input tds-tooltip
  tooltipTitle="Nhập email hợp lệ"
  tooltipTrigger="focus"
  tooltipPlacement="right">

<!-- Controlled visibility programmatically -->
<button (click)="showTip = !showTip">Toggle Tooltip</button>
<div [tds-tooltip]="'Controlled'"
  [tooltipVisible]="showTip"
  (tooltipVisibleChange)="showTip = $event"
  tooltipTrigger="null">
  Target
</div>

<!-- Tooltip with overlay style -->
<button tds-tooltip
  tooltipTitle="Styled tooltip"
  [tooltipOverlayStyle]="{'max-width': '300px', 'font-size': '14px'}">
  Wide tooltip
</button>
```

```typescript
import { TDSTooltipDirective, TDSToolTipModule } from 'tds-ui/tooltip';

@Component({
  standalone: true,
  imports: [TDSTooltipDirective, TDSToolTipModule],
})
export class MyComponent {
  showTip = false;
}
```

## Notes

- **Tooltip vs Popover**: Dùng Tooltip cho text ngắn. Dùng Popover cho nội dung phức tạp với footer/actions.
- **Trigger types**:
  - `hover` (default): Hiện khi hover, ẩn khi leave
  - `focus`: Hiện khi focus (thích hợp cho form inputs)
  - `click`: Hiện khi click
  - `null`: Hoàn toàn controlled via `tooltipVisible` input
- **Color presets**: `info` (xanh dương), `success` (xanh lá), `error` (đỏ), `warning` (vàng)
- **Sizes**: `sm` (nhỏ gọn), `md` (mặc định)
- **Custom styling**: Dùng `tooltipContentCss` và `tooltipArrowCss` để customize style riêng.
- **Delay**: `mouseEnterDelay` và `mouseLeaveDelay` tính bằng giây (không phải ms).
- **Placement auto-adjust**: Tooltip tự động đổi vị trí nếu không đủ không gian.
- **Standalone**: Directive và component đều standalone, không cần import module.
