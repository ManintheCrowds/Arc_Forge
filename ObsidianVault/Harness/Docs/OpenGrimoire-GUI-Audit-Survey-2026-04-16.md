---
title: "GUI + agent-native audit — OpenGrimoire System 1 (survey / moderation)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# GUI + agent-native audit — OpenGrimoire System 1 (survey / moderation)

**Date:** 2026-04-16  
**Scope:** Post–OA-FR-1 backlog surfaces: Sync Session (`/operator-intake`, `/survey` redirect), `POST /api/survey`, survey read APIs (`checkSurveyReadGate`), admin moderation APIs + AdminPanel UI, discovery (`GET /api/capabilities`, verify scripts).  
**Repo:** OpenGrimoire (local path varies by clone).

---

## AuditorSpec

- **App / repo:** OpenGrimoire
- **Branch / PR:** ad hoc audit (no single PR)
- **Environment:** local dev (`npm run dev`, default port 3001); E2E via Playwright `webServer`
- **Base URL:** `http://localhost:3001`
- **Critical routes:** `/operator-intake`, `/survey` (redirect), `/login`, `/admin` (moderation), `POST /api/survey`, `GET /api/survey/visualization`, `GET /api/survey/approved-qualities`, `GET /api/admin/moderation-queue`
- **Top 3 human jobs**
  1. Complete Sync Session and submit without dead ends.
  2. Sign in as operator and review / act on moderation queue.
  3. Understand what agents may call vs what requires an operator session (discovery).
- **CI / verify targets**
  - Lint / typecheck: `npm run lint`, `npm run type-check`
  - Unit: `npm run test` (includes `survey-read-gate-logic.test.ts`)
  - E2E: `npm run test:e2e` — `e2e/survey.spec.ts`, `e2e/admin-moderation.spec.ts`, `e2e/capabilities.spec.ts`, `e2e/clarification-queue.spec.ts` (alignment header when secret set); **`e2e/sync-session-admin-a11y.spec.ts`** (axe, OG-GUI-04); Percy visual spec excluded from default run — **`npm run test:e2e:visual`** (OG-GUI-06, requires `PERCY_TOKEN` + `percy exec`)
  - Contract: `npm run verify` (capabilities, openapi, route-index, **`verify:moderation-auth`**)
  - A11y / visual: axe (`npm run test:e2e:a11y`); Percy baselines for intake + admin queue (`npm run test:e2e:visual`; CI when `PERCY_TOKEN` secret set on MiscRepos workflow)
- **Existing audit doc:** this file (first cut)
- **Parity / capability docs:** `src/app/api/capabilities/route.ts`, `docs/ARCHITECTURE_REST_CONTRACT.md`, `docs/plans/OA_FR_1_SYSTEM1_SURVEY_MODERATION.md`, `docs/agent/SYNC_SESSION_HANDOFF.md`
- **Notes:** Playwright sets `ALIGNMENT_CONTEXT_API_SECRET` for clarification + moderation negative tests; moderation routes use **operator session only** (`requireOpenGrimoireAdminRoute`). `checkSurveyReadGate` returns early in non-production before `cookies()` / session verification.

### BrowserReviewSpec (stub — extend before release gate)

| Field | Value |
|-------|--------|
| Base URL | `http://localhost:3001` |
| Auth | Operator: `/login` → password from [`e2e/helpers/e2e-secrets.ts`](../../e2e/helpers/e2e-secrets.ts) (`e2eOpenGrimoireAdminPassword` / `buildPlaywrightWebServerEnv`, default `e2e-test-password`); survey POST unauthenticated |
| Viewports | Desktop 1280×720 minimum; add tablet when UI changes land |
| Flows | (1) `/operator-intake` full submit to success or error banner (2) `/survey` → redirect to `/operator-intake` (3) `/login` → `/admin` moderation panel with queue |
| Evidence to attach | Playwright HTML report path or `npx playwright test …` log; optional screenshots on failure |
| Stable selectors | Prefer `data-testid` from `SyncSessionForm` / admin tests (`e2e/survey.spec.ts`, `e2e/admin-moderation.spec.ts`) |

---

## Flow evidence (this audit pass)

Commands referenced from the authoring session (re-run before release sign-off):

