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


def check_span_overlap(span1: Dict[str, Any], span2: Dict[str, Any], max_overlap_ratio: float = 0.3) -> bool:
    """
    Check if two evidence spans overlap significantly.

    Args:
        span1, span2: Evidence span dictionaries with 'start' and 'end' keys
        max_overlap_ratio: Maximum allowed overlap as fraction of smaller span

    Returns:
        True if overlaps too much, False if acceptable
    """
    if not (span1 and span2):
        return False

    start1, end1 = span1.get("start", 0), span1.get("end", 0)
    start2, end2 = span2.get("start", 0), span2.get("end", 0)

    # Calculate overlap
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    overlap_length = max(0, overlap_end - overlap_start)

    if overlap_length == 0:
        return False

    # Check if overlap exceeds threshold relative to smaller span
    min_span_length = min(end1 - start1, end2 - start2)
    overlap_ratio = overlap_length / min_span_length if min_span_length > 0 else 0

    return overlap_ratio > max_overlap_ratio


def validate_trait_evidence(
    trait: Dict[str, Any], min_spans: int = 2, min_span_length: int = 50
) -> bool:
    """
    Validate personality trait evidence quality.

    Args:
        trait: Trait dictionary with evidence_spans
        min_spans: Minimum number of distinct evidence spans required
        min_span_length: Minimum characters per span

    Returns:
        True if valid, False otherwise
    """
    evidence_spans = trait.get("evidence_spans", [])

    # Check minimum number of spans
    if len(evidence_spans) < min_spans:
        return False

    # Validate each span length
    valid_spans = []
    for span in evidence_spans:
        if not span or "text" not in span:
            continue
        if len(span["text"].strip()) >= min_span_length:
            valid_spans.append(span)

    if len(valid_spans) < min_spans:
        return False

    # Check for excessive overlap between spans
    for i, span1 in enumerate(valid_spans):
        for span2 in valid_spans[i+1:]:
            if check_span_overlap(span1, span2):
                return False  # Reject if spans overlap too much

    return True


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

    # Calculate retention rate safely (avoid division by zero)
    retention_rate = (
        f"{100 * final_count / initial_count:.1f}%"
        if initial_count > 0
        else "0.0%"
    )

    logger.info(
        "qa_filters",
        f"QA filtering complete: {final_count} triples retained",
        total_dropped=total_dropped,
        retention_rate=retention_rate,
    )

    return deduplicated
