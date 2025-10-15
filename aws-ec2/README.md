# AWS EC2 MCP Server

The AWS EC2 MCP server offers a suite of tools for interacting with Amazon Elastic Compute Cloud instances and images.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure AWS credentials via environment variables, config files, or IAM roles.
4. Optional `.env` values:
   - `AWS_REGION` (defaults to `us-east-1`)
   - `AWS_PROFILE` (optional profile name)
   - `LOG_LEVEL` (defaults to `INFO`)

## Running the Server

```bash
python server.py
```

## Claude Desktop Configuration

Add the server to your `claude_desktop_config.json` so it can be launched from Claude Desktop:

```json
{
  "mcpServers": {
    "aws-ec2": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/aws-mcp-server/aws-ec2"
    }
  }
}
```

Update the `cwd` path to match your local checkout of this repository, then restart Claude Desktop to pick up the change.

## Available Tools

| Tool | Description |
| --- | --- |
| `list_instances` | List EC2 instances |
| `describe_instance` | Describe a specific instance |
| `start_instance` | Start an instance |
| `stop_instance` | Stop an instance |
| `reboot_instance` | Reboot an instance |
| `terminate_instance` | Terminate an instance |
| `run_instances` | Launch new instances |
| `create_image` | Create an AMI from an instance |
| `create_tags` | Apply tags to EC2 resources |

### Example Usage

**Launch an instance**

- Launch one `t3.micro` instance from image `ami-0abcdef1234567890`.

**Stop an instance**

- Stop instance `i-0123456789abcdef0` without using the force flag.

## Authentication

Ensure AWS credentials are configured before invoking tools.
