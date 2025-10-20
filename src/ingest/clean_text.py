"""
Clean and normalize extracted text from PDFs.
"""

import regex as re
import unicodedata
from typing import List


def normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC form."""
    return unicodedata.normalize("NFC", text)


def collapse_whitespace(text: str) -> str:
    """Collapse multiple spaces to single space."""
    # Replace multiple spaces with single space
    text = re.sub(r" {2,}", " ", text)
    return text


def dehyphenate(text: str) -> str:
    """
    Remove line-break hyphens while preserving compound words.
    Converts: 'exam-\nple' -> 'example'
    Preserves: 'long-term' (same line)
    """
    # Remove hyphen followed by newline and optional whitespace
    text = re.sub(r"-\s*\n\s*", "", text)
    return text


def remove_page_numbers_headers(text: str) -> str:
    """
    Heuristically remove page numbers and repeated headers/footers.
    """
    lines = text.split("\n")
    cleaned_lines = []

    # Track repeated short lines that appear frequently (likely headers/footers)
    line_freq = {}
    for line in lines:
        stripped = line.strip()
        if len(stripped) < 80:  # Short lines only
            line_freq[stripped] = line_freq.get(stripped, 0) + 1

    # Consider lines appearing 5+ times as headers/footers
    common_lines = {line for line, count in line_freq.items() if count >= 5}

    for line in lines:
        stripped = line.strip()

        # Skip empty lines temporarily (we'll normalize later)
        if not stripped:
            cleaned_lines.append("")
            continue

        # Skip common headers/footers
        if stripped in common_lines:
            continue

        # Skip lines that look like page numbers
        if re.match(r"^[\d\s\-–—]+$", stripped) and len(stripped) < 10:
            continue

        # Skip lines like "Page 123" or "Chapter 5 - 123"
        if re.match(r"^(page|p\.?)\s*\d+", stripped, re.IGNORECASE):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def normalize_paragraph_breaks(text: str) -> str:
    """
    Normalize paragraph breaks: preserve intentional paragraph breaks (double newline),
    collapse accidental single newlines within paragraphs.
    """
    # First, collapse 3+ newlines to double newline
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Split into potential paragraphs
    paragraphs = re.split(r"\n\n+", text)

    cleaned_paragraphs = []
    for para in paragraphs:
        # Within each paragraph, replace single newlines with space
        para = re.sub(r"(?<!\n)\n(?!\n)", " ", para)
        para = para.strip()
        if para:
            cleaned_paragraphs.append(para)

    # Join paragraphs with double newline
    return "\n\n".join(cleaned_paragraphs)


def clean_text(text: str) -> str:
    """
    Complete text cleaning pipeline.

    Steps:
    1. Normalize Unicode (NFC)
    2. Dehyphenate line breaks
    3. Remove page numbers and headers/footers
    4. Collapse whitespace
    5. Normalize paragraph breaks

    Args:
        text: Raw extracted text

    Returns:
        Cleaned, normalized text
    """
    # Normalize Unicode
    text = normalize_unicode(text)

    # Dehyphenate
    text = dehyphenate(text)

    # Remove page artifacts
    text = remove_page_numbers_headers(text)

    # Collapse whitespace
    text = collapse_whitespace(text)

    # Normalize paragraphs
    text = normalize_paragraph_breaks(text)

    # Final trim
    text = text.strip()

    return text
