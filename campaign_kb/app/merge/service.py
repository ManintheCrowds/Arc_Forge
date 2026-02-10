# PURPOSE: Merge seed docs and attach citations from indexed sources.
# DEPENDENCIES: pathlib, sqlalchemy, app.utils.text, app.search.service
# MODIFICATION NOTES: MVP merged seed doc generator.

from pathlib import Path
from sqlalchemy.orm import Session
from app.search.service import search_sections
from app.utils.text import extract_keywords, normalize_text
from app.models import Section, Document, Source


def _render_citation(section: Section, document: Document, source: Source) -> str:
    # PURPOSE: Format a simple citation line for a section result.
    # DEPENDENCIES: app.models
    # MODIFICATION NOTES: MVP citation formatter.
    location = f"p.{section.page_number}" if section.page_number else "n/a"
    origin = document.url or document.path or "unknown"
    return f"- {document.title} ({source.name}) [{location}] {origin}"


def create_merged_seed_doc(
    db: Session,
    seed_paths: list[Path],
    output_path: Path,
    max_citations: int = 25,
) -> tuple[Path, int]:
    # PURPOSE: Merge seed docs and append source citations for baseline context.
    # DEPENDENCIES: SQLAlchemy, app.utils.text, app.search.service
    # MODIFICATION NOTES: MVP merge output for campaign baseline.
    merged_sections: list[str] = []
    combined_seed_text = ""

    for seed_path in seed_paths:
        if not seed_path.exists():
            continue
        raw_text = seed_path.read_text(encoding="utf-8", errors="ignore")
        merged_sections.append(f"## Seed: {seed_path.name}\n\n{raw_text.strip()}\n")
        combined_seed_text += f"\n{raw_text}"

    normalized = normalize_text(combined_seed_text)
    keywords = extract_keywords(normalized, max_terms=20)

    citations: list[str] = []
    seen_section_ids: set[int] = set()
    for term in keywords:
        results = search_sections(db, term, limit=3)
        for section, _rank in results:
            if section.id in seen_section_ids:
                continue
            seen_section_ids.add(section.id)
            document = db.query(Document).filter(Document.id == section.document_id).one()
            source = db.query(Source).filter(Source.id == document.source_id).one()
            citations.append(_render_citation(section, document, source))
            if len(citations) >= max_citations:
                break
        if len(citations) >= max_citations:
            break

    citations_block = "\n".join(citations)
    output_text = "# Merged Campaign Seed Doc\n\n" + "\n".join(merged_sections)
    if citations_block:
        output_text += "\n## Source Citations\n\n" + citations_block + "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    return output_path, len(citations)
