# Column Settings

Component cho phép hiển thị và cấu hình các cột của bảng/data grid với tính năng ẩn/hiện cột và drag-drop để sắp xếp thứ tự.

**Selector:** `tds-column-settings`
**Import:** `import { TDSColumnSettingsModule } from 'tds-ui/column-settings';`
**Export as:** `tdsColumnSettings`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsData` | `TDSColumnSettingsDTO[]` | `[]` | Danh sách cấu hình các cột |
| `tdsPlacement` | `string \| string[]` | `'bottomRight'` | Vị trí hiển thị popover |
| `tdsVisible` | `boolean` | `false` | Trạng thái visible của popover |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa component |
| `tdsLoading` | `boolean` | `false` | Hiển thị trạng thái loading |
| `tdsOverlayClassName` | `string` | `'tds-column-settings-overlay'` | Class name tùy chỉnh cho overlay |
| `tdsSortable` | `boolean` | `false` | Cho phép drag-drop để sắp xếp cột |
| `tdsHeaderTemplate` | `string \| TemplateRef` | `undefined` | Template header tùy chỉnh |
| `tdsFooterTemplate` | `string \| TemplateRef` | `undefined` | Template footer tùy chỉnh |
| `tdsWidth` | `number` | `undefined` | Chiều rộng của popover |
| `tdsMaxHeight` | `number \| string` | `600` | Chiều cao tối đa của popover |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsDataChange` | `EventEmitter<TDSColumnSettingsDTO[]>` | Emit khi dữ liệu thay đổi (check/uncheck hoặc drag-drop) |
| `tdsVisibleChange` | `EventEmitter<boolean>` | Emit khi trạng thái visible thay đổi |

## Type: TDSColumnSettingsDTO

```typescript
interface TDSColumnSettingsDTO {
  tdsField: string;                          // Field name/ID của cột
  tdsTitle: string | TemplateRef<void>;      // Tiêu đề cột
  tdsChecked: boolean;                       // Trạng thái hiển thị cột
  tdsDisabled?: boolean;                     // Vô hiệu hóa checkbox
  tdsIndeterminate?: boolean;                // Trạng thái indeterminate
  tdsLeft?: boolean;                         // Cố định bên trái
  tdsRight?: boolean;                        // Cố định bên phải
  tdsWidth?: string | null;                  // Chiều rộng cột
  [key: string]: any;                        // Custom properties
}
```

## Usage

### Basic

```html
<tds-column-settings
  [(tdsData)]="listColumn"
  (tdsDataChange)="onDataChange($event)">
</tds-column-settings>
```

### With sortable (drag-drop)

```html
<tds-column-settings
  [(tdsData)]="listColumn"
  (tdsDataChange)="onDataChange($event)"
  [tdsSortable]="true">
</tds-column-settings>
```

### With header/footer template

Header và footer hiển thị bên trong popover, phía trên và dưới danh sách checkbox.

```html
<tds-column-settings
  [(tdsData)]="listColumn"
  (tdsDataChange)="onDataChange($event)"
  [tdsSortable]="true"
  [tdsHeaderTemplate]="headerTpl"
  [tdsFooterTemplate]="footerTpl">
</tds-column-settings>

<ng-template #headerTpl>
  <div class="px-3 py-2 tds-body-2">Hiển thị cột</div>
</ng-template>

<ng-template #footerTpl>
  <div class="px-3 py-2">
    <button tds-button tdsType="flat" (click)="resetColumns()">Reset mặc định</button>
  </div>
</ng-template>
```

```typescript
import { TDSColumnSettingsModule, TDSColumnSettingsDTO } from 'tds-ui/column-settings';

@Component({
  standalone: true,
  imports: [TDSColumnSettingsModule],
})
export class MyComponent {
  listColumn: TDSColumnSettingsDTO[] = [
    { tdsTitle: 'Họ tên', tdsField: 'name', tdsChecked: true },
    { tdsTitle: 'Tuổi', tdsField: 'age', tdsChecked: false },
    { tdsTitle: 'Địa chỉ', tdsField: 'address', tdsChecked: false },
  ];

  onDataChange(columns: TDSColumnSettingsDTO[]) {
    console.log('Columns changed:', columns);
  }
}
```

## Notes

- Component đã tích hợp sẵn button + popover, không cần wrap thêm popover bên ngoài
- Nên dùng `[(tdsData)]` two-way binding để tự cập nhật danh sách cột
- Khi `tdsSortable = true`, cho phép drag-drop để thay đổi thứ tự cột
- Mỗi lần thay đổi (check/uncheck hoặc drag-drop) sẽ emit `tdsDataChange`
- `tdsDisabled` trên `TDSColumnSettingsDTO` ngăn người dùng ẩn cột quan trọng
