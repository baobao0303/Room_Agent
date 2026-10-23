# Architecture Specification: Real-Time Pipelines & Real-Time Memory Guard

> **Spec Identifier**: `ARCH-SPEC-REALTIME-PIPELINES-MEMORY-GUARD-2026-V1`  
> **Related Issue**: GitHub Issue #7 (`Tính năng Pipelines check realtime mỗi agent tránh bùa chú + bổ memmory real time`)  
> **Authors**: Supervisor & PM Agent (`pm`)  
> **Approved By**: Kev System One (`Feasibility 1.21/3.0`, `Strategic Alignment perfect_fit 80.64%`, `Risk Lane Green`)  
> **Target Framework**: RTK v1.0 Pipeline Engine + Paseo Lifecycle Hooks + SLPPC State Machine

---

## 1. Context & Architectural Rationale

In high-concurrency multi-agent workspaces (`Room_Agent`), autonomous agents (Supervisor, Lead, Peer 1..4, QC) operate simultaneously across different tasks. Without real-time constraints, three critical failure modes emerge:
1. **"Bùa chú" (Fabricated Success & Silent Pass)**:
   - Maker agents (Peer) asserting that tests pass or code compiles without actually running the mechanical test commands or by masking stderr.
   - Truncating error logs to fool downstream reviewers into believing task completion.
2. **Role Boundary Trespassing (`role_trespass`)**:
   - Management agents (Supervisor, Lead) directly modifying or patching source code files when under pressure or commanded to "triển khai".
   - Bypassing the PM Feasibility & Alignment Gate (`pm_bypass`).
3. **Stale Memory Drift & Mid-Turn Amnesia**:
   - Crucial operational rules learned mid-session (e.g. "always connect PM", "max peer medium", "no hardcoded hex") remain isolated in transient context and are forgotten in subsequent turns or by newly spawned ephemeral sub-agents.
4. **Hook Overhead Latency**:
   - Heavy audit scripts running disk-wide scans on every user prompt cause terminal lag and high CPU consumption.

This specification defines a **Two-Tier Real-Time Pipeline Guard** combined with a **Real-Time Memory Augmentation Protocol** to eliminate hallucinations while maintaining sub-5ms interactive responsiveness.

---

## 2. Two-Tier Real-Time Pipeline Architecture

To address the performance concern raised by the User (*"hook này chạy liên tục cũng căng lắm nha"*), the system separates enforcement into two decoupled tiers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TWO-TIER REAL-TIME PIPELINE GUARD                      │
│                                                                             │
│  [TIER 1: SUB-5MS IN-MEMORY FAST GUARD]                                     │
│  Trigger: On every tool call & prompt submit (RTK Hook before_tool)         │
│  Mechanism: Pure in-memory regex, role flags, and memory cache checks       │
│  Rules:                                                                     │
│    ├── Supervisor/Lead: Block edit/patch/write on production files           │
│    ├── Supervisor: Intercept unverified intake (Check active PM Memo)        │
│    └── Latency: < 5ms guaranteed, 0 disk scans, 0 child processes           │
│                                                                             │
│  [TIER 2: EVENT-GATED DEEP AUDIT]                                           │
│  Trigger: State Transitions on Harness DB & Git Pre-Commit Hook             │
│  Mechanism: Full mechanical audit (slppc_flow_guard.py + AST check)         │
│  Rules:                                                                     │
│    ├── Active ➔ Resolved: Validate real test runner exit code 0             │
│    ├── Resolved ➔ Closed: Exclusive QC sign-off + 5-Stage ISTQB check       │
│    └── Git Pre-Commit: Anti-leak scan + 0 hardcoded hex validation          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Tier 1: Fast In-Memory Guard Specifications
- **Latency Budget**: $\le 5\text{ ms}$.
- **Storage**: In-memory regex matchers and environment flags (`RTK_ACTIVE_ROLE`, `HERMES_PROFILE`).
- **Behavior**:
  - If `ROLE == Supervisor` and tool is `patch` or `write_file` on `projects/` or `tools/`: **IMMEDIATELY DENY** with error:
    `⛔ [ROLE TRESPASS BLOCKED]: Supervisor is strictly forbidden from editing code. Delegate to Lead -> Peer.`
  - If `ROLE == Supervisor` and user requests new task without an active PM Memo in `bmad/rooms/pm/`: **INJECT DIRECTIVE** requiring PM connection.
  - If `ROLE == Lead` and tool targets `projects/*/src/`: **IMMEDIATELY DENY** with error:
    `⛔ [ROLE TRESPASS BLOCKED]: Lead Dev cannot write feature code. Decompose into Zero-Search task for Peer.`

### 2.2 Tier 2: Event-Gated Mechanical Audit
- **Latency Budget**: $200\text{ ms} - 1500\text{ ms}$.
- **Execution Points**:
  1. `harness_manager.py update --state Resolved`: Peer must provide empirical test logs with Exit Code 0 and exact test counts.
  2. `harness_manager.py update --state Closed`: Gated exclusively to `QC`. Rejects any non-QC caller.
  3. `.git/hooks/pre-commit`: Runs `scripts/anti_leak_sentinel.py` and `tools/strict_typing_scanner.py`.

