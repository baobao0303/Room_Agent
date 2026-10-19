"""
tools/floci_client.py - Floci DynamoDB & S3 Client for Harness Operating Framework.
Transparently supports Floci emulation endpoint on local / host network.
"""
import os
import sys
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime

import glob

# Transparent auto-discovery of boto3 site-packages if missing from system python
try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError
except ImportError:
    for pattern in [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../.venv/lib/python*/site-packages")),
        "/Users/bao312/Desktop/Room_Agent/.venv/lib/python*/site-packages",
        "/home/baoltb/.hermes/hermes-agent/venv/lib/python*/site-packages",
        "/home/baoltb/ponytail/venv/lib/python*/site-packages",
        os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python*/site-packages")
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
from urllib.parse import urlparse

LOCAL_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.harness_local_db.json"))
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
                    return data
        except Exception:
            pass
    return {"metadata": {}, "work_items": {}, "stories": {}, "tools": {}}


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

    def init_schema(self) -> Dict[str, Any]:
        """Create tables in DynamoDB and bucket in S3 on Floci if they do not exist."""
        if not self._is_online():
            store = _load_local_store()
            _save_local_store(store)
            return {
                "status": "local_fallback",
                "endpoint": LOCAL_DB_PATH,
                "created_tables": [],
                "existing_tables": ["harness_metadata", "harness_work_items", "harness_stories", "harness_tools"],
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
            }
        }

        for table_name, schema in schemas.items():
            if table_name not in existing_tables:
                self.ddb_client.create_table(
                    TableName=table_name,
                    KeySchema=schema["KeySchema"],
                    AttributeDefinitions=schema["AttributeDefinitions"],
                    BillingMode="PAY_PER_REQUEST"
                )
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

