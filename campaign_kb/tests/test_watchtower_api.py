# PURPOSE: Test WatchTower API endpoints (run-complete, errors).
# DEPENDENCIES: FastAPI TestClient, conftest client fixture
# MODIFICATION NOTES: T4 - campaign_kb serves as WatchTower receiver.

import pytest
from fastapi.testclient import TestClient


def test_daggr_run_complete_204(client: TestClient) -> None:
    """POST /api/daggr/run-complete returns 204 and records metrics."""
    payload = {
        "workflow": "rag",
        "duration_sec": 1.5,
        "success": True,
        "project": "rag_pipeline",
    }
    response = client.post("/api/daggr/run-complete", json=payload)
    assert response.status_code == 204


def test_errors_204(client: TestClient) -> None:
    """POST /api/errors returns 204."""
    payload = {
        "project": "rag_pipeline",
        "error_type": "ValueError",
        "message": "test error",
        "traceback": "Traceback...",
        "context": {"entry": "test"},
        "error_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "severity": "error",
    }
    response = client.post("/api/errors", json=payload)
    assert response.status_code == 204


def test_errors_204_backward_compat(client: TestClient) -> None:
    """POST /api/errors without error_id/severity still returns 204 (backward compat)."""
    payload = {
        "project": "rag_pipeline",
        "error_type": "ValueError",
        "message": "test error",
        "traceback": "Traceback...",
        "context": {"entry": "test"},
    }
    response = client.post("/api/errors", json=payload)
    assert response.status_code == 204
