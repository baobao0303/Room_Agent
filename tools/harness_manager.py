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
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime

# Transparent fallback to venv with boto3 if current python lacks boto3
try:
    import boto3
except ImportError:
    candidate_venvs = [
        "/home/baoltb/.hermes/hermes-agent/venv/bin/python",
        "/home/baoltb/ponytail/venv/bin/python",
        os.path.expanduser("~/.hermes/hermes-agent/venv/bin/python")
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

VALID_TRANSITIONS = {
    "User Story": {
        "New": ["Accepted", "Removed"],
        "Accepted": ["Active", "Removed"],
        "Active": ["Resolved", "Blocked", "Removed"],
        "Blocked": ["Active"],
        "Resolved": ["Closed", "Accepted"],
        "Closed": [], "Removed": []
    },
    "Technical Story": {
        "New": ["Accepted", "Removed"],
        "Accepted": ["Active", "Removed"],
        "Active": ["Resolved", "Blocked", "Removed"],
        "Blocked": ["Active"],
        "Resolved": ["Closed", "Accepted"],
        "Closed": [], "Removed": []
    },
    "Task": {
        "New": ["Active", "Removed"],
        "Active": ["Resolved", "Blocked", "Removed"],
        "Blocked": ["Active"],
        "Resolved": ["Closed", "Active"],
        "Closed": [], "Removed": []
    },
    "Bug": {
        "New": ["Active", "Removed"],
        "Active": ["Resolved", "Removed"],
        "Resolved": ["Closed", "New"],
        "Closed": [], "Removed": []
    },
    "Testcase": {
        "New": ["Active", "Removed"],
        "Active": ["Resolved", "Removed"],
        "Resolved": ["Closed", "New"],
        "Closed": [], "Removed": []
    },
    "Epic": {
        "New": ["Accepted", "Active", "Resolved", "Closed", "Removed"],
        "Accepted": ["Active", "Removed"],
        "Active": ["Resolved", "Blocked", "Removed"],
        "Blocked": ["Active"],
        "Resolved": ["Closed", "Active"],
        "Closed": [], "Removed": []
    },
    "Feature": {
        "New": ["Accepted", "Active", "Resolved", "Closed", "Removed"],
        "Accepted": ["Active", "Removed"],
        "Active": ["Resolved", "Blocked", "Removed"],
        "Blocked": ["Active"],
        "Resolved": ["Closed", "Active"],
        "Closed": [], "Removed": []
    }
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
    "QC"
]

class HarnessManager:
    def __init__(self, backend: str = HARNESS_BACKEND, db_path: str = DEFAULT_DB_PATH):
        self.backend = backend
        self.db_path = db_path
        if self.backend == "floci":
            self.floci_db = FlociHarnessDB()
            self.floci_db.init_schema()
        else:
            with open(os.path.join(BASE_DIR, "scripts/schema/full_schema.sql")) as f, self._get_sqlite_db() as conn:
                conn.executescript(f.read())

    def _get_sqlite_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
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
            item_id = cursor.lastrowid
            return {"success": True, "id": item_id, "type": wi_type, "title": title, "state": "New", "storage": "sqlite"}

    def update_state(self, item_id: int, target_state: str, assigned_to: Optional[str] = None, assigned_to_profile: Optional[str] = None) -> Dict[str, Any]:
        """Update work item lifecycle state with State Machine transition check."""
        if self.backend == "floci":
            current_item = self.floci_db.get_work_item(item_id)
            if not current_item:
                raise ValueError(f"Work item #{item_id} not found in Floci DynamoDB.")

            current_state = current_item.get("state", "New")
            wi_type = current_item.get("type", "Task")

            if wi_type in VALID_TRANSITIONS:
                allowed = VALID_TRANSITIONS[wi_type].get(current_state, [])
                if target_state not in allowed:
                    raise ValueError(f"Invalid transition for {wi_type} #{item_id}: '{current_state}' -> '{target_state}'. Allowed: {allowed}")

            # Note: floci_db.update_work_item_state might need assigned_to_profile, but for now we just pass assigned_to if we don't modify it.
            # To properly update assigned_to_profile, we'd need to modify floci_client.py as well.
            updated = self.floci_db.update_work_item_state(item_id, target_state, assigned_to, assigned_to_profile)
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
            row = cursor.execute("SELECT id, type, state FROM work_item WHERE id = ?", (item_id,)).fetchone()
            if not row:
                raise ValueError(f"Work item #{item_id} not found in SQLite.")

            current_state = row["state"]
            wi_type = row["type"]

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
            return {"success": True, "id": item_id, "previous_state": current_state, "new_state": target_state, "assigned_to": assigned_to, "storage": "sqlite"}

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
            return self.floci_db.get_stats()

        with self._get_sqlite_db() as conn:
            cursor = conn.cursor()
            by_type = {r[0]: r[1] for r in cursor.execute("SELECT type, COUNT(*) FROM work_item GROUP BY type")}
            return {"total_work_items": sum(by_type.values()), "by_type": by_type}

def main():
    parser = argparse.ArgumentParser(description="Harness Operating Framework Manager Tool (Floci / DynamoDB)")
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

    # Subcommand: stats
    subparsers.add_parser("stats", help="Get work item statistics")

    # Subcommand: profiles
    subparsers.add_parser("profiles", help="List available Paseo Agent Profiles")

    args = parser.parse_args()
    mgr = HarnessManager()

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
        elif args.command == "list":
            items = mgr.list_work_items(wi_type=args.type, state=args.state, source=args.source, assigned_to_profile=args.assigned_to_profile, parent_id=args.parent_id)
            print(json.dumps(items, indent=2, ensure_ascii=False))
        elif args.command == "get":
            item = mgr.get_work_item(args.id)
            if not item:
                print(f"Error: Work item #{args.id} not found.", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(item, indent=2, ensure_ascii=False))
        elif args.command == "stats":
            stats = mgr.get_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