- `npm run verify` (OpenGrimoire root) — lint, typecheck, Vitest, `verify:capabilities`, `verify:openapi`, `verify:route-index`, **`verify:moderation-auth`** — exit **0**.
- **2026-04-18 — Wave 10 post-close revalidation:** `npm run verify` — exit **0** (Vitest **51** passed; ESLint **warnings** only in viz/test components). `npm run test:e2e:a11y` — **2 passed** (`e2e/sync-session-admin-a11y.spec.ts`). `npx playwright test e2e/survey.spec.ts e2e/admin-moderation.spec.ts e2e/capabilities.spec.ts e2e/clarification-queue.spec.ts` — **7 passed**, **2 skipped** (`SURVEY_POST_REQUIRE_TOKEN`). `npm run verify:survey-read-prod` — exit **0** (runs `npm run build` then `next start` profiles deny / public / viz-key / alignment-key on ports 3010–3013). **Build troubleshooting:** if `next build` fails with `Cannot find module for page: /_document`, delete `.next` and rebuild (stale output); do not use `SKIP_BUILD=1` unless `.next` is known-good.
- `npx playwright test e2e/survey.spec.ts e2e/admin-moderation.spec.ts e2e/clarification-queue.spec.ts e2e/auth-alignment-constellation.spec.ts e2e/capabilities.spec.ts` — **9 passed**, **2 skipped** (`SURVEY_POST_REQUIRE_TOKEN` gated tests).
- **2026-04-17 — OG-GUI-01 (BrowserReviewSpec + evidence):** `npm run verify` — exit **0**. `npx playwright test e2e/survey.spec.ts e2e/admin-moderation.spec.ts e2e/og-gui-01-browser-review-evidence.spec.ts` — **10 passed**, **2 skipped** (survey token gate). HTML report: `playwright-report/index.html`. Human-readable report + PNG + console/network JSON: [`docs/audit/evidence/og-gui-01/BROWSER_REVIEW_REPORT.md`](evidence/og-gui-01/BROWSER_REVIEW_REPORT.md).
- **2026-04-18 — OG-GUI-02 (moderation UI E2E):** `npx playwright test e2e/admin-moderation.spec.ts` — **2 passed** (API + UI row `moderation-queue-item-${surveyResponseId}` after `loginAsAdmin` + `GET /api/admin/moderation-queue` 200).
- **2026-04-18 — OG-GUI-03 (survey POST token gate in CI):** MiscRepos [`.github/workflows/opengrimoire_e2e.yml`](../../../MiscRepos/.github/workflows/opengrimoire_e2e.yml) — second step `SURVEY_POST_REQUIRE_TOKEN=true` + `npx playwright test e2e/survey.spec.ts` (full suite unchanged). Local repro: `npm run test:e2e:survey-post-token` (OpenGrimoire root).
- **2026-04-18 — OG-GUI-05 (Sync Session error copy):** `npm run test` — includes Vitest `sync-session-submit-user-message.test.ts` (suite size grows with repo; **51** tests as of 2026-04-18 revalidation). User messages for **401** / **429** (detail + Retry-After), **503**, JSON parse failure, and network-style `fetch` errors in [`useSyncSessionForm`](../../src/lib/hooks/useSyncSessionForm.ts).
- **2026-04-18 — OG-GUI-04 (axe a11y E2E):** `npx playwright test e2e/sync-session-admin-a11y.spec.ts` — **2 passed** (`@axe-core/playwright` on `/operator-intake` after bootstrap token + `/admin` after `loginAsAdmin`; asserts zero violations). Local fast path: `npm run test:e2e:a11y`. UI fixes: [`brand.css`](../../src/styles/brand.css) secondary text contrast; [`Layout.tsx`](../../src/components/Layout.tsx) remove nested `<main>`; [`AdminPanel`](../../src/components/AdminPanel/index.tsx) button contrast.
- **2026-04-18 — OG-GUI-06 (Percy visual baselines):** [`e2e/visual-baselines-og-gui-06.spec.ts`](../../e2e/visual-baselines-og-gui-06.spec.ts) — `npm run test:e2e:visual` (`cross-env PLAYWRIGHT_VISUAL_BASELINES=1 percy exec -- npx playwright test …`). Without `percy exec`, Playwright still runs the file but Percy logs “not running, disabling snapshots”. **CI:** MiscRepos [`.github/workflows/opengrimoire_e2e.yml`](../../../MiscRepos/.github/workflows/opengrimoire_e2e.yml) optional step when `secrets.PERCY_TOKEN` is set; add token in repo Actions secrets, then approve first Percy build for baseline.
- **2026-04-18 — OG-GUI-07 (E2E secrets single source):** `npm run type-check` — exit **0**. `npx playwright test e2e/admin-moderation.spec.ts e2e/clarification-queue.spec.ts` — **3 passed**. Defaults + `buildPlaywrightWebServerEnv()` in [`e2e/helpers/e2e-secrets.ts`](../../e2e/helpers/e2e-secrets.ts); [`playwright.config.ts`](../../playwright.config.ts) imports builder for `webServer.env`.
- **2026-04-18 — OG-GUI-08 (read-gate copy SSOT):** `npm run type-check` + `npm run verify:capabilities` + `npm run test` (**50** passed) + `npx playwright test e2e/capabilities.spec.ts` — **1 passed**. [`survey-read-gate-public-messages.ts`](../../src/lib/survey/survey-read-gate-public-messages.ts); [`survey-read-gate.ts`](../../src/lib/survey/survey-read-gate.ts); [`capabilities/route.ts`](../../src/app/api/capabilities/route.ts); [`ARCHITECTURE_REST_CONTRACT.md`](../../docs/ARCHITECTURE_REST_CONTRACT.md) pointers.

