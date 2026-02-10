# PURPOSE: Orchestrate ingestion into the database.
# DEPENDENCIES: SQLAlchemy, ingest modules
# MODIFICATION NOTES: MVP ingest orchestration for PDFs, seeds, and web.

from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Source, Document, Section
from app.utils.files import list_pdf_files, list_text_files
from app.ingest.pdf_ingest import extract_pdf_sections
from app.ingest.seed_ingest import extract_seed_sections
from app.ingest.dod_crawl import crawl_doctors_of_doom
from app.ingest.docs_ingest import extract_doc_section
from app.ingest.repo_ingest import extract_repo_documents


def _get_or_create_source(
    db: Session,
    name: str,
    source_type: str,
    base_url: str | None = None,
) -> Source:
    # PURPOSE: Reuse or create a source record.
    # DEPENDENCIES: SQLAlchemy Session, app.models.Source
    # MODIFICATION NOTES: MVP upsert-style helper.
    existing = db.query(Source).filter(Source.name == name).one_or_none()
    if existing:
        return existing
    source = Source(name=name, source_type=source_type, base_url=base_url)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def ingest_pdfs(db: Session, pdf_root: Path, source_name: str = "local_pdfs") -> tuple[int, int]:
    # PURPOSE: Ingest all PDFs under a directory into the database.
    # DEPENDENCIES: SQLAlchemy, pdfplumber
    # MODIFICATION NOTES: MVP PDF ingestion with page sections.
    source = _get_or_create_source(db, source_name, "pdf", None)
    documents_ingested = 0
    sections_ingested = 0

    for pdf_path in list_pdf_files(pdf_root):
        document = Document(
            source_id=source.id,
            title=pdf_path.stem,
            doc_type="pdf",
            path=str(pdf_path),
            url=None,
            metadata_json=None,
        )
        db.add(document)
        db.flush()
        position = 0
        for section_payload in extract_pdf_sections(pdf_path):
            section = Section(
                document_id=document.id,
                section_title=section_payload["section_title"],
                page_number=section_payload["page_number"],
                position=position,
                raw_text=section_payload["raw_text"],
                normalized_text=section_payload["normalized_text"],
            )
            db.add(section)
            position += 1
            sections_ingested += 1
        documents_ingested += 1

    db.commit()
    return documents_ingested, sections_ingested


def ingest_reference_docs(
    db: Session,
    docs_root: Path,
    source_name: str = "dod_docs",
) -> tuple[int, int]:
    # PURPOSE: Ingest local reference docs into the database.
    # DEPENDENCIES: SQLAlchemy, app.utils.files.list_text_files
    # MODIFICATION NOTES: MVP ingestion for markdown/text/html and PDFs.
    source = _get_or_create_source(db, source_name, "docs", None)
    documents_ingested = 0
    sections_ingested = 0

    for doc_path in list_text_files(docs_root, recursive=True):
        section_payload = extract_doc_section(doc_path)
        if not section_payload:
            continue
        document = Document(
            source_id=source.id,
            title=doc_path.stem,
            doc_type="doc",
            path=str(doc_path),
            url=None,
            metadata_json=None,
        )
        db.add(document)
        db.flush()
        section = Section(
            document_id=document.id,
            section_title=section_payload["section_title"],
            page_number=None,
            position=0,
            raw_text=section_payload["raw_text"],
            normalized_text=section_payload["normalized_text"],
        )
        db.add(section)
        documents_ingested += 1
        sections_ingested += 1

    for pdf_path in list_pdf_files(docs_root, recursive=True):
        document = Document(
            source_id=source.id,
            title=pdf_path.stem,
            doc_type="doc_pdf",
            path=str(pdf_path),
            url=None,
            metadata_json=None,
        )
        db.add(document)
        db.flush()
        position = 0
        for section_payload in extract_pdf_sections(pdf_path):
            section = Section(
                document_id=document.id,
                section_title=section_payload["section_title"],
                page_number=section_payload["page_number"],
                position=position,
                raw_text=section_payload["raw_text"],
                normalized_text=section_payload["normalized_text"],
            )
            db.add(section)
            position += 1
            sections_ingested += 1
        documents_ingested += 1

    db.commit()
    return documents_ingested, sections_ingested


