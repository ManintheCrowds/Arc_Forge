# PURPOSE: Extract text sections from PDF files.
# DEPENDENCIES: pdfplumber, app.utils.text
# MODIFICATION NOTES: MVP PDF extraction utilities.

from pathlib import Path
from typing import Iterable
import pdfplumber
from app.utils.text import normalize_text


def extract_pdf_sections(pdf_path: Path) -> Iterable[dict]:
    # PURPOSE: Yield page-level sections from a PDF file.
    # DEPENDENCIES: pdfplumber, app.utils.text.normalize_text
    # MODIFICATION NOTES: MVP page-by-page extraction.
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            normalized = normalize_text(raw_text)
            if not normalized:
                continue
            yield {
                "page_number": page_index,
                "section_title": f"Page {page_index}",
                "raw_text": raw_text,
                "normalized_text": normalized,
            }
