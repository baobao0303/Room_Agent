# Tour

Hướng dẫn người dùng qua các bước (tour guide) với backdrop, keyboard navigation, và nhiều tùy chọn hiển thị.

**Selector:** `tds-tour`, `[tds-tour-anchor]`
**Import:** `import { TDSTourModule, TDSTourService, TDSTourAnchorDirective } from 'tds-ui/tour';`
**Export as:** `TDSTourComponent`

## Key Inputs

### TDSTourModule (tds-tour)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsCurrentStep` | `TDSITourStepOption` | `required` | Step hiện tại |
| `tdsSteps` | `TDSITourStepOption[]` | `required` | Danh sách tất cả steps |
| `tdsTourAnchorFooterTemplate` | `TDSTSType` | `undefined` | Custom footer template |
| `tdsTourAnchorContentTemplate` | `TDSTSType` | `undefined` | Custom content template |
| `tdsTourAnchorTitleTemplate` | `TDSTSType` | `undefined` | Custom title template |

### TDSTourAnchorDirective ([tds-tour-anchor])

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTourAnchor` | `string` | `required` | ID của anchor (khớp với `anchorId` trong step config) |
| `tdsTourAnchorFooterTemplate` | `TDSTSType` | `undefined` | Custom footer template cho anchor này |
| `tdsTourAnchorContentTemplate` | `TDSTSType` | `undefined` | Custom content template cho anchor này |
| `tdsTourAnchorTitleTemplate` | `TDSTSType` | `undefined` | Custom title template cho anchor này |

### TDSITourStepOption (Step Configuration)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `stepId` | `number \| string` | `undefined` | ID của step |
| `anchorId` | `string` | `required` | ID khớp với `tdsTourAnchor` |
| `title` | `string` | `undefined` | Tiêu đề hiển thị |
| `content` | `string` | `undefined` | Nội dung mô tả |
| `route` | `string \| UrlSegment[]` | `undefined` | Route để navigate đến khi step hiển thị |
| `nextStep` | `number \| string` | `undefined` | Step ID để next (không theo thứ tự) |
| `prevStep` | `number \| string` | `undefined` | Step ID để prev (không theo thứ tự) |
| `prevBtnTitle` | `string` | `'Quay lại'` | Text nút Previous |
| `nextBtnTitle` | `string` | `'Tiếp theo'` | Text nút Next |
| `endBtnTitle` | `string` | `'Kết thúc'` | Text nút End |
| `prevBtnIcon` | `string` | `undefined` | Icon class cho nút Previous |
| `nextBtnIcon` | `string` | `undefined` | Icon class cho nút Next |
| `endBtnIcon` | `string` | `undefined` | Icon class cho nút End |
| `backdrop` | `boolean` | `false` | Hiển thị backdrop |
| `showArrow` | `boolean` | `true` | Hiển thị mũi tên chỉ đến anchor |
| `closable` | `boolean` | `true` | Hiển thị nút close |
| `showButton` | `boolean` | `true` | Hiển thị các nút điều khiển |
| `showProgress` | `boolean` | `true` | Hiển thị dots progress |
| `status` | `TDSTourStatus` | `'default'` | Trạng thái: `default`, `info`, `success`, `error`, `warning` |
| `scrollContainer` | `string \| HTMLElement` | `undefined` | Container để scroll (nếu cần) |
| `delayBeforeStepShow` | `number` | `undefined` | Delay trước khi hiển thị (ms) |
| `delayAfterNavigation` | `number` | `undefined` | Delay sau khi navigate (ms) |
| `nextOnAnchorClick` | `boolean` | `false` | Next step khi click vào anchor |
| `backdropConfig.offset` | `number` | `0` | Offset của backdrop (px) |
| `stepDimensions` | `{width?, minWidth?, maxWidth?}` | `undefined` | Kích thước của tour popup |

## Service Methods

### TDSTourService

| Method | Description |
|--------|-------------|
| `initialize(steps, stepDefaults)` | Khởi tạo tour với danh sách steps |
| `start()` | Bắt đầu tour từ đầu |
| `startAt(stepId)` | Bắt đầu tour từ step cụ thể |
| `next()` | Đi đến step tiếp theo |
| `prev()` | Quay lại step trước |
| `end()` | Kết thúc tour |
| `pause()` | Tạm dừng tour |
| `resume()` | Tiếp tục tour |
| `hasNext(step)` | Kiểm tra có step tiếp theo không |
| `hasPrev(step)` | Kiểm tra có step trước không |

## Usage

```typescript
import { TDSTourModule, TDSTourService, TDSTourAnchorDirective } from 'tds-ui/tour';
import { TDSITourStepOption } from 'tds-ui/tour';

