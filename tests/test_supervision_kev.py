import os
import sys
import json
import tempfile
import unittest
import subprocess
from pathlib import Path

class TestSupervisionKevIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Locate project root and cargo binary
        cls.repo_root = Path(__file__).resolve().parent.parent / "projects" / "harness"
        if not cls.repo_root.is_dir():
            cls.repo_root = Path("/home/baoltb/Desktop/Room_Agent/projects/harness")
        
        # Build binary
        subprocess.run(
            ["cargo", "build", "-p", "harness-cli", "--bin", "harness-cli"],
            cwd=str(cls.repo_root),
            check=True,
            capture_output=True,
            text=True
        )
        cls.cli_bin = cls.repo_root / "target" / "debug" / "harness-cli"

    def run_cli(self, args, env_extra=None):
        env = os.environ.copy()
        if env_extra:
            env.update(env_extra)
        res = subprocess.run(
            [str(self.cli_bin)] + args,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            env=env
        )
        return res

    def test_supervise_evaluate_green_fast_path(self):
        """Simulate low risk task: doc/UI typo -> Green -> automated_worker"""
        res = self.run_cli(["supervise", "evaluate", "--text", "Update button label on dashboard", "--json"])
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["decision"], "green")
        self.assertEqual(data["risk_lane"], "tiny")
        self.assertFalse(data["requires_human_review"])
        self.assertEqual(data["suggested_route"], "automated_worker")

    def test_supervise_evaluate_yellow_peer_review(self):
        """Simulate moderate risk task: feature logic/refactor -> Yellow -> peer_review_queue"""
        res = self.run_cli(["supervise", "evaluate", "--text", "Refactor payment calculation API", "--json"])
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["decision"], "yellow")
        self.assertEqual(data["risk_lane"], "normal")
        self.assertFalse(data["requires_human_review"])
        self.assertEqual(data["suggested_route"], "peer_review_queue")

    def test_supervise_evaluate_red_human_approval(self):
        """Simulate high risk task: auth/db migration/secret -> Red -> human_supervisor_approval"""
        res = self.run_cli(["supervise", "evaluate", "--text", "Drop table users and migrate JWT auth permissions", "--json"])
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["decision"], "red")
        self.assertEqual(data["risk_lane"], "high_risk")
        self.assertTrue(data["requires_human_review"])
        self.assertEqual(data["suggested_route"], "human_supervisor_approval")

    def test_supervise_route_subcommand(self):
        """Test supervise route subcommand output"""
        res = self.run_cli(["supervise", "route", "--text", "Minor fix in readme", "--json"])
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data["route"], "automated_worker")

        res_red = self.run_cli(["supervise", "route", "--text", "Alter schema for auth credentials", "--json"])
        self.assertEqual(res_red.returncode, 0, f"CLI error: {res_red.stderr}")
        data_red = json.loads(res_red.stdout)
        self.assertEqual(data_red["route"], "human_supervisor_approval")

if __name__ == "__main__":
    unittest.main()
