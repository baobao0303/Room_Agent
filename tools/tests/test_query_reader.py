#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import tools.query_reader as qr


class TestQueryReader(unittest.TestCase):
    def test_stem(self):
        self.assertEqual(qr.stem("testing"), "test")
        self.assertEqual(qr.stem("classes"), "class")
        self.assertEqual(qr.stem("created"), "creat")
        self.assertEqual(qr.stem("cats"), "cat")
        self.assertEqual(qr.stem("is"), "is")  # short word preserved

    def test_tokenize(self):
        tokens = qr.tokenize("Hello-World! 123 foo_bar.baz")
        self.assertEqual(tokens, ["hello-world", "123", "foo_bar.baz"])

    def test_is_text_file(self):
        self.assertTrue(qr.is_text_file(Path("spec.md")))
        self.assertTrue(qr.is_text_file(Path("main.ts")))
        self.assertTrue(qr.is_text_file(Path("LICENSE")))
        self.assertFalse(qr.is_text_file(Path(".hidden.txt")))
        self.assertFalse(qr.is_text_file(Path("image.png")))

    def test_chunk_markdown(self):
        md_text = "# Header 1\nLine 1\nLine 2\n\n## Header 2\nLine 3"
        chunks = qr.chunk_markdown(md_text, "test.md")
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["heading"], "# Header 1")
        self.assertEqual(chunks[1]["heading"], "## Header 2")

    def test_chunk_generic(self):
        lines = "\n".join([f"line {i}" for i in range(1, 100)])
        chunks = qr.chunk_generic(lines, "code.py", chunk_size=40)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]["start_line"], 1)

    def test_query_read_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".md") as tmp:
            tmp.write("# Authentication Flow\nJWT tokens are validated in the auth middleware.\n")
            tmp_path = Path(tmp.name)

        try:
            res = qr.query_read(str(tmp_path), query="auth middleware", top_k=2)
            self.assertIn("results", res)
            self.assertGreater(len(res["results"]), 0)
            self.assertIn("Authentication Flow", res["results"][0]["heading"])
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_query_read_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dir_path = Path(tmp_dir)
            f1 = dir_path / "service.ts"
            f1.write_text("export class PaymentService {\n  processPayment() {}\n}\n", encoding="utf-8")

            res = qr.query_read(str(dir_path), query="PaymentService", top_k=1)
            self.assertIn("results", res)
            self.assertGreater(len(res["results"]), 0)
            self.assertTrue(res["results"][0]["file"].endswith("service.ts"))

            tree_res = qr.query_read(str(dir_path), show_tree=True)
            self.assertEqual(tree_res.get("type"), "directory_tree")
            self.assertIn("service.ts", tree_res.get("tree", ""))


if __name__ == "__main__":
    unittest.main()
