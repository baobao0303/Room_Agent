# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 14:45:00`
- **Work Item**: `#3886`
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Thêm config assetsBaseUrl và i18n cho remote customer trong 4 manifest

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Bổ sung block `config` cho remote `customer` trong 4 file manifest của `apps/app-shell/public/assets/manifest/`:
- `development/module-federation.manifest.json`
- `staging/module-federation.manifest.json`
- `qa/module-federation.manifest.json`
- `production/module-federation.manifest.json`
theo chuẩn `docs/providers/installation.md` dòng 190-197. Đảm bảo khối `default` trong cả 4 file đều có `gatewayUrl` chuẩn để remote customer gọi API.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa 4 file manifest được chỉ định. Không chạm vào file nào khác.
- Cú pháp JSON phải hợp lệ 100% (valid JSON syntax).
- Cấu trúc `config` của remote `customer` phải đầy đủ `assetsBaseUrl` và `i18n` (`CUSTOMER`, `TAGS`, `PRODUCT`).
- Giữ nguyên `lazy: true` và URL `ver261019-3` của remote `customer`.

### 1.3. Giải pháp gợi ý chi tiết (Suggested Path)
Trong mỗi file manifest, cập nhật entry `customer` dưới `remotes`:
```json
"customer": {
  "url": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/mf-manifest.json",
  "lazy": true,
  "config": {
    "assetsBaseUrl": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/assets",
    "i18n": {
      "CUSTOMER": "assets/i18n/{locale}/customer.json",
      "TAGS": "assets/i18n/{locale}/tags.json",
      "PRODUCT": "assets/i18n/{locale}/product.json"
    }
  }
}
```
Kiểm tra khối `default` có `gatewayUrl` tương ứng:
- `development`: `"gatewayUrl": "https://gateway.dev-v3.wionpos.public.rke.app.dev.tmtco.org"`
- `staging`: `"gatewayUrl": "https://gateway.staging-v3.wionpos.public.rke.app.dev.tmtco.org"`
- `qa`: `"gatewayUrl": "https://gateway.qa-v3.wionpos.public.rke.app.dev.tmtco.org"`
- `production`: `"gatewayUrl": "https://gateway.wionpos.vn"`

Kiểm tra bằng `python3 -m json.tool <file>` trên cả 4 file để xác minh tính toàn vẹn.
