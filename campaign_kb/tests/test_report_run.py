# PURPOSE: Test report_workflow_run_to_watchtower (no server); reporter returns True/False as expected.
# DEPENDENCIES: daggr_workflows.report_run; stdlib unittest.mock
# MODIFICATION NOTES: Complements WatchTower_main test_daggr_run_complete.py (endpoint tests).

import os
from unittest.mock import patch

import pytest

from daggr_workflows.report_run import report_workflow_run_to_watchtower


def test_report_run_no_url_returns_false():
    """With WATCHTOWER_METRICS_URL unset and no base_url, reporter is no-op and returns False."""
    with patch.dict(os.environ, {"WATCHTOWER_METRICS_URL": ""}, clear=False):
        assert report_workflow_run_to_watchtower("search", 1.0, True) is False


def test_report_run_post_204_returns_true():
    """Mocked POST returning 204 yields True; POST called with expected URL and JSON."""
    with patch("daggr_workflows.report_run.requests") as m_requests:
        m_requests.post.return_value.status_code = 204
        result = report_workflow_run_to_watchtower(
            "ingest", 2.0, False, base_url="http://test"
        )
    assert result is True
    m_requests.post.assert_called_once()
    call_args, call_kwargs = m_requests.post.call_args
    assert call_args[0] == "http://test/api/daggr/run-complete"
    assert call_kwargs["json"] == {
        "workflow": "ingest",
        "duration_sec": 2.0,
        "success": False,
        "project": "campaign_kb",
    }


def test_report_run_post_500_returns_false():
    """Mocked POST returning 500 yields False."""
    with patch("daggr_workflows.report_run.requests") as m_requests:
        m_requests.post.return_value.status_code = 500
        result = report_workflow_run_to_watchtower(
            "search", 1.5, True, base_url="http://test"
        )
    assert result is False
