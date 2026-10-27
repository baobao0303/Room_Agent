# List

Component hiển thị danh sách các items với layout linh hoạt, hỗ trợ header, footer, pagination, loading state và grid layout.

**Selector:** `tds-list` hoặc `[tds-list]`
**Import:** `import { TDSListModule } from 'tds-ui/list';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsBordered` | `boolean` | `false` | Hiển thị viền cho list |
| `tdsDataSource` | `any[]` | — | Dữ liệu để render list items động |
| `tdsFooter` | `string \| TemplateRef<void>` | — | Footer của list |
| `tdsHeader` | `string \| TemplateRef<void>` | — | Header của list |
| `tdsItemLayout` | `'vertical' \| 'horizontal'` | `'horizontal'` | Layout của items: `vertical` hoặc `horizontal` |
| `tdsLoadMore` | `TemplateRef<void>` | — | Template cho load more button |
| `tdsLoading` | `boolean` | `false` | Hiển thị trạng thái loading |
| `tdsNoResult` | `string \| TemplateRef<void>` | — | Content hiển thị khi list rỗng |
| `tdsPagination` | `TemplateRef<void>` | — | Template cho pagination |
| `tdsRenderItem` | `TemplateRef<{ $implicit: any; index: number }>` | — | Template để render từng item từ `tdsDataSource` |
| `tdsSize` | `'sm' \| 'md' \| 'lg'` | `'md'` | Kích thước của list |
| `tdsSplit` | `boolean` | `true` | Hiển thị đường phân cách giữa các items |

## List Item

**Selector:** `tds-list-item` hoặc `[tds-list-item]`

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsActions` | `TemplateRef<void>[]` | `[]` | Mảng các action templates |
| `tdsContent` | `string \| TemplateRef<void>` | — | Content của list item |
| `tdsExtra` | `TemplateRef<void>` | — | Extra content (hiển thị bên phải trong horizontal layout) |
| `tdsNoFlex` | `boolean` | `false` | Tắt flex layout cho item |

## List Item Meta

**Selector:** `tds-list-item-meta` hoặc `[tds-list-item-meta]`

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsAvatar` | `string \| TemplateRef<void>` | — | Avatar của item (string URL hoặc template) |
| `tdsDescription` | `string \| TemplateRef<void>` | — | Mô tả của item |
| `tdsTitle` | `string \| TemplateRef<void>` | — | Tiêu đề của item |

## List Item Meta Sub-components

**Component** | **Selector** | **Description**
-------------|--------------|--------------
`TDSListItemMetaTitleModule` | `tds-list-item-meta-title` | Tiêu đề của meta item
`TDSListItemMetaDescriptionModule` | `tds-list-item-meta-description` | Mô tả của meta item
`TDSListItemMetaAvatarModule` | `tds-list-item-meta-avatar` | Avatar của meta item

## List Item Actions

**Component** | **Selector** | **Description**
-------------|--------------|--------------
`TDSListItemActionsModule` | `ul[tds-list-item-actions]` | Container cho các actions
`TDSListItemActionModule` | `tds-list-item-action` | Một action đơn lẻ
`TDSListItemExtraModule` | `tds-list-item-extra` hoặc `[tds-list-item-extra]` | Extra content

## List Sections

**Component** | **Selector** | **Description**
-------------|--------------|--------------
`TDSListHeaderModule` | `tds-list-header` | Header section của list
`TDSListFooterModule` | `tds-list-footer` | Footer section của list
`TDSListPaginationModule` | `tds-list-pagination` | Pagination section
`TDSListEmptyModule` | `tds-list-empty` | Empty state (hiển thị khi không có data)
`TDSListLoadMoreDirective` | `tds-list-load-more` | Load more directive
`TDSListGridDirective` | `tds-list[tdsGrid]` | Grid layout directive

## Usage

