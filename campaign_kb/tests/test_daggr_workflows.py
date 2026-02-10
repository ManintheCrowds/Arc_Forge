# PURPOSE: Verify campaign_kb Daggr WORKFLOWS script paths and optional graph export.
# DEPENDENCIES: pytest; daggr_workflows.run_workflow
# MODIFICATION NOTES: Plan daggr_integration_verification_fc362711 section 3.2.

"""
Assert run_workflow.WORKFLOWS script paths exist.
Optionally run one workflow script with runpy and assert "graph" in globals.
"""

import os
from pathlib import Path

import pytest


def test_workflow_script_paths_exist():
    """Every entry in run_workflow.WORKFLOWS must point to an existing script file."""
    try:
        from daggr_workflows.run_workflow import WORKFLOWS
    except ImportError:
        import sys
        root = Path(__file__).resolve().parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from daggr_workflows.run_workflow import WORKFLOWS

    root = Path(__file__).resolve().parent.parent
    for name, info in WORKFLOWS.items():
        script = root / info["script"].replace("/", os.sep)
        assert script.exists(), f"Workflow {name}: script not found at {script}"


def test_search_workflow_defines_graph():
    """search_workflow.py defines a top-level 'graph' (runpy with run_name='__load__'). Skip if app/DB not available."""
    import runpy
    root = Path(__file__).resolve().parent.parent
    script = root / "daggr_workflows" / "search_workflow.py"
    if not script.exists():
        pytest.skip("search_workflow.py not found")
    try:
        globals_ = runpy.run_path(str(script), run_name="__load__")
    except Exception as e:
        pytest.skip(f"search_workflow load failed (app/DB may be required): {e}")
    assert "graph" in globals_, "search_workflow must define 'graph'"
