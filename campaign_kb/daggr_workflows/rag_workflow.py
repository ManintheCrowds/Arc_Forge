# PURPOSE: Daggr workflow for RAG pipeline (ObsidianVault scripts).
# DEPENDENCIES: daggr, gradio, rag_pipeline.run_pipeline (ObsidianVault/scripts)
# MODIFICATION NOTES: Reports runs with project=rag_pipeline; workflow name=rag.

"""
RAG Workflow – run the ObsidianVault RAG pipeline with query input.
Reports to WatchTower with project=rag_pipeline when DAGGR_CURRENT_PROJECT is set.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARC_FORGE = ROOT.parent
OBSIDIAN_SCRIPTS = ARC_FORGE / "ObsidianVault" / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(OBSIDIAN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(OBSIDIAN_SCRIPTS))

# Set Daggr reporting context for rag_pipeline
os.environ.setdefault("DAGGR_CURRENT_PROJECT", "rag_pipeline")
os.environ.setdefault("DAGGR_CURRENT_WORKFLOW_NAME", "rag")

from daggr import FnNode, Graph
import gradio as gr
from daggr_workflows.report_run import with_run_reporting

_DEFAULT_CONFIG_RAW = os.environ.get("RAG_INGEST_CONFIG_PATH", "").strip()
DEFAULT_CONFIG = Path(_DEFAULT_CONFIG_RAW) if _DEFAULT_CONFIG_RAW else (OBSIDIAN_SCRIPTS / "ingest_config.json")


@with_run_reporting
def rag_step(query: str, config_path_str: str) -> str:
    """Run RAG pipeline with optional query. Reports run to WatchTower."""
    config_path = Path(config_path_str.strip()) if config_path_str.strip() else DEFAULT_CONFIG
    if not config_path.exists():
        return f"Config not found: {config_path}"
    try:
        from rag_pipeline import run_pipeline
        result = run_pipeline(
            config_path=config_path,
            query=query.strip() or None,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"RAG error: {type(e).__name__}: {e}"


query_in = gr.Textbox(label="Query (optional)", placeholder="Enter query for context retrieval", lines=2)
config_in = gr.Textbox(label="Config path", value=str(DEFAULT_CONFIG), lines=1)

rag_node = FnNode(
    fn=rag_step,
    inputs={"query": query_in, "config_path_str": config_in},
    outputs={"result": gr.Textbox(label="RAG result", lines=12)},
)

graph = Graph(name="RAG Pipeline", nodes=[rag_node])

if __name__ == "__main__":
    print("RAG Pipeline – run ObsidianVault RAG with optional query.")
    graph.launch()
