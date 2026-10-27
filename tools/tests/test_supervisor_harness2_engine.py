#!/usr/bin/env python3
"""
Unit tests for tools/supervisor_harness2_engine.py:
- 3-Tier Memory (Working, Short-Term Session Buffer, Long-Term SQL/Vector + Harness² Library)
- Kev Uncertainty & Level Check (<50ms API with deterministic heuristic fallback)
- Stage-by-Stage Evals Gate (Golden Dataset + LLM-as-a-Judge + Guardrails, Pass >= 98.5%)
- Harness² Recursive Re-learning (INV + DOM + COMPOSE, Ledger R=4k, P=3k)
- Autonomous Skill Self-Authoring
"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from tools.supervisor_harness2_engine import (
    HARNESS2_LIBRARY_DIR,
    PRODUCTION_PASS_THRESHOLD,
    SESSION_BUFFER_FILE,
    SUPERVISOR_DIR,
    assess_supervisor_readiness,
    check_uncertainty_with_kev,
    evaluate_stage,
    relearn_with_harness2,
    self_author_skill,
)


class TestSupervisorHarness2Engine(unittest.TestCase):
    def test_kev_uncertainty_detects_hesitation_and_confidence(self) -> None:
        hesitant = check_uncertainty_with_kev(
            stage="intake",
            context_text="Tôi đang phân vân không chắc nên chọn kiến trúc nào? Maybe TBD?",
            use_kev_daemon=False,
        )
        self.assertTrue(hesitant.is_hesitant)
        self.assertLess(hesitant.confidence, 0.80)
        self.assertIn(hesitant.risk_lane, ("yellow", "red"))

        confident = check_uncertainty_with_kev(
            stage="intake",
            context_text=(
                "Target Files: tools/evos_engine.py. Acceptance Criteria: tdsTestId, "
                "Test Command: pytest, Strict Typing, Exit Code 0, Harness, Kev, Evals 98.5%, Guardrails, Memory."
            ),
            use_kev_daemon=False,
        )
        self.assertFalse(confident.is_hesitant)
        self.assertGreaterEqual(confident.confidence, 0.92)
        self.assertEqual(confident.risk_lane, "green")

    def test_eval_stage_blocks_incomplete_or_unsafe_and_relearns_via_harness2(self) -> None:
        incomplete_spec = "Thiết kế sơ bộ tính năng mới, vẫn còn phân vân chưa rõ cách test."
        eval_before = evaluate_stage(stage="intake", artifact_text=incomplete_spec)
        self.assertFalse(eval_before.passed)
        self.assertLess(eval_before.overall_pass_rate, PRODUCTION_PASS_THRESHOLD)

        healed_text, report = relearn_with_harness2(
            stage="intake",
            failed_artifact=incomplete_spec,
            task_id="test-relearn-intake-01",
            k=1,
        )
        self.assertTrue(report.ledger_identity_ok)
        self.assertEqual(report.rollouts_r, 4)
        self.assertEqual(report.sessions_p, 3)
        self.assertGreaterEqual(report.after_pass_rate, PRODUCTION_PASS_THRESHOLD)
        self.assertTrue(report.passed_graduation)
        self.assertIn("HARNESS² SELF-HEALED SPECIFICATION", healed_text)
        self.assertTrue(SESSION_BUFFER_FILE.exists())
        self.assertTrue((HARNESS2_LIBRARY_DIR / "supervisor_intake" / "INDEX.md").exists())

    def test_self_author_skill_creates_valid_skill_and_passes_evals(self) -> None:
        temp_skill = "auto-cost-telemetry-guard"
        pillar = "governance-and-retro"
        skill_dir = SUPERVISOR_DIR / "skills" / pillar / temp_skill
        mem_file = SUPERVISOR_DIR / "MEMORY.md"
        original_memory = mem_file.read_text(encoding="utf-8") if mem_file.exists() else ""

        try:
            res = self_author_skill(
                skill_name=temp_skill,
                pillar=pillar,
                intent_description="Giám sát ngân sách token và tự động tối ưu hóa chi phí thực thi đa Agent.",
                trigger_keywords=["cost-telemetry", "token-budget-guard"],
            )
            self.assertEqual(res["skill_name"], temp_skill)
            self.assertTrue(Path(str(res["skill_path"])).exists())
            eval_dict = res["eval_result"]
            self.assertIsInstance(eval_dict, dict)
            if isinstance(eval_dict, dict):
                self.assertTrue(eval_dict.get("passed"))
                self.assertGreaterEqual(float(eval_dict.get("overall_pass_rate", 0.0)), PRODUCTION_PASS_THRESHOLD)
        finally:
            if skill_dir.exists():
                shutil.rmtree(skill_dir, ignore_errors=True)
            if original_memory and mem_file.exists():
                mem_file.write_text(original_memory, encoding="utf-8")

    def test_supervisor_readiness_status(self) -> None:
        info = assess_supervisor_readiness()
        self.assertTrue(info["harness2_engine_installed"])
        self.assertGreaterEqual(int(str(info["total_skills"])), 23)
        self.assertEqual(info["evals_graduation_threshold"], "98.5%")


if __name__ == "__main__":
    unittest.main()
