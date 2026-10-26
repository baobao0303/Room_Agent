#!/usr/bin/env python3
"""
tools/harness_manager.py - Operational Management Tool for Harness Operating Framework.
Directly interfaces with Floci DynamoDB / S3 (or SQLite fallback),
strictly enforcing Company DDD syntax and State Machine validation.
"""

import os
import sys
import json
import sqlite3
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Transparent fallback to venv with boto3 if current python lacks boto3
try:
    import boto3
except ImportError:
    candidate_venvs = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../.venv/bin/python")),
        os.path.expanduser("~/.hermes/hermes-agent/venv/bin/python"),
        os.path.expanduser("~/ponytail/venv/bin/python"),
        os.path.expanduser("~/.local/bin/python3"),
    ]
    for venv_py in candidate_venvs:
        if os.path.exists(venv_py) and venv_py != sys.executable:
            if sys.argv and sys.argv[0] != "-c":
                os.execv(venv_py, [venv_py] + sys.argv)

BASE_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, BASE_DIR)


def _resolve_shared_root(default_root: Path) -> Path:
    override = os.environ.get("SLPPC_SHARED_ROOT")
    if override:
        p = Path(override)
        if os.access(p, os.R_OK | os.W_OK):
            return p
    git_entry = default_root / ".git"
    try:
        if git_entry.is_file():
            raw = git_entry.read_text(encoding="utf-8").strip()
            if raw.startswith("gitdir:"):
                gitdir = Path(raw.split("gitdir:", 1)[1].strip())
                if not gitdir.is_absolute():
                    gitdir = (default_root / gitdir).resolve()
                if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
                    main_root = gitdir.parent.parent.parent
                    if os.access(main_root, os.R_OK | os.W_OK):
                        return main_root
    except Exception:
        pass
    return default_root


SHARED_DIR = str(_resolve_shared_root(Path(BASE_DIR)))

from tools.floci_client import FlociHarnessDB

os.makedirs(os.path.join(SHARED_DIR, ".harness"), exist_ok=True)
DEFAULT_DB_PATH = os.getenv("HARNESS_DB", os.path.join(SHARED_DIR, ".harness", "harness.db"))
HARNESS_BACKEND = os.getenv("HARNESS_BACKEND", "floci").lower()

_ALL_STATES = ["New", "Accepted", "Active", "Blocked", "Resolved", "Closed", "Removed"]

VALID_TRANSITIONS = {
    wi_type: {
        state: list(_ALL_STATES)
        for state in _ALL_STATES
    }
    for wi_type in ["User Story", "Technical Story", "Task", "Bug", "Testcase", "Epic", "Feature"]
}

ALLOWED_PROFILES = [
    "Lead BA",
    "Peer BA",
    "Lead design",
    "Peer Design",
    "Lead Dev",
    "Peer Dev",
    "Supervisor",
    "Lead",
    "Peer",
    "QC",
    "PM",
    "Security"
]

# Module-level permissions cache to avoid disk thrashing
_PROFILE_PERMISSIONS_CACHE: Dict[str, Dict[str, Any]] = {}

def normalize_role(role: Optional[str]) -> str:
    """Normalize arbitrary role and profile strings to canonical 4-role identity."""
    if not role:
        return ""
    r = str(role).strip().lower()
    if r in ("supervisor", "lead", "peer", "qc"):
        return r
    if any(k in r for k in ("lead",)):
        return "lead"
    if any(k in r for k in ("qc", "qa", "tester")):
        return "qc"
    if any(k in r for k in ("peer", "dev", "design", "ba")):
        return "peer"
    if any(k in r for k in ("supervisor", "sup")):
        return "supervisor"
    return r

