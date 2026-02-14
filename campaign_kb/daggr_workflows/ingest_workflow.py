# PURPOSE: Daggr workflow for campaign_kb multi-source ingestion.
# DEPENDENCIES: daggr, gradio, app.database, app.ingest.service, app.config
# MODIFICATION NOTES: Visual ingest pipeline with per-source nodes.

"""
Ingest Workflow – run PDFs, seeds, DoD, docs, repos and inspect counts per step.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from daggr import FnNode, Graph
import gradio as gr
from app.database import SessionLocal
from app.ingest.service import (
    ingest_pdfs,
    ingest_seed_docs,
    ingest_dod_site,
    ingest_reference_docs,
    ingest_github_repos,
)
from app.config import settings
from daggr_workflows.report_run import with_run_reporting


@with_run_reporting
def _run_pdfs(pdf_root_str: str, source_name: str) -> str:
    db = SessionLocal()
    try:
        root = Path(pdf_root_str.strip()) if pdf_root_str.strip() else settings.pdf_root
        docs, sections = ingest_pdfs(db, root, source_name or "local_pdfs")
        return f"PDFs: {docs} documents, {sections} sections"
    except Exception as e:
        return f"PDF ingest error: {str(e)}"
    finally:
        db.close()


@with_run_reporting
def _run_seeds(seed_paths_str: str, source_name: str) -> str:
    db = SessionLocal()
    try:
        paths = [Path(p.strip()) for p in seed_paths_str.splitlines() if p.strip()]
        if not paths:
            paths = list(settings.seed_doc_paths)
        docs, sections = ingest_seed_docs(db, paths, source_name or "seed_docs")
        return f"Seeds: {docs} documents, {sections} sections"
    except Exception as e:
        return f"Seed ingest error: {str(e)}"
    finally:
        db.close()


@with_run_reporting
def _run_dod(base_url: str, max_pages: int, source_name: str) -> str:
    db = SessionLocal()
    try:
        url = base_url.strip() or settings.dod_base_url
        docs, sections = ingest_dod_site(
            db, url, max_pages,
            settings.dod_request_timeout_seconds,
            settings.dod_user_agent,
            source_name or "doctors_of_doom",
        )
        return f"DoD: {docs} documents, {sections} sections"
    except Exception as e:
        return f"DoD ingest error: {str(e)}"
    finally:
        db.close()


@with_run_reporting
def _run_docs(docs_root_str: str, source_name: str) -> str:
    db = SessionLocal()
    try:
        root = Path(docs_root_str.strip()) if docs_root_str.strip() else settings.dod_docs_root
        docs, sections = ingest_reference_docs(db, root, source_name or "dod_docs")
        return f"Docs: {docs} documents, {sections} sections"
    except Exception as e:
        return f"Docs ingest error: {str(e)}"
    finally:
        db.close()


@with_run_reporting
def _run_campaign_docs(docs_root_str: str, source_name: str) -> str:
    """Ingest campaign docs (RAG-aligned). Run before RAG with use_kb_search=true."""
    db = SessionLocal()
    try:
        root = Path(docs_root_str.strip()) if docs_root_str.strip() else settings.campaign_docs_root
        docs, sections = ingest_reference_docs(db, root, source_name or "campaign_docs")
        return f"Campaign docs: {docs} documents, {sections} sections"
    except Exception as e:
        return f"Campaign docs ingest error: {str(e)}"
    finally:
        db.close()


@with_run_reporting
def _run_repos(repo_urls_str: str, timeout: float, source_name: str) -> str:
    db = SessionLocal()
    try:
        urls = [u.strip() for u in repo_urls_str.splitlines() if u.strip()]
        if not urls:
            urls = list(settings.repo_urls)
        docs, sections = ingest_github_repos(db, urls, timeout, source_name or "github_repos")
        return f"Repos: {docs} documents, {sections} sections"
    except Exception as e:
        return f"Repos ingest error: {str(e)}"
    finally:
        db.close()


pdf_root_in = gr.Textbox(label="PDF root", value=str(settings.pdf_root), lines=1)
source_pdfs = gr.Textbox(label="Source name (PDFs)", value="local_pdfs", lines=1)
pdf_node = FnNode(
    fn=_run_pdfs,
    inputs={"pdf_root_str": pdf_root_in, "source_name": source_pdfs},
    outputs={"result": gr.Textbox(label="PDF ingest result", lines=2)},
)

seed_paths_in = gr.Textbox(
    label="Seed paths (one per line)",
    value="\n".join(str(p) for p in settings.seed_doc_paths),
    lines=3,
)
source_seeds = gr.Textbox(label="Source name (seeds)", value="seed_docs", lines=1)
seed_node = FnNode(
    fn=_run_seeds,
    inputs={"seed_paths_str": seed_paths_in, "source_name": source_seeds},
    outputs={"result": gr.Textbox(label="Seed ingest result", lines=2)},
)

dod_url_in = gr.Textbox(label="DoD base URL", value=settings.dod_base_url, lines=1)
dod_pages_in = gr.Number(label="Max pages", value=min(10, settings.dod_max_pages))
source_dod = gr.Textbox(label="Source name (DoD)", value="doctors_of_doom", lines=1)
dod_node = FnNode(
    fn=_run_dod,
    inputs={"base_url": dod_url_in, "max_pages": dod_pages_in, "source_name": source_dod},
    outputs={"result": gr.Textbox(label="DoD ingest result", lines=2)},
)

docs_root_in = gr.Textbox(label="Docs root", value=str(settings.dod_docs_root), lines=1)
source_docs = gr.Textbox(label="Source name (docs)", value="dod_docs", lines=1)
docs_node = FnNode(
    fn=_run_docs,
    inputs={"docs_root_str": docs_root_in, "source_name": source_docs},
    outputs={"result": gr.Textbox(label="Docs ingest result", lines=2)},
)

campaign_docs_root_in = gr.Textbox(
    label="Campaign docs root (RAG-aligned)",
    value=str(settings.campaign_docs_root),
    lines=1,
)
source_campaign_docs = gr.Textbox(label="Source name (campaign)", value="campaign_docs", lines=1)
campaign_docs_node = FnNode(
    fn=_run_campaign_docs,
    inputs={"docs_root_str": campaign_docs_root_in, "source_name": source_campaign_docs},
    outputs={"result": gr.Textbox(label="Campaign docs ingest result", lines=2)},
)

repos_in = gr.Textbox(
    label="Repo URLs (one per line)",
    value="\n".join(settings.repo_urls),
    lines=3,
)
repo_timeout = gr.Number(label="Timeout (s)", value=15.0)
source_repos = gr.Textbox(label="Source name (repos)", value="github_repos", lines=1)
repos_node = FnNode(
    fn=_run_repos,
    inputs={"repo_urls_str": repos_in, "timeout": repo_timeout, "source_name": source_repos},
    outputs={"result": gr.Textbox(label="Repos ingest result", lines=2)},
)

graph = Graph(
    name="Campaign KB Ingest",
    nodes=[pdf_node, seed_node, dod_node, docs_node, campaign_docs_node, repos_node],
)

if __name__ == "__main__":
    print("Campaign KB Ingest – run any node(s) to ingest into SQLite.")
    graph.launch()
