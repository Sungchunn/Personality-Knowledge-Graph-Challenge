"""
Extract knowledge graph triples from text passages.
"""

import json
from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

from .config import PipelineConfig
from .io_utils import discover_jsonl_files, iter_jsonl, save_jsonl
from .logging_utils import PipelineLogger
from .schemas import Triple, TextSpan


def extract_triples_from_passage(
    passage: Dict[str, Any],
    config: PipelineConfig,
    client: OpenAI,
) -> List[Dict[str, Any]]:
    """
    Extract triples from a single passage using LLM.

    Args:
        passage: JSONL passage record
        config: Pipeline configuration
        client: OpenAI API client

    Returns:
        List of triple dictionaries
    """
    prompt_template = config.load_prompt("extract_triples")
    prompt = prompt_template.format(passage_text=passage["text"])

    try:
        response = client.chat.completions.create(
            model=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content

        # Parse JSON response
        result = json.loads(response_text)
        triples = result.get("triples", [])

        # Add source metadata
        for triple in triples:
            triple["source_passage_id"] = f"{passage['book_id']}_{passage['chunk_index']}"
            triple["book_id"] = passage["book_id"]

        return triples

    except Exception as e:
        print(f"Error extracting triples from passage: {e}")
        return []


def run_extract(config: PipelineConfig, logger: PipelineLogger) -> Path:
    """
    Run triple extraction on all input passages.

    Args:
        config: Pipeline configuration
        logger: Pipeline logger

    Returns:
        Path to output triples_raw.jsonl file
    """
    with logger.stage_context("extract_triples"):
        logger.info("extract_triples", "Discovering input JSONL files")

        # Discover input files (single file mode or all files)
        if config.input_file:
            jsonl_files = [config.input_file]
            logger.info(
                "extract_triples",
                f"Processing single file: {config.input_file.name}",
            )
        else:
            jsonl_files = discover_jsonl_files(config.input_jsonl_root)
            logger.info(
                "extract_triples",
                f"Found {len(jsonl_files)} JSONL files",
                file_count=len(jsonl_files),
            )

        # Initialize OpenAI client
        client = OpenAI()

        all_triples = []
        passage_count = 0

        # Process each book
        for jsonl_file in tqdm(jsonl_files, desc="Processing books"):
            book_id = jsonl_file.stem
            logger.info("extract_triples", f"Processing book: {book_id}")

            passages = list(iter_jsonl(jsonl_file))

            # Limit passages if configured
            if config.max_passages_per_book:
                passages = passages[: config.max_passages_per_book]

            # Process each passage
            for passage in tqdm(
                passages, desc=f"  {book_id}", leave=False, disable=True
            ):
                triples = extract_triples_from_passage(passage, config, client)
                all_triples.extend(triples)
                passage_count += 1

        logger.info(
            "extract_triples",
            f"Extracted {len(all_triples)} triples from {passage_count} passages",
            triple_count=len(all_triples),
            passage_count=passage_count,
        )

        # Save raw triples
        output_path = config.output_root / "triples_raw.jsonl"
        save_jsonl(all_triples, output_path)

        logger.info("extract_triples", f"Saved raw triples to {output_path}")

        return output_path