---

## Product-scope (requirements / AC snapshot)

**Requirements**

1. Operators complete Sync Session submit; failures are intelligible.
2. Moderation list + PATCH work only with operator session; alignment automation header does **not** authorize moderation.
3. Production survey reads gated; dev avoids unnecessary cookie/session work on hot path.
4. Machine discovery (capabilities + verify) matches route auth behavior.
5. CI blocks moderation auth drift and exercises core API flows.

**Acceptance criteria (checklist)**

- [x] Unauthenticated `PATCH /api/admin/moderation/:id` → **401** (E2E: `e2e/admin-moderation.spec.ts` — `patchNoCookie` / API flow).
- [x] Valid `x-alignment-context-key`, no session → moderation `PATCH` **401** (E2E with `ALIGNMENT_CONTEXT_API_SECRET` set — `patchAlignmentOnly`).
- [x] Authenticated `GET /api/admin/moderation-queue` → **200**, `items` contains seeded response with non-empty `unique_quality` (E2E + UI row `moderation-queue-item-{id}`).
- [x] Non-production: `checkSurveyReadGate` does not call `cookies()` / `verifyAdminSessionToken` — implementation: early `NODE_ENV !== 'production'` return in [`survey-read-gate.ts`](../../src/lib/survey/survey-read-gate.ts) before `cookies()` (lines 22–24).
- [x] `npm run verify` includes passing **`verify:moderation-auth`**.
- [x] `GET /api/capabilities` moderation routes include `operator_session_only_no_alignment_key` (E2E: `e2e/capabilities.spec.ts`).
- [x] Production `NODE_ENV`: survey read endpoints honor env/header matrix (`verify:survey-read-prod`). **OG-GUI-10 (2026-04-18):** [`scripts/survey-read-gate-prod-smoke.mjs`](../../scripts/survey-read-gate-prod-smoke.mjs).

**Evidence map (AC → artifact)**

| AC | Primary evidence |
|----|-------------------|
| Moderation 401 unauth / alignment-only | `e2e/admin-moderation.spec.ts` (`patchNoCookie`, `patchAlignmentOnly`) |
| Moderation 200 queue + PATCH | Same file + `src/app/api/admin/moderation-queue/route.ts`, `src/app/api/admin/moderation/[responseId]/route.ts` |
| Moderation **UI** row when queue non-empty | `e2e/admin-moderation.spec.ts` (UI test); `AdminPanel` `data-testid=moderation-queue-item-{id}` |
| Read gate dev short-circuit | `src/lib/survey/survey-read-gate.ts` (early return); logic matrix `src/lib/survey/survey-read-gate-logic.test.ts` |
| Read gate production matrix | **OG-GUI-10 (2026-04-18):** `npm run verify:survey-read-prod` — [`scripts/survey-read-gate-prod-smoke.mjs`](../../scripts/survey-read-gate-prod-smoke.mjs); CI [`.github/workflows/survey-visualization-prod-smoke.yml`](../../.github/workflows/survey-visualization-prod-smoke.yml) |
| verify hook | `package.json` scripts `verify`, `verify:moderation-auth`; implementation `scripts/verify-moderation-auth-purity.mjs` (**OG-GUI-09 2026-04-17:** admin moderation `route.ts` glob + ESLint override + Vitest [`verify-moderation-auth-purity.script.test.ts`](../../src/lib/alignment-context/verify-moderation-auth-purity.script.test.ts)) |
| Capabilities substring | `e2e/capabilities.spec.ts`; strings `src/app/api/capabilities/route.ts` |

