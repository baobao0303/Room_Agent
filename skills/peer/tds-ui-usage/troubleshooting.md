# tds-ui Troubleshooting

Common issues and solutions when using tds-ui components.

## Install Issues

### Cannot find module 'tds-ui/...'

**Vấn đề:** `Module not found: Can't resolve 'tds-ui/button'` sau khi npm install.

**Nguyên nhân:** Package chưa install hoặc install fail.

**Giải pháp:** Xem `reference/install-guide.md` Section 2. Check:

```powershell
ls node_modules/tds-ui
npm ls tds-ui
```

### Component render "trần" không có style

**Vấn đề:** Component hiển thị nhưng không có CSS (button tròn, không màu, không padding).

**Nguyên nhân:** Tailwind chưa load hoặc `styles.scss` thiếu tds imports.

**Giải pháp:** Xem `reference/install-guide.md` Section 3 + 4. Verify:

- `tailwind.config.js` require `./node_modules/tds-ui/tailwindcss/v2/tailwind.config.js`
- `styles.scss` có `@import "../node_modules/tds-ui/assets/v2/scss/components/tds.component.scss"`
- `styles.scss` có `@import "../node_modules/tds-ui/assets/v2/scss/theme/theme.all.scss"` (hoặc theme đơn)

### @angular/cdk version mismatch

**Vấn đề:** Console lỗi `NG0200: Circular dependency` hoặc overlay vỡ layout.

**Nguyên nhân:** `@angular/cdk` major khác `@angular/core`.

**Giải pháp:**

```powershell
npm ls @angular/cdk
npm install @angular/cdk@^18.2.1
```

CDK phải cùng major version với Angular core (18.x).

### Icon không hiển thị (tdsi-*)

**Vấn đề:** Icon renders là ô vuông hoặc ký tự lạ.

**Nguyên nhân:** Thiếu font-icon CDN trong `index.html`.

**Giải pháp:** Xem `reference/install-guide.md` Section 5. Add 2 CDN link vào `<head>`:

```html
<link rel="stylesheet" href="https://static-tds-public-projects.tds.local/assets/font-icon/style.css">
```

### Pipe date/i18n báo lỗi

**Vấn đề:** `Missing locale data for 'vi-VN'"` hoặc tds-ui text hiển thị tiếng Anh.

**Nguyên nhân:** Chưa `registerLocaleData(localeVi)` hoặc thiếu `TDS_I18N` provider.

**Giải pháp:** Xem `reference/install-guide.md` Section 6. Add `registerLocaleData(localeVi)` và `{ provide: TDS_I18N, useValue: vi_VN }` vào app config.

## Import Issues

### Import path not found

**Vấn đề:** `Module not found: Can't resolve 'tds-ui/checkbox'`

**Nguyên nhân:** Một số components có import path đặc biệt.

**Giải pháp:** Kiểm tra `reference/import-guide.md` section "Special import paths".

Các path hay sai:
- `tds-ui/checkbox` → đúng là `tds-ui/tds-checkbox`
- `tds-ui/input` (cho TDSInputModule) → đúng là `tds-ui/tds-input`
- `tds-ui/badge` → đúng là `tds-ui/badges` (số nhiều)

### Imported but not working

**Vấn đề:** Component không hiển thị hoặc không có style.

**Kiểm tra:**
1. Import **Module** (e.g., `TDSButtonModule`), không phải Component (`TDSButtonComponent`)
2. Module đã thêm vào `imports: []` chưa
3. Selector đúng chưa — check `reference/components-index.md`

## Modal Issues

### Modal không đóng được

**Kiểm tra:**
1. `visible` binding: `[visible]="isVisible"` và `(visibleChange)="isVisible = $event"`
2. Nếu dùng `TDSModalService.confirm()` — modal tự đóng khi nhấn OK/Cancel
3. Nếu dùng `TDSModalService.create()` — gọi `this.modal.closeAll()` hoặc dùng `TDSModalRef.close()`

### TDSModalService không inject được

**Nguyên nhân:** Chưa import `TDSModalModule`.

**Giải pháp:** `TDSModalService` được provide qua `TDSModalModule`, không phải `providedIn: 'root'`.

