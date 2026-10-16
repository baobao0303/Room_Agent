#!/usr/bin/env python3
"""
tools/test_qc_generator.py - Self-check for Paseo QC Test Generator.
Verifies:
1. validate_work_item enforces ALLOWED_PROFILES (rejects bad profiles).
2. Generated TypeScript output contains no 'toBeDefined' and uses real values or test.todo.
3. Generated Pytest output contains no 'assert True' and uses real values or pytest.fail.
4. run_verify_command does not use shell=True and executes via argv.
"""

import sys
import inspect
from pathlib import Path

_cur = Path(__file__).resolve()
BASE_DIR = _cur.parent.parent if _cur.parent.name == "tools" else _cur.parents[2]
sys.path.insert(0, str(BASE_DIR))

from tools.qc_test_generator import (
    validate_work_item,
    ALLOWED_PROFILES,
    render_unit_test_file,
    run_verify_command,
)


def test_validate_work_item():
    # 1. Valid profiles should pass
    assert validate_work_item(assigned_to_profile="QC", created_by_profile="QC") is True
    assert validate_work_item({"assigned_to_profile": "Lead", "created_by_profile": "Supervisor"}) is True

    # 2. Bad profiles should raise ValueError
    bad_profiles = ["evil_profile", "unknown", "admin", "root", "hacker"]
    for bad in bad_profiles:
        try:
            validate_work_item(assigned_to_profile=bad)
            assert False, f"Should have rejected bad assigned_to_profile: {bad}"
        except ValueError:
            pass

        try:
            validate_work_item(created_by_profile=bad)
            assert False, f"Should have rejected bad created_by_profile: {bad}"
        except ValueError:
            pass

        try:
            validate_work_item({"assigned_to_profile": bad, "created_by_profile": "QC"})
            assert False, f"Should have rejected dict with bad assigned_to_profile: {bad}"
        except ValueError:
            pass


def test_ts_generated_output():
    code_ctx = {
        "file_path": "/fake/path/auth.service.ts",
        "module_name": "AuthService",
        "language": "typescript",
        "framework": "vitest",
        "classes": ["AuthService"],
        "symbols": [
            {
                "name": "login",
                "method_name": "login",
                "class_name": "AuthService",
                "kind": "method",
                "params": [{"name": "token", "type": "string"}],
                "return_type": "boolean",
                "has_branches": True,
                "has_throws": False,
            }
        ],
    }

    # Case 1: Concrete expectation derivable
    cases_with_ac = [
        {
            "id": "TC-TP001-01",
            "title": "[AuthService]: succeeds when valid token provided",
            "steps": ["Given context", "When login", "Then verify returns true"],
            "test_data": "token='valid-token'",
            "expected_results": ["returns true"],
            "acceptance_criteria": ["login returns true on success"],
            "test_point_refs": ["TP-001"],
            "covered_items": ["CI-01"],
            "symbol_ref": "login",
            "is_negative": False,
        }
    ]
    out_ts = render_unit_test_file(code_ctx, cases_with_ac, Path("auth.service.spec.ts"))
    assert "toBeDefined" not in out_ts, "Found forbidden toBeDefined in generated TS output"
    assert "toBe(true)" in out_ts, f"Expected real assertion toBe(true), got:\n{out_ts}"

    # Case 2: No expectation derivable -> test.todo marker
    cases_no_ac = [
        {
            "id": "TC-TP002-01",
            "title": "[AuthService]: unknown behavior",
            "steps": ["Given context", "When unknown", "Then verify something"],
            "test_data": "",
            "expected_results": [],
            "acceptance_criteria": [],
            "test_point_refs": ["TP-002"],
            "covered_items": ["CI-02"],
            "symbol_ref": None,
            "is_negative": False,
        }
    ]
    out_ts_todo = render_unit_test_file(code_ctx, cases_no_ac, Path("auth.service.spec.ts"))
    assert "toBeDefined" not in out_ts_todo, "Found forbidden toBeDefined in generated TS output"
    assert "test.todo" in out_ts_todo, f"Expected test.todo marker for unassertable case, got:\n{out_ts_todo}"


def test_py_generated_output():
    code_ctx = {
        "file_path": "/fake/path/calculator.py",
        "module_name": "calculator",
        "language": "python",
        "framework": "pytest",
        "classes": [],
        "symbols": [
            {
                "name": "add",
                "method_name": "add",
                "class_name": None,
                "kind": "function",
                "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
                "return_type": "int",
                "has_branches": False,
                "has_throws": False,
            }
        ],
    }

    # Case 1: Concrete expectation derivable
    cases_with_ac = [
        {
            "id": "TC-TP001-01",
            "title": "[calculator]: returns 42 when adding 40 and 2",
            "steps": ["Given numbers", "When adding", "Then verify returns 42"],
            "test_data": "a=40, b=2",
            "expected_results": ["returns 42"],
            "acceptance_criteria": ["returns 42"],
            "test_point_refs": ["TP-001"],
            "covered_items": ["CI-01"],
            "symbol_ref": "add",
            "is_negative": False,
        }
    ]
    out_py = render_unit_test_file(code_ctx, cases_with_ac, Path("test_calculator.py"))
    assert "assert True" not in out_py, "Found forbidden 'assert True' in generated Pytest output"
    assert "assert result == 42" in out_py, f"Expected real assertion == 42, got:\n{out_py}"

    # Case 2: No expectation derivable -> pytest.fail marker
    cases_no_ac = [
        {
            "id": "TC-TP002-01",
            "title": "[calculator]: vague check",
            "steps": ["Given numbers", "When vague", "Then verify something"],
            "test_data": "",
            "expected_results": [],
            "acceptance_criteria": [],
            "test_point_refs": ["TP-002"],
            "covered_items": ["CI-02"],
            "symbol_ref": None,
            "is_negative": False,
        }
    ]
    out_py_fail = render_unit_test_file(code_ctx, cases_no_ac, Path("test_calculator.py"))
    assert "assert True" not in out_py_fail, "Found forbidden 'assert True' in generated Pytest output"
    assert "pytest.fail" in out_py_fail, f"Expected pytest.fail marker, got:\n{out_py_fail}"


def test_run_verify_command_no_shell():
    src = inspect.getsource(run_verify_command)
    assert "shell=True" not in src, "run_verify_command must not use shell=True"

    # Execution check with argv
    res = run_verify_command([sys.executable, "--version"], cwd=BASE_DIR)
    assert res["passed"] is True, f"Execution failed: {res}"
    assert "Python" in res["output_tail"], f"Unexpected output: {res}"


def main():
    test_validate_work_item()
    test_ts_generated_output()
    test_py_generated_output()
    test_run_verify_command_no_shell()
    print("ALL QC GENERATOR SELF-CHECKS PASSED.")


if __name__ == "__main__":
    main()
