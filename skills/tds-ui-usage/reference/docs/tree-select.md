# Tree Select

Chọn từ cấu trúc cây, thay thế cho cascader khi cần multi-select flexible.

**Selector:** `tds-tree-select`
**Import:** `import { TDSTreeSelectModule } from 'tds-ui/tree-select';`
**Export as:** `tdsTreeSelect`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsNodes` | `TDSTreeNodeOptions[] \| TDSTreeNode[]` | `[]` | Dữ liệu cây |
| `tdsPlaceHolder` | `string` | `''` | Placeholder |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa |
| `tdsMultiple` | `boolean` | `false` | Cho phép chọn nhiều |
| `tdsCheckable` | `boolean` | `false` | Dùng checkbox |
| `tdsShowSearch` | `boolean` | `false` | Tìm kiếm |
| `tdsSize` | `ButtonSize` (`'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`) | `'md'` | Kích thước |
| `tdsAllowClear` | `boolean` | `true` | Xóa giá trị |
| `tdsMaxTagCount` | `number` | — | Max tags hiển thị |
| `tdsDefaultExpandAll` | `boolean` | `false` | Mở rộng tất cả nodes mặc định |
| `tdsCheckStrictly` | `boolean` | `false` | Không auto-select parent/children |
| `tdsShowExpand` | `boolean` | `true` | Hiển thị nút mở rộng |
| `tdsShowLine` | `boolean` | `false` | Hiển thị các đường nối |
| `tdsId` | `string \| null` | `null` | ID cho component |
| `tdsShowArrow` | `boolean` | `true` | Hiển thị mũi tên dropdown |
| `tdsRequired` | `boolean` | `false` | Bắt buộc nhập |
| `tdsAsyncData` | `boolean` | `false` | Dữ liệu bất đồng bộ |
| `tdsHideUnMatched` | `boolean` | `false` | Ẩn các node không khớp khi tìm kiếm |
| `tdsShowIcon` | `boolean` | `false` | Hiển thị icon |
| `tdsBackdrop` | `boolean` | `false` | Hiển thị backdrop |
| `tdsPlacement` | `'bottomLeft' \| 'bottomRight' \| 'topLeft' \| 'topRight' \| ''` | `''` | Vị trí dropdown |
| `tdsDropdownMatchSelectWidth` | `boolean` | `true` | Dropdown width khớp với select |
| `tdsDropdownStyle` | `NgStyleInterface \| null` | `null` | Inline style cho dropdown |
| `tdsDropdownClassName` | `string` | — | CSS class cho dropdown |
| `tdsExpandedKeys` | `string[]` | — | Keys của nodes được mở rộng |
| `tdsExpandedIcon` | `TemplateRef` | — | Template cho icon mở rộng |
| `tdsNotFoundContent` | `string` | — | Nội dung khi không tìm thấy kết quả |
| `tdsDisplayWith` | `(node: TDSTreeNode) => string \| undefined` | — | Custom display function |
| `tdsMaxTagPlaceholder` | `TemplateRef<{ $implicit: TDSTreeNode[] }>` | — | Template cho max tag placeholder |
| `tdsSearchFunc` | `(node: TDSTreeNodeOptions, searchValue?: string) => boolean` | — | Custom search function |
| `tdsVirtualItemSize` | `number` | `28` | Kích thước item virtual scroll |
| `tdsVirtualMaxBufferPx` | `number` | `500` | Buffer tối đa virtual scroll |
| `tdsVirtualMinBufferPx` | `number` | `28` | Buffer tối thiểu virtual scroll |
| `tdsVirtualHeight` | `string \| null` | `null` | Chiều cao virtual scroll |
| `tdsOpen` | `boolean` | `false` | Trạng thái mở/đóng dropdown |
| `tdsTreeTemplate` | `TemplateRef<{ $implicit: TDSTreeNode; origin: TDSTreeNodeOptions }>` | — | Custom template cho tree node (có thể dùng `#tdsTreeTemplate` content child thay thế) |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsOpenChange` | `EventEmitter<boolean>` | Khi mở/đóng dropdown |
| `tdsCleared` | `EventEmitter<void>` | Khi xóa giá trị |
| `tdsRemoved` | `EventEmitter<TDSTreeNode>` | Khi xóa một node (multi-select) |
| `tdsExpandChange` | `EventEmitter<TDSFormatEmitEvent>` | Khi mở/đóng node |
| `tdsTreeClick` | `EventEmitter<TDSFormatEmitEvent>` | Khi click node |
| `tdsTreeCheckBoxChange` | `EventEmitter<TDSFormatEmitEvent>` | Khi checkbox thay đổi |

## TDSTreeNodeOptions structure

```typescript
interface TDSTreeNodeOptions {
  title: string;
  key: string;
  children?: TDSTreeNodeOptions[];
  isLeaf?: boolean;
  disabled?: boolean;
  selectable?: boolean;
}
```

## Usage

```html
<!-- Single Select -->
<tds-tree-select
  [(ngModel)]="selectedKey"
  [tdsNodes]="treeData"
  tdsPlaceHolder="Chọn phòng ban">
