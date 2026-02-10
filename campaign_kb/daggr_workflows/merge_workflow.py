# PURPOSE: Daggr workflow for merging seed docs with citations from KB.
# DEPENDENCIES: daggr, gradio, app.database, app.merge.service, app.utils.text
# MODIFICATION NOTES: Visual merge pipeline: seeds -> keywords -> citations -> output.

"""
Merge Workflow – load seed paths, extract keywords, search for citations, write merged doc.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from daggr import FnNode, Graph
import gradio as gr
from app.database import SessionLocal
from app.merge.service import create_merged_seed_doc
from app.config import settings
from app.utils.text import normalize_text, extract_keywords
from daggr_workflows.report_run import with_run_reporting


@with_run_reporting
def load_and_keywords(seed_paths_str: str, max_terms: int) -> str:
    try:
        paths = [Path(p.strip()) for p in seed_paths_str.splitlines() if p.strip()]
        if not paths:
            paths = list(settings.seed_doc_paths)
        combined = ""
        for p in paths:
            if p.exists():
                combined += "\n" + p.read_text(encoding="utf-8", errors="ignore")
        normalized = normalize_text(combined)
        keywords = extract_keywords(normalized, max_terms=max_terms)
        return "Keywords: " + ", ".join(keywords[:15]) + (f" (+{len(keywords)-15} more)" if len(keywords) > 15 else "")
    except Exception as e:
        return f"Keywords error: {str(e)}"


@with_run_reporting
def merge_step(seed_paths_str: str, output_path_str: str, max_citations: int, max_terms: int) -> str:
    paths = [Path(p.strip()) for p in seed_paths_str.splitlines() if p.strip()]
    if not paths:
        paths = list(settings.seed_doc_paths)
    output_path = Path(output_path_str.strip()) if output_path_str.strip() else settings.output_dir / "campaign_seed_merged.md"
    db = SessionLocal()
    try:
        out_path, citation_count = create_merged_seed_doc(db, paths, output_path, max_citations=max_citations)
        return f"Wrote {out_path}\nCitations: {citation_count}"
    except Exception as e:
        return f"Merge error: {str(e)}"
    finally:
        db.close()


seed_paths_in = gr.Textbox(
    label="Seed paths (one per line)",
    value="\n".join(str(p) for p in settings.seed_doc_paths),
    lines=3,
)
output_path_in = gr.Textbox(
    label="Output path",
    value=str(settings.output_dir / "campaign_seed_merged.md"),
    lines=1,
)
max_cit_in = gr.Number(label="Max citations", value=25)
max_terms_in = gr.Number(label="Keyword max terms", value=20)

keywords_node = FnNode(
    fn=load_and_keywords,
    inputs={
        "seed_paths_str": seed_paths_in,
        "max_terms": max_terms_in,
    },
    outputs={"result": gr.Textbox(label="Extracted keywords", lines=3)},
)

merge_node = FnNode(
    fn=merge_step,
    inputs={
        "seed_paths_str": seed_paths_in,
        "output_path_str": output_path_in,
        "max_citations": max_cit_in,
        "max_terms": max_terms_in,
    },
    outputs={"result": gr.Textbox(label="Merge result", lines=5)},
)

graph = Graph(
    name="Campaign KB Merge",
    nodes=[keywords_node, merge_node],
)

if __name__ == "__main__":
    print("Campaign KB Merge – merge seeds with citations.")
    graph.launch()
