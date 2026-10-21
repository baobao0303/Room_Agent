# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 14:26:00`
- **Work Item**: `#3871` (Parent Epic: `#3870`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Bổ sung remote customer ver261019-3 và gatewayUrl vào 4 manifest

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Bổ sung remote `'customer'` (`ver261019-3`, `lazy: true`) và chuẩn hóa `gatewayUrl` trong 4 file manifest của `apps/app-shell/public/assets/manifest/`:
- `development/module-federation.manifest.json`
- `staging/module-federation.manifest.json`
- `production/module-federation.manifest.json`
- `qa/module-federation.manifest.json`
theo mục 2 spec `docs/spec-wionpos-mfe-integration.md`.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa 4 file manifest được chỉ định. Không can thiệp vào các file khác.
- Cú pháp JSON phải hoàn toàn hợp lệ (valid syntax).
- Remote `customer` bắt buộc dùng phiên bản `ver261019-3`.

### 1.3. Giải pháp gợi ý (Suggested Path)
Trong `remotes` của mỗi file manifest, thêm entry:
```json
"customer": {
  "url": "https://team-fe.public.rke.app.dev.tmtco.org/wionpos/ver261019-3/apps/customer/mf-manifest.json",
  "lazy": true
}
```
Kiểm tra trường `gatewayUrl` trong `default` của từng môi trường:
- `development`: `"gatewayUrl": "https://gateway.dev-v3.wionpos.public.rke.app.dev.tmtco.org"`
- `staging`: `"gatewayUrl": "https://gateway.staging-v3.wionpos.public.rke.app.dev.tmtco.org"`
- `qa`: `"gatewayUrl": "https://gateway.qa-v3.wionpos.public.rke.app.dev.tmtco.org"`
- `production`: `"gatewayUrl": "https://gateway.wionpos.vn"`
