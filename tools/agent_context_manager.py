#!/usr/bin/env python3
"""
tools/agent_context_manager.py - Bộ quản lý Context Window, Auto-Compact & Auto-Rehydration cho Agent SLPPC.

Tính năng:
1. Ping check & kiểm tra trạng thái Terminal (is_ready, is_busy, token_count_k) trước khi gửi tin.
2. Tự động Compact (`/compact`) khi context đạt ngưỡng cao (> 200k tokens), giảm tải 60-70% request size.
3. Tự động Re-hydrate sau khi `/new`: Nạp lại hồ sơ vai trò (profiles/*.md), task active trên Harness DB và latest handoff.
4. Chống flood: Kiểm tra TUI idle, không ngắt quãng turn đang chạy của agent khác.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_shared_root(default_root: Path) -> Path:
    """Resolve canonical main worktree root so all room-* worktrees share bmad/rooms."""
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
BASE_DIR = str(SHARED_ROOT)
REGISTRY_FILE = SHARED_ROOT / "bmad" / "rooms" / "agent_terminals.json"

COMPACT_THRESHOLD_K = 200.0  # Ngưỡng token (k) để kích hoạt tự động /compact


def _normalize_room_role(role: str) -> str:
    r = role.lower().strip().replace("-", "_")
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


def get_live_terminals() -> Dict[str, str]:
    """Trả về mapping {role: handle} cho các terminal đang active trong Orca (tự động đóng tab trùng trong cùng room)."""
    if os.environ.get("SLPPC_DRY_RUN") == "1" or not shutil.which("orca"):
        return {}
    try:
        reg_data: Dict[str, Any] = {}
        if REGISTRY_FILE.exists():
            try:
                reg_data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            except Exception:
                reg_data = {}

        res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return {}
        terminals = [
            t for t in json.loads(res.stdout).get("result", {}).get("terminals", [])
            if t.get("handle") and not t.get("stopped") and t.get("connected", True)
        ]

        by_room: Dict[str, list[Dict[str, Any]]] = {}
        for t in terminals:
            room = _infer_terminal_room(t)
            if room:
                by_room.setdefault(room, []).append(t)

        valid_map: Dict[str, str] = {}
        updated_reg = False

        for room, room_terms in by_room.items():
            reg_h = (reg_data.get(room) or {}).get("handle") if isinstance(reg_data.get(room), dict) else None
            room_terms.sort(
                key=lambda x: (1 if x.get("handle") == reg_h else 0, x.get("lastOutputAt") or 0),
                reverse=True,
            )
            primary = room_terms[0]
            primary_h = primary.get("handle")
            if primary_h:
                valid_map[room] = primary_h
                if reg_h != primary_h:
                    reg_data[room] = {"handle": primary_h, "tabId": primary.get("tabId") or ""}
                    updated_reg = True
                # Đóng mọi terminal dư thừa trong cùng room (đảm bảo đúng 1 agent/room)
                for extra in room_terms[1:]:
                    extra_h = extra.get("handle")
                    if extra_h and extra_h != primary_h:
                        subprocess.run(["orca", "terminal", "close", "--terminal", extra_h, "--tab", "--json"], capture_output=True, timeout=5)

        if updated_reg:
            try:
                REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
                REGISTRY_FILE.write_text(json.dumps(reg_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception:
                pass

        return valid_map
    except Exception:
        return {}


def has_live_terminal(role: str) -> Optional[str]:
    """Kiểm tra xem room tương ứng với role đã có live terminal hay chưa."""
    live_map = get_live_terminals()
    canonical = _normalize_room_role(role)
    return live_map.get(canonical)


def inspect_terminal(handle: str) -> Dict[str, Any]:
    """Đọc màn hình terminal, trích xuất token usage, trạng thái bận/rảnh."""
    info = {
        "handle": handle,
        "is_live": False,
        "is_ready": False,
        "is_busy": True,
        "token_count_k": 0.0,
        "needs_compact": False,
        "status_line": ""
    }
    if not shutil.which("orca"):
        return info

    try:
        res = subprocess.run(
            ["orca", "terminal", "read", "--terminal", handle, "--screen"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode != 0:
            return info
        info["is_live"] = True
        screen = res.stdout

        # Tìm token count (VD: 243.6k t hoặc 180.2k t)
        match = re.search(r"([\d\.]+)k\s*t", screen)
        if match:
            tokens_k = float(match.group(1))
            info["token_count_k"] = tokens_k
            info["needs_compact"] = tokens_k >= COMPACT_THRESHOLD_K

        # Kiểm tra trạng thái prompt
        lines = [line.strip() for line in screen.split("\n") if line.strip()]
        tail = " \n ".join(lines[-5:]) if lines else ""
        info["status_line"] = tail

        # Ready khi có dấu nhắc ❯ và KHÔNG có cảnh báo 'Ctrl+C to interrupt' hoặc đang chạy command
        if "Ctrl+C to interrupt" in tail or "brainstorming" in tail or "cogitating" in tail or "computing" in tail:
            info["is_busy"] = True
            info["is_ready"] = False
        elif "ready" in tail or (lines and lines[-1].endswith("❯")):
            info["is_busy"] = False
            info["is_ready"] = True
        else:
            info["is_busy"] = False
            info["is_ready"] = True

    except Exception:
        pass
    return info


def wait_for_terminal_ready(handle: str, max_wait_sec: int = 10) -> bool:
    """Chờ cho đến khi terminal ở trạng thái sẵn sàng (ready prompt ❯)."""
    start = time.time()
    while time.time() - start < max_wait_sec:
        state = inspect_terminal(handle)
        if state["is_ready"]:
            return True
        time.sleep(1)
    return False


def compact_agent_terminal(handle: str, max_wait_sec: int = 25) -> bool:
    """Gửi lệnh /compact tới terminal và chờ quá trình nén hoàn tất."""
    if not shutil.which("orca"):
        return False
    print(f"🗜️ [Auto-Compact]: Kích hoạt /compact trên terminal {handle}...")
    try:
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", "/compact", "--enter"],
            capture_output=True, timeout=5
        )
        # Chờ quá trình nén hoàn tất
        start = time.time()
        time.sleep(2)
        while time.time() - start < max_wait_sec:
            state = inspect_terminal(handle)
            if state["is_ready"] and "Compacting context" not in state["status_line"]:
                print(f"✅ [Auto-Compact]: Đã nén context thành công cho {handle}! Tokens hiện tại: {state['token_count_k']}k")
                return True
            time.sleep(1.5)
    except Exception as e:
        print(f"⚠️ [Auto-Compact Error]: {e}")
    return False


def build_rehydration_prompt(
    role: str,
    user_id: str = "default_user",
    project_id: str = "Room_Agent",
    domain: Optional[str] = None,
) -> str:
    """
    Tạo bản tin context nạp lại (3-Tier Dynamic Hydration) cho Agent khi phiên bị /new hoặc khởi động lại:
    - Tầng 1 (Working Memory): Role profile & kỷ luật thực thi tức thời.
    - Tầng 2 (Short-Term Memory): Task Active hiện hành & latest_handoff.md trong phiên.
    - Tầng 3 (Long-Term Memory): Truy vấn Database (Harness Learn Store) theo User ID / Project ID để nạp top-3 quy chuẩn & bẫy lỗi lịch sử.
    """
    clean_role = role.lower().replace("-", "_").replace(" ", "_")
    
    # 1. Tra cứu file profile, IDENTITY.md và SOUL.md
    if clean_role in ("peer1", "peer2", "peer3", "peer4", "peer_2", "peer_3", "peer_4", "design", "peer_design", "peer_dev"):
        clean_role = "peer"
    if clean_role == "pm":
        clean_role = "supervisor"
    profile_file = PROJECT_ROOT / "profiles" / clean_role / "PROFILE.md"
    if not profile_file.exists():
        profile_file = PROJECT_ROOT / "profiles" / f"{clean_role}.md"
    identity_file = PROJECT_ROOT / "profiles" / clean_role / "IDENTITY.md"
    soul_file = PROJECT_ROOT / "profiles" / clean_role / "SOUL.md"
    mission = f"Vai trò {role.upper()} trong mô hình điều hành SLPC."
    identity_summary = f"Name: {role.upper()}"
    soul_summary = "Direct, resourceful first, zero performative fluff."
    if profile_file.exists():
        try:
            lines = profile_file.read_text(encoding="utf-8").split("\n")
            for line in lines:
                if "MISSION:" in line or "Room role:" in line:
                    mission = line.strip()
                    break
        except Exception:
            pass
    if identity_file.exists():
        try:
            id_lines = [
                l.strip()
                for l in identity_file.read_text(encoding="utf-8").splitlines()
                if l.strip().startswith(("Name:", "Character:", "Vibe:", "Emoji:"))
            ]
            if id_lines:
                identity_summary = " | ".join(id_lines)
        except Exception:
            pass
    if soul_file.exists():
        try:
            s_lines = [l.strip() for l in soul_file.read_text(encoding="utf-8").splitlines() if l.strip().startswith("- ")]
            if s_lines:
                soul_summary = " ".join(s_lines[:2])
        except Exception:
            pass

    # 2. Tra cứu task active trên Harness DB (Short-Term / Active Session State)
    active_tasks_info = "Không có task Active tồn đọng"
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "tools"))
        from tools.harness_manager import HarnessManager  # type: ignore
        mgr = HarnessManager()
        active_items = mgr.list_work_items(state="Active", assigned_to_profile=clean_role)
        if active_items:
            task_strs = [f"#{item['id']} [{item.get('type')}] {item.get('title')}" for item in active_items[:3]]
            active_tasks_info = "; ".join(task_strs)
    except Exception:
        pass

    # 3. Tra cứu handoff gần nhất & Session Buffer (Short-Term Memory: Bộ đệm phiên làm việc)
    handoff_info = "Không có biên bản handoff gần đây"
    role_dir = PROJECT_ROOT / "bmad" / "rooms" / clean_role
    if role_dir.exists():
        latest = role_dir / "latest_handoff.md"
        if latest.exists():
            try:
                txt = latest.read_text(encoding="utf-8")
                summary_match = re.search(r"-\s*\*\*Tóm tắt\*\*:\s*(.+)", txt)
                if summary_match:
                    handoff_info = summary_match.group(1).strip()
            except Exception:
                pass
        session_buf = role_dir / "session_buffer.json"
        if session_buf.exists():
            try:
                buf_obj = json.loads(session_buf.read_text(encoding="utf-8"))
                loops = buf_obj.get("recent_loops", [])
                if isinstance(loops, list) and loops:
                    last_loop = loops[-1]
                    if isinstance(last_loop, dict):
                        handoff_info = f"{handoff_info} | Loop gần nhất: [{last_loop.get('stage')}] {last_loop.get('summary')}"
            except Exception:
                pass

    # 4. Tra cứu Long-Term Memory (MEMORY.md + Database Learn Store) theo Project ID / Domain (Top-3 chunks)
    memory_file = PROJECT_ROOT / "profiles" / clean_role / "MEMORY.md"
    curated_memory_summary = ""
    if memory_file.exists():
        try:
            m_lines = [l.strip() for l in memory_file.read_text(encoding="utf-8").splitlines() if l.strip().startswith("- ")]
            if m_lines:
                curated_memory_summary = " ".join(m_lines[:3])
        except Exception:
            pass

    long_term_lessons = "Chưa có bài học lịch sử đặc thù; áp dụng chuẩn mặc định của dự án."
    try:
        from tools.harness_learning_search import search_experiences  # type: ignore
        experiences = search_experiences(domain=domain, limit=3)
        if experiences:
            lesson_snippets = [
                f"[{exp.get('domain', 'general')}] {exp.get('cue', '')}: {exp.get('lesson', '')}"
                for exp in experiences[:3]
            ]
            long_term_lessons = " | ".join(lesson_snippets)
    except Exception:
        pass
    if curated_memory_summary:
        long_term_lessons = f"[Curated MEMORY.md: {curated_memory_summary}] | [Learn Store: {long_term_lessons}]"

    prompt = (
        f"=== [SLPPC AUTO-REHYDRATION BOOT | 3-TIER DYNAMIC HYDRATION] ===\n"
        f"Identity: User={user_id} | Project={project_id} | Vai trò={role.upper()}\n"
        f"Agent Identity (profiles/{clean_role}/IDENTITY.md): {identity_summary}\n"
        f"Soul Persona (profiles/{clean_role}/SOUL.md): {soul_summary}\n"
        f"Tầng 1 (Working Memory - Sứ mệnh): {mission}\n"
        f"Tầng 2 (Short-Term Memory - Phiên hiện tại): Task={active_tasks_info} | Handoff={handoff_info}\n"
        f"Tầng 3 (Long-Term Memory - Tri thức bền vững Top-3): {long_term_lessons}\n"
        f"Kỷ luật: 100% Strict Typing (0 any/unknown), Chuẩn Zero-Search 5 thành phần, Anti-Leak, cấm role_trespass.\n"
        f"Xác nhận đã nạp lại context đầy đủ và sẵn sàng làm việc."
    )
    return prompt


def rehydrate_agent(role: str, handle: str) -> bool:
    """Thực thi lệnh /new và nạp lại context tức thời cho agent."""
    if not shutil.which("orca"):
        return False
    print(f"🔄 [Auto-Rehydration]: Khởi tạo phiên mới (/new) và nạp lại context cho {role.upper()}...")
    try:
        # 1. Gửi lệnh /new
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", "/new", "--enter"],
            capture_output=True, timeout=5
        )
        time.sleep(2)
        wait_for_terminal_ready(handle, max_wait_sec=10)

        # 2. Bắn prompt rehydration
        boot_prompt = build_rehydration_prompt(role)
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", boot_prompt, "--enter"],
            capture_output=True, timeout=5
        )
        print(f"✅ [Auto-Rehydration]: Đã nạp lại context thành công cho {role.upper()} ({handle}).")
        return True
    except Exception as e:
        print(f"⚠️ [Auto-Rehydration Error]: {e}")
        return False


def _extract_envelope_dict(message: Union[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Helper to detect and extract an AgentHandoffEnvelope dict from dict or JSON string."""
    if isinstance(message, dict):
        if "schema_version" in message or ("spec" in message and "verification" in message) or ("from_role" in message and "to_role" in message and "task_id" in message):
            return message
    elif isinstance(message, str):
        trimmed = message.strip()
        if trimmed.startswith("{") and trimmed.endswith("}"):
            try:
                parsed = json.loads(trimmed)
                if isinstance(parsed, dict) and (
                    "schema_version" in parsed
                    or ("spec" in parsed and "verification" in parsed)
                    or ("from_role" in parsed and "to_role" in parsed and "task_id" in parsed)
                ):
                    return parsed
            except Exception:
                pass
    return None


