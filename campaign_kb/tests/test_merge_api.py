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
    out = tmp_path / "merged.md"
    original_seed_paths = config.settings.seed_doc_paths
    try:
        config.settings.seed_doc_paths = [seed]
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
