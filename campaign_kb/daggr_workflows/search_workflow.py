# PURPOSE: Daggr workflow for campaign_kb search with visible results.
# DEPENDENCIES: daggr, gradio, app.database, app.search.service, app.models
# MODIFICATION NOTES: Visual search pipeline with citation-style output.

"""
Search Workflow – query sections and see results with document/source context.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from daggr import FnNode, Graph
import gradio as gr
from app.database import SessionLocal
import json
import time
from app.search.service import search_sections
from app.models import Document, Source
from daggr_workflows.report_run import with_run_reporting


def _render_citation(section, document, source) -> str:
    loc = f"p.{section.page_number}" if section.page_number else "n/a"
    origin = document.url or document.path or "unknown"
    return f"- {document.title} ({source.name}) [{loc}] {origin}\n  {section.normalized_text[:200]}..."


@with_run_reporting
def search_step(query: str, limit: int, source_name: str) -> str:
    # #region agent log
    try:
        with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": "search_step_entry",
                "timestamp": int(time.time() * 1000),
                "location": "daggr_workflows/search_workflow.py:34",
                "message": "search_step entry",
                "data": {
                    "query": query,
                    "limit": limit,
                    "source_name": source_name
                },
                "runId": "pre-fix",
                "hypothesisId": "H2"
            }) + "\n")
    except Exception:
        pass
    # #endregion
    if not (query and query.strip()):
        # #region agent log
        try:
            with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "id": "search_step_empty_query",
                    "timestamp": int(time.time() * 1000),
                    "location": "daggr_workflows/search_workflow.py:43",
                    "message": "query missing or blank",
                    "data": {"query": query},
                    "runId": "pre-fix",
                    "hypothesisId": "H3"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        return "Enter a search query."
    db = SessionLocal()
    try:
        # #region agent log
        try:
            with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "id": "search_step_before_search",
                    "timestamp": int(time.time() * 1000),
                    "location": "daggr_workflows/search_workflow.py:55",
                    "message": "before search_sections",
                    "data": {
                        "query": query.strip(),
                        "limit": int(limit) if limit is not None else None,
                        "source_name": (source_name.strip() if source_name else None)
                    },
                    "runId": "pre-fix",
                    "hypothesisId": "H4"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        results = search_sections(
            db, query.strip(), limit=int(limit) or 20,
            source_name=source_name.strip() or None,
        )
        if not results:
            # #region agent log
            try:
                with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "id": "search_step_no_results",
                        "timestamp": int(time.time() * 1000),
                        "location": "daggr_workflows/search_workflow.py:69",
                        "message": "no results",
                        "data": {"query": query.strip()},
                        "runId": "pre-fix",
                        "hypothesisId": "H4"
                    }) + "\n")
            except Exception:
                pass
            # #endregion
            return "No sections matched."
        lines = []
        for section, rank in results:
            document = db.query(Document).filter(Document.id == section.document_id).one()
            src = db.query(Source).filter(Source.id == document.source_id).one()
            lines.append(_render_citation(section, document, src))
        return "\n".join(lines)
    except Exception as e:
        # #region agent log
        try:
            with open(r"d:\CodeRepositories\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "id": "search_step_exception",
                    "timestamp": int(time.time() * 1000),
                    "location": "daggr_workflows/search_workflow.py:81",
                    "message": "search_step exception",
                    "data": {"error": str(e)},
                    "runId": "pre-fix",
                    "hypothesisId": "H5"
                }) + "\n")
        except Exception:
            pass
        # #endregion
        return f"Search error: {str(e)}"
    finally:
        db.close()


query_in = gr.Textbox(label="Query", placeholder="e.g. tier 2 requisition", lines=2)
limit_in = gr.Number(label="Limit", value=20)
source_filter = gr.Textbox(label="Source name (optional)", value="", lines=1)
search_node = FnNode(
    fn=search_step,
    inputs={"query": query_in, "limit": limit_in, "source_name": source_filter},
    outputs={"result": gr.Textbox(label="Search results", lines=15)},
)

graph = Graph(name="Campaign KB Search", nodes=[search_node])

if __name__ == "__main__":
    print("Campaign KB Search – query the knowledge base.")
    graph.launch()
