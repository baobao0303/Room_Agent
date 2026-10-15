#!/usr/bin/env python3
"""
tools/remote_mcp_server.py - High-Performance Model Context Protocol (MCP) Server for Remote Azure DevOps
Provides full stdio JSON-RPC 2.0 interface for Work Items, Repositories, Pull Requests, Use Cases, and Git.
"""

import sys
import os
import re
import json
import base64
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
_default_doc = next((p for p in [BASE_DIR / "projects/crm-doc", BASE_DIR.parent / "wicx-crm-doc", BASE_DIR.parent / "crm-doc"] if p.exists()), BASE_DIR.parent / "wicx-crm-doc")
_default_fe = next((p for p in [BASE_DIR / "projects/wicx-crm-fe", BASE_DIR / "projects/crm-fe", BASE_DIR.parent / "crm-fe"] if p.exists()), BASE_DIR / "projects/wicx-crm-fe")
DOC_REPO_PATH = Path(os.getenv("DOC_REPO_PATH") or os.getenv("CRM_DOC_PATH") or str(_default_doc))
FE_REPO_PATH = Path(os.getenv("FE_REPO_PATH") or os.getenv("CRM_FE_PATH") or str(_default_fe))
CRM_DOC_READER = BASE_DIR / "tools/crm_doc_reader.py"

# REMOTE Configuration
REMOTE_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL", "").rstrip("/")
REMOTE_PROJECT = os.getenv("AZURE_DEVOPS_DEFAULT_PROJECT") or os.getenv("AZURE_DEVOPS_PROJECT", "")
REMOTE_PAT = os.getenv("AZURE_DEVOPS_PAT", "")

def get_remote_config() -> tuple[str, str, str]:
    """Validate and return (org_url, project, pat) from environment variables.
    Fails with clear ValueError if any required variable is unset."""
    org_url = os.getenv("AZURE_DEVOPS_ORG_URL", REMOTE_ORG_URL).rstrip("/")
    project = os.getenv("AZURE_DEVOPS_DEFAULT_PROJECT") or os.getenv("AZURE_DEVOPS_PROJECT", REMOTE_PROJECT)
    pat = os.getenv("AZURE_DEVOPS_PAT", REMOTE_PAT)
    missing = []
    if not org_url:
        missing.append("AZURE_DEVOPS_ORG_URL")
    if not project:
        missing.append("AZURE_DEVOPS_DEFAULT_PROJECT (or AZURE_DEVOPS_PROJECT)")
    if not pat:
        missing.append("AZURE_DEVOPS_PAT")
    if missing:
        raise ValueError(f"Missing required environment variables for Remote MCP Server: {', '.join(missing)}")
    return org_url, project, pat

def get_auth_header() -> Dict[str, str]:
    _, _, pat = get_remote_config()
    token_b64 = base64.b64encode(f":{pat}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token_b64}"}

