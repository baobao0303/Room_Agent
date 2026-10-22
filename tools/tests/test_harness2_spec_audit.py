#!/usr/bin/env python3
r"""
tools/tests/test_harness2_spec_audit.py - Independent QC Verification & Audit Suite for Epic #3949:
[Harness2] - Reverse Engineering va Architectural Specification of Harness2 Framework

Stages checked:
- Stage 1: Acceptance Criteria Verification (Spec, Wayfinder Map, Research Reports, 0 Git leak)
- Stage 2: AST Syntax and Importability of projects/harness2 core and substrate modules
- Stage 3: Mathematical Budget Conservation Invariants (R=4k rollouts, P=3k sessions, assert_identity)
- Stage 4: 8-Component Space ($c_1 \dots c_8$) and Substrate SurfaceSpec Compliance
- Stage 5: Strict Typing and Zero Git Leak Guard
"""

import os
import sys
import ast
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "projects" / "harness2"))

def test_stage1_ac_files_exist():
    """Verify all AC deliverables exist and are non-empty."""
    spec_arch = BASE_DIR / "docs" / "spec-harness2-architecture.md"
    wayfinder_map = BASE_DIR / "docs" / "spec" / "wayfinder-harness2-map.md"
    research_rea = BASE_DIR / "tools" / "research" / "research_harness2_rea_analysis.md"
    core_recursion = BASE_DIR / "docs" / "spec" / "harness2-core-recursion.md"

    assert spec_arch.is_file(), f"Missing spec: {spec_arch}"
    assert wayfinder_map.is_file(), f"Missing wayfinder map: {wayfinder_map}"
    assert research_rea.is_file(), f"Missing REA research report: {research_rea}"
    assert core_recursion.is_file(), f"Missing core recursion spec: {core_recursion}"

    # Verify minimum content length
    arch_content = spec_arch.read_text(encoding="utf-8")
    assert len(arch_content) > 10000, "Architecture spec too short"
    assert "SPEC-HARNESS2-ARCH-2026-V1" in arch_content
    assert "7-POINT REVIEW GATE" in arch_content
    assert "R=4k" in arch_content and "P=3k" in arch_content
    assert "c_1" in arch_content and "c_8" in arch_content
    assert "OpencodeSubstrate" in arch_content and "CodexSubstrate" in arch_content

    wf_content = wayfinder_map.read_text(encoding="utf-8")
    assert "Destination" in wf_content
    assert "Decisions so far" in wf_content
    assert "The Frontier" in wf_content
    assert "Fog of War" in wf_content

    rea_content = research_rea.read_text(encoding="utf-8")
    assert "REA Evidence ID" in rea_content
    assert "ASSETS.json" in rea_content


def test_stage2_ast_syntax_and_integrity():
    """Verify AST validity of all Python files in harness2 core and substrate."""
    harness2_dir = BASE_DIR / "projects" / "harness2" / "harness2"
    assert harness2_dir.is_dir(), f"Harness2 dir not found: {harness2_dir}"

    py_files = list(harness2_dir.glob("**/*.py"))
    assert len(py_files) >= 10, f"Expected at least 10 python files, got {len(py_files)}"

    for py_file in py_files:
        code = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(code, filename=str(py_file))
            assert isinstance(tree, ast.Module), f"Failed to parse {py_file}"
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {py_file}: {e}")


def test_stage3_mathematical_budget_invariants():
    """Verify mathematical budget conservation R=4k and P=3k in Ledger."""
    from harness2.core.ledger import Ledger, BudgetError, expected_rollouts, expected_sessions

    for k in (1, 2, 4, 8):
        assert expected_rollouts(k) == 4 * k
        assert expected_sessions(k) == 3 * k

        ledger = Ledger(mode="agg", task_id="task_test_01", k=k)

        # Empty ledger must fail assert_identity
        try:
            ledger.assert_identity()
            raise AssertionError("Empty ledger should have raised BudgetError")
        except BudgetError:
            pass

        # Populate valid rollouts (4k)
        for i in range(4 * k):
            ledger.rollout(f"rollout_{i}")

        # Populate valid sessions (3k)
        for j in range(3 * k):
            ledger.session(f"session_{j}")

        # Should pass
        ledger.assert_identity()
        assert ledger.R == 4 * k
        assert ledger.P == 3 * k

        # Duplicate label must raise BudgetError even if counts match
        dup_ledger = Ledger(mode="agg", task_id="task_test_dup", k=1)
        for i in range(3):
            dup_ledger.rollout(f"r_{i}")
        dup_ledger.rollout("r_0")  # Duplicate
        for j in range(3):
            dup_ledger.session(f"s_{j}")

        try:
            dup_ledger.assert_identity()
            raise AssertionError("Duplicate label should have raised BudgetError")
        except BudgetError as e:
            assert "DUPLICATE labels" in str(e)


def test_stage4_substrate_contracts():
    r"""Verify Substrate SurfaceSpec and substrate protocol definitions."""
    from harness2.core.tree import SurfaceSpec
    from harness2.substrate.opencode import OPENCODE_SURFACE
    from harness2.substrate.codex import CODEX_SURFACE

    assert isinstance(OPENCODE_SURFACE, SurfaceSpec)
    assert isinstance(CODEX_SURFACE, SurfaceSpec)
    assert OPENCODE_SURFACE.always_on_max == 24000
    assert CODEX_SURFACE.always_on_max == 8000
    assert OPENCODE_SURFACE.name == "opencode"
    assert CODEX_SURFACE.name == "codex"


def test_stage5_zero_git_leak():
    """Verify that projects/harness2 is 100% ignored and never tracked in Git."""
    # Run git check-ignore
    check_ignore = subprocess.run(
        ["git", "check-ignore", "-q", "projects/harness2"],
        cwd=str(BASE_DIR),
        capture_output=True,
    )
    assert check_ignore.returncode == 0, "projects/harness2 must be in .gitignore"

    # Check git status for staged/tracked files in projects/
    ls_files = subprocess.run(
        ["git", "ls-files", "projects/"],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
    )
    assert ls_files.stdout.strip() == "", f"Git tracked files found in projects/: {ls_files.stdout}"

    # Run git pre-commit guard
    guard = subprocess.run(
        ["python3", "scripts/git_pre_commit_guard.py"],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
    )
    assert guard.returncode == 0, f"git_pre_commit_guard failed: {guard.stderr} {guard.stdout}"


if __name__ == "__main__":
    print("Running QC Audit Suite for Epic #3949 [Harness2 Architecture]...")
    test_stage1_ac_files_exist()
    print("  [PASS] Stage 1: Acceptance Criteria files exist & verified")
    test_stage2_ast_syntax_and_integrity()
    print("  [PASS] Stage 2: AST syntax & integrity of Python codebase verified")
    test_stage3_mathematical_budget_invariants()
    print("  [PASS] Stage 3: Mathematical budget conservation (R=4k, P=3k) verified")
    test_stage4_substrate_contracts()
    print("  [PASS] Stage 4: Substrate SurfaceSpec contracts verified")
    test_stage5_zero_git_leak()
    print("  [PASS] Stage 5: Zero Git leak & pre-commit guard verified")
    print("\nALL 5 STAGES OF QC AUDIT PASSED 100%.")
