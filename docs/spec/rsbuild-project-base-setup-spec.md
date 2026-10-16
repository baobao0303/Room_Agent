# ĐẶC TẢ KỸ THUẬT: THIẾT KẾ & KHỞI TẠO PROJECT_BASE VỚI RSBUILD
## (RSBUILD ENTERPRISE PROJECT BASE SPECIFICATION)

- **Mã tài liệu**: `docs/spec/rsbuild-project-base-setup-spec.md`
- **Phiên bản**: 1.0.0
- **Phân loại**: Core Architecture / Infrastructure
- **Đối tượng áp dụng**: Lead Developer, DevOps, Frontend Architects

---

# 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)

## 1.1 Mục Tiêu
Xây dựng một khung dự án chuẩn mẫu (**Enterprise `project_base`**) sử dụng **Rsbuild** (Rspack Core) làm công cụ build chính. Khung dự án này loại bỏ hoàn toàn các điểm nghẽn về tốc độ của Webpack truyền thống, chuẩn hóa quy chuẩn code, quản lý biến môi trường, tối ưu hóa bundle sản xuất, và sẵn sàng cho việc mở rộng sang kiến trúc Micro-Frontend hoặc tích hợp vào hệ thống CI/CD tự động.

## 1.2 Các Chỉ Số Mục Tiêu (Target KPIs)
* **Thời gian khởi động Dev Server (Cold Start)**: < 500ms.
* **Thời gian phản hồi HMR (Hot Module Replacement)**: < 30ms.
* **Thời gian đóng gói Production (Cold Build)**: < 5s cho dự án cỡ vừa.
* **Mức độ phụ thuộc**: Độc lập, không phụ thuộc vào các loader Babel/Webpack cồng kềnh.
* **Độ phủ kiểm tra kiểu (Type Safety)**: 100% TypeScript Strict Mode.

---

# 2. CẤU TRÚC THƯ MỤC CHUẨN (DIRECTORY STRUCTURE)

Khung thư mục được tổ chức theo cấu trúc module hóa phân tầng:

```text
project_base/
├── .env                          # Biến môi trường chung
├── .env.development              # Biến môi trường dev
├── .env.production               # Biến môi trường production
├── .gitignore                    # Git ignore file
├── .prettierrc                   # Định dạng mã nguồn chuẩn
├── .prettierignore
├── eslint.config.mjs             # Cấu hình ESLint 9 Flat Config
├── package.json                  # Khai báo dependencies & scripts
├── postcss.config.mjs            # Cấu hình PostCSS & Autoprefixer
├── rsbuild.config.ts             # TRỌNG TÂM: Cấu hình Rsbuild & Rspack engine
├── tailwind.config.ts            # Cấu hình Tailwind CSS tokens
├── tsconfig.json                 # Base TypeScript configuration
├── tsconfig.app.json             # App TypeScript configuration
├── public/                       # Tài nguyên tĩnh không qua đóng gói
│   ├── favicon.ico
│   ├── robots.txt
│   └── site.webmanifest
└── src/                          # Mã nguồn ứng dụng
    ├── env.d.ts                  # Type definitions cho PUBLIC_* env vars
    ├── index.html                # HTML template gốc
    ├── main.ts (hoặc main.tsx)   # Điểm khởi chạy ứng dụng (Entry point)
    ├── app/                      # Thành phần ứng dụng lõi
    │   ├── app.component.ts      # Component gốc
    │   └── app.routes.ts         # Khai báo routing
    ├── assets/                   # Hình ảnh, fonts, icons nội bộ
    │   ├── icons/
    │   └── images/
    ├── core/                     # Hạ tầng dùng chung không phụ thuộc UI
    │   ├── api/                  # HTTP Client, API Interceptors
    │   ├── auth/                 # Guards, Auth token storage
    │   └── constants/            # Global constants
    ├── shared/                   # UI components dùng lại, pipes, directives
    │   ├── components/
    │   └── utils/
    └── styles/                   # Global CSS / SCSS tokens
        ├── main.scss
        └── tailwind.css
```

---

# 3. DANH MỤC GÓI PHỤ THUỘC (DEPENDENCY MATRIX)

### 3.1 Dependencies (Runtime)
Tùy thuộc vào Framework mục tiêu (Angular / React / Vue / Vanilla):
```json
{
  "dependencies": {
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4"
  }
}
```

### 3.2 DevDependencies (Tooling & Build System)
```json
{
  "devDependencies": {
    "@rsbuild/core": "^1.1.0",
    "@rsbuild/plugin-sass": "^1.0.3",
    "@rsbuild/plugin-type-check": "^1.0.1",
    "@rsbuild/plugin-svgr": "^1.0.1",
    "@rsdoctor/rspack-plugin": "^0.4.0",
    "typescript": "^5.6.3",
    "tailwindcss": "^3.4.14",
    "postcss": "^8.4.47",
    "autoprefixer": "^10.4.20",
    "sass": "^1.80.3",
    "eslint": "^9.13.0",
    "prettier": "^3.3.3"
  }
}
```