def remote_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    org_url, _, _ = get_remote_config()
    url = f"{org_url}/{endpoint}"
    if params:
        query_str = urllib.parse.urlencode(params)
        url = f"{url}?{query_str}"
    headers = get_auth_header()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def remote_api_post(endpoint: str, payload: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Any:
    org_url, _, _ = get_remote_config()
    url = f"{org_url}/{endpoint}"
    if params:
        query_str = urllib.parse.urlencode(params)
        url = f"{url}?{query_str}"
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

ALLOWED_WORK_ITEM_TYPES = {
    "User Story", "Bug", "Task", "Epic", "Feature", "Issue", "Test Case", "Testcase", "Technical Story"
}
ALLOWED_STATES = {
    "New", "Active", "Resolved", "Closed", "Removed", "Done",
    "In Progress", "To Do", "Committed", "Approved", "Accepted", "Blocked"
}
ALLOWED_FIELDS = {
    "System.Id",
    "System.Title",
    "System.WorkItemType",
    "System.State",
    "System.AssignedTo",
    "System.CreatedDate",
    "System.ChangedDate",
    "System.AreaPath",
    "System.IterationPath",
    "System.Description",
    "System.Tags",
    "Microsoft.VSTS.Common.Priority",
    "Microsoft.VSTS.Common.AcceptanceCriteria",
    "Microsoft.VSTS.Scheduling.StoryPoints",
    "Microsoft.VSTS.Scheduling.RemainingWork",
}

def escape_wiql_literal(value: Any) -> str:
    """Escape single quotes in values for WIQL queries."""
    return str(value).replace("'", "''")

TOOLS_SCHEMA = [
    {
        "name": "remote_list_work_items",
        "description": "List recent work items (User Stories, Bugs, Tasks, Epics) from configured Remote Azure DevOps project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "work_item_type": {
                    "type": "string",
                    "description": "Filter by type (e.g. 'User Story', 'Bug', 'Task', 'Epic', or omit for all)",
                    "enum": ["User Story", "Bug", "Task", "Epic", "Feature"]
                },
                "state": {
                    "type": "string",
                    "description": "Filter by state (e.g. 'New', 'Active', 'Resolved', 'Closed')"
                },
                "top": {
                    "type": "integer",
                    "description": "Maximum number of items to return (default: 15)",
                    "default": 15
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of fields to retrieve (must be in whitelist)"
                }
            }
        }
    },
    {
        "name": "remote_get_work_item",
        "description": "Retrieve full details, description, acceptance criteria, state, and fields of a Remote Work Item by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "work_item_id": {
                    "type": "integer",
                    "description": "Remote Work Item ID (e.g. 160736)"
                }
            },
            "required": ["work_item_id"]
        }
    },
    {
        "name": "remote_query_wiql",
        "description": "Execute a custom WIQL (Work Item Query Language) query on configured Remote Azure DevOps project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wiql": {
                    "type": "string",
                    "description": "WIQL query string starting with SELECT (e.g. 'SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = @project AND [System.WorkItemType] = \\'Bug\\' ORDER BY [System.ChangedDate] DESC')"
                }
            },
            "required": ["wiql"]
        }
    },
    {
        "name": "remote_list_repositories",
        "description": "List all Git repositories under configured Remote Azure DevOps project.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "remote_list_pull_requests",
        "description": "List active or completed Pull Requests for a Remote repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string",
                    "description": "Repository name (e.g. 'crm-fe', 'crm-crm')",
                    "default": "crm-fe"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status: 'active', 'completed', 'abandoned', 'all'",
                    "enum": ["active", "completed", "abandoned", "all"],
                    "default": "active"
                }
            }
        }
    },
    {
        "name": "remote_search_use_cases",
        "description": "Semantic search across all CRM Use Cases (UC1.01 to UC4.09), User Stories, and Acceptance Criteria from Remote docs/base.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword or question (e.g. 'Hồ sơ khách hàng 360', 'Facebook connect', 'Zalo OA')"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top matching results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "remote_get_use_case",
        "description": "Retrieve full detailed specification, acceptance criteria, and flow for a specific Use Case by its ID (e.g. UC1.01, UC2.05).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "use_case_id": {
                    "type": "string",
                    "description": "Use Case identifier (e.g. 'UC1.01', 'UC2.05', 'UC4.01')"
                }
            },
            "required": ["use_case_id"]
        }
    },
    {
        "name": "remote_sync_docs",
        "description": "Synchronize and pull latest documentation changes from Remote repository (branch docs/base).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "remote_list_doc_tree",
        "description": "Get hierarchical directory tree of all CRM documentation on Remote.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "remote_git_status",
        "description": "Get git branch and working tree status for Remote repositories (crm-doc or crm-fe).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Target repository: 'doc' (crm-doc) or 'fe' (crm-fe)",
                    "enum": ["doc", "fe"],
                    "default": "doc"
                }
            }
        }
    },
    {
        "name": "remote_git_log",
        "description": "View recent git commit log from Remote repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Target repository: 'doc' (crm-doc) or 'fe' (crm-fe)",
                    "enum": ["doc", "fe"],
                    "default": "doc"
                },
                "max_count": {
                    "type": "integer",
                    "description": "Number of commits to retrieve (default: 10)",
                    "default": 10
                }
            }
        }
    }
]

def run_reader_cmd(args: List[str]) -> str:
    cmd = [sys.executable, str(CRM_DOC_READER)] + args
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return res.stdout or res.stderr