---

## Dimension matrix

| # | Dimension | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Task success | **PARTIAL** | Multi-step survey E2E + admin-moderation **API** E2E + **UI** row assert after `loginAsAdmin` ([`e2e/admin-moderation.spec.ts`](../../e2e/admin-moderation.spec.ts)); deeper moderation interaction coverage still optional |
| 2 | Cognitive load | **PARTIAL** | Primary flows exist; operator-intake error copy for 401/429/503 / token gate not systematically reviewed |
| 3 | Accessibility | **PASS** | **OG-GUI-04 (2026-04-18):** `e2e/sync-session-admin-a11y.spec.ts` — axe zero violations on `/operator-intake` + `/admin` (see Flow evidence); supporting contrast + landmark fixes in repo |
| 4 | Visual system | **PASS** | **OG-GUI-06 (2026-04-18):** Percy + Playwright — [`e2e/visual-baselines-og-gui-06.spec.ts`](../../e2e/visual-baselines-og-gui-06.spec.ts), [`.percy.yml`](../../.percy.yml), `npm run test:e2e:visual`; CI gated on `PERCY_TOKEN` (see Flow evidence) |
| 5 | A2UI / catalog | **PARTIAL (N/A product today)** | No A2UI catalog until agent-rendered admin (**OA-OG-5**); **OG-GUI-A2 (2026-04-18):** `verify:admin-panel-a2ui` — [`scripts/verify-admin-panel-a2ui-monitor.mjs`](../../scripts/verify-admin-panel-a2ui-monitor.mjs) + [CONTRIBUTING.md](../../CONTRIBUTING.md) § AdminPanel; catalog rows when A2UI ships |
| 6 | Agent parity | **PARTIAL** | Strong: `capabilities` + `verify:moderation-auth` + **OG-GUI-09** ESLint + Vitest smoke; moderation intentionally **excludes** alignment-key bypass — document clearly for harness authors |

---

## Automation vs gaps

| Layer | Present | Gap |
|-------|---------|-----|
| Static | ESLint, `tsc`, **`verify:admin-panel-a2ui`** (OG-GUI-A2 decorative component name denylist under `AdminPanel/`) | — |
| Contract | capabilities + openapi + route-index + moderation-auth script (**OG-GUI-09:** glob discovery + ESLint literal ban + script Vitest) | **OG-GUI-08 (2026-04-18):** read-gate 401 `detail` + capabilities strings SSOT — [`survey-read-gate-public-messages.ts`](../../src/lib/survey/survey-read-gate-public-messages.ts); [`ARCHITECTURE_REST_CONTRACT.md`](../../docs/ARCHITECTURE_REST_CONTRACT.md) pointers only |
| Unit | `survey-read-gate-logic.test.ts`, **`sync-session-submit-user-message.test.ts`** | No unit test for **impure** wrapper JSON shape (optional) |
| E2E | Survey flow, admin moderation API + **UI queue row**, capabilities, clarification; **CI** second step runs `e2e/survey.spec.ts` with `SURVEY_POST_REQUIRE_TOKEN=true` (MiscRepos workflow) | **OG-GUI-10 (2026-04-18):** `npm run verify:survey-read-prod` — [`scripts/survey-read-gate-prod-smoke.mjs`](../../scripts/survey-read-gate-prod-smoke.mjs) + [`.github/workflows/survey-visualization-prod-smoke.yml`](../../.github/workflows/survey-visualization-prod-smoke.yml) (`next start`, env/header matrix) |
| A11y | **`e2e/sync-session-admin-a11y.spec.ts`** (`@axe-core/playwright`), `npm run test:e2e:a11y` | Broader component coverage / manual spot checks still optional |
| Visual | **`npm run test:e2e:visual`** (`@percy/cli` + `@percy/playwright`), [`.github/workflows/opengrimoire_e2e.yml`](../../../MiscRepos/.github/workflows/opengrimoire_e2e.yml) when `PERCY_TOKEN` set | Tablet viewports / marketing-only pages still optional |

---

## Security sentinel (2026-04-18)

Structured read-only pass (authz, read gate, test routes, logging): [`SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md`](./SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md). Moderation **session-only** posture confirmed; new suggested IDs (**OGAN-SEC-***) are optional harness extensions beyond **OGAN-01–17**.

---

