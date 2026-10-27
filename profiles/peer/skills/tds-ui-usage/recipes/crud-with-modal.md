# CRUD với Modal

## Use case
Tạo CRUD form trong modal, sử dụng `TDSModalService.create()` để mở custom component dynamically. Tạo 2 files: list page + modal form component riêng biệt.

## File Structure
```
src/app/design-preview/pages/{page-name}/
├── {page-name}.component.ts                 (list page — dùng TDSModalService)
└── {page-name}-form-modal.component.ts      (modal form — dùng TDSModalRef)
```

## Components cần import

**List page:**
```typescript
import { TDSModalModule, TDSModalService } from 'tds-ui/modal';
import { TDSButtonModule } from 'tds-ui/button';
import { TDSDataTableModule } from 'tds-ui/data-table';
import { TDSMessageService } from 'tds-ui/message';
import { ViewContainerRef } from '@angular/core';
```

**Modal form component:**
```typescript
import { TDSModalRef, TDS_MODAL_DATA } from 'tds-ui/modal';
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSInputModule } from 'tds-ui/tds-input';
import { TDSButtonModule } from 'tds-ui/button';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';
```

## Code example

### 1. List page — mở modal cho Add/Edit

```typescript
import { Component, OnInit, ViewContainerRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl } from '@angular/forms';

import { TDSDataTableModule } from 'tds-ui/data-table';
import { TDSPaginationModule } from 'tds-ui/pagination';
import { TDSButtonModule } from 'tds-ui/button';
import { TDSInputModule } from 'tds-ui/tds-input';
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSTagModule } from 'tds-ui/tag';
import { TDSDropdownModule } from 'tds-ui/dropdown';
import { TDSModalModule, TDSModalService } from 'tds-ui/modal';
import { TDSMessageService } from 'tds-ui/message';
import { TDSPageHeaderModule } from 'tds-ui/page-header';

import { UserFormModalComponent } from './user-form-modal.component';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [
    CommonModule,
    TDSDataTableModule,
    TDSPaginationModule,
    TDSButtonModule,
    TDSInputModule,
    TDSFormFieldModule,
    TDSTagModule,
    TDSDropdownModule,
    TDSModalModule,
    TDSPageHeaderModule,
  ],
  template: `
    <div class="p-4 h-full flex flex-col">
      <tds-page-header tdsTitle="User Management">
        <button tds-button color="primary" (click)="onAdd()">
          Add New
        </button>
      </tds-page-header>

      <!-- Data Table -->
      <tds-data-table
        [dataList]="dataSource"
        [columns]="columns">

        <ng-template tdsDataTableCell let-row let-column="column">
          @switch (column.key) {
            @case ('status') {
              <tds-tag [color]="row.status === 'active' ? 'success' : 'default'">
                {{ row.status }}
              </tds-tag>
            }
            @case ('actions') {
              <tds-dropdown>
                <button tds-button-text tds-dropdown-trigger>
                  Actions <span tds-icon tds-icon-name="down"></span>
                </button>
                <ul tds-dropdown-menu>
                  <li tds-dropdown-item (click)="onEdit(row)">
                    <span tds-icon tds-icon-name="edit"></span> Edit
                  </li>
                  <li tds-dropdown-item (click)="onDelete(row)">
                    <span tds-icon tds-icon-name="delete"></span> Delete
                  </li>
                </ul>
              </tds-dropdown>
            }
            @default {
              {{ row[column.key] }}
            }
          }
        </ng-template>
      </tds-data-table>
    </div>
  `,
})
export class UserListComponent implements OnInit {
  dataSource: any[] = [];
  columns: any[] = [];

  constructor(
    private modal: TDSModalService,
    private viewContainerRef: ViewContainerRef,
    private message: TDSMessageService
  ) {}

  ngOnInit() {
    this.columns = [
      { key: 'name', title: 'Name' },
      { key: 'email', title: 'Email' },
      { key: 'role', title: 'Role' },
      { key: 'status', title: 'Status' },
      { key: 'actions', title: 'Actions', width: '120px' },
    ];
    this.loadData();
  }

  loadData() {
    this.dataSource = mockUsers;
  }

  onAdd() {
    const ref = this.modal.create({
      content: UserFormModalComponent,
      title: 'Add New User',
      size: 'md',
      footer: null,
      viewContainerRef: this.viewContainerRef,
      tdsData: null,
    });
    ref.afterClose.subscribe(result => {
      if (result) {
        this.message.success('User created successfully');
        this.loadData();
      }
    });
  }

  onEdit(row: any) {
    const ref = this.modal.create({
      content: UserFormModalComponent,
      title: 'Edit User',
      size: 'md',
      footer: null,
      viewContainerRef: this.viewContainerRef,
      tdsData: row,
    });
    ref.afterClose.subscribe(result => {
      if (result) {
        this.message.success('User updated successfully');
        this.loadData();
      }
    });
  }

  onDelete(row: any) {
    this.modal.confirm({
      tdsTitle: 'Xác nhận xóa',
      tdsContent: `Bạn có chắc chắn muốn xóa "${row.name}"?`,
      tdsOkDanger: true,
      tdsOnOk: () => {
        this.message.success('User deleted successfully');
        this.loadData();
      },
    });
  }
}

const mockUsers = [
  { id: 1, name: 'Nguyễn Văn An', email: 'an@example.com', role: 'Admin', status: 'active' },
  { id: 2, name: 'Trần Thị Bình', email: 'binh@example.com', role: 'User', status: 'active' },
  { id: 3, name: 'Lê Minh Châu', email: 'chau@example.com', role: 'User', status: 'inactive' },
];
```

