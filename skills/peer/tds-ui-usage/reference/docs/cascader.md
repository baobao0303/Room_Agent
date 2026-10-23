# Cascader

Chọn dữ liệu phân cấp (danh mục, địa chỉ...).

**Selector:** `tds-cascader`, `[tds-cascader]`
**Import:** `import { TDSCascaderModule } from 'tds-ui/cascader';`
**Export as:** `tdsCascader`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsOptions` | `TDSCascaderOption[] \| null` | `[]` | Dữ liệu nguồn |
| `tdsPlaceHolder` | `string` | `''` | Placeholder |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa |
| `tdsSize` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước |
| `tdsAllowClear` | `boolean` | `true` | Xóa giá trị |
| `tdsShowSearch` | `boolean \| TDSShowSearchOptions` | `false` | Tìm kiếm |
| `tdsTriggerAction` | `'click' \| 'hover' \| ('click' \| 'hover')[]` | `['click']` | Cách mở panel |
| `tdsLoadData` | `(node, index) => Promise \| Observable` | — | Lazy load children |
| `tdsChangeOnSelect` | `boolean` | `false` | Emit change khi chọn node trung gian |
| `tdsMultiple` | `boolean` | `false` | Cho phép chọn nhiều |
| `tdsExpandTrigger` | `'click' \| 'hover'` | `'hover'` | Trigger mở rộng column |
| `tdsDisplayWith` | `(nodes) => string \| undefined` | — | Custom hiển thị giá trị |
| `tdsOpen` | `boolean \| undefined` | `undefined` | Mở/đóng dropdown (controlled) |
| `tdsShowInput` | `boolean` | `true` | Hiển thị input |
| `tdsShowArrow` | `boolean` | `true` | Hiển thị arrow icon |
| `tdsAutoFocus` | `boolean` | `false` | Tự động focus |
| `tdsColumnClassName` | `string \| undefined` | `undefined` | Custom class cho column |
| `tdsWidthColumn` | `string` | `'220px'` | Chiều rộng column |
| `tdsValueProperty` | `string` | `'value'` | Field dùng làm value |
| `tdsLabelRender` | `TemplateRef \| null` | `null` | Template hiển thị label |
| `tdsLabelProperty` | `string` | `'label'` | Field hiển thị label |
| `tdsVariant` | `string` | `'outlined'` | Variant: `outlined`, `borderless`, `filled`, `underlined` |
| `tdsNotFoundContent` | `string \| TemplateRef<void> \| undefined` | `undefined` | Content khi không có data |
| `tdsBackdrop` | `boolean` | `false` | Hiển thị backdrop |
| `tdsMenuClassName` | `string \| undefined` | `undefined` | Custom class cho menu |
| `tdsMenuStyle` | `NgStyleInterface \| null` | `null` | Custom style cho menu |
| `tdsMouseLeaveDelay` | `number` | `150` | Delay đóng menu khi mouse leave (ms) |
| `tdsMouseEnterDelay` | `number` | `150` | Delay mở menu khi mouse enter (ms) |
| `tdsMaxTagCount` | `number` | `Infinity` | Max tags hiển thị (multiple mode) |
| `tdsPlacement` | `'bottomLeft' \| 'bottomRight' \| 'topLeft' \| 'topRight'` | `'bottomLeft'` | Vị trí dropdown |
| `tdsChangeOn` | `((option, level) => boolean) \| undefined` | `undefined` | Callback để xác định có thay đổi không |
| `tdsOptionRender` | `TemplateRef \| null` | `null` | Template render option |
| `tdsDebounceTime` | `number` | `250` | Debounce time cho search (ms) |
| `tdsPrefix` | `string \| TemplateRef<void> \| null` | `null` | Template prefix |
| `tdsSuffixIcon` | `string \| TemplateRef<void>` | `'tdsi-chevron-down-fill'` | Icon suffix |
| `tdsExpandIcon` | `string \| TemplateRef<void>` | `''` | Icon expand |
| `tdsHeader` | `string \| TemplateRef \| null` | `null` | Header content |
| `tdsFooter` | `string \| TemplateRef \| null` | `null` | Footer content |
| `required` | `boolean` | `false` | Bắt buộc nhập |
| `id` | `string` | `'tds-cascader'` | ID của component |
| `userAriaDescribedBy` | `string` | — | ARIA described by |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsVisibleChange` | `EventEmitter<boolean>` | Khi dropdown mở/đóng |
| `tdsSelectionChange` | `EventEmitter<TDSCascaderOption[]>` | Mảng options được chọn (path từ root đến leaf) |
| `tdsClear` | `EventEmitter<void>` | Khi nhấn nút clear |
| `tdsRemoved` | `EventEmitter<TDSCascaderOption>` | Khi xóa một node (multi-select) |

