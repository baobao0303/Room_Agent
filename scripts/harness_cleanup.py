#!/usr/bin/env python3
"""Chuẩn hóa assigned_to_profile + (tùy chọn) gỡ item test trên Harness (Floci).
Mặc định dry-run. Thêm --apply để ghi. Chỉ đụng item source != remote.

  python3 scripts/harness_cleanup.py                       # xem trước
  python3 scripts/harness_cleanup.py --apply               # đổi tên profile
  python3 scripts/harness_cleanup.py --remove-ids 1-9,16 --apply   # + set state=Removed
"""
import argparse, os, sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from tools.floci_client import FlociHarnessDB

# ponytail: map cố định; peer-qa / peer-eng chưa có profile chuẩn -> chỉ báo, không tự đoán.
PROFILE_MAP = {"lead": "Lead", "peer": "Peer", "peer-dev": "Peer Dev"}


def parse_ids(s):
    out = set()
    for part in filter(None, s.split(",")):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--remove-ids", default="", help="vd: 1-9,16 (state -> Removed)")
    args = ap.parse_args()
    remove = parse_ids(args.remove_ids)

    db = FlociHarnessDB()
    table = db.ddb_resource.Table("harness_work_items")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unmapped = {}

    for it in db.list_work_items():
        if it.get("source") == "remote":
            continue
        iid, prof = int(it["id"]), it.get("assigned_to_profile")
        sets, vals, names = [], {}, {}
        if prof in PROFILE_MAP:
            sets.append("assigned_to_profile = :p"); vals[":p"] = PROFILE_MAP[prof]
        elif prof and prof not in PROFILE_MAP.values() and prof not in (
            "Lead BA", "Peer BA", "Lead design", "Peer Design", "Lead Dev", "Peer Dev", "Supervisor"
        ):
            unmapped.setdefault(prof, []).append(iid)
        if iid in remove and it.get("state") != "Removed":
            sets.append("#st = :s"); vals[":s"] = "Removed"; names["#st"] = "state"
        if not sets:
            continue
        print(f"#{iid}: {', '.join(f'{k}={v}' for k, v in vals.items())}")
        if args.apply:
            kw = {"ExpressionAttributeNames": names} if names else {}
            table.update_item(
                Key={"id": iid},
                UpdateExpression="SET " + ", ".join(sets) + ", updated_at = :u",
                ExpressionAttributeValues={**vals, ":u": now},
                **kw,
            )

    if unmapped:
        print("Chưa map (tự quyết):", unmapped)
    print("APPLIED" if args.apply else "DRY-RUN (thêm --apply để ghi)")


if __name__ == "__main__":
    main()
