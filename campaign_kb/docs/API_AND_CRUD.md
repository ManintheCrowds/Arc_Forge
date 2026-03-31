# campaign_kb API surface and CRUD scope

## Supported operations (HTTP)

The FastAPI app exposes **ingest** (create content in the DB), **search** (read sections), and **merge** (produce a merged markdown artifact). See **`GET /openapi.json`** on the running server for the full schema.

Typical routes:

- `POST /ingest/pdfs`, `POST /ingest/seed`, `POST /ingest/dod`, `POST /ingest/docs`, `POST /ingest/campaign-docs`, `POST /ingest/repos` — create/update `Source`, `Document`, `Section` rows via ingestion pipelines.
- `GET /search` — read matching sections (full-text).
- `POST /merge` — read DB + seed paths, write merged output file.
- `POST /api/daggr/run-complete`, `POST /api/errors` — operational hooks (WatchTower).

## CRUD stance (Option A)

| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| **Document / Section / Source** | Via **ingest** endpoints (additive) | Via **search** (sections) | **Not** exposed as generic PATCH | **Not** exposed as HTTP DELETE |

**Deletion and row-level updates** are not part of the public API. Administrative cleanup uses **database tools** (SQL, migrations) or future admin-guarded endpoints if you add auth first.

This keeps the MVP surface small and avoids accidental data loss from unauthenticated agents.
