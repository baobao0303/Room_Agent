# Table

Bảng dữ liệu với sort, filter, pagination, selection, virtual scroll.

**Selector:** `tds-table`
**Import:** `import { TDSTableModule } from 'tds-ui/table';`
**Export as:** `tdsTable`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `listData` | `readonly T[]` | `[]` | Dữ liệu rows (dữ liệu trang hiện tại) |
| `loading` | `boolean` | `false` | Loading state |
| `loadingDelay` | `number` | `0` | Delay hiển thị loading (ms) |
| `loadingIndicator` | `TemplateRef<any> \| null` | `null` | Template loading indicator |
| `bordered` | `boolean` | `false` | Hiển thị border ô |
| `outerBordered` | `boolean` | `false` | Hiển thị border ngoài table |
| `size` | `'default' \| 'middle' \| 'small'` | `'default'` | Kích thước row |
| `tableLayout` | `'auto' \| 'fixed'` | `'auto'` | Kiểu layout table |
| `scroll` | `{ x?: string \| null, y?: string \| null }` | `{ x: null, y: 'auto' }` | Scroll cố định header/body |
| `total` | `number` | `0` | Tổng số records (cho pagination) |
| `pageIndex` | `number` | `1` | Trang hiện tại |
| `pageSize` | `number` | `20` | Số rows mỗi trang |
| `pageSizeOptions` | `number[]` | `[10, 20, 30, 40, 50]` | Tùy chọn page size |
| `paginationType` | `ButtonSize` | `'sm'` | Kích thước pagination |
| `showPagination` | `boolean` | `true` | Hiển thị pagination |
| `frontPagination` | `boolean` | `true` | Pagination phía client (true) hay server (false) |
| `noResult` | `string \| TemplateRef<any> \| undefined` | `undefined` | Nội dung khi không có data |
| `title` | `string \| TemplateRef<any> \| null` | `null` | Tiêu đề table |
| `footer` | `string \| TemplateRef<any> \| null` | `null` | Footer content |
| `showSizeChanger` | `boolean` | `false` | Hiển thị chọn page size |
| `hideOnSinglePage` | `boolean` | `false` | Ẩn pagination khi chỉ 1 trang |
| `showQuickJumper` | `boolean` | `false` | Hiển thị ô nhập trang |
| `simple` | `boolean` | `false` | Pagination đơn giản (prev/next) |
| `showRefresh` | `boolean` | `true` | Hiển thị nút refresh |
| `showTotal` | `TemplateRef<{ $implicit: number; range: [number, number] }> \| null` | `null` | Template hiển thị tổng items |
| `itemRender` | `TemplateRef<PaginationItemRenderContext> \| null` | `null` | Template custom pagination item |
| `widthConfig` | `ReadonlyArray<string \| null>` | `[]` | Cấu hình width cột |
| `paginationPosition` | `'top' \| 'bottom' \| 'both'` | `'bottom'` | Vị trí pagination |
| `templateMode` | `boolean` | `false` | Chế độ template |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |
| `fullScreen` | `boolean` | `true` | Full-height layout (dùng với maxHeight/minHeight) |
| `maxHeight` | `string \| undefined` | `undefined` | Max height cho body, kích hoạt scroll dọc |
| `minHeight` | `string \| undefined` | `undefined` | Min height cho body |
| `rounded` | `boolean` | `false` | Bo tròn border |
| `virtualItemSize` | `number` | `0` | Kích thước item cho virtual scroll |
| `virtualMaxBufferPx` | `number` | `200` | Max buffer cho virtual scroll |
| `virtualMinBufferPx` | `number` | `100` | Min buffer cho virtual scroll |
| `virtualForTrackBy` | `TrackByFunction<T>` | `index => index` | Track by function cho virtual scroll |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `pageIndexChange` | `EventEmitter<number>` | Khi đổi trang |
| `pageSizeChange` | `EventEmitter<number>` | Khi đổi page size |
| `queryParams` | `EventEmitter<TDSTableQueryParams>` | Khi sort/filter/page thay đổi |
| `currentPageDataChange` | `EventEmitter<readonly T[]>` | Khi dữ liệu trang thay đổi |
| `clickRefresh` | `EventEmitter<MouseEvent>` | Khi click nút refresh |

## TDSTableQueryParams Interface

```typescript
interface TDSTableQueryParams {
  pageIndex: number;
  pageSize: number;
  sort: Array<{ key: string; value: TDSTableSortOrder }>;
  filter: Array<{ key: string; value: TDSTableFilterValue }>;
}
```

## Column Directives

`<th>`, `<td>`, `<tr>` elements receive styling automatically when placed inside `<tds-table>` — no attribute directives needed. Sort and filter are enabled by adding inputs directly on `<th>`:

| Input on `<th>` | Type | Description |
|-----------------|------|-------------|
| `[sortFn]` | `TDSTableSortFn \| boolean \| null` | Kích hoạt sort; truyền hàm compare hoặc `true` cho server-side sort |
| `[sortOrder]` | `TDSTableSortOrder` | Trạng thái sort hiện tại (`'ascend' \| 'descend' \| null`) |
| `[filters]` | `TDSTableFilterList` | Danh sách filter options |
| `[showSort]` | `boolean` | Hiển thị icon sort |
| `[showFilter]` | `boolean` | Hiển thị icon filter |

## Usage

```html
<tds-table
  [listData]="tableData"
  [loading]="loading"
  [total]="total"
  [(pageIndex)]="pageIndex"
  [(pageSize)]="pageSize"
  (queryParams)="onQueryChange($event)">

  <thead>
    <tr>
      <th>STT</th>
      <th [sortFn]="true" [(sortOrder)]="nameSortOrder">Tên</th>
      <th>Thao tác</th>
    </tr>
  </thead>

  <tbody>
    @for (row of tableData; track row.id) {
      <tr>
        <td>{{ $index + 1 }}</td>
        <td>{{ row.name }}</td>
        <td>
          <button (click)="onEdit(row)">Edit</button>
        </td>
      </tr>
    }
  </tbody>
</tds-table>
```

```typescript
import { TDSTableModule } from 'tds-ui/table';
import { TDSTableQueryParams } from 'tds-ui/table';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [TDSTableModule, CommonModule]
})
export class UserListComponent implements OnInit {
  tableData: any[] = [];
  loading = false;
  total = 0;
  pageIndex = 1;
  pageSize = 20;
  nameSortOrder: 'ascend' | 'descend' | null = null;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.loading = true;
    this.api.getUsers(this.pageIndex, this.pageSize).subscribe(res => {
      this.tableData = res.data;
      this.total = res.total;
      this.loading = false;
    });
  }

  onQueryChange(params: TDSTableQueryParams) {
    this.pageIndex = params.pageIndex;
    this.pageSize = params.pageSize;
    this.loadData();
  }

  onEdit(row: any) {
    console.log('Edit', row);
  }
}
```

## Notes

- `listData` là dữ liệu của trang hiện tại, server-side pagination cần tự quản lý tổng số record qua `total`
- Dùng `@for` (Angular 17+ control flow) thay vì `*ngFor`
- Khi `frontPagination=true`, component tự xử lý pagination phía client
- Khi `frontPagination=false`, phải tự xử lý pagination server-side và update `listData`, `total`, `pageIndex`
- `queryParams` event phát ra khi có thay đổi sort/filter/page để call API load dữ liệu mới
- `virtualItemSize`, `virtualMaxBufferPx`, `virtualMinBufferPx` dùng cho virtual scroll mode
- `loadingDelay` trì hoãn hiển thị loading spinner, tránh flicker
