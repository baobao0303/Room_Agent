# Transfer

Component chuyển đổi dữ liệu giữa hai danh sách (dual-list box). Hỗ trợ search, filter, và custom render.

**Selector:** `tds-transfer`
**Import:** `import { TDSTransferModule } from 'tds-ui/transfer';`
**Export as:** `tdsTransfer`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDataSource` | `TransferItem[]` | `[]` | Dữ liệu nguồn |
| `tdsTargetKeys` | `string[]` | `[]` | Keys của items ở target (right side) |
| `tdsSelectedKeys` | `string[]` | `[]` | Keys của items được chọn |
| `tdsTitles` | `string[]` | `['', '']` | Tiêu đề 2 cột (source, target) |
| `tdsOperations` | `string[]` | `[]` | Text cho 2 nút operation |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa component |
| `tdsShowSelectAll` | `boolean` | `true` | Hiển thị checkbox "Select All" |
| `tdsShowSearch` | `boolean` | `false` | Hiển thị ô tìm kiếm |
| `tdsFilterOption` | `function` | — | Custom filter function |
| `tdsSearchPlaceholder` | `string` | — | Placeholder cho ô tìm kiếm |
| `tdsNotFoundContent` | `string` | — | Text khi không tìm thấy kết quả |
| `tdsItemUnit` | `string` | — | Đơn vị cho 1 item (vd: 'item') |
| `tdsItemsUnit` | `string` | — | Đơn vị cho nhiều items (vd: 'items') |
| `tdsListStyle` | `object` | `{}` | CSS style cho danh sách |
| `tdsCanMove` | `function` | — | Validate trước khi move (return `Observable<TransferItem[]>`) |
| `tdsRender` | `TemplateRef` | — | Custom render cho từng item |
| `tdsRenderList` | `TemplateRef[]` | — | Custom render cho cả 2 danh sách |
| `tdsFooter` | `TemplateRef` | — | Custom footer cho danh sách |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsChange` | `EventEmitter<TransferChange>` | Khi items chuyển giữa 2 danh sách |
| `tdsSearchChange` | `EventEmitter<TransferSearchChange>` | Khi search text thay đổi |
| `tdsSelectChange` | `EventEmitter<TransferSelectChange>` | Khi select/deselect item |

## TransferItem structure

```typescript
interface TransferItem {
  title: string;              // Hiển thị
  key: string;                // Unique ID (required)
  direction?: 'left' | 'right'; // Vị trí hiện tại
  disabled?: boolean;         // Vô hiệu hóa (không thể move)
  checked?: boolean;          // Được chọn hay không
  hide?: boolean;             // Ẩn khi filter
  [key: string]: any;         // Custom data
}
```

## TransferChange structure

```typescript
interface TransferChange {
  from: 'left' | 'right';     // Direction nguồn
  to: 'left' | 'right';       // Direction đích
  list: TransferItem[];       // Items được chuyển
}
```

## TransferSelectChange structure

```typescript
interface TransferSelectChange {
  direction: 'left' | 'right'; // Danh sách được select
  checked: boolean;            // Select hay deselect
  list: TransferItem[];        // Tất cả items được chọn
  item?: TransferItem;         // Item được click (nếu có)
}
```

## Usage

```html
<!-- Basic transfer -->
<tds-transfer
  [tdsDataSource]="dataSource"
  [(tdsTargetKeys)]="targetKeys"
  [tdsTitles]="['Available', 'Selected']">
</tds-transfer>

<!-- With search -->
<tds-transfer
  [tdsDataSource]="dataSource"
  [(tdsTargetKeys)]="targetKeys"
  [tdsShowSearch]="true"
  [tdsFilterOption]="filterOption">
</tds-transfer>

<!-- With custom item render -->
<ng-template #itemTemplate let-item>
  <span class="custom-item">
    <i class="tdsi-user"></i>
    {{ item.title }} - {{ item.department }}
  </span>
</ng-template>

<tds-transfer
  [tdsDataSource]="dataSource"
  [(tdsTargetKeys)]="targetKeys"
  [tdsRender]="itemTemplate">
</tds-transfer>

<!-- With custom list render -->
<ng-template #listTemplate let-items let-direction="direction">
  <div class="custom-list">
    <div *ngFor="let item of items">{{ item.title }}</div>
  </div>
</ng-template>

<tds-transfer
  [tdsDataSource]="dataSource"
  [(tdsTargetKeys)]="targetKeys"
  [tdsRenderList]="[listTemplate, listTemplate]">
</tds-transfer>

<!-- With move validation -->
<tds-transfer
  [tdsDataSource]="dataSource"
  [(tdsTargetKeys)]="targetKeys"
  [tdsCanMove]="canMove"
  (tdsChange)="handleChange($event)">
</tds-transfer>
```