@Component({
  standalone: true,
  imports: [TDSTourModule, TDSTourAnchorDirective],
})
export class MyComponent {
  tourSteps: TDSITourStepOption[] = [
    {
      stepId: 1,
      anchorId: 'tour-step-1',
      title: 'Chào mừng!',
      content: 'Đây là bước đầu tiên trong tour.',
      status: 'info'
    },
    {
      stepId: 2,
      anchorId: 'tour-step-2',
      title: 'Tính năng',
      content: 'Khám phá các tính năng chính.',
      prevBtnTitle: 'Trở về',
      nextBtnTitle: 'Tiếp tục'
    },
    {
      stepId: 3,
      anchorId: 'tour-step-3',
      title: 'Hoàn thành!',
      content: 'Bạn đã hoàn thành tour.',
      status: 'success',
      endBtnTitle: 'Bắt đầu sử dụng'
    }
  ];

  constructor(private tourService: TDSTourService) {
    this.tourService.initialize(this.tourSteps, {
      showArrow: true,
      closable: true,
      showButton: true
    });
  }

  startTour() {
    this.tourService.start();
  }
}
```

```html
<!-- Elements với tour anchor -->
<div class="feature-section">
  <h1 tds-tour-anchor="tour-step-1">Chào mừng</h1>
  <p>Giới thiệu về ứng dụng</p>
</div>

<div class="feature-section">
  <button tds-tour-anchor="tour-step-2">Tính năng</button>
  <p>Xem các tính năng chính</p>
</div>

<div class="feature-section">
  <div tds-tour-anchor="tour-step-3">Hoàn thành</div>
  <p>Bạn đã sẵn sàng!</p>
</div>

<!-- Nút start tour -->
<button (click)="startTour()">Bắt đầu tour</button>
```

```html
<!-- Custom templates -->
<div tds-tour-anchor="tour-custom"
  [tdsTourAnchorTitleTemplate]="customTitle"
  [tdsTourAnchorContentTemplate]="customContent"
  [tdsTourAnchorFooterTemplate]="customFooter">
  Custom Element
</div>

<ng-template #customTitle let-step>
  <div class="custom-title">
    <i class="tdsi-star-fill"></i>
    {{ step.title }}
  </div>
</ng-template>

<ng-template #customContent let-step>
  <div class="custom-content">
    <img [src]="step.image" />
    <p>{{ step.content }}</p>
  </div>
</ng-template>

<ng-template #customFooter let-step>
  <div class="custom-footer">
    <button tds-button (click)="tourService.next()">Skip</button>
  </div>
</ng-template>
```

## Notes

- **Bắt buộc import module với `forRoot()`**: `TDSTourModule.forRoot()` để inject service
- Mỗi `tds-tour-anchor` phải có `anchorId` khớp với step config
- Tour tự động tạo overlay với backdrop, có thể click backdrop để end tour
- Hỗ trợ keyboard navigation (ESC để end, arrows để navigate)
- Mặc định hiển thị progress dots ở footer
- Có thể custom hoàn toàn title, content, footer với templates
- `status` thay đổi màu sắc: `info` (xanh dương), `success` (xanh lá), `error` (đỏ), `warning` (vàng), `default` (xám)
- Support RTL (right-to-left)
- Responsive positioning với flexible connected overlay strategy
- **Inheritance**: `TDSITourStepOption` extends the base `IStepOption` interface from the underlying tour library, inheriting additional properties such as `disableScrollToAnchor`, `centerAnchorOnScroll`, `smoothScroll`, `enableBackdrop`, `isAsync`, `isOptional`, `disablePageScrolling`, `stepDimensions`, `popoverClass`, and more. See `tour.dto.ts` for the full list.
