"""
Extract text from PDFs using PyMuPDF or OCR fallback.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Tuple
import subprocess
import tempfile
import io


def extract_text_based_pdf(pdf_path: Path) -> str:
    """
    Extract text from a text-based PDF using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Concatenated text from all pages
    """
    doc = fitz.open(pdf_path)
    pages_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages_text.append(text)

    doc.close()

    # Join pages with single newline
    return "\n".join(pages_text)


def extract_scanned_pdf_ocrmypdf(pdf_path: Path) -> Tuple[str, bool]:
    """
    Attempt OCR using ocrmypdf CLI tool (if available).

    Args:
        pdf_path: Path to the scanned PDF

    Returns:
        Tuple of (extracted text, success flag)
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_output:
            tmp_path = Path(tmp_output.name)

        # Run ocrmypdf
        result = subprocess.run(
            [
                "ocrmypdf",
                "--force-ocr",
                "--output-type",
                "pdf",
                str(pdf_path),
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            # Extract text from OCR'd PDF
            text = extract_text_based_pdf(tmp_path)
            tmp_path.unlink()
            return text, True
        else:
            if tmp_path.exists():
                tmp_path.unlink()
            return "", False

    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return "", False


def extract_scanned_pdf_pytesseract(pdf_path: Path) -> str:
    """
    Fallback OCR using pytesseract on rendered PDF pages.

    Args:
        pdf_path: Path to the scanned PDF

    Returns:
        Concatenated OCR text from all pages
    """
    doc = fitz.open(pdf_path)
    pages_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render page to image at 300 DPI
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # Run Tesseract OCR
        text = pytesseract.image_to_string(img, lang="eng")
        pages_text.append(text)

    doc.close()

    return "\n".join(pages_text)


def extract_pdf(pdf_path: Path, mode: str = "auto") -> Tuple[str, str]:
    """
    Extract text from PDF using appropriate method.

    Args:
        pdf_path: Path to PDF file
        mode: "text", "ocr", or "auto" (auto-detect)

    Returns:
        Tuple of (extracted text, extraction mode used)
    """
    from .detect_pdf_type import detect_pdf_type

    if mode == "auto":
        detected_mode = detect_pdf_type(pdf_path)
    else:
        detected_mode = mode

    if detected_mode == "text":
        text = extract_text_based_pdf(pdf_path)
        return text, "text"
    else:
        # Try ocrmypdf first, fallback to pytesseract
        text, success = extract_scanned_pdf_ocrmypdf(pdf_path)
        if success and text.strip():
            return text, "ocr_ocrmypdf"
        else:
            text = extract_scanned_pdf_pytesseract(pdf_path)
            return text, "ocr_pytesseract"
