#!/usr/bin/env python3
"""
Unified Paseo Hook Tool for Paseo_Project (SLPC 4-Role Architecture).

Bridges all 3 Paseo Hook mechanisms:
1. Plugin Lifecycle Hooks (@getpaseo/plugin/server):
   - Workspace: before:workspace.create, workspace.created, workspace.archived
   - Agent: before:agent.create, before:agent.session_open, agent.created, agent.closed
   - Turn & Tool: agent.turn_started, agent.turn_ended, agent.permission_requested, agent.permission_resolved
   - Archive: agent.archived
2. Worktree Lifecycle Hooks (paseo.json worktree.setup / worktree.teardown):
   - pre-create, post-create, pre-destroy
3. CLI Agent Activity Hooks (paseo hooks <agent> <event>):
   - claude: UserPromptSubmit, Stop, StopFailure, SessionEnd, Notification
   - codex: UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop
   - opencode: session.status.busy, session.status.retry, session.status.idle, permission.asked, permission.replied
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOOKS_LOG_FILE = PROJECT_ROOT / ".harness_hooks.jsonl"
PASEO_HOME = Path(os.environ.get("PASEO_HOME", str(Path.home() / ".paseo")))
PASEO_CONFIG_FILE = PASEO_HOME / "config.json"
PLUGIN_DIR = PROJECT_ROOT / "plugins" / "slpc-lifecycle-hooks"
PLUGIN_ID = "slpc-lifecycle-hooks"
AGENT_PROGRESS_SCRIPT = PROJECT_ROOT / "tools" / "agent_progress.py"
PROFILE_RESEARCH_GEN_SCRIPT = PROJECT_ROOT / "tools" / "profile_research_gen.py"

SUPPORTED_CLI_AGENT_EVENTS: dict[str, list[str]] = {
    "claude": [
        "UserPromptSubmit",
        "Stop",
        "StopFailure",
        "SessionEnd",
        "Notification",
    ],
    "codex": [
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "PermissionRequest",
        "Stop",
    ],
    "opencode": [
        "session.status.busy",
        "session.status.retry",
        "session.status.idle",
        "permission.asked",
        "permission.replied",
    ],
}

ALL_PLUGIN_LIFECYCLE_HOOKS: list[str] = [
    "before:workspace.create",
    "workspace.created",
    "workspace.archived",
    "before:agent.create",
    "before:agent.session_open",
    "agent.created",
    "agent.turn_started",
    "agent.turn_ended",
    "agent.permission_requested",
    "agent.permission_resolved",
    "agent.archived",
]


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def redact_sensitive(obj: Any) -> Any:
    """Recursively redact sensitive environment maps or tokens before logging."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            key_lower = str(k).lower()
            if k == "env" and isinstance(v, dict):
                out[k] = {ek: "[redacted]" for ek in v.keys()}
            elif any(s in key_lower for s in ("token", "secret", "password", "api_key", "apikey", "authorization")):
                out[k] = "[redacted]"
            else:
                out[k] = redact_sensitive(v)
        return out
    if isinstance(obj, list):
        return [redact_sensitive(item) for item in obj]
    return obj


def append_hook_log(entry: dict[str, Any]) -> None:
    record = {
        "timestamp": utc_now_iso(),
        **redact_sensitive(entry),
    }
    HOOKS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HOOKS_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def find_paseo_bin() -> str:
    env_cli = os.environ.get("PASEO_HOOK_CLI")
    if env_cli and shutil.which(env_cli):
        return env_cli
    which_paseo = shutil.which("paseo")
    if which_paseo:
        return which_paseo
    for fallback in (
        Path.home() / ".local" / "bin" / "paseo",
        Path("/Applications/Paseo.app/Contents/Resources/bin/paseo"),
    ):
        if fallback.exists():
            return str(fallback)
    return "paseo"


