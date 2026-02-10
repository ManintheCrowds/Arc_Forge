# PURPOSE: Static verification of Daggr integration (script paths exist, graph export).
# DEPENDENCIES: run_workflow.WORKFLOWS
# MODIFICATION NOTES: Run from campaign_kb root; exit 0 if all pass.

"""
Verify that each registered workflow script exists and defines a top-level `graph = Graph(...)`.
Usage: python -m daggr_workflows.verify_integration
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

try:
    from .run_workflow import WORKFLOWS
except ImportError:
    from run_workflow import WORKFLOWS


def has_graph_export(script_path: Path) -> bool:
    """Return True if file contains a top-level graph = Graph(...) assignment."""
    if not script_path.exists():
        return False
    text = script_path.read_text(encoding="utf-8", errors="ignore")
    return "graph = Graph(" in text


def main() -> int:
    failed = []
    for name, info in WORKFLOWS.items():
        script = ROOT / info["script"].replace("/", os.sep)
        if not script.exists():
            failed.append(f"{name}: script not found: {script}")
            continue
        if not has_graph_export(script):
            failed.append(f"{name}: no 'graph = Graph(...)' in {script.name}")
    if failed:
        for msg in failed:
            print(msg, file=sys.stderr)
        return 1
    print("All workflow scripts exist and export graph.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
