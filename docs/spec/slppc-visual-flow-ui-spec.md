# Architecture Specification: SLPPC Visual Flow UI Dashboard

> **Spec Identifier**: `ARCH-SPEC-SLPPC-VISUAL-FLOW-UI-2026-V1`  
> **Topic**: Giao diện Web trực quan hóa luồng Pipeline SLPPC (Visual Flow UI: Node Graph tiến độ PM ➔ Lead ➔ Peer ➔ QC)  
> **Authors**: Supervisor & PM Agent (`pm`)  
> **Approved By**: Kev System One (`Feasibility 1.61/3.0`, `Strategic Alignment perfect_fit 61.68%`, `Supervision Decision Yellow`)  
> **Target Path**: `tools/web/flow_ui.html` + `tools/web/flow_server.py`

---

## 1. Executive Summary & Problem Context

In the SLPPC (`Supervisor - PM - Lead - Peer - QC`) architecture, multiple autonomous agents execute concurrently. Currently, observability is confined to CLI terminal logs and markdown progress ledgers:
- Operators and users cannot visually track where a task sits in the 5-stage pipeline at a glance.
- There is no immediate visual signal when a sub-agent is spawned, executing, blocked, or handed off.
- The **Visual Flow UI** provides a zero-dependency, ultra-lightweight real-time visual dashboard mapping the live state machine of the SLPPC pipeline.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SLPPC VISUAL FLOW UI - NODE GRAPH OVERVIEW               │
│                                                                             │
│  [1. USER / SUPERVISOR] ────► [2. PM GATE] ────────► [3. LEAD ARCHITECT]   │
│  • Scope & Intent Guard      • Kev System One <50ms   • 5-Point Zero-Search │
│  • Concurrency Ceiling       • Feasibility / Alignment• Architecture Review │
│            │                              │                      │          │
│            ▼                              ▼                      ▼          │
│   (State: Active/Idle)           (State: Approved/Deny)  (State: Dispatched)│
│                                                                  │          │
│                                           ┌──────────────────────┘          │
│                                           ▼                                 │
│                                  [4. PEER MAKER POOL]                       │
│                                  • Ephemeral Worker (gemini-flash-medium)   │
│                                  • Bounded Implementation + Local Tests     │
│                                  • State: Active ➔ Resolved ➔ Auto-Close    │
│                                           │                                 │
│                                           ▼                                 │
│                                  [5. QC QUALITY GATE]                       │
│                                  • 5-Stage ISTQB Mechanical Verification    │
│                                  • Exit Code 0 + Kev Verification Check     │
│                                  • State: Closed (or Reopen Peer on Bug)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technical Architecture & Component Hierarchy

### 2.1 Technology Stack (Zero-Dependency Constraint)
To ensure immediate load times (<100ms) and zero background resource drain:
- **Frontend**: Pure HTML5, SVG Dynamic Bezier Connectors, Vanilla JavaScript ES2022, TDS Design Tokens / Tailwind Utility Classes (Dark Theme by default).
- **Backend Bridge**: Python stdlib `http.server` with SSE (Server-Sent Events) or Fast Polling (1.5s interval) reading `.harness_progress.json` and Harness DB (`floci_client` / `sqlite`).
- **Deployment**: Single-file SPA at `tools/web/flow_ui.html` served locally on `http://localhost:8088/flow`.

### 2.2 Component Hierarchy
1. **Header Bar**:
   - Workspace Name, Active Work Item Title & ID, Concurrency Indicator (e.g. `2/5 Active Sub-Agents`), Live Connection Status (`🟢 Connected`).
2. **Interactive Node Graph (Pipeline Stepper)**:
   - 5 Main Stage Nodes connected with SVG dynamic status paths:
     - `Supervisor`: Scope status, active Epic ID.
     - `PM Agent`: Kev System One score badge, Alignment pill (`perfect_fit`).
     - `Lead Dev`: Task breakdown count, Review status (`Approved` / `Rejected`).
     - `Peer Dev`: Active worker role (Peer 1..4), model tier, execution timer (watchdog 300s).
     - `QC Verifier`: Mechanical test status (`26/26 PASS`), sign-off status.
   - Dynamic Node States: `IDLE` (Grey/Muted), `RUNNING` (Pulsing Blue/Yellow), `RESOLVED` (Cyan), `PASSED/CLOSED` (Emerald Green), `REJECTED/BUG` (Rose Red).
3. **Interactive Inspection Drawer (Bottom/Right)**:
   - Clicking any node opens a detail panel displaying:
     - Current Handoff Memo (`bmad/rooms/<role>/latest_handoff.md`).
     - Zero-Search 5 Anchors.
     - Recent test runner output & error stack traces.

