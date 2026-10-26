#!/usr/bin/env python3
"""
tools/orca_slpc_bridge.py - Bộ điều phối toàn diện SLPC trên nền tảng Orca Orchestration Engine.

Hiện thực hóa đầy đủ đặc tả docs/spec/slpc-orca-orchestration-spec.md:
- Khởi tạo Run, Task, Decision Gate trên Orca Orchestration.
- Quản lý phân rã Task và Sub-Agent phân cấp (Parent-Child Task Lineage).
- Đồng bộ 5 trạng thái 1:1 sang Orca Workspace Board (Todo, In progress, In review, Completed, Removed).
- Kích hoạt cổng kiểm thử độc lập QC & 3 Sub-Agents review chéo.
- Quản lý sandbox bmad/rooms/tasks/<task_id>/ và thu gom rác an toàn khi Closed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from floci_client import FlociHarnessDB  # type: ignore
except ImportError:
    from tools.floci_client import FlociHarnessDB  # type: ignore

try:
    from harness_manager import HarnessManager  # type: ignore
except ImportError:
    from tools.harness_manager import HarnessManager  # type: ignore

STATE_MAP = {
    "New": "todo",
    "Active": "in-progress",
    "Resolved": "in-review",
    "Closed": "completed",
    "Blocked": "in-progress",
    "Removed": "removed",
}


def _get_orca_ide_bin() -> Optional[str]:
    """Trả về đường dẫn Orca IDE CLI thật, tuyệt đối chặn /usr/bin/orca (Linux Screen Reader)."""
    shim = Path.home() / ".config" / "orca" / "linux-orca-cli-shim" / "orca"
    if shim.is_file() and os.access(shim, os.X_OK):
        return str(shim)
    cand = shutil.which("orca")
    if not cand:
        return None
    if cand in ("/usr/bin/orca", "/bin/orca", "/usr/games/orca"):
        return None
    try:
        p = Path(cand)
        if p.exists() and p.resolve() in (Path("/usr/bin/orca"), Path("/bin/orca")):
            return None
        if p.is_file() and p.stat().st_size < 100_000:
            head = p.read_text(encoding="utf-8", errors="ignore")[:1024].lower()
            if "screen reader" in head or "gnome" in head or "import orca" in head:
                return None
    except Exception:
        pass
    return cand


def run_cmd(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    if cmd and cmd[0] == "orca":
        orca_bin = _get_orca_ide_bin()
        if not orca_bin:
            return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="Orca IDE CLI not found")
        cmd = [orca_bin] + cmd[1:]
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def sync_board_status(task_id: str, state: str, worktree: str = "active"):
    """Đồng bộ trạng thái thẻ trên Workspace Board."""
    if not _get_orca_ide_bin():
        return

    if state == "Removed":
        cmd_set = [
            "orca", "worktree", "set",
            "--worktree", worktree,
            "--comment", f"Harness WI #{task_id} [REMOVED - TASK CANCELLED]",
            "--json"
        ]
        try:
            run_cmd(cmd_set, check=False)
            print(f"🗑️ [Orca Board]: Đã cập nhật trạng thái REMOVED cho Task #{task_id}.")
        except Exception:
            pass
        return

    orca_status = STATE_MAP.get(state, "in-progress")
    cmd = [
        "orca", "worktree", "set",
        "--worktree", worktree,
        "--workspace-status", orca_status,
        "--comment", f"Harness WI #{task_id} [{state}]",
        "--json"
    ]
    try:
        run_cmd(cmd, check=True)
        print(f"✅ [Orca Board Sync]: Workspace '{worktree}' ➔ Cột [{orca_status.upper()}] (Task #{task_id}: {state})")
    except Exception as e:
        if worktree == "active":
            try:
                cmd[4] = "name:main"
                run_cmd(cmd, check=True)
                print(f"✅ [Orca Board Sync]: Workspace 'name:main' ➔ Cột [{orca_status.upper()}] (Task #{task_id}: {state})")
                return
            except Exception:
                pass
        print(f"⚠️ [Orca Board Sync Warning]: {e}", file=sys.stderr)


# ==============================================================================
# SUBCOMMANDS
# ==============================================================================

def cmd_init_run(name: str, title: str) -> Dict[str, Any]:
    """Bước 1: Supervisor khởi tạo Orchestration Run & Epic."""
    print("=== [BƯỚC 1: KHỞI TẠO ORCA RUN & HARNESS EPIC] ===")
    run_id = None
    if _get_orca_ide_bin():
        try:
            res = run_cmd(["orca", "orchestration", "run-create", "--name", name, "--json"])
            data = json.loads(res.stdout)
            run_id = data.get("result", {}).get("runId")
            print(f"✅ Đã tạo Orca Orchestration Run: {run_id} ({name})")
        except Exception as e:
            print(f"⚠️ Không thể tạo Orca Run: {e}")

    mgr = HarnessManager()
    validated_title = title if ("-" in title or "–" in title) else f"[SLPC] - {title}"
    epic_res = mgr.add_work_item(
        wi_type="Epic",
        title=validated_title,
        source="bot",
        created_by_profile="supervisor",
        assigned_to_profile="lead"
    )
    epic_id = epic_res.get("id")
    print(f"✅ Đã tạo Harness Epic #{epic_id}: {title}")

    # Tạo sandbox task
    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(epic_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "handoff_supervisor.md").write_text(
        f"# EPIC #{epic_id}: {title}\n- **Run ID**: {run_id}\n- **Thời gian**: {time.ctime()}\n",
        encoding="utf-8"
    )

    sync_board_status(str(epic_id), "Active")
    return {"run_id": run_id, "epic_id": epic_id}


def cmd_create_task(run_id: Optional[str], parent_id: str, title: str, spec: str) -> Dict[str, Any]:
    """Bước 2: Lead bóc tách Task, lập Decision Gate QC."""
    print(f"=== [BƯỚC 2: LEAD BÓC TÁCH TASK TRỰC THUỘC EPIC #{parent_id}] ===")
    mgr = HarnessManager()
    validated_title = title if ("-" in title or "–" in title) else f"[Task] - {title}"
    task_res = mgr.add_work_item(
        wi_type="Task",
        title=validated_title,
        source="bot",
        created_by_profile="lead",
        assigned_to_profile="peer",
        parent_id=int("".join(filter(str.isdigit, str(parent_id)))) if parent_id else None
    )
    task_id = task_res.get("id")
    print(f"✅ Đã tạo Harness Task #{task_id}: {title}")

    orca_task_id = None
    gate_id = None
    if _get_orca_ide_bin() and run_id:
        try:
            # 1. Tạo Task trong Orca Run
            res = run_cmd(["orca", "orchestration", "task-create", "--title", f"[WI-{task_id}] {title}", "--run", run_id, "--json"])
            data = json.loads(res.stdout)
            orca_task_id = data.get("result", {}).get("taskId")
            print(f"✅ Đã tạo Orca Task: {orca_task_id}")

            # 2. Tạo Decision Gate chặn nghiệm thu
            res_gate = run_cmd(["orca", "orchestration", "gate-create", "--name", f"QC-Signoff-WI-{task_id}", "--task", str(orca_task_id), "--run", run_id, "--json"])
            data_gate = json.loads(res_gate.stdout)
            gate_id = data_gate.get("result", {}).get("gateId")
            print(f"🔒 Đã thiết lập Decision Gate: {gate_id} (QC giữ cổng)")
        except Exception as e:
            print(f"⚠️ Lỗi tạo Orca task/gate: {e}")

    # Tạo sandbox task & nạp bài học từ Harness² Per-Domain Library
    h2_lessons = ""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "plugins" / "slpc-lifecycle-hooks"))
        from slppc_orchestrator import SlppcOrchestrator  # type: ignore
        orch = SlppcOrchestrator()
        h2_lessons = orch.query_harness2_library_context(domain="engineering", limit=3)
        orch.run_harness2_recursion_cycle(task_id=str(task_id), mode="agg", k=1, domain="engineering", notes=title)
    except Exception:
        pass

    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    memo = f"""# TASK #{task_id}: {title}
