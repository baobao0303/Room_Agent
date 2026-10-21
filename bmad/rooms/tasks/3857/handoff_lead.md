# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 3

- **Thời gian**: `2026-10-21 14:10:00`
- **Work Item**: `#3857` (Parent Epic: `#3854`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 3` (`peer3`)
- **Nội dung**: Sửa apps/app-shell/public/assets/manifest/*/module-federation.manifest.json bổ sung gatewayUrl

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)

### 1.1. Mục tiêu tối hậu (Ultimate Goal)
Bổ sung và chuẩn hóa `gatewayUrl` trong 4 file manifest của `apps/app-shell/public/assets/manifest/`:
- `development/module-federation.manifest.json`
- `staging/module-federation.manifest.json`
- `production/module-federation.manifest.json`
- `qa/module-federation.manifest.json`
theo mục 6 spec `docs/spec-wionpos-mfe-integration.md`.

### 1.2. Ràng buộc cứng (Hard Constraints)
- **Single-Ownership**: Chỉ sửa 4 file manifest được chỉ định.
- Giữ nguyên cấu trúc JSON hợp lệ (valid syntax).
- Giữ nguyên các trường `production`, `locale`, `apiBaseUrl`, `redirectURI`, `linkRegister` hiện có nếu cần tương thích ngược, nhưng bắt buộc có `gatewayUrl`.

### 1.3. Giải pháp gợi ý (Suggested Path)
Trong mỗi file manifest, dưới trường `default`:
- Nếu đã có `apiBaseUrl`, bổ sung `gatewayUrl` với giá trị tương ứng của gateway môi trường đó:
  - `development`: `"gatewayUrl": "https://wicx-crm.public.rke.app.dev.tmtco.org"`
  - `staging`: `"gatewayUrl": "https://gateway.staging-v3.wionpos.public.rke.app.dev.tmtco.org"` (hoặc giá trị apiBaseUrl hiện tại)
  - `production`: `"gatewayUrl": "https://gateway.wionpos.vn"` (hoặc giá trị apiBaseUrl hiện tại)
  - `qa`: `"gatewayUrl": "https://gateway.qa-v3.wionpos.public.rke.app.dev.tmtco.org"` (hoặc giá trị apiBaseUrl hiện tại)
- Kiểm tra `jq` hoặc `json.loads` đảm bảo cú pháp JSON chuẩn 100%.
