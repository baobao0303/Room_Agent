# Research Report: [Lead] Verify UC1.01 IAM & Tenant Management

> Generated via **Local BM25 Evidence Synthesizer (query_reader + crm_doc_reader)** on 2026-10-15 10:22:53

## 1. Problem Statement & Scope
- **Research Topic**: `[Lead] Verify UC1.01 IAM & Tenant Management`
- **Workspace**: `/home/baoltb/Desktop/Paseo_Project`
- **Architecture Mode**: 4-Role SLPC (`Supervisor` - `Lead` - `Peer` - `QC`) with `031_claude_code_sub_agents` & `knowledge` skill.

## 2. Core Architecture & Codebase Evidence
### Local Evidence (docs):
🔍 Query: "Lead Verify UC1.01 IAM Tenant Management" | Target: /home/baoltb/Desktop/Paseo_Project/docs
📊 Found 41 matches across 11 files. Top 3 shown:

┌── [Rank #1 | Score: 28.71] /home/baoltb/Desktop/Paseo_Project/docs/spec/example-project/ba/user-management-spec.md:7-8
│   Section: ## 2. User Stories & Acceptance Criteria
├── ────────────────────────────────────────────────────────
│   ## 2. User Stories & Acceptance Criteria
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 28.59] /home/baoltb/Desktop/Paseo_Project/docs/spec/example-project/ba/user-management-spec.md:1-2
│   Section: # Business Analysis Specification: Example Project
├── ────────────────────────────────────────────────────────
│   # Business Analysis Specification: Example Project
└── ────────────────────────────────────────────────────────

