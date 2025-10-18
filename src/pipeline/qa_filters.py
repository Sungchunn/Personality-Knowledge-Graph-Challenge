"""
Quality assurance filters for extracted data.
"""

from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

from .config import PipelineConfig
from .logging_utils import PipelineLogger


def validate_confidence(
    item: Dict[str, Any], threshold: float
) -> bool:
    """Check if item meets confidence threshold."""
    return item.get("confidence", 0.0) >= threshold


def validate_evidence_span(
    span: Dict[str, Any], min_length: int, max_length: int
) -> bool:
    """Validate evidence span format and length."""
    if not span:
        return False

    # Check required fields
    if "text" not in span or "start" not in span or "end" not in span:
        return False

    # Check offsets
    if span["start"] >= span["end"]:
        return False

    # Check length
    text_length = len(span["text"])
    if text_length < min_length or text_length > max_length:
        return False

    # Check text is meaningful
    if not span["text"].strip():
        return False

    return True


def normalize_entity(entity: str) -> str:
    """Normalize entity name."""
    if not entity:
        return ""

    # Trim whitespace
    entity = entity.strip()

    # Remove empty
    if not entity:
        return ""

    return entity


def deduplicate_triples(triples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate triples, keeping highest confidence version.

    Args:
        triples: List of triple dictionaries

    Returns:
        Deduplicated list of triples
    """
    # Group by (subject, relation, object)
    groups = defaultdict(list)

    for triple in triples:
        key = (
            triple["subject"],
            triple["relation"],
            triple["object"],
        )
        groups[key].append(triple)

    # Keep highest confidence from each group
    deduplicated = []
    for key, group in groups.items():
        best = max(group, key=lambda t: t.get("confidence", 0.0))
        deduplicated.append(best)

    return deduplicated


def apply_filters(
    triples: List[Dict[str, Any]], config: PipelineConfig, logger: PipelineLogger
) -> List[Dict[str, Any]]:
    """
    Apply QA filters to triples.

    Args:
        triples: List of triple dictionaries
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Filtered list of triples
    """
    initial_count = len(triples)
    logger.info("qa_filters", f"Starting with {initial_count} triples")

    # Pass 1: Confidence threshold
    filtered = [
        t for t in triples if validate_confidence(t, config.confidence_threshold)
    ]
    logger.info(
        "qa_filters",
        f"After confidence filter: {len(filtered)} triples",
        dropped=initial_count - len(filtered),
    )

    # Pass 2: Evidence span validation
    validated = []
    for triple in filtered:
        evidence = triple.get("evidence_span")
        if evidence and validate_evidence_span(
            evidence, config.min_span_length, config.max_span_length
        ):
            validated.append(triple)

    logger.info(
        "qa_filters",
        f"After evidence validation: {len(validated)} triples",
        dropped=len(filtered) - len(validated),
    )

    # Pass 3: Normalize entities
    for triple in validated:
        triple["subject"] = normalize_entity(triple["subject"])
        triple["object"] = normalize_entity(triple["object"])

    # Remove empty entities
    validated = [
        t
        for t in validated
        if t["subject"] and t["object"] and t["subject"] != t["object"]
    ]

    logger.info(
        "qa_filters",
        f"After normalization: {len(validated)} triples",
    )

    # Pass 4: Deduplicate
    deduplicated = deduplicate_triples(validated)

    logger.info(
        "qa_filters",
        f"After deduplication: {len(deduplicated)} triples",
        dropped=len(validated) - len(deduplicated),
    )

    final_count = len(deduplicated)
    total_dropped = initial_count - final_count
    logger.info(
        "qa_filters",
        f"QA filtering complete: {final_count} triples retained",
        total_dropped=total_dropped,
        retention_rate=f"{100 * final_count / initial_count:.1f}%",
    )

    return deduplicated
