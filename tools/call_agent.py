#!/usr/bin/env python3
"""
tools/call_agent.py - Dispatcher for Supervisor to call Paseo agent profiles.
"""
import os
import sys
import json
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.home() / ".paseo" / "config.json"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def resolve_room(role_name: str) -> str:
    r = role_name.lower()
    if "supervisor" in r:
        return "supervisor"
    if "lead" in r:
        return "lead"
    if "qc" in r:
        return "qc"
    return "peer"

def get_profiles():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    profiles = data.get("daemon", {}).get("agentProfiles", [])
    return {p["name"].lower(): p for p in profiles}

import re

def resolve_thinking_directive(prompt: str) -> tuple[str, str, str]:
    """
    Phân tích tiền tố tư duy [THUẬN], [NGHỊCH], [LƯỠNG-DIỆN] từ prompt.
    Returns: (cleaned_prompt, mode_name, directive_text)
    """
    p_lower = prompt.lower()
    if any(k in p_lower for k in ("[thuận]", "[thuan]", "[forward]", "[happy-path]", "[happy]")):
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

def print_hook_banner(status: str, role: str, task_id: Any, model: str, from_role: str, details: str = "", thinking_mode: str = ""):
    width = 76
    print("\n" + "─" * width)
    print(f"🚀 [SLPPC SUB-AGENT HOOK DISPATCH] - {status}")
    print("─" * width)
    print(f"• Sub-Agent Role   : {role}")
    print(f"• Task / Work Item : #{task_id if task_id else 'N/A'}")
    print(f"• Model / Tier     : {model}")
    print(f"• Handoff Boundary : {from_role} ➔ {role}")
    if thinking_mode:
        print(f"• Thinking Mode    : {thinking_mode}")
    if details:
        print(f"• Instructions     : {details[:60]}")
    print("─" * width + "\n")