def infer_slpc_role(text_or_title: str | None, provider: str | None = None) -> str | None:
    combined = f"{text_or_title or ''} {provider or ''}".lower()
    if "supervisor" in combined:
        return "Supervisor"
    if "qc" in combined or "verifier" in combined or "istqb" in combined:
        return "QC"
    if "lead" in combined:
        return "Lead"
    if "peer" in combined:
        return "Peer"
    return None


def log_to_agent_progress(agent: str, summary: str, done: str, next_step: str = "") -> None:
    if not AGENT_PROGRESS_SCRIPT.exists():
        return
    cmd = [
        sys.executable,
        str(AGENT_PROGRESS_SCRIPT),
        "log",
        "--agent",
        agent,
        "--summary",
        summary,
        "--done",
        done,
    ]
    if next_step:
        cmd.extend(["--next", next_step])
    try:
        subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False, capture_output=True, text=True, timeout=10)
    except Exception:
        pass


def trigger_research_gen(role: str, topic: str) -> dict[str, Any]:
    if not PROFILE_RESEARCH_GEN_SCRIPT.exists():
        return {"triggered": False, "reason": "profile_research_gen.py not found"}
    cmd = [
        sys.executable,
        str(PROFILE_RESEARCH_GEN_SCRIPT),
        "--profile",
        role,
        "--topic",
        topic[:200],
    ]
    try:
        proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False, capture_output=True, text=True, timeout=25)
        return {
            "triggered": True,
            "exit_code": proc.returncode,
            "role": role,
            "topic": topic[:200],
        }
    except Exception as exc:
        return {"triggered": False, "error": str(exc)}


