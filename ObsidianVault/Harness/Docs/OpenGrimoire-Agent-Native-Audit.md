---
title: "OpenGrimoire — agent-native audit (canonical)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# OpenGrimoire — agent-native audit (canonical)

**Role:** Gap report and **harness-facing scorecard** vs [ARCHITECTURE_REST_CONTRACT.md](./ARCHITECTURE_REST_CONTRACT.md) and [AGENT_INTEGRATION.md](./AGENT_INTEGRATION.md). This file is **not** a substitute for those contracts.

**Last updated:** 2026-04-23 (full eight-explore compound re-pass — see [§ Refresh 2026-04-23](#refresh-2026-04-23))

---

## Related artifacts (GUI + product matrices)

| Artifact | Scope |
|----------|--------|
| [docs/audit/gui-2026-04-16-opengrimoire-survey.md](./audit/gui-2026-04-16-opengrimoire-survey.md) | System 1 — survey / moderation GUI matrix + desk audit |
| [docs/audit/gui-2026-04-16-opengrimoire-data-viz.md](./audit/gui-2026-04-16-opengrimoire-data-viz.md) | System 2 — data viz GUI matrix, dimension action items, architecture strategist synthesis |
| [docs/audit/evidence/og-system2-mcp-wave/BROWSER_REVIEW_REPORT.md](./audit/evidence/og-system2-mcp-wave/BROWSER_REVIEW_REPORT.md) | MCP hardening wave — BrowserReviewReport + Playwright evidence (2026-04-18) |
| [docs/plans/OA_FR_1_SYSTEM1_SURVEY_MODERATION.md](./plans/OA_FR_1_SYSTEM1_SURVEY_MODERATION.md) | OA-FR-1 REQ/AC |
| [docs/plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md](./plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md) | OA-FR-2 REQ/AC |
| [docs/plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md](./plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md) | Post-charter refresh — delta, verify matrix, GUI + critic |

**Harness backlog:** decomposed rows live in [MiscRepos `.cursor/state/pending_tasks.md`](../../MiscRepos/.cursor/state/pending_tasks.md) under **PENDING_OPENGRIMOIRE_AGENT_NATIVE_DECOMPOSED** (**OGAN-09**–**OGAN-10** deferred only); **OGAN-01–OGAN-08** and **OGAN-11–OGAN-17** archived in [completed_tasks.md § PENDING_AGENT_NATIVE](../../../MiscRepos/.cursor/state/completed_tasks.md#pending_agent_native).

---

## Eight-agent scorecard (2026-04-23 compound re-pass)

**Method:** Eight parallel **explore** subagents (compound **agent-native-audit** workflow), one per principle, against OpenGrimoire `C:\Users\Dell\Documents\GitHub\OpenGrimoire` (System 2 slice + shared survey/API). **Synthesis below** merges subagent returns into this file; per-principle caveats unchanged (e.g. dual definitions of “full parity”, Principle 5 percentages are qualitative not computed in code).

### Overall score summary

| Core principle | Score | Approx. % | Status |
|----------------|-------|-----------|--------|
| 1 Action parity | **4 / 15** full UI-equivalent without browser; **7 / 15** raw survey/quote bytes via HTTP | 27% strict · 47% data | ❌ |
| 2 Tools as primitives | **3 / 3** survey viz HTTP surfaces are thin reads; E2E = workflow (CI only) | 100% API | ✅ |
| 3 Context injection | **4 / 8** context types present (re-score: `workflows` + `ui_surfaces` in `GET /api/capabilities` close part of prior gap) | 50% | ❌ |
| 4 Shared workspace | Single SQLite + same GET gates; mitigations (mock banner, `surveyVisualizationFetch` SSOT) | **9 / 10** | ✅ |
| 5 CRUD completeness | HTTP over entities touching viz (qualitative; see §5 table) | ~55% strict · ~80% viz-read-scoped | ⚠️ |
| 6 UI integration | Survey POST / moderation → `dispatchSurveyDataChanged` → hook refetch; still no Playwright “second GET” proof; external writers out-of-band | **7 / 10** | ⚠️ |
| 7 Capability discovery | `GET /api/capabilities` **workflows** + **`ui_surfaces`** + `documentation.non_contractual_ui`; seven-mechanism rubric unchanged | **5 / 7** (~**71%**) | ⚠️ |
| 8 Prompt-native features | **0 / 8** viz behaviors defined as LLM prompts (all CODE) | 0% prompt | ⚠️ (expected for code-first viz) |

**Blended agent-native posture (this slice): ~58%** if principle 8 counts as neutral 50%; **lower** if prompt-native is mandatory product doctrine.

> **Note (2026-04-17 refresh):** Principles **6** and **7** were spot-audited after `18111c9`; see [OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md](./plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md). **2026-04-23:** Full eight-explore re-pass updated **§3**, **§4**, **§6** numeric rows and reconciled Principle 6 narrative vs table.

**Status legend:** ✅ ≈ 80%+ · ⚠️ roughly 50–79% or structural tradeoff · ❌ below 50% or blocking for that principle.

---

### 1 — Action parity (explore re-pass 2026-04-23)

| User action | Agent without browser |
|-------------|------------------------|
| `GET /api/survey/visualization?all=1`, `GET /api/survey/approved-qualities` | **Full** (same gate family as UI) |
| Constellation **rows** via `?all=0&showTestData=` | **Full** |
| Alluvial/Chord tab, auto-play, theme, admin color prefs, Three camera/modes | **Browser only** |
| `/test-chord` mock chord | **Browser only** |

**Score:** **4 / 15** actions with full non-UI parity for **entire visible outcome**; **7 / 15** with **data byte** parity — **unchanged** vs 2026-04-16; re-pass confirmed `visualization/route.ts` query semantics, `surveyVisualizationFetch.ts` SSOT, `middleware.ts` `/test*` gating, no new HTTP graph or prefs APIs.

**Recommendations (abridged):** Optional **viz bundle GET** (rows + optional `processVisualizationData` output); extend OpenAPI bodies; persist operator prefs via API if agents must set them (**OGAN-09** still deferred).

---

### 2 — Tools as primitives (explore re-pass 2026-04-23)

Executable viz-related capabilities in-tree are **`GET` route handlers** + **`GET /api/capabilities`** — each is a **primitive** read. **No** first-party MCP server in this repo; [AGENT_TOOL_MANIFEST.md](./AGENT_TOOL_MANIFEST.md) maps to HTTP. Playwright specs are **workflow** (appropriate for CI, not agent tools).

**Score:** **N/A** for MCP count; **100%** of in-repo **HTTP tools** touching viz are primitive-shaped.

**Risk (remediated for in-repo links):** ~~Stale docs pointing at missing `mcp-server/` paths~~ — REQ-4 / engineering plan links now point to [AGENT_TOOL_MANIFEST.md](./AGENT_TOOL_MANIFEST.md); keep manifests aligned when adding harness MCP docs.

---

### 3 — Context injection (explore re-pass 2026-04-23)

Dynamic LLM runtime injection: **no** (explicit non-goal). **Partial:** `GET /api/capabilities` (now **`workflows[]`**, **`ui_surfaces[]`**, `auth_env_hints`, `documentation` — closes part of the old “UI routes in capabilities” gap), static docs, DOM `data-region` / `data-usage-hint`, `AGENT_TOOL_MANIFEST.md`. **Still missing:** single JSON “context bundle” for dual-stack + query semantics; **no** in-repo `.cursor/` rules for viz; no merged brain-map + alignment + survey one-shot.

**Score:** **4 / 8** ≈ **50%** (revised **+1** vs 2026-04-16 for machine-readable `ui_surfaces` / `workflows` on the capabilities spine).

---

### 4 — Shared workspace (explore re-pass 2026-04-23)

Single **`OPENGRIMOIRE_DB_PATH`** SQLite; user and gated agent hit same **`getVisualizationData`** + **`checkSurveyReadGate`**. **Anti-patterns (residual):** client **mock fallback** in `useVisualizationData` (banner mitigates “silent” on main surfaces); **`?all=1`** still mixes test+live by design; **`loadSurveyData`** in `dataAdapter.ts` unused but revival risk; **`NODE_ENV !== 'production'`** skips read gate (documented in [SURVEY_READ_GATING_RUNBOOK.md](./admin/SURVEY_READ_GATING_RUNBOOK.md)).

**Score:** **9 / 10** (~**90%**) — revised **+0.5** vs 2026-04-16 for shipped mock-banner + `surveyVisualizationFetch` clarity; not 10/10 while `all=1` cohort semantics and env-based gate bypass remain.

---

### 5 — CRUD completeness (explore re-pass 2026-04-23)

| Entity | Agent-relevant HTTP |
|--------|---------------------|
| Survey response | **C** POST; **R** bulk viz (no public by-id read); **U** partial via admin moderation; **D** none |
| Moderation | **R/U** via admin session; first PATCH upserts |
| Approved quotes | **R** only (derived) |

**Score:** **~55%** strict full CRUD; **~80%** if scoped to “viz is read-heavy”.

---

### 6 — UI integration (explore re-pass 2026-04-23)

`useVisualizationData` and `useApprovedQuotes` refetch when `refreshToken` increments; both register `window` listener for **`OPENGRIMOIRE_SURVEY_DATA_CHANGED`** via `dispatchSurveyDataChanged` from `useSyncSessionForm` (POST success), `AdminPanel` (moderation PATCH / focus / refresh), per [AGENT_INTEGRATION.md](./AGENT_INTEGRATION.md). **No** poll/SSE for unrelated writers — external SQLite mutators must dispatch the same event or reload.

**Score:** **7 / 10** (~**70%**) — revised **+1** vs table-as-of-2026-04-22 to match code strength and prior “revised upward” note; **remaining:** Playwright proof of second `GET` after event; no push for out-of-process writers.

---

### 7 — Capability discovery (explore re-pass 2026-04-23)

Mechanisms: onboarding **partial**; help docs **strong**; UI hints **partial** (good on `DataVisualization`); ApiDiscoveryMirror **no self-describe** by design; suggested actions **partial**; empty states **partial**; slash commands **no**. **`GET /api/capabilities`** includes **`workflows[]`**, **`ui_surfaces[]`**, **`documentation.non_contractual_ui`**, `auth_env_hints`, and self-listing route — **spine improved** vs 2026-04-16, but the seven-mechanism rubric still has two fixed **no** rows.

**Score:** **5 / 7** (~**71%**) — headline **unchanged**; content of `capabilities/route.ts` richer (no regression).

---

### 8 — Prompt-native features (explore re-pass 2026-04-23)

Alluvial/Chord/constellation lab: **CODE** (React + D3/Three). **0 / 8** rows classified as **PROMPT**-defined.

**Score:** **0%** prompt-native — **appropriate** for this product slice unless the roadmap adds a JSON/spec → renderer layer.

---

### Top 10 recommendations (by impact, deduped)

| Priority | Action | Principle |
|----------|--------|-------------|
| P1 | **Refetch** path for viz + quotes after survey POST / moderation — **shipped** via `OPENGRIMOIRE_SURVEY_DATA_CHANGED` listeners (`survey-post` on POST success; `moderation-patch` on admin PATCH success, 2026-04-18); **remaining:** Playwright proof of second `GET` + external-writer dispatch doc. | UI integration |
| P2 | Extend **`GET /api/capabilities`** with `workflows` / `ui_surfaces` for `/visualization`, `/constellation`, query semantics (`all` vs `showTestData`). | **Shipped (2026-04-19):** `ui_surfaces[]` + workflow `api` string; matrix row in `ARCHITECTURE_REST_CONTRACT.md`; `e2e/capabilities.spec.ts`. |
| P3 | Optional **GET** returning rows + optional **precomputed graph** for constellation mode (or document “must run `processVisualizationData` locally”). | **Doc path shipped (2026-04-19):** `AGENT_INTEGRATION.md` § Survey graph JSON; optional API remains backlog if product asks. |
| P4 | **Banner** when `isMockData` / empty API — kill silent mock confusion. | **Shipped (2026-04-19):** `/visualization/alluvial` + copy tweak + `e2e/visualization-mock-banner.spec.ts` (main `/visualization` already had banner). |
| P5 | **OpenAPI** response schemas for visualization + approved-qualities bodies. | **Shipped (2026-04-19):** `openapi-document.ts` `components.schemas` + `e2e/openapi.spec.ts`. |
| P6 | **Single client module** for visualization fetch query shapes (prevent `?all=1` drift). | **Shipped (2026-04-19):** `surveyVisualizationFetch.ts`; hook + Zustand wrapper + `export.ts`. |
| P7 | **Archive or fix** root `## Master System Prompt*` file if still Supabase-stale. | **Shipped (2026-04-19):** archived under `docs/archive/master-system-prompt-dataviz-legacy.md`; root artifact removed. |
| P8 | Mark **`/test*`** explicitly non-contractual in capabilities or agent docs. | **Shipped (2026-04-19):** `AGENT_INTEGRATION.md` § Dev / mock UI routes; `GET /api/capabilities` `documentation.non_contractual_ui`. |
| P9 | **Persist** theme/autoplay/color prefs via authenticated API if operators need agent parity. | **Deferred** — product scope; no API in this slice ([pending_tasks OGAN-09](../../../MiscRepos/.cursor/state/pending_tasks.md)). |
| P10 | If prompt-native ever required: **versioned chart spec JSON** + thin renderer over existing D3. | **Deferred** — roadmap-only unless product commits ([pending_tasks OGAN-10](../../../MiscRepos/.cursor/state/pending_tasks.md)). |
| P11 | **Survey POST bootstrap** threat model + hardening backlog (doc-only, 2026-04-22). | **Shipped:** [SURVEY_POST_BOOTSTRAP_THREAT_MODEL.md](./security/SURVEY_POST_BOOTSTRAP_THREAT_MODEL.md) — **OGSEC-07**; complements rate limits + Turnstile story. |

---

### What is working well

1. **Thin HTTP primitives** for PII survey reads with a single gate implementation.  
2. **Single SQLite SSOT** for persisted survey data used by viz APIs.  
3. **`GET /api/capabilities` + AGENT_INTEGRATION** as the discovery spine for external agents.  
4. **DOM contract** (`data-region`, `data-testid`, `vizLayoutIds`) for browser automation.  
5. **Code-first D3/Three** — clear ownership; no fake “LLM drives layout” story.

---

## Refresh 2026-04-17 (integration audit)

**Trigger:** [OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md](./plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md) — post–OA-FR-SCOPE delta (`18111c9` and parents). **Mechanical verification:** `npm run verify` PASS; `npm run test:e2e` **34 passed**, **2 skipped** with Playwright `webServer`. **Principle deltas:** **#6 UI integration** and **#7 Capability discovery** scores raised after code/doc review (`useVisualizationData` / `useApprovedQuotes` event listeners; `CAPABILITIES.workflows`). Other principles unchanged vs 2026-04-16 subagent synthesis **until** [§ Refresh 2026-04-23](#refresh-2026-04-23), which re-scored **#3**, **#4**, **#6** again from eight **explore** returns.

---

## Refresh 2026-04-22 (OG-AUDIT-01 — doc + security hygiene; **no** full eight-explore re-run)

**Trigger:** [gui-2026-04-16-opengrimoire-data-viz.md](./audit/gui-2026-04-16-opengrimoire-data-viz.md) § Post-implementation checklist — “substantial survey or visualization path changes” and refresh this scorecard. **This pass:** security and survey **documentation** plus validation hardening landed in-repo (**OGSEC-01–07** family: trusted client IP for rate limits, `answers` cap, moderation `notes` cap, survey read runbook + `NODE_ENV` / E2E runbook, **bootstrap threat model** [SURVEY_POST_BOOTSTRAP_THREAT_MODEL.md](./security/SURVEY_POST_BOOTSTRAP_THREAT_MODEL.md)); cross-links in `AGENT_INTEGRATION`, `OPERATIONAL_TRADEOFFS`, `SYNC_SESSION_HANDOFF`, `PUBLIC_SURFACE_AUDIT`, route JSDoc.

**What did *not* run:** The **compound agent-native-audit** workflow (eight parallel **explore** subagents) was **not** re-executed. **As of this 2026-04-22 publish:** numeric scorecard rows matched 2026-04-19. **Superseded (2026-04-23):** See [§ Refresh 2026-04-23](#refresh-2026-04-23) — full eight-explore re-pass updated Principles **3**, **4**, and **6** (and blended %) in the table and body §§3–6.

**Mechanical verification (editorial):** `npm test` (Vitest) expected PASS on branch with these merges; operators should run `npm run verify` before release as usual.

**Operator follow-up:** When the next **material** visualization or survey **contract** change ships, either (a) schedule a full eight-agent **agent-native-audit** re-run and rescale the table, or (b) append another dated **Refresh** subsection here with honest scope (doc-only vs subagent synthesis).

---

## Refresh 2026-04-23

**Full eight-explore compound re-pass.** **Trigger:** Operator pass — **full** compound **agent-native-audit** rescoring (eight parallel **explore** subagents, one per [ARCHITECTURE_REST_CONTRACT.md](./ARCHITECTURE_REST_CONTRACT.md) agent-native principle), merged into this file as the canonical harness scorecard for the System 2 + shared survey slice.

**Scope:** Read-only codebase reconnaissance + doc synthesis (no application code changes in this pass). **Not claimed:** fresh Playwright counts or `npm run verify` solely *because* of this doc edit — run before release as always.

**Score deltas vs 2026-04-22 table (doc-only refresh):**

| Principle | Before (as left 2026-04-22) | After (2026-04-23) |
|-----------|------------------------------|---------------------|
| 3 Context injection | **3 / 8** (~38%) | **4 / 8** (~50%) — `workflows` + `ui_surfaces` on `GET /api/capabilities` count toward machine-readable context |
| 4 Shared workspace | **8.5 / 10** | **9 / 10** — mock banner + `surveyVisualizationFetch` SSOT reduce silent-divergence risk; residual `all=1` mix + env gate bypass keep it below 10 |
| 6 UI integration | **6 / 10** | **7 / 10** — align narrative with shipped `dispatchSurveyDataChanged` + hook listeners; still missing second-GET Playwright proof + external-writer story |
| 1, 2, 5, 7, 8 | unchanged | unchanged |

**Blended posture:** ~**57%** → ~**58%** (same neutral handling of Principle 8 as the summary table note).

**Supersedes for numbers:** The 2026-04-22 refresh remains the audit trail for **OGSEC-01–07** / **OG-AUDIT-01** documentation scope; use **this** refresh for **scorecard percentages** and Principle **3 / 4 / 6** subsection text.

---

## OGAN backlog — closure policy (2026-04-18)

**AN1** (MiscRepos [pending_tasks.md § PENDING_AGENT_NATIVE](../../../MiscRepos/.cursor/state/pending_tasks.md)) closes only when each **OGAN-*** row is **implemented**, **waived** (explicit product decision + date), or **deferred** with owner. This table is the working disposition for the **compound agent-native-audit** Option B (no full eight-agent re-run this pass).

| ID | Default disposition | Notes |
|----|---------------------|--------|
| OGAN-01 | **Done (2026-04-18)** | In-app: POST + PATCH dispatch `opengrimoire-survey-data-changed`; viz + approved-quotes hooks refetch. **Remaining:** Playwright “second GET” proof ([OPENGRIMOIRE_FULL_REVIEW_REFRESH](./plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md) checklist). |
| OGAN-02 | **Done (2026-04-19)** | `ui_surfaces[]` + workflow updates + contract row + capabilities e2e — see [completed_tasks.md § PENDING_AGENT_NATIVE](../../../MiscRepos/.cursor/state/completed_tasks.md). |
| OGAN-03 | **Done (2026-04-19)** | Doc-first closure: `AGENT_INTEGRATION.md` § Survey graph JSON + capabilities `agent_note` pointers; no graph bundle API. |
| OGAN-04 | **Done (2026-04-19)** | Mock banner on `/visualization/alluvial`, copy, Playwright — see completed_tasks. |
| OGAN-05 | **Done (2026-04-19)** | OpenAPI schemas for survey read GETs + openapi e2e — see completed_tasks. |
| OGAN-06 | **Done (2026-04-19)** | `surveyVisualizationFetch.ts` SSOT — see completed_tasks. |
| OGAN-07 | **Done (2026-04-19)** | Root Master System Prompt archived + deleted — see completed_tasks. |
| OGAN-08 | **Done (2026-04-19)** | `AGENT_INTEGRATION` + capabilities `documentation.non_contractual_ui` — see completed_tasks. |
| OGAN-09 | **Defer** | Persisted viz prefs — product scope (status `deferred` in pending_tasks). |
| OGAN-10 | **Defer** | Prompt-native chart spec — roadmap-only (status `deferred` in pending_tasks). |
| OGAN-11 | **Done (2026-04-19)** | Manifest + sibling doc links — see completed_tasks. |
| OGAN-12 | **Done (2026-04-19)** | ConstellationView + visualizationStore + viz index logging — see completed_tasks; diagram-level F4 may remain. |
| OGAN-13 | **Done (2026-04-19)** | `NavigationDots` `/visualization` + `/constellation` only — see completed_tasks. |
| OGAN-14 | **Done (2026-04-19)** | Removed orphan `DataVisualization/Constellation/` view — see completed_tasks. |
| OGAN-15 | **Done (2026-04-19)** | `e2e/visualization-constellation-a11y.spec.ts` — see completed_tasks; `canvas` excluded. |
| OGAN-16 | **Done (2026-04-19)** | `e2e/visualization-constellation-network-shape.spec.ts` — see completed_tasks. |
| OGAN-17 | **Done (2026-04-19)** | `docs/agent/PLAYWRIGHT_VIZ_HARNESS_SELECTORS.md` + OA-FR-2 / AGENT_INTEGRATION links — see completed_tasks. |

**Wave 10 note:** MiscRepos **OG-GUI-*** (System 1 GUI release) is **closed** 2026-04-18 — see [gui-2026-04-16-opengrimoire-survey.md](./audit/gui-2026-04-16-opengrimoire-survey.md) § Flow evidence. **AN1** remains **pending** until the table above is executed or formally waived row-by-row.

**Harness status (2026-04-21):** MiscRepos [**AN1** / **OG-PR-4** rows](../../../MiscRepos/.cursor/state/pending_tasks.md#pending_agent_native) stay **`pending`** until the operator sets **AN1** to **`done`** and runs **`split_done_tasks_to_completed.py`**, or documents a formal **waive**, and until **OG-PR-4** (compound **`/ce-review`** on the PR branch, if required) is satisfied per policy. Narrative read-only review on merged **`master`** and this cross-link are recorded in [`CE_REVIEW_DEFERRAL.md`](./audit/evidence/og-system2-mcp-wave/CE_REVIEW_DEFERRAL.md) § **OG-PR-4 status (2026-04-21)**.

**Security + audit extras:** Labeled **OGSEC-***, **OG-AUDIT-***, **OG-DV-***, **OG-GUI-AUDIT-*** rows from GUI/security audits live in MiscRepos [pending_tasks.md § PENDING_OPENGRIMOIRE_GUI_AUDIT_FOLLOWUPS](../../../MiscRepos/.cursor/state/pending_tasks.md#pending_opengrimoire_gui_audit_followups) (implement or `done` + `split_done_tasks_to_completed.py` independently of **AN1** unless tied to an **OGAN-*** closure). **Operator observability hub:** **OG-OH-*** (internal monitoring / reflections / AI ops charter) lives in [pending_tasks.md § PENDING_OPENGRIMOIRE_OBSERVABILITY_HUB](../../../MiscRepos/.cursor/state/pending_tasks.md#pending_opengrimoire_observability_hub).

---

## Scoped pass — MCP hardening wave (2026-04-18)

**Scope:** `src/app/**` and `src/app/api/**` (shared types only where referenced by routes). **Principle exercised:** **1 — Action parity** (survey + viz read path vs UI). **Evidence:** Playwright `e2e/visualization.spec.ts` + `e2e/test-routes.spec.ts` **7/7 passed** same day; GUI audit BrowserReviewSpec in [gui-2026-04-16-opengrimoire-data-viz.md](./audit/gui-2026-04-16-opengrimoire-data-viz.md).

### Action parity (System 2 + shared survey reads)

| UI / human outcome | HTTP / capability surface | Parity |
|--------------------|---------------------------|--------|
| Main viz cohort data | `GET /api/survey/visualization` | **Data:** full via query params; **rendered** D3/Three outcome browser-only (**OGAN-03**) |
| Approved header quotes | `GET /api/survey/approved-qualities` | **Data:** full |
| Capability discovery | `GET /api/capabilities` incl. `workflows` + **`ui_surfaces`** | **Discovery:** **shipped** for viz/constellation query mapping (**OGAN-02**, 2026-04-19) |
| Constellation rows | same visualization route family with `all=0` + `showTestData` | **Data:** full; **camera/UI** browser-only |
| Operator probes / admin | `/api/admin/*`, `/api/operator-probes/*` | Out of System 2 slice; parity not rescored here |

**Harness docs (MiscRepos):** [MCP_CAPABILITY_MAP.md](../../../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md) (which MCP tools may touch OG-facing data) · [ENTITY_CRUD_MATRIX.md](../../../MiscRepos/local-proto/docs/ENTITY_CRUD_MATRIX.md) (entity × MCP × human). **Follow-ups:** same **OGAN-*** / **OG-GUI-AUDIT-*** rows as § OGAN backlog above; **MCP wave** hygiene does not close AN1 by itself.

---

## References

- [PUBLIC_SURFACE_AUDIT.md](./security/PUBLIC_SURFACE_AUDIT.md)
- [MiscRepos GUI audit portfolio index](../../MiscRepos/docs/audit/GUI_AUDIT_PORTFOLIO_INDEX.md)
- [SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md](./audit/SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md) — Wave 10 adjunct; maps residual risks to **OGAN-12** and suggested **OGAN-SEC-*** IDs (bootstrap finding #8 → [SURVEY_POST_BOOTSTRAP_THREAT_MODEL.md](./security/SURVEY_POST_BOOTSTRAP_THREAT_MODEL.md))
