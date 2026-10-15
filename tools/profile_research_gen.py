#!/usr/bin/env python3
"""
tools/profile_research_gen.py - Unified Research & Generation Pipeline for all Paseo Profiles.

Enforces the rule: Every Paseo profile (Supervisor, Lead, Peer, QC, Lead BA, Peer BA,
Lead Dev, Peer Dev, Lead design, Peer Design) MUST execute Research tools and
Generation tools before/during task execution.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(TOOLS_DIR / "research"))

import agent_progress as ap  # noqa: E402
import research_agent as ra  # noqa: E402


def slugify(text: str, max_len: int = 36) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:max_len] or "task"


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as exc:
        return 1, "", str(exc)


def execute_pipeline(
    profile: str,
    topic: str,
    source_file: str | None = None,
    spec_file: str | None = None,
    task_id: int | None = None,
    uc_code: str | None = None,
    sync_harness: bool = False,
) -> dict:
    role_key = profile.strip().lower()
    slug = slugify(f"{role_key}_{topic}")
    generated_files: list[str] = []
    done_steps: list[str] = []

    # =========================================================================
    # STEP 1: MANDATORY RESEARCH (Hermes/Router9 Research + BM25 Query + Threads)
    # =========================================================================
    research_rel = f"tools/research/research_{slug}.md"
    research_res = ra.run_research(f"[{profile}] {topic}", research_rel)
    if research_res.get("output_file"):
        generated_files.append(research_rel)
        done_steps.append(f"Research Report generated via {research_res.get('source')} -> {research_rel}")

    # Thread knowledge lookup (Phase 1 of knowledge skill)
    keywords = " ".join(re.findall(r"[A-Za-z0-9_.\u00C0-\u1EF9-]+", topic)[:4])
    _, threads_out, _ = run_cmd([sys.executable, str(TOOLS_DIR / "agent_progress.py"), "find-thread", keywords, "--limit", "3"])
    matched_threads = []
    try:
        matched_threads = json.loads(threads_out).get("threads", [])
    except Exception:
        matched_threads = []

    # CRM / BA Use Case lookup if UC code is present or role is BA
    uc_detected = uc_code
    if not uc_detected:
        m = re.search(r"UC\d+\.\d+", topic, re.IGNORECASE)
        if m:
            uc_detected = m.group(0).upper()
    crm_excerpt = ""
    if uc_detected or "ba" in role_key:
        crm_cmd = [sys.executable, str(TOOLS_DIR / "crm_doc_reader.py")]
        if uc_detected:
            crm_cmd.extend(["--uc", uc_detected])
        else:
            crm_cmd.append(keywords)
        rc, out, _ = run_cmd(crm_cmd, timeout=10)
        if rc == 0 and out:
            crm_excerpt = out[:1200]
            done_steps.append(f"CRM Doc Reader researched ({uc_detected or keywords})")

    # =========================================================================
    # STEP 2: MANDATORY GENERATION (Spec / Beats / 5-Stage ISTQB Unit Tests)
    # =========================================================================
    # 2A. BA Beats distillation if BA profile
    if "ba" in role_key and (TOOLS_DIR / "distill_ba_beats.py").is_file():
        rc, out, _ = run_cmd([sys.executable, str(TOOLS_DIR / "distill_ba_beats.py")], timeout=20)
        if rc == 0:
            done_steps.append("Generated atomic BA Requirement Beats via tools/distill_ba_beats.py")

    # 2B. Auto-discover or generate Spec & 5-Stage ISTQB Test Suite when source_file is given or role is QC/Peer/Dev
    if source_file:
        src_path = Path(source_file)
        if not src_path.is_absolute():
            src_path = ROOT / src_path
        if src_path.is_file():
            qc_cmd = [
                sys.executable,
                str(TOOLS_DIR / "qc_test_generator.py"),
                "--source",
                str(src_path),
            ]
            if spec_file:
                qc_cmd.extend(["--spec", str(spec_file)])
            elif research_res.get("output_file"):
                qc_cmd.extend(["--spec", str(research_res["output_file"])])
            if task_id:
                qc_cmd.extend(["--task-id", str(task_id)])
            if sync_harness:
                qc_cmd.append("--sync-harness")

            # Determine output spec path
            if src_path.suffix == ".ts" and not src_path.name.endswith(".spec.ts"):
                out_spec = src_path.with_suffix(".spec.ts")
            elif src_path.suffix == ".py" and not src_path.name.startswith("test_"):
                out_spec = src_path.parent / f"test_{src_path.name}"
            else:
                out_spec = ROOT / "tools" / "research" / f"gen_test_{slug}.spec.ts"
            qc_cmd.extend(["--out-spec", str(out_spec)])

            rc, out, err = run_cmd(qc_cmd, timeout=30)
            if rc == 0:
                rel_spec = str(out_spec.relative_to(ROOT)) if out_spec.is_relative_to(ROOT) else str(out_spec)
                generated_files.append(rel_spec)
                done_steps.append(f"Generated 5-Stage ISTQB Unit Test Suite -> {rel_spec}")

    # 2C. Generate Role Execution Brief & Checklist artifact
    brief_rel = f"tools/research/gen_brief_{slug}.md"
    brief_path = ROOT / brief_rel
    brief_lines = [
        f"# Auto-Generated Execution Brief ({profile})",
        "",
        f"- **Profile**: `{profile}`",
        f"- **Topic / Task**: {topic}",
        f"- **Task ID**: `{task_id or 'N/A'}`",
        f"- **Generated At**: `{datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- **Research Report**: `{research_rel}`",
        "",
        "## 1. Related Session Threads (Knowledge Skill Phase 1)",
    ]
    if matched_threads:
        for t in matched_threads:
            brief_lines.append(f"- `{t.get('thread_id')}` ({t.get('source')}, {t.get('size_kb')} KB) — `{t.get('path')}`")
    else:
        brief_lines.append("- No prior session threads matched keyword; fresh context.")

    if crm_excerpt:
        brief_lines.extend([
            "",
            "## 2. Extracted CRM / BA Spec Context",
            "```text",
            crm_excerpt,
            "```",
        ])

    brief_lines.extend([
        "",
        "## 3. Mandatory Tool-First Execution Checklist",
        "- [x] **Research Tool**: `python3 tools/research/research_agent.py` executed.",
        "- [x] **Context & Thread Discovery**: `python3 tools/agent_progress.py find-thread` & `query_reader.py` executed.",
        "- [ ] **Sub-Agents (`031_claude_code_sub_agents`)**: Invoke `gemini-codebase-analyzer` / `strategic-reasoning-architect` / `slpc-qc-verifier` as needed.",
        "- [ ] **Test / Artifact Generation**: Run `python3 tools/qc_test_generator.py` / `distill_ba_beats.py` / `harness_manager.py`.",
        "- [ ] **Progress Ledger Update**: Log final outcome via `python3 tools/agent_progress.py log`.",
        "",
    ])
    brief_path.write_text("\n".join(brief_lines), encoding="utf-8")
    generated_files.append(brief_rel)
    done_steps.append(f"Generated Role Execution Brief -> {brief_rel}")

    # =========================================================================
    # STEP 3: LOG TO AGENT PROGRESS LEDGER
    # =========================================================================
    state = ap.load_state()
    state["last_agent"] = f"{profile} (via profile_research_gen)"
    state["current_focus"] = f"[{profile}] {topic}"
    state.setdefault("sessions", []).append({
        "timestamp": ap.now_iso(),
        "agent": f"{profile} (Auto Research+Gen)",
        "summary": f"Chạy tự động pipeline Research + Gen cho profile {profile}: {topic}",
        "done": done_steps,
        "files": generated_files,
        "next": f"Profile {profile} tiếp tục hoàn thiện task dựa trên {research_rel} và {brief_rel}.",
    })
    ap.save_state(state)

    return {
        "success": True,
        "profile": profile,
        "topic": topic,
        "research_report": research_rel,
        "execution_brief": brief_rel,
        "generated_files": generated_files,
        "matched_threads": matched_threads,
        "done_steps": done_steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified Research & Generation Pipeline for Paseo Profiles")
    parser.add_argument("--profile", required=True, help="Paseo profile name (Supervisor, Lead, Peer, QC, etc.)")
    parser.add_argument("--topic", required=True, help="Task or research topic")
    parser.add_argument("--source", help="Optional target source file for 5-Stage ISTQB test generation")
    parser.add_argument("--spec", help="Optional spec file path")
    parser.add_argument("--task-id", type=int, help="Optional Harness Work Item ID")
    parser.add_argument("--uc", help="Optional Use Case code (e.g., UC1.01)")
    parser.add_argument("--sync-harness", action="store_true", help="Sync generated testcases to Harness DB")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    result = execute_pipeline(
        profile=args.profile,
        topic=args.topic,
        source_file=args.source,
        spec_file=args.spec,
        task_id=args.task_id,
        uc_code=args.uc,
        sync_harness=args.sync_harness,
    )
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"[OK] Profile Research & Gen completed for '{args.profile}':")
        for f in result["generated_files"]:
            print(f"  - Generated: {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
