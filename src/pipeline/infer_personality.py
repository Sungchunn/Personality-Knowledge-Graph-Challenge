"""
Infer Big Five personality traits for people mentioned in text.
"""

import json
import anthropic
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict
from tqdm import tqdm

from .config import PipelineConfig
from .io_utils import discover_jsonl_files, iter_jsonl, load_jsonl, save_jsonl
from .logging_utils import PipelineLogger


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
    jsonl_files = discover_jsonl_files(config.input_jsonl_root)

    for jsonl_file in jsonl_files:
        for passage in iter_jsonl(jsonl_file):
            if person_name.lower() in passage["text"].lower():
                passages.append(passage)

    return passages


def infer_personality_for_person(
    person_name: str,
    passages: List[Dict[str, Any]],
    config: PipelineConfig,
    client: anthropic.Anthropic,
) -> Dict[str, Any]:
    """
    Infer Big Five personality traits for a person.

    Args:
        person_name: Name of person
        passages: Relevant text passages
        config: Pipeline configuration
        client: Anthropic API client

    Returns:
        Personality profile dictionary
    """
    # Combine passages (limit to avoid token limits)
    max_context = 8000
    combined_text = ""
    source_ids = []

    for passage in passages[:10]:  # Limit passages
        combined_text += passage["text"] + "\n\n"
        source_ids.append(f"{passage['book_id']}_{passage['chunk_index']}")

        if len(combined_text) > max_context:
            break

    prompt_template = config.load_prompt("infer_personality")
    prompt = prompt_template.format(
        person_name=person_name, passage_text=combined_text
    )

    try:
        message = client.messages.create(
            model=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
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
        client = anthropic.Anthropic()

        all_profiles = []

        # Process each person
        for person_name in tqdm(people, desc="Inferring personalities"):
            logger.info("infer_personality", f"Processing: {person_name}")

            # Find relevant passages
            passages = find_passages_mentioning_person(person_name, config)

            if not passages:
                logger.warning(
                    "infer_personality",
                    f"No passages found for {person_name}",
                )
                continue

            # Infer personality
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

        # Filter by confidence and save final
        final_profiles = []
        for profile in all_profiles:
            # Check if at least 3 traits meet confidence threshold
            high_conf_traits = sum(
                1
                for trait in profile.get("traits", [])
                if trait["confidence"] >= config.confidence_threshold
            )

            if high_conf_traits >= 3:
                final_profiles.append(profile)

        logger.info(
            "infer_personality",
            f"Filtered to {len(final_profiles)} high-confidence profiles",
        )

        final_output_path = config.output_root / "traits_final.jsonl"
        save_jsonl(final_profiles, final_output_path)

        logger.info("infer_personality", f"Saved final traits to {final_output_path}")

        return final_output_path