┌── [Rank #3 | Score: 27.35] /home/baoltb/Desktop/Paseo_Project/docs/spec/example-project/ba/user-management-spec.md:3-6
│   Section: ## 1. Overview & Business Goal
├── ────────────────────────────────────────────────────────
│   ## 1. Overview & Business Goal
│   - **Mục tiêu**: Xây dựng module quản lý người dùng chuẩn hóa.
│   - **Phạm vi**: Xem danh sách, tìm kiếm, tạo mới và phân quyền người dùng.
└── ────────────────────────────────────────────────────────

### Local Evidence (profiles):
🔍 Query: "Lead Verify UC1.01 IAM Tenant Management" | Target: /home/baoltb/Desktop/Paseo_Project/profiles
📊 Found 4 matches across 4 files. Top 3 shown:

┌── [Rank #1 | Score: 19.78] /home/baoltb/Desktop/Paseo_Project/profiles/lead.md:1-44 (truncated to 30 lines)
│   Section: Top of File
├── ────────────────────────────────────────────────────────
│   ---
│   name: Lead
│   provider: router9
│   model: ag/gemini-3.8-flash-high
│   modeId: bypassPermissions
│   thinkingOptionId: high
│   ---
│   Room role: Lead (Technical Architect & Project Manager in SLPC).
│   
│   MISSION:
│   You hold final technical responsibility in the SLPC (`Supervisor - Lead - Peer - QC`) pipeline. You do not edit production code yourself; you break requirements into subtasks, assign implementation to `peer`, and coordinate independent verification with `qc`.
│   
│   WORKFLOW:
│   1. POLL: Find new Epics/Features (`python3 tools/harness_manager.py list --source bot --assigned-to-profile lead --state New`).
│   2. ANALYZE: Read the codebase, specs, and architecture.
│   3. ASSIGN:
│      - Break down into Tasks with clear Acceptance Criteria (`--ac`) and target source files.
│      - Assign implementation Tasks to `peer`:
│        `python3 tools/harness_manager.py add --type Task --title "[<Module>] - <Action>" --ac "<AC list>" --source bot --created-by-profile lead --assigned-to-profile peer --parent-id <epic_id> --dispatch`
│      - Notify or assign `qc` to generate `Testcase` items and unit test s

### Local Evidence (tools):
🔍 Query: "Lead Verify UC1.01 IAM Tenant Management" | Target: /home/baoltb/Desktop/Paseo_Project/tools
📊 Found 64 matches across 23 files. Top 3 shown:

┌── [Rank #1 | Score: 22.32] /home/baoltb/Desktop/Paseo_Project/tools/research/codex_room_setup_research.md:39-43
│   Section: ### A. Tầng Lãnh đạo (Lead Roles)
├── ────────────────────────────────────────────────────────
│   ### A. Tầng Lãnh đạo (Lead Roles)
│   - **Lead BA**: Sở hữu phạm vi phân tích nghiệp vụ, tạo User Stories, Use Cases và Acceptance Criteria (AC).
│   - **Lead Design**: Sở hữu giao diện UI/UX, Design Tokens, wireframes, và mapping components (Figma sang UI-Lib).
│   - **Lead Dev**: Sở hữu kiến trúc hệ thống, API contracts, schema database, phân rã task và phê duyệt kỹ thuật trước khi merge.
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 10.52] /home/baoltb/Desktop/Paseo_Project/tools/distill_ba_beats.py:1-50 (truncated to 30 lines)
│   Section: Lines 1-50
├── ────────────────────────────────────────────────────────
│   #!/usr/bin/env python3
│   """
│   tools/distill_ba_beats.py - Distills raw BA Use Cases from wicx-crm-doc into
│   atomic, agent-ready Requirement Beats inside obsidian-obsidian/02-Product/04-Requirement-Beats/.
│   """
│   
│   import os
│   import re
│   from pathlib import Path
│   from typing import Dict, Any, List
│   
│   DOC_ROOT = Path("/home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/stories")
│   OBS_TARGET = Path("/home/baoltb/D

### Local Evidence (projects):
🔍 Query: "Lead Verify UC1.01 IAM Tenant Management" | Target: /home/baoltb/Desktop/Paseo_Project/projects
📊 Found 2369 matches across 5879 files. Top 3 shown:

┌── [Rank #1 | Score: 57.56] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/feature-spec.md:1-7
│   Section: # Đặc tả chức năng: Cụm IAM & Quản lý Tenant / Thành viên (Phase 0.5)
├── ────────────────────────────────────────────────────────
│   # Đặc tả chức năng: Cụm IAM & Quản lý Tenant / Thành viên (Phase 0.5)
│   
│   > **Trạng thái:** Đã hoàn thiện đặc tả yêu cầu  
│   > **Phạm vi bao phủ:** UC1.01, UC1.02, UC1.03, UC1.04, UC1.05, UC1.06, UC1.07, UC1.08, UC1.09 (Epic E1 - IAM & Quản lý Tenant/Thành viên Phase 0.5)
│   
│   ---
└── ────────────────────────────────────────────────────────

┌── [Rank #2 | Score: 45.03] /home/baoltb/Desktop/Paseo_Project/projects/wicx-crm-fe/docs/spec-channel-management.md:2-15
│   Section: ## Hệ Thống Quản Lý Kênh Mạng Xã Hội (Social Connections) & Bảo Vệ Phiên Doanh Nghiệp (Tenant Access Guard)
├── ────────────────────────────────────────────────────────
│   ## Hệ Thống Quản Lý Kênh Mạng Xã Hội (Social Connections) & Bảo Vệ Phiên Doanh Nghiệp (Tenant Access Guard)
│   
│   > **Dự án:** WiCX Enterprise CRM Frontend (`apps/mfe-account`, `apps/app-shell`, `libs/features/*`)  
│   > **Tác giả các commit:** baobao0303 (`baobao22.work@gmail.com`)  
│   > **Ngày thực hiện:** 05/10/2026  
│   > **Nhánh:** `feature/20260929-ConnectFacebookPage`  
│   > **Phạm vi commit được revi

### CRM BA Spec Evidence:
📄 User Story: UC1.01 (/home/baoltb/Desktop/wicx-crm-doc/BA/implementation-artifacts/stories/Phase 0.5_User_Stories/UC1.01 - Đăng nhập hệ thống qua WiAccount.md) [Total lines: 335] [Showing first 59 lines]
============================================================
# Use Case UC1.01 - Đăng nhập hệ thống qua WiAccount (Phase 0.5)

| title                                              | use_case_id | story_id | sprint     | epic                                             | status  | priority  | created   |
| -------------------------------------------------- | ----------- | -------- | ---------- | ------------------------------------------------ | ------- | --------- | --------- |
| Use Case UC1.01 - Đăng nhập hệ thống qua WiAccount | UC1.01      | US-E1.2  | Sprint 1–2 | Epic E1 - Truy cập hệ thống (IAM đủ dùng nội bộ) | pending | Must Have | 7/30/2026 |

---

> **Phạm vi Phase 0.5 (so với Phase 1):** bỏ toàn bộ luồng **lời mời vào doanh nghiệp** (0.5 thêm người thẳng bằng SĐT — UC1.05); bỏ **RBAC/vai trò** — mọi thành viên trong doanh nghiệp cùng quyền. Actor dùng "Người dùng" thay "Quản trị viên/Nhân viên".  
> **Doanh nghiệp tạo qua UI (UC1.07)** — người dùng chưa có doanh nghiệp (hoặc muốn tạo thêm) tự tạo doanh nghiệp trong hệ thống, trở thành thành viên đầu tiên. Màn 2a "Đề xuất tạo doanh nghiệp" + nút "+" ở Chọn doanh nghiệp → mở form tạo doanh nghiệp (UC1.07). Phase 0.5 cap 5 doanh nghiệp / 1 user (dogfood — BR1.07-7); đạt cap 5 → nút "+" disable. Multi-org đầy đủ (vượ

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
