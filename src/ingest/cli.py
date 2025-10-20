"""
Command-line interface for PDF ingestion pipeline.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict
from tqdm import tqdm
from slugify import slugify

from .detect_pdf_type import detect_pdf_type
from .pdf_to_text import extract_pdf
from .clean_text import clean_text
from .split_structure import split_text
from .make_jsonl import write_jsonl
from .manifest import create_manifest, write_manifest, compute_sha256


def parse_filename_metadata(pdf_path: Path) -> Dict[str, any]:
    """
    Attempt to extract title and authors from filename.

    Common patterns:
    - "Title - Author.pdf"
    - "Author - Title.pdf"
    - "Title.pdf"

    Returns:
        Dict with 'title' and 'authors' keys
    """
    stem = pdf_path.stem

    # Try to split on common separators
    if " - " in stem:
        parts = stem.split(" - ", 1)
        # Heuristic: if first part looks like author (short), use it
        if len(parts[0].split()) <= 3:
            return {"title": parts[1], "authors": [parts[0]]}
        else:
            return {"title": parts[0], "authors": [parts[1]]}
    elif " by " in stem.lower():
        parts = stem.lower().split(" by ", 1)
        return {"title": parts[0].strip(), "authors": [parts[1].strip()]}
    else:
        # Just use filename as title
        return {"title": stem, "authors": ["Unknown"]}


def discover_pdfs(root_dir: Path) -> List[Path]:
    """
    Recursively discover all PDF files in a directory.

    Args:
        root_dir: Root directory to search

    Returns:
        List of PDF file paths
    """
    return sorted(root_dir.rglob("*.pdf"))


def should_process(
    pdf_path: Path, text_path: Path, jsonl_path: Path, manifest_path: Path
) -> bool:
    """
    Determine if a PDF should be processed (idempotency check).

    Skip if:
    - All output files exist
    - PDF hasn't changed (based on manifest checksum)

    Args:
        pdf_path: Source PDF path
        text_path: Expected text output path
        jsonl_path: Expected JSONL output path
        manifest_path: Expected manifest path

    Returns:
        True if should process, False if can skip
    """
    # If any output missing, must process
    if not all([text_path.exists(), jsonl_path.exists(), manifest_path.exists()]):
        return True

    # Check if PDF has changed
    try:
        with manifest_path.open("r") as f:
            manifest = json.load(f)

        current_hash = compute_sha256(pdf_path)
        stored_hash = manifest.get("pdf_sha256", "")

        if current_hash != stored_hash:
            return True  # PDF changed, reprocess

        return False  # All outputs exist and PDF unchanged

    except Exception:
        return True  # If can't read manifest, reprocess


def process_pdf(
    pdf_path: Path,
    out_root: Path,
    ocr_mode: str,
    min_chars: int,
    max_chars: int,
    overlap: int,
) -> Dict[str, any]:
    """
    Process a single PDF through the complete pipeline.

    Args:
        pdf_path: Path to PDF file
        out_root: Root output directory
        ocr_mode: "auto", "text", or "ocr"
        min_chars: Minimum chunk size
        max_chars: Maximum chunk size
        overlap: Chunk overlap

    Returns:
        Dict with processing results and metadata
    """
    result = {
        "pdf_path": str(pdf_path),
        "success": False,
        "error": None,
        "book_id": None,
        "num_chunks": 0,
        "extraction_mode": None,
    }

    try:
        # Generate book_id and metadata
        book_id = slugify(pdf_path.stem, max_length=100)
        metadata = parse_filename_metadata(pdf_path)

        result["book_id"] = book_id

        # Define output paths
        text_path = out_root / "text" / f"{book_id}.txt"
        jsonl_path = out_root / "jsonl" / f"{book_id}.jsonl"
        manifest_path = out_root / "metadata" / f"{book_id}.json"

        # Check if should process (idempotency)
        if not should_process(pdf_path, text_path, jsonl_path, manifest_path):
            result["success"] = True
            result["skipped"] = True
            return result

        # Extract text
        raw_text, extraction_mode = extract_pdf(pdf_path, mode=ocr_mode)
        result["extraction_mode"] = extraction_mode

        if not raw_text.strip():
            result["error"] = "No text extracted"
            return result

        # Clean text
        cleaned_text = clean_text(raw_text)

        # Save cleaned text
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(cleaned_text, encoding="utf-8")

        # Split into chunks
        chunks = split_text(cleaned_text, book_id, min_chars, max_chars, overlap)

        if not chunks:
            result["error"] = "No chunks created"
            return result

        result["num_chunks"] = len(chunks)

        # Determine split method
        split_method = "chapters" if chunks[0].chapter is not None else "length"

        # Write JSONL
        write_jsonl(
            chunks,
            jsonl_path,
            title=metadata["title"],
            authors=metadata["authors"],
            source_path=str(pdf_path.resolve()),
            extraction_mode=extraction_mode,
        )

        # Create and write manifest
        manifest = create_manifest(
            book_id=book_id,
            title=metadata["title"],
            authors=metadata["authors"],
            source_path=pdf_path,
            cleaned_text=cleaned_text,
            extraction_mode=extraction_mode,
            num_chunks=len(chunks),
            split_method=split_method,
        )

        write_manifest(manifest, manifest_path)

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="PDF Ingestion Pipeline for Knowledge Graph",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--pdf-root",
        type=Path,
        required=True,
        help="Root directory containing PDFs to process",
    )

    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path("./data"),
        help="Root directory for outputs (text, jsonl, metadata)",
    )

    parser.add_argument(
        "--ocr",
        choices=["auto", "text", "ocr"],
        default="auto",
        help="Extraction mode: auto-detect, force text, or force OCR",
    )

    parser.add_argument(
        "--min-chars",
        type=int,
        default=1200,
        help="Minimum chunk size (characters)",
    )

    parser.add_argument(
        "--max-chars",
        type=int,
        default=2000,
        help="Maximum chunk size (characters)",
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=200,
        help="Overlap between chunks (characters)",
    )

    parser.add_argument(
        "--only-mode",
        choices=["text", "ocr"],
        help="Only process PDFs of specific type",
    )

    args = parser.parse_args()

    # Validate paths
    if not args.pdf_root.exists():
        print(f"Error: PDF root directory does not exist: {args.pdf_root}")
        sys.exit(1)

    # Discover PDFs
    print(f"Discovering PDFs in: {args.pdf_root}")
    pdf_files = discover_pdfs(args.pdf_root)

    if not pdf_files:
        print("No PDF files found.")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF files")

    # Filter by mode if requested
    if args.only_mode:
        filtered = []
        for pdf in tqdm(pdf_files, desc="Filtering by type"):
            detected = detect_pdf_type(pdf)
            if detected == args.only_mode:
                filtered.append(pdf)
        pdf_files = filtered
        print(f"Filtered to {len(pdf_files)} {args.only_mode} PDFs")

    # Process each PDF
    results = []
    successful = 0
    skipped = 0
    failed = 0

    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        result = process_pdf(
            pdf_path,
            args.out_root,
            args.ocr,
            args.min_chars,
            args.max_chars,
            args.overlap,
        )

        results.append(result)

        if result["success"]:
            if result.get("skipped"):
                skipped += 1
            else:
                successful += 1
        else:
            failed += 1
            print(f"\nFailed: {pdf_path.name} - {result['error']}")

    # Write run log
    log_path = args.out_root / "metadata" / f"ingest_run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    run_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pdf_root": str(args.pdf_root.resolve()),
        "out_root": str(args.out_root.resolve()),
        "total_pdfs": len(pdf_files),
        "successful": successful,
        "skipped": skipped,
        "failed": failed,
        "parameters": {
            "ocr_mode": args.ocr,
            "min_chars": args.min_chars,
            "max_chars": args.max_chars,
            "overlap": args.overlap,
            "only_mode": args.only_mode,
        },
        "results": results,
    }

    with log_path.open("w") as f:
        json.dump(run_log, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"Total PDFs:      {len(pdf_files)}")
    print(f"Successful:      {successful}")
    print(f"Skipped:         {skipped}")
    print(f"Failed:          {failed}")
    print(f"Run log:         {log_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
