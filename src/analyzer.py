#!/usr/bin/env python3
"""
AWS CloudWatch Log Analyzer
Filters, aggregates, and exports log events from CloudWatch.
"""

import os
import csv
import json
import click
import boto3
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()


def get_client(region=None):
    region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    return boto3.client("logs", region_name=region)


def fetch_events(client, group, hours, level=None, pattern=None):
    end_time   = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    kwargs = {
        "logGroupName": group,
        "startTime":    int(start_time.timestamp() * 1000),
        "endTime":      int(end_time.timestamp() * 1000),
        "limit":        int(os.getenv("MAX_EVENTS", 10000)),
    }
    if pattern:
        kwargs["filterPattern"] = pattern
    elif level:
        kwargs["filterPattern"] = level.upper()

    events = []
    paginator = client.get_paginator("filter_log_events")
    for page in paginator.paginate(**kwargs):
        events.extend(page.get("events", []))

    return events


def aggregate_errors(events):
    counts = {}
    for e in events:
        msg = e.get("message", "")
        level = "ERROR" if "ERROR" in msg else "WARN" if "WARN" in msg else "INFO"
        counts[level] = counts.get(level, 0) + 1
    return counts


def export_csv(events, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "logStreamName", "message"])
        w.writeheader()
        for e in events:
            w.writerow({
                "timestamp":     datetime.fromtimestamp(e["timestamp"] / 1000).isoformat(),
                "logStreamName": e.get("logStreamName", ""),
                "message":       e.get("message", "").strip(),
            })
    return path


def export_json(events, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(events, f, indent=2, default=str)
    return path


@click.command()
@click.option("--group",     "-g", required=True, help="CloudWatch log group name")
@click.option("--hours",     "-h", default=24,    help="How many hours back to query (default: 24)")
@click.option("--level",     "-l", default=None,  help="Filter by log level: DEBUG, INFO, WARN, ERROR")
@click.option("--pattern",   "-p", default=None,  help="CloudWatch filter pattern (overrides --level)")
@click.option("--export",    "-e", default=None,  type=click.Choice(["csv", "json"]), help="Export format")
@click.option("--aggregate", "-a", is_flag=True,  help="Show aggregated error counts")
@click.option("--region",    "-r", default=None,  help="AWS region (default: AWS_DEFAULT_REGION env var)")
def main(group, hours, level, pattern, export, aggregate, region):
    """Analyze AWS CloudWatch logs and optionally export results."""

    client = get_client(region)
    console.print(f"[bold cyan]Fetching logs from [/bold cyan][yellow]{group}[/yellow] (last {hours}h)...")

    try:
        events = fetch_events(client, group, hours, level, pattern)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    console.print(f"[green]Found {len(events)} events[/green]")

    if aggregate:
        counts = aggregate_errors(events)
        t = Table(title="Event Aggregation")
        t.add_column("Level", style="cyan")
        t.add_column("Count", justify="right")
        for lvl, cnt in sorted(counts.items()):
            t.add_row(lvl, str(cnt))
        console.print(t)

    if export == "csv":
        out = export_csv(events, f"output/{group.replace('/', '_')}.csv")
        console.print(f"[green]Exported:[/green] {out}")
    elif export == "json":
        out = export_json(events, f"output/{group.replace('/', '_')}.json")
        console.print(f"[green]Exported:[/green] {out}")
    else:
        t = Table(title="Log Events (latest 50)")
        t.add_column("Timestamp", style="dim")
        t.add_column("Stream")
        t.add_column("Message")
        for e in events[-50:]:
            ts  = datetime.fromtimestamp(e["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            msg = e.get("message", "").strip()[:120]
            t.add_row(ts, e.get("logStreamName", "")[:30], msg)
        console.print(t)


if __name__ == "__main__":
    main()
