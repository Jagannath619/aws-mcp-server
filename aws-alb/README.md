# AWS ALB MCP Server

This MCP server surfaces tooling for Amazon Application Load Balancers (ALB) and related resources.

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

## Claude Desktop Configuration

Add the server to your `claude_desktop_config.json` to make it available in Claude Desktop:

```json
{
  "mcpServers": {
    "aws-alb": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/aws-mcp-server/aws-alb"
    }
  }
}
```

Replace the `cwd` value with the absolute path to this server on your machine. Restart Claude Desktop after saving the configuration.

## Available Tools

| Tool | Description |
| --- | --- |
| `list_load_balancers` | List ALBs |
| `describe_load_balancer` | Describe an ALB |
| `create_load_balancer` | Create an ALB |
| `delete_load_balancer` | Delete an ALB |
| `modify_load_balancer_attributes` | Update ALB attributes |
| `list_target_groups` | List target groups |
| `create_target_group` | Create a target group |
| `delete_target_group` | Delete a target group |
| `register_targets` | Register targets to a target group |
| `deregister_targets` | Deregister targets from a target group |
| `list_listeners` | List listeners |
| `create_listener` | Create a listener |
| `delete_listener` | Delete a listener |
| `modify_listener` | Modify a listener |

### Example Usage

Create a target group:

```json
{
  "tool": "create_target_group",
  "arguments": {
    "name": "web-targets",
    "protocol": "HTTP",
    "port": 80,
    "vpc_id": "vpc-0123456789abcdef0"
  }
}
```

Register targets:

```json
{
  "tool": "register_targets",
  "arguments": {
    "target_group_arn": "arn:aws:elasticloadbalancing:...:targetgroup/web-targets/123456",
    "targets": [
      {"Id": "i-0123456789abcdef0"},
      {"Id": "i-0fedcba9876543210"}
    ]
  }
}
```

## Authentication

The server uses boto3; ensure AWS credentials are configured.
