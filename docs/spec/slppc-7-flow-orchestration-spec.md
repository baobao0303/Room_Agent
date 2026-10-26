# Architecture Specification: SLPPC 7-Flow Autonomous Orchestration & Prefix Taxonomy

> **Spec Identifier**: `ARCH-SPEC-SLPPC-7-FLOW-ORCHESTRATION-2026-V1`  
> **Topic**: Standard 7 Autonomous Workflow Pipelines, Prefix Directives, and Dual-IDE Routing (Orca & Paseo)  
> **Target Audience**: Supervisor, PM Agent, Lead Dev, Peer Maker Pool, QC Verifier, Security Sentinel  
> **Authors**: Supervisor (Scope & Intent Guard) & Lead Architect  
> **Approved By**: Kev System One (`Feasibility 1.83/3.0`, `Strategic Alignment perfect_fit 68.2%`, `Risk Decision Green`)  
> **Canonical Target**: `docs/spec/slppc-7-flow-orchestration-spec.md`

---

## 1. Executive Summary & Core Philosophy

The SLPPC (`Supervisor - PM - Lead - Peer - QC`) architecture enforces rigorous role boundaries and deterministic governance over software development. In traditional multi-agent systems, agents frequently drift, over-engineer, write unauthorized code, or loop infinitely.

This specification standardizes the **7 Canonical Flow Pipelines** triggered by structured prompt prefixes. Each flow defines an unambiguous state-transition path across the 5 governance gates:

```text
               ┌────────────────────────────────────────────────────────┐
               │              USER (Single Point of Contact)            │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │          GATE 1: SUPERVISOR (Scope & Intent)           │
               └─────────┬──────────────────────────────────┬───────────┘
                         │                                  │
    [NO-CODE PATHS:      │                                  │ [CODE PATHS:
     DISCUSS / REVIEW /  │                                  │  FEATURE / BUGFIX /
     EXPLORE]            ▼                                  ▼  REFACTOR / ADVERSARIAL]
               ┌──────────────────┐               ┌──────────────────┐
               │ COMMITTEE & ADR  │               │ GATE 2: PM INTAKE│
               │ (No Code Edits)  │               │ (Kev System One) │
               └─────────┬────────┘               └─────────┬────────┘
                         │                                  │
                         │                                  ▼
                         │                        ┌──────────────────┐
                         │                        │ GATE 3: LEAD DEV │
                         │                        │ (Zero-Search 5P) │
                         │                        └─────────┬────────┘
                         │                                  │
                         │                        ┌─────────┴────────┐
                         │                        ▼                  ▼
                         │               ┌────────────────┐ ┌────────────────┐
                         │               │ GATE 4: PEER   │ │ GATE 5: QC     │
                         │               │ (Maker Pool)   │ │ (5-Stage ISTQB)│
                         │               │ [Auto-Spawn &  │ │ [Auto-Spawn &  │
                         │               │  Auto-Close]   │ │  Auto-Close]   │
                         │               └────────────────┘ └────────────────┘
                         ▼                                  ▼
               ┌────────────────────────────────────────────────────────┐
               │           TASK RESOLUTION, ARCHIVE & USER REPORT       │
               └────────────────────────────────────────────────────────┘
```

### Key Invariants:
1. **Single Point of Contact (SPOC)**: The User interacts exclusively with the Supervisor. The Supervisor orchestrates subordinates and relays synthesized findings.
2. **Strict Role Fences**:
   - `Supervisor` & `PM`: NEVER touch source code, NEVER inspect low-level code lines (`role_trespass`).
   - `Lead`: NEVER write production code; solely breaks down Zero-Search tasks and reviews architecture.
   - `Peer`: NEVER close tasks (`premature_close`); only submits status `Resolved`.
   - `QC`: Exclusively holds authority to transition tasks to `Closed`.
3. **Ephemeral Resource Model**:
   - Persistent tabs: `Supervisor`, `PM`, `Lead`.
   - Ephemeral tabs: `Peer 1..4`, `QC`, `Design` (Auto-spawned on-demand, auto-closed on `Resolved`/`Closed` to bring RAM to 0).

---

## 2. Standard 7-Flow Taxonomy & Prefix Matrix

