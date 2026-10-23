# Tree

Component hiển thị dữ liệu dạng cây phân cấp. Hỗ trợ chọn, checkbox, drag-drop, search, và virtual scroll.

**Selector:** `tds-tree`
**Import:** `import { TDSTreeModule } from 'tds-ui/tree';`
**Export as:** `tdsTree`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `data` | `TDSTreeNodeOptions[] \| TDSTreeNode[]` | `[]` | Dữ liệu cây (chấp cả raw options hoặc tree node instances) |
| `expandedKeys` | `TDSTreeNodeKey[]` | `[]` | Keys của nodes đang mở rộng |
| `selectedKeys` | `TDSTreeNodeKey[]` | `[]` | Keys của nodes được chọn |
| `checkedKeys` | `TDSTreeNodeKey[]` | `[]` | Keys của nodes được checked |
| `checkable` | `boolean` | `false` | Hiển thị checkbox |
| `checkStrictly` | `boolean` | `false` | Không auto-select parent/children khi check |
| `multiple` | `boolean` | `false` | Cho phép chọn nhiều node |
| `selectMode` | `boolean` | `false` | Chế độ select (cho tree-select) |
| `showIcon` | `boolean` | `false` | Hiển thị icon |
| `showLine` | `boolean` | `false` | Hiển thị đường nối |
| `showExpand` | `boolean` | `true` | Hiển thị nút mở rộng |
| `expandAll` | `boolean` | `false` | Mở rộng tất cả nodes |
| `asyncData` | `boolean` | `false` | Dữ liệu bất đồng bộ |
| `draggable` | `boolean` | `false` | Cho phép drag-drop nodes |
| `hideUnMatched` | `boolean` | `false` | Ẩn nodes không khớp khi search |
| `blockNode` | `boolean` | `true` | Node chiếm toàn bộ chiều rộng |
| `searchValue` | `string` | `''` | Giá trị tìm kiếm |
| `searchFunc` | `function` | — | Custom search function |
| `beforeDrop` | `function` | — | Callback trước khi drop (return `Observable<boolean>`) |
| `expandedIcon` | `TemplateRef` | — | Custom icon cho node đã mở rộng |
| `treeTemplate` | `TemplateRef` | — | Custom template cho tree node |
| `virtualItemSize` | `number` | `28` | Chiều cao mỗi item khi virtual scroll (px) |
| `virtualMaxBufferPx` | `number` | `500` | Max buffer size khi virtual scroll |
| `virtualMinBufferPx` | `number` | `28` | Min buffer size khi virtual scroll |
| `virtualHeight` | `string` | — | Chiều cao viewport khi virtual scroll |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `onExpandedKeysChange` | `EventEmitter<string[]>` | Khi expanded keys thay đổi |
| `onSelectedKeysChange` | `EventEmitter<string[]>` | Khi selected keys thay đổi |
| `onCheckedKeysChange` | `EventEmitter<TDSTreeNodeKey[]>` | Khi checked keys thay đổi |
| `onSearchValueChange` | `EventEmitter<TDSFormatEmitEvent>` | Khi search value thay đổi |
| `onClick` | `EventEmitter<TDSFormatEmitEvent>` | Khi click node |
| `onDblClick` | `EventEmitter<TDSFormatEmitEvent>` | Khi double-click node |
| `onContextMenu` | `EventEmitter<TDSFormatEmitEvent>` | Khi right-click node |
| `onCheckBoxChange` | `EventEmitter<TDSFormatEmitEvent>` | Khi checkbox thay đổi |
| `onExpandChange` | `EventEmitter<TDSFormatEmitEvent>` | Khi node mở rộng/thu gọn |
| `onDragStart` | `EventEmitter<TDSFormatEmitEvent>` | Khi bắt đầu drag |
| `onDragEnter` | `EventEmitter<TDSFormatEmitEvent>` | Khi drag enter node |
| `onDragOver` | `EventEmitter<TDSFormatEmitEvent>` | Khi drag over node |
| `onDragLeave` | `EventEmitter<TDSFormatEmitEvent>` | Khi drag leave node |
| `onDrop` | `EventEmitter<TDSFormatEmitEvent>` | Khi drop node |
| `onDragEnd` | `EventEmitter<TDSFormatEmitEvent>` | Khi kết thúc drag |

## TDSTreeNodeOptions structure

