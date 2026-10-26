#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import tools.lead_code_review as lcr


class TestLeadCodeReview(unittest.TestCase):
    def test_analyze_code_quality_approved(self):
        clean_diff = """
diff --git a/src/app/button.component.ts b/src/app/button.component.ts
--- a/src/app/button.component.ts
+++ b/src/app/button.component.ts
@@ -1,3 +1,5 @@
+@Component({
+  changeDetection: ChangeDetectionStrategy.OnPush,
+})
+export class ButtonComponent {}
"""
        res = lcr.analyze_code_quality(clean_diff)
        self.assertEqual(res["verdict"], "APPROVED")
        self.assertEqual(res["total_findings"], 0)

    def test_analyze_code_quality_hardcoded_hex(self):
        dirty_diff = """
diff --git a/src/app/header.component.ts b/src/app/header.component.ts
--- a/src/app/header.component.ts
+++ b/src/app/header.component.ts
@@ -1,3 +1,4 @@
+const color = '#ff0000';
"""
        res = lcr.analyze_code_quality(dirty_diff)
        self.assertEqual(res["verdict"], "ADVICE_PROVIDED")
        self.assertEqual(res["total_findings"], 1)
        self.assertEqual(res["findings"][0]["category"], "TDS_DESIGN_TOKEN")

    def test_analyze_code_quality_hardcoded_testid_error(self):
        error_diff = """
diff --git a/src/app/card.component.html b/src/app/card.component.html
--- a/src/app/card.component.html
+++ b/src/app/card.component.html
@@ -1,2 +1,2 @@
-<div class="card">
+<div class="card" data-testid="user-card">
"""
        res = lcr.analyze_code_quality(error_diff)
        self.assertEqual(res["verdict"], "REJECTED")
        self.assertEqual(res["findings"][0]["category"], "TDS_TEST_ID_VIOLATION")

    @patch("subprocess.run")
    def test_run_git_diff(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="diff --git a b\n")
        diff = lcr.run_git_diff(Path("."))
        self.assertIn("diff --git", diff)


if __name__ == "__main__":
    unittest.main()
