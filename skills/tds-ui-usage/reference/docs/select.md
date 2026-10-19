# Select

Dropdown chọn giá trị từ danh sách. Hỗ trợ single/multiple, search, virtual scroll, và grouping.

**Selector:** `tds-select`
**Import:** `import { TDSSelectModule } from 'tds-ui/select';`
**Export as:** `tdsSelect`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `data` | `Array<any> \| any` | `[]` | Dữ liệu options |
| `mode` | `TDSSelectModeType` | `'default'` | Chế độ chọn: `default`, `multiple`, `tags` |
| `textField` | `string` | `'lable'` | Field hiển thị label |
| `valueField` | `string` | `'value'` | Field dùng làm value |
| `disabledField` | `string` | `'disabled'` | Field kiểm tra disabled |
| `groupField` | `string` | `'group'` | Field nhóm (group options) |
| `placeholder` | `string` | — | Placeholder |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `required` | `boolean` | `false` | Bắt buộc nhập |
| `size` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `allowSearch` | `boolean` | `true` | Hiển thị ô tìm kiếm |
| `showSearch` | `boolean` | `true` | Hiển thị ô tìm kiếm |
| `allowClear` | `boolean` | `false` | Cho phép xóa giá trị đã chọn |
| `loading` | `boolean` | `false` | Trạng thái loading danh sách |
| `maxTagCount` | `number` | `Infinity` | Max tags hiển thị (multiple mode) |
| `maxMultipleCount` | `number` | `Infinity` | Max items chọn được (multiple mode) |
| `autoClose` | `boolean` | `false` | Tự động đóng sau chọn (multiple/tags mode) |
| `autoClearSearchValue` | `boolean` | `true` | Tự động xóa search value sau khi chọn |
| `open` | `boolean` | `false` | Mở/đóng dropdown |
| `autofocus` | `boolean` | `false` | Tự động focus khi init |
| `compareWith` | `(o1: any, o2: any) => boolean` | `(o1, o2) => o1 === o2` | Hàm so sánh giá trị |
| `filterOption` | `TDSFilterOptionType` | `TDSDefaultFilterOption` | Hàm filter options |
| `serverSearch` | `boolean` | `false` | Xử lý search phía server |
| `optionHeightPx` | `number` | `33` (sm: 29, md: 33, lg: 37, xl: 45) | Chiều cao mỗi option (px) |
| `optionOverflowSize` | `number` | `8` | Số option hiển thị trong viewport |
| `hideSelected` | `boolean` | `false` | Ẩn selected items khỏi dropdown |
| `border` | `boolean` | `true` | Hiển thị border |
| `valuePrimitive` | `boolean` | `true` | Value là primitive hay object |
| `classIcon` | `string \| null` | `'tdsi-chevron-down-fill'` | Icon cho dropdown arrow |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |
| `backdrop` | `boolean` | `false` | Hiển thị backdrop |
| `dropdownMatchSelectWidth` | `boolean` | `true` | Dropdown width bằng select width |
| `dropdownClassName` | `string \| null` | — | Custom class cho dropdown |
| `tokenSeparators` | `string[]` | `[]` | Token separators cho tags mode |
| `maxTagPlaceholder` | `TemplateRef<{ $implicit: any[] }> \| null` | `null` | Template cho tags vượt maxTagCount |
| `allowTagSpace` | `boolean` | `false` | Cho phép tag có space |
| `selectOnTab` | `boolean` | `false` | Chọn item khi nhấn Tab |
| `tdsBeforeValueChange` | `(action, listOfValue) => Observable<boolean> \| Promise<boolean> \| boolean \| null` | `null` | Callback trước khi thay đổi giá trị |
| `tdsGroupSettings` | `TDSSelectGroupSettings \| null` | `null` | Cấu hình grouping |
| `tdsCheckable` | `boolean` | `false` | Hiển thị checkbox trong options (multiple/tags mode) |
| `tdsCssOption` | `NgClassType \| null` | `null` | Custom CSS cho options |
| `tdsRemoveIcon` | `TemplateRef<any> \| null` | `null` | Icon remove |
| `tdsPrefix` | `TemplateRef<any> \| null` | `null` | Template prefix |
| `tdsCustomTemplate` | `TemplateRef<any> \| null` | `null` | Template tùy chỉnh |
| `id` | `string` | `tds-select-{n}` | ID của component |
| `userAriaDescribedBy` | `string` | — | ARIA described by |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `selectChange` | `EventEmitter<any>` | Khi giá trị thay đổi |
| `openChange` | `EventEmitter<boolean>` | Khi dropdown mở/đóng |
| `onSearch` | `EventEmitter<string>` | Khi search text thay đổi |
| `scrollToBottom` | `EventEmitter<void>` | Khi scroll đến cuối (lazy load) |
| `blurChange` | `EventEmitter<void>` | Khi blur |
| `focusChange` | `EventEmitter<void>` | Khi focus |
| `tdsClear` | `EventEmitter<void>` | Khi nhấn nút clear |

## Template Directives

