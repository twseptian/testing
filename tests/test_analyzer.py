import pytest
from unittest.mock import MagicMock, patch
from src.analyzer import aggregate_errors, export_json, export_csv
import os, json, tempfile


SAMPLE_EVENTS = [
    {"timestamp": 1700000000000, "logStreamName": "stream-1", "message": "INFO  server started"},
    {"timestamp": 1700000001000, "logStreamName": "stream-1", "message": "ERROR  connection refused"},
    {"timestamp": 1700000002000, "logStreamName": "stream-2", "message": "WARN   slow query detected"},
    {"timestamp": 1700000003000, "logStreamName": "stream-2", "message": "ERROR  timeout after 30s"},
]


def test_aggregate_errors():
    counts = aggregate_errors(SAMPLE_EVENTS)
    assert counts["ERROR"] == 2
    assert counts["WARN"]  == 1
    assert counts["INFO"]  == 1


def test_export_json():
    with tempfile.TemporaryDirectory() as d:
        out = export_json(SAMPLE_EVENTS, f"{d}/events.json")
        with open(out) as f:
            data = json.load(f)
        assert len(data) == 4
        assert data[0]["message"] == "INFO  server started"


def test_export_csv():
    with tempfile.TemporaryDirectory() as d:
        out = export_csv(SAMPLE_EVENTS, f"{d}/events.csv")
        assert os.path.exists(out)
        with open(out) as f:
            lines = f.readlines()
        assert len(lines) == 5  # header + 4 events
