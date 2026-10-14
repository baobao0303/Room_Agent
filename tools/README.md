# Tools Directory

Thư mục chứa các bộ công cụ bổ trợ cho Agent trong dự án Paseo.

## Danh sách công cụ
- `crm_doc_reader.py`: Tool tra cứu tài liệu đặc tả, User Stories (UC1.01-UC4.09) từ repo REMOTE `crm` nhánh `docs/base` (`/home/baoltb/Desktop/crm-doc`). Hỗ trợ `--uc <CODE>`, search BM25, git sync `--sync` (dành cho Profile `Lead BA` / `Peer BA`).
- `floci_client.py`: Client DynamoDB & S3 kết nối Floci emulator phục vụ lưu trữ phân tán cho Harness.
- `harness_manager.py`: Tool quản lý và điều phối các đối tượng Work Item trong framework Harness (hỗ trợ cả SQLite local và Floci DynamoDB backend).
- `query_reader.py`: Tool đọc file/thư mục thông minh dạng query, giải quyết triệt để lỗi `EISDIR` và đoán mò file; trích xuất section chính xác cao theo heading/token.
- `research/`: Bộ công cụ nghiên cứu, tạo prompt 3 tầng và xuất báo cáo Markdown thông qua Hermes Gateway / CLI.