---

# 4. CHI TIẾT CẤU HÌNH TỪNG FILE CỐT LÕI

## 4.1 `rsbuild.config.ts` (Trái Tim Hệ Thống)

File cấu hình được tối ưu hóa toàn diện cho môi trường Dev và Production:

```typescript
import { defineConfig, loadEnv } from '@rsbuild/core';
import { pluginSass } from '@rsbuild/plugin-sass';
import { pluginTypeCheck } from '@rsbuild/plugin-type-check';
import { pluginSvgr } from '@rsbuild/plugin-svgr';
import { RsdoctorRspackPlugin } from '@rsdoctor/rspack-plugin';

// Tự động load biến môi trường tương ứng
const { publicVars } = loadEnv({ prefixes: ['PUBLIC_'] });

export default defineConfig({
  plugins: [
    pluginSass(),
    pluginSvgr(),
    // Chỉ kích hoạt type-check khi chạy build hoặc biến TYPE_CHECK=true
    process.env.TYPE_CHECK === 'true' && pluginTypeCheck({
      forkTsCheckerOptions: {
        typescript: {
          configFile: './tsconfig.app.json',
        },
      },
    }),
  ].filter(Boolean),

  source: {
    entry: {
      index: './src/main.ts',
    },
    alias: {
      '@': './src',
      '@core': './src/core',
      '@shared': './src/shared',
      '@assets': './src/assets',
      '@styles': './src/styles',
    },
    define: publicVars,
  },

  html: {
    template: './src/index.html',
    title: 'Enterprise Project Base',
    favicon: './public/favicon.ico',
    meta: {
      viewport: 'width=device-width, initial-scale=1, shrink-to-fit=no',
      'theme-color': '#0f172a',
      description: 'Production-ready Web Base powered by Rsbuild',
    },
    inject: 'body',
  },

  server: {
    port: 3000,
    host: '0.0.0.0',
    open: false,
    strictPort: false,
    proxy: {
      '/api': {
        target: process.env.PUBLIC_API_BACKEND_URL || 'http://localhost:8080',
        changeOrigin: true,
        pathRewrite: { '^/api': '/api/v1' },
        secure: false,
      },
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },

  output: {
    assetPrefix: '/',
    distPath: {
      root: 'dist',
      html: '',
      js: 'static/js',
      css: 'static/css',
      image: 'static/media',
      font: 'static/fonts',
    },
    cleanDistPath: true,
    filename: {
      js: '[name].[contenthash:8].js',
      css: '[name].[contenthash:8].css',
      image: '[name].[contenthash:8][ext]',
    },
    dataUriLimit: {
      image: 4096, // Dưới 4KB tự động inline base64
      font: 8192,  // Dưới 8KB inline base64 để tránh FOUT
    },
    legalComments: 'none',
  },

  performance: {
    chunkSplit: {
      strategy: 'split-by-experience', // Phân chia chunk thông minh của ByteDance
      customSplitting: {
        vendor: {
          test: /node_modules/,
          name: 'vendor',
          priority: 10,
        },
      },
    },
    removeConsole: process.env.NODE_ENV === 'production' ? ['log', 'info'] : false,
    bundleAnalyze: process.env.ANALYZE === 'true' ? {} : undefined,
  },

  tools: {
    rspack: (config, { isProd }) => {
      // Chẩn đoán bundle chuyên sâu với Rsdoctor khi RSDOCTOR=true
      if (process.env.RSDOCTOR === 'true') {
        config.plugins = config.plugins || [];
        config.plugins.push(new RsdoctorRspackPlugin());
      }
      return config;
    },
  },
});
```

---

## 4.2 `package.json` (Scripts Tiêu Chuẩn)

```json
{
  "name": "enterprise-project-base",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "rsbuild dev",
    "dev:open": "rsbuild dev --open",
    "build": "rsbuild build",
    "build:check": "TYPE_CHECK=true rsbuild build",
    "preview": "rsbuild preview",
    "inspect": "rsbuild inspect",
    "doctor": "RSDOCTOR=true rsbuild build",
    "analyze": "ANALYZE=true rsbuild build",
    "type-check": "tsc --project tsconfig.app.json --noEmit",
    "lint": "eslint . --cache",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,json,scss,css,html}\""
  }
}
```

---

## 4.3 Cấu Hình TypeScript

### `tsconfig.json` (Root Config)
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "noEmit": true,
    "resolveJsonModule": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@core/*": ["src/core/*"],
      "@shared/*": ["src/shared/*"],
      "@assets/*": ["src/assets/*"],
      "@styles/*": ["src/styles/*"]
    }
  },
  "include": ["src/**/*", "rsbuild.config.ts"]
}
```

### `src/env.d.ts` (Kiểu Cho Biến Môi Trường)
```typescript
/// <reference types="@rsbuild/core/types" />

