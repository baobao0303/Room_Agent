---
name: rea-reverse-engineering
description: "Use when reverse engineering web bundles, MFEs, APKs, Electron, or binaries with REA."
version: 1.0.0
roles: [lead, peer, qc, supervisor]
---

# REA Reverse Engineering Skill (Kỹ Năng Dịch Ngược Đa Nền Tảng Với REA)

Bộ kỹ năng thực chiến sử dụng **REA (`rea-agents@6.5.0`)** — công cụ dịch ngược hơn 300,000 GitHub stars — dành riêng cho kỹ sư frontend, mobile và lead architect trong mô hình SLPC khi:
1. Tích hợp Remote Micro-Frontend (MFE) từ CDN/3rd party mà không có mã nguồn thô (chỉ có link CDN `remoteEntry.js`, `mf-manifest.json`).
2. Khôi phục mã nguồn, routes, DTOs, API endpoints từ gói bundle minified.
3. Dịch ngược ứng dụng Electron, trích xuất IPC events, ASAR packages.
4. Dịch ngược file Android APK/AAB để lấy schema API hoặc đối chiếu tính năng.

---

## 1. Phương Thức Gọi REA Trong Môi Trường

Hệ thống hỗ trợ 2 cơ chế thực thi:
- **CLI Native (Khuyên dùng trong terminal/scripts)**:
  `rea <command> [options]` (Đã cài tại `~/.local/bin/rea`)
  *Fallback*: `npx -y rea-agents@6.5.0 <command>`
- **MCP Tools (Trong Agent Sessions)**:
  Hermes đã nạp sẵn **209 công cụ** tiền tố `mcp__rea__*` (`mcp__rea__analyze_web_bundle`, `mcp__rea__recover_javascript_sources`...).

---

## 2. Kịch Bản Thực Chiến 1: Dịch Ngược Remote MFE & Web Bundle

Áp dụng khi cần tích hợp Remote MFE (VD: Remote POS Customer, Zoho widget, payment SDK) khi chỉ có link CDN:

### A. Phân tích toàn cảnh Web Bundle & Metadata
```bash
# Phân tích bundle từ URL hoặc file bundle local
rea analyze-web-bundle <url_hoặc_file_js> --json

# Ví dụ phân tích manifest remote:
rea analyze-web-bundle "https://cdn.example.com/demo-pos/ver261019-3/apps/customer/mf-manifest.json" --json
```
- **Kết quả trả về**: Danh sách chunk, exports, dependencies, routes và các endpoint API backend được nhúng trong bundle.

### B. Khôi phục mã nguồn JavaScript (Source Recovery)
Khi bundle có kèm hoặc giấu Source Map trong comment `//# sourceMappingURL=`:
```bash
# Trích xuất toàn bộ file script và source map về thư mục local
rea export-web-scripts --url "<url_trang_web>" --out-dir "<thu_muc_dich>"

# Khôi phục file nguồn có thể đọc được (readable code)
rea recover-javascript-sources "<file_bundle_hoac_map>" --json
```

### C. Đối chiếu Mã nguồn Dev với Bundle Release
Phát hiện mã nguồn hiện tại trong repo có khớp 100% với bundle đang chạy trên staging/production không:
```bash
rea compare-source-to-bundle \
  --source-dir "projects/demo-crm-fe/apps/app-shell" \
  --bundle-file "dist/apps/app-shell/main.js" \
  --json
```

---

## 3. Kịch Bản Thực Chiến 2: Dịch Ngược Electron & Node.js App

Áp dụng khi phân tích ứng dụng Desktop (Aevum, Slack, VSCode, Desktop Agent):

```bash
# 1. Phân tích cấu trúc ứng dụng Electron / ASAR
rea analyze-javascript-application "/path/to/app" --json

# 2. Kiểm tra fuses bảo mật của Electron (chống inject script / devtools)
rea inspect-electron-fuses "/path/to/electron_binary" --json

# 3. Trích xuất file ASAR an toàn
rea extract-artifact "app.asar" --out-dir "extracted_app/"
```

---

## 4. Kịch Bản Thực Chiến 3: Dịch Ngược Android APK & Mobile POS

Áp dụng khi cần kiểm tra API Contract hoặc logic tính toán của app Android Mobile POS:

```bash
# 1. Bóc tách manifest, permissions, activities mà không cần chạy app
rea inspect-android-package "app-release.apk" --json

# 2. Giải mã tài nguyên XML và strings qua apktool
rea decode-android-resources "app-release.apk" --out-dir "decompiled_res/"

# 3. Tìm kiếm class và decompile hàm cụ thể
rea search-android-classes "app-release.apk" --query "Customer" --json
rea inspect-android-method "app-release.apk" --class-name "com.example.pos.CustomerService" --method-name "getShopUsers"
```

---

## 5. Kịch Bản Thực Chiến 4: Native Binary, Go, Rust & Crash Dumps

```bash
# 1. Trích xuất danh sách dependencies Rust từ binary ELF/PE
rea inspect-rust-binary "/path/to/binary" --json

# 2. Kiểm tra thông tin build và modules Go
rea inspect-go-binary "/path/to/go_binary" --json

# 3. Xem layout ELF sections/segments offline (thay thế readelf/objdump)
rea inspect-binary-layout "/path/to/binary" --json
```

---

## 6. Quy Trình Phối Hợp SLPC Khi Dùng REA

1. **Lead Dev**:
   - Khi nhận yêu cầu tích hợp bên thứ 3 hoặc remote MFE thiếu spec: Chạy `rea analyze-web-bundle` để bóc tách API contract và DTOs thực tế trước khi viết spec kiến trúc.
2. **Peer Dev**:
   - Dùng `rea recover-javascript-sources` hoặc `rea extract-artifact` để lấy mock data mẫu và kiểm chứng cấu trúc response.
3. **QC**:
   - Dùng `rea compare-source-to-bundle` hoặc `rea compare-javascript-export-shapes` để xác minh bundle build cuối cùng không làm rơi rụng export hay gãy contract.

---

## 7. Nguyên Tắc An Toàn (Security & Zero-Leak Rules)
- **Cấm đưa dữ liệu nhạy cảm**: Không phân tích các file chứa credentials thật hoặc token production lên môi trường public.
- **Thư mục cách ly (Sandbox)**: Luôn trỏ output của lệnh export/extract vào thư mục tạm `scratch/` hoặc `bmad/rooms/tasks/<id>/artifacts/`, tuyệt đối không xuất vào source tree để tránh commit nhầm vào Git.
