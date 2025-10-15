"""AWS Network Load Balancer MCP server."""
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
elbv2_client = session.client("elbv2")

server = Server("aws-nlb")


def _json_content(data: Any) -> Dict[str, Any]:
    return {"type": "application/json", "data": data}


def _handle_boto_error(error: Exception) -> ToolError:
    logger.exception("AWS NLB operation failed: %s", error)
    if isinstance(error, (ClientError, BotoCoreError)):
        payload = getattr(error, "response", {"error": str(error)})
        return ToolError(json.dumps(payload))
    return ToolError(str(error))


@server.tool("list_load_balancers", "List Network Load Balancers")
async def list_load_balancers() -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.describe_load_balancers()
        nlbs = [lb for lb in response.get("LoadBalancers", []) if lb.get("Type") == "network"]
        return [_json_content(nlbs)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("describe_load_balancer", "Describe a Network Load Balancer")
async def describe_load_balancer(load_balancer_arn: str) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.describe_load_balancers(LoadBalancerArns=[load_balancer_arn])
        load_balancers = response.get("LoadBalancers", [])
        if not load_balancers:
            raise ToolError(f"Load balancer {load_balancer_arn} not found")
        return [_json_content(load_balancers[0])]
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_load_balancer", "Create a Network Load Balancer")
async def create_load_balancer(name: str, subnets: List[str], scheme: str = "internet-facing", ip_address_type: str = "ipv4", type_: str = "network") -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {
            "Name": name,
            "Subnets": subnets,
            "Scheme": scheme,
            "Type": type_,
            "IpAddressType": ip_address_type,
        }
        response = elbv2_client.create_load_balancer(**params)
        return [_json_content(response.get("LoadBalancers", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_load_balancer", "Delete a Network Load Balancer")
async def delete_load_balancer(load_balancer_arn: str) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
        return [_json_content(response or {"message": f"Load balancer {load_balancer_arn} deletion initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("modify_load_balancer_attributes", "Update NLB attributes")
async def modify_load_balancer_attributes(load_balancer_arn: str, attributes: Dict[str, str]) -> List[Dict[str, Any]]:
    try:
        attr_list = [{"Key": key, "Value": value} for key, value in attributes.items()]
        response = elbv2_client.modify_load_balancer_attributes(LoadBalancerArn=load_balancer_arn, Attributes=attr_list)
        return [_json_content(response.get("Attributes", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("list_target_groups", "List NLB target groups")
async def list_target_groups(load_balancer_arn: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        params = {"LoadBalancerArn": load_balancer_arn} if load_balancer_arn else {}
        response = elbv2_client.describe_target_groups(**params)
        target_groups = [tg for tg in response.get("TargetGroups", []) if tg.get("Protocol", "").upper() in {"TCP", "TLS", "UDP", "TCP_UDP"}]
        return [_json_content(target_groups)]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_target_group", "Create a target group for NLB")
async def create_target_group(name: str, protocol: str, port: int, vpc_id: str, target_type: str = "instance", health_check_protocol: Optional[str] = None, health_check_port: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {
            "Name": name,
            "Protocol": protocol,
            "Port": port,
            "VpcId": vpc_id,
            "TargetType": target_type,
        }
        if health_check_protocol:
            params["HealthCheckProtocol"] = health_check_protocol
        if health_check_port:
            params["HealthCheckPort"] = health_check_port
        response = elbv2_client.create_target_group(**params)
        return [_json_content(response.get("TargetGroups", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_target_group", "Delete an NLB target group")
async def delete_target_group(target_group_arn: str) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.delete_target_group(TargetGroupArn=target_group_arn)
        return [_json_content(response or {"message": f"Target group {target_group_arn} deletion initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("register_targets", "Register targets with an NLB target group")
async def register_targets(target_group_arn: str, targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.register_targets(TargetGroupArn=target_group_arn, Targets=targets)
        return [_json_content(response or {"message": "Targets registration initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("deregister_targets", "Deregister targets from an NLB target group")
async def deregister_targets(target_group_arn: str, targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.deregister_targets(TargetGroupArn=target_group_arn, Targets=targets)
        return [_json_content(response or {"message": "Targets deregistration initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("list_listeners", "List listeners for a Network Load Balancer")
async def list_listeners(load_balancer_arn: str) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.describe_listeners(LoadBalancerArn=load_balancer_arn)
        return [_json_content(response.get("Listeners", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_listener", "Create a listener for an NLB")
async def create_listener(load_balancer_arn: str, protocol: str, port: int, default_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    try:
        params = {
            "LoadBalancerArn": load_balancer_arn,
            "Protocol": protocol,
            "Port": port,
            "DefaultActions": default_actions,
        }
        response = elbv2_client.create_listener(**params)
        return [_json_content(response.get("Listeners", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_listener", "Delete an NLB listener")
async def delete_listener(listener_arn: str) -> List[Dict[str, Any]]:
    try:
        response = elbv2_client.delete_listener(ListenerArn=listener_arn)
        return [_json_content(response or {"message": f"Listener {listener_arn} deletion initiated"})]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("modify_listener", "Modify an NLB listener")
async def modify_listener(listener_arn: str, default_actions: Optional[List[Dict[str, Any]]] = None, port: Optional[int] = None, protocol: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {"ListenerArn": listener_arn}
        if default_actions is not None:
            params["DefaultActions"] = default_actions
        if port is not None:
            params["Port"] = port
        if protocol is not None:
            params["Protocol"] = protocol
        response = elbv2_client.modify_listener(**params)
        return [_json_content(response.get("Listeners", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


async def main() -> None:
    await run(server)


if __name__ == "__main__":
    asyncio.run(main())
