# AWS NLB MCP Server

This MCP server exposes tools for managing Amazon Network Load Balancers (NLB) and their target groups/listeners.

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
| `list_load_balancers` | List NLBs |
| `describe_load_balancer` | Describe an NLB |
| `create_load_balancer` | Create an NLB |
| `delete_load_balancer` | Delete an NLB |
| `modify_load_balancer_attributes` | Update NLB attributes |
| `list_target_groups` | List target groups |
| `create_target_group` | Create a target group |
| `delete_target_group` | Delete a target group |
| `register_targets` | Register targets |
| `deregister_targets` | Deregister targets |
| `list_listeners` | List listeners |
| `create_listener` | Create a listener |
| `delete_listener` | Delete a listener |
| `modify_listener` | Modify a listener |

### Example Usage

Create an NLB:

```json
{
  "tool": "create_load_balancer",
  "arguments": {
    "name": "network-lb",
    "subnets": ["subnet-1", "subnet-2"],
    "scheme": "internet-facing"
  }
}
```

Register targets:

```json
{
  "tool": "register_targets",
  "arguments": {
    "target_group_arn": "arn:aws:elasticloadbalancing:...:targetgroup/network/abcdef",
    "targets": [
      {"Id": "10.0.0.10", "Port": 8080},
      {"Id": "10.0.0.11", "Port": 8080}
    ]
  }
}
```

## Authentication

The server relies on boto3's credential resolution chain. Configure credentials before use.