## TDSCascaderOption Interface

```typescript
interface TDSCascaderOption {
  value?: any;
  label?: string;
  title?: string;
  disabled?: boolean;
  loading?: boolean;
  isLeaf?: boolean;
  parent?: TDSCascaderOption;
  children?: TDSCascaderOption[];
  labelSearchValue?: string;
  disableCheckbox?: boolean;
  [key: string]: any;
}
```

## TDSShowSearchOptions Interface

```typescript
interface TDSShowSearchOptions {
  filter?: (searchValue: string, path: TDSCascaderOption[]) => boolean;
  sorter?: (a: TDSCascaderOption[], b: TDSCascaderOption[], inputValue: string) => number;
}
```

## Key Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `focus` | - | Focus vào cascader |
| `blur` | - | Blur cascader |
| `closeMenu` | - | Đóng dropdown |
| `clearSelection` | `event?: Event` | Xóa selection |

## Usage

```html
<!-- Basic với ngModel -->
<tds-cascader
  [(ngModel)]="selectedValue"
  [tdsOptions]="options"
  tdsPlaceHolder="Chọn danh mục"
  (tdsSelectionChange)="onSelectionChange($event)">
</tds-cascader>

<!-- Multiple mode -->
<tds-cascader
  [(ngModel)]="selectedValues"
  [tdsOptions]="options"
  [tdsMultiple]="true"
  tdsPlaceHolder="Chọn nhiều danh mục">
</tds-cascader>

<!-- With search -->
<tds-cascader
  [(ngModel)]="selectedValue"
  [tdsOptions]="options"
  [tdsShowSearch]="true"
  tdsPlaceHolder="Tìm kiếm và chọn">
</tds-cascader>

<!-- Lazy load -->
<tds-cascader
  [(ngModel)]="selectedValue"
  [tdsOptions]="options"
  [tdsLoadData]="loadData"
  (tdsSelectionChange)="onSelectionChange($event)">
</tds-cascader>

<!-- Custom label render -->
<tds-cascader
  [(ngModel)]="selectedValue"
  [tdsOptions]="options"
  [tdsLabelRender]="labelRenderTpl">
</tds-cascader>

<ng-template #labelRenderTpl let-labels let-selectedOptions="selectedOptions">
  <span *ngFor="let label of labels; let isLast = last">
    {{ label }}{{ isLast ? '' : ' > ' }}
  </span>
</ng-template>

<!-- Change on select -->
<tds-cascader
  [(ngModel)]="selectedValue"
  [tdsOptions]="options"
  [tdsChangeOnSelect]="true"
  (tdsSelectionChange)="onSelectionChange($event)">
</tds-cascader>

<!-- Different variants -->
<tds-cascader tdsVariant="filled">...</tds-cascader>
<tds-cascader tdsVariant="borderless">...</tds-cascader>

<!-- Custom size -->
<tds-cascader tdsSize="lg">...</tds-cascader>
<tds-cascader tdsSize="sm">...</tds-cascader>

<!-- Hover trigger -->
<tds-cascader
  [tdsOptions]="options"
  [tdsTriggerAction]="['hover']"
  [tdsExpandTrigger]="'hover'">
</tds-cascader>

<!-- With custom filter and sorter -->
<tds-cascader
  [(ngModel)]="selectedValue"
  [tdsOptions]="options"
  [tdsShowSearch]="searchOptions">
</tds-cascader>
```

