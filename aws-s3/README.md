# AWS S3 MCP Server

This MCP (Model Context Protocol) server exposes a collection of tools for managing Amazon S3 resources using the AWS SDK for Python (boto3).

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure AWS credentials using one of the supported mechanisms (environment variables, AWS config files, or IAM roles).
4. Optionally set environment variables in a `.env` file:
   - `AWS_REGION` (defaults to `us-east-1`)
   - `AWS_PROFILE` (optional named profile)
   - `LOG_LEVEL` (defaults to `INFO`)

## Running the Server

```bash
python server.py
```

## Claude Desktop Configuration

Register the server in Claude Desktop by updating your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-s3": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/aws-mcp-server/aws-s3"
    }
  }
}
```

Be sure to replace the `cwd` with the absolute path on your machine and restart Claude Desktop after making the change.

## Available Tools

| Tool | Description |
| --- | --- |
| `list_buckets` | List all S3 buckets in the account |
| `create_bucket` | Create a new S3 bucket |
| `delete_bucket` | Delete an S3 bucket |
| `list_objects` | List objects in a bucket |
| `upload_object` | Upload content or a file into S3 |
| `download_object` | Download an object to the local filesystem |
| `delete_object` | Delete an object from S3 |
| `get_bucket_policy` | Retrieve the bucket policy |
| `set_bucket_policy` | Apply or update the bucket policy |

### Example Usage

List all buckets:

```json
{
  "tool": "list_buckets"
}
```

Upload a file:

```json
{
  "tool": "upload_object",
  "arguments": {
    "bucket_name": "example-bucket",
    "object_key": "data/report.csv",
    "file_path": "./report.csv"
  }
}
```

## Authentication

This server relies on standard AWS authentication mechanisms supported by boto3. Ensure credentials are configured before invoking tools.
