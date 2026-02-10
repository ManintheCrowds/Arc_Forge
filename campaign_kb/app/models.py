# PURPOSE: ORM models for sources, documents, and sections.
# DEPENDENCIES: SQLAlchemy, PostgreSQL dialects
# MODIFICATION NOTES: Initial schema for MVP.

from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, Index, JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Source(Base):
    # PURPOSE: Track ingestion sources (PDFs, seeds, web).
    # DEPENDENCIES: SQLAlchemy
    # MODIFICATION NOTES: MVP source model.

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    documents: Mapped[list["Document"]] = relationship(back_populates="source", cascade="all, delete-orphan")


class Document(Base):
    # PURPOSE: Store document-level metadata and provenance.
    # DEPENDENCIES: SQLAlchemy
    # MODIFICATION NOTES: MVP document model.

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    source: Mapped["Source"] = relationship(back_populates="documents")
    sections: Mapped[list["Section"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Section(Base):
    # PURPOSE: Store chunked text content for search and citations.
    # DEPENDENCIES: SQLAlchemy, PostgreSQL TSVECTOR
    # MODIFICATION NOTES: MVP section model with computed search vector.

    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    section_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    search_vector: Mapped[str | None] = mapped_column(
        Text().with_variant(TSVECTOR, "postgresql"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    document: Mapped["Document"] = relationship(back_populates="sections")


Index("ix_sections_search_vector", Section.search_vector)
