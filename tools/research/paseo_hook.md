# Research Report: paseo hook

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-19 11:00:37

## 1. Problem Statement & Scope
- **Research Topic**: `paseo hook`
- **Workspace**: `/home/baoltb/Desktop/Room_Agent`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "paseo hook" | Target: /home/baoltb/Desktop/Room_Agent/docs
📊 Found 30 matches across 20 files. Top 3 shown:

┌── [Rank #1 | Score: 38.87] /home/baoltb/Desktop/Room_Agent/docs/spec/codex-room-setup-spec.md:19-31
│   Section: ### 1.1. Pin phiên bản Paseo bất biến (`paseo/source.toml`)
├── ────────────────────────────────────────────────────────
│   ### 1.1. Pin phiên bản Paseo bất biến (`paseo/source.toml`)
│   - **Upstream repository**: `https://github.com/getpaseo/paseo.git`
│   - **Release tag**: `v0.8.0`
│   - **Branch nội bộ**: `codex-room-stable`
│   - **Verified Commit SHA**: `b8e24677e12b226c7c38c1c3a40649daa9f1152f`
│   - **Target cài đặt mặc định**: `~/projects/supervisors/paseo` (CLI symlink tại `~/.local/bin/paseo` trỏ tới `packages/cli/bin/paseo`).
│   - **Cơ chế khóa toàn vẹn (`scripts/install-paseo`)**:
│     - Đối chiếu trực tiếp `refs/tags/v0.8.0` từ remote với `verified_commit` (40 ký tự hex).
│     - Kiểm tra SHA-256 của `package-lock.json` trước và sau khi chạy `npm ci`; nếu `npm ci` làm thay đổi `package-lock.json` hoặc sinh thêm Git hook ngoài `lefthook`, quá trình cài đặt lập tức báo lỗi và khôi phục file gốc.
│     - Biên dịch bằng `npm run build:server:clean` và kiểm tra sự tồn tại thực tế (không phải symlink) của `packages/cli/dist/index.js` và `packages/server/dist/scripts/supervisor-entrypoint.js`.
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 27.53] /home/baoltb/Desktop/Room_Agent/docs/spe

### Local Evidence (profiles):
⚠️ No matching content found for query 'paseo hook' in /home/baoltb/Desktop/Room_Agent/profiles (Scanned 4 files, 4 sections).

### Local Evidence (tools):
🔍 Query: "paseo hook" | Target: /home/baoltb/Desktop/Room_Agent/tools
📊 Found 22 matches across 85 files. Top 3 shown:

┌── [Rank #1 | Score: 68.55] /home/baoltb/Desktop/Room_Agent/tools/paseo_hooks.py:626-660 (truncated to 30 lines)
│   Section: Lines 626-660
├── ────────────────────────────────────────────────────────
│   p_plugin.add_argument("--payload-file", help="Path to JSON payload file")
│       p_plugin.add_argument("--json", action="store_true", help="Output JSON")
│       p_plugin.set_defaults(func=cmd_plugin_event)
│   
│       # 3. worktree: pre-create, post-create, pre-destroy
│       p_wt = sub.add_parser("worktree", help="Execute worktree lifecycle hook (pre-create, post-create, pre-destroy)")
│       p_wt.add_argument("phase", choices=["pre-create", "post-create", "pre-destroy"], help="Worktree hook phase")
│       p_wt.set_defaults(func=cmd_worktree)
│   
│       # 4. install
│       p_install = sub.add_parser("install", help="Enable Paseo plugins & terminal hooks and install slpc-lifecycle-hooks")
│       p_install.set_defaults(func=cmd_install)
│   
│       # 5. status
│       p_status = sub.add_parser("status", help="Inspect status of all 3 Paseo hook layers and recent events")
│       p_status.add_argument("--limit", type=int, default=15, help="Max recent hook events to display")
│       p_status.set_defaults(func=cmd_status)
│   
│       # 6. clean-rooms: purge closed task memos & prune old handoffs
│       p_clean = sub.add_parser("clean-rooms", help=

## 3. Findings & Spec Mapping
- **Documentation & Spec Targets**: `docs/spec/`, `AGENTS.md`, `CLAUDE.md`, `docs/AGENT_PROGRESS.md`.
- **Sub-Agents Available**:
  - `gemini-codebase-analyzer`: Holistic 1M+ token context scan.
  - `strategic-reasoning-architect`: Deep architectural trade-off and root-cause analysis.
  - `slpc-qc-verifier`: 5-Stage ISTQB Testcase & Unit Test generation (`tools/qc_test_generator.py`).

## 4. Trade-offs & Edge Cases
- Maintain single moving write-scope ownership per Peer.
- Ensure all business rules and boundary values are verified via deterministic unit tests before `QC` transitions any item to `Closed`.

## 5. Actionable Recommendations & Next Generation Steps
1. **Task / Spec Generation**: Register or update Work Items via `python3 tools/harness_manager.py`.
2. **Test Generation (5-Stage ISTQB)**: Run `python3 tools/qc_test_generator.py --source <target_file> --spec <spec_file> --sync-harness`.
3. **Progress Ledger Update**: Log completion via `python3 tools/agent_progress.py log --agent "<Role>" ...`.
