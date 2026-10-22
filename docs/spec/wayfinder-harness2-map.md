# Wayfinder Map: Reverse Engineering & Architectural Specification of Harness²

## Destination
Hoàn thành bộ tài liệu đặc tả kiến trúc toàn diện `docs/spec-harness2-architecture.md` giải mã 100% mã nguồn Google Research Harness² (Recursive Agent Harnessing for an Open World), bao gồm cơ chế đệ quy, execution substrate, benchmark runners, và hệ thống lưu trữ kinh nghiệm agent.

## Notes
- **Target Repository**: `projects/harness2`
- **Domain**: Recursive Agent Harnessing, Multi-Agent Orchestration, Substrate Sandboxes.
- **Skills bắt buộc**: `rea-reverse-engineering`, `wayfinder`, `to-spec`, `lead-review`, `qc`.
- **Standing Preferences**:
  - Không commit vào Git (`projects/harness2` nằm trong `.gitignore`).
  - Phân bổ 4 bậc Peer theo năng lực: Peer 4 (Extra/Max), Peer 3 (High), Peer 2 (Medium), Peer 1 (Low).
  - Review liên tục qua cổng 7 điểm của Lead Dev.

## Decisions so far
- [Epic #3949 - Thiết lập phạm vi nghiên cứu Harness²](bmad/rooms/tasks/3949/handoff_supervisor.md): Xác định kiến trúc tổng thể 39 Python modules và 3 runners benchmarks.
- [Phân tầng 4 bậc mô hình cho Peer Devs](docs/AGENT_PROGRESS.md): Peer 1 (Low), Peer 2 (Medium), Peer 3 (High), Peer 4 (Extra/Max).

## The Frontier (Open Decision Tickets)

### 1. [Ticket #3951] Cơ chế Vòng lặp Đệ quy (Core Recursion Engine)
- **Question**: Cơ chế lập lịch song song (parallel) vs tuần tự (sequential) giữa rollout (4k) và improvement stage (3k) trong `harness2/core/recursion.py` hoạt động ra sao? Làm thế nào proposer sinh đề xuất tối ưu harness mà không vi phạm budget token?
- **Assignee**: `Peer Dev 4 (Extra Tier)`
- **Type**: `wayfinder:research`

### 2. [Ticket #3952] Khung Thực thi Substrate (Codex & OpenCode Bridges)
- **Question**: `harness2/substrate/base.py`, `codex.py`, `opencode.py` đóng gói môi trường thực thi (sandbox), format prompt, và phân giải output từ CLI agent như thế nào?
- **Assignee**: `Peer Dev 3 (High Tier)`
- **Type**: `wayfinder:research`

### 3. [Ticket #3953] Pipeline Đánh giá Benchmark & Presets
- **Question**: Các benchmark `JobBench`, `WorkBuddy`, `Lab` được tích hợp, render và chấm điểm qua `core/judge.py` và `wb_render.py` như thế nào?
- **Assignee**: `Peer Dev 2 (Medium Tier)`
- **Type**: `wayfinder:research`

### 4. [Ticket #3954] Cơ chế Tích lũy Tri thức Harness (Library & Runmark)
- **Question**: `harness2/core/library.py` và `runmark.py` lưu trữ, tìm kiếm và tái sử dụng các mẫu harness tối ưu giữa các domain nhiệm vụ ra sao?
- **Assignee**: `Lead Dev (Architect & Reviewer)`
- **Type**: `wayfinder:task`

## Not yet specified (Fog of War)
- [ ] Khả năng ánh xạ và chuyển giao cơ chế Recursive Harnessing của Google vào mô hình SLPC của Paseo/Hermes.
- [ ] Cơ chế tự sinh testcases và chấm điểm độc lập của `judge.py` đối chiếu với chuẩn ISTQB 5-Stage hiện có của QC.

## Out of scope
- Cài đặt toàn bộ môi trường nặng JAX/GPU hoặc chạy sweep benchmark thực tế ngốn hàng ngàn USD token trên cloud Google.
- Thay đổi mã nguồn nội bộ của `projects/harness2` (chỉ reverse engineer và viết spec kiến trúc).
