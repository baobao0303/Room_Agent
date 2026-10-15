# Auto-Generated Execution Brief (Peer Dev)

- **Profile**: `Peer Dev`
- **Topic / Task**: Work Item #448 [Bug]: [Bug] [CDP/Contact]: Khi hover vào cột Khách hàng thì thiếu font-semibold theo đúng thông số Figma
Tại apps/mfe-cdp/src/app/pages/contact/components/contact-list/contact-list.component.html:
- Thông số Figma chuẩn khi hover vào link/giá trị cột Khách hàng:
  + Font: SF Pro Text
  + Weight: 600 (Style: Semibold -> class: hover:font-semibold)
  + Size: 14px, Line height: 20px (tds-body-2)
  + Text decoration: Underline (hover:underline)
  + Color: Alias/color/text/interactive (hover:tds-color-text-interactive)
  + Cursor: pointer (cursor-pointer)
- Hiện tại thiếu 'hover:font-semibold' làm chữ không đậm lên 600 khi hover như thiết kế Figma.
- Cần fix: Thêm 'hover:font-semibold' cùng với 'hover:underline hover:tds-color-text-interactive cursor-pointer'.
- **Task ID**: `448`
- **Generated At**: `2026-10-15 14:18:55 +0700`
- **Research Report**: `tools/research/research_peer_dev_work_item_448_bug_bug_cdp_c.md`

## 1. Related Session Threads (Knowledge Skill Phase 1)
- No prior session threads matched keyword; fresh context.

## 3. Mandatory Tool-First Execution Checklist
- [x] **Research Tool**: `python3 tools/research/research_agent.py` executed.
- [x] **Context & Thread Discovery**: `python3 tools/agent_progress.py find-thread` & `query_reader.py` executed.
- [ ] **Sub-Agents (`031_claude_code_sub_agents`)**: Invoke `gemini-codebase-analyzer` / `strategic-reasoning-architect` / `slpc-qc-verifier` as needed.
- [ ] **Test / Artifact Generation**: Run `python3 tools/qc_test_generator.py` / `distill_ba_beats.py` / `harness_manager.py`.
- [ ] **Progress Ledger Update**: Log final outcome via `python3 tools/agent_progress.py log`.