| # | Prefix (En / Vi) | Flow Name | Purpose | Sub-Agents / Tools | Code Edits Allowed? |
|---|---|---|---|---|:---:|
| **1** | `[FEATURE]` / `[FORWARD]` / `[THUẬN]` | **Constructive Feature Flow** | New feature, component, DTO, or API adhering to YAGNI. | Peer Dev + `slpc-qc-verifier` | **YES** |
| **2** | `[BUGFIX]` / `[FIX-BUG]` | **Root Cause & Minimal Fix Flow** | Investigate root cause, write failing reproduction test first, fix with minimal diff. | `gemini-codebase-analyzer` + Peer Dev | **YES** |
| **3** | `[ADVERSARIAL]` / `[EDGE-CASE]` / `[NGHỊCH]` | **Boundary & Stress Defense Flow** | Test extreme boundaries, mock network failure/timeout, enforce fail-safe and rollback. | `strategic-reasoning-architect` + QC | **YES** (Defensive) |
| **4** | `[REFACTOR]` / `[CLEANUP]` | **YAGNI Simplification Flow** | Remove dead code, eliminate unused abstractions, adopt native platform/signals with zero logic drift. | `simplify` + Peer Dev | **YES** (Deletions) |
| **5** | `[DISCUSS]` / `[ADR]` / `[THẢO-LUẬN]` | **Architectural Debate & ADR Flow** | Compare architectural trade-offs A vs B, evaluate monorepo impact, record consensus ADR. | `gemini-analyzer` + `strategic-architect` + `record_discussion.py` | **STRICT NO** |
| **6** | `[REVIEW]` / `[AUDIT]` | **Cross-Role Multi-Angle Review Flow** | Audit PR/diff across 3 dimensions: Specs & AC, Angular 18/Strict Typing, Anti-Leak Sentinel. | `gemini-analyzer` + `strategic-architect` + `security_sentinel` | **STRICT NO** |
| **7** | `[EXPLORE]` / `[SCAN]` / `[QUÉT]` | **Deep Codebase Mapping Flow** | Scan high-context monorepo (1M+ tokens), map cross-file dependencies and blast radius. | `gemini-codebase-analyzer` | **STRICT NO** |
| *(8)*| `[TEST]` / `[QC-GATE]` | **5-Stage ISTQB Generation Flow** | Standalone black-box unit/E2E test suite generation for an existing target file. | `tools/qc_test_generator.py` | **TESTS ONLY** |

---

## 3. Detailed Sequence Diagrams & Execution Steps

### 3.1. Flow 1: `[FEATURE]` / `[FORWARD]` (Constructive Feature Flow)
*Goal: Implement new user requirements rapidly with minimal diff, zero boilerplate, and full test compliance.*

```text
User ──► [Supervisor]
           │ 1. Validate Scope & Create Epic (#ID)
           ▼
         [PM Gate (Kev System One)]
           │ 2. Feasibility Score (>=1.5) & Alignment check (<50ms)
           ▼
         [Lead Dev]
           │ 3. Decompose Zero-Search Task (5 mandatory sections)
           │    Triggers Auto-Launch on Orca: Tab "[Peer Dev 1] Code Executor"
           ▼
         [Peer Dev 1 (Ephemeral)]
           │ 4. Implement code adhering to Angular 18 / TDS tokens
           │ 5. Execute local tests -> PASS 100% -> State: Resolved
           │    Triggers Auto-Close on Orca: Peer Tab terminates (RAM -> 0)
           ▼
         [QC Verifier (Ephemeral)]
           │ 6. Auto-Launch on Orca: Tab "[QC] 5-Stage ISTQB Verifier"
           │ 7. Run mechanical verification (Exit Code 0)
           │ 8. Anti-Leak Sentinel scan -> PASS -> State: Closed
           │    Triggers Auto-Close on Orca: QC Tab terminates (RAM -> 0)
           ▼
         [Supervisor] ──► Report Completed Feature to User
```

---

### 3.2. Flow 2: `[BUGFIX]` / `[FIX-BUG]` (Root Cause & Minimal Fix Flow)
*Goal: Prevent regressions by enforcing TDD (Test-Driven Development): reproduce first, then apply minimal diff.*

