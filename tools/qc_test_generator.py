#!/usr/bin/env python3
"""
tools/qc_test_generator.py - Paseo QC 5-Stage ISTQB Unit Test & Testcase Generator.

5-Stage Deterministic + AST Pipeline:
  Stage 1: Spec & Codebase Context Analysis (RequirementAnalysis + AST/Symbol Extraction)
  Stage 2: Test Point Identification across 9 Dimensions (TestPointSet + Deduplication & Budget Clamp)
  Stage 3: Deterministic Test Design Plan (7 ISTQB Techniques + CoverageItem Skeletons + Case Budget)
  Stage 4: Test Case & Executable Unit Test Generation (TC-TPxxx-xx + Jest/Vitest *.spec.ts + Harness Sync)
  Stage 5: Deterministic Coverage Report & Automated Test Execution Gate (0% LLM self-grading)
"""

import os
import re
import sys
import ast
import json
import shlex
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from collections import Counter
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple, Set, Union

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# ---------- Paseo Agent Profile Constraints ----------
ALLOWED_PROFILES: List[str] = [
    "Lead BA",
    "Peer BA",
    "Lead design",
    "Peer Design",
    "Lead Dev",
    "Peer Dev",
    "Supervisor",
    "Lead",
    "Peer",
    "QC",
]


def validate_work_item(
    work_item: Any = None,
    *args: Any,
    assigned_to_profile: Optional[str] = None,
    created_by_profile: Optional[str] = None,
    **kwargs: Any,
) -> bool:
    """Validate work item profile constraints against ALLOWED_PROFILES."""
    if isinstance(work_item, dict):
        assigned_to_profile = assigned_to_profile or work_item.get("assigned_to_profile")
        created_by_profile = created_by_profile or work_item.get("created_by_profile")
    else:
        assigned_to_profile = assigned_to_profile or kwargs.get("assigned_to_profile")
        created_by_profile = created_by_profile or kwargs.get("created_by_profile")

    allowed_set = set(ALLOWED_PROFILES)
    if assigned_to_profile is not None and assigned_to_profile not in allowed_set:
        raise ValueError(
            f"Invalid assigned_to_profile '{assigned_to_profile}': must be one of {sorted(allowed_set)}"
        )

    if created_by_profile is not None and created_by_profile not in allowed_set:
        raise ValueError(
            f"Invalid created_by_profile '{created_by_profile}': must be one of {sorted(allowed_set)}"
        )

    return True

# ---------- Scale & Similarity Constants (Aligned with D-036 workflows/test_design.py) ----------

TEST_POINT_PER_REQUIREMENT = 3
TEST_POINT_LIMIT_MIN = 6
TEST_POINT_LIMIT_MAX = 40

CASE_PER_TEST_POINT = 2
CASE_BUDGET_MIN = 10
CASE_BUDGET_MAX = 40
CASE_BATCH_SIZE = 4

TEST_POINT_DUPLICATE_THRESHOLD = 0.85
DUPLICATE_SIMILARITY_THRESHOLD = 0.85

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
RISK_ORDER = {"high": 0, "medium": 1, "low": 2}

TEST_POINT_DIMENSIONS = (
    "function",
    "flow",
    "state",
    "permission",
    "data",
    "boundary",
    "exception",
    "business_rule",
    "nonfunctional",
)

TEST_DESIGN_TECHNIQUES = (
    "equivalence_partitioning",
    "boundary_value",
    "decision_table",
    "state_transition",
    "scenario",
    "error_guessing",
    "exploratory",
)

# Heuristic keyword patterns (Vietnamese + English + Code tokens)
QUANTITY_PATTERN = re.compile(
    r"\d+|lần|phút|giây|ngày|ký tự|độ dài|tối đa|tối thiểu|không quá|ít nhất|nhiều nhất|"
    r"max|min|limit|length|count|timeout|retry|size|threshold|range|<|>|<=|>=",
    re.IGNORECASE,
)

STATE_KEYWORDS = (
    "trạng thái", "state", "status", "chuyển", "transition", "khoá", "lock", "unlock",
    "kích hoạt", "active", "inactive", "pending", "resolved", "closed", "signal", "store",
    "loading", "disabled", "enabled", "expired", "hết hạn",
)
PERMISSION_KEYWORDS = (
    "quyền", "permission", "role", "vai trò", "auth", "login", "đăng nhập", "token",
    "guard", "tenant", "admin", "user", "unauthenticated", "forbidden", "401", "403",
)
RULE_KEYWORDS = (
    "nếu", "khi", "điều kiện", "quy tắc", "rule", "condition", "and", "or", "&&", "||",
    "hợp lệ", "valid", "invalid", "bắt buộc", "required",
)
FLOW_KEYWORDS = (
    "luồng", "bước", "quy trình", "flow", "step", "submit", "gửi", "lưu", "save",
    "create", "update", "delete", "callback", "redirect", "pipeline",
)
ERROR_KEYWORDS = (
    "lỗi", "ngoại lệ", "exception", "error", "fail", "thất bại", "timeout", "null",
    "undefined", "empty", "rỗng", "duplicate", "trùng", "race", "catch", "throw", "reject",
)

# Deterministic Coverage Templates per Technique (D-036 Stage 3)
COVERAGE_TEMPLATES: Dict[str, Tuple[Tuple[str, str], ...]] = {
    "equivalence_partitioning": (
        ("Valid equivalence partition input", "Provide typical valid inputs within allowed spec/type domain"),
        ("Invalid equivalence partition input", "Provide malformed, null/undefined, or disallowed inputs"),
    ),
    "boundary_value": (
        ("Lower boundary and below-min edge", "Test at minimum allowed value and (min - 1) / empty"),
        ("Upper boundary and above-max edge", "Test at maximum allowed value and (max + 1) / overflow"),
    ),
    "decision_table": (
        ("All rule conditions satisfied", "All boolean/business conditions evaluate to true simultaneously"),
        ("Individual condition falsified", "Toggle each required condition to false one by one"),
    ),
    "state_transition": (
        ("Valid state transition path", "Trigger allowed state mutation from valid initial state"),
        ("Invalid/guarded state transition", "Trigger action from disallowed or locked state"),
    ),
    "scenario": (
        ("End-to-end happy path scenario", "Execute main functional flow from precondition to expected output"),
        ("Interrupted or alternative branch scenario", "Trigger early return, cancellation, or fallback branch"),
    ),
    "error_guessing": (
        ("Exception, null-safety & fault tolerance", "Simulate thrown error, rejected promise/observable, duplicate call, or corrupt payload"),
    ),
    "exploratory": (
        ("Non-functional & security/isolation check", "Verify performance bounds, tenant isolation, or idempotency"),
    ),
}

# Type Mutation Rules (Adapted from services/api_case_engine.py D-020)
TYPE_MUTATIONS: Dict[str, Dict[str, Any]] = {
    "string": {"valid": "'valid-sample'", "empty": "''", "nullish": "null as any", "overflow": "'x'.repeat(256)"},
    "number": {"valid": "10", "zero": "0", "negative": "-1", "nan": "NaN"},
    "boolean": {"valid": "true", "falsy": "false"},
    "array": {"valid": "[{ id: '1' }]", "empty": "[]"},
    "object": {"valid": "{ id: '1' }", "empty": "{} as any", "nullish": "null as any"},
}


# ---------- Pure Helper Functions ----------

