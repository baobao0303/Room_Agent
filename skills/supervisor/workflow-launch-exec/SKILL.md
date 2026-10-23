---
name: workflow-launch-exec
description: Launch, orchestrate, and drive end-to-end multi-agent pipelines (BA -> DESIGN -> DEV -> VERIFY) for any task.
---

# Workflow Launch & Execution Skill (`workflow-launch-exec`)

Orchestrate and automatically execute the entire software development lifecycle across closed departmental gates (BA ➔ DESIGN ➔ DEV ➔ VERIFY).

---

## 1. Quick Start / Agent Run Path
Run the automated orchestration driver for any task through the entire lifecycle:

```bash
python3 tools/workflow_driver.py "<project_name>" "<task_description_or_user_story>"
```

### Example:
```bash
python3 tools/workflow_driver.py "crm-portal" "Customer Export to Excel"
```

---

## 2. Pipeline Execution Stages

1. **Stage 1 (BA)**: Automatically bootstrap and standardize User Story + Acceptance Criteria at `docs/spec/<project>/ba/`.
2. **Stage 2 (Design)**: Map TDS UI components and semantic Color Tokens at `docs/spec/<project>/design/`.
3. **Stage 3 (Dev)**: Construct typed DTO contracts and Architecture specs at `docs/spec/<project>/dev/`.
4. **Stage 4 (Verify)**: Mechanically verify integrity and synchronize status into Harness SDLC.

---

## 3. Manual Run Path
For developers or operators executing steps manually:
- Create BA spec: Author file at `docs/spec/<project>/ba/<task>-spec.md`
- Create UI spec: Author file at `docs/spec/<project>/design/<task>-ui.md`
- Manage task: `python3 tools/harness_manager.py add --type "User Story" ...`
