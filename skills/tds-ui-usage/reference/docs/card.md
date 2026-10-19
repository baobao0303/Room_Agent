# Card

Thẻ container với các section header, content, actions, và image. Hỗ trợ loading state và bordered.

**Selector:** `tds-card`
**Import:** `import { TDSCardModule } from 'tds-ui/card';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsBordered` | `boolean` | `false` | Hiển thị viền |
| `tdsLoading` | `boolean` | `false` | Hiển thị trạng thái loading |
| `tdsSize` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước card |

## Card Sections

**Component** | **Selector** | **Description**
-------------|--------------|--------------
`TDSCardHeaderComponent` | `tds-card-header` | Phần header của card
`TDSCardContentComponent` | `tds-card-content` | Phần nội dung chính
`TDSCardActionsComponent` | `tds-card-actions` | Phần hành động (buttons, links)
`TDSCardTitleComponent` | `tds-card-title` | Tiêu đề card
`TDSCardImageDirective` | `[tds-card-image]` | Hình ảnh card (attribute directive, không phải element)

## Usage

```html
<!-- Basic card -->
<tds-card [tdsBordered]="true">
  <tds-card-header>
    <tds-card-title>Card Title</tds-card-title>
  </tds-card-header>
  <tds-card-content>
    <p>Card content goes here...</p>
  </tds-card-content>
  <tds-card-actions>
    <button tds-button color="primary">Action</button>
  </tds-card-actions>
</tds-card>

<!-- Card with loading state -->
<tds-card [tdsLoading]="isLoading">
  <tds-card-content>
    Loading content...
  </tds-card-content>
</tds-card>

<!-- Card with image -->
<tds-card>
  <img tds-card-image src="https://example.com/image.jpg" alt="Card image" />
  <tds-card-header>
    <tds-card-title>Image Card</tds-card-title>
  </tds-card-header>
  <tds-card-content>
    <p>Description goes here...</p>
  </tds-card-content>
</tds-card>

<!-- Size variants -->
<tds-card tdsSize="sm">Small Card</tds-card>
<tds-card tdsSize="md">Medium Card</tds-card>
<tds-card tdsSize="lg">Large Card</tds-card>
<tds-card tdsSize="xl">Extra Large Card</tds-card>
```

```typescript
import { TDSCardModule } from 'tds-ui/card';

@Component({
  standalone: true,
  imports: [TDSCardModule],
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

## Card Grid Example

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  @for (item of items; track item.id) {
    <tds-card [tdsBordered]="true">
      <tds-card-header>
        <tds-card-title>{{ item.title }}</tds-card-title>
      </tds-card-header>
      <tds-card-content>
        <p>{{ item.description }}</p>
      </tds-card-content>
      <tds-card-actions>
        <button tds-button color="primary" size="sm">View</button>
        <button tds-button color="secondary" size="sm">Edit</button>
      </tds-card-actions>
    </tds-card>
  }
</div>
```

## Notes

- Các section components là optional — chỉ dùng khi cần
- `tdsLoading` hiển thị loading skeleton trên toàn bộ card
- `tdsBordered` thêm viền cho card
- `tdsSize` controls padding và spacing bên trong card
- Có thể dùng `<ng-content>` thay vì section components cho cấu trúc đơn giản
- `tds-card-image` là attribute directive (`[tds-card-image]`), dùng trên element như `<img tds-card-image>` — không phải element `<tds-card-image>`
- Chỉ cần import `TDSCardModule`, nó đã export tất cả sub-components/directives
