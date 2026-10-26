---
name: migration-i18n
description: Migrate i18n (đa ngôn ngữ) cho Angular 18 Micro-Frontend (Nx Monorepo, Module Federation, Rsbuild, @demo/i18n). Dùng khi cần thêm/refactor translation keys, chuẩn hóa JSON dictionary, hoặc audit lỗi missing key trên Demo-CRM/Demo-POS. Không dùng cho các task Angular không liên quan đến i18n.
metadata:
  short-description: i18n migration cho Demo-CRM/Demo-POS MFE
---

# i18n Migration — Demo-CRM / Demo-POS MFE

Workflow chuẩn di chuyển đa ngôn ngữ cho hệ sinh thái **Demo-CRM / Demo-POS** (Angular 18, Nx Monorepo, Module Federation, Rsbuild).

Chi tiết đầy đủ trong `references/workflow.md`. Đọc file đó trước khi bắt tay vào bất kỳ module nào.

## Nguyên tắc cốt lõi (không được phá vỡ)

1. **Single Root Namespace** — Mỗi module chỉ có đúng 1 Root Key viết hoa ở cấp root JSON (`CUSTOMER`, `PRODUCT`, `TAGS`...). Cấm key trôi nổi như `ACTIONS`, `TABLE`, `COMMON` ở cấp root.
2. **Đồng bộ song ngữ 100%** — `vi` và `en` phải đối xứng hoàn toàn, không được lệch key.
3. **Đồng bộ 2 vị trí** — JSON phải tồn tại ở cả `apps/<module>/src/assets/i18n/` và `libs/<module>/ui/public/i18n/`.
4. **Bảo toàn mustache** — Không được xóa/sửa `{{name}}`, `{{count}}`, `{{from}}`, `{{to}}`.

## Quy trình tóm tắt (4 giai đoạn)

1. **Scope Discovery** — Đọc spec, quét routes, liệt kê components/modals/drawers.
2. **Dictionary Namespacing** — Tạo/chuẩn hóa JSON với single root key, kiểm tra bằng node script.
3. **Refactor Code** — Cập nhật template HTML và TypeScript (pipe, service, modal).
4. **Audit & QA** — Kiểm tra build, network 200, console warnings, DOM raw-key scan, screenshot.

## Bảng port chuẩn (tra nhanh)

| Module | Port | Feature Key |
|---|---|---|
| admin (Host) | 4200 | `SHELL` |
| account | 4201 | `ACCOUNT` |
| product | 4202 | `PRODUCT` |
| customer | 4203 | `CUSTOMER` |
| shop | 4204 | `SHOP` |
| supplier | 4205 | `SUPPLIER` |
| dashboard | 4206 | `DASHBOARD` |
| cashbook | 4208 | `CASHBOOK` |
| tags | 4210 | `TAGS` |
| ordering | 4211 | `ORDERING` |
| setting | 4212 | `SETTING` / `UMAC` |
| inventory | 4213 | `INVENTORY` |
| report | 4214 | `REPORT` |
| price-list | 4217 | `PRICE_LIST` |
| billing | 4218 | `BILLING` |
| integration | 4219 | `INTEGRATION` |
