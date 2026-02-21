# PURPOSE: Pydantic schemas for API requests and responses.
# DEPENDENCIES: Pydantic
# MODIFICATION NOTES: Initial schemas for ingest/search/merge endpoints.

from pydantic import BaseModel, Field


class IngestPdfRequest(BaseModel):
    # PURPOSE: Validate PDF ingestion request inputs.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP request schema.

    pdf_root: str | None = Field(default=None, description="Directory containing PDF files.")


class IngestSeedRequest(BaseModel):
    # PURPOSE: Validate seed document ingestion request inputs.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP request schema.

    seed_paths: list[str] | None = Field(default=None, description="List of seed doc file paths.")


class IngestDodRequest(BaseModel):
    # PURPOSE: Validate Doctors of Doom ingestion request inputs.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP request schema.

    base_url: str | None = Field(default=None, description="Base URL for Doctors of Doom crawl.")
    max_pages: int | None = Field(default=None, description="Maximum number of pages to crawl.")


class IngestDocsRequest(BaseModel):
    # PURPOSE: Validate local docs ingestion request inputs.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP request schema for reference docs.

    docs_root: str | None = Field(default=None, description="Directory containing reference docs.")


class IngestCampaignDocsRequest(BaseModel):
    # PURPOSE: Validate campaign docs ingestion (RAG-aligned sources).
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: Aligns campaign_kb with RAG pipeline campaign_docs.

    docs_root: str | None = Field(default=None, description="Campaign docs directory (default: campaign_docs_root).")


class IngestRepoRequest(BaseModel):
    # PURPOSE: Validate GitHub repo ingestion request inputs.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP request schema for repo ingestion.

    repo_urls: list[str] | None = Field(default=None, description="GitHub repo URLs to ingest.")


class IngestResponse(BaseModel):
    # PURPOSE: Provide a standard ingest result payload.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP response schema.

    documents_ingested: int
    sections_ingested: int


class SearchResponseItem(BaseModel):
    # PURPOSE: Serialize search results for a section.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP response schema.

    section_id: int
    document_title: str
    source_name: str
    snippet: str
    score: float
    page_number: int | None
    url: str | None
    path: str | None


class SearchResponse(BaseModel):
    # PURPOSE: Provide a standard search result payload.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP response schema.

    query: str
    total: int
    results: list[SearchResponseItem]


class MergeRequest(BaseModel):
    # PURPOSE: Validate merged seed doc output request inputs.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP request schema.

    output_path: str | None = Field(default=None, description="Output path for merged seed doc.")
    max_citations: int = Field(default=25, description="Max citations to include from search.")


class MergeResponse(BaseModel):
    # PURPOSE: Provide a standard merge result payload.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: MVP response schema.

    output_path: str
    citations_included: int


class DaggrRunCompleteRequest(BaseModel):
    # PURPOSE: WatchTower run-complete payload from report_run.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: T4 - campaign_kb serves as WatchTower receiver.

    workflow: str
    duration_sec: float
    success: bool
    project: str = "campaign_kb"


class ErrorReportRequest(BaseModel):
    # PURPOSE: WatchTower /api/errors payload from log_structured_error.
    # DEPENDENCIES: Pydantic
    # MODIFICATION NOTES: T4 - structured error reporting; error_id, severity optional.

    project: str = "unknown"
    error_type: str
    message: str
    traceback: str = ""
    context: dict | None = None
    error_id: str | None = None
    severity: str | None = None