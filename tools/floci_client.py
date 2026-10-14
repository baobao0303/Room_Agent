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
        raise RuntimeError("boto3 is required for Floci integration. Please install boto3.")

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

        self.ddb_resource = boto3.resource(
            "dynamodb",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        self.ddb_client = boto3.client(
            "dynamodb",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def init_schema(self) -> Dict[str, Any]:
        """Create tables in DynamoDB and bucket in S3 on Floci if they do not exist."""
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

        # Initialize S3 bucket for backups/snapshots
        try:
            existing_buckets = [b["Name"] for b in self.s3_client.list_buckets().get("Buckets", [])]
            if self.s3_bucket not in existing_buckets:
                self.s3_client.create_bucket(Bucket=self.s3_bucket)
        except Exception as e:
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
        table = self.ddb_resource.Table("harness_metadata")
        res = table.update_item(
            Key={"key": counter_key},
            UpdateExpression="ADD #val :incr",
            ExpressionAttributeNames={"#val": "value"},
            ExpressionAttributeValues={":incr": 1},
            ReturnValues="UPDATED_NEW"
        )
        return int(res["Attributes"]["value"])

    # --- Work Items CRUD ---
    def put_work_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        table = self.ddb_resource.Table("harness_work_items")
        if "id" not in item or item["id"] is None:
            item["id"] = self.get_next_id("work_item_id")
        if "source" not in item or not item["source"]:
            item["source"] = "local"
        
        # Clean null values
        cleaned = {k: v for k, v in item.items() if v is not None}
        table.put_item(Item=cleaned)
        return DecimalEncoder.decode(cleaned)

    def get_work_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        table = self.ddb_resource.Table("harness_work_items")
        res = table.get_item(Key={"id": item_id})
        item = res.get("Item")
        return DecimalEncoder.decode(item) if item else None

    def update_work_item_state(
        self,
        item_id: int,
        target_state: str,
        assigned_to: Optional[str] = None,
        assigned_to_profile: Optional[str] = None
    ) -> Dict[str, Any]:
        table = self.ddb_resource.Table("harness_work_items")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        expr = "SET #st = :state, updated_at = :updated"
        names = {"#st": "state"}
        values: Dict[str, Any] = {":state": target_state, ":updated": now_str}

        if assigned_to:
            expr += ", assigned_to = :assigned"
            values[":assigned"] = assigned_to

        if assigned_to_profile:
            expr += ", assigned_to_profile = :assigned_prof"
            values[":assigned_prof"] = assigned_to_profile

        res = table.update_item(
            Key={"id": item_id},
            UpdateExpression=expr,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW"
        )
        return DecimalEncoder.decode(res.get("Attributes", {}))

    def list_work_items(
        self,
        wi_type: Optional[str] = None,
        state: Optional[str] = None,
        source: Optional[str] = None,
        iteration: Optional[str] = None,
        assigned_to_profile: Optional[str] = None,
        parent_item_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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

        decoded = [DecimalEncoder.decode(i) for i in items]
        decoded.sort(key=lambda x: x.get("id", 0), reverse=True)
        return decoded

    # --- Stories CRUD ---
    def put_story(self, item: Dict[str, Any]) -> Dict[str, Any]:
        table = self.ddb_resource.Table("harness_stories")
        if "id" not in item or item["id"] is None:
            item["id"] = self.get_next_id("story_id")
        if "source" not in item or not item["source"]:
            item["source"] = "local"
        cleaned = {k: v for k, v in item.items() if v is not None}
        table.put_item(Item=cleaned)
        return DecimalEncoder.decode(cleaned)

    def list_stories(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        table = self.ddb_resource.Table("harness_stories")
        scan_kwargs = {}
        if source:
            scan_kwargs["FilterExpression"] = Attr("source").eq(source.lower())
        response = table.scan(**scan_kwargs)
        items = [DecimalEncoder.decode(i) for i in response.get("Items", [])]
        items.sort(key=lambda x: x.get("id", 0))
        return items

    # --- Tools CRUD ---
    def put_tool(self, item: Dict[str, Any]) -> Dict[str, Any]:
        table = self.ddb_resource.Table("harness_tools")
        table.put_item(Item=item)
        return DecimalEncoder.decode(item)

    def list_tools(self, responsibility: Optional[str] = None) -> List[Dict[str, Any]]:
        table = self.ddb_resource.Table("harness_tools")
        scan_kwargs = {}
        if responsibility:
            scan_kwargs["FilterExpression"] = Attr("responsibility").eq(responsibility)
        response = table.scan(**scan_kwargs)
        items = [DecimalEncoder.decode(i) for i in response.get("Items", [])]
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
