# i18n Migration — Chi tiết workflow đầy đủ

## 1. Điều kiện tiên quyết

### 1.1 Spec file
Phải có `docs/spec_*.md` chứa:
- `app_path` — thư mục remote app (ví dụ: `apps/customer`)
- `lib_path` — thư mục shared UI lib (ví dụ: `libs/customer/ui`)
- `port` — port dev server (ví dụ: `4203`)
- `feature_key` — Root Key viết hoa (`CUSTOMER`)
- `routing_map` — danh sách route cha, con, redirect
- `component_inventory` — Page components, Filter Drawers, Sub-components, Modal động

### 1.2 Dependencies
- `@wi-mfes/i18n` — cung cấp `TranslatePipe`, `TranslateService`, loader, `mergeDeep()`
- `@wion-pos/shared/util` — cung cấp `provideWII18n` (nếu module có lib UI)
- `@wi-mfes/config` — cung cấp môi trường build

### 1.3 Cross-module dependencies
Rà soát modal/drawer được gọi từ module khác (ví dụ: `customer` mở modal từ `tags`). Khi đó translation key cần nằm trong namespace của module chứa component, không phải module gọi.

---

## 2. Giai đoạn 1 — Scope Discovery

1. Đọc `docs/spec_*.md` tương ứng.
2. Mở `apps/<module>/src/app/remote-entry/entry.routes.ts` — liệt kê tất cả component trang và child routes.
3. Quét `apps/<module>/src/app/components` và `libs/<module>/ui/src/`, phân loại:
   - **Main Pages** — Page Header, Tabs, Action buttons, Tables, Filters
   - **Modals động** — gọi qua `TDSModalService.create({...})`
   - **Drawers** — gọi qua `TDSDrawerService.create({...})` hoặc component drawer
   - **Toast/Notifications** — `TDSNotificationService`, `TDSMessageService`

---

## 3. Giai đoạn 2 — Dictionary Namespacing

### Vị trí file JSON
```
apps/<module>/src/assets/i18n/vi/<module>.json
apps/<module>/src/assets/i18n/en/<module>.json
libs/<module>/ui/public/i18n/vi/<module>.json   ← nếu có lib UI
libs/<module>/ui/public/i18n/en/<module>.json   ← nếu có lib UI
```

### Cấu trúc JSON chuẩn
```json
{
  "FEATURE_KEY": {
    "PAGE_TITLE": "Danh sách khách hàng",
    "TABLE": {
      "COLUMNS": { "NAME": "Tên", "CODE": "Mã" },
      "TOOLTIPS": { "EDIT": "Chỉnh sửa", "DELETE": "Xóa" }
    },
    "ACTIONS": { "CREATE": "Tạo mới", "SAVE": "Lưu", "CANCEL": "Hủy" },
    "FILTER": { "PLACEHOLDER_SEARCH": "Tìm kiếm..." },
    "MODALS": {
      "TITLE_CREATE": "Tạo khách hàng",
      "TITLE_EDIT": "Chỉnh sửa khách hàng"
    },
    "MESSAGES": {
      "SAVE_SUCCESS": "Lưu thành công",
      "DELETE_CONFIRM": "Xác nhận xóa {{name}}?"
    },
    "VALIDATION": { "REQUIRED": "Trường này bắt buộc" }
  }
}
```

### Kiểm tra root key bằng node
```bash
node -e "
const vi = require('./apps/<module>/src/assets/i18n/vi/<module>.json');
const en = require('./apps/<module>/src/assets/i18n/en/<module>.json');
const viKeys = Object.keys(vi);
const enKeys = Object.keys(en);
console.log('VI root keys:', viKeys);
console.log('EN root keys:', enKeys);
if (viKeys.length !== 1 || enKeys.length !== 1) {
  console.error('LỖI: Phải có đúng 1 root key!');
  process.exit(1);
}
if (viKeys[0] !== enKeys[0]) {
  console.error('LỖI: Root key VI và EN không khớp!');
  process.exit(1);
}
console.log('OK: Root key hợp lệ:', viKeys[0]);
"
```

---

## 4. Giai đoạn 3 — Refactor Code

### 4.1 Template HTML

**Text thông thường:**
```html
<span>{{ 'FEATURE_KEY.PAGE_TITLE' | translate }}</span>
```

**Attribute:**
```html
<tds-input [placeholder]="'FEATURE_KEY.FILTER.PLACEHOLDER_SEARCH' | translate"></tds-input>
```

**Tooltip:**
```html
<button [tds-tooltip]="'FEATURE_KEY.TABLE.TOOLTIPS.EDIT' | translate">...</button>
```

**Biến nội suy:**
```html
<p>{{ 'FEATURE_KEY.MESSAGES.DELETE_CONFIRM' | translate:{ name: currentItem.name } }}</p>
```

### 4.2 TypeScript — Standalone Component

