---
title: "Completed tasks (archive)"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
---

# Completed tasks (archive)

**Purpose:** Task rows removed from [pending_tasks.md](pending_tasks.md) when status is **done**. The pending file stays focused on open work (`pending`, `in_progress`, `deferred`, etc.).

**Last updated:** 2026-04-17

**Workflow:** After marking tasks done in `pending_tasks.md`, run:

`python .cursor/scripts/split_done_tasks_to_completed.py`

Then ensure the vault mirror is current: the script runs **int-vault-resync** (Scheduler) when not in ``--dry-run`` and not ``--skip-vault-resync``; or run ``npm run vault:sync`` / ``local-proto/scripts/Sync-VaultHarness.ps1`` manually.

Or move rows manually and bump **Last updated** above.

---

## PENDING_GOVERNANCE_SCHEDULE

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| GV-1 | done | **Windows — Task Scheduler:** Create the weekly job per [GOVERNANCE_RITUAL § Scheduled task (Windows)](../docs/GOVERNANCE_RITUAL.md#scheduled-task-windows) only (no duplicate steps elsewhere). **Verify:** one manual run; check `.cursor/state/governance_runs/*.log`. Copy-paste CLI: [SCHEDULED_TASKS § Harness-GovernanceRuns (CLI)](../../local-proto/docs/SCHEDULED_TASKS.md#harness-governanceruns-cli). **Closed 2026-04-13:** `Harness-GovernanceRuns` registered; `schtasks /run` last result **0**; log under `governance_runs/`. | [scheduled_governance.ps1](../scripts/scheduled_governance.ps1) |

## PENDING_AI_TRENDS_HUB

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AT-H4 | done | **Operator:** If `AI-Trends-Ingest` Task Scheduler job predates hub ingest, update `--sources` to `youtube,futuretools,newsletters,github,huggingface`. **Closed 2026-04-13 (N/A):** `schtasks /Query /TN "AI-Trends-Ingest"` — task not found on Windows dev host; no `--sources` migration required. Re-open if you add `AI-Trends-Ingest` on a machine that predates hub sources. | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § Cron |
| AT-H3 | done | **MCP_CAPABILITY_MAP** — hub tools + `list_ingested` / YT primitives / `summarize_content` row; full list still in `ai_trends_mcp.py` | [MCP_CAPABILITY_MAP.md](../docs/MCP_CAPABILITY_MAP.md) § ai_trends |

## PENDING_AFTER_RESTART

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| R2 | done | **obsidian-vault MCP:** foam-pkm prompt 1 — note created under `LLM-Wiki/Topics/` with `[[CHAOS_BITCOIN_MAPPING]]`; **strict** `apply_patch` vs `Write` re-check optional in MCP-enabled chat (this session used `Write` fallback; see log). | [TEST_PROMPTS.md](../skills/foam-pkm/TEST_PROMPTS.md) #1 · [R2 log](adhoc/2026-04-16_foam_pkm_TEST_PROMPTS_1_R2.md) |

## OPENGRIMOIRE_FULL_REVIEW (product-scope)

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OA-FR-SCOPE | done | **Charter + definition of done** — [SCOPE_OPENGRIMOIRE_FULL_REVIEW.md](../../OpenGrimoire/docs/plans/SCOPE_OPENGRIMOIRE_FULL_REVIEW.md) complete (2026-04-16): stakeholders, definition of done, MVP vs deferred, review order, harness link. | [SCOPE_OPENGRIMOIRE_FULL_REVIEW.md](../../OpenGrimoire/docs/plans/SCOPE_OPENGRIMOIRE_FULL_REVIEW.md) |
| OA-FR-BASE | done | **Base-features engineering plan** — [OPENGRIMOIRE_BASE_FEATURES_ENGINEERING_PLAN.md](../../OpenGrimoire/docs/plans/OPENGRIMOIRE_BASE_FEATURES_ENGINEERING_PLAN.md) verified 2026-04-16: waves W1–W5, REQ-1–REQ-10 template blocks, ADR log, out-of-scope table, verbatim agent-native guardrails; `/wiki` slice reconciled in REQ-1/2. | [OPENGRIMOIRE_BASE_FEATURES_ENGINEERING_PLAN.md](../../OpenGrimoire/docs/plans/OPENGRIMOIRE_BASE_FEATURES_ENGINEERING_PLAN.md) |
| OA-FR-1 | done | **System 1 — Survey & moderation:** REQ/AC matrix (submit survey, admin auth, moderate queue, RLS intent); gap list vs code + [PUBLIC_SURFACE_AUDIT.md](../../OpenGrimoire/docs/security/PUBLIC_SURFACE_AUDIT.md); smoke checklist (curl/Playwright optional). | **[OA_FR_1_SYSTEM1_SURVEY_MODERATION.md](../../OpenGrimoire/docs/plans/OA_FR_1_SYSTEM1_SURVEY_MODERATION.md)** · [operator-intake](../../OpenGrimoire/src/app/operator-intake), [admin](../../OpenGrimoire/src/app/admin), [api/survey](../../OpenGrimoire/src/app/api/survey) |
| OA-FR-2 | done | **System 2 — Data visualization:** REQ/AC (routes, data sources, quotes, auto-play, debug flags); perf/logging gates; list test pages (`/visualization`, `/test-chord`, etc.) and data dependencies. | **[OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md](../../OpenGrimoire/docs/plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md)** · [DataVisualization](../../OpenGrimoire/src/components/DataVisualization), [useVisualizationData](../../OpenGrimoire/src/components/DataVisualization/shared/useVisualizationData.ts) |
| OA-FR-3 | done | **System 3 — Brain map / context atlas:** REQ/AC (parser → JSON → API → UI); port resolution [PORT_REGISTRY.md](../docs/PORT_REGISTRY.md); `BRAIN_MAP_*` / empty state; link **BM-A11Y** and [BRAIN_MAP_E2E.md](../../docs/BRAIN_MAP_E2E.md). Shipped 2026-04-17: hub § System 3, E2E rewrite, PORT_REGISTRY 3001, capabilities `ui_path` `/context-atlas`, AGENT_INTEGRATION + OPENGRIMOIRE_BASE_FEATURES REQ-3.1; vault `Decision-Index` link rewrites in `sync_harness_to_vault.ps1`. | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md), [BrainMapGraph](../../OpenGrimoire/src/components/BrainMap/BrainMapGraph.tsx) |
| OA-FR-4 | done | **System 4 — Alignment & operator APIs:** REQ/AC (SQLite schema bootstrap + `alignment_context_items` contract, prod secret + header, public CRUD + admin BFF, CLI); critic gaps closed (admin PATCH title/body + optional `source` in UI, CLI `--attendee-id`). | [OA_FR_4_SYSTEM4_ALIGNMENT_OPERATOR_APIS.md](../../OpenGrimoire/docs/plans/OA_FR_4_SYSTEM4_ALIGNMENT_OPERATOR_APIS.md), [ALIGNMENT_CONTEXT_API.md](../../OpenGrimoire/docs/agent/ALIGNMENT_CONTEXT_API.md), § OPENGRIMOIRE_ALIGNMENT above |
| OA-FR-X | done | **Cross-cutting:** Go-live checklist shipped — Docker vs dev port matrix, `.env.example` vs DEPLOYMENT, local `npm run verify` / optional E2E, agent parity table, operator doc index, doc-drift note on hosted CI. | [OA_FR_X_CROSS_CUTTING_GO_LIVE.md](../../OpenGrimoire/docs/plans/OA_FR_X_CROSS_CUTTING_GO_LIVE.md), [DEPLOYMENT.md](../../OpenGrimoire/DEPLOYMENT.md), [MCP_CAPABILITY_MAP](../docs/MCP_CAPABILITY_MAP.md) § OpenGrimoire, [OPENGRIMOIRE_BASE_FEATURES_ENGINEERING_PLAN.md](../../OpenGrimoire/docs/plans/OPENGRIMOIRE_BASE_FEATURES_ENGINEERING_PLAN.md) |
| OA-FR-REFRESH-2026-04-17 | done | **Post-charter delta audit (since 2026-04-16):** git delta vs `31c9ca0`, `npm run verify` + `npm run test:e2e` evidence, product-scope REQ deltas (read-gate tests, bootstrap E2E), GUI dimension matrix + six todos, agent-native principles **#6/#7** score bump, Playwright `webServer` footgun documented in DEPLOY_AND_VERIFY. | [OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md](../../OpenGrimoire/docs/plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md) |

## PENDING_FUTURE

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| G5 | done | Model escalation pattern: documented in [AI_TASK_EVALS.md](../docs/AI_TASK_EVALS.md) + normative router contract [LOCAL_FIRST_MODEL_ROUTER_SPEC.md](../docs/LOCAL_FIRST_MODEL_ROUTER_SPEC.md). **Implementation backlog:** [§ PENDING_MODEL_ROUTER](#pending_model_router-local-first) (MR1–MR8). **Closed 2026-04-17.** | [BitDevs MPLS 2026-03-10](../../docs/bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md) |

## PENDING_AI_TRENDS

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AT1 | done | AI Trends MCP: WhisperX / CLI fallback for videos without captions (`transcribe_video`; yt-dlp audio + `WHISPERX_PATH` or `AI_TRENDS_TRANSCRIBE_CMD`; SCP). **Closed 2026-04-17.** | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § WhisperX |
| AT2 | done | AI Trends MCP: Firecrawl + optional Playwright for FutureTools when static scrape is empty (`futuretools_fetch_tools`; ingest + MCP). **Closed 2026-04-17.** | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § FutureTools |