```text
User: "[BUGFIX] Null pointer when submitting checkout without address"
  │
  ▼
[Supervisor] ──► Intake incident, link bug report
  │
  ▼
[Lead Dev] ─────► Invoke Sub-agent: `gemini-codebase-analyzer`
  │               Trace call stack, locate exact file & anchor
  ▼
[Peer Dev] ─────► Step 1: Write Unit Test reproducing failure (Test MUST FAIL)
  │               Step 2: Apply minimal patch (YAGNI, null-safe check) -> Test PASS
  │               Step 3: Submit state `Resolved`
  ▼
[QC Verifier] ──► Run full regression test suite (Zero broken existing tests)
  │               Confirm fix -> State: `Closed`
  ▼
[Harness Learn] ─► Save root-cause prevention note to `harness_experience` table
```

---

### 3.3. Flow 3: `[ADVERSARIAL]` / `[EDGE-CASE]` (Boundary & Stress Defense Flow)
*Goal: Probe edge cases, simulate race conditions, enforce fail-safe degradation and boundary value handling.*

```text
User: "[ADVERSARIAL] Verify simultaneous payment requests with expired token"
  │
  ▼
[Supervisor] ──► Inject Thinking Directive: `ADVERSARIAL / EDGE-CASE`
  │
  ▼
[Lead Dev] ─────► Invoke Sub-agent: `strategic-reasoning-architect`
  │               Map out failure modes: concurrent locks, null DTOs, network timeout
  ▼
[Peer Dev] ─────► Implement defensive guards (idempotency token, fallback DTO, retry limiter)
  │
  ▼
[QC Verifier] ──► Invoke Sub-agent: `slpc-qc-verifier`
  │               Generate ISTQB Stage 3 (EP/BVA) + Stage 4 (Decision Table 16 combinations)
  │               Verify graceful error responses without application crash
  ▼
[Supervisor] ──► Report: Robustness certified, 100% boundary cases covered
```

---

### 3.4. Flow 4: `[REFACTOR]` / `[CLEANUP]` (YAGNI Simplification Flow)
*Goal: Eliminate technical debt, prune dead code, upgrade to native signals/platform features with 0 logic change.*

```text
User: "[REFACTOR] Modernize CartService from RxJS Subject to Angular 18 Signal"
  │
  ▼
[Lead Dev] ─────► Invoke Sub-agent: `simplify`
  │               Audit dead imports, orphan state, mark non-expanding boundaries
  ▼
[Peer Dev] ─────► Refactor logic using native computed signals / platform primitives
  │               Rule: Shortest working diff wins; NO new external dependencies
  ▼
[QC Verifier] ──► Run 100% existing unit & E2E tests: Must pass with 0 regressions
  │               Verify zero functional behavior change
  ▼
[Supervisor] ──► Report: Codebase compressed, diff reduced, context window clean
```

---

### 3.5. Flow 5: `[DISCUSS]` / `[ADR]` (Architectural Debate & Consensus Flow)
*Goal: Evaluate architectural directions, compare trade-offs A vs B, and record an immutable ADR. STRICTLY PROHIBITS CODE EDITS.*

```text
User: "[DISCUSS] Evaluate JWT vs HttpOnly Cookie for session persistence"
  │
  ▼
[PM Gate] ──────► Kev System One evaluates architectural alignment (<50ms)
  │
  ▼
[Lead & Committee Consultation]:
  ├── 1. `gemini-codebase-analyzer`: Scan existing auth headers and interceptors
  └── 2. `strategic-reasoning-architect`: Formulate Trade-Off Matrix (Security, SSR, Complexity)
  │
  ▼
[Lead Dev] ─────► Synthesize recommendations into Consensus Resolution
  │
  ▼
[ADR Recorder] ─► Mechanical execution: `tools/record_discussion.py`
  │               ├── Writes Minutes: `bmad/rooms/discussions/latest_discussion.md`
  │               └── Writes ADR: `bmad/adrs/ADR_<id>_<slug>.md`
  ▼
[Supervisor] ──► Present Consensus Brief to User (Epic Closed, 0 code touched, RAM = 0)
```

---

### 3.6. Flow 6: `[REVIEW]` / `[AUDIT]` (Cross-Role Multi-Perspective Review Flow)
*Goal: Provide rigorous 360-degree review of git diffs before merging. STRICTLY PROHIBITS CODE EDITS.*

