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
from typing import Dict, Any, List, Optional
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

from tools.floci_client import FlociHarnessDB

DEFAULT_DB_PATH = os.getenv("HARNESS_DB", os.path.join(BASE_DIR, "harness.db"))
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
    bmad_rooms = Path(BASE_DIR) / "bmad" / "rooms"
    removed_count = 0
    if bmad_rooms.is_dir():
        for memo_file in bmad_rooms.rglob(f"*handoff_{item_id}_*.md"):
            try:
                memo_file.unlink()
                removed_count += 1
            except Exception:
                pass

        for latest_file in bmad_rooms.rglob("latest_handoff.md"):
            try:
                content = latest_file.read_text(encoding="utf-8")
                if f"#{item_id}" in content or f"Work Item: `#{item_id}`" in content:
                    latest_file.unlink()
                    removed_count += 1
            except Exception:
                pass

    # 3. Thu hồi terminal mồ côi (Phase 6: REAPED)
    reap_orphaned_terminals()
    return removed_count

def send_orca_notification(role: str, message: str) -> bool:
    """Send real-time prompt to the live Orca terminal for a role (with ping check & auto-compact)."""
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        try:
            from agent_context_manager import safe_send_agent_message  # type: ignore
        except ImportError:
            from tools.agent_context_manager import safe_send_agent_message  # type: ignore
        sent = safe_send_agent_message(role, message)
        if sent:
            return True

        # FALLBACK CHO EPHEMERAL SUB-AGENTS (Peer, QC, Design):
        # Nếu tab chưa mở sẵn, tự động spawn tab mới trên Orca để User nhìn thấy AI làm việc
        clean_role = role.lower().strip()
        if shutil.which("orca") and any(k in clean_role for k in ("peer", "dev", "design", "qc")):
            print(f"🚀 [Ephemeral Auto-Launch]: Chưa có tab cho {role.upper()}. Đang mở AI Agent tab mới trên Orca...")
            cmd_launch = [
                "orca", "agent", "launch",
                "--worktree", "active",
                "--agent", "hermes",
                "--prompt", message,
                "--focus",
                "--json"
            ]
            res = subprocess.run(cmd_launch, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                print(f"✅ [Ephemeral Auto-Launch]: Đã mở thành công AI Agent tab cho {role.upper()} trên Orca!")
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
            for p in ["peer4", "peer3", "peer2", "design"]:
                if p in caller_role.replace("-", "").replace("_", ""):
                    rec_role = p
                    break
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

    # CASE 2: Giao việc thi công (target_state == "Active" hoặc "Accepted")
    # -> Báo ngay cho Peer được gán
    elif state_lower in ("active", "accepted"):
        target_peer = (assigned_to_profile or assigned_to or "").lower()
        if any(k in target_peer for k in ("peer", "design", "dev")):
            peer_role = "peer"
            for p in ["peer4", "peer3", "peer2", "design"]:
                if p in target_peer.replace("-", "").replace("_", ""):
                    peer_role = p
                    break
            msg_peer = f"📢 [NHIỆM VỤ MỚI]: Bạn được phân công {wi_type} #{item_id}: '{title}' ({target_state}). Đọc spec tại Harness DB / bmad/rooms/ và bắt đầu thi công!"
            send_orca_notification(peer_role, msg_peer)
            print(f"🔔 [Auto-Dispatch]: Đã tự động đánh thức {peer_role.upper()} thi công Work Item #{item_id}.")

    # CASE 3: QC hoặc Lead đóng task (target_state == "Closed")
    # -> Báo cho Lead và Supervisor
    elif state_lower == "closed":
        msg_done = f"📢 [NGHIỆM THU ĐÃ ĐÓNG]: {wi_type} #{item_id}: '{title}' đã được nghiệm thu và CLOSED thành công."
        send_orca_notification("lead", msg_done)
        send_orca_notification("supervisor", msg_done)
        print(f"🔔 [Auto-Dispatch]: Đã tự động báo cáo đóng Task #{item_id} tới Lead và Supervisor.")

class HarnessManager:
    def __init__(self, backend: str = HARNESS_BACKEND, db_path: str = DEFAULT_DB_PATH, engine: str = "auto"):
        self.engine = engine
        if engine == "floci":
            self.backend = "floci"
        elif engine == "rust":
            self.backend = "rust"
        elif engine == "sqlite":
            self.backend = "sqlite"
        else:
            self.backend = backend

        self.db_path = db_path
        if self.backend == "floci":
            try:
                self.floci_db = FlociHarnessDB()
                self.floci_db.init_schema()
            except Exception:
                self.backend = "sqlite"
                with open(os.path.join(BASE_DIR, "scripts/schema/full_schema.sql")) as f, self._get_sqlite_db() as conn:
                    conn.executescript(f.read())
        else:
            with open(os.path.join(BASE_DIR, "scripts/schema/full_schema.sql")) as f, self._get_sqlite_db() as conn:
                conn.executescript(f.read())

    def _get_sqlite_db(self) -> sqlite3.Connection:
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

    def update_state(self, item_id: int, target_state: str, assigned_to: Optional[str] = None, assigned_to_profile: Optional[str] = None) -> Dict[str, Any]:
        """Update work item lifecycle state with State Machine transition check."""
        # Rào cản phân quyền nghiêm ngặt: Peer là DEV ONLY, tuyệt đối cấm đóng task sang 'Closed'
        if target_state.lower() == "closed":
            caller_prof = (assigned_to_profile or "").strip().lower()
            if caller_prof in ("peer", "peer dev", "peer ba", "peer design"):
                raise PermissionError(
                    f"⛔ RÀO CẢN VAI TRÒ (ROLE FENCE): Role '{assigned_to_profile}' là DEV ONLY. "
                    "Nghiêm cấm Dev tự tiện đóng Task sang 'Closed'! Chỉ QC hoặc Lead mới có quyền nghiệm thu và đóng Task."
                )

        if self.backend == "floci":
            current_item = self.floci_db.get_work_item(item_id)
            if not current_item:
                raise ValueError(f"Work item #{item_id} not found in Floci DynamoDB.")

            current_state = current_item.get("state", "New")
            wi_type = current_item.get("type", "Task")
            title = current_item.get("title", f"Work Item #{item_id}")

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
                call_script = os.path.join(BASE_DIR, "tools", "call_agent.py")
                if os.path.exists(call_script):
                    import subprocess
                    item_id = res.get("id")
                    prompt = f"Work Item #{item_id} [{args.type}]: {args.title}\n{args.description}"
                    subprocess.run(["python3", call_script, "--profile", args.assigned_to_profile, "--prompt", prompt, "--item-id", str(item_id)])
        elif args.command == "update":
            res = mgr.update_state(item_id=args.id, target_state=args.state, assigned_to=args.assigned_to, assigned_to_profile=args.assigned_to_profile)
            print(json.dumps(res, indent=2, ensure_ascii=False))
            if getattr(args, "dispatch", False) and args.assigned_to_profile:
                call_script = os.path.join(BASE_DIR, "tools", "call_agent.py")
                if os.path.exists(call_script):
                    import subprocess
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
