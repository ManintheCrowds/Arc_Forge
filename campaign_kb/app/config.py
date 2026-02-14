# PURPOSE: Centralized configuration for the campaign knowledge base service.
# DEPENDENCIES: pydantic-settings, pathlib
# MODIFICATION NOTES: Initial settings for MVP ingest/search service.

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _campaign_docs_root_default() -> Path:
    """Default: campaign_kb/campaign (aligns with RAG pipeline campaign_docs)."""
    return Path(__file__).resolve().parent.parent / "campaign"


class Settings(BaseSettings):
    # PURPOSE: Provide validated configuration with environment overrides.
    # DEPENDENCIES: pydantic-settings
    # MODIFICATION NOTES: MVP configuration parameters for ingest/search.

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///D:/arc_forge/campaign_kb/data/kb.sqlite3"
    pdf_root: Path = Path("D:/arc_forge/pdf")
    seed_doc_paths: list[Path] = [
        Path("D:/arc_forge/campaign_seed_doc"),
        Path("D:/arc_forge/campaign_seed_doc.md"),
    ]
    output_dir: Path = Path("D:/arc_forge/output")
    dod_docs_root: Path = Path("D:/arc_forge/pdf/dod_docs")
    campaign_docs_root: Path = Field(default_factory=_campaign_docs_root_default)
    repo_urls: list[str] = [
        "https://github.com/tecera/dod-importer",
        "https://github.com/LordFckHelmchen/WrathAndGloryXPOptimizer",
    ]

    dod_base_url: str = "https://www.doctors-of-doom.com/"
    dod_max_pages: int = 100
    dod_request_timeout_seconds: float = 15.0
    dod_user_agent: str = "WrathAndGloryKB/1.0 (+https://www.doctors-of-doom.com/)"


settings = Settings()