## Architecture notes (external review)

- **Layering:** Public survey POST vs production read gate vs cookie-only moderation is coherent; capabilities document `operator_session_only_no_alignment_key` for moderation paths.
- **Risks:** **OG-GUI-07 (2026-04-18):** E2E default secrets consolidated — literals + `buildPlaywrightWebServerEnv()` in [`e2e/helpers/e2e-secrets.ts`](../../e2e/helpers/e2e-secrets.ts); **OG-GUI-09 (2026-04-17):** moderation verifier is still substring-based (not AST-deep) but gains glob coverage + ESLint + Vitest entrypoint guard; SQLite + per-process limits bound horizontal scale until shared limiter + DB port.
- **Trajectory:** Storage port before Postgres/RLS; export APIs behind same read-gate family; keep capabilities/OpenAPI aligned in same PR families.

---

## Dimension action items

### 1 Task success

- [x] Add Playwright: `loginAsAdmin` → `/admin` → wait for moderation **fetch** 200 (or visible table region) → assert at least one row when `GET /api/admin/moderation-queue` returns non-empty `items` (use stable `data-testid` if present on row container; otherwise assert heading + network idle contract documented in spec). **Shipped 2026-04-18 (OG-GUI-02):** `data-testid={moderation-queue-item-${item.id}}` on [`AdminPanel`](../../src/components/AdminPanel/index.tsx); UI test in [`e2e/admin-moderation.spec.ts`](../../e2e/admin-moderation.spec.ts).

### 2 Cognitive load

- [x] Copy audit on Sync Session form: network failure, rate limit (**429**), optional survey post token (**401**) — user-facing strings and recovery hints. **Shipped 2026-04-18 (OG-GUI-05):** [`sync-session-submit-user-message.ts`](../../src/lib/survey/sync-session-submit-user-message.ts) + [`useSyncSessionForm.ts`](../../src/lib/hooks/useSyncSessionForm.ts); tests [`sync-session-submit-user-message.test.ts`](../../src/lib/survey/sync-session-submit-user-message.test.ts).

### 3 Accessibility

- [x] Run axe-playwright (or BrowserStack accessibility MCP) on `/operator-intake` and `/admin`; ticket violations. **Shipped 2026-04-18 (OG-GUI-04):** [`e2e/sync-session-admin-a11y.spec.ts`](../../e2e/sync-session-admin-a11y.spec.ts) (`npm run test:e2e:a11y`); contrast (`--brand-secondary-text`), nested `<main>` removal in [`Layout.tsx`](../../src/components/Layout.tsx), admin action buttons in [`AdminPanel`](../../src/components/AdminPanel/index.tsx).

### 4 Visual system

- [x] If UI changes land on intake or admin table, add or update visual regression baselines (Chromatic/Percy) in CI. **Shipped 2026-04-18 (OG-GUI-06):** [`e2e/visual-baselines-og-gui-06.spec.ts`](../../e2e/visual-baselines-og-gui-06.spec.ts), [`.percy.yml`](../../.percy.yml), `npm run test:e2e:visual`; optional CI step in MiscRepos [`opengrimoire_e2e.yml`](../../../MiscRepos/.github/workflows/opengrimoire_e2e.yml) when `PERCY_TOKEN` is configured.

### 5 A2UI / catalog

- [ ] **Trigger for A2UI work:** first admin surface that is **agent-generated or declarative** (A2UI/A2A) — then add catalog semantics + props map per `.cursor/docs/A2UI_FRONTEND_DESIGN_GUIDANCE.md` (MiscRepos harness) or OG equivalent (tracks **OA-OG-5** deferred: A2UI on `/capabilities`).
- [x] Until then: no new decorative-only component names in `src/components/AdminPanel/` (or successor paths). **OG-GUI-A2 (2026-04-18):** `npm run verify` includes [`scripts/verify-admin-panel-a2ui-monitor.mjs`](../../scripts/verify-admin-panel-a2ui-monitor.mjs); [CONTRIBUTING.md](../../CONTRIBUTING.md) § AdminPanel and A2UI naming.

### 6 Agent parity

- [x] When adding routes, update `capabilities/route.ts`, `ROUTE_INDEX`/generator, OpenAPI slice, and extend `verify:moderation-auth` if new admin surfaces must remain alignment-free. **OG-GUI-09 (2026-04-17):** new moderation handlers under `src/app/api/admin/moderation-queue/**` or `moderation/**` are picked up automatically; non-moderation admin routes stay excluded.
- [ ] **Maintain:** On new admin or survey routes, run `npm run verify` before merge; keep **OGAN-02** / capabilities prose aligned for visualization surfaces (System 2).

