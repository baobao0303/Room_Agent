#!/usr/bin/env python3
"""
tools/slppc_flow_guard.py - Bộ Canh Gác Tuân Thủ Quy Trình Điều Hành SLPPC & Tự Động Lập Biên Bản Vi Phạm (SLPPC Flow Guard & Automated Violation Auditor).

Mô hình SLPPC (Supervisor - PM - Lead - Peer - QC):
Kiểm tra tự động và lập biên bản phạt khi:
1. Lead Dev tự ý gõ code (role_trespass) thay vì bóc tách Zero-Search task giao cho Peers.
2. Supervisor tự ý code tính năng hoặc duyệt task mơ hồ.
3. Bỏ qua cổng thẩm định Khả thi & Phù hợp của PM Agent (pm_bypass).
4. Peer tự tiện đóng task (premature_close) không qua nghiệm thu độc lập của QC.
5. Giao task 1 dòng cẩu thả vi phạm Zero-Search Mandate (vague_specs).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIOLATIONS_DIR = PROJECT_ROOT / "bmad" / "rooms" / "violations"
VIOLATIONS_DIR.mkdir(parents=True, exist_ok=True)

# 4 Tiêu chuẩn bắt buộc của Zero-Search Task Specification
ZERO_SEARCH_MANDATORY_SECTIONS = [
    "target file",
    "anchor",
    "concrete change",
    "acceptance criteria",
]


def record_violation_minute(
    from_role: str,
    to_role: str,
    violation_type: str,
    task_id: Optional[str | int],
    evidence: str,
    message: str,
) -> Path:
    """Tạo biên bản vi phạm chính thức lưu vĩnh viễn trong bmad/rooms/violations/ (tránh ghi trùng lặp)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tid_str = f"{task_id}" if task_id else "general"

    # Tránh tạo file trùng lặp nếu đã có biên bản cho vi phạm này
    existing = list(VIOLATIONS_DIR.glob(f"violation_{tid_str}_{from_role.lower()}_to_{to_role.lower()}_*.md"))
    if existing:
        return existing[0]

    filename = f"violation_{tid_str}_{from_role.lower()}_to_{to_role.lower()}_{ts}.md"
    file_path = VIOLATIONS_DIR / filename

    content = f"""# BIÊN BẢN VI PHẠM KỶ LUẬT ĐIỀU HÀNH SLPPC
**Mã Biên Bản**: `VIO-{ts}-{to_role.upper()}`  
**Thời gian lập**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  
**Người lập biên bản (From)**: `{from_role.upper()}`  
**Đối tượng vi phạm (To)**: `{to_role.upper()}`  
**Loại sai phạm**: `{violation_type}`  
**Work Item ID liên quan**: `#{task_id or 'N/A'}`  

---

## 1. Hành Vi Sai Phạm (Violation Details)
> **Mô tả hành vi**: {message}

## 2. Bằng Chứng Thực Nghiệm (Empirical Evidence)
```text
{evidence.strip()}
```

## 3. Rào Cản Thẩm Quyền Bị Phá Vỡ (Broken Invariant)
- **Quy chế SLPPC**: Phân định rạch ròi 5 vai trò (Supervisor - PM - Lead - Peer - QC).
- **Nguyên tắc vi phạm**: Quản lý cấm ôm code; Dev cấm tự duyệt/đóng task; Giao task cấm mơ hồ; Cấm bypass cổng PM.

## 4. Chế Tài Xử Phạt (Penalties & Next Actions)
1. Giáng cấp trạng thái công việc về `Active` hoặc `Blocked`.
2. Đối tượng `{to_role.upper()}` bắt buộc chấn chỉnh quy trình và khắc phục sai phạm.
3. Ghi nhận vi phạm vào Sổ cái Kỷ luật của phòng ban SLPPC.
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def check_zero_search_compliance(description: str) -> Tuple[bool, List[str]]:
    """Kiểm tra mô tả task có đủ các trường Zero-Search bắt buộc hay không."""
    lower = description.lower()
    missing = []
    for sec in ZERO_SEARCH_MANDATORY_SECTIONS:
        if sec not in lower:
            missing.append(sec)
    return len(missing) == 0, missing


def build_agent_handoff_envelope(
    task_id: str | int,
    from_role: str,
    to_role: str,
    status: str,
    target_files: List[str],
    anchors: List[str],
    concrete_changes: str,
    acceptance_criteria: List[str],
    test_command: str,
    exit_code: int = 0,
    error_stack_trace: str = "",
    retry_count: int = 0,
) -> Dict[str, Any]:
    """Khởi tạo JSON Schema AgentHandoffEnvelope chuẩn hóa giữa PM, Coder, Tester, Reviewer (Pillar 2)."""
    return {
        "schema_version": "ARCH-SPEC-ENTERPRISE-AI-4-PILLARS-2026-V1",
        "task_id": str(task_id),
        "from_role": from_role.upper().strip(),
        "to_role": to_role.upper().strip(),
        "status": status.upper().strip(),
        "spec": {
            "target_files": list(target_files),
            "anchors": list(anchors),
            "concrete_changes": str(concrete_changes),
            "acceptance_criteria": list(acceptance_criteria),
            "test_command": str(test_command),
        },
        "verification": {
            "exit_code": int(exit_code) if exit_code is not None else 0,
            "error_stack_trace": "" if error_stack_trace is None else str(error_stack_trace),
            "retry_count": int(retry_count) if retry_count is not None else 0,
        },
    }


def validate_agent_handoff_envelope(envelope: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Kiểm định JSON Schema AgentHandoffEnvelope và Feedback/Retry Loop:
    - Đầy đủ các trường bắt buộc: task_id, from_role, to_role, status, spec, verification.
    - Spec đủ 5 thành phần Zero-Search (target_files, anchors, concrete_changes, acceptance_criteria, test_command).
    - Khi status == FAILED_RETRY (Tester -> Coder), bắt buộc có error_stack_trace và retry_count <= 3.
    """
    errors: List[str] = []
    if not isinstance(envelope, dict):
        return False, ["Envelope phải là một JSON object (dict)."]

    for req_field in ("task_id", "from_role", "to_role", "status", "spec", "verification"):
        val = envelope.get(req_field)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"Thiếu trường bắt buộc hoặc rỗng: '{req_field}'")

    spec = envelope.get("spec")
    if not isinstance(spec, dict):
        errors.append("Trường 'spec' phải là JSON object.")
    else:
        for s_key in ("target_files", "anchors", "concrete_changes", "acceptance_criteria", "test_command"):
            val = spec.get(s_key)
            if val is None:
                errors.append(f"Spec thiếu hoặc rỗng thành phần Zero-Search: '{s_key}'")
            elif isinstance(val, str):
                if not val.strip():
                    errors.append(f"Spec thiếu hoặc rỗng thành phần Zero-Search: '{s_key}'")
            elif isinstance(val, (list, tuple)):
                if len(val) == 0 or not [x for x in val if x is not None and str(x).strip()]:
                    errors.append(f"Spec thiếu hoặc rỗng thành phần Zero-Search: '{s_key}'")
            else:
                errors.append(f"Spec thiếu hoặc rỗng thành phần Zero-Search: '{s_key}'")

    ver = envelope.get("verification")
    if not isinstance(ver, dict):
        errors.append("Trường 'verification' phải là JSON object.")
    else:
        raw_retry = ver.get("retry_count", 0)
        if isinstance(raw_retry, bool) or raw_retry is None:
            errors.append("Trường 'retry_count' phải là số nguyên.")
        else:
            try:
                val_float = float(raw_retry)
                if not val_float.is_integer():
                    errors.append("Trường 'retry_count' phải là số nguyên.")
                else:
                    rc = int(val_float)
                    if rc > 3 or val_float > 3:
                        errors.append(f"Vượt quá trần vòng lặp Turn Ceiling: retry_count={rc} > 3")
                    elif rc < 0 or val_float < 0:
                        errors.append(f"Trường 'retry_count' không hợp lệ: {rc} < 0")
            except (ValueError, TypeError, OverflowError):
                errors.append("Trường 'retry_count' phải là số nguyên.")

        status_str = str(envelope.get("status", "")).upper().strip()
        if status_str == "FAILED_RETRY":
            raw_stack = ver.get("error_stack_trace")
            if (
                raw_stack is None
                or not str(raw_stack).strip()
                or str(raw_stack).strip().lower() in ("none", "null")
            ):
                errors.append("Luồng Feedback/Retry Loop (FAILED_RETRY) bắt buộc phải đính kèm 'error_stack_trace'.")

    return len(errors) == 0, errors