| Directive | Selector | Description |
|-----------|----------|-------------|
| `TDSOptionTemplateDirective` | `[tds-option-tmp]` | Template tùy chỉnh cho option |
| `TDSOptgroupTemplateDirective` | `[tds-optgroup-tmp]` | Template tùy chỉnh cho option group |
| `TDSLabelTemplateDirective` | `[tds-label-tmp]` | Template tùy chỉnh cho label |
| `TDSHeaderTemplateDirective` | `[tds-header-tmp]` | Template cho header dropdown |
| `TDSFooterTemplateDirective` | `[tds-footer-tmp]` | Template cho footer dropdown |
| `TDSNotFoundTemplateDirective` | `[tds-notfound-tmp]` | Template khi không tìm thấy kết quả |
| `TDSTagTemplateDirective` | `[tds-tag-tmp]` | Template tùy chỉnh cho tag |
| `TDSTypeToSearchTemplateDirective` | `[tds-typetosearch-tmp]` | Template khi chưa nhập search |
| `TDSLoadingTextTemplateDirective` | `[tds-loadingtext-tmp]` | Template khi loading |
| `TDSLoadingSpinnerTemplateDirective` | `[tds-loadingspinner-tmp]` | Template cho loading spinner |
| `TDSItemLabelDirective` | `[tds-item-tmp]` | Template cho item label |
| `TDSMultiLabelTemplateDirective` | `[tds-multi-label-tmp]` | Template cho multi label |

## TDSSelectGroupSettings Interface

```typescript
interface TDSSelectGroupSettings {
  groupField: string;              // Field dùng để nhóm (mặc định: 'group')
  collapsedAll: boolean;           // Thu gọn tất cả groups (mặc định: false)
  expandedGroupValue: string;      // Group được mở rộng
  showSelectedCount?: boolean;     // Hiển thị số phần tử được chọn trong từng nhóm (mặc định: true)
  stickyGroupLabel?: boolean;      // Nhóm tiêu đề cố định khi cuộn (mặc định: true)
}
```

## Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `focus` | - | Focus vào select |
| `blur` | - | Blur select |
| `close` | - | Đóng dropdown |
| `onItemDelete` | `event: MouseEvent \| KeyboardEvent, item: TDSSelectItemInterface` | Xóa item |
| `onItemClick` | `value: any` | Chọn item |

## Usage

```html
<!-- Basic với ngModel -->
<tds-select
  [(ngModel)]="selectedId"
  [data]="statusList"
  textField="name"
  valueField="id"
  placeholder="Chọn trạng thái">
</tds-select>

<!-- Multiple mode -->
<tds-select
  mode="multiple"
  [(ngModel)]="selectedIds"
  [data]="tagList"
  textField="label"
  valueField="id"
  [allowSearch]="true">
</tds-select>

<!-- Tags mode -->
<tds-select
  mode="tags"
  [(ngModel)]="tags"
  [data]="tagList"
  placeholder="Nhập tag">
</tds-select>

<!-- Reactive Form -->
<tds-select 
  [formControl]="statusCtrl" 
  [data]="statusList">
</tds-select>

<!-- With server search -->
<tds-select
  [data]="filteredList"
  [serverSearch]="true"
  (onSearch)="onSearchChange($event)">
</tds-select>

<!-- Lazy load with scroll -->
<tds-select
  [data]="items"
  (scrollToBottom)="loadMore()">
</tds-select>

<!-- With custom templates -->
<tds-select [data]="users" textField="name" valueField="id">
  <ng-template tds-option-tmp let-item>
    <div class="user-option">
      <img [src]="item.avatar" class="avatar">
      <span>{{ item.name }}</span>
    </div>
  </ng-template>
  <ng-template tds-header-tmp>
    <div class="p-2 text-center text-muted">Danh sách users</div>
  </ng-template>
  <ng-template tds-notfound-tmp>
    <div class="p-2 text-center">Không tìm thấy kết quả</div>
  </ng-template>
</tds-select>

<!-- With grouping -->
<tds-select
  [data]="groupedData"
  [tdsGroupSettings]="groupSettings">
</tds-select>

<!-- With checkable (multiple mode) -->
<tds-select
  mode="multiple"
  [data]="items"
  [tdsCheckable]="true">
</tds-select>
```

```typescript
import { TDSSelect } from 'tds-ui/select';

@Component({
  standalone: true,
  imports: [TDSSelect, FormsModule, ReactiveFormsModule]
})
export class MyComponent {
  statusList = [
    { id: 1, name: 'Hoạt động' },
    { id: 0, name: 'Không hoạt động' },
  ];
  
  selectedId: number | null = null;
  statusCtrl = new FormControl(null);
  
  // Group settings
  groupSettings: TDSSelectGroupSettings = {
    groupField: 'category',
    collapsedAll: false,
    expandedGroupValue: 'active'
  };
  
  groupedData = [
    { id: 1, name: 'Option 1', category: 'active' },
    { id: 2, name: 'Option 2', category: 'active' },
    { id: 3, name: 'Option 3', category: 'inactive' },
  ];
  
  onSearchChange(text: string) {
    // Fetch từ server
  }
  
  loadMore() {
    // Load thêm items
  }
}
```

## Notes

- Mặc định field tìm kiếm là `textField`
- Dùng bên trong `tds-form-field` cho layout đồng bộ với các inputs khác
- `scrollToBottom` dùng để lazy load thêm data
- Có thể dùng `<tds-option>` tags hoặc `<tds-optgroup>` thay vì `data` nếu options là static
- `mode="tags"` cho phép tạo tag mới không có trong danh sách
- `valuePrimitive="false"` để lưu toàn bộ object thay vì chỉ ID
- `tdsGroupSettings` dùng để cấu hình grouping options
- `tdsCheckable="true"` hiển thị checkbox trong options (chỉ work với multiple/tags mode)
- `tdsBeforeValueChange` dùng để validate trước khi thay đổi giá trị, return false để hủy thay đổi
- Template directives dùng để tùy chỉnh giao diện của các phần trong select
- `allowTagSpace="true"` cho phép tag có khoảng trắng (mặc định: false)
- `selectOnTab="true"` cho phép chọn item khi nhấn Tab (mặc định: false)
- `tdsGroupSettings` and `tdsCheckable` are Angular signal-based inputs (`input()`) — use normal binding syntax `[tdsGroupSettings]="..."` and `[tdsCheckable]="true"`
