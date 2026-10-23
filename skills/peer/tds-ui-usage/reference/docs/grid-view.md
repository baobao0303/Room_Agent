# Grid View

Component hiển thị danh sách dữ liệu dạng lưới với virtual scrolling, hỗ trợ responsive và lazy loading. Tự động tính toán số cột dựa trên chiều rộng container.

**Selector:** `tds-grid-view`
**Import:** `import { TDSGridViewModule } from 'tds-ui/grid-view';`
**Export as:** `tdsGridView`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsData` | `Array<T>` | `[]` | Dữ liệu để hiển thị |
| `tdsCellWidth` | `number` | `150` | Chiều rộng mặc định của mỗi ô |
| `tdsCellMaxWidth` | `number` | `Infinity` | Chiều rộng tối đa của mỗi ô |
| `tdsCellHeight` | `number` | `200` | Chiều cao của mỗi ô |
| `tdsCellGutter` | `number` | `6` | Khoảng cách giữa các ô (padding) |
| `tdsItemTemplate` | `TemplateRef` | `null` | Template để render mỗi item |
| `tdsVirtualForTrackBy` | `TrackByFunction<T>` | `index => index` | Track by function cho virtual scroll |
| `tdsLoading` | `boolean` | `false` | Hiển thị loading spinner |
| `tdsScrolledIndex` | `number` | `0` | Index để scroll đến khi thay đổi |
| `tdsAppendOnly` | `boolean` | `false` | Chỉ append dữ liệu (không re-render toàn bộ) |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsPageSizeChange` | `EventEmitter<number>` | Emit khi số lượng item trên trang thay đổi |
| `tdsScrolledIndexChange` | `EventEmitter<number>` | Emit khi scroll index thay đổi |
| `tdsLoadMore` | `EventEmitter<void>` | Emit khi scroll đến cuối danh sách |

## Usage

```html
<!-- Basic grid view -->
<tds-grid-view 
  [tdsData]="items"
  [tdsCellWidth]="200"
  [tdsCellHeight]="250"
  [tdsCellGutter]="8">
  <ng-template let-item let-colIndex="colIdex" let-rowIndex="rowIdex">
    <div class="grid-item">
      <img [src]="item.image" [alt]="item.title">
      <h3>{{ item.title }}</h3>
      <p>{{ item.description }}</p>
    </div>
  </ng-template>
</tds-grid-view>

<!-- Grid view with loading -->
<tds-grid-view 
  [tdsData]="items"
  [tdsLoading]="isLoading"
  (tdsLoadMore)="loadMore()">
  <ng-template let-item>
    <div class="card">{{ item.name }}</div>
  </ng-template>
</tds-grid-view>

<!-- Responsive grid view with max width -->
<tds-grid-view 
  [tdsData]="products"
  [tdsCellWidth]="180"
  [tdsCellMaxWidth]="300"
  [tdsCellHeight]="220"
  [tdsCellGutter]="12"
  (tdsLoadMore)="onLoadMore()">
  <ng-template let-product>
    <tds-card [tdsBordered]="true">
      <tds-card-image [tdsSrc]="product.image"></tds-card-image>
      <tds-card-content>
        <h4>{{ product.name }}</h4>
        <p>{{ product.price }}</p>
      </tds-card-content>
    </tds-card>
  </ng-template>
</tds-grid-view>

<!-- Grid view with track by -->
<tds-grid-view 
  [tdsData]="users"
  [tdsVirtualForTrackBy]="trackByUserId"
  (tdsScrolledIndexChange)="onScrollIndexChange($event)">
  <ng-template let-user>
    <div class="user-card">
      <tds-avatar [tdsSrc]="user.avatar"></tds-avatar>
      <span>{{ user.name }}</span>
    </div>
  </ng-template>
</tds-grid-view>
```

```typescript
import { TDSGridViewModule } from 'tds-ui/grid-view';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [TDSGridViewModule, CommonModule],
})
export class MyComponent {
  items = [
    { id: 1, title: 'Item 1', image: '...', description: '...' },
    { id: 2, title: 'Item 2', image: '...', description: '...' },
    // ...
  ];
  
  isLoading = false;
  
  loadMore() {
    if (this.isLoading) return;
    this.isLoading = true;
    
    // Fetch more data
    this.dataService.getMoreItems().subscribe(newItems => {
      this.items = [...this.items, ...newItems];
      this.isLoading = false;
    });
  }
  
  trackByUserId(index: number, user: any): number {
    return user.id;
  }
  
  onScrollIndexChange(index: number) {
    console.log('Scrolled to index:', index);
  }
}
```

## Responsive Behavior

Grid view tự động tính toán số cột dựa trên:
- Chiều rộng của container component
- Chiều rộng mỗi ô (`tdsCellWidth`) + gutter
- Chiều rộng tối đa (`tdsCellMaxWidth`) nếu có

```html
<!-- Grid tự động responsive -->
<tds-grid-view 
  [tdsData]="items"
  [tdsCellWidth]="150"
  [tdsCellMaxWidth]="250"
  [tdsCellGutter]="10">
  <!-- Items sẽ tự động co giãn theo container width -->
</tds-grid-view>
```

## Infinite Scroll

```html
<tds-grid-view 
  [tdsData]="items"
  [tdsLoading]="isLoading"
  (tdsLoadMore)="loadMore()">
  <ng-template let-item>
    <div class="item">{{ item.name }}</div>
  </ng-template>
</tds-grid-view>
```

```typescript
loadMore() {
  this.isLoading = true;
  this.apiService.getItems(this.items.length, 20).subscribe(newItems => {
    this.items = [...this.items, ...newItems];
    this.isLoading = false;
  });
}
```

## Notes

- Component sử dụng `CdkVirtualScrollViewport` để tối ưu performance với lượng dữ liệu lớn
- `tdsCellGutter` được áp dụng double (x2) cho padding xung quanh mỗi ô
- Khi `tdsCellMaxWidth` > `tdsCellWidth`, component sẽ tự động mở rộng ô để lấp đầy khoảng trống
- `tdsLoadMore` emit khi scroll đến cuối danh sách (hết dữ liệu visible)
- `tdsScrolledIndex` có thể dùng để control scroll position từ ngoài component
- **Note:** `tdsAppendOnly` lacks `@Input()` decorator in the current codebase — it is a plain property, not a bindable Angular input. Setting it via `[tdsAppendOnly]` in templates will not work as expected until the decorator is added upstream
- Template variables available: `$implicit` (item data), `colIdex` (column index), `rowIdex` (row index)
- Component tự động tính toán lại layout khi resize window
- Dùng `tdsAppendOnly` = true khi chỉ thêm mới dữ liệu để tránh re-render không cần thiết
- `tdsPageSizeChange` emit khi số lượng item hiển thị trên trang thay đổi (do resize)
