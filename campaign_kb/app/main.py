# PURPOSE: FastAPI entrypoint for the campaign knowledge base service.
# DEPENDENCIES: FastAPI, SQLAlchemy, app modules, prometheus_client
# MODIFICATION NOTES: MVP API for ingest, search, merge; /metrics for Grafana.

from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.config import settings
import app.monitoring.daggr_metrics  # noqa: F401 -- register metrics for /metrics
from app.database import get_db
from app.schemas import (
    IngestPdfRequest,
    IngestSeedRequest,
    IngestDodRequest,
    IngestDocsRequest,
    IngestRepoRequest,
    IngestResponse,
    SearchResponse,
    SearchResponseItem,
    MergeRequest,
    MergeResponse,
)
from app.ingest.service import (
    ingest_pdfs,
    ingest_seed_docs,
    ingest_dod_site,
    ingest_reference_docs,
    ingest_github_repos,
)
from app.search.service import search_sections
from app.merge.service import create_merged_seed_doc
from app.models import Document, Source


app = FastAPI(
    title="Wrath & Glory Campaign KB",
    description="Ingest PDFs and web content, search, and merge campaign seeds.",
    version="0.1.0",
)


@app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
def metrics():
    """Prometheus metrics (DAGGR workflow runs and same convention as WatchTower)."""
    from prometheus_client import generate_latest
    return generate_latest()


@app.post(
    "/ingest/pdfs",
    response_model=IngestResponse,
    summary="Ingest local PDFs",
    description="Extract text from PDFs in a directory and store them as page sections.",
)
def ingest_pdfs_endpoint(
    payload: IngestPdfRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    # PURPOSE: Ingest PDF files from disk into the knowledge base.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.ingest.service.ingest_pdfs
    # MODIFICATION NOTES: MVP ingest endpoint for local PDFs.
    pdf_root = Path(payload.pdf_root) if payload.pdf_root else settings.pdf_root
    documents, sections = ingest_pdfs(db, pdf_root)
    return IngestResponse(documents_ingested=documents, sections_ingested=sections)


@app.post(
    "/ingest/seeds",
    response_model=IngestResponse,
    summary="Ingest seed docs",
    description="Ingest the campaign seed docs as authoritative notes.",
)
def ingest_seeds_endpoint(
    payload: IngestSeedRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    # PURPOSE: Ingest seed documents into the knowledge base.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.ingest.service.ingest_seed_docs
    # MODIFICATION NOTES: MVP ingest endpoint for seed docs.
    seed_paths = [Path(path) for path in payload.seed_paths] if payload.seed_paths else settings.seed_doc_paths
    documents, sections = ingest_seed_docs(db, seed_paths)
    return IngestResponse(documents_ingested=documents, sections_ingested=sections)


@app.post(
    "/ingest/dod",
    response_model=IngestResponse,
    summary="Ingest Doctors of Doom",
    description="Crawl doctors-of-doom.com and store pages as sections.",
)
def ingest_dod_endpoint(
    payload: IngestDodRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    # PURPOSE: Ingest Doctors of Doom site pages into the knowledge base.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.ingest.service.ingest_dod_site
    # MODIFICATION NOTES: MVP ingest endpoint for Doctors of Doom.
    base_url = payload.base_url or settings.dod_base_url
    max_pages = payload.max_pages or settings.dod_max_pages
    documents, sections = ingest_dod_site(
        db,
        base_url=base_url,
        max_pages=max_pages,
        timeout_seconds=settings.dod_request_timeout_seconds,
        user_agent=settings.dod_user_agent,
    )
    return IngestResponse(documents_ingested=documents, sections_ingested=sections)


@app.post(
    "/ingest/docs",
    response_model=IngestResponse,
    summary="Ingest reference docs",
    description="Ingest local markdown/text/html docs as reference material.",
)
def ingest_docs_endpoint(
    payload: IngestDocsRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    # PURPOSE: Ingest reference documents into the knowledge base.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.ingest.service.ingest_reference_docs
    # MODIFICATION NOTES: MVP ingest endpoint for local docs.
    docs_root = Path(payload.docs_root) if payload.docs_root else settings.dod_docs_root
    documents, sections = ingest_reference_docs(db, docs_root)
    return IngestResponse(documents_ingested=documents, sections_ingested=sections)


@app.post(
    "/ingest/repos",
    response_model=IngestResponse,
    summary="Ingest GitHub repos",
    description="Download GitHub repos and ingest markdown/text/html docs.",
)
def ingest_repos_endpoint(
    payload: IngestRepoRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    # PURPOSE: Ingest GitHub repositories into the knowledge base.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.ingest.service.ingest_github_repos
    # MODIFICATION NOTES: MVP ingest endpoint for GitHub repos.
    repo_urls = payload.repo_urls or settings.repo_urls
    documents, sections = ingest_github_repos(
        db,
        repo_urls=repo_urls,
        timeout_seconds=settings.dod_request_timeout_seconds,
    )
    return IngestResponse(documents_ingested=documents, sections_ingested=sections)


@app.get(
    "/search",
    response_model=SearchResponse,
    summary="Search sections",
    description="Full-text search across ingested sections with optional filters.",
)
def search_endpoint(
    query: str,
    limit: int = 20,
    source_name: str | None = None,
    doc_type: str | None = None,
    db: Session = Depends(get_db),
) -> SearchResponse:
    # PURPOSE: Search the knowledge base for relevant sections.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.search.service.search_sections
    # MODIFICATION NOTES: MVP search endpoint with ranking.
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    results = search_sections(db, query, limit=limit, source_name=source_name, doc_type=doc_type)
    items: list[SearchResponseItem] = []
    for section, score in results:
        document = db.query(Document).filter(Document.id == section.document_id).one()
        source = db.query(Source).filter(Source.id == document.source_id).one()
        snippet = section.normalized_text[:250]
        items.append(
            SearchResponseItem(
                section_id=section.id,
                document_title=document.title,
                source_name=source.name,
                snippet=snippet,
                score=float(score or 0.0),
                page_number=section.page_number,
                url=document.url,
                path=document.path,
            )
        )
    return SearchResponse(query=query, total=len(items), results=items)


@app.post(
    "/merge",
    response_model=MergeResponse,
    summary="Merge seed docs",
    description="Merge seed docs and append citations from ingested sources.",
)
def merge_endpoint(
    payload: MergeRequest,
    db: Session = Depends(get_db),
) -> MergeResponse:
    # PURPOSE: Create a merged campaign seed doc with citations.
    # DEPENDENCIES: FastAPI, SQLAlchemy, app.merge.service.create_merged_seed_doc
    # MODIFICATION NOTES: MVP merge endpoint.
    output_path = Path(payload.output_path) if payload.output_path else settings.output_dir / "campaign_seed_merged.md"
    merged_path, citations = create_merged_seed_doc(
        db,
        seed_paths=settings.seed_doc_paths,
        output_path=output_path,
        max_citations=payload.max_citations,
    )
    return MergeResponse(output_path=str(merged_path), citations_included=citations)
