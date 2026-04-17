---
title: "OpenGrimoire — GUI + agent-native audit (System 2 data visualization)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# OpenGrimoire — GUI + agent-native audit (System 2 data visualization)

**Date:** 2026-04-16  
**Scope:** Data visualization surfaces (Alluvial/Chord, quotes, constellation, test routes), REST reads, harness/agent assumptions.  
**Normative traceability:** [OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md](../plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md) · [OA_FR_1_SYSTEM1_SURVEY_MODERATION.md](../plans/OA_FR_1_SYSTEM1_SURVEY_MODERATION.md) (read gates)  
**Critic / debate:** Structural critic + dialectic revision on **2026-04-17** (§ Critic revision log). **MiscRepos `/debate` gate:** satisfied for this file on **2026-04-17** (§ MiscRepos /debate); re-run if the audit or product surface changes materially.

---

## AuditorSpec

- **App / repo:** OpenGrimoire (`C:/Users/Dell/Documents/GitHub/OpenGrimoire`)
- **Branch / PR:** (not pinned)
- **Environment:** local dev primary; production gate checks optional

- **Base URL:** `http://localhost:3001` (Playwright default per `playwright.config.ts`)

- **Critical routes:** `/visualization`, `/visualization/dark`, `/visualization/alluvial`, `/constellation`, `/test`, `/test-chord`, `/test-context`, `/test-sqlite`

- **Top 3 human jobs**
  1. **Interpret cohorts** — see Alluvial or Chord without misleading empty states when DB is empty (mock fallback).
  2. **Trust the display** — approved quotes in header reflect moderation, not raw survey.
  3. **Operate demos safely** — prod: survey reads gated; dev-only test routes blocked unless `OPENGRIMOIRE_ALLOW_TEST_ROUTES`.

- **CI / verify targets**
  - Lint / typecheck: `npm run lint`, `npm run build` (or repo-standard scripts from `package.json`)
  - E2E: `npx playwright test e2e/visualization.spec.ts e2e/test-routes.spec.ts`
  - Contract: `GET /api/capabilities`, `docs/api/ROUTE_INDEX.json`, OpenAPI doc in repo
  - A11y / visual: no dedicated OG workflow at audit time; manual + optional axe on `/visualization`

- **Existing audit doc:** [gui-2026-04-16-opengrimoire-survey.md](./gui-2026-04-16-opengrimoire-survey.md) (System 1)

- **Parity / capability docs:** [AGENT_INTEGRATION.md](../AGENT_INTEGRATION.md) · [ARCHITECTURE_REST_CONTRACT.md](../ARCHITECTURE_REST_CONTRACT.md) · `src/app/api/capabilities/route.ts`

- **Notes:** Two visualization stacks (`DataVisualization` vs `components/visualization` + Zustand); `?all=1` vs `?all=0` + `showTestData` must not be conflated in harnesses.

---

## Product scope (concise)

| ID | Requirement | Source |
|----|-------------|--------|
| P2.1 | Primary viz pages load survey-backed diagrams or documented mock fallback. | OA-FR-2 REQ-S2.1 |
| P2.2 | Header quotes only from **approved** `unique_quality`. | OA-FR-2 REQ-S2.2 |
| P2.3 | Survey GETs share production read gate. | OA-FR-1 / OA-FR-2 REQ-S2.3 |
| P2.4 | Debug logging does not leak PII in default dev. | PUBLIC_SURFACE_AUDIT F1/F4 |
| P2.5 | Test routes are middleware-gated in production. | `middleware.ts` |

---

## GUI dimension matrix (human audit)

| # | Dimension | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Task success | **PARTIAL** | Diagrams + quotes work when API and DB align; empty DB → mock data with **banner** (`opengrimoire-viz-mock-data-banner`). `NavigationDots` still includes routes without `app/` pages (dead links). |
| 2 | Cognitive load | **PARTIAL** | Two “visualization” mental models (D3 main vs Three constellation vs `/test` fixtures). Header `data-usage-hint` helps agents. |
| 3 | Accessibility | **PARTIAL** | `vizLayoutIds`, tab panel wiring, `data-testid` on diagrams; full WCAG pass not claimed (no axe CI on this slice). |
| 4 | Visual system | **PASS** | Header uses CSS variables (`--opengrimoire-viz-*`); theme via `AppContext`. |
| 5 | A2UI / catalog | **PARTIAL** | `data-region` on header, quote slot, canvas; good for selectors. Legacy `/test` stack less instrumented. |
| 6 | Agent parity | **PARTIAL** | REST + `/api/capabilities` includes **`workflows.cohort_survey_visualization`**; tab/auto-play still browser-only. |

