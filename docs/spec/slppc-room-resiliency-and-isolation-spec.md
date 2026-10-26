# Architecture Specification: SLPPC Room Resiliency & Ephemeral Isolation

> **Spec Identifier**: `ARCH-SPEC-SLPPC-ROOM-RESILIENCY-ISOLATION-2026-V1`  
> **Topic**: Git Worktree Isolation, Automated Staging Rollback, Pre-flight Doctor, Desktop Notifications, and Zero-RAM CLI Status HUD  
> **Target Audience**: Supervisor, PM Agent, Lead Architect, Maker Pool (Peer 1..4), QC Gate, Operators  
> **Authors**: Supervisor (Scope & Intent Guard) & Lead Architect  
> **Approved By**: Kev System One (`Feasibility 1.85/3.0`, `Strategic Alignment perfect_fit 71.4%`, `Risk Decision Green`)  
> **Canonical Target**: `docs/spec/slppc-room-resiliency-and-isolation-spec.md`

---

## 1. Executive Summary & Problem Statement

The `Room_Agent` workspace has established an autonomous 5-gate pipeline (`Supervisor ➔ PM ➔ Lead ➔ Peer ➔ QC`), ephemeral sub-agent lifecycles, and RTK token compression. However, production multi-agent orchestration reveals 5 structural vulnerabilities:

1. **Shared Workspace Collision**: Multiple concurrent Peer agents operating directly inside the root working tree collide on uncommitted files, creating race conditions and corrupted git states.
2. **Polluted Workspace on Rejection**: When QC rejects a task or local tests fail, leftover dirty files remain in the working tree, contaminating subsequent tasks.
3. **Blind Execution without Pre-flight Validation**: Pipelines fail mid-flight if Tailscale drops connection to Kev System One (:8008), if uncommitted files exist, or if RTK binaries are misconfigured.
4. **Operator Blindness**: Long-running autonomous tasks (1–3 minutes) lack passive ambient alerts, forcing operators to poll CLI logs constantly.
5. **Observability Dilemma**: Heavy web-based visualizers (such as the deprecated Flow UI on port 8088) drain workstation RAM and require open browser tabs. A zero-RAM, terminal-native HUD is required.

This specification provides the comprehensive architecture to resolve all 5 vulnerabilities with zero external dependencies.

---

## 2. Technical Architecture: 5 Resiliency Pillars

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SLPPC ROOM RESILIENCY ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PILLAR 3: PRE-FLIGHT DOCTOR]                                              │
│  • Network Connectivity (Kev System One :8008 < 150ms)                      │
│  • Clean Working Tree Check (Zero dirty files)                              │
│  • Binary & Pipeline Health (rtk verify 151/151 PASS)                       │
│                         │                                                   │
│                         ▼ [PASS]                                            │
│  [PILLAR 1: GIT WORKTREE ISOLATION]                                         │
│  • Dynamic worktree: `.worktrees/task-<id>`                                 │
│  • Dedicated branch: `ephemeral/task-<id>`                                  │
│  • Peer operates in 100% isolated directory                                 │
│                         │                                                   │
│          ┌──────────────┴──────────────┐                                    │
│          ▼ [SUCCESS: Resolved]         ▼ [FAILURE: Rejected/Aborted]        │
│  [MERGE & CLOSE]               [PILLAR 2: AUTO-ROLLBACK & QUARANTINE]       │
│  • QC signs off Exit 0         • Archive dirty patch to `bmad/rooms/archive`│
│  • Merge back to active branch • Hard reset / purge worktree directory      │
│  • Prune ephemeral worktree    • Revert main tree to clean baseline         │
│                         │                      │                            │
│                         └──────────┬───────────┘                            │
│                                    ▼                                        │
│  [PILLAR 4: AMBIENT DESKTOP & SYSTEM NOTIFICATIONS]                         │
│  • Native Desktop Toast: `notify-send` (Linux) / `osascript` (macOS)        │
│  • Sound Chime & Orca Terminal Notice on Closed 🟢 or Blocked 🔴            │
│                                    │                                        │
│                                    ▼                                        │
│  [PILLAR 5: ZERO-RAM CLI LIVE STATUS HUD]                                   │
│  • 1-Line ANSI Terminal Status Line (`./agent-start watch`)                 │
│  • Real-time Agent Matrix, Concurrency Ceiling, RTK Savings, RAM: 0MB       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Pillar 1: Git Worktree Isolation per Ephemeral Worker

### 3.1. Worktree Lifecycle Specification
To guarantee **Single-Ownership Invariant** across concurrent workers, no two agents may write to the same physical directory:

