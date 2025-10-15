"""AWS Transit Gateway MCP server."""
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

server = Server("aws-tgw")


def _json_content(data: Any) -> Dict[str, Any]:
    return {"type": "application/json", "data": data}


def _handle_boto_error(error: Exception) -> ToolError:
    logger.exception("AWS Transit Gateway operation failed: %s", error)
    if isinstance(error, (ClientError, BotoCoreError)):
        payload = getattr(error, "response", {"error": str(error)})
        return ToolError(json.dumps(payload))
    return ToolError(str(error))


@server.tool("list_transit_gateways", "List Transit Gateways")
async def list_transit_gateways() -> List[Dict[str, Any]]:
    try:
        response = ec2_client.describe_transit_gateways()
        return [_json_content(response.get("TransitGateways", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("describe_transit_gateway", "Describe a Transit Gateway")
async def describe_transit_gateway(transit_gateway_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.describe_transit_gateways(TransitGatewayIds=[transit_gateway_id])
        gateways = response.get("TransitGateways", [])
        if not gateways:
            raise ToolError(f"Transit gateway {transit_gateway_id} not found")
        return [_json_content(gateways[0])]
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_transit_gateway", "Create a Transit Gateway")
async def create_transit_gateway(description: Optional[str] = None, amazon_side_asn: Optional[int] = None, auto_accept_shared_attachments: Optional[str] = None, default_route_table_association: Optional[str] = None, default_route_table_propagation: Optional[str] = None, dns_support: Optional[str] = None, vpn_ecmp_support: Optional[str] = None) -> List[Dict[str, Any]]:  # noqa: E501
    try:
        params: Dict[str, Any] = {}
        if description:
            params["Description"] = description
        if amazon_side_asn:
            params["Options"] = params.get("Options", {})
            params["Options"]["AmazonSideAsn"] = amazon_side_asn
        options_map = {
            "AutoAcceptSharedAttachments": auto_accept_shared_attachments,
            "DefaultRouteTableAssociation": default_route_table_association,
            "DefaultRouteTablePropagation": default_route_table_propagation,
            "DnsSupport": dns_support,
            "VpnEcmpSupport": vpn_ecmp_support,
        }
        for key, value in options_map.items():
            if value is not None:
                params.setdefault("Options", {})[key] = value
        response = ec2_client.create_transit_gateway(**params)
        return [_json_content(response.get("TransitGateway", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_transit_gateway", "Delete a Transit Gateway")
async def delete_transit_gateway(transit_gateway_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.delete_transit_gateway(TransitGatewayId=transit_gateway_id)
        return [_json_content(response.get("TransitGateway", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("modify_transit_gateway", "Modify Transit Gateway options")
async def modify_transit_gateway(transit_gateway_id: str, auto_accept_shared_attachments: Optional[str] = None, default_route_table_association: Optional[str] = None, default_route_table_propagation: Optional[str] = None, dns_support: Optional[str] = None, vpn_ecmp_support: Optional[str] = None, description: Optional[str] = None) -> List[Dict[str, Any]]:  # noqa: E501
    try:
        options: Dict[str, Any] = {}
        if auto_accept_shared_attachments is not None:
            options["AutoAcceptSharedAttachments"] = auto_accept_shared_attachments
        if default_route_table_association is not None:
            options["DefaultRouteTableAssociation"] = default_route_table_association
        if default_route_table_propagation is not None:
            options["DefaultRouteTablePropagation"] = default_route_table_propagation
        if dns_support is not None:
            options["DnsSupport"] = dns_support
        if vpn_ecmp_support is not None:
            options["VpnEcmpSupport"] = vpn_ecmp_support
        params: Dict[str, Any] = {"TransitGatewayId": transit_gateway_id}
        if options:
            params["Options"] = options
        if description is not None:
            params["Description"] = description
        response = ec2_client.modify_transit_gateway(**params)
        return [_json_content(response.get("TransitGateway", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("list_transit_gateway_attachments", "List TGW attachments")
async def list_transit_gateway_attachments(transit_gateway_id: Optional[str] = None, attachment_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {}
        if transit_gateway_id:
            params["Filters"] = params.get("Filters", []) + [{"Name": "transit-gateway-id", "Values": [transit_gateway_id]}]
        if attachment_ids:
            params["TransitGatewayAttachmentIds"] = attachment_ids
        response = ec2_client.describe_transit_gateway_attachments(**params)
        return [_json_content(response.get("TransitGatewayAttachments", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_vpc_attachment", "Create a VPC attachment")
async def create_vpc_attachment(transit_gateway_id: str, vpc_id: str, subnet_ids: List[str], options: Optional[Dict[str, Any]] = None, tags: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {
            "TransitGatewayId": transit_gateway_id,
            "VpcId": vpc_id,
            "SubnetIds": subnet_ids,
        }
        if options:
            params["Options"] = options
        if tags:
            params["TagSpecifications"] = [
                {
                    "ResourceType": "transit-gateway-attachment",
                    "Tags": [{"Key": key, "Value": value} for key, value in tags.items()],
                }
            ]
        response = ec2_client.create_transit_gateway_vpc_attachment(**params)
        return [_json_content(response.get("TransitGatewayVpcAttachment", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_vpc_attachment", "Delete a VPC attachment")
async def delete_vpc_attachment(transit_gateway_attachment_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.delete_transit_gateway_vpc_attachment(TransitGatewayAttachmentId=transit_gateway_attachment_id)
        return [_json_content(response.get("TransitGatewayVpcAttachment", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("accept_vpc_attachment", "Accept a shared VPC attachment")
async def accept_vpc_attachment(transit_gateway_attachment_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.accept_transit_gateway_vpc_attachment(TransitGatewayAttachmentId=transit_gateway_attachment_id)
        return [_json_content(response.get("TransitGatewayVpcAttachment", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("list_route_tables", "List Transit Gateway route tables")
async def list_route_tables(transit_gateway_id: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {}
        if transit_gateway_id:
            params["Filters"] = [{"Name": "transit-gateway-id", "Values": [transit_gateway_id]}]
        response = ec2_client.describe_transit_gateway_route_tables(**params)
        return [_json_content(response.get("TransitGatewayRouteTables", []))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_route_table", "Create a Transit Gateway route table")
async def create_route_table(transit_gateway_id: str, tags: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {"TransitGatewayId": transit_gateway_id}
        if tags:
            params["TagSpecifications"] = [
                {
                    "ResourceType": "transit-gateway-route-table",
                    "Tags": [{"Key": key, "Value": value} for key, value in tags.items()],
                }
            ]
        response = ec2_client.create_transit_gateway_route_table(**params)
        return [_json_content(response.get("TransitGatewayRouteTable", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_route_table", "Delete a Transit Gateway route table")
async def delete_route_table(transit_gateway_route_table_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.delete_transit_gateway_route_table(TransitGatewayRouteTableId=transit_gateway_route_table_id)
        return [_json_content(response.get("TransitGatewayRouteTable", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("associate_route_table", "Associate attachment to a route table")
async def associate_route_table(transit_gateway_route_table_id: str, transit_gateway_attachment_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.associate_transit_gateway_route_table(
            TransitGatewayRouteTableId=transit_gateway_route_table_id,
            TransitGatewayAttachmentId=transit_gateway_attachment_id,
        )
        return [_json_content(response.get("Association", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("disassociate_route_table", "Disassociate attachment from a route table")
async def disassociate_route_table(transit_gateway_route_table_id: str, transit_gateway_attachment_id: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.disassociate_transit_gateway_route_table(
            TransitGatewayRouteTableId=transit_gateway_route_table_id,
            TransitGatewayAttachmentId=transit_gateway_attachment_id,
        )
        return [_json_content(response.get("Association", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("create_route", "Create a Transit Gateway route")
async def create_route(transit_gateway_route_table_id: str, destination_cidr_block: str, transit_gateway_attachment_id: Optional[str] = None, blackhole: bool = False) -> List[Dict[str, Any]]:
    try:
        params: Dict[str, Any] = {
            "TransitGatewayRouteTableId": transit_gateway_route_table_id,
            "DestinationCidrBlock": destination_cidr_block,
        }
        if transit_gateway_attachment_id:
            params["TransitGatewayAttachmentId"] = transit_gateway_attachment_id
        if blackhole:
            params["Blackhole"] = True
        response = ec2_client.create_transit_gateway_route(**params)
        return [_json_content(response.get("Route", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


@server.tool("delete_route", "Delete a Transit Gateway route")
async def delete_route(transit_gateway_route_table_id: str, destination_cidr_block: str) -> List[Dict[str, Any]]:
    try:
        response = ec2_client.delete_transit_gateway_route(
            TransitGatewayRouteTableId=transit_gateway_route_table_id,
            DestinationCidrBlock=destination_cidr_block,
        )
        return [_json_content(response.get("Route", {}))]
    except Exception as exc:  # noqa: BLE001
        raise _handle_boto_error(exc)


async def main() -> None:
    await run(server)


if __name__ == "__main__":
    asyncio.run(main())