def ingest_seed_docs(db: Session, seed_paths: list[Path], source_name: str = "seed_docs") -> tuple[int, int]:
    # PURPOSE: Ingest seed documents as authoritative notes.
    # DEPENDENCIES: SQLAlchemy
    # MODIFICATION NOTES: MVP seed ingestion with single section per doc.
    source = _get_or_create_source(db, source_name, "seed", None)
    documents_ingested = 0
    sections_ingested = 0

    for seed_path in seed_paths:
        if not seed_path.exists():
            continue
        document = Document(
            source_id=source.id,
            title=seed_path.stem,
            doc_type="seed",
            path=str(seed_path),
            url=None,
            metadata_json=None,
        )
        db.add(document)
        db.flush()
        for position, section_payload in enumerate(extract_seed_sections(seed_path)):
            section = Section(
                document_id=document.id,
                section_title=section_payload["section_title"],
                page_number=None,
                position=position,
                raw_text=section_payload["raw_text"],
                normalized_text=section_payload["normalized_text"],
            )
            db.add(section)
            sections_ingested += 1
        documents_ingested += 1

    db.commit()
    return documents_ingested, sections_ingested


def ingest_dod_site(
    db: Session,
    base_url: str,
    max_pages: int,
    timeout_seconds: float,
    user_agent: str,
    source_name: str = "doctors_of_doom",
) -> tuple[int, int]:
    # PURPOSE: Ingest Doctors of Doom site pages into the database.
    # DEPENDENCIES: SQLAlchemy, httpx, BeautifulSoup
    # MODIFICATION NOTES: MVP crawl ingestion with one section per page.
    source = _get_or_create_source(db, source_name, "web", base_url)
    documents_ingested = 0
    sections_ingested = 0

    for page in crawl_doctors_of_doom(base_url, max_pages, timeout_seconds, user_agent):
        document = Document(
            source_id=source.id,
            title=page.title,
            doc_type="web",
            path=None,
            url=page.url,
            metadata_json=None,
        )
        db.add(document)
        db.flush()
        section = Section(
            document_id=document.id,
            section_title=page.title,
            page_number=None,
            position=0,
            raw_text=page.text,
            normalized_text=page.text,
        )
        db.add(section)
        documents_ingested += 1
        sections_ingested += 1

    db.commit()
    return documents_ingested, sections_ingested


def ingest_github_repos(
    db: Session,
    repo_urls: list[str],
    timeout_seconds: float,
    source_name: str = "github_repos",
) -> tuple[int, int]:
    # PURPOSE: Ingest documentation from GitHub repositories.
    # DEPENDENCIES: SQLAlchemy, app.ingest.repo_ingest.extract_repo_documents
    # MODIFICATION NOTES: MVP repo ingestion by downloading zip archives.
    source = _get_or_create_source(db, source_name, "repo", None)
    documents_ingested = 0
    sections_ingested = 0

    for repo_url in repo_urls:
        documents = extract_repo_documents(repo_url, timeout_seconds=timeout_seconds)
        for doc in documents:
            document = Document(
                source_id=source.id,
                title=doc.title,
                doc_type="repo_doc",
                path=doc.relative_path,
                url=repo_url,
                metadata_json=None,
            )
            db.add(document)
            db.flush()
            section = Section(
                document_id=document.id,
                section_title=doc.relative_path,
                page_number=None,
                position=0,
                raw_text=doc.text,
                normalized_text=doc.text,
            )
            db.add(section)
            documents_ingested += 1
            sections_ingested += 1

    db.commit()
    return documents_ingested, sections_ingested
