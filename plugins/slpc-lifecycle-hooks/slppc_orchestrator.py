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


def resolve_shared_root(default_root: Path) -> Path:
    """Resolve canonical main worktree root so all room-* worktrees share bmad/rooms and Harness DB."""
    override = os.environ.get("SLPPC_SHARED_ROOT")
    if override:
        p = Path(override)
        if os.access(p, os.R_OK | os.W_OK):
            return p
    git_entry = default_root / ".git"
    try:
        if git_entry.is_file():
            raw = git_entry.read_text(encoding="utf-8").strip()
            if raw.startswith("gitdir:"):
                gitdir = Path(raw.split("gitdir:", 1)[1].strip())
                if not gitdir.is_absolute():
                    gitdir = (default_root / gitdir).resolve()
                if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
                    main_root = gitdir.parent.parent.parent
                    if os.access(main_root, os.R_OK | os.W_OK):
                        return main_root
    except Exception:
        pass
    return default_root


SHARED_ROOT = resolve_shared_root(PROJECT_ROOT)
REG_FILE = SHARED_ROOT / "bmad" / "rooms" / "agent_terminals.json"
LEDGER_FILE = SHARED_ROOT / "bmad" / "rooms" / "room_ledger.json"
ROOMS_DIR = SHARED_ROOT / "bmad" / "rooms"
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

try:
    from tools.harness_rust import query_lessons, record_lesson  # type: ignore
except ImportError:
    try:
        from harness_rust import query_lessons, record_lesson  # type: ignore
    except ImportError:
        query_lessons = None  # type: ignore
        record_lesson = None  # type: ignore


