# Card View

Component hiển thị thẻ với header, cover, body, và actions. Hỗ trợ loading state, bordered, hoverable, và nhiều kích thước.

**Selector:** `tds-card-view`
**Import:** `import { TDSCardViewModule } from 'tds-ui/card-view';`
**Export as:** `tdsCardView`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsBordered` | `boolean` | `false` | Hiển thị viền cho card |
| `tdsLoading` | `boolean` | `false` | Hiển thị trạng thái loading với skeleton |
| `tdsHoverable` | `boolean` | `false` | Hiệu ứng hover khi rê chuột |
| `tdsBodyStyle` | `NgStyleInterface \| null` | `null` | Custom style cho phần body |
| `tdsCover` | `TemplateRef<void>` | `undefined` | Template cho phần cover (hình ảnh bìa) |
| `tdsActions` | `Array<TemplateRef<void>>` | `[]` | Danh sách các action buttons |
| `tdsType` | `'inner' \| 'default' \| null` | `'default'` | Loại card: inner hoặc default |
| `tdsSize` | `'default' \| 'small'` | `'default'` | Kích thước card |
| `tdsTitle` | `string \| TemplateRef<void>` | `undefined` | Tiêu đề của card |
| `tdsExtra` | `string \| TemplateRef<void>` | `undefined` | Nội dung bổ sung bên cạnh title |

## Sub-components

**Component** | **Selector** | **exportAs** | **Description**
-------------|--------------|------------|--------------
`TDSCardViewMetaComponent` | `tds-card-view-meta` | `tdsCardViewMeta` | Phần meta thông tin (avatar, title, description)
`TDSCardViewTabComponent` | `tds-card-view-tab` | `tdsCardViewTab` | Phần tab cho card
`TDSCardViewGridDirective` | `[tds-card-view-grid]` | `tdsCardViewGrid` | Directive để tạo grid layout

## TDSCardViewMetaComponent Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsTitle` | `string \| TemplateRef<void> \| null` | `null` | Tiêu đề meta |
| `tdsDescription` | `string \| TemplateRef<void> \| null` | `null` | Mô tả meta |
| `tdsAvatar` | `TemplateRef<void> \| null` | `null` | Avatar template |

## TDSCardViewGridDirective Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsHoverable` | `boolean` | `true` | Hiệu ứng hover cho grid items |

## Usage

```html
<!-- Basic card view -->
<tds-card-view [tdsTitle]="'Card Title'" [tdsBordered]="true">
  <p>Card content goes here...</p>
</tds-card-view>

<!-- Card with loading state -->
<tds-card-view [tdsLoading]="isLoading">
  <p>Loading content...</p>
</tds-card-view>

<!-- Card with cover and actions -->
<tds-card-view [tdsTitle]="'Product Card'" [tdsBordered]="true">
  <ng-template #cover>
    <img [alt]="cover" tds-image [tdsSrc]="'https://example.com/image.jpg'" />
  </ng-template>
  <ng-template [tdsCover]="cover"></ng-template>

  <p>Product description goes here...</p>

  <ng-template #action1>
    <button tds-button color="primary">View</button>
  </ng-template>
  <ng-template #action2>
    <button tds-button color="secondary">Edit</button>
  </ng-template>
  <ng-template [tdsActions]="[action1, action2]"></ng-template>
</tds-card-view>

<!-- Card with meta -->
<tds-card-view [tdsBordered]="true">
  <tds-card-view-meta [tdsTitle]="'John Doe'" [tdsDescription]="'Software Engineer'">
    <ng-template #avatarTemplate>
      <tds-avatar tdsSrc="https://example.com/avatar.jpg"></tds-avatar>
    </ng-template>
    <ng-template [tdsAvatar]="avatarTemplate"></ng-template>
  </tds-card-view-meta>
  <p>Additional content...</p>
</tds-card-view>

<!-- Small size card -->
<tds-card-view tdsSize="small" [tdsTitle]="'Small Card'">
  <p>Compact card content...</p>
</tds-card-view>

<!-- Inner type card -->
<tds-card-view tdsType="inner" [tdsTitle]="'Inner Card'">
  <p>Inner card style...</p>
</tds-card-view>

<!-- Hoverable card -->
<tds-card-view [tdsHoverable]="true" [tdsBordered]="true">
  <p>Hover over me...</p>
</tds-card-view>
```

```typescript
import { TDSCardViewModule } from 'tds-ui/card-view';

@Component({
  standalone: true,
  imports: [TDSCardViewModule],
})
export class MyComponent {
  isLoading = false;

  loadData() {
    this.isLoading = true;
    // Load data...
    setTimeout(() => {
      this.isLoading = false;
    }, 2000);
  }
}
```

## Grid Layout Example

```html
<div tds-card-view-grid [tdsHoverable]="true">
  @for (item of items; track item.id) {
    <tds-card-view [tdsTitle]="item.title" [tdsBordered]="true">
      <tds-card-view-meta [tdsTitle]="item.author" [tdsDescription]="item.date">
        <ng-template #avatar>
          <tds-avatar [tdsSrc]="item.avatar"></tds-avatar>
        </ng-template>
        <ng-template [tdsAvatar]="avatar"></ng-template>
      </tds-card-view-meta>
      <p>{{ item.description }}</p>
    </tds-card-view>
  }
</div>
```

## Card with Tabs

```html
<tds-card-view [tdsTitle]="'Card with Tabs'">
  <tds-card-view-tab>
    <ng-template tds-tab-set>
      <tds-tabset>
        <tds-tab [tdsTitle]="'Tab 1'">Content 1</tds-tab>
        <tds-tab [tdsTitle]="'Tab 2'">Content 2</tds-tab>
      </tds-tabset>
    </ng-template>
  </tds-card-view-tab>
  <p>Card body content...</p>
</tds-card-view>
```

## Notes

- `tdsLoading` hiển thị skeleton placeholder thay vì nội dung thực
- `tdsBordered` thêm viền cho card
- `tdsHoverable` thêm hiệu ứng hover khi rê chuột
- `tdsSize` controls kích thước padding và spacing
- `tdsType="inner"` cho style card lồng bên trong các container khác
- `tdsBodyStyle` cho phép custom CSS style cho phần body
- `tdsActions` phân chia đều chiều rộng cho các action buttons
- `tdsCover` thường dùng để hiển thị hình ảnh bìa
- `tds-card-view-meta` useful cho hiển thị thông tin người dùng, tác giả, v.v.
- Component hỗ trợ RTL (right-to-left) layout
- Grid directive `tds-card-view-grid` giúp tạo responsive grid layout cho nhiều cards
- Sub-components (`TDSCardViewMetaComponent`, `TDSCardViewTabComponent`, `TDSCardViewGridDirective`) là standalone, không có separate module — dùng `TDSCardViewModule` để import tất cả
- `exportAs`: `tdsCardView` (card-view), `tdsCardViewMeta` (card-view-meta), `tdsCardViewTab` (card-view-tab), `tdsCardViewGrid` (card-view-grid)
