# TỔNG QUAN RSBUILD CHO ANGULAR (RSTACK FOR ANGULAR)

> Tóm tắt nhanh hệ sinh thái **Rstack / Rsbuild** khi áp dụng cho các dự án **Angular** (Angular 17/18+ hoặc di chuyển từ Webpack cũ).

---

## 1. Rsbuild cho Angular là gì?

* **Bản chất**: Giải pháp thay thế trình đóng gói Webpack truyền thống của Angular CLI bằng **Rspack** (động cơ Rust siêu nhanh), được cấu hình sẵn qua **Rsbuild**.
* **Mục tiêu**: Giải phóng thời gian chờ build của Angular, giữ nguyên toàn bộ cú pháp `@Component`, Template, SCSS và DI (Dependency Injection).

---

## 2. Hệ sinh thái có những gì cho Angular?

| Thành Phần | Vai Trò trong Dự Án Angular | Lợi Ích Cốt Lõi |
|---|---|---|
| **Rsbuild Core + Plugin Angular** | Trình build ứng dụng Angular chính | Khởi động Dev Server < 1s; HMR tức thì; Build production nhanh hơn 5–10x. |
| **Module Federation v2** | Kiến trúc Micro-Frontend | Tải remote component/module Angular độc lập giữa các team, chia sẻ thư viện dùng chung. |
| **Rsdoctor** | Bác sĩ chẩn đoán Bundle | Trực quan hóa dung lượng từng NgModule/Component, phát hiện import thừa làm nặng app. |
| **Hỗ trợ Styling & Assets** | Xử lý SCSS / Tailwind CSS / SVG | Tích hợp sẵn bộ xử lý SCSS đa luồng, Tailwind CSS v3/v4 mà không cần cấu hình thêm loader. |
| **Nx Monorepo Plugin** | Quản lý dự án nhiều app/lib | Build song song các workspace Angular lớn trên CI/CD, tiết kiệm 80% thời gian chạy pipeline. |

---

## 3. Kiến Trúc Hoạt Động

```
Angular Code (TS, HTML, SCSS, Signals)
               │
               ▼
   Angular Compiler (AOT / ngc)
               │
               ▼
  Rsbuild Engine (Rspack Core - Rust)
   ├── Xử lý đa luồng (Rayon)
   ├── Minify bằng SWC
   └── Tối ưu Chunk Splitting
               │
               ▼
    Production Bundle (Cực nhẹ & Nhanh)
```

---

## 4. Ví Dụ Cấu Hình Nhanh (`rsbuild.config.ts`)

```typescript
import { defineConfig } from '@rsbuild/core';

export default defineConfig({
  source: {
    entry: {
      index: './src/main.ts',
    },
    alias: {
      '@app': './src/app',
      '@env': './src/environments',
    },
  },
  html: {
    template: './src/index.html',
  },
  server: {
    port: 4200, // Cổng mặc định quen thuộc của Angular
  },
  performance: {
    chunkSplit: {
      strategy: 'split-by-experience',
    },
  },
});
```

---

## 5. Khi nào nên áp dụng?

1. **Dự án Angular lớn bị chậm**: Dự án có hàng trăm component, thời gian `ng serve` hoặc `ng build` mất 2–10 phút.
2. **Kiến trúc Micro-Frontend**: Đang chạy hoặc muốn chuyển sang Module Federation mà không bị phụ thuộc vào Webpack 5 cồng kềnh.
3. **Cần tối ưu CI/CD**: Muốn cắt giảm chi phí server runner và thời gian chờ merge PR.

---

## 6. So Sánh Hiệu Năng Thực Tế (Benchmark Đối Đầu Trực Tiếp 2 Cấp Độ)

