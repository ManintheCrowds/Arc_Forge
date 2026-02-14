# PURPOSE: CLI launcher for campaign_kb Daggr workflows.
# DEPENDENCIES: daggr, gradio
# MODIFICATION NOTES: Same pattern as WatchTower run_workflow.

"""
Launch a campaign_kb Daggr workflow by name.

Usage:
  python -m daggr_workflows.run_workflow              # list and prompt
  python -m daggr_workflows.run_workflow ingest      # ingest (PDFs, seeds, DoD, docs, repos)
  python -m daggr_workflows.run_workflow search       # search sections
  python -m daggr_workflows.run_workflow merge       # merge seed doc with citations
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

WORKFLOWS = {
    "ingest": {
        "script": "daggr_workflows/ingest_workflow.py",
        "description": "Ingest PDFs, seeds, DoD, docs, repos into SQLite",
    },
    "search": {
        "script": "daggr_workflows/search_workflow.py",
        "description": "Search campaign KB sections",
    },
    "merge": {
        "script": "daggr_workflows/merge_workflow.py",
        "description": "Merge seed doc with citations from KB",
    },
    "rag": {
        "script": "daggr_workflows/rag_workflow.py",
        "description": "Run ObsidianVault RAG pipeline with optional query",
    },
}


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Campaign KB Daggr Workflows")
        print("===========================\n")
        for name, info in WORKFLOWS.items():
            print(f"  {name:10} - {info['description']}")
        print("\nUsage: python -m daggr_workflows.run_workflow <name>")
        print("  e.g.  python -m daggr_workflows.run_workflow ingest")
        return 0

    name = args[0].lower().strip()
    if name not in WORKFLOWS:
        print(f"Unknown workflow: {name}", file=sys.stderr)
        print("Available:", ", ".join(WORKFLOWS.keys()), file=sys.stderr)
        return 1

    info = WORKFLOWS[name]
    script = ROOT / info["script"].replace("/", os.sep)
    if not script.exists():
        print(f"Script not found: {script}", file=sys.stderr)
        return 1

    os.environ["DAGGR_CURRENT_WORKFLOW_NAME"] = name
    import runpy
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
