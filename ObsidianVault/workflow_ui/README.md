# Workflow GUI (Phase 3)

Thin web UI for the Storyboard-to-Encounter workflow. Calls `scripts/storyboard_workflow.py` entry points only; no new backend APIs.

## Run

From **ObsidianVault** (parent of `workflow_ui`):

```bash
cd D:\Arc_Forge\ObsidianVault
pip install -r workflow_ui/requirements.txt
python -m workflow_ui.app
```

Then open http://127.0.0.1:5050

**Required paths (when running via `python -m workflow_ui.app`):** `Campaigns/` must exist and be a directory; `scripts/ingest_config.json` must exist (used by session ingest). If either is missing, the app prints clear errors to stderr and exits with code 1. When using `flask run`, validation is not run at startup (paths are checked on first use).

Or:

```bash
cd D:\Arc_Forge\ObsidianVault
set FLASK_APP=workflow_ui.app
flask run --host=127.0.0.1 --port=5050
```

## Features

- **Pipeline view**: Storyboard → S1 → S2 → S3 → S4 → S5, with artifact checkmarks for the selected arc.
- **Arc file-tree**: List of `Campaigns/{arc_id}/` files; encounter drafts show version and source (provenance).
- **Stage screens**: S1 (Run Stage 1), S2 (Run Stage 2), S3 (human-only), S4 (Refine encounter), S5 (Export final specs).
- **Stage 1 form**: Edit task decomposition (encounters, opportunities, sequence_constraints); load/save `task_decomposition.yaml`.
- **Stage 3 form**: Edit feedback (per-encounter items with type and type-specific fields); load/save `{arc_id}_feedback.yaml`.
- **Session memory**: Run Archivist and Foreshadow from the UI; outputs in `Campaigns/_session_memory/` (e.g. `YYYY-MM-DD_archivist.md`, `threads.md`).
- **Gradio demo** (optional): Header link "Gradio demo" opens `/tools/gradio`, which redirects to a standalone Gradio app (KB Search). See [Gradio](#gradio) below.

## Gradio

**Use Gradio for:** Quick tool screens — (1) **Campaign KB Search** (calls `/api/kb/search`), (2) **Workflow demo** (quick reference for campaign_kb ingest/search/merge). **Use existing HTML/templates for:** Main storyboard/encounter workflow, pipeline view, stage forms, session memory. Conventions and when to use Gradio vs templates: `.cursor/docs/GRADIO_FRAMEWORK.md`.

- **Route:** `/tools/gradio` (redirects to the Gradio app URL).
- **To run:** Start the Gradio app in a second terminal (same machine as Flask), then use the header link or open `/tools/gradio`:

```bash
cd D:\Arc_Forge\ObsidianVault
pip install -r workflow_ui/requirements.txt   # includes gradio>=4.0.0
python -m workflow_ui.gradio_app
```

Default Gradio URL: `http://localhost:7861`. Override with `GRADIO_APP_URL` (Flask) and `GRADIO_PORT` (Gradio app). The Gradio screen calls the Flask app's `/api/kb/search` (no duplicate backend logic).

## Backend contract

GUI uses the same entry points as the CLI: `run_stage_1`, `run_stage_2`, `refine_encounter`, `export_final_specs`. Paths and `arc_id` are sent in request bodies; Stage 4 accepts `arc_id` and derives `feedback_path` when omitted.

## Testing

Run API tests from **workflow_ui** so pytest uses project-local temp (`.pytest-tmp/`; no system temp):

```bash
cd D:\Arc_Forge\ObsidianVault\workflow_ui
pytest tests/ -v
```

Or from ObsidianVault: `cd workflow_ui && pytest tests/ -v`. (If `pytest` is not on PATH, use `python -m pytest tests/ -v`.)

### Playwright (E2E)

Install Playwright browsers after dependencies:

```bash
pip install -r workflow_ui/requirements.txt
python -m playwright install
```

**Env requirements:** Storyboard under `Campaigns/_rag_outputs/` (or path passed to Stage 1); `ingest_config.json` in `scripts/` for Stage 2/4 and for Session memory (Archivist/Foreshadow). "Real" run stages (S1, S2, S4, S5) and Session memory need RAG/LLM; tests mock workflow functions so RAG/LLM are not invoked.

- **Manual I/O checklist:** [docs/manual_io_checklist.md](docs/manual_io_checklist.md) – stepwise browser validation.
- **Remaining work:** [docs/DEVELOPMENT_PLAN_REMAINING.md](docs/DEVELOPMENT_PLAN_REMAINING.md) – tasks and agent-referenceable plan.

## See also

- [Campaigns/docs/gui_spec.md](../Campaigns/docs/gui_spec.md) – full GUI spec  
- [Campaigns/docs/workflow_diagrams.md](../Campaigns/docs/workflow_diagrams.md) – pipeline and file-tree diagrams
- [docs/DEVELOPMENT_PLAN_REMAINING.md](docs/DEVELOPMENT_PLAN_REMAINING.md) – remaining tasks and agent-referenceable plan
- `.cursor/docs/GRADIO_FRAMEWORK.md` – Gradio + Daggr conventions (cross-codebase)