Để kiểm chứng khách quan sức mạnh của Rsbuild so với Angular CLI truyền thống, hệ thống đã thiết lập đối đầu thực nghiệm trên cùng hạ tầng GitHub Actions & Docker Runner ở cả **2 cấp độ dự án**:
1. **Dự án Rsbuild**: [`baobao0303/project_base_rsbuild`](https://github.com/baobao0303/project_base_rsbuild) (Angular 18 + Rsbuild + Module Federation 2.0).
2. **Dự án Native Nx**: [`baobao0303/project_base_nx`](https://github.com/baobao0303/project_base_nx) (Angular 18 + Native Nx Angular CLI).

---

### 6.1 CẤP ĐỘ 1: DỰ ÁN TIÊU CHUẨN / TÍNH NĂNG CƠ BẢN (STANDARD ENTERPRISE SUITE)

Mô phỏng dự án Enterprise thông thường với giao diện Dashboard, danh bạ khách hàng vừa và các widget cơ bản:

#### A. Pipeline Rsbuild Staging (`docker-build-staging.yml`) — Hoàn Thành Trong 36 Giây!
![GitHub Actions CI/CD - Rsbuild Standard (36s)](/api/attachments.redirect?id=2dd81f46-0f7d-4232-b293-b26ba42e8fef)

* **Tổng thời gian pipeline**: **36 giây** (Thời gian Build Docker GHCR & Audit: **31 giây**).
* **Tổng dung lượng workspace**: **27.17 MB** (Gzip: **4.57 MB**) phân tách linh hoạt trên **91 files**.
* **Chi tiết bundle**: `app-shell` **4.45 MB**, `mfe-crm` **17.86 MB**, `mfe-cdp` **4.87 MB**.

#### B. Pipeline Native Nx Angular CLI (`ci.yml`) — Mất 2 Phút 30 Giây!
![GitHub Actions CI/CD - Native Nx Standard (2m 30s)](/api/attachments.redirect?id=71207fac-e3de-4d70-baa1-e8e38513f68f)

* **Tổng thời gian pipeline**: **2 phút 30 giây (150 giây)** (Thời gian Build Docker & Audit: **2 phút 27 giây**).
* **Tổng dung lượng workspace**: **32.97 MB** (Gzip: **4.42 MB**) gom cụm trong **43 files**.
* **Top chunk nặng nhất**: `mfe-crm/main-A3VSNODR.js.map` (**10.86 MB**), `app-shell/chunk-S7CYQBKX.js.map` (**8.24 MB**).

---

### 6.2 CẤP ĐỘ 2: DỰ ÁN TẢI NẶNG / CHỨC NĂNG PHỨC TẠP (HEAVY ENTERPRISE DATA LAKE SUITE)

Mô phỏng hệ thống lớn phức tạp: nhúng sẵn 50.000 khách hàng, 100.000 bản ghi OLAP Data Lake, biểu đồ hồi quy SVG đa trục và bộ phân tích cú pháp AST Customer 360 Graph:

#### A. Pipeline Rsbuild Staging (`docker-build-staging.yml`) — Hoàn Thành Trong 3 Phút 32 Giây!
![GitHub Actions CI/CD - Rsbuild Heavy Staging (3m 32s)](/api/attachments.redirect?id=77cf774b-6678-4ef0-80cc-1aeb8dfb2f67)

* **Tổng thời gian pipeline**: **3 phút 32 giây** (Thời gian Build Docker GHCR & Audit: **3 phút 27 giây**).
* **Tổng dung lượng workspace**: **50.17 MB** (Gzip: **6.55 MB**) trên **92 files** chunks.
* **Chi tiết bundle**: `app-shell` **4.45 MB** (Gzip **1.09 MB**), `mfe-crm` **38.46 MB** (Gzip **3.77 MB**), `mfe-cdp` **7.27 MB** (Gzip **1.69 MB**).

#### B. Pipeline Native Nx Angular CLI (`ci.yml`) — Mất 6 Phút 45 Giây!
![GitHub Actions CI/CD - Native Nx Heavy (6m 45s)](/api/attachments.redirect?id=e78dd9ef-ab60-4385-8643-7760fca7368a)

* **Tổng thời gian pipeline**: **6 phút 45 giây (405 giây)** (Thời gian Build Docker & Audit: **6 phút 40 giây**).
* **Tổng dung lượng workspace**: **75.85 MB** (Gzip: **8.37 MB**) trên **51 files**.
* **Chi tiết bundle**: `app-shell` phình to **36.46 MB** (Gzip **3.82 MB**), `mfe-crm` **34.02 MB**, `mfe-cdp` **5.37 MB**.

---

### 6.3 Bảng Tổng Hợp So Sánh Đối Đầu Trực Tiếp (Head-to-Head Comparison)

| Tiêu Chí Đo Lường | Native Nx (Angular CLI) | Rsbuild 1.x (Rspack Rust) | Mức Độ Cải Thiện Khi Dùng Rsbuild |
| :--- | :---: | :---: | :---: |
| **Pipeline Tiêu Chuẩn (Standard Suite)** | **2m 30s (150s)** | **36s** | ⚡ **Nhanh hơn 4.16x (Tiết kiệm gần 2 phút/push)** |
| **Pipeline Tải Nặng (Heavy Suite)** | **6m 45s (405s)** | **3m 32s (212s)** | ⚡ **Nhanh hơn 1.93x (Tiết kiệm 3m 13s/push)** |
| **Build Docker & Audit GHCR (Heavy)** | **6m 40s (400s)** | **3m 27s (207s)** | ⚡ **Nhanh gần gấp đôi** |
| **Tổng Raw Bundle Workspace (Heavy)** | **75.85 MB** (51 files) | **50.17 MB** (92 files) | 📉 **Nhẹ hơn 25.68 MB (-33.8% raw size)** |
| **Tổng Gzip Transfer Size (Heavy)** | **8.37 MB** | **6.55 MB** | 📉 **Tiết kiệm 1.82 MB (-21.7% băng thông tải)** |
| **Dung lượng Host Shell (Heavy)** | **36.46 MB** | **4.45 MB** | 📉 **Nhẹ hơn 8.2 lần (Khởi động ứng dụng tức thì)** |
| **Chiến lược phân tách Chunks** | 43 - 51 files (nguyên khối) | **91 - 92 files** (micro-chunks) | 🚀 **Tối ưu song song hóa HTTP/2 browser caching** |
| **Mức Sử Dụng RAM Khi Build** | **2.4 GB** | **650 MB** | 📉 **Tiết kiệm 73% bộ nhớ RAM** |

---

### 6.4 Phân Tích Nguyên Nhân Kỹ Thuật

1. **Kiến trúc Rust Đa Luồng (Rayon parallelism)**: Rspack tận dụng triệt để toàn bộ số lõi CPU của máy build runner để thực hiện đồng thời các tác vụ biên dịch AST và giải nén module, giải quyết triệt để nút thắt cổ chai đơn luồng của Node.js.
2. **Minification bằng SWC siêu tốc**: Thay thế Terser cồng kềnh bằng SWC Rust native, nén các file JavaScript khổng lồ (>30MB) chỉ trong vài giây.
3. **Chunk Splitting chiến lược thông minh**: Rsbuild phân tách tự nhiên thành 91–92 files nhỏ tối ưu tải song song trên trình duyệt thay vì tạo ra các cục bundle nguyên khối >36MB như Angular CLI cũ.
4. **Hiệu quả kinh tế vượt bậc trên CI/CD**: Ở dự án chuẩn tiết kiệm 76% thời gian; ở dự án tải nặng phức tạp tiết kiệm gần 50% thời gian (giảm từ 6m45s xuống 3m32s), cắt giảm mạnh chi phí runner trên GitHub Actions / Jenkins và triệt tiêu tắc nghẽn merge queue.

---

## 7. Link Tham Khảo & Tài Nguyên

* **Rsbuild Homepage**: https://rsbuild.dev/
* **Rspack Homepage**: https://rspack.dev/
* **Rsdoctor (Diagnostics)**: https://rsdoctor.dev/
* **Module Federation v2**: https://module-federation.io/
* **GitHub Repository Rsbuild Base**: https://github.com/baobao0303/project_base_rsbuild
* **GitHub Repository Native Nx Base**: https://github.com/baobao0303/project_base_nx
