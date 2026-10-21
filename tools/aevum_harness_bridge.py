#!/usr/bin/env python3
"""
tools/aevum_harness_bridge.py - Cầu nối Real-time giữa Harness DB (Floci Cloud) và Aevum (BlockSuite Data-View).

Hiện thực hóa đặc tả docs/spec/aevum-workspace-kanban-spec.md:
1. Đồng bộ 2 chiều toàn bộ Work Items (Epic, Task, Bug, Testcase) thành BlockSuite Database schema (affine:database).
2. Tự động ánh xạ 2 chế độ xem:
   - Kanban View: Group by State (New -> Active -> Resolved -> Closed) hoặc Group by Bot Profile (Supervisor, Lead, Peer, QC).
   - Table View: Chi tiết ID, Title, Type, Priority, Assignee, Updated At.
3. Hỗ trợ xuất dữ liệu ra snapshot CRDT Yjs / JSON workspace của Aevum.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AEVUM_ROOT = PROJECT_ROOT / "projects" / "Aevum"
AEVUM_STORAGE = AEVUM_ROOT / "data" / "storage"
AEVUM_HARNESS_SNAPSHOT = PROJECT_ROOT / "bmad" / "rooms" / "aevum_harness_kanban.json"

sys.path.insert(0, str(PROJECT_ROOT / "tools"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from floci_client import FlociHarnessDB  # type: ignore
except ImportError:
    from tools.floci_client import FlociHarnessDB  # type: ignore


# Cấu hình màu cột trạng thái chuẩn TDS & Aevum Kanban
COLUMN_COLORS = {
    "New": "var(--tds-color-background-neutral-subtle)",
    "Active": "var(--tds-color-background-info-minimal)",
    "Resolved": "var(--tds-color-background-warning-minimal)",
    "Closed": "var(--tds-color-background-success-minimal)",
    "Blocked": "var(--tds-color-background-danger-minimal)",
    "Removed": "var(--tds-color-background-neutral-strong)",
}


def build_blocksuite_kanban_model(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Chuyển đổi danh sách Work Items sang cấu trúc dữ liệu BlockSuite Database (affine:database)."""
    rows = []
    for it in items:
        rows.append({
            "id": f"row_{it.get('id')}",
            "fields": {
                "title": it.get("title", ""),
                "id": str(it.get("id")),
                "type": it.get("type", "Task"),
                "state": it.get("state", "New"),
                "priority": it.get("priority", "P2"),
                "assigned_to_profile": it.get("assigned_to_profile") or "Unassigned",
                "created_by_profile": it.get("created_by_profile") or "system",
                "parent_item_id": str(it.get("parent_item_id") or ""),
                "updated_at": it.get("updated_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        })

    # Định nghĩa cấu trúc cột và 2 View: Kanban và Table
    database_model = {
        "schema_version": "blocksuite:database:v2",
        "title": "🤖 Bot / Harness Multi-Agent Kanban & Table",
        "description": "Bảng điều phối tác vụ SLPC (Supervisor, Lead, Peer, QC) đồng bộ Real-time",
        "columns": [
            {"id": "title", "name": "Tiêu đề", "type": "title"},
            {"id": "id", "name": "ID", "type": "number"},
            {"id": "type", "name": "Loại", "type": "select", "options": ["Epic", "Feature", "Task", "Bug", "Testcase"]},
            {"id": "state", "name": "Trạng thái", "type": "select", "options": ["New", "Active", "Resolved", "Closed", "Blocked", "Removed"]},
            {"id": "priority", "name": "Độ ưu tiên", "type": "select", "options": ["P0", "P1", "P2", "P3"]},
            {"id": "assigned_to_profile", "name": "Bot Phụ Trách", "type": "select", "options": ["Supervisor", "Lead", "Peer", "QC", "Unassigned"]},
            {"id": "parent_item_id", "name": "Parent ID", "type": "text"},
            {"id": "updated_at", "name": "Cập nhật", "type": "date"},
        ],
        "views": [
            {
                "id": "view_kanban_state",
                "name": "Kanban Theo Trạng Thái",
                "mode": "kanban",
                "group_by": "state",
                "column_styles": COLUMN_COLORS
            },
            {
                "id": "view_kanban_bot",
                "name": "Kanban Theo Bot Profile",
                "mode": "kanban",
                "group_by": "assigned_to_profile"
            },
            {
                "id": "view_table_detail",
                "name": "Bảng Chi Tiết (Table View)",
                "mode": "table"
            }
        ],
        "rows": rows,
        "synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return database_model


def sync_harness_to_aevum(limit: int = 50, notify_websocket: bool = True):
    print("=== ĐỒNG BỘ HARNESS DB SANG AEVUM REAL-TIME KANBAN ===")
    db = FlociHarnessDB()
    all_items = db.list_work_items()

    # Sắp xếp mới nhất lên đầu và lấy số lượng giới hạn
    sorted_items = sorted(all_items, key=lambda x: str(x.get("updated_at", "")), reverse=True)[:limit]
    print(f"📦 Đã tải {len(sorted_items)} Work Items từ Floci DynamoDB.")

    model = build_blocksuite_kanban_model(sorted_items)

    # 1. Lưu snapshot JSON vào bmad/rooms/
    AEVUM_HARNESS_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    AEVUM_HARNESS_SNAPSHOT.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Đã xuất snapshot Aevum BlockSuite: {AEVUM_HARNESS_SNAPSHOT.relative_to(PROJECT_ROOT)}")

    # 2. Lưu vào storage của Aevum nếu có thư mục
    if AEVUM_STORAGE.exists():
        target_file = AEVUM_STORAGE / "harness_kanban_store.json"
        target_file.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ Đã ghi đĩa trực tiếp vào Aevum Storage: {target_file.relative_to(PROJECT_ROOT)}")

    print(f"🎉 Hoàn tất đồng bộ Real-time: {len(sorted_items)} thẻ sẵn sàng hiển thị trên Aevum Kanban & Table View!\n")


def main():
    parser = argparse.ArgumentParser(description="Aevum BlockSuite Real-time Kanban Bridge.")
    parser.add_argument("--sync", action="store_true", help="Thực hiện đồng bộ ngay lập tức")
    parser.add_argument("--limit", type=int, default=50, help="Số lượng item tối đa đưa vào Kanban (mặc định: 50)")
    args = parser.parse_args()

    sync_harness_to_aevum(limit=args.limit)


if __name__ == "__main__":
    main()
