## Data Table Nâng Cao

**Use case:** Data table với expandable row, checkbox selection, custom column template, cột thao tác, dynamic columns và column settings.

**Components cần import:**
```typescript
import { TDSDataTableModule } from 'tds-ui/data-table';
import { TDSColumnSettingsDTO } from 'tds-ui/column-settings';
import { TDSTableQueryParams } from 'tds-ui/table';
```

---

### 1. Data Table với Expandable Row + Checkbox + Custom Template

```html
<div class="w-full h-[500px]">
  <tds-data-table
    [tdsData]="data"
    [tdsPageSize]="10"
    [tdsSelectable]="{ multiple: true }">

    <!-- Expand row -->
    <tds-data-table-expand-row [tdsContent]="expandTpl">
      <ng-template #expandTpl let-dataRow let-expand="expand">
        <div class="w-full p-4">
          <p><strong>Chi tiết:</strong> {{ dataRow.address }}</p>
          <p><strong>Ghi chú:</strong> {{ dataRow.note }}</p>
        </div>
      </ng-template>
    </tds-data-table-expand-row>

    <!-- Checkbox column -->
    <tds-data-table-checkbox-column></tds-data-table-checkbox-column>

    <!-- Cột thường -->
    <tds-data-table-column tdsField="id" tdsTitle="ID" tdsWidth="60px"
      [tdsDataType]="'numeric'" [tdsLeft]="true">
    </tds-data-table-column>

    <!-- Cột với custom template (avatar + text) -->
    <tds-data-table-column tdsField="name" tdsTitle="Tên" tdsWidth="200px"
      [tdsContent]="nameTpl" [tdsLeft]="true">
      <ng-template #nameTpl let-dataRow>
        <div class="flex items-center">
          <tds-avatar size="sm" [tdsSrc]="dataRow.avatar"></tds-avatar>
          <div class="text-caption-2 ml-2">{{ dataRow.name }}</div>
        </div>
      </ng-template>
    </tds-data-table-column>

    <!-- Cột số có format thousand separator -->
    <tds-data-table-column tdsField="amount" tdsTitle="Số tiền" tdsWidth="200px"
      [tdsDataType]="'numeric'" [tdsFormat]="{ thousandSeparator: ',' }">
    </tds-data-table-column>

    <!-- Cột ngày -->
    <tds-data-table-column tdsField="createDate" tdsTitle="Ngày tạo" tdsWidth="150px"
      [tdsDataType]="'date'" [tdsFormat]="'dd/MM/yyyy'" [tdsRight]="true">
    </tds-data-table-column>

    <!-- Cột thao tác -->
    <tds-data-table-column tdsTitle="Thao tác" tdsWidth="110px"
      [tdsColumnType]="'command'" [tdsRight]="true">
      <ng-template #commandTpl let-dataRow>
        <button tds-button-flat-icon class="mr-2" color="primary">
          <i class="tdsi-edit-fill"></i>
        </button>
        <button tds-button-flat-icon color="secondary">
          <i class="tdsi-trash-fill"></i>
        </button>
      </ng-template>
    </tds-data-table-column>
  </tds-data-table>
</div>
```