---

## Agent-native architecture (condensed review)

Principles from the **compound agent-native-audit** skill (numeric scorecard: [AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md)). This table is qualitative for **this slice only**.

| Principle | Assessment | Notes |
|-----------|------------|--------|
| 1 Action parity | **Partial** | Human can switch Alluvial/Chord, auto-play, theme; agent achieves same only via UI automation or undocumented client state — survey **data** parity via GET endpoints. |
| 2 Tools as primitives | **N/A / OK** | No OG-specific agent tools in-repo; REST routes are the primitives. |
| 3 Context injection | **N/A** | Not applicable to standalone OG UI. |
| 4 Shared workspace | **Pass** | Agents and users hit same SQLite-backed APIs (when gate allows). |
| 5 CRUD completeness | **N/A** | Viz is read-heavy; moderation CRUD is System 1. |
| 6 UI integration | **Partial** | Main `/visualization` refetches on `opengrimoire-survey-data-changed` after moderation / survey POST ([AGENT_INTEGRATION.md](../AGENT_INTEGRATION.md)); no SSE; constellation / Zustand path unchanged. |
| 7 Capability discovery | **Pass** | `GET /api/capabilities` **workflows.cohort_survey_visualization** + OA-FR-2 doc. |
| 8 Prompt-native features | **N/A** | Viz is code-first D3/Three. |

**Overall:** acceptable for a read-only analytics UI; **risk** is automation assuming a single component stack (see architecture strategist).

---

## Architecture strategist — synthesis

**Dual stack:** Short-term seam (D3 survey viz vs Three + Zustand graph) is defensible; **debt** is duplicate naming (`ConstellationView` × 2), two HTTP query shapes for one API, and an **orphan** [`DataVisualization/Constellation/ConstellationView.tsx`](../../src/components/DataVisualization/Constellation/ConstellationView.tsx) (uses `useVisualizationData` but **no** App Router parent — live `/constellation` imports [`visualization/ConstellationView`](../../src/components/visualization/ConstellationView.tsx)).

**Biggest agent/harness risk:** False-green when selectors or network assumptions from `/visualization` are applied to `/constellation` or `/test` (different data path and DOM).

**North star (6–12 months):** One typed survey-read client module; one canonical constellation implementation; legacy Three behind a clearly named adapter until removed or formally supported.

---

## Automation gaps

| Layer | OpenGrimoire System 2 |
|-------|------------------------|
| Contract | Capabilities + OpenAPI exist; **no** CI in-repo at audit time enforcing route↔OpenAPI drift for OG alone. |
| E2E | `visualization.spec.ts`, `test-routes.spec.ts` — good smoke; **no** assertion that `/constellation` uses `?all=0` + `showTestData` vs `/visualization` `?all=1`. |
| A11y | Manual / optional; not wired as merge gate for viz routes. |

---

## Dimension action items

### 1 — Task success

- [ ] Add E2E or smoke: `NavigationDots` targets either get real `app/` pages or are removed from shipped UI.
- [x] When mock fallback activates, show non-blocking banner (`MockSurveyDataBanner`, `data-testid="opengrimoire-viz-mock-data-banner"`).

### 2 — Cognitive load

- [ ] In admin or docs, one diagram: “Which page uses which stack” (D3 vs Three vs fixtures).
- [ ] Rename or namespace exports so `ConstellationView` search resolves to the live file first.

### 3 — Accessibility

- [ ] Run axe-playwright (or equivalent) on `/visualization` + `/constellation`; file issues for focus traps in Three canvas if any.

### 4 — Visual system

- [ ] Audit `DataVisualization` for stray hex outside tokens; align with `--opengrimoire-viz-*` where missing.

### 5 — A2UI / catalog

- [ ] Extend `data-region` / `data-testid` to `/constellation` loading shell and Zustand-driven controls used in demos.
- [ ] Document `data-usage-hint` on header in AGENT_INTEGRATION or OA-FR-2 appendix.

### 6 — Agent parity

- [x] Add **`workflows`** entry **`cohort_survey_visualization`** plus refresh contract on `GET /api/capabilities` (see [`src/app/api/capabilities/route.ts`](../../src/app/api/capabilities/route.ts)); prod headers remain in ARCHITECTURE / AGENT_INTEGRATION.
- [ ] Optional: document Playwright selectors for tab + auto-play for external agents (link from OA-FR-2 verification).

---

## Critic revision log

