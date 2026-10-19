# Typography

Thành phần typography dùng để hiển thị văn bản với các tính năng mở rộng như copy, edit, ellipsis. Hỗ trợ nhiều selector khác nhau cho các thẻ HTML tiêu biểu.

**Selector:** `tds-typography`, `[tds-typography]`, `p[tds-paragraph]`, `span[tds-text]`, `h1[tds-title]`, `h2[tds-title]`, `h3[tds-title]`, `h4[tds-title]`
**Import:** `import { TDSTypographyModule } from 'tds-ui/typography';`
**Export as:** `tdsTypography`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsContent` | `string` | `undefined` | Nội dung văn bản hiển thị |
| `tdsType` | `'secondary' \| 'warning' \| 'error' \| 'success'` | `undefined` | Kiểu màu sắc văn bản |
| `tdsCopyable` | `boolean` | `false` | Cho phép copy nội dung |
| `tdsEditable` | `boolean` | `false` | Cho phép sửa nội dung |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa typography |
| `tdsExpandable` | `boolean` | `false` | Cho phép mở rộng khi bị ellipsis |
| `tdsEllipsis` | `boolean` | `false` | Hiển thị ellipsis khi văn bản quá dài |
| `tdsEllipsisRows` | `number` | `1` | Số dòng hiển thị trước khi ellipsis |
| `tdsCopyText` | `string` | `undefined` | Text để copy (mặc định là `tdsContent`) |
| `tdsSuffix` | `string` | `undefined` | Hậu tố hiển thị sau nội dung |
| `tdsCopyTooltips` | `[TDSTSType, TDSTSType]` | `undefined` | Tooltip cho nút copy `[before, after]` |
| `tdsCopyIcons` | `[TDSTSType, TDSTSType]` | `['tdsi-copy-fill', 'tdsi-check-fill']` | Icon cho nút copy `[before, after]` |
| `tdsEditTooltip` | `TDSTSType` | `undefined` | Tooltip cho nút edit |
| `tdsEditIcon` | `TDSTSType` | `'tdsi-edit-fill'` | Icon cho nút edit |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsContentChange` | `EventEmitter<string>` | Phát sinh khi nội dung thay đổi (khi edit) |
| `tdsCopy` | `EventEmitter<string>` | Phát sinh khi copy text |
| `tdsExpandChange` | `EventEmitter<void>` | Phát sinh khi mở rộng ellipsis |
| `tdsOnEllipsis` | `EventEmitter<boolean>` | Phát sinh khi trạng thái ellipsis thay đổi |

## Usage

```html
<!-- Text thường với màu -->
<span tds-typography tdsType="secondary">Text màu secondary</span>
<p tds-paragraph tdsType="error">Lỗi: Không thể kết nối</p>

<!-- Copyable text -->
<span tds-typography [tdsCopyable]="true" tdsContent="Copy me!">
  Copy this text
</span>

<!-- Editable text -->
<span tds-typography [tdsEditable]="true" [(tdsContent)]="text">
  Click để sửa
</span>

<!-- Ellipsis với expand -->
<p tds-paragraph
   [tdsEllipsis]="true"
   [tdsEllipsisRows]="3"
   [tdsExpandable]="true">
  Văn bản dài sẽ bị cắt sau 3 dòng và hiển thị nút mở rộng...
</p>

<!-- Kết hợp nhiều tính năng -->
<p tds-paragraph
   tdsType="success"
   [tdsCopyable]="true"
   [tdsEditable]="true"
   [tdsEllipsis]="true"
   [tdsEllipsisRows]="2"
   [tdsCopyTooltips]="['Copy', 'Copied!']"
   [(tdsContent)]="myText">
  {{ myText }}
</p>

<!-- Title -->
<h1 tds-title tdsType="secondary">Tiêu đề cấp 1</h1>
```

```typescript
import { TDSTypographyModule } from 'tds-ui/typography';

@Component({
  standalone: true,
  imports: [TDSTypographyModule],
})
export class MyComponent {
  myText = 'Nội dung có thể chỉnh sửa';
  text = 'Text ban đầu';

  onContentChange(text: string): void {
    console.log('Nội dung mới:', text);
  }

  onCopy(text: string): void {
    console.log('Đã copy:', text);
  }
}
```

## Notes

- **Ellipsis tự động**: Component tự động dùng CSS ellipsis nếu có thể, nếu không sẽ dùng JavaScript để tính toán
- **RTL support**: Component hỗ trợ ngôn ngữ RTL (Right-to-Left)
- **Responsive**: Tự động cập nhật ellipsis khi resize window
- **Các component liên quan**: `TDSTextCopyModule`, `TDSTextEditModule` - được sử dụng nội bộ bởi `TDSTypographyModule`
- **Styling**: Các class CSS được thêm vào host element dựa trên `tdsType` để style màu sắc: `.tds-typography-secondary`, `.tds-typography-warning`, `.tds-typography-danger`, `.tds-typography-success`, `.tds-typography-disabled`
