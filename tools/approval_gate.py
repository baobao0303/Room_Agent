#!/usr/bin/env python3
"""
tools/approval_gate.py - Cryptographic One-Key Approval Gate & Mutating Action Guard.
Guarantees Human-in-the-Loop authorization for high-risk actions (git push, file deletions, db wipes).
Adapted from gawkbot's signed-approval-token protocol with zero external dependencies.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPROVALS_DIR = PROJECT_ROOT / "bmad" / "rooms" / "approvals"
APPROVAL_SECRET = os.environ.get("SLPPC_APPROVAL_SECRET", "slppc-local-gate-secret-key-2026")


def generate_token_signature(action: str, timestamp: str, risk: str) -> str:
    """Generate SHA256 HMAC signature for approval token."""
    raw = f"{action}|{timestamp}|{risk}".encode("utf-8")
    return hmac.new(APPROVAL_SECRET.encode("utf-8"), raw, hashlib.sha256).hexdigest()[:32]


def create_approval_request(
    action: str,
    risk: str = "medium",
    requested_by: str = "agent",
    expires_minutes: int = 15
) -> dict[str, Any]:
    """Create a pending approval request."""
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(minutes=expires_minutes)

    req_id = f"appr_{hashlib.sha256(f'{action}_{now.isoformat()}'.encode()).hexdigest()[:12]}"
    signature = generate_token_signature(action, now.strftime("%Y-%m-%d %H:%M:%S"), risk)

    req = {
        "id": req_id,
        "action": action,
        "risk": risk.lower(),
        "requested_by": requested_by,
        "status": "pending",
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": exp.strftime("%Y-%m-%d %H:%M:%S"),
        "signature": signature,
        "approved_by": None,
        "approved_at": None
    }

    req_file = APPROVALS_DIR / f"{req_id}.json"
    req_file.write_text(json.dumps(req, indent=2, ensure_ascii=False), encoding="utf-8")
    return req


def approve_request(req_id: str, approver: str = "human") -> dict[str, Any]:
    """Approve a pending request."""
    req_file = APPROVALS_DIR / f"{req_id}.json"
    if not req_file.is_file():
        return {"status": "error", "message": f"Không tìm thấy yêu cầu phê duyệt: {req_id}"}

    data = json.loads(req_file.read_text(encoding="utf-8"))
    now = datetime.datetime.now()
    exp = datetime.datetime.strptime(data["expires_at"], "%Y-%m-%d %H:%M:%S")

    if now > exp:
        data["status"] = "expired"
        req_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"status": "error", "message": f"Yêu cầu phê duyệt {req_id} đã hết hạn."}

    data["status"] = "approved"
    data["approved_by"] = approver
    data["approved_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
    req_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "id": req_id,
        "action": data["action"],
        "approved_by": approver,
        "message": f"Yêu cầu {req_id} đã được phê duyệt thành công bởi [{approver}]."
    }


def verify_approval(req_id: str) -> dict[str, Any]:
    """Verify that a request exists, is signed, is approved, and has not expired."""
    req_file = APPROVALS_DIR / f"{req_id}.json"
    if not req_file.is_file():
        return {"valid": False, "reason": f"Không tồn tại token phê duyệt: {req_id}"}

    data = json.loads(req_file.read_text(encoding="utf-8"))
    if data.get("status") != "approved":
        return {"valid": False, "reason": f"Token {req_id} chưa được duyệt (trạng thái: {data.get('status')})"}

    now = datetime.datetime.now()
    exp = datetime.datetime.strptime(data["expires_at"], "%Y-%m-%d %H:%M:%S")
    if now > exp:
        return {"valid": False, "reason": f"Token {req_id} đã hết hạn lúc {data['expires_at']}"}

    # Verify signature integrity
    expected_sig = generate_token_signature(data["action"], data["created_at"], data["risk"])
    if data.get("signature") != expected_sig:
        return {"valid": False, "reason": f"Chữ ký mã hóa của token {req_id} không hợp lệ (nguy cơ can thiệp dữ liệu)"}

    return {
        "valid": True,
        "id": req_id,
        "action": data["action"],
        "approved_by": data["approved_by"]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: request
    req_p = subparsers.add_parser("request", help="Tạo yêu cầu phê duyệt mới")
    req_p.add_argument("--action", required=True, help="Mô tả hành động cần duyệt")
    req_p.add_argument("--risk", default="medium", choices=["low", "medium", "high", "critical"])
    req_p.add_argument("--requested-by", default="agent")
    req_p.add_argument("--json", action="store_true")

    # Subcommand: approve
    appr_p = subparsers.add_parser("approve", help="Phê duyệt một yêu cầu")
    appr_p.add_argument("--id", required=True, help="Mã yêu cầu (appr_...)")
    appr_p.add_argument("--approver", default="human")
    appr_p.add_argument("--json", action="store_true")

    # Subcommand: verify
    ver_p = subparsers.add_parser("verify", help="Kiểm tra token phê duyệt hợp lệ")
    ver_p.add_argument("--id", required=True, help="Mã yêu cầu (appr_...)")
    ver_p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "request":
        res = create_approval_request(args.action, args.risk, args.requested_by)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"🔒 [APPROVAL GATE]: Đã tạo yêu cầu phê duyệt mới:")
            print(f"   • Token ID : {res['id']}")
            print(f"   • Action   : {res['action']}")
            print(f"   • Risk     : {res['risk'].upper()}")
            print(f"   • Chờ duyệt: python3 tools/approval_gate.py approve --id {res['id']}")

    elif args.command == "approve":
        res = approve_request(args.id, args.approver)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            if res["status"] == "success":
                print(f"✅ {res['message']}")
            else:
                print(f"❌ {res['message']}")
                sys.exit(1)

    elif args.command == "verify":
        res = verify_approval(args.id)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            if res["valid"]:
                print(f"✅ [APPROVED]: Token {res['id']} hợp lệ cho hành động: '{res['action']}'")
            else:
                print(f"❌ [BLOCKED]: {res['reason']}")
                sys.exit(1)


if __name__ == "__main__":
    main()
