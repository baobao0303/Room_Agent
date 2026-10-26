#!/usr/bin/env python3
"""
tools/query_reader.py - High-precision query-based file/directory reader.
Solves EISDIR errors and file guessing by inspecting directories,
chunking markdown/code, and scoring relevance with exact-match and TF-IDF boosting.
"""

import os
import sys
import re
import math
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set

try:
    import resource
    # Cap virtual memory at 768MB to prevent system OOM
    resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024, 768 * 1024 * 1024))
except Exception:
    pass

DEFAULT_EXTS = {".md", ".markdown", ".ts", ".js", ".json", ".html", ".css", ".py", ".sh", ".yaml", ".yml", ".txt"}
IGNORED_DIRS = {"node_modules", "dist", ".git", "coverage", "__pycache__", ".nx", ".cache", "tmp", ".build", ".angular"}
MAX_COLLECT_FILES = 120

def stem(word: str) -> str:
    """Lightweight suffix stripping for plural and verb forms."""
    w = word.lower()
    for suffix in ("ing", "es", "ed", "s"):
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            return w[:-len(suffix)]
    return w

def tokenize(text: str) -> List[str]:
    """Tokenize string into lowercase alphanumeric tokens."""
    return re.findall(r"[a-zA-Z0-9_\-\.]+", text.lower())

def is_text_file(path: Path) -> bool:
    """Check if file has readable text extension."""
    if path.name.startswith("."):
        return False
    return path.suffix.lower() in DEFAULT_EXTS or path.name in {"Dockerfile", "Makefile", "LICENSE"}

