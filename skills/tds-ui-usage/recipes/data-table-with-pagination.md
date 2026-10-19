# Data Table với Pagination

## Use case
Hiển thị bảng dữ liệu có phân trang tích hợp. `tds-data-table` đã có sẵn pagination — chỉ cần cấu hình inputs, không cần `tds-pagination` riêng.

## Components cần import
```typescript
import { TDSDataTableModule } from 'tds-ui/data-table';
```

## Code example

### Template
```html
<tds-data-table
  [tdsData]="data"
  [tdsLoading]="loading"
  [tdsTotal]="total"
  [(tdsPageIndex)]="pageIndex"
  [(tdsPageSize)]="pageSize"
  [tdsShowSizeChanger]="true"
  [tdsPageSizeOptions]="[10, 20, 50]"
  (tdsQueryParams)="onQueryParams($event)">

  <tds-data-table-column tdsField="name" tdsTitle="Tên"></tds-data-table-column>
  <tds-data-table-column tdsField="email" tdsTitle="Email"></tds-data-table-column>
  <tds-data-table-column tdsField="status" tdsTitle="Trạng thái"></tds-data-table-column>
</tds-data-table>
```

### TypeScript
```typescript
import { Component, OnInit } from '@angular/core';
import { TDSDataTableModule } from 'tds-ui/data-table';

@Component({
  standalone: true,
  imports: [TDSDataTableModule],
  templateUrl: './my-table.component.html'
})
export class MyTableComponent implements OnInit {
  data: any[] = [];
  total = 0;
  pageIndex = 1;
  pageSize = 10;
  loading = false;

  ngOnInit() {
    this.loadData();
  }

  onQueryParams(params: any) {
    this.pageIndex = params.pageIndex;
    this.pageSize = params.pageSize;
    this.loadData();
  }

  loadData() {
    this.loading = true;
    // Call API with pageIndex, pageSize
    // this.api.getData(this.pageIndex, this.pageSize).subscribe(res => {
    //   this.data = res.items;
    //   this.total = res.total;
    //   this.loading = false;
    // });
    this.loading = false;
  }
}
```

## Pagination modes

### Client-side pagination (mặc định)
```html
<tds-data-table
  [tdsData]="allData"
  [tdsFrontPagination]="true">
```
Truyền toàn bộ data vào `tdsData`, component tự phân trang.

### Server-side pagination
```html
<tds-data-table
  [tdsData]="data"
  [tdsTotal]="total"
  [tdsFrontPagination]="false"
  [(tdsPageIndex)]="pageIndex"
  [(tdsPageSize)]="pageSize"
  (tdsQueryParams)="onQueryParams($event)">
```
Chỉ truyền data của trang hiện tại. `tdsTotal` cho biết tổng số records.

## Tips
- Pagination mặc định hiển thị ở bottom, đổi qua `tdsPaginationPosition="top"` hoặc `"both"`
- `tdsShowSizeChanger="true"` cho phép user chọn page size
- `tdsHideOnSinglePage="true"` ẩn pagination khi chỉ có 1 trang
- `tdsShowQuickJumper="true"` thêm ô nhập số trang
- Dùng `tdsShowTotal` template để hiển thị "1-20 của 100 items"
- Xem thêm: `reference/docs/data-table.md`