def safe_send_agent_message(
    role: str,
    message: Union[str, Dict[str, Any]],
    auto_compact: bool = True,
    raise_on_invalid: bool = False
) -> bool:
    """Gửi thông điệp an toàn cho agent: Có validation envelope, ping check, context auto-compact, chống đè lệnh."""
    # 0. Step 0: Validate AgentHandoffEnvelope immediately before terminal lookup
    envelope_dict = _extract_envelope_dict(message)
    if envelope_dict is not None:
        try:
            from tools.slppc_flow_guard import validate_agent_handoff_envelope
        except ImportError:
            try:
                from slppc_flow_guard import validate_agent_handoff_envelope
            except ImportError:
                validate_agent_handoff_envelope = None

        if validate_agent_handoff_envelope:
            is_valid, errors = validate_agent_handoff_envelope(envelope_dict)
            if not is_valid:
                err_msg = f"Invalid AgentHandoffEnvelope: {'; '.join(errors)}"
                print(f"❌ [Handoff Validation Rejected]: {err_msg}")
                if raise_on_invalid:
                    raise ValueError(err_msg)
                return False

    live_map = get_live_terminals()
    canonical_role = _normalize_room_role(role)
    handle = live_map.get(canonical_role)
    if not handle:
        clean_role = role.lower().strip().replace("-", "_").replace(" ", "_")
        handle = live_map.get(clean_role)
    if not handle:
        return False

    # 1. Ping check: Kiểm tra terminal còn sống và trạng thái hiện tại
    state = inspect_terminal(handle)
    if not state["is_live"]:
        print(f"⚠️ [Ping Check]: Terminal của {role.upper()} ({handle}) không phản hồi.")
        return False

    # 2. Nếu agent đang bận, chờ tối đa 8s
    if state["is_busy"]:
        print(f"⏳ [Ping Check]: {role.upper()} đang bận xử lý, chờ TUI idle...")
        if not wait_for_terminal_ready(handle, max_wait_sec=8):
            print(f"⚠️ [Ping Check]: {role.upper()} vẫn bận sau 8s. Hủy gửi để tránh gián đoạn tiến trình.")
            return False

    # 3. Kiểm tra Context Window & Auto-Compact
    if auto_compact and state["needs_compact"]:
        print(f"⚠️ [Context Warning]: {role.upper()} đạt {state['token_count_k']}k tokens. Đang tự động nén context...")
        compact_agent_terminal(handle, max_wait_sec=20)
        wait_for_terminal_ready(handle, max_wait_sec=5)

    # 4. Gửi lệnh
    message_str = json.dumps(message, ensure_ascii=False, indent=2) if isinstance(message, dict) else str(message)
    try:
        subprocess.run(
            ["orca", "terminal", "send", "--terminal", handle, "--text", message_str, "--enter"],
            capture_output=True, timeout=10
        )
        return True
    except Exception as e:
        print(f"⚠️ [Send Error]: {e}")
        return False


