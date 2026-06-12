# PURPOSE: Pytest tests for ingest endpoints.
# DEPENDENCIES: pytest, fastapi.testclient, conftest
# MODIFICATION NOTES: Uses test DB; mocks for DoD and repo to avoid network.

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app import config


def test_ingest_pdfs_stub(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/pdfs returns 200 and IngestResponse shape (empty dir => 0, 0)."""
    original_pdf_root = config.settings.pdf_root
    config.settings.pdf_root = tmp_path
    try:
        response = client.post(
            "/ingest/pdfs",
            json={"pdf_root": str(tmp_path)},
        )
    finally:
        config.settings.pdf_root = original_pdf_root
    assert response.status_code == 200
    data = response.json()
    assert "documents_ingested" in data
    assert "sections_ingested" in data
    assert data["documents_ingested"] >= 0
    assert data["sections_ingested"] >= 0


def test_ingest_pdfs_rejects_root_outside_configured_pdf_root(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/pdfs must not read arbitrary client-selected directories."""
    allowed_root = tmp_path / "allowed"
    outside_root = tmp_path / "outside"
    allowed_root.mkdir()
    outside_root.mkdir()
    original_pdf_root = config.settings.pdf_root
    config.settings.pdf_root = allowed_root
    try:
        response = client.post(
            "/ingest/pdfs",
            json={"pdf_root": str(outside_root)},
        )
    finally:
        config.settings.pdf_root = original_pdf_root
    assert response.status_code == 400
    assert "pdf_root" in response.json()["detail"]


def test_ingest_pdfs_accepts_configured_relative_root(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """POST /ingest/pdfs should not double-prefix a configured relative root."""
    monkeypatch.chdir(tmp_path)
    relative_root = Path("data/pdfs")
    expected_root = (tmp_path / relative_root).resolve()
    expected_root.mkdir(parents=True)
    original_pdf_root = config.settings.pdf_root
    config.settings.pdf_root = relative_root
    try:
        with patch("app.main.ingest_pdfs") as mock_ingest:
            mock_ingest.return_value = (0, 0)
            response = client.post(
                "/ingest/pdfs",
                json={"pdf_root": str(relative_root)},
            )
    finally:
        config.settings.pdf_root = original_pdf_root
    assert response.status_code == 200
    assert mock_ingest.call_args.args[1] == expected_root


def test_ingest_seeds_stub(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/seeds returns 200 and IngestResponse shape."""
    seed = tmp_path / "seed.md"
    seed.write_text("# Test\n\nBody.", encoding="utf-8")
    original_seed_paths = config.settings.seed_doc_paths
    config.settings.seed_doc_paths = [tmp_path]
    try:
        response = client.post(
            "/ingest/seeds",
            json={"seed_paths": [str(seed)]},
        )
    finally:
        config.settings.seed_doc_paths = original_seed_paths
    assert response.status_code == 200
    data = response.json()
    assert "documents_ingested" in data
    assert "sections_ingested" in data
    assert isinstance(data["documents_ingested"], int)
    assert isinstance(data["sections_ingested"], int)


def test_ingest_seeds_rejects_paths_outside_configured_seed_roots(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/seeds must not read arbitrary client-selected files."""
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    secret = tmp_path / "secret.md"
    secret.write_text("do not ingest", encoding="utf-8")
    original_seed_paths = config.settings.seed_doc_paths
    config.settings.seed_doc_paths = [allowed_root]
    try:
        response = client.post(
            "/ingest/seeds",
            json={"seed_paths": [str(secret)]},
        )
    finally:
        config.settings.seed_doc_paths = original_seed_paths
    assert response.status_code == 400
    assert "seed_paths" in response.json()["detail"]


def test_ingest_seeds_relative_file_prefers_configured_file_entry(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/seeds should not shadow configured file entries with earlier directories."""
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    seed = tmp_path / "configured-seed.md"
    seed.write_text("# Seed\n\nBody.", encoding="utf-8")
    original_seed_paths = config.settings.seed_doc_paths
    config.settings.seed_doc_paths = [allowed_root, seed]
    try:
        response = client.post(
            "/ingest/seeds",
            json={"seed_paths": [seed.name]},
        )
    finally:
        config.settings.seed_doc_paths = original_seed_paths
    assert response.status_code == 200
    assert response.json()["documents_ingested"] == 1
    assert response.json()["sections_ingested"] == 1


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
    original_docs_root = config.settings.dod_docs_root
    config.settings.dod_docs_root = tmp_path
    try:
        response = client.post(
            "/ingest/docs",
            json={"docs_root": str(tmp_path)},
        )
    finally:
        config.settings.dod_docs_root = original_docs_root
    assert response.status_code == 200
    data = response.json()
    assert "documents_ingested" in data
    assert "sections_ingested" in data
    assert isinstance(data["documents_ingested"], int)
    assert isinstance(data["sections_ingested"], int)


def test_ingest_docs_rejects_root_outside_configured_docs_root(client: TestClient, tmp_path: Path) -> None:
    """POST /ingest/docs must not read arbitrary client-selected directories."""
    allowed_root = tmp_path / "allowed"
    outside_root = tmp_path / "outside"
    allowed_root.mkdir()
    outside_root.mkdir()
    (outside_root / "secret.md").write_text("do not ingest", encoding="utf-8")
    original_docs_root = config.settings.dod_docs_root
    config.settings.dod_docs_root = allowed_root
    try:
        response = client.post(
            "/ingest/docs",
            json={"docs_root": str(outside_root)},
        )
    finally:
        config.settings.dod_docs_root = original_docs_root
    assert response.status_code == 400
    assert "docs_root" in response.json()["detail"]


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
