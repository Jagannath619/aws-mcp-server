# AWS VPC MCP Server

This MCP server provides tooling for Amazon Virtual Private Cloud (VPC) operations.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure AWS credentials (environment variables, AWS config files, or IAM roles).
4. Optional `.env` variables:
   - `AWS_REGION` (defaults to `us-east-1`)
   - `AWS_PROFILE` (optional profile name)
   - `LOG_LEVEL` (defaults to `INFO`)

## Running the Server

```bash
python server.py
```

## Claude Desktop Configuration

Make the server accessible in Claude Desktop by editing `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-vpc": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/aws-mcp-server/aws-vpc"
    }
  }
}
```

Set the `cwd` to the absolute path for this directory on your machine and restart Claude Desktop to load the new configuration.

## Available Tools

| Tool | Description |
| --- | --- |
| `list_vpcs` | List all VPCs |
| `describe_vpc` | Describe a VPC by ID |
| `create_vpc` | Create a VPC |
| `delete_vpc` | Delete a VPC |
| `modify_vpc_attribute` | Update DNS support/hostnames |
| `list_subnets` | List subnets with optional VPC filter |
| `create_subnet` | Create a subnet |
| `delete_subnet` | Delete a subnet |
| `create_tags` | Apply tags to resources |

### Example Usage

Describe a VPC:

```json
{
  "tool": "describe_vpc",
  "arguments": {
    "vpc_id": "vpc-0123456789abcdef0"
  }
}
```

Create a subnet:

```json
{
  "tool": "create_subnet",
  "arguments": {
    "vpc_id": "vpc-0123456789abcdef0",
    "cidr_block": "10.0.1.0/24",
    "availability_zone": "us-east-1a"
  }
}
```

## Authentication

AWS credentials must be available via the default boto3 search order.