def clean_closed_task_rooms(max_retain_per_room: int = 2) -> dict[str, Any]:
    """Inspect bmad/rooms/ and purge handoff files belonging to Closed work items on Harness DB.
    Also prunes excess timestamped files in each room to prevent context overlap.
    """
    bmad_rooms = PROJECT_ROOT / "bmad" / "rooms"
    if not bmad_rooms.is_dir():
        return {"cleaned_files": 0, "closed_tasks": []}

    removed_files: list[str] = []
    referenced_ids: set[int] = set()

    for f in bmad_rooms.rglob("*.md"):
        if f.name in ("README.md", "template-handoff.md"):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            matches = re.findall(r"#(\d{4,6})", content)
            for m in matches:
                referenced_ids.add(int(m))
        except Exception:
            pass

    closed_ids: set[int] = set()
    if referenced_ids:
        try:
            sys.path.insert(0, str(PROJECT_ROOT / "tools"))
            from harness_manager import HarnessManager
            mgr = HarnessManager()
            for tid in referenced_ids:
                try:
                    wi = mgr.floci_db.get_work_item(tid)
                    if wi and str(wi.get("state", "")).lower() in ("closed", "removed"):
                        closed_ids.add(tid)
                except Exception:
                    pass
        except Exception:
            pass

    if closed_ids:
        for f in bmad_rooms.rglob("*.md"):
            if f.name in ("README.md", "template-handoff.md"):
                continue
            try:
                content = f.read_text(encoding="utf-8")
                for cid in closed_ids:
                    if f"#{cid}" in content or f"Work Item: `#{cid}`" in content or f"handoff_{cid}_" in f.name:
                        f.unlink()
                        removed_files.append(str(f.relative_to(PROJECT_ROOT)))
                        break
            except Exception:
                pass

    for role_dir in ("supervisor", "lead", "peer", "qc"):
        r_path = bmad_rooms / role_dir
        if not r_path.is_dir():
            continue
        ts_files = sorted(
            [p for p in r_path.glob("handoff_*.md") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if len(ts_files) > max_retain_per_room:
            for old_file in ts_files[max_retain_per_room:]:
                try:
                    old_file.unlink()
                    removed_files.append(str(old_file.relative_to(PROJECT_ROOT)))
                except Exception:
                    pass

        if role_dir == "lead":
            rev_files = sorted(
                [p for p in r_path.glob("review_*.md") if p.is_file()],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if len(rev_files) > max_retain_per_room:
                for old_rev in rev_files[max_retain_per_room:]:
                    try:
                        old_rev.unlink()
                        removed_files.append(str(old_rev.relative_to(PROJECT_ROOT)))
                    except Exception:
                        pass

    return {
        "cleaned_files": len(removed_files),
        "removed_paths": removed_files,
        "closed_task_ids": list(closed_ids),
    }


def cmd_clean_rooms(args: argparse.Namespace) -> int:
    """Manually or hooked purge of closed task rooms and pruning of old handoffs."""
    res = clean_closed_task_rooms(max_retain_per_room=args.keep)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"[Paseo Room Hook] Đã dọn dẹp {res['cleaned_files']} file biên bản trùng lặp/closed trong bmad/rooms/.")
        for p in res["removed_paths"]:
            print(f"  - Xóa: {p}")
    return 0


def cmd_emit(args: argparse.Namespace) -> int:
    """Invoke `paseo hooks <agent> <event>` and record activity in .harness_hooks.jsonl."""
    paseo_bin = find_paseo_bin()
    stdin_payload: str | None = args.payload_json
    if stdin_payload is None and not sys.stdin.isatty():
        try:
            stdin_payload = sys.stdin.read()
        except Exception:
            stdin_payload = None

    terminal_id = os.environ.get("PASEO_TERMINAL_ID")
    activity_url = os.environ.get("PASEO_TERMINAL_ACTIVITY_URL")
    paseo_cmd = [paseo_bin, "hooks", args.agent, args.event]

    proc = subprocess.run(
        paseo_cmd,
        input=stdin_payload if stdin_payload else None,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=5,
        check=False,
    )

    parsed_payload: Any = None
    if stdin_payload:
        try:
            parsed_payload = json.loads(stdin_payload)
        except Exception:
            parsed_payload = stdin_payload[:500]

    research_result = None
    if args.trigger_research and args.event in ("UserPromptSubmit", "session.status.busy"):
        role = args.role or infer_slpc_role(stdin_payload, args.agent) or "Peer"
        topic = args.topic or (stdin_payload[:160] if stdin_payload else f"{args.agent}:{args.event}")
        research_result = trigger_research_gen(role, topic)

    cleanup_result = None
    if args.event in ("Stop", "SessionEnd"):
        cleanup_result = clean_closed_task_rooms()

    entry = {
        "kind": "cli_agent_hook",
        "agent": args.agent,
        "event": args.event,
        "terminalId": terminal_id,
        "hasActivityTarget": bool(terminal_id and activity_url),
        "exitCode": proc.returncode,
        "payload": parsed_payload,
        "researchGen": research_result,
    }
    append_hook_log(entry)

    if args.json:
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    else:
        print(
            f"[PASEO_HOOK_EMIT] agent={args.agent} event={args.event} "
            f"exit={proc.returncode} terminal={terminal_id or 'none'}"
        )
    return proc.returncode


def cmd_plugin_event(args: argparse.Namespace) -> int:
    """Handle lifecycle hook callbacks from @getpaseo/plugin/server."""
    raw_payload = args.payload_json
    if not raw_payload and args.payload_file:
        raw_payload = Path(args.payload_file).read_text(encoding="utf-8")
    if not raw_payload and not sys.stdin.isatty():
        raw_payload = sys.stdin.read()

    data: dict[str, Any] = {}
    if raw_payload:
        try:
            data = json.loads(raw_payload)
        except Exception:
            data = {"raw": raw_payload[:1000]}

    hook = args.hook
    agent_info = data.get("agent") if isinstance(data.get("agent"), dict) else {}
    workspace_info = data.get("workspace") if isinstance(data.get("workspace"), dict) else {}
    agent_id = agent_info.get("id") or data.get("request", {}).get("agentId")
    agent_title = agent_info.get("title") or data.get("request", {}).get("config", {}).get("title")
    provider = agent_info.get("provider") or data.get("request", {}).get("config", {}).get("provider")
    role = infer_slpc_role(agent_title, provider)

    research_result = None
    if hook == "agent.created" and role:
        topic = agent_title or f"Session for {role} ({agent_id})"
        research_result = trigger_research_gen(role, topic)

    if hook == "agent.turn_ended":
        outcome = data.get("outcome", {})
        outcome_kind = outcome.get("kind", "unknown") if isinstance(outcome, dict) else "unknown"
        turn_id = data.get("turnId")
        agent_label = f"Paseo/{role or provider or 'Agent'}"
        log_to_agent_progress(
            agent=agent_label,
            summary=f"Paseo hook agent.turn_ended ({outcome_kind}) - {agent_title or agent_id or 'session'}",
            done=f"Turn {turn_id or 'N/A'} ended with outcome={outcome_kind} (agentId={agent_id})",
        )

    if hook in ("agent.closed", "agent.archived", "agent.turn_ended"):
        clean_closed_task_rooms()

    entry = {
        "kind": "plugin_lifecycle_hook",
        "hook": hook,
        "agentId": agent_id,
        "agentTitle": agent_title,
        "provider": provider,
        "role": role,
        "workspaceId": workspace_info.get("id") or agent_info.get("workspaceId"),
        "researchGen": research_result,
        "data": data,
    }
    append_hook_log(entry)

    if args.json:
        print(json.dumps(entry, ensure_ascii=False))
    else:
        print(f"[PASEO_PLUGIN_HOOK] hook={hook} agent={agent_id or 'N/A'} role={role or 'N/A'}")
    return 0


def cmd_worktree(args: argparse.Namespace) -> int:
    """Handle Worktree Lifecycle Hooks (pre-create, post-create, pre-destroy)."""
    phase = args.phase
    worktree_env = {
        "PASEO_SOURCE_CHECKOUT_PATH": os.environ.get("PASEO_SOURCE_CHECKOUT_PATH", str(PROJECT_ROOT)),
        "PASEO_ROOT_PATH": os.environ.get("PASEO_ROOT_PATH", str(PROJECT_ROOT)),
        "PASEO_WORKTREE_PATH": os.environ.get("PASEO_WORKTREE_PATH", os.getcwd()),
        "PASEO_BRANCH_NAME": os.environ.get("PASEO_BRANCH_NAME", "main"),
        "PASEO_WORKTREE_PORT": os.environ.get("PASEO_WORKTREE_PORT", "8765"),
    }

    worktree_path = Path(worktree_env["PASEO_WORKTREE_PATH"]).resolve()
    source_root = Path(worktree_env["PASEO_ROOT_PATH"]).resolve()
    actions_taken: list[str] = []

    if phase == "pre-create":
        actions_taken.append(f"Verified source root {source_root}")
    elif phase == "post-create":
        # Copy .env.example -> .env in worktree if needed
        wt_env = worktree_path / ".env"
        src_env = source_root / ".env"
        src_env_example = source_root / ".env.example"
        if not wt_env.exists():
            if src_env.exists() and worktree_path != source_root:
                shutil.copy2(src_env, wt_env)
                actions_taken.append("Copied .env from source root into worktree")
            elif src_env_example.exists():
                shutil.copy2(src_env_example, wt_env)
                actions_taken.append("Initialized .env from .env.example")
        # Symlink shared .venv if worktree is separate from source_root
        wt_venv = worktree_path / ".venv"
        src_venv = source_root / ".venv"
        if worktree_path != source_root and src_venv.exists() and not wt_venv.exists():
            try:
                wt_venv.symlink_to(src_venv)
                actions_taken.append("Symlinked .venv into worktree")
            except Exception as exc:
                actions_taken.append(f"Skipped .venv symlink: {exc}")
        actions_taken.append(f"Worktree ready on branch {worktree_env['PASEO_BRANCH_NAME']}")
    elif phase == "pre-destroy":
        actions_taken.append(
            f"Prepared teardown for worktree {worktree_path} (branch {worktree_env['PASEO_BRANCH_NAME']})"
        )

    entry = {
        "kind": "worktree_lifecycle_hook",
        "phase": phase,
        "worktreeEnv": worktree_env,
        "actions": actions_taken,
    }
    append_hook_log(entry)

    log_to_agent_progress(
        agent="Paseo Worktree Hook",
        summary=f"Worktree lifecycle hook: {phase} ({worktree_env['PASEO_BRANCH_NAME']})",
        done="; ".join(actions_taken) or f"Executed {phase}",
    )

    print(json.dumps(entry, ensure_ascii=False))
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    """Enable pluginsEnabled + enableTerminalAgentHooks in ~/.paseo/config.json and install slpc-lifecycle-hooks."""
    paseo_bin = find_paseo_bin()
    config_updated = False

    if PASEO_CONFIG_FILE.exists():
        cfg = json.loads(PASEO_CONFIG_FILE.read_text(encoding="utf-8"))
        if cfg.get("pluginsEnabled") is not True:
            cfg["pluginsEnabled"] = True
            config_updated = True
        daemon_cfg = cfg.setdefault("daemon", {})
        if daemon_cfg.get("enableTerminalAgentHooks") is not True:
            daemon_cfg["enableTerminalAgentHooks"] = True
            config_updated = True
        if config_updated:
            backup = PASEO_CONFIG_FILE.with_suffix(".json.bak-hooks")
            shutil.copy2(PASEO_CONFIG_FILE, backup)
            PASEO_CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reload_res = subprocess.run(
        [paseo_bin, "reload", "--json"],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    install_res = None
    if PLUGIN_DIR.exists():
        ls_proc = subprocess.run(
            [paseo_bin, "plugin", "ls", "--json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        already_installed = False
        if ls_proc.returncode == 0 and ls_proc.stdout.strip():
            try:
                plugins_list = json.loads(ls_proc.stdout)
                already_installed = any(p.get("id") == PLUGIN_ID for p in plugins_list if isinstance(p, dict))
            except Exception:
                already_installed = False

        if already_installed:
            install_res = subprocess.run(
                [paseo_bin, "plugin", "reload", PLUGIN_ID, "--json"],
                capture_output=True,
                text=True,
                check=False,
                timeout=20,
            )
        else:
            install_res = subprocess.run(
                [paseo_bin, "plugin", "install", str(PLUGIN_DIR), "--id", PLUGIN_ID, "--json"],
                capture_output=True,
                text=True,
                check=False,
                timeout=25,
            )

    summary = {
        "configUpdated": config_updated,
        "daemonReloadExit": reload_res.returncode,
        "pluginDir": str(PLUGIN_DIR),
        "pluginInstallExit": install_res.returncode if install_res else None,
        "pluginInstallOutput": (install_res.stdout or install_res.stderr).strip() if install_res else None,
    }
    append_hook_log({"kind": "hook_system_install", **summary})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if (install_res is None or install_res.returncode == 0) else install_res.returncode


def cmd_status(args: argparse.Namespace) -> int:
    """Show full status of Paseo Plugin Hooks, Worktree Hooks, CLI Hooks, and recent events."""
    paseo_bin = find_paseo_bin()
    cfg: dict[str, Any] = {}
    if PASEO_CONFIG_FILE.exists():
        try:
            cfg = json.loads(PASEO_CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}

    plugin_ls = subprocess.run(
        [paseo_bin, "plugin", "ls", "--json"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    plugins_data: Any = []
    if plugin_ls.returncode == 0 and plugin_ls.stdout.strip():
        try:
            plugins_data = json.loads(plugin_ls.stdout)
        except Exception:
            plugins_data = plugin_ls.stdout.strip()

    paseo_json_path = PROJECT_ROOT / "paseo.json"
    paseo_json_data: dict[str, Any] = {}
    if paseo_json_path.exists():
        try:
            paseo_json_data = json.loads(paseo_json_path.read_text(encoding="utf-8"))
        except Exception:
            paseo_json_data = {}

    recent_events: list[dict[str, Any]] = []
    if HOOKS_LOG_FILE.exists():
        lines = HOOKS_LOG_FILE.read_text(encoding="utf-8").splitlines()
        for line in lines[-args.limit :]:
            try:
                recent_events.append(json.loads(line))
            except Exception:
                continue

    report = {
        "paseoBin": paseo_bin,
        "pluginsEnabled": cfg.get("pluginsEnabled", False),
        "enableTerminalAgentHooks": cfg.get("daemon", {}).get("enableTerminalAgentHooks", False),
        "installedPlugins": plugins_data,
        "supportedPluginLifecycleHooks": ALL_PLUGIN_LIFECYCLE_HOOKS,
        "supportedCliAgentEvents": SUPPORTED_CLI_AGENT_EVENTS,
        "worktreeConfig": paseo_json_data.get("worktree", {}),
        "hooksLogFile": str(HOOKS_LOG_FILE),
        "recentEventsCount": len(recent_events),
        "recentEvents": recent_events,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified Paseo Hook Tool (Plugin Lifecycle Hooks, Worktree Hooks, CLI Agent Hooks)."
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # 1. emit: wrapper around `paseo hooks <agent> <event>`
    p_emit = sub.add_parser("emit", help="Call `paseo hooks <agent> <event>` and record hook activity")
    p_emit.add_argument("agent", help="Agent hook source (claude, codex, opencode)")
    p_emit.add_argument("event", help="Agent hook event (e.g. UserPromptSubmit, PreToolUse, PostToolUse, Stop)")
    p_emit.add_argument("--payload-json", help="Optional JSON string payload to pass via stdin")
    p_emit.add_argument("--role", help="Optional SLPC role (Supervisor, Lead, Peer, QC)")
    p_emit.add_argument("--topic", help="Optional topic when triggering research/gen")
    p_emit.add_argument("--trigger-research", action="store_true", help="Trigger profile_research_gen.py on start events")
    p_emit.add_argument("--json", action="store_true", help="Output JSON")
    p_emit.set_defaults(func=cmd_emit)

    # 2. plugin-event: callback target for @getpaseo/plugin/server hooks
    p_plugin = sub.add_parser("plugin-event", help="Record & process @getpaseo/plugin/server lifecycle hook events")
    p_plugin.add_argument("--hook", required=True, help="Hook name (e.g. before:agent.create, agent.turn_ended)")
    p_plugin.add_argument("--payload-json", help="JSON payload string")
    p_plugin.add_argument("--payload-file", help="Path to JSON payload file")
    p_plugin.add_argument("--json", action="store_true", help="Output JSON")
    p_plugin.set_defaults(func=cmd_plugin_event)

    # 3. worktree: pre-create, post-create, pre-destroy
    p_wt = sub.add_parser("worktree", help="Execute worktree lifecycle hook (pre-create, post-create, pre-destroy)")
    p_wt.add_argument("phase", choices=["pre-create", "post-create", "pre-destroy"], help="Worktree hook phase")
    p_wt.set_defaults(func=cmd_worktree)

    # 4. install
    p_install = sub.add_parser("install", help="Enable Paseo plugins & terminal hooks and install slpc-lifecycle-hooks")
    p_install.set_defaults(func=cmd_install)

    # 5. status
    p_status = sub.add_parser("status", help="Inspect status of all 3 Paseo hook layers and recent events")
    p_status.add_argument("--limit", type=int, default=15, help="Max recent hook events to display")
    p_status.set_defaults(func=cmd_status)

    # 6. clean-rooms: purge closed task memos & prune old handoffs
    p_clean = sub.add_parser("clean-rooms", help="Inspect bmad/rooms/ and purge handoff files belonging to Closed tasks")
    p_clean.add_argument("--keep", type=int, default=2, help="Max recent handoff files to keep per role room (default: 2)")
    p_clean.add_argument("--json", action="store_true", help="Output JSON result")
    p_clean.set_defaults(func=cmd_clean_rooms)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
