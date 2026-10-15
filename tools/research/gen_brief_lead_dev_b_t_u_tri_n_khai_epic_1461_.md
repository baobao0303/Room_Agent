# Auto-Generated Execution Brief (Lead Dev)

- **Profile**: `Lead Dev`
- **Topic / Task**: Bắt đầu triển khai Epic #1461 Hồ sơ khách hàng 360 (Customer 360 Profile).
Nhiệm vụ:
1. Thiết kế DTOs và Customer360Store (Signals) quản lý state của 3 cột (Profile, Purchase, Heatmap, Appointments, Notes) theo đặc tả docs/spec/customer-360-profile-spec.md.
2. Cấu hình route /customers/:id trong mfe-cdp và app-shell.
3. Chỉ đạo QC triển khai trước 4 bộ Unit Test (Tasks #1467..#1470) theo chuẩn TDD trước khi Peer Dev code UI.
- **Task ID**: `1466`
- **Generated At**: `2026-10-15 14:48:15 +0700`
- **Research Report**: `tools/research/research_lead_dev_b_t_u_tri_n_khai_epic_1461_.md`

## 1. Related Session Threads (Knowledge Skill Phase 1)
- `e024b094-17f1-41c6-b03e-ac7d610b511a` (paseo-claude, 3726.0 KB) — `/home/baoltb/.paseo/claude-config/projects/-home-baoltb-Desktop-Paseo-Project/e024b094-17f1-41c6-b03e-ac7d610b511a.jsonl`
- `f23719cc-51a7-45b2-b678-70475f6af014` (paseo-claude, 4120.0 KB) — `/home/baoltb/.paseo/claude-config/projects/-home-baoltb-Desktop-Paseo-Project/f23719cc-51a7-45b2-b678-70475f6af014.jsonl`

## 3. Mandatory Tool-First Execution Checklist
- [x] **Research Tool**: `python3 tools/research/research_agent.py` executed.
- [x] **Context & Thread Discovery**: `python3 tools/agent_progress.py find-thread` & `query_reader.py` executed.
- [ ] **Sub-Agents (`031_claude_code_sub_agents`)**: Invoke `gemini-codebase-analyzer` / `strategic-reasoning-architect` / `slpc-qc-verifier` as needed.
- [ ] **Test / Artifact Generation**: Run `python3 tools/qc_test_generator.py` / `distill_ba_beats.py` / `harness_manager.py`.
- [ ] **Progress Ledger Update**: Log final outcome via `python3 tools/agent_progress.py log`.
