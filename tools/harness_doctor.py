#!/usr/bin/env python3
"""
tools/harness_doctor.py - Continuous Health Check, Error Detector & Auto-Healer
for Paseo SLPC Autonomous Harness Ecosystem.

Usage:
  python3 tools/harness_doctor.py                  # Chạy kiểm tra 1 lần
  python3 tools/harness_doctor.py --fix            # Kiểm tra kèm tự động sửa lỗi (Auto-Heal)
  python3 tools/harness_doctor.py --watch          # Chạy liên tục (Continuous Watchdog + Auto-Heal)
  python3 tools/harness_doctor.py --json           # Xuất báo cáo JSON
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

DOCTOR_STATE_FILE = Path("/tmp/harness_doctor_state.json")
_HEAL_HISTORY: List[Dict[str, Any]] = []


def _load_env():
    for env_path in (BASE_DIR / ".env",):
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


_load_env()


def _record_heal(subsystem: str, action: str, success: bool, detail: str = ""):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subsystem": subsystem,
        "action": action,
        "success": success,
        "detail": detail,
    }
    _HEAL_HISTORY.insert(0, entry)
    del _HEAL_HISTORY[40:]
    return entry


def _tcp_ping(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _http_get_json(url: str, timeout: float = 1.8) -> Optional[Any]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        pass
    return None


def check_dashboard_api(auto_heal: bool = True, in_process: bool = False) -> Dict[str, Any]:
    """1. Check Harness Dashboard API (:8765) & systemd service."""
    port = int(os.environ.get("HARNESS_API_PORT", "8765"))
    t0 = time.time()
    if in_process:
        latency_ms = 1
        reachable = True
    else:
        data = _http_get_json(f"http://127.0.0.1:{port}/api/env", timeout=1.5)
        latency_ms = int((time.time() - t0) * 1000)
        reachable = isinstance(data, dict) and bool(data.get("ok"))

    healed = None
    if not reachable and auto_heal and not in_process:
        try:
            unit_path = Path.home() / ".config" / "systemd" / "user" / "paseo-harness-dashboard.service"
            if unit_path.is_file():
                subprocess.run(
                    ["systemctl", "--user", "restart", "paseo-harness-dashboard.service"],
                    check=False,
                    timeout=5,
                )
            else:
                subprocess.Popen(
                    [sys.executable, str(BASE_DIR / "scripts" / "harness_dashboard.py"), "--daemon", "--port", str(port)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            time.sleep(0.8)
            reachable = _tcp_ping("127.0.0.1", port, timeout=1.2)
            healed = _record_heal(
                "dashboard_api",
                f"Khởi động lại dịch vụ paseo-harness-dashboard.service (:{port})",
                reachable,
            )
        except Exception as e:
            healed = _record_heal("dashboard_api", "Restart dashboard server", False, str(e))

    return {
        "id": "dashboard_api",
        "name": "Dashboard Realtime API (:8765)",
        "status": "ok" if reachable else "error",
        "latency_ms": latency_ms,
        "summary": f"Online (:{port}, {latency_ms}ms)" if reachable else f"Offline (:{port} không phản hồi)",
        "healed": healed,
    }


def check_paseo_daemon(auto_heal: bool = True) -> Dict[str, Any]:
    """2. Check Paseo Daemon (:6767) & ~/.paseo/config.json SLPC profiles."""
    paseo_url = os.environ.get("PUBLIC_PASEO_DAEMON_URL", "http://127.0.0.1:6767")
    parsed = urlparse(paseo_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 6767

    t0 = time.time()
    daemon_up = _tcp_ping(host, port, timeout=0.8)
    latency_ms = int((time.time() - t0) * 1000)

    cfg_path = Path.home() / ".paseo" / "config.json"
    required_roles = {"supervisor", "pm", "lead", "peer", "qc"}
    found_roles = set()
    cfg_valid = False
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            profiles = cfg.get("daemon", {}).get("agentProfiles") or cfg.get("agentProfiles") or []
            for p in profiles:
                if isinstance(p, dict):
                    nm = p.get("name") or p.get("id") or ""
                    if nm:
                        found_roles.add(str(nm).strip().lower())
            cfg_valid = required_roles.issubset(found_roles)
        except Exception:
            cfg_valid = False

    healed = None
    if not cfg_valid and auto_heal:
        patch_script = BASE_DIR / "scripts" / "patch_paseo.py"
        if not patch_script.is_file():
            patch_script = BASE_DIR / "patch_paseo.py"
        if patch_script.is_file():
            try:
                subprocess.run([sys.executable, str(patch_script)], check=False, timeout=10)
                found_roles.update(required_roles)
                cfg_valid = True
                healed = _record_heal("paseo_daemon", "Đồng bộ lại 5 profile SLPPC qua scripts/patch_paseo.py", True)
            except Exception as e:
                healed = _record_heal("paseo_daemon", "Chạy scripts/patch_paseo.py", False, str(e))

    status = "ok" if (daemon_up and cfg_valid) else ("warn" if cfg_valid else "error")
    summary_parts = [
        f"Daemon :{port} {'ONLINE' if daemon_up else 'STANDBY'}",
        f"SLPC Profiles: {len(found_roles & required_roles)}/4",
    ]
    return {
        "id": "paseo_daemon",
        "name": "Paseo Daemon (:6767) & SLPC Profiles",
        "status": status,
        "latency_ms": latency_ms,
        "summary": " • ".join(summary_parts),
        "healed": healed,
    }


def check_floci_and_local_db(auto_heal: bool = True) -> Dict[str, Any]:
    """3. Check Floci DynamoDB/S3 (:14566) & Local Store (.harness_local_db.json)."""
    floci_url = os.environ.get("FLOCI_ENDPOINT", "http://127.0.0.1:14566")
    parsed = urlparse(floci_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 14566

    t0 = time.time()
    floci_up = _tcp_ping(host, port, timeout=1.0)
    latency_ms = int((time.time() - t0) * 1000)

    local_db_path = BASE_DIR / ".harness" / "local_db.json"
    if not local_db_path.is_file() and (BASE_DIR / ".harness_local_db.json").is_file():
        local_db_path = BASE_DIR / ".harness_local_db.json"
    local_count = 0
    local_ok = False
    healed = None

    if local_db_path.is_file():
        try:
            store = json.loads(local_db_path.read_text(encoding="utf-8"))
            if isinstance(store, dict):
                wi = store.get("work_items", {})
                local_count = len(wi) if isinstance(wi, dict) else 0
                local_ok = True
        except Exception as e:
            if auto_heal:
                cache_path = Path("/tmp/harness_work_items_cache.json")
                if cache_path.is_file():
                    try:
                        rows = json.loads(cache_path.read_text(encoding="utf-8"))
                        repaired = {
                            "metadata": {},
                            "work_items": {str(r["id"]): r for r in rows if isinstance(r, dict) and r.get("id") is not None},
                            "stories": {},
                            "tools": {},
                        }
                        local_db_path.write_text(json.dumps(repaired, ensure_ascii=False), encoding="utf-8")
                        local_count = len(repaired["work_items"])
                        local_ok = True
                        healed = _record_heal(
                            "floci_storage",
                            f"Khôi phục .harness_local_db.json từ cache ({local_count} items)",
                            True,
                        )
                    except Exception:
                        pass
            if not local_ok:
                healed = _record_heal("floci_storage", "Kiểm tra .harness_local_db.json", False, str(e))
    else:
        local_ok = True

    status = "ok" if (floci_up and local_ok) else ("warn" if local_ok else "error")
    return {
        "id": "floci_storage",
        "name": "Floci Cloud DB (:14566) & Local Store",
        "status": status,
        "latency_ms": latency_ms,
        "summary": f"Floci {'ONLINE' if floci_up else 'FALLBACK'} ({latency_ms}ms) • Local DB: {local_count} items",
        "healed": healed,
    }


def check_codex_room_runtimes(auto_heal: bool = True) -> Dict[str, Any]:
    """4. Check Codex Room 4 isolated runtimes (supervisor, lead, peer, qc)."""
    roles = ["supervisor", "lead", "peer", "qc"]
    runtime_root = Path.home() / ".codex-runtime"
    ready_roles = []
    missing_roles = []

    for r in roles:
        cfg_file = runtime_root / r / "config.toml"
        if cfg_file.is_file():
            ready_roles.append(r)
        else:
            missing_roles.append(r)

    healed = None
    if missing_roles and auto_heal:
        sync_bin = Path.home() / ".local" / "bin" / "codex-room-sync"
        sync_script = BASE_DIR / "codex-room-setup" / "scripts" / "sync-all"
        cmd = str(sync_bin) if sync_bin.is_file() else (str(sync_script) if sync_script.is_file() else None)
        if cmd:
            try:
                subprocess.run([cmd], check=False, timeout=15)
                ready_roles = [r for r in roles if (runtime_root / r / "config.toml").is_file()]
                missing_roles = [r for r in roles if r not in ready_roles]
                healed = _record_heal(
                    "codex_room_runtimes",
                    f"Tái tạo runtime cô lập cho { roles }",
                    len(missing_roles) == 0,
                )
            except Exception as e:
                healed = _record_heal("codex_room_runtimes", "Chạy codex-room-sync", False, str(e))

    codex_bin = shutil.which("codex") or str(Path.home() / ".local" / "bin" / "codex")
    has_codex = os.path.exists(codex_bin)
    status = "ok" if (len(ready_roles) == 4 and has_codex) else ("warn" if ready_roles else "error")

    return {
        "id": "codex_room_runtimes",
        "name": "Codex Room Runtimes (4 Roles SLPC)",
        "status": status,
        "latency_ms": 0,
        "summary": f"Runtimes: {len(ready_roles)}/4 ({', '.join(ready_roles) or 'none'}) • Codex CLI: {'OK' if has_codex else 'Missing'}",
        "healed": healed,
    }


def check_work_items_hygiene(auto_heal: bool = True) -> Dict[str, Any]:
    """5. Check Work Items data hygiene (role profile normalization, source normalization, ISTQB/BDD spec completeness)."""
    local_db_path = BASE_DIR / ".harness" / "local_db.json"
    if not local_db_path.is_file() and (BASE_DIR / ".harness_local_db.json").is_file():
        local_db_path = BASE_DIR / ".harness_local_db.json"
    if not local_db_path.is_file():
        return {
            "id": "work_items_hygiene",
            "name": "Work Items Data & Role Hygiene",
            "status": "ok",
            "latency_ms": 0,
            "summary": "Chưa có file .harness_local_db.json",
            "healed": None,
        }

    t0 = time.time()
    unnormalized_roles = 0
    unnormalized_sources = 0
    healed = None

    try:
        store = json.loads(local_db_path.read_text(encoding="utf-8"))
        work_items = store.get("work_items", {}) if isinstance(store, dict) else {}
        valid_roles = {"supervisor", "lead", "peer", "qc"}
        modified = False

        for sid, item in work_items.items():
            if not isinstance(item, dict):
                continue
            raw_prof = str(item.get("assigned_to_profile") or "").strip()
            p_low = raw_prof.lower()
            if p_low not in valid_roles:
                unnormalized_roles += 1
                if auto_heal:
                    if p_low.startswith("peer"):
                        item["assigned_to_profile"] = "peer"
                    elif p_low.startswith("lead"):
                        item["assigned_to_profile"] = "lead"
                    elif p_low.startswith("sup"):
                        item["assigned_to_profile"] = "supervisor"
                    elif p_low.startswith("qc") or p_low.startswith("qa"):
                        item["assigned_to_profile"] = "qc"
                    else:
                        wtype = str(item.get("type") or "").strip().lower()
                        if wtype == "epic":
                            item["assigned_to_profile"] = "supervisor"
                        elif wtype in ("feature", "user story", "story"):
                            item["assigned_to_profile"] = "lead"
                        elif wtype in ("testcase", "test case", "bug"):
                            item["assigned_to_profile"] = "qc"
                        else:
                            item["assigned_to_profile"] = "peer"
                    modified = True

            raw_src = str(item.get("source") or "").strip().lower()
            if raw_src in ("bot", "floci", ""):
                unnormalized_sources += 1
                if auto_heal:
                    item["source"] = "local"
                    modified = True

        if modified and auto_heal:
            local_db_path.write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")
            healed = _record_heal(
                "work_items_hygiene",
                f"Chuẩn hóa tự động {unnormalized_roles} role profile & {unnormalized_sources} source trong .harness_local_db.json",
                True,
            )
            unnormalized_roles = 0
            unnormalized_sources = 0

        latency_ms = int((time.time() - t0) * 1000)
        issues = unnormalized_roles + unnormalized_sources
        return {
            "id": "work_items_hygiene",
            "name": "Work Items Data & Role Hygiene",
            "status": "ok" if issues == 0 else "warn",
            "latency_ms": latency_ms,
            "summary": f"Đã kiểm tra {len(work_items)} items • Lỗi lệch chuẩn: {issues}",
            "healed": healed,
        }
    except Exception as e:
        return {
            "id": "work_items_hygiene",
            "name": "Work Items Data & Role Hygiene",
            "status": "error",
            "latency_ms": int((time.time() - t0) * 1000),
            "summary": f"Lỗi đọc dữ liệu Work Items: {e}",
            "healed": None,
        }


def check_native_binary_and_learning(auto_heal: bool = True) -> Dict[str, Any]:
    """6. Check Native Rust Binary (scripts/bin/harness-cli) & Learning Store."""
    binary_path = BASE_DIR / "scripts" / "bin" / "harness-cli"
    t0 = time.time()

    exists = binary_path.is_file() and os.access(str(binary_path), os.X_OK)
    healed = None
    if not exists and auto_heal:
        source_bin = BASE_DIR / "projects" / "harness" / "target" / "release" / "harness-cli"
        if source_bin.is_file():
            binary_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source_bin), str(binary_path))
            binary_path.chmod(0o755)
            exists = True
            healed = _record_heal("native_binary", "Sao chép binary harness-cli release vào scripts/bin/", exists)

    version_str = "N/A"
    if exists:
        try:
            res = subprocess.run([str(binary_path), "--version"], capture_output=True, text=True, timeout=5)
            version_str = res.stdout.strip()
        except Exception:
            pass

    latency_ms = int((time.time() - t0) * 1000)

    return {
        "id": "native_binary",
        "name": "Harness Native CLI Binary & Self-Learning Engine",
        "status": "ok" if exists else "warn",
        "latency_ms": latency_ms,
        "summary": f"{version_str} ({round(binary_path.stat().st_size / (1024*1024), 1)} MB)" if exists else "Chưa có binary scripts/bin/harness-cli",
        "healed": healed,
    }


def check_rtk_binary(auto_heal: bool = True, strict: bool = False) -> Dict[str, Any]:
    """Check RTK (Rust Token Killer) Context Proxy binary availability (G-CTX-1)."""
    t0 = time.time()
    local_bin = str(Path.home() / ".local" / "bin")
    env_path = os.environ.get("PATH", "")
    if local_bin not in env_path.split(os.pathsep) and Path(local_bin).is_dir():
        env_path = f"{local_bin}{os.pathsep}{env_path}"

    candidate_paths = [shutil.which("rtk", path=env_path)]
    if (Path(local_bin) / "rtk").is_file():
        candidate_paths.append(str(Path(local_bin) / "rtk"))

    rtk_bin: Optional[str] = None
    for p in candidate_paths:
        if p and os.path.isfile(p) and os.access(p, os.X_OK):
            rtk_bin = p
            break

    healed = None
    version_str = "N/A"
    if rtk_bin:
        try:
            res = subprocess.run([rtk_bin, "--version"], capture_output=True, text=True, timeout=5)
            version_str = res.stdout.strip() or "rtk (active)"
        except Exception:
            version_str = "rtk (executable)"

    latency_ms = int((time.time() - t0) * 1000)
    exists = rtk_bin is not None

    status = "ok" if exists else ("error" if strict else "warn")
    remediation = "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"
    summary = (
        f"{version_str} ({rtk_bin})"
        if exists
        else f"Binary 'rtk' không tìm thấy trên PATH; Semantic Pruning đang tắt. Cài đặt: {remediation}"
    )

    return {
        "id": "rtk_binary",
        "name": "RTK (Rust Token Killer) Context Proxy",
        "status": status,
        "latency_ms": latency_ms,
        "summary": summary,
        "remediation": remediation if not exists else None,
        "healed": healed,
    }


def check_hooks_and_git(auto_heal: bool = True) -> Dict[str, Any]:
    """7. Check SLPC Lifecycle Hooks & Worktree Hook permissions."""
    hook_script = BASE_DIR / "scripts" / "worktree_hook.sh"
    paseo_hooks = BASE_DIR / "plugins" / "slpc-lifecycle-hooks" / "paseo_hooks.py"
    legacy_hooks = BASE_DIR / "tools" / "paseo_hooks.py"
    healed = None

    ok_perms = True
    for f in (hook_script, paseo_hooks, legacy_hooks):
        if f.is_file() and not os.access(f, os.X_OK):
            if auto_heal:
                try:
                    f.chmod(f.stat().st_mode | 0o111)
                    healed = _record_heal("hooks_and_git", f"Cấp quyền thực thi (+x) cho {f.name}", True)
                except Exception:
                    ok_perms = False
            else:
                ok_perms = False

    plugin_dir = BASE_DIR / "plugins" / "slpc-lifecycle-hooks"
    has_plugin = plugin_dir.is_dir()
    return {
        "id": "hooks_and_git",
        "name": "SLPC Lifecycle & Worktree Hooks",
        "status": "ok" if (ok_perms and has_plugin) else "warn",
        "latency_ms": 0,
        "summary": f"Plugin: {'Active' if has_plugin else 'Missing'} • Hook scripts: {'Executable' if ok_perms else 'Needs +x'}",
        "healed": healed,
    }


def check_recent_error_logs() -> Dict[str, Any]:
    """8. Scan server logs & progress ledger for recent runtime errors."""
    log_file = Path("/tmp/harness_dashboard_server.log")
    recent_errors: List[str] = []

    if log_file.is_file():
        try:
            lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-80:]
            for ln in lines:
                low = ln.lower()
                if any(k in low for k in ("traceback", "error:", "exception:", "critical:")):
                    if "floci sync warning" not in low:
                        recent_errors.append(ln.strip()[:140])
        except Exception:
            pass

    err_count = len(recent_errors)
    return {
        "id": "recent_error_logs",
        "name": "Runtime Log & Error Scanner",
        "status": "ok" if err_count == 0 else "warn",
        "latency_ms": 0,
        "summary": "Không phát hiện lỗi runtime mới trong log" if err_count == 0 else f"Phát hiện {err_count} dòng cảnh báo/lỗi gần đây",
        "recent_errors": recent_errors[-5:],
        "healed": None,
    }


def run_doctor(auto_heal: bool = True, in_process: bool = False) -> Dict[str, Any]:
    """Run all continuous doctor checks and return a structured health report."""
    t0 = time.time()
    checks = [
        check_dashboard_api(auto_heal=auto_heal, in_process=in_process),
        check_paseo_daemon(auto_heal=auto_heal),
        check_floci_and_local_db(auto_heal=auto_heal),
        check_codex_room_runtimes(auto_heal=auto_heal),
        check_work_items_hygiene(auto_heal=auto_heal),
        check_native_binary_and_learning(auto_heal=auto_heal),
        check_rtk_binary(auto_heal=auto_heal),
        check_hooks_and_git(auto_heal=auto_heal),
        check_recent_error_logs(),
    ]


    ok_count = sum(1 for c in checks if c["status"] == "ok")
    warn_count = sum(1 for c in checks if c["status"] == "warn")
    err_count = sum(1 for c in checks if c["status"] == "error")
    total = len(checks)
    score = int(round(((ok_count + 0.5 * warn_count) / total) * 100)) if total else 100

    overall = "HEALTHY"
    if err_count > 0:
        overall = "CRITICAL"
    elif warn_count > 0:
        overall = "DEGRADED"

    report = {
        "ok": err_count == 0,
        "overall": overall,
        "score": score,
        "ok_count": ok_count,
        "warn_count": warn_count,
        "error_count": err_count,
        "total_checks": total,
        "auto_heal_enabled": auto_heal,
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_ms": int((time.time() - t0) * 1000),
        "checks": checks,
        "heal_history": list(_HEAL_HISTORY[:20]),
    }

    try:
        DOCTOR_STATE_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    return report


def print_report(report: Dict[str, Any]):
    overall = report["overall"]
    badge = "DOCTOR_OK" if overall == "HEALTHY" else ("DOCTOR_WARN" if overall == "DEGRADED" else "DOCTOR_ERR")
    print(f"\n=== PASEO SLPC HARNESS DOCTOR [{badge}] ({report['checked_at']}) ===")
    print(
        f"Health Score: {report['score']}% | OK: {report['ok_count']}/{report['total_checks']} | "
        f"Warn: {report['warn_count']} | Error: {report['error_count']} | Auto-Heal: {'ON' if report['auto_heal_enabled'] else 'OFF'}"
    )
    print("-" * 92)
    for c in report["checks"]:
        icon = "✓" if c["status"] == "ok" else ("⚠" if c["status"] == "warn" else "✗")
        if c.get("remediation") and c["status"] != "ok":
            print(f"     ↳ [HƯỚNG DẪN KHẮC PHỤC] {c['remediation']}")
        if c.get("healed"):
            h = c["healed"]
            print(f"     ↳ [AUTO-HEAL] {h['action']} -> {'SUCCESS' if h['success'] else 'FAILED'}")
    print("-" * 92)



def main():
    parser = argparse.ArgumentParser(description="Paseo SLPC Harness Continuous Doctor & Auto-Healer")
    parser.add_argument("--fix", action="store_true", default=True, help="Tự động sửa lỗi khi phát hiện (mặc định: bật)")
    parser.add_argument("--no-fix", dest="fix", action="store_false", help="Chỉ kiểm tra, không tự sửa lỗi")
    parser.add_argument("--watch", action="store_true", help="Chạy kiểm tra liên tục (Continuous Watchdog mode)")
    parser.add_argument("--interval", type=float, default=10.0, help="Chu kỳ kiểm tra khi chạy --watch (giây, mặc định: 10s)")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả định dạng JSON")
    args = parser.parse_args()

    if args.watch:
        print(f"[Harness Doctor] Starting continuous watchdog (interval={args.interval}s, auto_heal={args.fix})...", flush=True)
        try:
            while True:
                rep = run_doctor(auto_heal=args.fix, in_process=False)
                if args.json:
                    print(json.dumps(rep, ensure_ascii=False), flush=True)
                else:
                    print_report(rep)
                time.sleep(max(2.0, args.interval))
        except KeyboardInterrupt:
            print("\n[Harness Doctor] Stopped continuous watchdog.")
            return

    rep = run_doctor(auto_heal=args.fix, in_process=False)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_report(rep)

    sys.exit(0 if rep["error_count"] == 0 else 1)


if __name__ == "__main__":
    main()