def send_handoff_envelope(
    sender: str,
    recipient: str,
    envelope: Union[Dict[str, Any], str],
    auto_compact: bool = True,
    strict: bool = True,
    persist_to_room: bool = True
) -> bool:
    """
    Gửi thông điệp bàn giao có cấu trúc (AgentHandoffEnvelope) giữa 2 agent theo chuẩn MAG-02.
    - Thẩm định schema và Zero-Search 5 thành phần trước khi gửi.
    - Kiểm soát Feedback/Retry loop (FAILED_RETRY bắt buộc có stack trace, retry_count <= 3).
    - Tùy chọn lưu trữ đồng bộ vào bmad/rooms/<recipient>/latest_handoff.md.
    - Nếu strict=True và envelope không hợp lệ -> Ném ngoại lệ ValueError.
    """
    if isinstance(envelope, str):
        try:
            env_dict = json.loads(envelope)
        except Exception as e:
            err_msg = f"Envelope string is not valid JSON: {e}"
            print(f"❌ [Handoff Validation Rejected]: {err_msg}")
            if strict:
                raise ValueError(err_msg)
            return False
    elif isinstance(envelope, dict):
        env_dict = dict(envelope)
    else:
        err_msg = f"Envelope must be a dict or JSON string, got {type(envelope).__name__}"
        print(f"❌ [Handoff Validation Rejected]: {err_msg}")
        if strict:
            raise ValueError(err_msg)
        return False

    norm_sender = _normalize_room_role(sender).upper()
    norm_recipient = _normalize_room_role(recipient).upper()
    if not env_dict.get("from_role"):
        env_dict["from_role"] = norm_sender
    if not env_dict.get("to_role"):
        env_dict["to_role"] = norm_recipient

    try:
        from tools.slppc_flow_guard import validate_agent_handoff_envelope
    except ImportError:
        try:
            from slppc_flow_guard import validate_agent_handoff_envelope
        except ImportError:
            validate_agent_handoff_envelope = None

    if validate_agent_handoff_envelope:
        is_valid, errors = validate_agent_handoff_envelope(env_dict)
        if not is_valid:
            err_msg = f"Invalid AgentHandoffEnvelope: {'; '.join(errors)}"
            print(f"❌ [Handoff Validation Rejected]: {err_msg}")
            if strict:
                raise ValueError(err_msg)
            return False

    if persist_to_room:
        try:
            target_room = _normalize_room_role(recipient)
            room_dir = PROJECT_ROOT / "bmad" / "rooms" / target_room
            if room_dir.exists():
                handoff_file = room_dir / "latest_handoff.md"
                spec = env_dict.get("spec", {})
                ver = env_dict.get("verification", {})
                content = (
                    f"# AGENT HANDOFF ENVELOPE: {env_dict.get('from_role')} ➔ {env_dict.get('to_role')}\n\n"
                    f"- **Task ID**: #{env_dict.get('task_id')}\n"
                    f"- **Status**: {env_dict.get('status')}\n"
                    f"- **Schema**: {env_dict.get('schema_version')}\n\n"
                    f"## 1. Zero-Search Specification\n"
                    f"- **Target Files**: {', '.join(spec.get('target_files', []))}\n"
                    f"- **Anchors**: {', '.join(spec.get('anchors', []))}\n"
                    f"- **Concrete Changes**: {spec.get('concrete_changes', '')}\n"
                    f"- **Acceptance Criteria**:\n"
                    + "\n".join(f"  * {ac}" for ac in spec.get("acceptance_criteria", []))
                    + f"\n- **Test Command**: `{spec.get('test_command', '')}`\n\n"
                    f"## 2. Verification Context\n"
                    f"- **Exit Code**: {ver.get('exit_code', 0)}\n"
                    f"- **Retry Count**: {ver.get('retry_count', 0)}\n"
                    f"- **Stack Trace**: {ver.get('error_stack_trace', '') or 'None'}\n"
                )
                handoff_file.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"⚠️ [Handoff Persist Warning]: {e}")

    return safe_send_agent_message(
        role=recipient,
        message=env_dict,
        auto_compact=auto_compact,
        raise_on_invalid=strict
    )



