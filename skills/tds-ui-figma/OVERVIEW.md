# TDS UI Figma Workflow Skill

## Mục Đích

`tds-ui-figma` là skill dùng chung cho team khi cần phân tích hoặc triển khai giao diện Angular từ Figma bằng hệ sinh thái **tds-ui** và **tds-color**.

Skill này giúp agent đi theo một luồng thống nhất thay vì tự suy đoán từ ảnh chụp hoặc màu hex. Mục tiêu chính là giảm sai lệch giữa Figma và code, chuẩn hóa cách map component, map màu, setup Figma MCP, và bắt buộc hỏi lại khi thiếu thông tin quan trọng như theme preset.

## Skill Này Giải Quyết Vấn Đề Gì

| Vấn đề thường gặp | Cách skill xử lý |
|---|---|
| Agent đoán màu primary/secondary từ hex | Bắt buộc có `themePreset`; nếu thiếu thì dừng và hỏi |
| Figma có màu hex nhưng không biết class TDS | Dùng `tds-token-lookup.js` để tra từ token map |
| Token JSON trên server thay đổi | Dùng `sync-tds-tokens.js` để kéo bản mới nhất về cache local |
| Agent tự viết HTML/CSS dù có component `tds-ui` | Bắt buộc map qua `tds-ui` component trước |
| Team setup Figma MCP thủ công phức tạp | Có script setup riêng cho Codex và Claude Ubuntu |
| Phân tích Figma mỗi người một kiểu | Có template output chuẩn: token lookup, layout, component mapping, color mapping |

## Khi Nào Dùng

Dùng skill này khi:

- Có Figma link/frame/node cần phân tích UI.
- Cần implement Angular UI từ Figma bằng `tds-ui`.
- Cần map Figma component sang `tds-ui` component.
- Cần map màu từ Figma hex sang `tds-color`.
- Cần cập nhật token JSON mới nhất từ TDS Design Token.
- Cần setup Framelink Figma MCP cho Codex hoặc Claude Code.

Không dùng skill này cho bugfix Angular thông thường nếu task không liên quan Figma, `tds-ui`, hoặc `tds-color`.

## Luồng Hoạt Động Tổng Quát

```text
Người dùng gửi Figma link
|
|-- 1. Kiểm tra theme preset
|     |-- Có trong project-config của skill -> tiếp tục
|     `-- Không có -> dừng và hỏi, không đoán màu
|
|-- 2. Đọc Figma qua Framelink MCP
|     |-- get_figma_data
|     `-- download_figma_images nếu thật sự cần asset
|
|-- 3. Phân tích layout
|     |-- hierarchy
|     |-- spacing
|     |-- typography
|     `-- responsive/state nếu có
|
|-- 4. Map component
|     |-- đọc references/mapping/tds-ui-component-map.md
|     |-- đọc references/mapping/figma-to-tds-ui-rules.md
|     `-- nếu không chắc -> hỏi lại, không tự chế component
|
|-- 5. Map màu
|     |-- lấy hex từ Framelink MCP
|     |-- chạy scripts/tds-token-lookup.js
|     `-- nếu missing/ambiguous/themePresetRequired -> hỏi lại
|
`-- 6. Trả report hoặc implement
      |-- Analysis Mode: trả bảng phân tích chuẩn
      `-- Implementation Mode: code trực tiếp khi user nói "làm luôn"
```

## Hai Chế Độ Chính

### Analysis Mode

Đây là chế độ mặc định khi user gửi Figma link hoặc yêu cầu "phân tích".

Output phải đi theo thứ tự:

1. JS/Token Lookup Output
2. Layout
3. Figma Component to TDS UI Mapping
4. Color Mapping

Mục tiêu của chế độ này là giúp team review trước khi code, nhìn rõ phần nào chắc chắn, phần nào thiếu dữ liệu, phần nào cần hỏi lại.

### Implementation Mode

Dùng khi user nói rõ là "làm luôn", "implement luôn", "khỏi phân tích".

Agent có thể bỏ qua report phân tích dài, nhưng vẫn phải:

- kiểm tra `themePreset`
- không đoán màu
- dùng `tds-ui` nếu có component phù hợp
- dùng token lookup khi cần map màu
- hỏi lại nếu thiếu thông tin bắt buộc

## Theme Preset Là Bắt Buộc

TDS theme có thể đổi vai trò primary/secondary theo preset. Cùng một hex có thể là `primary` ở theme này nhưng là `secondary` ở theme khác.

Vì vậy, skill bắt buộc kiểm tra:

```text
references/config/tds-project-token-map.json
```

Nếu không có `themePreset`, agent phải dừng trước khi đọc Figma hoặc map màu.

Preset hỗ trợ không hardcode trong skill. Agent lấy danh sách từ remote `theme.json` sau khi sync token:

```bash
node scripts/set-tds-theme-preset.js --list
```

## Lưu Theme Preset Trong Skill

Sau khi user chọn preset, agent lưu vào một file cấu hình nằm trong skill:

```text
references/config/tds-project-token-map.json
```

Có thể lưu bằng lệnh:

```bash
node scripts/set-tds-theme-preset.js <themePreset>
```

Lần sau agent đọc lại preset đã lưu và không hỏi lại, trừ khi preset vẫn là
`null`, không còn được hỗ trợ, hoặc user yêu cầu đổi theme. Xóa token cache
không xóa file cấu hình này.
## Token JSON Và Cơ Chế Cache

Skill không hardcode token JSON trong repo. Các nguồn token được khai báo tại:

```text
references/config/tds-token-sources.json
```

Bao gồm:

| Nguồn | URL |
|---|---|
| `themeTokens` | `https://tds.tmtco.org/assets/tds-design-token/theme.json` |
| `globalTokens` | `https://tds.tmtco.org/assets/tds-design-token/global.json` |
| `aliasTokens` | `https://tds.tmtco.org/assets/tds-design-token/alias.json` |

