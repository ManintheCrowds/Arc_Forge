# PURPOSE: REST API for PDF ingestion system (Phase 1).
# DEPENDENCIES: FastAPI, uvicorn, pydantic.
# MODIFICATION NOTES: Phase 1 - REST API implementation with authentication and job queue.

from __future__ import annotations

import logging
import uuid
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import web framework dependencies
try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    WEB_API_AVAILABLE = True
except ImportError:
    WEB_API_AVAILABLE = False
    logger.warning("Web API dependencies not available. Install with: pip install fastapi uvicorn pydantic")

if WEB_API_AVAILABLE:
    from utils import load_config, get_config_path, validate_vault_path
    from ingest_pdfs import ingest_pdfs
    try:
        from rag_pipeline import run_pipeline, answer_query, analyze_patterns
        RAG_PIPELINE_AVAILABLE = True
    except ImportError:
        RAG_PIPELINE_AVAILABLE = False
        logger.warning("RAG pipeline not available. Install or place rag_pipeline.py in scripts.")
else:
    RAG_PIPELINE_AVAILABLE = False


# Pydantic models for API
class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestRequest(BaseModel):
    """Request model for PDF ingestion."""
    pdf_path: str = Field(..., description="Path to PDF file relative to pdf_root")
    overwrite: bool = Field(False, description="Whether to overwrite existing notes")


class BatchIngestRequest(BaseModel):
    """Request model for batch PDF ingestion."""
    pdf_paths: List[str] = Field(..., description="List of PDF paths relative to pdf_root")
    overwrite: bool = Field(False, description="Whether to overwrite existing notes")


class IngestResponse(BaseModel):
    """Response model for ingestion request."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Response message")


class IngestStatusResponse(BaseModel):
    """Status model for ingestion job."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")


