"""
Generate provenance metadata manifests for processed books.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional


def compute_sha256(file_path: Path) -> str:
    """
    Compute SHA256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compute_text_sha256(text: str) -> str:
    """
    Compute SHA256 hash of text string.

    Args:
        text: Text content

    Returns:
        Hex digest of SHA256 hash
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_manifest(
    book_id: str,
    title: str,
    authors: List[str],
    source_path: Path,
    cleaned_text: str,
    extraction_mode: str,
    num_chunks: int,
    split_method: str,
    year: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict:
    """
    Create a metadata manifest for a processed book.

    Args:
        book_id: Book identifier
        title: Book title
        authors: List of authors
        source_path: Path to source PDF
        cleaned_text: Cleaned text content
        extraction_mode: "text" or "ocr"
        num_chunks: Number of chunks created
        split_method: "chapters" or "length"
        year: Publication year (if known)
        notes: Additional notes

    Returns:
        Manifest dictionary
    """
    pdf_hash = compute_sha256(source_path)
    text_hash = compute_text_sha256(cleaned_text)

    manifest = {
        "book_id": book_id,
        "title": title,
        "authors": authors,
        "year": year,
        "source_path": str(source_path.resolve()),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "extraction_mode": extraction_mode,
        "split_method": split_method,
        "num_chunks": num_chunks,
        "pdf_sha256": pdf_hash,
        "cleaned_text_sha256": text_hash,
        "cleaned_text_length": len(cleaned_text),
        "notes": notes or "",
    }

    return manifest


def write_manifest(manifest: Dict, output_path: Path) -> None:
    """
    Write manifest to JSON file.

    Args:
        manifest: Manifest dictionary
        output_path: Path to write JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
