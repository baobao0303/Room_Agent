# Divider

Đường kẻ ngang hoặc dọc để phân chia nội dung, có thể kèm theo text.

**Selector:** `tds-divider`
**Import:** `import { TDSDividerModule } from 'tds-ui/divider';`
**Export as:** `tdsDivider`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsText` | `string \| TemplateRef<void>` | `undefined` | Text hiển thị ở giữa divider |
| `tdsType` | `'horizontal' \| 'vertical'` | `'horizontal'` | Kiểu divider: ngang hoặc dọc |
| `tdsOrientation` | `'left' \| 'right' \| 'center'` | `'center'` | Vị trí text khi có text |
| `tdsDashed` | `boolean` | `false` | Hiển thị đường nét đứt |
| `tdsPlain` | `boolean` | `false` | Text style plain (không background) |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |

## Key Outputs

Divider không có outputs. Đây là component hiển thị thuần túy.

## Usage

```html
<!-- Divider ngang cơ bản -->
<tds-divider></tds-divider>

<!-- Divider với text -->
<tds-divider tdsText="Thông tin"></tds-divider>

<!-- Divider với text căn trái -->
<tds-divider tdsText="Tiêu đề" tdsOrientation="left"></tds-divider>

<!-- Divider với text căn phải -->
<tds-divider tdsText="Kết thúc" tdsOrientation="right"></tds-divider>

<!-- Divider nét đứt -->
<tds-divider tdsDashed="true"></tds-divider>

<!-- Divider với text và dashed -->
<tds-divider tdsText="Hoặc" tdsDashed="true"></tds-divider>

<!-- Divider dọc -->
<div class="row">
  <span>Text 1</span>
  <tds-divider tdsType="vertical"></tds-divider>
  <span>Text 2</span>
  <tds-divider tdsType="vertical"></tds-divider>
  <span>Text 3</span>
</div>

<!-- Divider với plain text -->
<tds-divider tdsText="Plain Text" tdsPlain="true"></tds-divider>

<!-- Divider với theme -->
<tds-divider tdsText="Dark Theme" tdsTheme="dark"></tds-divider>
<tds-divider tdsText="Light Theme" tdsTheme="light"></tds-divider>

<!-- Divider với template -->
<tds-divider [tdsText]="customTemplate"></tds-divider>

<ng-template #customTemplate>
  <span style="color: red;">Custom Text</span>
</ng-template>
```

```typescript
import { TDSDividerModule } from 'tds-ui/divider';

@Component({
  standalone: true,
  imports: [TDSDividerModule],
})
export class MyComponent {
  // Divider tự thêm class CSS dựa trên inputs
}
```

## Notes

- `tdsType="horizontal"` (default): Đường kẻ ngang, thường dùng để phân chia các section
- `tdsType="vertical"`: Đường kẻ dọc, thường dùng để phân chia các item trên cùng dòng
- `tdsText` có thể là string hoặc `TemplateRef` cho custom content
- `tdsOrientation` chỉ hoạt động khi có `tdsText` và `tdsType="horizontal"`
- `tdsDashed="true"` hiển thị đường nét đứt thay vì đường liền
- `tdsPlain="true"` text không có background, phù hợp với style minimal
- Hỗ trợ 3 theme: `default`, `light`, `dark`
- Component rất nhẹ, không có logic phức tạp, chỉ hiển thị
- Auto thêm class CSS dựa trên inputs:
  - `.tds-divider-horizontal`
  - `.tds-divider-vertical`
  - `.tds-divider-with-text`
  - `.tds-divider-with-text-left/center/right`
  - `.tds-divider-dashed`
  - `.tds-divider-plain`
  - `.tds-divider-theme-default/light/dark`
