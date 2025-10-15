"""AWS EC2 MCP server exposing instance management tools."""
import asyncio
import json
import logging
import os
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
ec2_client = session.client("ec2")

server = Server("aws-ec2")


def _json_content(data: Any) -> Dict[str, Any]:
    return {"type": "application/json", "data": data}


def _handle_boto_error(error: Exception) -> ToolError:
    logger.exception("AWS EC2 operation failed: %s", error)
    if isinstance(error, (ClientError, BotoCoreError)):
        payload = getattr(error, "response", {"error": str(error)})
        return ToolError(json.dumps(payload))
    return ToolError(str(error))


@server.tool("list_instances", "List EC2 instances")
async def list_instances(state: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        filters = [{"Name": "instance-state-name", "Values": [state]}] if state else []
        response = ec2_client.describe_instances(Filters=filters)
        reservations = response.get("Reservations", [])
        instances = [instance for reservation in reservations for instance in reservation.get("Instances", [])]
        return [_json_content(instances)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("describe_instance", "Describe an EC2 instance")
async def describe_instance(instance_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        reservations = response.get("Reservations", [])
        instances = [instance for reservation in reservations for instance in reservation.get("Instances", [])]
        if not instances:
            raise ToolError(f"Instance {instance_id} not found")
        return [_json_content(instances[0])]
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("start_instance", "Start an EC2 instance")
async def start_instance(instance_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        return [_json_content(response.get("StartingInstances", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("stop_instance", "Stop an EC2 instance")
async def stop_instance(instance_id: str, force: bool = False) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id], Force=force)
        return [_json_content(response.get("StoppingInstances", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("reboot_instance", "Reboot an EC2 instance")
async def reboot_instance(instance_id: str) -> List[Dict[str, Any]]:
    try:
        ec2_client.reboot_instances(InstanceIds=[instance_id])
        return [_json_content({"message": f"Instance {instance_id} rebooted"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("terminate_instance", "Terminate an EC2 instance")
async def terminate_instance(instance_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        return [_json_content(response.get("TerminatingInstances", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("run_instances", "Launch new EC2 instances")
async def run_instances(image_id: str, instance_type: str, key_name: Optional[str] = None, min_count: int = 1, max_count: int = 1, subnet_id: Optional[str] = None, security_group_ids: Optional[List[str]] = None, user_data: Optional[str] = None, iam_instance_profile: Optional[str] = None) -> List[Dict[str, Any]]:  # noqa: D401,E501
    """Launch new EC2 instances with optional networking and user data."""
    try:
        params: Dict[str, Any] = {
            "ImageId": image_id,
            "InstanceType": instance_type,
            "MinCount": min_count,
            "MaxCount": max_count,
        }
        if key_name:
            params["KeyName"] = key_name
        if subnet_id:
            params["SubnetId"] = subnet_id
        if security_group_ids:
            params["SecurityGroupIds"] = security_group_ids
        if user_data:
            params["UserData"] = user_data
        if iam_instance_profile:
            params["IamInstanceProfile"] = {"Name": iam_instance_profile}
        response = ec2_client.run_instances(**params)
        return [_json_content(response.get("Instances", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_image", "Create an AMI from an instance")
async def create_image(instance_id: str, name: str, description: Optional[str] = None, no_reboot: bool = False) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.create_image(InstanceId=instance_id, Name=name, Description=description, NoReboot=no_reboot)
        return [_json_content({"ImageId": response.get("ImageId")})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_tags", "Apply tags to EC2 resources")
async def create_tags(resource_ids: List[str], tags: Dict[str, str]) -> List[Dict[str, Any]]:
    try:
        ec2_client.create_tags(Resources=resource_ids, Tags=[{"Key": key, "Value": value} for key, value in tags.items()])
        return [_json_content({"message": "Tags applied", "resources": resource_ids})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


async def main() -> None:
    await run(server)


if __name__ == "__main__":
    asyncio.run(main())
