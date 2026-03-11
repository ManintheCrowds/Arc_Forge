# PURPOSE: Playwright smoke test for campaign_kb search workflow Gradio UI
# DEPENDENCIES: pytest, pytest-playwright
# MODIFICATION NOTES: E2E Playwright plan Phase 1.3

"""
Playwright smoke test for campaign_kb search workflow. Page loads, search input visible.

Run: pytest tests/e2e/test_campaign_kb_search_workflow_loads.py -v
Requires: pip install pytest-playwright && playwright install
"""

import pytest


@pytest.fixture
def campaign_kb_base_url(campaign_kb_server):
    """Base URL for Playwright page.goto."""
    return campaign_kb_server


def test_campaign_kb_search_workflow_loads(page, campaign_kb_base_url):
    """Search workflow Gradio page loads and search input is visible."""
    page.goto(campaign_kb_base_url)
    page.wait_for_load_state("networkidle")
    # Search workflow has Query textbox (label="Query")
    expect = page.get_by_label("Query", exact=False)
    expect.first.wait_for(state="visible", timeout=10000)
