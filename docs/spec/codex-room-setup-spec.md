# Spec: Kiến trúc & Cơ chế vận hành `codex-room-setup` (Core-3 Paseo Room)

- **Nguồn tham chiếu**: `https://github.com/hoangnb24/codex-room-setup` (clone cục bộ tại `codex-room-setup/`)
- **Phiên bản kiến trúc**: Three-Role Codex Room (`codex-supervisor`, `codex-lead`, `codex-peer`) trên nền Paseo `v0.8.0`

---

## 1. Kiến trúc tổng thể: "Three-Role Codex Room" trên Paseo `v0.8.0`

Khác với các mô hình thử nghiệm đa hồ sơ trước đây (như 9 profile BA/Design/Dev hoặc mô hình 5 role có tách riêng `Review` và `Harness`), phiên bản chuẩn hiện tại của `codex-room-setup` đã thực hiện **Core-3 hard-cut**: chuẩn hóa về đúng **3 ghế (3-seat room)** chạy trên bản phát hành ổn định chính thức của **Paseo `v0.8.0`**.

```text
Human (Operator)
  └── Supervisor (codex-supervisor)  ──► Quản trị danh mục, định tuyến ý định, giữ biên thông tin
        └── Lead (codex-lead)        ──► Quyền kỹ thuật, chia việc, kiểm chứng & ACCEPT/REJECT
              └── Peer (codex-peer)  ──► Thực thi 1 đầu việc độc lập (code hoặc review chỉ-đọc)
```

### 1.1. Pin phiên bản Paseo bất biến (`paseo/source.toml`)
- **Upstream repository**: `https://github.com/getpaseo/paseo.git`
- **Release tag**: `v0.8.0`
- **Branch nội bộ**: `codex-room-stable`
- **Verified Commit SHA**: `b8e24677e12b226c7c38c1c3a40649daa9f1152f`
- **Target cài đặt mặc định**: `~/projects/supervisors/paseo` (CLI symlink tại `~/.local/bin/paseo` trỏ tới `packages/cli/bin/paseo`).
- **Cơ chế khóa toàn vẹn (`scripts/install-paseo`)**:
  - Đối chiếu trực tiếp `refs/tags/v0.8.0` từ remote với `verified_commit` (40 ký tự hex).
  - Kiểm tra SHA-256 của `package-lock.json` trước và sau khi chạy `npm ci`; nếu `npm ci` làm thay đổi `package-lock.json` hoặc sinh thêm Git hook ngoài `lefthook`, quá trình cài đặt lập tức báo lỗi và khôi phục file gốc.
  - Biên dịch bằng `npm run build:server:clean` và kiểm tra sự tồn tại thực tế (không phải symlink) của `packages/cli/dist/index.js` và `packages/server/dist/scripts/supervisor-entrypoint.js`.

---

## 2. Cơ chế cô lập Runtime & Khóa Native Subagent

Mục tiêu cốt lõi của tầng runtime là: **tận dụng tài nguyên xác thực/kỹ năng từ `~/.codex` của người dùng nhưng không bao giờ sửa đổi `~/.codex`**, đồng thời ngăn chặn Codex tự ý đẻ subagent nội bộ nằm ngoài sự kiểm soát của Paseo.

### 2.1. Luồng khởi chạy (`Paseo -> codex-room -> codex-room-sync -> codex`)
1. **Paseo Daemon** đọc `~/.paseo/config.json` (sinh từ `home/.paseo/config.json.template`) và gọi binary tương ứng cho từng provider:
   - `codex-supervisor` $\rightarrow$ `~/.local/bin/codex-room supervisor`
   - `codex-lead` $\rightarrow$ `~/.local/bin/codex-room lead`
   - `codex-peer` $\rightarrow$ `~/.local/bin/codex-room peer`
2. **Launcher (`home/.local/bin/codex-room`)**:
   - Chỉ chấp nhận đúng 3 tham số `supervisor | lead | peer` (từ chối mọi role cũ như `review` hoặc `harness`).
   - Gọi `~/.local/bin/codex-room-sync <role>` để tái tạo cấu hình mới nhất trước mỗi lần khởi chạy.
   - Đặt `export CODEX_HOME="$HOME/.codex-runtime/<role>"` và `exec codex "$@"`.

### 2.2. Quy trình đồng bộ và cô lập (`home/.local/bin/codex-room-sync`)
Tại mỗi thư mục `~/.codex-runtime/<role>` (permission `0700`):
- **Trộn cấu hình TOML (`config.toml`, permission `0600`)**:
  - Đọc `~/.codex/config.toml` của người dùng làm cấu hình cơ sở (giữ nguyên MCP servers, model providers, `projects.*` trust entries...).
  - Ghi đè 6 khóa scalar từ `~/.config/codex-room/overlays/<role>.config.toml`:
    - `model`
    - `model_instructions_file` (trỏ tuyệt đối vào `~/.codex-runtime/<role>/model-instructions.md`)
    - `model_reasoning_effort`
    - `sandbox_mode`
    - `approval_policy`
    - `approvals_reviewer`
  - Ghi đè `developer_instructions` bằng nội dung hướng dẫn chuyên biệt của từng role từ overlay.
- **Khóa chặt Native Multi-Agent của Codex (2 lớp)**:
  1. **Lớp Policy trong `config.toml`**: Ép cứng `[agents].enabled = false`, `[features].multi_agent = false`, và `[features].multi_agent_v2 = false`.
  2. **Lớp Model Catalog (`model-catalog.no-native-agents.json`)**: Chạy `codex debug models`, dùng `jq` ép `.models[].multi_agent_version = null`, ghi ra `~/.codex-runtime/<role>/model-catalog.no-native-agents.json` và gán vào khóa `model_catalog_json` trong `config.toml`. Điều này đảm bảo bản thân model không nhận diện được khả năng gọi native subagent của Codex CLI.
