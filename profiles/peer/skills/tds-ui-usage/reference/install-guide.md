# tds-ui Install Guide

Cài đặt tds-ui vào Angular 18 project có sẵn.

## 1. Prerequisites

- Node.js >= 18.x
- Angular 18.2.x project đã tồn tại
- Tailwind CSS 3.4.x (nếu chưa có, cài trước khi tiếp tục)

## 2. Install package

tds-ui distrib qua private registry. Thêm vào `package.json`:

```json
{
  "dependencies": {
    "tds-ui": "https://design-system.local/lib/tds-ui-18.6.0.tgz"
  }
}
```

Chạy:

```powershell
npm install
```

Peer deps tự cài: `@angular/cdk`, `date-fns`, `imask`, `text-mask-core`, `@ng-web-apis/common`.

Tailwind plugins (bắt buộc):

```powershell
npm install -D tailwindcss@^3.4.10 postcss@^8.4.41 autoprefixer@^10.4.20 @tailwindcss/forms@^0.5.7 @tailwindcss/typography@^0.5.14
```

### Version peer deps (quan trọng)

| Package | Version yêu cầu |
|---------|----------------|
| `@angular/cdk` | `^18.2.1` (khớp Angular core major) |
| `@angular/common` | `^18.2.0` |
| `@angular/core` | `^18.2.0` |

Check trước khi install:

```powershell
npm ls @angular/cdk @angular/core
```

Nếu `@angular/cdk` lệch major (vd. 17.x hoặc 19.x), force đúng version:

```powershell
npm install @angular/cdk@^18.2.1
```

Lý do: tds-ui dùng CDK overlays, scrolling, drag-drop. Sai major version → runtime error `NG0200` hoặc component không render.

## 3. Tailwind config

### Path relativity cho require

Path trong `require()` **tương đối từ project root** (Tailwind CLI CWD = root), không phải từ vị trí file `tailwind.config.js`.

Verify file tồn tại sau install:

```powershell
ls node_modules/tds-ui/tailwindcss/v2/tailwind.config.js
```

### tailwind.config.js (consumer version)

Tạo/sửa `tailwind.config.js` ở project root:

```javascript
const TDS_UI_CONFIG = require("./node_modules/tds-ui/tailwindcss/v2/tailwind.config.js").TDS_UI_TAILWINDCSS_CONFIG;
//màu mặc định từ tds-ui
const TDS_UI_COLOR = require("./node_modules/tds-ui/tailwindcss/v2/tailwind.config.js").TDS_UI_TAILWINDCSS_COLORS;
const APP_COLOR = {
    // primary:{
    //     ... TDS_UI_COLOR.primary,
    //     1:'red'
    // }
};
//override màu theo thiết kế
const COLOR = { ...TDS_UI_COLOR,...TDS_UI_CONFIG.theme.extend.colors, ...APP_COLOR }
module.exports = {
    content: [
        ...TDS_UI_CONFIG.content,
        './src/**/*.{html,ts}',
    ],
    darkMode: "class",
    theme: {
        extend: {
            zIndex: {
                ...TDS_UI_CONFIG.theme.extend.zIndex
            },
            colors: {
                ...COLOR,
            },
            ringColor: {
                ...COLOR,
            },
            borderColor: {
                ...COLOR,
            },
            boxShadow: {
                ...TDS_UI_CONFIG.theme.extend.boxShadow,
            },
            minWidth: {
                ...TDS_UI_CONFIG.theme.extend.minWidth,
            },
            minHeight: {
                ...TDS_UI_CONFIG.theme.extend.minHeight,
            },
            opacity: {
                ...TDS_UI_CONFIG.theme.extend.opacity,
            },
            fontSize: {
                ...TDS_UI_CONFIG.theme.extend.fontSize,
            },
            placeholderColor: {
                ...COLOR,
            },
            ringWidth: {
                ...TDS_UI_CONFIG.theme.extend.ringWidth,
            },
            height: {
                ...TDS_UI_CONFIG.theme.extend.height,
            },
            borderRadius: {
                ...TDS_UI_CONFIG.theme.extend.borderRadius,
            },
            fontWeight: {
                ...TDS_UI_CONFIG.theme.extend.fontWeight,
            },
            borderWidth: {
                ...TDS_UI_CONFIG.theme.extend.borderWidth,
            },
            spacing: {
                ...TDS_UI_CONFIG.theme.extend.spacing,
            },
            backgroundImage: {
                ...TDS_UI_CONFIG.theme.extend.backgroundImage,
            },
            transitionProperty: {
                ...TDS_UI_CONFIG.theme.extend.transitionProperty,
            },
            transitionTimingFunction: {
                ...TDS_UI_CONFIG.theme.extend.transitionTimingFunction,
            },
            keyframes: {
                ...TDS_UI_CONFIG.theme.extend.keyframes,
            },
            animation: {
                ...TDS_UI_CONFIG.theme.extend.animation,
            },
            fontFamily: {
                ...TDS_UI_CONFIG.theme.extend.fontFamily
            },
            lineHeight: {
                ...TDS_UI_CONFIG.theme.extend.lineHeight
            },
            screens: {
                ...TDS_UI_CONFIG.theme.extend.screens
            }
        },
    },
    variants: {
        extend: {}
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        ...TDS_UI_CONFIG.plugin,
    ],
};
```