```typescript
import { TDSCascaderModule } from 'tds-ui/cascader';
import type { TDSCascaderOption, TDSShowSearchOptions } from 'tds-ui/cascader';

@Component({
  standalone: true,
  imports: [TDSCascaderModule, FormsModule]
})
export class MyComponent {
  selectedValue: any = null;
  selectedValues: any[] = [];

  // Basic options
  options: TDSCascaderOption[] = [
    {
      value: 'vn',
      label: 'Việt Nam',
      children: [
        { value: 'hcm', label: 'TP.HCM', isLeaf: true },
        { value: 'hn', label: 'Hà Nội', isLeaf: true },
      ]
    },
  ];

  // Lazy load
  loadData(node: TDSCascaderOption, index: number): Observable<TDSCascaderOption[]> {
    return this.service.getChildren(node.value);
  }

  onSelectionChange(options: TDSCascaderOption[]) {
    console.log('Selected path:', options);
  }

  // Custom search options
  searchOptions: TDSShowSearchOptions = {
    filter: (searchValue: string, path: TDSCascaderOption[]): boolean => {
      return path.some(option =>
        option.label?.toLowerCase().includes(searchValue.toLowerCase())
      );
    },
    sorter: (a: TDSCascaderOption[], b: TDSCascaderOption[], inputValue: string): number => {
      // Custom sort logic
      return 0;
    }
  };
}
```

## Notes

- `isLeaf: true` bắt buộc trên node lá khi dùng lazy load (`tdsLoadData`)
- `tdsSelectionChange` trả về mảng options từ root đến leaf (full path)
- `tdsMultiple` cho phép chọn nhiều leaf nodes đồng thời
- `tdsChangeOnSelect` emit change khi chọn node trung gian (không chỉ leaf)
- `tdsExpandTrigger` điều khiển cách mở rộng column khi hover/click
- `tdsTriggerAction` điều khiển cách mở dropdown chính
- `tdsVariant` hỗ trợ: `outlined`, `borderless`, `filled`, `underlined`
- `tdsDisplayWith` custom function để hiển thị giá trị đã chọn (default: `labels.join(' / ')`)
- `tdsDebounceTime` thời gian debounce cho search (default: 250ms)
- `tdsMaxTagCount` giới hạn số tags hiển thị trong multiple mode
- `tdsMouseEnterDelay` và `tdsMouseLeaveDelay` dùng cho hover trigger
- `tdsWidthColumn` set chiều rộng cho mỗi column (default: '220px')
- `tdsChangeOn` callback để quyết định có thay đổi value không khi chọn option
- `tdsValueProperty` và `tdsLabelProperty` custom field names cho value và label
- `tdsOptionRender` template để custom render mỗi option
- `tdsLabelRender` template để custom render label hiển thị
- `tdsPrefix` và `tdsSuffixIcon` để thêm icon/text prefix/suffix
- `tdsHeader` và `tdsFooter` để thêm content vào header/footer của dropdown
- `tdsNotFoundContent` custom content khi không có kết quả tìm kiếm
- `tdsColumnClassName` và `tdsMenuClassName` để custom CSS classes
- `tdsMenuStyle` để custom inline styles cho menu
- `tdsPlacement` hỗ trợ 4 vị trí: `bottomLeft`, `bottomRight`, `topLeft`, `topRight`
- `tdsBackdrop` hiển thị backdrop khi dropdown mở
- Supports RTL direction
- Hỗ trợ keyboard navigation (Arrow keys, Enter, Backspace, Escape)
- Form validation compatible (ngModel, Reactive Forms)