```typescript
import { TDSTransferModule } from 'tds-ui/transfer';
import { of, Observable } from 'rxjs';

@Component({
  standalone: true,
  imports: [TDSTransferModule, FormsModule],
})
export class MyComponent {
  dataSource: TransferItem[] = [
    { key: '1', title: 'Item 1', disabled: false },
    { key: '2', title: 'Item 2', disabled: false },
    { key: '3', title: 'Item 3', disabled: true },
    { key: '4', title: 'Item 4', disabled: false },
  ];

  targetKeys: string[] = [];

  // Custom filter function
  filterOption(inputValue: string, item: TransferItem): boolean {
    return item.title.toLowerCase().includes(inputValue.toLowerCase());
  }

  // Validate before move
  canMove(arg: TransferCanMove): Observable<TransferItem[]> {
    // Chỉ cho move max 3 items
    if (arg.list.length > 3) {
      console.warn('Chỉ được chuyển tối đa 3 items!');
      return of([]);
    }
    return of(arg.list);
  }

  // Handle change event
  handleChange(event: TransferChange) {
    console.log('Moved from', event.from, 'to', event.to);
    console.log('Items:', event.list);
    // Xử lý logic business
  }
}
```

## Advanced Usage

```html
<!-- Real user assignment example -->
<tds-transfer
  [tdsDataSource]="users"
  [(tdsTargetKeys)]="assignedUserIds"
  [tdsTitles]="["All Users", "Team Members"]"
  [tdsOperations]="["Remove", "Add"]"
  [tdsShowSearch]="true"
  [tdsItemUnit]="'user'"
  [tdsItemsUnit]="'users'"
  [tdsCanMove]="validateMove"
  [tdsRender]="userTemplate">
</tds-transfer>

<ng-template #userTemplate let-item>
  <div class="user-item">
    <tds-avatar [tdsSrc]="item.avatar" [tdsSize]="'sm'"></tds-avatar>
    <span>{{ item.name }}</span>
    <span class="role">{{ item.role }}</span>
  </div>
</ng-template>
```

```typescript
users: TransferItem[] = [
  {
    key: 'u1',
    title: 'John Doe',
    name: 'John Doe',
    avatar: '/avatar1.jpg',
    role: 'Developer'
  },
  {
    key: 'u2',
    title: 'Jane Smith',
    name: 'Jane Smith',
    avatar: '/avatar2.jpg',
    role: 'Designer'
  }
];

assignedUserIds: string[] = ['u1'];

validateMove(arg: TransferCanMove): Observable<TransferItem[]> {
  // Validate business logic
  const allowed = arg.list.filter(item => {
    // Ví dụ: không cho move nếu user đã có task đang chạy
    return !this.hasActiveTasks(item.key);
  });
  return of(allowed);
}

hasActiveTasks(userId: string): boolean {
  // Check logic
  return false;
}
```

## Notes

- Dùng `[(tdsTargetKeys)]` để two-way binding keys của target list
- `tdsCanMove` để validate trước khi move (return empty array để hủy)
- `tdsFilterOption` để custom filter logic khi search
- `tdsRender` để custom hiển thị từng item
- `tdsRenderList` để custom hiển thị cả danh sách (header, list, footer)
- `tdsShowSearch="true"` để enable filter ở cả 2 danh sách
- Items có `disabled: true` sẽ không được select và move
- Component tự động quản lý trạng thái checked/unchecked
- Hỗ trợ RTL layout
- Search hoạt động độc lập ở 2 danh sách
- Có thể dùng với Reactive Forms (ControlValueAccessor)