```text
User: "[REVIEW] Audit pull request #45 for security and spec compliance"
  │
  ▼
[Parallel 3-Pillar Review Fan-Out]:
  ├── Pillar 1: `gemini-codebase-analyzer` ➔ Compare diff vs spec.md & AC
  ├── Pillar 2: `strategic-reasoning-architect` ➔ Audit Angular 18 style & Strict Typing
  └── Pillar 3: `security_sentinel` ➔ Audit proprietary tokens, internal IPs & secrets
  │
  ▼
[Lead Dev] ─────► Aggregate findings into 3-Dimensional Review Report:
  │               • Standard Violations (Must-Fix)
  │               • Architectural Suggestions (Nice-to-Have)
  │               • Sentinel Verdict (PASS / VETO)
  ▼
[Supervisor] ──► Deliver actionable review verdict to User
```

---

### 3.7. Flow 7: `[EXPLORE]` / `[SCAN]` (Deep Codebase Mapping Flow)
*Goal: Explore monorepos, map cross-file data flows and predict blast radius. STRICTLY PROHIBITS CODE EDITS.*

```text
User: "[EXPLORE] Trace all downstream consumers of LoyaltyPointService"
  │
  ▼
[Supervisor] ──► Dispatch Sub-agent: `gemini-codebase-analyzer` (1M+ context window)
  │
  ▼
[Codebase Scanner]:
  ├── Parse Nx project graph (`projects/demo-crm-fe`, `projects/demo_pos_fe`)
  ├── Map dependency tree, DI injection points, and HTTP endpoints
  └── Compute Blast Radius Matrix (High / Medium / Low impact files)
  │
  ▼
[Supervisor] ──► Present structural tree map & refactoring safety recommendations
```

---

## 4. Dual-IDE Mechanical Implementation Architecture

The system operates seamlessly across both runtime environments via `tools/dual_ide_hook.py`:

```text
┌───────────────────────────────────────┬───────────────────────────────────────┐
│          ORCA IDE WORKSPACE           │         PASEO CLI / CLAUDE CODE       │
├───────────────────────────────────────┼───────────────────────────────────────┤
│ • Runtime: Visual PTY Desktop         │ • Runtime: Headless Daemon / CLI      │
│ • Interception: `orca terminal send`  │ • Interception: `UserPromptSubmit`    │
│ • Terminal Sync: Auto-renames tab via │ • Thinking Directive: Injected via    │
│   `orca terminal rename` + `/title`   │   `hookSpecificOutput.additionalCtx`  │
│ • Ephemeral Tabs: Peer & QC spawn on  │ • Ephemeral Process: Background fork  │
│   demand, auto-close on completion    │   terminates with exit code 0         │
│ • Kanban Sync: Active workspace card  │ • Progress Ledger: Recorded in        │
│   moves between IN-PROGRESS/COMPLETED │   `.harness_progress.json`            │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

### 4.1. Automatic Prefix Interception (`tools/dual_ide_hook.py`)
Registered in `.claude/settings.json` under `UserPromptSubmit`. When any user prompt arrives:
1. Strips prefix tags while classifying the intent category (`DISCUSS`, `FORWARD`, `REVERSE`, `FIX_BUG`, `REFACTOR`, `REVIEW`, `SCAN`, `TEST`).
2. Detects whether Orca PTY is alive or operating in headless Paseo mode.
3. Injects the **Mandatory Thinking Directive** into the LLM context.
4. If Orca is running, syncs the terminal state and updates `bmad/rooms/supervisor/latest_handoff.md`.

---

## 5. Ready-to-Use Prompt Triggers

Users trigger these flows directly in chat with the Supervisor or via the 1-touch CLI runner:

### 5.1. Chat Trigger Examples:
```text
[FEATURE] Build export customer list to Excel in demo-crm-fe
[BUGFIX] Resolve race condition in CartItemComponent quantity counter
[ADVERSARIAL] Test behavior when API returns HTTP 504 Gateway Timeout
[REFACTOR] Modernize AuthInterceptor to functional interceptor with inject()
[DISCUSS] Evaluate trade-offs between Tailwind utility vs SCSS modules
[REVIEW] Audit git diff on branch feat/checkout-redesign
[EXPLORE] Map all usages of StoreService across customer module
[TEST] Generate 5-Stage ISTQB unit tests for orderService.ts
```

### 5.2. CLI 1-Touch Triggers:
```bash
# Feature development (Autonomous 5-gate pipeline):
./trigger-flow "[FEATURE] Add bulk status update action in shop user list"

# Architectural debate (Produces ADR, 0 code edits):
./trigger-flow "[DISCUSS] Evaluate SQLite vs DynamoDB local storage engine"

