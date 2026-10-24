---
name: claude-code-sub-agents
description: "Bộ kỹ năng tích hợp 031_claude_code_sub_agents (gemini-codebase-analyzer, strategic-reasoning-architect) kết hợp kiến trúc 4-Role SLPC (Supervisor, Lead, Peer, QC) để phân tích codebase lớn bằng Gemini 1M+ context, suy luận kiến trúc bằng Codex/GPT và kiểm định độc lập bằng QC Subagent."
version: 1.0.0
author: HoangNB24, Antigravity, BaoLTB
license: MIT
platforms: [linux, macos, windows]
metadata:
  source: "https://github.com/hoangnb24/storage/tree/main/031_claude_code_sub_agents"
  roles: [supervisor, lead, peer, qc]
---

# Claude Code Sub-Agents for 4-Role SLPC (`031_claude_code_sub_agents`)

Tài liệu kỹ năng chuẩn hóa từ [`031_claude_code_sub_agents`](https://github.com/hoangnb24/storage/tree/main/031_claude_code_sub_agents) được mở rộng cho mô hình **4 Role SLPC (`Supervisor - Lead - Peer - QC`)** của `Paseo_Project`.

Skill này cung cấp các **Sub-Agent chuyên biệt** để các Role trong hệ thống SLPC gọi hỗ trợ (qua Claude Code Sub-Agents `.claude/agents/*.md`, CLI `gemini`, `codex`, hoặc `tools/call_agent.py`) mà không làm tràn Context Window của Agent chính.

---

## 1. Danh mục Sub-Agents (`031_claude_code_sub_agents` + `SLPC QC`)

| Sub-Agent | File định nghĩa | Công cụ / Model nền | Khi nào sử dụng trong 4-Role SLPC |
| :--- | :--- | :--- | :--- |
| **`gemini-codebase-analyzer`** | `.claude/agents/gemini-codebase-analyzer.md` | `gemini --prompt "..." --all-files` (1M+ token context) | Khi **Lead**, **Peer** hoặc **QC** cần quét toàn bộ monorepo frontend (`projects/`), tìm luồng dữ liệu liên file, lập bản đồ phụ thuộc hoặc rà soát lỗi bảo mật/technical debt trên diện rộng. |
| **`strategic-reasoning-architect`** | `.claude/agents/strategic-reasoning-architect.md` | `codex -m "gpt-5" "..."` / `codex-room` | Khi **Lead** hoặc **Peer** cần phân tích đánh đổi kiến trúc (trade-offs), thiết kế thuật toán phức tạp, xử lý race condition, hoặc phản biện giải pháp kỹ thuật trước khi sửa code. |
| **`slpc-qc-verifier`** | `.claude/agents/slpc-qc-verifier.md` | `python3 tools/qc_test_generator.py` + `codex-room qc` | Khi **Lead** hoặc **Supervisor** cần gọi **Role thứ 4 (`QC`)** dưới dạng Sub-Agent để kiểm định hộp đen (Black-box), sinh Unit Test theo chuẩn **ISTQB 5-Stage** và xác thực `Test Matrix` trên Harness DB. |

---

## 3. Quy Trình 3 Sub-Agents Review Chéo Công Việc Các Agent Khác (Cross-Agent Review Protocol)

Khi bất kỳ Agent nào (như Peer Dev, Lead Dev) hoàn thành một commit hoặc thay đổi code, 3 Sub-Agents được kích hoạt song song để kiểm định toàn diện từ 3 lăng kính độc lập:

```text
                     [Commit / Code Diff của Agent]
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
1. gemini-codebase-analyzer   2. strategic-architect    3. slpc-qc-verifier
   (Tác động toàn cục &       (Tuân thủ Kiến trúc &     (Chất lượng Thực nghiệm &
    Rò rỉ Dead Code)           Lazy Senior Dev)          Bao phủ 17 UI Standards)
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
                    [Biên bản Review Tổng hợp ➔ Lead]
```

### Chi tiết nhiệm vụ Review của từng Sub-Agent:
1. **`gemini-codebase-analyzer` (Codebase Impact & Dead Code Reviewer)**:
   - Quét toàn bộ monorepo xem thay đổi có gây hiệu ứng cánh bướm (Blast Radius), vỡ import ở module khác không.
   - Tìm kiếm code thừa / import rác bị bỏ quên sau khi refactor (như module cũ chưa gỡ bỏ).
2. **`strategic-reasoning-architect` (Architecture & Constraint Reviewer)**:
   - Thẩm định tính tối giản (YAGNI, Lazy Senior Dev) - xóa trước thêm sau.
   - Kiểm tra ràng buộc Single-Ownership: Không sửa chéo sang file của module khác.
   - Kiểm tra tiêu chuẩn giao diện: Không có mã màu hex cứng (`#...`), 100% dùng token TDS UI, giữ `ChangeDetectionStrategy.OnPush`.
3. **`slpc-qc-verifier` (Quality Gate & Test Coverage Reviewer)**:
   - Chạy test suite thực tế (`npm test`), xác nhận tỷ lệ PASS 100%.
   - Rà soát độ bao phủ theo 17 Hạng mục Chuẩn Web UI (Checkbox, Table sort/filter, Expand row, Drawer footer, Empty states).
   - Kiểm tra các ca biên (null, undefined, mảng rỗng).

---

## 2. Cách phối hợp Sub-Agents trong 4 Role SLPC (`Supervisor -> Lead -> Peer -> QC`)

```text
[1. Supervisor] ──► Giữ biên phạm vi (Scope & Intent Guard), tạo/điều phối Epic & Story trên Harness DB
       │
       ▼
[2. Lead]       ──► Gọi sub-agent `gemini-codebase-analyzer` (quét toàn cục)
       │            + `strategic-reasoning-architect` (chốt kiến trúc & chia moving write scope)
       ▼
[3. Peer]       ──► Thực thi code (TDD); có thể gọi `gemini-codebase-analyzer` để tra cứu nhanh
       │            liên kết module mà không làm bẩn context chính
       ▼
[4. QC]         ──► Role thứ 4 độc lập (`slpc-qc-verifier` / `codex-qc`):
                    - Dùng `gemini-codebase-analyzer` để đối chiếu toàn bộ Spec vs Code
                    - Chạy `tools/qc_test_generator.py` (5-Stage ISTQB) & E2E/Unit Test
                    - Cập nhật `Resolved -> Closed` (PASS) hoặc tạo `Bug` trả về `Active` (FAIL)
```

---

## 3. Lệnh thực thi chuẩn cho từng Sub-Agent

### 3.1. `gemini-codebase-analyzer` (Large Context Codebase Specialist)
Sử dụng khả năng nạp ngữ cảnh lớn của Gemini CLI để phân tích toàn bộ codebase hoặc nhiều thư mục cùng lúc:

```bash
# Phân tích kiến trúc tổng thể toàn bộ dự án
gemini --prompt "Analyze this entire codebase architecture" --all-files

# Kiểm tra sâu kèm theo dõi bộ nhớ
gemini --prompt "Find all security vulnerabilities and cross-file regressions" --all-files --show-memory-usage

# Phân tích có chọn lọc theo danh sách thư mục
gemini --prompt "Document the API structure and component dependencies" --include-directories api,docs,tests

# Tự động rà soát technical debt quy mô lớn
gemini --prompt "Identify technical debt patterns" --all-files --yolo
```

### 3.2. `strategic-reasoning-architect` (Codex Reasoning Specialist)
Sử dụng năng lực suy luận sâu của Codex để đánh giá phương án kỹ thuật, tìm root cause và thiết kế hệ thống:

```bash
# Phân tích đánh đổi kiến trúc
codex -m "gpt-5" "Analyze the architectural trade-offs for microservices vs monolith for this codebase"

# Tìm nút thắt hiệu năng và chiến lược tối ưu
codex -m "gpt-5" "Analyze performance bottlenecks in this codebase and suggest optimization strategies"

# Hoặc gọi qua runtime cô lập của Codex Room (4-role SLPC)
~/.local/bin/codex-room lead
```

### 3.3. `slpc-qc-verifier` (Role thứ 4: QC Gate 4 & ISTQB 5-Stage Sub-Agent)
Khi **Lead** nhận candidate từ **Peer**, Lead kích hoạt Sub-Agent **QC** để kiểm định độc lập:

```bash
# 1. Gọi QC Agent qua Paseo Dispatcher
python3 tools/call_agent.py --profile QC --prompt "Verify Task #<TASK_ID> theo chuẩn ISTQB 5-Stage"

# 2. Hoặc chạy trực tiếp pipeline 5-Stage ISTQB sinh Unit Test & đồng bộ Harness DB
python3 tools/qc_test_generator.py \
  --source <đường_dẫn_source_code> \
  --spec <đường_dẫn_spec_md> \
  --task-id <TASK_ID> \
  --sync-harness \
  --run
```

---

## 4. Vị trí cài đặt đồng bộ trên máy

- **Claude Code Sub-Agents (Workspace)**: `.claude/agents/`
- **Claude Code Sub-Agents (Paseo Runtime)**: `~/.paseo/claude-config/agents/`
- **Claude Code Sub-Agents (User Global)**: `~/.claude/agents/`
- **Workspace Skills**: `.agents/skills/claude-code-sub-agents/`
- **Codex Shared Skills (tự động symlink sang 4 role `supervisor`, `lead`, `peer`, `qc`)**: `~/.codex/skills/claude-code-sub-agents/`
- **Hermes Skills**: `~/.hermes/skills/031_claude_code_sub_agents/`
