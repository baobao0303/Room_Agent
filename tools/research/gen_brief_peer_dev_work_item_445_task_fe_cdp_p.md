# Auto-Generated Execution Brief (Peer Dev)

- **Profile**: `Peer Dev`
- **Topic / Task**: Work Item #445 [Task]: [FE/CDP] - Áp dụng màu Alias/color/text/interactive và gạch chân khi hover cột Khách hàng
Tại apps/mfe-cdp/src/app/pages/contact/components/contact-list/contact-list.component.html:
- Cột Khách hàng (fullName / customerTpl) hiện đang dùng 'hover:tds-color-primary-500-light' và thiếu underline khi hover.
- Cần cập nhật chuẩn Design System TDS:
  + Khi hover vào text giá trị (Phan Tấn Hải, Đặng Viết Quý,...), đổi màu sang token 'Alias/color/text/interactive' (class: hover:tds-color-text-interactive).
  + Thêm đường kẻ gạch chân (class: hover:underline) và con trỏ chuột pointer (cursor-pointer).
  + Rà soát các cột link/value tương tự trong bảng dữ liệu để đảm bảo đồng nhất chuẩn TDS UI.
- **Task ID**: `445`
- **Generated At**: `2026-10-15 14:10:21 +0700`
- **Research Report**: `tools/research/research_peer_dev_work_item_445_task_fe_cdp_p.md`

## 1. Related Session Threads (Knowledge Skill Phase 1)
- No prior session threads matched keyword; fresh context.

## 3. Mandatory Tool-First Execution Checklist
- [x] **Research Tool**: `python3 tools/research/research_agent.py` executed.
- [x] **Context & Thread Discovery**: `python3 tools/agent_progress.py find-thread` & `query_reader.py` executed.
- [ ] **Sub-Agents (`031_claude_code_sub_agents`)**: Invoke `gemini-codebase-analyzer` / `strategic-reasoning-architect` / `slpc-qc-verifier` as needed.
- [ ] **Test / Artifact Generation**: Run `python3 tools/qc_test_generator.py` / `distill_ba_beats.py` / `harness_manager.py`.
- [ ] **Progress Ledger Update**: Log final outcome via `python3 tools/agent_progress.py log`.
