"""AWS VPC MCP server exposing VPC management tools."""
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

server = Server("aws-vpc")


def _json_content(data: Any) -> Dict[str, Any]:
    return {"type": "application/json", "data": data}


def _handle_boto_error(error: Exception) -> ToolError:
    logger.exception("AWS VPC operation failed: %s", error)
    if isinstance(error, (ClientError, BotoCoreError)):
        payload = getattr(error, "response", {"error": str(error)})
        return ToolError(json.dumps(payload))
    return ToolError(str(error))


@server.tool("list_vpcs", "List all VPCs")
async def list_vpcs() -> List[Dict[str, Any]]:
    try:
        response = ec2_client.describe_vpcs()
        return [_json_content(response.get("Vpcs", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("describe_vpc", "Describe a specific VPC")
async def describe_vpc(vpc_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
        vpcs = response.get("Vpcs", [])
        if not vpcs:
            raise ToolError(f"VPC {vpc_id} not found")
        return [_json_content(vpcs[0])]
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_vpc", "Create a new VPC")
async def create_vpc(cidr_block: str, ipv6_support: bool = False, instance_tenancy: str = "default") -> List[Dict[str, Any]]:
    try:
        response = ec2_client.create_vpc(CidrBlock=cidr_block, InstanceTenancy=instance_tenancy)
        vpc = response.get("Vpc", {})
        if ipv6_support:
            ec2_client.associate_vpc_cidr_block(VpcId=vpc.get("VpcId"), AmazonProvidedIpv6CidrBlock=True)
        return [_json_content(vpc)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_vpc", "Delete a VPC")
async def delete_vpc(vpc_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.delete_vpc(VpcId=vpc_id)
        return [_json_content(response or {"message": f"VPC {vpc_id} deletion initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("modify_vpc_attribute", "Modify a VPC attribute")
async def modify_vpc_attribute(vpc_id: str, enable_dns_support: Optional[bool] = None, enable_dns_hostnames: Optional[bool] = None) -> List[Dict[str, Any]]:
    try:
        if enable_dns_support is not None:
            ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": enable_dns_support})
        if enable_dns_hostnames is not None:
            ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": enable_dns_hostnames})
        return [_json_content({"message": "VPC attributes updated", "vpc_id": vpc_id})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("list_subnets", "List subnets optionally filtered by VPC")
async def list_subnets(vpc_id: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        filters = [{"Name": "vpc-id", "Values": [vpc_id]}] if vpc_id else []
        response = ec2_client.describe_subnets(Filters=filters)
        return [_json_content(response.get("Subnets", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_subnet", "Create a subnet within a VPC")
async def create_subnet(vpc_id: str, cidr_block: str, availability_zone: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {"VpcId": vpc_id, "CidrBlock": cidr_block}
        if availability_zone:
            params["AvailabilityZone"] = availability_zone
        response = ec2_client.create_subnet(**params)
        return [_json_content(response.get("Subnet", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_subnet", "Delete a subnet")
async def delete_subnet(subnet_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.delete_subnet(SubnetId=subnet_id)
        return [_json_content(response or {"message": f"Subnet {subnet_id} deletion initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_tags", "Apply tags to AWS resources")
async def create_tags(resource_ids: List[str], tags: Dict[str, str]) -> List[Dict[str, Any]]:
    try:
        tag_list = [{"Key": key, "Value": value} for key, value in tags.items()]
        ec2_client.create_tags(Resources=resource_ids, Tags=tag_list)
        return [_json_content({"message": "Tags applied", "resources": resource_ids})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


async def main() -> None:
    await run(server)


if __name__ == "__main__":
    asyncio.run(main())
