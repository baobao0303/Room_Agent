# Affix

Giữ nguyên phần tử cố định khi cuộn trang đến vị trí xác định.

**Selector:** `tds-affix`
**Export as:** `tdsAffix`
**Import:** `import { TDSAffixModule } from 'tds-ui/affix';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `offsetTop` | `null \| number` | `undefined` | Khoảng cách từ phía trên để kích hoạt affix |
| `offsetBottom` | `null \| number` | `undefined` | Khoảng cách từ phía dưới để kích hoạt affix |
| `tdsTarget` | `string \| Element \| Window` | `window` | Container để theo dõi scroll |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `affixChange` | `EventEmitter<boolean>` | Khi trạng thái affix thay đổi |

## Usage

```html
<!-- Basic affix with offset top -->
<tds-affix [offsetTop]="120">
  <button tds-button>Fixed Button</button>
</tds-affix>

<!-- Affix with offset bottom -->
<tds-affix [offsetBottom]="50">
  <div class="footer-bar">Footer Bar</div>
</tds-affix>

<!-- Affix with custom target -->
<tds-affix [offsetTop]="50" tdsTarget=".scroll-container">
  <div class="sidebar">Sidebar</div>
</tds-affix>

<!-- Listen to affix state changes -->
<tds-affix [offsetTop]="100" (affixChange)="onAffixChange($event)">
  <div>Sticky Header</div>
</tds-affix>
```

```typescript
import { TDSAffixModule } from 'tds-ui/affix';
import { Component } from '@angular/core';

@Component({
  selector: 'app-affix-demo',
  standalone: true,
  imports: [TDSAffixModule],
  template: `
    <tds-affix [offsetTop]="120" (affixChange)="isAffixed = $event">
      <div class="toolbar" [class.active]="isAffixed">
        Toolbar
      </div>
    </tds-affix>
  `
})
export class AffixDemoComponent {
  isAffixed = false;

  onAffixChange(affixed: boolean) {
    console.log('Affix state:', affixed);
  }
}
```

## Notes

- Chỉ nên set `offsetTop` hoặc `offsetBottom`, không nên dùng cả 2
- Mặc định `tdsTarget` là `window`, có thể thay đổi bằng selector string hoặc Element
- Khi phần tử được affix, class `tds-affix` và `fixed` được thêm vào
- Hỗ trợ RTL với class `tds-affix-rtl`
- Tự động tạo placeholder để giữ nguyên layout khi affix