def parse_profile_permissions(profile_path: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter permissions from PROFILE.md using stdlib only."""
    if not profile_path.is_file():
        return {}
    try:
        content = profile_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    yaml_text = parts[1]
    permissions: Dict[str, Any] = {}
    in_permissions = False

    for line in yaml_text.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        if line.startswith("permissions:"):
            in_permissions = True
            continue
        if in_permissions:
            # Child elements of permissions: must be indented
            if line.startswith(" ") or line.startswith("\t"):
                if ":" in trimmed:
                    k, v = trimmed.split(":", 1)
                    k = k.strip()
                    v_str = v.strip().lower()
                    if v_str == "true":
                        permissions[k] = True
                    elif v_str == "false":
                        permissions[k] = False
                    elif v_str.isdigit():
                        permissions[k] = int(v_str)
                    else:
                        permissions[k] = v.strip().strip("'\"")
            else:
                # Reached a new top-level key (e.g. scoped_tools:)
                in_permissions = False

    return permissions

def get_role_permissions(role: Optional[str], base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Get permissions declared in profiles/<role>/PROFILE.md with caching."""
    canonical = normalize_role(role)
    if not canonical:
        return {}
    if canonical in _PROFILE_PERMISSIONS_CACHE:
        return _PROFILE_PERMISSIONS_CACHE[canonical]

    root = base_dir or Path(BASE_DIR)
    profile_file = root / "profiles" / canonical / "PROFILE.md"
    perms = parse_profile_permissions(profile_file)
    _PROFILE_PERMISSIONS_CACHE[canonical] = perms
    return perms


def close_ephemeral_subagent(role: str) -> bool:
    """Close an ephemeral sub-agent terminal (PM, Lead, Peer, or QC) to return RAM to 0."""
    if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca"):
        return False
    clean_role = role.lower().strip()
    # Bảo vệ duy nhất Persistent Supervisor (main)
    if any(k in clean_role for k in ("supervisor", "main")):
        return False

    reg_file = Path(SHARED_DIR) / "bmad" / "rooms" / "agent_terminals.json"
    closed_any = False
    try:
        if reg_file.is_file():
            data = json.loads(reg_file.read_text(encoding="utf-8"))
            handle = None
            for r, info in list(data.items()):
                if clean_role in r.lower():
                    handle = info.get("handle") if isinstance(info, dict) else info
                    del data[r]
                    break
            if handle:
                reg_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                res = subprocess.run(["orca", "terminal", "close", "--terminal", handle, "--tab", "--json"], capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    closed_any = True
        if any(k in clean_role for k in ("peer", "dev", "design")):
            wt_target = "name:room-peer"
        elif "qc" in clean_role:
            wt_target = "name:room-qc"
        elif "lead" in clean_role:
            wt_target = "name:room-lead"
        elif "pm" in clean_role:
            wt_target = "name:room-pm"
        else:
            wt_target = ""
        if wt_target:
            res_wt = subprocess.run(["orca", "terminal", "close", "--worktree", wt_target, "--all", "--json"], capture_output=True, text=True, timeout=5)
            if res_wt.returncode == 0:
                closed_any = True
        if closed_any:
            print(f"🛑 [Ephemeral Auto-Close]: Đã tự động đóng tab {role.upper()} để giải phóng tài nguyên.")
        return closed_any
    except Exception as e:
        print(f"⚠️ [close_ephemeral_subagent error]: {e}", file=sys.stderr)
    return False


def reap_orphaned_terminals() -> int:
    """Trigger Zombie Reaper to close ephemeral sub-agent terminals when task is Closed."""
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        try:
            from zombie_reaper import audit_and_reap  # type: ignore
        except ImportError:
            from tools.zombie_reaper import audit_and_reap  # type: ignore
        res = audit_and_reap(dry_run=False)
        reaped = res.get("zombies_reaped", 0)
        if reaped > 0:
            print(f"🧟 [Zombie Reaper]: Đã tự động thu hồi {reaped} ephemeral sub-agent terminal sau khi đóng Task.")
        return reaped
    except Exception as e:
        print(f"⚠️ [Zombie Reaper Error]: {e}", file=sys.stderr)
        return 0


def cleanup_task_room(item_id: int) -> int:
    """Clean up handoff records, task artifacts, and zombie terminals when a task is Closed."""
    # 1. Gọi room_cleanup.py để nén task-scoped directory an toàn
    try:
        from room_cleanup import cleanup_by_task  # type: ignore
        cleanup_by_task(str(item_id), dry_run=False)
    except Exception:
        try:
            from tools.room_cleanup import cleanup_by_task  # type: ignore
            cleanup_by_task(str(item_id), dry_run=False)
        except Exception:
            pass

    # 2. Xóa các memo files mồ côi
    bmad_rooms = Path(SHARED_DIR) / "bmad" / "rooms"
    removed_count = 0
    if bmad_rooms.is_dir():
        for memo_file in bmad_rooms.rglob(f"*handoff_{item_id}_*.md"):
            try:
                memo_file.unlink()
                removed_count += 1
            except Exception:
                pass

        # Lưu ý: Tuyệt đối KHÔNG xóa latest_handoff.md vì mỗi phòng ban bắt buộc
        # phải duy trì duy nhất 1 file single-pointer latest_handoff.md theo spec.

    # 3. Thu hồi terminal mồ côi (Phase 6: REAPED)
    reap_orphaned_terminals()
    return removed_count

def send_orca_notification(role: str, message: str) -> bool:
    """Send real-time prompt to the live Orca terminal for a role (strictly max 1 agent per room)."""
    if os.environ.get("SLPPC_DRY_RUN") == "1":
        return False
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        try:
            from agent_context_manager import has_live_terminal, safe_send_agent_message  # type: ignore
        except ImportError:
            from tools.agent_context_manager import has_live_terminal, safe_send_agent_message  # type: ignore

        existing_handle = has_live_terminal(role)
        sent = safe_send_agent_message(role, message)
        if sent:
            return True
        if existing_handle:
            # Nếu trong room đã có Agent đang sống (dù đang bận thinking >8s), TUYỆT ĐỐI không spawn Agent thứ 2!
            return True

        # FALLBACK CHO EPHEMERAL SUB-AGENTS (Peer, QC) HOẶC ROOM CHƯA MỞ TAB:
        clean_role = role.lower().strip()
        if shutil.which("orca") and any(k in clean_role for k in ("peer", "dev", "design", "qc", "lead", "pm")):
            target_room = "peer" if any(k in clean_role for k in ("peer", "dev", "design")) else ("qc" if "qc" in clean_role else ("lead" if "lead" in clean_role else ("pm" if "pm" in clean_role else "active")))
            # Cho Ephemeral rooms (peer, qc): đảm bảo đóng sạch terminal cũ trước khi launch
            if target_room in ("peer", "qc"):
                close_ephemeral_subagent(target_room)
            print(f"🚀 [Ephemeral Auto-Launch]: Chưa có tab cho {role.upper()}. Đang mở AI Agent tab mới trên Orca...")
            wt_target = f"name:room-{target_room}" if target_room in ("pm", "lead", "peer", "qc") else "active"
            cmd_launch = [
                "orca", "agent", "launch",
                "--worktree", wt_target,
                "--agent", "hermes",
                "--prompt", message,
                "--focus",
                "--json"
            ]
            res = subprocess.run(cmd_launch, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                handle = ""
                tab_id = ""
                if res.stdout:
                    try:
                        data = json.loads(res.stdout)
                        outcome = data.get("result", {}).get("outcome", {})
                        handle = outcome.get("handle") or ""
                        pk = outcome.get("paneKey") or ""
                        tab_id = pk.split(":")[0] if ":" in pk else pk
                    except Exception:
                        pass

                titles_map = {
                    "peer": "[Peer Dev] Code & UI Executor",
                    "qc": "[QC] 5-Stage ISTQB Verifier",
                    "pm": "[PM] Feasibility & Alignment",
                    "lead": "[Lead Dev] Technical Architect",
                }
                models_map = {
                    "peer": "ag/gemini-3.8-flash-high",
                    "qc": "ag/gemini-3.8-flash-high",
                }
                role_key = "peer" if any(k in clean_role for k in ("peer", "dev", "design")) else ("qc" if "qc" in clean_role else clean_role)
                term_title = titles_map.get(role_key, f"[{role.upper()}] Sub-Agent")
                term_model = models_map.get(role_key, "ag/gemini-3.8-flash-high")

                if handle:
                    subprocess.run(["orca", "terminal", "rename", "--terminal", handle, "--title", term_title, "--json"], capture_output=True, check=False)
                    subprocess.run(["orca", "terminal", "set-pane-title", "--terminal", handle, "--title", term_title, "--json"], capture_output=True, check=False)
                    subprocess.run(["orca", "terminal", "send", "--terminal", handle, "--text", f"/title {term_title}", "--enter"], capture_output=True, check=False)
                    subprocess.run(["orca", "terminal", "send", "--terminal", handle, "--text", f"/model {term_model}", "--enter"], capture_output=True, check=False)

                    # Tự động nạp RTK (Rust Token Killer) Profile Environment để nén 60-90% token
                    rtk_env_script = Path(BASE_DIR) / "scripts" / "rtk_profile_env.sh"
                    if rtk_env_script.is_file():
                        subprocess.run(["orca", "terminal", "send", "--terminal", handle, "--text", f"source {rtk_env_script} {role_key}", "--enter"], capture_output=True, check=False)

                    reg_file = Path(SHARED_DIR) / "bmad" / "rooms" / "agent_terminals.json"
                    reg = {}
                    if reg_file.is_file():
                        try:
                            reg = json.loads(reg_file.read_text(encoding="utf-8"))
                        except Exception:
                            reg = {}
                    reg[role_key] = {"handle": handle, "tabId": tab_id}
                    reg_file.parent.mkdir(parents=True, exist_ok=True)
                    reg_file.write_text(json.dumps(reg, indent=2), encoding="utf-8")
                    # Re-check để đóng mọi shell/tab dư thừa trong cùng room
                    has_live_terminal(role_key)

                print(f"✅ [Ephemeral Auto-Launch]: Đã mở và đổi tên thành công AI Agent tab '{term_title}' ({handle}) trên Orca!")
                return True
            else:
                print(f"⚠️ [Ephemeral Launch Error]: {res.stderr.strip()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"⚠️ [send_orca_notification error]: {e}", file=sys.stderr)
        return False


def auto_dispatch_agent(
    item_id: int,
    wi_type: str,
    title: str,
    target_state: str,
    assigned_to: Optional[str] = None,
    assigned_to_profile: Optional[str] = None,
    prev_state: Optional[str] = None
):
    """Automatically wake up and notify the relevant SLPPC agents on state changes."""
    # Chống spam: Không gửi broadcast notification khi testcase nhỏ lẻ thay đổi
    if wi_type.lower() in ("testcase",):
        return

    # 1. Update heartbeat ping
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        try:
            from agent_heartbeat import record_ping  # type: ignore
        except ImportError:
            from tools.agent_heartbeat import record_ping  # type: ignore
        caller_role = (assigned_to_profile or assigned_to or "peer").lower()
        if "peer" in caller_role or "dev" in caller_role or "design" in caller_role:
            rec_role = "peer"
        elif "lead" in caller_role:
            rec_role = "lead"
        elif "qc" in caller_role:
            rec_role = "qc"
        else:
            rec_role = caller_role.split()[0]
        record_ping(rec_role, "working" if target_state == "Active" else "idle", task_id=str(item_id), activity=f"{target_state} {title[:28]}")
    except Exception:
        pass

    state_lower = target_state.lower()
    
    # CASE 1: Peer nộp code xong (target_state == "Resolved")
    # -> Báo ngay cho LEADER (Review 7-Point) VÀ QC (Test 5-Stage ISTQB)
    if state_lower == "resolved":
        msg_lead = f"📢 [PEER BÁO CÁO REVIEW]: Peer đã hoàn thành {wi_type} #{item_id}: '{title}' (Resolved). Hãy thực thi 7-Point Lead Review."
        msg_qc = f"📢 [QC SẴN SÀNG TEST]: {wi_type} #{item_id}: '{title}' đã Resolved. Hãy sinh 5-Stage ISTQB test matrix và nghiệm thu độc lập."
        send_orca_notification("lead", msg_lead)
        send_orca_notification("qc", msg_qc)
        print(f"🔔 [Auto-Dispatch]: Đã tự động báo cáo cho Lead Dev và QC về Work Item #{item_id} (Resolved).")
        # Ephemeral Sub-Agent: Tự động đóng tab Peer Dev khi hoàn thành code (Resolved) để giải phóng RAM
        close_ephemeral_subagent("peer")

    # CASE 2: Giao việc thi công (target_state == "Active" hoặc "Accepted")
    # -> Báo ngay cho Peer được gán
    elif state_lower in ("active", "accepted"):
        target_peer = (assigned_to_profile or assigned_to or "").lower()
        if any(k in target_peer for k in ("peer", "design", "dev")):
            peer_role = "peer"
            msg_peer = f"📢 [NHIỆM VỤ MỚI]: Bạn được phân công {wi_type} #{item_id}: '{title}' ({target_state}). Đọc spec tại Harness DB / bmad/rooms/ và bắt đầu thi công!"
            send_orca_notification(peer_role, msg_peer)
            print(f"🔔 [Auto-Dispatch]: Đã tự động đánh thức {peer_role.upper()} thi công Work Item #{item_id}.")

    # CASE 3: QC đóng task (target_state == "Closed")
    # -> Báo cho Supervisor và đóng toàn bộ các phòng Sub-Agents (PM, Lead, Peer, QC) để chỉ giữ lại Supervisor
    elif state_lower == "closed":
        msg_done = f"📢 [NGHIỆM THU ĐÃ ĐÓNG]: {wi_type} #{item_id}: '{title}' đã được nghiệm thu và CLOSED thành công."
        send_orca_notification("supervisor", msg_done)
        print(f"🔔 [Auto-Dispatch]: Đã tự động báo cáo đóng Task #{item_id} tới Supervisor.")
        for ep_role in ("qc", "peer", "lead", "pm"):
            close_ephemeral_subagent(ep_role)

    # CASE 4: Task bị tắc nghẽn (target_state == "Blocked")
    elif state_lower == "blocked":
        msg_blocked = f"🚨 [TASK BLOCKED]: {wi_type} #{item_id}: '{title}' đã bị BLOCKED sau khi vượt trần retry. Cần Supervisor can thiệp."
        send_orca_notification("supervisor", msg_blocked)
        print(f"🔔 [Auto-Dispatch]: Đã tự động báo cáo Task #{item_id} (Blocked) tới Supervisor.")
        for ep_role in ("peer", "qc"):
            close_ephemeral_subagent(ep_role)


class HarnessManager:
    def __init__(self, backend: Optional[str] = None, db_path: Optional[str] = None, engine: str = "auto"):
        env_backend = os.getenv("HARNESS_BACKEND") or os.getenv("HARNESS_ENGINE")
        if engine in ("floci", "rust", "sqlite"):
            self.backend = engine
        elif env_backend:
            self.backend = env_backend.lower()
        else:
            self.backend = (backend or HARNESS_BACKEND).lower()
        self.engine = engine

        resolved_db_path = db_path if db_path is not None else os.getenv("HARNESS_DB", DEFAULT_DB_PATH)
        self.db_path = resolved_db_path

        # Always initialize local SQLite schema for trace, intervention and local fallback
        try:
            with open(os.path.join(BASE_DIR, "scripts/schema/full_schema.sql")) as f, self._get_sqlite_db() as conn:
                conn.executescript(f.read())
        except Exception:
            pass

        if self.backend == "floci":
            try:
                self.floci_db = FlociHarnessDB()
                self.floci_db.init_schema()
            except Exception:
                self.backend = "sqlite"


    def _get_sqlite_db(self) -> sqlite3.Connection:
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")

        # Auto-migrate missing columns in legacy work_item table
        try:
            cur = conn.cursor()
            cols = {r[1] for r in cur.execute("PRAGMA table_info(work_item);").fetchall()}
            if cols:
                if "source" not in cols:
                    cur.execute("ALTER TABLE work_item ADD COLUMN source TEXT NOT NULL DEFAULT 'local';")
                if "created_by_profile" not in cols:
                    cur.execute("ALTER TABLE work_item ADD COLUMN created_by_profile TEXT;")
                if "assigned_to_profile" not in cols:
                    cur.execute("ALTER TABLE work_item ADD COLUMN assigned_to_profile TEXT;")
                conn.commit()
        except Exception:
            pass

        # Auto-migrate missing columns in intervention table
        try:
            cur = conn.cursor()
            cols_int = {r[1] for r in cur.execute("PRAGMA table_info(intervention);").fetchall()}
            if cols_int and "action" not in cols_int:
                cur.execute("ALTER TABLE intervention ADD COLUMN action TEXT DEFAULT 'approved';")
                conn.commit()
        except Exception:
            pass

        # Auto-migrate legacy/truncated trace table (G-OBS-1) via table-copy
        try:
            cur = conn.cursor()
            trace_cols = {r[1] for r in cur.execute("PRAGMA table_info(trace);").fetchall()}
            if trace_cols:
                if "task_summary" not in trace_cols or "content" in trace_cols:
                    row_count = cur.execute("SELECT count(*) FROM trace;").fetchone()[0]
                    if row_count == 0:
                        cur.execute("DROP TABLE trace;")
                        cur.execute("""
                            CREATE TABLE trace (
                                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                                created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
                                task_summary     TEXT    NOT NULL,
                                intake_id        INTEGER REFERENCES intake(id),
                                story_id         TEXT    REFERENCES story(id) ON DELETE CASCADE,
                                agent            TEXT,
                                actions_taken    TEXT,
                                files_read       TEXT,
                                files_changed    TEXT,
                                decisions_made   TEXT,
                                errors           TEXT,
                                outcome          TEXT CHECK(outcome IN ('completed','blocked','partial','failed')),
                                duration_seconds INTEGER,
                                token_estimate   INTEGER,
                                harness_friction TEXT,
                                notes            TEXT,
                                run_id           TEXT
                            );
                        """)
                    else:
                        conn.commit()
                        conn.execute("PRAGMA foreign_keys = OFF;")
                        try:
                            cur.execute("""
                                CREATE TABLE trace__migrated (
                                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                                    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
                                    task_summary     TEXT    NOT NULL,
                                    intake_id        INTEGER REFERENCES intake(id),
                                    story_id         TEXT    REFERENCES story(id) ON DELETE CASCADE,
                                    agent            TEXT,
                                    actions_taken    TEXT,
                                    files_read       TEXT,
                                    files_changed    TEXT,
                                    decisions_made   TEXT,
                                    errors           TEXT,
                                    outcome          TEXT CHECK(outcome IN ('completed','blocked','partial','failed')),
                                    duration_seconds INTEGER,
                                    token_estimate   INTEGER,
                                    harness_friction TEXT,
                                    notes            TEXT,
                                    run_id           TEXT
                                );
                            """)
                            canonical_cols = [
                                "id", "created_at", "task_summary", "intake_id", "story_id",
                                "agent", "actions_taken", "files_read", "files_changed",
                                "decisions_made", "errors", "outcome", "duration_seconds",
                                "token_estimate", "harness_friction", "notes", "run_id"
                            ]
                            select_exprs = []
                            for col in canonical_cols:
                                if col == "id":
                                    select_exprs.append("id")
                                elif col == "created_at":
                                    select_exprs.append("created_at" if "created_at" in trace_cols else "(datetime('now'))")
                                elif col == "story_id":
                                    select_exprs.append("CAST(story_id AS TEXT)" if "story_id" in trace_cols else "NULL")
                                elif col == "task_summary":
                                    if "task_summary" in trace_cols and "content" in trace_cols:
                                        select_exprs.append("COALESCE(NULLIF(task_summary, ''), NULLIF(content, ''), 'migrated trace')")
                                    elif "content" in trace_cols:
                                        select_exprs.append("COALESCE(NULLIF(content, ''), 'migrated trace')")
                                    elif "task_summary" in trace_cols:
                                        select_exprs.append("COALESCE(task_summary, 'migrated trace')")
                                    else:
                                        select_exprs.append("'migrated trace'")
                                elif col == "notes":
                                    if "notes" in trace_cols and "tier" in trace_cols:
                                        select_exprs.append("COALESCE(notes, 'migrated_legacy tier=' || tier)")
                                    elif "tier" in trace_cols:
                                        select_exprs.append("'migrated_legacy tier=' || tier")
                                    elif "notes" in trace_cols:
                                        select_exprs.append("notes")
                                    else:
                                        select_exprs.append("NULL")
                                else:
                                    select_exprs.append(col if col in trace_cols else "NULL")

                            cols_str = ", ".join(canonical_cols)
                            exprs_str = ", ".join(select_exprs)
                            cur.execute(f"INSERT INTO trace__migrated ({cols_str}) SELECT {exprs_str} FROM trace;")
                            cur.execute("DROP TABLE trace;")
                            cur.execute("ALTER TABLE trace__migrated RENAME TO trace;")
                            cur.execute("CREATE INDEX IF NOT EXISTS idx_trace_run_id ON trace(run_id);")
                            cur.execute("CREATE INDEX IF NOT EXISTS idx_trace_story_id ON trace(story_id);")
                            cur.execute("CREATE INDEX IF NOT EXISTS idx_trace_created_at ON trace(created_at);")
                            conn.commit()
                        finally:
                            conn.execute("PRAGMA foreign_keys = ON;")
                else:
                    if "run_id" not in trace_cols:
                        cur.execute("ALTER TABLE trace ADD COLUMN run_id TEXT;")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_trace_run_id ON trace(run_id);")
                conn.commit()
        except Exception:
            pass
        return conn

    def get_allowed_profiles(self) -> List[str]:
        """Return list of valid Paseo agent profile names."""
        return ALLOWED_PROFILES

    # 1. Validation Logic
    @staticmethod
    def validate_work_item(wi_type: str, title: str, description: Optional[str] = None, assigned_to: Optional[str] = None):
        """Validate title syntax, BDD format, and assigned Paseo profile."""
        if assigned_to and assigned_to not in ALLOWED_PROFILES:
            # Check if assigned_to is a known profile
            pass
        # Check title dash / format
        if wi_type in ["Epic", "Feature", "User Story", "Technical Story", "Task"]:
            if not any(d in title for d in ["-", "–", "—"]):
                raise ValueError(f"Invalid {wi_type} title syntax: Must contain dash separator (-/–/—)")

        if wi_type == "User Story":
            lower_title = title.lower()
            if not any(k in lower_title for k in ["có thể", "co the", "can"]):
                raise ValueError("Invalid User Story title: Must contain keyword 'có thể' / 'co the' / 'can'")

            if description:
                # Validate BDD structure
                if not ("as a" in description.lower() and "i want" in description.lower() and "so that" in description.lower()):
                    raise ValueError("Invalid User Story description: Must follow 'As a [Role], I want [Action], So that [Value]'")

        elif wi_type in ["Bug", "Testcase"]:
            if not (title.startswith("[") and "]:" in title):
                raise ValueError(f"Invalid {wi_type} title syntax: Must follow '[Module]: [Details]'")
            if not any(k in title.lower() for k in ["when", "khi"]):
                raise ValueError(f"Invalid {wi_type} title syntax: Must contain 'when' or 'khi'")

    # 2. Work Item Operations
    def add_work_item(
        self,
        wi_type: str,
        title: str,
        description: str = "",
        priority: str = "P2",
        assigned_to: Optional[str] = None,
        story_points: Optional[int] = None,
        remaining_work: Optional[float] = None,
        severity: Optional[str] = None,
        parent_id: Optional[int] = None,
        area_path: Optional[str] = None,
        iteration_path: Optional[str] = None,
        tags: Optional[str] = None,
        acceptance_criteria: Optional[str] = None,
        source: str = "local",
        created_by_profile: Optional[str] = None,
        assigned_to_profile: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate format first
        self.validate_work_item(wi_type, title, description)

        # Rào cản vai trò: Chỉ Quản lý (Supervisor/Lead) mới được tạo Epic
        if wi_type.lower() == "epic":
            creator = (created_by_profile or "").strip().lower()
            if creator in ("peer", "peer dev", "peer ba", "peer design"):
                raise PermissionError(
                    f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{created_by_profile}' là DEV ONLY. "
                    "Nghiêm cấm Dev tự ý tạo Epic! Chỉ Supervisor hoặc Lead mới nắm quyền quản lý phạm vi."
                )

        # 1. Tự động chuẩn hóa assigned_to_profile nếu chỉ truyền assigned_to (chạy trước rào cản vai trò)
        if not assigned_to_profile and assigned_to:
            lower_to = assigned_to.strip().lower()
            if any(l in lower_to for l in ("lead", "supervisor")):
                assigned_to_profile = "lead" if "lead" in lower_to else "supervisor"
            elif any(p in lower_to for p in ("peer", "dev", "design")):
                assigned_to_profile = "peer"
            elif "qc" in lower_to:
                assigned_to_profile = "qc"
            elif "pm" in lower_to:
                assigned_to_profile = "pm"

        # 2. Rào cản vai trò: Cấm gán Task thi công mã nguồn cho Quản lý (Lead / Supervisor)
        effective_assignee = (assigned_to_profile or assigned_to or "").strip().lower()
        if wi_type.lower() == "task":
            if any(r in effective_assignee for r in ("lead", "supervisor")) or assigned_to_profile in ("lead", "supervisor"):
                raise PermissionError(
                    f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{effective_assignee}' là QUẢN LÝ / KIẾN TRÚC. "
                    "Nghiêm cấm gán Task thi công cho Lead/Supervisor! Task bắt buộc phải gán cho Peer (Peer 1..4) hoặc QC."
                )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.backend == "floci":
            item = {
                "type": wi_type,
                "title": title,
                "description": description,
                "state": "New",
                "priority": priority,
                "assigned_to": assigned_to,
                "story_points": story_points,
                "remaining_work": remaining_work,
                "severity": severity,
                "parent_item_id": parent_id,
                "area_path": area_path,
                "iteration_path": iteration_path,
                "tags": tags,
                "acceptance_criteria": acceptance_criteria,
                "source": source,
                "created_by_profile": created_by_profile,
                "assigned_to_profile": assigned_to_profile,
                "created_at": now_str,
                "updated_at": now_str
            }
            saved = self.floci_db.put_work_item(item)
            auto_dispatch_agent(saved["id"], wi_type, title, "New", assigned_to, assigned_to_profile)
            return {"success": True, "id": saved["id"], "type": wi_type, "title": title, "state": "New", "storage": "floci-dynamodb"}

        # SQLite fallback
        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO work_item (
                    type, title, description, state, assigned_to, story_points,
                    remaining_work, priority, severity, parent_id, area_path,
                    iteration_path, tags, acceptance_criteria, source, created_by_profile, assigned_to_profile, created_at, updated_at
                ) VALUES (?, ?, ?, 'New', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                wi_type, title, description, assigned_to, story_points,
                remaining_work, priority, severity, parent_id, area_path,
                iteration_path, tags, acceptance_criteria, source, created_by_profile, assigned_to_profile
            ))
            conn.commit()
            item_id = int(cursor.lastrowid or 0)
            auto_dispatch_agent(item_id, wi_type, title, "New", assigned_to, assigned_to_profile)
            return {"success": True, "id": item_id, "type": wi_type, "title": title, "state": "New", "storage": "sqlite"}

    def _enforce_permissions(
        self,
        wi_type: str,
        target_state: str,
        assigned_to_profile: Optional[str] = None,
        current_assignee_profile: Optional[str] = None
    ) -> None:
        """Enforce role permissions from profiles/<role>/PROFILE.md during state transitions."""
        if (target_state or "").strip().lower() != "closed":
            return

        raw_profile = (assigned_to_profile or current_assignee_profile or "").strip()
        canonical_role = normalize_role(raw_profile)
        perms = get_role_permissions(canonical_role)

        if wi_type.lower() == "task":
            # G-HRN-1 / G-HRN-2: Only QC has can_close_task: true.
            # Lead, Peer, Supervisor, and unknown roles must be rejected.
            can_close = perms.get("can_close_task", False)
            if not can_close:
                dev_hint = " là DEV ONLY" if canonical_role == "peer" else ""
                profile_desc = f"profiles/{canonical_role}/PROFILE.md" if canonical_role else "PROFILE.md"
                raise PermissionError(
                    f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{raw_profile}'{dev_hint} không có quyền đóng Task "
                    f"('can_close_task: false' trong {profile_desc}). "
                    "Chỉ QC mới có quyền nghiệm thu và đóng Task."
                )
        elif wi_type.lower() in ("epic", "feature", "story", "user story", "technical story"):
            # Peer is DEV ONLY and strictly barred from closing macro artifacts
            if canonical_role == "peer":
                raise PermissionError(
                    f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{raw_profile}' là DEV ONLY. "
                    f"Nghiêm cấm Dev tự tiện đóng {wi_type} sang 'Closed'!"
                )

    def update_state(self, item_id: int, target_state: str, assigned_to: Optional[str] = None, assigned_to_profile: Optional[str] = None) -> Dict[str, Any]:
        """Update work item lifecycle state with State Machine transition check."""
        if self.backend == "floci":
            current_item = self.floci_db.get_work_item(item_id)
            if not current_item:
                raise ValueError(f"Work item #{item_id} not found in Floci DynamoDB.")

            current_state = current_item.get("state", "New")
            wi_type = current_item.get("type", "Task")
            title = current_item.get("title", f"Work Item #{item_id}")

            self._enforce_permissions(
                wi_type=wi_type,
                target_state=target_state,
                assigned_to_profile=assigned_to_profile,
                current_assignee_profile=current_item.get("assigned_to_profile") or current_item.get("assigned_to")
            )

            # Rào cản vai trò (PM Gate): Cấm gán hoặc kích hoạt Task thi công cho Lead/Supervisor (ngoại trừ khi đóng Closed)
            effective_assignee = (assigned_to_profile or assigned_to or current_item.get("assigned_to_profile") or current_item.get("assigned_to") or "").strip().lower()
            if wi_type.lower() == "task" and target_state.lower() != "closed":
                if any(r in effective_assignee for r in ("lead", "supervisor")):
                    raise PermissionError(
                        f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{effective_assignee}' là QUẢN LÝ / KIẾN TRÚC. "
                        "Nghiêm cấm gán hoặc kích hoạt Task thi công cho Lead/Supervisor! Task bắt buộc phải gán cho Peer (Peer 1..4) hoặc QC."
                    )

            if wi_type in VALID_TRANSITIONS:
                allowed = VALID_TRANSITIONS[wi_type].get(current_state, [])
                if target_state not in allowed:
                    raise ValueError(f"Invalid transition for {wi_type} #{item_id}: '{current_state}' -> '{target_state}'. Allowed: {allowed}")

            # Note: floci_db.update_work_item_state might need assigned_to_profile, but for now we just pass assigned_to if we don't modify it.
            # To properly update assigned_to_profile, we'd need to modify floci_client.py as well.
            updated = self.floci_db.update_work_item_state(item_id, target_state, assigned_to, assigned_to_profile)
            if target_state.lower() == "closed":
                cleaned = cleanup_task_room(item_id)
                if cleaned > 0:
                    print(f"[bmad/rooms] Task #{item_id} Closed -> Đã dọn dẹp {cleaned} file biên bản trong bmad/rooms/.")
            try:
                from orca_harness_bridge import sync_state_to_orca  # type: ignore
                sync_state_to_orca(str(item_id), target_state)
            except Exception:
                pass
            
            auto_dispatch_agent(
                item_id=item_id,
                wi_type=wi_type,
                title=title,
                target_state=target_state,
                assigned_to=assigned_to or current_item.get("assigned_to"),
                assigned_to_profile=assigned_to_profile or current_item.get("assigned_to_profile"),
                prev_state=current_state
            )

            return {
                "success": True,
                "id": item_id,
                "previous_state": current_state,
                "new_state": target_state,
                "assigned_to": updated.get("assigned_to"),
                "storage": "floci-dynamodb"
            }

        # SQLite fallback
        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT id, type, state, title, assigned_to, assigned_to_profile FROM work_item WHERE id = ?", (item_id,)).fetchone()
            if not row:
                raise ValueError(f"Work item #{item_id} not found in SQLite.")

            current_state = row["state"]
            wi_type = row["type"]
            title = row["title"]

            self._enforce_permissions(
                wi_type=wi_type,
                target_state=target_state,
                assigned_to_profile=assigned_to_profile,
                current_assignee_profile=row["assigned_to_profile"] or row["assigned_to"]
            )

            # Rào cản vai trò (PM Gate - SQLite branch): Cấm gán hoặc kích hoạt Task thi công cho Lead/Supervisor (ngoại trừ khi đóng Closed)
            sqlite_effective = (assigned_to_profile or assigned_to or row["assigned_to_profile"] or row["assigned_to"] or "").strip().lower()
            if wi_type.lower() == "task" and target_state.lower() != "closed":
                if any(r in sqlite_effective for r in ("lead", "supervisor")):
                    raise PermissionError(
                        f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{sqlite_effective}' là QUẢN LÝ / KIẾN TRÚC. "
                        "Nghiêm cấm gán hoặc kích hoạt Task thi công cho Lead/Supervisor! Task bắt buộc phải gán cho Peer (Peer 1..4) hoặc QC."
                    )

            if wi_type in VALID_TRANSITIONS:
                allowed = VALID_TRANSITIONS[wi_type].get(current_state, [])
                if target_state not in allowed:
                    raise ValueError(f"Invalid transition for {wi_type} #{item_id}: '{current_state}' -> '{target_state}'. Allowed: {allowed}")

            updates = ["state = ?", "updated_at = datetime('now')"]
            params = [target_state]

            if assigned_to:
                updates.append("assigned_to = ?")
                params.append(assigned_to)
            if assigned_to_profile:
                updates.append("assigned_to_profile = ?")
                params.append(assigned_to_profile)

            params.append(item_id)
            query = f"UPDATE work_item SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()
            if target_state.lower() == "closed":
                cleanup_task_room(item_id)

            auto_dispatch_agent(
                item_id=item_id,
                wi_type=wi_type,
                title=title,
                target_state=target_state,
                assigned_to=assigned_to or row["assigned_to"],
                assigned_to_profile=assigned_to_profile or row["assigned_to_profile"],
                prev_state=current_state
            )

            return {"success": True, "id": item_id, "previous_state": current_state, "new_state": target_state, "assigned_to": assigned_to, "storage": "sqlite"}

    def delete_work_item(self, item_id: int) -> Dict[str, Any]:
        """Delete a work item by ID."""
        if self.backend == "floci":
            self.floci_db.delete_work_item(item_id)
            return {"success": True, "id": item_id, "storage": "floci"}

        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM work_item WHERE id = ?", (item_id,))
            conn.commit()
            return {"success": True, "id": item_id, "storage": "sqlite"}

    def list_work_items(self, wi_type: Optional[str] = None, state: Optional[str] = None, source: Optional[str] = None, assigned_to_profile: Optional[str] = None, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.backend == "floci":
            return self.floci_db.list_work_items(wi_type=wi_type, state=state, source=source, assigned_to_profile=assigned_to_profile, parent_item_id=parent_id)

        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            query = "SELECT id, type, title, state, priority, assigned_to, assigned_to_profile, story_points, parent_id, source FROM work_item WHERE 1=1"
            params = []
            if wi_type:
                query += " AND type = ?"
                params.append(wi_type)
            if state:
                query += " AND state = ?"
                params.append(state)
            if source:
                query += " AND source = ?"
                params.append(source)
            if assigned_to_profile:
                query += " AND assigned_to_profile = ?"
                params.append(assigned_to_profile)
            if parent_id is not None:
                query += " AND parent_id = ?"
                params.append(parent_id)
            query += " ORDER BY id DESC"
            rows = cursor.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_work_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        if self.backend == "floci":
            return self.floci_db.get_work_item(item_id)

        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM work_item WHERE id = ?", (item_id,)).fetchone()
            return dict(row) if row else None

    def get_stats(self) -> Dict[str, Any]:
        if self.backend == "floci":
            stats = self.floci_db.get_stats()
            stats["engine"] = self.engine
            return stats

        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            by_type = {r[0]: r[1] for r in cursor.execute("SELECT type, COUNT(*) FROM work_item GROUP BY type")}
            stats = {"engine": self.backend, "total_work_items": sum(by_type.values()), "by_type": by_type}
            if self.backend == "rust":
                stats["native_binary"] = os.path.exists(os.path.join(BASE_DIR, "scripts/bin/harness-cli"))
            return stats

    def record_trace(
        self,
        task_summary: str,
        intake_id: Optional[int] = None,
        story_id: Optional[str] = None,
        agent: Optional[str] = None,
        actions_taken: Optional[Union[str, List[Any]]] = None,
        files_read: Optional[Union[str, List[str]]] = None,
        files_changed: Optional[Union[str, List[str]]] = None,
        decisions_made: Optional[Union[str, List[str]]] = None,
        errors: Optional[Union[str, List[str]]] = None,
        outcome: Optional[str] = "completed",
        duration_seconds: Optional[int] = None,
        token_estimate: Optional[int] = None,
        harness_friction: Optional[str] = None,
        notes: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> int:
        """
        Record an agent execution trace span into the canonical trace table (G-OBS-1).
        Conforms to 16 canonical columns from 001-init.sql / harness-cli plus run_id.
        Returns the inserted row ID.
        """
        def _to_json_str(val: Any) -> Optional[str]:
            if val is None:
                return None
            if isinstance(val, str):
                return val
            try:
                return json.dumps(val, ensure_ascii=False)
            except Exception:
                return str(val)

        norm_outcome = "completed"
        if outcome:
            o_lower = outcome.lower().strip()
            if o_lower in ("completed", "pass", "passed", "ok", "success"):
                norm_outcome = "completed"
            elif o_lower in ("failed", "fail", "error", "err"):
                norm_outcome = "failed"
            elif o_lower in ("blocked", "block"):
                norm_outcome = "blocked"
            elif o_lower in ("partial", "inconclusive", "warn", "warning"):
                norm_outcome = "partial"
            elif o_lower in ("completed", "blocked", "partial", "failed"):
                norm_outcome = o_lower
            else:
                norm_outcome = "completed"

        dur_sec = int(duration_seconds) if duration_seconds is not None else None
        tok_est = int(token_estimate) if token_estimate is not None else None

        with self._get_sqlite_db() as conn:
            cur = conn.cursor()
            # If story_id or intake_id are provided, ensure stub records exist in story and intake tables
            # so that FOREIGN KEY constraints are satisfied when referencing them in trace.
            if story_id is not None:
                try:
                    s_id_val = int(story_id) if str(story_id).isdigit() else str(story_id)
                    cur.execute("SELECT id FROM story WHERE id = ?;", (s_id_val,))
                    if not cur.fetchone():
                        cur.execute(
                            "INSERT OR IGNORE INTO story (id, title, state) VALUES (?, ?, 'New');",
                            (s_id_val, f"Story #{story_id}"),
                        )
                except Exception:
                    pass

            if intake_id is not None:
                try:
                    cur.execute("SELECT id FROM intake WHERE id = ?;", (intake_id,))
                    if not cur.fetchone():
                        cur.execute(
                            "INSERT OR IGNORE INTO intake (id, title) VALUES (?, ?);",
                            (intake_id, f"Intake #{intake_id}"),
                        )
                except Exception:
                    pass

            trace_cols = {r[1] for r in cur.execute("PRAGMA table_info(trace);").fetchall()}
            if "content" in trace_cols:
                cur.execute(
                    """
                    INSERT INTO trace (
                        task_summary, intake_id, story_id, agent,
                        actions_taken, files_read, files_changed, decisions_made,
                        errors, outcome, duration_seconds, token_estimate,
                        harness_friction, notes, run_id, content
                    ) VALUES (
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?
                    );
                    """,
                    (
                        task_summary,
                        intake_id,
                        str(story_id) if story_id is not None else None,
                        agent,
                        _to_json_str(actions_taken),
                        _to_json_str(files_read),
                        _to_json_str(files_changed),
                        _to_json_str(decisions_made),
                        _to_json_str(errors),
                        norm_outcome,
                        dur_sec,
                        tok_est,
                        harness_friction,
                        notes,
                        run_id,
                        task_summary or "",
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO trace (
                        task_summary, intake_id, story_id, agent,
                        actions_taken, files_read, files_changed, decisions_made,
                        errors, outcome, duration_seconds, token_estimate,
                        harness_friction, notes, run_id
                    ) VALUES (
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?
                    );
                    """,
                    (
                        task_summary,
                        intake_id,
                        str(story_id) if story_id is not None else None,
                        agent,
                        _to_json_str(actions_taken),
                        _to_json_str(files_read),
                        _to_json_str(files_changed),
                        _to_json_str(decisions_made),
                        _to_json_str(errors),
                        norm_outcome,
                        dur_sec,
                        tok_est,
                        harness_friction,
                        notes,
                        run_id,
                    ),
                )
            conn.commit()
            return int(cur.lastrowid or 0)

    def record_trace_span(
        self,
        run_id: str,
        stage: str,
        agent: str,
        task_summary: str,
        duration_seconds: int,
        outcome: str = "completed",
        errors: Optional[Union[str, List[str]]] = None,
        story_id: Optional[str] = None,
        intake_id: Optional[int] = None,
        token_estimate: Optional[int] = None,
        harness_friction: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs: Any,
    ) -> int:
        """
        Record a pipeline stage span conforming to M1 <-> M2 interface contract.
        Wraps record_trace with stage metadata and shared run_id.
        """
        combined_notes = notes
        if not combined_notes and stage:
            combined_notes = f"stage={stage}"
        elif stage and combined_notes and f"stage={stage}" not in combined_notes:
            combined_notes = f"stage={stage}; {combined_notes}"

        return self.record_trace(
            task_summary=task_summary,
            intake_id=intake_id,
            story_id=story_id,
            agent=agent,
            errors=errors,
            outcome=outcome,
            duration_seconds=duration_seconds,
            token_estimate=token_estimate,
            harness_friction=harness_friction,
            notes=combined_notes,
            run_id=run_id,
            **kwargs,
        )

    def get_trace(self, trace_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single trace record by primary key."""
        with self._get_sqlite_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM trace WHERE id = ?;", (trace_id,))
            row = cur.fetchone()
            if not row:
                return None
            d = dict(row)
            if "content" not in d and "task_summary" in d:
                d["content"] = d["task_summary"]
            return d

    def list_traces(
        self,
        run_id: Optional[str] = None,
        story_id: Optional[str] = None,
        agent: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List trace records, optionally filtered by run_id, story_id, or agent."""
        query = "SELECT * FROM trace WHERE 1=1"
        params: List[Any] = []
        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
        if story_id:
            query += " AND story_id = ?"
            params.append(str(story_id))
        if agent:
            query += " AND agent = ?"
            params.append(agent)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self._get_sqlite_db() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            res = []
            for r in cur.fetchall():
                d = dict(r)
                if "content" not in d and "task_summary" in d:
                    d["content"] = d["task_summary"]
                res.append(d)
            return res

    def record_intervention(
        self,
        target_type: str,
        target_id: int,
        actor: str,
        reason: str,
        action: Optional[str] = None
    ) -> int:
        """Record reviewer/human intervention into the intervention table."""
        with self._get_sqlite_db() as conn:
            cur = conn.cursor()
            cols = {r[1] for r in cur.execute("PRAGMA table_info(intervention);").fetchall()}
            if "action" in cols:
                cur.execute(
                    """
                    INSERT INTO intervention (target_type, target_id, actor, action, reason)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (target_type, int(target_id), actor, action or "approved", reason)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO intervention (target_type, target_id, actor, reason)
                    VALUES (?, ?, ?, ?)
                    """,
                    (target_type, int(target_id), actor, f"[{action.upper()}] {reason}" if action else reason)
                )
            conn.commit()
            return int(cur.lastrowid or 0)

    def get_interventions(
        self,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query intervention history."""
        with self._get_sqlite_db() as conn:
            cur = conn.cursor()
            query = "SELECT * FROM intervention WHERE 1=1"
            params: List[Any] = []
            if target_type:
                query += " AND target_type = ?"
                params.append(target_type)
            if target_id is not None:
                query += " AND target_id = ?"
                params.append(int(target_id))
            query += " ORDER BY id DESC"
            rows = cur.execute(query, params).fetchall()
            return [dict(r) for r in rows]

def main():
    parser = argparse.ArgumentParser(description="Harness Operating Framework Manager Tool (Floci / DynamoDB)")
    parser.add_argument("--engine", choices=["auto", "floci", "rust", "sqlite"], default="auto", help="Execution engine (default: auto)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: add
    p_add = subparsers.add_parser("add", help="Add a new work item")
    p_add.add_argument("--type", required=True, choices=["Epic", "Feature", "User Story", "Technical Story", "Task", "Bug", "Testcase"])
    p_add.add_argument("--title", required=True, help="Work item title (strictly formatted)")
    p_add.add_argument("--description", default="", help="Description (BDD format for User Story)")
    p_add.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"])
    p_add.add_argument("--assigned-to", default=None)
    p_add.add_argument("--parent-id", type=int, default=None)
    p_add.add_argument("--story-points", type=int, default=None)
    p_add.add_argument("--ac", default=None, help="Acceptance criteria")
    p_add.add_argument("--source", default="local", help="Source: remote, local, bot")
    p_add.add_argument("--created-by-profile", default=None, help="Profile that created this (e.g. supervisor, lead)")
    p_add.add_argument("--assigned-to-profile", default=None, help="Profile assigned to this (e.g. lead, peer-eng)")
    p_add.add_argument("--dispatch", action="store_true", help="Automatically trigger/wake up the assigned agent profile via Paseo")

    # Subcommand: update
    p_up = subparsers.add_parser("update", help="Update work item state")
    p_up.add_argument("--id", type=int, required=True)
    p_up.add_argument("--state", required=True, choices=["New", "Accepted", "Active", "Resolved", "Closed", "Blocked", "Removed"])
    p_up.add_argument("--assigned-to", default=None)
    p_up.add_argument("--assigned-to-profile", default=None)
    p_up.add_argument("--dispatch", action="store_true", help="Automatically trigger/wake up the assigned agent profile via Paseo")

    # Subcommand: list
    p_list = subparsers.add_parser("list", help="List work items")
    p_list.add_argument("--type", default=None)
    p_list.add_argument("--state", default=None)
    p_list.add_argument("--source", default=None)
    p_list.add_argument("--assigned-to-profile", default=None)
    p_list.add_argument("--parent-id", type=int, default=None)

    # Subcommand: get
    p_get = subparsers.add_parser("get", help="Get a single work item by ID")
    p_get.add_argument("id", type=int, help="Work item ID")

    # Subcommand: delete
    p_del = subparsers.add_parser("delete", help="Delete a work item by ID")
    p_del.add_argument("--id", type=int, required=True, help="Work item ID to delete")

    # Subcommand: stats
    subparsers.add_parser("stats", help="Get work item statistics")

    # Subcommand: profiles
    subparsers.add_parser("profiles", help="List available Paseo Agent Profiles")

    args = parser.parse_args()
    mgr = HarnessManager(engine=args.engine)

    try:
        if args.command == "profiles":
            profiles = mgr.get_allowed_profiles()
            print(json.dumps({"profiles": profiles, "total": len(profiles)}, indent=2, ensure_ascii=False))
        elif args.command == "add":
            res = mgr.add_work_item(
                wi_type=args.type,
                title=args.title,
                description=args.description,
                priority=args.priority,
                assigned_to=args.assigned_to,
                parent_id=args.parent_id,
                story_points=args.story_points,
                acceptance_criteria=args.ac,
                source=args.source,
                created_by_profile=args.created_by_profile,
                assigned_to_profile=args.assigned_to_profile
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))
            if getattr(args, "dispatch", False) and args.assigned_to_profile:
                item_id = res.get("id")
                prompt = f"Work Item #{item_id} [{args.type}]: {args.title}\n{args.description}"
                if shutil.which("orca"):
                    send_orca_notification(args.assigned_to_profile, prompt)
                else:
                    call_script = os.path.join(BASE_DIR, "tools", "call_agent.py")
                    if os.path.exists(call_script):
                        subprocess.run(["python3", call_script, "--profile", args.assigned_to_profile, "--prompt", prompt, "--item-id", str(item_id)])
        elif args.command == "update":
            res = mgr.update_state(item_id=args.id, target_state=args.state, assigned_to=args.assigned_to, assigned_to_profile=args.assigned_to_profile)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            # Lưu ý: update_state đã gọi auto_dispatch_agent cho Active/Accepted/Resolved/Closed trên Orca.
            # Chỉ gọi call_agent.py khi không có Orca hoặc state nằm ngoài luồng auto_dispatch_agent.
            if getattr(args, "dispatch", False) and args.assigned_to_profile and not shutil.which("orca"):
                call_script = os.path.join(BASE_DIR, "tools", "call_agent.py")
                if os.path.exists(call_script):
                    item = mgr.get_work_item(args.id) or {}
                    title = item.get("title", f"Work Item #{args.id}")
                    prompt = f"Work Item #{args.id} transitioned to '{args.state}': {title}"
                    subprocess.run(["python3", call_script, "--profile", args.assigned_to_profile, "--prompt", prompt, "--item-id", str(args.id)])
        elif args.command == "list":
            items = mgr.list_work_items(wi_type=args.type, state=args.state, source=args.source, assigned_to_profile=args.assigned_to_profile, parent_id=args.parent_id)
            print(json.dumps(items, indent=2, ensure_ascii=False))
        elif args.command == "get":
            item = mgr.get_work_item(args.id)
            if not item:
                print(f"Error: Work item #{args.id} not found.", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(item, indent=2, ensure_ascii=False))
        elif args.command == "delete":
            res = mgr.delete_work_item(args.id)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        elif args.command == "stats":
            stats = mgr.get_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
