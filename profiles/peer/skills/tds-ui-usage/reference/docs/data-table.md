# Data Table

Bảng dữ liệu nâng cao với pagination, selection, expandable rows, virtual scroll. Wrapper của `tds-table` với thêm tính năng checkbox, expand row và column grouping.

**Selector:** `tds-data-table`
**Import:** `import { TDSDataTableModule } from 'tds-ui/data-table';`
**Export as:** `tdsDataTable`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsData` | `readonly T[]` | `[]` | Dữ liệu rows |
| `tdsPageIndex` | `number` | `1` | Trang hiện tại |
| `tdsPageSize` | `number` | `50` | Số rows mỗi trang |
| `tdsTotal` | `number` | `0` | Tổng số records (cho server pagination) |
| `tdsFrontPagination` | `boolean` | `true` | Pagination phía client (true) hay server (false) |
| `tdsShowPagination` | `boolean` | `true` | Hiển thị pagination |
| `tdsLoading` | `boolean` | `false` | Loading state |
| `tdsBordered` | `boolean` | `false` | Hiển thị border ô |
| `tdsOuterBordered` | `boolean` | `false` | Border ngoài table |
| `tdsHeightAuto` | `boolean` | `false` | Height tự động |
| `tdsShowSizeChanger` | `boolean` | `false` | Hiển thị chọn page size |
| `tdsHideOnSinglePage` | `boolean` | `false` | Ẩn pagination khi chỉ 1 trang |
| `tdsShowQuickJumper` | `boolean` | `false` | Hiển thị ô nhập trang |
| `tdsPageSizeOptions` | `number[]` | `[10, 20, 30, 40, 50]` | Tùy chọn page size |
| `tdsPaginationPosition` | `'top' \| 'bottom' \| 'both'` | `'bottom'` | Vị trí pagination |
| `tdsScroll` | `{ x?: string \| null, y?: string \| null }` | `{ x: null, y: 'auto' }` | Scroll cố định header/body |
| `tdsTitle` | `string \| TemplateRef<any> \| null` | `null` | Tiêu đề table |
| `tdsFooter` | `string \| TemplateRef<any> \| null` | `null` | Footer content |
| `tdsNoResult` | `string \| TemplateRef<any>` | `undefined` | Nội dung khi không có data |
| `tdsLoadingIndicator` | `TemplateRef<any> \| null` | `null` | Custom loading template |
| `tdsLoadingDelay` | `number` | `0` | Delay hiển thị loading (ms) |
| `tdsShowRefresh` | `boolean` | `true` | Hiển thị nút refresh |
| `tdsShowTotal` | `TemplateRef<{ $implicit: number; range: [number, number] }> \| null` | `null` | Template hiển thị "1-20 của 100 items" |
| `tdsPaginationItemRender` | `TemplateRef<PaginationItemRenderContext> \| null` | `null` | Custom pagination item |
| `tdsSelectable` | `TDSDataTableSelectableSettings \| null` | `{ multiple: true }` | Cấu hình selection. `{ multiple: true/false, checkboxOnly?: boolean, enabled?: boolean }` |
| `tdsSelectedKeys` | `any[]` | `[]` | Danh sách keys của rows được chọn |
| `tdsSelectedField` | `string \| null` | `null` | Field dùng làm key (ưu tiên hơn tdsSelectedKeyFn) |
| `tdsSelectedKeyFn` | `(data) => any` | `(data) => data.dataRowId` | Hàm trả về key cho selection |
| `tdsDisabledSelectedFn` | `(data) => boolean` | `() => false` | Hàm kiểm tra row bị disabled |
| `tdsShowCheckboxFn` | `(data) => boolean` | `() => true` | Hàm kiểm tra hiển thị checkbox |
| `tdsSelectedAll` | `boolean` | `false` | Select tất cả rows |
| `tdsIndeterminateAll` | `boolean` | `false` | Indeterminate state cho select all |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |
| `tdsMaxHeight` | `string \| undefined` | `undefined` | Max height cho body |
| `tdsMinHeight` | `string \| undefined` | `undefined` | Min height cho body |
| `tdsRounded` | `boolean` | `false` | Bo tròn góc |
| `tdsVirtualItemSize` | `number` | `0` | Item size cho virtual scroll |
| `tdsVirtualMaxBufferPx` | `number` | `200` | Max buffer cho virtual scroll |
| `tdsVirtualMinBufferPx` | `number` | `100` | Min buffer cho virtual scroll |
| `tdsVirtualForTrackBy` | `TrackByFunction` | `index => index` | TrackBy function cho virtual scroll |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsPageIndexChange` | `EventEmitter<number>` | Khi đổi trang |
| `tdsPageSizeChange` | `EventEmitter<number>` | Khi đổi page size |
| `tdsQueryParams` | `EventEmitter<TDSTableQueryParams>` | Khi sort/filter/page thay đổi |
| `tdsCurrentPageDataChange` | `EventEmitter<readonly T[]>` | Khi dữ liệu trang thay đổi |
| `tdsClickRefresh` | `EventEmitter<MouseEvent>` | Khi click nút refresh |
| `tdsClickCheckAll` | `EventEmitter<boolean>` | Khi click check all |
| `tdsClickRow` | `EventEmitter<{ dataRow, event }>` | Khi click row |
| `tdsSelectedRowChange` | `EventEmitter<{ data, selected }>` | Khi select/unselect row |
| `tdsSelectedKeysChange` | `EventEmitter<any[]>` | Khi danh sách selected keys thay đổi |
| `tdsSelectedAllChange` | `EventEmitter<boolean>` | Khi select all thay đổi |

