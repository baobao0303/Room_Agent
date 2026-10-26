# Data List Panel

Panel hiển thị danh sách dữ liệu với hỗ trợ tìm kiếm, loading state, và templates tùy chỉnh. Component này sử dụng Angular signals và computed để quản lý state.

**Selector:** `tds-data-list-panel`
**Import:** `import { TDSDataListPanelModule } from 'tds-ui/data-list';`
**Export as:** `tdsDataListPanel`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsData` | `T[]` | `[]` | Danh sách dữ liệu cần hiển thị |
| `tdsLoading` | `boolean` | `false` | Trạng thái loading khi tải dữ liệu |
| `tdsSearchable` | `boolean` | `false` | Bật/tắt chức năng tìm kiếm |
| `tdsServerSearch` | `boolean` | `false` | Bật chế độ tìm kiếm phía server (không filter client-side) |
| `tdsHeaderTemplate` | `TemplateRef \| string \| undefined` | `undefined` | Template header tùy chỉnh |
| `tdsFooterTemplate` | `TemplateRef \| string \| undefined` | `undefined` | Template footer tùy chỉnh |
| `tdsEmptyTemplate` | `TemplateRef \| string \| undefined` | `undefined` | Template hiển thị khi không có dữ liệu |
| `tdsItemTemplate` | `TemplateRef<TDSDataListItemContext<T>>` | — | Template để render từng item trong danh sách |
| `tdsMaxHeight` | `string` | `'205px'` | Chiều cao tối đa của panel (vd: '300px', '50vh', ...) |
| `tdsFilterFn` | `(term: string, item: T) => boolean` | — | Hàm filter dữ liệu (client-side search) |
| `tdsSearchPlaceholder` | `string` | `'Search...'` | Placeholder cho ô tìm kiếm |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsSearchChange` | `output<string>` (signal-based output API, Angular 17.3+) | Emit khi giá trị ô tìm kiếm thay đổi |

## Usage

```html
<!-- Basic data list với item template -->
<tds-data-list-panel
  [tdsData]="users"
  [tdsItemTemplate]="userTemplate"
  [tdsLoading]="isLoading">
</tds-data-list-panel>

<ng-template #userTemplate let-item>
  <div class="user-item">
    <span>{{ item.name }}</span>
    <span>{{ item.email }}</span>
  </div>
</ng-template>

<!-- With search functionality -->
<tds-data-list-panel
  [tdsData]="products"
  [tdsItemTemplate]="productTemplate"
  [tdsSearchable]="true"
  [tdsFilterFn]="filterProducts"
  (tdsSearchChange)="onSearch($event)">
</tds-data-list-panel>

<!-- With server-side search -->
<tds-data-list-panel
  [tdsData]="serverItems"
  [tdsItemTemplate]="itemTemplate"
  [tdsSearchable]="true"
  [tdsServerSearch]="true"
  [tdsLoading]="isLoading"
  (tdsSearchChange)="onServerSearch($event)">
</tds-data-list-panel>

<!-- With custom header/footer -->
<tds-data-list-panel
  [tdsData]="notifications"
  [tdsItemTemplate]="notifTemplate"
  [tdsHeaderTemplate]="headerTemplate"
  [tdsFooterTemplate]="footerTemplate"
  tdsMaxHeight="400px">
</tds-data-list-panel>

<ng-template #headerTemplate>
  <div class="panel-header">
    <h3>Thông báo</h3>
  </div>
</ng-template>
```

```typescript
import { TDSDataListPanelModule } from 'tds-ui/data-list';

@Component({
  standalone: true,
  imports: [TDSDataListPanelModule],
})
export class MyComponent {
  users: User[] = [];
  products: Product[] = [];
  isLoading = false;

  // Filter function cho client-side search
  filterProducts(term: string, item: Product): boolean {
    return item.name.toLowerCase().includes(term) ||
           item.category.toLowerCase().includes(term);
  }

  onSearch(searchTerm: string) {
    console.log('Search term:', searchTerm);
  }

  onServerSearch(searchTerm: string) {
    this.isLoading = true;
    // Gọi API để tìm kiếm
    this.productService.search(searchTerm).subscribe(data => {
      this.serverItems = data;
      this.isLoading = false;
    });
  }
}
```

## Notes

- Component sử dụng Angular signals (đòi hỏi Angular 16+)
- `tdsFilterFn` chỉ hoạt động khi `tdsServerSearch = false` (client-side filter)
- Khi `tdsServerSearch = true`, component không filter dữ liệu mà chỉ emit `tdsSearchChange` event
- `tdsItemTemplate` nhận context với `$implicit` là item hiện tại
- Dữ liệu được hiển thị trong container có chiều cao tối đa, hỗ trợ scroll khi quá nhiều items
- Empty state hiển thị tự động khi `tdsData` rỗng (trừ khi có custom `tdsEmptyTemplate`)
- Component sử dụng Angular signal-based `input()` / `output()` API (Angular 17.3+), không dùng `@Input`/`@Output` decorators truyền thống
- `tdsSearchChange` sử dụng `output<string>()` thay vì `EventEmitter<string>` — hành vi emit tương tự nhưng là signal-based
