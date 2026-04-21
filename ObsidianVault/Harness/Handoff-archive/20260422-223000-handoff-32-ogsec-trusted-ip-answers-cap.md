---
title: "Handoff #32: OGSEC-01/02 — OpenGrimoire trusted proxy IP + survey answers cap"
tags: ["type/harness-state", "status/shipped", "domain/opengrimoire", "domain/security"]
group: harness-core
color: slate
cssclasses:
  - vault-grp-harness-core
  - vault-col-slate
---

# Handoff #32: OGSEC-01/02 — OpenGrimoire trusted proxy IP + survey answers cap

decision_id: handoff-2026-04-22-ogsec-01-02
Updated: 2026-04-22T22:30:00Z

## Done

- **OGSEC-01** — Middleware rate-limit client IP: added [`OpenGrimoire/src/lib/rate-limit/get-client-ip.ts`](../../OpenGrimoire/src/lib/rate-limit/get-client-ip.ts) (`getRateLimitClientIp`, `shouldTrustForwardedIpForRateLimit`). Trust `X-Forwarded-For` / `X-Real-IP` only when `OPENGRIMOIRE_TRUST_FORWARDED_IP` is `1`/`true` **or** `VERCEL=1`; else key is **`unknown`** (no header spoof bypass). [`middleware.ts`](../../OpenGrimoire/middleware.ts) wired to helper. Vitest: [`get-client-ip.test.ts`](../../OpenGrimoire/src/lib/rate-limit/get-client-ip.test.ts).
- **OGSEC-02** — [`schemas.ts`](../../OpenGrimoire/src/lib/survey/schemas.ts): `answers` **`.max(64)`**; test in [`survey.test.ts`](../../OpenGrimoire/src/lib/survey/survey.test.ts).
- **Docs:** [`.env.example`](../../OpenGrimoire/.env.example), [`DEPLOYMENT.md`](../../OpenGrimoire/DEPLOYMENT.md) (checklist + nginx `X-Forwarded-For $remote_addr`), [`OPERATIONAL_TRADEOFFS.md`](../../OpenGrimoire/docs/engineering/OPERATIONAL_TRADEOFFS.md), [`ARCHITECTURE_REST_CONTRACT.md`](../../OpenGrimoire/docs/ARCHITECTURE_REST_CONTRACT.md) (Client IP subsection + cross-links), [`SYNC_SESSION_HANDOFF.md`](../../OpenGrimoire/docs/agent/SYNC_SESSION_HANDOFF.md) §7.2 (400 row for >64 answers).

## Next

- **Operator:** Commit + push OpenGrimoire when ready (single PR for OGSEC-01+02 is fine).
- **Self-hosted prod:** Set `OPENGRIMOIRE_TRUST_FORWARDED_IP=1` only after reverse proxy overwrites/forwards a trustworthy leftmost hop; otherwise limits remain one shared `unknown` bucket per process.
- **Harness / vault:** Mark **OGSEC-01** / **OGSEC-02** completed in [Pending-Tasks.md](Harness/Pending-Tasks.md) (or MiscRepos `pending_tasks.md` if that is SSOT for OG rows) so audit follow-ups do not drift.

## Paths / artifacts

| Area | Path |
|------|------|
| Client IP SSOT | `OpenGrimoire/src/lib/rate-limit/get-client-ip.ts` |
| Middleware | `OpenGrimoire/middleware.ts` |
| Survey body cap | `OpenGrimoire/src/lib/survey/schemas.ts` |
| Audit source | `OpenGrimoire/docs/audit/SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md` (findings #1–2) |

## dependency_links

- [SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md](../../OpenGrimoire/docs/audit/SECURITY_SENTINEL_OPENGRIMOIRE_GUI_2026-04-18.md)
- [OPERATIONAL_TRADEOFFS.md](../../OpenGrimoire/docs/engineering/OPERATIONAL_TRADEOFFS.md)
- [Pending-Tasks.md](Harness/Pending-Tasks.md) (OGSEC rows)

## open_risks

- **Breaking:** Non-Vercel production without trust env gets stricter shared bucket; document in release notes for operators.
- Multi-hop CDN + nginx still requires ops to ensure the hop OpenGrimoire reads is not client-spoofable (docs call this out; no automatic “rightmost trusted hop” in code).

## Decisions / gotchas

- **`VERCEL=1`** implies trust for forwarded IP (platform edge). Self-hosted must use **`OPENGRIMOIRE_TRUST_FORWARDED_IP`** explicitly.
- Prefer **`python .cursor/scripts/write_handoff.py`** for this chain so **`sessions.db`** + **int-vault-resync** run when `OBSIDIAN_VAULT_ROOT` is set ([HANDOFF_FLOW.md](../HANDOFF_FLOW.md)).

## Verification

- OpenGrimoire: `npm test` exit **0** (67 tests); `npm run type-check` exit **0**.

## Vault navigation

**Handoff chain:** [[Harness/MOC_Harness_State]]
**Decision index:** [[Harness/Decision-Index]]
