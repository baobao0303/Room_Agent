# ĐẶC TẢ KỸ THUẬT: QUY TRÌNH CHUYỂN ĐỔI (MIGRATION) TỪ NX WEBPACK SANG RSBUILD & KHỞI TẠO DỰ ÁN MỚI
## (ANGULAR NX TO RSBUILD MIGRATION & FRESH SETUP SPECIFICATION)

- **Mã tài liệu**: `docs/spec/angular-nx-to-rsbuild-migration-spec.md`
- **Phiên bản**: 1.0.0
- **Phân loại**: Core Architecture / Migration Guide
- **Áp dụng cho**: Toàn bộ dự án Angular Monorepo (Nx Workspace) và Angular Single Apps trong hệ thống

---

# 1. TỔNG QUAN & MỤC TIÊU (OVERVIEW & OBJECTIVES)

## 1.1 Bối Cảnh & Vấn Đề Cần Giải Quyết
Các ứng dụng Angular quy mô lớn (Enterprise Monorepo với Nx) chạy trên Webpack (`@angular-devkit/build-angular` hoặc `@nx/webpack`) đang gặp các điểm nghẽn nghiêm trọng:
* **Thời gian build CI/CD kéo dài**: Pipeline tốn từ **6 đến 15 phút** cho mỗi commit/PR.
* **Khởi động Dev Server chậm**: Mất từ **20s đến 60s** để bắt đầu lập trình.
* **HMR Rebuild giật lag**: Sửa một dòng code mất **3s – 8s** mới hiển thị lên trình duyệt.
* **Tốn tài nguyên bộ nhớ**: Webpack ngốn **2GB – 4GB RAM**, dễ gây lỗi `JavaScript heap out of memory`.

## 1.2 Mục Tiêu Sau Khi Chuyển Sang Rsbuild (Rspack Rust)
| Chỉ Số Đo Lường | Hiện Tại (Nx Webpack) | Mục Tiêu Sau Chuyển Đổi (Rsbuild) | Mức Độ Cải Thiện |
| :--- | :---: | :---: | :---: |
| **Khởi động Dev Server** | 20s – 40s | **< 1s** | ⚡ **Nhanh gấp 30x** |
| **Hot Module Replacement (HMR)** | 3,000ms – 5,000ms | **< 50ms** | ⚡ **Phản hồi tức thì** |
| **Build CI/CD Container** | 6m 45s (405s) | **3m 32s (212s)** | ⚡ **Tiết kiệm 48% thời gian** |
| **Bộ nhớ RAM tiêu thụ** | 2.4 GB | **650 MB** | 📉 **Giảm 73% RAM** |
| **Tính tương thích** | Angular 18 | **Giữ nguyên 100% cú pháp Angular & Signals** | Không đổi logic nghiệp vụ |

---

# 2. LỰA CHỌN KỊCH BẢN (CHOOSE YOUR PATH)

Tài liệu này cung cấp 2 kịch bản hoàn chỉnh:
* **Kịch bản A (Migration)**: Dành cho dự án Nx Monorepo đang chạy sẵn bằng Webpack muốn nâng cấp lên Rsbuild mà không phá vỡ cấu trúc code hiện tại.
* **Kịch bản B (Fresh Setup)**: Dành cho việc khởi tạo dự án Angular mới toanh (Single App hoặc Nx Monorepo MFE).

```text
               BẠN MUỐN LÀM GÌ?
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
 [Kịch Bản A: Migration]   [Kịch Bản B: Fresh Setup]
  Dự án Nx Webpack cũ      Khởi tạo dự án mới từ đầu
  (Chuyển đổi 5 bước)       (Scaffolding 4 bước)
```

---

# 3. KỊCH BẢN A: QUY TRÌNH CHUYỂN ĐỔI TỪ NX WEBPACK SANG RSBUILD

Quy trình chuyển đổi gồm 5 bước chuẩn hóa (áp dụng thành công trên Demo CRM Monorepo):

```text
[Bước 1: Cài đặt Dependencies]
         │
         ▼
[Bước 2: Tạo module-federation.shared.ts dùng chung]
         │
         ▼
[Bước 3: Tạo rsbuild.config.ts cho từng App (Host & Remotes)]
         │
         ▼
[Bước 4: Cập nhật project.json sang nx:run-commands]
         │
         ▼
[Bước 5: Dọn dẹp Webpack cũ & Cập nhật package.json scripts]
```

