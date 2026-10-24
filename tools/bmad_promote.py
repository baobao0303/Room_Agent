#!/usr/bin/env python3
"""
tools/bmad_promote.py - BMAD Notebook-to-Wiki Promotion Gate.
Promotes draft notes from bmad/rooms/<role>/drafts/ into canonical bmad/wiki/
following strict Lead/QC review and verification.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIKI_ROOT = PROJECT_ROOT / "bmad" / "wiki"
ARCHIVE_ROOT = PROJECT_ROOT / "bmad" / "rooms" / "archive" / "promoted_drafts"
ROOM_LEDGER_PATH = PROJECT_ROOT / "bmad" / "rooms" / "room_ledger.json"

ALLOWED_REVIEWERS = {"lead", "qc", "supervisor"}
VALID_DOMAINS = {"architecture", "governance", "protocols", "testing", "general"}


def slugify(text: str) -> str:
    """Convert text to URL-safe kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "untitled"


def validate_draft_content(content: str) -> list[str]:
    """Validate that draft is meaningful, formatted and clean."""
    errors = []
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) < 5:
        errors.append("Bản nháp quá ngắn (yêu cầu tối thiểu 5 dòng nội dung).")
    if not any(line.startswith("# ") for line in lines):
        errors.append("Bản nháp thiếu tiêu đề Markdown cấp 1 ('# <Tiêu đề>').")

    # Anti-leak check for private IPs or passwords
    leak_patterns = [
        (re.compile(r"ghp_[a-zA-Z0-9]{30,}"), "GitHub Personal Access Token"),
        (re.compile(r"(password|secret|apikey)\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE), "Hardcoded Secret"),
    ]
    for pattern, desc in leak_patterns:
        if pattern.search(content):
            errors.append(f"Phát hiện rò rỉ dữ liệu nhạy cảm: {desc}")

    return errors


def record_promotion_in_ledger(article_path: str, domain: str, reviewer: str, task_id: int | None):
    """Record the promotion event in bmad/rooms/room_ledger.json (FIFO 50)."""
    if not ROOM_LEDGER_PATH.exists():
        return
    try:
        data = json.loads(ROOM_LEDGER_PATH.read_text(encoding="utf-8"))
        events = data.get("recent_events", [])
        events.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "WIKI_PROMOTION",
            "article": article_path,
            "domain": domain,
            "reviewer": reviewer,
            "task_id": task_id
        })
        if len(events) > 50:
            events = events[-50:]
        data["recent_events"] = events
        ROOM_LEDGER_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def promote_draft(
    draft_path: str | Path,
    domain: str,
    title: str,
    reviewer: str,
    task_id: int | None = None,
    dry_run: bool = False
) -> dict:
    reviewer = reviewer.lower().strip()
    if reviewer not in ALLOWED_REVIEWERS:
        return {
            "status": "error",
            "message": f"Thẩm quyền không hợp lệ: '{reviewer}'. Chỉ có 'lead', 'qc' hoặc 'supervisor' mới có quyền duyệt Promote vào Wiki."
        }

    domain = domain.lower().strip()
    if domain not in VALID_DOMAINS:
        return {
            "status": "error",
            "message": f"Phân vùng domain không hợp lệ: '{domain}'. Cho phép: {sorted(VALID_DOMAINS)}"
        }

    p = Path(draft_path).resolve()
    if not p.is_file():
        return {
            "status": "error",
            "message": f"Không tìm thấy file bản nháp tại: {draft_path}"
        }

    content = p.read_text(encoding="utf-8", errors="replace")
    errors = validate_draft_content(content)
    if errors:
        return {
            "status": "error",
            "message": "Bản nháp không đạt chuẩn nghiệm thu",
            "errors": errors
        }

    # Generate target paths
    slug = slugify(title)
    dest_dir = WIKI_ROOT / domain
    dest_file = dest_dir / f"{slug}.md"
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    dest_dir.mkdir(parents=True, exist_ok=True)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frontmatter = (
        "---\n"
        f"title: \"{title}\"\n"
        f"domain: \"{domain}\"\n"
        f"promoted_by: \"{reviewer}\"\n"
        f"promoted_at: \"{now_str}\"\n"
        f"source_draft: \"{p.name}\"\n"
        f"task_id: {task_id if task_id else 'null'}\n"
        "---\n\n"
    )

    promoted_content = frontmatter + content

    if dry_run:
        return {
            "status": "dry_run",
            "target_article": str(dest_file.relative_to(PROJECT_ROOT)),
            "archive_path": str(ARCHIVE_ROOT.relative_to(PROJECT_ROOT) / f"{now_str[:10]}_{p.name}"),
            "message": "Dry-run hợp lệ. Bản nháp sẵn sàng để Promote vào Wiki."
        }

    # Write canonical wiki article
    dest_file.write_text(promoted_content, encoding="utf-8")

    # Safely archive the original draft
    archive_file = ARCHIVE_ROOT / f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{p.name}"
    shutil.move(str(p), str(archive_file))

    # Log in room ledger
    record_promotion_in_ledger(str(dest_file.relative_to(PROJECT_ROOT)), domain, reviewer, task_id)

    return {
        "status": "success",
        "target_article": str(dest_file.relative_to(PROJECT_ROOT)),
        "archive_path": str(archive_file.relative_to(PROJECT_ROOT)),
        "message": f"Đã promote thành công bài viết '{title}' vào Wiki phân vùng [{domain}]."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", required=True, help="Đường dẫn tới file bản nháp cần promote")
    parser.add_argument("--domain", default="architecture", choices=sorted(VALID_DOMAINS), help="Phân vùng tri thức Wiki")
    parser.add_argument("--title", required=True, help="Tiêu đề bài viết chính thức")
    parser.add_argument("--reviewer", required=True, help="Vai trò duyệt (lead, qc, supervisor)")
    parser.add_argument("--task-id", type=int, help="Mã Task trên Harness DB (nếu có)")
    parser.add_argument("--dry-run", action="store_true", help="Kiểm tra hợp lệ nhưng không ghi file")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dưới định dạng JSON")

    args = parser.parse_args()
    res = promote_draft(
        draft_path=args.draft,
        domain=args.domain,
        title=args.title,
        reviewer=args.reviewer,
        task_id=args.task_id,
        dry_run=args.dry_run
    )

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        if res["status"] == "success":
            print(f"✅ {res['message']}")
            print(f"   📄 Bài viết Wiki: {res['target_article']}")
            print(f"   📦 Đã lưu trữ nháp: {res['archive_path']}")
        elif res["status"] == "dry_run":
            print(f"🔍 [DRY-RUN]: {res['message']}")
            print(f"   📄 Dự kiến bài viết: {res['target_article']}")
        else:
            print(f"❌ [LỖI THẨM ĐỊNH]: {res['message']}")
            for err in res.get("errors", []):
                print(f"   - {err}")
            sys.exit(1)


if __name__ == "__main__":
    main()
