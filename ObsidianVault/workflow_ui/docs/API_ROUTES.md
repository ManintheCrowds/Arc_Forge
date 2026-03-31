# workflow_ui HTTP API (Flask)

**Base URL:** `http://WORKFLOW_UI_HOST:WORKFLOW_UI_PORT` (defaults `127.0.0.1:5050`).

**Auth (current):** No session or API key unless `WORKFLOW_UI_REQUIRE_API_KEY=1` and `WORKFLOW_UI_API_KEY` are set (see [CAPABILITY_MAP.md](../../docs/CAPABILITY_MAP.md)). Rate limit: `30/min` on `POST /api/workbench/chat`.

**Machine-readable:** `GET /openapi.json` (partial schema) and `GET /docs` (Swagger UI) on this app.

| Method | Path | Purpose | Body / query | Auth |
|--------|------|---------|----------------|------|
| GET | `/metrics` | Prometheus metrics | — | open |
| GET | `/` | Main UI | — | open |
| GET | `/guide/<path>` | Static guide files | — | open |
| GET | `/openapi.json` | Partial OpenAPI 3 spec | — | open |
| GET | `/docs` | Swagger UI | — | open |
| GET | `/api/status` | Health; may proxy campaign_kb `/openapi.json` | — | open |
| GET | `/api/arcs` | List story arcs | — | open |
| GET | `/api/modules` | List modules | — | open |
| GET | `/api/modules/<c>/<m>/tree` | Module file tree | — | open |
| GET | `/api/modules/<c>/<m>/file/<path>` | Read module file | — | open |
| POST | `/api/modules/create` | Create module scaffold | JSON | key if required |
| GET | `/api/arc/<arc_id>/tree` | Arc file tree | — | open |
| GET | `/api/arc/<arc_id>/artifacts` | Arc artifacts | — | open |
| GET/PUT | `/api/arc/<arc_id>/task_decomposition` | Get/save task decomposition | PUT: body | key if required |
| GET/PUT | `/api/arc/<arc_id>/feedback` | Get/save feedback | PUT: body | key if required |
| GET/PUT | `/api/arc/<arc_id>/file/<path>` | Read/write arc file | PUT: body | key if required |
| POST | `/api/run/stage1` | Storyboard → task decomposition | JSON | key if required |
| POST | `/api/run/stage2` | Stage 2 pipeline | JSON | key if required |
| POST | `/api/run/stage4` | Stage 4 pipeline | JSON | key if required |
| POST | `/api/run/stage5` | Stage 5 pipeline | JSON | key if required |
| GET | `/api/workbench/idea-web` | Idea web graph data | query params | open |
| GET | `/api/workbench/dependencies` | Dependency data | — | open |
| GET | `/api/workbench/campaigns` | Campaign list | — | open |
| GET | `/api/workbench/modules` | Modules for workbench | — | open |
| GET | `/api/workbench/tree` | Workbench tree | query | open |
| POST | `/api/workbench/create-module` | Create module | JSON | key if required |
| POST | `/api/workbench/chat` | Ollama chat + optional context | JSON: `message`, optional `context_path`, `campaign`, `module`, `arc_id`, `recent_files[]` | rate limited; key if required |
| GET | `/api/workbench/timeline` | Timeline notes | query | open |
| GET | `/api/session/files` | List session memory files | — | open |
| GET | `/api/session/file/<path>` | Read session file | — | open |
| POST | `/api/session/archivist` | Run archivist | JSON | key if required |
| POST | `/api/session/foreshadow` | Run foreshadow | JSON | key if required |
| GET | `/api/kb/status` | campaign_kb reachable | — | open |
| GET | `/api/kb/search` | Proxy KB search | `query`, `limit`, … | open |
| POST | `/api/kb/ingest/pdfs` | Proxy KB PDF ingest | JSON | key if required |
| POST | `/api/kb/merge` | Proxy KB merge | JSON | key if required |
| GET | `/tools/kb-daggr` | Redirect to Daggr UI | — | open |
| GET | `/tools/gradio` | Redirect to Gradio | — | open |
| GET | `/tools/daggr-graphs` | DAGGR graph page | — | open |
| GET | `/api/daggr/graph/<stack>/<name>` | Workflow graph JSON | — | open |
| GET | `/api/diagrams/pipeline` | Markdown diagrams | — | open |
| GET | `/api/diagrams/pipeline_mermaid` | Mermaid extract | — | open |

**Environment:** `CAMPAIGN_KB_URL`, `OLLAMA_URL`, `OLLAMA_MODEL`, `WORKFLOW_UI_CAMPAIGNS_PATH`, etc. (see `app.py`).
