#!/usr/bin/env python3
"""
tools/agent_progress.py - Sổ cái lưu trữ tiến độ & bàn giao giữa các Agent (Session Continuity & Handoff Ledger).

Mục đích:
- Lưu lại toàn bộ những gì các Agent đã làm, những mục còn thiếu, và bước tiếp theo cần thực hiện.
- Khi User yêu cầu "làm tiếp" hoặc "báo cáo tiến độ", bất kỳ Agent nào (Antigravity, Claude, Codex, Hermes, Supervisor, Lead, Peer, QC)
  chỉ cần chạy `python3 tools/agent_progress.py status` hoặc đọc `docs/AGENT_PROGRESS.md` để nắm ngay ngữ cảnh và báo cáo cho User.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
(BASE_DIR / ".harness").mkdir(parents=True, exist_ok=True)
STATE_FILE = BASE_DIR / ".harness" / "progress.json"
MARKDOWN_FILE = BASE_DIR / "docs" / "AGENT_PROGRESS.md"
VN_TZ = timezone(timedelta(hours=7))


def now_iso() -> str:
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S %z")


def split_items(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(";") if item.strip()]


def split_files(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def sanitize_text(text: str | None) -> str:
    """Loại bỏ các đường dẫn tuyệt đối cá nhân để chống leak và giữ tính linh động."""
    if not text:
        return ""
    base_str = str(BASE_DIR)
    text = text.replace(base_str + "/", "")
    text = text.replace(base_str, ".")
    home_str = str(Path.home())
    if home_str and home_str != "/":
        text = text.replace(home_str + "/", "~/")
        text = text.replace(home_str, "~")
    text = re.sub(r'/(?:Users|home)/[a-zA-Z0-9._-]+/?', '~/', text)
    text = re.sub(r'[a-zA-Z]:\\(?:Users|home)\\[a-zA-Z0-9._-]+\\?', r'~\\', text)
    return text


def default_state() -> dict[str, Any]:
    return {
        "updated_at": now_iso(),
        "current_focus": "Phân tích kiến trúc Paseo_Project & codex-room-setup, lập Spec 8 mục và chuẩn bị Setup Paseo v0.8.0",
        "last_agent": "Antigravity (Supervisor/Architect)",
        "next_action": (
            "1. Cài đặt Paseo v0.8.0 về ~/projects/supervisors/paseo (`cd codex-room-setup && ./scripts/install-paseo`). "
            "2. Nếu dùng Codex Room (3-role SLP): cài `@openai/codex`, `codex login`, tạo `~/.codex/{skills,plugins,config.toml,AGENTS.md}` rồi chạy `./install --apply`. "
            "3. Nếu dùng kết hợp SLPC: chạy thêm `python3 patch_paseo.py` để bơm profiles SLPPC vào `~/.paseo/config.json`."
        ),
        "completed_items": [
            "Đọc và phân tích toàn bộ mã nguồn workspace Room_Agent (AGENTS.md, CLAUDE.md, setup_home.sh, setup_harness.sh, patch_paseo.py, profiles/*, scripts/*, tools/*, docs/spec/*).",
            "Clone repo `https://github.com/hoangnb24/codex-room-setup` vào `codex-room-setup` và thêm `/codex-room-setup/` vào `.gitignore`.",
            "Đọc 100% mã nguồn của `codex-room-setup` (`install`, `scripts/install-room`, `scripts/install-paseo`, `scripts/verify`, `scripts/doctor`, `home/.local/bin/codex-room*`, `home/.config/codex-room/*`, `home/.paseo/config.json.template`).",
            "Chạy kiểm chứng mã nguồn `./scripts/verify --source` (đạt 100% `VERIFY_OK`) và chẩn đoán máy trạm qua `./scripts/doctor` & `./install --dry-run`.",
            "Tạo và hoàn thiện tài liệu đặc tả 8 mục tại `docs/spec/codex-room-setup-spec.md`.",
            "Xây dựng hệ thống Sổ cái Tiến độ & Bàn giao Agent (`docs/AGENT_PROGRESS.md` + `tools/agent_progress.py`) và tích hợp vào `AGENTS.md`, `CLAUDE.md`."
        ],
        "missing_items": [
            "[Máy trạm] Chưa có binary `codex` (`npm install -g @openai/codex`) trên PATH.",
            "[Máy trạm] Chưa khởi tạo thư mục gốc `~/.codex` cùng 5 tài nguyên bắt buộc (`config.toml`, `auth.json`, `AGENTS.md`, `skills/`, `plugins/`).",
            "[Máy trạm] Chưa clone & build Paseo `v0.8.0` tại `~/projects/supervisors/paseo` và chưa có symlink `~/.local/bin/paseo` (có thể chạy ngay bằng `./scripts/install-paseo`).",
            "[Máy trạm] Chưa xuất bản 9 file cấu hình Codex Room (`~/.config/codex-room/*`, `~/.local/bin/codex-room*`, `~/.paseo/config.json`) và 3 thư mục `~/.codex-runtime/{supervisor,lead,peer}` qua `./install --apply`.",
            "[Daemon] Paseo Daemon chưa khởi chạy ở `127.0.0.1:6767` nên chưa chạy bước kiểm chứng live (`./install --verify --live`)."
        ],
        "sessions": [
            {
                "timestamp": now_iso(),
                "agent": "Antigravity (Supervisor/Architect)",
                "summary": "Đọc toàn bộ Paseo_Project & codex-room-setup, viết Spec 8 mục và thiết lập hệ thống lưu tiến độ Agent",
                "done": [
                    "Đọc hiểu toàn bộ cấu trúc Paseo_Project (4-role SLPC + Harness DB) và codex-room-setup (3-role SLP + Paseo v0.8.0)",
                    "Cấu hình `.gitignore` ẩn `/codex-room-setup/` để không làm bẩn git status của dự án",
                    "Chạy `./scripts/verify --source`, `./scripts/doctor`, `./install --dry-run` để xác định chính xác các mục còn thiếu trên máy",
                    "Tạo file spec đầy đủ 8 mục tại `docs/spec/codex-room-setup-spec.md`",
                    "Tạo `tools/agent_progress.py` và `docs/AGENT_PROGRESS.md` làm nơi lưu trữ trạng thái bàn giao giữa các Agent"
                ],
                "files": [
                    ".gitignore",
                    "docs/spec/codex-room-setup-spec.md",
                    "docs/AGENT_PROGRESS.md",
                    "tools/agent_progress.py",
                    "AGENTS.md",
                    "CLAUDE.md"
                ],
                "next": "Chờ lệnh từ User: Cài Paseo v0.8.0 (`./scripts/install-paseo`) hoặc cài đặt đầy đủ Codex CLI + `./install --apply`."
            }
        ]
    }


def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    state = default_state()
    save_state(state)
    return state


def render_markdown(state: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Sổ Cái Tiến Độ & Bàn Giao Giữa Các Agent (Agent Progress & Handoff Ledger)",
        "",
        "> **QUY TẮC BẮT BUỘC CHO MỌI AGENT**:",
        "> 1. Khi User yêu cầu **\"làm tiếp\"**, **\"tiếp tục\"**, hoặc **\"báo cáo những gì đã làm\"**, Agent phải đọc file này đầu tiên (hoặc chạy `python3 tools/agent_progress.py status`) để báo cáo ngay cho User trước khi bắt tay vào việc.",
        "> 2. Sau khi hoàn thành một đầu việc hoặc trước khi dừng chờ User, Agent phải cập nhật lại tiến độ bằng lệnh `python3 tools/agent_progress.py log ...`.",
        "",
        "---",
        "",
        "## 1. Trạng thái Tổng quan Hiện tại (Current Snapshot)",
        "",
        f"- **Cập nhật lần cuối**: `{state.get('updated_at', '')}`",
        f"- **Agent cập nhật gần nhất**: `{state.get('last_agent', '')}`",
        f"- **Trọng tâm hiện tại**: {state.get('current_focus', '')}",
        f"- **Hành động kế tiếp (Khi User bảo \"làm tiếp\")**:",
        f"  > {state.get('next_action', '')}",
        "",
        "---",
        "",
        "## 2. Những Hạng Mục Đã Hoàn Thành (Completed Items)",
        "",
    ]

    completed = state.get("completed_items", [])
    if completed:
        for item in completed:
            lines.append(f"- [x] {item}")
    else:
        lines.append("- *(Chưa có hạng mục nào được ghi nhận)*")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Những Mục Còn Thiếu / Đang Chờ Thực Hiện (Missing & Pending Items)",
        "",
    ])

    missing = state.get("missing_items", [])
    if missing:
        for idx, item in enumerate(missing, start=1):
            lines.append(f"- [ ] **[M{idx}]** {item}")
    else:
        lines.append("- 🎉 *Tất cả các hạng mục đều đã hoàn tất!*")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Nhật Ký Bàn Giao Phiên Làm Việc (Session Handoff Log)",
        "",
    ])

    sessions = state.get("sessions", [])
    recent_sessions = sessions[-20:]
    if len(sessions) > 20:
        lines.append(f"> Lưu ý: Hiển thị 20 phiên gần nhất (tổng số: {len(sessions)} phiên được lưu trong `.harness_progress.json`).\n")
    for idx, session in enumerate(reversed(recent_sessions), start=1):
        lines.append(f"### Phiên #{len(sessions) - idx + 1} — `{session.get('timestamp', '')}` | **{session.get('agent', '')}**")
        lines.append(f"- **Tóm tắt**: {session.get('summary', '')}")
        done_list = session.get("done", [])
        if done_list:
            lines.append("- **Đã thực hiện**:")
            for d in done_list:
                lines.append(f"  - {d}")
        files_list = session.get("files", [])
        if files_list:
            formatted_files = ", ".join(f"`{f}`" for f in files_list)
            lines.append(f"- **File đã tạo/cập nhật**: {formatted_files}")
        if session.get("next"):
            lines.append(f"- **Bàn giao bước tiếp theo**: {session.get('next')}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 5. Hướng Dẫn Lệnh Nhanh Cho Agent",
        "",
        "```bash",
        "# 1. Xem nhanh báo cáo để trả lời User khi được yêu cầu \"làm tiếp\":",
        "python3 tools/agent_progress.py status",
        "",
        "# 2. Ghi nhận công việc vừa làm xong & cập nhật bước tiếp theo:",
        "python3 tools/agent_progress.py log \\",
        "  --agent \"Lead Dev\" \\",
        "  --focus \"Trọng tâm công việc hiện tại\" \\",
        "  --summary \"Tóm tắt ngắn gọn phiên làm việc\" \\",
        "  --done \"Việc đã xong 1; Việc đã xong 2\" \\",
        "  --missing \"Việc còn thiếu 1; Việc còn thiếu 2\" \\",
        "  --next \"Bước cụ thể cần làm ngay khi User bảo làm tiếp\" \\",
        "  --files \"docs/spec/file1.md,tools/script2.py\"",
        "```",
        "",
    ])
    return "\n".join(lines)


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MARKDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_FILE.write_text(render_markdown(state), encoding="utf-8")


def cmd_status(state: dict[str, Any]) -> None:
    print("======================================================================")
    print("📋 BÁO CÁO TIẾN ĐỘ & BÀN GIAO AGENT (AGENT PROGRESS LEDGER)")
    print("======================================================================")
    print(f"⏱  Cập nhật cuối : {state.get('updated_at')}")
    print(f"🤖 Agent gần nhất: {state.get('last_agent')}")
    print(f"🎯 Trọng tâm     : {state.get('current_focus')}")
    print("----------------------------------------------------------------------")
    print("✅ ĐÃ HOÀN THÀNH (COMPLETED):")
    for idx, item in enumerate(state.get("completed_items", []), start=1):
        print(f"  {idx}. {item}")
    print("----------------------------------------------------------------------")
    print("⚠️  CÒN THIẾU / CHƯA LÀM (MISSING / PENDING):")
    missing = state.get("missing_items", [])
    if missing:
        for idx, item in enumerate(missing, start=1):
            print(f"  [M{idx}] {item}")
    else:
        print("  (Không còn mục nào bị thiếu)")
    print("----------------------------------------------------------------------")
    print("🚀 BƯỚC TIẾP THEO KHI USER BẢO 'LÀM TIẾP' (NEXT ACTION):")
    print(f"  {state.get('next_action')}")
    print("======================================================================")


def cmd_log(args: argparse.Namespace, state: dict[str, Any]) -> None:
    done_items = [sanitize_text(d) for d in split_items(args.done)]
    missing_items = [sanitize_text(m) for m in split_items(args.missing)]
    files = [sanitize_text(f) for f in split_files(args.files)]

    agent_name = sanitize_text(args.agent)
    summary_text = sanitize_text(args.summary)
    focus_text = sanitize_text(args.focus) if args.focus else None
    next_text = sanitize_text(args.next) if args.next else None

    state["last_agent"] = agent_name
    if focus_text:
        state["current_focus"] = focus_text
    if next_text:
        state["next_action"] = next_text

    existing_completed = state.setdefault("completed_items", [])
    for item in done_items:
        if item not in existing_completed:
            existing_completed.append(item)

    if args.replace_missing and missing_items:
        state["missing_items"] = missing_items
    elif missing_items:
        existing_missing = state.setdefault("missing_items", [])
        for item in missing_items:
            if item not in existing_missing:
                existing_missing.append(item)

    if args.resolve_missing:
        resolved_keywords = [sanitize_text(kw) for kw in split_items(args.resolve_missing)]
        state["missing_items"] = [
            m for m in state.get("missing_items", [])
            if not any(kw.lower() in m.lower() for kw in resolved_keywords)
        ]

    session_entry = {
        "timestamp": now_iso(),
        "agent": agent_name,
        "summary": summary_text,
        "done": done_items,
        "files": files,
        "next": next_text or state.get("next_action", ""),
    }
    state.setdefault("sessions", []).append(session_entry)
    save_state(state)

    # Automatically save handoff memo into bmad/rooms/<role>/
    agent_lower = agent_name.lower()
    room = "peer"
    if "supervisor" in agent_lower:
        room = "supervisor"
    elif "pm" in agent_lower:
        room = "pm"
    elif "lead" in agent_lower:
        room = "lead"
    elif "qc" in agent_lower:
        room = "qc"

    room_dir = BASE_DIR / "bmad" / "rooms" / room
    try:
        room_dir.mkdir(parents=True, exist_ok=True)
        latest_file = room_dir / "latest_handoff.md"
        done_bullets = "\n".join(f"- [x] {d}" for d in done_items) if done_items else "- (Không có mục chi tiết)"
        file_bullets = "\n".join(f"- `{f}`" for f in files) if files else "- (Không có file)"
        missing_bullets = "\n" + "\n".join(f"- [ ] {m}" for m in missing_items) if missing_items else ""

        handoff_memo = f"""# BIÊN BẢN BÀN GIAO: {agent_name}

