# PURPOSE: Single Daggr app that selects campaign_kb workflow via CLI or env and launches its graph.
# DEPENDENCIES: daggr, gradio, run_workflow.WORKFLOWS
# MODIFICATION NOTES: Parity with WatchTower single_app; enables one Gradio entry point for KB workflows.

"""
Single Daggr app for campaign_kb – choose workflow by name and launch.

Usage:
  python -m daggr_workflows.single_app              # list and prompt, or default search
  python -m daggr_workflows.single_app search
  python -m daggr_workflows.single_app ingest
  python -m daggr_workflows.single_app merge
  DAGGR_WORKFLOW=search python -m daggr_workflows.single_app
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from daggr_workflows.run_workflow import WORKFLOWS

_ROOT = Path(__file__).resolve().parent.parent


def get_workflow_name() -> str | None:
    if len(sys.argv) > 1:
        return sys.argv[1].lower().strip()
    return (
        os.environ.get("DAGGR_WORKFLOW_SELECTOR", "").strip().lower()
        or os.environ.get("DAGGR_WORKFLOW", "").strip().lower()
        or None
    )


def load_graph(name: str):
    if name not in WORKFLOWS:
        return None
    script = _ROOT / WORKFLOWS[name]["script"].replace("/", os.sep)
    if not script.exists():
        return None
    import runpy
    globals_ = runpy.run_path(str(script), run_name="__load__")
    return globals_.get("graph")


def main() -> int:
    name = get_workflow_name()
    if not name:
        print("Campaign KB Daggr Single App – choose a workflow")
        print("================================================\n")
        for n, info in WORKFLOWS.items():
            print(f"  {n:10} - {info['description']}")
        print("\nUsage: python -m daggr_workflows.single_app <name>")
        print("   or: DAGGR_WORKFLOW=<name> python -m daggr_workflows.single_app")
        print("   or: DAGGR_WORKFLOW_SELECTOR=<name> python -m daggr_workflows.single_app")
        print("\nDefaulting to 'search' in 3s (Ctrl+C to cancel)...")
        import time
        try:
            time.sleep(3)
            name = "search"
        except KeyboardInterrupt:
            return 0
    if name not in WORKFLOWS:
        print(f"Unknown workflow: {name}", file=sys.stderr)
        print("Available:", ", ".join(WORKFLOWS.keys()), file=sys.stderr)
        return 1
    graph = load_graph(name)
    if graph is None:
        print(f"Could not load graph for: {name}", file=sys.stderr)
        return 1
    os.environ["DAGGR_CURRENT_WORKFLOW_NAME"] = name
    print(f"Launching workflow: {name}")
    graph.launch()
    return 0


if __name__ == "__main__":
    sys.exit(main())
