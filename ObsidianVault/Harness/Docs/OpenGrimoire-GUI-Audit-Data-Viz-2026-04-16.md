---
title: "OpenGrimoire — GUI + agent-native audit (System 2 data visualization)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# OpenGrimoire — GUI + agent-native audit (System 2 data visualization)

**Date:** 2026-04-16  
**Scope:** Data visualization surfaces (Alluvial/Chord, quotes, constellation, test routes), REST reads, harness/agent assumptions.  
**Normative traceability:** [OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md](../plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md) · [OA_FR_1_SYSTEM1_SURVEY_MODERATION.md](../plans/OA_FR_1_SYSTEM1_SURVEY_MODERATION.md) (read gates)  
**Critic / debate:** Structural critic + dialectic revision on **2026-04-17** (§ Critic revision log). **MiscRepos `/debate` gate:** satisfied for this file on **2026-04-17** (§ MiscRepos /debate); re-run if the audit or product surface changes materially.

---

## AuditorSpec

- **App / repo:** OpenGrimoire (sibling checkout next to MiscRepos / Arc_Forge; no host-specific path in audit text)
- **Branch / PR:** (not pinned)
- **Environment:** local dev primary; production gate checks optional

- **Base URL:** `http://localhost:3001` (Playwright default per `playwright.config.ts`)

- **Critical routes:** `/visualization`, `/visualization/dark`, `/visualization/alluvial`, `/constellation`, `/test`, `/test-chord`, `/test-context`, `/test-sqlite`

- **Top 3 human jobs**
  1. **Interpret cohorts** — see Alluvial or Chord without misleading empty states when DB is empty (mock fallback).
  2. **Trust the display** — approved quotes in header reflect moderation, not raw survey.
  3. **Operate demos safely** — prod: survey reads gated; dev-only test routes blocked unless `OPENGRIMOIRE_ALLOW_TEST_ROUTES`.

- **CI / verify targets**
  - Lint / typecheck / unit: `npm run lint`, `npm run type-check`, `npm run test` (Vitest)
  - Full gate (repo root): `npm run verify` — includes `verify:capabilities`, `verify:openapi`, `verify:route-index`, `verify:moderation-auth`, `verify:admin-panel-a2ui` (shared with System 1)
  - E2E (viz smoke): `npx playwright test e2e/visualization.spec.ts e2e/test-routes.spec.ts`
  - **System 1 a11y gate (2026-04-18):** `npm run test:e2e:a11y` — **does not** visit `/visualization` or `/constellation`; viz a11y remains **OGAN-15** backlog
  - A11y / visual (viz): manual or future axe spec on `/visualization` + `/constellation` (see dimension 3)

- **Existing audit doc:** [gui-2026-04-16-opengrimoire-survey.md](./gui-2026-04-16-opengrimoire-survey.md) (System 1)

- **Parity / capability docs:** [AGENT_INTEGRATION.md](../AGENT_INTEGRATION.md) · [ARCHITECTURE_REST_CONTRACT.md](../ARCHITECTURE_REST_CONTRACT.md) · `src/app/api/capabilities/route.ts`

- **Notes:** Two visualization stacks (`DataVisualization` vs `components/visualization` + Zustand); `?all=1` vs `?all=0` + `showTestData` must not be conflated in harnesses.

---

## BrowserReviewSpec (MCP hardening wave, 2026-04-18)

Aligned with **browser-review-protocol** (three human jobs above → flows).

- **Base URL:** `http://localhost:3001`
- **Route(s):** `/visualization`, `/constellation`, `/visualization/alluvial`, `/test-chord`
- **Auth:** none (local dev); prod/staging not in scope for this desk pass
- **Viewports:** 1280×720 (desktop), 375×667 (mobile) when live browser is used
- **Flows**
  1. Open `/visualization` → **Expected:** page settles; diagram or mock banner present; no uncaught console errors on first paint.
  2. Open `/constellation` → **Expected:** Three view loads or documented empty state; network uses `all=0` semantics per OA-FR-2 (contrast with `/visualization` `?all=1` — **OGAN-16**).
  3. Open `/test-chord` (dev) → **Expected:** mock chord only when test routes allowed; blocked in prod per middleware.