# Bugfix with custom test command:
./trigger-flow "[BUGFIX] Fix null pointer on profile page" --test-cmd "pytest tools/tests"
```

---

## 6. Safety Invariants & Reprimand Enforcements

Any attempt to bypass the governance framework triggers immediate automated penalties:

1. **PM Bypass Prevention (`pm_bypass`)**:
   - Every requirement must pass Kev System One evaluation before task breakdown.
   - Enforced by `tools/slppc_flow_guard.py audit`.
2. **Role Trespass Prevention (`role_trespass`)**:
   - Supervisors and Leads attempting code edits are blocked by Git pre-commit hooks and Harness DB role fences.
   - Violation issues an automatic reprimand via `tools/agent_reprimand.py`.
3. **Premature Close Prevention (`premature_close`)**:
   - Only QC holds authority to update tasks to `Closed`. Peer attempts throw `PermissionError`.
4. **Unverified Handoff Prevention (`unverified_handoff`)**:
   - Verbal declarations of "done" without a matching mechanical test run (Exit Code 0) are strictly rejected.

---

## 7. Sub-Agent Context Hygiene & Automatic Purge Protocol (Anti-Context Bloat)

### 7.1. The Threat of Context Bloat & "Ngáo" (Context Rot)
In long-running multi-agent setups, leaving sub-agents alive across multiple tasks inevitably inflates the context window:
- **Cost Escalation**: Passing 200k–500k inactive tokens on every prompt multiplies API consumption by 5x–10x.
- **Latency Spikes**: Time-to-first-token (TTFT) degrades from ~2 seconds to 30+ seconds.
- **Context Rot / Hallucination ("Ngáo")**: LLMs lose track of strict boundaries, hallucinating variable names, obsolete DTOs, or cross-file imports from previous tasks.

### 7.2. The 4 Enforcement Rules of Context Hygiene
1. **Immediate Ephemeral Termination Rule**:
   - Every ephemeral worker (`Peer 1..4`, `QC`, `Design`, `Review`, `Explore`) operates under a **Strict Single-Task Lifespan**.
   - As soon as Peer transitions a task to `Resolved`, its terminal/process is **instantly closed** via `orca terminal close --terminal <handle>` or process exit (`RAM -> 0`).
   - As soon as QC transitions a task to `Closed`, its terminal/process is **instantly closed**.
   - **Zero Tab Leftovers**: Ephemeral agents are NEVER recycled for unrelated subsequent tasks. Every new task starts in a pristine, uncontaminated context window (<15k tokens).
2. **Auto-Compaction for Persistent Roles (`Supervisor`, `PM`, `Lead`)**:
   - Monitored by `tools/agent_context_manager.py`.
   - Threshold: `COMPACT_THRESHOLD_K = 200.0` (200k tokens).
   - Once exceeded, the manager automatically executes `/compact` on the live PTY terminal, shedding 60%–70% of historical tokens while anchoring active invariants into `.harness_progress.json`.
3. **Automated Zombie Watchdog & Reaper (`tools/zombie_reaper.py`)**:
   - Hard timeout ceiling of **300 seconds (5 minutes)** per worker turn.
   - Periodically compares live Orca terminals against active tasks in `harness.db`.
   - Automatically reaps orphan terminals whose parent tasks are already `Closed`, `Resolved`, or cancelled.
4. **Manual Context Purge CLI**:
   - Users or orchestrators can instantly clear all ephemeral workers via:
     ```bash
     ./agent-start clear    # Closes all ephemeral tabs, resets RAM to zero
     ./agent-start stop --all
     ```

---

## 8. Verification & Compliance Checklist

- [x] All 7 flows mapped to distinct prefix tags and sub-agent roles.
- [x] Dual-IDE compatibility certified (Orca PTY live terminals & Paseo CLI headless).
- [x] Context Hygiene & Ephemeral Auto-Purge protocol fully specified and enforced.
- [x] `tools/dual_ide_hook.py` unit tested and registered in `.claude/settings.json`.
- [x] Mechanical execution verified via `./trigger-flow` (Exit Code 0).
- [x] Ephemeral tab auto-launch and auto-close verified (Zero background RAM leakage).
- [x] Documented in `docs/spec/slppc-7-flow-orchestration-spec.md` and indexed in `AGENTS.md`.
