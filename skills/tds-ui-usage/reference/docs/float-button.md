# Float Button

> **WARNING: Shell component -- not fully implemented.**
> The component template is empty (renders nothing). Lifecycle hooks (`ngOnInit`, `ngOnDestroy`, `ngOnChanges`) are stubbed out with commented-out throw statements. Do not use this component in production until it is completed.

Nút floating action button với hỗ trợ badge hiển thị số lượng thông báo.

**Selector:** `tds-float-button`
**Export As:** `tdsFloatButton`
**Import:** `import { TDSFloatButtonModule } from 'tds-ui/float-button';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsBadge` | `number \| TemplateRef` | `undefined` | Số lượng hiển thị hoặc custom template cho badge |
| `tdsBadgeDot` | `boolean` | `undefined` | Hiển thị badge dạng chấm đỏ (không có số) |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| N/A | N/A | Không có outputs được định nghĩa |

## Usage

> The examples below show the intended API, but the component currently renders nothing (empty template). These are provided for reference only.

```html
<!-- Basic float button -->
<tds-float-button></tds-float-button>

<!-- With badge count -->
<tds-float-button [tdsBadge]="5"></tds-float-button>

<!-- With badge dot -->
<tds-float-button [tdsBadgeDot]="true"></tds-float-button>

<!-- With custom badge template -->
<ng-template #customBadge>
  <span class="custom-badge">NEW</span>
</ng-template>

<tds-float-button [tdsBadge]="customBadge"></tds-float-button>
```

```typescript
import { TDSFloatButtonModule } from 'tds-ui/float-button';
import { Component } from '@angular/core';

@Component({
  selector: 'app-float-button-demo',
  standalone: true,
  imports: [TDSFloatButtonModule],
  template: `
    <div class="demo-container">
      <!-- Basic usage -->
      <tds-float-button></tds-float-button>

      <!-- With notification count -->
      <tds-float-button [tdsBadge]="notificationCount"></tds-float-button>

      <!-- With badge dot -->
      <tds-float-button [tdsBadgeDot]="hasNewNotifications"></tds-float-button>
    </div>
  `
})
export class FloatButtonDemoComponent {
  notificationCount = 12;
  hasNewNotifications = true;
}
```

## Notes

- Component sử dụng `ChangeDetectionStrategy.OnPush` để tối ưu performance
- Hỗ trợ lifecycle hooks: `OnInit`, `OnDestroy`, `OnChanges` (currently stubbed out, not implemented)
- Có thể export component reference qua `exportAs: 'tdsFloatButton'` để sử dụng trong template

## Internal Types (not publicly exported)

The following interface exists in `types.ts` but is **not exported** from `public-api.ts`. It is internal and should not be used directly.

```typescript
interface TDSFloatButtonBadge {
  count?: number | TemplateRef<any>;
  dot?: boolean;
  color?: string;
}
```