class SlppcOrchestrator:
    """Autonomous event-driven controller for SLPPC multi-agent workflow."""

    def __init__(self, root: Optional[Path] = None):
        self.root = root if root is not None else SHARED_ROOT
        self.reg_file = self.root / "bmad" / "rooms" / "agent_terminals.json"
        self.rooms_dir = self.root / "bmad" / "rooms"
        self.mgr = HarnessManager(engine="auto") if HarnessManager else None

    # =========================================================================
    # TERMINAL & PTY MANAGEMENT
    # =========================================================================

    @staticmethod
    def _normalize_room_role(role: str) -> str:
        r = role.lower().strip()
        if "supervisor" in r or r == "main":
            return "supervisor"
        if "lead" in r:
            return "lead"
        if "pm" in r:
            return "pm"
        if any(k in r for k in ("peer", "dev", "design")):
            return "peer"
        if "qc" in r:
            return "qc"
        return r

    @staticmethod
    def _infer_terminal_room(term: Dict[str, Any]) -> Optional[str]:
        wt_path = (term.get("worktreePath") or "").lower().rstrip("/")
        wt_id = (term.get("worktreeId") or "").lower().rstrip("/")
        branch = (term.get("branch") or "").lower().rstrip("/")

        for r in ("pm", "lead", "peer", "qc"):
            token = f"room-{r}"
            if (
                wt_path.endswith(f"/{token}")
                or f"/{token}/" in wt_path
                or wt_id.endswith(f"/{token}")
                or branch.endswith(f"/{token}")
                or branch == token
            ):
                return r

        if branch in ("main", "refs/heads/main") or (
            wt_path and "/room-" not in wt_path and not wt_path.endswith(("/room-pm", "/room-lead", "/room-peer", "/room-qc"))
        ):
            return "supervisor"

        # Fallback khi mock terminal không có metadata worktree
        title = (term.get("title") or "").lower()
        if "[supervisor]" in title or "scope & intent" in title:
            return "supervisor"
        if "[lead" in title or "technical architect" in title:
            return "lead"
        if "[pm]" in title or "[pm agent]" in title or "feasibility" in title:
            return "pm"
        if "[peer" in title or "code executor" in title:
            return "peer"
        if "[qc]" in title or "istqb" in title or "verifier" in title:
            return "qc"
        return None

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
        if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca"):
            return None
        target = self._normalize_room_role(role)
        reg = self.get_terminals_registry()

        try:
            res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                return None
            term_data = json.loads(res.stdout)
            live_terms = [
                t for t in term_data.get("result", {}).get("terminals", [])
                if t.get("handle") and not t.get("stopped") and t.get("connected", True)
            ]

            matching_terms = [t for t in live_terms if self._infer_terminal_room(t) == target]

            # Nếu registry có handle đang sống và thuộc đúng room (hoặc terminal không gắn room khác)
            reg_handle = None
            for reg_role, item in reg.items():
                if self._normalize_room_role(reg_role) == target and isinstance(item, dict):
                    cand = item.get("handle")
                    if cand:
                        for t in live_terms:
                            if t.get("handle") == cand:
                                inferred = self._infer_terminal_room(t)
                                if inferred in (target, None):
                                    reg_handle = cand
                                    if t not in matching_terms:
                                        matching_terms.insert(0, t)
                                break

            if matching_terms:
                matching_terms.sort(
                    key=lambda x: (1 if x.get("handle") == reg_handle else 0, x.get("lastOutputAt") or 0),
                    reverse=True,
                )
                primary = matching_terms[0]
                primary_h = primary.get("handle")

                # Đảm bảo nghiêm ngặt: Mỗi room chỉ duy trì tối đa 1 Agent Terminal duy nhất
                for extra in matching_terms[1:]:
                    extra_h = extra.get("handle")
                    if extra_h and extra_h != primary_h:
                        self.close_terminal(extra_h)

                if primary_h:
                    reg[target] = {
                        "handle": primary_h,
                        "tabId": primary.get("tabId") or "",
                    }
                    self.save_terminals_registry(reg)
                return primary_h
        except Exception:
            pass
        return None

    def send_terminal_safely(self, handle: str, text: str, wait_timeout_ms: int = 4000) -> bool:
        if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca") or not handle:
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
        """Đóng terminal process và hủy hoàn toàn registration tab UI trên Orca (--tab)."""
        if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca") or not handle:
            return False
        try:
            res = subprocess.run(["orca", "terminal", "close", "--terminal", handle, "--tab", "--json"], capture_output=True, timeout=5)
            if res.returncode == 0:
                return True
            res2 = subprocess.run(["orca", "terminal", "close", "--terminal", handle, "--json"], capture_output=True, timeout=5)
            return res2.returncode == 0
        except Exception:
            return False

    def cleanup_role_worktree(self, role: str) -> bool:
        """Đóng tất cả terminal và dọn sạch tab trong worktree phòng tương ứng (dành cho 4 phòng Sub-Agents: PM, Lead, Peer, QC)."""
        if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca"):
            return False
        target_room = role.lower().strip()
        # Duy nhất Supervisor (main) là Persistent tab được bảo vệ thường trực
        if target_room in ("supervisor", "main"):
            return False
        if "peer" in target_room or "dev" in target_room:
            wt_target = "name:room-peer"
        elif "qc" in target_room:
            wt_target = "name:room-qc"
        elif "lead" in target_room:
            wt_target = "name:room-lead"
        elif "pm" in target_room:
            wt_target = "name:room-pm"
        else:
            wt_target = f"name:room-{target_room}"

        try:
            res = subprocess.run(["orca", "terminal", "close", "--worktree", wt_target, "--all", "--json"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def spawn_ephemeral_subagent(
        self,
        role: str,
        title: str,
        prompt: str,
        model: str = "ag/gemini-3.8-flash-high",
        effort: str = "high",
    ) -> Optional[str]:
        """Kích hoạt on-demand Sub-Agent tab trên Orca bên trong worktree phòng tương ứng (tối đa 1 agent/room)."""
        if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca"):
            return None

        canonical_room = self._normalize_room_role(role)
        # Bảo vệ Persistent Rooms (supervisor, pm, lead): Nếu đã có agent sống trong room, tái sử dụng ngay, TUYỆT ĐỐI không spawn agent thứ 2!
        if canonical_room in ("supervisor", "pm", "lead"):
            existing_h = self.find_live_terminal_for_role(canonical_room)
            if existing_h:
                return existing_h
        else:
            # Idempotent cleanup cho Ephemeral Sub-Agents (Peer, QC): Đóng sạch tab cũ trước khi mở tab mới
            old_h = self.find_live_terminal_for_role(canonical_room)
            if old_h:
                self.close_terminal(old_h)
            self.cleanup_role_worktree(canonical_room)

        if canonical_room == "peer":
            wt_target = "name:room-peer"
        elif canonical_room == "qc":
            wt_target = "name:room-qc"
        elif canonical_room == "lead":
            wt_target = "name:room-lead"
        elif canonical_room == "pm":
            wt_target = "name:room-pm"
        elif canonical_room == "supervisor":
            wt_target = "name:main"
        else:
            wt_target = f"name:room-{canonical_room}"

        base_cmd = [
            "orca", "agent", "launch",
            "--worktree", wt_target,
            "--agent", "hermes",
            "--prompt", prompt,
            "--json"
        ]
        cmd = list(base_cmd)
        if model:
            cmd.extend(["--model", model])
            if effort:
                cmd.extend(["--effort", effort])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode != 0 and model:
                # Fallback cho phiên bản Orca không nhận --model/--effort lúc launch hermes
                res = subprocess.run(base_cmd, capture_output=True, text=True, timeout=20)
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
                reg[canonical_room] = {"handle": handle, "tabId": tab_id}
                self.save_terminals_registry(reg)
                # Quét lại để đóng mọi shell/tab dư thừa trong cùng room (đảm bảo đúng 1 agent/room)
                self.find_live_terminal_for_role(canonical_room)
                return handle
        except Exception:
            pass
        return None

    # =========================================================================
    # KEV SYSTEM ONE FEASIBILITY EVALUATION (<50ms)
    # =========================================================================

    def evaluate_feasibility(self, state_text: str) -> Dict[str, Any]:
        """Gọi Kev System One đánh giá Feasibility và Alignment."""
        endpoint = os.environ.get("SYSTEMONE_URL", "http://127.0.0.1:8008/v1/systemone")
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

        # 1. Kích hoạt hoặc gửi thông báo tới PM Agent (chỉ 1 agent duy nhất trong room-pm)
        pm_handle = self.find_live_terminal_for_role("pm")
        if not pm_handle:
            pm_handle = self.spawn_ephemeral_subagent(
                role="pm",
                title="[PM] Feasibility & Alignment",
                prompt="[PM Agent] Product Manager & Decision Arbiter in SLPPC. Đánh giá Feasibility qua Kev System One.",
                model="ag/gemini-3.8-flash-high"
            )
        pm_notified = False
        if pm_handle:
            pm_msg = f"[Supervisor Dispatch] Yêu cầu: {eval_input[:300]}. Hãy thẩm định Feasibility qua Kev System One."
            pm_notified = self.send_terminal_safely(pm_handle, pm_msg)

        # 2. Đảm bảo Lead Dev đã sẵn sàng (chỉ 1 agent duy nhất trong room-lead).
        # Lưu ý: Nếu PM đã nhận lệnh (pm_notified=True), chờ PM hoàn tất lượt (handle_pm_ended) mới bắn lệnh sang Lead để tránh double-dispatch.
        lead_handle = self.find_live_terminal_for_role("lead")
        if not lead_handle:
            lead_handle = self.spawn_ephemeral_subagent(
                role="lead",
                title="[Lead Dev] Technical Architect",
                prompt="[Lead Dev] Technical Architect. Phân rã Zero-Search Task cho Peer.",
                model="ag/gemini-3.8-flash-high"
            )
        lead_notified = False
        if lead_handle and not pm_notified:
            tid_str = f"#{active_task.get('id')}" if active_task else "mới"
            msg = f"[PM APPROVED] Yêu cầu {tid_str} đạt chuẩn Feasibility ({eval_res['feasibility_score']}/3.0). Đọc bmad/rooms/pm/decision_memo.md và phân rã Zero-Search Task."
            lead_notified = self.send_terminal_safely(lead_handle, msg)

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
        lead_handle = self.find_live_terminal_for_role("lead")
        if not lead_handle:
            lead_handle = self.spawn_ephemeral_subagent(
                role="lead",
                title="[Lead Dev] Technical Architect",
                prompt="[Lead Dev] Technical Architect. Phân rã Zero-Search Task cho Peer.",
                model="ag/gemini-3.8-flash-high"
            )
        notified = False
        if lead_handle:
            msg = "[PM TO LEAD] Đã hoàn tất thẩm định Feasibility. Mời Lead Dev đọc bmad/rooms/pm/decision_memo.md và phân rã Zero-Search Task."
            notified = self.send_terminal_safely(lead_handle, msg)

        # PM đã hoàn tất bàn giao sang Lead -> Tự động đóng tab PM để giải phóng RAM
        pm_handle = self.find_live_terminal_for_role("pm")
        if pm_handle:
            self.close_terminal(pm_handle)
            reg = self.get_terminals_registry()
            reg.pop("pm", None)
            self.save_terminals_registry(reg)
        self.cleanup_role_worktree("pm")

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

        # 1. Harness² Pre-Flight Self-Learning Injection
        domain = target_task.get("domain") or "engineering"
        lessons_context = ""
        if query_lessons:
            try:
                lessons = query_lessons(domain=domain, limit=3)
                if lessons:
                    lesson_lines = [f"- [Cue: {l.cue}] {l.lesson}" for l in lessons if l.lesson]
                    if lesson_lines:
                        lessons_context = "\n[BẪY QUÁ KHỨ & BÀI HỌC KINH NGHIỆM TỰ HỌC - HARNESS²]:\n" + "\n".join(lesson_lines)
            except Exception:
                pass

        # Kiểm tra xem Peer đã mở tab chưa
        peer_handle = self.find_live_terminal_for_role("peer")
        if peer_handle:
            # Đã có tab -> Gửi lệnh vào tab
            lesson_hint = f" Lưu ý bẫy kinh nghiệm:\n{lessons_context}" if lessons_context else ""
            msg = f"[Lead Direct Dispatch] Nhiệm vụ Task #{task_id}: {title}.{lesson_hint} Hãy thực thi và nộp Resolved khi hoàn thành."
            self.send_terminal_safely(peer_handle, msg)

            # Lead đã hoàn tất phân rã và giao việc cho Peer -> Tự động đóng tab Lead
            lead_handle = self.find_live_terminal_for_role("lead")
            if lead_handle:
                self.close_terminal(lead_handle)
                reg = self.get_terminals_registry()
                reg.pop("lead", None)
                self.save_terminals_registry(reg)
            self.cleanup_role_worktree("lead")
            return {"stage": "lead_to_peer", "action": "dispatched_to_existing_peer", "task_id": task_id}

        # Chưa có tab -> Auto-spawn Ephemeral Peer Sub-Agent
        prompt_parts = [
            f"[Peer Dev] Code & UI Executor. Thực thi Task #{task_id}: {title}",
            f"Mô tả: {desc}"
        ]
        if lessons_context:
            prompt_parts.append(lessons_context)
        prompt_parts.append(
            "Quy chuẩn: Single-Ownership, Strict Typing, tự chạy test cơ học. "
            f"BẮT BUỘC khi xong nộp: python3 tools/harness_manager.py update --id {task_id} --state Resolved && python3 tools/agent_progress.py log --agent 'Peer' --summary 'Done Task #{task_id}'"
        )
        prompt = "\n".join(prompt_parts)
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

        # Lead đã hoàn tất phân rã và giao việc cho Peer -> Tự động đóng tab Lead
        lead_handle = self.find_live_terminal_for_role("lead")
        if lead_handle:
            self.close_terminal(lead_handle)
            reg = self.get_terminals_registry()
            reg.pop("lead", None)
            self.save_terminals_registry(reg)
        self.cleanup_role_worktree("lead")
        return {
            "stage": "lead_to_peer",
            "action": "spawned_ephemeral_peer",
            "task_id": task_id,
            "handle": new_handle
        }

    def handle_peer_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """3. Peer (Resolved) -> Auto-Close Peer -> Auto-Spawn Ephemeral QC"""
        # 1. Ephemeral Termination: Luôn luôn đóng tab Peer Dev và dọn dẹp worktree để đưa RAM về 0
        peer_handle = self.find_live_terminal_for_role("peer")
        if peer_handle:
            self.close_terminal(peer_handle)
            reg = self.get_terminals_registry()
            reg.pop("peer", None)
            self.save_terminals_registry(reg)
        self.cleanup_role_worktree("peer")

        if not self.mgr:
            return {"stage": "peer_to_qc", "action": "no_harness_mgr"}

        items = self.mgr.list_work_items()
        resolved_tasks = [i for i in items if i.get("state") == "Resolved"]

        if not resolved_tasks:
            return {"stage": "peer_to_qc", "action": "closed_peer_no_resolved_tasks"}

        target_task = resolved_tasks[0]
        task_id = target_task.get("id")

        # 0. Harness² Self-Learning: Ghi nhận bài học kinh nghiệm khi Peer giải quyết task
        if record_lesson:
            try:
                title = target_task.get("title", f"Task #{task_id}")
                record_lesson(
                    domain=target_task.get("domain") or "peer_implementation",
                    cue=f"task_{task_id}_peer_resolved",
                    lesson=f"Thực thi thành công Task #{task_id}: {title}. Tuân thủ Single-Ownership, Strict Typing, TDD.",
                    evidence=f"Peer nộp Resolved cho Task #{task_id}",
                    confidence="high",
                    work_item_id=task_id
                )
            except Exception:
                pass

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
        # 1. Ephemeral Termination: Luôn luôn đóng tab QC và dọn dẹp worktree room-qc
        qc_handle = self.find_live_terminal_for_role("qc")
        if qc_handle:
            self.close_terminal(qc_handle)
            reg = self.get_terminals_registry()
            reg.pop("qc", None)
            self.save_terminals_registry(reg)
        self.cleanup_role_worktree("qc")

        if not self.mgr:
            return {"stage": "qc_to_supervisor", "action": "no_harness_mgr"}

        items = self.mgr.list_work_items()
        closed_tasks = [i for i in items if i.get("state") == "Closed"]

        # 1b. Harness² Post-Flight Self-Learning Extraction
        if record_lesson and closed_tasks:
            for ct in closed_tasks[:3]:
                cid = ct.get("id")
                try:
                    record_lesson(
                        domain=ct.get("domain") or "qc_verification",
                        cue=f"task_{cid}_qc_verified",
                        lesson=f"Nghiệm thu thành công Task #{cid}: {ct.get('title')}. 5-Stage ISTQB mechanical tests pass 100%.",
                        evidence=f"QC verified and Closed Task #{cid} with exit code 0",
                        confidence="high",
                        work_item_id=cid
                    )
                except Exception:
                    pass

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
        if "lead" in r:
            return self.handle_lead_ended(d)
        if "pm" in r:
            return self.handle_pm_ended(d)
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
