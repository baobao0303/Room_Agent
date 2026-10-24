# Tools Directory - Cấu Trúc Bộ Công Cụ Multi-Agent SLPPC

Thư mục chứa toàn bộ CLI, scripts tự động hóa và công cụ điều hành dành cho các Agent (`Supervisor`, `PM`, `Lead`, `Peer 1..4`, `QC`, `Security Sentinel`) trong hệ sinh thái SLPPC.

---

## 📂 Phân Loại Công Cụ Theo Nhóm Nghiệp Vụ

```text
tools/
├── 1. Core Harness & Data Store
│   ├── floci_client.py              # DynamoDB & S3 local client (endpoint :14566)
│   ├── harness_manager.py           # Quản lý Work Items & State Machine (auto/floci/sqlite)
│   ├── harness_rust.py              # Native Rust Bridge v0.1.14 & Kev System One Decision Engine
│   ├── harness_doctor.py            # Continuous DB Health Monitor & Auto-Healer
│   └── harness_learning_search.py   # Tra cứu & kiểm soát chất lượng tri thức tự học
│
├── 2. SLPPC Governance & Quality Gates
│   ├── slppc_flow_guard.py          # Canh gác ranh giới 5 vai trò (role_trespass, pm_bypass, vague_specs)
│   ├── lead_code_review.py          # Bộ công cụ rà soát mã nguồn & thẩm định kiến trúc của Lead Dev
│   ├── strict_typing_scanner.py     # Quét nghiêm ngặt cấm 'any', 'unknown' và fallback chắp vá
│   ├── zombie_reaper.py             # Zombie Terminal Reaper & Watchdog timeout 300s
│   └── room_cleanup.py              # Thu gom rác an toàn khi Work Item đạt Closed
│
├── 3. Agent Runtime & Lifecycle
│   ├── agent_progress.py            # Sổ cái tiến độ & biên bản bàn giao (docs/AGENT_PROGRESS.md)
│   ├── agent_heartbeat.py           # Giám sát nhịp tim và trạng thái của từng Agent
│   ├── agent_heartbeat_watcher.py   # Daemon watcher cảnh báo mất nhịp tim
│   ├── agent_reprimand.py           # Lập biên bản chế tài và xử phạt vi phạm quy trình
│   ├── agent_context_manager.py     # Giám sát ngân sách context window (<30k tokens)
│   ├── call_agent.py                # Dispatcher kích hoạt Paseo agent profiles
│   └── paseo_hooks.py               # Forwarding wrapper sang plugins/slpc-lifecycle-hooks/paseo_hooks.py
│
├── 4. Testing & Code Generation
│   ├── qc_test_generator.py         # Bộ sinh Test Matrix & Unit Test 5-Stage ISTQB
│   ├── tester_team_tool.py          # Bộ công cụ tự động hóa kiểm thử Tester Team
│   └── profile_research_gen.py      # Pipeline ép cổng Research + Gen Brief tự động
│
├── 5. Search, Knowledge & Integration
│   ├── skill_manager.py             # Master Registry & Inverted Index DB Search cho 80+ skills
│   ├── tds_search.py                # Tra cứu offline/online API & selectors TDS UI
│   ├── query_reader.py              # Đọc ngữ cảnh thông minh, chống lỗi EISDIR, BM25
│   ├── record_discussion.py         # Ghi biên bản thảo luận & đồng thuận (ADR minutes)
│   ├── remote_mcp_server.py         # MCP Server kết nối Azure DevOps / TFS
│   ├── remote_sync.py               # Đồng bộ backlog từ Azure DevOps về DynamoDB
│   └── doc_sync.py                  # Đồng bộ và kiểm tra cấu trúc đặc tả trong docs/spec/
│
├── 6. Orchestration Bridges & Autonomous Controllers
│   ├── slppc_orchestrator.py        # Bộ điều phối tự hành SLPPC Autonomous Orchestrator (plugins/)
│   ├── orca_slpc_bridge.py          # Bộ điều phối toàn diện SLPC trên Orca Orchestration
│   ├── orca_worktree_manager.py     # Quản trị Worktree cô lập & Human-in-the-Loop Review Gate (./orca-review)
│   ├── dual_ide_hook.py             # Bộ định tuyến Universal Dual-IDE Hook Router (Orca & Paseo)
│   ├── orca_harness_bridge.py       # Cầu nối đồng bộ Harness DB với Orca Workspace Board
│   └── aevum_harness_bridge.py      # Cầu nối đồng bộ BlockSuite Aevum Real-Time Kanban
│
└── 7. Subdirectories
    ├── tests/                       # Unit test suites cho toàn bộ tools (100% PASS)
    │   ├── test_harness.py
    │   ├── test_qc_generator.py
    │   ├── test_skill_manager.py
    │   ├── test_strict_typing_scanner.py
    │   ├── test_role_fence_audit.py
    │   ├── test_tds_search.py
    │   ├── test_harness2_spec_audit.py
    │   └── test_harness_core_issue12_13.py
    ├── research/                    # Sub-agent nghiên cứu kỹ thuật & Hermes Gateway
    │   ├── research_agent.py
    │   ├── hermes_research_client.py
    │   └── reports/                 # Các báo cáo nghiên cứu kỹ thuật chuẩn hóa
    └── web/                         # Giao diện dashboard trực quan
        └── skill_dashboard.html     # HTML UI cho Skill Manager
```

---

## ⚡ Lệnh Thường Dùng

```bash
# 1. Tra cứu ma trận kiểm thử & backlog
python3 tools/harness_manager.py stats
python3 tools/harness_manager.py list --source bot --assigned-to-profile lead

# 2. Canh gác ranh giới vai trò SLPPC
python3 tools/slppc_flow_guard.py audit

# 3. Quét Zombie Terminal & giám sát Watchdog
python3 tools/zombie_reaper.py --dry-run

# 4. Quét vi phạm Strict Typing
python3 tools/strict_typing_scanner.py projects/wicx-crm-fe

# 5. Chạy toàn bộ test suite của tools
python3 -m unittest discover -s tools/tests
```
