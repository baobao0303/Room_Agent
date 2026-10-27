#!/usr/bin/env python3
"""
tools/graph_sync.py - Floci S3 synchronization for Understand-Anything knowledge graphs.
Pushes and pulls knowledge-graph.json between local workspace and Floci S3.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Ensure tools and workspace root are in import path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from tools.floci_client import FlociHarnessDB, FLOCI_S3_BUCKET


def find_graph_file(project_path: Union[str, Path]) -> Path:
    """Find knowledge-graph.json in .ua/ or .understand-anything/ inside project_path."""
    base = Path(project_path).resolve()
    if base.is_file() and base.name == "knowledge-graph.json":
        return base

    candidates = [
        base / ".ua" / "knowledge-graph.json",
        base / ".understand-anything" / "knowledge-graph.json",
    ]
    for c in candidates:
        if c.is_file():
            return c

    raise FileNotFoundError(
        f"knowledge-graph.json not found in {base / '.ua'} or {base / '.understand-anything'}"
    )


def _is_not_found_error(err: Exception) -> bool:
    """Check if exception represents a missing S3 object."""
    if hasattr(err, "response") and isinstance(err.response, dict):
        code = err.response.get("Error", {}).get("Code")
        if code in ("NoSuchKey", "404", "NotFound"):
            return True
    err_str = str(err).lower()
    return "nosuchkey" in err_str or "not found" in err_str or "404" in err_str


def push_graph(
    project_path: Union[str, Path] = ".",
    commit_sha: Optional[str] = None,
    dry_run: bool = False,
    db: Optional[FlociHarnessDB] = None,
    project_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Push local knowledge-graph.json to Floci S3."""
    base = Path(project_path).resolve()
    graph_file = find_graph_file(base)

    if not project_name:
        project_name = base.name if base.is_dir() else base.parent.name

    raw_text = graph_file.read_text(encoding="utf-8")
    # Validate JSON payload integrity
    json.loads(raw_text)
    raw_bytes = raw_text.encode("utf-8")

    keys = [f"graphs/{project_name}/latest.json"]
    if commit_sha:
        keys.append(f"graphs/{project_name}/commits/{commit_sha}.json")

    bucket = FLOCI_S3_BUCKET
    if db is not None:
        bucket = getattr(db, "s3_bucket", FLOCI_S3_BUCKET) or FLOCI_S3_BUCKET

    if dry_run:
        return {
            "status": "dry_run",
            "action": "push",
            "project": project_name,
            "source_file": str(graph_file),
            "bucket": bucket,
            "keys": keys,
            "bytes": len(raw_bytes),
        }

    if db is None:
        db = FlociHarnessDB()

    bucket = getattr(db, "s3_bucket", FLOCI_S3_BUCKET) or FLOCI_S3_BUCKET
    s3 = getattr(db, "s3_client", None)

    if s3 is None or not db.is_floci_reachable():
        raise ConnectionError(
            f"Floci S3 is offline or unreachable at {getattr(db, 'endpoint_url', 'unknown')}"
        )

    # Ensure bucket exists
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        try:
            s3.create_bucket(Bucket=bucket)
        except Exception:
            pass

    for key in keys:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=raw_bytes,
            ContentType="application/json",
        )

    return {
        "status": "success",
        "action": "push",
        "project": project_name,
        "source_file": str(graph_file),
        "bucket": bucket,
        "uploaded_keys": keys,
        "bytes": len(raw_bytes),
    }


