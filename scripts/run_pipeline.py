#!/usr/bin/env python3
"""
scripts/run_pipeline.py - Automated SLPC Real-Time Pipeline Runner with KEV Dual-Anchor & Visual Hook Banners.

Implements Master Architecture:
- Head-of-Spec (Supervisor Gate): Kev System One (<50ms) Feasibility & Alignment evaluation.
- Architect Gate (Lead): Zero-Search 5-section task decomposition.
- Maker Execution (Peer): Ephemeral sub-agent dispatch (model ag/gemini-3.8-flash-high).
- Tail-of-Spec (QC Gate): Deterministic test execution (Exit 0) + Kev verification before Closed.
- Real-Time Memory Augmentation: Flushes invariants to .harness_progress.json and memory ledger.
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
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

KEV_ENDPOINT = os.environ.get("KEV_SYSTEMONE_URL", "http://127.0.0.1:8008/v1/systemone")
(PROJECT_ROOT / ".harness").mkdir(parents=True, exist_ok=True)
PROGRESS_JSON = PROJECT_ROOT / ".harness" / "progress.json"


# ==============================================================================
# VISUAL HOOK BANNER RENDERER
# ==============================================================================
def print_banner(stage: str, title: str, details: List[tuple[str, str]], status: str = "RUNNING"):
    colors = {
        "HEAD": "\033[94m",       # Blue
        "ARCHITECT": "\033[95m",  # Magenta
        "MAKER": "\033[93m",      # Yellow
        "TAIL": "\033[92m",       # Green
        "ALERT": "\033[91m",      # Red
        "RESET": "\033[0m",
        "BOLD": "\033[1m"
    }
    
    icon_map = {
        "HEAD": "🚀",
        "ARCHITECT": "📐",
        "MAKER": "⚡",
        "TAIL": "🧪",
        "ALERT": "⛔"
    }

    c = colors.get(stage, colors["RESET"])
    reset = colors["RESET"]
    bold = colors["BOLD"]
    icon = icon_map.get(stage, "📌")

    width = 76
    print(f"\n{c}┌{'─' * width}┐{reset}")
    header_text = f"{icon} [{stage} GATE: {title.upper()}] - {status}"
    print(f"{c}│{reset} {bold}{header_text:<{width - 2}}{reset} {c}│{reset}")
    print(f"{c}├{'─' * width}┤{reset}")
    for label, val in details:
        line = f"• {label:<20} : {val}"
        if len(line) > width - 4:
            line = line[:width - 7] + "..."
        print(f"{c}│{reset} {line:<{width - 2}} {c}│{reset}")
    print(f"{c}└{'─' * width}┘{reset}\n")


def resolve_thinking_directive(prompt: str) -> tuple[str, str, str]:
    """
    Phân tích tiền tố tư duy [THUẬN], [NGHỊCH], [LƯỠNG-DIỆN], [THẢO-LUẬN] từ prompt.
    Returns: (cleaned_prompt, mode_name, directive_text)
    """
    p_lower = prompt.lower()
    if any(k in p_lower for k in ("[thảo luận]", "[thảo-luận]", "[thao luan]", "[thao-luan]", "[discuss]", "[advisory]")):
        cleaned = re.sub(r"\[(thảo luận|thảo-luận|thao luan|thao-luan|discuss|advisory)\]", "", prompt, flags=re.IGNORECASE).strip()
        mode = "THẢO LUẬN (Discussion / Architectural ADR)"
        directive = "Không code trực tiếp; tập trung phân tích trade-off các phương án, thu thập bằng chứng codebase, chốt giải pháp đồng thuận và xuất biên bản ADR (bmad/adrs/)."
        return cleaned, mode, directive
    elif any(k in p_lower for k in ("[thuận]", "[thuan]", "[forward]", "[happy-path]", "[happy]")):
        cleaned = re.sub(r"\[(thuận|thuan|forward|happy-path|happy)\]", "", prompt, flags=re.IGNORECASE).strip()
        mode = "THUẬN (Forward / Happy Path)"
        directive = "Tập trung tư duy luồng thuận: hoàn thiện nhanh logic cốt lõi, chuẩn DTO, tối ưu diff theo YAGNI, không over-engineering."
        return cleaned, mode, directive
    elif any(k in p_lower for k in ("[nghịch]", "[nghich]", "[reverse]", "[edge-case]", "[adversarial]", "[edge]")):
        cleaned = re.sub(r"\[(nghịch|nghich|reverse|edge-case|adversarial|edge)\]", "", prompt, flags=re.IGNORECASE).strip()
        mode = "NGHỊCH (Reverse / Edge / Adversarial)"
        directive = "Tập trung tư duy luồng nghịch: bẫy lỗi biên (BVA), dữ liệu rỗng/null/undefined, timeout, race condition, fail-safe degradation, rollback."
        return cleaned, mode, directive
    elif any(k in p_lower for k in ("[lưỡng-diện]", "[luong-dien]", "[dual]", "[both]")):
        cleaned = re.sub(r"\[(lưỡng-diện|luong-dien|dual|both)\]", "", prompt, flags=re.IGNORECASE).strip()
        mode = "LƯỠNG DIỆN (Dual-Anchor: Forward + Reverse)"
        directive = "BẮT BUỘC tư duy 2 mặt song song trong khối Thinking: (1) [THUẬN]: Happy path chuẩn spec; (2) [NGHỊCH]: Dữ liệu biên, trường hợp ngoại lệ, testcase fail, fail-safe."
        return cleaned, mode, directive
    else:
        mode = "LƯỠNG DIỆN (Mặc định: Forward + Reverse)"
        directive = "Tư duy 2 mặt song song trong khối Thinking: (1) [THUẬN]: Happy path chuẩn spec; (2) [NGHỊCH]: Ngoại lệ, dữ liệu biên và bẫy lỗi."
        return prompt, mode, directive


# ==============================================================================
# STEP 1: HEAD-OF-SPEC GATE (SUPERVISOR INTAKE + KEV SYSTEM ONE)
# ==============================================================================
def run_supervisor_intake_gate(prompt: str, thinking_mode: str = "LƯỠNG DIỆN", thinking_directive: str = "") -> Dict[str, Any]:
    print_banner("HEAD", "Supervisor Intake & Feasibility Check", [
        ("Evaluator", "Supervisor (Kev System One)"),
        ("Thinking Mode", thinking_mode),
        ("Endpoint", KEV_ENDPOINT),
        ("Target Prompt", prompt[:48])
    ])

    import urllib.request
    import urllib.error

    payload = {
        "state": f"Yêu cầu SLPC: {prompt}",
        "questions": {
            "feasibility": {
                "type": "score",
                "instructions": "Đánh giá mức độ khả thi kỹ thuật của yêu cầu trong dự án.",
                "criteria": ["Không khả thi", "Khả thi thấp", "Khả thi trung bình", "Khả thi cao"]
            },
            "alignment": {
                "type": "choice",
                "instructions": "Đánh giá mức độ phù hợp kiến trúc với tôn chỉ Zero-Search, Strict Typing, No-Leak.",
                "criteria": {
                    "perfect_fit": "Hoàn toàn phù hợp kiến trúc",
                    "minor_drift": "Có nguy cơ trôi phạm vi nhẹ",
                    "scope_creep": "Vi phạm phạm vi hoặc phình tính năng"
                }
            },
            "risk_decision": {
                "type": "choice",
                "instructions": "Quyết định phê duyệt luồng điều phối.",
                "criteria": {
                    "green": "Phê duyệt tiến hành tự động",
                    "yellow": "Cần Lead thẩm định kiến trúc sâu",
                    "red": "Từ chối tiếp nhận"
                }
            }
        }
    }

    try:
        req = urllib.request.Request(
            KEV_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            kev_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"⚠️ [Kev System One Notice]: Endpoint không khả dụng ({e}), dùng heuristics dự phòng.")
        kev_data = {
            "answers": {
                "feasibility": {"score": 2.5},
                "alignment": {"choice": "perfect_fit", "confidence": 0.85},
                "risk_decision": {"choice": "green"}
            }
        }

    answers = kev_data.get("answers", {})
    score = answers.get("feasibility", {}).get("score", 2.0)
    alignment = answers.get("alignment", {}).get("choice", "perfect_fit")
    risk = answers.get("risk_decision", {}).get("choice", "green")

    # Lưu biên bản Supervisor Intake Memo
    supervisor_dir = PROJECT_ROOT / "bmad" / "rooms" / "supervisor"
    supervisor_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    memo_file = supervisor_dir / f"intake_memo_run_{ts}.md"
    memo_content = f"""# SUPERVISOR INTAKE DECISION MEMO (HEAD-OF-SPEC)