- **Symlink tài nguyên dùng chung & cô lập trạng thái**:
  - Tạo symlink chỉ-đọc trỏ về `~/.codex/` cho: `auth.json`, `AGENTS.md`, `skills`, `plugins` (và `hooks.json` nếu tồn tại).
  - Tạo symlink `model-instructions.md` trỏ về `~/.config/codex-room/model-instructions.md`.
  - Toàn bộ trạng thái động (`sessions/`, `log/`, `sqlite/`, `state_*.sqlite`, `models_cache.json`, `tmp/`) nằm riêng trong từng `~/.codex-runtime/<role>/`, không bao giờ đụng độ giữa Supervisor, Lead và Peer.

---

## 3. Phân quyền Paseo MCP Tools & Giao thức 3 Role

### 3.1. Biên giới công cụ Paseo (`home/.paseo/config.json.template` & `scripts/lib/paseo-tools.jq`)
- Trong `~/.paseo/config.json`:
  - `daemon.mcp.enabled = true`
  - `daemon.mcp.injectIntoAgents = true`
  - Không sử dụng `injectIntoProviders` cấp toàn cục mà định nghĩa tường minh `paseoTools.enabled` trên **từng provider**:
    - `codex-supervisor`: `paseoTools.enabled = true`
    - `codex-lead`: `paseoTools.enabled = true`
    - `codex-peer`: `paseoTools.enabled = false`
    - Tất cả các provider mặc định khác (`claude`, `codex`, `copilot`, `opencode`, `pi`, `omp`, `hermes`, `grok`): `paseoTools.enabled = false`.
- **Hệ quả kiến trúc**: `codex-peer` hoàn toàn mù với hệ thống điều phối Paseo (không có quyền liệt kê agent, không thể tạo agent mới, không thể gửi tin nhắn ngang hàng). Peer chỉ nhận đề bài tại lúc khởi tạo/nhắn tin từ Lead và trả kết quả khi kết thúc lượt chạy.

### 3.2. Đặc tả chi tiết 3 Role (`WORKSPACE_PROTOCOL.md` & `overlays/*.config.toml`)

| Thuộc tính | Supervisor (`codex-supervisor`) | Lead (`codex-lead`) | Peer (`codex-peer`) |
| :--- | :--- | :--- | :--- |
| **File Overlay** | `overlays/supervisor.config.toml` | `overlays/lead.config.toml` | `overlays/peer.config.toml` |
| **Model mặc định** | `gpt-6.1-sol` (fallback: `gpt-6-astra`) | `gpt-6-astra` (fallback: `gpt-6.1-sol`) | `gpt-6.1-sol` (fallback: `gpt-6-astra`) |
| **Reasoning Effort** | `medium` (`low` / `medium` / `high` / `xhigh`) | `medium` (`low` / `medium` / `high` / `xhigh`) | `medium` (`low` / `medium` / `high` / `xhigh`) |
| **Sandbox & Approval** | `danger-full-access`, `never` | `danger-full-access`, `never` | `danger-full-access`, `never` |
| **Paseo MCP Tools** | Có (`enabled: true`) | Có (`enabled: true`) | **Không** (`enabled: false`) |
| **Vai trò cốt lõi** | Quản trị danh mục (portfolio), định tuyến ý định từ Human xuống Lead, giữ biên thông tin. | Quyền kỹ thuật (technical authority), thiết kế, phân rã phụ thuộc, kiểm chứng và nghiệm thu. | Thực thi 1 đầu việc có biên rõ ràng (writable implementation hoặc read-only review). |

#### Quy tắc vận hành bắt buộc theo Role:
1. **Supervisor**:
   - **Biên thông tin (Information Boundary)**: Khi chuyển yêu cầu từ Human sang Lead, Supervisor chỉ truyền đạt mục tiêu, phạm vi, ràng buộc và tiêu chí nghiệm thu; **tuyệt đối không** tiết lộ nội dung trò chuyện riêng với Human hoặc dùng cụm từ *"Human vừa bảo trong phòng..."*.
   - **Ranh giới hành động**: Cấm sửa code dự án, cấm chạy lệnh build/test dự án để tự nghiệm thu, cấm ra phán quyết `ACCEPT`/`REJECT` cho sản phẩm của Peer, và cấm liên hệ trực tiếp với Peer.
   - **Theo dõi tiến độ (Event-driven + Fallback Heartbeat)**: Ưu tiên nhận sự kiện từ Paseo; duy trì đúng **1 heartbeat tự nhắc chính mình** (`create_heartbeat` với cron `*/2 * * * *`) khi có công việc đang mở để kiểm tra xem chuỗi `Lead brief -> Peer response -> Lead disposition (ACCEPT/REJECT)` có bị đứt quãng hay không. Hủy heartbeat ngay khi đóng việc.
2. **Lead**:
   - **Quy tắc Moving Write Scope**: Mỗi phạm vi ghi đang dịch chuyển (`moving write scope`) chỉ có **1 chủ sở hữu duy nhất** tại một thời điểm.
   - **Điều kiện chạy song song (Parallel Writable Peers)**: Chỉ được mở nhiều Peer có quyền ghi chạy song song khi: (a) đầu vào phụ thuộc đã được kiểm chứng và `ACCEPT`, và (b) phạm vi file/module ghi của các Peer hoàn toàn tách biệt.
   - **Giao thức giao việc (Briefing)**: Mỗi brief gửi cho Peer phải nêu rõ: mục tiêu, các tiền đề đã được `ACCEPT`, phạm vi đường dẫn được phép sửa (hoặc chế độ `read-only` kèm commit/snapshot cần review), kỳ vọng kiểm chứng và điều kiện dừng.
   - **Nghiệm thu tường minh**: Sau khi Peer trả kết quả, Lead phải kiểm chứng và phát hành phán quyết rõ ràng: `ACCEPT` hoặc `REJECT` (kèm nguyên nhân cụ thể). Trạng thái im lặng không bao giờ được coi là đã nghiệm thu.
