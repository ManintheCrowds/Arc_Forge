# PURPOSE: Pytest tests for ingest endpoints.
# DEPENDENCIES: pytest, fastapi.testclient, conftest
# MODIFICATION NOTES: Uses test DB; mocks for DoD and repo to avoid network.

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_ingest_pdfs_stub(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/pdfs returns 200 and IngestResponse shape (empty dir => 0, 0)."""
    response = client.post(
        "/ingest/pdfs",
        json={"pdf_root": str(tmp_path)},
    )
    assert response.status_code == 200
    data = response.json()
    assert "documents_ingested" in data
    assert "sections_ingested" in data
    assert data["documents_ingested"] >= 0
    assert data["sections_ingested"] >= 0


def test_ingest_seeds_stub(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/seeds returns 200 and IngestResponse shape."""
    seed = tmp_path / "seed.md"
    seed.write_text("# Test\n\nBody.", encoding="utf-8")
    response = client.post(
        "/ingest/seeds",
        json={"seed_paths": [str(seed)]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "documents_ingested" in data
    assert "sections_ingested" in data
    assert isinstance(data["documents_ingested"], int)
    assert isinstance(data["sections_ingested"], int)


def test_ingest_dod_stub(client: TestClient) -> None:
    """POST /ingest/dod returns 200 when crawl is mocked (no network)."""
    with patch("app.main.ingest_dod_site") as mock_ingest:
        mock_ingest.return_value = (0, 0)
        response = client.post(
            "/ingest/dod",
            json={"base_url": "https://example.com/", "max_pages": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents_ingested" in data
        assert "sections_ingested" in data


def test_ingest_docs_stub(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/docs returns 200 and IngestResponse shape."""
    (tmp_path / "doc.md").write_text("# Doc\n\nText.", encoding="utf-8")
    response = client.post(
        "/ingest/docs",
        json={"docs_root": str(tmp_path)},
    )
    assert response.status_code == 200
    data = response.json()
    assert "documents_ingested" in data
    assert "sections_ingested" in data
    assert isinstance(data["documents_ingested"], int)
    assert isinstance(data["sections_ingested"], int)


def test_ingest_repos_stub(client: TestClient) -> None:
    """POST /ingest/repos returns 200 when repo fetch is mocked (no network)."""
    with patch("app.main.ingest_github_repos") as mock_ingest:
        mock_ingest.return_value = (0, 0)
        response = client.post(
            "/ingest/repos",
            json={"repo_urls": ["https://github.com/fake/repo"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents_ingested" in data
        assert "sections_ingested" in data