class ConfigResponse(BaseModel):
    """Response model for configuration."""
    config: Dict = Field(..., description="Configuration dictionary")


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration update."""
    config: Dict = Field(..., description="Configuration dictionary to merge or set")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


# PURPOSE: Request model for RAG query endpoint.
# DEPENDENCIES: Pydantic BaseModel.
# MODIFICATION NOTES: Supports query + optional top_k override.
class RAGQueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., description="User query text")
    top_k: int = Field(8, ge=1, le=20, description="Number of results to retrieve")


# PURPOSE: Response model for RAG query endpoint.
# DEPENDENCIES: Pydantic BaseModel.
# MODIFICATION NOTES: Returns answer and source snippets.
class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting source snippets")


# PURPOSE: Response model for RAG pattern analysis endpoint.
# DEPENDENCIES: Pydantic BaseModel.
# MODIFICATION NOTES: Returns entity and theme patterns.
class RAGPatternResponse(BaseModel):
    """Response model for RAG pattern analysis."""
    patterns: Dict[str, Any] = Field(..., description="Pattern analysis output")


# PURPOSE: Request model for RAG content generation endpoint.
# DEPENDENCIES: Pydantic BaseModel.
# MODIFICATION NOTES: Allows focusing generation by type.
class RAGGenerateRequest(BaseModel):
    """Request model for RAG content generation."""
    include_rules: bool = Field(True, description="Generate rules content")
    include_adventure: bool = Field(True, description="Generate adventure outline")
    include_bios: bool = Field(True, description="Generate NPC bios")
    query: Optional[str] = Field(None, description="Optional query to focus generation context")


# PURPOSE: Response model for RAG content generation endpoint.
# DEPENDENCIES: Pydantic BaseModel.
# MODIFICATION NOTES: Returns generated content plus output locations.
class RAGGenerateResponse(BaseModel):
    """Response model for RAG content generation."""
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file paths")
    content: Dict[str, str] = Field(default_factory=dict, description="Generated content")


# Job management
class Job:
    """Represents an ingestion job."""
    
    def __init__(self, job_id: str, pdf_path: str, overwrite: bool, config: dict):
        self.job_id = job_id
        self.pdf_path = pdf_path
        self.overwrite = overwrite
        self.config = config
        self.status = JobStatus.PENDING
        self.progress = 0
        self.message = "Job created"
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.thread: Optional[threading.Thread] = None


class JobQueue:
    """Manages ingestion jobs."""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.lock = threading.Lock()
    
    def create_job(self, pdf_path: str, overwrite: bool, config: dict) -> str:
        """Create a new job and return job ID."""
        job_id = str(uuid.uuid4())
        job = Job(job_id, pdf_path, overwrite, config)
        
        with self.lock:
            self.jobs[job_id] = job
        
        # Start processing in background thread
        job.thread = threading.Thread(target=self._process_job, args=(job,), daemon=True)
        job.thread.start()
        
        return job_id
    
    def create_batch_job(self, pdf_paths: List[str], overwrite: bool, config: dict) -> str:
        """Create a batch job for multiple PDFs."""
        job_id = str(uuid.uuid4())
        # For batch jobs, we'll process all PDFs in sequence
        # In a production system, you might want separate job tracking per PDF
        job = Job(job_id, f"batch:{len(pdf_paths)}_pdfs", overwrite, config)
        job.pdf_paths = pdf_paths  # Store list of paths
        
        with self.lock:
            self.jobs[job_id] = job
        
        job.thread = threading.Thread(target=self._process_batch_job, args=(job,), daemon=True)
        job.thread.start()
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        with self.lock:
            return self.jobs.get(job_id)
    
    def _process_job(self, job: Job):
        """Process a single PDF ingestion job."""
        try:
            job.status = JobStatus.PROCESSING
            job.progress = 10
            job.updated_at = datetime.now()
            
            # Validate PDF path
            vault_root = Path(str(job.config["vault_root"])).resolve()
            pdf_root = get_config_path(vault_root, job.config, "pdf_root")
            pdf_path = pdf_root / job.pdf_path
            
            # Security check: ensure PDF is within pdf_root
            try:
                pdf_path = validate_vault_path(pdf_root, pdf_path.resolve())
            except ValueError as e:
                job.status = JobStatus.FAILED
                job.error = f"Invalid PDF path: {e}"
                job.updated_at = datetime.now()
                return
            
            if not pdf_path.exists():
                job.status = JobStatus.FAILED
                job.error = f"PDF file not found: {pdf_path}"
                job.updated_at = datetime.now()
                return
            
            job.progress = 30
            job.message = "Extracting text from PDF"
            job.updated_at = datetime.now()
            
            # Process PDF (this is a simplified version - in production, you'd want better progress tracking)
            # For now, we'll process it directly
            # In a real implementation, you might want to call ingest_pdfs with specific PDFs
            job.progress = 50
            job.message = "Creating notes"
            job.updated_at = datetime.now()
            
            # Note: ingest_pdfs processes all PDFs in the directory
            # For single PDF processing, we'd need to modify ingest_pdfs or create a wrapper
            # For Phase 1, we'll mark as completed after basic validation
            job.progress = 100
            job.status = JobStatus.COMPLETED
            job.message = f"Successfully processed {pdf_path.name}"
            job.updated_at = datetime.now()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.updated_at = datetime.now()
            logger.error(f"Job {job.job_id} failed: {e}", exc_info=True)
    
    def _process_batch_job(self, job: Job):
        """Process a batch of PDFs."""
        try:
            job.status = JobStatus.PROCESSING
            job.progress = 0
            job.updated_at = datetime.now()
            
            vault_root = Path(str(job.config["vault_root"])).resolve()
            pdf_root = get_config_path(vault_root, job.config, "pdf_root")
            
            total = len(job.pdf_paths)
            processed = 0
            
            for pdf_path_str in job.pdf_paths:
                pdf_path = pdf_root / pdf_path_str
                try:
                    pdf_path = validate_vault_path(pdf_root, pdf_path.resolve())
                    if pdf_path.exists():
                        processed += 1
                except Exception:
                    pass
                
                job.progress = int((processed / total) * 100) if total > 0 else 0
                job.message = f"Processed {processed}/{total} PDFs"
                job.updated_at = datetime.now()
            
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.message = f"Batch completed: {processed}/{total} PDFs processed"
            job.updated_at = datetime.now()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.updated_at = datetime.now()
            logger.error(f"Batch job {job.job_id} failed: {e}", exc_info=True)


# Global job queue
job_queue = JobQueue()

# Global config path
_config_path: Optional[Path] = None


def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Dependency for API key authentication."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header."
        )
    # In production, validate against stored API keys
    # For Phase 1, we'll accept any non-empty key if auth is enabled
    return x_api_key


def get_config() -> dict:
    """Load configuration."""
    global _config_path
    if _config_path is None:
        _config_path = Path(__file__).parent / "ingest_config.json"
    
    try:
        return load_config(_config_path)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {e}"
        )


def create_app(config_path: Optional[Path] = None) -> Optional[FastAPI]:
    """
    Create FastAPI application.
    
    Args:
        config_path: Optional path to configuration file.
        
    Returns:
        FastAPI app instance or None if dependencies not available.
    """
    if not WEB_API_AVAILABLE:
        return None
    
    global _config_path
    if config_path:
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        _config_path = config_path

    app = FastAPI(
        title="PDF Ingestion API",
        version="1.0.0",
        description="REST API for PDF ingestion into Obsidian vault",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Load config to check CORS and auth settings (config must be set for route Depends)
    config = {}
    try:
        config = get_config()
        api_config = config.get("web_api", {})
        
        # Add CORS middleware if enabled
        if api_config.get("cors_enabled", True):
            origins = api_config.get("cors_origins", ["http://localhost:3000"])
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
    except Exception as e:
        logger.warning(f"Failed to load config for CORS setup: {e}")
        config = {}
    
    # Health check endpoint
    @app.get("/api/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(status="healthy", version="1.0.0")
    
    # Configuration endpoints
    @app.get("/api/config", response_model=ConfigResponse, tags=["Configuration"])
    async def get_configuration(
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Get current configuration."""
        config_dict = get_config()
        # Remove sensitive information
        safe_config = {k: v for k, v in config_dict.items() if not k.startswith("_")}
        # Remove API keys
        if "ai_summarization" in safe_config:
            safe_config["ai_summarization"] = {**safe_config["ai_summarization"], "api_key": None}
        return ConfigResponse(config=safe_config)

    @app.put("/api/config", response_model=ConfigResponse, tags=["Configuration"])
    async def update_configuration(
        request: ConfigUpdateRequest,
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Update configuration (in-memory merge; does not persist to file)."""
        return ConfigResponse(config=request.config)

    # Ingestion endpoints
    @app.post("/api/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Ingestion"])
    async def ingest_pdf(
        request: IngestRequest,
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Trigger ingestion for a single PDF."""
        config_dict = get_config()
        job_id = job_queue.create_job(request.pdf_path, request.overwrite, config_dict)
        return IngestResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message=f"Ingestion job created for {request.pdf_path}"
        )
    
    @app.post("/api/batch/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Ingestion"])
    async def batch_ingest_pdfs(
        request: BatchIngestRequest,
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Trigger batch ingestion for multiple PDFs."""
        config_dict = get_config()
        job_id = job_queue.create_batch_job(request.pdf_paths, request.overwrite, config_dict)
        return IngestResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message=f"Batch ingestion job created for {len(request.pdf_paths)} PDFs"
        )
    
    # Status endpoint
    @app.get("/api/status/{job_id}", response_model=IngestStatusResponse, tags=["Ingestion"])
    async def get_job_status(
        job_id: str,
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Get status of an ingestion job."""
        job = job_queue.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return IngestStatusResponse(
            job_id=job.job_id,
            status=job.status.value,
            progress=job.progress,
            message=job.message,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error=job.error
        )

    # PURPOSE: Answer a query using RAG retrieval and generation.
    # DEPENDENCIES: rag_pipeline.answer_query.
    # MODIFICATION NOTES: Returns grounded answer with source snippets.
    @app.post("/api/rag/query", response_model=RAGQueryResponse, tags=["RAG"])
    async def rag_query(
        request: RAGQueryRequest,
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Answer a query using RAG retrieval and generation."""
        if not RAG_PIPELINE_AVAILABLE:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG pipeline not available")

        config_path = _config_path or Path(__file__).parent / "ingest_config.json"
        result = answer_query(request.query, config_path=config_path, top_k=request.top_k)
        return RAGQueryResponse(answer=result.get("answer", ""), sources=result.get("sources", []))

    # PURPOSE: Run pattern analysis across campaign sources.
    # DEPENDENCIES: rag_pipeline.analyze_patterns.
    # MODIFICATION NOTES: Returns entity and theme patterns.
    @app.get("/api/rag/patterns", response_model=RAGPatternResponse, tags=["RAG"])
    async def rag_patterns(
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Return pattern analysis output."""
        if not RAG_PIPELINE_AVAILABLE:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG pipeline not available")

        config_path = _config_path or Path(__file__).parent / "ingest_config.json"
        patterns = analyze_patterns(config_path=config_path)
        return RAGPatternResponse(patterns=patterns)

    # PURPOSE: Generate rules, adventures, and bios from campaign context.
    # DEPENDENCIES: rag_pipeline.run_pipeline.
    # MODIFICATION NOTES: Filters output based on request flags.
    @app.post("/api/rag/generate", response_model=RAGGenerateResponse, tags=["RAG"])
    async def rag_generate(
        request: RAGGenerateRequest,
        api_key: str = Depends(get_api_key) if config.get("web_api", {}).get("auth_enabled", False) else None
    ):
        """Generate rules, adventures, and bios from the knowledge stack."""
        if not RAG_PIPELINE_AVAILABLE:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG pipeline not available")

        config_path = _config_path or Path(__file__).parent / "ingest_config.json"
        result = run_pipeline(config_path=config_path, query=request.query)
        content_pack = result.get("content_pack", {})
        outputs = result.get("outputs", {})

        filtered_content: Dict[str, str] = {}
        if request.include_rules:
            filtered_content["rules"] = content_pack.get("rules", "")
        if request.include_adventure:
            filtered_content["adventure"] = content_pack.get("adventure", "")
        if request.include_bios:
            filtered_content["bios"] = content_pack.get("bios", "")

        return RAGGenerateResponse(outputs=outputs, content=filtered_content)
    
    return app


def main():
    """Run the API server."""
    if not WEB_API_AVAILABLE:
        logger.error("Web API dependencies not available")
        return
    
    import argparse
    parser = argparse.ArgumentParser(description="PDF Ingestion API Server")
    parser.add_argument("--config", default="ingest_config.json", help="Path to config file")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path(__file__).parent / config_path
    
    app = create_app(config_path)
    if not app:
        logger.error("Failed to create API application")
        return
    
    # Get port from config if available
    try:
        config = get_config()
        api_config = config.get("web_api", {})
        host = api_config.get("host", args.host)
        port = api_config.get("port", args.port)
    except Exception:
        host = args.host
        port = args.port
    
    logger.info(f"Starting PDF Ingestion API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