3. **Peer**:
   - **Cơ chế phản biện (Challenge Signals)**: Nếu phát hiện đề bài của Lead có tiền đề sai, thiếu phụ thuộc hoặc vượt biên, Peer không được tự ý mở rộng phạm vi mà phải dừng lại và trả về 1 trong 3 tín hiệu chuẩn:
     - `REOPEN_REQUEST`: Yêu cầu mở lại một quyết định/hợp đồng đã đóng vì phát hiện mâu thuẫn.
     - `DEPENDENCY_REQUEST`: Yêu cầu cung cấp hoặc nghiệm thu trước một thành phần phụ thuộc.
     - `BLOCKED`: Báo cáo tắc nghẽn không thể tự giải quyết trong phạm vi được giao.
     *(Mỗi tín hiệu bắt buộc đi kèm: bằng chứng cụ thể, hệ quả kỹ thuật, và quyết định cần Lead chốt).*
   - **Đầu ra bàn giao (Immutable Candidate)**: Khi hoàn tất, Peer phải trả về một ứng viên bất biến (commit SHA hoặc snapshot rõ ràng), điểm gốc ban đầu (base commit), danh sách đường dẫn đã sửa, các lệnh kiểm chứng đã chạy kèm kết quả, và rủi ro còn tồn đọng.

---

## 4. Cơ chế Cài đặt Giao dịch (Transactional Installer) & Kiểm chứng

Hệ thống cài đặt được thiết kế theo triết lý **Fail-Closed Transactional Lifecycle** qua `install` (gọi `scripts/install-room`).

### 4.1. Ba chế độ của `./install` (`scripts/install-room`)
1. **`./install` hoặc `./install --dry-run` (Mặc định - Read-only Plan)**:
   - Không ghi hay sửa bất kỳ file nào trên máy.
   - Kiểm tra toàn bộ lệnh bắt buộc (`git`, `node`, `npm`, `jq`, `codex`), kiểm tra an toàn đường dẫn, kiểm tra `~/.codex` của người dùng và in ra bảng kế hoạch chi tiết (`CREATE`, `REPLACE`, `UNCHANGED`, `RETIRE`, `PRESERVE-WARNING`).
2. **`./install --apply` (Transactional Apply)**:
   - **Bước 1 – Kiểm tra chướng ngại & chống leo thang symlink (`check_configured_path_safety`, `check_checkout_links`)**: Từ chối chạy nếu bất kỳ thư mục cha nào là symlink chuyển hướng, hoặc nếu cấu hình đường dẫn chồng lấn lên `~/.codex`, `~/.codex-runtime`, `~/.codex-room-backups`, hoặc nếu trong `.git` của Paseo có chứa symlink.
   - **Bước 2 – Preflight Paseo độc lập (`run_preflight_paseo`)**: Clone và build thử Paseo `v0.8.0` trong thư mục tạm `TMPDIR` với `npm_config_cache` tạm để đảm bảo mạng, commit SHA và quá trình build hoàn toàn sạch trước khi chạm vào hệ thống thật.
   - **Bước 3 – Staging toàn bộ file cấu hình & Runtime (`stage_home`, `generate_role_stage`)**: Thay thế biến `@@HOME@@` và chạy thử `codex-room-sync` cho cả 3 role ngay trong thư mục tạm.
   - **Bước 4 – Mở Transaction & Sao lưu (`Transaction`)**:
     - Tạo thư mục backup riêng tại `~/.codex-room-backups/core3-<timestamp>-<pid>-<ns>` với quyền `0700` (file bên trong `0600`).
     - Sao lưu nguyên trạng Paseo checkout hiện có, CLI link và các file quản lý trước khi ghi đè bằng thao tác nguyên tử (`tempfile` + `os.replace`).
   - **Bước 5 – Dọn dẹp di sản 5-role (`OBSOLETE_HASHES` & `OBSOLETE_TEMPLATES`)**:
     - Tự động thu hồi (`retire`) các file cũ từ kiến trúc 5-role (`review.config.toml`, `harness.config.toml`, `codex-room-hard-cut`, `codex-review-apply`, `ANTI_PATTERNS.md`, `SUPERVISOR_NOTEBOOK.md`, `paseo.phase2-*.candidate.json`) **chỉ khi** mã băm SHA-256 và file mode khớp tuyệt đối với bản lịch sử của repo. Nếu người dùng đã chỉnh sửa hoặc thêm ghi chú riêng, bộ cài sẽ giữ nguyên (`preserve-warning`).
   - **Bước 6 – Tự động Rollback khi lỗi hoặc hủy (`CancellationHandlers` & `Transaction.rollback`)**:
     - Bắt tín hiệu `SIGINT`/`SIGTERM` có kiểm soát (chờ tiến trình con kết thúc an toàn) và nếu bất kỳ bước publish hay verify cuối cùng nào thất bại, toàn bộ Paseo checkout, symlink và file cấu hình được khôi phục về đúng trạng thái trước khi chạy lệnh.