---

## Agent-native condensed scores (desk review)

| Principle | Score | Notes |
|-----------|-------|--------|
| Action parity | ~65% | Agents mirror **API** flows with session or public POST; moderation **by design** rejects alignment header alone. |
| Capability discovery | ~80% | `GET /api/capabilities` + verify scripts; watch string drift across markdown. |
| Shared workspace | High | Same SQLite + HTTP surface for UI and scripts. |
| Other principles (tools/primitives, context injection, prompt-native, etc.) | N/A | No embedded agent runtime in server scope. |

---

## Critic / debate

### Round 1 — adversarial-document-reviewer (domain: `docs`)

Critic JSON (verbatim):

```json
{"intent_alignment":4,"safety":4,"correctness":4,"completeness":2,"minimality":4,"total":18,"pass":true,"issues":["Dimension 5 is marked N/A with a single forward-looking bullet—weak as a audited dimension row versus expecting explicit non-applicability criteria, monitors, and exit triggers.","No BrowserReviewSpec-style block (viewports, auth/session recipe, stable selectors, failure screenshots, artifact links).","Little primary flow evidence: no attached traces, screenshots, Playwright report URLs, or dated command outputs tying claims to runs.","Several behavioral claims (e.g., operator-only moderation, alignment header behavior, survey POST paths) lack consistent file:line or symbol pointers beyond a few citations.","The “Critic / debate” section promises JSON below but the file ends there—unfinished self-reference.","Dimension 4 marked PASS (assumed) without visual baselines or review notes conflicts with a evidence-first human GUI audit bar.","Task success PARTIAL cites missing moderation UI E2E but does not define minimal UI acceptance steps (selectors, loading/empty/error states).","A11y/visual explicitly not executed yet dimensions 2–3 carry PARTIAL status without documenting what evidence would flip them to PASS/FAIL."],"revision_suggestions":["Add a compact BrowserReviewSpec under AuditorSpec: base URL, auth steps, 2–3 viewports, must-hit routes, and where to attach screenshots/traces.","Replace assumed PASS on dimension 4 with FAIL/PARTIAL until baselines or a recorded visual review exists, or document the explicit waiver owner/date.","Expand dimension 5 with N/A justification plus monitoring checks (e.g., what would trigger A2UI work, which components would need catalog rows).","Link each major AC to a concrete evidence artifact (E2E spec + assertion name, or file:line for implementation review items).","Fill or delete the “Critic / debate” section; if keeping JSON, embed the critic output or link to a stable location.","Add a short “flow evidence” subsection listing commands actually run and their timestamps/exit codes, or state explicitly that none were run this pass."]}
```

### Revision log (debate round 1 → doc revise)

| When | Delta | Change |
|------|-------|--------|
| 2026-04-17 | +completeness | Added **BrowserReviewSpec** stub, **Flow evidence** (commands + pass/skip counts), tightened AC pointer to `survey-read-gate.ts`, matrix dims 3–5 aligned to critic (PARTIAL + pass criteria / monitor), expanded dimension-5 todos, embedded critic JSON |

### Round 2 — self-check (structural)

Second pass after edits: completeness raised by adding BrowserReviewSpec + flow evidence + dimension-5 monitor; **no second external critic JSON** (within max 2 rounds per dialectic; marginal gain expected). If promoting to **release gate**, re-run **adversarial-document-reviewer** on this path after substantive UI changes.

**Verdict:** `pass: true` for Round 1 JSON stands for **documentation structure**; **human GUI sign-off** still requires executing BrowserReviewSpec + a11y/visual evidence.

---

## Tracking (harness)

When this repo sits next to **MiscRepos** under a common parent (e.g. `GitHub/`):

- **Labeled todos:** `MiscRepos/.cursor/state/pending_tasks.md` — section **PENDING_OG_GUI_RELEASE** (`OG-GUI-*`, plus **OG-GUI-A2** A2UI monitor).
- **Waved decomposition:** `MiscRepos/local-proto/workspace/docs/WAVED_PENDING_TASKS.md` — **Wave 10 — OG GUI release (decomposed)** (R1 → R2 → R3 exit criteria).
- **Portfolio index:** `MiscRepos/docs/audit/GUI_AUDIT_PORTFOLIO_INDEX.md`.
