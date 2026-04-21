---
title: "GUI audit portfolio index"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# GUI audit portfolio index

**Purpose:** Map sibling repos to their latest **human + machine GUI audit** markdown (dated filenames may evolve; this index is the navigation hub).

**Convention:** One primary audit file per OpenGrimoire *system* during wave audits; update the row when superseding.

---

## OpenGrimoire

| System | Audit doc | Wave / harness | Status |
|--------|-------------|----------------|--------|
| **System 1** — Survey, Sync Session, moderation, discovery | [OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-survey.md](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-survey.md) | MiscRepos [WAVED_PENDING_TASKS.md](../../local-proto/workspace/docs/WAVED_PENDING_TASKS.md) **Wave 10** (`OG-GUI-*`); archived rows [completed_tasks.md § PENDING_OG_GUI_RELEASE](../../.cursor/state/completed_tasks.md) | **done** (Wave 10 R1–R3, 2026-04-18) |
| **System 2** — Data visualization, constellation, survey read UX | [OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md) | Agent-native backlog **OGAN-*** in [pending_tasks.md § PENDING_AGENT_NATIVE](../../.cursor/state/pending_tasks.md) | pending |
| **Operator observability** — `/admin/observability`, probe ingest | Evidence stub **2026-04-20** (no standalone `gui-*.md`): [OpenGrimoire `e2e/operator-observability.spec.ts`](../../OpenGrimoire/e2e/operator-observability.spec.ts); [OpenGrimoire `e2e/sync-session-admin-a11y.spec.ts`](../../OpenGrimoire/e2e/sync-session-admin-a11y.spec.ts) (axe: list + detail). **A2UI / declarative admin catalog:** **N/A** — operator session + conventional table/detail UI only; no OG-GUI-style A2UI catalog surface (align with **OG-GUI-AUDIT-01** deferred scope). | [OpenGrimoire `docs/ARCHITECTURE_REST_CONTRACT.md`](../../OpenGrimoire/docs/ARCHITECTURE_REST_CONTRACT.md); workflow **`operator_observability_probes`** in [OpenGrimoire `src/app/api/capabilities/route.ts`](../../OpenGrimoire/src/app/api/capabilities/route.ts); hub backlog [pending_tasks.md § PENDING_OPENGRIMOIRE_OBSERVABILITY_HUB](../../.cursor/state/pending_tasks.md#pending_opengrimoire_observability_hub) | **OG-OH-02** — release-gate parity row |

**Agent-native scorecard (cross-system):** [OpenGrimoire/docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md](../../OpenGrimoire/docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md)

**Evidence packs:** e.g. [OpenGrimoire/docs/audit/evidence/og-gui-01/BROWSER_REVIEW_REPORT.md](../../OpenGrimoire/docs/audit/evidence/og-gui-01/BROWSER_REVIEW_REPORT.md) (BrowserReviewSpec).

**Security (Wave 10 adjunct):** [OpenGrimoire/docs/audit/SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md](../../OpenGrimoire/docs/audit/SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md)

**Harness backlog (audit-derived IDs):** [MiscRepos `.cursor/state/pending_tasks.md` § PENDING_OPENGRIMOIRE_GUI_AUDIT_FOLLOWUPS](../../.cursor/state/pending_tasks.md#pending_opengrimoire_gui_audit_followups) — **OGSEC-***, **OG-AUDIT-***, **OG-GUI-AUDIT-***, **OG-DV-*** (dedup with **OGAN-*** where noted).

---

## Other repos

_Add rows here when sibling repos receive dated `docs/audit/gui-*.md` files (see [.cursor/skills/gui-human-audit/SKILL.md](../../.cursor/skills/gui-human-audit/SKILL.md))._

| Repo | Audit doc | Notes |
|------|-------------|--------|
| — | — | — |
