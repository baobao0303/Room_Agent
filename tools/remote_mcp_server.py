#!/usr/bin/env python3
"""
tools/remote_mcp_server.py - High-Performance Model Context Protocol (MCP) Server for REMOTE ACME (https://remote.example.com)
Provides full stdio JSON-RPC 2.0 interface for Work Items, Repositories, Pull Requests, Use Cases, and Git.
"""

import sys
import os
import json
import base64
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DOC_REPO_PATH = Path("/home/baoltb/Desktop/crm-doc")
FE_REPO_PATH = Path("/home/baoltb/Desktop/Paseo_Project/projects/crm-fe") if Path("/home/baoltb/Desktop/Paseo_Project/projects/crm-fe").exists() else Path("/home/baoltb/Desktop/WiCRM/crm-fe")
CRM_DOC_READER = BASE_DIR / "tools/crm_doc_reader.py"

# REMOTE Configuration
REMOTE_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL", "https://remote.example.com/MainCollection").rstrip("/")
REMOTE_PROJECT = os.getenv("AZURE_DEVOPS_DEFAULT_PROJECT", "ACME")
REMOTE_PAT = os.getenv("AZURE_DEVOPS_PAT", "")

def get_auth_header() -> Dict[str, str]:
    if not REMOTE_PAT:
        return {}
    token_b64 = base64.b64encode(f":{REMOTE_PAT}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token_b64}"}

def remote_api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{REMOTE_ORG_URL}/{endpoint}"
    if params:
        query_str = urllib.parse.urlencode(params)
        url = f"{url}?{query_str}"
    headers = get_auth_header()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def remote_api_post(endpoint: str, payload: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{REMOTE_ORG_URL}/{endpoint}"
    if params:
        query_str = urllib.parse.urlencode(params)
        url = f"{url}?{query_str}"
    headers = get_auth_header()
    headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

TOOLS_SCHEMA = [
    {
        "name": "remote_list_work_items",
        "description": "List recent work items (User Stories, Bugs, Tasks, Epics) from REMOTE ACME project.",
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
                }
            }
        }
    },
    {
        "name": "remote_get_work_item",
        "description": "Retrieve full details, description, acceptance criteria, state, and fields of a REMOTE Work Item by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "work_item_id": {
                    "type": "integer",
                    "description": "REMOTE Work Item ID (e.g. 160736)"
                }
            },
            "required": ["work_item_id"]
        }
    },
    {
        "name": "remote_query_wiql",
        "description": "Execute a custom WIQL (Work Item Query Language) query on REMOTE ACME.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wiql": {
                    "type": "string",
                    "description": "WIQL query string (e.g. 'SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = @project AND [System.WorkItemType] = \\'Bug\\' ORDER BY [System.ChangedDate] DESC')"
                }
            },
            "required": ["wiql"]
        }
    },
    {
        "name": "remote_list_repositories",
        "description": "List all Git repositories under REMOTE project ACME (e.g. crm-crm, crm-fe, helm-charts).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "remote_list_pull_requests",
        "description": "List active or completed Pull Requests for a REMOTE repository.",
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
        "description": "Semantic search across all ACME CRM Use Cases (UC1.01 to UC4.09), User Stories, and Acceptance Criteria from REMOTE docs/base.",
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
        "description": "Synchronize and pull latest documentation changes from REMOTE remote repository (branch docs/base).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "remote_list_doc_tree",
        "description": "Get hierarchical directory tree of all ACME CRM documentation on REMOTE.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "remote_git_status",
        "description": "Get git branch and working tree status for REMOTE repositories (crm-doc or crm-fe).",
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
        "description": "View recent git commit log from REMOTE repository.",
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
        wi_type = arguments.get("work_item_type")
        state = arguments.get("state")
        top = arguments.get("top", 15)

        where_clauses = ["[System.TeamProject] = @project"]
        if wi_type:
            where_clauses.append(f"[System.WorkItemType] = '{wi_type}'")
        if state:
            where_clauses.append(f"[System.State] = '{state}'")

        where_stmt = " AND ".join(where_clauses)
        wiql = f"SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], [System.AssignedTo] FROM WorkItems WHERE {where_stmt} ORDER BY [System.ChangedDate] DESC"
        
        data = remote_api_post(f"{REMOTE_PROJECT}/_apis/wit/wiql", {"query": wiql}, {"api-version": "5.0", "$top": str(top)})
        work_items_meta = data.get("workItems", [])
        if not work_items_meta:
            return f"No work items found matching criteria in REMOTE project {REMOTE_PROJECT}."

        ids_str = ",".join(str(w["id"]) for w in work_items_meta[:top])
        details = remote_api_get(f"_apis/wit/workitems", {
            "ids": ids_str,
            "fields": "System.Id,System.Title,System.WorkItemType,System.State,System.AssignedTo,System.CreatedDate",
            "api-version": "5.0"
        })

        results = []
        for item in details.get("value", []):
            fields = item.get("fields", {})
            assigned = fields.get("System.AssignedTo", {})
            assigned_name = assigned.get("displayName") if isinstance(assigned, dict) else (assigned or "Unassigned")
            results.append({
                "id": fields.get("System.Id"),
                "type": fields.get("System.WorkItemType"),
                "state": fields.get("System.State"),
                "title": fields.get("System.Title"),
                "assigned_to": assigned_name,
                "url": item.get("_links", {}).get("html", {}).get("href")
            })
        return json.dumps(results, indent=2, ensure_ascii=False)

    elif name == "remote_get_work_item":
        wi_id = arguments.get("work_item_id")
        data = remote_api_get(f"_apis/wit/workitems/{wi_id}", {"$expand": "all", "api-version": "5.0"})
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
        wiql = arguments.get("wiql", "")
        data = remote_api_post(f"{REMOTE_PROJECT}/_apis/wit/wiql", {"query": wiql}, {"api-version": "5.0"})
        return json.dumps(data, indent=2, ensure_ascii=False)

    elif name == "remote_list_repositories":
        data = remote_api_get(f"{REMOTE_PROJECT}/_apis/git/repositories", {"api-version": "5.0"})
        repos = [{
            "id": r.get("id"),
            "name": r.get("name"),
            "default_branch": r.get("defaultBranch"),
            "remote_url": r.get("remoteUrl"),
            "web_url": r.get("webUrl")
        } for r in data.get("value", [])]
        return json.dumps(repos, indent=2, ensure_ascii=False)

    elif name == "remote_list_pull_requests":
        repo_name = arguments.get("repository", "crm-fe")
        status = arguments.get("status", "active")
        data = remote_api_get(f"{REMOTE_PROJECT}/_apis/git/repositories/{repo_name}/pullrequests", {
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