def audit_lead_role_trespass(lead_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Kiểm tra xem Lead Dev có vi phạm role_trespass:
    Tự ý sửa mã nguồn production thay vì phân rã giao cho Peer.
    """
    violations = []
    bmad_rooms = lead_dir if lead_dir is not None else (PROJECT_ROOT / "bmad" / "rooms" / "lead")
    if not bmad_rooms.is_dir():
        return violations

    now = time.time()
    candidates = list(bmad_rooms.glob("handoff_*.md"))
    latest_file = bmad_rooms / "latest_handoff.md"
    if latest_file.is_file():
        candidates.append(latest_file)

    for memo_file in candidates:
        try:
            # Chỉ quét các biên bản gần nhất trong vòng 2 giờ
            if (now - memo_file.stat().st_mtime) > 7200:
                continue
            content = memo_file.read_text(encoding="utf-8")
            lower = content.lower()
            if ("modified files" in lower or "đã sửa" in lower) and "peer" not in lower:
                if "crates/harness-cli/src" in content or "apps/app-shell/src" in content or "projects/demo-crm-fe" in content:
                    tid_match = re.search(r"#(\d+)", content)
                    violations.append({
                        "file": str(memo_file.relative_to(PROJECT_ROOT)) if memo_file.is_relative_to(PROJECT_ROOT) else memo_file.name,
                        "evidence": "Lead Dev ghi nhận trực tiếp sửa mã nguồn sản phẩm thay vì giao cho Peer",
                        "task_id": tid_match.group(1) if tid_match else None,
                    })
        except Exception:
            pass

    return violations


def audit_pm_bypass(supervisor_dir: Optional[Path] = None, pm_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Kiểm tra xem có bỏ qua cổng thẩm định Feasibility & Alignment:
    Tạo hoặc kích hoạt Epic mà chưa có Intake Decision Memo (từ Supervisor hoặc PM).
    """
    violations = []
    sup_dir = supervisor_dir if supervisor_dir is not None else (PROJECT_ROOT / "bmad" / "rooms" / "supervisor")
    pm_d = pm_dir if pm_dir is not None else (PROJECT_ROOT / "bmad" / "rooms" / "pm")

    if not sup_dir.is_dir():
        return violations

    now = time.time()
    candidates = list(sup_dir.glob("handoff_*.md"))
    latest_file = sup_dir / "latest_handoff.md"
    if latest_file.is_file():
        candidates.append(latest_file)

    for handoff in candidates:
        try:
            # Chỉ quét các biên bản gần nhất trong vòng 2 giờ
            if (now - handoff.stat().st_mtime) > 7200:
                continue
            content = handoff.read_text(encoding="utf-8")
            epic_match = re.search(r"Epic\s*#(\d+)", content, re.IGNORECASE)
            if epic_match:
                epic_id = epic_match.group(1)
                # Bỏ qua các Epic lịch sử trước khi áp dụng chuẩn SLPPC (ID < 4116)
                if int(epic_id) < 4116:
                    continue
                has_memo = False
                # Kiểm tra memo trong supervisor_dir
                for sup_memo in sup_dir.glob("*.md"):
                    if epic_id in sup_memo.name or f"#{epic_id}" in sup_memo.read_text(encoding="utf-8"):
                        if "decision_memo" in sup_memo.name or "feasibility" in sup_memo.read_text(encoding="utf-8").lower():
                            has_memo = True
                            break
                # Hoặc kiểm tra trong pm_dir cũ nếu có
                if not has_memo and pm_d.is_dir():
                    for pm_memo in pm_d.glob("*.md"):
                        if epic_id in pm_memo.name or f"#{epic_id}" in pm_memo.read_text(encoding="utf-8"):
                            has_memo = True
                            break
                # Hoặc chính trong content của handoff có phần [SUPERVISOR INTAKE DECISION MEMO] hoặc Feasibility
                if not has_memo and ("decision memo" in content.lower() or "feasibility" in content.lower()):
                    has_memo = True
                if not has_memo:
                    violations.append({
                        "file": str(handoff.relative_to(PROJECT_ROOT)) if handoff.is_relative_to(PROJECT_ROOT) else handoff.name,
                        "evidence": f"Epic #{epic_id} được khởi tạo/giao việc mà chưa qua cổng thẩm định Feasibility/Alignment của Supervisor",
                        "task_id": epic_id,
                    })
        except Exception:
            pass

    return violations


def audit_premature_close(peer_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Kiểm tra xem Dev/Peer có tự ý đóng task (premature_close):
    Peer chỉ được phép chuyển trạng thái sang Resolved; cấm tự chuyển sang Closed.
    """
    violations = []
    p_dir = peer_dir if peer_dir is not None else (PROJECT_ROOT / "bmad" / "rooms" / "peer")
    if not p_dir.is_dir():
        return violations

    now = time.time()
    candidates = list(p_dir.glob("handoff_*.md"))
    latest_file = p_dir / "latest_handoff.md"
    if latest_file.is_file():
        candidates.append(latest_file)

    for memo in candidates:
        try:
            # Chỉ quét các biên bản gần nhất trong vòng 2 giờ
            if (now - memo.stat().st_mtime) > 7200:
                continue
            content = memo.read_text(encoding="utf-8")
            lower = content.lower()
            if "trạng thái: closed" in lower or "state: closed" in lower or "đã đóng task" in lower or "chuyển sang closed" in lower:
                tid_match = re.search(r"#(\d+)", content)
                violations.append({
                    "file": str(memo.relative_to(PROJECT_ROOT)) if memo.is_relative_to(PROJECT_ROOT) else memo.name,
                    "evidence": "Peer Dev tự ý tuyên bố hoặc cập nhật trạng thái Task sang Closed thay vì nộp Resolved cho QC",
                    "task_id": tid_match.group(1) if tid_match else None,
                })
        except Exception:
            pass

    return violations


def audit_ephemeral_room_hygiene(rooms_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Kiểm tra vệ sinh phòng ban BMAD Rooms theo kiến trúc Ephemeral State:
    1. Không có file timestamp legacy (handoff_*.md).
    2. File bmad/rooms/room_ledger.json phải tồn tại, schema hợp lệ và dung lượng < 50KB.
    3. Mỗi phòng ban (supervisor, pm, lead, peer, qc) duy trì duy nhất 1 file latest_handoff.md <= 150 dòng, không leak path cá nhân.
    """
    violations = []
    r_dir = rooms_dir if rooms_dir is not None else (PROJECT_ROOT / "bmad" / "rooms")
    if not r_dir.exists():
        return violations

    # Check 1: Legacy handoff files có timestamp
    legacy_files = [f for f in r_dir.rglob("handoff_*.md") if "archive" not in f.parts]
    if legacy_files:
        violations.append({
            "evidence": f"Phát hiện {len(legacy_files)} file handoff timestamp cũ: {[f.name for f in legacy_files[:5]]}",
            "type": "room_hygiene_violation"
        })

    # Check 2: room_ledger.json tồn tại và kiểm soát trần kích thước (< 50KB, history <= 50)
    ledger_file = r_dir / "room_ledger.json"
    if not ledger_file.is_file():
        violations.append({
            "evidence": "Thiếu file sổ cái tập trung bmad/rooms/room_ledger.json",
            "type": "missing_ledger_violation"
        })
    else:
        size_bytes = ledger_file.stat().st_size
        if size_bytes > 50 * 1024:
            violations.append({
                "evidence": f"File room_ledger.json phình to vượt trần: {size_bytes} bytes > 50KB",
                "type": "ledger_bloat_violation"
            })
        try:
            ledger_data = json.loads(ledger_file.read_text(encoding="utf-8"))
            if not isinstance(ledger_data, dict):
                violations.append({
                    "evidence": "File room_ledger.json root phải là JSON object",
                    "type": "ledger_schema_violation"
                })
            else:
                for req_key in ("version", "roles", "history"):
                    if req_key not in ledger_data:
                        violations.append({
                            "evidence": f"room_ledger.json thiếu trường bắt buộc: '{req_key}'",
                            "type": "ledger_schema_violation"
                        })
                history = ledger_data.get("history", [])
                if not isinstance(history, list):
                    violations.append({
                        "evidence": "Trường 'history' trong room_ledger.json phải là danh sách (list)",
                        "type": "ledger_schema_violation"
                    })
                elif len(history) > 50:
                    violations.append({
                        "evidence": f"room_ledger.json vượt quá trần FIFO 50: {len(history)} entries",
                        "type": "ledger_overflow_violation"
                    })
        except Exception as e:
            violations.append({
                "evidence": f"File room_ledger.json hỏng định dạng hoặc không thể đọc: {e}",
                "type": "ledger_schema_violation"
            })

    # Check 3: latest_handoff.md <= 150 dòng cho mỗi role, Zero-Leak, và không thừa file handoff
    for role in ("supervisor", "pm", "lead", "peer", "qc"):
        role_dir = r_dir / role
        if not role_dir.is_dir():
            continue

        latest_file = role_dir / "latest_handoff.md"
        if not latest_file.is_file():
            violations.append({
                "evidence": f"Phòng ban {role} thiếu file bắt buộc {role}/latest_handoff.md",
                "type": "missing_handoff_memo",
                "role": role,
            })
        else:
            try:
                lines = latest_file.read_text(encoding="utf-8").splitlines()
                if len(lines) > 150:
                    violations.append({
                        "evidence": f"{role}/latest_handoff.md vượt quá 150 dòng: {len(lines)} dòng",
                        "type": "oversized_handoff_memo",
                        "role": role,
                    })
                content = "\n".join(lines)
                if re.search(r"/(?:Users|home)/[a-zA-Z0-9_-]+", content):
                    violations.append({
                        "evidence": f"File {role}/latest_handoff.md chứa đường dẫn máy tính cá nhân (vi phạm Zero-Leak)",
                        "type": "anti_leak_violation",
                        "role": role,
                    })
            except Exception:
                pass

        extra_handoffs = [f for f in role_dir.glob("*handoff*.md") if f.name != "latest_handoff.md"]
        if extra_handoffs:
            violations.append({
                "evidence": f"Phòng {role} chứa file handoff dư thừa: {[f.name for f in extra_handoffs]}",
                "type": "room_hygiene_violation",
                "role": role,
            })

    return violations


def audit_vague_specs(tasks_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Kiểm tra xem có vi phạm giao task cẩu thả / mơ hồ (vague_specs):
    Task giao cho Peer thiếu các mục định danh Zero-Search.
    """
    violations = []
    t_dir = tasks_dir if tasks_dir is not None else (PROJECT_ROOT / "bmad" / "rooms" / "tasks")
    if not t_dir.is_dir():
        return violations

    for task_folder in t_dir.iterdir():
        if not task_folder.is_dir():
            continue
        task_id = task_folder.name
        candidates = list(task_folder.glob("handoff_*.md"))
        latest_file = task_folder / "latest_handoff.md"
        if latest_file.is_file():
            candidates.append(latest_file)

        for memo in candidates:
            try:
                content = memo.read_text(encoding="utf-8")
                if "supervisor" in memo.name or "lead" in memo.name:
                    is_compliant, missing = check_zero_search_compliance(content)
                    if not is_compliant and len(content.strip()) < 200:
                        violations.append({
                            "file": str(memo.relative_to(PROJECT_ROOT)) if memo.is_relative_to(PROJECT_ROOT) else memo.name,
                            "evidence": f"Mô tả task #{task_id} thiếu các mục Zero-Search bắt buộc: {', '.join(missing)}",
                            "task_id": task_id,
                        })
            except Exception:
                pass

    return violations


def audit_settlement_verification_gate(
    ledger_path: Optional[Path] = None,
    tasks_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Kiểm tra tính tuân thủ của Dual-Verification Settlement Gate:
    Bắt buộc mọi task chuyển sang trạng thái Resolved phải có biên bản kiểm định / verification record
    hợp lệ từ Settlement Gate (git diff audit, execution log exit code 0, ISTQB pass).
    Chặn đứng hành vi tự khai / bypass settlement gate khi nộp Resolved.
    """
    violations: List[Dict[str, Any]] = []
    l_path = ledger_path if ledger_path is not None else (PROJECT_ROOT / "bmad" / "rooms" / "room_ledger.json")
    t_dir = tasks_dir if tasks_dir is not None else (l_path.parent / "tasks" if l_path.parent.name == "rooms" else PROJECT_ROOT / "bmad" / "rooms" / "tasks")

    verified_task_ids: set[str] = set()

    # 1. Thu thập danh sách task đã được Settlement Gate kiểm định từ ledger
    if l_path.is_file():
        try:
            data = json.loads(l_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # Check root-level settlement records / verifications
                records = data.get("settlement_records") or data.get("settlement_verifications") or data.get("settlements")
                if isinstance(records, dict):
                    for tid, rec in records.items():
                        if isinstance(rec, dict):
                            if rec.get("verified") is True or str(rec.get("status", "")).upper() in ("VERIFIED", "APPROVED", "PASS", "SUCCESS"):
                                verified_task_ids.add(str(tid))
                        elif rec is True or str(rec).upper() in ("VERIFIED", "PASS"):
                            verified_task_ids.add(str(tid))
                elif isinstance(records, list):
                    for rec in records:
                        if isinstance(rec, dict):
                            tid = rec.get("task_id") or rec.get("id")
                            if tid is not None and (rec.get("verified") is True or str(rec.get("status", "")).upper() in ("VERIFIED", "APPROVED", "PASS", "SUCCESS")):
                                verified_task_ids.add(str(tid))

                # Check recent_events or history for settlement verification records
                events = data.get("history", []) + data.get("recent_events", [])
                for ev in events:
                    if isinstance(ev, dict):
                        action_str = f"{ev.get('action', '')} {ev.get('event', '')} {ev.get('summary', '')}".lower()
                        if "settlement" in action_str and ("verif" in action_str or "pass" in action_str or "approved" in action_str or ev.get("settlement_verified") is True):
                            tid = ev.get("task_id")
                            if tid is not None:
                                verified_task_ids.add(str(tid))
                            else:
                                m = re.search(r"#(\d+)", action_str)
                                if m:
                                    verified_task_ids.add(m.group(1))
                        elif ev.get("settlement_verified") is True:
                            tid = ev.get("task_id")
                            if tid is not None:
                                verified_task_ids.add(str(tid))
        except Exception:
            pass

    # 2. Thu thập danh sách task đã kiểm định từ disk (nếu có settlement.json hoặc settlement_verification.json)
    if t_dir.is_dir():
        for t_folder in t_dir.iterdir():
            if not t_folder.is_dir():
                continue
            tid = t_folder.name
            for s_name in ("settlement_verification.json", "settlement.json", "settlement_gate.json"):
                s_file = t_folder / s_name
                if s_file.is_file():
                    try:
                        s_data = json.loads(s_file.read_text(encoding="utf-8"))
                        if isinstance(s_data, dict) and (s_data.get("verified") is True or str(s_data.get("status", "")).upper() in ("VERIFIED", "APPROVED", "PASS", "SUCCESS")):
                            verified_task_ids.add(str(tid))
                    except Exception:
                        pass

    # 3. Quét kiểm tra các task chuyển sang Resolved trong ledger_path
    if l_path.is_file():
        try:
            data = json.loads(l_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # 3a. Quét trong history
                for ev in data.get("history", []):
                    if not isinstance(ev, dict):
                        continue
                    summary = str(ev.get("summary", ""))
                    summary_lower = summary.lower()
                    action = str(ev.get("action", "")).lower()
                    state = str(ev.get("state", "")).lower()
                    to_state = str(ev.get("to_state", "")).lower()
                    status = str(ev.get("status", "")).lower()

                    # Bỏ qua event nếu action là 'log' (nhật ký ghi chép tiến độ, không phải chuyển trạng thái)
                    if action == "log":
                        continue

                    # Bỏ qua event nếu action hoặc trạng thái đích là closed hoặc blocked
                    if (
                        action in ("close", "closed", "block", "blocked")
                        or state in ("closed", "blocked")
                        or to_state in ("closed", "blocked")
                        or status in ("closed", "blocked")
                    ):
                        continue

                    # Bỏ qua nếu summary thể hiện task được đóng (Closed) hoặc bị chặn (Blocked)
                    if bool(re.search(r"\b(?:closed|blocked|đóng|chặn|khoá|block)\b", summary_lower)):
                        continue

                    is_resolved = (
                        state == "resolved"
                        or to_state == "resolved"
                        or status == "resolved"
                        or action in ("resolve", "resolved", "submit_resolved")
                        or bool(re.search(r"\b(?:trạng thái|state|status|chuyển sang|nộp|mark(?:ed)?)\s*:?\s*resolved\b", summary_lower))
                    )

                    if is_resolved:
                        tid = ev.get("task_id")
                        if not tid:
                            m = re.search(r"#(\d+)", summary)
                            if m:
                                tid = m.group(1)
                        if tid is not None:
                            str_tid = str(tid)
                            # Kiểm tra xem bản thân event này có settlement_verified không
                            ev_verified = (
                                ev.get("settlement_verified") is True
                                or str(ev.get("settlement_gate", "")).upper() in ("VERIFIED", "APPROVED", "PASS")
                            )
                            if not ev_verified and str_tid not in verified_task_ids:
                                violations.append({
                                    "file": str(l_path.relative_to(PROJECT_ROOT)) if l_path.is_relative_to(PROJECT_ROOT) else str(l_path),
                                    "evidence": f"Task #{str_tid} chuyển trạng thái Resolved trong history nhưng thiếu biên bản xác thực của Settlement Gate (Dual-Verification Gate bypass)",
                                    "task_id": str_tid,
                                    "type": "settlement_gate_bypass",
                                })

                # 3b. Quét trong tasks dict (nếu có)
                tasks_dict = data.get("tasks", {})
                if isinstance(tasks_dict, dict):
                    for tid, tinfo in tasks_dict.items():
                        if isinstance(tinfo, dict) and str(tinfo.get("state", "")).lower() == "resolved":
                            t_verified = (
                                tinfo.get("settlement_verified") is True
                                or str(tinfo.get("settlement_gate", "")).upper() in ("VERIFIED", "APPROVED", "PASS")
                            )
                            if not t_verified and str(tid) not in verified_task_ids:
                                violations.append({
                                    "file": str(l_path.relative_to(PROJECT_ROOT)) if l_path.is_relative_to(PROJECT_ROOT) else str(l_path),
                                    "evidence": f"Task #{tid} trong bảng tasks có trạng thái Resolved nhưng thiếu biên bản xác thực của Settlement Gate",
                                    "task_id": str(tid),
                                    "type": "settlement_gate_bypass",
                                })
        except Exception:
            pass

    # 4. Quét kiểm tra các task folders trên disk
    if t_dir.is_dir():
        for task_folder in t_dir.iterdir():
            if not task_folder.is_dir():
                continue
            tid = task_folder.name
            candidates = list(task_folder.glob("handoff_*.md"))
            latest = task_folder / "latest_handoff.md"
            if latest.is_file():
                candidates.append(latest)

            for memo in candidates:
                try:
                    content = memo.read_text(encoding="utf-8")
                    lower = content.lower()
                    if ("trạng thái: resolved" in lower or "state: resolved" in lower or "status: resolved" in lower) and "chờ qc" in lower:
                        is_doc_verified = (
                            "settlement gate: verified" in lower
                            or "settlement gate: approved" in lower
                            or "settlement: pass" in lower
                            or "settlement_verified: true" in lower
                        )
                        if not is_doc_verified and str(tid) not in verified_task_ids:
                            violations.append({
                                "file": str(memo.relative_to(PROJECT_ROOT)) if memo.is_relative_to(PROJECT_ROOT) else memo.name,
                                "evidence": f"Task #{tid} tại {memo.name} nộp trạng thái Resolved nhưng thiếu biên bản kiểm định Settlement Gate",
                                "task_id": str(tid),
                                "type": "settlement_gate_bypass",
                            })
                except Exception:
                    pass

    # Deduplicate theo (type, task_id, file)
    seen = set()
    deduped = []
    for v in violations:
        key = (v.get("type"), str(v.get("task_id")), v.get("file"))
        if key not in seen:
            seen.add(key)
            deduped.append(v)

    return deduped


def audit_circuit_breaker(
    ledger_path: Optional[Path] = None,
    rooms_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Kiểm tra trạng thái Supervisor Circuit Breaker:
    Nếu Circuit Breaker đang ở trạng thái TRIPPED hoặc OPEN (>= 6 lỗi/15m),
    cảnh báo vi phạm để ngăn sub-agent tiếp tục spawn gây lãng phí tài nguyên và cascade failure.
    """
    violations: List[Dict[str, Any]] = []
    l_path = ledger_path if ledger_path is not None else (PROJECT_ROOT / "bmad" / "rooms" / "room_ledger.json")
    r_dir = rooms_dir if rooms_dir is not None else (l_path.parent if l_path.is_file() else PROJECT_ROOT / "bmad" / "rooms")

    # 1. Check in ledger
    if l_path.is_file():
        try:
            data = json.loads(l_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cb = data.get("circuit_breaker")
                if isinstance(cb, dict):
                    state = str(cb.get("state", "")).upper()
                    tripped = cb.get("tripped") is True
                    fail_count = cb.get("failure_count", 0)
                    if state in ("TRIPPED", "OPEN") or tripped or (isinstance(fail_count, int) and fail_count >= 6):
                        violations.append({
                            "file": str(l_path.relative_to(PROJECT_ROOT)) if l_path.is_relative_to(PROJECT_ROOT) else str(l_path),
                            "evidence": f"Supervisor Circuit Breaker đang ở trạng thái {state or 'TRIPPED'} (failures: {fail_count}/6, backoff: {cb.get('backoff_seconds', 'N/A')}s)",
                            "task_id": cb.get("task_id"),
                            "type": "circuit_breaker_tripped",
                        })
        except Exception:
            pass

    # 2. Check in circuit_breaker.json
    cb_file = r_dir / "circuit_breaker.json"
    if cb_file.is_file():
        try:
            cb_data = json.loads(cb_file.read_text(encoding="utf-8"))
            if isinstance(cb_data, dict):
                state = str(cb_data.get("state", "")).upper()
                tripped = cb_data.get("tripped") is True
                fail_count = cb_data.get("failure_count", 0)
                if state in ("TRIPPED", "OPEN") or tripped or (isinstance(fail_count, int) and fail_count >= 6):
                    violations.append({
                        "file": str(cb_file.relative_to(PROJECT_ROOT)) if cb_file.is_relative_to(PROJECT_ROOT) else str(cb_file),
                        "evidence": f"Supervisor Circuit Breaker tại {cb_file.name} đang ở trạng thái {state or 'TRIPPED'} (failures: {fail_count}/6, backoff: {cb_data.get('backoff_seconds', 'N/A')}s)",
                        "task_id": cb_data.get("task_id"),
                        "type": "circuit_breaker_tripped",
                    })
        except Exception:
            pass

    return violations


def run_slppc_audit(auto_record: bool = True) -> Dict[str, Any]:
    """Chạy toàn bộ các chốt chặn kiểm tra quy trình SLPPC."""
    results = {
        "status": "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "violations_detected": 0,
        "violations_list": [],
        "minutes_created": [],
    }

    # 1. Kiểm tra Lead Role Trespass
    lead_trespasses = audit_lead_role_trespass()
    for v in lead_trespasses:
        results["violations_detected"] += 1
        v_info = {
            "from": "Supervisor",
            "to": "Lead",
            "type": "role_trespass",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Lead Dev tự ý code sản phẩm thay vì phân rã Zero-Search Task cho Peer Devs.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="Supervisor",
                to_role="Lead",
                violation_type="role_trespass",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 2. Kiểm tra PM Bypass
    pm_bypasses = audit_pm_bypass()
    for v in pm_bypasses:
        results["violations_detected"] += 1
        v_info = {
            "from": "PM",
            "to": "Supervisor",
            "type": "pm_bypass",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Bỏ qua cổng thẩm định Khả thi & Phù hợp của PM Agent trước khi tạo/kích hoạt Epic.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="PM",
                to_role="Supervisor",
                violation_type="pm_bypass",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 3. Kiểm tra Premature Close
    premature_closes = audit_premature_close()
    for v in premature_closes:
        results["violations_detected"] += 1
        v_info = {
            "from": "QC",
            "to": "Peer",
            "type": "premature_close",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Peer tự ý đóng task thay vì nộp trạng thái Resolved để QC nghiệm thu độc lập.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="QC",
                to_role="Peer",
                violation_type="premature_close",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 4. Kiểm tra Vague Specs
    vague_specs = audit_vague_specs()
    for v in vague_specs:
        results["violations_detected"] += 1
        v_info = {
            "from": "Peer",
            "to": "Lead",
            "type": "vague_specs",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Giao task vi phạm quy chuẩn Zero-Search Mandate (thiếu các trường bắt buộc).",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="Peer",
                to_role="Lead",
                violation_type="vague_specs",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 5. Kiểm tra Ephemeral Room Hygiene
    hygiene_issues = audit_ephemeral_room_hygiene()
    for v in hygiene_issues:
        results["violations_detected"] += 1
        v_info = {
            "from": "QC",
            "to": "Supervisor",
            "type": v.get("type", "room_hygiene_violation"),
            "evidence": v["evidence"],
            "message": "Vi phạm quy chuẩn vệ sinh phòng ban BMAD Rooms (file rác timestamp hoặc phình to ledger).",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="QC",
                to_role="Supervisor",
                violation_type=v.get("type", "room_hygiene_violation"),
                task_id=None,
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 6. Kiểm tra Settlement Verification Gate (Task Resolved bắt buộc có record verification của Settlement Gate)
    settlement_bypasses = audit_settlement_verification_gate()
    for v in settlement_bypasses:
        results["violations_detected"] += 1
        v_info = {
            "from": "QC",
            "to": "Peer",
            "type": "settlement_gate_bypass",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Task chuyển trạng thái Resolved mà thiếu biên bản xác thực kiểm định 2 chiều của Settlement Gate.",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="QC",
                to_role="Peer",
                violation_type="settlement_gate_bypass",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    # 7. Kiểm tra Circuit Breaker State
    cb_trips = audit_circuit_breaker()
    for v in cb_trips:
        results["violations_detected"] += 1
        v_info = {
            "from": "Supervisor",
            "to": "Supervisor",
            "type": "circuit_breaker_tripped",
            "evidence": v["evidence"],
            "task_id": v.get("task_id"),
            "message": "Supervisor Circuit Breaker ở trạng thái TRIPPED/OPEN do tỷ lệ lỗi vượt ngưỡng (>=6 lỗi/15m).",
        }
        results["violations_list"].append(v_info)
        if auto_record:
            path = record_violation_minute(
                from_role="Supervisor",
                to_role="Supervisor",
                violation_type="circuit_breaker_tripped",
                task_id=v.get("task_id"),
                evidence=v["evidence"],
                message=v_info["message"],
            )
            results["minutes_created"].append(str(path.relative_to(PROJECT_ROOT)))

    if results["violations_detected"] > 0:
        results["status"] = "violations_found"

    return results


# Alias for run_slppc_audit
run_audit = run_slppc_audit


def main():
    parser = argparse.ArgumentParser(description="SLPPC Flow Guard & Violation Auditor")
    parser.add_argument("command", nargs="?", default="audit", choices=["audit", "hygiene", "settlement"], help="Action to run: 'audit' (default), 'hygiene', or 'settlement'")
    parser.add_argument("--record", action="store_true", default=True, help="Tự động ghi biên bản vi phạm vào bmad/rooms/violations/")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả JSON")
    args = parser.parse_args()

    if args.command == "hygiene":
        issues = audit_ephemeral_room_hygiene()
        if args.json:
            print(json.dumps({"hygiene_violations": issues, "count": len(issues)}, indent=2, ensure_ascii=False))
            sys.exit(0 if not issues else 1)
        print("=" * 75)
        print("🧹 EPHEMERAL ROOM HYGIENE AUDIT")
        print("=" * 75)
        print(f"• Số lượng vi phạm: {len(issues)}")
        for idx, iss in enumerate(issues, 1):
            print(f"  {idx}. [{iss.get('type')}] {iss.get('evidence')}")
        if not issues:
            print("✅ PASS: 100% đạt chuẩn Ephemeral Room Hygiene (Zero-Leak, FIFO <= 50, Single-Pointer).")
        print("=" * 75)
        sys.exit(0 if not issues else 1)

    if args.command == "settlement":
        issues = audit_settlement_verification_gate()
        if args.json:
            print(json.dumps({"settlement_violations": issues, "count": len(issues)}, indent=2, ensure_ascii=False))
            sys.exit(0 if not issues else 1)
        print("=" * 75)
        print("⚖️ SETTLEMENT VERIFICATION GATE AUDIT")
        print("=" * 75)
        print(f"• Số lượng vi phạm: {len(issues)}")
        for idx, iss in enumerate(issues, 1):
            print(f"  {idx}. [{iss.get('type')}] Task #{iss.get('task_id')}: {iss.get('evidence')}")
        if not issues:
            print("✅ PASS: 100% các task Resolved đều có xác thực hợp lệ từ Settlement Gate.")
        print("=" * 75)
        sys.exit(0 if not issues else 1)

    res = run_slppc_audit(auto_record=args.record)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    print("=" * 75)
    print("🛡️ SLPPC FLOW GUARD & GOVERNANCE AUDITOR")
    print("=" * 75)
    print(f"• Thời gian quét     : {res['timestamp']}")
    print(f"• Vi phạm phát hiện  : {res['violations_detected']}")
    if res['minutes_created']:
        print(f"• Biên bản đã lập    : {len(res['minutes_created'])}")
        for m in res['minutes_created']:
            print(f"  ➔ {m}")

    if res['violations_detected'] == 0:
        print("✅ PASS: 100% tuân thủ mô hình SLPPC. Không có vi phạm quyền hạn hay quy trình.")
    else:
        print("⚠️ CẢNH BÁO: Đã phát hiện vi phạm rào cản thẩm quyền điều hành.")
    print("=" * 75)


if __name__ == "__main__":
    main()
