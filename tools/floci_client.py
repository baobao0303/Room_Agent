"""
tools/floci_client.py - Floci DynamoDB & S3 Client for Harness Operating Framework.
Transparently supports Floci emulation endpoint on local / host network.
"""
from __future__ import annotations

import os
import sys
import re
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime

import glob
import sqlite3


# Transparent auto-discovery of boto3 site-packages if missing from system python
try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError
except ImportError:
    for pattern in [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../.venv/lib/python*/site-packages")),
        os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python*/site-packages"),
        os.path.expanduser("~/ponytail/venv/lib/python*/site-packages"),
        os.path.expanduser("~/.venv/lib/python*/site-packages"),
    ]:
        matches = glob.glob(pattern)
        if matches:
            sys.path.insert(0, matches[0])
            break
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr
        from botocore.exceptions import ClientError
    except ImportError:
        boto3 = None  # type: ignore
        Key = None  # type: ignore
        Attr = None  # type: ignore
        ClientError = Exception  # type: ignore

# Load .env configuration
def load_env():
    env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

load_env()

FLOCI_ENDPOINT = os.getenv("FLOCI_ENDPOINT", "http://<FLOCI_HOST>:14566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "floci_local_key")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "floci_local_secret")
FLOCI_S3_BUCKET = os.getenv("FLOCI_S3_BUCKET", "harness-data")

class DecimalEncoder:
    """Helper to convert DynamoDB Decimal to Python int/float/str."""
    @staticmethod
    def decode(obj: Any) -> Any:
        if isinstance(obj, list):
            return [DecimalEncoder.decode(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: DecimalEncoder.decode(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return obj

import json
import socket
import time
from pathlib import Path
from urllib.parse import urlparse


def _resolve_shared_root(default_root: Path) -> Path:
    override = os.environ.get("SLPPC_SHARED_ROOT")
    if override:
        p = Path(override)
        if os.access(p, os.R_OK | os.W_OK):
            return p
    git_entry = default_root / ".git"
    try:
        if git_entry.is_file():
            raw = git_entry.read_text(encoding="utf-8").strip()
            if raw.startswith("gitdir:"):
                gitdir = Path(raw.split("gitdir:", 1)[1].strip())
                if not gitdir.is_absolute():
                    gitdir = (default_root / gitdir).resolve()
                if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
                    main_root = gitdir.parent.parent.parent
                    if os.access(main_root, os.R_OK | os.W_OK):
                        return main_root
    except Exception:
        pass
    return default_root


_SHARED_ROOT = _resolve_shared_root(Path(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))))
(_SHARED_ROOT / ".harness").mkdir(parents=True, exist_ok=True)
LOCAL_DB_PATH = str(_SHARED_ROOT / ".harness" / "local_db.json")


def _get_sqlite_harness_db_path() -> Path:
    if os.environ.get("HARNESS_DB"):
        p = Path(os.environ["HARNESS_DB"])
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    p = Path(_SHARED_ROOT) / ".harness" / "harness.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _ensure_sqlite_experience_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS harness_experience (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            domain               TEXT    NOT NULL,
            work_item_id         INTEGER,
            cue                  TEXT    NOT NULL,
            lesson               TEXT    NOT NULL,
            evidence             TEXT    NOT NULL,
            confidence           TEXT    NOT NULL DEFAULT 'medium'
                                 CHECK(confidence IN ('low', 'medium', 'high')),
            harness_patch        TEXT,
            created_at           TEXT    NOT NULL DEFAULT (datetime('now')),
            pattern_hash         TEXT,
            successful_harness   TEXT,
            failure_trajectories TEXT
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_harness_experience_domain ON harness_experience(domain);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_harness_experience_work_item ON harness_experience(work_item_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_exp_domain_pattern ON harness_experience(domain, pattern_hash);")


_REACHABLE_CACHE = {"ok": None, "checked_at": 0.0}



def _check_endpoint_reachable(endpoint_url: str) -> bool:
    now = time.time()
    ttl = 15.0 if _REACHABLE_CACHE["ok"] else 2.0
    if _REACHABLE_CACHE["ok"] is not None and (now - _REACHABLE_CACHE["checked_at"] < ttl):
        return bool(_REACHABLE_CACHE["ok"])
    try:
        parsed = urlparse(endpoint_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=1.0):
            _REACHABLE_CACHE["ok"] = True
            _REACHABLE_CACHE["checked_at"] = now
            return True
    except Exception:
        _REACHABLE_CACHE["ok"] = False
        _REACHABLE_CACHE["checked_at"] = now
        return False


def _load_local_store() -> Dict[str, Any]:
    if os.path.exists(LOCAL_DB_PATH):
        try:
            with open(LOCAL_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("metadata", {})
                    data.setdefault("work_items", {})
                    data.setdefault("stories", {})
                    data.setdefault("tools", {})
                    data.setdefault("skills", {})
                    data.setdefault("skills_inverted_index", {})
                    data.setdefault("experiences", [])
                    return data
        except Exception:
            pass
    return {"metadata": {}, "work_items": {}, "stories": {}, "tools": {}, "skills": {}, "skills_inverted_index": {}, "experiences": []}


def _save_local_store(store: Dict[str, Any]) -> None:
    try:
        with open(LOCAL_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False)
    except Exception:
        pass


def _normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(item, dict):
        return item
    out = dict(item)
    raw_prof = str(out.get("assigned_to_profile") or "").strip()
    p_low = raw_prof.lower()
    if p_low not in ("supervisor", "lead", "peer", "qc"):
        if p_low.startswith("peer"):
            if p_low != "peer" and not out.get("assigned_to"):
                out["assigned_to"] = raw_prof
            out["assigned_to_profile"] = "peer"
        elif p_low.startswith("lead"):
            if p_low != "lead" and not out.get("assigned_to"):
                out["assigned_to"] = raw_prof
            out["assigned_to_profile"] = "lead"
        elif p_low.startswith("sup"):
            out["assigned_to_profile"] = "supervisor"
        elif p_low.startswith("qc") or p_low.startswith("qa"):
            out["assigned_to_profile"] = "qc"
        else:
            wtype = str(out.get("type") or "").strip().lower()
            if wtype == "epic":
                out["assigned_to_profile"] = "supervisor"
            elif wtype in ("feature", "user story", "story"):
                out["assigned_to_profile"] = "lead"
            elif wtype in ("testcase", "test case", "bug"):
                out["assigned_to_profile"] = "qc"
            else:
                out["assigned_to_profile"] = "peer"

    raw_src = str(out.get("source") or "local").strip().lower()
    out["source"] = "tfs" if raw_src == "tfs" else "local"
    return out


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he",
    "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were",
    "will", "with", "this", "but", "they", "have", "had", "what", "when",
    "where", "who", "which", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "can", "just", "should", "now",
    "của", "và", "là", "cho", "các", "những", "trong", "được", "có", "này", "với"
}


def tokenize_for_search(text: str) -> List[str]:
    """Tokenize and normalize text for inverted indexing and search."""
    if not text:
        return []
    expanded = re.sub(r"[-_./]", " ", str(text))
    tokens = re.findall(r"[a-zA-Z0-9]+", (str(text) + " " + expanded).lower())
    result = []
    seen = set()
    for tok in tokens:
        if len(tok) >= 2 and tok not in STOP_WORDS and tok not in seen:
            seen.add(tok)
            result.append(tok)
    return result


class FlociHarnessDB:
    def __init__(
        self,
        endpoint_url: str = FLOCI_ENDPOINT,
        region_name: str = AWS_REGION,
        aws_access_key_id: str = AWS_ACCESS_KEY_ID,
        aws_secret_access_key: str = AWS_SECRET_ACCESS_KEY,
        s3_bucket: str = FLOCI_S3_BUCKET
    ):
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3_bucket = s3_bucket

        if boto3 is not None:
            from botocore.config import Config
            boto_cfg = Config(
                connect_timeout=1.5,
                read_timeout=10,
                retries={"max_attempts": 1, "mode": "standard"}
            )

            self.ddb_resource = boto3.resource(
                "dynamodb",
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                config=boto_cfg
            )
            self.ddb_client = boto3.client(
                "dynamodb",
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                config=boto_cfg
            )
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                config=boto_cfg
            )
        else:
            self.ddb_resource = None
            self.ddb_client = None
            self.s3_client = None

    def _is_online(self) -> bool:
        if boto3 is None:
            return False
        return _check_endpoint_reachable(self.endpoint_url)

    def is_floci_reachable(self) -> bool:
        """Check whether Floci DynamoDB endpoint is reachable."""
        return self._is_online()

    def init_schema(self) -> Dict[str, Any]:
        """Create tables in DynamoDB and bucket in S3 on Floci if they do not exist."""
        if not self._is_online():
            store = _load_local_store()
            _save_local_store(store)
            return {
                "status": "local_fallback",
                "endpoint": LOCAL_DB_PATH,
                "created_tables": [],
                "existing_tables": ["harness_metadata", "harness_work_items", "harness_stories", "harness_tools", "harness_skills", "harness_skills_index"],
                "s3_bucket": self.s3_bucket
            }

        existing_tables = self.ddb_client.list_tables().get("TableNames", [])
        created_tables = []

        schemas = {
            "harness_metadata": {
                "KeySchema": [{"AttributeName": "key", "KeyType": "HASH"}],
                "AttributeDefinitions": [{"AttributeName": "key", "AttributeType": "S"}]
            },
            "harness_work_items": {
                "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
                "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}]
            },
            "harness_stories": {
                "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
                "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "N"}]
            },
            "harness_tools": {
                "KeySchema": [{"AttributeName": "name", "KeyType": "HASH"}],
                "AttributeDefinitions": [{"AttributeName": "name", "AttributeType": "S"}]
            },
            "harness_skills": {
                "KeySchema": [{"AttributeName": "name", "KeyType": "HASH"}],
                "AttributeDefinitions": [{"AttributeName": "name", "AttributeType": "S"}]
            },
            "harness_skills_index": {
                "KeySchema": [{"AttributeName": "token", "KeyType": "HASH"}, {"AttributeName": "skill_name", "KeyType": "RANGE"}],
                "AttributeDefinitions": [
                    {"AttributeName": "token", "AttributeType": "S"},
                    {"AttributeName": "skill_name", "AttributeType": "S"}
                ]
            },
            "harness_experience": {
                "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"},
                    {"AttributeName": "domain", "AttributeType": "S"},
                    {"AttributeName": "created_at", "AttributeType": "S"},
                    {"AttributeName": "work_item_id", "AttributeType": "S"}
                ],
                "GlobalSecondaryIndexes": [
                    {
                        "IndexName": "domain-index",
                        "KeySchema": [
                            {"AttributeName": "domain", "KeyType": "HASH"},
                            {"AttributeName": "created_at", "KeyType": "RANGE"}
                        ],
                        "Projection": {"ProjectionType": "ALL"}
                    },
                    {
                        "IndexName": "workitem-index",
                        "KeySchema": [
                            {"AttributeName": "work_item_id", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"}
                    }
                ]
            }
        }

        for table_name, schema in schemas.items():
            if table_name not in existing_tables:
                create_kwargs = {
                    "TableName": table_name,
                    "KeySchema": schema["KeySchema"],
                    "AttributeDefinitions": schema["AttributeDefinitions"],
                    "BillingMode": "PAY_PER_REQUEST"
                }
                if "GlobalSecondaryIndexes" in schema:
                    create_kwargs["GlobalSecondaryIndexes"] = schema["GlobalSecondaryIndexes"]
                self.ddb_client.create_table(**create_kwargs)
                created_tables.append(table_name)

        try:
            existing_buckets = [b["Name"] for b in self.s3_client.list_buckets().get("Buckets", [])]
            if self.s3_bucket not in existing_buckets:
                self.s3_client.create_bucket(Bucket=self.s3_bucket)
        except Exception:
            pass

        return {
            "status": "success",
            "endpoint": self.endpoint_url,
            "created_tables": created_tables,
            "existing_tables": existing_tables,
            "s3_bucket": self.s3_bucket
        }

    def get_next_id(self, counter_key: str = "work_item_id") -> int:
        """Atomically generate the next sequential numeric ID."""
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_metadata")
                res = table.update_item(
                    Key={"key": counter_key},
                    UpdateExpression="ADD #val :incr",
                    ExpressionAttributeNames={"#val": "value"},
                    ExpressionAttributeValues={":incr": 1},
                    ReturnValues="UPDATED_NEW"
                )
                return int(res["Attributes"]["value"])
            except Exception:
                pass
        store = _load_local_store()
        cur = int(store["metadata"].get(counter_key, 0))
        if cur == 0 and counter_key == "work_item_id" and store["work_items"]:
            cur = max(int(k) for k in store["work_items"].keys())
        nxt = cur + 1
        store["metadata"][counter_key] = nxt
        _save_local_store(store)
        return nxt

    # --- Work Items CRUD ---
    def _sync_item_to_s3(self, item: Dict[str, Any]) -> None:
        if not self.s3_client or "id" not in item:
            return
        try:
            key = f"work-items/item-{item['id']}.json"
            body = json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8")
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=body,
                ContentType="application/json"
            )
        except Exception:
            pass

    def _delete_item_from_s3(self, item_id: int) -> None:
        if not self.s3_client:
            return
        try:
            key = f"work-items/item-{item_id}.json"
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=key)
        except Exception:
            pass

    def put_work_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        if "id" not in item or item["id"] is None:
            item["id"] = self.get_next_id("work_item_id")
        if "source" not in item or not item["source"]:
            item["source"] = "local"

        cleaned = _normalize_item({k: v for k, v in item.items() if v is not None})
        decoded = _normalize_item(DecimalEncoder.decode(cleaned))

        store = _load_local_store()
        store["work_items"][str(decoded["id"])] = decoded
        _save_local_store(store)

        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_work_items")
                table.put_item(Item=cleaned)
            except Exception:
                pass
            self._sync_item_to_s3(decoded)
        return decoded

    def get_work_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_work_items")
                res = table.get_item(Key={"id": item_id})
                item = res.get("Item")
                if item:
                    return _normalize_item(DecimalEncoder.decode(item))
            except Exception:
                pass
        store = _load_local_store()
        found = store["work_items"].get(str(item_id))
        return _normalize_item(found) if found else None

    def update_work_item_state(
        self,
        item_id: int,
        target_state: str,
        assigned_to: Optional[str] = None,
        assigned_to_profile: Optional[str] = None
    ) -> Dict[str, Any]:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store = _load_local_store()
        local_item = store["work_items"].get(str(item_id), {"id": item_id})
        local_item["state"] = target_state
        local_item["updated_at"] = now_str
        if assigned_to:
            local_item["assigned_to"] = assigned_to
        if assigned_to_profile:
            local_item["assigned_to_profile"] = assigned_to_profile
        local_item = _normalize_item(local_item)
        store["work_items"][str(item_id)] = local_item
        _save_local_store(store)

        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_work_items")
                expr = "SET #st = :state, updated_at = :updated"
                names = {"#st": "state"}
                values: Dict[str, Any] = {":state": target_state, ":updated": now_str}
                if assigned_to:
                    expr += ", assigned_to = :assigned"
                    values[":assigned"] = assigned_to
                if assigned_to_profile:
                    expr += ", assigned_to_profile = :assigned_prof"
                    values[":assigned_prof"] = local_item.get("assigned_to_profile", assigned_to_profile)
                res = table.update_item(
                    Key={"id": item_id},
                    UpdateExpression=expr,
                    ExpressionAttributeNames=names,
                    ExpressionAttributeValues=values,
                    ReturnValues="ALL_NEW"
                )
                updated_item = _normalize_item(DecimalEncoder.decode(res.get("Attributes", {})))
                self._sync_item_to_s3(updated_item)
                return updated_item
            except Exception:
                pass
        return local_item

    def delete_work_item(self, item_id: int) -> bool:
        """Delete a work item from DynamoDB and local JSON store."""
        if self._is_online() and self.ddb_resource:
            try:
                table = self.ddb_resource.Table("harness_work_items")
                table.delete_item(Key={"id": item_id})
            except Exception:
                pass
            self._delete_item_from_s3(item_id)

        store = _load_local_store()
        sid = str(item_id)
        if sid in store.get("work_items", {}):
            del store["work_items"][sid]
            _save_local_store(store)
        return True

    def list_work_items(
        self,
        wi_type: Optional[str] = None,
        state: Optional[str] = None,
        source: Optional[str] = None,
        iteration: Optional[str] = None,
        assigned_to_profile: Optional[str] = None,
        parent_item_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        decoded: List[Dict[str, Any]] = []
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_work_items")
                scan_kwargs: Dict[str, Any] = {}
                filters = []
                if wi_type:
                    filters.append(Attr("type").eq(wi_type))
                if state:
                    filters.append(Attr("state").eq(state))
                if source:
                    filters.append(Attr("source").eq(source.lower()))
                if iteration:
                    filters.append(Attr("iteration_path").contains(iteration))
                if assigned_to_profile:
                    filters.append(Attr("assigned_to_profile").eq(assigned_to_profile))
                if parent_item_id is not None:
                    filters.append(Attr("parent_item_id").eq(parent_item_id))
                if filters:
                    combined = filters[0]
                    for f in filters[1:]:
                        combined = combined & f
                    scan_kwargs["FilterExpression"] = combined

                items: List[Dict[str, Any]] = []
                done = False
                start_key = None
                while not done:
                    if start_key:
                        scan_kwargs["ExclusiveStartKey"] = start_key
                    response = table.scan(**scan_kwargs)
                    items.extend(response.get("Items", []))
                    start_key = response.get("LastEvaluatedKey")
                    if not start_key:
                        done = True
                decoded = [_normalize_item(DecimalEncoder.decode(i)) for i in items]
                if not any([wi_type, state, source, iteration, assigned_to_profile, parent_item_id is not None]):
                    store = _load_local_store()
                    remote_map = {str(d["id"]): d for d in decoded if d.get("id") is not None}
                    if store.get("work_items") != remote_map:
                        store["work_items"] = remote_map
                        _save_local_store(store)
                decoded.sort(key=lambda x: x.get("id", 0), reverse=True)
                return decoded
            except Exception:
                pass

        store = _load_local_store()
        all_items = list(store["work_items"].values())
        res_list = []
        for it in all_items:
            if wi_type and it.get("type") != wi_type:
                continue
            if state and it.get("state") != state:
                continue
            if source and (it.get("source") or "").lower() != source.lower():
                continue
            if iteration and iteration not in (it.get("iteration_path") or ""):
                continue
            if assigned_to_profile and (it.get("assigned_to_profile") or "") != assigned_to_profile:
                continue
            if parent_item_id is not None and it.get("parent_item_id") != parent_item_id:
                continue
            res_list.append(it)
        res_list.sort(key=lambda x: int(x.get("id") or 0), reverse=True)
        return res_list

    # --- Stories CRUD ---
    def put_story(self, item: Dict[str, Any]) -> Dict[str, Any]:
        if "id" not in item or item["id"] is None:
            item["id"] = self.get_next_id("story_id")
        if "source" not in item or not item["source"]:
            item["source"] = "local"
        cleaned = {k: v for k, v in item.items() if v is not None}
        decoded = DecimalEncoder.decode(cleaned)

        store = _load_local_store()
        store["stories"][str(decoded["id"])] = decoded
        _save_local_store(store)

        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_stories")
                table.put_item(Item=cleaned)
            except Exception:
                pass
        return decoded

    def list_stories(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_stories")
                scan_kwargs = {}
                if source:
                    scan_kwargs["FilterExpression"] = Attr("source").eq(source.lower())
                response = table.scan(**scan_kwargs)
                items = [DecimalEncoder.decode(i) for i in response.get("Items", [])]
                items.sort(key=lambda x: x.get("id", 0))
                return items
            except Exception:
                pass
        store = _load_local_store()
        items = list(store["stories"].values())
        if source:
            items = [i for i in items if (i.get("source") or "").lower() == source.lower()]
        items.sort(key=lambda x: int(x.get("id") or 0))
        return items

    # --- Tools CRUD ---
    def put_tool(self, item: Dict[str, Any]) -> Dict[str, Any]:
        decoded = DecimalEncoder.decode(item)
        store = _load_local_store()
        store["tools"][str(decoded.get("name", ""))] = decoded
        _save_local_store(store)
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_tools")
                table.put_item(Item=item)
            except Exception:
                pass
        return decoded

    def list_tools(self, responsibility: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_tools")
                scan_kwargs = {}
                if responsibility:
                    scan_kwargs["FilterExpression"] = Attr("responsibility").eq(responsibility)
                response = table.scan(**scan_kwargs)
                items = [DecimalEncoder.decode(i) for i in response.get("Items", [])]
                items.sort(key=lambda x: x.get("name", ""))
                return items
            except Exception:
                pass
        store = _load_local_store()
        items = list(store["tools"].values())
        if responsibility:
            items = [i for i in items if i.get("responsibility") == responsibility]
        items.sort(key=lambda x: x.get("name", ""))
        return items

    # --- Skills CRUD & Inverted Index Search ---
    def sync_skills_index(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synchronizes skills into the primary skills store and builds an Inverted Index
        (token -> skill_name) on DynamoDB and local store.
        Avoids full table scans during search.
        """
        store = _load_local_store()
        store.setdefault("skills", {})
        store.setdefault("skills_inverted_index", {})

        online = self._is_online()
        table_skills = self.ddb_resource.Table("harness_skills") if online else None
        table_index = self.ddb_resource.Table("harness_skills_index") if online else None

        new_local_index: Dict[str, Dict[str, Any]] = {}
        indexed_count = 0
        total_tokens = set()
        items_skills = []
        items_index = []

        for skill in skills:
            name = str(skill.get("name", "")).strip()
            if not name:
                continue

            desc = str(skill.get("description", "")).strip()
            source = str(skill.get("source", "")).strip()
            source_type = str(skill.get("source_type", "")).strip()
            path = str(skill.get("path", "")).strip()
            synced = bool(skill.get("synced", True))
            files_count = int(skill.get("files_count", 1))
            updated_at = datetime.utcnow().isoformat()

            skill_record = {
                "name": name,
                "description": desc,
                "source": source,
                "source_type": source_type,
                "path": path,
                "synced": synced,
                "files_count": files_count,
                "updated_at": updated_at
            }

            # Update primary store
            store["skills"][name] = skill_record
            if online:
                items_skills.append(skill_record)

            # Tokenize fields with specific weights
            name_tokens = set(tokenize_for_search(name))
            desc_tokens = set(tokenize_for_search(desc))
            all_skill_tokens = name_tokens | desc_tokens

            snippet = desc[:180] + ("..." if len(desc) > 180 else "")

            for tok in all_skill_tokens:
                total_tokens.add(tok)
                weight = 0
                fields = []
                if tok in name_tokens:
                    weight += 10
                    fields.append("name")
                if tok in desc_tokens:
                    weight += 2
                    fields.append("description")

                # Local index
                if tok not in new_local_index:
                    new_local_index[tok] = {}
                new_local_index[tok][name] = {
                    "weight": weight,
                    "fields": fields,
                    "snippet": snippet
                }

                # DynamoDB index item
                if online:
                    items_index.append({
                        "token": tok,
                        "skill_name": name,
                        "weight": Decimal(str(weight)),
                        "fields": ",".join(fields),
                        "snippet": snippet
                    })

            indexed_count += 1

        # Batch write to DynamoDB if online
        if online and table_skills and table_index:
            try:
                with table_skills.batch_writer() as writer:
                    for it in items_skills:
                        writer.put_item(Item=it)
                with table_index.batch_writer() as writer:
                    for it in items_index:
                        writer.put_item(Item=it)
            except Exception:
                pass

        store["skills_inverted_index"] = new_local_index
        _save_local_store(store)

        return {
            "status": "success",
            "indexed_skills": indexed_count,
            "unique_tokens": len(total_tokens),
            "backend": "dynamodb" if online else "local_json"
        }

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch single skill by primary key (O(1) point lookup)."""
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_skills")
                resp = table.get_item(Key={"name": name})
                if "Item" in resp:
                    return DecimalEncoder.decode(resp["Item"])
            except Exception:
                pass
        store = _load_local_store()
        return store.get("skills", {}).get(name)

    def search_skills(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        High-performance skill search using the Inverted Index.
        DOES NOT perform full table scans (ScanAll).
        Instead, directly queries the partition key (token) for each query token,
        merges relevance scores, and only fetches the top-K matching skill documents.
        """
        query_tokens = tokenize_for_search(query_text)
        if not query_tokens:
            return []

        online = self._is_online()
        table_skills = self.ddb_resource.Table("harness_skills") if online else None
        table_index = self.ddb_resource.Table("harness_skills_index") if online else None
        store = _load_local_store()

        aggregated_scores: Dict[str, Dict[str, Any]] = {}

        # 1. Query ONLY the partitions matching query_tokens (O(1) per token, ZERO table scan)
        for tok in query_tokens:
            entries = []
            if online:
                try:
                    # Exact Partition Key Query: Key('token').eq(tok)
                    resp = table_index.query(KeyConditionExpression=Key("token").eq(tok))
                    entries = [DecimalEncoder.decode(i) for i in resp.get("Items", [])]
                except Exception:
                    entries = []

            # Fallback or local lookup
            if not entries:
                local_map = store.get("skills_inverted_index", {}).get(tok, {})
                entries = [
                    {
                        "token": tok,
                        "skill_name": sname,
                        "weight": data.get("weight", 1),
                        "fields": ",".join(data.get("fields", [])),
                        "snippet": data.get("snippet", "")
                    }
                    for sname, data in local_map.items()
                ]

            for entry in entries:
                sname = entry.get("skill_name")
                if not sname:
                    continue
                w = float(entry.get("weight", 1.0))
                if sname not in aggregated_scores:
                    aggregated_scores[sname] = {
                        "score": 0.0,
                        "matched_tokens": set(),
                        "snippet": entry.get("snippet", "")
                    }
                aggregated_scores[sname]["score"] += w
                aggregated_scores[sname]["matched_tokens"].add(tok)

        if not aggregated_scores:
            return []

        # 2. Ranking and multi-term match boosting
        clean_q = query_text.strip().lower()
        for sname, meta in aggregated_scores.items():
            matched_count = len(meta["matched_tokens"])
            # Bonus for matching multiple tokens in a query
            if matched_count > 1:
                meta["score"] *= (1.0 + (matched_count / len(query_tokens)) * 0.8)
            # Bonus if exact query substring matches skill name
            if clean_q in sname.lower():
                meta["score"] += 25.0

        # 3. Sort by score descending and take Top-K
        sorted_names = sorted(aggregated_scores.keys(), key=lambda k: aggregated_scores[k]["score"], reverse=True)[:limit]

        # 4. Fetch ONLY the top-K full documents by Primary Key (O(1) Point Lookup)
        results = []
        for rank, sname in enumerate(sorted_names, start=1):
            doc = None
            if online:
                try:
                    resp = table_skills.get_item(Key={"name": sname})
                    doc = DecimalEncoder.decode(resp.get("Item")) if "Item" in resp else None
                except Exception:
                    pass
            if not doc:
                doc = store.get("skills", {}).get(sname)

            score_info = aggregated_scores[sname]
            if doc:
                item_result = dict(doc)
                item_result["rank"] = rank
                item_result["score"] = round(score_info["score"], 2)
                item_result["matched_tokens"] = sorted(list(score_info["matched_tokens"]))
                results.append(item_result)
            else:
                results.append({
                    "rank": rank,
                    "name": sname,
                    "score": round(score_info["score"], 2),
                    "matched_tokens": sorted(list(score_info["matched_tokens"])),
                    "description": score_info.get("snippet", ""),
                    "source": "index"
                })

        return results

    # --- Stats ---
    def get_stats(self) -> Dict[str, Any]:
        work_items = self.list_work_items()
        stories = self.list_stories()
        tools = self.list_tools()

        type_counts: Dict[str, int] = {}
        source_counts: Dict[str, int] = {"remote": 0, "local": 0}
        iteration_counts: Dict[str, int] = {}

        for wi in work_items:
            t = wi.get("type", "Unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

            src = wi.get("source", "local").lower()
            source_counts[src] = source_counts.get(src, 0) + 1

            it = wi.get("iteration_path")
            if it:
                sprint_name = it.split("\\")[-1]
                iteration_counts[sprint_name] = iteration_counts.get(sprint_name, 0) + 1

        return {
            "total_work_items": len(work_items),
            "total_stories": len(stories),
            "total_tools": len(tools),
            "by_source": source_counts,
            "by_type": type_counts,
            "by_iteration": iteration_counts
        }

    def get_item_count(self) -> int:
        """Tổng số work items trong database (DynamoDB hoặc local store)."""
        return self.get_stats().get("total_work_items", 0)

    def init_experience_table(self) -> Dict[str, Any]:
        """Khởi tạo bảng harness_experience trên DynamoDB nếu chưa tồn tại."""
        schema = {
            "TableName": "harness_experience",
            "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "domain", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
                {"AttributeName": "work_item_id", "AttributeType": "S"}
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "domain-index",
                    "KeySchema": [
                        {"AttributeName": "domain", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                },
                {
                    "IndexName": "workitem-index",
                    "KeySchema": [
                        {"AttributeName": "work_item_id", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            "BillingMode": "PAY_PER_REQUEST"
        }
        if not self._is_online():
            return {"status": "offline", "message": "DynamoDB endpoint offline, using local store"}

        existing_tables = self.ddb_client.list_tables().get("TableNames", [])
        if "harness_experience" not in existing_tables:
            self.ddb_client.create_table(**schema)
            return {"status": "created", "table": "harness_experience"}

        # Check existing table description and add missing GSIs if needed
        desc = self.ddb_client.describe_table(TableName="harness_experience")["Table"]
        existing_gsis = {g["IndexName"] for g in desc.get("GlobalSecondaryIndexes", [])}
        target_gsis = {"domain-index", "workitem-index"}

        # If old index name exists and target names don't match, recreate table cleanly in local dev DynamoDB
        if not target_gsis.issubset(existing_gsis):
            try:
                # Scan items to preserve
                table = self.ddb_resource.Table("harness_experience")
                saved_items = table.scan().get("Items", [])
                self.ddb_client.delete_table(TableName="harness_experience")
                time.sleep(0.5)
                self.ddb_client.create_table(**schema)
                time.sleep(0.5)
                new_table = self.ddb_resource.Table("harness_experience")
                for it in saved_items:
                    # ensure string work_item_id if exists
                    if "work_item_id" in it and not isinstance(it["work_item_id"], str):
                        it["work_item_id"] = str(it["work_item_id"])
                    new_table.put_item(Item=it)
                return {"status": "recreated_with_gsi", "table": "harness_experience", "migrated_items": len(saved_items)}
            except Exception as e:
                return {"status": "error", "message": f"Failed to recreate table: {e}"}

        return {"status": "exists", "table": "harness_experience"}

    def put_experience(self, exp_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Lưu một bản ghi kinh nghiệm vào DynamoDB, SQLite harness_experience và local_db.json (G-MEM-2)."""
        import uuid
        import hashlib
        from datetime import datetime

        domain = str(exp_dict.get("domain") or exp_dict.get("category") or "general").strip()
        cue = str(exp_dict.get("cue") or exp_dict.get("trigger_pattern") or exp_dict.get("pattern") or "unspecified_cue").strip()
        lesson = str(exp_dict.get("lesson") or exp_dict.get("content") or "").strip()
        evidence = str(exp_dict.get("evidence") or exp_dict.get("proof") or "")
        if not evidence and "tags" in exp_dict:
            tags_val = exp_dict["tags"]
            evidence = ", ".join(tags_val) if isinstance(tags_val, list) else str(tags_val)

        raw_conf = exp_dict.get("confidence") if exp_dict.get("confidence") is not None else exp_dict.get("severity")
        if isinstance(raw_conf, (int, float)):
            conf_str = "high" if raw_conf >= 0.8 else ("low" if raw_conf < 0.5 else "medium")
        else:
            conf_val = str(raw_conf or "medium").strip().lower()
            conf_str = "high" if conf_val in ("high", "critical") else ("low" if conf_val in ("low", "minor") else "medium")

        item = dict(exp_dict)
        item["domain"] = domain
        item["category"] = domain
        item["cue"] = cue
        item["trigger_pattern"] = cue
        item["lesson"] = lesson
        item["evidence"] = evidence
        item["confidence"] = conf_str
        item["severity"] = conf_str

        if not item.get("id"):
            item["id"] = str(uuid.uuid4())
        if not item.get("created_at"):
            item["created_at"] = datetime.now().isoformat()
        if not item.get("pattern_hash"):
            pattern_raw = f"{domain}:{cue}:{lesson}"
            item["pattern_hash"] = hashlib.sha256(pattern_raw.encode("utf-8")).hexdigest()[:16]

        work_item_id_val = item.get("work_item_id")
        work_item_id_int = None
        if work_item_id_val is not None:
            try:
                work_item_id_int = int(work_item_id_val)
            except Exception:
                pass
            item["work_item_id"] = str(work_item_id_val)

        # 1. Ghi vào SQLite .harness/harness.db (bảng harness_experience) với deduplication trên (domain, cue)
        try:
            sqlite_db_path = _get_sqlite_harness_db_path()
            conn = sqlite3.connect(str(sqlite_db_path))
            conn.row_factory = sqlite3.Row
            _ensure_sqlite_experience_table(conn)
            cur = conn.cursor()
            cur.execute("SELECT id FROM harness_experience WHERE domain = ? AND cue = ?", (domain, cue))
            existing_row = cur.fetchone()
            if existing_row:
                cur.execute(
                    "UPDATE harness_experience SET lesson = ?, evidence = ?, confidence = ?, pattern_hash = ?, work_item_id = ? WHERE id = ?",
                    (lesson, evidence, conf_str, item["pattern_hash"], work_item_id_int, existing_row[0])
                )
            else:
                cur.execute(
                    "INSERT INTO harness_experience (domain, cue, lesson, evidence, confidence, pattern_hash, work_item_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (domain, cue, lesson, evidence, conf_str, item["pattern_hash"], work_item_id_int)
                )
            conn.commit()
            conn.close()
        except Exception:
            pass

        # 2. Ghi vào .harness/local_db.json với deduplication trên (domain, cue)
        try:
            store = _load_local_store()
            store.setdefault("experiences", [])
            store["experiences"] = [
                e for e in store["experiences"]
                if not (
                    (str(e.get("domain") or e.get("category") or "").strip() == domain and str(e.get("cue") or e.get("trigger_pattern") or "").strip() == cue)
                    or (item.get("id") and e.get("id") == item["id"])
                )
            ]
            store["experiences"].append(item)
            _save_local_store(store)
        except Exception:
            pass

        # 3. Ghi vào DynamoDB nếu online
        if self._is_online():
            try:
                table = self.ddb_resource.Table("harness_experience")
                table.put_item(Item=item)
            except Exception:
                pass

        return item

    def record_experience(
        self,
        domain: str,
        cue: str,
        lesson: str,
        evidence: str,
        confidence: str = "high",
        work_item_id: Optional[str | int] = None
    ) -> Dict[str, Any]:
        """Record a learned experience in DynamoDB harness_experience (and local store fallback)."""
        item = {
            "domain": domain,
            "cue": cue,
            "lesson": lesson,
            "evidence": evidence,
            "confidence": confidence,
        }
        if work_item_id is not None:
            item["work_item_id"] = str(work_item_id)
        return self.put_experience(item)

    def query_experiences(
        self,
        domain: Optional[str] = None,
        limit: int = 20,
        work_item_id: Optional[str | int] = None
    ) -> List[Dict[str, Any]]:
        """Query experiences with dual-store reconciliation (G-MEM-2, MEM-04)."""
        online = self._is_online()
        if online and domain:
            try:
                table = self.ddb_resource.Table("harness_experience")
                index_to_use = "domain-index"
                try:
                    resp = table.query(
                        IndexName=index_to_use,
                        KeyConditionExpression=Key("domain").eq(domain),
                        ScanIndexForward=False,
                        Limit=limit
                    )
                except Exception:
                    resp = table.query(
                        IndexName="domain-created_at-index",
                        KeyConditionExpression=Key("domain").eq(domain),
                        ScanIndexForward=False,
                        Limit=limit
                    )
                items = [DecimalEncoder.decode(i) for i in resp.get("Items", [])]
                if items:
                    return items
            except Exception:
                pass

        if online and work_item_id is not None:
            try:
                table = self.ddb_resource.Table("harness_experience")
                resp = table.query(
                    IndexName="workitem-index",
                    KeyConditionExpression=Key("work_item_id").eq(str(work_item_id)),
                    Limit=limit
                )
                items = [DecimalEncoder.decode(i) for i in resp.get("Items", [])]
                if items:
                    return items
            except Exception:
                pass

        if online and not domain and work_item_id is None:
            try:
                table = self.ddb_resource.Table("harness_experience")
                resp = table.scan(Limit=limit)
                items = [DecimalEncoder.decode(i) for i in resp.get("Items", [])]
                if items:
                    return items
            except Exception:
                pass

        # Fallback local store & SQLite reconciliation
        sqlite_items: List[Dict[str, Any]] = []
        try:
            sqlite_db_path = _get_sqlite_harness_db_path()
            if sqlite_db_path.exists():
                conn = sqlite3.connect(str(sqlite_db_path))
                conn.row_factory = sqlite3.Row
                _ensure_sqlite_experience_table(conn)
                sql = "SELECT * FROM harness_experience WHERE 1=1"
                params: List[Any] = []
                if domain and domain.lower() != "all":
                    sql += " AND domain = ?"
                    params.append(domain)
                if work_item_id is not None:
                    sql += " AND work_item_id = ?"
                    params.append(work_item_id)
                sql += " ORDER BY id DESC"
                cur = conn.cursor()
                cur.execute(sql, params)
                sqlite_items = [dict(r) for r in cur.fetchall()]
                conn.close()
        except Exception:
            sqlite_items = []

        store = _load_local_store()
        json_items = store.get("experiences", [])
        if domain and domain.lower() != "all":
            json_items = [e for e in json_items if (e.get("domain") == domain or e.get("category") == domain)]
        if work_item_id is not None:
            json_items = [e for e in json_items if str(e.get("work_item_id")) == str(work_item_id)]

        # Reconcile / Merge records by (domain, cue)
        merged_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for it in sqlite_items:
            d = str(it.get("domain", "")).strip()
            c = str(it.get("cue", "")).strip()
            if d and c:
                merged_by_key[(d, c)] = dict(it)

        missing_in_sqlite: List[Dict[str, Any]] = []
        for it in json_items:
            d = str(it.get("domain") or it.get("category") or "").strip()
            c = str(it.get("cue") or it.get("trigger_pattern") or "").strip()
            if not d or not c:
                continue
            key = (d, c)
            if key not in merged_by_key:
                merged_by_key[key] = dict(it)
                missing_in_sqlite.append(it)
            else:
                merged_by_key[key].update({k: v for k, v in it.items() if k not in merged_by_key[key] or merged_by_key[key][k] is None})

        # Sync missing items from JSON into SQLite
        if missing_in_sqlite:
            try:
                sqlite_db_path = _get_sqlite_harness_db_path()
                conn = sqlite3.connect(str(sqlite_db_path))
                _ensure_sqlite_experience_table(conn)
                cur = conn.cursor()
                for it in missing_in_sqlite:
                    d = str(it.get("domain") or it.get("category") or "").strip()
                    c = str(it.get("cue") or it.get("trigger_pattern") or "").strip()
                    l = str(it.get("lesson") or "").strip()
                    ev = str(it.get("evidence") or "")
                    conf = str(it.get("confidence") or "medium").lower()
                    if conf not in ("low", "medium", "high"):
                        conf = "medium"
                    ph = it.get("pattern_hash")
                    wid = None
                    if it.get("work_item_id") is not None:
                        try:
                            wid = int(it["work_item_id"])
                        except Exception:
                            pass
                    cur.execute(
                        "INSERT OR IGNORE INTO harness_experience (domain, cue, lesson, evidence, confidence, pattern_hash, work_item_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (d, c, l, ev, conf, ph, wid)
                    )
                conn.commit()
                conn.close()
            except Exception:
                pass

        # Sync missing items from SQLite into JSON store
        existing_json_keys = {
            (str(e.get("domain") or e.get("category") or "").strip(), str(e.get("cue") or e.get("trigger_pattern") or "").strip())
            for e in store.get("experiences", [])
        }
        needs_json_save = False
        for key, it in merged_by_key.items():
            if key not in existing_json_keys:
                store.setdefault("experiences", []).append(it)
                needs_json_save = True
        if needs_json_save:
            _save_local_store(store)

        # Output with schema aliases
        results = []
        for it in merged_by_key.values():
            rec = dict(it)
            dom = rec.get("domain") or rec.get("category") or "general"
            cu = rec.get("cue") or rec.get("trigger_pattern") or "unspecified_cue"
            cf = str(rec.get("confidence") or rec.get("severity") or "medium").lower()
            rec["domain"] = dom
            rec["category"] = dom
            rec["cue"] = cu
            rec["trigger_pattern"] = cu
            rec["confidence"] = cf
            rec["severity"] = cf
            results.append(rec)

        return results[:limit]