```text
Root Workspace: /home/baoltb/Desktop/Room_Agent/
                   │
                   ├── Active Persistent Branch: `feat/unified-room-agent-supervision`
                   │
                   └── .worktrees/ (Added to .gitignore)
                         ├── task-4702/  (Ephemeral Worker: Peer 1)
                         ├── task-4704/  (Ephemeral Worker: Peer 2)
                         └── task-4706/  (Ephemeral Worker: Peer 3)
```

### 3.2. Automated Provisioning & Pruning Protocol
1. **Creation upon Lead Dispatch**:
   When Lead assigns a Task `#<id>` to Peer:
   ```bash
   git worktree add -b "ephemeral/task-<id>" ".worktrees/task-<id>" HEAD
   ```
2. **Binding to Sub-Agent**:
   The Orca terminal or background subprocess is launched with working directory set to `.worktrees/task-<id>`.
3. **Merge-Back on QC Approval**:
   When QC issues `Closed` verdict:
   ```bash
   git merge --ff-only "ephemeral/task-<id>"
   git worktree remove --force ".worktrees/task-<id>"
   git branch -D "ephemeral/task-<id>"
   ```
4. **Emergency Pruning**:
   If an agent crashes or times out (Watchdog 300s):
   `tools/zombie_reaper.py` automatically runs `git worktree prune` and purges abandoned directories.

---

## 4. Pillar 2: Automated Rollback & Staging Quarantine (Fail-Safe Recovery)

### 4.1. The Threat of Contaminated Workspace
When a task fails local unit tests or is REJECTED by Lead/QC, dirty uncommitted modifications linger in the workspace. If a second task begins, it inherits broken code, resulting in compounding build failures.

### 4.2. Automated Quarantine Mechanism
Upon transition to `Rejected`, `Blocked`, or `Aborted`:
1. **Snapshot Dirty State**:
   Save the diff as an empirical evidence artifact:
   ```bash
   git diff > "bmad/rooms/archive/rejected_task_<id>_$(date +%s).patch"
   ```
2. **Enforce Clean Slate**:
   - For worktree mode: Instantly delete the ephemeral worktree:
     ```bash
     git worktree remove --force ".worktrees/task-<id>"
     ```
   - For root working tree fallback:
     ```bash
     git reset --hard HEAD
     git clean -fd -e bmad/rooms/ -e .harness*
     ```
3. **State Transition**:
   The task is moved to `Blocked` on Harness DB with a recorded violation minutes (`tools/agent_reprimand.py`).

---

## 5. Pillar 3: Pre-flight Doctor & Health Check

### 5.1. Pre-flight Matrix (`tools/harness_doctor.py` / `./scripts/doctor`)
Before initiating any autonomous pipeline run (`./trigger-flow` or `scripts/run_pipeline.py`), the system executes a 5-point non-interactive health check:

| # | Check Item | Target | Failure Policy |
|---|---|---|---|
| **D-01** | **Git Working Tree Cleanliness** | `git status --porcelain` returns 0 dirty files (excluding ignore) | **ABORT**: Warn user to commit or stash before running autonomous agent. |
| **D-02** | **Kev System One Connectivity** | HTTP GET `http://127.0.0.1:8008/v1/systemone` responds `< 150ms` | **FALLBACK**: Use deterministic heuristic fallback without hanging CLI. |
| **D-03** | **RTK Proxy Integrity** | `rtk verify` passes 151/151 tests; `PreToolUse` hook active | **AUTO-REPAIR**: Execute `rtk trust --yes && rtk init -g --auto-patch`. |
| **D-04** | **Orca Desktop Runtime** | If Orca in PATH: `orca status --json` verifies reachable runtime | **AUTO-LAUNCH**: Run `orca open` if stopped; else fallback to Paseo CLI. |
| **D-05** | **Room Ledger Hygiene** | Verify single `latest_handoff.md` per role, `room_ledger.json` size `< 50KB` | **AUTO-CLEAN**: Run `python3 tools/room_cleanup.py`. |

### 5.2. Non-Interactive CLI Interface
```bash
python3 tools/harness_doctor.py --check-only   # Exits 0 if healthy, non-zero if blocked
python3 tools/harness_doctor.py --fix          # Automatically repairs soft failures
```

---

## 6. Pillar 4: Ambient Desktop & System Notification Dispatcher

### 6.1. Notification Policy
To free the operator from staring at CLI transcripts, ambient notifications are emitted on critical state events:
- 🟢 **TASK_CLOSED**: Feature or bugfix successfully certified by QC (ISTQB tests pass, Exit 0).
- 🔴 **TASK_BLOCKED**: Build panic, architectural reject, or human decision required.
- 🟡 **WATCHDOG_INTERRUPT**: 300s timeout reached; zombie terminal reaped.
- 📋 **ADR_RECORDED**: Architectural discussion completed and ADR committed.

