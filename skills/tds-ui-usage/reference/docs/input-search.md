# Input Search

Input tìm kiếm với icon search tích hợp và nút xóa.

**Selector:** `tds-input-search`
**Import:** `import { TDSInputSearchModule } from 'tds-ui/input-search';`
**Export as:** `tdsInputSearch`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsPrefix` | `string \| TemplateRef<void> \| undefined` | `undefined` | Nội dung prefix (text hoặc template) |
| `tdsSuffix` | `string \| TemplateRef<void> \| undefined` | `undefined` | Nội dung suffix (text hoặc template) |
| `tdsPrefixIcon` | `string \| null` | `null` | Icon prefix (tên icon từ TDS icon set) |
| `tdsSuffixIcon` | `string \| null` | `null` | Icon suffix (tên icon từ TDS icon set) |
| `tdsAllowClear` | `boolean` | `true` | Hiển thị nút xóa khi có nội dung |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa input |
| `tdsAutoFocus` | `boolean` | `false` | Tự động focus khi component được khởi tạo |
| `tdsSize` | `ButtonSize` (`'sm' \| 'md' \| 'lg' \| 'xl'`) | `'md'` | Kích thước input |
| `tdsPlaceHolder` | `string` | `'Tìm kiếm'` | Placeholder text |
| `tdsInputValue` | `string \| null` | `null` | Giá trị input (two-way binding) |
| `tdsInputDebounce` | `number` | `300` | Thời gian debounce (ms) khi nhập |
| `tdsInputEventName` | `string \| null` | `null` | Tên sự kiện custom để lắng nghe (ví dụ: `'change'`, `'keydown'`) |
| `tdsVariant` | `TDSInputVariant` (`'outline' \| 'fill' \| 'flat' \| 'underline'`) | `'outline'` | Kiểu hiển thị |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsInputValueChange` | `EventEmitter<string>` | Phát ra khi giá trị input thay đổi |
| `tdsInputEventTriggered` | `EventEmitter<TDSInputSearchEventDTO>` | Phát ra khi sự kiện custom được kích hoạt ({ value, event }) |
| `tdsFocusChange` | `EventEmitter<boolean>` | Phát ra khi input thay đổi trạng thái focus |

## Usage

```html
<!-- Basic usage -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  tdsPlaceHolder="Tìm kiếm...">
</tds-input-search>

<!-- Với size và variant -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  tdsSize="lg"
  tdsVariant="fill">
</tds-input-search>

<!-- Custom prefix/suffix icons -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  tdsPrefixIcon="tdsi-filter-fill"
  tdsSuffixIcon="tdsi-setting-fill">
</tds-input-search>

<!-- Disabled -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  [tdsDisabled]="true">
</tds-input-search>

<!-- Auto focus -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  [tdsAutoFocus]="true">
</tds-input-search>

<!-- Với custom event và debounce -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  tdsInputEventName="change"
  [tdsInputDebounce]="500"
  (tdsInputEventTriggered)="handleSearch($event)">
</tds-input-search>

<!-- Không cho phép xóa -->
<tds-input-search
  [(tdsInputValue)]="searchText"
  [tdsAllowClear]="false">
</tds-input-search>
```

```typescript
import { TDSInputSearchModule } from 'tds-ui/input-search';

@Component({
  standalone: true,
  imports: [TDSInputSearchModule],
})
export class MyComponent {
  searchText = '';

  handleSearch(event: TDSInputSearchEventDTO) {
    console.log('Search value:', event.value);
    // Gọi API search với giá trị event.value
  }
}
```

## Notes

- Dùng `[(tdsInputValue)]` cho two-way binding — component không hỗ trợ `ngModel` hay `formControl`
- Icon prefix mặc định là `tdsi-search-fill` nếu không có prefix/suffix nào được cung cấp
- Nút xóa (clear button) chỉ hiển thị khi có nội dung và `tdsAllowClear = true`
- Hỗ trợ debounce để tối ưu performance khi nhập (mặc định 300ms)
- Hỗ trợ nhiều biến thể: outline (mặc định), fill, flat, underline
- Hỗ trợ các kích thước: sm, md (mặc định), lg, xl
- Placeholder mặc định là 'Tìm kiếm'
