# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 14:58:00`
- **Work Item**: `#3896`
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Thêm gatewayUrl trực tiếp vào BÊN TRONG remotes.customer.config trong 4 manifest

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Bổ sung khóa `"gatewayUrl"` vào **BÊN TRONG** `remotes.customer.config` (cùng cấp với `assetsBaseUrl` và `i18n`) của 4 file manifest:
- `apps/app-shell/public/assets/manifest/development/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/staging/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/qa/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/production/module-federation.manifest.json`
để `WIMfConfigService.createApiConfig('customer')` đọc được `gatewayUrl`.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa 4 file manifest được chỉ định.
- Cú pháp JSON phải hợp lệ 100%.
- Giá trị `gatewayUrl` chuẩn bên trong `remotes.customer.config`:
  - `development`: `"https://gateway.dev-v3.wionpos.public.rke.app.dev.tmtco.org"`
  - `staging`: `"https://gateway.staging-v3.wionpos.public.rke.app.dev.tmtco.org"`
  - `qa`: `"https://gateway.qa-v3.wionpos.public.rke.app.dev.tmtco.org"`
  - `production`: `"https://gateway.wionpos.vn"`

### 1.3. Giải pháp chi tiết (Suggested Path)
Cấu trúc chính xác bắt buộc trong mỗi file:
```json
"customer": {
  "url": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/mf-manifest.json",
  "lazy": true,
  "config": {
    "gatewayUrl": "<URL gateway theo môi trường>",
    "assetsBaseUrl": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/assets",
    "i18n": {
      "CUSTOMER": "assets/i18n/{locale}/customer.json",
      "TAGS": "assets/i18n/{locale}/tags.json",
      "PRODUCT": "assets/i18n/{locale}/product.json"
    }
  }
}
```
Sau khi sửa, chạy `python3 -m json.tool <file>` trên cả 4 file để xác minh tính hợp lệ.
