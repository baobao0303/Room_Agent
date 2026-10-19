## CRUD với Drawer

**Use case:** Tạo CRUD form trong drawer (panel trượt từ bên cạnh), sử dụng `TDSDrawerService.create()` để mở custom component. Tương tự CRUD với Modal nhưng dùng drawer cho không gian rộng hơn.

**File Structure:**
```
src/app/design-preview/pages/{page-name}/
├── {page-name}.component.ts                 (list page — dùng TDSDrawerService)
└── {page-name}-form-drawer.component.ts     (drawer form — dùng TDSDrawerRef)
```

**Components cần import:**

*List page:*
```typescript
import { TDSDrawerModule, TDSDrawerService } from 'tds-ui/drawer';
import { TDSButtonModule } from 'tds-ui/button';
import { TDSDataTableModule } from 'tds-ui/data-table';
import { TDSMessageService } from 'tds-ui/message';
```

*Drawer form component:*
```typescript
import { TDSDrawerRef, TDS_DRAWER_DATA } from 'tds-ui/drawer';
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSInputModule } from 'tds-ui/tds-input';
import { TDSButtonModule } from 'tds-ui/button';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';
```

---

### List page (mở drawer)

```html
<!-- Nút thêm mới -->
<button tds-button color="primary" (click)="openAdd()">
  <i class="tdsi-plus-fill mr-2"></i>Thêm mới
</button>

<!-- Data table -->
<tds-data-table [tdsData]="data" [tdsLoading]="loading" [tdsTotal]="total"
  [(tdsPageIndex)]="pageIndex" [(tdsPageSize)]="pageSize"
  [tdsFrontPagination]="false" (tdsQueryParams)="onQueryParams($event)">

  <tds-data-table-column tdsField="name" tdsTitle="Tên"></tds-data-table-column>
  <tds-data-table-column tdsField="email" tdsTitle="Email"></tds-data-table-column>
  <tds-data-table-column tdsTitle="Thao tác" [tdsContent]="commandTpl" tdsWidth="110px">
    <ng-template #commandTpl let-dataRow>
      <button tds-button-flat-icon color="primary" (click)="openEdit(dataRow)">
        <i class="tdsi-edit-fill"></i>
      </button>
      <button tds-button-flat-icon color="error" (click)="onDelete(dataRow)">
        <i class="tdsi-trash-fill"></i>
      </button>
    </ng-template>
  </tds-data-table-column>
</tds-data-table>
```

```typescript
import { Component, ViewContainerRef, inject } from '@angular/core';
import { TDSDrawerService } from 'tds-ui/drawer';
import { TDSMessageService } from 'tds-ui/message';

@Component({
  selector: 'app-list-page',
  templateUrl: './list-page.component.html'
})
export class ListPageComponent {
  data: any[] = [];
  loading = false;
  total = 0;
  pageIndex = 1;
  pageSize = 10;

  constructor(
    private drawerService: TDSDrawerService,
    private msg: TDSMessageService,
    private viewContainerRef: ViewContainerRef
  ) {}

  openAdd(): void {
    const drawerRef = this.drawerService.create({
      title: 'Thêm mới',
      content: FormDrawerComponent,
      width: 500,
      viewContainerRef: this.viewContainerRef
    });

    drawerRef.afterClose.subscribe(result => {
      if (result) {
        this.loadData();
        this.msg.success('Thêm thành công');
      }
    });
  }

  openEdit(item: any): void {
    const drawerRef = this.drawerService.create({
      title: 'Chỉnh sửa',
      content: FormDrawerComponent,
      width: 500,
      tdsData: { ...item },
      viewContainerRef: this.viewContainerRef
    });

    drawerRef.afterClose.subscribe(result => {
      if (result) {
        this.loadData();
        this.msg.success('Cập nhật thành công');
      }
    });
  }

  onDelete(item: any): void {
    // Sử dụng TDSModalService.confirm() cho xác nhận xóa
    // ...
  }
}
```

---

### Drawer form component

```typescript
import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { TDSDrawerRef, TDS_DRAWER_DATA } from 'tds-ui/drawer';

@Component({
  selector: 'app-form-drawer',
  standalone: true,
  imports: [ReactiveFormsModule, TDSFormFieldModule, TDSInputModule, TDSButtonModule],
  template: `
    <form [formGroup]="form" class="flex flex-col gap-4">
      <tds-form-field>
        <tds-label>Tên</tds-label>
        <input tdsInput formControlName="name" placeholder="Nhập tên" />
        @if (form.get('name')?.hasError('required')) {
          <tds-error>Tên là bắt buộc</tds-error>
        }
      </tds-form-field>

      <tds-form-field>
        <tds-label>Email</tds-label>
        <input tdsInput formControlName="email" placeholder="Nhập email" />
        @if (form.get('email')?.hasError('required')) {
          <tds-error>Email là bắt buộc</tds-error>
        }
      </tds-form-field>

      <div class="flex justify-end gap-2 mt-4">
        <button tds-button color="secondary" (click)="close()">Hủy</button>
        <button tds-button color="primary" (click)="submit()" [disabled]="form.invalid">
          {{ isEdit ? 'Cập nhật' : 'Thêm' }}
        </button>
      </div>
    </form>
  `
})
export class FormDrawerComponent {
  tdsData: any = inject(TDS_DRAWER_DATA);
  isEdit: boolean;

  constructor(private drawerRef: TDSDrawerRef<any>, private fb: FormBuilder) {
    this.isEdit = !!this.tdsData;
    this.form = this.fb.group({
      name: [this.tdsData?.name || '', Validators.required],
      email: [this.tdsData?.email || '', [Validators.required, Validators.email]],
    });
  }

  form: FormGroup;

  submit(): void {
    if (this.form.invalid) return;
    this.drawerRef.close(this.form.value);
  }

  close(): void {
    this.drawerRef.close(null);
  }
}
```

---

**Tips:**
- `TDSDrawerService.create()` thay `TDSModalService.create()` — API rất giống nhau
- `inject(TDS_DRAWER_DATA)` — nhận data truyền từ list page qua `tdsData`
- `inject(TDSDrawerRef)` hoặc inject constructor — đóng drawer bằng `close(value)` hoặc `close(null)`
- `width` — chiều rộng drawer (px hoặc string), ưu tiên cao hơn `size`
- `size`: `"sm"` | `"md"` | `"lg"` | `"xl"` — kích thước mặc định
- `placement`: `"left"` | `"right"` (mặc định) | `"top"` | `"bottom"` — vị trí drawer
- `footer` — dùng `string` hoặc `TemplateRef` cho footer tùy chỉnh
- `viewContainerRef` — bắt buộc trong `create()` khi dùng component content