- **Thời gian**: `{now_iso()}`
- **Agent bàn giao**: `{agent_name}`
- **Tóm tắt**: {summary_text}

## 1. Đã hoàn thành trong phiên
{done_bullets}

## 2. File đã tạo / chỉnh sửa
{file_bullets}

## 3. Trọng tâm & Bước tiếp theo
- **Trọng tâm hiện tại**: {focus_text or state.get('current_focus', '')}
- **Bàn giao hành động tiếp**: {next_text or state.get('next_action', '')}{missing_bullets}
"""
        handoff_memo = sanitize_text(handoff_memo)
        memo_lines = handoff_memo.strip().splitlines()
        if len(memo_lines) > 150:
            memo_lines = memo_lines[:149] + ["- ... (đã cắt bớt để bảo đảm trần <=150 dòng)"]
        latest_file.write_text("\n".join(memo_lines) + "\n", encoding="utf-8")
        try:
            rel_latest = latest_file.relative_to(BASE_DIR)
        except Exception:
            rel_latest = latest_file.name
        print(f"Đã lưu biên bản bàn giao vào {rel_latest}.")
    except Exception:
        pass

    # Update bmad/rooms/room_ledger.json (FIFO 50, < 50KB)
    ledger_path = BASE_DIR / "bmad" / "rooms" / "room_ledger.json"
    try:
        ledger: dict[str, Any] = {}
        if ledger_path.is_file():
            try:
                ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            except Exception:
                ledger = {}
        if not isinstance(ledger, dict) or "version" not in ledger:
            ledger = {
                "version": "1.0.0",
                "updated_at": now_iso(),
                "roles": {
                    "supervisor": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_iso()},
                    "pm": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_iso()},
                    "lead": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_iso()},
                    "peer": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_iso()},
                    "qc": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_iso()},
                },
                "history": [],
            }
        ledger["updated_at"] = now_iso()
        roles = ledger.setdefault("roles", {})
        if room not in roles or not isinstance(roles[room], dict):
            roles[room] = {}
        roles[room]["status"] = "IDLE"
        roles[room]["last_action"] = summary_text
        roles[room]["updated_at"] = now_iso()

        task_id = getattr(args, "task_id", None)
        if not task_id and summary_text:
            m = re.search(r'#(\d+)', summary_text)
            if m:
                try:
                    task_id = int(m.group(1))
                except Exception:
                    pass
        if task_id:
            roles[room]["active_task_id"] = task_id

        history = ledger.setdefault("history", [])
        history.append({
            "timestamp": now_iso(),
            "agent": agent_name,
            "action": "log",
            "task_id": task_id,
            "summary": summary_text,
        })
        if len(history) > 50:
            ledger["history"] = history[-50:]

        ledger_str = json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"
        while len(ledger_str.encode("utf-8")) > 50 * 1024 and len(ledger.get("history", [])) > 1:
            ledger["history"].pop(0)
            ledger_str = json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"

        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(ledger_str, encoding="utf-8")
    except Exception:
        pass

    try:
        md_rel = MARKDOWN_FILE.relative_to(BASE_DIR)
    except Exception:
        md_rel = MARKDOWN_FILE
    try:
        st_rel = STATE_FILE.relative_to(BASE_DIR)
    except Exception:
        st_rel = STATE_FILE
    print(f"Đã cập nhật tiến độ vào {md_rel} và {st_rel}.")


def _get_paseo_dirs() -> tuple[Path, Path]:
    home = Path.home()
    slug = str(BASE_DIR).strip("/").replace("/", "-")
    
    paseo_agents_dir = home / ".paseo" / "agents" / slug
    if not paseo_agents_dir.exists():
        agents_parent = home / ".paseo" / "agents"
        if agents_parent.is_dir():
            matches = sorted(
                [d for d in agents_parent.iterdir() if d.is_dir() and ("Room_Agent" in d.name or "Paseo_Project" in d.name)],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if matches:
                paseo_agents_dir = matches[0]

    claude_proj_dir = home / ".paseo" / "claude-config" / "projects" / f"-{slug}"
    if not claude_proj_dir.exists():
        proj_parent = home / ".paseo" / "claude-config" / "projects"
        if proj_parent.is_dir():
            matches = sorted(
                [d for d in proj_parent.iterdir() if d.is_dir() and ("Room_Agent" in d.name or "Paseo_Project" in d.name)],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if matches:
                claude_proj_dir = matches[0]

    return paseo_agents_dir, claude_proj_dir


def cmd_sessions() -> None:
    home = Path.home()
    paseo_agents_dir, claude_proj_dir = _get_paseo_dirs()
    codex_rt_dir = home / ".codex-runtime"

    print("======================================================================")
    print("🧠 BẢN ĐỒ VỊ TRÍ CONTEXT WINDOW & SUB-AGENTS CỦA 4 ROLE (SLPC)")
    print("======================================================================")
    print(f"1. Paseo Agent Metadata : {paseo_agents_dir}")
    print(f"2. Claude Context JSONL : {claude_proj_dir}")
    print(f"3. Codex Room Runtimes  : {codex_rt_dir}/{{supervisor,lead,peer,qc}}")
    print(f"4. Sub-Agents (031)     : {home / '.paseo/claude-config/agents'} & {home / '.codex/skills/claude-code-sub-agents'}")
    print("----------------------------------------------------------------------")
    if paseo_agents_dir.is_dir():
        files = sorted(paseo_agents_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:8]
        print("📌 8 Agent gần nhất trong Paseo (Paseo_Project):")
        for f in files:
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                agent_id = meta.get("id", f.stem)
                provider = meta.get("provider", "?")
                model = meta.get("config", {}).get("model", "?")
                status = meta.get("lastStatus", "?")
                session_id = meta.get("persistence", {}).get("sessionId") or meta.get("runtimeInfo", {}).get("sessionId")
                updated = meta.get("updatedAt", "?")
                ctx_file = claude_proj_dir / f"{session_id}.jsonl" if session_id else None
                size_kb = f"{ctx_file.stat().st_size / 1024:.1f} KB" if (ctx_file and ctx_file.exists()) else "N/A"
                print(f"  - Agent {agent_id[:8]}.. | provider={provider} | model={model} | status={status} | updated={updated}")
                if ctx_file and ctx_file.exists():
                    print(f"    ↳ Context Window ({size_kb}): {ctx_file}")
            except Exception:
                continue
    print("======================================================================")


def _collect_all_thread_files() -> list[tuple[str, Path]]:
    home = Path.home()
    candidates: list[tuple[str, Path]] = []
    _, claude_proj_dir = _get_paseo_dirs()
    if claude_proj_dir.is_dir():
        for p in claude_proj_dir.glob("*.jsonl"):
            candidates.append(("paseo-claude", p))
    for role in ("supervisor", "lead", "peer", "qc"):
        sess_dir = home / ".codex-runtime" / role / "sessions"
        if sess_dir.is_dir():
            for p in sess_dir.rglob("*.jsonl"):
                candidates.append((f"codex-{role}", p))
    codex_sess = home / ".codex" / "sessions"
    if codex_sess.is_dir():
        for p in codex_sess.rglob("*.jsonl"):
            candidates.append(("codex-cli", p))
    return sorted(candidates, key=lambda item: item[1].stat().st_mtime, reverse=True)


def cmd_find_thread(query: str = "", limit: int = 15) -> None:
    q = (query or "").strip().lower()
    results = []
    for source, path in _collect_all_thread_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if q and q not in text.lower() and q not in path.name.lower():
            continue
        results.append({
            "thread_id": path.stem,
            "source": source,
            "path": str(path),
            "size_kb": round(path.stat().st_size / 1024, 1),
            "updated_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        })
        if len(results) >= limit:
            break
    print(json.dumps({"query": query, "count": len(results), "threads": results}, indent=2, ensure_ascii=False))


def cmd_read_thread(thread_id_or_path: str, max_messages: int = 40) -> None:
    target = Path(thread_id_or_path).expanduser()
    if not target.is_file():
        for _, candidate in _collect_all_thread_files():
            if candidate.stem.startswith(thread_id_or_path) or thread_id_or_path in candidate.name:
                target = candidate
                break
    if not target.is_file():
        print(json.dumps({"error": f"Thread not found: {thread_id_or_path}"}))
        return
    messages = []
    for line in target.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        role = obj.get("type") or obj.get("role") or obj.get("message", {}).get("role")
        content = obj.get("message", {}).get("content") or obj.get("content")
        text_parts = []
        if isinstance(content, str):
            text_parts.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") in ("text", "input_text", "output_text"):
                    text_parts.append(str(part.get("text", "")))
        merged = "\n".join(t for t in text_parts if t).strip()
        if merged:
            messages.append({"role": role, "text": merged[:1200]})
    print(json.dumps({
        "thread_id": target.stem,
        "path": str(target),
        "total_extracted_messages": len(messages),
        "messages": messages[-max_messages:],
    }, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Quản lý sổ cái tiến độ & bàn giao công việc giữa các Agent")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Hiển thị trạng thái công việc đã làm, còn thiếu và bước tiếp theo")
    subparsers.add_parser("resume", help="Alias của status dùng khi User yêu cầu 'làm tiếp'")
    subparsers.add_parser("sync", help="Tái tạo lại file docs/AGENT_PROGRESS.md từ trạng thái hiện tại")
    subparsers.add_parser("sessions", help="Liệt kê vị trí file Context Window (*.jsonl) của các Agent đang chạy")

    find_parser = subparsers.add_parser("find-thread", help="[Knowledge Skill Phase 1] Tìm kiếm thread (*.jsonl) theo từ khóa")
    find_parser.add_argument("query", nargs="?", default="", help="Từ khóa tìm kiếm trong các session thread")
    find_parser.add_argument("--limit", type=int, default=15, help="Số lượng thread tối đa trả về")

    read_parser = subparsers.add_parser("read-thread", help="[Knowledge Skill Phase 2] Đọc nội dung rút gọn của 1 thread (*.jsonl)")
    read_parser.add_argument("thread", help="Thread ID (sessionId) hoặc đường dẫn file .jsonl")
    read_parser.add_argument("--max-messages", type=int, default=40, help="Số thông điệp tối đa trích xuất")

    log_parser = subparsers.add_parser("log", help="Ghi nhận thêm một phiên làm việc của Agent")
    log_parser.add_argument("--agent", required=True, help="Tên Agent hoặc Role (VD: Supervisor, Lead, Peer, QC, Antigravity)")
    log_parser.add_argument("--summary", required=True, help="Tóm tắt ngắn gọn phiên làm việc")
    log_parser.add_argument("--focus", help="Cập nhật trọng tâm công việc hiện tại")
    log_parser.add_argument("--done", help="Danh sách việc đã hoàn thành (ngăn cách bởi dấu ';')")
    log_parser.add_argument("--missing", help="Danh sách việc còn thiếu cần bổ sung (ngăn cách bởi dấu ';')")
    log_parser.add_argument("--replace-missing", action="store_true", help="Ghi đè toàn bộ danh sách còn thiếu bằng --missing mới")
    log_parser.add_argument("--resolve-missing", help="Từ khóa các mục còn thiếu đã được giải quyết (ngăn cách bởi dấu ';')")
    log_parser.add_argument("--next", help="Bước tiếp theo cần làm khi User bảo 'làm tiếp'")
    log_parser.add_argument("--files", help="Danh sách file đã tạo/sửa (ngăn cách bởi dấu ',')")
    log_parser.add_argument("--task-id", help="Task ID hoặc Work Item ID đang xử lý")

    args = parser.parse_args()
    state = load_state()

    if args.command in (None, "status", "resume"):
        save_state(state)
        cmd_status(state)
        return 0
    if args.command == "sync":
        save_state(state)
        print(f"Đã đồng bộ {MARKDOWN_FILE}.")
        return 0
    if args.command == "sessions":
        cmd_sessions()
        return 0
    if args.command == "find-thread":
        cmd_find_thread(args.query, args.limit)
        return 0
    if args.command == "read-thread":
        cmd_read_thread(args.thread, args.max_messages)
        return 0
    if args.command == "log":
        cmd_log(args, state)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
