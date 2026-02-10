# PURPOSE: Extract sections from seed documents.
# DEPENDENCIES: pathlib, app.utils.text
# MODIFICATION NOTES: MVP seed ingestion utilities.

from pathlib import Path
from app.utils.text import normalize_text


def extract_seed_sections(seed_path: Path) -> list[dict]:
    # PURPOSE: Convert a seed doc into a single section payload.
    # DEPENDENCIES: pathlib, app.utils.text.normalize_text
    # MODIFICATION NOTES: MVP seed ingestion as single section.
    raw_text = seed_path.read_text(encoding="utf-8", errors="ignore")
    normalized = normalize_text(raw_text)
    if not normalized:
        return []
    return [
        {
            "page_number": None,
            "section_title": "Seed Document",
            "raw_text": raw_text,
            "normalized_text": normalized,
        }
    ]