### 2.3 KEV System One Dual-Anchor Pipeline Gate (Head & Tail Verification)
To eliminate subjective human/LLM bias and automate rigor at both boundaries of the spec lifecycle:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 KEV SYSTEM ONE DUAL-ANCHOR PIPELINE ARCHITECTURE            │
│                                                                             │
│  [INTAKE: HEAD-OF-SPEC GATE] ────► PM Agent + KEV System One (<50ms)        │
│  - POST /v1/systemone                                                       │
│  - Feasibility Score (0..3) & Strategic Alignment (perfect_fit, drift)     │
│  - Supervision Risk Decision (Green / Yellow / Red)                         │
│  - Output: Mandatory bmad/rooms/pm/intake_memo_*.md                         │
│                                                                             │
│  [EXECUTION: MAKER INNER LOOP] ──► Lead (Zero-Search) ➔ Peer Devs (Maker)   │
│                                                                             │
│  [VERIFICATION: END-OF-SPEC GATE] ► QC Verifier + KEV System One (<50ms)    │
│  - POST /v1/systemone                                                       │
│  - Test Coverage Depth (0..3) & Regression Risk Score                       │
│  - Mechanical Assertion Validation (0 trivial mocks, 0 hidden errors)       │
│  - Output: Signed-off bmad/rooms/qc/qc_audit_verdict_*.md ➔ Task Closed     │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Head-of-Spec Anchor (PM)**:
   - Mandatory prerequisite before Lead can decompose any Epic or Feature.
   - Evaluates technical viability, resource readiness, and roadmap alignment.
   - Rejects unviable or bloated requirements before code is planned.
2. **End-of-Spec Anchor (QC)**:
   - Mandatory prerequisite before any task or Epic can be transitioned to `Closed`.
   - Re-evaluates final aggregate git diff against original Acceptance Criteria and 17 Web UI Standards.
   - Flags hidden regressions or untested edge cases to prevent "bùa chú" closures.

### 2.4 Profile Permission Fencing Matrix (`profiles/*.md`)

Role boundaries are strictly codified into profile metadata and validated by hooks:

| Role | Profile File | `can_code` | `can_close_task` | Mandatory Gate Flag | Enforcement Behavior |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Supervisor** | `supervisor.md` | `false` | `false` | `mandatory_pm_gate: true`<br>`can_deep_inspect_code: false` | Block write/patch on code; block intake without PM memo. |
| **PM** | `pm.md` | `false` | `false` | `must_use_kev_systemone: true`<br>`can_enforce_loop_ceiling: true` | Enforce <50ms KEV intake; bound loop ceilings ($\le 3-5$). |
| **Lead** | `lead.md` | `false` | `false` | `can_review_architecture: true`<br>`can_decompose_tasks: true` | Block code edits in `projects/`; enforce 5-section Zero-Search. |
| **Peer 1..4** | `peer*.md` | `true` | `false` | `can_run_local_test: true` | Single-ownership only; max model `medium`; submit `Resolved` only. |
| **Peer Design**| `peer_design.md`| `false` | `false` | `can_parse_figma: true` | Output tokens & design specs; max model `medium`. |
| **QC** | `qc.md` | `false` | `true` | `must_verify_with_kev: true`<br>`can_generate_test: true` | Exclusive task closure; mandatory KEV end-of-spec check. |

---

## 3. RTK Pipeline Rules Specification (`pipeline.toml`)

The rules are formally declared in `.rtk/pipeline.toml` leveraging RTK v1.0 syntax:

```toml
schema_version = 1

[pipeline]
name = "slppc-realtime-guard"
extends = ["rtk:default", "rtk:proxy"]
enabled = true

# ==============================================================================
# 1. SUPERVISOR & LEAD ZERO-CODE FENCE (BEFORE TOOL)
# ==============================================================================
[[hook.before_tool.write]]
name    = "supervisor-deny-write"
when    = { "input.path_matches" = "^(projects|tools|libs|apps)/", is_management_role = true }
action  = "deny"
message = "⛔ [ROLE TRESPASS]: Management role cannot write code to ${file_path}. Delegate to Peer."

[[hook.before_tool.edit]]
name    = "supervisor-deny-edit"
when    = { "input.path_matches" = "^(projects|tools|libs|apps)/", is_management_role = true }
action  = "deny"
message = "⛔ [ROLE TRESPASS]: Management role cannot edit code in ${file_path}. Delegate to Peer."

# ==============================================================================
# 2. ANTI-BÙA CHÚ TEST OUTPUT FILTER (AFTER TOOL)
# ==============================================================================
[[hook.after_tool.shell]]
name    = "capture-test-verification"
when    = { command_matches = "^(npm test|nx test|cargo test|pytest|python3 -m unittest)" }
use     = ["ansi", "dedup", "cap"]

# ==============================================================================
# 3. REALTIME PROMPT DIRECTIVES
# ==============================================================================
[[directive]]
name    = "slppc-invariants"
text    = """
[SLPPC INVARIANTS ACTIVE]
- Supervisor: Scope Guard only. ZERO code editing. Connecting with PM is MANDATORY.
- Lead: Architect & Zero-Search delegator only. ZERO feature coding.
- Peer: Maker only. Must test locally. Transition to Resolved only.
- QC: Exclusive authority to close tasks. Requires Exit Code 0 and real test verification.
"""
```