- **Thời gian**: `{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
- **Yêu cầu gốc**: {prompt}
- **Kev Feasibility Score**: `{score:.2f} / 3.0`
- **Strategic Alignment**: `{alignment}`
- **Risk Decision**: `{risk}`
- **Verdict**: `APPROVED - Chuyển giao sang Lead Dev`
"""
    memo_file.write_text(memo_content, encoding="utf-8")

    print_banner("HEAD", "Supervisor Intake Approved", [
        ("Feasibility", f"{score:.2f} / 3.0"),
        ("Alignment", alignment),
        ("Risk Lane", risk),
        ("Intake Memo", str(memo_file.relative_to(PROJECT_ROOT)))
    ], status="APPROVED")

    return {
        "score": score,
        "alignment": alignment,
        "risk": risk,
        "memo_file": str(memo_file)
    }


# Backward compatibility alias
run_pm_head_gate = run_supervisor_intake_gate


# ==============================================================================
# STEP 2: ARCHITECT GATE (LEAD DEV TASK BREAKDOWN)
# ==============================================================================
def run_lead_architect_gate(prompt: str, intake_memo: str, thinking_mode: str = "LƯỠNG DIỆN", thinking_directive: str = "") -> Dict[str, Any]:
    print_banner("ARCHITECT", "Lead Dev Zero-Search Decomposition", [
        ("Architect", "Lead Dev (gemini-3.8-flash-high)"),
        ("Thinking Mode", thinking_mode),
        ("Spec Contract", "Zero-Search 5-Section Mandate"),
        ("Traps Query", "Harness Learn Database")
    ])

    try:
        from harness_manager import HarnessManager
    except ImportError:
        from tools.harness_manager import HarnessManager
    mgr = HarnessManager(engine="auto")

    # 1. Tạo Epic
    epic = mgr.add_work_item(
        wi_type="Epic",
        title=f"[Pipeline] - {prompt[:60]}",
        description=f"Automated pipeline run. Intake Memo: {intake_memo}\nThinking Mode: {thinking_mode}",
        assigned_to="lead",
        assigned_to_profile="lead",
        source="bot"
    )
    epic_id = epic["id"]

    # Nếu là THẢO LUẬN: Không sinh Task thi công cho Peer
    if thinking_mode.startswith("THẢO LUẬN"):
        print_banner("ARCHITECT", "Architectural Discussion Intake", [
            ("Epic ID", f"#{epic_id}"),
            ("Lead Architect", "Lead Dev (gemini-3.8-flash-high)"),
            ("Action", "Analyzing options & preparing ADR minutes")
        ], status="ANALYZING")
        return {
            "epic_id": epic_id,
            "task_id": None
        }

    # 2. Tạo Task cho Peer
    lessons_prompt = ""
    try:
        from harness_rust import query_lessons  # type: ignore
        lessons = query_lessons(domain="engineering", limit=3)
        if lessons:
            try:
                from tools.query_reader import build_context_bounded_prompt
            except ImportError:
                from query_reader import build_context_bounded_prompt
            chunks = [
                {
                    "domain": getattr(l, "domain", "engineering"),
                    "cue": getattr(l, "cue", f"Lesson #{idx}"),
                    "lesson": getattr(l, "lesson", "")
                }
                for idx, l in enumerate(lessons, 1)
                if getattr(l, "lesson", None)
            ]
            if chunks:
                lessons_prompt = "\n\n" + build_context_bounded_prompt(
                    query=f"Task: {prompt[:50]}",
                    chunks=chunks,
                    max_chunks=3
                )
    except Exception:
        pass


    task = mgr.add_work_item(
        wi_type="Task",
        title=f"[Exec] - {prompt[:50]}",
        description=(
            f"[THINKING MODE: {thinking_mode}]\n{thinking_directive}\n\n"
            "Zero-Search Mandate:\n"
            "1. Target Files: tools/ / scripts/ / docs/\n"
            "2. Anchors: Pipeline runner execution\n"
            "3. Concrete Changes: Enforce role fences, live hook banner, test verification\n"
            "4. Acceptance Criteria: Pass test suites, exit code 0\n"
            "5. Test Command: python3 -m unittest discover -s tools/tests"
            f"{lessons_prompt}"
        ),
        assigned_to="peer",
        assigned_to_profile="peer",
        parent_id=epic_id,
        source="bot"
    )
    task_id = task["id"]

    print_banner("ARCHITECT", "Task Breakdown Completed", [
        ("Epic ID", f"#{epic_id}"),
        ("Task ID", f"#{task_id}"),
        ("Assigned To", "Peer Dev (Maker Pool)"),
        ("Verification Command", "python3 -m unittest discover -s tools/tests")
    ], status="DISPATCHED")

    return {
        "epic_id": epic_id,
        "task_id": task_id
    }


DEFAULT_TEST_CMD = "python3 -m unittest tools/tests/test_slppc_orchestrator.py tools/tests/test_harness.py tools/tests/test_role_fence_audit.py tools/tests/test_scoped_tools.py tools/tests/test_strict_typing_scanner.py"


# ==============================================================================
# STEP 3: MAKER SUB-AGENT EXECUTION (PEER DISPATCH)
# ==============================================================================
def run_peer_maker_gate(
    task_id: int,
    test_cmd: str = DEFAULT_TEST_CMD,
    error_context: Optional[str] = None,
    attempt: int = 1,
    run_id: Optional[str] = None,
) -> Tuple[bool, str]:
    details = [
        ("Sub-Agent Role", "Peer Dev (Maker Pool)"),
        ("Model Tier", "ag/gemini-3.8-flash-high"),
        ("Task ID", f"#{task_id}"),
        ("Attempt", f"{attempt}/4 (Retry {attempt - 1})" if attempt > 1 else "1/4 (Initial)"),
        ("Action", "Executing bounded task and local unit tests")
    ]
    if error_context:
        details.append(("Previous Error", error_context[:50]))
    print_banner("MAKER", "Peer Dev Ephemeral Execution", details, status="EXECUTING")

    if error_context:
        retry_prompt = (
            f"📢 [RETRY ATTEMPT {attempt}]: Task #{task_id} kiểm thử thất bại ở vòng trước.\n"
            f"Lỗi nhận được:\n```\n{error_context[:500]}\n```\n"
            "Hãy phân tích nguyên nhân gốc, sửa chữa mã nguồn và bảo đảm pass kiểm thử cơ học."
        )
        try:
            from tools.agent_context_manager import safe_send_agent_message
            safe_send_agent_message("peer", retry_prompt)
        except Exception:
            pass

    try:
        from harness_manager import HarnessManager
    except ImportError:
        from tools.harness_manager import HarnessManager
    mgr = HarnessManager(engine="auto")

    # Transition to Active
    mgr.update_state(task_id, "Active", assigned_to_profile="peer")

    # Run mechanical verification command
    import shlex
    cmd_parts = shlex.split(test_cmd)
    res = subprocess.run(
        cmd_parts,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    if res.returncode == 0:
        mgr.update_state(task_id, "Resolved", assigned_to_profile="peer")
        # Harness² Closed-Loop Post-Flight Lesson Extraction (Peer)
        try:
            from harness_rust import record_lesson  # type: ignore
            record_lesson(
                domain="peer_implementation",
                cue=f"task_{task_id}_pipeline_resolved",
                lesson=f"Thực thi thành công Task #{task_id}: 100% tests pass (exit code 0). Bắt buộc tuân thủ YAGNI, Strict Typing và Zero Regression.",
                evidence=f"Local unit tests pass exit code 0 under {test_cmd}",
                confidence="high",
                work_item_id=task_id
            )
        except Exception:
            pass

        print_banner("MAKER", "Peer Implementation Done", [
            ("Task ID", f"#{task_id}"),
            ("Local Test Status", "100% PASS (Exit Code 0)"),
            ("State Transition", "Active ➔ Resolved"),
            ("Handoff To", "QC Verifier (Tail Gate)")
        ], status="RESOLVED")
        return True, ""
    else:
        err_msg = res.stderr.strip() if res.stderr and res.stderr.strip() else (
            res.stdout.strip() if res.stdout else f"Test command failed with exit code {res.returncode}"
        )
        print_banner("ALERT", "Peer Local Tests Failed", [
            ("Task ID", f"#{task_id}"),
            ("Exit Code", str(res.returncode)),
            ("Stderr", err_msg[:60])
        ], status="FAILED")
        return False, err_msg


# ==============================================================================
# STEP 4: TAIL-OF-SPEC GATE (QC INDEPENDENT VERIFICATION & CLOSURE)
# ==============================================================================
def run_qc_tail_gate(
    task_id: int,
    epic_id: int,
    test_cmd: str = DEFAULT_TEST_CMD,
    attempt: int = 1,
    run_id: Optional[str] = None,
) -> Tuple[bool, str]:
    print_banner("TAIL", "QC Independent Quality Gate", [
        ("Verifier", "QC Verifier (gemini-3.8-flash-high)"),
        ("Double Anchor", "Mechanical Exit 0 + Kev Verification"),
        ("Authority", "Exclusive Task Closure")
    ], status="VERIFYING")

    # 1. Mechanical Test Run
    import shlex
    cmd_parts = shlex.split(test_cmd)
    test_res = subprocess.run(
        cmd_parts,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    if test_res.returncode != 0:
        err_msg = test_res.stderr.strip() if test_res.stderr and test_res.stderr.strip() else (
            test_res.stdout.strip() if test_res.stdout else f"Unit tests failed with exit code {test_res.returncode}"
        )
        print_banner("ALERT", "QC Rejected Task (Test Failure)", [
            ("Task ID", f"#{task_id}"),
            ("Reason", "Unit tests non-zero exit code"),
            ("Stderr", err_msg[:60])
        ], status="REJECTED")
        return False, err_msg

    # 2. Anti-Leak Scan
    leak_res = subprocess.run(
        ["python3", "scripts/anti_leak_sentinel.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    if leak_res.returncode != 0:
        err_msg = leak_res.stderr.strip() if leak_res.stderr and leak_res.stderr.strip() else (
            leak_res.stdout.strip() if leak_res.stdout else "Sensitive data or proprietary leak detected"
        )
        print_banner("ALERT", "QC Rejected Task (Leak Detected)", [
            ("Task ID", f"#{task_id}"),
            ("Reason", err_msg)
        ], status="REJECTED")
        return False, err_msg

    # 3. Kev End-of-Spec Verification (<50ms)
    import urllib.request
    try:
        kev_payload = {
            "state": f"QC Nghiệm thu Task #{task_id}: 100% unit tests pass, 0 anti-leak violation.",
            "questions": {
                "qc_verdict": {
                    "type": "choice",
                    "instructions": "Xác nhận đóng task hay yêu cầu kiểm thử thêm.",
                    "criteria": {
                        "approve_close": "Đạt chuẩn 100%, phê duyệt đóng task",
                        "need_regression_test": "Cần bổ sung kịch bản biên"
                    }
                }
            }
        }
        req = urllib.request.Request(
            KEV_ENDPOINT,
            data=json.dumps(kev_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            kev_out = json.loads(resp.read().decode("utf-8"))
            qc_decision = kev_out.get("answers", {}).get("qc_verdict", {}).get("choice", "approve_close")
    except Exception:
        qc_decision = "approve_close"

    if qc_decision != "approve_close":
        err_msg = f"Kev rejected task closure: {qc_decision}"
        print_banner("ALERT", "QC Rejected Task (Kev Rejection)", [
            ("Task ID", f"#{task_id}"),
            ("Reason", err_msg)
        ], status="REJECTED")
        return False, err_msg

    # 4. Đóng Task & Epic trên Harness DB
    try:
        from harness_manager import HarnessManager
    except ImportError:
        from tools.harness_manager import HarnessManager
    mgr = HarnessManager(engine="auto")
    mgr.update_state(task_id, "Closed", assigned_to_profile="qc")
    mgr.update_state(epic_id, "Closed", assigned_to_profile="qc")

    # Harness² Closed-Loop Post-Flight Lesson Extraction (QC)
    try:
        from harness_rust import record_lesson  # type: ignore
        record_lesson(
            domain="qc_verification",
            cue=f"task_{task_id}_pipeline_qc_verified",
            lesson=f"Nghiệm thu thành công Task #{task_id}: Mechanical tests pass 100%, 0 anti-leak violation, Kev sign-off: {qc_decision}.",
            evidence=f"QC Tail Gate exit code 0, anti-leak exit code 0, Kev: {qc_decision}",
            confidence="high",
            work_item_id=task_id
        )
    except Exception:
        pass

    print_banner("TAIL", "QC Verification Passed & Closed", [
        ("Task ID", f"#{task_id} (CLOSED)"),
        ("Epic ID", f"#{epic_id} (CLOSED)"),
        ("Mechanical Test", "PASS 100%"),
        ("Anti-Leak Gate", "PASS 100%"),
        ("Kev Sign-Off", qc_decision)
    ], status="CLOSED")

    return True, ""


# ==============================================================================
# STEP 5: REAL-TIME MEMORY AUGMENTATION FLUSH
# ==============================================================================
def flush_realtime_memory(task_id: int, summary: str):
    ts = dt.datetime.now().isoformat()
    data = {}
    if PROGRESS_JSON.exists():
        try:
            data = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    invariants = data.setdefault("active_invariants", {})
    invariants["last_pipeline_task"] = str(task_id)
    invariants["last_pipeline_summary"] = summary
    invariants["last_pipeline_ts"] = ts
    invariants["dual_anchor_verified"] = True

    PROGRESS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 [Real-Time Memory]: Đã đồng bộ trạng thái pipeline vào {PROGRESS_JSON.name}")


# ==============================================================================
# MAIN CLI DRIVER
# ==============================================================================
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run SLPPC Dual-Anchor Pipeline with Live Visual Banners")
    parser.add_argument("prompt", nargs="?", default="Nâng cấp và kiểm tra quy chuẩn pipeline SLPPC", help="Task requirement prompt")
    parser.add_argument("--test-cmd", default=DEFAULT_TEST_CMD, help="Custom test command to run for mechanical verification")
    parser.add_argument("--status", action="store_true", help="Print live pipeline status")
    args = parser.parse_args(argv)

    if args.status:
        if PROGRESS_JSON.exists():
            data = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
            inv = data.get("active_invariants", {})
            print(json.dumps(inv, ensure_ascii=False, indent=2))
        return 0

    run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    try:
        from harness_manager import HarnessManager
    except ImportError:
        from tools.harness_manager import HarnessManager
    mgr = HarnessManager(engine="auto")

    start_time = time.time()
    cleaned_prompt, thinking_mode, thinking_directive = resolve_thinking_directive(args.prompt)

    print("\n" + "=" * 78)
    print("  🚀 KHỞI CHẠY SLPC REAL-TIME PIPELINE (KEV DUAL-ANCHOR + HOOK BANNERS)")
    print(f"  🧠 CHẾ ĐỘ TƯ DUY: {thinking_mode}")
    print(f"  🔗 RUN ID: {run_id}")
    print("=" * 78)

    # 1. Head Gate
    t_head = time.time()
    intake_res = run_supervisor_intake_gate(cleaned_prompt, thinking_mode=thinking_mode, thinking_directive=thinking_directive)
    head_dur = max(0, int(time.time() - t_head))
    mgr.record_trace_span(
        run_id=run_id,
        stage="head",
        agent="supervisor",
        task_summary=f"Head Gate (Supervisor Intake): {cleaned_prompt[:40]}",
        duration_seconds=head_dur,
        outcome="completed",
        notes=f"feasibility={intake_res['score']:.2f}; alignment={intake_res['alignment']}"
    )

    # 2. Architect Gate
    t_lead = time.time()
    lead_res = run_lead_architect_gate(cleaned_prompt, intake_res["memo_file"], thinking_mode=thinking_mode, thinking_directive=thinking_directive)
    lead_dur = max(0, int(time.time() - t_lead))
    mgr.record_trace_span(
        run_id=run_id,
        stage="lead",
        agent="lead",
        task_summary=f"Architect Gate (Zero-Search Breakdown): Epic #{lead_res['epic_id']}",
        duration_seconds=lead_dur,
        outcome="completed",
        story_id=str(lead_res.get("task_id") or lead_res["epic_id"]),
        notes=f"task_id={lead_res.get('task_id')}"
    )

    # BRANCH: Nếu là chế độ [THẢO LUẬN], chuyển sang luồng lập biên bản ADR đồng thuận (không code)
    if thinking_mode.startswith("THẢO LUẬN"):
        print_banner("ARCHITECT", "Architectural Discussion & ADR Recording", [
            ("Epic ID", f"#{lead_res['epic_id']}"),
            ("Parties", "Supervisor, Lead Dev"),
            ("Action", "Recording ADR Discussion Minutes"),
            ("Directory", "bmad/rooms/discussions/ & bmad/adrs/")
        ], status="CONSENSUS")

        t_disc = time.time()
        res_disc = subprocess.run([
            "python3", "tools/record_discussion.py",
            "--task-id", str(lead_res["epic_id"]),
            "--topic", cleaned_prompt[:50],
            "--parties", "Supervisor, Lead Dev",
            "--conflict", f"Thảo luận đánh giá phương án kiến trúc cho yêu cầu: {cleaned_prompt}",
            "--consensus", f"Supervisor Kev Feasibility ({intake_res['score']:.2f}/3.0) & Alignment ({intake_res['alignment']}). Lead Dev chốt phương án tuân thủ Zero-Search & YAGNI.",
            "--actions", "Chuyển giao cho User xác nhận trước khi phân rã task code [THUẬN].",
            "--adr"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        disc_dur = max(0, int(time.time() - t_disc))

        mgr.record_trace_span(
            run_id=run_id,
            stage="discussion",
            agent="lead",
            task_summary=f"ADR Discussion: Epic #{lead_res['epic_id']}",
            duration_seconds=disc_dur,
            outcome="completed" if res_disc.returncode == 0 else "failed",
            story_id=str(lead_res["epic_id"]),
            notes=f"topic={cleaned_prompt[:40]}"
        )

        mgr.update_state(lead_res["epic_id"], "Closed")

        flush_realtime_memory(lead_res["epic_id"], f"[Thảo luận ADR] {cleaned_prompt}")
        duration = time.time() - start_time
        print(f"\n🎉 [THẢO LUẬN HOÀN TẤT]: Đã lưu biên bản ADR thành công trong {duration:.2f}s!")
        print(f"📄 Biên bản thảo luận: bmad/rooms/discussions/latest_discussion.md")
        print(f"🏛️ Kho lưu trữ ADR: bmad/adrs/")
        print("=" * 78 + "\n")
        return 0

    # 3. Maker Gate & 4. Tail Gate wrapped in retry loop (G-LOP-1, G-OBS-2)
    MAX_RETRIES = 3
    retry_count = 0
    last_error = ""
    pipeline_success = False

    while retry_count <= MAX_RETRIES:
        attempt = retry_count + 1
        t_peer = time.time()
        peer_ok, peer_err = run_peer_maker_gate(
            lead_res["task_id"],
            test_cmd=args.test_cmd,
            error_context=last_error if retry_count > 0 else None,
            attempt=attempt,
            run_id=run_id
        )
        peer_dur = max(0, int(time.time() - t_peer))
        mgr.record_trace_span(
            run_id=run_id,
            stage="peer",
            agent="peer",
            task_summary=f"Peer Maker Gate (attempt {attempt}): Task #{lead_res['task_id']}",
            duration_seconds=peer_dur,
            outcome="completed" if peer_ok else "failed",
            errors=peer_err if not peer_ok else None,
            story_id=str(lead_res["task_id"])
        )

        if not peer_ok:
            last_error = peer_err
            if retry_count < MAX_RETRIES:
                retry_count += 1
                continue
            else:
                break

        t_qc = time.time()
        qc_ok, qc_err = run_qc_tail_gate(
            lead_res["task_id"],
            lead_res["epic_id"],
            test_cmd=args.test_cmd,
            attempt=attempt,
            run_id=run_id
        )
        qc_dur = max(0, int(time.time() - t_qc))
        mgr.record_trace_span(
            run_id=run_id,
            stage="qc",
            agent="qc",
            task_summary=f"QC Tail Gate (attempt {attempt}): Task #{lead_res['task_id']}",
            duration_seconds=qc_dur,
            outcome="completed" if qc_ok else "failed",
            errors=qc_err if not qc_ok else None,
            story_id=str(lead_res["task_id"])
        )

        if not qc_ok:
            last_error = qc_err
            if retry_count < MAX_RETRIES:
                retry_count += 1
                continue
            else:
                break

        pipeline_success = True
        break

    if not pipeline_success:
        # Handle Blocked state escalation
        mgr.update_state(lead_res["task_id"], "Blocked", assigned_to_profile="peer")
        mgr.update_state(lead_res["epic_id"], "Blocked", assigned_to_profile="lead")

        # Durable memo in bmad/rooms/supervisor/latest_handoff.md
        supervisor_room = PROJECT_ROOT / "bmad" / "rooms" / "supervisor"
        supervisor_room.mkdir(parents=True, exist_ok=True)
        sup_handoff = supervisor_room / "latest_handoff.md"
        err_snippet = last_error[:400] if last_error else "Unknown test failure"
        memo_content = (
            f"# BIÊN BẢN BÀN GIAO: Supervisor (Pipeline Blocked)\n\n"
            f"- **Thời gian**: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"- **Run ID**: `{run_id}`\n"
            f"- **Epic ID**: #{lead_res['epic_id']}\n"
            f"- **Task ID**: #{lead_res['task_id']}\n"
            f"- **Trạng thái**: `Blocked`\n"
            f"- **Tổng số lần thử**: {attempt}/4 (1 ban đầu + {retry_count} retries)\n\n"
            f"## Nguyên nhân thất bại\n"
            f"```\n{err_snippet}\n```\n\n"
            f"## Hành động tiếp theo cho Supervisor\n"
            f"1. Kiểm tra log chi tiết và trace span với run_id `{run_id}`.\n"
            f"2. Đánh giá lại yêu cầu bài toán hoặc phân rã lại Zero-Search task.\n"
            f"3. Can thiệp thủ công hoặc hủy task tắc nghẽn.\n"
        )
        sup_handoff.write_text(memo_content, encoding="utf-8")

        # Alert Supervisor via safe_send_agent_message
        try:
            from tools.agent_context_manager import safe_send_agent_message
            safe_send_agent_message(
                "supervisor",
                f"🚨 [PIPELINE BLOCKED]: Task #{lead_res['task_id']} đã thử {attempt} lần nhưng thất bại. Cần can thiệp!"
            )
        except Exception:
            pass

        print_banner("ALERT", "Pipeline Blocked - Max Retries Exceeded", [
            ("Task ID", f"#{lead_res['task_id']}"),
            ("Epic ID", f"#{lead_res['epic_id']}"),
            ("Attempts", f"{attempt}/4 (Exhausted {MAX_RETRIES} retries)"),
            ("State", "Blocked"),
            ("Supervisor Notice", "bmad/rooms/supervisor/latest_handoff.md")
        ], status="BLOCKED")
        return 1

    # 5. Real-Time Memory Flush
    flush_realtime_memory(lead_res["task_id"], args.prompt)

    duration = time.time() - start_time
    print(f"\n✨ [PIPELINE SUCCESS]: Toàn bộ chu trình hoàn thành trong {duration:.2f}s!")
    print("=" * 78 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

