# PURPOSE: Database session and engine setup for the service.
# DEPENDENCIES: SQLAlchemy, app.config
# MODIFICATION NOTES: Initial DB wiring for MVP ingest/search.

from collections.abc import Generator
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings


Base = declarative_base()


def get_engine():
    # PURPOSE: Create a SQLAlchemy engine using configured database URL.
    # DEPENDENCIES: SQLAlchemy, app.config.settings
    # MODIFICATION NOTES: Sync engine for MVP with SQLite support.
    url = settings.database_url
    connect_args = {}
    if url.startswith("sqlite:///"):
        db_path = Path(url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        connect_args = {"check_same_thread": False}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


ENGINE = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


def get_db() -> Generator[Session, None, None]:
    # PURPOSE: Provide a scoped database session for request handling.
    # DEPENDENCIES: SQLAlchemy
    # MODIFICATION NOTES: Sync session dependency for FastAPI.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
