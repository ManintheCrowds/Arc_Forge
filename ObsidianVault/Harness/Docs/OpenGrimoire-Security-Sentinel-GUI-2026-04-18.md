---
title: "Security sentinel — OpenGrimoire GUI / Wave 10 follow-up"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Security sentinel — OpenGrimoire GUI / Wave 10 follow-up

**Date:** 2026-04-18  
**Scope:** Read-only review aligned with Wave 10 exit + **PENDING_OG_GUI_RELEASE** verification (authz, survey read gate, test routes, secrets/logging).  
**Source:** MiscRepos `security-sentinel` subagent digest (no code changes in this pass).

---

## Executive summary

Moderation remains **operator-session only**; **`x-alignment-context-key` does not authorize** moderation (`requireOpenGrimoireAdminRoute`, `e2e/admin-moderation.spec.ts`, `verify-moderation-auth-purity`). Residual themes: **trusted-proxy / rate-limit IP** semantics, **large-body DoS** margins on survey/moderation JSON, **client-side logging** (**OGAN-12**), and **operational** env (`NODE_ENV`, alignment read escape hatch).

---

## Findings (severity-ordered)

| # | Severity | Topic | Files / notes | Backlog ID |
|---|----------|--------|-----------------|------------|
| 1 | Medium | Rate limits use `X-Forwarded-For` / `X-Real-IP` without a documented trusted-proxy contract | `middleware.ts` (`getClientIp`) | Suggest **OGAN-SEC-RL** (ops / edge) |
| 2 | Medium | Survey `answers` array has no `.max()` — memory/CPU stress with large arrays | `src/lib/survey/schemas.ts` | Suggest **OGAN-SEC-SURVEY-DOS** |
| 3 | Medium | Moderation PATCH `notes` optional string without max length | `src/app/api/admin/moderation/[responseId]/route.ts` | Suggest **OGAN-SEC-MOD-NOTES** |
| 4 | Low | Hot-path `console.log` may expose survey/graph-derived data in devtools | `src/store/visualizationStore.ts`, `src/components/visualization/ConstellationView.tsx` | **OGAN-12** |
| 5 | Low | `ALIGNMENT_CONTEXT_KEY_ALLOWS_SURVEY_READ` + valid header widens survey read blast radius if mis-set | `survey-read-gate-logic.ts`, `survey-read-gate.ts` | Suggest **OGAN-SEC-ALIGN-READ** (ops + docs) |
| 6 | Low | Non-production `NODE_ENV` short-circuits entire read gate | `survey-read-gate.ts` | Suggest **OGAN-SEC-NODEENV** (runbook) |
| 7 | Low | E2E default secrets predictable when env unset | `e2e/helpers/e2e-secrets.ts` | Suggest **OGAN-SEC-E2E-DEFAULTS** or credentials checklist |
| 8 | Low | Bootstrap token is thin abuse control vs scripted same-origin clients | `bootstrap-token/route.ts`, `survey-post-bootstrap.ts`, `api/survey/route.ts` | Suggest **OGAN-SEC-BST** or doc-only |

**OGAN-08** (mark `/test*` non-contractual) remains relevant for **agent doc** clarity, not a prod route bypass (middleware gates `/test*` in production).

---

## No-issue areas (this pass)

- Moderation **401** for unauthenticated and alignment-key-only flows; automated **verify-moderation-auth** + ESLint path guardrails.
- Survey read deny path uses SSOT messages; **constant-time** secret compare in logic helper; **access-denial** logging avoids body/header PII.
- **`survey-read-gate-prod-smoke.mjs`** profiles (deny / public / viz key / alignment) under **`NODE_ENV=production`**.
- Survey POST: Zod **strict** body, bounded strings on key fields, middleware rate limit on `/api/survey`.

---

## Cross-reference

- Harness **OGSEC-01–07:** [MiscRepos `.cursor/state/pending_tasks.md`](../../../MiscRepos/.cursor/state/pending_tasks.md) § **PENDING_OPENGRIMOIRE_GUI_AUDIT_FOLLOWUPS**
- Harness OGAN table: same file § **PENDING_OPENGRIMOIRE_AGENT_NATIVE_DECOMPOSED**
- Agent-native closure policy: [AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md](../AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md) § **OGAN backlog — closure policy (2026-04-18)**  
- Public surface: [PUBLIC_SURFACE_AUDIT.md](../security/PUBLIC_SURFACE_AUDIT.md)