## Sub Components

### tds-data-table-column

Định nghĩa cột dữ liệu.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsField` | `string` | — | Field path (nested: `user.name`) |
| `tdsTitle` | `string \| TemplateRef<void>` | — | Tiêu đề cột |
| `tdsWidth` | `string \| null` | `null` | Width cột |
| `tdsLeft` | `boolean` | `false` | Fixed left |
| `tdsRight` | `boolean` | `false` | Fixed right |
| `tdsHidden` | `boolean` | `false` | Ẩn cột |
| `tdsClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho ô |
| `tdsHeaderClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho header |
| `tdsContent` | `TemplateRef<{ $implicit, dataRowIndex }> \| null` | `null` | Template content. Context: `$implicit` = rowData, `dataRowIndex` = số thứ tự row |
| `tdsFormat` | `string \| TDSNumberFormatSettings` | — | Format config. Chỉ hoạt động khi `tdsDataType='date'` (Angular date pipe format string) hoặc `tdsDataType='numeric'` (tdsFormatNumber pipe config). Không hoạt động với `tdsDataType='text'` hoặc `'boolean'` |
| `tdsDataType` | `'text' \| 'numeric' \| 'boolean' \| 'date'` | `'text'` | Loại data, quyết định cách render |
| `tdsColumnType` | `'default' \| 'command'` | `'default'` | Loại cột. `'command'` dùng cho cột thao tác |

### tds-data-table-checkbox-column

Cột checkbox selection.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsWidth` | `string` | `'40px'` | Width cột checkbox |
| `tdsHiddenAll` | `boolean` | `false` | Ẩn checkbox header (check all) |
| `tdsCheckedAll` | `boolean` | `false` | Trạng thái checked all |
| `tdsIndeterminate` | `boolean` | `false` | Indeterminate state cho checkbox all |
| `tdsContent` | `TemplateRef<{ $implicit, dataRowIndex }> \| null` | `null` | Custom template cho checkbox cell |
| `tdsLeft` | `boolean` | `true` | Fixed left |
| `tdsClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho ô |
| `tdsHeaderClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho header |

### tds-data-table-expand-row

Row expandable.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsWidth` | `string` | `'26px'` | Width cột expand |
| `tdsExpandedKeys` | `any[]` | `[]` | Danh sách keys của rows đang expand |
| `tdsExpandField` | `string \| null` | `null` | Field dùng làm key cho expand (ưu tiên hơn tdsExpandKeyFn) |
| `tdsExpandKeyFn` | `(data) => any` | `(data) => data.dataRowId` | Hàm trả về key cho expand |
| `tdsContent` | `TemplateRef<{ $implicit, dataRowIndex, expand }> \| null` | `null` | Template nội dung expand. Context: `$implicit` = rowData, `dataRowIndex`, `expand` = boolean |
| `tdsLeft` | `boolean` | `true` | Fixed left |
| `tdsClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho ô |
| `tdsHeaderClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho header |

| Output | Type | Description |
|--------|------|-------------|
| `tdsExpandChange` | `EventEmitter<{ data, expand }>` | Khi expand/collapse row |
| `tdsExpandedKeysChange` | `EventEmitter<any[]>` | Khi danh sách expanded keys thay đổi |

### tds-data-table-column-group

Group cột (header nhiều level).

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTitle` | `string \| TemplateRef<void>` | — | Tiêu đề group |
| `tdsHidden` | `boolean` | `false` | Ẩn group |
| `tdsLeft` | `boolean` | `false` | Fixed left |
| `tdsRight` | `boolean` | `false` | Fixed right |
| `tdsHeaderClass` | `string \| string[] \| Set<string> \| { [klass: string]: any }` | `''` | Class cho header |

## Usage

### Data table với checkbox, pagination