```typescript
import { Component, OnInit } from '@angular/core';

interface ItemData {
  id: number;
  name: string;
  amount: number;
  address: string;
  note: string;
  createDate: Date;
  avatar: string;
}

@Component({
  selector: 'app-table-advanced',
  templateUrl: './table-advanced.component.html'
})
export class TableAdvancedComponent implements OnInit {
  data: ItemData[] = [];

  ngOnInit(): void {
    const items = [];
    for (let i = 0; i < 50; i++) {
      items.push({
        id: i,
        name: `Item ${i}`,
        amount: Math.floor(Math.random() * 200000000),
        address: `Địa chỉ ${i}`,
        note: `Ghi chú cho item ${i}`,
        createDate: new Date(),
        avatar: `https://randomuser.me/api/portraits/women/${i % 100}.jpg`,
      });
    }
    this.data = items;
  }
}
```

---

### 2. Data Table với Dynamic Columns + Column Settings

```html
<div class="w-full h-[500px] flex flex-col p-2">
  <!-- Nút column settings -->
  <div class="w-full flex justify-end pb-2">
    <tds-column-settings [tdsData]="columns" [tdsSortable]="true"
      (tdsDataChange)="onColumnsChange($event)">
    </tds-column-settings>
  </div>

  <!-- Data table -->
  <div class="flex-auto">
    <tds-data-table [tdsData]="data" [tdsFrontPagination]="false"
      [tdsShowSizeChanger]="true" [tdsLoading]="loading" [tdsTotal]="total"
      [(tdsPageSize)]="pageSize" [(tdsPageIndex)]="pageIndex"
      [tdsPageSizeOptions]="[10, 20, 50]"
      (tdsQueryParams)="onQueryParams($event)">

      @for (col of columns; track col.tdsField) {
        @switch (col.tdsField) {
          <!-- Avatar column -->
          @case ('avatar') {
            <tds-data-table-column [tdsField]="col.tdsField" [tdsTitle]="col.tdsTitle"
              [tdsContent]="avatarTpl" [tdsWidth]="col.tdsWidth" [tdsHidden]="!col.tdsChecked">
              <ng-template #avatarTpl let-dataRow>
                <tds-avatar size="sm" [tdsSrc]="dataRow.avatar"></tds-avatar>
              </ng-template>
            </tds-data-table-column>
          }
          <!-- Default columns -->
          @default {
            <tds-data-table-column [tdsField]="col.tdsField" [tdsTitle]="col.tdsTitle"
              [tdsWidth]="col.tdsWidth" [tdsHidden]="!col.tdsChecked"
              [tdsLeft]="col.tdsLeft ?? false" [tdsRight]="col.tdsRight ?? false"
              [tdsDataType]="col['tdsDataType']">
            </tds-data-table-column>
          }
        }
      }
    </tds-data-table>
  </div>
</div>
```

```typescript
import { Component, OnInit } from '@angular/core';
import { TDSColumnSettingsDTO } from 'tds-ui/column-settings';
import { TDSTableQueryParams } from 'tds-ui/table';

@Component({
  selector: 'app-table-dynamic',
  templateUrl: './table-dynamic.component.html'
})
export class TableDynamicComponent implements OnInit {
  columns: TDSColumnSettingsDTO[] = [];
  data: any[] = [];
  loading = false;
  total = 0;
  pageIndex = 1;
  pageSize = 10;

  ngOnInit(): void {
    this.columns = this.buildColumns();
  }

  buildColumns(): TDSColumnSettingsDTO[] {
    return [
      { tdsField: 'name', tdsTitle: 'Tên', tdsChecked: true, tdsWidth: '200px', tdsDataType: 'text', tdsLeft: true },
      { tdsField: 'avatar', tdsTitle: 'Ảnh', tdsChecked: true, tdsWidth: '80px', tdsDataType: 'text' },
      { tdsField: 'email', tdsTitle: 'Email', tdsChecked: true, tdsWidth: '250px', tdsDataType: 'text' },
      { tdsField: 'amount', tdsTitle: 'Số tiền', tdsChecked: true, tdsWidth: '150px', tdsDataType: 'numeric' },
      { tdsField: 'phone', tdsTitle: 'Điện thoại', tdsChecked: true, tdsWidth: '150px', tdsDataType: 'text', tdsRight: true, tdsDisabled: true },
    ];
  }

  onColumnsChange(columns: TDSColumnSettingsDTO[]): void {
    this.columns = [...columns];
  }

  onQueryParams(params: TDSTableQueryParams): void {
    const { pageIndex, pageSize } = params;
    this.loadData(pageIndex, pageSize);
  }

  loadData(pageIndex: number, pageSize: number): void {
    this.loading = true;
    // Call API...
    this.loading = false;
  }
}
```

---

**Tips:**
- `tds-data-table-expand-row` — thêm dòng mở rộng, dùng `tdsContent` cho template
- `tdsExpandChange` — event khi expand/collapse, `tdsExpandedKeysChange` — danh sách key đang expand
- `tds-data-table-checkbox-column` — thêm cột checkbox
- `[tdsSelectable]="{ multiple: true }"` — cho phép chọn nhiều dòng
- `tdsSelectedRowChange` — event khi chọn dòng, `tdsSelectedKeys` — danh sách key đã chọn
- `[tdsFormat]` — format dữ liệu: `"'dd/MM/yyyy'"` cho date, `"{ thousandSeparator: ',' }"` cho số
- `[tdsColumnType]="'command'"` — cột cố định không scroll
- `[tdsLeft]="true"` / `[tdsRight]="true"` — cố định cột trái/phải khi scroll ngang
- `TDSColumnSettingsDTO` — dùng cho column settings, có `tdsChecked`, `tdsDisabled`, `tdsWidth`