```html
<!-- Basic list -->
<tds-list [tdsBordered]="true">
  <tds-list-item>
    <tds-list-item-meta
      [tdsAvatar]="'https://example.com/avatar.jpg'"
      tdsTitle="Title 1"
      tdsDescription="Description 1">
    </tds-list-item-meta>
  </tds-list-item>
  <tds-list-item>
    <tds-list-item-meta
      tdsTitle="Title 2"
      tdsDescription="Description 2">
    </tds-list-item-meta>
  </tds-list-item>
</tds-list>

<!-- With header and footer -->
<tds-list
  [tdsHeader]="'List Header'"
  [tdsFooter]="'List Footer'"
  [tdsBordered]="true">
  <tds-list-item>
    <tds-list-item-meta tdsTitle="Item 1"></tds-list-item-meta>
  </tds-list-item>
</tds-list>

<!-- Vertical layout -->
<tds-list tdsItemLayout="vertical">
  <tds-list-item>
    <tds-list-item-meta
      tdsTitle="Title"
      tdsDescription="Description">
    </tds-list-item-meta>
    <tds-list-item-extra>
      <button tds-button>View</button>
    </tds-list-item-extra>
  </tds-list-item>
</tds-list>

<!-- With actions -->
<tds-list>
  <tds-list-item [tdsActions]="actionTemplates">
    <tds-list-item-meta
      tdsTitle="Item with actions"
      tdsDescription="Click actions below">
    </tds-list-item-meta>
  </tds-list-item>
</tds-list>

<ng-template #actionTemplate1>
  <a href="#">Edit</a>
</ng-template>
<ng-template #actionTemplate2>
  <a href="#">Delete</a>
</ng-template>

<!-- Dynamic list with data source -->
<tds-list
  [tdsDataSource]="items"
  [tdsRenderItem]="itemTemplate"
  [tdsLoading]="isLoading">
</tds-list>

<ng-template #itemTemplate let-item let-index="index">
  <tds-list-item>
    <tds-list-item-meta
      [tdsTitle]="item.title"
      [tdsDescription]="item.description">
    </tds-list-item-meta>
  </tds-list-item>
</ng-template>

<!-- With load more -->
<tds-list [tdsLoadMore]="loadMoreTemplate">
  <tds-list-item>
    <tds-list-item-meta tdsTitle="Item 1"></tds-list-item-meta>
  </tds-list-item>
</tds-list>

<ng-template #loadMoreTemplate>
  <button tds-button (click)="loadMore()">Load More</button>
</ng-template>

<!-- With pagination -->
<tds-list [tdsPagination]="paginationTemplate">
  <tds-list-item>
    <tds-list-item-meta tdsTitle="Item 1"></tds-list-item-meta>
  </tds-list-item>
</tds-list>

<ng-template #paginationTemplate>
  <tds-pagination [tdsTotal]="100" [tdsPageIndex]="1"></tds-pagination>
</ng-template>

<!-- Different sizes -->
<tds-list tdsSize="sm">Small List</tds-list>
<tds-list tdsSize="md">Medium List</tds-list>
<tds-list tdsSize="lg">Large List</tds-list>

<!-- Without split -->
<tds-list [tdsSplit]="false">
  <tds-list-item>
    <tds-list-item-meta tdsTitle="Item 1"></tds-list-item-meta>
  </tds-list-item>
  <tds-list-item>
    <tds-list-item-meta tdsTitle="Item 2"></tds-list-item-meta>
  </tds-list-item>
</tds-list>
```

```typescript
import {
  TDSListModule,
  TDSListItemModule,
  TDSListItemMetaModule,
  TDSListItemMetaTitleModule,
  TDSListItemMetaDescriptionModule,
  TDSListItemMetaAvatarModule
} from 'tds-ui/list';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [
    CommonModule,
    TDSListModule,
    TDSListItemModule,
    TDSListItemMetaModule
  ]
})
export class MyComponent {
  isLoading = false;
  items = [
    { id: 1, title: 'Item 1', description: 'Description 1' },
    { id: 2, title: 'Item 2', description: 'Description 2' },
    { id: 3, title: 'Item 3', description: 'Description 3' }
  ];

  actionTemplates = [
    this.actionTemplate1,
    this.actionTemplate2
  ];

  loadMore() {
    // Load more items
  }
}
```

## Grid Layout Example

```html
<!-- Grid layout with column count -->
<tds-list [tdsGrid]="{ gutter: 16, column: 3 }">
  <tds-list-item *ngFor="let item of items">
    <tds-list-item-meta tdsTitle="{{ item.title }}"></tds-list-item-meta>
  </tds-list-item>
</tds-list>

<!-- Responsive grid -->
<tds-list [tdsGrid]="{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4, xl: 6 }">
  <tds-list-item *ngFor="let item of items">
    <tds-list-item-meta tdsTitle="{{ item.title }}"></tds-list-item-meta>
  </tds-list-item>
</tds-list>
```

```typescript
import { TDSListGrid } from 'tds-ui/list';

@Component({
  // ...
})
export class MyComponent {
  gridConfig: TDSListGrid = {
    gutter: 16,
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
    xl: 6
  };
}
```

## Custom Empty State

```html
<tds-list [tdsNoResult]="noResultTemplate" [tdsDataSource]="[]">
</tds-list>

<ng-template #noResultTemplate>
  <div class="custom-empty">
    <p>No items found</p>
    <button tds-button>Create New</button>
  </div>
</ng-template>
```

## Notes

- `tdsItemLayout='horizontal'`: Meta và extra content nằm ngang hàng (mặc định)
- `tdsItemLayout='vertical'`: Meta và extra content nằm dọc
- `tdsSplit` controls đường phân cách giữa các items (mặc định `true`)
- `tdsBordered` thêm viền cho toàn bộ list
- `tdsLoading` hiển thị spinner và placeholder khi loading
- `tdsDataSource` + `tdsRenderItem` cho phép render list động từ data
- `tdsNoResult` hiển thị khi `tdsDataSource` rỗng
- `tdsGrid` hỗ trợ responsive grid layout với các breakpoints: `xs`, `sm`, `md`, `lg`, `xl`, `xxl`
- Column count options: `1`, `2`, `3`, `4`, `6`, `8`, `12`, `24`
- Component tự động detect và thêm class `tds-list-something-after-last-item` khi có footer/pagination/load-more
- Hỗ trợ RTL (right-to-left)
- Actions được hiển thị với đường phân cách tự động
- Extra content chỉ hiển thị bên phải trong horizontal layout
- **Note:** `tdsSize` input accepts `'sm'`/`'md'`/`'lg'` (ButtonSize), but host bindings check for `'small'`/`'large'` — size CSS classes (`tds-list-lg`, `tds-list-sm`) may not apply correctly unless the code is updated to match