```html
<tds-data-table
  [tdsData]="users"
  [tdsLoading]="loading"
  [tdsTotal]="total"
  [(tdsPageIndex)]="pageIndex"
  [(tdsPageSize)]="pageSize"
  [(tdsSelectedKeys)]="selectedKeys"
  [tdsSelectable]="{ multiple: true }"
  [tdsSelectedField]="'id'"
  (tdsQueryParams)="onQueryChange($event)"
  (tdsClickRow)="onClickRow($event)">

  <tds-data-table-checkbox-column [tdsWidth]="'50px'"></tds-data-table-checkbox-column>

  <tds-data-table-column
    tdsField="id"
    tdsTitle="ID"
    [tdsWidth]="'80px'">
  </tds-data-table-column>

  <tds-data-table-column
    tdsField="name"
    tdsTitle="Tên">
  </tds-data-table-column>

  <tds-data-table-column
    tdsField="email"
    tdsTitle="Email">
  </tds-data-table-column>

  <tds-data-table-column
    tdsField="status"
    tdsTitle="Trạng thái"
    [tdsContent]="statusTpl">
    <ng-template #statusTpl let-dataRow>
      {{ dataRow.status === 'active' ? 'Hoạt động' : 'Khóa' }}
    </ng-template>
  </tds-data-table-column>

  <tds-data-table-column
    tdsTitle="Thao tác"
    [tdsWidth]="'120px'"
    [tdsContent]="commandTpl"
    [tdsColumnType]="'command'"
    [tdsRight]="true">
    <ng-template #commandTpl let-dataRow>
      <button (click)="onEdit(dataRow)">Edit</button>
    </ng-template>
  </tds-data-table-column>
</tds-data-table>
```

```typescript
import { TDSDataTableModule } from 'tds-ui/data-table';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [TDSDataTableModule]
})
export class UserListComponent implements OnInit {
  users: User[] = [];
  loading = false;
  total = 0;
  pageIndex = 1;
  pageSize = 20;
  selectedKeys: number[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.loading = true;
    this.api.getUsers(this.pageIndex, this.pageSize).subscribe(res => {
      this.users = res.data;
      this.total = res.total;
      this.loading = false;
    });
  }

  onQueryChange(params: TDSTableQueryParams) {
    this.pageIndex = params.pageIndex;
    this.pageSize = params.pageSize;
    this.loadData();
  }

  onClickRow(event: { dataRow: any, event: MouseEvent }) {
    console.log('Clicked row:', event.dataRow);
  }

  onEdit(user: User) {
    console.log('Edit user:', user);
  }
}
```

### Data table với expandable rows

```html
<tds-data-table
  [tdsData]="orders"
  [tdsLoading]="loading"
  [tdsTotal]="total"
  [(tdsPageIndex)]="pageIndex"
  [(tdsPageSize)]="pageSize">

  <tds-data-table-expand-row
    [tdsWidth]="'40px'"
    [tdsExpandField]="'id'"
    [(tdsExpandedKeys)]="expandedKeys"
    [tdsContent]="expandTpl">
    <ng-template #expandTpl let-dataRow let-expand="expand">
      <tr>
        <td colspan="4">Chi tiết đơn hàng: {{ dataRow.id }}</td>
      </tr>
    </ng-template>
  </tds-data-table-expand-row>

  <tds-data-table-column tdsField="id" tdsTitle="ID" [tdsWidth]="'80px'"></tds-data-table-column>
  <tds-data-table-column tdsField="customer" tdsTitle="Khách hàng"></tds-data-table-column>
  <tds-data-table-column tdsField="total" tdsTitle="Tổng tiền" tdsDataType="numeric"></tds-data-table-column>
  <tds-data-table-column tdsField="date" tdsTitle="Ngày" tdsDataType="date" tdsFormat="dd/MM/yyyy"></tds-data-table-column>
</tds-data-table>
```

### Data table với column grouping

```html
<tds-data-table [tdsData]="data" [tdsBordered]="true">
  <tds-data-table-column tdsField="name" tdsTitle="Tên" [tdsLeft]="true"></tds-data-table-column>

  <tds-data-table-column-group tdsTitle="Thông tin liên hệ">
    <tds-data-table-column tdsField="email" tdsTitle="Email"></tds-data-table-column>
    <tds-data-table-column tdsField="phone" tdsTitle="Điện thoại"></tds-data-table-column>
  </tds-data-table-column-group>

  <tds-data-table-column tdsField="status" tdsTitle="Trạng thái" [tdsRight]="true"></tds-data-table-column>
</tds-data-table>
```

## Notes

- `tdsData` là toàn bộ dữ liệu, component tự phân trang khi `tdsFrontPagination=true`
- Khi `tdsFrontPagination=false`, phải tự xử lý server-side pagination
- `tdsSelectedField` hoặc `tdsSelectedKeyFn` dùng để định danh unique key cho mỗi row
- `tdsDisabledSelectedFn` và `tdsShowCheckboxFn` cho phép control checkbox per-row
- `tdsLeft`/`tdsRight` nên dùng binding: `[tdsLeft]="true"`, `[tdsRight]="true"`. Tránh dùng standalone attribute `tdsLeft`/`tdsRight` do có thể gây lỗi trên một số trường hợp
- `tdsFormat` chỉ hoạt động với `tdsDataType='date'` hoặc `'numeric'`. Để format text custom, dùng `tdsContent` template thay vì `tdsFormat`
- `tdsColumnType='command'` dùng cho cột thao tác, click vào cell sẽ không trigger `tdsClickRow`
- Support column grouping với `tds-data-table-column-group`
- Support expandable rows với `tds-data-table-expand-row`
- Support virtual scroll cho dữ liệu lớn
- Các sub-component đều standalone, có thể import riêng hoặc dùng `TDSDataTableModule` để import tất cả
