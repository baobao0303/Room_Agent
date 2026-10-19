# Search với Filter

## Use case
Tạo thanh tìm kiếm kết hợp bộ lọc (filter), hiển thị kết quả theo thời gian thực.

## Components cần import
```typescript
import { TDSInputSearchModule } from 'tds-ui/input-search';
import { TDSSelectModule } from 'tds-ui/select';
```

## Code example

### Template
```html
<div class="flex gap-2 mb-4">
  <tds-input-search
    [(tdsInputValue)]="searchText"
    (tdsInputValueChange)="onSearch()"
    tdsPlaceHolder="Tìm kiếm...">
  </tds-input-search>

  <tds-select
    [(ngModel)]="selectedFilter"
    [data]="filterOptions"
    textField="label"
    valueField="value"
    (selectChange)="onFilterChange()"
    style="min-width: 150px">
  </tds-select>
</div>
```

### TypeScript
```typescript
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TDSInputSearchModule } from 'tds-ui/input-search';
import { TDSSelectModule } from 'tds-ui/select';

@Component({
  standalone: true,
  imports: [FormsModule, TDSInputSearchModule, TDSSelectModule],
  templateUrl: './search-filter.component.html'
})
export class SearchFilterComponent {
  searchText = '';
  selectedFilter = 'all';
  filterOptions = [
    { label: 'Tất cả', value: 'all' },
    { label: 'Hoạt động', value: 'active' },
    { label: 'Ngừng', value: 'inactive' },
  ];

  onSearch() {
    this.applyFilters();
  }

  onFilterChange() {
    this.applyFilters();
  }

  private applyFilters() {
    // Filter logic using searchText and selectedFilter
  }
}
```

## Tips
- `tds-input-search` có built-in search icon và clear button
- `tds-input-search` dùng `tdsInputValue` + `tdsInputValueChange` thay vì `ngModel`
- `tds-select` dùng `data` binding cho options (không có prefix `tds`)
- Xem thêm: `reference/docs/input-search.md`, `reference/docs/select.md`
