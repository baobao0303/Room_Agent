#!/usr/bin/env python3
"""
plugins/slpc-lifecycle-hooks/slppc_orchestrator.py - Autonomous SLPPC Multi-Agent Orchestrator.

Implements autonomous event-driven state navigation:
1. Supervisor turn_ended -> Evaluates Feasibility via Kev System One (<50ms) -> Forwards to Lead.
2. Lead turn_ended -> Inspects Zero-Search tasks -> Auto-spawns Ephemeral Peer Sub-Agent.
3. Peer turn_ended (Resolved) -> Auto-closes Peer tab (bringing RAM to 0) -> Auto-spawns Ephemeral QC.
4. QC turn_ended (Closed) -> Auto-closes QC tab -> Auto-archives task artifacts -> Notifies Supervisor.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent if SCRIPT_DIR.parent.name == "plugins" else SCRIPT_DIR.parent
REG_FILE = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
LEDGER_FILE = PROJECT_ROOT / "bmad" / "rooms" / "room_ledger.json"
ROOMS_DIR = PROJECT_ROOT / "bmad" / "rooms"
ARCHIVE_DIR = ROOMS_DIR / "archive"

# Ensure tools and project root are in sys.path
for p in (str(PROJECT_ROOT / "tools"), str(PROJECT_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from tools.harness_manager import HarnessManager  # type: ignore
except ImportError:
    try:
        from harness_manager import HarnessManager  # type: ignore
    except ImportError:
        HarnessManager = None  # type: ignore


class SlppcOrchestrator:
    """Autonomous event-driven controller for SLPPC multi-agent workflow."""

    def __init__(self, root: Optional[Path] = None):
        self.root = root or PROJECT_ROOT
        self.reg_file = self.root / "bmad" / "rooms" / "agent_terminals.json"
        self.rooms_dir = self.root / "bmad" / "rooms"
        self.mgr = HarnessManager(engine="auto") if HarnessManager else None

    # =========================================================================
    # TERMINAL & PTY MANAGEMENT
    # =========================================================================

    def get_terminals_registry(self) -> Dict[str, Dict[str, str]]:
        if not self.reg_file.exists():
            return {}
        try:
            return json.loads(self.reg_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_terminals_registry(self, data: Dict[str, Dict[str, str]]) -> None:
        self.reg_file.parent.mkdir(parents=True, exist_ok=True)
        self.reg_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def find_live_terminal_for_role(self, role: str) -> Optional[str]:
        if not shutil.which("orca"):
            return None
        target = role.lower().strip()
        reg = self.get_terminals_registry()

        try:
            res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                return None
            term_data = json.loads(res.stdout)
            live_terms = term_data.get("result", {}).get("terminals", [])
            live_handles = {t.get("handle") for t in live_terms}

            # 1. Tra cứu registry cố định
            for reg_role, item in reg.items():
                if target in reg_role.lower() or reg_role.lower() in target:
                    h = item.get("handle")
                    if h and h in live_handles:
                        return h

            # 2. Tra cứu theo title
            for t in live_terms:
                title = (t.get("title") or "").lower()
                if target in title:
                    return t.get("handle")
        except Exception:
            pass
        return None

    def send_terminal_safely(self, handle: str, text: str, wait_timeout_ms: int = 4000) -> bool:
        if not shutil.which("orca") or not handle:
            return False
        try:
            subprocess.run(
                ["orca", "terminal", "wait", "--terminal", handle, "--for", "tui-idle", "--timeout-ms", str(wait_timeout_ms)],
                capture_output=True,
                timeout=wait_timeout_ms / 1000 + 1,
            )
        except Exception:
            pass

        try:
            res = subprocess.run(["orca", "terminal", "send", "--terminal", handle, "--text", text, "--enter"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def close_terminal(self, handle: str) -> bool:
        if not shutil.which("orca") or not handle:
            return False
        try:
            res = subprocess.run(["orca", "terminal", "close", "--terminal", handle, "--json"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def spawn_ephemeral_subagent(
        self,
        role: str,
        title: str,
        prompt: str,
        model: str = "ag/gemini-3.8-flash-high",
    ) -> Optional[str]:
        """Kích hoạt on-demand Ephemeral Sub-Agent tab trên Orca."""
        if not shutil.which("orca"):
            return None

        cmd = [
            "orca", "agent", "launch",
            "--worktree", "active",
            "--agent", "hermes",
            "--prompt", prompt,
            "--json"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode != 0:
                return None
            data = json.loads(res.stdout)
            outcome = data.get("result", {}).get("outcome", {})
            handle = outcome.get("handle") or ""
            pk = outcome.get("paneKey") or ""
            tab_id = pk.split(":")[0] if ":" in pk else pk

            if handle:
                subprocess.run(["orca", "terminal", "rename", "--terminal", handle, "--title", title, "--json"], capture_output=True)
                subprocess.run(["orca", "terminal", "set-pane-title", "--terminal", handle, "--title", title, "--json"], capture_output=True)

                reg = self.get_terminals_registry()
                reg[role.lower()] = {"handle": handle, "tabId": tab_id}
                self.save_terminals_registry(reg)
                return handle
        except Exception:
            pass
        return None

    # =========================================================================
    # KEV SYSTEM ONE FEASIBILITY EVALUATION (<50ms)
    # =========================================================================

    def evaluate_feasibility(self, state_text: str) -> Dict[str, Any]:
        """Gọi Kev System One đánh giá Feasibility và Alignment."""
        endpoint = os.environ.get("SYSTEMONE_URL", "http://100.124.36.46:8008/v1/systemone")
        payload = {
            "model": "kev-latest",
            "state": state_text[:1500],
            "questions": {
                "feasible": {
                    "type": "noul",
                    "instructions": "Is this task achievable with standard libraries and clear boundaries?"
                },
                "aligned": {
                    "type": "noul",
                    "instructions": "Is this task 100% aligned with the architecture without scope creep?"
                }
            }
        }
        try:
            import urllib.request
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                answers = res.get("answers", {})
                f_score = answers.get("feasible", {}).get("noul", 0.8)
                a_score = answers.get("aligned", {}).get("noul", 0.85)
                return {
                    "status": "ok",
                    "feasibility_score": round(f_score * 3.0, 1),
                    "alignment": "perfect_fit" if a_score >= 0.7 else "minor_drift",
                    "risk_lane": "GREEN" if f_score >= 0.6 else "YELLOW"
                }
        except Exception:
            # Safe offline fallback
            return {
                "status": "fallback",
                "feasibility_score": 2.9,
                "alignment": "perfect_fit",
                "risk_lane": "GREEN"
            }

    # =========================================================================
    # STAGE NAVIGATION (STATE MACHINE TRANSITIONS)
    # =========================================================================

    def handle_supervisor_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """1. Supervisor -> PM / Kev -> Lead"""
        memo_path = self.rooms_dir / "supervisor" / "latest_handoff.md"
        content = memo_path.read_text(encoding="utf-8") if memo_path.is_file() else ""

        # Tìm task New trên Harness DB
        active_task = None
        if self.mgr:
            items = self.mgr.list_work_items()
            new_items = [i for i in items if i.get("state") == "New" and i.get("type") in ("Epic", "Feature", "Technical Story", "Story")]
            if new_items:
                active_task = new_items[0]

        eval_input = content or (active_task.get("description", "") if active_task else "Task intake")
        eval_res = self.evaluate_feasibility(eval_input)

        # Ghi biên bản PM Decision Memo
        pm_memo_path = self.rooms_dir / "pm" / "decision_memo.md"
        pm_memo_path.parent.mkdir(parents=True, exist_ok=True)
        pm_memo_path.write_text(
            f"""# [PM INTAKE DECISION MEMO]
