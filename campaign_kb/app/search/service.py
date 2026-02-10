# PURPOSE: Search logic for full-text queries over sections.
# DEPENDENCIES: SQLAlchemy, PostgreSQL full-text search
# MODIFICATION NOTES: MVP search service using plainto_tsquery.

from sqlalchemy import func, literal
from sqlalchemy.orm import Session
from app.models import Section, Document, Source


def search_sections(
    db: Session,
    query: str,
    limit: int = 20,
    source_name: str | None = None,
    doc_type: str | None = None,
) -> list[tuple[Section, float]]:
    # PURPOSE: Execute a ranked full-text search for sections.
    # DEPENDENCIES: SQLAlchemy
    # MODIFICATION NOTES: SQLite uses LIKE; Postgres uses tsvector.
    dialect = db.get_bind().dialect.name if db.get_bind() is not None else "unknown"
    if dialect == "sqlite":
        like_pattern = f"%{query.lower()}%"
        rank = literal(0.0)
        base_query = (
            db.query(Section, rank.label("rank"))
            .join(Document, Section.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .filter(func.lower(Section.normalized_text).like(like_pattern))
            .order_by(Section.id.asc())
        )
    else:
        ts_query = func.plainto_tsquery("english", query)
        rank = func.ts_rank_cd(Section.search_vector, ts_query)
        base_query = (
            db.query(Section, rank.label("rank"))
            .join(Document, Section.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .filter(Section.search_vector.op("@@")(ts_query))
            .order_by(rank.desc())
        )
    if source_name:
        base_query = base_query.filter(Source.name == source_name)
    if doc_type:
        base_query = base_query.filter(Document.doc_type == doc_type)

    return base_query.limit(limit).all()