### 2. Modal form component — file riêng biệt

```typescript
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { TDSModalRef, TDS_MODAL_DATA } from 'tds-ui/modal';
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSInputModule } from 'tds-ui/tds-input';
import { TDSSelectModule } from 'tds-ui/select';
import { TDSButtonModule } from 'tds-ui/button';

@Component({
  selector: 'app-user-form-modal',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    TDSFormFieldModule,
    TDSInputModule,
    TDSSelectModule,
    TDSButtonModule,
  ],
  template: `
    <form [formGroup]="form">
      <tds-form-field>
        <label tds-label required>Name</label>
        <input tdsInput formControlName="name" placeholder="Enter name" />
      </tds-form-field>

      <tds-form-field class="mt-3">
        <label tds-label required>Email</label>
        <input tdsInput formControlName="email" tds-type="email" placeholder="user@example.com" />
      </tds-form-field>

      <tds-form-field class="mt-3">
        <label tds-label>Role</label>
        <tds-select formControlName="role" placeholder="Select role">
          <tds-option value="admin">Administrator</tds-option>
          <tds-option value="manager">Manager</tds-option>
          <tds-option value="user">User</tds-option>
        </tds-select>
      </tds-form-field>
    </form>

    <div *tdsModalFooter class="flex justify-end gap-2">
      <button tds-button (click)="cancel()">Huỷ</button>
      <button tds-button color="primary" [disabled]="form.invalid" (click)="save()">
        {{ data ? 'Cập nhật' : 'Thêm mới' }}
      </button>
    </div>
  `,
})
export class UserFormModalComponent {
  private modalRef = inject(TDSModalRef);
  data = inject(TDS_MODAL_DATA) as any;

  form = new FormGroup({
    name: new FormControl(this.data?.name || '', [Validators.required]),
    email: new FormControl(this.data?.email || '', [Validators.required, Validators.email]),
    role: new FormControl(this.data?.role || 'user'),
  });

  cancel() {
    this.modalRef.destroy(null);
  }

  save() {
    if (this.form.valid) {
      this.modalRef.destroy(this.form.value);
    }
  }
}
```

### 3. Confirm dialog (delete)

```typescript
this.modal.confirm({
  tdsTitle: 'Xác nhận xóa',
  tdsContent: `Bạn có chắc chắn muốn xóa "${item.name}"?`,
  tdsOkDanger: true,
  tdsOnOk: () => {
    // Call API xóa
    this.loadData();
  },
});
```

## Key patterns

- **`footer: null`** trong `TDSModalService.create()` — ẩn default OK/Cancel footer, để content component tự xây footer qua `*tdsModalFooter`
- **`inject(TDS_MODAL_DATA)`** — nhận data truyền vào modal (null = tạo mới, object = chỉnh sửa)
- **`inject(TDSModalRef)`** — đóng modal và trả kết quả: `destroy(value)` hoặc `destroy(null)`
- **`viewContainerRef`** — bắt buộc truyền vào `create()` để modal resolve đúng dependency injection
- **`tdsData`** trong config — truyền data vào modal component (nhận qua `TDS_MODAL_DATA`)

## Tips
- `TDSModalService` cần import `TDSModalModule` vào list page component
- `confirm()` dùng cho delete — không cần tạo component riêng
- `create()` dùng cho add/edit — cần tạo modal form component riêng biệt
- Xem thêm: `reference/docs/modal.md`