## 4. styles.scss

### Path relativity cho SCSS imports

Path `../node_modules/...` mặc định `styles.scss` ở `src/styles.scss`. Nếu đặt `styles.scss` chỗ khác, adjust:

- `src/styles.scss` → `../node_modules/tds-ui/...`
- `src/styles/styles.scss` → `../../node_modules/tds-ui/...`
- Root `styles.scss` → `./node_modules/tds-ui/...`

Verify file tồn tại sau install:

```powershell
ls node_modules/tds-ui/assets/v2/scss/components/tds.component.scss
ls node_modules/tds-ui/assets/v2/scss/theme/theme.all.scss
```

### styles.scss (consumer version)

```scss
@import "tailwindcss/base";
@import "tailwindcss/components";
@import "tailwindcss/utilities";
@import "../node_modules/tds-ui/assets/v2/scss/components/tds.component.scss";
// Tùy vào dự án chọn theme blue/green/orange/red/yellow hoặc all
// Theme Blue (Retail)
// @import "../node_modules/tds-ui/assets/v2/scss/theme/theme.blue.scss";
// Theme Green (Landing)
// @import "../node_modules/tds-ui/assets/v2/scss/theme/theme.green.scss";
// Theme Orange (Social)
// @import "../node_modules/tds-ui/assets/v2/scss/theme/theme.orange.scss";
// theme yellow
// @import "../node_modules/tds-ui/assets/v2/scss/theme/theme.yellow.scss";
// theme red
// @import "../node_modules/tds-ui/assets/v2/scss/theme/theme.red.scss";
// mặc định theme blue
@import "../node_modules/tds-ui/assets/v2/scss/theme/theme.all.scss";
```

### Theme mapping

| Project | Theme file |
|---------|-----------|
| Retail / POS | `theme.blue.scss` |
| Landing / Web | `theme.green.scss` |
| Social / Pixel | `theme.orange.scss` |
| Mặc định | `theme.all.scss` |

### Path reference table (consumer-facing files)

| File | Path type | Default |
|------|-----------|---------|
| `*.scss` imports trong `styles.scss` | Tương đối từ vị trí `styles.scss` | `../node_modules/tds-ui/...` (nếu `src/styles.scss`) |
| `tailwind.config.js` require | Từ project root (Tailwind CWD) | `./node_modules/tds-ui/...` |
| `*.js` scripts trong `angular.json` (nếu cần) | Từ project root | `node_modules/tds-ui/...` |

Note: `node_modules/tds-ui/icon/list-icon.js` là internal registry, **không cần load** trong consumer. Icons dùng CSS class `tdsi-*` từ font-icon CDN (Section 5).

## 5. index.html (fonts + icons)

Thêm vào `<head>` trong `src/index.html`:

```html
<link rel="stylesheet" href="https://static.design-system.local/assets/fonts/TMTSans/style.css">
<link rel="stylesheet" href="https://static.design-system.local/assets/font-icon/style.css">
```