3. **`./install --verify [--live]` (`scripts/verify` & `scripts/lib/model-alignment.py`)**:
   - Kiểm tra tính hợp lệ của JSON/TOML, quyền thực thi, trạng thái vắng mặt của các từ khóa quy trình cũ (`PARALLEL_CHECK`, `multiple-writer`, `OCR Review`, `Better Harness`, `workflow pilot`).
   - Dùng `tomllib` (Python 3.11+) trong `scripts/lib/model-alignment.py` để đối chiếu chéo 3 tầng: `~/.paseo/config.json` $\leftrightarrow$ `overlays/<role>.config.toml` $\leftrightarrow$ `~/.codex-runtime/<role>/config.toml`, đảm bảo `model` và `model_reasoning_effort` mặc định khớp nhau 100%.
   - Với cờ `--live`, truy vấn trực tiếp daemon đang chạy (`paseo provider ls --host 127.0.0.1:6767 --json`) để xác nhận danh sách provider `codex-*` đúng bằng `["codex-lead", "codex-peer", "codex-supervisor"]`.

---

## 5. So sánh `codex-room-setup` (Bản gốc) và `Paseo_Project` (Workspace hiện tại)

| Tiêu chí đối chiếu | `hoangnb24/codex-room-setup` (Core-3 Gốc) | `Paseo_Project` (Hệ thống SLPC hiện tại của bạn) |
| :--- | :--- | :--- |
| **Mô hình Role (Topology)** | **3 Role (`SLP`)**: `Supervisor`, `Lead`, `Peer`. Công việc Review được thực hiện bằng cách Lead spawn một `codex-peer` ở chế độ chỉ-đọc (`read-only`) trên một commit/snapshot cụ thể. | **4 Role (`SLPC`)**: `Supervisor`, `Lead`, `Peer`, và tách riêng **`QC`** (Black-box Tester & Unit Test Generator qua `tools/qc_test_generator.py`) thành một cực độc lập trong quy trình nghiệm thu. |
| **Nền tảng Agent / CLI** | Thuần **OpenAI Codex CLI** (`codex-supervisor`, `codex-lead`, `codex-peer`) chạy qua wrapper `codex-room` với `CODEX_HOME` tách biệt cho từng role. | Đa nền tảng (Claude Code / Hermes / Router9): `setup_home.sh` đồng bộ `~/.hermes/skills` (từ `hermes-profiles` & `storage`) và gọi `patch_paseo.py` bơm 4 profile (`profiles/{supervisor,lead,peer,qc}.md`) vào `daemon.agentProfiles` của `~/.paseo/config.json`. |
| **Kiểm soát Subagent nội bộ** | Tắt ở cả tầng cấu hình TOML (`agents.enabled = false`, `multi_agent = false`) lẫn tầng catalog (`multi_agent_version = null`). | Kiểm soát qua prompt hệ thống (`profiles/*.md`, `CLAUDE.md`, `AGENTS.md`) và điều phối qua `tools/call_agent.py`. |
| **Quản lý trạng thái & Task** | **Stateless ngoài Paseo**: Dựa hoàn toàn vào lịch sử phiên của Paseo, truyền thông điệp trực tiếp và đối chiếu trạng thái qua Git commit/snapshot. | **Stateful qua Harness DB**: Sử dụng `tools/harness_manager.py` & `./scripts/harness` kết nối Floci DynamoDB/S3 (hoặc fallback SQLite `harness.db`) kèm kiểm tra State Machine (`New -> Accepted -> Active -> Resolved -> Closed`). |
| **Cơ chế cài đặt & Đồng bộ** | Bộ cài đặt giao dịch bằng Python (`scripts/install-room`) có staging, kiểm tra SHA-256, backup tự động và rollback toàn phần. | Bộ script trực tiếp (`setup_home.sh`, `setup_harness.sh`, `patch_paseo.py`, `tools/remote_sync.py`, `tools/doc_sync.py`). |
| **Quy trình Kiểm thử / Nghiệm thu** | Lead tự chạy lệnh kiểm chứng hoặc ủy quyền cho một Read-only Peer kiểm tra diff/snapshot rồi Lead ra quyết định `ACCEPT`/`REJECT`. | Peer code xong $\rightarrow$ Lead/Scrum Master điều phối sang **QC** chạy kiểm thử & `verify_command` $\rightarrow$ cập nhật Test Matrix trên Harness DB. |

---

## 6. Quy trình thực hiện Setup cho `codex-room-setup` và Paseo

### 6.1. Điều kiện tiên quyết (Prerequisites) & Hiện trạng máy hiện tại

Bộ cài `codex-room-setup` yêu cầu các công cụ và cấu trúc thư mục gốc sau trước khi cho phép chạy `./install --apply`:

1. **Các binary bắt buộc trên `PATH`**:
   - `python3` (`/usr/bin/python3` — đã `OK`)
   - `git` (`/usr/bin/git` — đã `OK`)
   - `jq` (`/usr/bin/jq` — đã `OK`)
   - `node` & `npm` (`~/.local/bin/node`, `~/.local/bin/npm` — đã `OK`)
   - `codex` (`~/.local/bin/codex`, phiên bản `0.159.3` — đã `OK`)
   - `~/.local/bin` nằm trong `PATH` (đã `OK`)
2. **Thư mục gốc `~/.codex` của người dùng (Operator Codex Home)**:
   - Đã có đầy đủ thư mục thật `~/.codex` cùng toàn bộ tài nguyên cơ sở mà `codex-room-sync` symlink sang từng role runtime: `config.toml`, `auth.json`, `AGENTS.md`, `hooks.json`, `skills/`, `plugins/`.