---

## 3. Data Schema Contract (`PipelineStatusDto`)

The server exposes `GET /api/pipeline/status` returning:

```json
{
  "timestamp": "2026-10-23T17:45:00Z",
  "active_work_item": {
    "id": 4694,
    "title": "Kiểm tra quy chuẩn pipeline SLPPC",
    "state": "Closed",
    "assigned_to": "qc"
  },
  "concurrency": {
    "active_workers": 1,
    "ceiling": 5
  },
  "nodes": {
    "supervisor": {
      "role": "Supervisor",
      "model": "gemini-3.8-flash-high",
      "status": "idle",
      "action": "Supervising SLPPC Room and Real-time Pipelines"
    },
    "pm": {
      "role": "PM Agent",
      "model": "gemini-3.8-flash-high",
      "status": "passed",
      "kev_feasibility": 1.84,
      "kev_alignment": "perfect_fit",
      "risk_lane": "green"
    },
    "lead": {
      "role": "Lead Dev",
      "model": "gemini-3.8-flash-high",
      "status": "passed",
      "action": "Task #4694 Zero-Search Decomposition & Review APPROVED"
    },
    "peer": {
      "role": "Peer Dev 1",
      "model": "gemini-3.8-flash-low",
      "status": "closed",
      "uptime_secs": 42,
      "test_result": "100% PASS (Exit Code 0)"
    },
    "qc": {
      "role": "QC Verifier",
      "model": "gemini-3.8-flash-high",
      "status": "closed",
      "decision": "approve_close",
      "test_count": "26/26 PASS"
    }
  }
}
```

---

## 4. Acceptance Criteria (Quantitative Matrix)

| ID | Category | Requirement | Verifiable Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **AC-FLOW-01** | **Visual Stepper** | Hiển thị đầy đủ 5 nodes tuần tự | 100% 5 nodes hiển thị theo đúng thứ tự: Supervisor ➔ PM ➔ Lead ➔ Peer ➔ QC. |
| **AC-FLOW-02** | **Live Status Styling** | Phản ánh đúng trạng thái thực | Node đổi màu chuẩn: Running (vàng/xanh nhấp nháy), Closed (xanh lá), Rejected/Bug (đỏ). |
| **AC-FLOW-03** | **Real-Time Polling** | Tự động đồng bộ không cần F5 | Giao diện tự động fetch `/api/pipeline/status` mỗi 1500ms và repaint DOM <10ms. |
| **AC-FLOW-04** | **Node Detail Drawer** | Xem chi tiết khi click vào node | Click vào node mở modal/drawer hiển thị handoff memo và log test thật. |
| **AC-FLOW-05** | **Zero-Dependency** | Chạy độc lập, không thêm npm libs | File HTML duy nhất chạy trực tiếp bằng browser hoặc qua Python server stdlib. |

---

## 5. Zero-Search Task Breakdown For Lead Dev

Lead Dev shall decompose the implementation into 3 bounded Zero-Search subtasks:

### Task 1: Backend State Bridge (`tools/web/flow_server.py`)
- **Target File**: `tools/web/flow_server.py`
- **Anchors**: Class `FlowStatusHandler(BaseHTTPRequestHandler)`, method `do_GET`.
- **Concrete Changes**: Read `.harness_progress.json` and `tools/harness_manager.py` state; serve JSON endpoint `/api/pipeline/status` on port 8088.
- **AC**: `curl -s http://localhost:8088/api/pipeline/status | jq .nodes` returns valid 5-node JSON.
- **Test Command**: `python3 -m unittest discover -s tools/tests`

### Task 2: Single-File SPA Frontend (`tools/web/flow_ui.html`)
- **Target File**: `tools/web/flow_ui.html`
- **Anchors**: `<div id="pipeline-stepper">`, `<svg id="connectors">`, `<div id="detail-drawer">`.
- **Concrete Changes**: Implement SVG dynamic curve connectors, 5 node cards with TDS tokens, and 1.5s interval polling fetcher.
- **AC**: Fulfills AC-FLOW-01..05.
- **Test Command**: Verify HTTP 200 via `curl -I http://localhost:8088/flow`

### Task 3: QC Test Suite & End-to-End Verification (`tools/tests/test_flow_ui.py`)
- **Target File**: `tools/tests/test_flow_ui.py`
- **Anchors**: Test cases covering JSON schema, HTTP handler response, and DOM contract.
- **AC**: 100% assertions pass.
- **Test Command**: `python3 -m unittest tools/tests/test_flow_ui.py`