Khi muốn cập nhật token mới nhất:

```bash
node scripts/sync-tds-tokens.js
```

Khi tra một màu cụ thể:

```bash
node scripts/tds-token-lookup.js "#27A745" background my_project <themePreset> light
```

Nếu token cache chưa có, lookup helper có thể tự sync. Nếu muốn chỉ dùng cache local, set:

```bash
TDS_TOKEN_LOOKUP_OFFLINE=1
```

## Figma MCP Setup

Skill dùng Framelink MCP (`figma-developer-mcp`) để đọc Figma qua REST API.

MCP cung cấp hai tool chính:

```text
get_figma_data
download_figma_images
```

Setup Codex:

```bash
bash scripts/setup-figma-framelink-codex.sh
```

Setup Claude Code trên Ubuntu:

```bash
bash scripts/setup-figma-framelink-claude-ubuntu.sh
```

Script Claude Ubuntu sẽ:

- kiểm tra `node` và `npx`
- nhập Figma token dạng hiện rõ
- cập nhật `~/.claude.json`
- thêm hoặc thay thế `mcpServers.figma-framelink`
- tự điền `PATH` theo Node.js thật trên máy

## Cấu Trúc Thư Mục

```text
tds-ui-figma/
|-- SKILL.md
|-- INSTALL.md
|-- OVERVIEW.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- config/
|   |   |-- tds-project-token-map.json
|   |   `-- tds-token-sources.json
|   |-- mapping/
|   |   |-- figma-to-tds-ui-rules.md
|   |   |-- figma-color-to-tds-token-rules.md
|   |   `-- tds-ui-component-map.md
|   `-- setup/
|       `-- figma-framelink-mcp-setup.md
`-- scripts/
    |-- figma-digest.js
    |-- setup-figma-framelink-codex.sh
    |-- setup-figma-framelink-claude-ubuntu.sh
    |-- sync-tds-tokens.js
    `-- tds-token-lookup.js
```

## Vai Trò Của Từng Nhóm File

| Nhóm | Vai trò |
|---|---|
| `SKILL.md` | Instruction chính để agent biết khi nào dùng skill và chạy theo workflow nào |
| `INSTALL.md` | Hướng dẫn cài đặt cho team |
| `OVERVIEW.md` | Tài liệu giới thiệu cho người đọc hiểu skill dùng để làm gì |
| `references/config/` | Config nguồn token và file mẫu project theme |
| `references/mapping/` | Luật map Figma sang `tds-ui` và `tds-color` |
| `references/setup/` | Tài liệu setup Framelink MCP |
| `scripts/` | Tool tự động sync token, lookup màu, digest Figma, setup MCP |

## Nguyên Tắc Quan Trọng

- Không đoán theme preset.
- Không map màu bằng cảm tính từ hex.
- Không dùng REST Variables API của Figma cho workflow này.
- Không tự dựng button/input/select/table nếu `tds-ui` có component tương ứng.
- Không tải asset nếu có thể dùng TDS icon class hoặc CSS/token.
- Không yêu cầu user paste Figma token vào chat.
- Nếu thiếu dữ liệu bắt buộc, dừng và hỏi thay vì tiếp tục với giả định.

## Kết Quả Mong Muốn

Sau khi team dùng skill này, luồng làm UI từ Figma sẽ nhất quán hơn:

- Figma được đọc bằng MCP thay vì đoán từ ảnh.
- Component được map về `tds-ui` trước khi viết custom UI.
- Màu được map qua token chính thức.
- Theme preset được xác nhận rõ ràng.
- Token remote có thể cập nhật lại bằng một lệnh.
- Codex và Claude Code có thể setup MCP bằng script đơn giản.


