---
title: "Capability map (Arc_Forge / ObsidianVault)"
tags: ["type/research", "status/draft", "domain/harness"]
---

# Capability map (Arc_Forge / ObsidianVault)

This document ties together **user-facing surfaces**, **HTTP APIs**, and **auth** for agent parity and discovery.

## Services

| Service | Role | OpenAPI / spec |
|---------|------|----------------|
| **campaign_kb** | FastAPI: ingest PDFs/seeds/repos, search, merge | `GET {CAMPAIGN_KB_URL}/openapi.json` (e.g. `http://127.0.0.1:8000/openapi.json`) |
| **workflow_ui** | Flask: storyboard stages, arc files, workbench chat, KB proxy | `GET http://<host>:<port>/openapi.json` (partial), full route table: [API_ROUTES.md](../workflow_ui/docs/API_ROUTES.md) |

## UI → HTTP (high level)

| User intent | Primary API |
|-------------|-------------|
| List arcs / modules | `GET /api/arcs`, `GET /api/modules` |
| Edit arc files | `GET/PUT /api/arc/<id>/file/...` |
| Run pipeline stages | `POST /api/run/stage1` … `stage5` |
| Workbench LLM chat | `POST /api/workbench/chat` |
| Search campaign KB | `GET /api/kb/search?query=...` (proxies campaign_kb) |
| Session tools | `POST /api/session/archivist`, `POST /api/session/foreshadow` |

After long-running `POST /api/run/stage*`, refresh artifact views via `GET /api/arc/<id>/artifacts` (see [POLLING_AND_REALTIME.md](POLLING_AND_REALTIME.md)).

## Authentication

- **Default:** No login; bind Flask to `127.0.0.1` for local use.
- **Optional:** Set `WORKFLOW_UI_REQUIRE_API_KEY=1` and `WORKFLOW_UI_API_KEY`; mutating `POST`/`PUT` under `/api/` require header `Authorization: Bearer <key>` (unless `GET`/`/`).

## Related docs

- [PRIMITIVES_VS_WORKFLOWS.md](PRIMITIVES_VS_WORKFLOWS.md) — route classification
- [POLLING_AND_REALTIME.md](POLLING_AND_REALTIME.md) — stage runs vs live updates
- Auth: optional `WORKFLOW_UI_REQUIRE_API_KEY` + `WORKFLOW_UI_API_KEY`; localhost exempt via `WORKFLOW_UI_API_KEY_EXEMPT_LOCAL` (default on). See [workflow_ui/docs/API_ROUTES.md](../workflow_ui/docs/API_ROUTES.md).
- [Campaigns/docs/gui_spec.md](../Campaigns/docs/gui_spec.md) — GUI contract
- [campaign_kb/docs/API_AND_CRUD.md](../../campaign_kb/docs/API_AND_CRUD.md) — KB API and CRUD scope
