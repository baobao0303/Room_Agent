#!/usr/bin/env python3
"""
tools/tests/test_g_hrn_adversarial.py - Empirical Adversarial Stress Test Suite for G-HRN-1 & G-HRN-2

Tests authority fences and role permissions in tools/harness_manager.py:
1. Missing, whitespace, mixed-case, and unauthorized profile strings.
2. Macro (Epic/Feature/Story) vs Micro (Task) closure permissions per role.
3. Supervisor vs Lead vs Peer vs QC closure authority.
4. Fail-closed behavior on missing or unmapped profiles.
5. SQLite vs Floci engine parity.
6. Edge case formatting in wi_type and target_state.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ORIG_DRY_RUN = None


def setUpModule():
    global _ORIG_DRY_RUN
    _ORIG_DRY_RUN = os.environ.get("SLPPC_DRY_RUN")
    os.environ["SLPPC_DRY_RUN"] = "1"


def tearDownModule():
    global _ORIG_DRY_RUN
    if _ORIG_DRY_RUN is None:
        os.environ.pop("SLPPC_DRY_RUN", None)
    else:
        os.environ["SLPPC_DRY_RUN"] = _ORIG_DRY_RUN


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools.harness_manager import (
    HarnessManager,
    normalize_role,
    get_role_permissions,
    parse_profile_permissions,
)


class TestAdversarialRoleNormalizer(unittest.TestCase):
    """Stress-test normalize_role with adversarial, malformed, and fuzz inputs."""

    def test_canonical_roles(self):
        for role in ["supervisor", "lead", "peer", "qc"]:
            self.assertEqual(normalize_role(role), role)

    def test_whitespace_and_casing(self):
        cases = [
            ("  lead  ", "lead"),
            ("LEAD", "lead"),
            ("  LEAD DEV  ", "lead"),
            ("Lead Architect", "lead"),
            ("  qc  ", "qc"),
            ("QC", "qc"),
            ("Qc Tester", "qc"),
            ("QA", "qc"),
            ("  peer  ", "peer"),
            ("PEER", "peer"),
            ("Peer Dev", "peer"),
            ("Peer Design", "peer"),
            ("Lead BA", "lead"),
            ("Peer BA", "peer"),
            ("SUPERVISOR", "supervisor"),
            ("  Supervisor  ", "supervisor"),
        ]
        for inp, expected in cases:
            with self.subTest(inp=inp):
                self.assertEqual(normalize_role(inp), expected)

    def test_empty_and_none(self):
        self.assertEqual(normalize_role(None), "")
        self.assertEqual(normalize_role(""), "")
        self.assertEqual(normalize_role("   "), "")
        self.assertEqual(normalize_role("\t\n"), "")

    def test_unrecognized_roles(self):
        unknowns = ["random_agent", "hacker", "nobody", "root", "admin", "12345"]
        for u in unknowns:
            with self.subTest(u=u):
                self.assertEqual(normalize_role(u), u)
                perms = get_role_permissions(u)
                self.assertFalse(perms.get("can_close_task", False))


class TestProfilePermissionsIntegrity(unittest.TestCase):
    """Verify ground truth permissions declared in profiles/*/PROFILE.md."""

    def test_qc_profile_has_can_close_task(self):
        perms = get_role_permissions("qc")
        self.assertTrue(perms.get("can_close_task", False), "QC must have can_close_task: true")

    def test_lead_profile_forbidden_close_task(self):
        perms = get_role_permissions("lead")
        self.assertFalse(perms.get("can_close_task", False), "Lead must have can_close_task: false")

    def test_peer_profile_forbidden_close_task(self):
        perms = get_role_permissions("peer")
        self.assertFalse(perms.get("can_close_task", False), "Peer must have can_close_task: false")

    def test_supervisor_profile_forbidden_close_task(self):
        perms = get_role_permissions("supervisor")
        self.assertFalse(perms.get("can_close_task", False), "Supervisor must have can_close_task: false")

    def test_empty_or_unknown_role_permissions_fail_closed(self):
        self.assertEqual(get_role_permissions(""), {})
        self.assertEqual(get_role_permissions(None), {})
        self.assertEqual(get_role_permissions("unknown_xyz"), {})


class BaseAdversarialHarnessTest(unittest.TestCase):
    """Base class for testing HarnessManager engines under adversarial state transitions."""

    engine_name = "sqlite"

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.mgr = HarnessManager(engine=self.engine_name, db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except Exception:
                pass

    def test_task_closure_adversarial_profiles(self):
        """Stress-test closing a Task with unauthorized, malformed, or missing profiles."""
        item = self.mgr.add_work_item(
            wi_type="Task",
            title="[Adv] - Task for Closure Testing",
            assigned_to="peer",
            assigned_to_profile="peer"
        )
        tid = item["id"]
        self.mgr.update_state(tid, "Active", assigned_to_profile="peer")
        self.mgr.update_state(tid, "Resolved", assigned_to_profile="peer")

        unauthorized_profiles = [
            "lead",
            "Lead Dev",
            "LEAD",
            "  lead  ",
            "supervisor",
            "SUPERVISOR",
            "peer",
            "Peer Dev",
            "PEER",
            "  peer  ",
            "random_agent",
            "hacker",
            "",
            "   ",
            None,
        ]

        for prof in unauthorized_profiles:
            with self.subTest(profile=prof):
                with self.assertRaises(PermissionError, msg=f"Profile '{prof}' must NOT be allowed to close Task #{tid}"):
                    self.mgr.update_state(tid, "Closed", assigned_to_profile=prof)

        # Authorized closure: QC with various casings / padding
        for qc_variant in ["qc", "QC", "  qc  ", "Qc Tester"]:
            with self.subTest(qc_variant=qc_variant):
                # Reset task to Resolved first
                self.mgr.update_state(tid, "Resolved", assigned_to_profile="peer")
                res = self.mgr.update_state(tid, "Closed", assigned_to_profile=qc_variant)
                self.assertTrue(res["success"])
                self.assertEqual(res["new_state"], "Closed")

    def test_macro_artifacts_closure_by_peer_blocked(self):
        """Verify peer (DEV ONLY) is strictly barred from closing Epic, Feature, User Story."""
        macro_types = [
            ("Epic", "[Adv] - Core Architecture Epic"),
            ("Feature", "[Adv] - Subsystem Feature Module"),
            ("User Story", "[Adv] - User story có thể export reports"),
        ]

        for wi_type, title in macro_types:
            with self.subTest(wi_type=wi_type):
                item = self.mgr.add_work_item(
                    wi_type=wi_type,
                    title=title,
                    assigned_to="lead" if wi_type != "User Story" else "peer",
                    assigned_to_profile="lead" if wi_type != "User Story" else "peer",
                    created_by_profile="supervisor"
                )
                mid = item["id"]

                # Peer attempting to close -> MUST FAIL
                for peer_role in ["peer", "Peer Dev", "PEER", "  peer  ", "peer design"]:
                    with self.assertRaises(PermissionError, msg=f"Peer '{peer_role}' must not close {wi_type}"):
                        self.mgr.update_state(mid, "Closed", assigned_to_profile=peer_role)

                # Supervisor closing -> MUST SUCCEED
                res_sup = self.mgr.update_state(mid, "Closed", assigned_to_profile="supervisor")
                self.assertTrue(res_sup["success"])
                self.assertEqual(res_sup["new_state"], "Closed")

    def test_lead_closing_macro_vs_task(self):
        """Lead can close Epic/Feature/Story, but CANNOT close Task (G-HRN-2)."""
        # 1. Lead closing Epic -> Allowed
        epic = self.mgr.add_work_item(
            wi_type="Epic",
            title="[Adv] - Lead Architecture Epic",
            assigned_to="lead",
            assigned_to_profile="lead",
            created_by_profile="supervisor"
        )
        res_epic = self.mgr.update_state(epic["id"], "Closed", assigned_to_profile="lead")
        self.assertTrue(res_epic["success"])

        # 2. Lead closing Task -> MUST BE REJECTED
        task = self.mgr.add_work_item(
            wi_type="Task",
            title="[Adv] - Lead Task Closure Attempt",
            assigned_to="peer",
            assigned_to_profile="peer"
        )
        with self.assertRaises(PermissionError):
            self.mgr.update_state(task["id"], "Closed", assigned_to_profile="lead")

    def test_supervisor_closing_macro_vs_task(self):
        """Supervisor can close Epic/Feature, but CANNOT close Task (can_close_task: false)."""
        # 1. Supervisor closing Epic -> Allowed
        epic = self.mgr.add_work_item(
            wi_type="Epic",
            title="[Adv] - Supervisor Scope Epic",
            assigned_to="supervisor",
            assigned_to_profile="supervisor",
            created_by_profile="supervisor"
        )
        res_epic = self.mgr.update_state(epic["id"], "Closed", assigned_to_profile="supervisor")
        self.assertTrue(res_epic["success"])

        # 2. Supervisor closing Task -> MUST BE REJECTED (can_close_task: false in Supervisor PROFILE.md)
        task = self.mgr.add_work_item(
            wi_type="Task",
            title="[Adv] - Supervisor Task Closure Attempt",
            assigned_to="peer",
            assigned_to_profile="peer"
        )
        with self.assertRaises(PermissionError):
            self.mgr.update_state(task["id"], "Closed", assigned_to_profile="supervisor")

    def test_unassigned_work_item_closure_fails_closed(self):
        """If work item has no assignee and caller provides none, closing Task must fail closed."""
        item = self.mgr.add_work_item(
            wi_type="Task",
            title="[Adv] - Unassigned Task Check",
            assigned_to=None,
            assigned_to_profile=None
        )
        tid = item["id"]

        # Attempt to close without profile -> Must raise PermissionError
        with self.assertRaises(PermissionError):
            self.mgr.update_state(tid, "Closed", assigned_to_profile=None)

    def test_invalid_target_states(self):
        """Verify invalid or arbitrary states are rejected by state machine."""
        item = self.mgr.add_work_item(
            wi_type="Task",
            title="[Adv] - Invalid State Transition Check",
            assigned_to="peer",
            assigned_to_profile="peer"
        )
        tid = item["id"]

        invalid_states = ["Destroyed", "Finished", "Done", "RandomState", "12345"]
        for bad_state in invalid_states:
            with self.subTest(bad_state=bad_state):
                with self.assertRaises(ValueError):
                    self.mgr.update_state(tid, bad_state, assigned_to_profile="qc")


class TestAdversarialHarnessSQLite(BaseAdversarialHarnessTest):
    engine_name = "sqlite"


class TestAdversarialHarnessAuto(BaseAdversarialHarnessTest):
    engine_name = "auto"


if __name__ == "__main__":
    unittest.main(verbosity=2)