> [!NOTE]
> **Trạng thái thực thi Setup thực tế trên máy hiện tại (`DOCTOR_OK`)**:
> 1. **Kiểm tra nguồn (`./scripts/verify --source`) & Chẩn đoán máy (`./scripts/doctor`)**: Đạt 100% (`DOCTOR_OK: 1 warning(s)` chỉ do `codex-cli 0.159.3` mới hơn bản `0.150.1` trong manifest).
> 2. **Paseo `v0.8.0` Audited Checkout**: Đã clone và build thành công tại `~/projects/supervisors/paseo` (commit `b8e24677e12b226c7c38c1c3a40649daa9f1152f`, tag `v0.8.0`). Để bảo toàn launcher Paseo Desktop `0.10.2` đang chạy tại `~/.local/bin/paseo`, symlink CLI bản `v0.8.0` được đặt tại `~/.local/bin/paseo-cli-v0.8.0`.
> 3. **Codex Room Files & 3 Isolated Runtimes**: Đã xuất bản đầy đủ `~/.config/codex-room/*`, `~/.local/bin/{codex-room,codex-room-sync,paseo-local-update}` và chạy `./scripts/sync-all` sinh thành công 3 runtime cô lập tại `~/.codex-runtime/{supervisor,lead,peer}` (đã tắt native multi-agent và đồng bộ 100% model/effort).
> 4. **Cấu hình lai `~/.paseo/config.json` (Hybrid SLPC + Core-3)**: Đã sao lưu `~/.paseo/config.json.bak-pre-codex-room`, gộp 3 provider `codex-supervisor`, `codex-lead`, `codex-peer` vào `~/.paseo/config.json` và chạy `python3 patch_paseo.py` để giữ nguyên toàn bộ `router9`, `servre` cùng 10 `agentProfiles` (bao gồm 4 profile `SLPC`: `Supervisor`, `Lead`, `Peer`, `QC`).

---

### 6.2. Các bước Setup chuẩn cho `codex-room-setup` + Paseo `v0.8.0`

#### Bước 1: Cài đặt & Khởi tạo OpenAI Codex CLI (`~/.codex`)
Nếu máy chưa có `codex` và `~/.codex`, thực hiện cài đặt và tạo đủ khung tài nguyên chia sẻ:

```bash
# 1. Cài đặt OpenAI Codex CLI và đăng nhập để sinh ~/.codex/auth.json & ~/.codex/config.toml
npm install -g @openai/codex
codex login

# 2. Đảm bảo đủ các file/thư mục dùng chung bắt buộc trong ~/.codex
mkdir -p ~/.codex/skills ~/.codex/plugins
touch ~/.codex/config.toml ~/.codex/AGENTS.md
```

#### Bước 2: Chạy chẩn đoán môi trường & Kiểm tra mã nguồn
Di chuyển vào thư mục `codex-room-setup` và chạy bộ kiểm tra:

```bash
cd codex-room-setup

# Kiểm tra tính toàn vẹn của repo nguồn
./scripts/verify --source

# Kiểm tra đủ điều kiện môi trường máy trạm
./scripts/doctor
```

#### Bước 3: Xem kế hoạch cài đặt (Dry-Run - Không ghi đè)
```bash
./install --dry-run
```
Lệnh này sẽ in ra kế hoạch chi tiết:
- Chuẩn bị Paseo `v0.8.0` (`b8e24677e12b226c7c38c1c3a40649daa9f1152f`) tại `~/projects/supervisors/paseo` và tạo symlink CLI tại `~/.local/bin/paseo`.
- Danh sách 9 file quản lý sẽ được tạo/cập nhật:
  - `~/.config/codex-room/model-instructions.md` (`0644`)
  - `~/.config/codex-room/overlays/{supervisor,lead,peer}.config.toml` (`0600`)
  - `~/.config/codex-room/workflow/WORKSPACE_PROTOCOL.md` (`0644`)
  - `~/.local/bin/codex-room` (`0755`)
  - `~/.local/bin/codex-room-sync` (`0755`)
  - `~/.local/bin/paseo-local-update` (`0755`)
  - `~/.paseo/config.json` (`0600`)
- Sinh 3 thư mục runtime cô lập tại `~/.codex-runtime/{supervisor,lead,peer}`.

#### Bước 4: Thực thi cài đặt giao dịch (Transactional Apply)
```bash
./install --apply
```
Khi chạy lệnh này:
1. Hệ thống tự động chạy `./scripts/install-paseo --preflight` trong thư mục tạm, sau đó clone và build Paseo `v0.8.0` (`npm ci` + `npm run build:server:clean`) vào `~/projects/supervisors/paseo`.
2. Tạo bản sao lưu toàn phần vào `~/.codex-room-backups/core3-<timestamp>-<pid>-<ns>`.
3. Xuất bản 9 file cấu hình, symlink `~/.local/bin/paseo`, đồng bộ 3 role runtime `~/.codex-runtime/{supervisor,lead,peer}` và tự động chạy `./scripts/verify` để xác nhận kết quả (`CODEX_ROOM_APPLY_OK`).

> [!TIP]
> **Cài riêng bản Paseo `v0.8.0` độc lập (không cần `codex` CLI)**:
> Nếu bạn chỉ muốn tải và build chuẩn bộ Paseo `v0.8.0` về `~/projects/supervisors/paseo` + gắn link `~/.local/bin/paseo` ngay lúc này (trước khi cài `codex`), có thể gọi trực tiếp script con:
> ```bash
> cd codex-room-setup
> ./scripts/install-paseo --preflight
> ./scripts/install-paseo
> ```

#### Bước 5: Khởi động Paseo Daemon & Kiểm chứng Live
Sau khi cài đặt thành công, khởi chạy Paseo daemon và kiểm tra danh sách provider thực tế:

```bash
# 1. Khởi động Paseo daemon ở cổng mặc định 127.0.0.1:6767
paseo daemon start --home ~/.paseo --listen 127.0.0.1:6767 --relay

# 2. Kiểm tra trạng thái cài đặt + danh sách provider đang sống trên daemon
cd codex-room-setup
./install --verify --live
```
Khi đạt chuẩn, lệnh sẽ trả về `OK exact live room provider inventory` (xác nhận đúng 3 provider `codex-lead`, `codex-peer`, `codex-supervisor`) và kết thúc bằng `VERIFY_OK`.

