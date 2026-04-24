# aws-log-analyzer

A lightweight CLI tool for analyzing AWS CloudWatch logs, filtering events, and exporting to CSV/JSON.

## Features

- Parse and filter CloudWatch log streams by time range, log level, and pattern
- Aggregate error rates per service
- Export filtered results to CSV or JSON
- Support for multi-region log retrieval

## Requirements

- Python 3.9+
- AWS credentials configured (`aws configure` or environment variables)

## Installation

```bash
git clone https://github.com/dev-tools-lab/aws-log-analyzer
cd aws-log-analyzer
pip install -r requirements.txt
```

## Usage

```bash
# Analyze logs from the last 24 hours
python src/analyzer.py --group /aws/lambda/my-function --hours 24

# Filter by log level and export
python src/analyzer.py --group /aws/lambda/my-function --level ERROR --export csv

# Aggregate error rates across all services
python src/analyzer.py --all-groups --aggregate
```

## Configuration

Copy `.env.example` to `.env` and fill in your settings:

```
AWS_DEFAULT_REGION=us-east-1
LOG_LEVEL=INFO
OUTPUT_DIR=./output
```

## Contributing

Pull requests welcome. Run `pytest tests/` before submitting.

## License

MIT
