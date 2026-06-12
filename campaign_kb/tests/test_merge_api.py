# PURPOSE: Pytest tests for merge endpoint.
# DEPENDENCIES: pytest, fastapi.testclient, conftest.client
# MODIFICATION NOTES: Uses test DB fixture; patches settings.seed_doc_paths for test seed.

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app import config


def test_merge_stub(client: TestClient, tmp_path: Path) -> None:
    """POST /merge returns 200 and response with output_path and citations_included."""
    seed = tmp_path / "seed.md"
    seed.write_text("# Seed\n\nContent.", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    out = output_dir / "merged.md"
    original_seed_paths = config.settings.seed_doc_paths
    original_output_dir = config.settings.output_dir
    try:
        config.settings.seed_doc_paths = [seed]
        config.settings.output_dir = output_dir
        response = client.post(
            "/merge",
            json={"output_path": str(out), "max_citations": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert "output_path" in data
        assert "citations_included" in data
        assert isinstance(data["citations_included"], int)
    finally:
        config.settings.seed_doc_paths = original_seed_paths
        config.settings.output_dir = original_output_dir


def test_merge_rejects_output_path_outside_configured_output_dir(client: TestClient, tmp_path: Path) -> None:
    """POST /merge must not overwrite arbitrary client-selected files."""
    seed = tmp_path / "seed.md"
    seed.write_text("# Seed\n\nContent.", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    outside_output = tmp_path / "outside.md"
    original_seed_paths = config.settings.seed_doc_paths
    original_output_dir = config.settings.output_dir
    try:
        config.settings.seed_doc_paths = [seed]
        config.settings.output_dir = output_dir
        response = client.post(
            "/merge",
            json={"output_path": str(outside_output), "max_citations": 5},
        )
    finally:
        config.settings.seed_doc_paths = original_seed_paths
        config.settings.output_dir = original_output_dir
    assert response.status_code == 400
    assert "output_path" in response.json()["detail"]
    assert not outside_output.exists()
