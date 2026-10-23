# Filter Result

Hiển thị danh sách các bộ lọc đã áp dụng dưới dạng tag, hỗ trợ xóa từng phần hoặc xóa tất cả.

**Selector:** `tds-filter-result`
**Import:** `import { TDSFilterResultModule } from 'tds-ui/filter-result';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsData` | `TDSFilterResultDTO[]` | `[]` | Danh sách các filter đang active |
| `tdsTagGutter` | `number` | `8` | Khoảng cách giữa các tag (pixel) |
| `tdsAddFilterContent` | `string \| TemplateRef<void> \| null` | `null` | Nội dung trong popover thêm filter |
| `tdsAddFilterTitle` | `string \| TemplateRef<void> \| undefined` | `undefined` | Tiêu đề popover thêm filter |
| `tdsAddFilterFooter` | `string \| TemplateRef<void> \| undefined` | `undefined` | Footer popover thêm filter |
| `tdsAddFilterOverlayClassName` | `string` | `'tds-filter-result-add-popover'` | Class tùy chỉnh cho popover |
| `tdsAddFilterVisible` | `boolean` | `false` | Trạng thái visible của popover thêm filter |
| `tdsAddFilterAutoClose` | `boolean` | `false` | Tự động đóng popover sau khi chọn |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsRemoveItem` | `EventEmitter<TDSFilterResultDTO>` | Khi xóa một filter item |
| `tdsRemoveAll` | `EventEmitter<void>` | Khi xóa tất cả filters |
| `tdsDataChange` | `EventEmitter<TDSFilterResultDTO[]>` | Khi data thay đổi |
| `tdsAddFilterVisibleChange` | `EventEmitter<boolean>` | Khi trạng thái popover thay đổi |
| `tdsAddFilter` | `EventEmitter<void>` | Khi click vào nút thêm filter |

## Data Interface

```typescript
interface TDSFilterResultDTO {
  tdsValue: any;                    // Giá trị của filter
  tdsTitle: string | TemplateRef;   // Tiêu đề hiển thị
  tdsDisabled?: boolean;            // Disable filter item
  tdsClass?: string | string[];     // Custom class
}
```

## Usage

```html
<!-- Basic filter result -->
<tds-filter-result 
  [tdsData]="filters"
  (tdsRemoveItem)="onRemoveItem($event)"
  (tdsRemoveAll)="onRemoveAll()">
</tds-filter-result>

<!-- With custom tag gutter -->
<tds-filter-result 
  [tdsData]="filters"
  [tdsTagGutter]="12">
</tds-filter-result>

<!-- With add filter popover -->
<tds-filter-result 
  [tdsData]="filters"
  [tdsAddFilterTitle]="'Add Filter'"
  [tdsAddFilterVisible]="addFilterVisible"
  [tdsAddFilterContent]="addFilterTemplate"
  (tdsAddFilter)="onAddFilter()"
  (tdsAddFilterVisibleChange)="addFilterVisible = $event">
</tds-filter-result>

<ng-template #addFilterTemplate>
  <div class="filter-options">
    <label *ngFor="let option of filterOptions">
      <input type="checkbox" [value]="option.value">
      {{ option.label }}
    </label>
  </div>
</ng-template>
```

```typescript
import { TDSFilterResultModule, TDSFilterResultDTO } from 'tds-ui/filter-result';
import { Component } from '@angular/core';

@Component({
  selector: 'app-filter-result-demo',
  standalone: true,
  imports: [TDSFilterResultModule],
  template: `
    <tds-filter-result
      [tdsData]="activeFilters"
      [tdsTagGutter]="8"
      (tdsRemoveItem)="removeFilter($event)"
      (tdsRemoveAll)="clearAllFilters()">
    </tds-filter-result>
  `
})
export class FilterResultDemoComponent {
  activeFilters: TDSFilterResultDTO[] = [
    { tdsValue: 'status', tdsTitle: 'Status: Active' },
    { tdsValue: 'date', tdsTitle: 'Date: This Week' },
    { tdsValue: 'priority', tdsTitle: 'Priority: High' }
  ];

  removeFilter(item: TDSFilterResultDTO) {
    this.activeFilters = this.activeFilters.filter(f => f !== item);
    console.log('Removed:', item);
  }

  clearAllFilters() {
    this.activeFilters = [];
    console.log('All filters cleared');
  }
}
```

## Notes

- Component tự động tính toán và ẩn các tag khi không đủ không gian hiển thị
- Sử dụng `ResizeObserver` để theo dõi thay đổi kích thước container
- Hỗ trợ cả string và `TemplateRef` cho `tdsTitle` của mỗi filter item
- Class `tds-filter-result-empty` được thêm khi không có filter nào
- ExportAs: `tdsFilterResult` để truy cập component instance từ template
- Import Module vào `imports: []` của standalone component
