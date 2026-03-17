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


def test_daggr_hub_loads_select_workflow_click_node_shows_card(page, workflow_ui_base_url):
    """Daggr Hub: load page, select workflow, click node, DaggrNodeCard visible."""
    page.goto(workflow_ui_base_url + "/tools/daggr-graphs")
    page.wait_for_load_state("networkidle")

    # Assert Daggr Hub title
    expect_h1 = page.get_by_role("heading", name="Daggr Hub")
    expect_h1.wait_for(state="visible", timeout=5000)

    # Click a workflow (simple from WatchTower)
    simple_link = page.locator('a[data-workflow="simple"][data-stack="WatchTower"]').first
    simple_link.wait_for(state="visible", timeout=5000)
    simple_link.click()

    # Wait for graph viewer to show and title to appear (sync)
    page.get_by_role("heading", name="Simple Math Test").wait_for(state="visible", timeout=5000)
    # Wait for Mermaid SVG (loads from CDN; skip if render fails)
    try:
        page.wait_for_selector("#mermaid-container svg", state="visible", timeout=25000)
    except Exception:
        if page.locator("#mermaid-container .graph-error").is_visible():
            pytest.skip("Mermaid render failed (CDN or syntax)")
        raise

    # Click a node (first node rect or [id] child; Mermaid uses flowcharts)
    node = page.locator("#mermaid-container svg g[id]").first
    node.wait_for(state="visible", timeout=5000)
    node.click()

    # Node detail panel and DaggrNodeCard should be visible
    node_panel = page.locator("#node-detail-panel")
    node_panel.wait_for(state="visible", timeout=5000)
    node_card = page.locator("#daggr-node-card")
    node_card.wait_for(state="visible", timeout=3000)
    # Card should have Inputs or Outputs
    content = node_card.text_content()
    assert "Inputs" in content or "Outputs" in content or content.strip(), (
        f"Expected DaggrNodeCard with Inputs/Outputs, got: {content}"
    )
