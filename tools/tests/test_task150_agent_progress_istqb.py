#!/usr/bin/env python3
"""
tools/tests/test_task150_agent_progress_istqb.py - 5-Stage ISTQB Audit Suite for Task #150:
[Task 1]: Chuẩn hóa agent_progress.py - Single-Pointer In-Place & Room Ledger FIFO 50

Stages checked:
- Stage 1: Acceptance Criteria Verification (AC-1 to AC-4)
- Stage 2: Boundary Value Analysis (BVA) & FIFO 50 Rolling Policy on room_ledger.json
- Stage 3: Equivalence Partitioning & Decision Table for Agent Roles (Supervisor, PM, Lead, Peer, QC)
- Stage 4: Single-Pointer In-Place Invariant & Line Limit (<=150 lines)
- Stage 5: Zero-Leak Invariant & SLPPC Flow Guard Compliance
"""

import sys
import json
import unittest
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools.agent_progress import cmd_log, default_state
from tools.harness_manager import HarnessManager
import argparse


class TestTask150AgentProgressISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Task #150."""

    def setUp(self):
        self.bmad_rooms = BASE_DIR / "bmad" / "rooms"
        self.ledger_path = self.bmad_rooms / "room_ledger.json"
        self.mgr = HarnessManager(engine="auto")

    # =========================================================================
    # STAGE 1: ACCEPTANCE CRITERIA VERIFICATION (AC-1 .. AC-4)
    # =========================================================================

    def test_stage1_ac1_zero_new_timestamped_handoff_files(self):
        """[AC-1] Verify logging does not produce any handoff_*.md files."""
        # Find all timestamped handoff files before
        handoff_files = list(self.bmad_rooms.glob("**/handoff_*.md"))
        self.assertEqual(len(handoff_files), 0, f"Found legacy handoff files: {handoff_files}")

        # Execute log command
        args = argparse.Namespace(
            agent="Peer",
            summary="ISTQB Stage 1 Verification",
            focus=None,
            done="AC-1 test run",
            missing=None,
            replace_missing=False,
            resolve_missing=None,
            next="Next verify step",
            files=None,
        )
        cmd_log(args, default_state())

        # Check again
        handoff_files_after = list(self.bmad_rooms.glob("**/handoff_*.md"))
        self.assertEqual(len(handoff_files_after), 0, "cmd_log created prohibited handoff_*.md file!")

    def test_stage1_ac2_latest_handoff_updated_inplace(self):
        """[AC-2] Verify latest_handoff.md is updated in-place."""
        peer_latest = self.bmad_rooms / "peer" / "latest_handoff.md"
        self.assertTrue(peer_latest.is_file(), "latest_handoff.md must exist in bmad/rooms/peer/")
        content = peer_latest.read_text(encoding="utf-8")
        self.assertIn("ISTQB Stage 1 Verification", content)

    def test_stage1_ac3_room_ledger_schema_and_size(self):
        """[AC-3] Verify room_ledger.json exists, adheres to schema and is < 50 KB."""
        self.assertTrue(self.ledger_path.is_file(), "room_ledger.json must exist")
        raw = self.ledger_path.read_text(encoding="utf-8")
        self.assertLess(len(raw.encode("utf-8")), 50 * 1024, "room_ledger.json exceeded 50KB ceiling")

        data = json.loads(raw)
        self.assertEqual(data.get("version"), "1.0.0")
        self.assertIn("roles", data)
        self.assertIn("history", data)
        self.assertLessEqual(len(data["history"]), 50)

    def test_stage1_ac4_zero_personal_absolute_paths(self):
        """[AC-4] Verify agent_progress.py contains zero personal machine absolute paths and sanitizes them."""
        source = (BASE_DIR / "tools" / "agent_progress.py").read_text(encoding="utf-8")
        self.assertNotIn("/home/baoltb", source)
        self.assertNotIn("/Users/bao312", source)

        args = argparse.Namespace(
            agent="Peer",
            summary="Refactored /Users/bao312/Desktop/Room_Agent/tools/agent_progress.py and /home/user/test.py",
            focus=None,
            done="Updated /Users/bao312/Desktop/Room_Agent/tools/agent_progress.py",
            missing=None,
            replace_missing=False,
            resolve_missing=None,
            next="Deploy /home/baoltb/app",
            files="/Users/bao312/Desktop/Room_Agent/tools/agent_progress.py,/home/user/other.py",
        )
        cmd_log(args, default_state())
        peer_latest = (self.bmad_rooms / "peer" / "latest_handoff.md").read_text(encoding="utf-8")
        self.assertNotIn("/Users/bao312", peer_latest)
        self.assertNotIn("/home/user", peer_latest)
        self.assertNotIn("/home/baoltb", peer_latest)

        ledger_content = self.ledger_path.read_text(encoding="utf-8")
        self.assertNotIn("/Users/bao312", ledger_content)
        self.assertNotIn("/home/user", ledger_content)
        self.assertNotIn("/home/baoltb", ledger_content)

    # =========================================================================
    # STAGE 2: BOUNDARY VALUE ANALYSIS (BVA) ON FIFO 50 POLICY
    # =========================================================================

    def test_stage2_fifo_50_limit_clamping(self):
        """[Stage 2 - BVA] Verify history array strictly caps at 50 records via FIFO."""
        for i in range(55):
            args = argparse.Namespace(
                agent="Peer",
                summary=f"FIFO test iteration {i}",
                focus=None,
                done=None,
                missing=None,
                replace_missing=False,
                resolve_missing=None,
                next=None,
                files=None,
            )
            cmd_log(args, default_state())

        data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(len(data["history"]), 50, "History did not clamp to exactly 50 entries")
        # Verify oldest was dropped (FIFO)
        summaries = [h["summary"] for h in data["history"]]
        self.assertNotIn("FIFO test iteration 0", summaries)
        self.assertIn("FIFO test iteration 54", summaries)

    # =========================================================================
    # STAGE 3: EQUIVALENCE PARTITIONING ON ROLE DISPATCH
    # =========================================================================

    def test_stage3_role_dispatch_all_five_roles(self):
        """[Stage 3 - EP] Verify all 5 SLPPC roles (Supervisor, PM, Lead, Peer, QC) update their latest_handoff.md."""
        roles_to_test = [
            ("Supervisor", "supervisor"),
            ("PM Agent", "pm"),
            ("Lead Architect", "lead"),
            ("Peer Dev", "peer"),
            ("QC Verifier", "qc"),
        ]

        for agent_name, folder_name in roles_to_test:
            args = argparse.Namespace(
                agent=agent_name,
                summary=f"Role test for {agent_name}",
                focus=None,
                done=f"{agent_name} done",
                missing=None,
                replace_missing=False,
                resolve_missing=None,
                next="Next",
                files=None,
            )
            cmd_log(args, default_state())
            role_file = self.bmad_rooms / folder_name / "latest_handoff.md"
            self.assertTrue(role_file.is_file(), f"latest_handoff.md missing for role {folder_name}")
            content = role_file.read_text(encoding="utf-8")
            self.assertIn(f"Role test for {agent_name}", content)

    # =========================================================================
    # STAGE 4: LINE CEILING & SINGLE-POINTER INVARIANT
    # =========================================================================

    def test_stage4_latest_handoff_line_ceiling(self):
        """[Stage 4] Verify latest_handoff.md files do not exceed 150 lines."""
        for folder in ["supervisor", "pm", "lead", "peer", "qc"]:
            f = self.bmad_rooms / folder / "latest_handoff.md"
            if f.is_file():
                lines = f.read_text(encoding="utf-8").splitlines()
                self.assertLessEqual(len(lines), 150, f"{f} exceeded 150 lines ceiling ({len(lines)} lines)")

    # =========================================================================
    # STAGE 5: SECURITY SENTINEL & GOVERNANCE COMPLIANCE
    # =========================================================================

    def test_stage5_governance_and_anti_leak_pass(self):
        """[Stage 5] Verify anti-leak sentinel and slppc flow guard pass 100%."""
        sentinel = subprocess.run(
            [sys.executable, "scripts/anti_leak_sentinel.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(sentinel.returncode, 0, f"Sentinel failed:\n{sentinel.stdout}\n{sentinel.stderr}")

        guard = subprocess.run(
            [sys.executable, "tools/slppc_flow_guard.py", "audit"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(guard.returncode, 0, f"Flow guard failed:\n{guard.stdout}\n{guard.stderr}")


if __name__ == "__main__":
    unittest.main()