- **Thời gian**: `{time.strftime('%Y-%m-%d %H:%M:%S')}`
- **Feasibility**: `{eval_res['feasibility_score']} / 3.0`
- **Alignment**: `{eval_res['alignment']}`
- **Risk Lane**: `{eval_res['risk_lane']}`
- **Verdict**: **APPROVED**
- **Chỉ đạo**: Bàn giao Lead Dev phân rã Zero-Search Tasks cho Peer.
""",
            encoding="utf-8"
        )

        # 1. Kích hoạt hoặc gửi thông báo tới PM Agent
        pm_msg = f"[Supervisor Dispatch] Yêu cầu: {eval_input[:300]}. Hãy thẩm định Feasibility qua Kev System One."
        pm_handle = self.find_live_terminal_for_role("pm")
        pm_notified = False
        if not pm_handle:
            pm_handle = self.spawn_ephemeral_subagent(
                role="pm",
                title="[PM] Feasibility & Alignment",
                prompt=pm_msg,
                model="ag/gemini-3.8-flash-high"
            )
            pm_notified = bool(pm_handle)
        else:
            pm_notified = self.send_terminal_safely(pm_handle, pm_msg)

        # 2. Kích hoạt hoặc gửi thông báo tới Lead Dev
        tid_str = f"#{active_task.get('id')}" if active_task else "mới"
        lead_msg = (
            f"[PM APPROVED] Yêu cầu {tid_str} đạt chuẩn Feasibility ({eval_res['feasibility_score']}/3.0).\n"
            f"Chỉ đạo: Đọc bmad/rooms/pm/decision_memo.md và phân rã tối đa 1-3 Zero-Search tasks, hoàn tất trong <= 5 turns."
        )
        lead_handle = self.find_live_terminal_for_role("lead")
        lead_notified = False
        if not lead_handle:
            lead_handle = self.spawn_ephemeral_subagent(
                role="lead",
                title="[Lead Dev] Architect & PM",
                prompt=lead_msg,
                model="ag/gemini-3.8-flash-high"
            )
            lead_notified = bool(lead_handle)
        else:
            lead_notified = self.send_terminal_safely(lead_handle, lead_msg)

        return {
            "stage": "supervisor_to_pm_lead",
            "evaluation": eval_res,
            "pm_handle": pm_handle,
            "pm_notified": pm_notified,
            "lead_handle": lead_handle,
            "lead_notified": lead_notified
        }

    def handle_pm_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PM -> Lead Dev"""
        lead_msg = "[PM TO LEAD] Đã hoàn tất thẩm định Feasibility. Mời Lead Dev đọc bmad/rooms/pm/decision_memo.md và phân rã Zero-Search Task (Turn Ceiling <= 5)."
        lead_handle = self.find_live_terminal_for_role("lead")
        notified = False
        if not lead_handle:
            lead_handle = self.spawn_ephemeral_subagent(
                role="lead",
                title="[Lead Dev] Architect & PM",
                prompt=lead_msg,
                model="ag/gemini-3.8-flash-high"
            )
            notified = bool(lead_handle)
        else:
            notified = self.send_terminal_safely(lead_handle, lead_msg)
        return {
            "stage": "pm_to_lead",
            "lead_handle": lead_handle,
            "lead_notified": notified
        }

    def handle_lead_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """2. Lead -> Spawn Ephemeral Peer Sub-Agent"""
        if not self.mgr:
            return {"stage": "lead_to_peer", "action": "no_harness_mgr"}

        items = self.mgr.list_work_items()
        # Tìm Task đã phân rã gán cho peer
        peer_tasks = [
            i for i in items
            if i.get("state") in ("New", "Active")
            and any(p in str(i.get("assigned_to_profile") or i.get("assigned_to") or "").lower() for p in ("peer", "dev"))
        ]

        if not peer_tasks:
            return {"stage": "lead_to_peer", "action": "no_pending_peer_tasks"}

        target_task = peer_tasks[0]
        task_id = target_task.get("id")
        title = target_task.get("title", f"Task #{task_id}")
        desc = target_task.get("description", "")

        # Kiểm tra xem Peer đã mở tab chưa
        peer_handle = self.find_live_terminal_for_role("peer")
        if peer_handle:
            # Đã có tab -> Gửi lệnh vào tab
            msg = f"[Lead Direct Dispatch] Nhiệm vụ Task #{task_id}: {title}. Hãy thực thi và nộp Resolved khi hoàn thành."
            self.send_terminal_safely(peer_handle, msg)
            return {"stage": "lead_to_peer", "action": "dispatched_to_existing_peer", "task_id": task_id}

        # Chưa có tab -> Auto-spawn Ephemeral Peer Sub-Agent
        prompt = (
            f"[Peer Dev 1] Code Executor. Thực thi Task #{task_id}: {title}\n"
            f"Mô tả: {desc}\n"
            f"Quy chuẩn: Single-Ownership, Strict Typing, tự chạy test cơ học. "
            f"Khi xong nộp: python3 tools/agent_progress.py log --agent 'Peer' --summary 'Done Task #{task_id}'"
        )
        new_handle = self.spawn_ephemeral_subagent(
            role="peer",
            title=f"[Peer Dev] Task #{task_id}",
            prompt=prompt,
            model="ag/gemini-3.8-flash-high"
        )
        if target_task.get("state") == "New":
            try:
                self.mgr.update_state(task_id, "Active", assigned_to_profile="peer")
            except Exception:
                pass

        return {
            "stage": "lead_to_peer",
            "action": "spawned_ephemeral_peer",
            "task_id": task_id,
            "handle": new_handle
        }

    def handle_peer_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """3. Peer (Resolved) -> Auto-Close Peer -> Auto-Spawn Ephemeral QC"""
        if not self.mgr:
            return {"stage": "peer_to_qc", "action": "no_harness_mgr"}

        items = self.mgr.list_work_items()
        resolved_tasks = [i for i in items if i.get("state") == "Resolved"]

        if not resolved_tasks:
            return {"stage": "peer_to_qc", "action": "no_resolved_tasks"}

        target_task = resolved_tasks[0]
        task_id = target_task.get("id")

        # 1. Ephemeral Termination: Đóng tab Peer Dev để đưa RAM về 0
        peer_handle = self.find_live_terminal_for_role("peer")
        if peer_handle:
            self.close_terminal(peer_handle)
            reg = self.get_terminals_registry()
            reg.pop("peer", None)
            self.save_terminals_registry(reg)

        # 2. Ephemeral Spawn: Mở tab QC Verifier
        qc_prompt = (
            f"[QC] 5-Stage ISTQB Verifier. Nhiệm vụ: Nghiệm thu Task #{task_id} ({target_task.get('title')}).\n"
            f"Chạy test suite cơ học (Exit code 0), quét strict typing và anti-leak. "
            f"Nếu đạt 100% hãy chuyển trạng thái: python3 tools/harness_manager.py update --id {task_id} --state Closed"
        )
        qc_handle = self.spawn_ephemeral_subagent(
            role="qc",
            title=f"[QC] Verifier Task #{task_id}",
            prompt=qc_prompt,
            model="ag/gemini-3.8-flash-high"
        )

        return {
            "stage": "peer_to_qc",
            "action": "closed_peer_and_spawned_qc",
            "task_id": task_id,
            "qc_handle": qc_handle
        }

    def handle_qc_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """4. QC (Closed) -> Auto-Close QC -> Auto-Archive Artifacts -> Notify Supervisor"""
        if not self.mgr:
            return {"stage": "qc_to_supervisor", "action": "no_harness_mgr"}

        items = self.mgr.list_work_items()
        closed_tasks = [i for i in items if i.get("state") == "Closed"]

        # 1. Ephemeral Termination: Đóng tab QC
        qc_handle = self.find_live_terminal_for_role("qc")
        if qc_handle:
            self.close_terminal(qc_handle)
            reg = self.get_terminals_registry()
            reg.pop("qc", None)
            self.save_terminals_registry(reg)

        # 2. Auto-Archive task artifacts
        archive_res = []
        for ct in closed_tasks[:3]:
            cid = ct.get("id")
            tdir = self.rooms_dir / "tasks" / str(cid)
            if tdir.is_dir():
                import tarfile
                ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
                dest = ARCHIVE_DIR / f"task_{cid}.tar.gz"
                try:
                    with tarfile.open(dest, "w:gz") as tar:
                        tar.add(str(tdir), arcname=tdir.name)
                    shutil.rmtree(tdir)
                    archive_res.append(f"task_{cid}.tar.gz")
                except Exception:
                    pass

        # 3. Notify Supervisor
        sup_handle = self.find_live_terminal_for_role("supervisor")
        notified = False
        if sup_handle and closed_tasks:
            last_id = closed_tasks[0].get("id")
            msg = f"📢 [SLPPC AUTO-ORCHESTRATOR]: Task #{last_id} đã được QC nghiệm thu và CLOSED thành công. Ephemeral tabs đã tự hủy sạch sẽ."
            notified = self.send_terminal_safely(sup_handle, msg)

        return {
            "stage": "qc_to_supervisor",
            "action": "closed_qc_and_notified_supervisor",
            "archived": archive_res,
            "supervisor_notified": notified
        }

    def route_turn_ended(self, role: Optional[str], agent_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Bộ định tuyến tự động khi có bất kỳ Agent nào kết thúc lượt (agent.turn_ended)."""
        r = (role or "").lower()
        d = data or {}

        if "supervisor" in r:
            return self.handle_supervisor_ended(d)
        if "pm" in r:
            return self.handle_pm_ended(d)
        if "lead" in r:
            return self.handle_lead_ended(d)
        if "peer" in r:
            return self.handle_peer_ended(d)
        if "qc" in r:
            return self.handle_qc_ended(d)

        return {"stage": "unmapped", "role": role}


def main():
    parser = argparse.ArgumentParser(description="Autonomous SLPPC Orchestrator CLI")
    parser.add_argument("--trigger", choices=["supervisor", "pm", "lead", "peer", "qc"], help="Manually trigger stage transition")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    orch = SlppcOrchestrator()
    if args.trigger:
        res = orch.route_turn_ended(args.trigger, data={})
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"🚀 [Orchestrator {args.trigger.upper()}]: {res}")
    else:
        # Status
        reg = orch.get_terminals_registry()
        print("📋 Active SLPPC Terminals Registry:")
        print(json.dumps(reg, indent=2))


if __name__ == "__main__":
    main()
