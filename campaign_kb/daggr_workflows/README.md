# Campaign KB Daggr Workflows

Visual, step-level pipelines for the Wrath & Glory campaign knowledge base (SQLite).

## Workflows

- **ingest** – Ingest PDFs, seed docs, Doctors of Doom site, reference docs, GitHub repos. Run any subset of nodes and inspect document/section counts.
- **search** – Query sections; see results with document/source and snippet.
- **merge** – Merge seed documents with citations from the KB; inspect keywords then write merged output.

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

**Monitoring:** Set `WATCHTOWER_METRICS_URL` to the WatchTower Flask app base URL (e.g. `http://localhost:5000`) to report workflow runs to WatchTower. Runs are sent to `POST /api/daggr/run-complete` with `project=campaign_kb`.
