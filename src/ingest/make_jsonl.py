"""
Create JSONL files from text chunks with metadata.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from .split_structure import TextChunk


def chunk_to_dict(
    chunk: TextChunk,
    title: str,
    authors: List[str],
    source_path: str,
    extraction_mode: str,
) -> Dict:
    """
    Convert a TextChunk to a dictionary suitable for JSONL export.

    Args:
        chunk: TextChunk object
        title: Book title
        authors: List of author names
        source_path: Absolute path to source PDF
        extraction_mode: "text" or "ocr"

    Returns:
        Dictionary with all metadata
    """
    return {
        "book_id": chunk.book_id,
        "title": title,
        "authors": authors,
        "source_path": source_path,
        "extraction_mode": extraction_mode,
        "chapter": chunk.chapter,
        "chunk_index": chunk.chunk_index,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
        "text": chunk.text,
    }


def write_jsonl(
    chunks: List[TextChunk],
    output_path: Path,
    title: str,
    authors: List[str],
    source_path: str,
    extraction_mode: str,
) -> None:
    """
    Write chunks to a JSONL file.

    Args:
        chunks: List of TextChunk objects
        output_path: Path to write JSONL file
        title: Book title
        authors: List of authors
        source_path: Source PDF path
        extraction_mode: Extraction method used
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            record = chunk_to_dict(chunk, title, authors, source_path, extraction_mode)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
