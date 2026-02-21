# Arc Forge — campaign workbench for Wrath & Glory

RAG-backed campaign workbench so GMs can plan Wrath & Glory arcs with AI assistance while keeping human authority.

**Arc Forge** is a RAG-backed campaign workbench for the **Wrath & Glory** (Warhammer 40K) TTRPG. It helps GMs and players create and track campaigns by synthesizing adventure arcs, representing stories visually and textually (pipeline, arc tree, storyboards), showing branching narrative (encounters and opportunities), and using AI to assist in rendering the universe during and asynchronously from sessions — with the human as final authority ("AI proposes, human disposes").

The repository folder is intended to be named **Arc_Forge** (paths in config and docs use `D:\Arc_Forge` or the folder name). If your folder is still `wrath_and_glory`, rename it on disk (e.g. `D:\wrath_and_glory` → `D:\Arc_Forge`) and reopen the workspace.

## Purpose

A **RAG system** that assists GMs and players in creating and tracking campaigns:

- **Adventure arcs**: Storyboard → encounter pipeline (S1–S5): task decomposition, encounter drafts, human feedback, refinement, export.
- **Visual and textual representation**: Pipeline view (Mermaid), arc file-tree (encounters, opportunities, task_decomposition, feedback, expanded storyboard), module tree in the workflow UI.
- **Branching narrative**: Encounter/opportunity structure (sequence, after/before, optional threads) and arc tree.
- **AI-assisted universe rendering**: RAG over rules/lore and campaign content; role-based prompts (Story Architect, Encounter Designer, Archivist, Foreshadowing Engine); support during and async from TTRPG sessions.
- **Human authority**: GM remains final arbiter; AI suggests, GM edits and approves.

## What this is

- **Memory**: RAG over rules/lore and campaign content (NPCs, locations, missions).
- **Temporal continuity**: Session summaries, Archivist, Foreshadow threads.
- **Collaborative narrative workbench**: Not "an AI that writes adventures" — modular components, provenance, and human gatekeeping. See [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md).

## Components