def get_directory_tree(dir_path: Path, max_depth: int = 3, max_files: int = 80) -> str:
    """Generate concise directory tree without overflowing context."""
    lines = [f"📂 {dir_path.resolve()}"]
    count = 0

    def walk(current: Path, prefix: str, depth: int):
        nonlocal count
        if depth > max_depth or count >= max_files:
            return
        try:
            entries = sorted(list(current.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
        except (PermissionError, FileNotFoundError):
            return

        for i, entry in enumerate(entries):
            if entry.name.startswith(".") or entry.name in {"node_modules", "dist", ".git", "coverage", "__pycache__"}:
                continue
            count += 1
            if count > max_files:
                lines.append(f"{prefix}... (truncated extra files)")
                break
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            sub_prefix = "    " if is_last else "│   "
            if entry.is_dir():
                lines.append(f"{prefix}{connector}📁 {entry.name}/")
                walk(entry, prefix + sub_prefix, depth + 1)
            else:
                lines.append(f"{prefix}{connector}📄 {entry.name}")

    walk(dir_path, "", 1)
    return "\n".join(lines)

def chunk_markdown(content: str, file_path: str) -> List[Dict[str, Any]]:
    """Split markdown into semantic sections based on headers."""
    lines = content.splitlines()
    chunks = []
    current_heading = "Top of File"
    current_lines = []
    start_line = 1

    header_regex = re.compile(r"^(#{1,6})\s+(.+)$")

    for idx, line in enumerate(lines, 1):
        m = header_regex.match(line.strip())
        if m:
            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text:
                    chunks.append({
                        "file_path": file_path,
                        "heading": current_heading,
                        "content": chunk_text,
                        "start_line": start_line,
                        "end_line": idx - 1
                    })
            current_heading = m.group(0).strip()
            current_lines = [line]
            start_line = idx
        else:
            current_lines.append(line)

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text:
            chunks.append({
                "file_path": file_path,
                "heading": current_heading,
                "content": chunk_text,
                "start_line": start_line,
                "end_line": len(lines)
            })

    return chunks

def chunk_generic(content: str, file_path: str, chunk_size: int = 50) -> List[Dict[str, Any]]:
    """Split generic code or text files into overlapping line chunks."""
    lines = content.splitlines()
    if not lines:
        return []
    chunks = []
    step = max(25, chunk_size // 2)
    for i in range(0, len(lines), step):
        batch = lines[i:i + chunk_size]
        if not batch:
            break
        chunk_text = "\n".join(batch).strip()
        if chunk_text:
            chunks.append({
                "file_path": file_path,
                "heading": f"Lines {i + 1}-{min(i + len(batch), len(lines))}",
                "content": chunk_text,
                "start_line": i + 1,
                "end_line": min(i + len(batch), len(lines))
            })
    return chunks

def extract_chunks(path: Path) -> List[Dict[str, Any]]:
    """Read a file and chunk it appropriately."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    if path.suffix.lower() in {".md", ".markdown"}:
        chunks = chunk_markdown(content, str(path))
        if chunks:
            return chunks
    return chunk_generic(content, str(path))

def collect_files(target: Path, exts: Set[str], max_files: int = MAX_COLLECT_FILES) -> List[Path]:
    """Collect up to max_files text files to prevent memory explosion."""
    if target.is_file():
        return [target]
    if not target.is_dir():
        return []
    collected = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORED_DIRS]
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in exts or is_text_file(p):
                collected.append(p)
                if len(collected) >= max_files:
                    return collected
    return collected

def score_chunk(chunk: Dict[str, Any], query: str, query_tokens: List[str], query_stemmed: List[str]) -> float:
    """Calculate relevance score for a chunk with exact and heuristic boosts."""
    content_lower = chunk["content"].lower()
    heading_lower = chunk["heading"].lower()
    file_name = Path(chunk["file_path"]).name.lower()
    file_path_lower = chunk["file_path"].lower()

    score = 0.0
    query_lower = query.lower()

    # 1. Exact phrase matches (Highest priority)
    if query_lower in file_name:
        score += 80.0
    elif any(q in file_name for q in query_tokens):
        score += 40.0
    elif any(s in file_name for s in query_stemmed):
        score += 25.0

    if query_lower in heading_lower:
        score += 60.0

    if query_lower in content_lower:
        score += 40.0

    # 2. Token overlap & stemming frequency
    content_tokens = tokenize(content_lower)
    heading_tokens = tokenize(heading_lower)
    
    token_counts: Dict[str, int] = {}
    for t in content_tokens:
        token_counts[t] = token_counts.get(t, 0) + 1

    stem_counts: Dict[str, int] = {}
    for t in content_tokens:
        st = stem(t)
        stem_counts[st] = stem_counts.get(st, 0) + 1

    matched_tokens = 0
    for q_tok, q_stem in zip(query_tokens, query_stemmed):
        matched_this = False
        if q_tok in heading_tokens or q_stem in [stem(h) for h in heading_tokens]:
            score += 25.0
            matched_this = True
        
        if q_tok in token_counts:
            score += 8.0 * (1.0 + math.log(token_counts[q_tok]))
            matched_this = True
        elif q_stem in stem_counts:
            score += 6.0 * (1.0 + math.log(stem_counts[q_stem]))
            matched_this = True
        elif q_tok in file_path_lower or q_stem in file_path_lower:
            score += 10.0
            matched_this = True

        if matched_this:
            matched_tokens += 1

    if not matched_tokens:
        return 0.0

    # Coverage bonus: reward chunks covering more query tokens
    coverage_ratio = matched_tokens / max(1, len(query_tokens))
    score *= (0.5 + 0.5 * coverage_ratio)

    # Length penalty: avoid giant dump chunks
    length_penalty = 1.0 / (1.0 + 0.0004 * len(chunk["content"]))
    score *= length_penalty

    return round(score, 2)

def query_read(
    target_path: str,
    query: Optional[str] = None,
    top_k: int = 3,
    max_lines: int = 60,
    show_tree: bool = False,
    as_json: bool = False
) -> Dict[str, Any]:
    """Execute query read on directory or file."""
    path = Path(target_path).expanduser().resolve()

    if not path.exists():
        return {
            "error": f"Path not found: {path}",
            "status": "not_found",
            "results": []
        }

    # Case 1: Directory with no query or tree requested -> Output directory tree
    if path.is_dir() and (not query or show_tree):
        tree = get_directory_tree(path)
        return {
            "type": "directory_tree",
            "path": str(path),
            "tree": tree,
            "status": "success",
            "results": []
        }

    # Case 2: File with no query -> Read entire file (or up to max_lines)
    if path.is_file() and not query:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            snippet = "\n".join(lines[:max_lines])
            truncated = len(lines) > max_lines
            return {
                "type": "file_read",
                "path": str(path),
                "total_lines": len(lines),
                "truncated": truncated,
                "content": snippet,
                "status": "success",
                "results": []
            }
        except Exception as e:
            return {"error": str(e), "status": "error", "results": []}

    # Case 3: Query search across file or directory
    query_str = (query or "").strip()
    query_tokens = tokenize(query_str)
    query_stemmed = [stem(t) for t in query_tokens]

    if not query_tokens:
        return {"error": "Query string is empty.", "status": "empty_query", "results": []}

    files = collect_files(path, DEFAULT_EXTS)
    if not files:
        return {
            "error": f"No readable text/code files found in: {path}",
            "status": "empty_directory",
            "results": []
        }

    scored = []
    total_chunks = 0
    for f in files:
        for ch in extract_chunks(f):
            total_chunks += 1
            sc = score_chunk(ch, query_str, query_tokens, query_stemmed)
            if sc > 0:
                scored.append((sc, ch))
                if len(scored) > top_k * 10:
                    scored.sort(key=lambda x: x[0], reverse=True)
                    del scored[top_k * 3:]

    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = scored[:top_k]

    results_data = []
    for rank, (sc, ch) in enumerate(top_results, 1):
        content_lines = ch["content"].splitlines()
        trimmed_content = "\n".join(content_lines[:max_lines])
        is_truncated = len(content_lines) > max_lines
        results_data.append({
            "rank": rank,
            "score": sc,
            "file": ch["file_path"],
            "heading": ch["heading"],
            "start_line": ch["start_line"],
            "end_line": ch["end_line"],
            "truncated": is_truncated,
            "content": trimmed_content
        })

    return {
        "type": "query_match",
        "target": str(path),
        "query": query_str,
        "top_k_enforced": top_k,
        "context_bounded_rule": "NÓI CÓ SÁCH, MÁCH CÓ CHỨNG: Chỉ tổng hợp câu trả lời duy nhất từ các context chunks dưới đây; nghiêm cấm suy đoán ngoài ngữ cảnh.",
        "scanned_files": len(files),
        "scanned_chunks": total_chunks,
        "match_count": len(scored),
        "results": results_data,
        "status": "success"
    }

def build_context_bounded_prompt(query: str, chunks: List[Dict[str, Any]], max_chunks: int = 3) -> str:
    """Đóng gói tối đa 3 đoạn ngữ cảnh thành Context-Bounded Prompt chống Hallucination (Pillar 1 RAG)."""
    # Enforce strict ceiling of at most 3 chunks (clamped to [0, 3])
    limit = min(max(0, int(max_chunks)), 3)
    bounded_chunks = chunks[:limit]
    lines = [
        "=== [CONTEXT-BOUNDED RAG ENGINE (TOP-K = 3 CHUNKS)] ===",
        "NGUYÊN TẮC BẮT BUỘC ('Nói có sách, mách có chứng'):",
        "1. Chỉ được phép tổng hợp câu trả lời DUY NHẤT từ các đoạn ngữ cảnh được trích xuất dưới đây (tối đa 3 chunks).",
        "2. Tuyệt đối không sử dụng trí nhớ ngoài hoặc tự suy diễn/bịa đặt thông tin (0% Hallucination).",
        f"Truy vấn: {query}",
        "---"
    ]
    for idx, ch in enumerate(bounded_chunks, 1):
        src = ch.get("file") or ch.get("file_path") or ch.get("domain") or "unknown"
        heading = ch.get("heading") or ch.get("cue") or f"Section #{idx}"
        content = ch.get("content") or ch.get("lesson") or ""
        lines.append(f"[Chunk #{idx} | Source: {src} | Section: {heading}]")
        lines.append(str(content))
        lines.append("---")
    return "\n".join(lines)

def format_output_cli(data: Dict[str, Any]) -> str:
    """Format dictionary result into clean, readable terminal text."""
    if data.get("error"):
        return f"❌ Error: {data['error']}"

    if data.get("type") == "directory_tree":
        return f"{data['tree']}\n\n💡 Tip: Run with a query to search inside files: python3 tools/query_reader.py \"{data['path']}\" \"<query>\""

    if data.get("type") == "file_read":
        header = f"📄 File: {data['path']} (Total lines: {data['total_lines']})"
        if data.get("truncated"):
            header += f" [Showing first {len(data['content'].splitlines())} lines]"
        return f"{header}\n" + "=" * 60 + f"\n{data['content']}"

    if data.get("type") == "query_match":
        if not data["results"]:
            return f"⚠️ No matching content found for query '{data['query']}' in {data['target']} (Scanned {data['scanned_files']} files, {data['scanned_chunks']} sections)."

        out = [
            f"🔍 Query: \"{data['query']}\" | Target: {data['target']}",
            f"📊 Found {data['match_count']} matches across {data['scanned_files']} files. Top {len(data['results'])} shown:\n"
        ]

        for res in data["results"]:
            trunc_note = f" (truncated to {len(res['content'].splitlines())} lines)" if res["truncated"] else ""
            out.append(f"┌── [Rank #{res['rank']} | Score: {res['score']}] {res['file']}:{res['start_line']}-{res['end_line']}{trunc_note}")
            out.append(f"│   Section: {res['heading']}")
            out.append("├── " + "─" * 56)
            for line in res["content"].splitlines():
                out.append(f"│   {line}")
            out.append("└── " + "─" * 56 + "\n")

        return "\n".join(out)

    return json.dumps(data, indent=2)

def main():
    parser = argparse.ArgumentParser(
        description="High-precision query-based reader for files and directories (solves EISDIR and guessing)."
    )
    parser.add_argument("path", help="Target file or directory path.")
    parser.add_argument("query", nargs="?", default=None, help="Search query, keyword, or question.")
    parser.add_argument("-n", "--top", type=int, default=3, help="Number of top matches to return (default: 3).")
    parser.add_argument("-m", "--max-lines", type=int, default=60, help="Max lines per content snippet (default: 60).")
    parser.add_argument("-t", "--tree", action="store_true", help="Display directory tree.")
    parser.add_argument("-j", "--json", action="store_true", help="Output results in JSON format.")

    args = parser.parse_args()

    data = query_read(
        target_path=args.path,
        query=args.query,
        top_k=args.top,
        max_lines=args.max_lines,
        show_tree=args.tree,
        as_json=args.json
    )

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_output_cli(data))

if __name__ == "__main__":
    main()
