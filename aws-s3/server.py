"""AWS S3 MCP server exposing S3 management tools."""
import asyncio
import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

from mcp.server import Server, ToolError, run

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE")

_session_kwargs: Dict[str, Any] = {"region_name": AWS_REGION}
if AWS_PROFILE:
    _session_kwargs["profile_name"] = AWS_PROFILE

session = boto3.Session(**_session_kwargs)
s3_client = session.client("s3")

server = Server("aws-s3")


def _json_content(data: Any) -> Dict[str, Any]:
    return {"type": "application/json", "data": data}


def _handle_boto_error(error: Exception) -> ToolError:
    logger.exception("AWS S3 operation failed: %s", error)
    message = str(error)
    if isinstance(error, (ClientError, BotoCoreError)):
        message = json.dumps(error.response if hasattr(error, "response") else {"error": str(error)})
    return ToolError(message)


@server.tool("list_buckets", "List all S3 buckets in the account")
async def list_buckets() -> List[Dict[str, Any]]:
    try:
        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])
        return [_json_content(buckets)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_bucket", "Create a new S3 bucket")
async def create_bucket(bucket_name: str, region: Optional[str] = None) -> List[Dict[str, Any]]:
    kwargs: Dict[str, Any] = {"Bucket": bucket_name}
    target_region = region or AWS_REGION
    if target_region != "us-east-1":
        kwargs["CreateBucketConfiguration"] = {"LocationConstraint": target_region}
    try:
        response = s3_client.create_bucket(**kwargs)
        return [_json_content(response)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_bucket", "Delete an S3 bucket")
async def delete_bucket(bucket_name: str) -> List[Dict[str, Any]]:
    try:
        response = s3_client.delete_bucket(Bucket=bucket_name)
        return [_json_content(response or {"message": "Bucket deletion initiated."})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("list_objects", "List objects within an S3 bucket")
async def list_objects(bucket_name: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        objects: List[Dict[str, Any]] = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix or ""):
            objects.extend(page.get("Contents", []))
        return [_json_content(objects)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("upload_object", "Upload an object to S3 from a file or inline content")
async def upload_object(bucket_name: str, object_key: str, file_path: Optional[str] = None, content: Optional[str] = None, is_base64: bool = False) -> List[Dict[str, Any]]:  # noqa: D401
    """Upload an object to S3 either from a local file or provided content."""
    if not file_path and content is None:
        raise ToolError("Either file_path or content must be provided.")

    try:
        if file_path:
            with open(Path(file_path).expanduser(), "rb") as file_handle:
                s3_client.upload_fileobj(file_handle, bucket_name, object_key)
        else:
            data = base64.b64decode(content) if is_base64 else content.encode("utf-8")
            s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=data)
        return [_json_content({"bucket": bucket_name, "key": object_key})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("download_object", "Download an object from S3 to the local filesystem")
async def download_object(bucket_name: str, object_key: str, destination_path: str) -> List[Dict[str, Any]]:
    try:
        dest = Path(destination_path).expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as file_handle:
            s3_client.download_fileobj(bucket_name, object_key, file_handle)
        return [_json_content({"message": f"Object saved to {dest}"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_object", "Delete an object from S3")
async def delete_object(bucket_name: str, object_key: str) -> List[Dict[str, Any]]:
    try:
        response = s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        return [_json_content(response)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("get_bucket_policy", "Retrieve the policy for an S3 bucket")
async def get_bucket_policy(bucket_name: str) -> List[Dict[str, Any]]:
    try:
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(response.get("Policy", "{}"))
        return [_json_content(policy)]
    except ClientError as exc:
        if exc.response["Error"].get("Code") == "NoSuchBucketPolicy":
            return [_json_content({"message": "Bucket policy not found"})]
        raise _handle_boto_error(exc)
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("set_bucket_policy", "Set the policy for an S3 bucket")
async def set_bucket_policy(bucket_name: str, policy_json: str) -> List[Dict[str, Any]]:
    try:
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy_json)
        return [_json_content({"message": "Bucket policy updated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


async def main() -> None:
    await run(server)


if __name__ == "__main__":
    asyncio.run(main())