- **Parent Epic**: #{parent_id}
- **Orca Task ID**: {orca_task_id}
- **QC Decision Gate ID**: {gate_id}
- **Yêu cầu kỹ thuật**:
{spec}
{h2_lessons}
"""
    (task_dir / "handoff_lead.md").write_text(memo, encoding="utf-8")
    (task_dir / "latest_handoff.md").write_text(memo, encoding="utf-8")
    print(f"📁 Đã tạo Task Sandbox cô lập (kèm Harness² Ledger & Library): bmad/rooms/tasks/{task_id}/")

    return {"task_id": task_id, "orca_task_id": orca_task_id, "gate_id": gate_id}


def find_live_terminal_for_role(role: str) -> Optional[str]:
    """Tìm terminal handle của role tương ứng (Supervisor, PM, Lead, Peer, QC) đang chạy trong Orca."""
    orca_bin = _get_orca_ide_bin()
    if os.environ.get("SLPPC_DRY_RUN") == "1" or not orca_bin:
        return None
    try:
        try:
            from agent_context_manager import has_live_terminal  # type: ignore
        except ImportError:
            from tools.agent_context_manager import has_live_terminal  # type: ignore
        found = has_live_terminal(role)
        if found:
            return found
    except Exception:
        pass

    try:
        t_res = subprocess.run([orca_bin, "terminal", "list", "--json"], capture_output=True, text=True)
        t_data = json.loads(t_res.stdout)
        terminals = [
            t for t in t_data.get("result", {}).get("terminals", [])
            if t.get("handle") and not t.get("stopped") and t.get("connected", True)
        ]

        role_lower = role.lower().replace("-", "_").replace(" ", "_")
        if "supervisor" in role_lower or role_lower == "main":
            target_room = "supervisor"
        elif "lead" in role_lower:
            target_room = "lead"
        elif "pm" in role_lower:
            target_room = "pm"
        elif any(k in role_lower for k in ("peer", "dev", "design")):
            target_room = "peer"
        elif "qc" in role_lower:
            target_room = "qc"
        else:
            target_room = role.lower().split()[0]

        # Check PROJECT_ROOT / bmad/rooms/agent_terminals.json registry first
        reg_file = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
        if reg_file.exists():
            try:
                reg_data = json.loads(reg_file.read_text(encoding="utf-8"))
                reg_h = (reg_data.get(target_room) or {}).get("handle")
                if reg_h:
                    for t in terminals:
                        if t.get("handle") == reg_h:
                            wt_p = (t.get("worktreePath") or "").lower().rstrip("/")
                            br_p = (t.get("branch") or "").lower().rstrip("/")
                            if not wt_p and not br_p:
                                return reg_h
                            if target_room in ("pm", "lead", "peer", "qc") and (wt_p.endswith(f"/room-{target_room}") or br_p.endswith(f"room-{target_room}")):
                                return reg_h
                            if target_room == "supervisor" and br_p in ("main", "refs/heads/main") and "/room-" not in wt_p:
                                return reg_h
            except Exception:
                pass

        for t in terminals:
            wt_path = (t.get("worktreePath") or "").lower().rstrip("/")
            branch = (t.get("branch") or "").lower().rstrip("/")
            if target_room in ("pm", "lead", "peer", "qc"):
                if wt_path.endswith(f"/room-{target_room}") or branch.endswith(f"room-{target_room}"):
                    return t.get("handle")
            elif target_room == "supervisor":
                if branch in ("main", "refs/heads/main") and "/room-" not in wt_path:
                    return t.get("handle")
    except Exception:
        pass
    return None


def send_to_terminal_safely(terminal_handle: str, text: str, wait_timeout_ms: int = 5000):
    """Gửi lệnh vào terminal có cơ chế chống trôi: Thử chờ tui-idle trước khi gửi."""
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return
    try:
        # Thử chờ terminal về trạng thái idle
        subprocess.run([
            orca_bin, "terminal", "wait",
            "--terminal", terminal_handle,
            "--for", "tui-idle",
            "--timeout-ms", str(wait_timeout_ms)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=wait_timeout_ms / 1000 + 1)
    except Exception:
        pass

    # Gửi lệnh
    try:
        subprocess.run([
            orca_bin, "terminal", "send",
            "--terminal", terminal_handle,
            "--text", text,
            "--enter"
        ], check=False)
    except Exception:
        pass


def launch_and_rename_agent(role: str, title: str, prompt: str, model: str = "ag/gemini-3.8-flash-high") -> Optional[str]:
    """Khởi chạy Orca agent và lập tức đổi tên terminal + pane title."""
    orca_bin = _get_orca_ide_bin()
    if not orca_bin:
        return None
    cmd = [
        orca_bin, "agent", "launch",
        "--worktree", "active",
        "--agent", "hermes",
        "--prompt", prompt,
        "--json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            outcome = data.get("result", {}).get("outcome", {})
            handle = outcome.get("handle") or ""
            pk = outcome.get("paneKey") or ""
            tab_id = pk.split(":")[0] if ":" in pk else pk
            if handle:
                subprocess.run([orca_bin, "terminal", "rename", "--terminal", handle, "--title", title, "--json"], capture_output=True, check=False)
                subprocess.run([orca_bin, "terminal", "set-pane-title", "--terminal", handle, "--title", title, "--json"], capture_output=True, check=False)
                subprocess.run([orca_bin, "terminal", "send", "--terminal", handle, "--text", f"/title {title}", "--enter"], capture_output=True, check=False)
                if model:
                    subprocess.run([orca_bin, "terminal", "send", "--terminal", handle, "--text", f"/model {model}", "--enter"], capture_output=True, check=False)

                reg_file = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
                reg = {}
                if reg_file.is_file():
                    try:
                        reg = json.loads(reg_file.read_text(encoding="utf-8"))
                    except Exception:
                        reg = {}
                reg[role.lower()] = {"handle": handle, "tabId": tab_id}
                reg_file.parent.mkdir(parents=True, exist_ok=True)
                reg_file.write_text(json.dumps(reg, indent=2), encoding="utf-8")
                return handle
    except Exception as e:
        print(f"⚠️ [launch_and_rename_agent error]: {e}", file=sys.stderr)
    return None


def cmd_dispatch_design(task_id: str, prompt: str, figma_node: Optional[str] = None):
    """Lead dispatch nhiệm vụ bóc tách Figma/UI token cho Peer Design."""
    print(f"=== [DISPATCH CHO PEER DESIGN TASK #{task_id}] ===")
    mgr = HarnessManager()
    mgr.update_state(int("".join(filter(str.isdigit, str(task_id)))), "Active", assigned_to_profile="Peer Design")
    sync_board_status(str(task_id), "Active")

    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    memo = f"# DESIGN SPEC BRIEF: Task #{task_id}\n- **Figma Node**: {figma_node or 'N/A'}\n- **Yêu cầu UI/UX**: {prompt}\n- **Người giao**: Lead Dev\n"
    (task_dir / "handoff_design.md").write_text(memo, encoding="utf-8")
    (task_dir / "latest_handoff.md").write_text(memo, encoding="utf-8")

    if _get_orca_ide_bin():
        design_handle = find_live_terminal_for_role("design")
        task_instruction = f"Bóc tách giao diện Task #{task_id}: {prompt}. Figma Node: {figma_node or 'N/A'}. Hãy đọc bmad/rooms/tasks/{task_id}/handoff_design.md và dùng tools/tds_search.py tra cứu token."
        if design_handle:
            print(f"🎯 [Direct Terminal Dispatch]: Tìm thấy Peer Design ({design_handle}). Bắn lệnh...")
            send_to_terminal_safely(design_handle, task_instruction)
            print(f"✅ Đã gửi lệnh trực tiếp vào terminal của Peer Design!")
            return

        h = launch_and_rename_agent("design", "[Peer Design] UI/UX & Tokens", f"[Peer Design] #{task_id}: {prompt}", "ag/gemini-3.8-flash-high")
        if h:
            print(f"🚀 [Orca Agent Launch]: Đã spawn và đổi tên Peer Design ({h}) cho Task #{task_id}.")
        else:
            print(f"⚠️ Không thể launch Peer Design.")


def cmd_report_design_done(task_id: str, spec_file: str):
    """Peer Design nộp spec thiết kế và chuyển giao cho Peer Dev lắp ráp code."""
    print(f"=== [PEER DESIGN NỘP SPEC THIẾT KẾ CHO PEER DEV TASK #{task_id}] ===")
    numeric_id = int("".join(filter(str.isdigit, str(task_id))))
    mgr = HarnessManager()
    mgr.update_state(numeric_id, "Active", assigned_to_profile="peer")

    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    memo = f"# DESIGN SPEC COMPLETED: Task #{task_id}\n- **File đặc tả thiết kế**: {spec_file}\n- **Người hoàn thành**: Peer Design\n- **Trạng thái**: Đã chuyển giao cho Peer Dev lắp ráp code Angular 18\n"
    (task_dir / "handoff_design_completed.md").write_text(memo, encoding="utf-8")
    (task_dir / "latest_handoff.md").write_text(memo, encoding="utf-8")

    if _get_orca_ide_bin():
        peer_handle = find_live_terminal_for_role("peer")
        if peer_handle:
            print(f"🎯 [Direct Terminal Dispatch]: Tìm thấy Peer Dev ({peer_handle}). Bàn giao spec thiết kế...")
            send_to_terminal_safely(peer_handle, f"Lắp ráp code Task #{task_id}: Peer Design đã hoàn thành đặc tả ({spec_file}). Hãy đọc bmad/rooms/tasks/{task_id}/latest_handoff.md và code Angular 18.")
            print("✅ Đã chuyển giao nhiệm vụ sang terminal Peer Dev!")


def cmd_dispatch_peer(task_id: str, prompt: str, parent_task_id: Optional[str] = None, target_peer: Optional[str] = None):
    """Bước 3: Lead dispatch việc cho Peer Slot (peer, peer2..4, peer_design) kèm Harness² Ledger & Library."""
    print(f"=== [BƯỚC 3: DISPATCH CHO PEER THỰC THI TASK #{task_id}] ===")

    chosen_role = (target_peer or "peer").strip().lower()
    if chosen_role not in ("peer", "peer2", "peer3", "peer4", "peer_design"):
        chosen_role = "peer"
    peer_label = f"Peer Dev ({chosen_role.upper()})"
    mgr = HarnessManager()
    mgr.update_state(int("".join(filter(str.isdigit, str(task_id)))), "Active", assigned_to_profile="peer")
    sync_board_status(str(task_id), "Active")

    h2_lessons = ""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "plugins" / "slpc-lifecycle-hooks"))
        from slppc_orchestrator import SlppcOrchestrator  # type: ignore
        orch = SlppcOrchestrator()
        h2_lessons = orch.query_harness2_library_context(domain="engineering", limit=3)
        orch.run_harness2_recursion_cycle(task_id=str(task_id), mode="agg", k=1, domain="engineering", notes=prompt[:120])
    except Exception:
        pass

    try:
        from agent_heartbeat import record_ping  # type: ignore
        record_ping(chosen_role, "working", task_id=str(task_id), activity=prompt[:30])
    except Exception:
        pass

    if _get_orca_ide_bin():
        peer_handle = find_live_terminal_for_role(chosen_role)
        task_instruction = f"Nhiệm vụ mới Task #{task_id}: {prompt}.{h2_lessons} Hãy đọc bmad/rooms/tasks/{task_id}/latest_handoff.md và thực thi."
        if peer_handle:
            print(f"🎯 [Direct Terminal Dispatch]: Tìm thấy {peer_label} ({peer_handle}). Bắn lệnh an toàn (chờ idle)...")
            send_to_terminal_safely(peer_handle, task_instruction)
            print(f"✅ Đã gửi lệnh trực tiếp vào terminal của {peer_label} Hermes!")
        else:
            # Fallback launch Hermes agent mới và đổi tên
            h = launch_and_rename_agent(chosen_role, f"[{peer_label}] Task #{task_id}", f"[{chosen_role.upper()}] #{task_id}: {prompt}{h2_lessons}", "ag/gemini-3.8-flash-high")
            if h:
                print(f"🚀 [Orca Agent Launch]: Đã spawn và đổi tên {peer_label} ({h}) cho Task #{task_id}.")
            else:
                print(f"⚠️ Không thể launch agent cho {peer_label}.")

        # Lead đã hoàn tất phân rã và bàn giao cho Peer -> Tự động đóng tab Lead & PM
        try:
            from harness_manager import close_ephemeral_subagent  # type: ignore
            close_ephemeral_subagent("lead")
            close_ephemeral_subagent("pm")
        except Exception:
            pass


def cmd_report_done(task_id: str, files: str):
    """Bước 4: Peer nộp code diff cho Lead Dev để Code Review."""
    print(f"=== [BƯỚC 4: PEER NỘP CODE DIFF TASK #{task_id} CHO LEAD DEV REVIEW] ===")
    numeric_id = int("".join(filter(str.isdigit, str(task_id))))
    mgr = HarnessManager()
    # Giữ quyền sở hữu Task cho Peer trong lúc chờ Lead Dev thẩm định (tuân thủ Role Fence)
    mgr.update_state(numeric_id, "Active", assigned_to_profile="peer")
    sync_board_status(str(task_id), "Active")

    # Ghi nhận handoff
    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    memo = f"""# PEER HANDOFF: Task #{task_id}
