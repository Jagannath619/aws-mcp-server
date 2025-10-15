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

## Claude Desktop Configuration

Expose the server in Claude Desktop by adding it to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-nlb": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/aws-mcp-server/aws-nlb"
    }
  }
}
```

Adjust the `cwd` to point to your local repository path and restart Claude Desktop after saving the configuration.

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

**Create a Network Load Balancer**

- Provision a Network Load Balancer named `network-lb` in subnets `subnet-1` and `subnet-2` with an internet-facing scheme.

**Register IP targets**

- Register IP targets `10.0.0.10:8080` and `10.0.0.11:8080` to target group `arn:aws:elasticloadbalancing:...:targetgroup/network/abcdef`.

## Authentication

The server relies on boto3's credential resolution chain. Configure credentials before use.
