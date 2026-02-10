# PURPOSE: Prometheus metrics for DAGGR workflow runs (Grafana monitoring pipeline).
# DEPENDENCIES: prometheus_client
# MODIFICATION NOTES: Same metric names/labels as WatchTower; project=campaign_kb.

"""
DAGGR workflow metrics for the Grafana monitoring pipeline.

Metrics use the shared label convention: project, workflow, status (success|failure)
so Grafana dashboards can filter by project and workflow. Same names as WatchTower
for unified scraping. Uses the default Prometheus REGISTRY.
"""

from prometheus_client import Counter, Histogram

CAMPAIGN_KB_FIRST_CLASS_WORKFLOWS = frozenset({"search", "ingest", "merge"})

# Metric definitions (default REGISTRY; same names as WatchTower)
daggr_workflow_runs_total = Counter(
    "daggr_workflow_runs_total",
    "Total DAGGR workflow runs by project, workflow, and status",
    ["project", "workflow", "status"],
)

daggr_workflow_duration_seconds = Histogram(
    "daggr_workflow_duration_seconds",
    "DAGGR workflow run duration in seconds",
    ["project", "workflow"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def record_workflow_run(
    workflow_name: str,
    duration_seconds: float,
    success: bool,
    project: str = "campaign_kb",
) -> None:
    """
    Record a single DAGGR workflow run for Prometheus/Grafana.

    Call from in-process when a workflow step completes (e.g. from report_run decorator).

    Args:
        workflow_name: Workflow identifier (e.g. search, ingest, merge).
        duration_seconds: Run duration in seconds.
        success: True if run completed successfully.
        project: Label for project (default campaign_kb).
    """
    status = "success" if success else "failure"
    daggr_workflow_runs_total.labels(
        project=project,
        workflow=workflow_name,
        status=status,
    ).inc()
    daggr_workflow_duration_seconds.labels(
        project=project,
        workflow=workflow_name,
    ).observe(duration_seconds)
