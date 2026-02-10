# PURPOSE: Pytest fixtures for campaign_kb API tests (test DB override).
# DEPENDENCIES: pytest, FastAPI, SQLAlchemy, app.database, app.main
# MODIFICATION NOTES: In-memory SQLite and get_db override for isolated tests.

import tempfile
from pathlib import Path
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import get_db, Base
from app.main import app


@pytest.fixture(scope="function")
def test_db(tmp_path) -> Generator[Session, None, None]:
    """Create a temp-file SQLite DB with schema and yield a session (shared across connections)."""
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(tmp_path):
    """TestClient with get_db overridden to use a temp-file SQLite DB (shared connections)."""
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    c = TestClient(app)
    try:
        yield c
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    """Empty temp dir (no PDFs); ingest will return 0, 0."""
    return tmp_path


@pytest.fixture
def temp_seed_file(tmp_path: Path) -> Path:
    """A minimal seed .md file for seed ingest."""
    p = tmp_path / "seed.md"
    p.write_text("# Test seed\n\nSome text.", encoding="utf-8")
    return p


@pytest.fixture
def temp_docs_dir(tmp_path: Path) -> Path:
    """A minimal .md file for docs ingest."""
    (tmp_path / "doc.md").write_text("# Doc\n\nContent.", encoding="utf-8")
    return tmp_path