def text_similarity(a: str, b: str) -> float:
    """Order-sensitive character ratio similarity (0.0 - 1.0)."""
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def case_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """Weighted similarity across title (40%) and steps (60%) as in workflows/test_design.py."""
    title_sim = text_similarity(a.get("title", ""), b.get("title", ""))
    steps_a = "\n".join(a.get("steps") or [])
    steps_b = "\n".join(b.get("steps") or [])
    if not steps_a and not steps_b:
        return title_sim
    steps_sim = text_similarity(steps_a, steps_b)
    return 0.4 * title_sim + 0.6 * steps_sim


def short_code(tp_id: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", tp_id or "") or "TP"


def dynamic_test_point_limit(requirement_count: int) -> int:
    return min(
        TEST_POINT_LIMIT_MAX,
        max(TEST_POINT_LIMIT_MIN, max(1, requirement_count) * TEST_POINT_PER_REQUIREMENT),
    )


def dynamic_case_budget(test_point_count: int) -> int:
    return min(
        CASE_BUDGET_MAX,
        max(CASE_BUDGET_MIN, max(1, test_point_count) * CASE_PER_TEST_POINT),
    )


def _contains_any(text: str, keywords: Tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(k in lower for k in keywords)


def _tp_sort_key(tp: Dict[str, Any]) -> Tuple[int, int, str]:
    return (
        PRIORITY_ORDER.get(tp.get("priority", "P1"), 2),
        RISK_ORDER.get(tp.get("risk_level", "medium"), 2),
        tp.get("id") or "",
    )


# ---------- Stage 1: Spec & Codebase Context Extraction ----------

def parse_spec_content(spec_text: str, module_hint: str = "Core") -> Dict[str, Any]:
    """Parse Markdown spec or Acceptance Criteria into structured RequirementAnalysis (D-036 Stage 1)."""
    lines = [l.strip() for l in spec_text.splitlines() if l.strip()]
    summary = lines[0].lstrip("# ").strip() if lines else f"{module_hint} Specification"

    functional_reqs: List[Dict[str, str]] = []
    business_rules: List[str] = []
    acceptance_criteria: List[str] = []
    preconditions: List[str] = []
    risks: List[Dict[str, str]] = []
    assumptions: List[str] = []
    roles: Set[str] = set()

    req_counter = 1
    current_section = "general"

    for line in lines:
        lower = line.lower()
        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            if any(k in heading for k in ["acceptance", "ac", "tiêu chí", "nghiệm thu"]):
                current_section = "ac"
            elif any(k in heading for k in ["rule", "quy tắc", "business", "nghiệp vụ", "constraint"]):
                current_section = "rule"
            elif any(k in heading for k in ["pre-condition", "precondition", "tiền điều kiện"]):
                current_section = "pre"
            elif any(k in heading for k in ["risk", "rủi ro", "edge", "exception", "ngoại lệ"]):
                current_section = "risk"
            else:
                current_section = "req"
            continue

        # Role extraction from BDD "As a <Role>"
        m_role = re.search(r"as an?\s+([^,\n]+)", line, re.IGNORECASE)
        if m_role:
            roles.add(m_role.group(1).strip())

        # Bullet or numbered item
        is_item = bool(re.match(r"^(\-|\*|\d+[\.\)]|\[[ xX]\]|AC\d+|BR\d+|UC\d+)", line))
        clean_item = re.sub(r"^(\-|\*|\d+[\.\)]|\s*\[[ xX]\]\s*)+", "", line).strip()

        # Skip Markdown Table of Contents links like [Section](#anchor)
        if re.match(r"^\[[^\]]+\]\(#[^\)]+\)$", clean_item):
            continue

        if not clean_item or len(clean_item) < 4:
            continue

        if current_section == "ac" or re.match(r"^AC[\-\s\d:]+", clean_item, re.IGNORECASE):
            acceptance_criteria.append(clean_item)
            req_id = f"REQ-{req_counter:03d}"
            req_counter += 1
            functional_reqs.append({
                "id": req_id,
                "title": clean_item[:80],
                "description": clean_item,
            })
        elif current_section == "rule" or re.match(r"^BR[\-\s\d:]+", clean_item, re.IGNORECASE):
            business_rules.append(clean_item)
        elif current_section == "pre":
            preconditions.append(clean_item)
        elif current_section == "risk":
            risks.append({
                "id": f"RISK-{len(risks) + 1:03d}",
                "description": clean_item,
                "level": "high" if _contains_any(clean_item, ERROR_KEYWORDS + PERMISSION_KEYWORDS) else "medium",
            })
        elif is_item:
            req_id = f"REQ-{req_counter:03d}"
            req_counter += 1
            functional_reqs.append({
                "id": req_id,
                "title": clean_item[:80],
                "description": clean_item,
            })

    # Fallback: if no bullet points were found, treat non-empty sentences as requirements
    if not functional_reqs and spec_text.strip():
        for chunk in re.split(r"[\n\.]+", spec_text.strip()):
            c = chunk.strip()
            if len(c) > 8:
                functional_reqs.append({
                    "id": f"REQ-{req_counter:03d}",
                    "title": c[:80],
                    "description": c,
                })
                req_counter += 1

    # Detect ambiguities / missing boundary definitions (D-036 defect identification)
    for req in functional_reqs:
        desc = req["description"]
        if any(w in desc.lower() for w in ["nhanh", "nhiều", "lớn", "fast", "large", "appropriate", "hợp lý"]) and not QUANTITY_PATTERN.search(desc):
            assumptions.append(f"{req['id']} uses qualitative term without explicit numeric threshold: '{desc[:60]}'")

    return {
        "module": module_hint,
        "summary": summary,
        "scope": [r["title"] for r in functional_reqs],
        "roles": sorted(roles) if roles else ["User"],
        "functional_requirements": functional_reqs,
        "business_rules": business_rules,
        "constraints": [],
        "preconditions": preconditions,
        "acceptance_criteria": acceptance_criteria,
        "risks": risks,
        "assumptions": assumptions,
    }


def analyze_source_file(file_path: Path) -> Dict[str, Any]:
    """Extract classes, functions/methods, parameters, return types, branches, and framework hints from TS/JS/Py code."""
    if not file_path.exists() or not file_path.is_file():
        return {"file_path": str(file_path), "language": "unknown", "symbols": [], "classes": []}

    content = file_path.read_text(encoding="utf-8", errors="replace")
    suffix = file_path.suffix.lower()

    if suffix == ".py" or (content.startswith("#!/") and "python" in content.splitlines()[0]):
        return _analyze_python_source(file_path, content)
    return _analyze_ts_source(file_path, content)


def _analyze_python_source(file_path: Path, content: str) -> Dict[str, Any]:
    symbols: List[Dict[str, Any]] = []
    classes: List[str] = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith("__"):
                        params = [a.arg for a in item.args.args if a.arg != "self"]
                        has_raise = any(isinstance(sub, ast.Raise) for sub in ast.walk(item))
                        has_if = any(isinstance(sub, ast.If) for sub in ast.walk(item))
                        symbols.append({
                            "name": f"{node.name}.{item.name}",
                            "method_name": item.name,
                            "class_name": node.name,
                            "kind": "method",
                            "params": [{"name": p, "type": "any"} for p in params],
                            "has_branches": has_if,
                            "has_throws": has_raise,
                            "is_async": False,
                        })
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                params = [a.arg for a in node.args.args]
                symbols.append({
                    "name": node.name,
                    "method_name": node.name,
                    "class_name": None,
                    "kind": "function",
                    "params": [{"name": p, "type": "any"} for p in params],
                    "has_branches": any(isinstance(sub, ast.If) for sub in ast.walk(node)),
                    "has_throws": any(isinstance(sub, ast.Raise) for sub in ast.walk(node)),
                    "is_async": False,
                })
    except Exception:
        pass

    return {
        "file_path": str(file_path),
        "module_name": file_path.stem,
        "language": "python",
        "framework": "pytest",
        "classes": classes,
        "symbols": symbols,
    }


def _analyze_ts_source(file_path: Path, content: str) -> Dict[str, Any]:
    classes = re.findall(r"export\s+class\s+([A-Za-z0-9_]+)", content)
    is_angular_component = "@Component" in content
    is_angular_service = "@Injectable" in content
    has_signals = bool(re.search(r"\b(?:signal|computed|input|output)\s*[<\(]", content))

    symbols: List[Dict[str, Any]] = []
    primary_class = classes[0] if classes else None

    # 1. Extract standalone exported functions
    fn_pattern = re.compile(
        r"export\s+(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)\s*(?::\s*([^{;]+))?",
        re.MULTILINE,
    )
    for m in fn_pattern.finditer(content):
        fn_name = m.group(1)
        raw_params = m.group(2)
        ret_type = (m.group(3) or "any").strip()
        symbols.append({
            "name": fn_name,
            "method_name": fn_name,
            "class_name": None,
            "kind": "function",
            "params": _parse_ts_params(raw_params),
            "return_type": ret_type,
            "has_branches": "if (" in content or "switch (" in content or "?" in content,
            "has_throws": "throw " in content or "catch" in content,
            "is_async": "async " in m.group(0) or "Promise<" in ret_type or "Observable<" in ret_type,
        })

    # 2. Extract class methods
    reserved = {"if", "for", "while", "switch", "catch", "constructor", "super", "return", "function"}
    method_pattern = re.compile(
        r"^\s*(?:public\s+|private\s+|protected\s+)?(async\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*(?::\s*([^{;]+))?\s*\{",
        re.MULTILINE,
    )
    for m in method_pattern.finditer(content):
        is_async_kw = bool(m.group(1))
        m_name = m.group(2)
        if m_name in reserved:
            continue
        raw_params = m.group(3)
        ret_type = (m.group(4) or "void").strip()
        # Extract approximate method body slice (next 600 chars) to check branches/throws
        start_idx = m.end()
        body_slice = content[start_idx : start_idx + 800]
        symbols.append({
            "name": f"{primary_class}.{m_name}" if primary_class else m_name,
            "method_name": m_name,
            "class_name": primary_class,
            "kind": "method",
            "params": _parse_ts_params(raw_params),
            "return_type": ret_type,
            "has_branches": bool(re.search(r"\b(if|switch|else)\b|\?", body_slice)),
            "has_throws": bool(re.search(r"\b(throw|catch|error|reject|throwError)\b", body_slice)),
            "is_async": is_async_kw or "Promise" in ret_type or "Observable" in ret_type,
        })

    # 3. Extract Angular Signals / Computed properties if present
    signal_pattern = re.compile(
        r"^\s*(?:readonly\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(signal|computed|input)\s*(?:<([^>]+)>)?\s*\(",
        re.MULTILINE,
    )
    for m in signal_pattern.finditer(content):
        sig_name, sig_kind, sig_type = m.group(1), m.group(2), m.group(3) or "any"
        symbols.append({
            "name": f"{primary_class}.{sig_name}" if primary_class else sig_name,
            "method_name": sig_name,
            "class_name": primary_class,
            "kind": f"signal:{sig_kind}",
            "params": [],
            "return_type": sig_type,
            "has_branches": sig_kind == "computed",
            "has_throws": False,
            "is_async": False,
        })

    # Detect test runner (Vitest vs Jest)
    framework = "jest"
    curr = file_path.parent
    for _ in range(5):
        if (curr / "vitest.config.ts").exists() or (curr / "vite.config.ts").exists():
            framework = "vitest"
            break
        if (curr / "jest.config.ts").exists() or (curr / "jest.preset.js").exists():
            framework = "jest"
            break
        if curr.parent == curr:
            break
        curr = curr.parent

    return {
        "file_path": str(file_path),
        "module_name": primary_class or file_path.stem,
        "language": "typescript",
        "framework": framework,
        "is_angular_component": is_angular_component,
        "is_angular_service": is_angular_service,
        "has_signals": has_signals,
        "classes": classes,
        "symbols": symbols,
    }


def _parse_ts_params(raw_params: str) -> List[Dict[str, Any]]:
    params: List[Dict[str, Any]] = []
    if not raw_params.strip():
        return params
    for part in raw_params.split(","):
        p = part.strip()
        if not p or p.startswith("private ") or p.startswith("readonly ") and "inject(" in p:
            continue
        p_clean = re.sub(r"^(?:public|private|protected|readonly)\s+", "", p)
        optional = "?" in p_clean or "=" in p_clean
        name_part = re.split(r"[\?:=]", p_clean)[0].strip()
        type_match = re.search(r":\s*([^=]+)", p_clean)
        p_type = type_match.group(1).strip() if type_match else "any"
        params.append({
            "name": name_part,
            "type": p_type,
            "optional": optional,
        })
    return params


# ---------- Stage 2: Test Point Identification & Post-Processing (D-036 Stage 2) ----------

def generate_test_points(
    analysis: Dict[str, Any],
    code_ctx: Dict[str, Any],
) -> Dict[str, Any]:
    """Combine Spec Requirements + Codebase Symbols into structured TestPoints across 9 dimensions."""
    reqs = analysis.get("functional_requirements") or []
    symbols = code_ctx.get("symbols") or []
    module_name = code_ctx.get("module_name") or analysis.get("module") or "Module"

    raw_points: List[Dict[str, Any]] = []
    tp_seq = 1

    # Ensure at least one requirement exists even when running purely from code
    if not reqs:
        for idx, sym in enumerate(symbols or [{"name": module_name, "method_name": "default"}], start=1):
            reqs.append({
                "id": f"REQ-{idx:03d}",
                "title": f"Verify behavior of {sym['name']}",
                "description": f"Function/method {sym['name']} executes according to contract.",
            })
        analysis["functional_requirements"] = reqs

    req_ids = {r["id"] for r in reqs}

    # 1. Derive Code-Driven TestPoints for every exported symbol FIRST (guarantees 100% symbol coverage)
    default_req_id = reqs[0]["id"]
    for sym in symbols:
        m_name = sym["method_name"]
        matched_req = _match_req_for_symbol(sym, reqs) or default_req_id
        dim = "state" if sym["kind"].startswith("signal") else ("flow" if sym.get("has_branches") else "function")
        raw_points.append({
            "id": f"TP-{tp_seq:03d}",
            "title": f"[{module_name}] Functional contract of {sym['name']}()",
            "description": f"Verify input/output behavior and state transitions of {sym['name']}",
            "requirement_refs": [matched_req],
            "symbol_ref": m_name,
            "dimension": dim,
            "risk_level": "high",
            "priority": "P0",
            "rationale": f"Exported codebase symbol {sym['name']} requires unit test coverage",
        })
        tp_seq += 1

        if sym.get("has_throws") or sym.get("params"):
            raw_points.append({
                "id": f"TP-{tp_seq:03d}",
                "title": f"[{module_name}] Exception & boundary handling in {sym['name']}()",
                "description": f"Verify {sym['name']} handles null/invalid parameters and boundary limits safely",
                "requirement_refs": [matched_req],
                "symbol_ref": m_name,
                "dimension": "exception" if sym.get("has_throws") else "boundary",
                "risk_level": "high",
                "priority": "P0",
                "rationale": f"Parameter/error path detected in symbol {sym['name']}",
            })
            tp_seq += 1

    # 2. Derive TestPoints from Functional Requirements in Spec
    for idx_req, req in enumerate(reqs):
        r_id = req["id"]
        text = f"{req.get('title', '')} {req.get('description', '')}"

        matched_sym = _match_symbol_for_text(text, symbols, fallback_index=idx_req)
        sym_name = matched_sym["name"] if matched_sym else module_name

        dim = _classify_dimension(text, matched_sym)
        risk = "high" if dim in ("permission", "exception", "state", "boundary") else "medium"
        prio = "P0" if risk == "high" else "P1"

        raw_points.append({
            "id": f"TP-{tp_seq:03d}",
            "title": f"[{module_name}] {req['title'][:65]}",
            "description": f"Verify {sym_name}: {req['description']}",
            "requirement_refs": [r_id],
            "symbol_ref": matched_sym["method_name"] if matched_sym else None,
            "dimension": dim,
            "risk_level": risk,
            "priority": prio,
            "rationale": f"Directly validates requirement {r_id} on {sym_name}",
        })
        tp_seq += 1

    accepted, dropped, issues = validate_test_points(raw_points, req_ids)

    return {
        "test_points": accepted,
        "dropped_test_points": dropped,
        "validation_issues": issues,
        "coverage_target": f"Cover {len(req_ids)} requirements and {len(symbols)} codebase symbols across ISTQB dimensions",
    }


def _classify_dimension(text: str, sym: Optional[Dict[str, Any]] = None) -> str:
    if _contains_any(text, PERMISSION_KEYWORDS):
        return "permission"
    if _contains_any(text, STATE_KEYWORDS) or (sym and sym.get("kind", "").startswith("signal")):
        return "state"
    if _contains_any(text, ERROR_KEYWORDS) or (sym and sym.get("has_throws")):
        return "exception"
    if QUANTITY_PATTERN.search(text):
        return "boundary"
    if _contains_any(text, RULE_KEYWORDS):
        return "business_rule"
    if _contains_any(text, FLOW_KEYWORDS):
        return "flow"
    return "function"


def _match_symbol_for_text(text: str, symbols: List[Dict[str, Any]], fallback_index: int = 0) -> Optional[Dict[str, Any]]:
    if not symbols:
        return None
    lower = text.lower()
    best_sym = None
    best_score = 0.0
    for sym in symbols:
        m_name = sym["method_name"].lower()
        tokens = re.findall(r"[a-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", sym["method_name"]).lower())
        score = sum(1.0 for t in tokens if len(t) > 2 and t in lower)
        if m_name in lower:
            score += 3.0
        if score > best_score:
            best_score = score
            best_sym = sym
    return best_sym or symbols[fallback_index % len(symbols)]


def _match_req_for_symbol(sym: Dict[str, Any], reqs: List[Dict[str, Any]]) -> Optional[str]:
    if not reqs:
        return None
    tokens = re.findall(r"[a-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", sym["method_name"]).lower())
    for req in reqs:
        r_text = f"{req.get('title', '')} {req.get('description', '')}".lower()
        if any(t in r_text for t in tokens if len(t) > 2):
            return req["id"]
    return reqs[0]["id"]