### Bước 1: Cài Đặt Dependencies Tại Thư Mục Gốc
Bổ sung bộ công cụ Rsbuild vào `devDependencies` và Module Federation v2:

```bash
# Dùng pnpm (khuyến nghị cho Nx):
pnpm add -D @rsbuild/core @ng-rsbuild/plugin-angular @rsbuild/plugin-sass sass
pnpm add -D @module-federation/rsbuild-plugin
pnpm add @module-federation/enhanced

# Hoặc dùng npm:
npm install -D @rsbuild/core @ng-rsbuild/plugin-angular @rsbuild/plugin-sass sass --legacy-peer-deps
npm install -D @module-federation/rsbuild-plugin --legacy-peer-deps
npm install @module-federation/enhanced --legacy-peer-deps
```

---

### Bước 2: Tạo Hạt Nhân Cấu Hình Dùng Chung (`module-federation.shared.ts`)
Tạo file `module-federation.shared.ts` tại thư mục gốc workspace để đóng gói toàn bộ logic cấu hình cho tất cả các app:

```typescript
import { createConfig, type PluginAngularOptions } from '@ng-rsbuild/plugin-angular';
import { pluginModuleFederation } from '@module-federation/rsbuild-plugin';
import type { RsbuildConfig } from '@rsbuild/core';

export interface RsbuildOptions {
  appName?: string;
  isHost?: boolean;
  port?: number;
  exposes?: Record<string, string>;
  remotes?: Record<string, string>;
  extraOptions?: Partial<PluginAngularOptions>;
}

export function getSharedDependencies(isHost = false) {
  const eager = isHost;
  return {
    // Angular Singletons bắt buộc để không crash injector
    '@angular/core': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/common': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/common/http': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/router': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/platform-browser': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/forms': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    '@angular/cdk': { singleton: true, strictVersion: false, eager, requiredVersion: false },

    // Reactive singletons
    'rxjs': { singleton: true, strictVersion: false, eager, requiredVersion: false },
    'zone.js': { singleton: true, strictVersion: false, eager, requiredVersion: false },
  };
}

export async function createRsbuildConfig(config: RsbuildOptions = {}) {
  const appName = config.appName ?? 'app-shell';
  const isHost = config.isHost ?? (appName === 'app-shell');
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
      ...config.extraOptions,
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
            ? { remotes: config.remotes ?? {} }
            : {
                filename: 'remoteEntry.mjs',
                exposes: config.exposes ?? {
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

### Bước 3: Tạo File Cấu Hình Cho Từng App (`rsbuild.config.ts`)
Từng app con chỉ cần một file cấu hình siêu gọn (6 dòng code):

* **Tại Remote MFE (`apps/mfe-crm/rsbuild.config.ts`):**
  ```typescript
  import { createRsbuildConfig } from '../../module-federation.shared';

  export default async () => {
    return await createRsbuildConfig({
      appName: 'mfe-crm',
      port: 4204,
    });
  };
  ```

* **Tại Host Shell (`apps/app-shell/rsbuild.config.ts`):**
  ```typescript
  import { createRsbuildConfig } from '../../module-federation.shared';

  export default async () => {
    return await createRsbuildConfig({
      appName: 'app-shell',
      port: 4200,
      remotes: {
        'mfe_crm': 'mfe_crm@http://localhost:4204/mf-manifest.json',
      },
    });
  };
  ```

---

### Bước 4: Chuyển Target Trong `project.json` Sang `nx:run-commands`
Mở `project.json` của từng app, thay thế các builder Webpack cũ bằng executor `nx:run-commands`:

```json
{
  "name": "mfe-crm",
  "projectType": "application",
  "sourceRoot": "apps/mfe-crm/src",
  "targets": {
    "serve": {
      "executor": "nx:run-commands",
      "options": {
        "command": "npx rsbuild dev --config apps/mfe-crm/rsbuild.config.ts"
      }
    },
    "build": {
      "executor": "nx:run-commands",
      "options": {
        "command": "npx rsbuild build --config apps/mfe-crm/rsbuild.config.ts"
      },
      "outputs": ["{workspaceRoot}/dist/apps/mfe-crm"]
    },
    "build-rsbuild": {
      "executor": "nx:run-commands",
      "options": {
        "command": "npx rsbuild build --config apps/mfe-crm/rsbuild.config.ts"
      },
      "outputs": ["{workspaceRoot}/dist/apps/mfe-crm"]
    }
  }
}
```

---

### Bước 5: Dọn Rác & Cập Nhật `package.json` Scripts
1. **Xóa các file Webpack cũ không còn dùng trong từng app:**
   * `apps/*/webpack.config.ts`
   * `apps/*/webpack.prod.config.ts`
   * `apps/*/module-federation.config.ts`
2. **Gỡ bỏ gói custom webpack thừa:**
   ```bash
   npm uninstall @angular-builders/custom-webpack
   ```
3. **Cập nhật scripts trong root `package.json`:**
   ```json
   {
     "scripts": {
       "start": "rsbuild dev --config apps/app-shell/rsbuild.config.ts --port 4200",
       "start:shell": "rsbuild dev --config apps/app-shell/rsbuild.config.ts --port 4200",
       "start:crm": "rsbuild dev --config apps/mfe-crm/rsbuild.config.ts --port 4204",
       "start:dev": "concurrently -k -n \"SHELL,CRM\" -c \"bgCyan.bold,bgGreen.bold\" \"npm:start:shell\" \"npm:start:crm\"",
       "build": "nx run-many --target=build-rsbuild --all --parallel=true",
       "build:staging": "APP_ENV=staging nx run-many --target=build-rsbuild --all --parallel=true",
       "build:production": "APP_ENV=production nx run-many --target=build-rsbuild --all --parallel=true"
     }
   }
   ```

---

# 4. KỊCH BẢN B: QUY TRÌNH KHỞI TẠO DỰ ÁN MỚI (FRESH SETUP)

Nếu bắt đầu một dự án mới hoàn toàn từ đầu:

### Bước 1: Khởi Tạo Nx Workspace Rỗng
```bash
npx create-nx-workspace@latest angular-rsbuild-monorepo --preset=apps --packageManager=pnpm
cd angular-rsbuild-monorepo
```

### Bước 2: Cài Đặt Angular & Rsbuild Core
```bash
pnpm add @angular/core @angular/common @angular/router @angular/platform-browser @angular/forms rxjs zone.js
pnpm add -D @angular/compiler @angular/compiler-cli typescript
pnpm add -D @rsbuild/core @ng-rsbuild/plugin-angular @rsbuild/plugin-sass sass
pnpm add -D @module-federation/rsbuild-plugin @module-federation/enhanced
pnpm add -D concurrently
```

### Bước 3: Tạo Cấu Trúc Thư Mục Tiêu Chuẩn
```text
angular-rsbuild-monorepo/
├── apps/
│   ├── app-shell/               # Host Application
│   │   ├── rsbuild.config.ts
│   │   ├── project.json
│   │   └── src/
│   │       ├── main.ts
│   │       ├── index.html
│   │       ├── styles.scss
│   │       └── app/
│   │           ├── app.component.ts
│   │           └── app.routes.ts
│   └── mfe-crm/                 # Remote Micro-Frontend
│       ├── rsbuild.config.ts
│       ├── project.json
│       └── src/
│           ├── main.ts
│           └── app/
│               └── remote-entry/
│                   └── entry.routes.ts
├── module-federation.shared.ts  # Cấu hình dùng chung
├── package.json
└── tsconfig.base.json
```

### Bước 4: Thiết Lập Routing Nạp Động Giữa Host & Remote
* **Tại Remote (`apps/mfe-crm/src/app/remote-entry/entry.routes.ts`):**
  ```typescript
  import { Routes } from '@angular/router';
  import { CrmHomeComponent } from '../features/home/crm-home.component';

  export const routes: Routes = [
    { path: '', component: CrmHomeComponent }
  ];
  ```

* **Tại Host Shell (`apps/app-shell/src/app/app.routes.ts`):**
  ```typescript
  import { Routes } from '@angular/router';
  import { loadRemote } from '@module-federation/enhanced/runtime';

  export const routes: Routes = [
    {
      path: 'crm',
      loadChildren: () => loadRemote<any>('mfe_crm/Routes').then(m => m.routes),
    },
  ];
  ```

---

# 5. CÁC HỐ GÀ KỸ THUẬT BẮT BUỘC PHẢI TRÁNH (4 CRITICAL GOTCHAS)

Kinh nghiệm thực chiến từ dự án cho thấy 90% lập trình viên sẽ bị kẹt ở 4 điểm sau nếu không nắm rõ:

---

### Gotcha 1: Cấu Hình `tsconfig.app.json` Cho Angular Decorators
Angular 18 biên dịch trên SWC/Rspack yêu cầu cờ TypeScript chuẩn hóa. Nếu thiếu, decorator `@Component`, `@Injectable` hoặc Signals sẽ không hoạt động:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": false,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "experimentalDecorators": true,
    "emitDecoratorMetadata": false,
    "skipLibCheck": true
  }
}
```
*(Đặc biệt chú ý: `useDefineForClassFields: false` là bắt buộc để Angular DI hoạt động trơn tru).*

---

### Gotcha 2: Async Bootstrap Tránh Lỗi "Eager Consumption"
Trong Module Federation, nếu `main.ts` gọi `bootstrapApplication()` đồng bộ trực tiếp, trình duyệt có thể thực thi trước khi các Shared Singletons kịp tải về, sinh lỗi:  
`Uncaught Error: Shared module is not available for eager consumption: @angular/core`

* **Cách khắc phục chuẩn**:
  Tách `main.ts` thành 2 file:
  * File `src/bootstrap.ts`:
    ```typescript
    import { bootstrapApplication } from '@angular/platform-browser';
    import { appConfig } from './app/app.config';
    import { AppComponent } from './app/app.component';

    bootstrapApplication(AppComponent, appConfig).catch((err) => console.error(err));
    ```
  * File `src/main.ts` (chỉ import dynamic):
    ```typescript
    import('./bootstrap').catch((err) => console.error(err));
    ```

---

### Gotcha 3: Nạp Assets / SVG / Fonts Tránh Bị Lỗi 404
Khi Host nạp component của Remote CRM, nếu Remote dùng đường dẫn tuyệt đối như `<img src="/assets/logo.png">`, trình duyệt sẽ tìm tại `http://localhost:4200/assets/logo.png` (Host) thay vì cổng `4204` của CRM dẫn đến **lỗi 404**.

* **Cách khắc phục**:
  1. Trong `rsbuild.config.ts` của Remote, bắt buộc đặt:  
     `output: { assetPrefix: 'auto' }`
  2. Trong CSS / Template của Remote, ưu tiên dùng import hoặc CSS background:
     ```scss
     .logo { background-image: url('../../assets/logo.svg'); }
     ```

---

### Gotcha 4: Chuyển Đổi Biến Môi Trường (`environment.ts` Sang `.env`)
Webpack Angular truyền thống dùng cơ chế `fileReplacements` tráo đổi file `environment.ts` rất cồng kềnh.  
Với Rsbuild, chuyển sang chuẩn hiện đại:
1. Tạo file `.env`, `.env.development`, `.env.production` tại thư mục app.
2. Tiền tố `PUBLIC_` tự động được Rsbuild nhúng vào code:
   ```typescript
   // Thay vì import { environment } from '../environments/environment';
   export const API_URL = process.env['PUBLIC_API_URL'] || 'http://localhost:3000';
   ```

---

# 6. BẢNG TRA CỨU LỖI NHANH (QUICK TROUBLESHOOTING MATRIX)

| Hiện Tượng / Báo Lỗi | Nguyên Nhân Gốc | Giải Pháp Khắc Phục Ngay Lập Tức |
| :--- | :--- | :--- |
| **`NullInjectorError: No provider for...`** | Bị duplicate instance của `@angular/core` do version sai lệch. | Kiểm tra `module-federation.shared.ts`, đảm bảo package đó có `singleton: true, strictVersion: false, requiredVersion: false`. |
| **`CORS policy: No 'Access-Control-Allow-Origin'`** | Host Shell không thể nạp file `remoteEntry.mjs` từ domain/port khác. | Bổ sung `server: { headers: { 'Access-Control-Allow-Origin': '*' } }` vào cấu hình Remote hoặc NGINX. |
| **`Failed to load remote module: mfe_crm/Routes`** | Host không tìm thấy file metadata manifest của Remote. | Đảm bảo Remote đang chạy và Host khai báo remotes trỏ tới `http://localhost:4204/mf-manifest.json` (hoặc `remoteEntry.mjs`). |
| **`The "namedChunks" option is not supported`** | Thuộc tính thừa của Webpack cũ sót lại trong `project.json`. | Xóa key `namedChunks` trong phần options của `project.json`. |
| **`ZoneAwarePromise error`** | Host và Remote nạp 2 bản `zone.js` độc lập làm xung đột microtask. | Đảm bảo `zone.js` nằm trong danh sách `sharedDependencies` với `singleton: true`. |

---

# 7. CHIẾN LƯỢC TRIỂN KHAI CI/CD & DOCKER

### 7.1 Dockerfile Chuẩn Đa Tầng (Multi-Stage Build)
Áp dụng cho từng Remote MFE hoặc Host Shell:

```dockerfile
# Stage 1: Build bằng Rsbuild Rust engine siêu tốc
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
ARG APP_NAME=mfe-crm
RUN npx rsbuild build --config apps/${APP_NAME}/rsbuild.config.ts

# Stage 2: Serve tĩnh bằng NGINX Alpine với CORS headers
FROM nginx:1.27-alpine
ARG APP_NAME=mfe-crm
COPY --from=builder /app/dist/apps/${APP_NAME} /usr/share/nginx/html

COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        # Cho phép Host Shell nạp script remoteEntry từ xa
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS' always;
    }

    # Tuyệt đối không cache manifest và remoteEntry để cập nhật tức thì
    location ~* (remoteEntry\.mjs|mf-manifest\.json)$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Access-Control-Allow-Origin * always;
    }
}
EOF

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

# 8. BẢNG CHECKLIST NGHIỆM THU (DEFINITION OF DONE)

Khi hoàn thành di chuyển hoặc thiết lập mới, bắt buộc vượt qua 6 tiêu chuẩn nghiệm thu sau:

- [ ] **1. Dev Server Khởi Động Độc Lập**: Từng app chạy `npm run start:<app>` thành công trong **< 2 giây**.
- [ ] **2. Tích Hợp Host Shell**: Chạy `npm run start:all`, truy cập Host cổng 4200 điều hướng tới Remote không bị reload trang (SPA Routing mượt mà).
- [ ] **3. Singleton Verification**: Tab Console của trình duyệt KHÔNG báo lỗi duplicate `@angular/core`, `ZoneAwarePromise` hoặc `NullInjectorError`.
- [ ] **4. Build Song Song Đa Luồng**: Chạy `npm run build` thực thi `nx run-many --parallel=true` thành công 100% các app mà không nghẽn CPU/RAM.
- [ ] **5. Nạp Assets Không Lỗi CORS/404**: Font chữ, hình ảnh, SVG của Remote khi nạp qua Host hiển thị sắc nét nhờ `assetPrefix: 'auto'`.
- [ ] **6. Tối Ưu CI/CD Pipeline**: Thời gian chạy pipeline trên GitHub Actions hoặc Jenkins runner giảm tối thiểu **40%** so với trước khi di chuyển.

---

# 9. TÀI LIỆU THAM KHẢO & LIÊN KẾT LIÊN QUAN

* 📖 **Hướng Dẫn Sử Dụng Chi Tiết**: [Huong Dan Su Dung Thu Vien Rsbuild](https://example.com/doc/huong-dan-nang-cap-su-dung-thu-vien-rsbuild-chuan-demo-crm)
* 📊 **Báo Cáo Benchmark Đo Kiểm Thực Tế CI/CD**: [Gioi Thieu Rsbuild & He Sinh Thai Rstack](https://example.com/doc/gioi-thieu-ve-thu-vien-rsbuild-he-sinh-thai-rstack-cho-angular)
* 🛠 **Repository Mẫu MFE Hoàn Chỉnh**: [https://github.com/baobao0303/project_base_rsbuild](https://github.com/baobao0303/project_base_rsbuild)