def pull_graph(
    project_path: Union[str, Path] = ".",
    commit_sha: Optional[str] = None,
    fallback_latest: bool = True,
    dry_run: bool = False,
    db: Optional[FlociHarnessDB] = None,
    project_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Pull knowledge-graph.json from Floci S3 to project_path/.ua/knowledge-graph.json."""
    base = Path(project_path).resolve()
    dest_file = base / ".ua" / "knowledge-graph.json"

    if not project_name:
        project_name = base.name

    latest_key = f"graphs/{project_name}/latest.json"
    commit_key = f"graphs/{project_name}/commits/{commit_sha}.json" if commit_sha else None
    target_key = commit_key or latest_key

    bucket = FLOCI_S3_BUCKET
    if db is not None:
        bucket = getattr(db, "s3_bucket", FLOCI_S3_BUCKET) or FLOCI_S3_BUCKET

    if dry_run:
        return {
            "status": "dry_run",
            "action": "pull",
            "project": project_name,
            "commit_sha": commit_sha,
            "fallback_latest": fallback_latest,
            "bucket": bucket,
            "target_key": target_key,
            "destination": str(dest_file),
        }

    if db is None:
        db = FlociHarnessDB()

    bucket = getattr(db, "s3_bucket", FLOCI_S3_BUCKET) or FLOCI_S3_BUCKET
    s3 = getattr(db, "s3_client", None)

    if s3 is None or not db.is_floci_reachable():
        raise ConnectionError(
            f"Floci S3 is offline or unreachable at {getattr(db, 'endpoint_url', 'unknown')}"
        )

    pulled_key: Optional[str] = None
    body_bytes: Optional[bytes] = None

    if commit_key:
        try:
            resp = s3.get_object(Bucket=bucket, Key=commit_key)
            body = resp["Body"].read()
            body_bytes = body.encode("utf-8") if isinstance(body, str) else body
            pulled_key = commit_key
        except Exception as err:
            if fallback_latest and _is_not_found_error(err):
                try:
                    resp = s3.get_object(Bucket=bucket, Key=latest_key)
                    body = resp["Body"].read()
                    body_bytes = body.encode("utf-8") if isinstance(body, str) else body
                    pulled_key = latest_key
                except Exception as fb_err:
                    raise FileNotFoundError(
                        f"Knowledge graph not found in S3 for '{project_name}'. "
                        f"Commit key '{commit_key}' failed ({err}) and fallback '{latest_key}' failed ({fb_err})"
                    ) from fb_err
            else:
                raise FileNotFoundError(
                    f"Knowledge graph not found in S3 for '{project_name}' at key '{commit_key}': {err}"
                ) from err
    else:
        try:
            resp = s3.get_object(Bucket=bucket, Key=latest_key)
            body = resp["Body"].read()
            body_bytes = body.encode("utf-8") if isinstance(body, str) else body
            pulled_key = latest_key
        except Exception as err:
            raise FileNotFoundError(
                f"Knowledge graph not found in S3 for '{project_name}' at key '{latest_key}': {err}"
            ) from err

    # Validate JSON payload before writing
    json.loads(body_bytes.decode("utf-8"))

    # Atomic write to prevent local file corruption
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = dest_file.with_name(f"{dest_file.name}.tmp.{os.getpid()}")
    try:
        tmp_file.write_bytes(body_bytes)
        tmp_file.replace(dest_file)
    finally:
        if tmp_file.exists():
            tmp_file.unlink(missing_ok=True)

    return {
        "status": "success",
        "action": "pull",
        "project": project_name,
        "bucket": bucket,
        "pulled_key": pulled_key,
        "destination": str(dest_file),
        "bytes": len(body_bytes),
    }


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser for graph_sync."""
    parser = argparse.ArgumentParser(
        description="Synchronize knowledge graph between local workspace and Floci S3."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # push
    p_push = subparsers.add_parser("push", help="Push knowledge-graph.json to Floci S3")
    p_push.add_argument(
        "project_path",
        nargs="?",
        default=None,
        help="Path to project directory (default: current directory)",
    )
    p_push.add_argument("--project", default=None, help="Path to project directory")
    p_push.add_argument("--commit", default=None, help="Optional commit SHA for versioned snapshot")
    p_push.add_argument("--project-name", "-n", default=None, help="Override project name in S3 key")
    p_push.add_argument("--dry-run", action="store_true", help="Simulate upload without writing to S3")
    p_push.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # pull
    p_pull = subparsers.add_parser("pull", help="Pull knowledge-graph.json from Floci S3")
    p_pull.add_argument(
        "project_path",
        nargs="?",
        default=None,
        help="Path to project directory (default: current directory)",
    )
    p_pull.add_argument("--project", default=None, help="Path to project directory")
    p_pull.add_argument("--commit", default=None, help="Commit SHA to pull")
    p_pull.add_argument("--project-name", "-n", default=None, help="Override project name in S3 key")
    p_pull.add_argument(
        "--no-fallback",
        action="store_false",
        dest="fallback_latest",
        default=True,
        help="Disable fallback to latest.json if commit not found",
    )
    p_pull.add_argument("--dry-run", action="store_true", help="Simulate download without writing to local file")
    p_pull.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_path = args.project or args.project_path or "."

    try:
        if args.command == "push":
            res = push_graph(
                project_path=project_path,
                commit_sha=args.commit,
                dry_run=args.dry_run,
                project_name=args.project_name,
            )
        elif args.command == "pull":
            res = pull_graph(
                project_path=project_path,
                commit_sha=args.commit,
                fallback_latest=args.fallback_latest,
                dry_run=args.dry_run,
                project_name=args.project_name,
            )
        else:
            parser.print_help(sys.stderr)
            return 1

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            bucket = res.get("bucket", FLOCI_S3_BUCKET)
            if args.command == "push":
                prefix = "[DRY RUN] " if args.dry_run else ""
                print(f"{prefix}Knowledge graph pushed for project '{res['project']}' ({res['bytes']} bytes):")
                keys = res.get("uploaded_keys") or res.get("keys", [])
                for k in keys:
                    print(f"  - s3://{bucket}/{k}")
            elif args.command == "pull":
                prefix = "[DRY RUN] " if args.dry_run else ""
                print(f"{prefix}Knowledge graph pulled for project '{res['project']}':")
                if args.dry_run:
                    print(f"  Target key: s3://{bucket}/{res['target_key']}")
                else:
                    print(f"  Source key: s3://{bucket}/{res['pulled_key']}")
                    print(f"  Destination: {res['destination']} ({res['bytes']} bytes)")
        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
