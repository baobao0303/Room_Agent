#!/usr/bin/env python3
"""
tools/room_cleanup.py - Bộ thu gom rác an toàn & bảo vệ context BMAD (Safe Context Garbage Collector).

NGUYÊN TẮC BẢO VỆ CONTEXT TUYỆT ĐỐI:
1. CẤM XÓA nếu Task chưa ở trạng thái 'Closed' trên Harness DB (Floci DynamoDB).
   Nếu task đang Active, Resolved, New, Blocked -> TỪ CHỐI XÓA (Hard Abort).
2. ARCHIVE THAY VÌ DELETE: Khi Closed, chuyển các file vào bmad/rooms/archive/ thay vì xóa trắng.
3. KHÔNG BAO GIỜ XÓA bằng ngày tháng (sweep mù quáng) nếu file thuộc về một Task chưa Closed.
"""

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from floci_client import FlociHarnessDB  # type: ignore
except ImportError:
    from tools.floci_client import FlociHarnessDB  # type: ignore

ROOMS_DIR = PROJECT_ROOT / "bmad" / "rooms"
ARCHIVE_DIR = ROOMS_DIR / "archive"
PRESERVE_FILENAMES = {
    "latest_handoff.md",
    "latest_discussion.md",
    "latest_review.md",
    "README.md",
    "template-handoff.md",
    "template-discussion.md",
}


def get_task_state(db: FlociHarnessDB, task_id: str) -> str | None:
    try:
        numeric_id = int("".join(filter(str.isdigit, str(task_id))))
        item = db.get_work_item(numeric_id)
        if item:
            return item.get("state")
    except Exception:
        pass
    return None


def cleanup_by_task(task_id: str, dry_run: bool = False, force: bool = False):
    print(f"=== KIỂM TRA AN TOÀN TRƯỚC KHI THU GOM TASK #{task_id} ===")
    db = FlociHarnessDB()
    state = get_task_state(db, task_id)

    if not state and not force:
        print(f"❌ [TỪ CHỐI]: Không tìm thấy Work Item #{task_id} trên Harness DB.")
        print("   Không thể xác minh an toàn. Dừng dọn dẹp để chống mất context.")
        return

    print(f"ℹ️ Trạng thái Task #{task_id} trên Harness DB: [{state}]")

    if state != "Closed" and not force:
        print(f"❌ [CHẶN DỌN DẸP]: Task #{task_id} đang ở trạng thái '{state}' (CHƯA CLOSED)!")
        print("   Lý do: Các Agent (Peer/QC) có thể vẫn đang đọc hoặc kiểm thử.")
        print("   Xóa lúc này sẽ gây LOẠN CONTEXT và sinh BUG. Chỉ dọn dẹp khi state == 'Closed'.")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    task_archive_dir = ARCHIVE_DIR / f"task_{task_id}"
    if not dry_run:
        task_archive_dir.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    for room in ROOMS_DIR.iterdir():
        if not room.is_dir() or room.name in {"archive", ".claude"}:
            continue
        for file in room.glob("*.md"):
            if file.name in PRESERVE_FILENAMES:
                continue
            if task_id in file.name:
                moved_count += 1
                dest = task_archive_dir / file.name
                if dry_run:
                    print(f"  [DRY-RUN SẼ ARCHIVE] {file.relative_to(PROJECT_ROOT)} ➔ {dest.relative_to(PROJECT_ROOT)}")
                else:
                    shutil.move(str(file), str(dest))
                    print(f"  [ĐÃ ARCHIVE] {file.relative_to(PROJECT_ROOT)} ➔ {dest.relative_to(PROJECT_ROOT)}")

    action_label = "Sẽ lưu trữ" if dry_run else "Đã lưu trữ an toàn"
    print(f"✅ Hoàn tất: {action_label} {moved_count} file tạm của Task #{task_id} vào {ARCHIVE_DIR.name}/.\n")


def sweep_safe(days: int = 14, dry_run: bool = False):
    print(f"=== QUÉT DỌN AN TOÀN ĐỊNH KỲ (CHỈ ÁP DỤNG TASK ĐÃ CLOSED) ===")
    db = FlociHarnessDB()
    now = time.time()
    cutoff_seconds = days * 86400
    candidates = []

    for room in ROOMS_DIR.iterdir():
        if not room.is_dir() or room.name in {"archive", ".claude"}:
            continue
        for file in room.glob("*.md"):
            if file.name in PRESERVE_FILENAMES:
                continue
            mtime = file.stat().st_mtime
            if (now - mtime) > cutoff_seconds:
                name_digits = "".join(filter(str.isdigit, file.stem.split("_")[1] if "_" in file.stem else ""))
                candidates.append((file, name_digits, (now - mtime) / 86400))

    if not candidates:
        print(f"Không có file nào cũ hơn {days} ngày.")
        return

    for file, tid, age in candidates:
        if tid:
            state = get_task_state(db, tid)
            if state != "Closed":
                print(f"  🔒 [BẢO VỆ] Bỏ qua {file.name} ({age:.1f} ngày tuổi) vì Task #{tid} state là '{state}' (chưa Closed).")
                continue

        dest = ARCHIVE_DIR / file.name
        if dry_run:
            print(f"  [DRY-RUN ARCHIVE] {file.name} ({age:.1f} ngày tuổi)")
        else:
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(dest))
            print(f"  [ĐÃ ARCHIVE] {file.name} ({age:.1f} ngày tuổi)")


def main():
    parser = argparse.ArgumentParser(description="Thu gom rác an toàn cho BMAD rooms.")
    parser.add_argument("--task-id", type=str, help="Work Item / Task ID cần dọn dẹp (VD: 889, WI-65)")
    parser.add_argument("--sweep", action="store_true", help="Quét dọn an toàn file cũ hơn N ngày (chỉ dọn task đã Closed)")
    parser.add_argument("--days", type=int, default=14, help="Số ngày tuổi để quét dọn (mặc định: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra, không di chuyển file")
    parser.add_argument("--force", action="store_true", help="Bỏ qua kiểm tra Harness state (nguy hiểm, chỉ dùng khi khẩn cấp)")
    args = parser.parse_args()

    if not args.task_id and not args.sweep:
        parser.print_help()
        print("\nLỗi: Cần truyền --task-id <id> hoặc --sweep.")
        sys.exit(1)

    if args.task_id:
        cleanup_by_task(args.task_id, dry_run=args.dry_run, force=args.force)

    if args.sweep:
        sweep_safe(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