- **Critical screens:** `/visualization` (main D3), `/constellation` (Three + Zustand)

**Executor report:** [evidence/og-system2-mcp-wave/BROWSER_REVIEW_REPORT.md](./evidence/og-system2-mcp-wave/BROWSER_REVIEW_REPORT.md)

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
| 1 | Task success | **PARTIAL** | Diagrams + quotes work when API and DB align; empty DB → mock data with **banner** (`opengrimoire-viz-mock-data-banner`). **`NavigationDots`** was trimmed to real routes (**2026-04-19**, OGAN-13); dimension-1 checklist row below may still be used for **regression** verification. |
| 2 | Cognitive load | **PARTIAL** | Dual stack is real, but **OG-DV-DOC-01 (2026-04-23):** [page × stack table + diagram](#og-dv-doc-01-page-stack) documents routes vs D3 / Three / fixtures; header `data-usage-hint` still required reading for fine-grained agent hints. |
| 3 | Accessibility | **PARTIAL** | `vizLayoutIds`, tab panel wiring, `data-testid` on diagrams; full WCAG pass not claimed (no axe CI on this slice). |
| 4 | Visual system | **PASS** | Header + cohort **shell** use `--opengrimoire-viz-*` tokens (**2026-04-22**, OG-DV-UI-01); D3 categorical palettes remain hex by design. Theme via `AppContext`. |
| 5 | A2UI / catalog | **PARTIAL** | `data-region` / `data-testid` on `/visualization` shell; **`/constellation`** route loading + Three shell + Zustand demo toggle (**2026-04-22**, OG-DV-UI-02). Legacy `/test` stack less instrumented. |
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

**Dual stack:** Short-term seam (D3 survey viz vs Three + Zustand graph) is defensible; **debt** is two HTTP query shapes for one API. ~~Duplicate `ConstellationView` / orphan `DataVisualization/Constellation/`~~ **resolved (2026-04-19–22):** orphan tree removed (**CHANGELOG**); lazy wrapper + single named export (**OG-DV-DOC-02**). Live `/constellation` imports [`visualization/ConstellationView`](../../src/components/visualization/ConstellationView.tsx).

**Biggest agent/harness risk:** False-green when selectors or network assumptions from `/visualization` are applied to `/constellation` or `/test` (different data path and DOM).

**North star (6–12 months):** One typed survey-read client module; one canonical constellation implementation; legacy Three behind a clearly named adapter until removed or formally supported.

<a id="og-dv-doc-01-page-stack"></a>

### Page × rendering stack (OG-DV-DOC-01)

Harness authors should not assume one component tree or one query shape across routes.

| App route | Primary UI stack | Survey / viz data |
|-----------|------------------|-------------------|
| `/visualization` | [`DataVisualization`](../../src/components/DataVisualization) (D3 — Alluvial / Chord tabs) | `GET /api/survey/visualization` (typically `?all=1` cohort view) via [`useVisualizationData`](../../src/components/DataVisualization/shared/useVisualizationData.ts) |
| `/visualization/dark` | Same `DataVisualization` family (theme variant) | Same API family |
| `/visualization/alluvial` | [`AlluvialDiagram`](../../src/components/DataVisualization/AlluvialDiagram.tsx) + provider + mock banner | Same |
| `/constellation` | [`visualization/ConstellationView`](../../src/components/visualization/ConstellationView.tsx) — **Three.js** + Zustand | Same route handler; query semantics **`all=0`** + `showTestData` per OA-FR-2 / **OGAN-16** |
| `/test`, `/test-chord`, `/test-context` | [`components/visualization`](../../src/components/visualization) and route-local demos | Fixtures / mock paths; **middleware** blocks in production unless `OPENGRIMOIRE_ALLOW_TEST_ROUTES` |
| `/test-sqlite` | Minimal page — exercises `fetch` to visualization API | Direct `GET /api/survey/visualization?all=1` from browser |

```mermaid
flowchart LR
  subgraph d3["D3 cohort UI"]
    V["/visualization"]
    VA["/visualization/alluvial"]
    VD["/visualization/dark"]
  end
  subgraph three["Three + Zustand"]
    C["/constellation"]
  end
  subgraph fixtures["Dev / test fixtures"]
    T["/test*"]
  end
  API["GET /api/survey/visualization"]
  V --> API
  VA --> API
  VD --> API
  C --> API
  T -.->|"may bypass or mock"| API
```

---

## Automation gaps

| Layer | OpenGrimoire System 2 (2026-04-18 refresh) |
|-------|------------------------|
| Contract | **`npm run verify`** (OpenGrimoire) enforces capabilities ↔ routes ↔ OpenAPI coverage repo-wide — **not** viz-only, but drift is gated on every PR that runs verify. |
| E2E | `visualization.spec.ts`, `test-routes.spec.ts`, **`visualization-constellation-network-shape.spec.ts`** (OGAN-16 query drift), **`visualization-constellation-a11y.spec.ts`** (OGAN-15 axe shell). |
| A11y | **System 1:** `e2e/sync-session-admin-a11y.spec.ts` + `npm run test:e2e:a11y` (Wave **OG-GUI-04**). **System 2 viz routes:** not in that spec — track **OGAN-15**. |

**Wave boundary:** MiscRepos [Wave 10 — OG GUI release](../../../MiscRepos/local-proto/docs/WAVED_PENDING_TASKS.md) covers **System 1** survey/moderation evidence (`OG-GUI-*`). System 2 GUI debt stays here + **OGAN-*** in [MiscRepos pending_tasks — PENDING_AGENT_NATIVE](../../../MiscRepos/.cursor/state/pending_tasks.md).

---

## Dimension action items

### 1 — Task success

- [ ] Add E2E or smoke: `NavigationDots` targets either get real `app/` pages or are removed from shipped UI.
- [x] When mock fallback activates, show non-blocking banner (`MockSurveyDataBanner`, `data-testid="opengrimoire-viz-mock-data-banner"`).
- [ ] **Maintain:** After changing viz routes or `NavigationDots`, run `npx playwright test e2e/visualization.spec.ts e2e/test-routes.spec.ts` before merge.

### 2 — Cognitive load

- [x] In admin or docs, one diagram: “Which page uses which stack” (D3 vs Three vs fixtures). **Shipped 2026-04-23 (OG-DV-DOC-01):** [§ Page × rendering stack](#og-dv-doc-01-page-stack) above.
- [x] Rename or namespace exports so `ConstellationView` search resolves to the live file first. **Shipped 2026-04-22 (OG-DV-DOC-02):** `ConstellationViewLazy` on [`constellation/page.tsx`](../../src/app/constellation/page.tsx); named export only from [`ConstellationView.tsx`](../../src/components/visualization/ConstellationView.tsx).
- [ ] **Maintain:** When adding a viz surface, update OA-FR-2 or this audit’s “dual stack” note so harness authors do not assume one HTTP shape.

### 3 — Accessibility

- [x] Run axe-playwright on `/visualization` + `/constellation` — [`e2e/visualization-constellation-a11y.spec.ts`](../../e2e/visualization-constellation-a11y.spec.ts) (**OGAN-15**). **`canvas`** (WebGL) is **excluded** from axe; keyboard focus inside the Three scene is still a **product / AT** gap — track with UX if raised.
- [x] **Maintain:** **OG-GUI-04** remains Sync Session + admin; viz uses the dedicated spec above.

### 4 — Visual system

- [x] Audit `DataVisualization` for stray hex outside tokens; align with `--opengrimoire-viz-*` where missing. **Shipped 2026-04-22 (OG-DV-UI-01):** shell chrome (`index`, `VisualizationHeader`, `QuestionSelector`) — not full D3 palette migration.
- [ ] **Maintain:** If product adds Percy/Chromatic for viz pages, mirror the **OG-GUI-06** pattern (`e2e/visual-baselines-og-gui-06.spec.ts`) for stable selectors first.

### 5 — A2UI / catalog

- [x] Extend `data-region` / `data-testid` to `/constellation` loading shell and Zustand-driven controls used in demos. **Shipped 2026-04-22 (OG-DV-UI-02).**
- [x] Document `data-usage-hint` on header in AGENT_INTEGRATION or OA-FR-2 appendix. **Shipped 2026-04-22 (OG-DV-DOC-03).**
- [ ] **Maintain:** New operator-facing components should follow the same `data-region` / non-decorative naming discipline as System 1 **OG-GUI-A2**.

### 6 — Agent parity

- [x] Add **`workflows`** entry **`cohort_survey_visualization`** plus refresh contract on `GET /api/capabilities` (see [`src/app/api/capabilities/route.ts`](../../src/app/api/capabilities/route.ts)); prod headers remain in ARCHITECTURE / AGENT_INTEGRATION.
- [x] Document Playwright selectors for external harnesses — [agent/PLAYWRIGHT_VIZ_HARNESS_SELECTORS.md](../agent/PLAYWRIGHT_VIZ_HARNESS_SELECTORS.md) + OA-FR-2 §4.5 (**OGAN-17**).
- [ ] **Maintain:** On route or query-param changes, update **`GET /api/capabilities`** prose and verify scripts together (**OGAN-02**, **OGAN-05**).

---

## Critic revision log

| When | Delta | Reason |
|------|-------|--------|
| 2026-04-17 | +2 completeness, +1 correctness | Critic: stale “UI integration Pass” vs AGENT_NATIVE; header still said critic not run; dimension-1 evidence omitted mock banner; brittle absolute link to plugin skill path. |
| 2026-04-17 | +1 completeness | MiscRepos `/debate`: persisted critic JSON + agreement table; marked release-gate checklist row for `/debate`. |

## Post-implementation process checklist (release gate)

- [x] Run MiscRepos **`/debate`** on this audit file (critic domain **`docs`**) per **gui-human-audit** before treating the GUI audit as release-closing; attach critic JSON summary or a short revision subsection (no secrets). _(Done 2026-04-17 — see § MiscRepos /debate.)_
- [x] After substantial OpenGrimoire changes to survey or visualization paths, re-run the **compound agent-native-audit** eight-explore workflow and refresh scores in [`AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md`](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md). _(**Done 2026-04-23** — full eight-explore compound re-pass; see that file § **Refresh 2026-04-23**. Prior 2026-04-22 pass was doc-only + OGSEC hygiene — § **Refresh 2026-04-22**.)_
- [ ] **OG-AUDIT-02 — Rules import hygiene:** Before committing **community-sourced** Cursor **rules** or **skills** (anything under `.cursor/rules/`, `.cursor/skills/**/SKILL.md`, `.cursorrules`, or `AGENTS.md`), run the **security-audit-rules** workflow on **only** the added/changed files — not the whole repo. **How:** In Cursor, load the **security-audit-rules** skill (in a typical local-proto harness checkout it lives at **`.cursor/skills/security-audit-rules/SKILL.md`** in the workspace root; compound-engineering installs may expose the same skill under another path — use **Read** on the skill file your workspace actually has). Follow its checklist (red-flag patterns, extended threat model, exit criteria: scanned paths + findings). **Harness row:** [MiscRepos `pending_tasks` § GUI audit followups — **OG-AUDIT-02**](../../../MiscRepos/.cursor/state/pending_tasks.md#pending_opengrimoire_gui_audit_followups).

---

## Follow-ups (cross-cutting)

- [ ] **Single client module** for `GET /api/survey/visualization` query shapes (`all` + `showTestData`) — architecture strategist #1.
- [x] **Delete or quarantine** orphan `DataVisualization/Constellation/` — **done (2026-04-19)** per **CHANGELOG** / **OGAN-14**.
- [x] **Gate or remove** hot-path `console.log` in `visualization/ConstellationView.tsx` and related store — **partial done (2026-04-19)** per **CHANGELOG** / **OGAN-12**; diagram-level F4 may remain (Alluvial/Chord).

---

## Agent-native eight-agent scorecard (canonical)

The full **eight-agent explore scorecard** (last compound merge **2026-04-23**; prior baseline 2026-04-16) — overall table, per-principle detail, top-10 recommendations, strengths — lives in **[`AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md`](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md)**. Prefer that file for **AN1** closure citations and to avoid duplicate edits.

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