#### Bước 6: Lệnh vận hành & Đồng bộ định kỳ
- Khi bạn cập nhật `~/.codex/config.toml`, thêm skill/plugin mới hoặc đổi model trong `~/.config/codex-room/overlays/*.config.toml`, chỉ cần đồng bộ lại 3 runtime:
  ```bash
  ./scripts/sync-all
  ```
- Để xuất snapshot cấu hình runtime (đã ẩn thông tin nhạy cảm) phục vụ kiểm tra/audit:
  ```bash
  ./scripts/export-runtime-snapshots
  ```

---

### 6.3. Lưu ý khi kết hợp hoặc chuyển đổi với `Paseo_Project` (SLPC)

Vì cả `codex-room-setup` (Core-3) và `Paseo_Project` (SLPC) đều tác động vào `~/.paseo/config.json`, cần lưu ý cách hai hệ thống tương tác trên cùng một máy:

| Thành phần trên máy | Do `codex-room-setup` quản lý | Do `Paseo_Project` quản lý | Cách phối hợp không xung đột |
| :--- | :--- | :--- | :--- |
| **Paseo Engine & CLI** | `~/projects/supervisors/paseo` (`v0.8.0`) & `~/.local/bin/paseo` | Gọi `~/.local/bin/paseo` qua `tools/call_agent.py` | Hoàn toàn tương thích! Cài Paseo `v0.8.0` từ `codex-room-setup` sẽ cung cấp luôn binary `paseo` chuẩn cho `Paseo_Project`. |
| **Role Runtime / Skills** | `~/.codex-runtime/{supervisor,lead,peer}` | `~/.hermes/skills` & `~/.hermes/profiles` (qua `setup_home.sh`) | **Hoàn toàn tách biệt**, không đụng độ. |
| **File `~/.paseo/config.json`** | Ghi đè toàn bộ `~/.paseo/config.json` từ `home/.paseo/config.json.template` (thiết lập `daemon.mcp` và `agents.providers`) | `patch_paseo.py` đọc `~/.paseo/config.json` hiện có và chỉ bơm thêm mảng `daemon.agentProfiles` (4 profile `Supervisor`, `Lead`, `Peer`, `QC`) | **Trình tự chuẩn để dùng chung cả 2**: Chạy `./install --apply` của `codex-room-setup` **trước** (để tạo nền `daemon.mcp` + `agents.providers`), sau đó chạy `python3 patch_paseo.py` của `Paseo_Project` **sau** (để bổ sung `daemon.agentProfiles` mà không làm mất `agents.providers`). |

---

## 7. Hệ thống Kiểm thử Tự động (Test Suite), Nghiệm thu & Cập nhật Desktop

Để đảm bảo mọi thay đổi trên `codex-room-setup` không làm hỏng giao thức 3-role hoặc làm rò rỉ dữ liệu người dùng, repo đi kèm bộ kiểm thử tự động và quy trình nghiệm thu riêng:

### 7.1. Bộ Unit Test & Container Test (`Makefile` & `tests/*`)
- **Chạy toàn bộ Unit Test (`make test`)**:
  ```bash
  cd codex-room-setup
  make test
  ```
  Bao gồm 3 bộ test Python (`unittest`) + kiểm tra cú pháp shell (`bash -n` / `zsh -n`):
  1. `tests/test_install_room.py`: Kiểm thử toàn bộ vòng đời giao dịch của `scripts/install-room` (dry-run, apply, thu hồi file 5-role cũ theo SHA-256, bảo toàn file người dùng đã sửa, chống leo thang symlink, xử lý `SIGINT`/`SIGTERM`, và rollback khi lỗi).
  2. `tests/test_core4_acceptance.py`: Kiểm thử 4 kịch bản nghiệm thu cốt lõi của phòng Core-3 (routing, parallel write-scope isolation, peer challenge signals, read-only review).
  3. `tests/test_paseo_release_scripts.py`: Kiểm thử `scripts/install-paseo` và `home/.local/bin/paseo-local-update` (kiểm tra khóa SHA `v0.8.0`, phát hiện thay đổi `package-lock.json`, chống hook lạ).
- **Chạy Container Clean-Machine Test (`make test-container` / `tests/container/run`)**:
  - Dựng container Linux sạch để kiểm thử toàn bộ luồng cài đặt từ đầu (`install --dry-run` $\rightarrow$ `install --apply` $\rightarrow$ `verify`) trong môi trường cô lập.

### 7.2. Bộ 4 Kịch bản Nghiệm thu Hành vi (`docs/acceptance/core4.md`)
Một bản cài đặt `codex-room-setup` chỉ được coi là vận hành đúng về mặt hành vi khi vượt qua 4 bài kiểm tra (Core-4 Acceptance Drills):
1. **Drill 1 – Normal Sequential Slice**: `Human -> Supervisor -> Lead -> 1 Writable Peer -> Lead ACCEPT -> Supervisor`. Kiểm chứng Supervisor ẩn danh cuộc trò chuyện riêng với Human và không tự nghiệm thu.
2. **Drill 2 – Parallel Disjoint Slices**: Lead mở $\ge 2$ Writable Peers song song khi và chỉ khi đầu vào đã được `ACCEPT` và tập file ghi tách rời nhau hoàn toàn.
3. **Drill 3 – Peer Challenge (`REOPEN_REQUEST` / `DEPENDENCY_REQUEST` / `BLOCKED`)**: Peer phát hiện giả định sai của Lead, dừng lại và phát tín hiệu phản biện kèm bằng chứng thay vì tự ý sửa tràn lan.
4. **Drill 4 – Read-only Review Peer**: Lead mở một `codex-peer` ở chế độ chỉ-đọc để review một commit/snapshot cụ thể; Peer không sửa working tree và không tự ra phán quyết `ACCEPT`.

