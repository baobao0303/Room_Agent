# Empty

Trạng thái trống với hình ảnh và mô tả, hỗ trợ i18n.

**Selector:** `tds-empty`
**Import:** `import { TDSEmptyModule } from 'tds-ui/empty';`
**Export as:** `tdsEmpty`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `notFoundImage` | `'default' \| 'simple' \| string \| TemplateRef<void> \| null` | `'default'` | Hình ảnh: built-in (`default`, `simple`) hoặc custom URL/Template |
| `notFoundContent` | `string \| TemplateRef<void> \| null \| undefined` | `undefined` | Nội dung mô tả |
| `notFoundFooter` | `string \| TemplateRef<void>` | — | Footer content (thường là action button) |

## Key Outputs

None.

## Built-in Images

| Value | Description |
|-------|-------------|
| `'default'` | Hình ảnh mặc định (chi tiết hơn) |
| `'simple'` | Hình ảnh đơn giản |

## Usage

```html
<!-- Default -->
<tds-empty></tds-empty>

<!-- Custom content -->
<tds-empty notFoundContent="Không tìm thấy dữ liệu"></tds-empty>

<!-- Custom image -->
<tds-empty
  notFoundImage="/assets/images/no-data.png"
  notFoundContent="Chưa có sản phẩm nào">
</tds-empty>

<!-- With footer action -->
<tds-empty
  notFoundContent="Không tìm thấy kết quả"
  notFoundFooter="Tạo mới">
</tds-empty>

<!-- Template content -->
<tds-empty [notFoundContent]="contentTpl">
  <ng-template #contentTpl>
    <p>Không có dữ liệu</p>
    <small>Vui lòng thử lại sau</small>
  </ng-template>
</tds-empty>

<!-- Template footer with action -->
<tds-empty
  notFoundContent="Danh sách trống"
  [notFoundFooter]="footerTpl">
  <ng-template #footerTpl>
    <button tds-button color="primary" (click)="onCreate()">
      Tạo mới
    </button>
  </ng-template>
</tds-empty>

<!-- Custom image template -->
<tds-empty [notFoundImage]="imageTpl">
  <ng-template #imageTpl>
    <img src="/custom-empty.png" alt="Empty" />
  </ng-template>
</tds-empty>
```

```typescript
import { TDSEmptyModule } from 'tds-ui/empty';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [TDSEmptyModule, TDSButtonModule]
})
export class UserListComponent {
  users: User[] = [];

  onCreate() {
    // Handle create action
  }
}
```

## Notes

- Component tự động hiển thị text i18n khi không cung cấp `notFoundContent`
- Built-in images (`default`, `simple`) được SVG inline, không cần load external
- `notFoundFooter` thường dùng để đặt action button (Tạo mới, Thử lại, etc.)
- Hỗ trợ TemplateRef cho full customization
- Theme và style có thể customize qua CSS variables

## TDSEmbedEmptyComponent

Internal component dùng để render empty state trong các component khác (table, select, tree-select, cascader, transfer, list).

**Selector:** `tds-embed-empty`
**Export as:** `tdsEmbedEmpty`
**Import:** Exported from `TDSEmptyModule` / `tds-ui/empty`

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `componentName` | `string \| undefined` | `undefined` | Tên component cha (xác định size: `table`/`list` = normal, `select`/`tree-select`/`cascader`/`transfer` = small) |
| `specificContent` | `TDSEmptyCustomContent \| undefined` | `undefined` | Custom content override (string, TemplateRef, hoặc Component Type) |

### Behavior

- Khi `specificContent` không được cung cấp, component hiển thị `<tds-empty>` mặc định với size phù hợp
- Size `normal` dùng `notFoundImage="simple"` với class `tds-empty-normal`
- Size `small` dùng `notFoundImage="simple"` với class `tds-empty-small`
- Hỗ trợ global default empty content qua `TDSConfigService` config key `TDSDefaultEmptyContent`

## i18n

Component tự động load text từ i18n service:

```typescript
// Default i18n keys
Empty: {
  description: 'Trống'
}
```

Override text qua i18n config nếu cần.