### 6.2. Cross-Platform Zero-Dependency Dispatcher (`tools/desktop_notifier.py`)
```python
def notify(title: str, message: str, level: str = "info"):
    # 1. Linux Desktop (libnotify)
    if shutil.which("notify-send"):
        urgency = "critical" if level == "error" else "normal"
        subprocess.run(["notify-send", "-u", urgency, "-a", "SLPPC Orchestrator", title, message])

    # 2. macOS Desktop (AppleScript)
    elif sys.platform == "darwin" and shutil.which("osascript"):
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])

    # 3. Terminal Bell (Standard ANSI)
    sys.stdout.write("\a")
    sys.stdout.flush()
```

---

## 7. Pillar 5: Zero-RAM CLI Live Status HUD

### 7.1. Terminal-Native Observability (`./agent-start watch`)
Replaces deprecated web dashboards with a zero-RAM, single-window terminal status line:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🚀 SLPPC LIVE HUD │ WORKSPACE: active │ HARNESS TASK: #4706 [IN-PROGRESS]   │
├─────────────────────────────────────────────────────────────────────────────┤
│ ROLES: [Supervisor: 🟢 ALIVE] [PM: 🟢 ALIVE] [Lead: 🟢 ALIVE] [Peer: ⚡ RUN] │
│ QC VERIFIER: 💤 IDLE | ACTIVE WORKTREE: .worktrees/task-4706                │
│ RTK ECONOMY: 281 cmds | 51.1K tokens saved (23.9%) | RAM LEAKAGE: 0 MB      │
│ LAST OUTCOME: Task #4704 CLOSED (Exit 0) | Dual-Anchor Certified: ✅        │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Update Frequency**: 1.5 seconds.
- **Resource Footprint**: `< 5MB RSS`, zero browser dependencies, zero open ports.
- **Auto-Exit**: Closes automatically when all work items reach terminal state (`Closed` or `Blocked`).

---

## 8. Pillar 6: Task Collision, Supervisor Singleton SPOC & Single-Ownership Lock Protocol

### 8.1. The Threat of Duplicate Supervisors & Task Overwrite ("Task Đè")
When multiple user prompts arrive in rapid succession, or when multiple chat windows are opened, naive multi-agent systems suffer from:
1. **Duplicate Supervisors**: Spawning two parallel supervisor agents that issue conflicting directives and scramble the backlog.
2. **Task Clobbering ("Task Đè")**: A new incoming task overwriting an in-flight task's status or modifying the same files concurrently.
3. **Ghost Sub-agents**: Multiple Peer workers modifying the same git branch, causing merge panics.

### 8.2. Supervisor Singleton & SPOC Invariant
- **Rule**: Within any given workspace room, **exactly ONE Supervisor instance holds governance authority** at any moment.
- **Enforcement**:
  * The primary terminal handle is locked in `bmad/rooms/agent_terminals.json`.
  * If a second prompt arrives in another terminal/session, it MUST bind to the existing Supervisor session via `bmad/rooms/supervisor/latest_handoff.md` and read live state from `harness.db`.
  * **Zero Duplicate Managers**: Spawning a second supervisor process is strictly prohibited and rejected fail-closed.

### 8.3. Tri-State Task Collision Resolution Matrix
When a new user prompt arrives while an active task is already executing, the Supervisor applies the **Tri-State Resolution Matrix**:

```text
               New Incoming Prompt Arrives
                           │
                           ▼
          [Inspect Active Tasks on Harness DB]
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
     [SCENARIO A]    [SCENARIO B]    [SCENARIO C]
    Same Scope /    Different Task  Disjoint Scopes
    AC Extension    Touches Same    (Different Files
                    Files / DTOs     & Modules)
           │               │               │
           ▼               ▼               ▼
      [BATCHING]      [LOCK & QUEUE]  [PARALLEL WORKTREES]
    Append new AC   Queue in Backlog  Spawn independent
    to active task; as State: `New`   Worktree:
    DO NOT create   Hold until active `.worktrees/task-<id>`
    new task ticket task is `Closed`  Concurrency <= 3
```