| Component | Role | How to run |
|-----------|------|------------|
| **campaign_kb** | FastAPI service: ingest (PDFs, seeds, DoD, docs, repos), full-text search, merge seed doc. SQLite at `campaign_kb/data/kb.sqlite3`. No GUI; API only. | See [Quickstart](#quickstart). |
| **ObsidianVault** | Vault + scripts: PDF ingest, RAG pipeline, storyboard workflow (S1–S5), session Archivist/Foreshadow. | Scripts run from `ObsidianVault`; workflow is driven by **workflow_ui** or CLI. |
| **workflow_ui** | Flask app (default port 5050). Single dashboard: arcs, pipeline (S1–S5), task decomp/feedback forms, session memory, optional Campaign KB panel. | See [Quickstart](#quickstart). |
| **Grimoire** | Separate Obsidian vault (cursor-bridge, dataview, omnisearch, pdf-plus). Use as alternate/reference vault for note-taking and linking; "run workflow" is done via **workflow_ui** (browser) or CLI, not from Grimoire. | Open in Obsidian as a second vault if desired. |

## Quickstart

1. **Start campaign_kb** (optional; needed for KB search/ingest/merge in the dashboard):
   ```bash
   cd campaign_kb
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. **Start workflow_ui** (main GM interface):
   ```bash
   cd ObsidianVault
   pip install -r workflow_ui/requirements.txt
   python -m workflow_ui.app
   ```
   Then open **http://127.0.0.1:5050**

Or use the **unified launcher** (starts both and opens the browser):
- Windows: `.\scripts\start_stack.ps1`
- Linux/macOS: `./scripts/start_stack.sh`

Having issues? See [ObsidianVault/workflow_ui/docs/TROUBLESHOOTING.md](ObsidianVault/workflow_ui/docs/TROUBLESHOOTING.md) (workflow UI) and [ObsidianVault/scripts/TROUBLESHOOTING.md](ObsidianVault/scripts/TROUBLESHOOTING.md) (PDF ingestion).

## Interfacing the User

- **Primary**: Use **workflow_ui** (browser at http://127.0.0.1:5050) for storyboard→encounter workflow (S1–S5), session memory (Archivist/Foreshadow), and — when campaign_kb is running — KB search, ingest, and merge.
- **Secondary**: Use **ObsidianVault** (and optionally **Grimoire**) in Obsidian for editing campaign markdown, session notes, and viewing outputs. Run workflow from the dashboard or CLI, not from Obsidian.
- **API / power users**: campaign_kb exposes OpenAPI at `/openapi.json` when running. workflow_ui routes are documented in [ObsidianVault/workflow_ui/README.md](ObsidianVault/workflow_ui/README.md). Script ingest/search/merge and run stages via curl/Postman or your own scripts.

## Architecture

- **Canonical architecture**: [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md) — system prompt spine, role-based prompt layers, RAG strategy.
- **GUI spec**: [ObsidianVault/Campaigns/docs/gui_spec.md](ObsidianVault/Campaigns/docs/gui_spec.md) — one screen per stage, task decomp and feedback forms, pipeline view, provenance.
- **Workflow diagrams**: [ObsidianVault/Campaigns/docs/workflow_diagrams.md](ObsidianVault/Campaigns/docs/workflow_diagrams.md) — pipeline flowchart, data flow, arc file layout.

## UI roadmap status

- **Wave A (P0–P1): complete** — debug mode env-driven, error payloads normalized, onboarding/prereq status panel, modal file viewer.
- **Wave B (P2–P3): complete** — client-side validation with field errors, progress indicators (S2/S4/session), tab grouping, autosave drafts.
- **Wave C (P4): complete** — modularization, live updates (polling toggle), wizard flow, OpenAPI docs, E2E baseline.
- **Verification:** Unified run (`.\scripts\run_tests.ps1` or `./scripts/run_tests.sh`): campaign_kb 12 passed, workflow_ui 45 passed (1 skipped), ObsidianVault scripts 273 passed (9 skipped). Last run: see [ROADMAP_STATUS.md](ROADMAP_STATUS.md).
- **Remaining work breakdown:** see [ObsidianVault/workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md](ObsidianVault/workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md).

## Testing

Run tests per component:

```bash
# campaign_kb
cd campaign_kb && pytest tests/ -v

# workflow_ui (from ObsidianVault)
cd ObsidianVault && pytest workflow_ui/tests/ -v

# ObsidianVault scripts
cd ObsidianVault && pytest scripts/tests/ -v
```

Unified runner (all three from repo root):

```bash
# From Arc_Forge root
./scripts/run_tests.sh
# or on Windows (PowerShell):
# .\scripts\run_tests.ps1
```

See [scripts/run_tests.sh](scripts/run_tests.sh) (or run_tests.ps1) for exact paths and env notes. For browser I/O validation, see [ObsidianVault/workflow_ui/docs/manual_io_checklist.md](ObsidianVault/workflow_ui/docs/manual_io_checklist.md). workflow_ui exposes OpenAPI at **http://127.0.0.1:5050/docs** when running. Real runs of S2/S4 need RAG/LLM and storyboard under `Campaigns/_rag_outputs/` (or path passed to Stage 1) and `ingest_config.json` for Stage 2/4.

**RAG semantic retrieval (optional):** For ChromaDB-based semantic search, install `pip install -r ObsidianVault/scripts/requirements-rag.txt` and set `use_chroma: true` in `ingest_config.json` → `rag_pipeline`. See [campaign_kb/campaign/05_rag_integration.md](campaign_kb/campaign/05_rag_integration.md) for setup and config.

## Local-first alignment

Arc Forge aligns with [local-first principles](https://www.inkandswitch.com/local-first): vault and campaign markdown live on disk (you own your data); workflow_ui and scripts run locally. RAG/campaign_kb is optional—ingest and search can run fully offline with local embeddings. Community: [LoFi](https://lofi.so), [Local-First News](https://www.localfirstnews.com/).

## License and Credits

Per project conventions. **Wrath & Glory** is a trademark of its respective owners. Rulebook and supplement PDFs are used locally only and are not distributed with this repo; place your own PDFs in the paths configured in `ObsidianVault/scripts/ingest_config.json` (e.g. `ObsidianVault/pdf/`). See this repo's root `.gitignore` for excluded paths (PDFs and optional derived caches).
