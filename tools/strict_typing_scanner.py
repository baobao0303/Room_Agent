#!/usr/bin/env python3
"""
tools/strict_typing_scanner.py - Scanner & Guard for Strict Typing and Anti-Sloppy Fallbacks.

Enforces:
1. Zero `any` rule: Flags `: any`, `as any`, `<any>`, `Array<any>`, etc.
2. Anti-Sloppy Fallback `||` rule: Flags chaining `||` on object property access (e.g. `a.b || c.d` instead of `??`).
3. Safe pattern allowance: Allows `??`, ternary operator `cond ? a : b`, and `unknown` with type-narrowing.
4. Path exclusions: Skips `node_modules/`, `dist/`, `**/auto-gen/**`, `*.spec.ts`, `*.d.ts`.
"""

from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

EXCLUDED_PATH_GLOBS = [
    "*/node_modules/*",
    "node_modules/*",
    "*/dist/*",
    "dist/*",
    "*/auto-gen/*",
    "*auto-gen*",
    "*.spec.ts",
    "*.spec.tsx",
    "*.spec.js",
    "*.test.ts",
    "*.test.tsx",
    "*.test.js",
    "*.d.ts",
]

# Patterns for 'any' violation (mutually exclusive)
ANY_PATTERNS = [
    (re.compile(r":\s*any\b"), "Explicit ': any' type annotation is prohibited"),
    (re.compile(r"\bas\s+any\b"), "Type assertion 'as any' is prohibited"),
    (re.compile(r"(?<![a-zA-Z0-9_$])<\s*any\s*>"), "Type cast '<any>' is prohibited"),
    (re.compile(r"\b(Array|Promise|Observable|Set|List)\s*<\s*any\s*>"), "Container type '<any>' is prohibited"),
    (re.compile(r"\b(Record|Map)\s*<\s*[^,]+,\s*any\s*>"), "Key-value container type with 'any' value is prohibited"),
]

# Pattern for sloppy fallback with || on object property access:
# Matches: object.property || fallback or a.b || c.d
# Excludes boolean test contexts like if (... || ...), while (... || ...)
PROPERTY_FALLBACK_PATTERN = re.compile(
    r"""(?<!if\s)
        (?<!while\s)
        (?<!&&\s)
        \b([a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*|\?\.[a-zA-Z_$][a-zA-Z0-9_$]*)+)
        \s*\|\|\s*
        ([^;\n,\)]+)""",
    re.VERBOSE
)

@dataclass
class TypingViolation:
    file_path: str
    line_number: int
    rule: str
    snippet: str
    message: str

def is_path_excluded(file_path: str | Path) -> bool:
    """Check if the file matches any exclusion glob."""
    norm_path = str(file_path).replace("\\", "/")
    for pattern in EXCLUDED_PATH_GLOBS:
        if fnmatch.fnmatch(norm_path, pattern) or fnmatch.fnmatch(os.path.basename(norm_path), pattern):
            return True
        if "auto-gen" in norm_path.split("/"):
            return True
        if "node_modules" in norm_path.split("/"):
            return True
        if "dist" in norm_path.split("/"):
            return True
    return False

def strip_comments_and_strings(code: str) -> str:
    """
    Strip single-line comments, multi-line comments, and string literals
    to prevent false positives, while preserving line numbers with newline characters.
    """
    def replacer(match: re.Match) -> str:
        s = match.group(0)
        if s.startswith('/') or s.startswith('"') or s.startswith("'") or s.startswith('`'):
            # Preserve newlines inside comments/strings to keep line numbers intact
            return '\n' * s.count('\n')
        return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"|`(?:\\.|[^\\`])*`',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, code)

def is_inside_conditional_statement(line: str) -> bool:
    """Detect if the line is an if/while/filter boolean expression."""
    stripped = line.strip()
    return bool(re.match(r"^(if|while|for|switch)\s*\(", stripped))

def check_unknown_safety(line: str, code_block: str, line_no: int) -> bool:
    """
    Check if 'unknown' is used safely at boundary with type-narrowing (e.g. instanceof, typeof).
    Returns True if safe, False if bare unsafely used.
    """
    # Safe boundary declarations
    if re.search(r"\b(catch|function|constructor|parse|validate|decode)\b.*:\s*unknown\b", line):
        return True
    # Safe type guard predicates
    if re.search(r":\s*[a-zA-Z0-9_$]+\s+is\s+", line):
        return True
    # Safe narrowing presence in subsequent lines
    lines = code_block.splitlines()
    window = lines[line_no - 1 : min(len(lines), line_no + 10)]
    for w in window:
        if any(keyword in w for keyword in ["typeof", "instanceof", "isError", "hasProperty", "asserts", "as unknown as"]):
            return True
    return False

def scan_typescript_code(code: str, file_path: str = "") -> List[TypingViolation]:
    """Scan TypeScript code string and return detected violations."""
    if file_path and is_path_excluded(file_path):
        return []

    violations: List[TypingViolation] = []
    lines = code.splitlines()
    stripped_code = strip_comments_and_strings(code)
    stripped_lines = stripped_code.splitlines()

    for idx, (raw_line, clean_line) in enumerate(zip(lines, stripped_lines), start=1):
        if not clean_line.strip():
            continue

        # 1. Check for 'any' violations
        for pattern, msg in ANY_PATTERNS:
            match = pattern.search(clean_line)
            if match:
                violations.append(
                    TypingViolation(
                        file_path=file_path,
                        line_number=idx,
                        rule="zero-any",
                        snippet=raw_line.strip(),
                        message=msg
                    )
                )

        # 2. Check for sloppy fallback '||' on object property access
        if not is_inside_conditional_statement(clean_line):
            fallback_match = PROPERTY_FALLBACK_PATTERN.search(clean_line)
            if fallback_match:
                # Ensure it's not a ternary statement condition: 'cond ? a.b : c.d'
                # or a logical OR in return boolean
                left_side = fallback_match.group(1).strip()
                right_side = fallback_match.group(2).strip()

                # If right_side starts with '?' it might be part of ternary
                if not right_side.startswith("?"):
                    violations.append(
                        TypingViolation(
                            file_path=file_path,
                            line_number=idx,
                            rule="anti-sloppy-fallback",
                            snippet=raw_line.strip(),
                            message=(
                                f"Sloppy fallback '{left_side} || ...' on object property detected. "
                                f"Use nullish coalescing '??' or explicit mapping instead."
                            )
                        )
                    )

    return violations

def scan_file(file_path: Path | str) -> List[TypingViolation]:
    """Scan a single file if not excluded."""
    path = Path(file_path)
    if is_path_excluded(path):
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return scan_typescript_code(content, file_path=str(path))
    except Exception as e:
        return [
            TypingViolation(
                file_path=str(path),
                line_number=1,
                rule="read-error",
                snippet="",
                message=f"Failed to read file: {e}"
            )
        ]

def main() -> int:
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 tools/strict_typing_scanner.py <file_or_dir> [more_files...]")
        return 0
    total_violations: List[TypingViolation] = []
    for target in sys.argv[1:]:
        p = Path(target)
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in (".ts", ".tsx", ".js", ".jsx", ".py"):
                    total_violations.extend(scan_file(f))
        elif p.is_file():
            total_violations.extend(scan_file(p))
    if total_violations:
        print(f"❌ Found {len(total_violations)} strict typing violation(s):")
        for v in total_violations:
            print(f"  {v.file_path}:{v.line_number} [{v.rule}]: {v.message}")
            if v.snippet:
                print(f"    Snippet: {v.snippet}")
        return 1
    print("✅ Strict typing & anti-sloppy fallback check passed: 0 violations.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