def validate_test_points(
    test_points: List[Dict[str, Any]],
    requirement_ids: Set[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Deterministic post-processing (from workflows/test_design.py):
    1. Filter invalid requirement_refs
    2. Deduplicate within same requirement (>= 0.85 title similarity)
    3. Clamp to dynamic budget sorted by priority & risk
    4. Flag uncovered requirement gaps
    """
    accepted: List[Dict[str, Any]] = []
    dropped: List[Dict[str, Any]] = []
    issues: List[str] = []

    for raw in test_points or []:
        refs = [r for r in (raw.get("requirement_refs") or []) if r in requirement_ids]
        if not refs:
            dropped.append({"id": raw.get("id"), "title": raw.get("title"), "reason": "No valid requirement_refs"})
            continue

        candidate = {**raw, "requirement_refs": refs}
        dup = None
        for existing in accepted:
            if set(candidate["requirement_refs"]) & set(existing["requirement_refs"]):
                if text_similarity(candidate.get("title", ""), existing.get("title", "")) >= TEST_POINT_DUPLICATE_THRESHOLD:
                    dup = existing
                    break
        if dup:
            dropped.append({
                "id": raw.get("id"),
                "title": raw.get("title"),
                "reason": f"Semantically duplicate with {dup.get('id')}",
            })
            continue
        accepted.append(candidate)

    limit = dynamic_test_point_limit(len(requirement_ids))
    if len(accepted) > limit:
        accepted.sort(key=_tp_sort_key)
        overflow = accepted[limit:]
        accepted = accepted[:limit]
        for item in overflow:
            dropped.append({"id": item.get("id"), "title": item.get("title"), "reason": f"Exceeded dynamic limit {limit}"})
        issues.append(f"Trimmed {len(overflow)} test points exceeding budget {limit}")

    # Re-index accepted TP IDs sequentially
    for idx, tp in enumerate(accepted, start=1):
        tp["id"] = f"TP-{idx:03d}"

    covered = {r for tp in accepted for r in tp.get("requirement_refs", [])}
    missing = sorted(requirement_ids - covered)
    if missing:
        issues.append("Uncovered requirements: " + ", ".join(missing))

    return accepted, dropped, issues


# ---------- Stage 3: Deterministic Test Design Plan (D-036 Stage 3, 0% LLM) ----------

def detect_techniques(test_point: Dict[str, Any]) -> List[str]:
    """Deterministically select ISTQB test design techniques from dimension & text cues."""
    dim = test_point.get("dimension") or "function"
    text = " ".join(filter(None, [
        test_point.get("title"),
        test_point.get("description"),
        test_point.get("rationale"),
    ]))
    techniques: List[str] = []

    if dim == "nonfunctional":
        techniques.append("exploratory")
    elif dim == "boundary":
        techniques.extend(["boundary_value", "equivalence_partitioning"])
    elif dim == "state" or _contains_any(text, STATE_KEYWORDS):
        techniques.append("state_transition")
    elif dim == "business_rule" or _contains_any(text, RULE_KEYWORDS):
        techniques.append("decision_table")
    elif dim == "permission":
        techniques.append("scenario")
    elif dim == "exception" or _contains_any(text, ERROR_KEYWORDS):
        techniques.append("error_guessing")
    elif dim == "flow" or _contains_any(text, FLOW_KEYWORDS):
        techniques.append("scenario")
    else:
        techniques.append("equivalence_partitioning")

    if "boundary_value" not in techniques and QUANTITY_PATTERN.search(text) and dim != "nonfunctional":
        techniques.append("boundary_value")

    seen: Set[str] = set()
    ordered: List[str] = []
    for t in techniques:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered


def build_coverage_items(test_point: Dict[str, Any], techniques: List[str]) -> List[Dict[str, Any]]:
    tp_id = test_point.get("id") or "TP"
    code = short_code(tp_id)
    title = test_point.get("title") or ""
    items: List[Dict[str, Any]] = []
    seq = 0
    for tech in techniques:
        for desc, data_hint in COVERAGE_TEMPLATES.get(tech, ()):
            seq += 1
            items.append({
                "id": f"CI-{code}-{seq:02d}",
                "test_point_id": tp_id,
                "technique": tech,
                "description": f"{title}: {desc}" if title else desc,
                "data_hint": data_hint,
            })
    return items


def allocate_case_budget(test_points: List[Dict[str, Any]], total_budget: int) -> Dict[str, int]:
    budget: Dict[str, int] = {}
    ordered = sorted([tp for tp in test_points if tp.get("id")], key=_tp_sort_key)
    for tp in ordered:
        budget[tp["id"]] = 1

    remaining = max(0, total_budget - len(ordered))
    idx = 0
    while remaining > 0 and ordered:
        if all(budget[tp["id"]] >= CASE_BATCH_SIZE for tp in ordered):
            break
        tp = ordered[idx % len(ordered)]
        if budget[tp["id"]] < CASE_BATCH_SIZE:
            budget[tp["id"]] += 1
            remaining -= 1
        idx += 1
    return budget


def build_test_design_plan(test_points: List[Dict[str, Any]], total_budget: Optional[int] = None) -> Dict[str, Any]:
    if total_budget is None:
        total_budget = dynamic_case_budget(len(test_points))
    budget = allocate_case_budget(test_points, total_budget)
    items: List[Dict[str, Any]] = []

    for tp in sorted(test_points, key=_tp_sort_key):
        techs = detect_techniques(tp)
        cov_items = build_coverage_items(tp, techs)
        items.append({
            "test_point_id": tp["id"],
            "techniques": techs,
            "coverage_items": cov_items,
            "case_budget": min(len(cov_items), budget.get(tp["id"], 2)),
            "rationale": f"Dimension '{tp.get('dimension')}' -> {', '.join(techs)}",
        })

    tech_summary = dict(sorted(Counter(t for it in items for t in it["techniques"]).items()))
    return {
        "items": items,
        "total_budget": sum(it["case_budget"] for it in items),
        "technique_summary": tech_summary,
    }


# ---------- Stage 4: Test Case Instantiation & Unit Test Code Generator ----------

def generate_test_cases(
    analysis: Dict[str, Any],
    test_point_set: Dict[str, Any],
    design_plan: Dict[str, Any],
    code_ctx: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Instantiate traceable TestCases (TC-TPxxx-xx) covering every CoverageItem (CI-TPxxx-xx)."""
    module_name = code_ctx.get("module_name") or analysis.get("module") or "Module"
    tp_map = {tp["id"]: tp for tp in test_point_set.get("test_points", [])}
    sym_map = {s["method_name"]: s for s in code_ctx.get("symbols", [])}

    raw_cases: List[Dict[str, Any]] = []

    for plan_item in design_plan.get("items", []):
        tp_id = plan_item["test_point_id"]
        tp = tp_map.get(tp_id, {})
        cov_items = plan_item.get("coverage_items", [])
        sym = sym_map.get(tp.get("symbol_ref"))

        for idx, ci in enumerate(cov_items, start=1):
            ci_desc_lower = ci["description"].lower()
            is_negative = (
                ci["technique"] == "error_guessing"
                or any(k in ci_desc_lower for k in ("invalid", "below-min", "above-max", "falsified", "interrupted", "exception"))
            )
            target_label = sym["name"] if sym else module_name

            if is_negative:
                condition_clause = f"when invalid/edge input or boundary violation is passed to {target_label}"
                expected_clause = f"rejects or handles fault safely for {tp.get('title', target_label)}"
            else:
                condition_clause = f"when valid input is provided to {target_label}"
                expected_clause = f"succeeds and satisfies {tp.get('title', target_label)}"

            # Strictly formatted for Harness DB validation: "[Module]: <Expected> when <Condition>"
            clean_tp_title = re.sub(r"^\[[^\]]+\]\s*", "", tp.get("title", target_label))
            harness_title = f"[{module_name}]: {clean_tp_title} ({ci['technique']} #{idx}) {condition_clause}"

            sample_data = _synthesize_test_data(sym, is_negative=is_negative)

            raw_cases.append({
                "id": str(len(raw_cases) + 1),
                "title": harness_title,
                "preconditions": analysis.get("preconditions") or [f"{module_name} test environment is initialized"],
                "steps": [
                    f"Given {module_name} instance / context is ready with test data ({sample_data})",
                    f"When invoking {target_label} under condition: {ci['description']}",
                    f"Then verify {expected_clause}",
                ],
                "test_data": sample_data,
                "expected_results": [expected_clause],
                "acceptance_criteria": analysis.get("acceptance_criteria", []),
                "priority": tp.get("priority", "P1"),
                "automation": "Auto",
                "requirement_refs": tp.get("requirement_refs", []),
                "test_point_refs": [tp_id],
                "covered_items": [ci["id"]],
                "symbol_ref": tp.get("symbol_ref"),
                "is_negative": is_negative,
                "rationale": f"Covers {ci['id']} ({ci['technique']}) for {tp_id}",
            })

    return normalize_case_ids(raw_cases)


def normalize_case_ids(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assign deterministic immutable IDs: TC-TP001-01, TC-TP001-02 (D-036 Stage 4)."""
    counters: Dict[str, int] = {}
    normalized: List[Dict[str, Any]] = []
    for c in cases or []:
        refs = c.get("test_point_refs") or []
        code = short_code(refs[0]) if refs else "GEN"
        counters[code] = counters.get(code, 0) + 1
        normalized.append({**c, "id": f"TC-{code}-{counters[code]:02d}"})
    return normalized


def _synthesize_test_data(sym: Optional[Dict[str, Any]], is_negative: bool = False) -> str:
    if not sym or not sym.get("params"):
        return "invalidPayload = null" if is_negative else "validPayload = { id: '1' }"
    parts = []
    for p in sym["params"]:
        p_type = p.get("type", "any").lower()
        if "string" in p_type:
            val = TYPE_MUTATIONS["string"]["empty"] if is_negative else TYPE_MUTATIONS["string"]["valid"]
        elif "number" in p_type:
            val = TYPE_MUTATIONS["number"]["negative"] if is_negative else TYPE_MUTATIONS["number"]["valid"]
        elif "boolean" in p_type:
            val = TYPE_MUTATIONS["boolean"]["falsy"] if is_negative else TYPE_MUTATIONS["boolean"]["valid"]
        elif "[]" in p_type or "array" in p_type:
            val = TYPE_MUTATIONS["array"]["empty"] if is_negative else TYPE_MUTATIONS["array"]["valid"]
        else:
            val = TYPE_MUTATIONS["object"]["nullish"] if is_negative else TYPE_MUTATIONS["object"]["valid"]
        parts.append(f"{p['name']}={val}")
    return ", ".join(parts)


def _derive_expected_assertion(
    tc: Dict[str, Any],
    sym: Optional[Dict[str, Any]],
) -> Tuple[Optional[str], Any]:
    """Derive deterministic expectation kind and target value from AC/testcase data.

    Returns (kind, value) where kind is in:
      'throws', 'null', 'boolean', 'number', 'string', 'status', 'object_prop', 'array', 'falsy'
      or (None, None) if no concrete expectation can be derived.
    """
    is_neg = tc.get("is_negative", False)
    ac_list = tc.get("acceptance_criteria") or []
    exp_list = tc.get("expected_results") or []
    steps = tc.get("steps") or []
    test_data = str(tc.get("test_data") or "")
    all_text = " ".join([str(x) for x in ac_list + exp_list + steps])

    # 1. Negative scenario
    if is_neg:
        if sym and sym.get("has_throws"):
            return ("throws", None)
        if "null" in test_data.lower() or "null" in all_text.lower():
            return ("null", None)
        if "false" in test_data.lower() or "false" in all_text.lower():
            return ("boolean", False)
        status_m = re.search(r"\b(400|401|403|404|422|500)\b", all_text)
        if status_m:
            return ("status", int(status_m.group(1)))
        if any(w in all_text.lower() for w in ("fail", "error", "reject", "invalid", "violation")):
            return ("falsy", None)

    # 2. Positive scenario with concrete values in AC / expected results / test data
    status_m = re.search(r"\b(?:status|code)\s*(?:is|==|:)?\s*(\d{3})\b", all_text, re.I)
    if status_m:
        return ("status", int(status_m.group(1)))

    if re.search(r"\b(?:returns?|equals?|is|==)\s*true\b", all_text, re.I):
        return ("boolean", True)
    if re.search(r"\b(?:returns?|equals?|is|==)\s*false\b", all_text, re.I):
        return ("boolean", False)

    num_m = re.search(r"\b(?:returns?|equals?|==)\s*(-?\d+)\b", all_text, re.I)
    if num_m:
        return ("number", int(num_m.group(1)))

    str_m = re.search(r"\b(?:returns?|equals?|==)\s*['\"]([^'\"]+)['\"]", all_text, re.I)
    if str_m:
        return ("string", str_m.group(1))

    kv_m = re.search(r"([a-zA-Z_]\w*)\s*[:=]\s*['\"]([^'\"]+)['\"]", test_data)
    if kv_m and kv_m.group(1) not in ("module", "target"):
        return ("object_prop", (kv_m.group(1), kv_m.group(2)))

    # 3. Type-based derivation from AST return_type
    if sym:
        ret_type = (sym.get("return_type") or "").strip().lower()
        if ret_type in ("boolean", "bool"):
            return ("boolean", True)
        if "[]" in ret_type or "array" in ret_type or "list" in ret_type:
            return ("array", None)

    return (None, None)


def render_unit_test_file(
    code_ctx: Dict[str, Any],
    test_cases: List[Dict[str, Any]],
    output_path: Path,
) -> str:
    """Generate an executable TypeScript (Jest/Vitest/Angular) or Python (Pytest) unit test file."""
    lang = code_ctx.get("language", "typescript")
    if lang == "python":
        return _render_pytest_file(code_ctx, test_cases, output_path)
    return _render_ts_spec_file(code_ctx, test_cases, output_path)


def _render_ts_spec_file(
    code_ctx: Dict[str, Any],
    test_cases: List[Dict[str, Any]],
    output_path: Path,
) -> str:
    src_path = Path(code_ctx["file_path"]).resolve()
    out_dir = output_path.resolve().parent
    try:
        rel_import = os.path.relpath(src_path, out_dir)
    except ValueError:
        rel_import = src_path.name
    rel_import = re.sub(r"\.(ts|tsx|js)$", "", rel_import).replace("\\", "/")
    if not rel_import.startswith("."):
        rel_import = f"./{rel_import}"

    framework = code_ctx.get("framework", "jest")
    module_name = code_ctx.get("module_name", "TargetModule")
    classes = code_ctx.get("classes", [])
    symbols = code_ctx.get("symbols", [])
    is_ng_comp = code_ctx.get("is_angular_component", False)
    is_ng_svc = code_ctx.get("is_angular_service", False)

    exported_names = list(dict.fromkeys(
        classes + [s["method_name"] for s in symbols if s.get("kind") == "function"]
    ))
    import_stmt = (
        f"import {{ {', '.join(exported_names)} }} from '{rel_import}';"
        if exported_names
        else f"// import * as target from '{rel_import}';"
    )

    lines: List[str] = [
        "/**",
        f" * Auto-generated Unit Test Suite by Paseo QC Test Generator (ISTQB D-036 5-Stage Pipeline)",
        f" * Source Under Test : {src_path.name}",
        f" * Total Test Cases  : {len(test_cases)}",
        " */",
    ]
    if framework == "vitest":
        lines.append("import { describe, it, test, expect, beforeEach, vi } from 'vitest';")
    if is_ng_comp or is_ng_svc:
        lines.append("import { TestBed } from '@angular/core/testing';")
    lines.append(import_stmt)
    lines.append("")
    lines.append(f"describe('{module_name}', () => {{")

    if classes:
        main_cls = classes[0]
        lines.append(f"  let sut: {main_cls};")
        lines.append("")
        lines.append("  beforeEach(() => {")
        if is_ng_comp or is_ng_svc:
            lines.append("    TestBed.configureTestingModule({")
            lines.append(f"      providers: [{main_cls}],")
            lines.append("    });")
            lines.append(f"    sut = TestBed.inject({main_cls});")
        else:
            lines.append(f"    sut = new {main_cls}();")
        lines.append("  });")
        lines.append("")

    # Group cases by TestPoint
    by_tp: Dict[str, List[Dict[str, Any]]] = {}
    for tc in test_cases:
        tp_id = (tc.get("test_point_refs") or ["TP-GEN"])[0]
        by_tp.setdefault(tp_id, []).append(tc)

    sym_map = {s["method_name"]: s for s in symbols}

    for tp_id, cases in by_tp.items():
        lines.append(f"  describe('{tp_id}', () => {{")
        for tc in cases:
            tc_id = tc["id"]
            reqs = ",".join(tc.get("requirement_refs") or [])
            cis = ",".join(tc.get("covered_items") or [])
            safe_title = tc["title"].replace("'", "\\'")
            sym = sym_map.get(tc.get("symbol_ref"))
            is_neg = tc.get("is_negative", False)

            kind, val = _derive_expected_assertion(tc, sym)

            if kind is None:
                lines.append(f"    test.todo('[{tc_id}] {safe_title} ({reqs} | {cis})');")
                lines.append("")
                continue

            lines.append(f"    it('[{tc_id}] {safe_title} ({reqs} | {cis})', () => {{")
            lines.append(f"      // Arrange: {tc['steps'][0]}")
            if sym:
                call_args = _build_ts_call_args(sym, is_negative=is_neg)
                invoke_expr = (
                    f"sut.{sym['method_name']}({call_args})"
                    if sym.get("class_name") and not sym["kind"].startswith("signal")
                    else (
                        f"sut.{sym['method_name']}()"
                        if sym.get("class_name") and sym["kind"].startswith("signal")
                        else f"{sym['method_name']}({call_args})"
                    )
                )
                lines.append(f"      // Act: {tc['steps'][1]}")
                lines.append(f"      // Assert: {tc['steps'][2]}")
                if kind == "throws":
                    lines.append(f"      expect(() => {invoke_expr}).toThrow();")
                else:
                    lines.append(f"      const result = {invoke_expr};")
                    if kind == "null":
                        lines.append("      expect(result).toBeNull();")
                    elif kind == "boolean":
                        lines.append(f"      expect(result).toBe({'true' if val else 'false'});")
                    elif kind == "number":
                        lines.append(f"      expect(result).toBe({val});")
                    elif kind == "status":
                        lines.append(f"      expect((result as any)?.status ?? result).toBe({val});")
                    elif kind == "string":
                        lines.append(f"      expect(result).toBe('{val}');")
                    elif kind == "object_prop":
                        prop, pval = val
                        lines.append(f"      expect(result).toMatchObject({{ {prop}: '{pval}' }});")
                    elif kind == "array":
                        lines.append("      expect(Array.isArray(result)).toBe(true);")
                    elif kind == "falsy":
                        lines.append("      expect(result).toBeFalsy();")
            else:
                lines.append(f"      // Act & Assert: {tc['steps'][2]}")
                if kind == "boolean":
                    lines.append(f"      expect(Boolean(sut)).toBe({'true' if val else 'false'});")
                else:
                    lines.append("      expect(sut).not.toBeNull();")
            lines.append("    });")
            lines.append("")
        lines.append("  });")

    lines.append("});")
    lines.append("")
    return "\n".join(lines)


def _build_ts_call_args(sym: Dict[str, Any], is_negative: bool = False) -> str:
    args: List[str] = []
    for p in sym.get("params", []):
        p_type = p.get("type", "any").lower()
        if "string" in p_type:
            args.append("''" if is_negative else "'test-value'")
        elif "number" in p_type:
            args.append("-1" if is_negative else "1")
        elif "boolean" in p_type:
            args.append("false" if is_negative else "true")
        elif "[]" in p_type or "array" in p_type:
            args.append("[]" if is_negative else "[{ id: '1' } as any]")
        else:
            args.append("null as any" if is_negative else "{} as any")
    return ", ".join(args)


def _render_pytest_file(
    code_ctx: Dict[str, Any],
    test_cases: List[Dict[str, Any]],
    output_path: Path,
) -> str:
    module_name = code_ctx.get("module_name", "module")
    symbols = {s["method_name"]: s for s in code_ctx.get("symbols", [])}
    lines = [
        f'"""Auto-generated Pytest Suite for {module_name} (ISTQB D-036 Pipeline)."""',
        "import pytest",
        "",
    ]
    for tc in test_cases:
        fn_slug = re.sub(r"[^a-z0-9_]", "_", tc["id"].lower())
        sym = symbols.get(tc.get("symbol_ref"))
        kind, val = _derive_expected_assertion(tc, sym)

        lines.append(f"def test_{fn_slug}():")
        lines.append(f'    """{tc["title"]}"""')
        for step in tc.get("steps", []):
            lines.append(f"    # {step}")

        if kind is None:
            lines.append('    pytest.fail("Concrete expectation required: could not derive expected value from AC")')
        elif kind == "throws":
            lines.append("    with pytest.raises(Exception):")
            invoke_expr = f"{sym['method_name']}()" if sym else "raise RuntimeError('fault')"
            lines.append(f"        {invoke_expr}")
        else:
            invoke_expr = f"{sym['method_name']}()" if sym else "None"
            lines.append(f"    result = {invoke_expr}")
            if kind == "null":
                lines.append("    assert result is None")
            elif kind == "boolean":
                lines.append(f"    assert result is {'True' if val else 'False'}")
            elif kind == "number":
                lines.append(f"    assert result == {val}")
            elif kind == "status":
                lines.append(f"    assert getattr(result, 'status', result) == {val}")
            elif kind == "string":
                lines.append(f"    assert result == {repr(val)}")
            elif kind == "object_prop":
                prop, pval = val
                lines.append(f"    assert (result.get({repr(prop)}) if isinstance(result, dict) else getattr(result, {repr(prop)}, None)) == {repr(pval)}")
            elif kind == "array":
                lines.append("    assert isinstance(result, list)")
            elif kind == "falsy":
                lines.append("    assert not result")
        lines.append("")
    return "\n".join(lines)


# ---------- Stage 5: Deterministic Coverage Check (D-036 Stage 5, 0% LLM) ----------

def build_coverage_report(
    analysis: Dict[str, Any],
    test_cases: List[Dict[str, Any]],
    test_point_set: Dict[str, Any],
    test_design_plan: Dict[str, Any],
    code_ctx: Dict[str, Any],
) -> Dict[str, Any]:
    """Deterministic set-based coverage verification and quality check (0% LLM self-grading)."""
    req_ids = {r["id"] for r in analysis.get("functional_requirements", []) if r.get("id")}
    test_points = test_point_set.get("test_points", [])
    tp_ids = {tp["id"] for tp in test_points if tp.get("id")}
    tp_reqs = {tp["id"]: set(tp.get("requirement_refs") or []) for tp in test_points if tp.get("id")}

    all_coverage_items = {
        ci["id"]
        for item in test_design_plan.get("items", [])
        for ci in item.get("coverage_items", [])
        if ci.get("id")
    }
    all_symbols = {s["method_name"] for s in code_ctx.get("symbols", []) if s.get("method_name")}

    covered_points: Set[str] = set()
    declared_items: Set[str] = set()
    covered_reqs: Set[str] = set()
    covered_symbols: Set[str] = set()
    invalid_tp_refs: Set[str] = set()
    invalid_req_refs: Set[str] = set()

    for tc in test_cases:
        if tc.get("symbol_ref"):
            covered_symbols.add(tc["symbol_ref"])
        for ref in tc.get("test_point_refs") or []:
            if ref in tp_ids:
                covered_points.add(ref)
                covered_reqs |= tp_reqs.get(ref, set())
            else:
                invalid_tp_refs.add(ref)
        for ci_ref in tc.get("covered_items") or []:
            declared_items.add(ci_ref)
        for r_ref in tc.get("requirement_refs") or []:
            if r_ref in req_ids:
                covered_reqs.add(r_ref)
            else:
                invalid_req_refs.add(r_ref)

    duplicates: List[Dict[str, Any]] = []
    for i in range(len(test_cases)):
        for j in range(i + 1, len(test_cases)):
            sim = case_similarity(test_cases[i], test_cases[j])
            if sim >= DUPLICATE_SIMILARITY_THRESHOLD:
                duplicates.append({
                    "case_a": test_cases[i]["id"],
                    "case_b": test_cases[j]["id"],
                    "similarity": round(sim, 2),
                })

    quality_issues: List[str] = []
    for tc in test_cases:
        cid = tc.get("id", "UNKNOWN")
        if not (tc.get("title") or "").strip():
            quality_issues.append(f"{cid} missing title")
        if not tc.get("steps"):
            quality_issues.append(f"{cid} missing steps")
        if not tc.get("expected_results"):
            quality_issues.append(f"{cid} missing expected_results")

    uncovered_points = sorted(tp_ids - covered_points)
    uncovered_cis = sorted(all_coverage_items - declared_items)
    uncovered_reqs = sorted(req_ids - covered_reqs)
    uncovered_symbols = sorted(all_symbols - covered_symbols)

    if uncovered_points:
        quality_issues.append("Uncovered TestPoints: " + ", ".join(uncovered_points))
    if uncovered_cis:
        quality_issues.append("Uncovered CoverageItems: " + ", ".join(uncovered_cis))

    req_cov_pct = round(len(covered_reqs) / max(1, len(req_ids)) * 100, 1)
    ci_cov_pct = round(len(all_coverage_items & declared_items) / max(1, len(all_coverage_items)) * 100, 1)
    sym_cov_pct = round(len(covered_symbols) / max(1, len(all_symbols)) * 100, 1) if all_symbols else 100.0

    return {
        "total_cases": len(test_cases),
        "total_test_points": len(tp_ids),
        "total_coverage_items": len(all_coverage_items),
        "requirement_coverage_pct": req_cov_pct,
        "coverage_item_pct": ci_cov_pct,
        "symbol_coverage_pct": sym_cov_pct,
        "covered_requirements": sorted(covered_reqs),
        "uncovered_requirements": uncovered_reqs,
        "covered_test_points": sorted(covered_points),
        "uncovered_test_points": uncovered_points,
        "uncovered_coverage_items": uncovered_cis,
        "covered_symbols": sorted(covered_symbols),
        "uncovered_symbols": uncovered_symbols,
        "dimension_summary": dict(sorted(Counter(tp.get("dimension", "function") for tp in test_points).items())),
        "priority_summary": dict(sorted(Counter(tc.get("priority", "P1") for tc in test_cases).items())),
        "duplicates": duplicates,
        "quality_issues": quality_issues,
    }


# ---------- Harness Integration & Automated Test Execution ----------

def sync_cases_to_harness(
    test_cases: List[Dict[str, Any]],
    parent_task_id: Optional[int],
    verify_cmd: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Register generated TestCases onto Harness DB linked to parent_task_id."""
    from tools.harness_manager import HarnessManager
    mgr = HarnessManager()
    synced: List[Dict[str, Any]] = []

    for tc in test_cases:
        desc_lines = [
            f"Trace ID: {tc['id']} | Req: {', '.join(tc.get('requirement_refs', []))} | CI: {', '.join(tc.get('covered_items', []))}",
            "Steps:",
            *[f"  - {s}" for s in tc.get("steps", [])],
            f"Test Data: {tc.get('test_data', '')}",
            f"Expected: {'; '.join(tc.get('expected_results', []))}",
        ]
        if verify_cmd:
            desc_lines.append(f"Verify Command: {verify_cmd}")

        validate_work_item(
            assigned_to_profile="QC",
            created_by_profile="QC",
        )
        res = mgr.add_work_item(
            wi_type="Testcase",
            title=tc["title"],
            description="\n".join(desc_lines),
            priority=tc.get("priority", "P1"),
            parent_id=parent_task_id,
            source="bot",
            created_by_profile="QC",
            assigned_to_profile="QC",
        )
        synced.append({"tc_id": tc["id"], "harness_id": res.get("id"), "title": tc["title"]})
    return synced


def run_verify_command(cmd: str, cwd: Path) -> Dict[str, Any]:
    """Execute unit test command deterministically and capture pass/fail + output."""
    start_time = datetime.now()
    argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=180,
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    combined_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return {
        "passed": proc.returncode == 0,
        "exit_code": proc.returncode,
        "elapsed_seconds": round(elapsed, 2),
        "command": cmd if isinstance(cmd, str) else " ".join(cmd),
        "cwd": str(cwd),
        "output_tail": combined_out.strip()[-2000:],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Paseo QC Unit Test Case & Spec Generator (5-Stage ISTQB Pipeline)"
    )
    parser.add_argument("--source", required=True, help="Path to source code file under test (.ts/.py)")
    parser.add_argument("--spec", default=None, help="Path to Markdown spec file or inline requirement text")
    parser.add_argument("--task-id", type=int, default=None, help="Harness Task/Story ID to pull AC from and link Testcases to")
    parser.add_argument("--out-spec", default=None, help="Output path for generated unit test file (*.spec.ts / test_*.py)")
    parser.add_argument("--out-json", default=None, help="Output path for full 5-stage JSON artifact")
    parser.add_argument("--sync-harness", action="store_true", help="Push generated Testcase items into Harness DB")
    parser.add_argument("--run", action="store_true", help="Execute the unit test runner after generating")
    parser.add_argument("--verify-cmd", default=None, help="Custom test runner command to execute when --run is set")
    parser.add_argument("--cwd", default=None, help="Working directory for test runner execution (defaults to project root)")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    # 1. Load Spec Text from file, Harness Task ID, or inline string
    spec_text = ""
    if args.spec:
        spec_candidate = Path(args.spec)
        if spec_candidate.exists() and spec_candidate.is_file():
            spec_text = spec_candidate.read_text(encoding="utf-8", errors="replace")
        else:
            spec_text = args.spec

    if args.task_id is not None and not spec_text:
        try:
            from tools.harness_manager import HarnessManager
            item = HarnessManager().get_work_item(args.task_id)
            if item:
                spec_text = f"# {item.get('title', '')}\n{item.get('description', '')}\n## Acceptance Criteria\n{item.get('acceptance_criteria', '')}"
        except Exception as e:
            print(f"Warning: Could not load task #{args.task_id} from Harness: {e}", file=sys.stderr)

    # Execute 5-Stage Pipeline
    code_ctx = analyze_source_file(source_path)
    analysis = parse_spec_content(spec_text, module_hint=code_ctx.get("module_name", source_path.stem))
    tp_set = generate_test_points(analysis, code_ctx)
    design_plan = build_test_design_plan(tp_set["test_points"])
    test_cases = generate_test_cases(analysis, tp_set, design_plan, code_ctx)
    coverage_report = build_coverage_report(analysis, test_cases, tp_set, design_plan, code_ctx)

    # Optional: Write executable unit test file
    generated_spec_file = None
    if args.out_spec:
        out_spec_path = Path(args.out_spec).resolve()
        out_spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_code = render_unit_test_file(code_ctx, test_cases, out_spec_path)
        out_spec_path.write_text(spec_code, encoding="utf-8")
        generated_spec_file = str(out_spec_path)

    # Optional: Sync Testcases to Harness DB
    synced_items = []
    if args.sync_harness:
        synced_items = sync_cases_to_harness(test_cases, parent_task_id=args.task_id, verify_cmd=args.verify_cmd)

    # Optional: Run unit tests
    run_result = None
    if args.run:
        cmd = args.verify_cmd
        if not cmd:
            target_test = generated_spec_file or str(source_path)
            if code_ctx.get("framework") == "vitest":
                cmd = f"npx vitest run {target_test}"
            elif code_ctx.get("language") == "python":
                cmd = f"pytest {target_test}"
            else:
                cmd = f"npx jest {target_test}"
        if args.cwd:
            runner_cwd = Path(args.cwd).resolve()
        else:
            runner_cwd = source_path.parent
            for p in [source_path.parent, *source_path.parents]:
                if (p / "package.json").exists() or (p / "pyproject.toml").exists() or (p / "nx.json").exists():
                    runner_cwd = p
                    break
        run_result = run_verify_command(cmd, cwd=runner_cwd)

    artifact = {
        "stage1_requirement_analysis": analysis,
        "stage1_code_context": code_ctx,
        "stage2_test_point_set": tp_set,
        "stage3_test_design_plan": design_plan,
        "stage4_test_cases": test_cases,
        "stage5_coverage_report": coverage_report,
        "generated_spec_file": generated_spec_file,
        "harness_synced_testcases": synced_items,
        "execution_result": run_result,
    }

    if args.out_json:
        out_json_path = Path(args.out_json).resolve()
        out_json_path.parent.mkdir(parents=True, exist_ok=True)
        out_json_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary Console Output
    print("=== PASEO QC 5-STAGE TEST GENERATION SUMMARY ===")
    print(f"• Source Analyzed       : {source_path.name} ({len(code_ctx.get('symbols', []))} symbols, framework: {code_ctx.get('framework')})")
    print(f"• Stage 1 Requirements  : {len(analysis['functional_requirements'])} REQs extracted")
    print(f"• Stage 2 Test Points   : {len(tp_set['test_points'])} TPs accepted ({len(tp_set['dropped_test_points'])} dropped)")
    print(f"• Stage 3 Design Plan   : {coverage_report['total_coverage_items']} Coverage Items ({design_plan['technique_summary']})")
    print(f"• Stage 4 Test Cases    : {coverage_report['total_cases']} Traceable TestCases generated")
    print(f"• Stage 5 Coverage Check: REQ={coverage_report['requirement_coverage_pct']}% | CI={coverage_report['coverage_item_pct']}% | Symbols={coverage_report['symbol_coverage_pct']}%")
    if generated_spec_file:
        print(f"• Generated Spec File   : {generated_spec_file}")
    if synced_items:
        print(f"• Synced to Harness DB  : {len(synced_items)} Testcase work items created")
    if run_result:
        verdict = "PASSED ✓" if run_result["passed"] else "FAILED ✗"
        print(f"• Test Runner Execution : {verdict} ({run_result['elapsed_seconds']}s) [{run_result['command']}]")

if __name__ == "__main__":
    main()
