# PURPOSE: Extract sections from local reference documents.
# DEPENDENCIES: pathlib, app.utils.text
# MODIFICATION NOTES: MVP doc ingestion utilities for markdown/text/html.

from pathlib import Path
from app.utils.text import normalize_text


def extract_doc_section(doc_path: Path) -> dict | None:
    # PURPOSE: Convert a docs file into a section payload.
    # DEPENDENCIES: pathlib, app.utils.text.normalize_text
    # MODIFICATION NOTES: MVP docs ingestion as single section per file.
    try:
        raw_text = doc_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    normalized = normalize_text(raw_text)
    if not normalized:
        return None
    return {
        "section_title": doc_path.name,
        "raw_text": raw_text,
        "normalized_text": normalized,
    }
