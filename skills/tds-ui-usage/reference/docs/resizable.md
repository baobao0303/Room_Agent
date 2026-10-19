# Resizable

Directive cho phép resize element bằng cách kéo các handle ở cạnh hoặc góc. Hỗ trợ lock aspect ratio, preview, và grid-based resizing.

**Selector:** `[tds-resizable]`
**Import:** `import { TDSResizableDirective, TDSResizeHandlesModule, TDSResizeHandleModule } from 'tds-ui/resizable';`
**Export as:** `tdsResizable`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsBounds` | `'window' \| 'parent' \| ElementRef<HTMLElement>` | `'parent'` | Giới hạn resize: window, parent, hoặc custom element |
| `tdsMaxHeight` | `number` | - | Chiều cao tối đa (px) |
| `tdsMaxWidth` | `number` | - | Chiều rộng tối đa (px) |
| `tdsMinHeight` | `number` | `40` | Chiều cao tối thiểu (px) |
| `tdsMinWidth` | `number` | `40` | Chiều rộng tối thiểu (px) |
| `tdsLockAspectRatio` | `boolean` | `false` | Khóa tỷ lệ khung hình |
| `tdsPreview` | `boolean` | `false` | Hiển thị preview khi resize |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa resize |
| `tdsGridColumnCount` | `number` | `-1` | Số cột grid (cho grid-based resize) |
| `tdsMaxColumn` | `number` | `-1` | Số cột tối đa |
| `tdsMinColumn` | `number` | `-1` | Số cột tối thiểu |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsResize` | `EventEmitter<TDSResizeEvent>` | Phát ra trong quá trình resize |
| `tdsResizeStart` | `EventEmitter<TDSResizeEvent>` | Phát ra khi bắt đầu resize |
| `tdsResizeEnd` | `EventEmitter<TDSResizeEvent>` | Phát ra khi kết thúc resize |

## TDSResizeHandleModule Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDirection` | `TDSResizeDirection` | `'bottomRight'` | Hướng resize: `top`, `right`, `bottom`, `left`, `topRight`, `bottomRight`, `bottomLeft`, `topLeft` |
| `tdsCursorType` | `'window' \| 'grid'` | `'window'` | Kiểu cursor |

## TDSResizeHandlesModule Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDirections` | `Array<TDSResizeDirection \| TDSResizeHandleOption>` | All 8 directions | Mảng các hướng resize |

## Usage

```html
<!-- Basic resizable với handles mặc định -->
<div tds-resizable
     class="resizable-box"
     [tdsMinWidth]="100"
     [tdsMinHeight]="100"
     [tdsMaxWidth]="500"
     [tdsMaxHeight]="500"
     (tdsResizeEnd)="onResizeEnd($event)">
  <tds-resize-handles></tds-resize-handles>
  Content here
</div>

<!-- Lock aspect ratio -->
<div tds-resizable
     [tdsLockAspectRatio]="true"
     [tdsMinWidth]="200"
     [tdsMinHeight]="150">
  <tds-resize-handles [tdsDirections]="['bottomRight', 'topLeft']"></tds-resize-handles>
  4:3 content
</div>

<!-- Preview mode -->
<div tds-resizable
     [tdsPreview]="true"
     [tdsMinWidth]="150"
     [tdsMinHeight]="150"
     (tdsResize)="onResizing($event)"
     (tdsResizeEnd)="onResizeEnd($event)">
  <tds-resize-handles></tds-resize-handles>
  Drag to resize
</div>

<!-- Grid-based resizing -->
<div tds-resizable
     [tdsGridColumnCount]="12"
     [tdsMinColumn]="2"
     [tdsMaxColumn]="6"
     (tdsResizeEnd)="onColumnResize($event)">
  <tds-resize-handles [tdsDirections]="['right']"></tds-resize-handles>
  Grid item
</div>

<!-- Custom bounds -->
<div tds-resizable
     [tdsBounds]="containerRef"
     [tdsMinWidth]="100">
  <tds-resize-handles></tds-resize-handles>
  Bounded to container
</div>

<!-- Custom handle placement -->
<div tds-resizable>
  <tds-resize-handle tdsDirection="right"></tds-resize-handle>
  <tds-resize-handle tdsDirection="bottom"></tds-resize-handle>
  Only right and bottom handles
</div>
```

```typescript
import { TDSResizableDirective, TDSResizeHandlesModule, TDSResizeHandleModule } from 'tds-ui/resizable';
import { TDSResizeEvent } from 'tds-ui/resizable';

@Component({
  standalone: true,
  imports: [TDSResizableDirective, TDSResizeHandlesModule, TDSResizeHandleModule],
})
export class MyComponent {
  @ViewChild('container') containerRef!: ElementRef;

  onResizing(event: TDSResizeEvent) {
    console.log('Resizing:', event.width, event.height);
  }

  onResizeEnd(event: TDSResizeEvent) {
    console.log('Resize ended:', event.width, event.height);
    if (event.col !== undefined) {
      console.log('Column span:', event.col);
    }
  }

  onColumnResize(event: TDSResizeEvent) {
    console.log('New column span:', event.col);
  }
}
```

## TDSResizeEvent Interface

```typescript
interface TDSResizeEvent {
  width?: number;      // Chiều rộng mới (px)
  height?: number;     // Chiều cao mới (px)
  col?: number;        // Số cột (chỉ khi dùng grid)
  mouseEvent?: MouseEvent | TouchEvent; // Event gốc
}
```

## Notes

- Mặc định directive không hiển thị handle - cần thêm `<tds-resize-handles>` hoặc `<tds-resize-handle>`
- `tdsBounds` giới hạn element không thể resize vượt ngoài:
  - `'parent'`: Không resize lớn hơn parent element
  - `'window'`: Không resize lớn hơn viewport
  - `ElementRef`: Custom boundary element
- `tdsPreview=true` hiển thị preview box trong khi resize, chỉ apply size khi thả chuột
- Grid-based resize (`tdsGridColumnCount`): snap size theo số cột, useful cho dashboard layout
- Khi `tdsLockAspectRatio=true`, aspect ratio được tính từ kích thước ban đầu
- Cursor tự động thay đổi theo hướng resize
- Hỗ trợ cả mouse và touch events
