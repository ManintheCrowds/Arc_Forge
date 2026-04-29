---
title: "OpenGrimoire — human verification guide (system + GUI)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# OpenGrimoire — human verification guide (system + GUI)

**Audience:** Operator performing **manual** acceptance of OpenGrimoire (not only CI). **SSOT for HTTP/auth:** OpenGrimoire repo [`docs/AGENT_INTEGRATION.md`](../../../../OpenGrimoire/docs/AGENT_INTEGRATION.md) (local dev URL, headers, gates).

**Labeled backlog:** [MiscRepos `pending_tasks` § PENDING_OPENGRIMOIRE_HUMAN_VERIFICATION](../../../.cursor/state/pending_tasks.md#pending_opengrimoire_human_verification) (`OG-HV-*`).

---

## Before you start

1. **Repo:** Check out the **full OpenGrimoire app** (not only the `local-proto/workspace/OpenGrimoire/docs` stub). Typical path: sibling to MiscRepos, e.g. `...\GitHub\OpenGrimoire`.
2. **Tooling:** Node **≥ 18**, `npm install` completed once.
3. **Secrets:** Copy `.env.example` → `.env` per [OpenGrimoire `CONTRIBUTING.md`](../../../../OpenGrimoire/CONTRIBUTING.md) if you do not already have one. **Do not** paste secrets into tickets, handoffs, or vault notes—use “present / absent” only.
4. **Timebox:** Plan **45–90 minutes** for a first full pass (machine verify + GUI smoke + notes).

---

## Phase A — Machine verification (terminal)

**Goal:** Confirm the repo’s automated gate still passes on **your** machine.

| Step | Command | Pass criteria |
|------|---------|----------------|
| A1 | `cd` to OpenGrimoire repo root | You see `package.json`. |
| A2 | `npm run verify` | Exits **0** (lint, type-check, Vitest, route/capability/moderation/probe/A2UI script checks). |
| A3 | (Optional) `npm run verify:survey-read-prod` | Exits **0** if you need production read-gate semantics documented in AGENT_INTEGRATION. |

If **A2** fails: open the logged failing step, fix or file an issue, **do not** sign GUI verification until green (or explicitly waive in your report with reason).

---

## Phase B — Local GUI smoke (`http://localhost:3001`)

**Goal:** Eyes-on confirmation that operator surfaces load and behave plausibly.

| Step | Action | Pass criteria |
|------|--------|----------------|
| B1 | `npm run dev` | Next dev listens on **port 3001** (see `package.json` `dev` script). |
| B2 | Open `http://localhost:3001` | Home or redirect loads without 5xx. |
| B3 | Sign in as admin | Use UI login or documented API per [OPENGRIMOIRE_ADMIN_ROLE.md](../../../../OpenGrimoire/docs/admin/OPENGRIMOIRE_ADMIN_ROLE.md); session works (you can reach `/admin`). |
| B4 | Open **`/admin`** | Operator hub loads; navigation visible (e.g. Operations). |
| B5 | Moderation queue | List loads (may be empty); no unhandled error boundary. If items exist: row visible; note `data-testid` pattern from [AGENT_INTEGRATION](../../../../OpenGrimoire/docs/AGENT_INTEGRATION.md) / E2E docs only as **hints**, not required memorization. |
| B6 | **`/admin/observability`** (if you use probes) | Page loads; table or empty state consistent with env ([AGENT_INTEGRATION](../../../../OpenGrimoire/docs/AGENT_INTEGRATION.md) operator probe rows). |
| B7 | (Optional) **`/visualization`** or **`/constellation`** | Matches your product scope; read gates behave as expected for your `NODE_ENV` and secrets ([SURVEY_READ_GATING_RUNBOOK](../../../../OpenGrimoire/docs/admin/SURVEY_READ_GATING_RUNBOOK.md)). |

**While testing:** Keep **DevTools → Console** open; note red errors. Optionally **Network** tab: flag unexpected 4xx/5xx on critical paths.

---

## Phase C — Hosted / staging (if applicable)

**Goal:** Same flows against a **non-local** base URL you operate.

1. Set **Base URL** (no path) to your staging origin (HTTPS).
2. Repeat **B3–B7** (or a subset agreed with your team).
3. Confirm **`OPENGRIMOIRE_BASE_URL`** (or deployment env) matches that origin for any scripts you run.

Record only **non-secret** pointers (e.g. “`https://og-staging.example.com`”) in [MiscRepos `handoff_latest`](../../../.cursor/state/handoff_latest.md) or your runbook.

---

## Phase D — Evidence pack (required output)

Create a short **HumanVerificationReport** (markdown is fine) with:

| Section | Content |
|---------|---------|
| **Meta** | Date, OpenGrimoire commit SHA or tag, host (local vs staging), your name/role. |
| **Machine** | PASS/FAIL for `npm run verify` (+ optional survey-read prod). |
| **GUI** | Table: Route / PASS-FAIL / notes (console errors, UX friction). |
| **Blockers** | Env gaps, auth failures, data dependencies, “waived with reason”. |
| **Sign-off** | One line: “Approved for operator use” / “Not approved — see blockers”. |

---

## BrowserReviewSpec (optional structured pass)

```markdown
## BrowserReviewSpec — OpenGrimoire
- **Base URL:** http://localhost:3001 (or staging URL)
- **Route(s):** /admin, /admin/observability, (optional) /visualization
- **Auth:** admin session (where creds live: env / vault — do not paste)
- **Viewports:** 1280×720; optional 375×667
- **Flows:**
  1. Login → /admin → moderation queue visible → **Expected:** 200, no console errors.
  2. Navigate to observability → **Expected:** page renders, empty or seeded state OK.
  3. (Optional) Survey visualization → **Expected:** matches runbook for your NODE_ENV.
- **Critical screens:** /admin (full), observability table header
```

---

## Mapping to `pending_tasks` rows (`OG-HV-*`)

| ID | Phase | What “done” means |
|----|--------|-------------------|
| **OG-HV-01** | A | `npm run verify` green on operator machine (or waived in report). |
| **OG-HV-02** | B | B1–B5 complete; notes captured. |
| **OG-HV-03** | B | B6 observability pass **or** N/A documented. |
| **OG-HV-04** | B/C | Optional viz routes **or** N/A documented. |
| **OG-HV-05** | C | Hosted/staging subset **or** “local only” documented. |
| **OG-HV-06** | D | HumanVerificationReport filed and linked from handoff or backlog. |

---

## See also

- [GOVERNANCE_REVIEW_LOOP.md](../../docs/integrations/mission-control/GOVERNANCE_REVIEW_LOOP.md).
- [OpenGrimoire `docs/audit/gui-2026-04-16-opengrimoire-survey.md`](../../../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-survey.md).
- [PENDING_OPENGRIMOIRE_GUI_AUDIT_FOLLOWUPS](../../../.cursor/state/pending_tasks.md#pending_opengrimoire_gui_audit_followups).
