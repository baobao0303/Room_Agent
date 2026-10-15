#!/usr/bin/env python3
"""Harness Dashboard Realtime Server, SLPC Agent Command Center & QC Automation Workbench.

Usage:
  python3 scripts/harness_dashboard.py             # Sinh /tmp/harness_dashboard.html
  python3 scripts/harness_dashboard.py --serve     # Chạy foreground HTTP server trên cổng 8765
"""
import argparse
import http.server
import json
import mimetypes
import os
import re
import shlex
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def _load_env_files():
    for env_path in (BASE_DIR / ".env", BASE_DIR / "harness-ui" / ".env", BASE_DIR / ".env.example"):
        if not env_path.is_file():
            continue
        try:
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if k and k not in os.environ:
                    os.environ[k] = v
        except Exception:
            pass


_load_env_files()

from tools.floci_client import FlociHarnessDB
from tools.harness_manager import HarnessManager
from tools import qc_test_generator as qc_gen
from tools import agent_progress
from tools import harness_doctor

DIST_DIR = BASE_DIR / "harness-ui" / "dist"
INDEX_FILE = DIST_DIR / "index.html"

MIME_OVERRIDES = {
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
    ".wasm": "application/wasm",
}


def _get_content_type(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    guessed, _ = mimetypes.guess_type(str(file_path))
    if guessed:
        if guessed.startswith("text/") or guessed in ("application/javascript", "text/javascript", "application/json"):
            return f"{guessed}; charset=utf-8"
        return guessed
    return "application/octet-stream"

FIELDS = [
    "id", "type", "title", "description", "acceptance_criteria", "state",
    "priority", "assigned_to", "assigned_to_profile", "created_by_profile",
    "parent_item_id", "iteration_path", "source", "created_at", "updated_at"
]

LOCAL_CACHE_FILE = Path("/tmp/harness_work_items_cache.json")
LOCAL_DB_FILE = BASE_DIR / ".harness_local_db.json"

try:
    import signal
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
except Exception:
    pass

_CACHE = {
    "data": [],
    "json_str": "[]",
    "last_fetch": 0.0,
    "floci_backoff_until": 0.0,
    "local_db_mtime": 0.0,
    "cache_file_mtime": 0.0,
}
_LOCK = threading.Lock()

# Background Job Manager for Build, Automation Tests & Agent Dispatches
_JOBS_LOCK = threading.Lock()
_JOBS = []  # List of dicts: id, kind, title, command, cwd, status, exit_code, started_at, elapsed, output


def _synthesize_testcase_spec(row: dict) -> dict:
    title = str(row.get("title") or "").strip()
    if not title:
        return row
    wtype = str(row.get("type") or "Task").strip()
    item_id = row.get("id") or "--"

    # Extract [Module] prefix if present
    module_name = "Hệ thống WiCX CRM"
    rest_title = title
    if title.startswith("[") and "]" in title:
        close_idx = title.find("]")
        module_name = title[1:close_idx].strip() or module_name
        rest_title = title[close_idx + 1:].strip().lstrip("-:").strip()

    # Split "Kiểm tra <expected> khi <trigger>" if present
    lower_rest = rest_title.lower()
    expected_part = rest_title
    when_part = f"thực hiện thao tác kiểm thử trên phân hệ [{module_name}]"
    if " khi " in lower_rest:
        split_pos = lower_rest.rfind(" khi ")
        expected_part = rest_title[:split_pos].strip()
        when_part = rest_title[split_pos + 5:].strip()
        if expected_part.lower().startswith("kiểm tra "):
            expected_part = expected_part[9:].strip()
    elif lower_rest.startswith("kiểm tra "):
        expected_part = rest_title[9:].strip()

    if not str(row.get("description") or "").strip():
        if wtype.lower() in ("testcase", "test case"):
            row["description"] = (
                f"• Mã Test Case: TC-{item_id} | Phân hệ: {module_name}\n"
                f"• Kỹ thuật thiết kế (ISTQB): Phân vùng tương đương (EP) & Phân tích giá trị biên (BVA)\n"
                f"• Điều kiện tiên quyết (Preconditions):\n"
                f"  1. Người dùng đã đăng nhập hợp lệ và có quyền truy cập phân hệ [{module_name}].\n"
                f"  2. Dữ liệu kiểm thử và kết nối API/Backend ở trạng thái sẵn sàng.\n"
                f"• Các bước thực hiện (Test Steps):\n"
                f"  Bước 1: Truy cập màn hình chức năng [{module_name}].\n"
                f"  Bước 2: Thực hiện thao tác: {when_part}.\n"
                f"  Bước 3: Kiểm tra phản hồi giao diện (UI/UX), trạng thái dữ liệu và thông báo hệ thống.\n"
                f"• Kết quả mong đợi (Expected Result):\n"
                f"  - Đảm bảo hệ thống {expected_part}."
            )
        else:
            row["description"] = (
                f"• Phân hệ: {module_name} | Loại: {wtype} #{item_id}\n"
                f"• Mục tiêu thực thi: {rest_title}\n"
                f"• Phạm vi kiểm soát: Tuân thủ kiến trúc SLPC Harness, đảm bảo xử lý đầy đủ luồng chính và các trường hợp biên."
            )

    if not str(row.get("acceptance_criteria") or "").strip():
        row["acceptance_criteria"] = (
            f"Given: Người dùng đã đăng nhập và đang ở màn hình [{module_name}] với dữ liệu hợp lệ\n"
            f"When: Người dùng {when_part}\n"
            f"Then: Hệ thống phải {expected_part}\n"
            f"And: Giao diện hiển thị đúng chuẩn UI/UX, dữ liệu đồng bộ chính xác và không phát sinh lỗi console/API"
        )
    return row


def _infer_slpc_profile(row: dict) -> dict:
    raw_prof = str(row.get("assigned_to_profile") or "").strip()
    if not raw_prof:
        wtype = (row.get("type") or "").strip().lower()
        if wtype == "epic":
            row["assigned_to_profile"] = "supervisor"
        elif wtype in ("feature", "user story", "story"):
            row["assigned_to_profile"] = "lead"
        elif wtype in ("testcase", "test case", "bug"):
            row["assigned_to_profile"] = "qc"
        else:
            row["assigned_to_profile"] = "peer"
    else:
        p_low = raw_prof.lower()
        if p_low.startswith("peer"):
            if p_low != "peer" and not row.get("assigned_to"):
                row["assigned_to"] = raw_prof
            row["assigned_to_profile"] = "peer"
        elif p_low.startswith("lead"):
            if p_low != "lead" and not row.get("assigned_to"):
                row["assigned_to"] = raw_prof
            row["assigned_to_profile"] = "lead"
        elif p_low.startswith("sup"):
            row["assigned_to_profile"] = "supervisor"
        elif p_low.startswith("qc") or p_low.startswith("qa"):
            row["assigned_to_profile"] = "qc"
        else:
            row["assigned_to_profile"] = p_low

    raw_src = str(row.get("source") or "local").strip().lower()
    if raw_src in ("bot", "local", "floci", ""):
        row["source"] = "local"
    return _synthesize_testcase_spec(row)


def _bootstrap_local_cache():
    """Preserve existing work items from /tmp/harness_dashboard.html if local cache file does not exist yet."""
    if LOCAL_CACHE_FILE.exists():
        try:
            rows = json.loads(LOCAL_CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(rows, list) and rows:
                rows = [_infer_slpc_profile(r) for r in rows]
                _CACHE["data"] = rows
                _CACHE["json_str"] = json.dumps(rows, ensure_ascii=False)
                return
        except Exception:
            pass

    existing_html = Path("/tmp/harness_dashboard.html")
    if existing_html.exists():
        try:
            text = existing_html.read_text(encoding="utf-8", errors="replace")
            for marker in ("let D = ", "let D="):
                idx = text.find(marker)
                if idx != -1:
                    start = idx + len(marker)
                    end = text.find(";\n", start)
                    if end != -1:
                        raw_json = text[start:end].strip().replace("<\\/", "</")
                        rows = json.loads(raw_json)
                        if isinstance(rows, list) and rows:
                            rows = [_infer_slpc_profile(r) for r in rows]
                            LOCAL_CACHE_FILE.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
                            _CACHE["data"] = rows
                            _CACHE["json_str"] = json.dumps(rows, ensure_ascii=False)
                            return
        except Exception:
            pass


_bootstrap_local_cache()


def save_local_cache(rows):
    rows = [_infer_slpc_profile(r) for r in rows]
    _CACHE["data"] = rows
    _CACHE["json_str"] = json.dumps(rows, ensure_ascii=False)
    _CACHE["last_fetch"] = time.time()
    try:
        LOCAL_CACHE_FILE.write_text(_CACHE["json_str"], encoding="utf-8")
        _CACHE["cache_file_mtime"] = LOCAL_CACHE_FILE.stat().st_mtime
    except Exception:
        pass
    try:
        if LOCAL_DB_FILE.is_file():
            _CACHE["local_db_mtime"] = LOCAL_DB_FILE.stat().st_mtime
    except Exception:
        pass


def _merge_local_db_if_modified():
    """Instantly reflect any CLI harness_manager.py write to .harness_local_db.json in <1ms."""
    try:
        if not LOCAL_DB_FILE.is_file():
            return
        mtime = LOCAL_DB_FILE.stat().st_mtime
        if mtime <= _CACHE.get("local_db_mtime", 0.0):
            return
        with _LOCK:
            if mtime <= _CACHE.get("local_db_mtime", 0.0):
                return
            store = json.loads(LOCAL_DB_FILE.read_text(encoding="utf-8"))
            local_items = store.get("work_items", {}) if isinstance(store, dict) else {}
            if not local_items:
                _CACHE["local_db_mtime"] = mtime
                return
            by_id = {str(r.get("id")): dict(r) for r in (_CACHE["data"] or []) if r.get("id") is not None}
            changed = False
            for sid, loc in local_items.items():
                if not isinstance(loc, dict) or loc.get("id") is None:
                    continue
                cur = by_id.get(str(sid))
                if cur is None or str(loc.get("updated_at") or "") >= str(cur.get("updated_at") or ""):
                    norm = _infer_slpc_profile({k: loc.get(k) for k in FIELDS})
                    if cur != norm:
                        by_id[str(sid)] = norm
                        changed = True
            if changed:
                merged = sorted(by_id.values(), key=lambda x: int(x.get("id") or 0), reverse=True)
                _CACHE["data"] = merged
                _CACHE["json_str"] = json.dumps(merged, ensure_ascii=False)
            _CACHE["local_db_mtime"] = mtime
    except Exception:
        pass


_FETCH_LOCK = threading.Lock()


def sync_from_floci():
    """Fetch work items from Floci DynamoDB without blocking HTTP readers."""
    if not _FETCH_LOCK.acquire(blocking=False):
        return _CACHE["data"], _CACHE["json_str"]
    try:
        items = FlociHarnessDB().list_work_items()
        rows = [_infer_slpc_profile({k: it.get(k) for k in FIELDS}) for it in items]
        with _LOCK:
            save_local_cache(rows)
            _CACHE["floci_backoff_until"] = 0.0
        print(f"[Dashboard Server] Synced {len(rows)} items from Floci DynamoDB", flush=True)
    except Exception as e:
        print(f"[Dashboard Server] Floci sync warning: {e}", file=sys.stderr, flush=True)
        with _LOCK:
            _CACHE["floci_backoff_until"] = time.time() + 5.0
            _CACHE["last_fetch"] = time.time()
            if not _CACHE["data"]:
                _bootstrap_local_cache()
    finally:
        _FETCH_LOCK.release()
    return _CACHE["data"], _CACHE["json_str"]


def get_cached_rows(force=False, wait_if_empty=False):
    _merge_local_db_if_modified()
    now = time.time()
    if wait_if_empty and not _CACHE["data"]:
        return sync_from_floci()
    if force or (not _CACHE["data"] and now >= _CACHE["floci_backoff_until"]) or (
        (now - _CACHE["last_fetch"] > 2.5) and (now >= _CACHE["floci_backoff_until"])
    ):
        threading.Thread(target=sync_from_floci, daemon=True).start()
    return _CACHE["data"], _CACHE["json_str"]


def start_background_job(kind: str, title: str, command: str, cwd: str = None, item_id: int = None, auto_verify_item: bool = False) -> dict:
    job_id = "job-" + uuid.uuid4().hex[:8]
    work_dir = cwd if (cwd and os.path.isdir(cwd)) else str(BASE_DIR)
    job = {
        "id": job_id,
        "kind": kind,  # "test" | "build" | "agent" | "qc-gen"
        "title": title,
        "command": command,
        "cwd": work_dir,
        "item_id": item_id,
        "status": "running",
        "exit_code": None,
        "started_at": datetime.now().strftime("%H:%M:%S"),
        "elapsed": 0.0,
        "output": f"$ cd {work_dir}\n$ {command}\n\n"
    }
    with _JOBS_LOCK:
        _JOBS.insert(0, job)
        del _JOBS[30:]  # Keep latest 30 jobs

    def _runner():
        t0 = time.time()
        try:
            cmd = shlex.split(command) if isinstance(command, str) else list(command)
            proc = subprocess.Popen(
                cmd,
                cwd=work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in iter(proc.stdout.readline, ""):
                with _JOBS_LOCK:
                    job["output"] = (job["output"] + line)[-24000:]
                    job["elapsed"] = round(time.time() - t0, 1)
            proc.stdout.close()
            rc = proc.wait(timeout=300)
            with _JOBS_LOCK:
                job["exit_code"] = rc
                job["status"] = "passed" if rc == 0 else "failed"
                job["elapsed"] = round(time.time() - t0, 1)

            # Optional: If linked to a Harness item and auto_verify_item is enabled, update item/story
            if auto_verify_item and item_id:
                try:
                    mgr = HarnessManager()
                    item = mgr.get_work_item(int(item_id))
                    if item and rc == 0 and item.get("state") in ("Active", "Resolved"):
                        if item.get("state") == "Active":
                            mgr.update_state(int(item_id), "Resolved", assigned_to_profile="qc")
                    get_cached_rows(force=True)
                except Exception:
                    pass
        except Exception as e:
            with _JOBS_LOCK:
                job["output"] += f"\n[Execution Error]: {e}\n"
                job["exit_code"] = -1
                job["status"] = "failed"
                job["elapsed"] = round(time.time() - t0, 1)

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    return job


def get_slpc_profiles():
    config_path = Path.home() / ".paseo" / "config.json"
    profiles = []
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            profiles = data.get("daemon", {}).get("agentProfiles", [])
        except Exception:
            pass

    # Ensure the 4 core SLPC profiles are always represented
    core_map = {
        "Supervisor": {"role": "Scope & Intent Guard", "badge": "S", "color": "#8b5cf6"},
        "Lead": {"role": "Technical Architect & PM", "badge": "L", "color": "#0ea5e9"},
        "Peer": {"role": "Code Executor (FE/BE Dev)", "badge": "P", "color": "#10b981"},
        "QC": {"role": "Test Architect & Quality Gate", "badge": "C", "color": "#f59e0b"},
    }
    rows, _ = get_cached_rows()
    result = []
    seen = set()

    for p in profiles:
        name = p.get("name", "")
        seen.add(name.lower())
        meta = core_map.get(name, {"role": "Specialized Agent Profile", "badge": name[:1].upper(), "color": "#64748b"})
        assigned_items = [
            r for r in rows
            if (r.get("assigned_to_profile") or "").lower() == name.lower()
            or (r.get("assigned_to") or "").lower() == name.lower()
        ]
        result.append({
            "id": p.get("id", name),
            "name": name,
            "role": meta["role"],
            "badge": meta["badge"],
            "color": meta["color"],
            "provider": p.get("provider", "router9"),
            "model": p.get("model") or "",
            "thinking": p.get("thinkingOptionId", "high"),
            "notes": p.get("notes", ""),
            "counts": {
                "total": len(assigned_items),
                "new": sum(1 for r in assigned_items if r.get("state") == "New"),
                "active": sum(1 for r in assigned_items if r.get("state") == "Active"),
                "resolved": sum(1 for r in assigned_items if r.get("state") == "Resolved"),
                "closed": sum(1 for r in assigned_items if r.get("state") == "Closed"),
            }
        })

    for cname, meta in core_map.items():
        if cname.lower() not in seen:
            result.append({
                "id": f"agent_{cname.lower()}",
                "name": cname,
                "role": meta["role"],
                "badge": meta["badge"],
                "color": meta["color"],
                "provider": "router9",
                "model": "",
                "thinking": "high",
                "notes": "",
                "counts": {"total": 0, "new": 0, "active": 0, "resolved": 0, "closed": 0}
            })

    # Put Supervisor, Lead, Peer, QC first
    order = {"supervisor": 0, "lead": 1, "peer": 2, "qc": 3}
    result.sort(key=lambda x: (order.get(x["name"].lower(), 99), x["name"]))
    return result


def scan_workspace_Targets():
    """Return curated list of source files, specs, and preset automation commands for quick selection."""
    sources = []
    specs = []

    search_roots = [
        BASE_DIR / "projects/wicx-crm-fe/libs",
        BASE_DIR / "projects/wicx-crm-fe/apps",
        BASE_DIR / "game/src",
        BASE_DIR / "tools",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", "dist", ".git", "__pycache__", ".nx")]
            for fn in filenames:
                if fn.endswith((".ts", ".py")) and not fn.endswith((".spec.ts", ".test.ts", ".d.ts", "__init__.py")):
                    full_p = Path(dirpath) / fn
                    rel_p = str(full_p.relative_to(BASE_DIR))
                    sources.append(rel_p)
                    if len(sources) >= 80:
                        break
            if len(sources) >= 80:
                break

    spec_roots = [
        BASE_DIR / "docs/spec",
        BASE_DIR / "projects/wicx-crm-fe/docs",
        BASE_DIR / "projects/wicx-crm-fe/libs",
        BASE_DIR / "private/docs/spec",
    ]
    for sroot in spec_roots:
        if not sroot.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(sroot):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git")]
            for fn in filenames:
                if fn.endswith(".md") and "agent" not in fn.lower():
                    full_p = Path(dirpath) / fn
                    specs.append(str(full_p.relative_to(BASE_DIR)))

    presets = [
        {
            "id": "self-test-harness",
            "category": "Test",
            "title": "Harness & Floci DynamoDB Self-Test",
            "command": "python3 tools/test_harness.py",
            "cwd": str(BASE_DIR)
        },
        {
            "id": "qc-gen-validator",
            "category": "QC Unit Gen",
            "title": "Gen 5-Stage Unit Tests: validator.helper.ts",
            "command": "python3 tools/qc_test_generator.py --source projects/wicx-crm-fe/libs/wicx-core/src/utils/helps/validator.helper.ts --spec projects/wicx-crm-fe/libs/wicx-core/spec.md --out-spec /tmp/validator.helper.spec.ts",
            "cwd": str(BASE_DIR)
        },
        {
            "id": "wicx-core-test",
            "category": "Unit Test",
            "title": "Run Nx Unit Tests: wicx-core",
            "command": "npx nx test wicx-core",
            "cwd": str(BASE_DIR / "projects/wicx-crm-fe")
        },
        {
            "id": "wicx-build-shell",
            "category": "Build",
            "title": "Build Angular Host: app-shell (Rsbuild)",
            "command": "npx nx build app-shell",
            "cwd": str(BASE_DIR / "projects/wicx-crm-fe")
        },
        {
            "id": "game-vitest",
            "category": "Unit Test",
            "title": "Run 3D Game Vitest Suite",
            "command": "npx vitest run",
            "cwd": str(BASE_DIR / "game")
        },
        {
            "id": "game-build",
            "category": "Build",
            "title": "Build 3D Game Production Bundle",
            "command": "npm run build",
            "cwd": str(BASE_DIR / "game")
        },
        {
            "id": "harness-stats",
            "category": "Ops",
            "title": "Harness Matrix & Backlog Statistics",
            "command": "./scripts/harness query stats && ./scripts/harness query matrix",
            "cwd": str(BASE_DIR)
        },
        {
            "id": "harness-doctor",
            "category": "Doctor",
            "title": "🩺 Harness Doctor (Check & Auto-Heal)",
            "command": "./scripts/harness doctor --fix",
            "cwd": str(BASE_DIR)
        }
    ]
    return {"sources": sorted(set(sources)), "specs": sorted(set(specs)), "presets": presets}


_NODES_LOCK = threading.Lock()
_CONNECTED_NODES = [
    {
        "id": "local-8765",
        "name": "Local Master (:8765)",
        "url": "http://127.0.0.1:8765",
        "kind": "harness-node",
        "workspace": str(BASE_DIR),
        "online": True,
        "status": "online",
    },
    {
        "id": "tailscale-master",
        "name": "Tailscale Host (100.92.98.99:8765)",
        "url": os.environ.get("PUBLIC_API_BASE_URL", "http://100.92.98.99:8765"),
        "kind": "harness-node",
        "workspace": str(BASE_DIR),
        "online": True,
        "status": "online",
    },
    {
        "id": "remote-deploy",
        "name": "Deploy Node (100.124.36.46:4321)",
        "url": os.environ.get("PUBLIC_DEPLOY_URL", "http://100.124.36.46:4321"),
        "kind": "deploy-ui",
        "workspace": "/app",
        "online": True,
        "status": "online",
    },
    {
        "id": "paseo-daemon",
        "name": "Paseo Daemon (:6767)",
        "url": os.environ.get("PUBLIC_PASEO_DAEMON_URL", "http://127.0.0.1:6767"),
        "kind": "paseo-daemon",
        "workspace": str(BASE_DIR),
        "online": False,
        "status": "offline",
    },
]


def _normalize_node_url(raw_url: str) -> str:
    u = (raw_url or "").strip()
    if not u:
        return "http://127.0.0.1:8765"
    if u.startswith("paseo://"):
        u = "http://" + u[len("paseo://"):]
    if not u.startswith(("http://", "https://")):
        u = "http://" + u
    parsed = urllib.parse.urlparse(u)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base.rstrip("/")


def probe_and_register_node(raw_url: str, custom_name: str = "") -> dict:
    base_url = _normalize_node_url(raw_url)
    parsed = urllib.parse.urlparse(base_url)
    host_label = parsed.netloc or base_url
    kind = "paseo-daemon" if ":6767" in host_label else "harness-node"
    online = False
    workspace = str(BASE_DIR)
    model_name = os.environ.get("HARNESS_MODEL", "gemini-3.7-medium")
    latency_ms = 0

    t0 = time.time()
    for probe_path in ("/api/env", "/api/work-items", "/health", "/"):
        try:
            req = urllib.request.Request(base_url + probe_path, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                latency_ms = int((time.time() - t0) * 1000)
                if resp.status < 500:
                    online = True
                    if probe_path == "/api/env":
                        data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        model_name = data.get("HARNESS_MODEL", model_name)
                        workspace = data.get("WORKSPACE_ROOT", workspace)
                    break
        except Exception:
            continue

    node_entry = {
        "id": "node-" + re.sub(r"[^a-zA-Z0-9]+", "-", host_label).strip("-").lower(),
        "name": custom_name.strip() or f"Node ({host_label})",
        "url": base_url,
        "kind": kind,
        "workspace": workspace,
        "model": model_name,
        "online": online,
        "status": "online" if online else "offline",
        "latency_ms": latency_ms,
        "checked_at": datetime.now().strftime("%H:%M:%S"),
    }

    with _NODES_LOCK:
        replaced = False
        for i, existing in enumerate(_CONNECTED_NODES):
            if existing["url"].rstrip("/") == base_url:
                _CONNECTED_NODES[i] = {**existing, **node_entry}
                replaced = True
                break
        if not replaced:
            _CONNECTED_NODES.insert(0, node_entry)

    return node_entry


def _match_workspace_files_by_keywords(text: str, all_sources: list[str], max_files: int = 3) -> list[str]:
    text_low = (text or "").lower()
    scored = []
    # Keyword mappings from Vietnamese module names to repo paths
    module_hints = {
        "tài khoản": ["auth", "account", "user", "profile", "validator"],
        "cá nhân": ["profile", "user", "account", "validator"],
        "nhân viên": ["employee", "staff", "user", "member", "department"],
        "kênh kết nối": ["channel", "facebook", "social", "integration", "connect"],
        "facebook": ["facebook", "channel", "social", "webhook"],
        "email": ["validator", "email", "form", "helper"],
        "khóa": ["lock", "status", "employee", "auth", "permission"],
        "vai trò": ["role", "permission", "guard", "auth"],
        "đăng nhập": ["login", "auth", "session", "token"],
        "game": ["game", "player", "physics", "scene"],
        "harness": ["harness", "qc", "floci", "agent"],
    }
    extra_tokens = set(re.findall(r"[a-zA-Z0-9_.-]{3,}", text_low))
    for vn_key, en_list in module_hints.items():
        if vn_key in text_low:
            extra_tokens.update(en_list)

    for src in all_sources:
        src_low = src.lower()
        stem_low = Path(src).stem.lower()
        score = 0
        if src_low in text_low or Path(src).name.lower() in text_low:
            score += 50
        for tok in extra_tokens:
            if len(tok) >= 3 and tok in stem_low:
                score += 10
            elif len(tok) >= 4 and tok in src_low:
                score += 4
        if score > 0:
            scored.append((score, src))

    scored.sort(key=lambda x: (-x[0], x[1]))
    matched = [s for _, s in scored[:max_files]]
    if not matched and all_sources:
        # Default to validator.helper.ts or first available source file
        for s in all_sources:
            if "validator.helper.ts" in s:
                return [s]
        return [all_sources[0]]
    return matched


def resolve_link_and_generate_tests(body: dict) -> dict:
    """
    Smart resolver for developer links (GitHub PR/Commit/Blob, TFS PR/WorkItem/File path,
    Paseo Daemon/Workspace link, Work Item #ID, or developer name).
    Automatically discovers target source files, runs the 5-stage ISTQB Test Generator,
    writes the .spec.ts files, and optionally runs the test suite.
    """
    import urllib.request
    raw_link = (body.get("link") or "").strip()
    target_node = (body.get("target_node") or "").strip()
    write_alongside = bool(body.get("write_alongside", True))
    sync_harness = bool(body.get("sync_harness", True))
    run_test = bool(body.get("run_test", True))

    if not raw_link:
        raise ValueError("Vui lòng dán link (PR / Commit / Work Item / File URL / Mã #ID)!")

    # If target_node is a remote machine (not local 127.0.0.1 / 100.92.98.99), try forwarding to that node first
    if target_node:
        norm_node = _normalize_node_url(target_node)
        local_Self = {"http://127.0.0.1:8765", "http://localhost:8765", "http://100.92.98.99:8765"}
        if norm_node not in local_Self and not body.get("_forwarded"):
            try:
                fwd_payload = dict(body)
                fwd_payload["_forwarded"] = True
                req = urllib.request.Request(
                    norm_node + "/api/automation/resolve-link",
                    data=json.dumps(fwd_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status == 200:
                        remote_res = json.loads(resp.read().decode("utf-8", errors="replace"))
                        remote_res["executed_on_node"] = norm_node
                        return remote_res
            except Exception:
                # Fall back to local execution with remote context noted
                pass

    scan_data = scan_workspace_Targets()
    all_sources = scan_data.get("sources", [])

    discovered_sources = []
    spec_context_parts = [f"# Source Link: {raw_link}"]
    linked_task_id = body.get("task_id")
    link_kind = "auto-detected"

    # 1. Check if link contains a file path query (?path=/...) e.g. TFS Git link
    parsed_url = urllib.parse.urlparse(raw_link)
    qs = urllib.parse.parse_qs(parsed_url.query)
    if "path" in qs and qs["path"]:
        link_kind = "tfs-git-path"
        rel_cand = qs["path"][0].lstrip("/")
        for s in all_sources:
            if s.endswith(rel_cand) or Path(s).name == Path(rel_cand).name:
                discovered_sources.append(s)

    # 2. Check if GitHub Blob URL: github.com/<owner>/<repo>/blob/<branch>/<path>
    gh_blob = re.search(r"github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", raw_link)
    if gh_blob:
        link_kind = "github-blob"
        owner, repo, branch, file_path = gh_blob.groups()
        file_path = file_path.split("?")[0].split("#")[0]
        local_cand = BASE_DIR / file_path
        if local_cand.exists() and local_cand.is_file():
            discovered_sources.append(file_path)
        else:
            for s in all_sources:
                if s.endswith(file_path) or Path(s).name == Path(file_path).name:
                    discovered_sources.append(s)
                    break
            if not discovered_sources:
                # Download raw file from GitHub into /tmp/remote_sources/
                raw_gh_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                try:
                    tmp_dir = Path("/tmp/paseo_remote_sources")
                    tmp_dir.mkdir(parents=True, exist_ok=True)
                    dl_file = tmp_dir / Path(file_path).name
                    req = urllib.request.Request(raw_gh_url, headers={"User-Agent": "Paseo-Harness-QC"})
                    with urllib.request.urlopen(req, timeout=6) as r:
                        dl_file.write_bytes(r.read())
                    discovered_sources.append(str(dl_file))
                except Exception:
                    pass

    # 3. Check if GitHub PR URL: github.com/<owner>/<repo>/pull/<num>
    gh_pr = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", raw_link)
    if gh_pr:
        link_kind = "github-pr"
        owner, repo, pr_num = gh_pr.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Paseo-Harness-QC", "Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=6) as r:
                files_data = json.loads(r.read().decode("utf-8", errors="ignore"))
                for fobj in files_data:
                    fn = fobj.get("filename", "")
                    if fn.endswith((".ts", ".py")) and not fn.endswith((".spec.ts", ".test.ts", ".d.ts")):
                        if (BASE_DIR / fn).is_file():
                            discovered_sources.append(fn)
        except Exception:
            pass

    # 4. Check if GitHub Commit URL or git commit SHA
    gh_commit = re.search(r"github\.com/([^/]+)/([^/]+)/commit/([0-9a-fA-F]{7,40})", raw_link)
    if gh_commit or re.fullmatch(r"[0-9a-fA-F]{7,40}", raw_link):
        link_kind = "git-commit"
        sha = gh_commit.group(3) if gh_commit else raw_link
        try:
            out = subprocess.check_output(["git", "show", "--name-only", "--pretty=format:", sha], cwd=str(BASE_DIR), text=True, timeout=5)
            for line in out.splitlines():
                line = line.strip()
                if line.endswith((".ts", ".py")) and not line.endswith((".spec.ts", ".test.ts", ".d.ts")):
                    if (BASE_DIR / line).is_file():
                        discovered_sources.append(line)
        except Exception:
            pass

    # 5. Check if Work Item URL or #ID (e.g. _workitems/edit/160873, #160873, 160873)
    wi_match = re.search(r"(?:workitems(?:/edit)?/|#|^)(\d{4,7})(?:\b|$)", raw_link, re.IGNORECASE)
    if wi_match:
        wid = int(wi_match.group(1))
        linked_task_id = wid
        link_kind = f"work-item-#{wid}"
        rows, _ = get_cached_rows()
        found_wi = next((r for r in rows if int(r.get("id") or 0) == wid), None)
        if not found_wi:
            try:
                found_wi = HarnessManager().get_work_item(wid)
            except Exception:
                found_wi = None
        if found_wi:
            wi_text = f"{found_wi.get('title', '')}\n{found_wi.get('description', '')}\n{found_wi.get('acceptance_criteria', '')}"
            spec_context_parts.append(f"# Work Item #{wid}: {found_wi.get('title', '')}")
            spec_context_parts.append(str(found_wi.get("description") or ""))
            spec_context_parts.append("## Acceptance Criteria\n" + str(found_wi.get("acceptance_criteria") or ""))
            if not discovered_sources:
                discovered_sources.extend(_match_workspace_files_by_keywords(wi_text, all_sources, max_files=2))

    # 6. Check if direct relative path or filename in workspace
    if not discovered_sources:
        clean_cand = raw_link.strip().lstrip("/")
        if (BASE_DIR / clean_cand).is_file():
            link_kind = "workspace-file"
            discovered_sources.append(clean_cand)
        else:
            # Check if raw_link matches an assignee / developer name in Work Items
            rows, _ = get_cached_rows()
            dev_items = [
                r for r in rows
                if raw_link.lower() in str(r.get("assigned_to") or "").lower()
                or raw_link.lower() in str(r.get("title") or "").lower()
            ]
            if dev_items:
                link_kind = f"developer-backlog ({len(dev_items)} items)"
                top_item = dev_items[0]
                if not linked_task_id:
                    linked_task_id = int(top_item.get("id") or 0) or None
                combined_text = "\n".join(
                    f"#{it.get('id')} {it.get('title')} {it.get('description')} {it.get('acceptance_criteria')}"
                    for it in dev_items[:5]
                )
                spec_context_parts.append(combined_text)
                discovered_sources.extend(_match_workspace_files_by_keywords(combined_text, all_sources, max_files=2))
            else:
                discovered_sources.extend(_match_workspace_files_by_keywords(raw_link, all_sources, max_files=2))

    # Deduplicate discovered sources
    unique_sources = []
    for s in discovered_sources:
        if s not in unique_sources:
            unique_sources.append(s)

    if not unique_sources:
        raise ValueError(f"Không tìm thấy file nguồn phù hợp từ link: {raw_link}")

    spec_text = "\n\n".join(p for p in spec_context_parts if p)
    generated_files = []
    total_cases = 0
    combined_spec_code = []
    last_cov_report = {}
    total_synced = 0

    for src_rel in unique_sources:
        src_path = Path(src_rel) if os.path.isabs(src_rel) else (BASE_DIR / src_rel)
        if not src_path.exists():
            continue

        code_ctx = qc_gen.analyze_source_file(src_path)
        analysis = qc_gen.parse_spec_content(spec_text, module_hint=code_ctx.get("module_name", src_path.stem))
        tp_set = qc_gen.generate_test_points(analysis, code_ctx)
        design_plan = qc_gen.build_test_design_plan(tp_set["test_points"])
        test_cases = qc_gen.generate_test_cases(analysis, tp_set, design_plan, code_ctx)
        cov_report = qc_gen.build_coverage_report(analysis, test_cases, tp_set, design_plan, code_ctx)
        last_cov_report = cov_report
        total_cases += int(cov_report.get("total_cases") or len(test_cases))

        if write_alongside and src_path.is_relative_to(BASE_DIR):
            out_spec_path = src_path.with_name(f"{src_path.stem}.generated.spec.ts")
        else:
            out_spec_path = Path(f"/tmp/{src_path.stem}.generated.spec.ts")

        out_spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_code = qc_gen.render_unit_test_file(code_ctx, test_cases, out_spec_path)
        out_spec_path.write_text(spec_code, encoding="utf-8")

        rel_out = str(out_spec_path.relative_to(BASE_DIR)) if out_spec_path.is_relative_to(BASE_DIR) else str(out_spec_path)
        generated_files.append({
            "source": src_rel,
            "source_file": src_rel,
            "out_spec": rel_out,
            "abs_out_spec": str(out_spec_path),
            "written_on_disk": True,
            "cases_count": len(test_cases),
            "total_cases": len(test_cases),
            "requirement_coverage_pct": cov_report.get("requirement_coverage_pct", 100),
            "coverage_item_pct": cov_report.get("coverage_item_pct", 100),
            "symbol_coverage_pct": cov_report.get("symbol_coverage_pct", 100),
            "framework": code_ctx.get("framework", "jest"),
        })
        combined_spec_code.append(f"// ============================================================\n// FILE: {rel_out} (from {src_rel})\n// ============================================================\n" + spec_code)

        if sync_harness:
            try:
                synced = qc_gen.sync_cases_to_harness(test_cases, parent_task_id=int(linked_task_id) if linked_task_id else None)
                total_synced += len(synced)
            except Exception:
                pass

    if sync_harness and total_synced > 0:
        get_cached_rows(force=True)

    # Record a detailed background job in _JOBS so it streams in the Live Console
    node_label = target_node or "local (:8765)"
    src_list_str = ", ".join(g["source"] for g in generated_files)
    summary_lines = [
        f"echo '[PASEO LINK AUTO-GEN] Link: {raw_link} (Type: {link_kind})'",
        f"echo '[TARGET NODE] {node_label}'",
        f"echo '[DISCOVERED SOURCES] {len(generated_files)} file(s): {src_list_str}'",
    ]
    for g in generated_files:
        out_s = g["out_spec"]
        cnt_s = g["cases_count"]
        summary_lines.append(f"echo '[GENERATED SPEC] -> {out_s} ({cnt_s} ISTQB test cases)'")

    if run_test and generated_files:
        summary_lines.append("python3 tools/test_qc_generator.py")

    job_cmd = " && ".join(summary_lines)
    job = start_background_job(
        "qc-gen",
        f"Link Auto-Gen ({len(generated_files)} files)",
        f"bash -c {shlex.quote(job_cmd)}",
        cwd=str(BASE_DIR),
        item_id=int(linked_task_id) if linked_task_id else None,
    )

    return {
        "ok": True,
        "link": raw_link,
        "input_link": raw_link,
        "link_kind": link_kind,
        "executed_on_node": target_node or "http://127.0.0.1:8765",
        "target_node": target_node or "http://127.0.0.1:8765",
        "workspace": str(BASE_DIR),
        "task_id": linked_task_id,
        "generated_files": generated_files,
        "total_cases": total_cases,
        "total_cases_generated": total_cases,
        "synced_count": total_synced,
        "total_synced_to_harness": total_synced,
        "coverage_report": last_cov_report,
        "spec_code": "\n\n".join(combined_spec_code),
        "out_spec": generated_files[0]["out_spec"] if generated_files else "",
        "job_id": job["id"],
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Paseo Control Center</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0B0E14;
      --bg-surface: #121721;
      --bg-elevated: #181F2C;
      --bg-input: #0D1119;
      --border: rgba(255, 255, 255, 0.08);
      --border-hover: rgba(255, 255, 255, 0.16);
      --text: #F1F5F9;
      --text-secondary: #94A3B8;
      --text-muted: #64748B;
      --primary: #3B82F6;
      --primary-hover: #2563EB;
      --success: #10B981;
      --warning: #F59E0B;
      --danger: #F43F5E;
      --purple: #8B5CF6;
      --radius: 10px;
      --font: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color-scheme: dark;
    }
    * {
      box-sizing: border-box;
      scrollbar-width: thin;
      scrollbar-color: rgba(148, 163, 184, 0.25) transparent;
    }
    *::-webkit-scrollbar { width: 6px; height: 6px; }
    *::-webkit-scrollbar-track { background: transparent; }
    *::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.25);
      border-radius: 999px;
    }
    *::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.45); }
    *::-webkit-scrollbar-corner { background: transparent; }

    body {
      margin: 0;
      font-family: var(--font);
      font-size: 13.5px;
      -webkit-font-smoothing: antialiased;
      color: var(--text);
      background: var(--bg);
      line-height: 1.5;
    }

    /* Clean Minimalist Topbar */
    header.topbar {
      position: sticky;
      top: 0;
      z-index: 40;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 32px;
      background: rgba(11, 14, 20, 0.88);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      gap: 16px;
    }

    nav.main-nav {
      display: flex;
      gap: 4px;
      background: var(--bg-surface);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }
    .nav-btn {
      background: transparent;
      color: var(--text-secondary);
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      font-family: var(--font);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }
    .nav-btn:hover { color: var(--text); }
    .nav-btn.active {
      background: var(--bg-elevated);
      color: var(--text);
      font-weight: 600;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    .nav-counter {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 999px;
      background: rgba(59, 130, 246, 0.18);
      color: #60A5FA;
    }

    .status-bar {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .badge {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11.5px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .badge.live { background: rgba(16, 185, 129, 0.12); color: #34D399; }
    .badge.err { background: rgba(244, 63, 94, 0.12); color: #FB7185; }

    /* Main Container */
    main.container {
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px 32px 56px;
    }
    .view-section { display: none; }
    .view-section.active { display: block; }

    /* Clean 4-Card KPI Strip */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }
    @media (max-width: 900px) {
      .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    }
    .kpi-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: border-color 0.15s, background 0.15s;
    }
    .kpi-card:hover {
      border-color: var(--border-hover);
      background: var(--bg-elevated);
    }
    .kpi-label {
      font-size: 12.5px;
      color: var(--text-secondary);
      font-weight: 500;
    }
    .kpi-val {
      font-size: 24px;
      font-weight: 700;
      line-height: 1.1;
      margin-top: 4px;
    }

    /* Buttons & Inputs */
    .btn {
      background: var(--bg-elevated);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 7px 14px;
      border-radius: 7px;
      font-family: var(--font);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
      white-space: nowrap;
    }
    .btn:hover { border-color: var(--border-hover); background: #222B3D; }
    .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-success { background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.35); color: #34D399; }
    .btn-success:hover { background: rgba(16, 185, 129, 0.25); }
    .btn-warning { background: rgba(245, 158, 11, 0.14); border-color: rgba(245, 158, 11, 0.35); color: #FBBF24; }
    .btn-purple { background: rgba(139, 92, 246, 0.16); border-color: rgba(139, 92, 246, 0.4); color: #C4B5FD; }
    .btn-sm { padding: 5px 10px; font-size: 12px; border-radius: 6px; }

    input, select, textarea {
      background: var(--bg-input);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 8px 12px;
      font-size: 13px;
      font-family: var(--font);
    }
    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: var(--primary);
    }

    /* Streamlined 1-Row Filter Bar */
    search.filter-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }
    .filter-group {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      flex: 1;
    }

    /* Spacious Table */
    .table-wrap {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: auto;
      max-height: 70vh;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }
    th, td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      vertical-align: middle;
    }
    td.title-cell {
      white-space: normal;
      font-weight: 500;
      color: var(--text);
      max-width: 560px;
    }
    th {
      position: sticky;
      top: 0;
      background: #141A26;
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      z-index: 5;
      user-select: none;
      white-space: nowrap;
    }
    th:hover { color: var(--text); }
    tbody tr { transition: background 0.1s; cursor: pointer; }
    tbody tr:hover { background: rgba(255, 255, 255, 0.03); }

    /* Subtle Status Pills */
    .pill {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
    }
    .st-New, .st-Design { background: rgba(148, 163, 184, 0.12); color: #CBD5E1; }
    .st-Accepted { background: rgba(6, 182, 212, 0.14); color: #22D3EE; }
    .st-Active { background: rgba(59, 130, 246, 0.16); color: #60A5FA; }
    .st-Resolved { background: rgba(245, 158, 11, 0.16); color: #FBBF24; }
    .st-Closed { background: rgba(16, 185, 129, 0.14); color: #34D399; }
    .st-Blocked { background: rgba(244, 63, 94, 0.16); color: #FB7185; }

    .type-tag {
      font-size: 11.5px;
      padding: 3px 8px;
      border-radius: 5px;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-secondary);
      font-weight: 500;
    }
    .type-Bug { background: rgba(244, 63, 94, 0.12); color: #FDA4AF; }
    .type-Testcase { background: rgba(139, 92, 246, 0.12); color: #C4B5FD; }
    .type-Epic { background: rgba(59, 130, 246, 0.12); color: #93C5FD; }

    .src-tag {
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 600;
      text-transform: uppercase;
    }
    .src-local, .src-bot { background: rgba(6, 182, 212, 0.15); color: #22D3EE; }
    .src-tfs { background: rgba(148, 163, 184, 0.08); color: #94A3B8; }

    /* Panels & Grids */
    .split-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      align-items: start;
    }
    @media (max-width: 1024px) {
      .split-grid { grid-template-columns: 1fr; }
    }
    .panel {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 20px;
    }
    .panel-hdr {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
      gap: 12px;
      flex-wrap: wrap;
    }
    .panel-hdr h2, .panel-hdr h3 {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
    }
    .form-grid { display: grid; gap: 14px; }
    .field-row { display: flex; flex-direction: column; gap: 6px; }
    .field-row label {
      font-size: 12.5px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    /* Terminal Output */
    .terminal-box {
      background: #080B10;
      color: #E2E8F0;
      font-family: var(--font);
      font-size: 12.5px;
      padding: 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
      min-height: 260px;
      max-height: 500px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.6;
    }

    /* Clean 4-Column Core SLPC Agent Grid */
    .agent-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 20px;
    }
    @media (max-width: 1100px) {
      .agent-grid { grid-template-columns: repeat(2, 1fr); }
    }
    .agent-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
    }
    .agent-top {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .agent-avatar {
      width: 38px;
      height: 38px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 15px;
      color: #fff;
      flex-shrink: 0;
    }
    .agent-stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      background: var(--bg-input);
      border: 1px solid var(--border);
      padding: 10px;
      border-radius: 8px;
      text-align: center;
    }
    .agent-stat-num { font-size: 15px; font-weight: 700; }
    .agent-stat-lbl { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }

    /* Modal Dialog */
    dialog {
      background: var(--bg-surface);
      color: var(--text);
      border: 1px solid var(--border-hover);
      border-radius: 12px;
      padding: 0;
      width: min(720px, 94vw);
      max-height: 86vh;
      box-shadow: 0 24px 48px rgba(0, 0, 0, 0.6);
    }
    dialog::backdrop {
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(4px);
    }
    .dlg-hdr {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
    }
    .dlg-body {
      padding: 20px;
      overflow-y: auto;
      max-height: calc(86vh - 130px);
    }
    .dlg-ftr {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      padding: 14px 20px;
      border-top: 1px solid var(--border);
    }
  </style>
</head>
<body>
  <header class="topbar">
    <nav class="main-nav" aria-label="Main Navigation">
      <button type="button" class="nav-btn active" data-tab="view-board">
        Công việc <span class="nav-counter" id="nav-count">0</span>
      </button>
      <button type="button" class="nav-btn" data-tab="view-automation">
        Build &amp; Sinh Unit Test
      </button>
      <button type="button" class="nav-btn" data-tab="view-agents">
        Điều phối Agent
      </button>
    </nav>

    <div class="status-bar">
      <span id="st" class="badge live">Live</span>
      <button type="button" class="btn btn-primary btn-sm" id="btn-open-create">Tạo mới</button>
    </div>
  </header>

  <main class="container">
    <!-- ==================== TAB 1: DANH SÁCH CÔNG VIỆC ==================== -->
    <section id="view-board" class="view-section active">
      <div class="kpi-grid" id="kpi-container"></div>

      <search class="filter-bar">
        <div class="filter-group" id="f"></div>
        <div style="display:flex;align-items:center;gap:10px">
          <span id="n" style="font-size:12.5px;color:var(--text-secondary)"></span>
          <button type="button" class="btn btn-sm" id="btn-reset-filter">Bỏ lọc</button>
        </div>
      </search>

      <div class="table-wrap">
        <table>
          <thead><tr id="h"></tr></thead>
          <tbody id="b"></tbody>
        </table>
      </div>
    </section>

    <!-- ==================== TAB 2: BUILD & SINH UNIT TEST ==================== -->
    <section id="view-automation" class="view-section">
      <div class="split-grid">
        <!-- Left: Quick Actions + 5-Stage Unit Test Generator -->
        <div>
          <div class="panel">
            <div class="panel-hdr">
              <h3>Chạy nhanh (Build &amp; Kiểm thử)</h3>
            </div>
            <div id="preset-container" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px"></div>
            <div style="display:flex;gap:8px">
              <input id="custom-cmd-input" placeholder="Nhập lệnh CLI (VD: npx nx test wicx-core)..." style="flex:1">
              <input id="custom-cwd-input" placeholder="Thư mục (mặc định: root)" size="18">
              <button type="button" class="btn btn-primary" id="btn-run-custom">Chạy</button>
            </div>
          </div>

          <div class="panel" style="margin-bottom:0">
            <div class="panel-hdr">
              <h3>Sinh Unit Test &amp; Testcase tự động (5-Stage ISTQB)</h3>
            </div>
            <div class="form-grid">
              <div class="field-row">
                <label for="qc-source">File Source Code (<code>--source</code>)</label>
                <input id="qc-source" list="dl-sources" value="projects/wicx-crm-fe/libs/wicx-core/src/utils/helps/validator.helper.ts">
                <datalist id="dl-sources"></datalist>
              </div>
              <div class="field-row">
                <label for="qc-spec">File Spec / Acceptance Criteria (<code>--spec</code>)</label>
                <input id="qc-spec" list="dl-specs" value="projects/wicx-crm-fe/libs/wicx-core/spec.md">
                <datalist id="dl-specs"></datalist>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                <div class="field-row">
                  <label for="qc-task-id">Gắn với Work Item ID (Tuỳ chọn)</label>
                  <input id="qc-task-id" type="number" placeholder="VD: 161502">
                </div>
                <div class="field-row">
                  <label for="qc-out-spec">File <code>*.spec.ts</code> đầu ra</label>
                  <input id="qc-out-spec" value="/tmp/generated.spec.ts">
                </div>
              </div>
              <div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px;color:var(--text-secondary)">
                  <input type="checkbox" id="qc-sync-harness"> Đồng bộ Testcase lên DB
                </label>
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:13px;color:var(--text-secondary)">
                  <input type="checkbox" id="qc-run-after"> Chạy test ngay sau khi sinh
                </label>
              </div>
              <div style="display:flex;gap:10px">
                <button type="button" class="btn btn-primary" id="btn-qc-generate">Sinh Unit Test (5-Stage)</button>
                <button type="button" class="btn btn-purple" id="btn-qc-dispatch-agent">Giao Agent QC xử lý</button>
              </div>
            </div>

            <div id="qc-result-box" style="margin-top:16px;display:none">
              <div class="panel-hdr" style="margin-bottom:8px">
                <h3>Kết quả sinh Test</h3>
                <span id="qc-cov-badges" style="display:flex;gap:6px;flex-wrap:wrap"></span>
              </div>
              <pre class="terminal-box" id="qc-spec-preview" style="min-height:180px;max-height:300px"></pre>
            </div>
          </div>
        </div>

        <!-- Right: Live Console -->
        <div class="panel" style="margin-bottom:0">
          <div class="panel-hdr">
            <h3>Kết quả thực thi (Live Console)</h3>
            <button type="button" class="btn btn-sm" id="btn-refresh-jobs">Làm mới</button>
          </div>
          <div id="job-list" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px"></div>
          <pre class="terminal-box" id="job-terminal" style="min-height:460px">Chưa có lệnh nào đang chạy. Chọn một tác vụ bên trái để bắt đầu...</pre>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 3: ĐIỀU PHỐI AGENT (SLPC) ==================== -->
    <section id="view-agents" class="view-section">
      <div class="agent-grid" id="agent-cards-container"></div>

      <div class="split-grid">
        <div class="panel" style="margin-bottom:0">
          <div class="panel-hdr">
            <h3>Giao việc trực tiếp cho Agent</h3>
          </div>
          <div class="form-grid">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
              <div class="field-row">
                <label for="ag-profile">Vai trò Agent (SLPC)</label>
                <select id="ag-profile">
                  <option value="Supervisor">Supervisor (Quản lý Scope &amp; Epic)</option>
                  <option value="Lead">Lead (Kiến trúc &amp; Chia Task)</option>
                  <option value="Peer">Peer (Lập trình &amp; Unit Test)</option>
                  <option value="QC" selected>QC (Kiểm thử &amp; Nghiệm thu)</option>
                </select>
              </div>
              <div class="field-row">
                <label for="ag-item-id">Work Item ID (Tuỳ chọn)</label>
                <input id="ag-item-id" type="number" placeholder="VD: 161095">
              </div>
            </div>
            <div class="field-row">
              <label for="ag-prompt">Nội dung chỉ thị (Prompt)</label>
              <textarea id="ag-prompt" rows="4" placeholder="Nhập yêu cầu cho Agent..."></textarea>
            </div>
            <div>
              <button type="button" class="btn btn-primary" id="btn-dispatch-agent">Khởi chạy Agent</button>
            </div>
          </div>
        </div>

        <div class="panel" style="margin-bottom:0">
          <div class="panel-hdr">
            <h3>Quy tắc của Agent đang chọn</h3>
          </div>
          <pre class="terminal-box" id="ag-prompt-preview" style="min-height:220px;max-height:260px"></pre>
        </div>
      </div>
    </section>
  </main>

  <!-- ==================== MODAL 1: CHI TIẾT WORK ITEM ==================== -->
  <dialog id="dlg-item">
    <div class="dlg-hdr">
      <h2 id="dlg-item-title" style="margin:0;font-size:15px">Chi tiết công việc</h2>
      <button type="button" class="btn btn-sm" id="btn-close-item">Đóng</button>
    </div>
    <div class="dlg-body">
      <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-bottom:14px">
        <div class="field-row">
          <label for="ed-state">Trạng thái</label>
          <select id="ed-state">
            <option value="New">New</option>
            <option value="Design">Design</option>
            <option value="Accepted">Accepted</option>
            <option value="Active">Active</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
            <option value="Blocked">Blocked</option>
          </select>
        </div>
        <div class="field-row">
          <label for="ed-profile">Vai trò SLPC</label>
          <select id="ed-profile">
            <option value="">-- Giữ nguyên --</option>
            <option value="supervisor">Supervisor</option>
            <option value="lead">Lead</option>
            <option value="peer">Peer</option>
            <option value="qc">QC</option>
          </select>
        </div>
        <div class="field-row">
          <label for="ed-assignee">Người phụ trách</label>
          <input id="ed-assignee" placeholder="Tên người nhận...">
        </div>
      </div>
      <div class="field-row" style="margin-bottom:12px">
        <label>Mô tả</label>
        <pre class="terminal-box" id="dlg-item-desc" style="min-height:80px;max-height:160px"></pre>
      </div>
      <div class="field-row">
        <label>Tiêu chí nghiệm thu (Acceptance Criteria)</label>
        <pre class="terminal-box" id="dlg-item-ac" style="min-height:80px;max-height:160px"></pre>
      </div>
    </div>
    <div class="dlg-ftr">
      <button type="button" class="btn btn-purple" id="btn-item-wake-agent">Giao Agent xử lý</button>
      <button type="button" class="btn btn-warning" id="btn-item-qc-test">Sinh Unit Test (QC)</button>
      <button type="button" class="btn btn-primary" id="btn-item-save">Lưu thay đổi</button>
    </div>
  </dialog>

  <!-- ==================== MODAL 2: TẠO MỚI WORK ITEM ==================== -->
  <dialog id="dlg-create">
    <div class="dlg-hdr">
      <h2 style="margin:0;font-size:15px">Tạo công việc mới</h2>
      <button type="button" class="btn btn-sm" id="btn-close-create">Đóng</button>
    </div>
    <div class="dlg-body">
      <div class="form-grid">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
          <div class="field-row">
            <label for="new-type">Loại</label>
            <select id="new-type">
              <option value="Epic">Epic</option>
              <option value="Feature">Feature</option>
              <option value="User Story">User Story</option>
              <option value="Task" selected>Task</option>
              <option value="Testcase">Testcase</option>
              <option value="Bug">Bug</option>
            </select>
          </div>
          <div class="field-row">
            <label for="new-prio">Độ ưu tiên</label>
            <select id="new-prio">
              <option value="P0">P0 (Critical)</option>
              <option value="P1">P1 (High)</option>
              <option value="P2" selected>P2 (Medium)</option>
              <option value="P3">P3 (Low)</option>
            </select>
          </div>
          <div class="field-row">
            <label for="new-profile">Giao cho vai trò</label>
            <select id="new-profile">
              <option value="lead">Lead</option>
              <option value="peer" selected>Peer</option>
              <option value="qc">QC</option>
              <option value="supervisor">Supervisor</option>
            </select>
          </div>
        </div>
        <div class="field-row">
          <label for="new-title">Tiêu đề</label>
          <input id="new-title" placeholder="VD: [CRM] - Tích hợp bộ lọc khách hàng">
        </div>
        <div class="field-row">
          <label for="new-desc">Mô tả</label>
          <textarea id="new-desc" rows="3" placeholder="Mô tả chi tiết..."></textarea>
        </div>
        <div class="field-row">
          <label for="new-ac">Tiêu chí nghiệm thu (AC)</label>
          <textarea id="new-ac" rows="3" placeholder="- AC1: ..."></textarea>
        </div>
        <div style="display:flex;gap:16px;align-items:center">
          <div class="field-row" style="width:150px">
            <label for="new-parent">Parent ID (Tuỳ chọn)</label>
            <input id="new-parent" type="number" placeholder="VD: 1">
          </div>
          <label style="display:flex;align-items:center;gap:6px;cursor:pointer;margin-top:18px;font-size:13px;color:var(--text-secondary)">
            <input type="checkbox" id="new-dispatch" checked> Tự động gọi Agent nhận việc
          </label>
        </div>
      </div>
    </div>
    <div class="dlg-ftr">
      <button type="button" class="btn btn-primary" id="btn-submit-create">Tạo mới</button>
    </div>
  </dialog>

  <script>
    let D = __DATA__;
    const sel = { q: '', s: 'id', d: -1 };
    const filt = [
      { key: 'source', label: 'Tất cả nguồn' },
      { key: 'type', label: 'Tất cả loại' },
      { key: 'state', label: 'Tất cả trạng thái' },
      { key: 'assigned_to_profile', label: 'Tất cả vai trò SLPC' },
      { key: 'iteration_path', label: 'Tất cả Sprint' }
    ];
    const f = document.getElementById('f');
    let currentItem = null;
    let activeJobId = null;
    let cachedAgents = [];

    // Tab Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
        if (btn.dataset.tab === 'view-agents') loadAgents();
        if (btn.dataset.tab === 'view-automation') { loadTargets(); pollJobs(); }
      };
    });

    function esc(s) {
      return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function renderKPIs() {
      const total = D.length;
      const localCount = D.filter(x => (x.source || 'local') !== 'tfs').length;
      const tfsCount = total - localCount;
      const active = D.filter(x => x.state === 'Active').length;
      const resolved = D.filter(x => x.state === 'Resolved').length;
      const closed = D.filter(x => x.state === 'Closed').length;

      document.getElementById('nav-count').textContent = total;

      const cards = [
        { lbl: `Tổng công việc (TFS: ${tfsCount} · Local: ${localCount})`, val: total, color: '#F1F5F9', filter: {} },
        { lbl: 'Đang thực hiện (Active)', val: active, color: '#60A5FA', filter: { state: 'Active' } },
        { lbl: 'Chờ QC kiểm định (Resolved)', val: resolved, color: '#FBBF24', filter: { state: 'Resolved' } },
        { lbl: 'Đã hoàn tất (Closed)', val: closed, color: '#34D399', filter: { state: 'Closed' } },
      ];
      document.getElementById('kpi-container').innerHTML = cards.map((c, idx) => `
        <div class="kpi-card" data-kpi="${idx}">
          <div>
            <div class="kpi-label">${c.lbl}</div>
            <div class="kpi-val" style="color:${c.color}">${c.val}</div>
          </div>
        </div>
      `).join('');

      document.querySelectorAll('.kpi-card').forEach((el, idx) => {
        el.onclick = () => {
          const flt = cards[idx].filter;
          initFilters(flt);
          r();
        };
      });
    }

    function initFilters(cur = {}) {
      const qVal = cur.q !== undefined ? cur.q : (document.getElementById('q')?.value || '');
      let html = `<input id="q" placeholder="Tìm theo ID, tiêu đề, người phụ trách..." size="28" value="${esc(qVal)}">`;
      filt.forEach(({ key, label }) => {
        const vals = [...new Set(D.map(x => x[key] || ''))].filter(Boolean).sort();
        const selVal = cur[key] !== undefined ? cur[key] : (f.querySelector(`select[data-k="${key}"]`)?.value || '');
        html += `<select data-k="${key}"><option value="">${label}</option>` +
          vals.map(v => `<option value="${esc(v)}" ${v === selVal ? 'selected' : ''}>${esc(v.split('\\').pop())}</option>`).join('') +
          '</select>';
      });
      f.innerHTML = html;
      f.oninput = r;
    }

    document.getElementById('btn-reset-filter').onclick = () => {
      initFilters({ q: '', source: '', type: '', state: '', assigned_to_profile: '', iteration_path: '' });
      r();
    };

    const COLS = [
      { k: "id", label: "ID" },
      { k: "source", label: "Nguồn" },
      { k: "type", label: "Loại" },
      { k: "title", label: "Tiêu đề công việc" },
      { k: "state", label: "Trạng thái" },
      { k: "assigned_to", label: "Phụ trách" },
      { k: "iteration_path", label: "Sprint" }
    ];
    document.getElementById('h').innerHTML = COLS.map(c => `<th data-k="${c.k}">${c.label}</th>`).join('') + '<th style="text-align:right">Thao tác</th>';

    function r() {
      renderKPIs();
      const q = (document.getElementById('q')?.value || '').toLowerCase();
      const fs = [...f.querySelectorAll('select')].filter(s => s.value);
      let a = D.filter(x =>
        (!q || (String(x.id) + ' ' + (x.title || '') + ' ' + (x.assigned_to || '') + ' ' + (x.assigned_to_profile || '') + ' ' + (x.source || '')).toLowerCase().includes(q)) &&
        fs.every(s => String(x[s.dataset.k] || '') === s.value)
      );
      a.sort((x, y) => (x[sel.s] > y[sel.s] ? 1 : x[sel.s] < y[sel.s] ? -1 : 0) * sel.d);
      document.getElementById('n').textContent = `${a.length} / ${D.length} mục`;

      const b = document.getElementById('b');
      b.innerHTML = a.slice(0, 500).map(x => {
        const slpc = (x.assigned_to_profile || 'peer').toUpperCase();
        const person = x.assigned_to ? `${esc(x.assigned_to)} (${slpc})` : slpc;
        const src = (x.source || 'local').toLowerCase();
        return `
        <tr data-id="${x.id}">
          <td style="font-weight:600;color:#60A5FA;white-space:nowrap">#${x.id}</td>
          <td style="white-space:nowrap"><span class="src-tag src-${esc(src)}">${esc(src)}</span></td>
          <td style="white-space:nowrap"><span class="type-tag type-${esc(x.type)}">${esc(x.type)}</span></td>
          <td class="title-cell">${esc(x.title)}</td>
          <td style="white-space:nowrap"><span class="pill st-${esc(x.state)}">${esc(x.state)}</span></td>
          <td style="color:var(--text-secondary);font-size:13px;white-space:nowrap">${person}</td>
          <td style="color:var(--text-muted);font-size:12.5px;white-space:nowrap">${esc((x.iteration_path || '').split('\\').pop())}</td>
          <td style="text-align:right;white-space:nowrap" onclick="event.stopPropagation()">
            <button type="button" class="btn btn-sm" onclick="openItemModal(${x.id})">Chi tiết</button>
            <button type="button" class="btn btn-sm btn-warning" onclick="jumpToQC(${x.id})">QC Test</button>
          </td>
        </tr>`;
      }).join('');

      b.querySelectorAll('tr').forEach(tr => {
        tr.onclick = () => openItemModal(Number(tr.dataset.id));
      });
    }

    document.getElementById('h').onclick = e => {
      const k = e.target.dataset.k;
      if (!k) return;
      sel.d = sel.s === k ? -sel.d : 1;
      sel.s = k;
      r();
    };

    // Modal 1: Item Detail & Update
    const dlgItem = document.getElementById('dlg-item');
    window.openItemModal = function(id) {
      const item = D.find(x => Number(x.id) === Number(id));
      if (!item) return;
      currentItem = item;
      document.getElementById('dlg-item-title').textContent = `#${item.id} [${item.type}] ${item.title}`;
      document.getElementById('ed-state').value = item.state || 'New';
      document.getElementById('ed-profile').value = (item.assigned_to_profile || '').toLowerCase();
      document.getElementById('ed-assignee').value = item.assigned_to || '';
      document.getElementById('dlg-item-desc').textContent = item.description || '(Không có mô tả)';
      document.getElementById('dlg-item-ac').textContent = item.acceptance_criteria || '(Chưa có Acceptance Criteria)';
      dlgItem.showModal();
    };
    document.getElementById('btn-close-item').onclick = () => dlgItem.close();

    document.getElementById('btn-item-save').onclick = async () => {
      if (!currentItem) return;
      const payload = {
        id: currentItem.id,
        state: document.getElementById('ed-state').value,
        assigned_to_profile: document.getElementById('ed-profile').value || null,
        assigned_to: document.getElementById('ed-assignee').value || null
      };
      const res = await fetch('/api/work-items/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const out = await res.json();
      if (!res.ok) {
        alert('Lỗi cập nhật: ' + (out.error || res.statusText));
        return;
      }
      dlgItem.close();
      await poll(true);
    };

    document.getElementById('btn-item-wake-agent').onclick = async () => {
      if (!currentItem) return;
      const prof = document.getElementById('ed-profile').value || currentItem.assigned_to_profile || 'Peer';
      dlgItem.close();
      document.querySelector('[data-tab="view-agents"]').click();
      document.getElementById('ag-profile').value = prof.charAt(0).toUpperCase() + prof.slice(1);
      if (prof.toLowerCase() === 'qc') document.getElementById('ag-profile').value = 'QC';
      document.getElementById('ag-item-id').value = currentItem.id;
      document.getElementById('ag-prompt').value = `Xử lý Work Item #${currentItem.id} [${currentItem.type}]: ${currentItem.title}\nAC: ${currentItem.acceptance_criteria || currentItem.description || ''}`;
    };

    window.jumpToQC = function(id) {
      if (dlgItem.open) dlgItem.close();
      document.querySelector('[data-tab="view-automation"]').click();
      document.getElementById('qc-task-id').value = id;
    };
    document.getElementById('btn-item-qc-test').onclick = () => {
      if (currentItem) window.jumpToQC(currentItem.id);
    };

    // Modal 2: Create Work Item
    const dlgCreate = document.getElementById('dlg-create');
    document.getElementById('btn-open-create').onclick = () => dlgCreate.showModal();
    document.getElementById('btn-close-create').onclick = () => dlgCreate.close();
    document.getElementById('btn-submit-create').onclick = async () => {
      const payload = {
        type: document.getElementById('new-type').value,
        priority: document.getElementById('new-prio').value,
        assigned_to_profile: document.getElementById('new-profile').value,
        title: document.getElementById('new-title').value.trim(),
        description: document.getElementById('new-desc').value.trim(),
        acceptance_criteria: document.getElementById('new-ac').value.trim(),
        parent_id: document.getElementById('new-parent').value ? Number(document.getElementById('new-parent').value) : null,
        dispatch: document.getElementById('new-dispatch').checked
      };
      const res = await fetch('/api/work-items/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const out = await res.json();
      if (!res.ok) {
        alert('Lỗi tạo Work Item: ' + (out.error || res.statusText));
        return;
      }
      dlgCreate.close();
      await poll(true);
    };

    // Tab 2: Build & QC Automation
    let targetsLoaded = false;
    async function loadTargets() {
      if (targetsLoaded) return;
      try {
        const res = await fetch('/api/source-files');
        const data = await res.json();
        document.getElementById('dl-sources').innerHTML = (data.sources || []).map(s => `<option value="${esc(s)}">`).join('');
        document.getElementById('dl-specs').innerHTML = (data.specs || []).map(s => `<option value="${esc(s)}">`).join('');
        document.getElementById('preset-container').innerHTML = (data.presets || []).map(p => `
          <button type="button" class="btn btn-sm" title="${esc(p.command)}" onclick='runAutomationJob(${JSON.stringify(p.title)}, ${JSON.stringify(p.command)}, ${JSON.stringify(p.cwd)})'>${esc(p.title)}</button>
        `).join('');
        targetsLoaded = true;
      } catch (e) {
        console.error(e);
      }
    }

    window.runAutomationJob = async function(title, command, cwd = '') {
      const res = await fetch('/api/automation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind: 'automation', title, command, cwd })
      });
      const job = await res.json();
      activeJobId = job.id;
      await pollJobs();
    };

    document.getElementById('btn-run-custom').onclick = () => {
      const cmd = document.getElementById('custom-cmd-input').value.trim();
      const cwd = document.getElementById('custom-cwd-input').value.trim();
      if (!cmd) return alert('Vui lòng nhập lệnh cần chạy!');
      window.runAutomationJob('Custom: ' + cmd.slice(0, 32), cmd, cwd);
    };

    document.getElementById('btn-qc-generate').onclick = async () => {
      const btn = document.getElementById('btn-qc-generate');
      btn.disabled = true;
      btn.textContent = 'Đang chạy 5-Stage...';
      try {
        const payload = {
          source: document.getElementById('qc-source').value.trim(),
          spec: document.getElementById('qc-spec').value.trim(),
          task_id: document.getElementById('qc-task-id').value ? Number(document.getElementById('qc-task-id').value) : null,
          out_spec: document.getElementById('qc-out-spec').value.trim(),
          sync_harness: document.getElementById('qc-sync-harness').checked,
          run_test: document.getElementById('qc-run-after').checked
        };
        const res = await fetch('/api/automation/qc-generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const out = await res.json();
        if (!res.ok) {
          alert('Lỗi: ' + (out.error || res.statusText));
          return;
        }
        const cov = out.coverage_report || {};
        document.getElementById('qc-result-box').style.display = 'block';
        document.getElementById('qc-cov-badges').innerHTML = `
          <span class="badge live">Cases: ${cov.total_cases}</span>
          <span class="badge live">REQ: ${cov.requirement_coverage_pct}%</span>
          <span class="badge live">CI: ${cov.coverage_item_pct}%</span>
          <span class="badge live">Symbol: ${cov.symbol_coverage_pct}%</span>
        `;
        document.getElementById('qc-spec-preview').textContent = out.spec_code || JSON.stringify(cov, null, 2);
        if (out.job_id) {
          activeJobId = out.job_id;
          await pollJobs();
        }
        if (payload.sync_harness) await poll(true);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Sinh Unit Test (5-Stage)';
      }
    };

    document.getElementById('btn-qc-dispatch-agent').onclick = async () => {
      const src = document.getElementById('qc-source').value.trim();
      const spc = document.getElementById('qc-spec').value.trim();
      const tid = document.getElementById('qc-task-id').value;
      const prompt = `Chạy tools/qc_test_generator.py cho source '${src}' và spec '${spc}'${tid ? ' (Task #' + tid + ')' : ''}, hoàn thiện assertions cho unit test và verify kết quả.`;
      const res = await fetch('/api/agents/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: 'QC', item_id: tid ? Number(tid) : null, prompt })
      });
      const out = await res.json();
      if (out.job_id) {
        activeJobId = out.job_id;
        await pollJobs();
      }
    };

    async function pollJobs() {
      try {
        const res = await fetch('/api/automation/jobs?t=' + Date.now());
        const jobs = await res.json();
        const listEl = document.getElementById('job-list');
        if (!jobs.length) {
          listEl.innerHTML = '';
          return;
        }
        if (!activeJobId || !jobs.some(j => j.id === activeJobId)) {
          activeJobId = jobs[0].id;
        }
        listEl.innerHTML = jobs.slice(0, 6).map(j => {
          const stTxt = j.status === 'running' ? '[Đang chạy]' : (j.status === 'passed' ? '[OK]' : '[Lỗi]');
          const activeStyle = j.id === activeJobId ? 'border-color:var(--primary);background:rgba(59,130,246,0.16)' : '';
          return `<button type="button" class="btn btn-sm" style="${activeStyle}" onclick="selectJob('${j.id}')">${stTxt} ${esc(j.title)} (${j.elapsed}s)</button>`;
        }).join('');
        const current = jobs.find(j => j.id === activeJobId) || jobs[0];
        if (current) {
          const term = document.getElementById('job-terminal');
          if (term) {
            term.textContent = `[${current.status.toUpperCase()}] ${current.title} (${current.elapsed}s)\n` + current.output;
            term.scrollTop = term.scrollHeight;
          }
        }
      } catch (e) {
        console.error(e);
      }
    }
    window.selectJob = function(id) {
      activeJobId = id;
      pollJobs();
    };
    document.getElementById('btn-refresh-jobs').onclick = pollJobs;

    // Tab 3: SLPC Agent Management (Only 4 Core Roles for Clean Layout)
    async function loadAgents() {
      try {
        const res = await fetch('/api/agents?t=' + Date.now());
        const data = await res.json();
        cachedAgents = data.profiles || [];
        const coreNames = ['supervisor', 'lead', 'peer', 'qc'];
        const coreAgents = cachedAgents.filter(a => coreNames.includes(a.name.toLowerCase()));
        document.getElementById('agent-cards-container').innerHTML = coreAgents.map(a => `
          <div class="agent-card">
            <div>
              <div>
                <div style="font-size:15px;font-weight:700;color:${a.color}">${esc(a.name)}</div>
                <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">${esc(a.role)}</div>
              </div>
              <div class="agent-stats" style="margin-top:14px">
                <div><div class="agent-stat-num" style="color:#60A5FA">${a.counts.active}</div><div class="agent-stat-lbl">Đang làm</div></div>
                <div><div class="agent-stat-num" style="color:#FBBF24">${a.counts.resolved}</div><div class="agent-stat-lbl">Chờ QC</div></div>
                <div><div class="agent-stat-num" style="color:#34D399">${a.counts.closed}</div><div class="agent-stat-lbl">Hoàn tất</div></div>
              </div>
            </div>
            <div style="display:flex;gap:8px">
              <button type="button" class="btn btn-sm btn-primary" style="flex:1" onclick="selectAgentProfile('${esc(a.name)}')">Giao việc</button>
              <button type="button" class="btn btn-sm" onclick="filterBoardByAgent('${esc(a.name.toLowerCase())}')">Xem (${a.counts.total})</button>
            </div>
          </div>
        `).join('');
        updateAgentPromptPreview();
      } catch (e) {
        console.error(e);
      }
    }

    function updateAgentPromptPreview() {
      const selName = document.getElementById('ag-profile').value;
      const found = cachedAgents.find(a => a.name.toLowerCase() === selName.toLowerCase());
      document.getElementById('ag-prompt-preview').textContent = found ? (found.notes || '(Không có hướng dẫn)') : '';
    }
    document.getElementById('ag-profile').onchange = updateAgentPromptPreview;

    window.selectAgentProfile = function(name) {
      document.getElementById('ag-profile').value = name;
      updateAgentPromptPreview();
      document.getElementById('ag-prompt').focus();
    };

    window.filterBoardByAgent = function(profLower) {
      document.querySelector('[data-tab="view-board"]').click();
      initFilters({ assigned_to_profile: profLower });
      r();
    };

    document.getElementById('btn-dispatch-agent').onclick = async () => {
      const profile = document.getElementById('ag-profile').value;
      const item_id = document.getElementById('ag-item-id').value ? Number(document.getElementById('ag-item-id').value) : null;
      const prompt = document.getElementById('ag-prompt').value.trim();
      if (!prompt) return alert('Vui lòng nhập nội dung chỉ thị cho Agent!');
      const res = await fetch('/api/agents/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile, item_id, prompt })
      });
      const out = await res.json();
      if (out.job_id) {
        activeJobId = out.job_id;
        document.querySelector('[data-tab="view-automation"]').click();
        await pollJobs();
      }
    };

    initFilters();
    r();

    // Realtime Polling
    let lastHash = '';
    let uiVer = '';
    async function poll(force = false) {
      try {
        const origin = window.location.origin.includes('http') ? window.location.origin : 'http://127.0.0.1:8765';
        const res = await fetch(origin + '/api/work-items?t=' + Date.now() + (force ? '&force=1' : ''));
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const serverVer = res.headers.get('X-UI-Version') || '';
        if (uiVer && serverVer && uiVer !== serverVer) {
          window.location.reload();
          return;
        }
        if (serverVer) uiVer = serverVer;
        const text = await res.text();
        if (text !== lastHash || force) {
          lastHash = text;
          const data = JSON.parse(text);
          if (Array.isArray(data)) {
            const cur = { q: document.getElementById('q')?.value || '' };
            f.querySelectorAll('select').forEach(s => { cur[s.dataset.k] = s.value; });
            D = data.map(x => x.source === 'bot' ? { ...x, source: 'local' } : x);
            initFilters(cur);
            r();
          }
        }
        const st = document.getElementById('st');
        if (st) {
          st.className = 'badge live';
          st.textContent = 'Live';
        }
        if (document.getElementById('view-automation').classList.contains('active')) {
          pollJobs();
        }
      } catch (e) {
        const st = document.getElementById('st');
        if (st) {
          st.className = 'badge err';
          st.textContent = 'Offline';
        }
      }
    }
    setInterval(poll, 2500);
  </script>
</body>
</html>"""


def generate_html(out_path="/tmp/harness_dashboard.html", wait_if_empty=True):
    rows, json_str = get_cached_rows(wait_if_empty=wait_if_empty)
    clean_data = json_str.replace("</", "<\\/")
    content = HTML_TEMPLATE.replace("__DATA__", clean_data)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return len(rows)


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def _safe_write(self, body: bytes):
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self._safe_write(body)

    def _serve_file(self, file_path: Path):
        try:
            content_type = _get_content_type(file_path)
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(data)))
            path_str = str(file_path)
            if "/_astro/" in path_str or "/assets/" in path_str:
                self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            elif file_path.suffix.lower() in (".html", ""):
                self.send_header("Cache-Control", "no-cache")
            else:
                self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self._safe_write(data)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def _serve_inline_template(self):
        rows, json_str = get_cached_rows()
        clean_data = json_str.replace("</", "<\\/")
        html = HTML_TEMPLATE.replace("__DATA__", clean_data)
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self._safe_write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        url_path = parsed.path
        qs = parse_qs(parsed.query)

        if url_path in ["/api/work-items", "/harness_data.json"]:
            force = "force" in qs
            _, json_str = get_cached_rows(force=force)
            body = json_str.encode("utf-8")
            ui_ver = str(len(HTML_TEMPLATE))
            try:
                if INDEX_FILE.is_file():
                    st = INDEX_FILE.stat()
                    ui_ver = f"{len(HTML_TEMPLATE)}-{int(st.st_mtime)}-{st.st_size}"
            except Exception:
                pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Expose-Headers", "X-UI-Version")
            self.send_header("X-UI-Version", ui_ver)
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self._safe_write(body)
            return

        if url_path == "/api/env":
            self._send_json({
                "ok": True,
                "env_loaded": (BASE_DIR / ".env").is_file() or (BASE_DIR / "harness-ui" / ".env").is_file(),
                "WORKSPACE_ROOT": str(BASE_DIR),
                "HARNESS_BACKEND": os.environ.get("HARNESS_BACKEND", "floci"),
                "FLOCI_ENDPOINT": os.environ.get("FLOCI_ENDPOINT", "http://100.124.36.46:14566"),
                "FLOCI_S3_BUCKET": os.environ.get("FLOCI_S3_BUCKET", "harness-data"),
                "HARNESS_MODEL": os.environ.get("HARNESS_MODEL", "gemini-3.7-medium"),
                "AWS_REGION": os.environ.get("AWS_REGION", "us-east-1"),
                "HARNESS_LOG_LEVEL": os.environ.get("HARNESS_LOG_LEVEL", "info"),
                "PUBLIC_API_BASE_URL": os.environ.get("PUBLIC_API_BASE_URL", "http://127.0.0.1:8765"),
                "PUBLIC_PASEO_DAEMON_URL": os.environ.get("PUBLIC_PASEO_DAEMON_URL", "http://127.0.0.1:6767"),
            })
            return

        if url_path == "/api/doctor":
            force = "force" in qs
            report = get_doctor_report(force=force)
            self._send_json(report)
            return

        if url_path == "/api/nodes":
            with _NODES_LOCK:
                nodes_snapshot = [dict(n) for n in _CONNECTED_NODES]
            self._send_json({"nodes": nodes_snapshot, "current_workspace": str(BASE_DIR)})
            return

        if url_path == "/api/agents":
            self._send_json({"profiles": get_slpc_profiles()})
            return

        if url_path == "/api/source-files":
            self._send_json(scan_workspace_Targets())
            return

        if url_path == "/api/automation/jobs":
            with _JOBS_LOCK:
                snapshot = [dict(j) for j in _JOBS]
            self._send_json(snapshot)
            return

        if url_path == "/api/progress":
            try:
                state = agent_progress.load_state()
                payload = dict(state)

                # Check optional thread query parameter
                thread_param = qs.get("thread", [None])[0]
                if thread_param:
                    if "\x00" in thread_param:
                        self._send_json({"error": "Invalid thread parameter: embedded null byte"}, status=400)
                        return
                    target = None
                    try:
                        cand = Path(thread_param).expanduser()
                        if cand.is_file():
                            target = cand
                    except (ValueError, OSError):
                        pass
                    if not target or not target.is_file():
                        for _, candidate in agent_progress._collect_all_thread_files():
                            if candidate.stem.startswith(thread_param) or thread_param in candidate.name:
                                target = candidate
                                break
                    if not target or not target.is_file():
                        self._send_json({"error": f"Thread not found: {thread_param}"}, status=404)
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

                        if not isinstance(obj, dict):
                            continue

                        msg_val = obj.get("message")
                        msg_dict = msg_val if isinstance(msg_val, dict) else {}

                        role = (
                            obj.get("type")
                            or obj.get("role")
                            or msg_dict.get("role")
                            or msg_dict.get("type")
                        )

                        if isinstance(msg_val, str):
                            content = msg_val
                        else:
                            content = (
                                msg_dict.get("content")
                                or msg_dict.get("text")
                                or obj.get("content")
                                or obj.get("text")
                            )

                        text_parts = []
                        if isinstance(content, str):
                            text_parts.append(content)
                        elif isinstance(content, list):
                            for part in content:
                                if isinstance(part, dict) and part.get("type") in ("text", "input_text", "output_text"):
                                    text_parts.append(str(part.get("text", "")))
                                elif isinstance(part, str):
                                    text_parts.append(part)
                        elif isinstance(content, dict):
                            if "text" in content:
                                text_parts.append(str(content["text"]))

                        merged = "\n".join(t for t in text_parts if t).strip()
                        if merged:
                            messages.append({"role": role, "text": merged[:1200]})

                    limit_msg_raw = qs.get("max_messages", qs.get("limit", [40]))[0]
                    try:
                        limit_msg = int(limit_msg_raw)
                    except ValueError:
                        limit_msg = 40
                    turn_messages = messages[-limit_msg:] if limit_msg > 0 else messages

                    thread_detail = {
                        "thread_id": target.stem,
                        "path": str(target),
                        "total_extracted_messages": len(messages),
                        "messages": turn_messages,
                    }
                    payload["thread_detail"] = thread_detail
                    payload["messages"] = turn_messages
                    payload["total_extracted_messages"] = len(messages)
                    payload["thread_id"] = target.stem
                    payload["thread_path"] = str(target)

                # Collect session threads
                limit_threads_raw = qs.get("limit_threads", qs.get("limit", [50]))[0] if not thread_param else 50
                try:
                    limit_threads = int(limit_threads_raw)
                except ValueError:
                    limit_threads = 50

                thread_list = []
                for source, p in agent_progress._collect_all_thread_files()[:limit_threads]:
                    try:
                        st = p.stat()
                        thread_list.append({
                            "thread_id": p.stem,
                            "source": source,
                            "role": source.replace("codex-", "").replace("paseo-", ""),
                            "path": str(p),
                            "size_kb": round(st.st_size / 1024, 1),
                            "mtime": st.st_mtime,
                            "updated_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                    except Exception:
                        continue
                payload["threads"] = thread_list
                payload["markdown_path"] = "docs/AGENT_PROGRESS.md"
                self._send_json(payload)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        # Static file serving: / or /index.html serves dist/index.html if exists, else falls back to HTML_TEMPLATE
        if url_path in ["/", "/index.html"]:
            if INDEX_FILE.is_file():
                self._serve_file(INDEX_FILE)
                return
            self._serve_inline_template()
            return

        # Explicit legacy dashboard URL always serves HTML_TEMPLATE
        if url_path == "/harness_dashboard.html":
            self._serve_inline_template()
            return

        # Serve static assets from harness-ui/dist/
        if DIST_DIR.is_dir():
            clean_path = unquote(url_path.lstrip("/"))
            if "\x00" in clean_path:
                self.send_error(400, "Bad Request")
                return

            try:
                target_path = (DIST_DIR / clean_path).resolve()
                is_safe = target_path.is_relative_to(DIST_DIR)
            except (AttributeError, ValueError, OSError):
                is_safe = False

            if is_safe:
                if target_path.is_file():
                    self._serve_file(target_path)
                    return
                if target_path.is_dir() and (target_path / "index.html").is_file():
                    self._serve_file(target_path / "index.html")
                    return
                if target_path.with_suffix(".html").is_file():
                    self._serve_file(target_path.with_suffix(".html"))
                    return
                if not Path(clean_path).suffix and INDEX_FILE.is_file():
                    self._serve_file(INDEX_FILE)
                    return
            else:
                self.send_error(403, "Forbidden")
                return

        self.send_error(404, "Not Found")

    def do_POST(self):
        url_path = self.path.split("?")[0]
        try:
            body = self._read_json_body()
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return

        if url_path == "/api/nodes/connect":
            try:
                raw_url = body.get("url") or body.get("link") or ""
                if not raw_url:
                    self._send_json({"error": "Missing node URL"}, status=400)
                    return
                node_info = probe_and_register_node(raw_url, custom_name=body.get("name", ""))
                with _NODES_LOCK:
                    all_nodes = [dict(n) for n in _CONNECTED_NODES]
                self._send_json({"ok": True, "node": node_info, "nodes": all_nodes})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if url_path == "/api/automation/resolve-link":
            try:
                res = resolve_link_and_generate_tests(body)
                self._send_json(res)
            except ValueError as ve:
                self._send_json({"error": str(ve)}, status=400)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if url_path == "/api/work-items/add":
            try:
                try:
                    mgr = HarnessManager()
                    res = mgr.add_work_item(
                        wi_type=body.get("type", "Task"),
                        title=body.get("title", ""),
                        description=body.get("description", ""),
                        priority=body.get("priority", "P2"),
                        assigned_to=body.get("assigned_to"),
                        parent_id=body.get("parent_id"),
                        acceptance_criteria=body.get("acceptance_criteria"),
                        source="bot",
                        created_by_profile=body.get("created_by_profile", "supervisor"),
                        assigned_to_profile=body.get("assigned_to_profile", "peer"),
                    )
                    get_cached_rows(force=True)
                except Exception as ddb_err:
                    if isinstance(ddb_err, ValueError):
                        raise
                    rows, _ = get_cached_rows()
                    next_id = max([int(r.get("id") or 0) for r in rows] + [161200]) + 1
                    now_iso = datetime.now().isoformat()
                    res = {
                        "id": next_id,
                        "type": body.get("type", "Task"),
                        "title": body.get("title", ""),
                        "description": body.get("description", ""),
                        "acceptance_criteria": body.get("acceptance_criteria", ""),
                        "state": "New",
                        "priority": body.get("priority", "P2"),
                        "assigned_to": body.get("assigned_to"),
                        "assigned_to_profile": body.get("assigned_to_profile", "peer"),
                        "created_by_profile": body.get("created_by_profile", "supervisor"),
                        "parent_item_id": body.get("parent_id"),
                        "iteration_path": "Paseo\\SLPC",
                        "source": "local",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                    }
                    with _LOCK:
                        save_local_cache([res] + rows)
                if body.get("dispatch") and body.get("assigned_to_profile"):
                    prof = body["assigned_to_profile"]
                    item_id = res.get("id")
                    cmd = f"python3 tools/call_agent.py --profile {json.dumps(prof)} --item-id {item_id} --prompt {json.dumps(body.get('title', ''))}"
                    start_background_job("agent", f"Dispatch {prof} -> #{item_id}", cmd, str(BASE_DIR), item_id=item_id)
                self._send_json(res)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if url_path == "/api/work-items/update":
            try:
                target_id = int(body["id"])
                target_state = body.get("state")
                res = None
                now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    mgr = HarnessManager()
                    existing = mgr.get_work_item(target_id)
                    if existing:
                        res = mgr.update_state(
                            item_id=target_id,
                            target_state=target_state or existing.get("state", "New"),
                            assigned_to=body.get("assigned_to"),
                            assigned_to_profile=body.get("assigned_to_profile"),
                        )
                        if body.get("description") is not None or body.get("acceptance_criteria") is not None:
                            full_item = mgr.get_work_item(target_id) or dict(existing)
                            full_item["state"] = target_state or full_item.get("state", "New")
                            if body.get("description") is not None:
                                full_item["description"] = body["description"]
                            if body.get("acceptance_criteria") is not None:
                                full_item["acceptance_criteria"] = body["acceptance_criteria"]
                            full_item["updated_at"] = now_iso
                            FlociHarnessDB().put_work_item(full_item)
                            res = full_item
                        get_cached_rows(force=True)
                except Exception:
                    res = None

                # Always update in-memory cache synchronously so the next poll sees it in 0ms
                rows, _ = get_cached_rows()
                for r in rows:
                    if int(r.get("id") or 0) == target_id:
                        if target_state:
                            r["state"] = target_state
                        if body.get("assigned_to") is not None:
                            r["assigned_to"] = body["assigned_to"]
                        if body.get("assigned_to_profile") is not None:
                            r["assigned_to_profile"] = body["assigned_to_profile"]
                        if body.get("description") is not None:
                            r["description"] = body["description"]
                        if body.get("acceptance_criteria") is not None:
                            r["acceptance_criteria"] = body["acceptance_criteria"]
                        r["updated_at"] = now_iso
                        if not res:
                            res = r
                            try:
                                FlociHarnessDB().put_work_item(dict(r))
                            except Exception:
                                pass
                        break
                if not res:
                    raise ValueError(f"Work item #{target_id} not found")
                with _LOCK:
                    save_local_cache(rows)
                self._send_json(res)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if url_path == "/api/agents/call":
            profile = body.get("profile", "QC")
            prompt = body.get("prompt", "Check assigned work items on Harness DB")
            item_id = body.get("item_id")
            cmd = f"python3 tools/call_agent.py --profile {json.dumps(profile)} --prompt {json.dumps(prompt)}"
            if item_id:
                cmd += f" --item-id {int(item_id)}"
            job = start_background_job("agent", f"Agent {profile}" + (f" (#{item_id})" if item_id else ""), cmd, str(BASE_DIR), item_id=item_id)
            self._send_json({"status": "dispatched", "job_id": job["id"]})
            return

        if url_path == "/api/automation/run":
            title = body.get("title", "Automation Job")
            command = body.get("command", "")
            cwd = body.get("cwd") or str(BASE_DIR)
            if not command:
                self._send_json({"error": "Missing command"}, status=400)
                return
            job = start_background_job(body.get("kind", "test"), title, command, cwd=cwd, item_id=body.get("item_id"), auto_verify_item=bool(body.get("auto_verify")))
            self._send_json(job)
            return

        if url_path == "/api/automation/qc-generate":
            try:
                raw_src = body.get("source", "")
                src_path = Path(raw_src) if os.path.isabs(raw_src) else (BASE_DIR / raw_src)
                if not src_path.exists():
                    # If user pasted a link into the source input, delegate to resolve_link_and_generate_tests!
                    if raw_src.startswith(("http://", "https://", "paseo://", "#")):
                        res = resolve_link_and_generate_tests({"link": raw_src, **body})
                        self._send_json(res)
                        return
                    self._send_json({"error": f"Source file not found: {src_path}"}, status=400)
                    return

                spec_text = ""
                raw_spec = body.get("spec", "")
                if raw_spec:
                    spec_cand = Path(raw_spec) if os.path.isabs(raw_spec) else (BASE_DIR / raw_spec)
                    if spec_cand.exists() and spec_cand.is_file():
                        spec_text = spec_cand.read_text(encoding="utf-8", errors="replace")
                    else:
                        spec_text = raw_spec

                task_id = body.get("task_id")
                if task_id and not spec_text:
                    item = HarnessManager().get_work_item(int(task_id))
                    if item:
                        spec_text = f"# {item.get('title', '')}\n{item.get('description', '')}\n## Acceptance Criteria\n{item.get('acceptance_criteria', '')}"

                code_ctx = qc_gen.analyze_source_file(src_path)
                analysis = qc_gen.parse_spec_content(spec_text, module_hint=code_ctx.get("module_name", src_path.stem))
                tp_set = qc_gen.generate_test_points(analysis, code_ctx)
                design_plan = qc_gen.build_test_design_plan(tp_set["test_points"])
                test_cases = qc_gen.generate_test_cases(analysis, tp_set, design_plan, code_ctx)
                cov_report = qc_gen.build_coverage_report(analysis, test_cases, tp_set, design_plan, code_ctx)

                out_spec_str = body.get("out_spec", "").strip()
                if (not out_spec_str or out_spec_str == "/tmp/generated.spec.ts") and body.get("write_alongside") and src_path.is_relative_to(BASE_DIR):
                    out_spec_path = src_path.with_name(f"{src_path.stem}.generated.spec.ts")
                else:
                    out_spec_str = out_spec_str or f"/tmp/{src_path.stem}.generated.spec.ts"
                    out_spec_path = Path(out_spec_str) if os.path.isabs(out_spec_str) else (BASE_DIR / out_spec_str)
                out_spec_path.parent.mkdir(parents=True, exist_ok=True)
                spec_code = qc_gen.render_unit_test_file(code_ctx, test_cases, out_spec_path)
                out_spec_path.write_text(spec_code, encoding="utf-8")

                synced = []
                if body.get("sync_harness"):
                    synced = qc_gen.sync_cases_to_harness(test_cases, parent_task_id=int(task_id) if task_id else None)
                    get_cached_rows(force=True)

                job_id = None
                if body.get("run_test"):
                    fw = code_ctx.get("framework", "jest")
                    cmd = f"npx vitest run {out_spec_path}" if fw == "vitest" else f"npx jest {out_spec_path}"
                    job = start_background_job("test", f"Unit Test: {src_path.name}", cmd, cwd=str(src_path.parent))
                    job_id = job["id"]

                self._send_json({
                    "coverage_report": cov_report,
                    "spec_code": spec_code,
                    "out_spec": str(out_spec_path),
                    "synced_count": len(synced),
                    "job_id": job_id,
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if parsed.path == "/api/doctor/heal":
            try:
                if "auto_heal" in body:
                    _DOCTOR_STATE["auto_heal"] = bool(body["auto_heal"])
                report = get_doctor_report(force=True, force_heal=True)
                get_cached_rows(force=True)
                self._send_json(report)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        pass


_DOCTOR_LOCK = threading.Lock()
_DOCTOR_STATE = {
    "report": None,
    "last_check": 0.0,
    "auto_heal": True,
    "check_count": 0,
}


def get_doctor_report(force: bool = False, force_heal: bool = False) -> dict:
    now = time.time()
    if not force and _DOCTOR_STATE["report"] is not None and (now - _DOCTOR_STATE["last_check"] < 6.0):
        return _DOCTOR_STATE["report"]
    with _DOCTOR_LOCK:
        heal_flag = True if force_heal else bool(_DOCTOR_STATE.get("auto_heal", True))
        rep = harness_doctor.run_doctor(auto_heal=heal_flag, in_process=True)
        _DOCTOR_STATE["check_count"] = int(_DOCTOR_STATE.get("check_count", 0)) + 1
        rep["check_count"] = _DOCTOR_STATE["check_count"]
        rep["auto_heal_enabled"] = bool(_DOCTOR_STATE.get("auto_heal", True))
        _DOCTOR_STATE["report"] = rep
        _DOCTOR_STATE["last_check"] = time.time()
        return rep


def _bg_doctor_loop():
    while True:
        try:
            get_doctor_report(force=True)
        except Exception:
            pass
        time.sleep(8.0)


def _stop_existing_dashboard_server(port=None):
    skip_pids = {os.getpid()}
    try:
        out = subprocess.check_output(["pgrep", "-f", "harness_dashboard.py.*--serve"], text=True)
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            pid = int(line)
            if pid in skip_pids:
                continue
            if port is not None:
                try:
                    cmdline_file = Path(f"/proc/{pid}/cmdline")
                    if cmdline_file.exists():
                        raw_args = cmdline_file.read_bytes().split(b"\x00")
                        args = [a.decode("utf-8", errors="ignore") for a in raw_args if a]
                        if "--port" in args:
                            idx = args.index("--port")
                            proc_port = args[idx + 1] if idx + 1 < len(args) else "8765"
                        else:
                            proc_port = "8765"
                        if proc_port != str(port):
                            continue
                except Exception:
                    pass
            try:
                os.kill(pid, 9)
            except OSError:
                pass
        time.sleep(0.3)
    except Exception:
        pass


def _bg_floci_sync_loop(out_path="/tmp/harness_dashboard.html"):
    while True:
        try:
            rows, json_str = sync_from_floci()
            if rows:
                clean_data = json_str.replace("</", "<\\/")
                content = HTML_TEMPLATE.replace("__DATA__", clean_data)
                with open(out_path, "w", encoding="utf-8") as fh:
                    fh.write(content)
        except Exception:
            pass
        time.sleep(3.0)


def _is_port_healthy(port: int) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/work-items?force=1")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def run_server(port=8765, host="0.0.0.0", out_path="/tmp/harness_dashboard.html"):
    _stop_existing_dashboard_server(port=port)
    threading.Thread(target=_bg_floci_sync_loop, args=(out_path,), daemon=True).start()
    threading.Thread(target=_bg_doctor_loop, daemon=True).start()
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    server_address = (host, port)
    httpd = http.server.ThreadingHTTPServer(server_address, DashboardHandler)
    print(f"Harness Realtime Server listening at http://127.0.0.1:{port}/harness_dashboard.html", flush=True)
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Harness Dashboard Realtime Server & Static Generator")
    parser.add_argument("--serve", action="store_true", help="Chạy foreground HTTP server trên cổng 8765")
    parser.add_argument("--daemon", action="store_true", help="Khởi động HTTP server chạy ngầm (background daemon) và thoát ngay")
    parser.add_argument("--restart", action="store_true", help="Buộc khởi động lại daemon đang chạy")
    parser.add_argument("--port", type=int, default=8765, help="Cổng server HTTP (default 8765)")
    parser.add_argument("out", nargs="?", default="/tmp/harness_dashboard.html", help="Đường dẫn file html output")
    args = parser.parse_args()

    if args.daemon:
        generate_html(args.out, wait_if_empty=False)
        if not args.restart and _is_port_healthy(args.port):
            print(f"Existing dashboard server is healthy at http://127.0.0.1:{args.port}/harness_dashboard.html (triggered force sync)", flush=True)
            return
        if args.port == 8765:
            try:
                unit_path = Path.home() / ".config" / "systemd" / "user" / "paseo-harness-dashboard.service"
                if unit_path.is_file():
                    subprocess.run(["systemctl", "--user", "restart", "paseo-harness-dashboard.service"], check=True, timeout=5)
                    time.sleep(0.4)
                    if _is_port_healthy(args.port):
                        print(f"Started systemd user service paseo-harness-dashboard.service on port {args.port}", flush=True)
                        return
            except Exception:
                pass
        _stop_existing_dashboard_server(port=args.port)
        log_fh = open("/tmp/harness_dashboard_server.log", "w", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--serve", "--port", str(args.port)],
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        time.sleep(0.5)
        print(f"Started background server PID={proc.pid} at http://127.0.0.1:{args.port}/harness_dashboard.html (syncing Floci DB in background...)", flush=True)
        return

    if args.serve:
        generate_html(args.out, wait_if_empty=False)
        run_server(port=args.port, out_path=args.out)
        return

    count = generate_html(args.out, wait_if_empty=True)
    try:
        _is_port_healthy(args.port)
    except Exception:
        pass
    print(f"{count} items -> {args.out}", flush=True)


if __name__ == "__main__":
    main()


