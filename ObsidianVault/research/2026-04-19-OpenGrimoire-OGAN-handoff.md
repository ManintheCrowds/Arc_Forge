---
date: 2026-04-19
tags:
  - opengrimoire
  - engineering
  - handoff
  - ogan
  - rest-contract
---

# OpenGrimoire — OGAN handoff (capabilities, viz parity, mock banner, OpenAPI)

**Repo:** `OpenGrimoire` (GitHub sibling under same parent as `Arc_Forge`).

## Shipped in tree (session close-out)

### OGAN-02 / OGAN-03 — Capabilities + agent viz parity

- **`GET /api/capabilities`:** new **`ui_surfaces[]`** (`survey_cohort_charts`, `survey_network_constellation`) with paths, `fetch_pattern`, `survey_read_gate_hint` (SSOT string), `agent_note` pointers to **`docs/AGENT_INTEGRATION.md`** § Survey graph JSON.
- **`workflows`** entry **`cohort_survey_visualization`:** `api` documents **`all=1`** vs **`all=0` + `showTestData`**; `reference_note` defers to `ui_surfaces`.
- **Docs:** `docs/ARCHITECTURE_REST_CONTRACT.md` (capabilities matrix), **`docs/AGENT_INTEGRATION.md`** (graph parity: no HTTP `{nodes,edges}`; `processVisualizationData` / query semantics).
- **Tests:** `e2e/capabilities.spec.ts` asserts `ui_surfaces` shape.
- **OGAN-03 API bundle:** intentionally **not** added (doc-first); optional server graph remains backlog if product asks.

### OGAN-04 / OGAN-05 — Mock cohort UX + survey read OpenAPI

- **`/visualization/alluvial`:** **`MockSurveyDataBanner`** inside **`VisualizationSurveyDataProvider`** so standalone alluvial matches main viz (no silent mock cohort).
- **`MockSurveyDataBanner`:** copy when no HTTP error — empty API or rows failed validation (not “filters”).
- **E2E:** `e2e/visualization-mock-banner.spec.ts` — route stub empty `{ data: [] }`, assert **`data-testid="opengrimoire-viz-mock-data-banner"`**.
- **Partial OpenAPI:** `src/lib/openapi/openapi-document.ts` — **`components.schemas`** for visualization rows + **`{ data }` / `{ items }`**, query params **`all`**, **`showTestData`**, **`200`/`401`/`500`** for **`GET /api/survey/visualization`** and **`GET /api/survey/approved-qualities`**.
- **E2E:** `e2e/openapi.spec.ts` asserts **`$ref`** on those **`200`** bodies.
- **`CHANGELOG.md`:** Unreleased bullets for OGAN-04/05 (and prior OGAN-02/03 where applicable).

## Verification commands (re-run before PR)

```bash
cd OpenGrimoire
npm run type-check
npm run verify:capabilities
npm run verify:openapi
npx playwright test e2e/capabilities.spec.ts e2e/visualization-mock-banner.spec.ts e2e/openapi.spec.ts
```

## Tracker sync (post-screenshot)

Canonical **MiscRepos** harness state: **OGAN-02–OGAN-05** removed from **`pending_tasks.md`** (PENDING_OPENGRIMOIRE_AGENT_NATIVE_DECOMPOSED) and appended to **`completed_tasks.md`** (§ PENDING_AGENT_NATIVE) **2026-04-19**. **OpenGrimoire** **`docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md`** — closure policy table + top-10 P2–P5 rows + MCP action-parity discovery row updated to match. Operator: **`npm run vault:sync`** from MiscRepos if you mirror harness docs into **`ObsidianVault/Harness/`**.

## Follow-ups (not done here)

- **Constellation** (`/constellation`): still **Zustand / `fetchVisualizationData`** — not `useVisualizationData`; separate mock/empty UX if product wants parity with OGAN-04 wording.
- **Optional gated graph JSON API** (OGAN-03 alternate): still backlog.

## Canonical pointers in repo

| Topic | Path |
|--------|------|
| Capabilities manifest | `src/app/api/capabilities/route.ts` |
| Survey viz GET | `src/app/api/survey/visualization/route.ts` |
| Hook + mock | `src/components/DataVisualization/shared/useVisualizationData.ts` |
| OpenAPI partial | `src/lib/openapi/openapi-document.ts` |
| Agent integration | `docs/AGENT_INTEGRATION.md` |
