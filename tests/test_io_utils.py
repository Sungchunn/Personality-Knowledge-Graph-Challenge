"""
Tests for I/O utilities.
"""

import json
import pytest
from pathlib import Path
from src.pipeline.io_utils import (
    load_jsonl,
    save_jsonl,
    iter_jsonl,
    save_json,
    load_json,
)


def test_load_jsonl(tmp_path):
    """Test loading JSONL file."""
    # Create test file
    test_file = tmp_path / "test.jsonl"
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    with test_file.open("w") as f:
        for record in data:
            f.write(json.dumps(record) + "\n")

    # Load and verify
    loaded = load_jsonl(test_file)
    assert len(loaded) == 2
    assert loaded[0]["name"] == "Alice"
    assert loaded[1]["name"] == "Bob"


def test_save_jsonl(tmp_path):
    """Test saving JSONL file."""
    test_file = tmp_path / "output.jsonl"
    data = [{"key": "value1"}, {"key": "value2"}]

    save_jsonl(data, test_file)

    assert test_file.exists()

    # Verify content
    loaded = load_jsonl(test_file)
    assert loaded == data


def test_iter_jsonl(tmp_path):
    """Test iterating over JSONL file."""
    test_file = tmp_path / "test.jsonl"
    data = [{"n": i} for i in range(5)]

    save_jsonl(data, test_file)

    # Iterate and count
    count = 0
    for record in iter_jsonl(test_file):
        assert "n" in record
        count += 1

    assert count == 5


def test_json_roundtrip(tmp_path):
    """Test JSON save and load."""
    test_file = tmp_path / "test.json"
    data = {"name": "Test", "values": [1, 2, 3], "nested": {"key": "value"}}

    save_json(data, test_file)
    loaded = load_json(test_file)

    assert loaded == data