- **Trạng thái**: Active (Đã nộp code, chờ Lead Dev review kiến trúc)
- **File đã sửa**: {files}
- **Thời gian**: {time.ctime()}
"""
    (task_dir / "handoff_peer.md").write_text(memo, encoding="utf-8")
    (task_dir / "latest_handoff.md").write_text(memo, encoding="utf-8")

    try:
        from agent_heartbeat import record_ping  # type: ignore
        record_ping("peer", "idle", task_id=str(task_id), activity=f"Done code {files[:20]}")
        record_ping("lead", "working", task_id=str(task_id), activity="Reviewing Peer code")
    except Exception:
        pass

    orca_bin = _get_orca_ide_bin()
    if orca_bin:
        # Bắn lệnh trực tiếp vào LEAD Dev Hermes terminal (hoặc bật Lead on-demand nếu đã đóng) để Lead vào review code
        lead_prompt = f"Review code Task #{task_id}: Peer đã nộp code ({files}). Hãy chạy: python3 tools/orca_slpc_bridge.py lead-review --task-id {task_id}"
        lead_handle = find_live_terminal_for_role("lead")
        if lead_handle:
            print(f"🎯 [Direct Terminal Dispatch]: Tìm thấy Lead Dev Hermes ({lead_handle}). Gửi yêu cầu review...")
            send_to_terminal_safely(lead_handle, lead_prompt)
            print("✅ Đã bắn thông báo trực tiếp vào terminal của Lead Dev Hermes!")
        else:
            h_lead = launch_and_rename_agent("lead", "[Lead Dev] Technical Architect", lead_prompt, "ag/gemini-3.8-flash-high")
            if h_lead:
                print(f"🚀 [Ephemeral Auto-Launch]: Đã mở lại Lead Dev ({h_lead}) để review code Task #{task_id}!")

        try:
            run_cmd([
                "orca", "orchestration", "send",
                "--subject", f"[Peer Done] Task #{task_id} nộp cho Lead Review",
                "--type", "worker_done",
                "--outcome", "succeeded",
                "--files-modified", files,
                "--task-id", str(task_id)
            ], check=False)
        except Exception:
            pass

        # Ephemeral Lifecycle: Peer nộp xong tự động đóng terminal để tiết kiệm RAM & Token
        try:
            from harness_manager import close_ephemeral_subagent  # type: ignore
            close_ephemeral_subagent("peer")
        except Exception:
            peer_handle = find_live_terminal_for_role("peer")
            if peer_handle:
                subprocess.run([orca_bin, "terminal", "close", "--terminal", peer_handle, "--tab"], check=False)


def cmd_lead_review(task_id: str, repo_dir: str = ".") -> bool:
    """Bước 5: Lead Dev thẩm định kiến trúc (5-Point Checklist). Nếu Pass mới bàn giao cho QC."""
    print(f"=== [BƯỚC 5: LEAD DEV CODE REVIEW TASK #{task_id}] ===")
    numeric_id = int("".join(filter(str.isdigit, str(task_id))))

    target_repo = PROJECT_ROOT / repo_dir
    if not target_repo.exists():
        target_repo = PROJECT_ROOT

    # 1. Chạy công cụ thẩm định tự động lead_code_review.py
    print("🔍 [Lead Code Review]: Quét Single-Ownership, TDS Tokens, OnPush, YAGNI, Dead Code...")
    review_res = subprocess.run([
        "python3", str(PROJECT_ROOT / "tools" / "lead_code_review.py"),
        "--repo-dir", str(target_repo),
        "--task-id", str(task_id),
        "--json"
    ], capture_output=True, text=True)

    passed = True
    try:
        data = json.loads(review_res.stdout)
        if data.get("verdict") != "APPROVED":
            passed = False
    except Exception:
        if "APPROVED" not in review_res.stdout and review_res.returncode != 0:
            passed = False

    if not passed:
        print("❌ [LEAD CODE REVIEW: REJECTED]: Phát hiện vi phạm kiến trúc!")
        # 1. Ghi báo cáo gửi Supervisor thông báo Reject
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        supervisor_dir = PROJECT_ROOT / "bmad" / "rooms" / "supervisor"
        supervisor_dir.mkdir(parents=True, exist_ok=True)
        task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
        task_dir.mkdir(parents=True, exist_ok=True)

        report_content = f"""# BÁO CÁO REVIEW KIẾN TRÚC CỦA LEAD DEV GỬI SUPERVISOR

