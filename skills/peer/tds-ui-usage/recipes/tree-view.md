## Tree View

**Use case:** Hiển thị dữ liệu dạng cây phân cấp với checkbox (chọn nhiều), draggable (kéo thả sắp xếp), và expand/collapse.

**Components cần import:**
```typescript
import { TDSTreeModule } from 'tds-ui/tree';
import { TDSFormatEmitEvent, TDSTreeNodeOptions } from 'tds-ui/tree';
```

---

### 1. Tree cơ bản với Checkbox

```html
<tds-tree
  [data]="nodes"
  checkable
  [checkedKeys]="defaultCheckedKeys"
  [expandedKeys]="defaultExpandedKeys"
  [selectedKeys]="defaultSelectedKeys"
  (onClick)="onClick($event)"
  (onCheckBoxChange)="onCheck($event)"
  (onExpandChange)="onExpand($event)">
</tds-tree>
```

```typescript
import { Component } from '@angular/core';
import { TDSFormatEmitEvent, TDSTreeNodeOptions } from 'tds-ui/tree';

@Component({
  selector: 'app-tree-basic',
  templateUrl: './tree-basic.component.html'
})
export class TreeBasicComponent {
  defaultCheckedKeys = ['10020'];
  defaultSelectedKeys = ['10010'];
  defaultExpandedKeys = ['100', '1001'];

  nodes: TDSTreeNodeOptions[] = [
    {
      title: 'Phòng ban A',
      key: '100',
      children: [
        {
          title: 'Team A1',
          key: '1001',
          disabled: true,
          children: [
            { title: 'Nhân viên 1', key: '10010', isLeaf: true },
            { title: 'Nhân viên 2', key: '10011', isLeaf: true },
          ],
        },
        {
          title: 'Team A2',
          key: '1002',
          children: [
            { title: 'Nhân viên 3', key: '10020', isLeaf: true },
            { title: 'Nhân viên 4', key: '10021', isLeaf: true },
          ],
        },
      ],
    },
  ];

  onClick(event: any): void {
    console.log('Click:', event);
  }

  onCheck(event: TDSFormatEmitEvent): void {
    console.log('Check:', event);
  }

  onExpand(event: TDSFormatEmitEvent): void {
    console.log('Expand:', event);
  }
}
```

---

### 2. Tree Draggable (kéo thả sắp xếp)

```html
<tds-tree
  [data]="nodes"
  draggable
  blockNode
  (onDrop)="onDrop($event)">
</tds-tree>
```

```typescript
import { Component } from '@angular/core';
import { TDSFormatEmitEvent, TDSTreeNodeOptions } from 'tds-ui/tree';

@Component({
  selector: 'app-tree-draggable',
  templateUrl: './tree-draggable.component.html'
})
export class TreeDraggableComponent {
  nodes: TDSTreeNodeOptions[] = [
    {
      title: 'Danh mục 1',
      key: '0-0',
      expanded: true,
      children: [
        {
          title: 'Danh mục 1.1',
          key: '0-0-0',
          expanded: true,
          children: [
            { title: 'Sản phẩm A', key: '0-0-0-0', isLeaf: true },
            { title: 'Sản phẩm B', key: '0-0-0-1', isLeaf: true },
          ],
        },
        {
          title: 'Danh mục 1.2',
          key: '0-0-1',
          children: [
            { title: 'Sản phẩm C', key: '0-0-1-0', isLeaf: true },
          ],
        },
      ],
    },
  ];

  onDrop(event: TDSFormatEmitEvent): void {
    console.log('Drop:', event);
    // Xử lý cập nhật thứ tự sau khi kéo thả
  }
}
```

---

**Tips:**
- `[data]` — mảng `TDSTreeNodeOptions[]`, mỗi node có `title`, `key`, `children`, `isLeaf`
- `checkable` — hiện checkbox
- `draggable` — cho phép kéo thả node
- `blockNode` — click cả dòng thay vì chỉ text
- `isLeaf: true` — node lá (không có children)
- `disabled: true` — không cho click node
- `disableCheckbox: true` — không cho check (vẫn click được node)
- `[expandedKeys]` — danh sách key đang mở, có thể dùng `[(expandedKeys)]` two-way binding
- `[checkedKeys]` — danh sách key đã check
- `[selectedKeys]` — danh sách key đang select
- `(onDrop)` — event khi kéo thả xong, dùng để gọi API cập nhật thứ tự
- `(onCheckBoxChange)` — event khi check/uncheck
- `(onExpandChange)` — event khi expand/collapse node
