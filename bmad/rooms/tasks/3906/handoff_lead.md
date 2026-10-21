# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 15:15:00`
- **Work Item**: `#3906`
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Gỡ bỏ gatewayUrl khỏi khối default trong 4 manifest

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Xóa bỏ hoàn toàn trường `"gatewayUrl"` khỏi khối `default` trong 4 file manifest:
- `apps/app-shell/public/assets/manifest/development/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/staging/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/qa/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/production/module-federation.manifest.json`
Khôi phục khối `default` về nguyên bản của CRM (`environment`, `production`, `locale`, `apiBaseUrl`, `redirectURI`, `linkRegister`).

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa 4 file manifest được chỉ định. Không chạm vào file khác.
- Cú pháp JSON phải hợp lệ 100%.
- Giữ nguyên toàn bộ cấu hình `remotes` (bao gồm remote `customer` và `setting`).

### 1.3. Giải pháp chi tiết (Suggested Path)
Trong mỗi file manifest, xóa dòng `"gatewayUrl": ...` khỏi block `default`.
Ví dụ trong `development/module-federation.manifest.json`:
```json
  "default": {
    "environment": "DEV",
    "production": false,
    "locale": "vi",
    "apiBaseUrl": "https://wicx-crm.public.rke.app.dev.tmtco.org",
    "redirectURI": "http://localhost:4200/#/account/login",
    "linkRegister": "https://account.public.rke.app.dev.tmtco.org/web/#/o/auth/register"
  },
```
Kiểm tra cú pháp JSON bằng `python3 -m json.tool <file>` trên cả 4 file.
