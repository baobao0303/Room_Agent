# Auto-Generated Execution Brief (Peer Dev)

- **Profile**: `Peer Dev`
- **Topic / Task**: Work Item #281 [Bug]: [Bug] [CDP/Shell]: Khi mở CDP Raw Event và sidebar /setting thì nguồn bị mock tĩnh và active route sai
Khắc phục lỗi trên nhánh fix/20261015-RemoveMockSources (projects/wicx-crm-fe):
1. mfe-cdp: Xóa mock sources tĩnh trong raw-event-list, lấy động từ API và tự động phát hiện sources từ eventsList; xóa tenantSubName thừa.
2. app-shell: LayoutStore hỗ trợ generic path cho route con (/setting/employee); chuẩn hóa breadcrumbs và sidebar menu item.
3. Đảm bảo toàn bộ Unit Test (raw-event-list, layout, sidebar) pass 100%.
- **Task ID**: `281`
- **Generated At**: `2026-10-15 13:45:11 +0700`
- **Research Report**: `tools/research/research_peer_dev_work_item_281_bug_bug_cdp_s.md`

## 1. Related Session Threads (Knowledge Skill Phase 1)
- No prior session threads matched keyword; fresh context.

## 3. Mandatory Tool-First Execution Checklist
- [x] **Research Tool**: `python3 tools/research/research_agent.py` executed.
- [x] **Context & Thread Discovery**: `python3 tools/agent_progress.py find-thread` & `query_reader.py` executed.
- [ ] **Sub-Agents (`031_claude_code_sub_agents`)**: Invoke `gemini-codebase-analyzer` / `strategic-reasoning-architect` / `slpc-qc-verifier` as needed.
- [ ] **Test / Artifact Generation**: Run `python3 tools/qc_test_generator.py` / `distill_ba_beats.py` / `harness_manager.py`.
- [ ] **Progress Ledger Update**: Log final outcome via `python3 tools/agent_progress.py log`.
