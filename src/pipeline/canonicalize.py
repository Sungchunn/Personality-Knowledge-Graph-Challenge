"""
Canonicalize entities by merging aliases and variants.
"""

import json
from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict
from tqdm import tqdm

from .config import PipelineConfig
from .io_utils import load_jsonl, save_jsonl
from .logging_utils import PipelineLogger


def extract_unique_entities(triples: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract all unique entity names from triples.

    Args:
        triples: List of triple dictionaries

    Returns:
        Set of unique entity names
    """
    entities = set()
    for triple in triples:
        entities.add(triple["subject"])
        entities.add(triple["object"])
    return entities


def get_canonical_mappings(
    entities: List[str],
    config: PipelineConfig,
    client: OpenAI,
) -> Dict[str, str]:
    """
    Get canonical entity mappings from LLM.

    Args:
        entities: List of entity names
        config: Pipeline configuration
        client: OpenAI API client

    Returns:
        Dictionary mapping alias -> canonical name
    """
    # Batch entities into manageable chunks
    batch_size = 100
    mappings = {}

    for i in range(0, len(entities), batch_size):
        batch = entities[i : i + batch_size]
        entity_list = "\n".join(f"- {entity}" for entity in batch)

        prompt_template = config.load_prompt("canonicalize")
        prompt = prompt_template.format(entity_list=entity_list)

        try:
            response = client.chat.completions.create(
                model=config.model_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            response_text = response.choices[0].message.content
            result = json.loads(response_text)

            # Build mapping dictionary
            for mapping in result.get("mappings", []):
                if mapping["confidence"] >= config.confidence_threshold:
                    mappings[mapping["alias"]] = mapping["canonical"]

        except Exception as e:
            print(f"Error canonicalizing batch: {e}")
            continue

    return mappings


def apply_canonical_mappings(
    triples: List[Dict[str, Any]], mappings: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Apply canonical entity mappings to triples.

    Args:
        triples: List of triple dictionaries
        mappings: Dictionary mapping alias -> canonical

    Returns:
        List of triples with canonicalized entities
    """
    canonical_triples = []

    for triple in triples:
        # Apply mappings
        subject = mappings.get(triple["subject"], triple["subject"])
        obj = mappings.get(triple["object"], triple["object"])

        # Create new triple with canonical names
        canonical_triple = triple.copy()
        canonical_triple["subject"] = subject
        canonical_triple["object"] = obj

        canonical_triples.append(canonical_triple)

    return canonical_triples


def run_canonicalize(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Run entity canonicalization on raw triples.

    Args:
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Path to output triples_canonical.jsonl file
    """
    with logger.stage_context("canonicalize"):
        # Load raw triples
        raw_triples_path = config.output_root / "triples_raw.jsonl"
        logger.info("canonicalize", f"Loading raw triples from {raw_triples_path}")

        triples = load_jsonl(raw_triples_path)
        logger.info("canonicalize", f"Loaded {len(triples)} raw triples")

        # Extract unique entities
        entities = extract_unique_entities(triples)
        logger.info("canonicalize", f"Found {len(entities)} unique entities")

        # Get canonical mappings
        client = OpenAI()
        logger.info("canonicalize", "Generating canonical mappings")

        mappings = get_canonical_mappings(list(entities), config, client)
        logger.info(
            "canonicalize",
            f"Generated {len(mappings)} canonical mappings",
            mapping_count=len(mappings),
        )

        # Apply mappings
        canonical_triples = apply_canonical_mappings(triples, mappings)

        # Save canonical triples
        output_path = config.output_root / "triples_canonical.jsonl"
        save_jsonl(canonical_triples, output_path)

        logger.info("canonicalize", f"Saved canonical triples to {output_path}")

        return output_path
