# Research Report: [Supervisor] Dac ta quy trinh migration tu Nx Webpack sang Rsbuild hoac setup du an moi

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-16 13:56:17

## 1. Problem Statement & Scope
- **Research Topic**: `[Supervisor] Dac ta quy trinh migration tu Nx Webpack sang Rsbuild hoac setup du an moi`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Supervisor Dac ta quy trinh migration tu Nx" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 2376 matches across 30 files. Top 3 shown:

┌── [Rank #1 | Score: 53.89] /home/baoltb/Desktop/Paseo_Project/docs/spec/codex-room-setup-spec.md:354-357
│   Section: ## 9. Mở rộng lên 4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`) & Tích hợp `031_claude_code_sub_agents`
├── ────────────────────────────────────────────────────────
│   ## 9. Mở rộng lên 4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`) & Tích hợp `031_claude_code_sub_agents`
│   
│   Vì hệ thống của chúng ta vận hành theo mô hình **4 Role (`SLPC`: `Supervisor - Lead - Peer - QC`)** có thêm cực **`QC`** độc lập (Independent Quality Gate & ISTQB 5-Stage Test Specialist), toàn bộ hệ thống `codex-room-setup`, Paseo, Claude Code, Codex và Hermes đã được nâng cấp từ 3 role lên **4 role** và tích hợp bộ Subagent Skill từ [`hoangnb24/storage/tree/main/031_claude_code_sub_agents`](https://github.com/hoangnb24/storage/tree/main/031_claude_code_sub_agents):
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 51.28] /home/baoltb/Desktop/Paseo_Project/docs/spec/wicx-crm-fe/design/customer-detail-drawer.md:468-469
│   Section: ## 7. Câu hỏi mở / Quyết định
├── ────────────────────────────────────────────────────────
│   ## 7. Câu hỏi mở / Quyết định
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 50.94] /home/baoltb/Desktop/Paseo_Project/docs/spec/

### Local Evidence (profiles):
🔍 Query: "Supervisor Dac ta quy trinh migration tu Nx" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 17.18] /home/baoltb/Desktop/Paseo_Project/profiles/supervisor.md:1-39 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Supervisor
│   provider: router9
│   model: ag/claude-sonnet-5-5-medium
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: Supervisor (Scope & Intent Guard - SLPC Orchestrator).
│   
│   MISSION:
│   You are the project referee in the SLPC (`Supervisor - Lead - Peer - QC`) architecture. Do not write code, design systems, or review code.
│   Your job:
│   1. Ensure Lead, Peer, and QC do not drift from the User's original intent.
│   2. Track progress through the Harness DB.
│   3. Escalate to the User for decisions on: scope changes, data-deletion risk, cost, or production deploys.
│   
│   WORKFLOW:
│   - Check the board with `python3 tools/harness_manager.py list --source bot --state Active` or `--state Resolved` or `--state Blocked`.
│   - WHEN the User gives a new request: run `python3 tools/harness_manager.py add --type Epic --title "[CDP] - <name>" --source bot --created-by-profile supervisor --assigned-to-profile lead --dispatch` to assign it to Lead.
│   - WHEN a task stays `Blocked` too long or Lead goes out of scope: warn Lead via comment/Task, or tell the User directl

### Local Evidence (tools):
🔍 Query: "Supervisor Dac ta quy trinh migration tu Nx" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 1041 matches across 179 files. Top 3 shown:

┌── [Rank #1 | Score: 172.66] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_dac_ta_quy_trinh_setup_ch.md:1-4
│   Section: # Research Report: [Supervisor] Dac ta quy trinh setup checklist kiem tra va huong dan viet code Rsbuild Angular MFE
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Dac ta quy trinh setup checklist kiem tra va huong dan viet code Rsbuild Angular MFE
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-16 13:49:31
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 103.55] /home/baoltb/Desktop/Paseo_Project/tools/research/research_supervisor_dac_ta_setup_project_base.md:1-4
│   Section: # Research Report: [Supervisor] Dac ta setup project_base Angular su dung Rsbuild chi tiet
├── ────────────────────────────────────────────────────────
│   # Research Report: [Supervisor] Dac ta setup project_base Angular su dung Rsbuild chi tiet
│   
│   > Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-16 09:53:10
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 92.95] /home/baoltb/Desktop/Paseo_Project/tools/research/gen_brief_supervisor_dac_ta_quy_trinh_setup_ch.md:1-8
│   Section: #

### CRM BA Spec Evidence:
🔍 Query: "Supervisor Dac ta quy trinh migration tu Nx" | Category: all
📊 Tìm thấy 5135 kết quả (Đã quét 785 files, 8414 sections). Top 3:

┌── [Rank #1 | Score: 113.37] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/deploy/k8s/staging-setup.yaml:67-72
│   Section: # ở nhóm trên không cấp được quyền nào cả. Cần cho bước chạy migration bằng psql (deploy/README.md §5.4).
├── ────────────────────────────────────────────────────────
│   # ở nhóm trên không cấp được quyền nào cả. Cần cho bước chạy migration bằng psql (deploy/README.md §5.4).
│   - apiGroups: [""]
│     resources: ["pods/exec", "pods/portforward"]
│     verbs: ["create"]
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 113.37] /home/baoltb/Desktop/wicx-crm-doc/WiCX/wicx-crm/deploy/k8s/staging-setup.yaml:67-72
│   Section: # ở nhóm trên không cấp được quyền nào cả. Cần cho bước chạy migration bằng psql (deploy/README.md §5.4).
├── ────────────────────────────────────────────────────────
│   # ở nhóm trên không cấp được quyền nào cả. Cần cho bước chạy migration bằng psql (deploy/README.md §5.4).
│   - apiGroups: [""]
│     resources: ["pods/exec", "pods/portforward"]
│     verbs: ["create"]
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 80.14] /home/baoltb/Desktop/wicx-crm-doc/WiCX/docs/deploy/k8s/staging-setup.yaml:61-61
│   Section: # PVC của wicx-postgres do StatefulSet controller tạo nên user không cần quyền create; nhưn

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
