# tds-ui Import Guide

How to import and use tds-ui components in your Angular application.

## Standard Import Pattern

Import the **Module** into your standalone component's `imports: []`:

```typescript
import { TDSButtonModule } from 'tds-ui/button';

@Component({
  standalone: true,
  imports: [TDSButtonModule],
  template: `
    <button tds-button color="primary">Click</button>
  `
})
export class MyComponent {}
```

**Quan trọng:** Import **Module** (e.g., `TDSButtonModule`), không phải Component (`TDSButtonComponent`).

## Import Paths

### Standard paths

Hầu hết components dùng pattern `tds-ui/{directory-name}`:

| Component | Import Path | Module |
|-----------|-------------|--------|
| Button | `tds-ui/button` | `TDSButtonModule` |
| Modal | `tds-ui/modal` | `TDSModalModule` |
| Select | `tds-ui/select` | `TDSSelectModule` |
| Table | `tds-ui/table` | `TDSTableModule` |
| Date Picker | `tds-ui/date-picker` | `TDSDatePickerModule` |
| Form Field | `tds-ui/form-field` | `TDSFormFieldModule` |
| Tabs | `tds-ui/tabs` | `TDSTabsModule` |
| Tooltip | `tds-ui/tooltip` | `TDSToolTipModule` |
| Tag | `tds-ui/tag` | `TDSTagModule` |
| Pagination | `tds-ui/pagination` | `TDSPaginationModule` |

### Special import paths

Một số components có import path đặc biệt — **không** theo pattern chuẩn:

| Component | Import Path | Module | Note |
|-----------|-------------|--------|------|
| Input (tdsInput directive) | `tds-ui/tds-input` | `TDSInputModule` | Dùng trong `tds-form-field`, selector `input[tdsInput]` |
| Checkbox | `tds-ui/tds-checkbox` | `TDSCheckBoxModule` | Không phải `tds-ui/checkbox` |
| Badge | `tds-ui/badges` | `TDSBadgeModule` | Số nhiều: badges |
| Button Split | `tds-ui/buttton-split` | `TDSButtonSpitModule` | 3 chữ t |
| Data List | `tds-ui/data-list` | `TDSDataListPanelModule` | Module name khác directory name |
| Progress Spinner | `tds-ui/progress-spinner` | `TDSSpinnerModule` | Module name khác directory name |
| Skeleton | `tds-ui/skeleton` | `TDSSkeletonModule` | |

## Service Imports

### providedIn: 'root' — Inject trực tiếp

Services có `providedIn: 'root'` inject trực tiếp, không cần import module cho service:

```typescript
import { TDSMessageService } from 'tds-ui/message';

@Component({
  standalone: true,
  imports: [], // Không cần TDSMessageModule cho service
})
export class MyComponent {
  constructor(private msg: TDSMessageService) {}

  showMessage() {
    this.msg.success('Thành công!');
  }
}
```

Services `providedIn: 'root'`:
- `TDSMessageService` — từ `tds-ui/message`
- `TDSNotificationService` — từ `tds-ui/notification`

### Provide qua Module — Cần import module

Services được provide qua NgModule cần import module trước:

```typescript
import { TDSModalModule, TDSModalService } from 'tds-ui/modal';

@Component({
  standalone: true,
  imports: [TDSModalModule],
})
export class MyComponent {
  constructor(private modal: TDSModalService) {}

  showConfirm() {
    this.modal.confirm({
      tdsTitle: 'Xác nhận',
      tdsContent: 'Bạn có chắc chắn?'
    });
  }
}
```

Services cần module:
- `TDSModalService` — cần `TDSModalModule`
- `TDSDrawerService` — cần `TDSDrawerModule`

## Common Mistakes

### Sai: Import component trực tiếp
```typescript
// ❌ Sai
import { TDSButtonComponent } from 'tds-ui/button';
imports: [TDSButtonComponent]
```

### Đúng: Import module
```typescript
// ✅ Đúng
import { TDSButtonModule } from 'tds-ui/button';
imports: [TDSButtonModule]
```

### Sai: Import path sai cho tdsInput
```typescript
// ❌ Sai
import { TDSInputModule } from 'tds-ui/input';
```

### Đúng: Import path đặc biệt
```typescript
// ✅ Đúng — dùng trong tds-form-field
import { TDSInputModule } from 'tds-ui/tds-input';
```
