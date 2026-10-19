# Filter Status

Component hiển thị trạng thái filter dạng tab/segmented control, hỗ trợ forms integration và router linking.

**Selector:** `tds-filter-status`
**Import:** `import { TDSFilterStatusModule } from 'tds-ui/filter-status';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `disabled` | `boolean` | `false` | Disable toàn bộ component |
| `linkRouter` | `boolean` | `false` | Kích hoạt router linking mode |
| `linkExact` | `boolean` | `true` | Exact match khi active router link |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `selectChange` | `EventEmitter<any>` | Khi giá trị được chọn thay đổi |

## Filter Status Item Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `string \| null` | `null` | Tên hiển thị của item |
| `value` | `any \| null` | `null` | Giá trị của item |
| `count` | `number \| null` | `null` | Số lượng hiển thị (badge) |
| `disabled` | `boolean` | `false` | Disable item riêng lẻ |

## Sub-Components

### Filter Status Link (`tds-filter-status-link`)

Dùng thay cho `tds-filter-status-item` khi cần router integration. Hoạt động cùng `linkRouter` input trên component cha.

**Selector:** `tds-filter-status-link`
**Export as:** `tdsFilterLink`

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | `any \| null` | `null` | Giá trị của link item |
| `name` | `string \| null` | `null` | Tên hiển thị |
| `count` | `number \| null` | `null` | Số lượng hiển thị (badge) |
| `disabled` | `boolean` | `false` | Disable item |

Requires `[routerLink]` binding on inner `<a>` element using `tds-filter-status-router-link` directive.

### Filter Status Router Link (`a[tds-filter-status-router-link]`)

Directive bắt `routerLink` từ `<a>` element bên trong `tds-filter-status-link`.

**Selector:** `a[tds-filter-status-router-link]`
**Export as:** `tdsFilterStatusRouterLink`

Dùng để filter-status có thể detect active route dựa trên `routerLink` của thẻ `<a>`.

```html
<tds-filter-status-link [value]="'/dashboard'">
  <a tds-filter-status-router-link [routerLink]="['/dashboard']">Dashboard</a>
</tds-filter-status-link>
```

## Data Interface

```typescript
interface TDSFilterStatusItemDTO {
  name: string;           // Tên hiển thị
  value: any;             // Giá trị của item
  count: number;          // Số lượng
  disabled: boolean;      // Trạng thái disabled
}

interface FilterTabTemplateContext {
  disable: boolean;
  active: boolean;
  count: boolean;
  name: string;
}
```

## Usage

```html
<!-- Basic filter status with ng-content -->
<tds-filter-status [(ngModel)]="selectedFilter" (selectChange)="onFilterChange($event)">
  <tds-filter-status-item [value]="'all'" [name]="'All'"></tds-filter-status-item>
  <tds-filter-status-item [value]="'active'" [name]="'Active'"></tds-filter-status-item>
  <tds-filter-status-item [value]="'inactive'" [name]="'Inactive'"></tds-filter-status-item>
</tds-filter-status>

<!-- With count badges -->
<tds-filter-status [(ngModel)]="selectedStatus">
  <tds-filter-status-item [value]="'open'" [name]="'Open'" [count]="12"></tds-filter-status-item>
  <tds-filter-status-item [value]="'pending'" [name]="'Pending'" [count]="5"></tds-filter-status-item>
  <tds-filter-status-item [value]="'closed'" [name]="'Closed'" [count]="8"></tds-filter-status-item>
</tds-filter-status>

<!-- With router linking -->
<tds-filter-status 
  [linkRouter]="true" 
  [linkExact]="true"
  [(ngModel)]="selectedTab">
  <tds-filter-status-link [value]="'/dashboard'" [routerLink]="['/dashboard']">
    Dashboard
  </tds-filter-status-link>
  <tds-filter-status-link [value]="'/reports'" [routerLink]="['/reports']">
    Reports
  </tds-filter-status-link>
  <tds-filter-status-link [value]="'/settings'" [routerLink]="['/settings']">
    Settings
  </tds-filter-status-link>
</tds-filter-status>

<!-- With custom template -->
<tds-filter-status [(ngModel)]="selectedView">
  <tds-filter-status-item [value]="'grid'">
    Grid View
    <ng-template tds-filter-status-template let-context>
      <div class="custom-item" [class.active]="context.active">
        <i class="icon-grid"></i>
        <span>Grid</span>
      </div>
    </ng-template>
  </tds-filter-status-item>
  <tds-filter-status-item [value]="'list'">
    List View
  </tds-filter-status-item>
</tds-filter-status>

<!-- Disabled state -->
<tds-filter-status [disabled]="true">
  <tds-filter-status-item [value]="'1'" [name]="'Option 1'"></tds-filter-status-item>
  <tds-filter-status-item [value]="'2'" [name]="'Option 2'"></tds-filter-status-item>
</tds-filter-status>
```

```typescript
import { TDSFilterStatusModule } from 'tds-ui/filter-status';
import { Component } from '@angular/core';

@Component({
  selector: 'app-filter-status-demo',
  standalone: true,
  imports: [TDSFilterStatusModule],
  template: `
    <h3>Filter Status</h3>
    <tds-filter-status 
      [(ngModel)]="selectedStatus"
      (selectChange)="onStatusChange($event)">
      <tds-filter-status-item [value]="'all'" [name]="'All Items'" [count]="totalItems"></tds-filter-status-item>
      <tds-filter-status-item [value]="'active'" [name]="'Active'" [count]="activeCount"></tds-filter-status-item>
      <tds-filter-status-item [value]="'archived'" [name]="'Archived'" [count]="archivedCount"></tds-filter-status-item>
    </tds-filter-status>
    
    <p>Selected: {{ selectedStatus }}</p>
  `
})
export class FilterStatusDemoComponent {
  selectedStatus = 'all';
  totalItems = 100;
  activeCount = 45;
  archivedCount = 55;

  onStatusChange(value: any) {
    console.log('Status changed to:', value);
    // Load data based on filter
  }
}
```

## Router Integration

```typescript
import { TDSFilterStatusModule } from 'tds-ui/filter-status';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-filter-status-router-demo',
  standalone: true,
  imports: [TDSFilterStatusModule],
  template: `
    <tds-filter-status 
      [linkRouter]="true"
      [linkExact]="false"
      [(ngModel)]="currentRoute">
      <tds-filter-status-link [value]="'/users'" [routerLink]="['/users']">
        Users
      </tds-filter-status-link>
      <tds-filter-status-link [value]="'/products'" [routerLink]="['/products']">
        Products
      </tds-filter-status-link>
      <tds-filter-status-link [value]="'/orders'" [routerLink]="['/orders']">
        Orders
      </tds-filter-status-link>
    </tds-filter-status>
  `
})
export class FilterStatusRouterDemoComponent {
  currentRoute = '';
}
```

## Notes

- Component hỗ trợ `ControlValueAccessor` - có thể dùng với `[(ngModel)]` hoặc Reactive Forms
- ExportAs: `tdsFilterStatus` để truy cập component instance
- `linkRouter="true"` yêu cầu `RouterModule` đã được imported
- Khi `linkExact="true"` (default), router link chỉ active khi URL khớp hoàn toàn
- Hỗ trợ custom template với directive `tds-filter-status-template`
- Class `tds-filter-status-item-active` được thêm vào item đang được chọn
- Class `tds-filter-status-item-disabled` được thêm vào item bị disable
- Import Module vào `imports: []` của standalone component
- Hỗ trợ RTL layout