```typescript
import { TDSModalModule, TDSModalService } from 'tds-ui/modal';

@Component({
  standalone: true,
  imports: [TDSModalModule], // ← Bắt buộc
})
```

## Select Issues

### Select không hiển thị options

**Kiểm tra:**
1. `data` đã binding đúng chưa — cần array of objects
2. `textField` và `valueField` đúng field name chưa
3. Nếu dùng content projection — kiểm tra `tds-option` selector đúng chưa

### Select search không hoạt động

**Kiểm tra:**
1. `showSearch` đã set thành `true` chưa (mặc định `true` cho một số trường hợp)
2. Nếu dùng server-side search: `serverSearch` = `true` và lắng nghe `(onSearch)` output

## Form Issues

### tdsInput không nhận reactive form control

**Kiểm tra:**
1. Đã thêm `tdsInput` directive vào input chưa: `<input tdsInput formControlName="name">`
2. Import `TDSInputModule` từ `tds-ui/tds-input` (không phải `tds-ui/input`)
3. ReactiveFormsModule đã import chưa

## Style Issues

### Component không có style

**Nguyên nhân:** Tailwind CSS chưa được load.

**Giải pháp:** Đảm bảo Tailwind CSS được import trong `styles.scss` hoặc `angular.json`.

### Style bị ghi đè

**Nguyên nhân:** `ViewEncapsulation.None` — styles component ảnh hưởng global.

**Giải pháp:** Dùng CSS specificity cao hơn hoặc scope styles trong parent container.

## Layout

### Sider không auto-collapse ở breakpoint kỳ vọng

`tdsBreakpoint` của `tds-layout-sider` dùng `siderResponsiveMap`, **không** phải `gridResponsiveMap`.

| `tdsBreakpoint` | Tự collapse khi viewport |
|-----------------|--------------------------|
| `xs` | ≤ 479.98px |
| `sm` | ≤ 575.98px |
| `md` | ≤ 767.98px |
| `lg` | ≤ 991.98px |
| `xl` | ≤ 1199.98px |
| `xxl` | ≤ 1599.98px |

Nếu kỳ vọng collapse ở giá trị khác (vd. `md ≥ 768`), đó là `gridResponsiveMap`. Layout không dùng map đó. Xem `reference/docs/layout.md` → Responsive Breakpoints.

### Trigger collapse không hiện

Trigger render khi `tdsCollapsible === true && tdsTrigger !== null`. Source default trigger template bị comment (`projects/tds-ui/layout/sider-trigger.component.ts` lines 30–35) → không có icon mặc định.

Fix: cung cấp `tdsTrigger` custom:

```html
<tds-layout-sider [tdsCollapsible]="true" [tdsTrigger]="myTrigger">
  <ng-template #myTrigger><span tds-icon tds-icon-name="menu"></span></ng-template>
</tds-layout-sider>
```

Khi `tdsCollapsedWidth === 0`, sider chuyển sang zero-width trigger — cần cung cấp `tdsZeroTrigger` riêng.

### `tds-layout-content` không scroll

Host class `tds-custom-scroll` đã có, nhưng scroll cần height chain từ root:

```css
html, body { height: 100%; margin: 0; }
/* hoặc */
:host { display: block; height: 100vh; }
```

`tds-layout-content` có `flex-auto min-h-0` — chỉ fill khi parent cấp height. Walk DOM từ `tds-layout-content` lên `html`, mỗi level phải cho height đi qua (`height: 100%` hoặc flex chain).

### Nested `tds-layout` không render

`tds-layout` **không lồng nhau được**. CSS `projects/tds-ui/assets/v2/scss/components/layout.component.scss`:

```scss
.tds-layout.tds-layout-has-sider > .tds-layout { @apply w-0; }
```

Direct child `tds-layout` bị `width: 0` → collapse.

Fix: dùng cấu trúc flat, content area là `tds-layout-content`:

```html
<tds-layout>
  <tds-layout-sider>...</tds-layout-sider>
  <tds-layout-header>...</tds-layout-header>
  <tds-layout-content>...</tds-layout-content>
</tds-layout>
```
