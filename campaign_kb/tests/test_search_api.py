# PURPOSE: Pytest tests for search endpoint.
# DEPENDENCIES: pytest, fastapi.testclient, conftest.client
# MODIFICATION NOTES: Uses test DB fixture; asserts response shape.

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_search_stub(client: TestClient) -> None:
    """GET /search returns 200 and response with query, total, results (empty when no data)."""
    response = client.get("/search", params={"query": "test", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "total" in data
    assert "results" in data
    assert data["query"] == "test"
    assert isinstance(data["results"], list)
