#!/usr/bin/env python3
"""
tools/remote_sync.py - Synchronize full backlog and work items across all sprints from REMOTE ACME to Floci DynamoDB.
Strips all raw HTML tags and converts REMOTE rich text to clean Markdown / plain text.
"""

import os
import sys
import json
import base64
import html
import re
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, BASE_DIR)

from tools.floci_client import FlociHarnessDB

REMOTE_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL", "https://remote.example.com/MainCollection").rstrip("/")
REMOTE_PROJECT = os.getenv("AZURE_DEVOPS_DEFAULT_PROJECT", "ACME")
REMOTE_PAT = os.getenv("AZURE_DEVOPS_PAT", "")

if not REMOTE_PAT:
    # Try reading from global mcp_config.json if available
    mcp_cfg_path = os.path.expanduser("~/.gemini/config/mcp_config.json")
    if os.path.exists(mcp_cfg_path):
        try:
            with open(mcp_cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                REMOTE_PAT = cfg.get("mcpServers", {}).get("remote-crm", {}).get("env", {}).get("AZURE_DEVOPS_PAT", "")
        except Exception:
            pass

def clean_html(raw_html: Optional[str]) -> str:
    """Strip raw HTML tags and convert entities to clean readable plain text / markdown."""
    if not raw_html:
        return ""
    # Convert line breaks and paragraph ends to newlines
    text = re.sub(r'<(?:br\s*/?|/p|/div|/li)>', '\n', raw_html, flags=re.IGNORECASE)
    # Convert list items to bullet points
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities (&nbsp;, &lt;, &gt;, &quot;, &#39;, etc.)
    text = html.unescape(text)
    # Clean whitespace while preserving meaningful newlines
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(l for l in lines if l).strip()

def get_auth_headers() -> Dict[str, str]:
    token_b64 = base64.b64encode(f":{REMOTE_PAT}".encode("utf-8")).decode("ascii")
    return {
        "Authorization": f"Basic {token_b64}",
        "Content-Type": "application/json"
    }

def fetch_all_remote_work_item_ids() -> List[int]:
    wiql_url = f"{REMOTE_ORG_URL}/{REMOTE_PROJECT}/_apis/wit/wiql?api-version=5.0"
    payload = {
        "query": f"SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = '{REMOTE_PROJECT}' ORDER BY [System.IterationPath] ASC, [System.Id] ASC"
    }
    req = urllib.request.Request(
        wiql_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=get_auth_headers(),
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return [w["id"] for w in data.get("workItems", [])]

def fetch_work_items_batch(ids: List[int]) -> List[Dict[str, Any]]:
    if not ids:
        return []
    ids_str = ",".join(str(i) for i in ids)
    url = f"{REMOTE_ORG_URL}/_apis/wit/workitems?ids={ids_str}&api-version=5.0"
    req = urllib.request.Request(url, headers=get_auth_headers())
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("value", [])

def sync_full_backlog() -> Dict[str, Any]:
    print(f"--> Connecting to REMOTE ({REMOTE_ORG_URL}) project '{REMOTE_PROJECT}'...")
    all_ids = fetch_all_remote_work_item_ids()
    print(f"--> Found {len(all_ids)} work items in REMOTE ACME across all sprints.")

    db = FlociHarnessDB()
    db.init_schema()

    batch_size = 100
    synced_count = 0
    stories_synced = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Map REMOTE priority (1,2,3,4) to P0, P1, P2, P3
    priority_map = {1: "P0", 2: "P1", 3: "P2", 4: "P3"}

    for i in range(0, len(all_ids), batch_size):
        chunk_ids = all_ids[i:i + batch_size]
        items = fetch_work_items_batch(chunk_ids)

        for item in items:
            remote_id = item.get("id")
            fields = item.get("fields", {})

            wi_type = fields.get("System.WorkItemType", "Task")
            if wi_type == "Test Case":
                wi_type = "Testcase"

            title = clean_html(fields.get("System.Title", ""))
            state = fields.get("System.State", "New")
            assigned = fields.get("System.AssignedTo", {})
            assigned_name = assigned.get("displayName") if isinstance(assigned, dict) else (assigned or None)
            
            raw_priority = fields.get("Microsoft.VSTS.Common.Priority", 3)
            priority = priority_map.get(raw_priority, "P2")

            iteration = fields.get("System.IterationPath", "")
            area = fields.get("System.AreaPath", "")
            story_points = fields.get("Microsoft.VSTS.Scheduling.StoryPoints")
            remaining_work = fields.get("Microsoft.VSTS.Scheduling.RemainingWork")
            
            # Clean HTML from description and acceptance criteria
            raw_ac = fields.get("Microsoft.VSTS.Common.AcceptanceCriteria") or ""
            raw_desc = fields.get("System.Description") or ""
            ac = clean_html(raw_ac)
            desc = clean_html(raw_desc)
            tags = fields.get("System.Tags")

            # 1. Store in harness_work_items
            harness_item = {
                "id": remote_id,
                "type": wi_type,
                "title": title,
                "description": desc,
                "state": state,
                "priority": priority,
                "assigned_to": assigned_name,
                "story_points": int(story_points) if story_points is not None else None,
                "remaining_work": float(remaining_work) if remaining_work is not None else None,
                "area_path": area,
                "iteration_path": iteration,
                "tags": tags,
                "acceptance_criteria": ac,
                "source": "remote",
                "remote_url": item.get("_links", {}).get("html", {}).get("href"),
                "synced_at": now_str,
                "created_at": fields.get("System.CreatedDate", now_str),
                "updated_at": fields.get("System.ChangedDate", now_str)
            }
            db.put_work_item(harness_item)
            synced_count += 1

            # 2. If it's a User Story or Bug, also register into harness_stories (for test matrix)
            if wi_type in ["User Story", "Technical Story"]:
                story_entry = {
                    "id": remote_id,
                    "title": title,
                    "state": state,
                    "priority": priority,
                    "verify_command": f"npm run test:e2e -- --story={remote_id}",
                    "last_verified_at": None,
                    "last_verified_result": "UNVERIFIED",
                    "acceptance_criteria": ac,
                    "source": "remote",
                    "created_at": fields.get("System.CreatedDate", now_str),
                    "updated_at": fields.get("System.ChangedDate", now_str)
                }
                db.put_story(story_entry)
                stories_synced += 1

        print(f"    Processed & cleaned {min(i + batch_size, len(all_ids))}/{len(all_ids)} items...")

    print(f"✓ Successfully synced and cleaned {synced_count} work items ({stories_synced} user stories) to Floci DynamoDB!")
    return {"status": "success", "total_synced": synced_count, "stories_synced": stories_synced}

if __name__ == "__main__":
    sync_full_backlog()
