"""
Split text into chapters or length-based chunks.
"""

import regex as re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    book_id: str
    chapter: Optional[int]
    chunk_index: int
    start_char: int
    end_char: int
    text: str


def detect_chapters(text: str) -> List[Dict[str, any]]:
    """
    Detect chapter boundaries using common patterns.

    Returns:
        List of dicts with keys: chapter_num, start_pos, pattern_matched
    """
    patterns = [
        r"^CHAPTER\s+([IVXLCDM]+)",  # CHAPTER I, CHAPTER XII
        r"^CHAPTER\s+(\d+)",  # Chapter 1, Chapter 23
        r"^Chapter\s+(\d+)",  # Chapter 1 (case-sensitive variant)
        r"^BOOK\s+([IVXLCDM]+)",  # BOOK I
        r"^BOOK\s+(\d+)",  # Book 1
        r"^Part\s+([IVXLCDM]+)",  # Part I
        r"^Part\s+(\d+)",  # Part 1
        r"^\d+\.\s+[A-Z]",  # "1. The Beginning" (numbered titles)
    ]

    chapters = []
    lines = text.split("\n")
    char_pos = 0

    for line_num, line in enumerate(lines):
        stripped = line.strip()

        for pattern in patterns:
            match = re.match(pattern, stripped, re.IGNORECASE | re.MULTILINE)
            if match:
                chapters.append(
                    {
                        "chapter_num": len(chapters) + 1,
                        "start_pos": char_pos,
                        "line_num": line_num,
                        "pattern": pattern,
                    }
                )
                break

        char_pos += len(line) + 1  # +1 for newline

    return chapters


def split_by_chapters(text: str, book_id: str) -> List[TextChunk]:
    """
    Split text by detected chapters.

    Returns:
        List of TextChunk objects, one per chapter
    """
    chapters = detect_chapters(text)

    if not chapters:
        return []

    chunks = []

    for i, chapter in enumerate(chapters):
        start_pos = chapter["start_pos"]
        # End is the start of next chapter, or end of text
        end_pos = chapters[i + 1]["start_pos"] if i + 1 < len(chapters) else len(text)

        chapter_text = text[start_pos:end_pos].strip()

        chunks.append(
            TextChunk(
                book_id=book_id,
                chapter=chapter["chapter_num"],
                chunk_index=i,
                start_char=start_pos,
                end_char=end_pos,
                text=chapter_text,
            )
        )

    return chunks


def split_by_length(
    text: str, book_id: str, min_chars: int = 1200, max_chars: int = 2000, overlap: int = 200
) -> List[TextChunk]:
    """
    Split text into overlapping chunks of approximately equal length.

    Args:
        text: Input text
        book_id: Book identifier
        min_chars: Minimum chunk size
        max_chars: Maximum chunk size
        overlap: Number of characters to overlap between chunks

    Returns:
        List of TextChunk objects
    """
    chunks = []
    chunk_index = 0
    start = 0
    text_len = len(text)

    while start < text_len:
        # Determine end position
        end = min(start + max_chars, text_len)

        # If not at the end, try to break at sentence/paragraph boundary
        if end < text_len:
            # Look for paragraph break first
            para_break = text.rfind("\n\n", start + min_chars, end)
            if para_break != -1 and para_break > start + min_chars:
                end = para_break
            else:
                # Look for sentence break
                sentence_break = max(
                    text.rfind(". ", start + min_chars, end),
                    text.rfind("! ", start + min_chars, end),
                    text.rfind("? ", start + min_chars, end),
                )
                if sentence_break != -1 and sentence_break > start + min_chars:
                    end = sentence_break + 1  # Include the punctuation

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    book_id=book_id,
                    chapter=None,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end,
                    text=chunk_text,
                )
            )
            chunk_index += 1

        # Move start position with overlap
        start = end - overlap if end < text_len else text_len

    return chunks


def split_text(
    text: str,
    book_id: str,
    min_chars: int = 1200,
    max_chars: int = 2000,
    overlap: int = 200,
) -> List[TextChunk]:
    """
    Split text into structured chunks, preferring chapter detection.

    Args:
        text: Cleaned text to split
        book_id: Book identifier
        min_chars: Minimum chunk size for length-based splitting
        max_chars: Maximum chunk size for length-based splitting
        overlap: Overlap for length-based splitting

    Returns:
        List of TextChunk objects
    """
    # Try chapter-based splitting first
    chapters = split_by_chapters(text, book_id)

    if chapters and len(chapters) >= 3:  # At least 3 chapters for confidence
        return chapters

    # Fallback to length-based chunking
    return split_by_length(text, book_id, min_chars, max_chars, overlap)
