#!/usr/bin/env python3
from __future__ import annotations
"""
tools/room_cleanup.py - Bộ thu gom rác an toàn & bảo vệ context BMAD (Safe Context Garbage Collector).

NGUYÊN TẮC BẢO VỆ CONTEXT TUYỆT ĐỐI:
1. CẤM XÓA nếu Task chưa ở trạng thái 'Closed' trên Harness DB (Floci DynamoDB).
   Nếu task đang Active, Resolved, New, Blocked -> TỪ CHỐI XÓA (Hard Abort).
2. ARCHIVE THAY VÌ DELETE: Khi Closed, chuyển các file vào bmad/rooms/archive/ thay vì xóa trắng.
3. KHÔNG BAO GIỜ XÓA bằng ngày tháng (sweep mù quáng) nếu file thuộc về một Task chưa Closed.
"""

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

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
    "decision_memo.md",
    "README.md",
    "template-handoff.md",
    "template-discussion.md",
}


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except (ValueError, Exception):
        try:
            return str(path.relative_to(ROOMS_DIR))
        except (ValueError, Exception):
            return path.name


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
                    print(f"  [DRY-RUN SẼ ARCHIVE] {_rel(file)} ➔ {_rel(dest)}")
                else:
                    shutil.move(str(file), str(dest))
                    print(f"  [ĐÃ ARCHIVE] {_rel(file)} ➔ {_rel(dest)}")

    action_label = "Sẽ lưu trữ" if dry_run else "Đã lưu trữ an toàn"
    print(f"✅ Hoàn tất: {action_label} {moved_count} file tạm của Task #{task_id} vào {ARCHIVE_DIR.name}/.\n")

    # Tier 3: Task-Scoped Isolation & Auto-Archive (bmad/rooms/tasks/<task_id>/)
    clean_id = "".join(filter(str.isalnum, str(task_id)))
    numeric_id = "".join(filter(str.isdigit, str(task_id)))
    candidates_dirs = [ROOMS_DIR / "tasks" / str(task_id)]
    if clean_id and clean_id != str(task_id):
        candidates_dirs.append(ROOMS_DIR / "tasks" / clean_id)
    if numeric_id and numeric_id not in (str(task_id), clean_id):
        candidates_dirs.append(ROOMS_DIR / "tasks" / numeric_id)

    for task_scoped_dir in candidates_dirs:
        if task_scoped_dir.is_dir():
            dest_archive = ARCHIVE_DIR / f"task_{task_scoped_dir.name}.tar.gz"
            if dry_run:
                print(f"  [DRY-RUN SẼ ARCHIVE THƯ MỤC] {_rel(task_scoped_dir)} ➔ {_rel(dest_archive)}")
            else:
                import tarfile
                with tarfile.open(dest_archive, "w:gz") as tar:
                    tar.add(str(task_scoped_dir), arcname=task_scoped_dir.name)
                shutil.rmtree(task_scoped_dir)
                print(f"  [ĐÃ ARCHIVE THƯ MỤC] {_rel(task_scoped_dir)} ➔ {_rel(dest_archive)}")


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


def migrate_legacy(dry_run: bool = False) -> int:
    print("=== CHUẨN HÓA BMAD ROOMS: MIGRATE LEGACY HANDOFFS ===")
    legacy_archive_dir = ARCHIVE_DIR / "legacy_handoffs"
    if not dry_run:
        legacy_archive_dir.mkdir(parents=True, exist_ok=True)

    for subdir in ROOMS_DIR.rglob("*"):
        if not subdir.is_dir() or subdir.name in {"archive", ".claude", "legacy_handoffs"} or "archive" in subdir.parts:
            continue
        latest_file = subdir / "latest_handoff.md"
        if not latest_file.is_file():
            handoffs = sorted(subdir.glob("handoff_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if handoffs:
                if not dry_run:
                    shutil.copy2(str(handoffs[0]), str(latest_file))
                print(f"  [BẢO TOÀN] Khởi tạo {_rel(latest_file)} từ {handoffs[0].name}")
            elif subdir.name in ("supervisor", "pm", "lead", "peer", "qc"):
                if not dry_run:
                    now_str = time.strftime("%Y-%m-%d %H:%M:%S %z")
                    latest_file.write_text(f"# BIÊN BẢN BÀN GIAO: {subdir.name.upper()}\n\n- **Thời gian**: `{now_str}`\n- **Agent**: `{subdir.name.upper()}`\n- **Trạng thái**: Sẵn sàng.\n", encoding="utf-8")
                print(f"  [KHỞI TẠO] Khởi tạo {_rel(latest_file)} mặc định cho {subdir.name}")

    removed_count = 0
    for file in sorted(ROOMS_DIR.rglob("handoff_*.md")):
        if file.name in PRESERVE_FILENAMES or file.name == "latest_handoff.md":
            continue

        # If already inside archive/legacy_handoffs, rename to legacy_ if needed
        if "archive" in file.parts:
            renamed = file.parent / f"legacy_{file.name}"
            if not dry_run:
                shutil.move(str(file), str(renamed))
            continue

        removed_count += 1
        dest = legacy_archive_dir / f"legacy_{file.name}"
        if dest.exists():
            dest = legacy_archive_dir / f"legacy_{file.parent.name}_{file.name}"

        if dry_run:
            print(f"  [DRY-RUN SẼ ARCHIVE] {_rel(file)} ➔ {_rel(dest)}")
        else:
            shutil.move(str(file), str(dest))
            print(f"  [ĐÃ ARCHIVE] {_rel(file)} ➔ {_rel(dest)}")

    ledger_path = ROOMS_DIR / "room_ledger.json"
    now_str = time.strftime("%Y-%m-%d %H:%M:%S %z")
    ledger: dict[str, Any] = {}
    if ledger_path.is_file():
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        except Exception:
            ledger = {}
    if not isinstance(ledger, dict) or "version" not in ledger:
        ledger = {
            "version": "1.0.0",
            "updated_at": now_str,
            "roles": {
                "supervisor": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_str},
                "pm": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_str},
                "lead": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_str},
                "peer": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_str},
                "qc": {"status": "IDLE", "last_action": "", "active_task_id": None, "updated_at": now_str},
            },
            "history": [],
        }
    if not dry_run:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    action_label = "Sẽ lưu trữ" if dry_run else "Đã lưu trữ an toàn"
    print(f"✅ Hoàn tất: {action_label} {removed_count} file handoff cũ vào {_rel(legacy_archive_dir)}/.")
    print(f"✅ Đã chuẩn hóa {_rel(ledger_path)}.\n")
    return removed_count