---

## 4. Real-Time Memory Synchronization Protocol ("Bổ Memory Real-Time")

To prevent amnesia across turns and keep all agents aligned with newly discovered rules, the system establishes a **Three-Tier Dynamic Memory Ledger**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REAL-TIME MEMORY SYNCHRONIZATION LEDGER                   │
│                                                                             │
│  [LIVE TURN EVENT] (e.g. User sets rule "max peer medium", "always PM")     │
│       │                                                                     │
│       ├──► 1. Local Volatile Cache: In-memory session context               │
│       │                                                                     │
│       ├──► 2. Durable Working Tree Snapshot:                                │
│       │       - Append to docs/AGENT_PROGRESS.md                            │
│       │       - Update .harness_progress.json state ledger                  │
│       │                                                                     │
│       └──► 3. Persistent Memory Sync (Atomic Batch):                        │
│               - Invoke memory tool (target='user' / target='memory')        │
│               - Flush directly to ~/.hermes/memories/ & Paseo daemon        │
│                                                                             │
│  [SUB-AGENT SPAWN INHERITANCE]                                              │
│  Any ephemeral sub-agent (Peer, QC) automatically reads latest persistent   │
│  invariants from .harness_progress.json on startup (<10ms).                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Memory Update Contract
Whenever a new standing rule, bug trap, or operational constraint is established:
1. **Immediate Atomic Write**: The agent executes `memory(operations=[...])` within the same turn.
2. **Progress Ledger Mirroring**: The constraint is logged into `.harness_progress.json` under `active_invariants`:
   ```json
   {
     "invariants": {
       "peer_model_ceiling": "gemini-3.8-flash-medium",
       "supervisor_zero_code": true,
       "mandatory_pm_gate": true,
       "anti_bua_chu_mechanical_gate": true
     },
     "last_updated": "2026-10-23T16:35:00Z"
   }
   ```
3. **Sub-Agent Context Injection**: When `delegate_task` or `orca agent launch` is called, the child's initialization prompt automatically embeds the current snapshot of `active_invariants`.

---

## 5. Anti-"Bùa Chú" Mechanical Verification Matrix

To eliminate fake reports, test manipulation, and superficial completions:

| Fraud / "Bùa Chú" Pattern | Detection Vector | Enforcement Mechanism | Penalty / Action |
| :--- | :--- | :--- | :--- |
| **Fake Test Pass** ("All tests green" without running test command) | Hook detects no shell call matching test command in `recent_calls`. | Task update to `Resolved` rejected automatically. | Demote task to `Active`, log `untested_code` reprimand. |
| **Masking Stderr** (`command 2>/dev/null` or `|| true`) | RTK `hook.before_tool.shell` inspects regex for error suppression. | Command rewritten to preserve stderr or denied. | Warn agent; reject diff containing error masks. |
| **Premature Close** (Peer marking task `Closed`) | State machine gate in `harness_manager.py`. | State change refused if `assigned_to != qc` and caller $\neq$ QC. | Reject transition; flag `premature_close`. |
| **Hardcoded Test Hacks** (Mocking `expect(true).toBe(true)`) | QC 5-Stage ISTQB scanner audits spec file diffs for trivial assertions. | QC rejects task at Stage 4 (Assertion Depth). | Task returned to Peer with concrete assertion requirements. |
| **Styling Shortcuts** (Raw hex `#1a1a1a` to avoid looking up tokens) | `git_pre_commit_guard.py` & `strict_typing_scanner.py`. | Commit blocked; diff rejected. | Reprimand `hardcoded_hex` (-3 KPI points). |

---

## 6. Implementation Plan & Delivery Checklist

- [x] **Phase 1: PM & Supervisor Analysis**: Kev System One evaluation and Intake Decision Memo authored.
- [ ] **Phase 2: RTK Pipeline Config**: Create `.rtk/pipeline.toml` with fast in-memory guard rules.
- [ ] **Phase 3: Real-Time Memory Syncer**: Enhance `tools/agent_progress.py` to maintain live `active_invariants` in `.harness_progress.json`.
- [ ] **Phase 4: Harness State Gatekeeper**: Ensure `harness_manager.py` rejects state transitions violating anti-bùa chú rules.
- [ ] **Phase 5: Automated Test Suite**: Author `tools/tests/test_realtime_pipeline_guard.py` covering sub-5ms latency and role blocking.