def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quản trị Context Window, Auto-Compact & Rehydration cho Agent SLPPC.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    p_inspect = subparsers.add_parser("inspect", help="Kiểm tra context window và trạng thái của một hoặc toàn bộ role")
    p_inspect.add_argument("--role", default=None, help="Tên role cần kiểm tra (mặc định kiểm tra toàn bộ)")

    p_compact = subparsers.add_parser("compact", help="Kích hoạt nén context (/compact) cho một role")
    p_compact.add_argument("--role", required=True, help="Tên role (supervisor, lead, peer, qc...)")

    p_rehydrate = subparsers.add_parser("rehydrate", help="Kích hoạt /new và nạp lại context (re-hydrate) cho một role")
    p_rehydrate.add_argument("--role", required=True, help="Tên role")

    args = parser.parse_args()

    if args.action == "inspect":
        live_map = get_live_terminals()
        print("\n=========================================================================")
        print("      SLPPC AGENT CONTEXT WINDOW & TOKEN USAGE MONITOR")
        print("=========================================================================")
        print(f"{'ROLE':<12} | {'HANDLE':<38} | {'TOKENS':<10} | {'STATUS'}")
        print("-" * 73)
        for r, h in live_map.items():
            if args.role and args.role.lower() not in r:
                continue
            st = inspect_terminal(h)
            ready_str = "🟢 Ready" if st["is_ready"] else "🟡 Busy"
            compact_str = " (⚠️ CẦN COMPACT)" if st["needs_compact"] else ""
            tok_str = f"{st['token_count_k']}k t" if st['token_count_k'] > 0 else "N/A"
            print(f"{r.upper():<12} | {h:<38} | {tok_str:<10} | {ready_str}{compact_str}")
        print("=========================================================================\n")

    elif args.action == "compact":
        live_map = get_live_terminals()
        handle = live_map.get(args.role.lower())
        if not handle:
            print(f"❌ Không tìm thấy live terminal cho role '{args.role}'.")
            sys.exit(1)
        compact_agent_terminal(handle)

    elif args.action == "rehydrate":
        live_map = get_live_terminals()
        handle = live_map.get(args.role.lower())
        if not handle:
            print(f"❌ Không tìm thấy live terminal cho role '{args.role}'.")
            sys.exit(1)
        rehydrate_agent(args.role, handle)


if __name__ == "__main__":
    main()
