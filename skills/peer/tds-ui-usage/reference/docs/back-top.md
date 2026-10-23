# Back Top

Nút quay lại đầu trang với hiệu ứng fade in/out khi scroll.

**Selector:** `tds-back-top`
**Export as:** `tdsBackTop`
**Import:** `import { TDSBackTopModule } from 'tds-ui/back-top';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsVisibilityHeight` | `number` | `400` | Chiều cao scroll để hiển thị nút |
| `tdsTarget` | `string \| HTMLElement` | `window` | Container để theo dõi scroll |
| `tdsStyle` | `NgClassType` | `undefined` | Custom style cho nút |
| `tdsDuration` | `number` | `450` | Thời gian scroll animation (ms) |
| `tdsTemplate` | `TemplateRef<void>` | `undefined` | Custom template cho nút |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsClick` | `EventEmitter<boolean>` | Khi click vào nút back top |

## Usage

```html
<!-- Basic back top -->
<tds-back-top></tds-back-top>

<!-- Custom visibility height -->
<tds-back-top [tdsVisibilityHeight]="200"></tds-back-top>

<!-- Custom target -->
<tds-back-top [tdsTarget]="'.scroll-container'"></tds-back-top>

<!-- Custom duration -->
<tds-back-top [tdsDuration]="1000"></tds-back-top>

<!-- Custom style -->
<tds-back-top [tdsStyle]="{ right: '20px', bottom: '20px' }"></tds-back-top>

<!-- Custom template -->
<ng-template #customBackTop>
  <button tds-button color="primary" class="back-top-btn">
    <i class="tdsi-arrow-up"></i>
    <span>Top</span>
  </button>
</ng-template>

<tds-back-top [tdsTemplate]="customBackTop"></tds-back-top>

<!-- Listen to click events -->
<tds-back-top (tdsClick)="onBackTopClick()"></tds-back-top>
```

```typescript
import { TDSBackTopModule } from 'tds-ui/back-top';
import { Component } from '@angular/core';

@Component({
  selector: 'app-back-top-demo',
  standalone: true,
  imports: [TDSBackTopModule],
  template: `
    <div class="scroll-container">
      <div class="long-content">
        <!-- Long content here -->
      </div>
      
      <!-- Basic usage -->
      <tds-back-top></tds-back-top>
      
      <!-- Custom style and visibility -->
      <tds-back-top
        [tdsVisibilityHeight]="300"
        [tdsDuration]="800"
        [tdsStyle]="{ right: '40px', bottom: '40px' }"
        (tdsClick)="handleBackTop()">
      </tds-back-top>
      
      <!-- Custom template -->
      <ng-template #customTemplate>
        <div class="custom-back-top">
          <button tds-button-icon color="secondary" size="large">
            <i class="tdsi-chevron-up"></i>
          </button>
        </div>
      </ng-template>
      
      <tds-back-top [tdsTemplate]="customTemplate"></tds-back-top>
    </div>
  `
})
export class BackTopDemoComponent {
  handleBackTop() {
    console.log('Back to top clicked!');
  }
}
```

## Notes

- Mặc định hiển thị sau khi scroll quá 400px
- Sử dụng icon `tdsi-back-to-top-fill` từ TDS icon set
- Có fade animation khi hiển thị/ẩn
- Tự động scroll về đầu trang với animation mượt mà
- Hỗ trợ RTL với class `tds-back-top-rtl`
- Có thể custom template hoàn toàn với `tdsTemplate`
- `tdsTarget` có thể là selector string hoặc HTMLElement
- `tdsDuration` điều khiển tốc độ scroll animation (ms)