- Link 1: Font TMTSans (font family mặc định của tds-ui components)
- Link 2: Icon font cho `tdsi-*` CSS classes

## 6. App config (i18n + locale + animations + CDK)

### Standalone (mới — khuyến nghị)

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations';
import localeVi from '@angular/common/locales/vi';
import { registerLocaleData } from '@angular/common';
import { TDS_I18N, vi_VN } from 'tds-ui/i18n';

registerLocaleData(localeVi);

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    { provide: TDS_I18N, useValue: vi_VN },
  ],
};
```

### NgModule (cũ)

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { DragDropModule } from '@angular/cdk/drag-drop';
import localeVi from '@angular/common/locales/vi';
import { registerLocaleData } from '@angular/common';
import { TDS_I18N, vi_VN } from 'tds-ui/i18n';

registerLocaleData(localeVi);

@NgModule({
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    ScrollingModule,
    DragDropModule,
  ],
  providers: [{ provide: TDS_I18N, useValue: vi_VN }],
})
export class AppModule {}
```

### Lưu ý

- `provideAnimations()` / `BrowserAnimationsModule` bắt buộc (component dùng Angular animations)
- `ScrollingModule` cho menu, drawer scroll (`CdkScrollable`)
- `DragDropModule` cho drag feature
- `registerLocaleData(localeVi)` đăng ký locale Việt Nam cho pipes (`date`, `number`, `currency`)
- `{ provide: TDS_I18N, useValue: vi_VN }` cấu hình i18n cho tds-ui components (modal, table, pagination...)

## 7. AI Verify (Claude auto check)

Sau khi dev install, Claude auto check:

1. `node_modules/tds-ui/` tồn tại
2. `package.json` có entry `tds-ui`
3. `tailwind.config.js` require path `./node_modules/tds-ui/tailwindcss/v2/tailwind.config.js`
4. `styles.scss` có 3 import: `tailwindcss`, `tds.component.scss`, `theme.*.scss`
5. `index.html` có 2 CDN link (font + icon)
6. App config có `provideAnimations()` + `TDS_I18N` provider + `registerLocaleData`
7. `ng build` pass, no error `Cannot find module 'tds-ui/...'`

Lệnh check nhanh:

```powershell
ls node_modules/tds-ui
npm ls tds-ui
npm ls @angular/cdk @angular/core
```

## 8. Dev Verify (human check)

### Smoke test component

Tạo component test:

```typescript
import { Component } from '@angular/core';
import { TDSButtonModule } from 'tds-ui/button';

@Component({
  standalone: true,
  imports: [TDSButtonModule],
  template: `<button tds-button color="primary">Test</button>`,
})
export class InstallTestComponent {}
```

Route tạm `/install-test` → component này. Mở browser.

### Dấu hiệu OK

- Button render dạng pill, màu primary (xanh), có hover state
- Font TMTSans apply (không phải font mặc định browser)
- DevTools element `<button>` có class `tds-btn`, `tds-btn-primary`
- Console không lỗi `NG0303` / `NG0304`

### Dấu hiệu lỗi

| Triệu chứng | Nguyên nhân | Fix |
|-------------|-------------|-----|
| `NG0304: No directive found` | Thiếu import module | Thêm `TDSButtonModule` vào `imports: []` |
| Button "trần" không style | Tailwind/styles sai | Check Section 3 + 4, verify `styles.scss` có `tds.component.scss` import |
| `Cannot find module 'tds-ui/i18n'` | Package chưa install hoặc path sai | Run `npm install` lại, check `node_modules/tds-ui/` |
| Icon không hiển thị | Thiếu font-icon CDN | Add link Section 5 vào `index.html` |
| Pipe `date` báo lỗi locale | Thiếu `registerLocaleData` | Add `registerLocaleData(localeVi)` Section 6 |

### Next steps

Sau khi verify OK, xem:

- `reference/import-guide.md` — Import patterns trong code
- `reference/components-index.md` — Component catalog
- `recipes/` — Task-oriented guides