### 7.3. Công cụ Cập nhật Paseo Desktop (`home/.local/bin/paseo-local-update`)
- Dành riêng cho môi trường macOS khi người dùng sử dụng ứng dụng `/Applications/Paseo.app`.
- Tự động xác thực commit `v0.8.0`, chạy `npm ci` có kiểm tra SHA-256 của `package-lock.json`, build bản Desktop (`npm run build:desktop`), ký mã cục bộ (`codesign`), sao lưu bản `Paseo.app` cũ và khởi động lại daemon ở `127.0.0.1:6767`.

---

## 8. Cơ chế Lưu trữ Tiến độ & Bàn giao giữa các Agent (Agent Progress & Handoff Ledger)

Để giải quyết bài toán **liên tục ngữ cảnh (Session Continuity)** — giúp bất kỳ Agent nào (Antigravity, Claude Code, Codex, Hermes, hay các role `Supervisor`/`Lead`/`Peer`/`QC`) khi nhận lệnh **"làm tiếp"** hoặc **"báo cáo những gì đã làm"** từ User đều nắm bắt tức thì trạng thái công việc mà không phải đọc lại từ đầu:

### 8.1. Kiến trúc Lưu trữ Kép (Dual-Format Progress Ledger)
Hệ thống lưu trữ tiến độ tại 2 file đồng bộ trong workspace:
1. **`docs/AGENT_PROGRESS.md` (Human & LLM Readable Ledger)**:
   - Bảng tổng quan trạng thái hiện tại (**Current Snapshot**): Cột mốc vừa xong, việc đang làm dở, danh sách các mục còn thiếu/chờ thực thi (**Pending / Missing Items**).
   - Nhật ký bàn giao theo thời gian (**Session Handoff Log**): Ghi rõ từng phiên Agent nào làm, đã hoàn thành gì, tạo/sửa những file nào, và bước tiếp theo là gì.
2. **`.harness_progress.json` (Structured State via `tools/agent_progress.py`)**:
   - File JSON cấu trúc chuẩn lưu toàn bộ lịch sử bàn giao và checklist các việc cần làm tiếp, được `.gitignore` để không làm bẩn Git working tree khi các Agent cập nhật liên tục.

### 8.2. Giao thức bắt buộc cho mọi Agent (`AGENTS.md` & `CLAUDE.md`)
- **Khi bắt đầu phiên hoặc khi User nói *"làm tiếp"* / *"báo cáo tiến độ"***:
  1. Chạy `python3 tools/agent_progress.py status` (hoặc đọc trực tiếp `docs/AGENT_PROGRESS.md`).
  2. Báo cáo ngắn gọn cho User: **(a) Những gì đã làm xong**, **(b) Những mục còn thiếu/đang dở**, và **(c) Bước tiếp theo sẽ thực hiện ngay**.
- **Khi hoàn thành một đầu việc hoặc trước khi dừng chờ User**:
  1. Cập nhật tiến độ bằng lệnh:
     ```bash
     python3 tools/agent_progress.py log \
       --agent "<Tên_Agent_hoặc_Role>" \
       --summary "<Tóm tắt ngắn gọn đầu việc>" \
       --done "<Các mục đã hoàn thành, phân tách bằng dấu ;>" \
       --missing "<Các mục còn thiếu/chưa làm, phân tách bằng dấu ;>" \
       --next "<Bước tiếp theo cần làm khi User bảo làm tiếp>" \
       --files "<Danh sách file đã tạo/sửa, phân tách bằng dấu ,>"
     ```
  2. Lệnh trên sẽ tự động cập nhật cả `.harness_progress.json` lẫn render lại file `docs/AGENT_PROGRESS.md` để luôn sẵn sàng cho phiên kế tiếp.

### 8.3. Bản đồ Vị trí Lưu trữ Context Window Thực Tế của từng Nền tảng Agent (`*.jsonl` & `*.sqlite`)

Các Agent **không dùng Harness DB để nhớ lịch sử hội thoại nội bộ của chính nó**, mà mỗi nền tảng lưu toàn bộ Context Window (tin nhắn, suy nghĩ/thinking, kết quả gọi tool) thành file riêng trên đĩa và tự động nạp lại qua `--resume=<sessionId>`:

| Nền tảng / Role Agent | Nơi lưu Metadata / Con trỏ Session | Nơi lưu toàn bộ Context Window thực tế (`*.jsonl` / `*.sqlite`) |
| :--- | :--- | :--- |
| **Paseo Agents (`router9` / `claude` / `servre`)** | `~/.paseo/agents/<workspace-slug>/<agentId>.json` (chứa trường `persistence.sessionId`) | `~/.paseo/claude-config/projects/<workspace-slug>/<sessionId>.jsonl` (do `CLAUDE_CONFIG_DIR=~/.paseo/claude-config`) |
| **Codex Room – Supervisor (`codex-supervisor`)** | `~/.paseo/agents/<workspace-slug>/<agentId>.json` | `~/.codex-runtime/supervisor/sessions/YYYY/MM/DD/*.jsonl` & `~/.codex-runtime/supervisor/thread_history_*.sqlite` |
| **Codex Room – Lead (`codex-lead`)** | `~/.paseo/agents/<workspace-slug>/<agentId>.json` | `~/.codex-runtime/lead/sessions/YYYY/MM/DD/*.jsonl` & `~/.codex-runtime/lead/thread_history_*.sqlite` |
| **Codex Room – Peer (`codex-peer`)** | `~/.paseo/agents/<workspace-slug>/<agentId>.json` | `~/.codex-runtime/peer/sessions/YYYY/MM/DD/*.jsonl` & `~/.codex-runtime/peer/thread_history_*.sqlite` |
| **Codex Room – QC (`codex-qc`)** | `~/.paseo/agents/<workspace-slug>/<agentId>.json` | `~/.codex-runtime/qc/sessions/YYYY/MM/DD/*.jsonl` & `~/.codex-runtime/qc/thread_history_*.sqlite` |
| **Codex CLI Độc lập (ngoài Paseo)** | `~/.codex/session_index.jsonl` | `~/.codex/sessions/YYYY/MM/DD/*.jsonl` & `~/.codex/thread_history_1.sqlite` |
| **Antigravity IDE** | `~/.gemini/antigravity/brain/<conversation-id>/` | `~/.gemini/antigravity/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (và `transcript_full.jsonl`) |

> [!TIP]
> **Tra cứu nhanh các file Context Window đang active của dự án**:
> Chạy lệnh `python3 tools/agent_progress.py sessions` để liệt kê ngay danh sách các Agent trong Paseo cùng đường dẫn tuyệt đối tới file `.jsonl` chứa Context Window của từng Agent.

---

## 9. Mở rộng lên 4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`) & Tích hợp `031_claude_code_sub_agents`

