# Configuration Reference

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region for CloudWatch API calls |
| `LOG_LEVEL` | `INFO` | Application log verbosity |
| `OUTPUT_DIR` | `./output` | Directory for exported files |
| `MAX_EVENTS` | `10000` | Maximum log events to retrieve per query |

## AWS Permissions Required

The IAM role or user running this tool needs:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:FilterLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams"
    ],
    "Resource": "arn:aws:logs:*:*:*"
  }]
}
```