| Scenario | Condition | System Action | File Impact |
|---|---|---|---|
| **A: Scope Batching** | Prompt amends or extends in-flight requirement. | **DO NOT create new task**. Append AC to current Task/Epic description. | Single owner continues without restart. |
| **B: Lock & Queue** | New requirement touches any file already modified by an `Active` task. | **Block & Queue**. Register task in Backlog with state `New` or `Blocked`. Unblock only when active task transitions to `Closed`. | Zero collision; strict FIFO file isolation. |
| **C: Parallel Worktrees** | New requirement touches 100% disjoint modules/files AND active workers $< 3$. | **Isolate & Execute**. Provision dedicated worktree `.worktrees/task-<id>`. Run concurrent ephemeral Peer. | Complete git isolation on separate branch. |

### 8.4. Single-Ownership File Locking Invariant
- **Fundamental Law**: *"One file, one owner, one task at any single point in time."*
- **Mechanical Validation**:
  * Before assigning a Task to `Active`, `HarnessManager` verifies that no target files in the Zero-Search spec are registered under another `Active` work item.
  * If a collision is detected, `HarnessManager` rejects the transition with:
    `PermissionError: Target file '<path>' is currently locked by active Task #<active_id>. Queued in Backlog.`

---

## 9. Pillar 7: Orca Native Worktree User-Review Gate & Fast-Forward Merge Protocol

### 9.1. The Power of Orca Visual Worktree Cards
Orca's primary architectural strength is its visual representation of Git Worktrees as independent board cards:
- **Visual Card per Task**: Instead of executing inside the dirty root working tree, each task runs inside an isolated worktree card:
  `orca worktree create --name "task-<id>-<slug>" --base-branch HEAD --agent hermes --prompt "..."`
- **Zero Branch Contamination**: The Peer edits files inside `.worktrees/task-<id>` on dedicated branch `peer/task-<id>`. The main branch remains 100% pristine.
- **Side-by-Side Reviewing**: Operators can click into the Worktree card on Orca Desktop to review the live diff with visual syntax highlighting.

### 9.2. The 4-Step Human-in-the-Loop Review Lifecycle

```text
1. Lead Dispatches Task #<id>
          │
          ▼
   [Orca Worktree Created]
   • Thư mục riêng: `.worktrees/task-<id>-<slug>/`
   • Branch riêng: `peer/task-<id>-<slug>`
   • Peer Dev lập trình ➔ Chuyển trạng thái `Resolved`
          │
          ▼
2. QC Verification Inside Worktree
   • QC chạy test ISTQB 5-Stage + Anti-leak scan trong worktree
   • Test PASS 100% ➔ Chuyển trạng thái Worktree: [AWAITING USER REVIEW]
          │
          ▼
3. Ambient Alert to User
   • Emits Desktop Notification: "Task #<id> ready for review on Orca Board"
   • Task IS NOT MERGED AUTOMATICALLY (Human Gate Locked)
          │
          ├───────────────────────────────┐
          ▼ [USER APPROVES]               ▼ [USER REJECTS]
4A. Merge & Cleanup Worktree        4B. In-Worktree Feedback Loop
   • `./orca-review approve <id>`      • `./orca-review reject <id> --reason "..."`
   • Git merge --ff-only               • Feedback injected into Peer terminal
   • `orca worktree rm`                • Peer fixes in worktree (Main branch clean)
   • Task marked `Closed`              • Re-enters QC verification loop
```

### 9.3. CLI Tooling: `tools/orca_worktree_manager.py` & `./orca-review`
- **List Worktrees**: `./orca-review list`
- **Mark Ready for Review**: `./orca-review ready-review <id> --verdict "PASS 100%"`
- **User Approve & Fast-Forward Merge**: `./orca-review approve <id>`
- **User Reject with Actionable Feedback**: `./orca-review reject <id> --reason "<ghi chú>"`

---

## 10. Verification & Compliance Checklist

- [x] Ephemeral git worktree creation and pruning contract specified (`.worktrees/task-<id>`).
- [x] Automated quarantine & rollback on rejected tasks specified (`bmad/rooms/archive/*.patch`).
- [x] 5-point Pre-flight Doctor matrix defined (`tools/harness_doctor.py`).
- [x] Cross-platform desktop notification protocol defined (`notify-send` / `osascript` / bell).
- [x] Zero-RAM CLI Status HUD contract defined (`./agent-start watch`).
- [x] Supervisor Singleton SPOC & Tri-State Task Collision matrix fully specified.
- [x] Single-Ownership File Locking Invariant enforced across concurrent tasks.
- [x] Orca Native Worktree User-Review Gate & `./orca-review` CLI implementation certified.
- [x] Full alignment with Master Architecture Spec (`ARCH-SPEC-EPHEMERAL-SUBAGENT-ORCHESTRATION-2026-V1`).
- [x] Documented in `docs/spec/slppc-room-resiliency-and-isolation-spec.md`.