Vì hệ thống của chúng ta vận hành theo mô hình **4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`)** có thêm cực **`QC`** độc lập (Independent Quality Gate & ISTQB 5-Stage Test Specialist), toàn bộ hệ thống `codex-room-setup`, Paseo, Claude Code, Codex và Hermes đã được nâng cấp từ 3 role lên **4 role** và tích hợp bộ Subagent Skill từ [`hoangnb24/storage/tree/main/031_claude_code_sub_agents`](https://github.com/hoangnb24/storage/tree/main/031_claude_code_sub_agents):

### 9.1. Nâng cấp Codex Room từ 3 Role lên 4 Role (`supervisor | lead | peer | qc`)
- **Overlay thứ 4 (`qc.config.toml`)**: Tạo mới tại `codex-room-setup/home/.config/codex-room/overlays/qc.config.toml` và `~/.config/codex-room/overlays/qc.config.toml` (`model = "gpt-6.1-sol"`, `model_reasoning_effort = "medium"`, `paseoTools.enabled = false`).
- **Runtime thứ 4 (`~/.codex-runtime/qc`)**: Cập nhật `codex-room`, `codex-room-sync`, `scripts/sync-all`, `scripts/install-room`, `scripts/verify`, `scripts/lib/model-alignment.py`, và `scripts/lib/paseo-tools.jq` để hỗ trợ đầy đủ 4 role `supervisor | lead | peer | qc` và 4 provider `codex-supervisor | codex-lead | codex-peer | codex-qc`.

### 9.2. Bộ 3 Sub-Agents (`031_claude_code_sub_agents` + `slpc-qc-verifier`)
1. **`gemini-codebase-analyzer`** (từ `031_claude_code_sub_agents/gemini-codebase-analyzer.md`):
   - Sử dụng `gemini --prompt "..." --all-files` (tận dụng Context Window 1M+ tokens của Gemini 2.5 Pro) để quét toàn bộ codebase, đối chiếu Spec với thực tế triển khai, tìm luồng dữ liệu xuyên suốt nhiều file và phát hiện nợ kỹ thuật.
2. **`strategic-reasoning-architect`** (từ `031_claude_code_sub_agents/strategic-reasoning-architect.md`):
   - Sử dụng `codex -m "gpt-5" "..."` để suy luận sâu về kiến trúc hệ thống, phân tích đánh đổi (trade-offs), tìm nguyên nhân gốc rễ (root-cause analysis) của các lỗi phức tạp/race conditions và lập lộ trình chiến lược.
3. **`slpc-qc-verifier`** (bổ sung chuyên biệt cho Role thứ 4 `QC`):
   - Sub-agent chuyên trách cổng kiểm soát chất lượng độc lập (Independent Quality Gate) và sinh/chạy Unit Test theo quy trình **5-Stage ISTQB Pipeline** (`python3 tools/qc_test_generator.py`), kết hợp `gemini-codebase-analyzer` và `strategic-reasoning-architect` để đối chiếu Spec $\leftrightarrow$ Codebase và cập nhật Test Matrix lên `Harness DB`.

### 9.3. Vị trí cài đặt đồng bộ trên toàn bộ các tầng Agent
| Tầng Môi trường | Đường dẫn cài đặt | Mục đích |
| :--- | :--- | :--- |
| **Project Claude Sub-Agents** | `.claude/agents/*.md` | Cho phép Claude Code trong workspace gọi trực tiếp 3 sub-agents (`gemini-codebase-analyzer`, `strategic-reasoning-architect`, `slpc-qc-verifier`). |
| **Paseo Claude Config (`router9`/`claude`)** | `~/.paseo/claude-config/agents/*.md` & `~/.claude/agents/*.md` | Cho phép toàn bộ các Agent chạy trên Paseo Daemon (`Supervisor`, `Lead`, `Peer`, `QC`) gọi sub-agents ở cấp global. |
| **Codex Room 4 Roles (`supervisor`/`lead`/`peer`/`qc`)** | `~/.codex/skills/claude-code-sub-agents/` (symlink tự động vào `~/.codex-runtime/{supervisor,lead,peer,qc}/skills/`) | Cung cấp skill `claude-code-sub-agents` cho cả 4 role trong Codex Room. |
| **Project & Hermes Skills** | `.agents/skills/claude-code-sub-agents/SKILL.md` & `~/.hermes/skills/031_claude_code_sub_agents` | Đồng bộ skill chuẩn cho Antigravity, Hermes và `setup_home.sh`. |
| **4 Role Profiles (`SLPC`)** | `profiles/{supervisor,lead,peer,qc}.md` (đã patch vào `~/.paseo/config.json`) | Hướng dẫn từng role (`Supervisor`, `Lead`, `Peer`, `QC`) cách kết hợp 3 sub-agents phù hợp với chức năng của mình. |
