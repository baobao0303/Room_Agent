# Breadcrumb

Điều hướng phân cấp (breadcrumb trail).

**Selector:** `tds-breadcrumb`, `tds-breadcrumb-item`
**Import:** `import { TDSBreadCrumbModule } from 'tds-ui/breadcrumb';`
**Export as:** `tdsBreadcrumb`, `tdsBreadcrumbItem`

## tds-breadcrumb Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `autoGenerate` | `boolean` | `false` | Tự động generate từ route |
| `separator` | `string \| TemplateRef<void> \| null` | `'tdsi-chevron-right-fill'` | Ký tự phân cách |
| `routeLabel` | `string` | `'breadcrumb'` | Route data key để lấy label |
| `routeLabelFn` | `(label: string) => string` | `label => label` | Transform function cho label |
| `tdsRouteFn` | `(route: string) => string` | `route => route` | Transform function cho URL route |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |

## tds-breadcrumb-item Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `overlay` | `TDSDropdownMenuComponent` | — | Dropdown menu khi hover |

## BreadcrumbOption Interface

```typescript
interface BreadcrumbOption {
  label: string;
  params: Params;
  url: string;
}
```

## Usage

```html
<!-- Basic breadcrumb -->
<tds-breadcrumb>
  <tds-breadcrumb-item>
    <a routerLink="/">Trang chủ</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item>
    <a routerLink="/products">Sản phẩm</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item>Chi tiết</tds-breadcrumb-item>
</tds-breadcrumb>

<!-- Custom separator -->
<tds-breadcrumb [separator]="'/'">
  <tds-breadcrumb-item>
    <a routerLink="/">Home</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item>
    <a routerLink="/about">About</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item>Contact</tds-breadcrumb-item>
</tds-breadcrumb>

<!-- Custom separator with icon -->
<tds-breadcrumb [separator]="'tdsi-arrow-right-fill'">
  <tds-breadcrumb-item>
    <a routerLink="/">Home</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item>
    <a routerLink="/products">Products</a>
  </tds-breadcrumb-item>
</tds-breadcrumb>

<!-- Custom separator with template -->
<tds-breadcrumb [separator]="separatorTpl">
  <tds-breadcrumb-item>
    <a routerLink="/">Home</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item>
    <a routerLink="/about">About</a>
  </tds-breadcrumb-item>
</tds-breadcrumb>

<ng-template #separatorTpl>
  <span class="text-primary-500">→</span>
</ng-template>

<!-- Auto generate from router -->
<tds-breadcrumb [autoGenerate]="true"></tds-breadcrumb>

<!-- Auto generate with custom label key -->
<tds-breadcrumb
  [autoGenerate]="true"
  routeLabel="title">
</tds-breadcrumb>

<!-- Auto generate with custom label transform -->
<tds-breadcrumb
  [autoGenerate]="true"
  [routeLabelFn]="transformLabel">
</tds-breadcrumb>

<!-- Auto generate with custom route transform -->
<tds-breadcrumb
  [autoGenerate]="true"
  [tdsRouteFn]="transformRoute">
</tds-breadcrumb>

<!-- With overlay dropdown -->
<tds-breadcrumb>
  <tds-breadcrumb-item>
    <a routerLink="/">Home</a>
  </tds-breadcrumb-item>
  <tds-breadcrumb-item [overlay]="menu">
    <a routerLink="/products">Products</a>
  </tds-breadcrumb-item>
</tds-breadcrumb>

<tds-dropdown-menu #menu="tdsDropdownMenu">
  <button tds-dropdown-item (click)="navigate('/products/electronics')">Electronics</button>
  <button tds-dropdown-item (click)="navigate('/products/clothing')">Clothing</button>
</tds-dropdown-menu>

<!-- With theme -->
<tds-breadcrumb tdsTheme="light">
  <tds-breadcrumb-item>
    <a routerLink="/">Home</a>
  </tds-breadcrumb-item>
</tds-breadcrumb>

<tds-breadcrumb tdsTheme="dark">
  <tds-breadcrumb-item>
    <a routerLink="/">Home</a>
  </tds-breadcrumb-item>
</tds-breadcrumb>
```

```typescript
import { TDSBreadCrumbModule } from 'tds-ui/breadcrumb';
import { TDSDropdownMenuModule } from 'tds-ui/dropdown';
import { RouterModule } from '@angular/router';

@Component({
  standalone: true,
  imports: [
    TDSBreadCrumbModule,
    TDSDropdownMenuModule,
    RouterModule
  ]
})
export class MyComponent {
  // Custom label transformation
  transformLabel(label: string): string {
    return label.toUpperCase();
  }

  // Custom route transformation
  transformRoute(route: string): string {
    return `/admin${route}`;
  }

  navigate(url: string) {
    // Navigate to URL
  }
}

// Route configuration for autoGenerate
const routes = [
  {
    path: 'products',
    data: { breadcrumb: 'Sản phẩm' },  // Default key: 'breadcrumb'
    children: [
      {
        path: 'electronics',
        data: { breadcrumb: 'Điện tử' }
      }
    ]
  }
];
```

## Notes

- Component classes: `TDSBreadCrumbModule`
- Default separator là icon `tdsi-chevron-right-fill`
- Sử dụng `routerLink` trực tiếp trong `<a>` bên trong `tds-breadcrumb-item`
- `autoGenerate` cần có Router configuration với route data
- `routeLabel` key trong route data để lấy breadcrumb label (default: `'breadcrumb'`)
- `routeLabelFn` function để transform label trước khi hiển thị
- `tdsRouteFn` function để transform URL route trước khi navigate
- `overlay` input cho phép hiển thị dropdown menu khi hover vào breadcrumb item
- `tdsTheme` hỗ trợ: `default`, `light`, `dark`
- Supports RTL direction
- Khi dùng `autoGenerate`, breadcrumb tự động cập nhật khi route thay đổi
- Separator có thể là string (icon class hoặc text) hoặc TemplateRef
- Breadcrumb item cuối cùng không có separator
- Auto generate chỉ parse routes trong `PRIMARY_OUTLET` (router-outlet không có name)
- `params` trong `BreadcrumbOption` chứa route parameters
- Khi lazy loading modules, breadcrumbs vẫn hoạt động đúng