```typescript
interface TDSTreeNodeOptions {
  title: string;                      // Hiển thị
  key: string;                        // Unique ID
  icon?: string;                      // Icon class
  isLeaf?: boolean;                   // Node lá (không có con)
  checked?: boolean;                  // Trạng thái checked
  selected?: boolean;                 // Trạng thái selected
  selectable?: boolean;               // Có thể chọn hay không
  disabled?: boolean;                 | Vô hiệu hóa
  disableCheckbox?: boolean;          // Vô hiệu hóa checkbox
  expanded?: boolean;                 // Đã mở rộng
  children?: TDSTreeNodeOptions[];    // Nodes con
  [key: string]: any;                 // Custom data
}
```

## TDSFormatEmitEvent structure

```typescript
interface TDSFormatEmitEvent {
  eventName: string;      // Tên event
  node: TDSTreeNode;      // Node được trigger
  event: MouseEvent | KeyboardEvent | DragEvent;  // Native event
}
```

## Usage

```html
<!-- Basic tree -->
<tds-tree
  [data]="treeData"
  [(expandedKeys)]="expandedKeys"
  [(selectedKeys)]="selectedKeys">
</tds-tree>

<!-- With checkboxes -->
<tds-tree
  [data]="treeData"
  [checkable]="true"
  [(checkedKeys)]="checkedKeys"
  (onCheckBoxChange)="onCheckChange($event)">
</tds-tree>

<!-- With search -->
<tds-tree
  [data]="treeData"
  [searchValue]="searchText"
  [hideUnMatched]="true">
</tds-tree>
<input [(ngModel)]="searchText" placeholder="Search...">

<!-- Draggable tree -->
<tds-tree
  [data]="treeData"
  [draggable]="true"
  [beforeDrop]="beforeDrop"
  (onDrop)="onDrop($event)">
</tds-tree>

<!-- With custom template -->
<ng-template #treeTemplate let-node let-origin="origin">
  <span class="custom-node">
    <i class="tdsi-folder"></i>
    {{ origin.title }}
    <span class="extra-info">{{ origin.count }}</span>
  </span>
</ng-template>

<tds-tree
  [data]="treeData"
  [treeTemplate]="treeTemplate">
</tds-tree>

<!-- Virtual scroll cho cây lớn -->
<tds-tree
  [data]="largeTreeData"
  [virtualHeight]="'400px'"
  [virtualItemSize]="28">
</tds-tree>
```

```typescript
import { TDSTreeModule } from 'tds-ui/tree';

@Component({
  standalone: true,
  imports: [TDSTreeModule, FormsModule],
})
export class MyComponent {
  treeData = [
    {
      title: 'Công ty ABC',
      key: 'company',
      expanded: true,
      children: [
        {
          title: 'Phòng IT',
          key: 'it',
          icon: 'tdsi-code',
          children: [
            { title: 'Team Frontend', key: 'fe', isLeaf: true },
            { title: 'Team Backend', key: 'be', isLeaf: true },
          ]
        },
        {
          title: 'Phòng HR',
          key: 'hr',
          icon: 'tdsi-team',
          isLeaf: true
        }
      ]
    }
  ];

  expandedKeys: string[] = ['company'];
  selectedKeys: string[] = [];
  checkedKeys: string[] = [];
  searchText = '';

  onCheckChange(event: TDSFormatEmitEvent) {
    console.log('Checked:', event.node.key);
    console.log('All checked keys:', this.checkedKeys);
  }

  beforeDrop(confirm: TDSFormatBeforeDropEvent): Observable<boolean> {
    // Validate trước khi drop
    const canDrop = confirm.dragNode.key !== 'company'; // Không cho drop root
    return of(canDrop);
  }

  onDrop(event: TDSFormatEmitEvent) {
    console.log('Dropped:', event.node.key);
    // Xử lý update tree data
  }
}
```

## Notes

- Dùng `[(expandedKeys)]`, `[(selectedKeys)]`, `[(checkedKeys)]` để two-way binding
- `checkStrictly="true"` khi không muốn parent/children auto-select
- `draggable="true"` kết hợp với `beforeDrop` để validate drag-drop
- `virtualHeight` cho tree lớn (>1000 nodes) để tối ưu performance
- `searchValue` tự động mở rộng nodes khớp và ẩn nodes không khớp
- `showLine="true"` hiển thị đường nối giữa các nodes
- `asyncData="true"` cho lazy load children nodes
- Component hỗ trợ ControlValueAccessor (dùng với Reactive Forms)
- Hỗ trợ RTL layout
- Có thể dùng `ContentChild` với template ref `#treeTemplate` để custom node content