```typescript
import { TranslatePipe } from '@wi-mfes/i18n';

@Component({
  standalone: true,
  selector: 'wion-pos-feature-list',
  imports: [CommonModule, TranslatePipe /* ... TDS Modules */],
})
export class FeatureListComponent {}
```

### 4.3 TypeScript — Dynamic text & Toast

```typescript
import { inject } from '@angular/core';
import { TranslateService } from '@wi-mfes/i18n';

export class FeatureListComponent {
  private readonly translate = inject(TranslateService);

  showSuccess() {
    const msg = this.translate.instant('FEATURE_KEY.MESSAGES.SAVE_SUCCESS');
    this.notificationService.success('Thông báo', msg);
  }
}
```

### 4.4 Dynamic Modals (`TDSModalService.create`)

```typescript
openModal(item?: ItemType) {
  this.modalService.create({
    title: this.translate.instant(
      item ? 'FEATURE_KEY.MODALS.TITLE_EDIT' : 'FEATURE_KEY.MODALS.TITLE_CREATE'
    ),
    okText: this.translate.instant('FEATURE_KEY.ACTIONS.SAVE'),
    cancelText: this.translate.instant('FEATURE_KEY.ACTIONS.CANCEL'),
    content: FeatureFormComponent,
    viewContainerRef: this.viewContainerRef, // BẮT BUỘC — kế thừa DI context
    componentParams: { data: item },
  });
}
```

> **BẮT BUỘC**: luôn truyền `viewContainerRef` để modal kế thừa DI context từ caller.

### 4.5 Provider trong `app.config.ts` hoặc `remote-entry/entry.component.ts`

```typescript
import { provideWII18n } from '@wion-pos/shared/util';

export const appConfig: ApplicationConfig = {
  providers: [
    provideWII18n({ module: '<module>' }), // nếu có lib UI riêng
    // ...
  ],
};
```

---

## 5. Giai đoạn 4 — Audit & QA

### Bước 1 — Terminal checks
```bash
# Grep key thô còn sót (không qua pipe translate)
rg --type html '"[A-Z_]+\.[A-Z_.]+"' apps/<module>/src --no-filename | grep -v "| translate" | grep -v "translate.instant"

# Kiểm tra root key JSON
node -e "<script kiểm tra root key ở trên>"

# Build Rsbuild
npx nx build <module> --configuration=development
```

### Bước 2 — Network check
Mở browser → DevTools → Network tab → reload trang.
Xác nhận `/assets/i18n/vi/<module>.json` và `/assets/i18n/en/<module>.json` trả về HTTP `200`.

### Bước 3 — Console check
DevTools → Console.
Không được có: `Missing translation for key` hoặc `Missing translation key`.

### Bước 4 — DOM raw-key scan
```javascript
// Chạy trong DevTools Console hoặc evaluate_script
(() => {
  const rawKeyPattern = /^[A-Z][A-Z0-9_]*(\.[A-Z][A-Z0-9_]*)+$/;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node, count = 0, found = [];
  while ((node = walker.nextNode())) {
    const text = node.textContent.trim();
    if (rawKeyPattern.test(text)) {
      count++;
      found.push(text);
    }
  }
  return { count, found };
})();
```
Yêu cầu: `count === 0`.

### Bước 5 — Language switch VI ↔ EN
1. Bấm toggle đổi sang `EN`.
2. Xác nhận `/assets/i18n/en/<module>.json` được tải với HTTP `200`.
3. Kiểm tra UI hiển thị tiếng Anh đúng.
4. Bấm lại `VI` — xác nhận phản hồi tức thì, ổn định.

### Bước 6 — Screenshot nghiệm thu
Chụp màn hình trang danh sách đã dịch đầy đủ ở cả VI và EN.

---

## 6. Re-test Loop (khi phát hiện lỗi)

```
Sửa code → Rsbuild HMR / hard reload → Scan DOM → Kiểm tra console → Đạt count === 0
```

---

## 7. Checklist nghiệm thu

- [ ] Đã đọc spec: routes, components, modals, drawers
- [ ] JSON `vi` và `en` có đúng 1 root key, đối xứng hoàn toàn
- [ ] Đã sync JSON sang `libs/<module>/ui/public/i18n/` (nếu có lib UI)
- [ ] Tất cả template HTML dùng `| translate` pipe
- [ ] Tất cả dynamic text dùng `translate.instant()`
- [ ] Tất cả `TDSModalService.create` truyền `viewContainerRef`
- [ ] Build thành công (không lỗi TypeScript/Rsbuild)
- [ ] Network: JSON files trả về HTTP `200`
- [ ] Console: không có `Missing translation key`
- [ ] DOM scan: `count === 0`
- [ ] Language switch VI ↔ EN hoạt động mượt
- [ ] Screenshot nghiệm thu đã chụp
