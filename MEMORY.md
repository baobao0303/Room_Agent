<!-- Your curated long-term memory: durable facts, preferences, and commitments. Keep it tight: promote what lasts here, and leave raw day-to-day detail in your daily notes. -->

## Facts
- Communicates in Vietnamese.
- Exploring and operating the `Room_Agent` repository (`baobao0303/Room_Agent`) under the Enterprise AI 4-Pillar Architecture (`ARCH-SPEC-ENTERPRISE-AI-4-PILLARS-2026-V1`).
- Intends to use `Room_Agent` for personal solo orchestration with high efficiency (Ephemeral by Default, Persistent by Exception).
- Uses Orca Desktop and Paseo with `Room_Agent`; Supervisor acts as the Single Point of Contact (SPOC) on branch `main`.

## Preferences
- Prefers calling models and deterministic tools directly inside the chat/workspace without relying on external fragile proxies when offline.
- For `Room_Agent` changes: never delete anything currently running or working; only delete items proven dead and explicitly confirmed by the user.
- Keep responses concise, direct, and free of performative filler; always link files and symbols with clickable markdown links.

## Commitments
- Enforce the 4-Role SLPC Governance Gate (`Supervisor -> Lead -> Peer -> QC`) and Concurrency Ceiling (max 3–5 active sub-agents).
- Never write production code or perform deep code debugging (`role_trespass`); always evaluate intake through Kev System One first (`mandatory_feasibility_gate`).
- Require EVOS Engine Release Gate (`Pass Rate >= 98.5%`) and `anti_leak_sentinel.py` (`100% PASS`) before approving any release or PR.

## Pending Decisions (chờ User duyệt — chưa thực hiện)
- 2026-10-26 · G-PRM-1: Cả 4 profile trong `~/.paseo/config.json` đang `"modeId": "full-access"` (default cũng là `full-access` trong `tools/call_agent.py#L113`, `scripts/patch_paseo.py#L133`). Đề xuất hạ Peer/QC → `accept-edits`/`ask`, Lead → `ask`. User: "tạm thời chưa" — KHÔNG tự sửa; nhắc lại trước khi bật Computer Use hoặc chạy pipeline tự hành. Chi tiết: `docs/spec/ai-agent-4-concepts-spec.md` §10.4, §13.
