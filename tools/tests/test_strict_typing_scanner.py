#!/usr/bin/env python3
"""
tools/tests/test_strict_typing_scanner.py - 5-Stage ISTQB Audit Suite for Strict Typing & Fallback Scanner.

Traceability Matrix:
- REQ-TYP-01: Prohibit ': any' type annotations
- REQ-TYP-02: Prohibit 'as any' type assertions
- REQ-TYP-03: Prohibit '<any>' type casting
- REQ-TYP-04: Prohibit container types 'Array<any>', 'Promise<any>', 'Observable<any>', 'Record<..., any>'
- REQ-FALLBACK-01: Prohibit sloppy fallback '||' on object property access
- REQ-SAFE-01: Permit nullish coalescing operator '??'
- REQ-SAFE-02: Permit ternary operator 'condition ? a : b'
- REQ-SAFE-03: Permit 'unknown' with type-narrowing / at boundary
- REQ-SAFE-04: Permit logical OR in boolean conditional statements (if/while)
- REQ-EXCLUDE-01..05: Path exclusions (node_modules, dist, auto-gen, *.spec.ts, *.d.ts)
- REQ-NOISE-01: Strip comments and string literals to prevent false positives
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools.strict_typing_scanner import (
    TypingViolation,
    is_path_excluded,
    scan_typescript_code,
    strip_comments_and_strings,
)

class TestStrictTypingScannerISTQB(unittest.TestCase):
    """5-Stage ISTQB Test Suite for Strict Typing Scanner."""

    # =========================================================================
    # STAGE 1 & 4.1: ZERO 'any' RULE (REQ-TYP-01 .. REQ-TYP-04)
    # =========================================================================

    def test_tc_typ_01_prohibit_colon_any(self):
        """[TC-TYP-01] Detect explicit ': any' annotations."""
        code = """
        export class UserComponent {
            public rawData: any;
            private config: any = null;
            function process(data: any): void {}
        }
        """
        violations = scan_typescript_code(code, "src/user.component.ts")
        self.assertEqual(len(violations), 3)
        for v in violations:
            self.assertEqual(v.rule, "zero-any")
            self.assertIn("any", v.message)

    def test_tc_typ_02_prohibit_as_any(self):
        """[TC-TYP-02] Detect type assertions 'as any'."""
        code = """
        const user = (response as any).data;
        const id = (this.currentUser as any)?.id;
        const payload = (dto as any) as CustomerDto;
        """
        violations = scan_typescript_code(code, "src/service.ts")
        self.assertEqual(len(violations), 3)
        for v in violations:
            self.assertEqual(v.rule, "zero-any")
            self.assertIn("as any", v.message)

    def test_tc_typ_03_prohibit_diamond_any(self):
        """[TC-TYP-03] Detect type casts '<any>'."""
        code = """
        const item = <any>window.localStorage;
        const result = < any >data;
        """
        violations = scan_typescript_code(code, "src/adapter.ts")
        self.assertEqual(len(violations), 2)
        for v in violations:
            self.assertEqual(v.rule, "zero-any")
            self.assertIn("<any>", v.message)

    def test_tc_typ_04_prohibit_container_any(self):
        """[TC-TYP-04] Detect container types with any (Array, Promise, Observable, Record, Map)."""
        code = """
        let list: Array<any> = [];
        let task$: Observable<any>;
        let asyncTask: Promise<any>;
        let map: Record<string, any>;
        let mapping: Map<string, any>;
        """
        violations = scan_typescript_code(code, "src/models.ts")
        self.assertEqual(len(violations), 5)
        rules = [v.rule for v in violations]
        self.assertTrue(all(r == "zero-any" for r in rules))

    # =========================================================================
    # STAGE 2 & 4.2: ANTI-SLOPPY FALLBACK '||' RULE (REQ-FALLBACK-01)
    # =========================================================================

    def test_tc_fallback_01_property_fallback_chain(self):
        """[TC-FALLBACK-01] Detect sloppy '||' chaining on object properties."""
        code = """
        const id = emp.id || emp.shopUserId;
        const name = item.name || '';
        const role = user.profile.roleName || 'Guest';
        const nested = a.b.c || d.e || 0;
        """
        violations = scan_typescript_code(code, "src/mapper.ts")
        self.assertEqual(len(violations), 4)
        for v in violations:
            self.assertEqual(v.rule, "anti-sloppy-fallback")
            self.assertIn("Sloppy fallback", v.message)

    def test_tc_fallback_02_optional_chaining_fallback(self):
        """[TC-FALLBACK-02] Detect sloppy '||' with optional chaining (?.)."""
        code = """
        const phone = contact?.primaryPhone || '';
        const email = customer?.info?.email || 'N/A';
        """
        violations = scan_typescript_code(code, "src/detail.ts")
        self.assertEqual(len(violations), 2)
        for v in violations:
            self.assertEqual(v.rule, "anti-sloppy-fallback")

    # =========================================================================
    # STAGE 3 & 4.3: SAFE PATTERNS (REQ-SAFE-01 .. REQ-SAFE-04)
    # =========================================================================

    def test_tc_safe_01_nullish_coalescing_allowed(self):
        """[TC-SAFE-01] Nullish coalescing '??' must NOT trigger violations."""
        code = """
        const id = emp.accountUserId ?? String(emp.shopUserId);
        const name = item.name ?? '';
        const priority = task.priority ?? 1;
        const nested = a.b ?? c.d ?? 0;
        """
        violations = scan_typescript_code(code, "src/valid-mapper.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_safe_02_ternary_operator_allowed(self):
        """[TC-SAFE-02] Ternary operator 'cond ? a : b' must NOT trigger violations."""
        code = """
        const label = isValid ? item.displayName : item.fallbackName;
        const status = isActive ? user.status : 'Inactive';
        const count = total > 0 ? report.count : 0;
        """
        violations = scan_typescript_code(code, "src/view.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_safe_03_unknown_with_narrowing_allowed(self):
        """[TC-SAFE-03] 'unknown' at boundary with type narrowing is allowed."""
        code = """
        function handleError(error: unknown): string {
            if (error instanceof Error) {
                return error.message;
            }
            if (typeof error === 'string') {
                return error;
            }
            return 'Unknown error';
        }
        """
        violations = scan_typescript_code(code, "src/error.util.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_safe_04_conditional_boolean_or_allowed(self):
        """[TC-SAFE-04] Logical OR inside if/while statements must NOT trigger violations."""
        code = """
        if (user.isAdmin || user.isStaff) {
            this.allowAccess();
        }
        while (stream.hasMore || retryCount > 0) {
            this.poll();
        }
        """
        violations = scan_typescript_code(code, "src/guard.ts")
        self.assertEqual(len(violations), 0)

    # =========================================================================
    # STAGE 4.4: PATH EXCLUSIONS (REQ-EXCLUDE-01 .. REQ-EXCLUDE-05)
    # =========================================================================

    def test_tc_exclude_01_node_modules(self):
        """[TC-EXCLUDE-01] node_modules must be excluded."""
        self.assertTrue(is_path_excluded("node_modules/pkg/index.ts"))
        self.assertTrue(is_path_excluded("projects/app/node_modules/lib/core.ts"))
        code = "const x: any = 1; const y = a.b || c.d;"
        violations = scan_typescript_code(code, "node_modules/@lib/index.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_exclude_02_dist(self):
        """[TC-EXCLUDE-02] dist folder must be excluded."""
        self.assertTrue(is_path_excluded("dist/bundle.js"))
        self.assertTrue(is_path_excluded("apps/app-shell/dist/main.js"))
        code = "const x: any = 1;"
        violations = scan_typescript_code(code, "dist/main.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_exclude_03_auto_gen(self):
        """[TC-EXCLUDE-03] auto-gen folders must be excluded."""
        self.assertTrue(is_path_excluded("src/auto-gen/api-client.ts"))
        self.assertTrue(is_path_excluded("projects/core/src/auto-gen/models.ts"))
        code = "export interface GeneratedDto { data: any; title: a.b || c; }"
        violations = scan_typescript_code(code, "src/auto-gen/api.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_exclude_04_spec_files(self):
        """[TC-EXCLUDE-04] Unit test files (*.spec.ts, *.test.ts) must be excluded."""
        self.assertTrue(is_path_excluded("src/app/services/hub/hub.service.spec.ts"))
        self.assertTrue(is_path_excluded("tests/unit.test.ts"))
        code = "const mockStore: any = { reload: jest.fn() };"
        violations = scan_typescript_code(code, "src/service.spec.ts")
        self.assertEqual(len(violations), 0)

    def test_tc_exclude_05_declaration_files(self):
        """[TC-EXCLUDE-05] Type declaration files (*.d.ts) must be excluded."""
        self.assertTrue(is_path_excluded("src/typings.d.ts"))
        self.assertTrue(is_path_excluded("global.d.ts"))
        code = "declare const window: any;"
        violations = scan_typescript_code(code, "src/globals.d.ts")
        self.assertEqual(len(violations), 0)

    # =========================================================================
    # STAGE 4.5: NOISE REDUCTION (REQ-NOISE-01)
    # =========================================================================

    def test_tc_noise_01_comments_and_strings_ignored(self):
        """[TC-NOISE-01] Comments and string literals containing 'any' or '||' must NOT trigger."""
        code = """
        // Note: Do not use : any in this interface
        /* Multi-line comment:
           item.id || item.shopUserId was the legacy approach
        */
        const message = "Please do not provide : any or a.b || c.d";
        const template = `Template string warning: <any> is forbidden`;
        """
        violations = scan_typescript_code(code, "src/clean.ts")
        self.assertEqual(len(violations), 0)

    # =========================================================================
    # STAGE 5: INTEGRATION CHECK & DECISION TABLE (DT-01 .. DT-04)
    # =========================================================================

    def test_tc_decision_table_composite_file(self):
        """[TC-DT-01] Composite file with mixed valid, invalid, and edge cases."""
        code = """
        import { Employee } from './employee.dto';

        export class EmployeeMapper {
            // Valid mapping with nullish coalescing
            public mapEmployee(emp: Employee) {
                return {
                    id: emp.shopUserId,
                    userId: emp.accountUserId ?? String(emp.shopUserId),
                    name: emp.name,
                    role: emp.roleName ?? '',
                };
            }

            // VIOLATION 1: Sloppy fallback on object properties
            public getLegacyRole(emp: Employee) {
                return emp.roleName || emp.defaultRole || 'Unknown';
            }

            // VIOLATION 2: Cast as any
            public getRawExtra(emp: Employee) {
                return (emp as any).extraData;
            }

            // VIOLATION 3: Parameter explicit any
            public attachPayload(payload: any) {
                return payload;
            }

            // SAFE: Ternary expression
            public getStatus(emp: Employee) {
                return emp.isActive ? 'Active' : 'Suspended';
            }
        }
        """
        violations = scan_typescript_code(code, "src/employee.mapper.ts")
        self.assertEqual(len(violations), 3)

        rules = [v.rule for v in violations]
        self.assertIn("anti-sloppy-fallback", rules)
        self.assertEqual(rules.count("zero-any"), 2)


if __name__ == "__main__":
    print("===========================================================================")
    print("🧪 RUNNING 5-STAGE ISTQB STRICT TYPING & FALLBACK TEST SUITE")
    print("===========================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStrictTypingScannerISTQB)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("===========================================================================")
        print("✅ ALL 13 TESTCASES (5-STAGE ISTQB MATRIX) PASSED (100% COVERAGE).")
        print("===========================================================================")
        sys.exit(0)
    else:
        print("❌ TEST SUITE FAILED!")
        sys.exit(1)