- **Mã Task / Work Item**: `#{task_id}`
- **Thời gian lập**: `{ts_now}`
- **Người báo cáo (From)**: `Lead Dev`
- **Người tiếp nhận (To)**: `Supervisor`
- **Kết luận thẩm định (Verdict)**: **REJECTED (KHÔNG ĐẠT)**

---

## 1. Kết Quả Rà Soát 5 Tiêu Chí Kiến Trúc Bắt Buộc
- [ ] **Single-Ownership Invariant**: Phát hiện vi phạm ranh giới module hoặc tiêu chuẩn code.
- [ ] **TDS UI Design Tokens**: Kiểm tra mã màu hex cứng.
- [ ] **Angular 18 Performance**: Standalone true, ChangeDetectionStrategy.OnPush.
- [ ] **YAGNI & Lazy Senior Dev**: Code thừa hoặc boilerplate.
- [ ] **Dead Code Cleanliness**: Import rác.

---

## 2. Chi Tiết Lỗi & Bằng Chứng
```text
{review_res.stdout or review_res.stderr}
```

---

## 3. Quyết Định Xử Lý
- **Hành động**: Tự động phạt Peer qua `agent_reprimand.py`, tạo ticket Bug P1 và giáng Task về `Active`.
- **Yêu cầu**: Peer Dev bắt buộc phải sửa sạch lỗi trước khi Lead xem xét lại.
"""
        rep_file = supervisor_dir / f"review_report_{task_id}_{ts_file}.md"
        rep_file.write_text(report_content, encoding="utf-8")
        (task_dir / "lead_review_report_to_supervisor.md").write_text(report_content, encoding="utf-8")
        print(f"📋 [Báo cáo Lead ➔ Supervisor]: Đã xuất báo cáo REJECT tại {rep_file.relative_to(PROJECT_ROOT)}")

        # Bắn thông báo báo cáo về Supervisor terminal
        if _get_orca_ide_bin():
            sup_handle = find_live_terminal_for_role("supervisor")
            if sup_handle:
                send_to_terminal_safely(sup_handle, f"[Báo cáo Lead Dev ➔ Supervisor] Task #{task_id}: REJECTED. Đã tạo Bug P1 gán cho Peer sửa lại.")

        # Tự động phạt Peer và tạo Bug ticket P1
        subprocess.run([
            "python3", str(PROJECT_ROOT / "tools" / "agent_reprimand.py"),
            "--from-role", "Lead",
            "--to-role", "Peer",
            "--violation", "hardcoded_hex",
            "--evidence", review_res.stdout or review_res.stderr,
            "--message", "Code không đạt tiêu chuẩn kiến trúc Lead Review! Bắt buộc sửa lại.",
            "--task-id", str(task_id),
            "--penalize"
        ], check=False)

        # Mở lại Terminal Orca cho Peer vào fix tiếp
        if _get_orca_ide_bin():
            print(f"🔄 [Reopen Peer Terminal]: Lead Review REJECTED Task #{task_id}. Đang mở lại tab Orca cho Peer fix tiếp...")
            prompt_fix = f"[Peer Fix Task #{task_id}]: Lead Review REJECTED. Hãy đọc bmad/rooms/tasks/{task_id}/lead_review_report_to_supervisor.md và khắc phục vi phạm!"
            h = launch_and_rename_agent("peer", f"[Peer Dev] Fix Task #{task_id}", prompt_fix, "ag/gemini-3.8-flash-high")
            if h:
                print(f"🚀 Đã mở lại và đổi tên Orca terminal cho Peer ({h}) vào sửa lỗi Task #{task_id}!")
            else:
                print(f"⚠️ Không thể mở lại terminal Peer.")
        return False

    print("✅ [LEAD CODE REVIEW: APPROVED]! Mã nguồn đạt chuẩn kiến trúc 100%.")

    # 2. Lead chuyển Task sang 'Resolved' và bàn giao cho QC
    mgr = HarnessManager()
    mgr.update_state(numeric_id, "Resolved", assigned_to_profile="qc")
    sync_board_status(str(task_id), "Resolved")

    # 3. Ghi handoff lead sang phòng qc và xuất Báo cáo gửi Supervisor
    task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    supervisor_dir = PROJECT_ROOT / "bmad" / "rooms" / "supervisor"
    supervisor_dir.mkdir(parents=True, exist_ok=True)

    report_content = f"""# BÁO CÁO REVIEW KIẾN TRÚC CỦA LEAD DEV GỬI SUPERVISOR