</tds-tree-select>

<!-- Multi-Select with Checkboxes -->
<tds-tree-select
  [(ngModel)]="selectedKeys"
  [tdsNodes]="treeData"
  [tdsMultiple]="true"
  [tdsCheckable]="true"
  tdsPlaceHolder="Chọn nhiều phòng ban">
</tds-tree-select>

<!-- With search -->
<tds-tree-select
  [(ngModel)]="selectedKey"
  [tdsNodes]="treeData"
  [tdsShowSearch]="true"
  tdsPlaceHolder="Tìm kiếm...">
</tds-tree-select>

<!-- Custom display -->
<tds-tree-select
  [(ngModel)]="selectedKey"
  [tdsNodes]="treeData"
  [tdsDisplayWith]="displayNode"
  tdsPlaceHolder="Chọn">
</tds-tree-select>
```

```typescript
import { TDSTreeSelectModule } from 'tds-ui/tree-select';
import { FormsModule } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSTreeSelectModule, FormsModule],
})
export class MyComponent {
  treeData = [
    {
      title: 'Công ty',
      key: 'company',
      children: [
        { title: 'Phòng IT', key: 'it', isLeaf: true },
        { title: 'Phòng HR', key: 'hr', isLeaf: true },
      ]
    }
  ];

  selectedKey: string | null = null;
  selectedKeys: string[] = [];

  displayNode(node: TDSTreeNode): string {
    return `${node.title} (${node.key})`;
  }
}
```

## Notes

- Dùng `tdsCheckable="true"` khi cần chọn nhiều với checkbox
- Value là `key` của node được chọn
- `tdsCheckStrictly="true"` khi không muốn parent/children tự động select theo
- `tdsMultiple="true"` trả về mảng keys, single mode trả về string hoặc null
- `tdsShowSearch="true"` để bật tìm kiếm
- `tdsDisplayWith` để custom hiển thị node
- `tdsVirtualHeight` để enable virtual scroll với cây lớn
- `tdsPlacement` để điều chỉnh vị trí dropdown
- `tdsDropdownClassName` để custom style dropdown
- `tdsSearchFunc` để custom logic tìm kiếm
- `tdsMaxTagCount` để giới hạn số tags hiển thị trong multi-select mode
- `tdsHideUnMatched="true"` để ẩn các node không khớp khi tìm kiếm
- Import Module vào `imports: []` của standalone component
- Hỗ trợ Reactive Forms và Template-driven Forms
- **Note**: Size `'xs'` is accepted in the `tdsSize` input type (`ButtonSize`) but does not have a corresponding host binding class in the current implementation — only `sm`, `md`, `lg`, `xl` have `.tds-tree-select-{size}` host bindings
