"""
Smoke tests for CLI (no API calls).
"""

import pytest
from pathlib import Path
from src.pipeline.config import PipelineConfig
from src.pipeline.io_utils import load_jsonl


def test_config_creation(tmp_path):
    """Test pipeline config creation."""
    config = PipelineConfig(
        input_jsonl_root=tmp_path / "input",
        output_root=tmp_path / "output",
        confidence_threshold=0.7,
    )

    assert config.confidence_threshold == 0.7
    assert config.output_root.exists()


def test_config_load_prompt():
    """Test loading prompt templates."""
    config = PipelineConfig(
        input_jsonl_root=Path("./tests/data"),
        output_root=Path("./outputs/test"),
    )

    # Load extract_triples prompt
    prompt = config.load_prompt("extract_triples")
    assert "SCHEMA RELATIONS" in prompt
    assert "{passage_text}" in prompt


def test_sample_data_loads():
    """Test that sample test data loads correctly."""
    test_data_path = Path("./tests/data/tiny.jsonl")

    if not test_data_path.exists():
        pytest.skip("Test data not found")

    records = load_jsonl(test_data_path)

    assert len(records) >= 2
    assert "text" in records[0]
    assert "book_id" in records[0]


def test_allowed_relations():
    """Test that config has allowed relations."""
    config = PipelineConfig(
        input_jsonl_root=Path("./input"),
        output_root=Path("./output"),
    )

    assert len(config.allowed_relations) > 0
    assert "KNOWS" in config.allowed_relations
    assert "FAMILY_OF" in config.allowed_relations
