# PURPOSE: Report campaign_kb DAGGR workflow run completion to WatchTower for monitoring.
# DEPENDENCIES: requests (optional); env WATCHTOWER_METRICS_URL
# MODIFICATION NOTES: Call from Gradio/Daggr when a run completes; project=campaign_kb.

"""
Report a workflow run to WatchTower so it can record metrics for Prometheus/Grafana.

Set WATCHTOWER_METRICS_URL to the WatchTower Flask app base URL (e.g. http://localhost:5000).
If unset, report_workflow_run_to_watchtower is a no-op. Runs are reported with project=campaign_kb.
"""

import os
import sys
import time
import traceback
from pathlib import Path
from functools import wraps
from typing import Optional, Callable, TypeVar

try:
    import requests
except ImportError:
    requests = None

F = TypeVar("F", bound=Callable)


def _base_url() -> Optional[str]:
    url = os.environ.get("WATCHTOWER_METRICS_URL", "").strip()
    if not url:
        return None
    return url.rstrip("/")


def report_workflow_run_to_watchtower(
    workflow_name: str,
    duration_seconds: float,
    success: bool,
    base_url: Optional[str] = None,
    project: str = "campaign_kb",
) -> bool:
    """
    POST workflow run to WatchTower POST /api/daggr/run-complete.

    Returns True if the request succeeded (204), False otherwise.
    No-op if WATCHTOWER_METRICS_URL is unset or requests is not installed.
    """
    url = base_url or _base_url()
    if not url:
        return False
    if requests is None:
        return False
    endpoint = f"{url}/api/daggr/run-complete"
    payload = {
        "workflow": workflow_name,
        "duration_sec": duration_seconds,
        "success": success,
        "project": project,
    }
    try:
        r = requests.post(endpoint, json=payload, timeout=5)
        return r.status_code == 204
    except Exception:
        return False


class _RunReporter:
    """Context or helper to measure duration and report on exit."""

    def __init__(self, workflow_name: str, project: str = "campaign_kb"):
        self.workflow_name = workflow_name
        self.project = project
        self.start = time.perf_counter()

    def report(self, success: bool) -> bool:
        duration = time.perf_counter() - self.start
        return report_workflow_run_to_watchtower(
            self.workflow_name,
            duration,
            success,
            project=self.project,
        )


def with_run_reporting(fn: F) -> F:
    """
    Decorator for workflow step functions: measure duration, call fn, then report to
    WatchTower (and optionally local metrics) with project=campaign_kb.
    Workflow name is taken from DAGGR_CURRENT_WORKFLOW_NAME (set by single_app or run_workflow).
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        workflow_name = os.environ.get("DAGGR_CURRENT_WORKFLOW_NAME", "unknown")
        success = False
        try:
            out = fn(*args, **kwargs)
            success = True
            return out
        except Exception as e:
            success = False
            try:
                _scripts = Path(__file__).resolve().parent.parent.parent / "ObsidianVault" / "scripts"
                if str(_scripts) not in sys.path:
                    sys.path.insert(0, str(_scripts))
                from error_handling import log_structured_error
                project = os.environ.get("DAGGR_CURRENT_PROJECT", "campaign_kb")
                log_structured_error(
                    type(e).__name__,
                    str(e),
                    traceback.format_exc(),
                    context={"workflow": workflow_name, "project": project},
                    project=project,
                )
            except Exception:
                pass
            raise
        finally:
            duration = time.perf_counter() - start
            project = os.environ.get("DAGGR_CURRENT_PROJECT", "campaign_kb")
            report_workflow_run_to_watchtower(
                workflow_name, duration, success, project=project
            )
            try:
                from app.monitoring.daggr_metrics import record_workflow_run as record_local
                record_local(workflow_name, duration, success, project=project)
            except Exception:
                pass
    return wrapper  # type: ignore[return-value]
