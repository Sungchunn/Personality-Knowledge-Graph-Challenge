"""
Infer Big Five personality traits for people mentioned in text.
"""

import json
from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict
from tqdm import tqdm

from .config import PipelineConfig
from .io_utils import discover_jsonl_files, iter_jsonl, load_jsonl, save_jsonl
from .logging_utils import PipelineLogger
from .qa_filters import validate_trait_evidence


def extract_people_from_triples(triples: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract all person names from triples.

    Args:
        triples: List of triple dictionaries

    Returns:
        Set of person names
    """
    people = set()
    for triple in triples:
        # Heuristic: if relation indicates person, add to set
        if triple.get("relation") in [
            "KNOWS",
            "FAMILY_OF",
            "FRIENDS_WITH",
            "ENEMY_OF",
            "LOVES",
            "HATES",
        ]:
            people.add(triple["subject"])
            people.add(triple["object"])
    return people


def find_passages_mentioning_person(
    person_name: str, config: PipelineConfig
) -> List[Dict[str, Any]]:
    """
    Find all passages that mention a specific person.

    Args:
        person_name: Name of person to search for
        config: Pipeline configuration

    Returns:
        List of passage dictionaries mentioning the person
    """
    passages = []

    # Handle single file mode
    if config.input_file:
        jsonl_files = [config.input_file]
    else:
        jsonl_files = discover_jsonl_files(config.input_jsonl_root)

    for jsonl_file in jsonl_files:
        for passage in iter_jsonl(jsonl_file):
            if person_name.lower() in passage["text"].lower():
                passages.append(passage)

    return passages


def aggregate_character_context(
    person_name: str,
    passages: List[Dict[str, Any]],
    max_passages: int = 50,
    max_chars: int = 12000,
) -> str:
    """
    Aggregate passages mentioning a character into comprehensive context.

    Strategy:
    - Sample passages across the book (beginning, middle, end)
    - Prioritize longer passages (more context)
    - Stay within token limits

    Args:
        person_name: Character name
        passages: All passages mentioning the character
        max_passages: Maximum passages to include
        max_chars: Maximum total characters

    Returns:
        Aggregated text context
    """
    if not passages:
        return ""

    # Sort by position in book to maintain narrative order
    sorted_passages = sorted(passages, key=lambda p: p.get("chunk_index", 0))

    # Sample evenly across the book
    if len(sorted_passages) > max_passages:
        # Take every Nth passage to get even distribution
        step = len(sorted_passages) // max_passages
        sampled = [sorted_passages[i * step] for i in range(max_passages)]
    else:
        sampled = sorted_passages

    # Build aggregated context
    context_parts = []
    total_chars = 0

    for i, passage in enumerate(sampled):
        passage_text = passage["text"]

        # Add context marker
        chunk_id = passage.get("chunk_index", i)
        header = f"\n--- Passage {chunk_id} ---\n"

        # Check if we exceed limit
        if total_chars + len(header) + len(passage_text) > max_chars:
            break

        context_parts.append(header + passage_text)
        total_chars += len(header) + len(passage_text)

    return "\n".join(context_parts)


def infer_personality_for_person(
    person_name: str,
    passages: List[Dict[str, Any]],
    config: PipelineConfig,
    client: OpenAI,
) -> Dict[str, Any]:
    """
    Infer Big Five personality traits for a person using aggregated context.

    Args:
        person_name: Name of person
        passages: All relevant text passages mentioning the person
        config: Pipeline configuration
        client: OpenAI API client

    Returns:
        Personality profile dictionary
    """
    # Aggregate context from ALL passages mentioning the character
    aggregated_text = aggregate_character_context(
        person_name,
        passages,
        max_passages=50,  # Sample up to 50 passages
        max_chars=12000,  # ~3K tokens for GPT-4
    )

    if not aggregated_text:
        return None

    # Collect source IDs for provenance
    source_ids = [
        f"{p['book_id']}_{p['chunk_index']}"
        for p in passages[:100]  # Limit metadata
    ]

    prompt_template = config.load_prompt("infer_personality")
    prompt = prompt_template.format(
        person_name=person_name, passage_text=aggregated_text
    )

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

        # Add source metadata
        result["source_passage_ids"] = source_ids

        return result

    except Exception as e:
        print(f"Error inferring personality for {person_name}: {e}")
        return None


def run_personality(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Run personality inference on people from triples.

    Args:
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Path to output traits_final.jsonl file
    """
    with logger.stage_context("infer_personality"):
        # Load canonical triples
        triples_path = config.output_root / "triples_canonical.jsonl"
        logger.info("infer_personality", f"Loading triples from {triples_path}")

        triples = load_jsonl(triples_path)
        logger.info("infer_personality", f"Loaded {len(triples)} triples")

        # Extract people
        people = extract_people_from_triples(triples)
        logger.info("infer_personality", f"Found {len(people)} people")

        # Limit for testing
        if config.max_passages_per_book:
            people = list(people)[: min(5, len(people))]
            logger.info("infer_personality", f"Limited to {len(people)} people for testing")

        # Initialize client
        client = OpenAI()

        all_profiles = []

        # Process each person
        for person_name in tqdm(people, desc="Inferring personalities"):
            logger.info("infer_personality", f"Processing: {person_name}")

            # Find ALL relevant passages mentioning this character
            passages = find_passages_mentioning_person(person_name, config)

            if not passages:
                logger.warning(
                    "infer_personality",
                    f"No passages found for {person_name}",
                )
                continue

            logger.info(
                "infer_personality",
                f"Found {len(passages)} passages mentioning {person_name}",
                passage_count=len(passages),
            )

            # Infer personality using aggregated context from all passages
            profile = infer_personality_for_person(
                person_name, passages, config, client
            )

            if profile:
                all_profiles.append(profile)

        logger.info(
            "infer_personality",
            f"Generated {len(all_profiles)} personality profiles",
            profile_count=len(all_profiles),
        )

        # Save raw traits
        raw_output_path = config.output_root / "traits_raw.jsonl"
        save_jsonl(all_profiles, raw_output_path)
        logger.info("infer_personality", f"Saved raw traits to {raw_output_path}")

        # Filter by confidence, evidence quality, and save final
        final_profiles = []
        for profile in all_profiles:
            # Validate each trait's evidence quality
            valid_traits = []
            for trait in profile.get("traits", []):
                # Check confidence threshold
                if trait["confidence"] < config.confidence_threshold:
                    continue

                # Check evidence quality (min 2 spans, 50+ chars each, no overlap)
                if validate_trait_evidence(trait, min_spans=2, min_span_length=50):
                    valid_traits.append(trait)

            # Keep profile if at least 3 high-quality traits
            if len(valid_traits) >= 3:
                # Update profile with only valid traits
                profile["traits"] = valid_traits
                final_profiles.append(profile)

        logger.info(
            "infer_personality",
            f"Filtered to {len(final_profiles)} high-confidence profiles",
        )

        final_output_path = config.output_root / "traits_final.jsonl"
        save_jsonl(final_profiles, final_output_path)

        logger.info("infer_personality", f"Saved final traits to {final_output_path}")

        return final_output_path