def main():
    parser = argparse.ArgumentParser(description="Call or wake up a Paseo agent profile (with automatic Research & Gen pipeline and SLP Room Handoff).")
    parser.add_argument("--profile", required=True, help="Target profile name (e.g. Supervisor, Lead, Peer, QC, Lead BA, Lead Dev, etc.)")
    parser.add_argument("--prompt", required=True, help="Task description or prompt for the agent")
    parser.add_argument("--from-profile", default="Supervisor", help="Sender profile name (default: Supervisor)")
    parser.add_argument("--goal", help="Ultimate Goal of the task (3-part delegation)")
    parser.add_argument("--constraints", help="Hard Constraints (e.g. TDS UI tokens, Angular 18, no new deps)")
    parser.add_argument("--suggested-path", help="Suggested Temporary Path from Lead (non-binding)")
    parser.add_argument("--challenge", action="store_true", help="Flag for Peer challenging Lead's architecture with evidence")
    parser.add_argument("--evidence", help="Empirical evidence (compiler log, benchmark, test failure) supporting challenge")
    parser.add_argument("--item-id", type=int, help="Harness Work Item ID (optional)")
    parser.add_argument("--source", help="Optional target source file to auto-generate 5-Stage ISTQB unit tests")
    parser.add_argument("--spec", help="Optional spec file path")
    parser.add_argument("--uc", help="Optional Use Case code (e.g. UC1.01)")
    parser.add_argument("--skip-pre-gen", action="store_true", help="Skip automatic pre-spawn Research & Gen execution")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    profiles = get_profiles()
    key = args.profile.strip().lower()
    profile = profiles.get(key)

    if not profile:
        matches = [p for name, p in profiles.items() if key in name or name in key]
        if len(matches) == 1:
            profile = matches[0]
        else:
            print(f"Error: Profile '{args.profile}' not found.")
            print(f"Available profiles: {', '.join(p['name'] for p in profiles.values())}")
            sys.exit(1)

    profile_name = profile["name"]
    provider = profile.get("provider", "antigravity")
    model = profile.get("model", "gemini-3.8-flash-high")
    mode = profile.get("modeId", "full-access")
    thinking = profile.get("thinkingOptionId", "high")
    instructions = profile.get("notes", "")

    sender_role = args.from_profile
    sender_room = resolve_room(sender_role)
    target_room = resolve_room(profile_name)

    # 1. Write SLP Handoff Memo to bmad/rooms/<sender_room>/ and task namespace
    bmad_dir = PROJECT_ROOT / "bmad" / "rooms" / sender_room
    bmad_dir.mkdir(parents=True, exist_ok=True)
    ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    item_str = f"#{args.item_id}" if args.item_id else "N/A"

    task_handoff_path = None
    if args.item_id:
        task_dir = PROJECT_ROOT / "bmad" / "rooms" / "tasks" / str(args.item_id)
        task_dir.mkdir(parents=True, exist_ok=True)
        task_handoff_path = task_dir / f"handoff_{sender_room}.md"

    goal_str = args.goal or args.prompt
    constraints_str = args.constraints or "Tuân thủ TDS UI tokens, Angular 18 Standalone, không nạp thêm lib thừa (YAGNI), bảo đảm single-ownership."
    suggested_str = args.suggested_path or "Xem mã nguồn liên quan trong bmad/modules/ và bmad/flows/."

    challenge_header = "BẢN PHẢN BIỆN KỸ THUẬT (EVIDENCE-BACKED CHALLENGE)" if args.challenge else "BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO)"
    evidence_section = ""
    if args.challenge:
        evidence_section = f"\n\n### BẰNG CHỨNG PHẢN BIỆN THỰC NGHIỆM (EVIDENCE DISCIPLINE)\n- **Bằng chứng**: {args.evidence or 'Xem log chi tiết đính kèm'}\n- **Lý do**: Giải pháp gợi ý bị cản trở bởi lỗi thực nghiệm."

    memo_content = f"""# {challenge_header}: {sender_role} ➔ {profile_name}

- **Thời gian**: `{ts_now}`
- **Work Item**: `{item_str}`
- **Agent bàn giao (From)**: `{sender_role}`
- **Agent tiếp nhận (To)**: `{profile_name}`
- **Nội dung tóm tắt**: {args.prompt}

---

## 1. Giao Việc Chuẩn 3 Phần (3-Part Delegation)
1. **Mục tiêu tối hậu (Ultimate Goal)**:
   > {goal_str}

2. **Ràng buộc cứng (Hard Constraints)**:
   > {constraints_str}

3. **Giải pháp gợi ý tạm thời (Suggested Temporary Path)**:
   > {suggested_str}
{evidence_section}

---

## 2. Ranh Giới Quyền Hạn (Single-Ownership Invariant)
> *"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."*
- Nghiêm cấm can thiệp hoặc sửa đè vào module ngoài phạm vi bàn giao.
- Sau khi hoàn thành, bắt buộc xuất biên bản bàn giao tại `bmad/rooms/{target_room}/latest_handoff.md` qua lệnh `python3 tools/agent_progress.py log`.
"""
    try:
        (bmad_dir / "latest_handoff.md").write_text(memo_content, encoding="utf-8")
        (bmad_dir / f"handoff_{args.item_id or 'general'}_{ts_file}.md").write_text(memo_content, encoding="utf-8")
        if task_handoff_path:
            task_handoff_path.write_text(memo_content, encoding="utf-8")
            (task_handoff_path.parent / "latest_handoff.md").write_text(memo_content, encoding="utf-8")
            print(f"[SLP Room] Đã ghi biên bản cô lập theo Task: {task_handoff_path.relative_to(PROJECT_ROOT)}")
        print(f"[SLP Room] Đã ghi biên bản bàn giao: bmad/rooms/{sender_room}/latest_handoff.md")
    except Exception as exc:
        print(f"[Warning] Không thể ghi memo bmad: {exc}", file=sys.stderr)

    primary_memo_file = str(task_handoff_path) if task_handoff_path else f"{PROJECT_ROOT}/bmad/rooms/{sender_room}/latest_handoff.md"
    isolation_note = f"\n🔒 TASK NAMESPACE ISOLATION: You are strictly scoped to Task #{args.item_id}. Read only task files in `{PROJECT_ROOT}/bmad/rooms/tasks/{args.item_id}/` to avoid context collision with other concurrent agents.\n" if args.item_id else ""

    room_block = (
        f"\n\n=== SLPC MULTI-AGENT ROOM HANDOFF (MANDATORY READ FIRST) ===\n"
        f"{isolation_note}"
        f"A formal handoff memo has been registered by `{sender_role}` in:\n"
        f"  - `{primary_memo_file}`\n\n"
        f"You MUST:\n"
        f"1. Read `{primary_memo_file}` for your 3-part delegation (Ultimate Goal, Hard Constraints, Suggested Path).\n"
        f"2. Obey Single-Ownership Invariant: you own only your assigned module/scope. No cross-editing other modules.\n"
        f"3. If the suggested path fails in practice, exercise your Right to Challenge with empirical evidence (`python3 tools/call_agent.py --from-profile \"{profile_name}\" --profile \"{sender_role}\" --challenge --evidence \"...\"`).\n"
        f"4. When finished, record your handoff via `python3 tools/agent_progress.py log --agent \"{profile_name}\" ...` (auto-saves to `bmad/rooms/{target_room}/latest_handoff.md`) and transition the Work Item state on Harness DB.\n"
    )

    pre_gen_block = ""
    # Chống nghẽn: Bỏ qua pre-gen 35s nếu là task thi công cụ thể (đã có item_id hoặc role là Peer/QC)
    should_pre_gen = (not args.skip_pre_gen) and (not args.item_id) and (profile_name.lower() not in ("peer", "qc"))
    if should_pre_gen:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import profile_research_gen as prg
            pipeline_res = prg.execute_pipeline(
                profile=profile_name,
                topic=args.prompt,
                source_file=args.source,
                spec_file=args.spec,
                task_id=args.item_id,
                uc_code=args.uc,
                sync_harness=bool(args.item_id),
            )
            gen_list = "\n".join(f"  - `{PROJECT_ROOT}/{f}`" for f in pipeline_res.get("generated_files", []))
            pre_gen_block = (
                "\n\n=== AUTO-GENERATED RESEARCH & GEN ARTIFACTS (MANDATORY READ FIRST) ===\n"
                f"Pre-pipeline (`tools/profile_research_gen.py`) has already executed Research & Gen for `{profile_name}`:\n"
                f"{gen_list}\n"
                "You MUST read the generated Research Report & Execution Brief above, use `tools/query_reader.py` / "
                "`tools/research/research_agent.py` for any additional lookup, use `tools/qc_test_generator.py` / "
                "`tools/distill_ba_beats.py` / `tools/harness_manager.py` for generation, and log your result via "
                "`python3 tools/agent_progress.py log`."
            )
        except Exception as exc:
            print(f"[Warning] Pre-pipeline Research+Gen notice: {exc}", file=sys.stderr)

    cleaned_prompt, thinking_mode, thinking_directive = resolve_thinking_directive(args.prompt)
    thinking_block = (
        f"\n\n=== MANDATORY THINKING DIRECTIVE (CHẾ ĐỘ TƯ DUY) ===\n"
        f"• Mode: {thinking_mode}\n"
        f"• Yêu cầu: {thinking_directive}\n"
        f"Trong khối Thinking, hãy cấu trúc rõ ràng các trường hợp tư duy theo chỉ thị trên."
    )

    task_body = cleaned_prompt
    if args.item_id:
        task_body = f"[Harness Item #{args.item_id}] {task_body}"

    full_prompt = f"{instructions}{room_block}{pre_gen_block}{thinking_block}\n\n=== TASK ASSIGNMENT ===\n{task_body}" if instructions else f"{room_block}{pre_gen_block}{thinking_block}\n\n{task_body}"
    title = f"{profile_name}: {task_body[:40]}"

    cmd = [
        "paseo", "run", "-d",
        "--title", title,
        "--provider", provider,
        "--model", model,
        "--mode", mode,
    ]
    if provider != "antigravity" and thinking and thinking != "auto":
        cmd.extend(["--thinking", thinking])
    cmd.append(full_prompt)

    if args.dry_run:
        print("Dry run command:", " ".join(cmd[:10]), "...")
        print(f"Thinking Mode: {thinking_mode}")
        if pre_gen_block:
            print(pre_gen_block)
        sys.exit(0)

    # Nếu đang chạy trong Orca IDE (chặn tuyệt đối /usr/bin/orca GNOME Screen Reader trên Linux):
    shim_dir = Path.home() / ".config" / "orca" / "linux-orca-cli-shim"
    if shim_dir.is_dir():
        cur_p = os.environ.get("PATH", "")
        if str(shim_dir) not in cur_p.split(os.pathsep):
            os.environ["PATH"] = f"{shim_dir}{os.pathsep}{cur_p}"
    orca_cand = shutil.which("orca")
    is_valid_orca_ide = bool(
        orca_cand
        and orca_cand not in ("/usr/bin/orca", "/bin/orca", "/usr/games/orca")
        and os.path.realpath(orca_cand) not in ("/usr/bin/orca", "/bin/orca")
    )
    if is_valid_orca_ide:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from orca_slpc_bridge import find_live_terminal_for_role  # type: ignore
            target_term = find_live_terminal_for_role(profile_name) or find_live_terminal_for_role(target_room)
            if target_term:
                print_hook_banner("ORCA DIRECT DISPATCH", profile_name, args.item_id, f"{provider}/{model}", sender_role, task_body, thinking_mode=thinking_mode)
                print(f"🎯 [Orca Direct Dispatch]: Tìm thấy live terminal của {profile_name} ({target_term}). Bắn lệnh trực tiếp...")
                subprocess.run(["orca", "terminal", "send", "--terminal", target_term, "--text", f"{task_body}\n{thinking_block}\n{room_block}", "--enter"], check=True)
                print(f"✅ Đã gửi lệnh trực tiếp tới {profile_name} trên Orca Workspace Board!")
                sys.exit(0)
            else:
                # EPHEMERAL SUB-AGENT AUTO-LAUNCH IN ORCA:
                print_hook_banner("ORCA AGENT LAUNCH", profile_name, args.item_id, f"{provider}/{model}", sender_role, task_body, thinking_mode=thinking_mode)
                print(f"🚀 [Orca Agent Launch]: Chưa có tab cho {profile_name}. Đang mở AI Agent tab mới trên Orca...")
                wt_target = "name:main" if target_room == "supervisor" else (f"name:room-{target_room}" if target_room in ("pm", "lead", "peer", "qc") else "active")
                launch_cmd = [
                    "orca", "agent", "launch",
                    "--worktree", wt_target,
                    "--agent", "hermes",
                    "--prompt", f"[{profile_name}] {task_body}\n{thinking_block}\n{room_block}",
                    "--surface", "terminal",
                    "--focus",
                    "--json"
                ]
                # Hermes uses ~/.hermes/config.yaml directly; Orca rejects launch-time --model for hermes
                lres = subprocess.run(launch_cmd, capture_output=True, text=True, check=False)
                if lres.returncode == 0:
                    handle = ""
                    tab_id = ""
                    if lres.stdout:
                        try:
                            data = json.loads(lres.stdout)
                            outcome = data.get("result", {}).get("outcome", {})
                            handle = outcome.get("handle") or ""
                            pk = outcome.get("paneKey") or ""
                            tab_id = pk.split(":")[0] if ":" in pk else pk
                        except Exception:
                            pass

                    clean_name = profile_name.lower().strip().replace("-", "_").replace(" ", "_")
                    titles_map = {
                        "peer": "[Peer Dev 1] Code Executor",
                        "peer2": "[Peer Dev 2] Code Executor",
                        "peer3": "[Peer Dev 3] Code Executor",
                        "peer4": "[Peer Dev 4] Code Executor",
                        "peer_design": "[Peer Design] UI/UX & Tokens",
                        "design": "[Peer Design] UI/UX & Tokens",
                        "qc": "[QC] 5-Stage ISTQB Verifier",
                        "qc2": "[QC 2] 5-Stage ISTQB Verifier",
                        "qc3": "[QC 3] 5-Stage ISTQB Verifier",
                        "pm": "[PM] Feasibility & Alignment",
                        "lead": "[Lead Dev] Technical Architect",
                        "lead2": "[Lead Dev 2] Technical Architect",
                        "lead3": "[Lead Dev 3] Technical Architect",
                        "supervisor": "[Supervisor] Scope & Intent Guard",
                        "supervisor2": "[Supervisor 2] Nested Scope Guard",
                        "supervisor3": "[Supervisor 3] Nested Scope Guard",
                    }
                    if clean_name in titles_map:
                        role_key = "peer_design" if clean_name == "design" else clean_name
                    else:
                        role_key = "peer" if any(k in clean_name for k in ("peer", "dev", "design")) else ("qc" if "qc" in clean_name else clean_name)
                    term_title = titles_map.get(role_key, f"[{profile_name}] Sub-Agent")

                    if handle:
                        subprocess.run(["orca", "terminal", "rename", "--terminal", handle, "--title", term_title, "--json"], capture_output=True, check=False)
                        subprocess.run(["orca", "terminal", "set-pane-title", "--terminal", handle, "--title", term_title, "--json"], capture_output=True, check=False)

                        reg_file = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
                        reg = {}
                        if reg_file.is_file():
                            try:
                                reg = json.loads(reg_file.read_text(encoding="utf-8"))
                            except Exception:
                                reg = {}
                        reg[role_key] = {"handle": handle, "tabId": tab_id, "room": target_room}
                        reg_file.parent.mkdir(parents=True, exist_ok=True)
                        reg_file.write_text(json.dumps(reg, indent=2), encoding="utf-8")

                        # Chỉ dọn dẹp terminal vượt quá trần capacity của room (không đóng các Peer/Lead/QC đang chạy song song)
                        room_caps = {"supervisor": 3, "pm": 1, "lead": 3, "peer": 5, "qc": 3}
                        cap = room_caps.get(target_room, 1)
                        registered_handles = {
                            v.get("handle") for v in reg.values() if isinstance(v, dict) and v.get("handle")
                        }
                        try:
                            t_out = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, check=False)
                            if t_out.returncode == 0 and t_out.stdout:
                                t_data = json.loads(t_out.stdout).get("result", {}).get("terminals", [])
                                room_terms = [
                                    t_item for t_item in t_data
                                    if t_item.get("worktreePath", "").rstrip("/").endswith(f"/room-{target_room}")
                                ]
                                if len(room_terms) > cap:
                                    for t_item in room_terms[cap:]:
                                        t_h = t_item.get("handle")
                                        if t_h and t_h != handle and t_h not in registered_handles:
                                            subprocess.run(["orca", "terminal", "close", "--terminal", t_h, "--tab", "--json"], capture_output=True, check=False)
                        except Exception:
                            pass

                    print(f"✅ Đã spawn và đổi tên thành công AI Agent tab '{term_title}' ({handle}) trên Orca Workspace!")
                    sys.exit(0)
                else:
                    print(f"⚠️ [Orca Agent Launch Warning]: {lres.stderr.strip()}", file=sys.stderr)
        except Exception as e:
            print(f"[Notice] Orca dispatch fallback: {e}", file=sys.stderr)

    print_hook_banner("SPAWNING EPHEMERAL SUB-AGENT", profile_name, args.item_id, f"{provider}/{model}", sender_role, task_body)
    print(f"Calling {profile_name} ({provider}/{model})...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print_hook_banner("SUB-AGENT EXECUTION STARTED", profile_name, args.item_id, f"{provider}/{model}", sender_role, "Process launched in background")
        print(f"Success: {profile_name} spawned.")
        if res.stdout.strip():
            print(res.stdout.strip())
    else:
        print(f"Failed to spawn {profile_name}: {res.stderr.strip()}", file=sys.stderr)
        sys.exit(res.returncode)

if __name__ == "__main__":
    main()

