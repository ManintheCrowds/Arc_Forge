# Campaign KB Daggr Workflows

Visual, step-level pipelines for the Wrath & Glory campaign knowledge base (SQLite).

## Workflows

- **ingest** – Ingest PDFs, seed docs, Doctors of Doom site, reference docs, GitHub repos. Run any subset of nodes and inspect document/section counts.
- **search** – Query sections; see results with document/source and snippet.
- **merge** – Merge seed documents with citations from the KB; inspect keywords then write merged output.
- **rag** – Run ObsidianVault RAG pipeline with optional query; reports with `project=rag_pipeline`.

## Run

From `campaign_kb` directory:

```bash
# Single app (recommended): one Gradio UI per workflow
python -m daggr_workflows.single_app search
python -m daggr_workflows.single_app ingest
python -m daggr_workflows.single_app merge

# Or list and run via run_workflow
python -m daggr_workflows.run_workflow
python -m daggr_workflows.run_workflow search
```

## Dependencies

```bash
pip install -r requirements-daggr.txt
```

Uses the same DB as the FastAPI app (`data/kb.sqlite3`). Run workflows with the API stopped or alongside it.

Gradio UIs follow the shared framework: see `.cursor/docs/GRADIO_FRAMEWORK.md` (in the CodeRepositories workspace).

## Environment variables

| Variable | Purpose | Default | Used by |
|----------|---------|---------|---------|
| `WATCHTOWER_METRICS_URL` | Base URL for POST /api/daggr/run-complete | (unset = no-op) | report_run.py |
| `WATCHTOWER_ERRORS_URL` | Base URL for POST /api/errors | fallback to WATCHTOWER_METRICS_URL | error_handling.py (ObsidianVault) |
| `DAGGR_CURRENT_PROJECT` | Project label in run-complete payload | campaign_kb | report_run.py |
| `DAGGR_CURRENT_WORKFLOW_NAME` | Workflow name in run-complete payload | (set by single_app or run_workflow) | report_run.py |
| `DAGGR_WORKFLOW` | Default workflow for single_app when no CLI arg | (none) | single_app.py |
| `DAGGR_WORKFLOW_SELECTOR` | Alias for DAGGR_WORKFLOW (same behavior) | (none) | single_app.py |
| `DAGGR_PORT` | Gradio server port for Daggr workflows | 7860 (Gradio default) | graph.launch() |
| `RAG_INGEST_CONFIG_PATH` | Path to ingest_config.json for RAG workflow | ObsidianVault/scripts/ingest_config.json | rag_workflow.py |

**Monitoring:** Set `WATCHTOWER_METRICS_URL` to the WatchTower base URL (e.g. `http://localhost:8000` for campaign_kb FastAPI) to report workflow runs. Runs are sent to `POST /api/daggr/run-complete` with `project` from env `DAGGR_CURRENT_PROJECT` (default `campaign_kb`). The campaign_kb FastAPI app exposes both `/api/daggr/run-complete` and `/api/errors`; set `WATCHTOWER_METRICS_URL` to the campaign_kb URL to use it as the receiver.