def clean_timestamped_files(dry_run: bool = False) -> int:
    """
    Dọn dẹp các file tạm có timestamp (review_*, intake_memo_*, minutes_*) vào archive/
    theo WORKSPACE_PROTOCOL.md Section 5 (Room Hygiene Standard).
    """
    print("=== DỌN DẸP FILE TIMESTAMP KHÔNG CẦN THIẾT (WORKSPACE_PROTOCOL SECTION 5) ===")
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    reviews_archive = ARCHIVE_DIR / "legacy_reviews"
    memos_archive = ARCHIVE_DIR / "legacy_memos"
    discussions_archive = ARCHIVE_DIR / "legacy_discussions"

    if not dry_run:
        reviews_archive.mkdir(parents=True, exist_ok=True)
        memos_archive.mkdir(parents=True, exist_ok=True)
        discussions_archive.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    for room in ROOMS_DIR.iterdir():
        if not room.is_dir() or room.name in {"archive", ".claude", "tasks"}:
            continue
        for file in sorted(room.glob("*.md")):
            if file.name in PRESERVE_FILENAMES:
                continue

            target_archive = None
            if file.name.startswith("review_"):
                target_archive = reviews_archive
            elif file.name.startswith("intake_memo_"):
                target_archive = memos_archive
            elif file.name.startswith("minutes_"):
                target_archive = discussions_archive

            if target_archive:
                moved_count += 1
                dest = target_archive / file.name
                if dest.exists():
                    dest = target_archive / f"{file.parent.name}_{file.name}"
                if dry_run:
                    print(f"  [DRY-RUN SẼ ARCHIVE] {_rel(file)} ➔ {_rel(dest)}")
                else:
                    shutil.move(str(file), str(dest))
                    print(f"  [ĐÃ ARCHIVE] {_rel(file)} ➔ {_rel(dest)}")

    action_label = "Sẽ lưu trữ" if dry_run else "Đã lưu trữ an toàn"
    print(f"✅ Hoàn tất: {action_label} {moved_count} file timestamp vào {ARCHIVE_DIR.name}/.\n")
    return moved_count


def main():
    parser = argparse.ArgumentParser(description="Thu gom rác an toàn cho BMAD rooms.")
    parser.add_argument("--task-id", type=str, help="Work Item / Task ID cần dọn dẹp (VD: 889, WI-65)")
    parser.add_argument("--sweep", action="store_true", help="Quét dọn an toàn file cũ hơn N ngày (chỉ dọn task đã Closed)")
    parser.add_argument("--days", type=int, default=14, help="Số ngày tuổi để quét dọn (mặc định: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra, không di chuyển file")
    parser.add_argument("--force", action="store_true", help="Bỏ qua kiểm tra Harness state (nguy hiểm, chỉ dùng khi khẩn cấp)")
    parser.add_argument("--migrate-legacy", action="store_true", help="Xóa sạch mọi file handoff_*.md cũ có timestamp trong bmad/rooms/, chỉ giữ latest_handoff.md và khởi tạo room_ledger.json")
    parser.add_argument("--clean-timestamped", action="store_true", help="Dọn dẹp các file timestamp tạm thời (review_*, intake_memo_*, minutes_*) vào bmad/rooms/archive/")
    args = parser.parse_args()

    if not args.task_id and not args.sweep and not args.migrate_legacy and not args.clean_timestamped:
        parser.print_help()
        print("\nLỗi: Cần truyền --task-id <id>, --sweep, --migrate-legacy, hoặc --clean-timestamped.")
        sys.exit(1)

    if args.migrate_legacy:
        migrate_legacy(dry_run=args.dry_run)

    if args.clean_timestamped:
        clean_timestamped_files(dry_run=args.dry_run)

    if args.task_id:
        cleanup_by_task(args.task_id, dry_run=args.dry_run, force=args.force)

    if args.sweep:
        sweep_safe(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
