# tools/AGENTS.md - Tools Execution & Maintenance Directives

Chỉ thị dành cho Agent khi làm việc trong thư mục `tools/`.

---

## 1. Danh sách Tools
- **`crm_doc_reader.py`**:
  - Đọc và tra cứu tài liệu đặc tả CRM từ repo REMOTE `https://remote.example.com/MainCollection/ACME/_git/crm` nhánh `docs/base` (local: `/home/baoltb/Desktop/crm-doc`).
  - Cú pháp: `python3 /home/baoltb/Desktop/Paseo_Project/tools/crm_doc_reader.py [query] [--uc <UC_CODE>] [-c <all|ba|spec>] [-s] [-j]`
- **`query_reader.py`**:
  - Dùng để đọc file và duyệt thư mục không lỗi `EISDIR`.
  - Cú pháp: `python3 /home/baoltb/Desktop/Paseo_Project/tools/query_reader.py <path> [query] [-n top] [-m max_lines] [-j]`
- **`harness_manager.py` / `scripts/harness`**:
  - Quản trị Work Items & State Machine theo chuẩn DDD-COMPANY-2026 trên Floci DynamoDB (317 items).
  - Tra cứu ma trận kiểm thử: `./scripts/harness query matrix`
  - Tra cứu backlog: `./scripts/harness query backlog [--top 20] [--source remote|local] [--sprint "..."]`
  - Đồng bộ REMOTE: `./scripts/harness sync-remote`
  - Thêm/Cập nhật: `python3 /home/baoltb/Desktop/Paseo_Project/tools/harness_manager.py <add|update|list|stats> ...`
- **`research/research_agent.py`**:
  - Nghiên cứu kỹ thuật qua Hermes Gateway hoặc CLI.
  - Cú pháp: `python3 /home/baoltb/Desktop/Paseo_Project/tools/research/research_agent.py "<topic>" [output_path]`

---

## 2. Quy tắc phát triển Tools
- **Lazy Senior Developer**: Thuần Python stdlib, không thêm dependency ngoài nếu stdlib đáp ứng được.
- **Tự động hóa & Phi tương tác**: Luôn hỗ trợ flag `--json` và cờ non-interactive.
- **Xác thực dữ liệu**: Luôn validate schema và kiểm tra đầu vào trước khi ghi DB/file.
