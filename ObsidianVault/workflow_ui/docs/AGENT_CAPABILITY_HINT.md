# Agent capability hint (quick links)

## Prompt and template accuracy

Instructions to the model should **truthfully describe scope** (which API, which headers, what is not available). Misleading location or filler text reduces reliability more than missing length — see the portfolio research note [2026-03-31-introspection-rest-mission-control-sources.md](../../research/2026-03-31-introspection-rest-mission-control-sources.md) (VGEL process lesson). This is **not** a claim that models can introspect in production; apply the workspace **secure-contain-protect** skill for untrusted content.

- **workflow_ui API:** [API_ROUTES.md](API_ROUTES.md) — full route table.
- **Swagger UI:** `/docs` on the workflow_ui server (partial OpenAPI).
- **Raw spec:** `/openapi.json`
- **Vault-wide map:** [ObsidianVault/docs/CAPABILITY_MAP.md](../../docs/CAPABILITY_MAP.md)
- **campaign_kb:** `GET {CAMPAIGN_KB_URL}/openapi.json` — see [campaign_kb/docs/API_AND_CRUD.md](../../../campaign_kb/docs/API_AND_CRUD.md)

## Example chat prompts (Workbench)

- Summarize the active note for players in two short paragraphs.
- List open questions implied by this arc’s task decomposition.
- What encounters are missing NPC stat hooks?

## Example API usage (curl)

```bash
curl -s "http://127.0.0.1:5050/api/arcs"
curl -s "http://127.0.0.1:8000/openapi.json"   # campaign_kb
```

When `WORKFLOW_UI_REQUIRE_API_KEY=1`, add `Authorization: Bearer <WORKFLOW_UI_API_KEY>` for mutating `POST`/`PUT` (unless exempting localhost via `WORKFLOW_UI_API_KEY_EXEMPT_LOCAL`).
