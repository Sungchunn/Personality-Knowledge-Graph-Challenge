"""
Detect whether a PDF is text-based or scanned (requires OCR).
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Literal


def detect_pdf_type(
    pdf_path: Path, sample_pages: int = 5, min_chars_per_page: int = 100
) -> Literal["text", "ocr"]:
    """
    Determine if a PDF is text-based or scanned by sampling initial pages.

    Args:
        pdf_path: Path to the PDF file
        sample_pages: Number of pages to sample from the beginning
        min_chars_per_page: Minimum characters expected for text-based PDF

    Returns:
        "text" if PDF contains extractable text, "ocr" if scanned
    """
    try:
        doc = fitz.open(pdf_path)
        pages_to_check = min(sample_pages, len(doc))

        total_chars = 0
        for page_num in range(pages_to_check):
            page = doc[page_num]
            text = page.get_text("text")
            total_chars += len(text.strip())

        doc.close()

        avg_chars = total_chars / pages_to_check if pages_to_check > 0 else 0

        # If average chars per page is below threshold, likely scanned
        if avg_chars < min_chars_per_page:
            return "ocr"
        return "text"

    except Exception as e:
        # If we can't open/read the PDF, assume it needs OCR
        print(f"Warning: Could not analyze {pdf_path}: {e}")
        return "ocr"
