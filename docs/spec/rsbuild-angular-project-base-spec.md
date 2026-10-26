# HƯỚNG DẪN NÂNG CẤP & SỬ DỤNG RSBUILD CHO ANGULAR MICRO-FRONTEND
## (HƯỚNG DẪN CHUẨN HÓA THEO MÔ HÌNH THỰC TẾ DEMO CRM MONOREPO)

> **Mục tiêu**: Hướng dẫn chi tiết từng bước (step-by-step) giúp các lập trình viên dễ dàng **nâng cấp bất kỳ Remote MFE hoặc ứng dụng Angular nào** trong hệ thống Monorepo từ Webpack truyền thống lên **Rsbuild (Rspack Rust)** — bám sát 100% kiến trúc đang vận hành thực tế tại dự án **Demo CRM**.

---

## 1. Vì Sao Phải Nâng Cấp Lên Rsbuild?

So sánh thực tế trên hệ thống CI/CD và máy phát triển của dự án:
* ⚡ **Thời gian CI/CD Pipeline giảm gần 50%**: Giảm từ **6 phút 45 giây** (Native Nx Webpack) xuống **3 phút 32 giây** (Rsbuild Staging).
* ⚡ **Dev Server bật tức thì**: Khởi động trong **< 1 giây** thay vì phải chờ 20–40 giây.
* ⚡ **HMR phản hồi siêu tốc**: Lưu file `.ts`, `.html`, `.scss` cập nhật ngay trong **< 50ms**.
* 📉 **Xóa bỏ hơn 1,300 dòng boilerplate**: Loại bỏ hoàn toàn các file `webpack.config.ts`, `webpack.prod.config.ts`, `module-federation.config.ts` rườm rà ở từng app.

---

## 2. Bước 1: Cài Đặt Thư Viện Tại Root Monorepo

Nếu workspace chưa có các gói Rsbuild, bổ sung các thư viện sau vào `package.json` ở thư mục gốc:

```bash
# Dùng pnpm (khuyến nghị cho Nx Monorepo):
pnpm add -D @rsbuild/core @ng-rsbuild/plugin-angular @rsbuild/plugin-sass sass
pnpm add -D @module-federation/rsbuild-plugin
pnpm add @module-federation/enhanced

# Hoặc dùng npm:
npm install -D @rsbuild/core @ng-rsbuild/plugin-angular @rsbuild/plugin-sass sass --legacy-peer-deps
npm install -D @module-federation/rsbuild-plugin --legacy-peer-deps
npm install @module-federation/enhanced --legacy-peer-deps
```

---

## 3. Bước 2: Hạt Nhân Dùng Chung `module-federation.shared.ts`

Toàn bộ logic phức tạp của Rsbuild và Module Federation được đóng gói tập trung tại file `module-federation.shared.ts` ở thư mục gốc workspace. Mọi app con chỉ cần gọi lại:

### 3.1 Khai Báo Danh Mục Shared Dependencies (Singleton)
Đảm bảo toàn bộ Angular Framework, RxJS và các thư viện dùng chung trong công ty chạy đúng 1 phiên bản duy nhất (Singleton):

```typescript
// module-federation.shared.ts
export function getSharedDependencies(isHost = false) {
  const eager = isHost;
  return {
    // Angular Core packages
    '@angular/core': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/common': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/common/http': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/router': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/platform-browser': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/platform-browser/animations': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/animations': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/forms': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/cdk': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/cdk/': { singleton: true, strictVersion: false, eager, requiredVersion: false },

    // Reactive
    'rxjs': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    'rxjs/operators': { singleton: true, strictVersion: false, eager, requiredVersion: false },

    // Core Shared Suite & Design System
    '@wi-mfes/i18n': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@wi-mfes/config': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@wi-mfes/context': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@wi-mfes/perm': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@wi-mfes/remote-loader': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@wi-mfes/load-styles': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@wi-mfes/event-bus': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    'tds-ui': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    'tds-ui/': { singleton: true, strictVersion: false, eager, requiredVersion: false },
  };
}
```

### 3.2 Hàm Khởi Tạo Cấu Hình `createRsbuildConfig`
Hàm này tự động nhận diện Host vs Remote, tự cấu hình port, manifest, proxy API Gateway và Module Federation:

```typescript
// module-federation.shared.ts
import { createConfig } from '@ng-rsbuild/plugin-angular';
import { pluginModuleFederation } from '@module-federation/rsbuild-plugin';

export async function createRsbuildConfig(config: { appName?: string; port?: number } = {}) {
  const appName = config.appName ?? 'app-shell';
  const isHost = appName === 'app-shell';
  const appDir = `apps/${appName}`;
  const port = config.port ?? (isHost ? 4200 : 4201);
  const uniqueName = appName.replace(/-/g, '_');

  return await createConfig({
    options: {
      browser: `./${appDir}/src/main.ts`,
      index: `./${appDir}/src/index.html`,
      tsConfig: `./${appDir}/tsconfig.app.json`,
      styles: [`./${appDir}/src/styles.scss`],
      polyfills: ['zone.js'],
      inlineStyleLanguage: 'scss',
      devServer: { port },
    },
    rsbuildConfig: {
      server: {
        port,
        headers: { 'Access-Control-Allow-Origin': '*' },
      },
      output: {
        assetPrefix: isHost ? '/' : 'auto',
        distPath: { root: `dist/${appDir}` },
      },
      plugins: [
        pluginModuleFederation({
          name: uniqueName,
          shared: getSharedDependencies(isHost),
          ...(isHost
            ? {}
            : {
                filename: 'remoteEntry.mjs',
                exposes: {
                  './Routes': `./${appDir}/src/app/remote-entry/entry.routes.ts`,
                },
              }),
        }),
      ],
    },
  });
}
```

---

## 4. Bước 3: Nâng Cấp Một Remote MFE Cụ Thể (Chỉ 3 Bước)

Khi bạn muốn nâng cấp một app (ví dụ: `apps/mfe-crm`, `apps/mfe-cdp`, hoặc `apps/mfe-account`), thực hiện đúng 3 bước:

### 4.1 Tạo File `apps/<tên-app>/rsbuild.config.ts` (Chỉ 6 Dòng Code!)
Tạo file cấu hình cực kỳ gọn nhẹ:

* **Đối với Remote MFE (ví dụ `apps/mfe-crm/rsbuild.config.ts`):**
  ```typescript
  import { createRsbuildConfig } from '../../module-federation.shared';

  export default async () => {
    return await createRsbuildConfig({
      appName: 'mfe-crm',
      port: 4203,
    });
  };
  ```

* **Đối với Host Shell (`apps/app-shell/rsbuild.config.ts`):**
  ```typescript
  import { createRsbuildConfig } from '../../module-federation.shared';

  export default async () => {
    return await createRsbuildConfig();
  };
  ```

---

### 4.2 Cập Nhật File `apps/<tên-app>/project.json`
Mở `project.json` của app, chuyển các target `build` và `serve` cũ sang `nx:run-commands` ủy quyền cho Rsbuild:

```json
{
  "name": "mfe-crm",
  "projectType": "application",
  "sourceRoot": "apps/mfe-crm/src",
  "targets": {
    "build": {
      "executor": "nx:run-commands",
      "options": {
        "command": "npx rsbuild build --config apps/mfe-crm/rsbuild.config.ts"
      }
    },
    "build-rsbuild": {
      "executor": "nx:run-commands",
      "options": {
        "command": "npx rsbuild build --config apps/mfe-crm/rsbuild.config.ts"
      }
    },
    "serve": {
      "executor": "nx:run-commands",
      "options": {
        "command": "npx rsbuild dev --config apps/mfe-crm/rsbuild.config.ts"
      }
    },
    "lint": {
      "executor": "@nx/eslint:lint"
    },
    "test": {
      "executor": "@nx/jest:jest",
      "options": {
        "jestConfig": "apps/mfe-crm/jest.config.ts"
      }
    }
  }
}
```

---

### 4.3 Xóa Bỏ Các File Cấu Hình Webpack Cũ (Dọn Rác)
Xóa các file Webpack rườm rà không còn dùng trong thư mục của app:
* ❌ `apps/<tên-app>/webpack.config.ts`
* ❌ `apps/<tên-app>/webpack.prod.config.ts`
* ❌ `apps/<tên-app>/module-federation.config.ts`

---

## 5. Bước 4: Cập Nhật `scripts` Trong Root `package.json`

Thêm các script tiện ích để khởi chạy và build độc lập hoặc toàn bộ hệ thống:

```json
{
  "scripts": {
    "start": "rsbuild dev --config apps/app-shell/rsbuild.config.ts --port 4200",
    "start:shell": "rsbuild dev --config apps/app-shell/rsbuild.config.ts --port 4200",
    "start:crm": "rsbuild dev --config apps/mfe-crm/rsbuild.config.ts",
    "start:account": "rsbuild dev --config apps/mfe-account/rsbuild.config.ts",
    "start:cdp": "rsbuild dev --config apps/mfe-cdp/rsbuild.config.ts",
    "start:dev": "concurrently -k -n \"SHELL,CRM\" -c \"bgCyan.bold,bgGreen.bold\" \"npm:start:shell\" \"npm:start:crm\"",
    "start:all": "concurrently -k -n \"SHELL,ACCOUNT,CDP,CRM\" -c \"bgCyan.bold,bgYellow.bold,bgBlue.bold,bgGreen.bold\" \"npm:start:shell\" \"npm:start:account\" \"npm:start:cdp\" \"npm:start:crm\"",

    "build": "nx run-many --target=build-rsbuild --all --parallel=true",
    "build:dev": "nx run-many --target=build-rsbuild --all --parallel=true --configuration=development",
    "build:staging": "APP_ENV=staging nx run-many --target=build-rsbuild --all --parallel=true",
    "build:production": "APP_ENV=production nx run-many --target=build-rsbuild --all --parallel=true",

    "build:shell": "rsbuild build --config apps/app-shell/rsbuild.config.ts",
    "build:crm": "rsbuild build --config apps/mfe-crm/rsbuild.config.ts"
  }
}
```

---

## 6. Bước 5: Định Tuyến Nạp Động Remote Module (Angular Router Bridge)

Tại Host Shell (`apps/app-shell/src/app/app.routes.ts`), sử dụng API chuẩn của `@module-federation/enhanced/runtime` để lazy load remote module mà không cần import tĩnh:

```typescript
import { Routes } from '@angular/router';
import { loadRemote } from '@module-federation/enhanced/runtime';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'crm',
    pathMatch: 'full',
  },
  {
    path: 'crm',
    loadChildren: () =>
      loadRemote<any>('mfe_crm/Routes').then((m) => m.routes),
  },
  {
    path: 'cdp',
    loadChildren: () =>
      loadRemote<any>('mfe_cdp/Routes').then((m) => m.routes),
  },
];
```

Tại Remote MFE (`apps/mfe-crm/src/app/remote-entry/entry.routes.ts`):
```typescript
import { Routes } from '@angular/router';
import { CrmDashboardComponent } from '../features/dashboard/crm-dashboard.component';

export const routes: Routes = [
  {
    path: '',
    component: CrmDashboardComponent,
    children: [
      {
        path: 'customers',
        loadComponent: () =>
          import('../features/customers/customer-list.component').then(
            (m) => m.CustomerListComponent
          ),
      },
    ],
  },
];
```

---

## 7. Cấu Hình Docker & NGINX Sẵn Sàng Triển Khai Production

Khi đóng gói từng Micro-Frontend ra Docker container độc lập, cần cấu hình NGINX mở CORS để Host Shell tải được `remoteEntry.mjs`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        # Cho phép Host Shell nạp script từ xa qua domain khác
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS' always;
    }

    # remoteEntry.mjs & mf-manifest.json tuyệt đối KHÔNG cache để cập nhật tức thì khi deploy
    location ~* (remoteEntry\.mjs|mf-manifest\.json)$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Access-Control-Allow-Origin * always;
    }
}
```

---

## 8. Checklist Nghiệm Thu Sau Khi Nâng Cấp

Sau khi thực hiện các bước trên cho app của bạn, hãy kiểm tra:
- [x] Chạy lẻ app: `npm run start:<tên-app>` mở lên mượt mà, không lỗi injector.
- [x] Chạy kèm Host: `npm run start:all`, truy cập `http://localhost:4200/<route-app>` hiển thị chính xác component của Remote.
- [x] Build thử nghiệm: `npm run build` hoàn thành toàn bộ monorepo song song trong thời gian ngắn.
- [x] Kiểm tra tab Network/Console: Không xuất hiện duplicate `@angular/core` hay cảnh báo CORS.

---

## 9. Tài Liệu Tham Khảo & Báo Cáo Đo Kiểm Hiệu Năng Thực Tế

* 📊 **Báo cáo đối đầu thực tế trên GitHub Actions CI/CD**: Xem so sánh chi tiết giữa Rsbuild và Native Nx Angular (cả 2 cấp độ: Tiêu chuẩn 36s vs 2m30s và Tải nặng 3m32s vs 6m45s) cùng hình ảnh đối chiếu tại:  
  👉 [**Giới thiệu về thư viện Rsbuild & Hệ sinh thái Rstack cho Angular**](https://docs.example.com/doc/gioi-thieu-ve-thu-vien-rsbuild-he-sinh-thai-rstack-cho-angular-rbHdDQJfTw)
* **Kho mã nguồn mẫu chuẩn**: [https://github.com/baobao0303/project_base_rsbuild](https://github.com/baobao0303/project_base_rsbuild)
