# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 14:54:00`
- **Work Item**: `#3891` (Bug)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Bổ sung gatewayUrl vào remotes.customer.config trong 4 file manifest

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Bổ sung trường `"gatewayUrl"` trực tiếp vào trong `remotes.customer.config` của 4 file manifest:
- `apps/app-shell/public/assets/manifest/development/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/staging/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/qa/module-federation.manifest.json`
- `apps/app-shell/public/assets/manifest/production/module-federation.manifest.json`
để `WIMfConfigService.createApiConfig('customer')` nạp đúng gateway API tuyệt đối thay vì gửi relative URL về localhost:4200 gây lỗi 404.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa 4 file manifest được chỉ định. Không chạm vào các file khác.
- Cú pháp JSON phải hợp lệ 100%.
- Giá trị `gatewayUrl` tương ứng theo từng môi trường:
  - `development`: `"https://gateway.dev-v3.wionpos.public.rke.app.dev.tmtco.org"`
  - `staging`: `"https://gateway.staging-v3.wionpos.public.rke.app.dev.tmtco.org"`
  - `qa`: `"https://gateway.qa-v3.wionpos.public.rke.app.dev.tmtco.org"`
  - `production`: `"https://gateway.wionpos.vn"`

### 1.3. Giải pháp gợi ý chi tiết (Suggested Path)
Trong mỗi file manifest, cập nhật khối `remotes.customer.config`:
```json
"customer": {
  "url": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/mf-manifest.json",
  "lazy": true,
  "config": {
    "gatewayUrl": "<URL theo môi trường>",
    "assetsBaseUrl": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/assets",
    "i18n": {
      "CUSTOMER": "assets/i18n/{locale}/customer.json",
      "TAGS": "assets/i18n/{locale}/tags.json",
      "PRODUCT": "assets/i18n/{locale}/product.json"
    }
  }
}
```
Kiểm tra cú pháp JSON sau khi sửa bằng `python3 -m json.tool <file>`.
