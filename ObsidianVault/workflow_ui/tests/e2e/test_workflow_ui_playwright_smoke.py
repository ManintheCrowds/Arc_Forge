# PURPOSE: Playwright smoke test for workflow_ui index and /tools/kb-daggr redirect
# DEPENDENCIES: pytest, pytest-playwright, flask
# MODIFICATION NOTES: E2E Playwright + BrowserStack + Foam plan Phase 1.4

"""
Playwright smoke test for workflow_ui. Tests index load and /tools/kb-daggr redirect.

Run: pytest tests/e2e/test_workflow_ui_playwright_smoke.py -v
Requires: pip install pytest-playwright && playwright install
"""

import os
from urllib.parse import urlparse

import pytest


@pytest.fixture
def workflow_ui_base_url(workflow_ui_server):
    """Base URL for Playwright page.goto."""
    return workflow_ui_server


def test_index_loads(page, workflow_ui_base_url):
    """Index page loads and contains KB Workflows link."""
    page.goto(workflow_ui_base_url)
    page.wait_for_load_state("networkidle")
    expect = page.get_by_text("KB Workflows", exact=False)
    expect.first.wait_for(state="visible", timeout=10000)


def test_tools_kb_daggr_redirect(workflow_ui_base_url):
    """GET /tools/kb-daggr returns 302 and redirects to CAMPAIGN_KB_DAGGR_URL."""
    from http.client import HTTPConnection

    parsed = urlparse(workflow_ui_base_url)
    conn = HTTPConnection(parsed.hostname, parsed.port or 80)
    conn.request("GET", "/tools/kb-daggr")
    resp = conn.getresponse()
    conn.close()
    assert resp.status == 302, f"Expected 302, got {resp.status}"
    location = resp.getheader("Location")
    expected = os.environ.get("CAMPAIGN_KB_DAGGR_URL", "http://localhost:7860")
    assert location == expected, f"Expected Location {expected}, got {location}"