| When | Delta | Reason |
|------|-------|--------|
| 2026-04-17 | +2 completeness, +1 correctness | Critic: stale “UI integration Pass” vs AGENT_NATIVE; header still said critic not run; dimension-1 evidence omitted mock banner; brittle absolute link to plugin skill path. |
| 2026-04-17 | +1 completeness | MiscRepos `/debate`: persisted critic JSON + agreement table; marked release-gate checklist row for `/debate`. |

## Post-implementation process checklist (release gate)

- [x] Run MiscRepos **`/debate`** on this audit file (critic domain **`docs`**) per **gui-human-audit** before treating the GUI audit as release-closing; attach critic JSON summary or a short revision subsection (no secrets). _(Done 2026-04-17 — see § MiscRepos /debate.)_
- [ ] After substantial OpenGrimoire changes to survey or visualization paths, re-run the **compound agent-native-audit** eight-explore workflow and refresh scores in [`AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md`](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md).
- [ ] When importing **community Cursor rules or skills**, apply the **security-audit-rules** checklist to those new files only.

---

## Follow-ups (cross-cutting)

- [ ] **Single client module** for `GET /api/survey/visualization` query shapes (`all` + `showTestData`) — architecture strategist #1.
- [ ] **Delete or quarantine** orphan `DataVisualization/Constellation/` or merge into live route — strategist #2.
- [ ] **Gate or remove** hot-path `console.log` in `visualization/ConstellationView.tsx` and related store — PUBLIC_SURFACE_AUDIT F4 spirit.

---

## Agent-native eight-agent scorecard (canonical)

The full **eight-agent explore scorecard** (2026-04-16) — overall table, per-principle detail, top-10 recommendations, strengths — lives in **[`AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md`](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md)**. Prefer that file for **AN1** closure citations and to avoid duplicate edits.

---

## MiscRepos `/debate` (2026-04-17)

**Artifact:** this file · **Domain:** `docs` · **Command:** [MiscRepos `.cursor/commands/debate.md`](../../../MiscRepos/.cursor/commands/debate.md) (equivalent flow in Cursor agent session).

### Round 1 — Critic (independent second voice)

```json
{
  "pass": true,
  "threshold": 18,
  "intent_alignment": 5,
  "safety": 5,
  "correctness": 5,
  "completeness": 4,
  "minimality": 4,
  "issues": [
    {
      "type": "completeness",
      "detail": "Release checklist still asked for /debate while header implied prior critic only; no persisted /debate JSON on artifact until this section.",
      "evidence": "Former § Post-implementation checklist line 'Run MiscRepos /debate' unchecked vs header line 7"
    },
    {
      "type": "minimality",
      "detail": "Automation gaps table retains 'at audit time' without stating whether CI was added later—minor drift risk.",
      "evidence": "§ Automation gaps rows still say 'at audit time'"
    }
  ],
  "fixes": [
    {
      "action": "Mark /debate checklist complete and append this section with JSON + summary.",
      "detail": "Closes gui-human-audit gate for second voice on this revision."
    },
    {
      "action": "Optional follow-up",
      "detail": "Revisit Automation gaps when verify:* scripts change; not blocking pass."
    }
  ]
}
```

**Summary:** Pass. Agreement: audit now matches implemented survey refetch + capabilities workflow + mock banner; remaining work is **NavigationDots**, **constellation path**, **F4 logs**, and **optional** eight-agent score refresh—not contradictions within this doc.

### Agreement / remaining disputes

| Agreed | Still open (track elsewhere) |
|--------|--------------------------------|
| Dual-stack risk and harness false-greens are clearly stated | `NavigationDots` dead routes; orphan `DataVisualization/Constellation/` |
| UI integration row reflects CustomEvent + AGENT_INTEGRATION | Axe CI; constellation vs `?all=1` E2E assertion |
| Dimension action items stay actionable | Playwright selector appendix (dimension 6 optional row) |

### Round 2 — Critic (post-revision)

```json
{
  "pass": true,
  "threshold": 18,
  "intent_alignment": 5,
  "safety": 5,
  "correctness": 5,
  "completeness": 5,
  "minimality": 4,
  "issues": [],
  "fixes": []
}
```

**Summary:** Pass; `/debate` checklist closure and persisted transcript resolve round-1 completeness gap.

---

## References

- [AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md)
- [OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md](../plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md)
- [PUBLIC_SURFACE_AUDIT.md](../security/PUBLIC_SURFACE_AUDIT.md)
- [MiscRepos GUI audit index](../../../MiscRepos/docs/audit/GUI_AUDIT_PORTFOLIO_INDEX.md)
