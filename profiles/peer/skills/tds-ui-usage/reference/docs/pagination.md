# Pagination

Phân trang.

**Selector:** `tds-pagination`
**Import:** `import { TDSPaginationModule } from 'tds-ui/pagination';`
**Export as:** `tdsPagination`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `total` | `number` | `0` | Tổng số records |
| `pageIndex` | `number` | `1` | Trang hiện tại |
| `pageSize` | `number` | `10` | Số items mỗi trang |
| `pageSizeOptions` | `number[]` | `[10, 20, 30, 40]` | Tùy chọn page size |
| `showSizeChanger` | `boolean` | `false` | Hiển thị chọn page size |
| `showQuickJumper` | `boolean` | `false` | Hiển thị ô nhập trang |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'sm'` | Kích thước |
| `simple` | `boolean` | `false` | Chế độ đơn giản (prev/next) |
| `hideOnSinglePage` | `boolean` | `false` | Ẩn khi chỉ 1 trang |
| `showTotal` | `TemplateRef<{ $implicit: number; range: [number, number] }>` | `null` | Template hiển thị tổng |
| `itemRender` | `TemplateRef<PaginationItemRenderContext>` | `null` | Template custom item |
| `showRefresh` | `boolean` | `false` | Hiển thị nút refresh |
| `bordered` | `boolean` | `false` | Hiển thị border |
| `responsive` | `boolean` | `false` | Responsive size (tự động đổi size theo breakpoint) |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `pageIndexChange` | `EventEmitter<number>` | Khi đổi trang |
| `pageSizeChange` | `EventEmitter<number>` | Khi đổi page size |
| `clickRefresh` | `EventEmitter<MouseEvent>` | Khi click nút refresh |

## PaginationItemRenderContext Interface

```typescript
interface PaginationItemRenderContext {
  $implicit: PaginationItemType;
  page: number;
}

type PaginationItemType = 'page' | 'prev' | 'next' | 'prev_5' | 'next_5' | 'dot';
```

## Usage

```html
<tds-pagination
  [total]="totalRecords"
  [(pageIndex)]="currentPage"
  [(pageSize)]="pageSize"
  [pageSizeOptions]="[10, 20, 50, 100]"
  [showSizeChanger]="true"
  [showQuickJumper]="true"
  (pageIndexChange)="loadPage($event)">
</tds-pagination>
```

```typescript
import { TDSPaginationModule } from 'tds-ui/pagination';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-list',
  standalone: true,
  imports: [TDSPaginationModule, CommonModule]
})
export class ListComponent {
  totalRecords = 100;
  currentPage = 1;
  pageSize = 10;

  loadPage(page: number) {
    console.log('Loading page:', page);
    // Call API with page number
  }
}
```

## Notes

- `tds-table` có built-in pagination — dùng `tds-pagination` độc lập khi cần pagination cho layout khác
- Dùng `[(pageIndex)]` và `[(pageSize)]` để two-way binding
- `simple=true` hiển thị chỉ prev/next button, loại bỏ page number buttons
- Khi `hideOnSinglePage=true`, pagination sẽ ẩn nếu tổng record ≤ pageSize
- `responsive=true` tự động đổi size: `sm` cho breakpoint `xs`, `md` cho các breakpoint khác
- `showTotal` template nhận context: `{ $implicit: total, range: [start, end] }`
- `itemRender` template nhận context: `{ $implicit: type, page: number }`
- Component tự động validate pageIndex, không cho phép vượt quá tổng số trang
