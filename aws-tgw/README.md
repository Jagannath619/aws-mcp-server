# AWS Transit Gateway MCP Server

Tools for provisioning and managing AWS Transit Gateways (TGW) and related resources.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure AWS credentials (environment variables, AWS config files, or IAM roles).
4. Optional `.env` variables:
   - `AWS_REGION` (defaults to `us-east-1`)
   - `AWS_PROFILE` (optional profile)
   - `LOG_LEVEL` (defaults to `INFO`)

## Running the Server

```bash
python server.py
```

## Available Tools

| Tool | Description |
| --- | --- |
| `list_transit_gateways` | List Transit Gateways |
| `describe_transit_gateway` | Describe a Transit Gateway |
| `create_transit_gateway` | Create a Transit Gateway |
| `delete_transit_gateway` | Delete a Transit Gateway |
| `modify_transit_gateway` | Update Transit Gateway options |
| `list_transit_gateway_attachments` | List attachments |
| `create_vpc_attachment` | Create a VPC attachment |
| `delete_vpc_attachment` | Delete a VPC attachment |
| `accept_vpc_attachment` | Accept a shared attachment |
| `list_route_tables` | List Transit Gateway route tables |
| `create_route_table` | Create a route table |
| `delete_route_table` | Delete a route table |
| `associate_route_table` | Associate an attachment |
| `disassociate_route_table` | Disassociate an attachment |
| `create_route` | Create a route |
| `delete_route` | Delete a route |

### Example Usage

Create a Transit Gateway:

```json
{
  "tool": "create_transit_gateway",
  "arguments": {
    "description": "Prod TGW",
    "auto_accept_shared_attachments": "enable"
  }
}
```

Create a VPC attachment:

```json
{
  "tool": "create_vpc_attachment",
  "arguments": {
    "transit_gateway_id": "tgw-0123456789abcdef0",
    "vpc_id": "vpc-0123456789abcdef0",
    "subnet_ids": ["subnet-1", "subnet-2"]
  }
}
```

## Authentication

The server uses the default boto3 credential provider chain. Ensure credentials are set up before running the server.
