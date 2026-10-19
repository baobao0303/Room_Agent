# Button Split

Nút chia đôi với hành động chính và menu dropdown. Kết hợp button và dropdown trong một component.

**Selector:** `tds-button-split`
**Import:** `import { TDSButtonSplit } from 'tds-ui/button-split';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | `TDSThemePalette` | `'primary'` | Màu sắc: `primary`, `secondary` |
| `size` | `ButtonSize` | `'md'` | Kích thước: `sm`, `md`, `lg` |
| `disabled` | `boolean` | `false` | Vô hiệu hóa button |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `clickButton` | `EventEmitter<MouseEvent>` | Click event từ button chính (không emit khi disabled) |

## Usage

```html
<tds-button-split color="primary" (clickButton)="onMainAction()">
  <div class="js-label">Lưu</div>
  <tbutton-menu class="js-content">
    <button tds-menu-item (click)="onSaveDraft()">Lưu nháp</button>
    <button tds-menu-item (click)="onSaveTemplate()">Lưu mẫu</button>
  </tbutton-menu>
</tds-button-split>

<!-- Secondary color -->
<tds-button-split color="secondary" size="lg">
  <div class="js-label">Xuất dữ liệu</div>
  <tbutton-menu class="js-content">
    <button tds-menu-item (click)="exportPDF()">PDF</button>
    <button tds-menu-item (click)="exportExcel()">Excel</button>
  </tbutton-menu>
</tds-button-split>

<!-- Disabled -->
<tds-button-split [disabled]="!hasPermission">
  <div class="js-label">Tác vụ</div>
  <tbutton-menu class="js-content">
    <button tds-menu-item>Option 1</button>
    <button tds-menu-item>Option 2</button>
  </tbutton-menu>
</tds-button-split>
```

```typescript
import { TDSButtonSplit } from 'tds-ui/button-split';
import { TDSButtonMenuModule } from 'tds-ui/button-menu';

@Component({
  standalone: true,
  imports: [TDSButtonSplit, TDSButtonMenuModule],
})
export class MyComponent {
  onMainAction() {
    // Xử lý hành động chính
  }

  onSaveDraft() {
    // Xử lý lưu nháp
  }

  onSaveTemplate() {
    // Xử lý lưu mẫu
  }

  hasPermission = true;
}
```

## Notes

- Sử dụng `.js-label` class để định nghĩa nội dung button chính
- Sử dụng `.js-content` class để định nghĩa nội dung dropdown menu
- Component kết hợp `TDSButtonMenuModule` để hiển thị menu dropdown
- Button bên trái thực thi hành động chính, button bên phải mở menu dropdown
- Khi `disabled=true`, cả hai button đều bị vô hiệu hóa
- Icon dropdown sử dụng `tdsi-arrow-down-fill`