def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    if name == "remote_list_work_items":
        org_url, project, _ = get_remote_config()
        wi_type = arguments.get("work_item_type")
        state = arguments.get("state")
        top = arguments.get("top", 15)
        user_fields = arguments.get("fields")

        try:
            top_val = int(top)
            if top_val <= 0:
                top_val = 15
        except (ValueError, TypeError):
            top_val = 15

        safe_project = escape_wiql_literal(project)
        where_clauses = [f"[System.TeamProject] = '{safe_project}'"]

        if wi_type:
            matched_type = next((t for t in ALLOWED_WORK_ITEM_TYPES if t.lower() == str(wi_type).strip().lower()), None)
            if not matched_type:
                raise ValueError(f"Invalid work_item_type: '{wi_type}'. Allowed types: {sorted(ALLOWED_WORK_ITEM_TYPES)}")
            where_clauses.append(f"[System.WorkItemType] = '{escape_wiql_literal(matched_type)}'")

        if state:
            matched_state = next((s for s in ALLOWED_STATES if s.lower() == str(state).strip().lower()), None)
            if not matched_state:
                raise ValueError(f"Invalid state: '{state}'. Allowed states: {sorted(ALLOWED_STATES)}")
            where_clauses.append(f"[System.State] = '{escape_wiql_literal(matched_state)}'")

        # Whitelist field values
        select_fields = ["System.Id", "System.Title", "System.WorkItemType", "System.State", "System.AssignedTo"]
        if user_fields:
            if isinstance(user_fields, str):
                parsed_fields = [f.strip() for f in user_fields.split(",") if f.strip()]
            elif isinstance(user_fields, list):
                parsed_fields = [str(f).strip() for f in user_fields if str(f).strip()]
            else:
                raise ValueError("fields must be a comma-separated string or list of field names.")

            invalid_fields = [f for f in parsed_fields if f not in ALLOWED_FIELDS]
            if invalid_fields:
                raise ValueError(f"Invalid field(s): {invalid_fields}. Allowed fields: {sorted(ALLOWED_FIELDS)}")
            if parsed_fields:
                select_fields = parsed_fields

        select_clause = ", ".join(f"[{f.strip('[]')}]" for f in select_fields)
        where_stmt = " AND ".join(where_clauses)
        wiql = f"SELECT {select_clause} FROM WorkItems WHERE {where_stmt} ORDER BY [System.ChangedDate] DESC"

        data = remote_api_post(f"{project}/_apis/wit/wiql", {"query": wiql}, {"api-version": "5.0", "$top": str(top_val)})
        work_items_meta = data.get("workItems", [])
        if not work_items_meta:
            return f"No work items found matching criteria in REMOTE project {project}."

        ids_str = ",".join(str(w["id"]) for w in work_items_meta[:top_val])
        fetch_fields = list(dict.fromkeys(select_fields + ["System.Id", "System.Title", "System.WorkItemType", "System.State", "System.AssignedTo", "System.CreatedDate"]))
        details = remote_api_get(f"_apis/wit/workitems", {
            "ids": ids_str,
            "fields": ",".join(fetch_fields),
            "api-version": "5.0"
        })

        results = []
        for item in details.get("value", []):
            fields = item.get("fields", {})
            assigned = fields.get("System.AssignedTo", {})
            assigned_name = assigned.get("displayName") if isinstance(assigned, dict) else (assigned or "Unassigned")
            entry = {
                "id": fields.get("System.Id"),
                "type": fields.get("System.WorkItemType"),
                "state": fields.get("System.State"),
                "title": fields.get("System.Title"),
                "assigned_to": assigned_name,
                "url": item.get("_links", {}).get("html", {}).get("href")
            }
            for rf in select_fields:
                if rf not in entry:
                    entry[rf] = fields.get(rf)
            results.append(entry)
        return json.dumps(results, indent=2, ensure_ascii=False)

    elif name == "remote_get_work_item":
        wi_id = arguments.get("work_item_id")
        try:
            wi_id_int = int(wi_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid work_item_id: {wi_id}. Must be an integer.")
        data = remote_api_get(f"_apis/wit/workitems/{wi_id_int}", {"$expand": "all", "api-version": "5.0"})
        fields = data.get("fields", {})
        cleaned = {
            "id": data.get("id"),
            "url": data.get("_links", {}).get("html", {}).get("href"),
            "type": fields.get("System.WorkItemType"),
            "title": fields.get("System.Title"),
            "state": fields.get("System.State"),
            "assigned_to": fields.get("System.AssignedTo", {}).get("displayName") if isinstance(fields.get("System.AssignedTo"), dict) else fields.get("System.AssignedTo"),
            "area_path": fields.get("System.AreaPath"),
            "iteration_path": fields.get("System.IterationPath"),
            "description": fields.get("System.Description"),
            "acceptance_criteria": fields.get("Microsoft.VSTS.Common.AcceptanceCriteria"),
            "repro_steps": fields.get("Microsoft.VSTS.TCM.ReproSteps"),
            "created_date": fields.get("System.CreatedDate"),
            "changed_date": fields.get("System.ChangedDate")
        }
        return json.dumps({k: v for k, v in cleaned.items() if v is not None}, indent=2, ensure_ascii=False)

    elif name == "remote_query_wiql":
        _, project, _ = get_remote_config()
        wiql = arguments.get("wiql", "")
        if not isinstance(wiql, str) or not re.match(r"^\s*SELECT\s+", wiql, re.IGNORECASE):
            raise ValueError("Invalid WIQL query: query must start with 'SELECT'.")
        data = remote_api_post(f"{project}/_apis/wit/wiql", {"query": wiql.strip()}, {"api-version": "5.0"})
        return json.dumps(data, indent=2, ensure_ascii=False)

    elif name == "remote_list_repositories":
        _, project, _ = get_remote_config()
        data = remote_api_get(f"{project}/_apis/git/repositories", {"api-version": "5.0"})
        repos = [{
            "id": r.get("id"),
            "name": r.get("name"),
            "default_branch": r.get("defaultBranch"),
            "remote_url": r.get("remoteUrl"),
            "web_url": r.get("webUrl")
        } for r in data.get("value", [])]
        return json.dumps(repos, indent=2, ensure_ascii=False)

    elif name == "remote_list_pull_requests":
        _, project, _ = get_remote_config()
        repo_name = arguments.get("repository", "crm-fe")
        status = arguments.get("status", "active")
        data = remote_api_get(f"{project}/_apis/git/repositories/{repo_name}/pullrequests", {
            "searchCriteria.status": status,
            "api-version": "5.0"
        })
        prs = [{
            "id": pr.get("pullRequestId"),
            "title": pr.get("title"),
            "status": pr.get("status"),
            "created_by": pr.get("createdBy", {}).get("displayName"),
            "source_branch": pr.get("sourceRefName"),
            "target_branch": pr.get("targetRefName"),
            "url": pr.get("_links", {}).get("html", {}).get("href")
        } for pr in data.get("value", [])]
        return json.dumps(prs, indent=2, ensure_ascii=False)

    elif name == "remote_search_use_cases":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)
        return run_reader_cmd([query, "-n", str(top_k)])

    elif name == "remote_get_use_case":
        uc_id = arguments.get("use_case_id", "")
        return run_reader_cmd(["--uc", uc_id])

    elif name == "remote_sync_docs":
        return run_reader_cmd(["--sync", "-t"])

    elif name == "remote_list_doc_tree":
        return run_reader_cmd(["-t"])

    elif name == "remote_git_status":
        repo_choice = arguments.get("repo", "doc")
        repo_dir = FE_REPO_PATH if repo_choice == "fe" else DOC_REPO_PATH
        if not repo_dir.exists():
            return f"Error: Repository path {repo_dir} does not exist."
        res = subprocess.run(["git", "-C", str(repo_dir), "status", "-s", "-b"], capture_output=True, text=True)
        return res.stdout or res.stderr or "Clean working tree."

    elif name == "remote_git_log":
        repo_choice = arguments.get("repo", "doc")
        max_count = arguments.get("max_count", 10)
        repo_dir = FE_REPO_PATH if repo_choice == "fe" else DOC_REPO_PATH
        if not repo_dir.exists():
            return f"Error: Repository path {repo_dir} does not exist."
        res = subprocess.run(
            ["git", "-C", str(repo_dir), "log", f"-n{max_count}", "--pretty=format:%h - %an (%ad): %s", "--date=short"],
            capture_output=True, text=True
        )
        return res.stdout or res.stderr or "No commits found."

    else:
        raise ValueError(f"Unknown tool: {name}")

def handle_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "remote-crm",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS_SCHEMA
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            output = execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": output
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "isError": True,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing {tool_name}: {str(e)}"
                        }
                    ]
                }
            }

    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        return None

def main():
    try:
        get_remote_config()
    except ValueError as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.stderr.flush()
        sys.exit(1)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"JSON-RPC parse error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
