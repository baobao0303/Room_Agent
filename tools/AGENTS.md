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
  - Nghiên cứu kỹ thuật qua Hermes Gateway, Router9 (`ag/gemini-3.8-flash-high`), Hermes CLI hoặc tổng hợp BM25 cục bộ.
  - Cú pháp: `python3 /home/baoltb/Desktop/Paseo_Project/tools/research/research_agent.py "<topic>" [output_path]`
- **`profile_research_gen.py`**:
  - Pipeline ép buộc mọi Profile của Paseo (`Supervisor`, `Lead`, `Peer`, `QC`, `Lead BA`, `Peer BA`, `Lead Dev`, `Peer Dev`, `Lead design`, `Peer Design`) thực thi **Research + Gen** tự động trước/trong khi xử lý task.
  - Cú pháp: `python3 /home/baoltb/Desktop/Paseo_Project/tools/profile_research_gen.py --profile "<Role>" --topic "<Task>" [--source <file>] [--spec <spec>] [--task-id <id>] [--uc <UC>] [--sync-harness]`
- **`qc_test_generator.py`**:
  - Bộ sinh Test Matrix & Unit Test tự động theo **5-Stage ISTQB Pipeline** (cho `QC` và `Peer`).
  - Cú pháp: `python3 /home/baoltb/Desktop/Paseo_Project/tools/qc_test_generator.py --source <file> --spec <spec> --task-id <id> --out-spec <spec_ts> --sync-harness [--run]`
- **`agent_progress.py`**:
  - Quản lý Sổ cái Tiến độ & Bàn giao (`docs/AGENT_PROGRESS.md`) + tìm/đọc thread `.jsonl` (`find-thread`, `read-thread`, `sessions`, `status`, `log`).
- **`zombie_reaper.py`**:
  - Quét và thu hồi các terminal PTY mồ côi (Zombie Terminal Reaper) và giám sát trần timeout watchdog 300s cho Ephemeral Sub-Agents.
  - Cú pháp: `python3 tools/zombie_reaper.py [--dry-run] [--timeout 300] [--json] [--interrupt-stalled]`


---

## 2. Quy tắc phát triển Tools
- **Lazy Senior Developer**: Thuần Python stdlib, không thêm dependency ngoài nếu stdlib đáp ứng được.
- **Tự động hóa & Phi tương tác**: Luôn hỗ trợ flag `--json` và cờ non-interactive.
- **Xác thực dữ liệu**: Luôn validate schema và kiểm tra đầu vào trước khi ghi DB/file.