interface ImportMetaEnv {
  readonly PUBLIC_APP_TITLE: string;
  readonly PUBLIC_API_BACKEND_URL: string;
  readonly PUBLIC_ENABLE_ANALYTICS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

---

## 4.4 Cấu Hình Styling (Tailwind + SCSS + PostCSS)

### `postcss.config.mjs`
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### `tailwind.config.ts`
```typescript
import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{html,ts,tsx,js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
```

### `src/styles/main.scss`
```scss
@import './tailwind.css';

:root {
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-family-base);
  background-color: #f8fafc;
  color: #0f172a;
}
```

---

# 5. CHIẾN LƯỢC QUẢN LÝ BIẾN MÔI TRƯỜNG (ENV STRATEGY)

Áp dụng quy tắc bảo mật và nạp biến phân cấp:
1. `.env`: Giá trị mặc định chung cho toàn bộ môi trường.
2. `.env.development`: Dành cho máy dev (`rsbuild dev`).
3. `.env.production`: Dành cho production build (`rsbuild build`).

### Mẫu `.env`:
```ini
PUBLIC_APP_TITLE="WiCX Enterprise Platform"
PUBLIC_API_BACKEND_URL="https://api.crm.internal"
PUBLIC_ENABLE_ANALYTICS=false
```

> **Nguyên tắc bảo mật**: Chỉ những biến có tiền tố `PUBLIC_` mới được nhúng vào client bundle. Bất kỳ biến nào không có tiền tố này (như `DATABASE_PASSWORD`, `SECRET_KEY`) sẽ bị chặn, không bao giờ lộ ra trình duyệt.

---

# 6. ĐÓNG GÓI DOCKER PRODUCTION (MULTI-STAGE DOCKERFILE)

Quy trình build Docker tối ưu sử dụng Node LTS và NGINX Alpine siêu nhẹ:

```dockerfile
# Stage 1: Build mã nguồn bằng Rsbuild
FROM node:20-alpine AS builder
WORKDIR /app

# Cài đặt dependencies và tận dụng cache Docker layer
COPY package.json package-lock.json ./
RUN npm ci

# Copy toàn bộ mã nguồn và build
COPY . .
RUN npm run build

# Stage 2: Serve tĩnh bằng NGINX
FROM nginx:1.27-alpine AS runner
WORKDIR /usr/share/nginx/html

# Xóa trang html mặc định
RUN rm -rf ./*

# Copy artifacts từ Stage builder
COPY --from=builder /app/dist .

# Copy cấu hình NGINX hỗ trợ SPA Routing
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Cache tài nguyên tĩnh tối đa 1 năm (nhờ contenthash)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /usr/share/nginx/html;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

# 7. QUY TRÌNH SETUP TỪ ĐẦU (STEP-BY-STEP IMPLEMENTATION)

Dành cho Developer thực thi trực tiếp trên terminal:

```bash
# Bước 1: Khởi tạo thư mục và package.json
mkdir enterprise-project-base && cd enterprise-project-base
npm init -y

# Bước 2: Cài đặt Rsbuild và core plugins
npm install -D @rsbuild/core @rsbuild/plugin-sass @rsbuild/plugin-type-check @rsbuild/plugin-svgr @rsdoctor/rspack-plugin

# Bước 3: Cài đặt TypeScript, Styling và Linting
npm install -D typescript tailwindcss postcss autoprefixer sass eslint prettier

# Bước 4: Tạo cấu trúc thư mục
mkdir -p public src/{app,assets,core,shared,styles}

# Bước 5: Khởi tạo các file cấu hình
touch rsbuild.config.ts tsconfig.json tsconfig.app.json postcss.config.mjs tailwind.config.ts
touch .env .env.development .env.production
touch src/index.html src/main.ts src/env.d.ts src/styles/{main.scss,tailwind.css}

# Bước 6: Khởi chạy Dev Server
npm run dev
```

---

# 8. KẾT LUẬN & ĐÁNH GIÁ CHẤT LƯỢNG (DEFINITION OF DONE)

Một `project_base` Rsbuild đạt chuẩn nghiệm thu khi:
1. `npm run dev` khởi động và mở cổng trong vòng chưa đầy 1 giây.
2. `npm run build` xuất ra thư mục `dist/` đầy đủ hash filename cho JS/CSS/Media.
3. Không có cảnh báo Type Warning khi chạy `npm run type-check`.
4. Cơ chế load biến môi trường `import.meta.env.PUBLIC_*` hoạt động chính xác theo từng môi trường.
5. Lệnh `npm run doctor` hiển thị đầy đủ dashboard Rsdoctor phân tích trực quan bundle.
