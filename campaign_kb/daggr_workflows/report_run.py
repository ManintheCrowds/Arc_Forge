# PURPOSE: Report campaign_kb DAGGR workflow run completion to WatchTower for monitoring.
# DEPENDENCIES: requests (optional); env WATCHTOWER_METRICS_URL
# MODIFICATION NOTES: Call from Gradio/Daggr when a run completes; project=campaign_kb.

"""
Report a workflow run to WatchTower so it can record metrics for Prometheus/Grafana.

Set WATCHTOWER_METRICS_URL to the WatchTower Flask app base URL (e.g. http://localhost:5000).
If unset, report_workflow_run_to_watchtower is a no-op. Runs are reported with project=campaign_kb.
"""

import os
import time
import json
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
    Workflow name is taken from DAGGR_CURRENT_WORKFLOW_NAME (set by single_app).
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # #region agent log
        try:
            with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "id": "daggr_report_run_entry",
                    "timestamp": int(time.time() * 1000),
                    "location": "daggr_workflows/report_run.py:91",
                    "message": "with_run_reporting wrapper entry",
                    "data": {
                        "args_len": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                        "workflow_env": os.environ.get("DAGGR_CURRENT_WORKFLOW_NAME", "unknown"),
                    },
                    "runId": "pre-fix",
                    "hypothesisId": "H1"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        start = time.perf_counter()
        workflow_name = os.environ.get("DAGGR_CURRENT_WORKFLOW_NAME", "unknown")
        success = False
        try:
            # #region agent log
            try:
                with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "id": "daggr_report_run_before_fn",
                        "timestamp": int(time.time() * 1000),
                        "location": "daggr_workflows/report_run.py:111",
                        "message": "before calling workflow fn",
                        "data": {
                            "workflow_name": workflow_name,
                            "args_len": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                        },
                        "runId": "pre-fix",
                        "hypothesisId": "H1"
                    }) + "\n")
            except Exception:
                pass
            # #endregion
            out = fn(*args, **kwargs)
            success = True
            # #region agent log
            try:
                with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "id": "daggr_report_run_after_fn",
                        "timestamp": int(time.time() * 1000),
                        "location": "daggr_workflows/report_run.py:129",
                        "message": "workflow fn returned",
                        "data": {
                            "success": True
                        },
                        "runId": "pre-fix",
                        "hypothesisId": "H1"
                    }) + "\n")
            except Exception:
                pass
            # #endregion
            return out
        finally:
            duration = time.perf_counter() - start
            report_workflow_run_to_watchtower(
                workflow_name, duration, success, project="campaign_kb"
            )
            try:
                from app.monitoring.daggr_metrics import record_workflow_run as record_local
                record_local(workflow_name, duration, success, project="campaign_kb")
            except Exception:
                pass
    return wrapper  # type: ignore[return-value]