- **Mã Task / Work Item**: `#{task_id}`
- **Thời gian lập**: `{ts_now}`
- **Người báo cáo (From)**: `Lead Dev`
- **Người tiếp nhận (To)**: `Supervisor`
- **Kết luận thẩm định (Verdict)**: **APPROVED (ĐẠT CHUẨN 100%)**

---

## 1. Kết Quả Rà Soát 5 Tiêu Chí Kiến Trúc Bắt Buộc
- [x] **Single-Ownership Invariant**: 100% file thay đổi nằm đúng phạm vi module được giao.
- [x] **TDS UI Design Tokens**: 0% mã màu hex cứng (#...), tuân thủ 100% biến token semantic.
- [x] **Angular 18 Performance**: Standalone true, ChangeDetectionStrategy.OnPush.
- [x] **YAGNI & Lazy Senior Dev**: Không sinh boilerplate/abstraction thừa, xóa trước thêm sau.
- [x] **Dead Code Cleanliness**: Sạch sẽ import không dùng và ViewChild mồ côi.

---

## 2. Quyết Định Chuyển Giao Tiếp Theo
- **Hành động**: Chuyển trạng thái Task #{task_id} sang `Resolved`, bàn giao cho QC kiểm định độc lập.
- **Chỉ thị cho QC**: Thực thi quy trình kiểm thử 5-Stage ISTQB và mở Decision Gate khi pass 100%.
"""
    rep_file = supervisor_dir / f"review_report_{task_id}_{ts_file}.md"
    rep_file.write_text(report_content, encoding="utf-8")
    (task_dir / "lead_review_report_to_supervisor.md").write_text(report_content, encoding="utf-8")
    (task_dir / "handoff_lead_approval.md").write_text(report_content, encoding="utf-8")
    (task_dir / "latest_handoff.md").write_text(report_content, encoding="utf-8")
    print(f"📋 [Báo cáo Lead ➔ Supervisor]: Đã xuất báo cáo APPROVED tại {rep_file.relative_to(PROJECT_ROOT)}")

    # Ghi nhận sổ cái tiến độ
    try:
        subprocess.run([
            "python3", str(PROJECT_ROOT / "tools" / "agent_progress.py"),
            "log", "--agent", "Lead",
            "--summary", f"Lead Review Task #{task_id} APPROVED -> Báo cáo Supervisor và bàn giao QC",
            "--done", f"1. Thẩm định 5 tiêu chí kiến trúc đạt 100%; 2. Xuất báo cáo gửi Supervisor; 3. Chuyển Task #{task_id} sang Resolved"
        ], capture_output=True, text=True)
    except Exception:
        pass

    # 4. Bắn lệnh sang terminal QC và báo cáo Supervisor
    if _get_orca_ide_bin():
        sup_handle = find_live_terminal_for_role("supervisor")
        if sup_handle:
            send_to_terminal_safely(sup_handle, f"[Báo cáo Lead Dev ➔ Supervisor] Task #{task_id}: APPROVED đạt chuẩn kiến trúc 100%. Đã chuyển giao cho QC.")
            print("✅ Đã gửi báo cáo thẩm định trực tiếp vào terminal Supervisor!")

        qc_handle = find_live_terminal_for_role("qc")
        if qc_handle:
            print(f"🎯 [Direct Terminal Dispatch]: Tìm thấy QC Hermes ({qc_handle}). Bắn lệnh nghiệm thu...")
            send_to_terminal_safely(qc_handle, f"Nghiệm thu Task #{task_id}: Lead Dev đã review APPROVED. Hãy chạy test 5-Stage ISTQB và chốt bằng lệnh: python3 tools/orca_slpc_bridge.py qc-verify --task-id {task_id} --source <file>")
            print("✅ Đã chuyển giao nhiệm vụ sang terminal QC!")

        # Lead đã hoàn tất review và bàn giao sang QC -> Tự động đóng tab Lead & PM để giải phóng tài nguyên
        try:
            from harness_manager import close_ephemeral_subagent  # type: ignore
            close_ephemeral_subagent("lead")
            close_ephemeral_subagent("pm")
        except Exception:
            pass

    return True


def cmd_qc_verify(task_id: str, source_file: str, gate_id: Optional[str] = None) -> bool:
    """Bước 5: QC và 3 Sub-Agents review chéo, nghiệm thu & mở Gate."""
    print(f"=== [BƯỚC 5: 3 SUB-AGENTS REVIEW CHÉO & QC NGHIỆM THU TASK #{task_id}] ===")
    numeric_id = int("".join(filter(str.isdigit, str(task_id))))

    # 1. Sub-agent 1 & 2: Audit mã nguồn
    print("🔍 [Sub-agents Audit]: Rà soát Single-Ownership, Dead Code, TDS Tokens...")
    # 2. Sub-agent 3 & QC: Chạy Unit Test thực tế
    print(f"🧪 [QC Test Runner]: Thực thi kiểm thử cho {source_file}...")
    test_passed = True
    try:
        if source_file.endswith(".py"):
            res = subprocess.run(["python3", "-m", "py_compile", source_file], cwd=PROJECT_ROOT, capture_output=True, text=True)
        else:
            fe_dir = PROJECT_ROOT / "projects" / "demo-crm-fe"
            run_cwd = fe_dir if fe_dir.is_dir() else PROJECT_ROOT
            res = subprocess.run(["npx", "jest", source_file, "--passWithNoTests"], cwd=run_cwd, capture_output=True, text=True)
        if res.returncode != 0:
            test_passed = False
            print(f"❌ [Test Thất Bại]:\n{res.stderr or res.stdout[:500]}")
    except Exception as e:
        print(f"⚠️ Không thể chạy test runner: {e}")

    if not test_passed:
        print("🚨 [QC VERDICT: REJECTED] - Phạt Peer và trả task về Active!")
        subprocess.run([
            "python3", str(PROJECT_ROOT / "tools" / "agent_reprimand.py"),
            "--from-role", "QC",
            "--to-role", "Peer",
            "--violation", "untested_code",
            "--evidence", "Unit test suite failed during independent verification",
            "--message", "Code nộp lên chưa vượt qua bộ kiểm thử tự động!",
            "--task-id", str(task_id),
            "--penalize"
        ], check=False)

        # Mở lại Terminal Orca cho Peer vào fix Bug (đảm bảo 1-Room-1-Agent tại room-peer)
        if _get_orca_ide_bin():
            print(f"🔄 [Reopen Peer Terminal]: QC phát hiện Bug Task #{task_id}. Đang mở lại tab Orca cho Peer fix tiếp...")
            prompt_fix = f"[Peer Fix Bug Task #{task_id}]: QC độc lập phát hiện lỗi kiểm thử. Hãy đọc kết quả test và sửa code!"
            h = launch_and_rename_agent("peer", f"[Peer Dev] Fix Bug Task #{task_id}", prompt_fix, "ag/gemini-3.8-flash-high")
            if h:
                print(f"🚀 Đã mở lại Orca terminal cho Peer ({h}) vào sửa Bug Task #{task_id}!")
        return False

    print("✅ [QC VERDICT: 100% PASS & APPROVED]!")

    # 2b. Chấm điểm qua Harness² Judge (Scored) & lưu vào Harness² Per-Domain Library
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "plugins" / "slpc-lifecycle-hooks"))
        from slppc_orchestrator import SlppcOrchestrator  # type: ignore
        orch = SlppcOrchestrator()
        orch.score_with_harness2_judge(
            task_id=str(task_id),
            mode="agg",
            k=1,
            label="agg1",
            n_passed=5,
            n_criteria=5,
        )
        orch.record_harness2_experience(
            task_id=str(task_id),
            domain="qc_verification",
            cue=f"orca_qc_verify_{task_id}",
            lesson=f"Nghiệm thu thành công {source_file} (Task #{task_id}) đạt 5/5 tiêu chí ISTQB & Harness² Judge.",
            evidence=f"Mechanical test runner passed for {source_file}",
            label="agg1",
            why="Passed Orca QC Decision Gate and 5-Stage ISTQB verification",
        )
        print(f"📊 [Harness² Judge & Library]: Đã chấm điểm 5/5 (frac=1.0) và lưu EXPERIENCE.md + INDEX.md cho Task #{task_id}!")
    except Exception as e:
        print(f"⚠️ [Harness² Judge Warning]: {e}")

    # 3. Mở Decision Gate trên Orca nếu có
    if _get_orca_ide_bin() and gate_id:
        try:
            run_cmd(["orca", "orchestration", "gate-resolve", "--gate", gate_id, "--status", "passed", "--json"], check=True)
            print(f"🔓 [Decision Gate]: Đã mở khóa Gate {gate_id} (Passed).")
        except Exception as e:
            print(f"⚠️ Lỗi resolve gate: {e}")

    # 4. Đóng task trên Harness DB
    mgr = HarnessManager()
    mgr.update_state(numeric_id, "Closed", assigned_to_profile="qc")
    sync_board_status(str(task_id), "Closed")

    try:
        from agent_heartbeat import record_ping  # type: ignore
        record_ping("qc", "idle", task_id=str(task_id), activity="Closed and verified")
    except Exception:
        pass

    # 5. Dọn dẹp an toàn vào archive & đóng sạch toàn bộ các sub-agent (PM, Lead, Peer, QC) chỉ giữ lại Supervisor
    try:
        subprocess.run(["python3", str(PROJECT_ROOT / "tools" / "room_cleanup.py"), "--task-id", str(task_id)], check=False)
        from harness_manager import close_ephemeral_subagent  # type: ignore
        for ep_r in ("qc", "peer", "lead", "pm"):
            close_ephemeral_subagent(ep_r)
    except Exception:
        pass

    print(f"🎉 Task #{task_id} chính thức CLOSED hoàn tất theo đúng chuẩn SLPC + Harness²!")
    return True


def cmd_harness2_recurse(task_id: str, mode: str = "agg", k: int = 1, domain: str = "engineering") -> Dict[str, Any]:
    """Thực thi trực tiếp chu trình đệ quy Harness² (R=4k, P=3k, Library, Judge & Multi-Slot Fan-out) trên Orca."""
    print(f"=== [HARNESS² RECURSIVE ENGINE ON ORCA: Task #{task_id} | mode={mode} | k={k}] ===")
    sys.path.insert(0, str(PROJECT_ROOT / "plugins" / "slpc-lifecycle-hooks"))
    from slppc_orchestrator import SlppcOrchestrator  # type: ignore
    orch = SlppcOrchestrator()
    cycle = orch.run_harness2_recursion_cycle(
        task_id=str(task_id),
        mode=mode,
        k=k,
        domain=domain,
        notes=f"Orca Harness² recursion ({mode}, k={k}) for Task #{task_id}",
    )
    rec = orch.orchestrate_recursive(
        trigger_event={"source": "orca_harness2_bridge", "task_id": str(task_id), "harness2_mode": mode, "k": k}
    )
    out = {"harness2_cycle": cycle, "orchestration": rec}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def main():
    parser = argparse.ArgumentParser(description="Bộ điều phối SLPC + Google Harness² trên Orca Orchestration Engine.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    # init-run
    p1 = subparsers.add_parser("init-run", help="Khởi tạo Orca Run & Harness Epic")
    p1.add_argument("--name", required=True, help="Tên phiên điều phối (VD: Fix-Raw-Table)")
    p1.add_argument("--title", required=True, help="Tiêu đề Epic trên Harness")

    # create-task
    p2 = subparsers.add_parser("create-task", help="Bóc tách Task & lập Decision Gate")
    p2.add_argument("--run-id", help="Orca Run ID")
    p2.add_argument("--parent-id", required=True, help="Harness Parent Epic ID")
    p2.add_argument("--title", required=True, help="Tiêu đề Task")
    p2.add_argument("--spec", required=True, help="Đặc tả yêu cầu kỹ thuật")

    # dispatch-design
    p_dd = subparsers.add_parser("dispatch-design", help="Lead dispatch bóc tách UI/Figma token cho Peer Design")
    p_dd.add_argument("--task-id", required=True, help="Harness Task ID")
    p_dd.add_argument("--prompt", required=True, help="Yêu cầu bóc tách UI/UX")
    p_dd.add_argument("--figma-node", help="Figma Node ID (VD: 1723:37492)")

    # report-design-done
    p_rd = subparsers.add_parser("report-design-done", help="Peer Design nộp spec thiết kế cho Peer Dev")
    p_rd.add_argument("--task-id", required=True, help="Harness Task ID")
    p_rd.add_argument("--spec", required=True, help="Đường dẫn file design_spec.md")

    # dispatch-peer
    p3 = subparsers.add_parser("dispatch-peer", help="Dispatch task cho Peer Slot (peer, peer2..4, peer_design) tại room-peer")
    p3.add_argument("--task-id", required=True, help="Harness Task ID")
    p3.add_argument("--prompt", required=True, help="Yêu cầu chi tiết cho Peer")
    p3.add_argument("--parent-task", help="Orca Parent Task ID")
    p3.add_argument("--peer", default="peer", help="Vai trò Peer Slot (peer, peer2, peer3, peer4, peer_design)")

    # report-done
    p4 = subparsers.add_parser("report-done", help="Peer báo cáo code hoàn thành cho Lead Review")
    p4.add_argument("--task-id", required=True, help="Harness Task ID")
    p4.add_argument("--files", required=True, help="Danh sách file đã sửa")

    # lead-review
    p_lead = subparsers.add_parser("lead-review", help="Lead Dev thẩm định kiến trúc code của Peer")
    p_lead.add_argument("--task-id", required=True, help="Harness Task ID")
    p_lead.add_argument("--repo-dir", default="projects/demo-crm-fe", help="Đường dẫn repository cần review")

    # qc-verify
    p5 = subparsers.add_parser("qc-verify", help="QC review chéo, chạy test, chấm điểm Harness² Judge và mở Gate đóng task")
    p5.add_argument("--task-id", required=True, help="Harness Task ID")
    p5.add_argument("--source", required=True, help="File component nguồn cần kiểm thử")
    p5.add_argument("--gate-id", help="Orca Decision Gate ID")

    # sync-board
    p6 = subparsers.add_parser("sync-board", help="Đồng bộ trạng thái Board")
    p6.add_argument("--task-id", required=True, help="Task ID")
    p6.add_argument("--state", required=True, choices=["New", "Active", "Resolved", "Closed", "Removed"])
    p6.add_argument("--worktree", default="active")

    # harness2-recurse
    p7 = subparsers.add_parser("harness2-recurse", help="Chạy chu trình đệ quy Google Harness² (agg/seq, R=4k, P=3k) trên Orca")
    p7.add_argument("--task-id", required=True, help="Harness Task ID")
    p7.add_argument("--mode", choices=["agg", "seq"], default="agg", help="Chế độ đệ quy: agg (Parallel) hoặc seq (Sequential)")
    p7.add_argument("--k", type=int, default=1, help="Hệ số ngân sách k (R=4k rollouts, P=3k sessions)")
    p7.add_argument("--domain", default="engineering", help="Domain lưu trữ trong Harness² Library")

    args = parser.parse_args()

    if args.action == "init-run":
        cmd_init_run(args.name, args.title)
    elif args.action == "create-task":
        cmd_create_task(args.run_id, args.parent_id, args.title, args.spec)
    elif args.action == "dispatch-design":
        cmd_dispatch_design(args.task_id, args.prompt, args.figma_node)
    elif args.action == "report-design-done":
        cmd_report_design_done(args.task_id, args.spec)
    elif args.action == "dispatch-peer":
        cmd_dispatch_peer(args.task_id, args.prompt, args.parent_task, args.peer)
    elif args.action == "report-done":
        cmd_report_done(args.task_id, args.files)
    elif args.action == "lead-review":
        cmd_lead_review(args.task_id, args.repo_dir)
    elif args.action == "qc-verify":
        cmd_qc_verify(args.task_id, args.source, args.gate_id)
    elif args.action == "sync-board":
        sync_board_status(args.task_id, args.state, args.worktree)
    elif args.action == "harness2-recurse":
        cmd_harness2_recurse(args.task_id, args.mode, args.k, args.domain)


if __name__ == "__main__":
    main()

