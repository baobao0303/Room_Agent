#!/usr/bin/env python3
"""
tools/record_discussion.py - Ghi biên bản thảo luận & đồng thuận (ADR/Discussion Minutes) giữa các Agent.

Mục đích:
- Lưu vết tranh luận kỹ thuật giữa các Agent (Peer vs Lead, v.v.).
- Chắt lọc giải pháp đồng thuận thành văn bản rõ ràng, chống trôi thông tin.
- Lưu tại bmad/rooms/discussions/ và tùy chọn tạo ADR vĩnh viễn tại bmad/adrs/.
"""

import argparse
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCUSSIONS_DIR = PROJECT_ROOT / "bmad" / "rooms" / "discussions"
ADR_DIR = PROJECT_ROOT / "bmad" / "adrs"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:40] or "discussion"


def main():
    parser = argparse.ArgumentParser(description="Ghi biên bản thảo luận giữa các agent.")
    parser.add_argument("--task-id", type=str, required=True, help="Harness Work Item ID hoặc Task ID (VD: 889)")
    parser.add_argument("--topic", type=str, required=True, help="Chủ đề thảo luận hoặc vấn đề tranh cãi")
    parser.add_argument("--parties", type=str, default="Peer Dev, Lead Dev", help="Các agent tham gia thảo luận")
    parser.add_argument("--conflict", type=str, required=True, help="Nội dung bất đồng / log lỗi thực nghiệm")
    parser.add_argument("--consensus", type=str, required=True, help="Giải pháp đồng thuận chốt lại")
    parser.add_argument("--actions", type=str, default="", help="Các hành động tiếp theo (Action items)")
    parser.add_argument("--adr", action="store_true", help="Lưu thành ADR vĩnh viễn trong bmad/adrs/")
    args = parser.parse_args()

    DISCUSSIONS_DIR.mkdir(parents=True, exist_ok=True)
    if args.adr:
        ADR_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    ts_now = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_file = now.strftime("%Y%m%d_%H%M%S")
    slug = slugify(args.topic)

    minutes_filename = f"minutes_{args.task_id}_{slug}_{ts_file}.md"
    minutes_path = DISCUSSIONS_DIR / minutes_filename
    latest_path = DISCUSSIONS_DIR / "latest_discussion.md"

    content = f"""# BIÊN BẢN THẢO LUẬN & ĐỒNG THUẬN KỸ THUẬT (MINUTES OF DISCUSSION)

- **Mã Task/Work Item**: `#{args.task_id}`
- **Thời gian**: `{ts_now}`
- **Các bên tham gia**: {args.parties}
- **Chủ đề thảo luận**: {args.topic}

---

## 1. VẤN ĐỀ TRANH CÃI / XUNG ĐỘT (CONFLICT & EVIDENCE)
{args.conflict}

---

## 2. GIẢI PHÁP ĐỒNG THUẬN (CONSENSUS / RESOLUTION)
{args.consensus}

---

## 3. HÀNH ĐỘNG TIẾP THEO (ACTION ITEMS)
{args.actions if args.actions else "- Tiếp tục triển khai theo phương án đồng thuận."}
"""

    minutes_path.write_text(content, encoding="utf-8")
    latest_path.write_text(content, encoding="utf-8")
    print(f"Đã lưu biên bản thảo luận vào: {minutes_path}")

    if args.adr:
        adr_file = ADR_DIR / f"ADR-{args.task_id}-{slug}.md"
        adr_content = f"""# ADR-{args.task_id}: {args.topic}

- **Trạng thái**: Accepted
- **Ngày**: `{ts_now}`
- **Bên quyết định**: {args.parties}

## Ngữ cảnh & Vấn đề
{args.conflict}

## Quyết định kỹ thuật
{args.consensus}

## Hệ quả & Ràng buộc
{args.actions if args.actions else "- Áp dụng thống nhất cho toàn bộ module liên quan."}
"""
        adr_file.write_text(adr_content, encoding="utf-8")
        print(f"Đã lưu ADR vĩnh viễn vào: {adr_file}")

    # Tùy chọn bắn tín hiệu sang Orca nếu có CLI orca
    if shutil.which("orca"):
        try:
            subprocess.run([
                "orca", "orchestration", "send",
                "--subject", f"[Minutes] Đồng thuận Task #{args.task_id}: {args.topic}",
                "--body", f"Đã chốt phương án: {args.consensus}",
                "--type", "handoff",
                "--task-id", str(args.task_id)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        except Exception:
            pass


if __name__ == "__main__":
    main()
