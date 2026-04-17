---
title: "Pending Tasks (Labeled)"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
---

# Pending Tasks (Labeled)

**Archive (completed rows):** [completed_tasks.md](completed_tasks.md) — run `python .cursor/scripts/split_done_tasks_to_completed.py` after marking tasks done to move **done** rows out of the tables below.

**Purpose:** Labeled task list for HITL and async development. Cross-references [INTEGRATED_HITL_ASYNC_ROADMAP.md](../plans/INTEGRATED_HITL_ASYNC_ROADMAP.md). Check [handoff_latest.md](handoff_latest.md) for current focus before assuming all pending tasks are actionable. **Waved roadmap:** [WAVED_PENDING_TASKS.md](../../local-proto/docs/WAVED_PENDING_TASKS.md) (Waves 5–10; **Wave 10** = OpenGrimoire GUI release — `OG-GUI-*`).

**Last synced:** 2026-04-17 — **Handoff #22** (IronClaw G7 + [IRONCLAW_ENGINEERING_SPEC.md](../docs/specs/IRONCLAW_ENGINEERING_SPEC.md) ACE/local-first + **G10**); prior **Handoff #21** archived as [handoff_archive/20260417-192536.md](handoff_archive/20260417-192536.md). Same day earlier: **Handoff #21** + `split_done_tasks_to_completed.py` (**3** `done` rows → [completed_tasks.md](completed_tasks.md): G5, AT1, AT2); model router spec; **§ PENDING_MODEL_ROUTER** (MR1–MR8). Earlier: [§ PENDING_PORTABLE_AI_MEMORY](#pending_portable_ai_memory-byoc-session-db-vault-harness) (BYOC); single-vault consolidation. Prior **2026-04-13:** [SCP_PARASITIC_DYNAMICS_POSTURE.md](../docs/SCP_PARASITIC_DYNAMICS_POSTURE.md); **SCP-ANT1** in [§ PENDING_SCP_SAAS_MYCELIUM](#pending_scp_saas_mycelium-instrumental-money-fame).
**80% target:** Met (per INTEGRATED_HITL_ASYNC_ROADMAP)
**Next focus:** Close **TODO #8a** — [HOST_ASYNC_INTEGRATION_SPEC.md](../../local-proto/docs/HOST_ASYNC_INTEGRATION_SPEC.md) + **#10a** / **#10b** per [TODO.md](../../local-proto/TODO.md). OpenGrimoire product-scope charter rows are **archived**; active product work: [§ PENDING_OG_GUI_RELEASE](#pending_og_gui_release) (Wave 10), [§ PENDING_AGENT_NATIVE](#pending_agent_native) (**AN1** + **OGAN-***), [§ PENDING_OPENGRIMOIRE_HARNESS](#pending_opengrimoire_harness) (**OA-1**). Parallel: **NEXT-***, credentials (**CR***), **AL2**, I1/I2, AT-H1/H2.

**Cross-ref (local-proto/TODO ↔ pending_tasks):** local-proto #7 = I1 (Continue.dev); #8 = I2 (Aider); #8a = host async decision / [HOST_ASYNC_INTEGRATION_SPEC.md](../../local-proto/docs/HOST_ASYNC_INTEGRATION_SPEC.md); #10a = safeguards checklist before host MCP wiring; #10b = Tier-1 MCP wired to chosen async host; #24 = agent-native hardening post-host choice; #19 = AL2 (Bitcoin-Chaos); #21 = AL4 (Python Bitcoin); #23 = handoff Next (chaos + NIM testing).

**Cross-ref (Arc_Forge ops / token offload ↔ this file):** Phase-style plans live under [`Arc_Forge/.cursor/plans/`](../../../Arc_Forge/.cursor/plans/) (e.g. `phase_1_ops_bootstrap_*.plan.md`, `phase_2_token_offload_*.plan.md`, `ops_bootstrap_with_local_ai_*.plan.md`). Reconcile “next focus” with this list and any workspace `handoff_latest.md` before pulling new parallel work.

**Cross-ref (workspace / public-private audit — future):** [§ PENDING_WORKSPACE_PRIVACY_AUDIT](#pending_workspace_privacy_audit) — decomposed backlog for auditing workspaces and repos; same privacy/security bar, less friction.

**Cross-ref (Obsidian “brain” vault + stack atlas — 2026-04-17):** [§ PENDING_OBSIDIAN_BRAIN_VAULT](#pending_obsidian_brain_vault) (numeric audit, hygiene, rename/branding) · [§ PENDING_STACK_ATLAS](#pending_stack_atlas_openharness_in_opengrimoire) (OpenHarness visible in OpenGrimoire / Brain Map, directory layout survey).

**Cross-ref (SCP cognitohazard live test):** [§ PENDING_SCP_COGNITOHAZARD_LIVE](#pending_scp_cognitohazard_live) — live run = SCP classification + operator protocol; no automated cognitohazard detector; wellbeing layer design-only until SCP-CH4/CH5.

**When executing C4, C5, CRY1, CRY2, LF1:** Load CL4R1T4S patterns and AUTHORITY_MODEL_TAXONOMY per [PENTAGI_FEDIMINT_ACE_ROADMAP](../../docs/PENTAGI_FEDIMINT_ACE_ROADMAP.md) §7.

---

## Contents

Read [handoff_latest.md](handoff_latest.md) before pulling parallel work. Sections below stay in **source order**; this list groups by **theme** for scanning.

**Host / roadmap / harness hygiene**

- [PENDING_GOVERNANCE_SCHEDULE](#pending_governance_schedule) · [PENDING_SHORT_TERM](#pending_short_term) · [PENDING_AFTER_RESTART](#pending_after_restart) · [PENDING_GWS_MANUAL (human checklist)](#pending_gws_manual-human-checklist) · [PENDING_OTHER](#pending_other)

**Credentials & env**

- [PENDING_CREDENTIALS (human checklist from setup_env.py)](#pending_credentials-human-checklist-from-setup_envpy)

**Context graph / PKM / demos**

- [PENDING_NEXT (Context Graph, Foam, Obsidian, LLM Wiki, OpenGrimoire — E2E Demo & Education)](#pending_next-context-graph-foam-obsidian-llm-wiki-opengrimoire-e2e-demo-education) · [PENDING_BRAIN_MAP](#pending_brain_map) · [PENDING_OBSIDIAN_BRAIN_VAULT](#pending_obsidian_brain_vault) · [PENDING_STACK_ATLAS](#pending_stack_atlas_openharness_in_opengrimoire)

**OpenGrimoire (product + agent-native + GUI wave)**

- [OPENGRIMOIRE_FULL_REVIEW (product-scope)](#opengrimoire_full_review-product-scope) — charter rows in [completed_tasks.md § same title](completed_tasks.md#opengrimoire_full_review-product-scope)
- [OPENGRIMOIRE_ALIGNMENT](#opengrimoire_alignment) · [PENDING_OPENGRIMOIRE_HARNESS](#pending_opengrimoire_harness) · [PENDING_OG_GUI_RELEASE](#pending_og_gui_release) · [PENDING_AGENT_NATIVE](#pending_agent_native) (includes **OGAN-*** table)

**AI Trends**

- [PENDING_AI_TRENDS_HUB](#pending_ai_trends_hub) · [PENDING_AI_TRENDS](#pending_ai_trends) · [PENDING_PORTABLE_AI_MEMORY](#pending_portable_ai_memory-byoc-session-db-vault-harness)

**Bitcoin / alignment / local-first / Blue Hat**

- [PENDING_ALIGNMENT](#pending_alignment) · [PENDING_LOCAL_FIRST](#pending_local_first) · [PENDING_MODEL_ROUTER](#pending_model_router-local-first) · [PENDING_BLUE_HAT](#pending_blue_hat)

**SCP**

- [PENDING_SCP_COGNITOHAZARD_LIVE](#pending_scp_cognitohazard_live) · [PENDING_SCP_SAAS_MYCELIUM (instrumental: money + fame)](#pending_scp_saas_mycelium-instrumental-money-fame) · [PENDING_SCP_PROOF (user wants visual proof)](#pending_scp_proof-user-wants-visual-proof)

**Optional tools / backlog / research**

- [PENDING_OPTIONAL](#pending_optional) · [PENDING_FUTURE](#pending_future) · [PENDING_OPEN_GRIMOIRE](#pending_open_grimoire) · [PENDING_WORKSPACE_PRIVACY_AUDIT](#pending_workspace_privacy_audit)

**Archive pointers**

- [DONE_VIDEO_LEARNINGS](#done_video_learnings)

---

## DONE_VIDEO_LEARNINGS

Video Learnings Quick Wins plan — all items completed. Plan: [video_learnings_quick_wins_240bc12e.plan.md](D:\software\.cursor\plans\video_learnings_quick_wins_240bc12e.plan.md). Rows archived under [completed_tasks.md § DONE_VIDEO_LEARNINGS](completed_tasks.md#done_video_learnings).

---

## PENDING_AI_TRENDS_HUB

**Purpose:** Follow-ups after GitHub + Hugging Face SCP-gated hub ingest (core pipeline **done** 2026-03-20). Optional enhancements only.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AT-H1 | pending | **Operator / policy:** Optional GitHub trending **HTML** path is **implemented** behind `github.trending_page_enabled`; enable only after ToS review — see hub follow-ups | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § Hub follow-ups (AT-H1, AT-H2, AT-H4) |
| AT-H2 | pending | **Optional extension:** Hub + stack intel already use `wellbeing_keywords` / `focus_prompt`; extending **WellbeingSignals** to YouTube / FutureTools / newsletters is **not** required — see hub follow-ups | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § Hub follow-ups (AT-H1, AT-H2, AT-H4) |

**AT-H4:** Closed — see [completed_tasks.md](completed_tasks.md) (AT-H4) and [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § Hub follow-ups (AT-H1, AT-H2, AT-H4).

---

## PENDING_GOVERNANCE_SCHEDULE

**Purpose:** OS-level scheduling for weekly harness governance (log stub + meta-review prompt). **Not** local-proto hardware or async AI handoff—this is “run a script on a timer” on whatever machine you use. Docs: [GOVERNANCE_RITUAL.md](../docs/GOVERNANCE_RITUAL.md); troubleshooting: [TROUBLESHOOTING_AND_PLAYBOOKS.md](../docs/TROUBLESHOOTING_AND_PLAYBOOKS.md) § Governance; broader registry: [local-proto SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md).

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| GV-2 | pending | **Linux / macOS:** Install cron or launchd per [GOVERNANCE_RITUAL § Cron and launchd](../docs/GOVERNANCE_RITUAL.md#cron-and-launchd-linux-macos). **Verify:** log under `governance_runs/`; mark done after one successful run. Cron row: [SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md) (Cron examples table). | [GOVERNANCE_RITUAL.md](../docs/GOVERNANCE_RITUAL.md) |

**Verification note:** **GV-1** closed 2026-04-13 — `Harness-GovernanceRuns` exists on Windows dev host; `schtasks /query` / `schtasks /run` verified (last result 0). **GV-2** is satisfied after a Linux or macOS host completes cron/launchd and confirms the same log directory. **Archived audit (2026-04-13):** [.cursor/state/adhoc/2026-04-13_scheduled_tasks_audit.md](adhoc/2026-04-13_scheduled_tasks_audit.md) — findings table, top recommendations, acceptance criteria; links to [SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md) and AT-H4 / AN1.

---

## PENDING_OPTIONAL

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| I1 | pending | Evaluate Continue.dev: install, configure Ollama, test handoff paste flow | [continue_aider_eval plan](../plans/continue_aider_eval.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #7. **What AI needs:** Install path (VS Code extension); Ollama config (add llama3.2 in Continue settings); handoff flow: generate_next_prompt.ps1 → copy_continue_prompt.ps1 → paste in new Continue chat. **Human:** Confirm install + Ollama; run flow; report result. |
| I2 | pending | Evaluate Aider: install, test with handoff-derived prompt | [continue_aider_eval plan](../plans/continue_aider_eval.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #8. **What AI needs:** Install (`pip install aider-chat`); Ollama (`ollama pull qwen2.5-coder`); handoff flow: generate_next_prompt.ps1 → use continue_prompt.txt → `aider --model ollama_chat/qwen2.5-coder` + paste. **Human:** Same as I1. |

---

## PENDING_SHORT_TERM

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| ST2 | pending | **Alpha R2 + AGA setup:** Execute runbook (AGA connection, Ollama, OpenClaw, local-proto). **Blocked:** Pending hardware arrival. | [ALPHA_R2_AGA_SETUP.md](../../local-proto/docs/ALPHA_R2_AGA_SETUP.md) |

---

## PENDING_FUTURE

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| G1 | pending | Tier 1 tools (git, filesystem, sqlite) for Jarvis path; apply TOOL_SAFEGUARDS | [TOOLS_TO_INTEGRATE.md](../../local-proto/docs/TOOLS_TO_INTEGRATE.md) |
| G2 | pending | PentAGI → Signal approval round-trip (webhook to receive human response) | [Wave 4 plan](../plans/wave_4_async_delivery_25e3cf38.plan.md) |
| G3 | pending | C2 Option B: ORG_INTENT_ENFORCE blocking (when classifier/human intent_ok flow designed) | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| G4 | pending | org-intent.example.json in pentagi examples (optional; for local testing) | [integration verification](../plans/integration_points_verification_763e7765.plan.md) |
| G6 | pending | Research: Fedimint CLI, MCP2CLI, LiteLLM + Routstr/OpenRouter | [BitDevs MPLS 2026-03-10](../../docs/bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md) |
| VSH-1 | pending | **Session-Handoff:** Fork **2** (post-sync snapshot under `Harness/Session-Handoff/`) implemented in `sync_harness_to_vault.ps1`. Forks **1** (agent `apply_patch` at handoff) and **3** (`session_save` blob) remain **deferred** unless product reopens | [OBSIDIAN_VAULT_INTEGRATION.md § Session-Handoff vault artifact](../docs/OBSIDIAN_VAULT_INTEGRATION.md#session-handoff-vault-artifact) |
| G7 | done | IronClaw evaluation for Rust-based privacy-first AI path — **memo:** [2026-04-17_g7_ironclaw_evaluation.md](adhoc/2026-04-17_g7_ironclaw_evaluation.md); **decision:** pilot (bounded) / patterns now; defer default substrate until Postgres+IronClaw spike + MCP transport fit checked. | [BitDevs MPLS 2026-03-10](../../docs/bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md), [IronClaw](https://github.com/nearai/ironclaw) |
| G8 | pending | **MCP OAuth 2.1 + Streamable HTTP** — Track for future auth and deployment. Streamable HTTP uses OAuth 2.1 (Auth Code + PKCE) for remote MCP; enables secure SaaS MCP. | [MCP Authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization), [LavX News](https://news.lavx.hu/article/authentication-and-authorization-in-model-context-protocol-oauth-2-1-and-the-streamable-http-transport). **What AI needs:** Priority and scope. Options: (a) Tracking only — add to roadmap; (b) Implementation — design and implement for specific MCP (e.g. SCP SaaS). **Human:** Choose tracking vs implementation; if (b), scope and MCP. |
| G9 | pending | **Research: AI pools + Bitcoin block space** — AI compute pools using Bitcoin block space/data as prompts for sovereign decentralized AI. Survey: Gonka AI, x402 Stacks, Lumerin, DeltaHash, Routstr. Brainstorm: docs/brainstorms/2026-03-16-ai-pools-bitcoin-block-space-brainstorm.md. | [BITCOIN_OBSERVATION_SOURCES](../../docs/BITCOIN_OBSERVATION_SOURCES.md), [Routstr SKILL](../skills/routstr/SKILL.md) |
| G10 | pending | **IronClaw engineering spec (seed):** Maintain and refine [IRONCLAW_ENGINEERING_SPEC.md](../../docs/specs/IRONCLAW_ENGINEERING_SPEC.md) after G7-P1 spike; drive phased pilot (Postgres+pgvector, Ollama, WASM+MCP HTTP), agent-native parity, **local-first skill + D:\\local-first corpus**, **ACE (David Shapiro)** L1–L6 mapping per [PENTAGI_FEDIMINT_ACE_ROADMAP.md](../../docs/PENTAGI_FEDIMINT_ACE_ROADMAP.md), harness/MCP fit (stdio bridge vs defer). **Not** OpenClaw parity or core L402 inside IronClaw. | [IRONCLAW_ENGINEERING_SPEC.md](../../docs/specs/IRONCLAW_ENGINEERING_SPEC.md), [G7 memo](adhoc/2026-04-17_g7_ironclaw_evaluation.md) |

---

## PENDING_OPENGRIMOIRE_HARNESS

**Purpose:** One standard for verification and discoverability across harness + OpenGrimoire without multiplying “sources of truth.” OpenGrimoire inventory doc links to workspace [MCP_CAPABILITY_MAP.md](../docs/MCP_CAPABILITY_MAP.md) instead of copying MCP lists.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OA-OH-0 | pending | **OpenHarness inside OpenGrimoire (Brain Map):** Multi-root state + optional vault roots + directory recon — full task list under **§ [PENDING_STACK_ATLAS](#pending_stack_atlas_openharness_in_opengrimoire)** (**STK-***). | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md) |
| OA-1 | pending | **Maintain OpenGrimoire systems inventory** — Keep [OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md](../../OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md) accurate when adding routes, APIs, scripts, or security flags. **Inventory must list:** app routes, API routes, `build_brain_map.py` + env vars, npm scripts, Playwright, Docker, alignment HTTP API, key docs; **must link (not duplicate)** full MCP server matrix from MCP_CAPABILITY_MAP. | [OPENGRIMOIRE_SYSTEMS_INVENTORY.md](../../OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md) |
| OA-OG-2 | deferred | **Admin alignment UI:** React Query/SWR / SSE — not in this slice; focus/visibility refetch already meets contract baseline. | [admin/alignment/page.tsx](../../OpenGrimoire/src/app/admin/alignment/page.tsx) |
| OA-OG-5 | deferred | **P1:** A2UI on `/capabilities` — deferred until product scope explicitly requires agent-rendered discovery UI. | Scope R7 |

---

## PENDING_OG_GUI_RELEASE

**Purpose:** Aggregate **dimension action items** + architecture follow-ups from [OpenGrimoire `docs/audit/gui-2026-04-16-opengrimoire-survey.md`](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-survey.md) into a **waved, decomposed release** (R1 → R2 → R3). **Wave plan:** [WAVED_PENDING_TASKS.md](../../local-proto/docs/WAVED_PENDING_TASKS.md) — **Wave 10 — OG GUI release (decomposed)**. **Portfolio row:** [GUI_AUDIT_PORTFOLIO_INDEX.md](../docs/audit/GUI_AUDIT_PORTFOLIO_INDEX.md).

| ID | Status | Release | Task | Spec / Link |
|----|--------|---------|------|-------------|
| OG-GUI-01 | pending | R1 | Execute BrowserReviewSpec flows; attach Playwright report or screenshots (intake, `/survey` redirect, login → admin moderation) | [gui-2026-04-16-opengrimoire-survey.md](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-survey.md) § BrowserReviewSpec |
| OG-GUI-02 | pending | R1 | Playwright: after `loginAsAdmin`, `/admin` moderation **UI** asserts when queue non-empty | Same audit § Dimension action items (1) |
| OG-GUI-03 | pending | R1 | Optional CI: `SURVEY_POST_REQUIRE_TOKEN` on webServer to run skipped survey token tests | `e2e/survey.spec.ts`, `playwright.config.ts` |
| OG-GUI-04 | pending | R2 | axe-playwright (or BrowserStack a11y MCP) on `/operator-intake` + `/admin` | Audit dim 3 |
| OG-GUI-05 | pending | R2 | Copy pass: Sync Session — network fail, 429, survey post token 401 — user strings + recovery | Audit dim 2 |
| OG-GUI-06 | pending | R2 | Visual baselines (Chromatic/Percy) when intake or admin moderation table changes | Audit dim 4 |
| OG-GUI-07 | pending | R3 | Single source for Playwright default secrets (config + `e2e/helpers/e2e-secrets.ts`) | Architecture note in audit |
| OG-GUI-08 | pending | R3 | Dedupe read-gate 401 `detail` vs capabilities / ARCHITECTURE (constant or generator) | Audit § Automation vs gaps |
| OG-GUI-09 | pending | R3 | Harden `verify-moderation-auth-purity.mjs` (ESLint or import test) — optional | `scripts/verify-moderation-auth-purity.mjs` |
| OG-GUI-10 | pending | R3 | Production-profile smoke for survey read gate (`NODE_ENV=production` + header matrix) | Audit § Automation vs gaps |
| OG-GUI-A2 | pending | R2/R3 | **A2UI monitor:** no decorative-only component names in `AdminPanel`; when first agent-rendered admin ships, add catalog semantics (links **OA-OG-5**) | Audit dim 5 |

**Exit (whole wave):** R1–R3 exit criteria in WAVED Wave 10; mark rows `done` and run `split_done_tasks_to_completed.py` when appropriate.

---

## PENDING_AGENT_NATIVE

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AN1 | pending | **Agent-native audit** — Eight-principle scorecard lives in **[`AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md`](../../OpenGrimoire/docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md)** (2026-04-16; System 2 + shared survey/API). System 1 GUI desk audit: [`gui-2026-04-16-opengrimoire-survey.md`](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-survey.md). System 2 GUI + dimension todos: [`gui-2026-04-16-opengrimoire-data-viz.md`](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md). **Closure:** implement or waive **OGAN-*** backlog (below), then set AN1 `done` + `split_done_tasks_to_completed.py`. | [AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md](../../OpenGrimoire/docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md) |

### PENDING_OPENGRIMOIRE_AGENT_NATIVE_DECOMPOSED (OGAN — from scorecard + GUI audit)

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OGAN-01 | pending | **UI integration:** Refetch `/visualization` data + approved quotes after successful `POST /api/survey` and after moderation `PATCH` (shared cache key, `router.refresh`, focus listener, or bounded poll). | [AGENT_NATIVE_AUDIT §P1](../../OpenGrimoire/docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md) |
| OGAN-02 | pending | **`GET /api/capabilities`:** Add `workflows` / `ui_surfaces` entries for `/visualization`, `/constellation`, `?all=1` vs `showTestData`+`all=0`, prod gate hints. | §P2 |
| OGAN-03 | pending | **Action parity (optional):** New gated `GET` returning survey rows + optional precomputed graph payload **or** document that agents must run `processVisualizationData` locally / via browser. | §P3 |
| OGAN-04 | pending | **Shared workspace UX:** Banner when `useVisualizationData` uses mock fallback or `isMockData` (no silent fake cohort). | §P4 · [gui data-viz dimension 1](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md) |
| OGAN-05 | pending | **OpenAPI:** Response schemas for `GET /api/survey/visualization` and `GET /api/survey/approved-qualities` bodies; align `verify-openapi` if present. | §P5 |
| OGAN-06 | pending | **Single client module** for visualization fetches (`?all=1` vs `all=0`+`showTestData`) consumed by hook + Zustand + export paths. | §P6 |
| OGAN-07 | pending | **Context injection:** Find root `## Master System Prompt*` (or similar); archive, delete, or rewrite for SQLite + current APIs. | §P7 |
| OGAN-08 | pending | **Docs:** Mark `/test*`, `/test-chord` mock paths as **non-contractual** in `AGENT_INTEGRATION.md` and/or capabilities prose. | §P8 |
| OGAN-09 | pending | **Product decision + API (optional):** Persist operator viz prefs (theme, autoplay, colors) behind authenticated routes if agent parity is required without browser. | §P9 |
| OGAN-10 | pending | **Backlog / future:** Versioned chart-spec JSON + thin renderer (prompt-native path); only if product commits. | §P10 |
| OGAN-11 | pending | **Doc hygiene:** Reconcile `AGENT_TOOL_MANIFEST.md` vs older plans mentioning missing `mcp-server/` paths; fix broken links. | [AGENT_NATIVE §2](../../OpenGrimoire/docs/AGENT_NATIVE_AUDIT_OPENGRIMOIRE.md) |
| OGAN-12 | pending | **Logging:** Gate or remove hot-path `console.log` in `visualization/ConstellationView.tsx` and `visualizationStore` (PUBLIC_SURFACE_AUDIT F4). | [gui data-viz follow-ups](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md) |
| OGAN-13 | pending | **NavigationDots:** Remove dead `/tapestry` `/comparison` `/waves` `/qualities` links or add real `app/` routes. | [OA_FR_2 G-S2-04](../../OpenGrimoire/docs/plans/OA_FR_2_SYSTEM2_DATA_VISUALIZATION.md) |
| OGAN-14 | pending | **Codebase:** Delete or merge orphan `src/components/DataVisualization/Constellation/` (unused by App Router). | OA-FR-2 · strategist |
| OGAN-15 | pending | **A11y:** Run axe-playwright on `/visualization` and `/constellation`; file issues for Three canvas focus. | [gui data-viz §3](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md) |
| OGAN-16 | pending | **E2E:** Assert network query shape differs `/visualization` vs `/constellation` (smoke against `?all=1` vs `all=0` drift). | [gui data-viz automation gaps](../../OpenGrimoire/docs/audit/gui-2026-04-16-opengrimoire-data-viz.md) |
| OGAN-17 | pending | **Agent docs:** Document Playwright selectors (`vizLayoutIds`, `data-testid`, `data-region`) for external harnesses; link from OA-FR-2 verification. | OA-FR-2 |

---

## PENDING_CREDENTIALS (human checklist from setup_env.py)

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| CR1 | pending | PentAGI: Add INSTALLATION_ID, LICENSE_KEY (PentAGI Cloud) | [pentagi/.env](../../pentagi/.env) |
| CR2 | pending | PentAGI: Add OAUTH_* if using OAuth (Google/GitHub) | [pentagi/.env](../../pentagi/.env) |
| CR3 | pending | PentAGI: Add TAVILY_API_KEY, PERPLEXITY_API_KEY, etc. (search APIs; DuckDuckGo is free) | [pentagi/.env](../../pentagi/.env) |
| CR4 | pending | local-proto: Add CRAIGSLIST_EMAIL, CRAIGSLIST_PASSWORD (for browser flows) | [local-proto/.env](../../local-proto/.env) |
| CR5 | pending | local-proto: Add CURSOR_API_KEY (orchestrator) | [local-proto/.env](../../local-proto/.env) |
| CR6 | pending | OpenGrimoire: Add NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY | [OpenGrimoire/.env](../../OpenGrimoire/.env) |

**Note:** LLM and embeddings use Ollama by default (no API keys). Run `python .cursor/scripts/setup_env.py --force` to regenerate with Ollama defaults.

**Audit (redacted, no secrets printed):** `python .cursor/scripts/audit_pending_credentials.py` — see [.cursor/docs/TWO_MACHINE_ENV.md](../docs/TWO_MACHINE_ENV.md) for two-machine and `--also` usage.

---

## PENDING_ALIGNMENT

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AL2 | in_progress | Bitcoin-Chaos Convergence: Execute plan phases A–C. Expect gap of operations; planning phase. | [bitcoin_chaos_convergence plan](../../plans/bitcoin_chaos_convergence_a219e7b9.plan.md), [integration plan](../../plans/bitcoin_chaos_convergence_integration_827d4828.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #19 |
| C4 | pending | Fedimint testnet exploration (3–5 guardian; AuthModule design) | deep-research-report §7 |
| C5 | pending | Capability token schema (Fedimint-native or standalone) | PentAGI protocol; deep-research-report §4 |
| C4a | pending | Fedimint AuthModule design doc: Document AuthModule interface, capability token flow, and harness integration points (per deep-research-report §7) | [FEDIMINT_AUTHMODULE_DESIGN_TARGET.md](../../docs/FEDIMINT_AUTHMODULE_DESIGN_TARGET.md) |
| CRY1 | pending | secp256k1 / AuthModule: Implement or integrate capability token signing (blocked on C4/C5; design in FEDIMINT_AUTHMODULE_DESIGN_TARGET.md) | [FEDIMINT_AUTHMODULE_DESIGN_TARGET.md](../../docs/FEDIMINT_AUTHMODULE_DESIGN_TARGET.md) |
| CRY2 | pending | hb-4 escalation tools: Wire capability token verification to escalation_tools when CRY1 available | [org-intent.bitcoin-inspired.json](../../org-intent-spec/examples/org-intent.bitcoin-inspired.json) |
| AL5 | pending | Build the Anti-Basilisk: harness + Bitcoin + SCP — protective mycology defending humans from unaligned/hostile AI | Block 11 outro; [goals.json](goals.json) anti-basilisk |

---

## PENDING_LOCAL_FIRST

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| LF1 | pending | Local-first sync engine: Document stack choice (Electric/PowerSync/p2panda) per LOCAL_FIRST_STACK_CHOICE.md; log to scope-notes.md | [LOCAL_FIRST_STACK_CHOICE.md](../../local-proto/docs/LOCAL_FIRST_STACK_CHOICE.md) |

---

## PENDING_MODEL_ROUTER (local-first)

**Purpose:** Implement the **local-first model router** after [LOCAL_FIRST_MODEL_ROUTER_SPEC.md](../docs/LOCAL_FIRST_MODEL_ROUTER_SPEC.md) (hardware-aware execution vs verification; no silent cloud). **Spec + examples + cross-links:** done (G5). **Ordered backlog:**

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| MR1 | pending | **Core resolver (pure):** Implement `resolve_models` (or equivalent) — inputs: `task_type`, `risk_tier`, hardware profile YAML, `available_models`, orchestrator char caps; outputs: `execution_model`, `verification_model`, `verification_skipped_reason`, `verification_channel` per spec §3–§4. No Ollama calls inside pure function. | [LOCAL_FIRST_MODEL_ROUTER_SPEC.md](../docs/LOCAL_FIRST_MODEL_ROUTER_SPEC.md), [AI_TASK_EVALS.md](../docs/AI_TASK_EVALS.md) Model-Floor Table |
| MR2 | pending | **Operator CLI:** Script to load profile from `.cursor/private/hardware_profile.yaml` (or `--profile`), fetch `ollama list` / `--models-file`, emit resolved pair (stdout JSON) and optional `--dry-run` / `--write-config` patch of `execution_model` + `verification_model` only. | [examples/hardware_profile.yaml.example](../docs/examples/hardware_profile.yaml.example), [ORCHESTRATOR_CONFIG.md](../../local-proto/docs/ORCHESTRATOR_CONFIG.md) |
| MR3 | pending | **Config schema (optional keys):** Add `hardware_profile`, `model_router_config_path` to `orchestrator_config.example.json` + document in ORCHESTRATOR_CONFIG Fields table when MR4 consumes them. | [ORCHESTRATOR_CONFIG.md](../../local-proto/docs/ORCHESTRATOR_CONFIG.md) § Future — model router |
| MR4 | pending | **Orchestrator integration:** Call resolver at handoff processing start (or read env `ORCHESTRATOR_EXECUTION_MODEL` / pre-resolved JSON); apply `verification_hourly_budget` via state_dir counter file; respect `verification_enabled` and existing same-tag skip. | [`orchestrator.py`](../scripts/orchestrator.py), spec §7 |
| MR5 | pending | **Observability:** Append structured `router_decision` (or spec §4.2 fields) to `agent_log.jsonl` / `log_agent_event.py` when router runs. | [.cursor/state/README.md](README.md), spec §4.2 |
| MR6 | pending | **Tests:** Unit tests with fixtures — installed-model clamp, moral-boundary override rejection without `human_exception`, budget_exhausted path, same-tag → skip reason. | `local-proto/tests/` or `.cursor/scripts/` test layout per repo convention |
| MR7 | pending | **Runbook:** One short “daily / new machine” checklist — copy `hardware_profile.yaml.example`, run MR2 CLI, confirm `ollama list`, run `run_model_floor_evals.ps1` after model pull. | [COMMANDS_README.md](../docs/COMMANDS_README.md) or ORCHESTRATOR_CONFIG § Reducing silent misconfiguration |
| MR8 | pending | **Docs hygiene:** Remove or stub broken `CONTINUAL_LEARNING_EXTRACTORS.md` links (AI_TASK_EVALS, scripts) — replace with [.cursor/state/README.md](README.md) anchor or add minimal `CONTINUAL_LEARNING_EXTRACTORS.md` that points to continual-learning flow. | Grep `CONTINUAL_LEARNING_EXTRACTORS` |

---

## PENDING_GWS_MANUAL (human checklist)

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| GW1 | pending | Run `gws auth login -s drive,gmail,sheets` (or desired scopes) to authenticate | [GWS_INTEGRATION.md](../../docs/GWS_INTEGRATION.md) |
| GW2 | pending | For OpenClaw: `npx skills add https://github.com/googleworkspace/cli` | [GWS_INTEGRATION.md](../../docs/GWS_INTEGRATION.md), [OPENCLAW.md](../../local-proto/docs/OPENCLAW.md) |
| GW3 | pending | For headless/CI: `gws auth export --unmasked > credentials.json`; store path in credential-vault under key `gws` | [GWS_INTEGRATION.md](../../docs/GWS_INTEGRATION.md) |

---

## PENDING_OTHER

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| H2 | pending | Run continual-learning once transcripts exist to populate AGENTS.md | [run_continual_learning_prompt.ps1](../scripts/run_continual_learning_prompt.ps1), [SKILL_SELF_IMPROVEMENT_WINS.md](../docs/SKILL_SELF_IMPROVEMENT_WINS.md) |
| H5 | pending | **Agent Korean-language switch:** Investigate and fix unexpected Korean responses when user sends short prompts (e.g. "do it") in English context. Check .cursorrules, workspace rules, language-preference handling. | [known-issues.md](known-issues.md) §Agent behavior. **What AI needs:** Confirmation fixed vs still happening. .cursorrules has "Respond in English unless user requests otherwise"; no "Always Korean" rule found. **Human:** Test "do it" in new chat; report (a) still Korean or (b) fixed. |

---

## PENDING_AI_TRENDS

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AT3b | pending | AI Trends MCP: Playwright E2E when Gradio UI exists — placeholder skip in `test_ai_trends_gradio_e2e.py`. | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md). Blocked: no Gradio UI in current design. |

---

## PENDING_PORTABLE_AI_MEMORY (BYOC, session DB, vault harness)

**Purpose:** Continue threads from **2026-04-17** Cursor work — Nate B Jones / **BYOC** (“fifth capital”, MCP pull, honing vs lock-in), **cryptography layers** (SHA / signing / encryption vs L402), **Obsidian** session persistence + **Harness/** mirror. Composes with **SCP-ANT1**, **CHAOS_BITCOIN_MAPPING**, **AI Trends** archive index.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| BYOC-1 | pending | **AI Trends ingest (canonical video):** When operator supplies YouTube URL / playlist config for Nate B Jones (or other named BYOC source), ingest transcript → `raw/{date}/`; run `ai_trends_archive_index.py --date …`; optional `scp_analyze_ai_trends` / stack_intel. Ties BYOC thesis to **SHA-256 manifest** row. | [adhoc/2026-04-17_nate-b-jones-byoc-working-intelligence.md](adhoc/2026-04-17_nate-b-jones-byoc-working-intelligence.md); [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § Archive index |
| BYOC-2 | pending | **External research doc:** Expand portable / signed / hash-anchored **AI context** stacks (Nostr, IPFS CID workflows, W3C VC, age/minisign, `@modelcontextprotocol/server-memory` limits) into **`docs/research/`** or **`docs/brainstorms/`** — comparison table: integrity vs confidentiality vs payment; cross-ref [SCP-ANT1](../../docs/superpowers/specs/2026-04-12-scp-antigen-l402-design.md), [CHAOS_BITCOIN_MAPPING](../../docs/CHAOS_BITCOIN_MAPPING.md), [BITCOIN_AGENT_CAPABILITIES](../../docs/BITCOIN_AGENT_CAPABILITIES.md) | Same adhoc § External patterns; [CASHU_L402_REFERENCE](../../docs/CASHU_L402_REFERENCE.md) |
| BYOC-3 | pending | **Obsidian discoverability:** Add `docMappings` in `sync_harness_to_vault.ps1` **or** keep a **vault-owned** one-pager under `LLM-Wiki/` linking to repo adhoc (do **not** edit `Harness/` as SSOT) so BYOC synthesis is searchable from Obsidian | [OBSIDIAN_VAULT_INTEGRATION.md](../docs/OBSIDIAN_VAULT_INTEGRATION.md); [HARNESS_VAULT_WRITE_CONTRACT.md](../../local-proto/docs/HARNESS_VAULT_WRITE_CONTRACT.md) |
| BYOC-4 | pending | **VSH-1 / fork-3 decision:** `write_handoff.py` now writes **`sessions.db`** via [handoff_vault_session.py](../scripts/handoff_vault_session.py) — update **VSH-1** narrative or mark **done** if fork-3 markdown blob export is waived; else spec remaining blob export | [OBSIDIAN_VAULT_INTEGRATION § Session-Handoff](../docs/OBSIDIAN_VAULT_INTEGRATION.md#session-handoff-vault-artifact); [§ PENDING_FUTURE](#pending_future) VSH-1 |
| BYOC-5 | pending | **Vault DB hygiene (optional):** Delete stray **`smoke-test`** `write_handoff` session row from `.cursor_context/sessions.db` (2026-04-17 dev smoke) if operator wants a clean history | `%OBSIDIAN_VAULT_ROOT%/.cursor_context/sessions.db` |
| BYOC-6 | pending | **Agent-native checklist pass:** Map BYOC four layers + MCP pull + user-owned DB to harness **action parity** doc — short outcome: gaps vs [AGENT_ENTRY_INDEX.md](../docs/AGENT_ENTRY_INDEX.md) checklist / OpenHarness `AGENT_NATIVE_CHECKLIST.md` | [HANDOFF_FLOW.md](../HANDOFF_FLOW.md) vault §; agent-native checklist chain from AGENT_ENTRY_INDEX |

---

## PENDING_AFTER_RESTART

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| R1 | pending | **obsidian-vault MCP:** Check Cursor Settings → MCP; confirm obsidian-vault shows running or has errors | Session 2026-03-11. **What AI needs:** Whether MCP is running. Check Cursor Settings → MCP. If obsidian-vault tools (session_save, apply_patch, vault_search) not in agent list, MCP may not be loaded. **Human:** Report obsidian-vault status. |
| R3 | pending | **Critic follow-up:** Apply critic fixes (known-issues obsidian-vault entry; SKILL.md guardrail; AI_TASK_EVALS; TEST_PROMPTS procedure; test_mcp_and_audit skip) | Critic report 2026-03-11. **What AI needs:** Which fixes to apply. Options: (1) known-issues obsidian-vault entry; (2) foam-pkm SKILL.md guardrail (prefer apply_patch); (3) AI_TASK_EVALS; (4) TEST_PROMPTS procedure; (5) test_mcp_and_audit skip for obsidian-vault. **Human:** Choose all or subset. |

---

## PENDING_SCP_COGNITOHAZARD_LIVE

**Purpose:** Live test = **SCP technical classification** (`scp_inspect`, `scp_run_pipeline`, optional `scp_mask_secrets`) **+ operator protocol** — not a second ML gate. There is **no** automated cognitohazard detector in code; [WELLBEING_TRIGGER_LAYER_DESIGN.md](../docs/WELLBEING_TRIGGER_LAYER_DESIGN.md) remains **design-only** until SCP-CH4/CH5.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| SCP-CH1 | pending | **Live operator run:** Paste critic article (or approved file path); run `scp_inspect` + `scp_run_pipeline` per live-run doc; do not treat `clean` as psychological safety | [cognitohazard_scp_live_run.md](cognitohazard_scp_live_run.md) |
| SCP-CH2 | pending | **Post-run logging:** Record tier, categories, blocked, content hash in metadata only; **no** full article in handoff/state unless operator approves | Same + [AGENT_TELEMETRY.md](../docs/AGENT_TELEMETRY.md) |
| SCP-CH4 | pending | **Future — wellbeing layer:** Revisit [WELLBEING_TRIGGER_LAYER_DESIGN.md](../docs/WELLBEING_TRIGGER_LAYER_DESIGN.md) §6 go/no-go when product priority allows (still **not** a substitute for operator protocol) | Design doc |
| SCP-CH5 | pending | **Future — if wellbeing implemented:** Prefer separate MCP tool or documented `scp_run_pipeline` option per design §4; **separate** eval row in AI_TASK_EVALS — **never** merge pass/fail with SCP injection/reversal tiers | [WELLBEING_TRIGGER_LAYER_DESIGN.md](../docs/WELLBEING_TRIGGER_LAYER_DESIGN.md), [AI_TASK_EVALS.md](../docs/AI_TASK_EVALS.md) |

---

## PENDING_SCP_SAAS_MYCELIUM (instrumental: money + fame)

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| SCP-SAAS1 | pending | **SCP SaaS Mycelium Network Defense** — Ship SCP-as-SaaS MCP server with collective threat intelligence. Phase 1 (local + promptfoo eval) done; 16/16 red-team prompts pass. | [scp_saas_mycelium plan](D:\software\.cursor\plans\scp_saas_mycelium_network_defense_4dd995ea.plan.md), [design doc](../../docs/plans/2026-03-12-scp-saas-mycelium-design.md), [LEARNINGS_PROMPTFOO.md](../skills/secure-contain-protect/LEARNINGS_PROMPTFOO.md) |

**Shared threat registry (mycelium) — task decomposition:**

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| SCP-R1 | pending | **Schema & API design** — Define threat pattern schema (anonymized format), contribution API, fetch API. No PII or raw content. | [design doc](../../docs/plans/2026-03-12-scp-saas-mycelium-design.md) |
| SCP-R2 | pending | **Repository setup** — Create open-source repo (GitHub/GitLab) for shared threat registry; license (MIT/CC), governance, contribution guidelines. | scp_saas_mycelium plan §Approach B |
| SCP-R3 | pending | **Contribution flow** — `scp_contribute_pattern` tool (or equivalent); human gate before submit; anonymization pipeline. | frontier-ops seam design; design doc §CL4R1T4S |
| SCP-R4 | pending | **Fetch flow** — `scp_fetch_registry` tool; merge with local `threat_registry.json`; fallback to local on network failure. | design doc §Recovery |
| SCP-R5 | pending | **MCP integration** — Wire SCP MCP to optionally use shared registry; all SCP instances can pull. Demo: Block 5 future vision. | [CONTEXT_ENGINEERING_DEMO_CHEATSHEET](../docs/CONTEXT_ENGINEERING_DEMO_CHEATSHEET.md) §Block 5 |
| SCP-R6 | pending | **Privacy & consent** — Anonymization spec; explicit permission before contribution; document in contribution guidelines. | design doc §Collective Learning |
| SCP-ANT1 | pending | **Decentralized antigen mesh + L402** — Local-first documentation of malicious AI/code experiences; export **antigens** (signed threat-pattern bundles) to a **node-based** registry (no single mandatory hub; contrasts with one public repo in SCP-R2 if that feels too centralized). Optional **L402** / Cashu / x402 so sellers (humans or agents) can **charge** for antigen pulls or curated feeds. Composes with SCP-R1 schema; trust/reputation and Sybil resistance are open design problems. | [ANT1 equal-weight design spec](../../docs/superpowers/specs/2026-04-12-scp-antigen-l402-design.md); [SCP_PARASITIC_DYNAMICS_POSTURE.md](../docs/SCP_PARASITIC_DYNAMICS_POSTURE.md); [CASHU_L402_REFERENCE](../../docs/CASHU_L402_REFERENCE.md); [BITCOIN_AGENT_CAPABILITIES](../../docs/BITCOIN_AGENT_CAPABILITIES.md); [mycelium design](../../docs/plans/2026-03-12-scp-saas-mycelium-design.md) |

**How to get it running and generating money + fame:**

- ~~**Fix inj-4 gap**~~ — Done (2026-03-12): path_traversal patterns in sanitize_input.py; all 16/16 pass.
- **Ship promptfoo YAML config** — Add `promptfoo-scp.yaml` so users can run `npx promptfoo eval -c promptfoo-scp.yaml`; lowers friction, increases adoption.
- **Host SCP as SaaS MCP** — Deploy SCP MCP server (e.g. Fly.io, Railway, or self-host); agents connect via MCP URL. Enables "SCP as a service" for teams without local setup.
- **Shared threat registry (mycelium)** — SCP-R1..SCP-R6 above. Add optional network layer: anonymized pattern contributions, pull of shared registry. Each node contributes; all benefit. Differentiator vs single-org tools.
- **Decentralized antigen marketplace (SCP-ANT1)** — Optional mesh + micropayments: agents and operators sell or subscribe to high-signal antigens without depending on one global GitHub registry; pairs with L402 docs in repo.
- **Red-team reports as product** — Run promptfoo + SCP evals; sell or publish "AI security posture reports" for enterprises. OWASP LLM Top 10 alignment = compliance angle.
- **Conference / blog visibility** — Submit to AI security tracks (Black Hat, DEF CON AI Village, OWASP); write "Mycelium defense for LLM apps" post. promptfoo (12.7k stars) + novel collective-learning angle = shareable.
- **MCP Registry listing** — Submit SCP MCP to [MCP Registry](https://github.com/modelcontextprotocol/servers); discoverability for Cursor/Claude users.
- **Enterprise tier** — On-prem deployment, custom threat registry, SLA. Revenue from security-conscious orgs (finance, healthcare, gov).

---

## PENDING_BLUE_HAT

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| BH0 | pending | **Bitcoin Core regtest setup** — Install Bitcoin Core >= 26; run Stealth `setup.sh` per secure runbook. | [STEALTH_E2E_SECURE_RUNBOOK.md](../../local-proto/docs/STEALTH_E2E_SECURE_RUNBOOK.md), [BLUE_HAT_STEALTH_STATUS.md](../../local-proto/docs/BLUE_HAT_STEALTH_STATUS.md) |
| BH1 | pending | **Stealth integration** — Client in `local-proto/scripts/stealth_client.py`; `blue_hat_privacy_review.py` imports it. Run backend (Quarkus) + Bitcoin Core for full E2E. | [2026-03-12-blue-hat-bitcoin-design.md](../../docs/plans/2026-03-12-blue-hat-bitcoin-design.md), [Stealth README](https://github.com/LORDBABUINO/stealth) |
| BH2 | pending | **Manual TEST_PROMPTS** — Run 5 prompts from `.cursor/skills/blue-hat-bitcoin/TEST_PROMPTS.md` in new chat; record pass/fail. | [TEST_PROMPTS.md](../skills/blue-hat-bitcoin/TEST_PROMPTS.md) |
| BH3 | pending | **Fedimint (when C4/C5 ready)** — Add privacy_review capability token and LogEvent for each review. | [FEDIMINT_AUTHMODULE_DESIGN_TARGET.md](../../docs/FEDIMINT_AUTHMODULE_DESIGN_TARGET.md) §When C4/C5 Ready |

---

## PENDING_SCP_PROOF (user wants visual proof)

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| SCP1 | pending | **SCP Daggr UI:** Run `python -m daggr_workflows.run_workflow scp` from portfolio-harness; open Gradio in browser; paste test content; show inspect + pipeline result on screen. User must SEE the SCP Gradio page in Cursor/browser. | [daggr_test_matrix.md](../docs/daggr_test_matrix.md), [scp_pipeline.py](../../daggr_workflows/scp_pipeline.py) |
| SCP2 | pending | **Foam / Playwright proof:** Use cursor-ide-browser or Playwright MCP to navigate to a Foam/Obsidian page OR run a Playwright smoke test that opens a visible page. User expects "foam and or playwright web pages showing up on my cursor screen." | [browser-web SKILL](../skills/browser-web/SKILL.md), [foam-pkm SKILL](../skills/foam-pkm/SKILL.md), [test_daggr_playwright_smoke.py](../../WatchTower_main/WatchTower_main/tests/e2e/test_daggr_playwright_smoke.py) |
| SCP3 | pending | **Feature-video / test-browser style:** Record a short walkthrough (screenshots → video/GIF) showing SCP Gradio UI, Foam note creation, or Daggr Playwright smoke—per /feature-video and /test-browser command patterns. Deliver: visible proof that SCP + Daggr + Foam/Playwright work. | [e2e_playwright_browserstack plan](D:\software\.cursor\plans\e2e_playwright_browserstack_foam_cf7aa656.plan.md) |

---

## PENDING_BRAIN_MAP

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| BM-A11Y | pending | **BrowserStack MCP + Brain Map a11y:** Configure BrowserStack credentials in MCP; start Local (or use staging URL); run `startAccessibilityScan` and `accessibilityExpert` on Brain Map viewer (standalone and/or OpenGrimoire); append rows to **BrowserStack scan log** in [docs/BRAIN_MAP_AUDIT.md](../../docs/BRAIN_MAP_AUDIT.md) and in OpenHarness `docs/BRAIN_MAP_AUDIT.md` (public harness clone) with scan ID, scan run ID, URL, date. **Template row + viz tab keyboard (ArrowUp/Down) landed 2026-03-20; cloud scan still operator-dependent.** | [BRAIN_MAP_E2E.md](../../docs/BRAIN_MAP_E2E.md) Step 8, [BRAIN_MAP_AUDIT.md](../../docs/BRAIN_MAP_AUDIT.md) |

---

## PENDING_OBSIDIAN_BRAIN_VAULT

**Purpose:** Persist **2026-04-17 Cursor vault audit** outcomes (numeric passes, graph hygiene, agent-native parity gaps) so they are not lost in chat. **Canonical vault path:** sibling `Arc_Forge/ObsidianVault` (Obsidian app “vault name” can differ from folder name). Composes with **NEXT-3**, **BYOC-6**, [Vault-meta `GRAPH_VIEWS`](../../../Arc_Forge/ObsidianVault/Vault-meta/GRAPH_VIEWS.md), [Graph_and_lint_dashboard](../../../Arc_Forge/ObsidianVault/Vault-meta/Graph_and_lint_dashboard.md). **Harness mirror:** after changing this file, run `local-proto/scripts/sync_harness_to_vault.ps1` so `Harness/Pending-Tasks.md` stays aligned.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OBV-0 | pending | **Audit snapshot (reference):** Vault-wide **258** `.md` (excl. noise paths); **§2 graph slice** **183** files; **105** strict orphans (wikilink-only parser); **95** strict orphans in §2; **137** files zero outgoing `[[wikilinks]]`; **3** ambiguous multi-stem link events; **7×** `README.md` stem collision + **2×** `task_decomposition`; super-hub **MOC_Harness_State** ~114–115 incoming wikilinks. Re-run counts after major merges. | [adhoc/2026-04-17_obsidian_vault_audit_snapshot.md](adhoc/2026-04-17_obsidian_vault_audit_snapshot.md) |
| OBV-1 | pending | **Orphan budget (§2):** Define numeric target (e.g. strict §2 orphans &lt; N) + completion signal for “caption merge” passes; link from [[Graph_and_lint_dashboard]] or weekly note. | [Vault-meta Graph_and_lint_dashboard](../../../Arc_Forge/ObsidianVault/Vault-meta/Graph_and_lint_dashboard.md) |
| OBV-2 | pending | **Link convention:** Document when harness-side notes use `[[wikilinks]]` vs Markdown `[](path)` so Obsidian graph + agent grep agree; add one example to `00_VAULT_RULES` or `Vault-meta`. | [00_VAULT_RULES.md](../../../Arc_Forge/ObsidianVault/Vault-meta/00_VAULT_RULES.md) |
| OBV-3 | pending | **README / ambiguous stems:** Disambiguate or rename colliding `README` notes; agent rule: path-qualified `[[folder/README]]` only for those paths. | OBV-0 counts |
| OBV-4 | pending | **§2b metrics script:** Read-only PowerShell (or extend existing vault scripts) for **GRAPH_VIEWS §2b** (−`Handoff-archive`) — file counts + strict orphans + top hubs; same exclusions as §2. | [GRAPH_VIEWS.md](../../../Arc_Forge/ObsidianVault/Vault-meta/GRAPH_VIEWS.md) §2b |
| OBV-5 | pending | **`domain/harness` outside §2 paths:** List the **4** files tagged harness but not under Harness/LLM-Wiki/Vault-meta/Pointers/research/docs/.cursor_context; retag or relocate per `00_VAULT_RULES`. | Pass-2 audit |
| OBV-6 | pending | **Entity template:** Replace hard-coded `campaign/redacted_records` placeholder in `Templates/entity_note.md` with neutral placeholder + doc reminder. | `Arc_Forge/ObsidianVault/Templates/entity_note.md` |
| OBV-7 | pending | **Hub diet / blast radius:** Review **MOC_Harness_State** fan-in; optional sub-MOCs by theme/wave so renames and cognitive load stay bounded; `alwaysUpdateLinks` already on in vault `app.json`. | `Harness/MOC_Harness_State.md` |
| OBV-8 | pending | **Agent parity row:** Add AGENT_ENTRY_INDEX (or MCP doc) entry — agents can run the same read-only audit script(s) + paths (`OBSIDIAN_VAULT_ROOT`, §2 definition). | [AGENT_ENTRY_INDEX.md](../docs/AGENT_ENTRY_INDEX.md), **BYOC-6** |
| OBV-9 | pending | **Optional CI / cadence:** Monthly run of orphan/hub metrics → one line in handoff or `LLM-Wiki/log` (no blocking CI unless desired). | HANDOFF_FLOW |
| OBV-10 | pending | **“Obsidian Brain” branding / rename:** Decide scope — (A) Obsidian **vault display name** only (“Obsidian Brain” in app, folder stays `ObsidianVault` for scripts), (B) **rename folder** + migration checklist (`OBSIDIAN_VAULT_ROOT`, MCP, `sync_harness_to_vault`, `BRAIN_MAP_VAULT_ROOTS`, workspace roots). **Do not** rename folder until checklist + **WS-PRIV-7**-style gate if paths are wide. | [WORKSPACE_PATH_ENV_CHECKLIST.md](../../local-proto/docs/WORKSPACE_PATH_ENV_CHECKLIST.md); [HARNESS_VAULT_WRITE_CONTRACT.md](../../local-proto/docs/HARNESS_VAULT_WRITE_CONTRACT.md) |
| OBV-11 | pending | **Default entry note (“this month”):** Pick one door (START_HERE vs operator MOC vs daily); align first row of `START_HERE.md` if habit drifted. | `Arc_Forge/ObsidianVault/START_HERE.md`, `MOC_Operator_Base_Camp.md` |
| OBV-12 | pending | **Align vault canon with Brain Map hub:** Ensure `Vault-meta` / `START_HERE` link to [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md) and `BRAIN_MAP_VAULT_*` env vars where operator should enable vault nodes in context atlas. | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md) § env table |

---

## PENDING_STACK_ATLAS_OPENHARNESS_IN_OPENGRIMOIRE

**Purpose:** **Surveillance + closure** for “I want OpenHarness **in** OpenGrimoire” and **software stack / directory layout** pain — without ad-hoc moves. OpenGrimoire already hosts **Brain Map** at `/context-atlas` fed by `build_brain_map.py`; OpenHarness narrative state can appear as a **second state root** via `CURSOR_STATE_DIRS` / `CURSOR_STATE_DIR_LABELS` ([BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md) multi-root). This section tracks **recon**, **config**, **docs**, and **optional UI** work. Composes with **WS-PRIV-2**, **WS-PRIV-4**, **NEXT-1**, **OA-1**, **BM-A11Y**.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| STK-0 | pending | **Recon checklist (fill in paths):** Document on-disk locations of **MiscRepos**, **OpenGrimoire**, **OpenHarness** (if cloned), **Arc_Forge/ObsidianVault**; current values of `CURSOR_STATE_DIRS`, `CURSOR_STATE_DIR_LABELS`, `BRAIN_MAP_VAULT_ROOTS`, `BRAIN_MAP_VAULT_LABELS`, `BRAIN_MAP_OUTPUT`, `OBSIDIAN_VAULT_ROOT`. One table, one owner per row. | [REPO_BOUNDARY_INDEX.md](../../local-proto/docs/REPO_BOUNDARY_INDEX.md); [HITL_CONNECTIVITY.md](../../local-proto/docs/HITL_CONNECTIVITY.md) |
| STK-1 | pending | **Wire OpenHarness into Brain Map build:** After STK-0, add OpenHarness `.cursor/state` (or agreed path) to **`CURSOR_STATE_DIRS`** (semicolon-separated) + matching **`CURSOR_STATE_DIR_LABELS`** so `/context-atlas` shows a **labeled layer** for harness handoffs; rebuild JSON and verify in OpenGrimoire. | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md) Data flow + multi-root; [build_brain_map.py](../scripts/build_brain_map.py) |
| STK-2 | pending | **Vault nodes in same graph (optional):** Set **`BRAIN_MAP_VAULT_ROOTS`** to `Arc_Forge/ObsidianVault` and **`BRAIN_MAP_VAULT_LABELS`** to operator label (e.g. `obsidian-brain`); confirm parser load + JSON size; document in `.cursor/brain-map.env.example`. | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md); `.cursor/brain-map.env.example` |
| STK-3 | pending | **Docs alignment — OpenHarness `docs/BRAIN_MAP.md`:** Public **OpenHarness** repo should carry **`docs/BRAIN_MAP.md`** (or stub) pointing to MiscRepos **BRAIN_MAP_HUB** + multi-root operator steps — **no drift** between “harness brain map” and portfolio hub. Clone may live outside this workspace; task is content + link parity. | OpenHarness `docs/BRAIN_MAP.md` (create/update); [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md) |
| STK-4 | pending | **OpenGrimoire inventory row:** Extend [OPENGRIMOIRE_SYSTEMS_INVENTORY.md](../../OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md) — multi-root Brain Map, env vars, “where OpenHarness appears” operator two-minute steps. | **OA-1** |
| STK-5 | pending | **Optional UI follow-up:** If labels are insufficient, product decision: layer filter defaults, legend, or deep-link from OpenGrimoire to Obsidian vault path (read-only). Log decision in `decision-log.md`. | **OGAN-*** / AN1 as applicable |
| STK-6 | pending | **Directory layout proposal:** After STK-0 friction data, add **one** recommended layout doc (e.g. under `local-proto/docs/` or Arc_Forge plans): sibling repos order, single place for env files, “no OpenGrimoire folder inside vault” rule. Gate execution on **WS-PRIV-6** / **WS-PRIV-7**. | [WS-PRIV-*](#pending_workspace_privacy_audit) |

---

## OPENGRIMOIRE_ALIGNMENT

**Purpose:** Approach B alignment context in OpenGrimoire. OA-ALIGN-1 = read path shipped; follow-ons = auth hardening, writes, agent surfaces. **Completed OA-ALIGN rows:** [completed_tasks.md § OPENGRIMOIRE_ALIGNMENT](completed_tasks.md#opengrimoire_alignment).

---

## OPENGRIMOIRE_FULL_REVIEW (product-scope)

**Purpose:** Prepare and execute a **full review of four OpenGrimoire systems** so the product can be declared *fully functioning* with explicit requirements, acceptance criteria, gaps, and verification. Uses **product-scope** discipline (numbered REQ, testable AC, 80% observer test). **Tech-lead:** keep findings in `OpenGrimoire/docs/plans/` + harness state; **critic** after each system or once at integration.

**Status:** All **OA-FR-*** labeled rows are **done** and live in [completed_tasks.md § OPENGRIMOIRE_FULL_REVIEW (product-scope)](completed_tasks.md#opengrimoire_full_review-product-scope) (run `split_done_tasks_to_completed.py` after future `done` marks). **Ongoing** verification and agent-native work: [SCOPE_OPENGRIMOIRE_FULL_REVIEW.md](../../OpenGrimoire/docs/plans/SCOPE_OPENGRIMOIRE_FULL_REVIEW.md), [OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md](../../OpenGrimoire/docs/plans/OPENGRIMOIRE_FULL_REVIEW_REFRESH_2026-04-17.md), plus **OG-GUI-***, **OGAN-***, **AN1**, **OA-1** elsewhere in this file.

---

## PENDING_NEXT (Context Graph, Foam, Obsidian, LLM Wiki, OpenGrimoire — E2E Demo & Education)

**Purpose:** Labeled next to-do's for presenting end-to-end functionality of Brain Map, Foam, Obsidian, **LLM Wiki** (vault canon), and **OpenGrimoire** as hybrid **base camp** (atlas, alignment, optional wiki mirror). Addresses operator need for access and education. Plan: [context_graph_foam_obsidian_e2e_demo_plan](../plans/context_graph_foam_obsidian_e2e_demo_plan.md).

| ID | Label | Status | Task | Spec / Link |
|----|-------|--------|------|-------------|
| NEXT-1 | **Brain Map** | pending | Brain Map E2E demo: document data flow; run parser; view graph/table; "How to read" section; optional `scripts/demo_brain_map.ps1` | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md), [BRAIN_MAP_E2E.md](../../docs/BRAIN_MAP_E2E.md) |
| NEXT-2 | **Foam** | pending | Foam E2E demo: "What is Foam"; workspace path; agent actions; demo prompt; Foam vs Obsidian comparison | [foam-pkm SKILL](../skills/foam-pkm/SKILL.md), [MCP_CAPABILITY_MAP](../docs/MCP_CAPABILITY_MAP.md) |
| NEXT-3 | **Obsidian** | pending | Obsidian E2E demo: "What is Obsidian"; MCP tools; MCP setup; demo prompt; handoff + `session_save` + **`write_handoff.py` → `sessions.db`**; `npm run vault:sync` / int-vault-resync. **Parallel research:** [§ BYOC-*](#pending_portable_ai_memory-byoc-session-db-vault-harness). **Vault hygiene + rename + Brain Map link:** [§ PENDING_OBSIDIAN_BRAIN_VAULT](#pending_obsidian_brain_vault), [§ PENDING_STACK_ATLAS](#pending_stack_atlas_openharness_in_opengrimoire). | [obsidian_cursor_integration/README](../../obsidian_cursor_integration/README.md), [MCP_SETUP.md](../../obsidian_cursor_integration/docs/MCP_SETUP.md), [GUI + agent-native engineering spec](../../docs/superpowers/specs/2026-04-16-obsidian-vault-llm-wiki-gui-agent-native-engineering.md), [HANDOFF_FLOW.md](../HANDOFF_FLOW.md) |
| NEXT-4 | **Unified** | pending | Maintain `docs/CONTEXT_PKM_E2E_DEMO.md` + prerequisites — unified operator journey (Brain Map → LLM Wiki → Foam → Obsidian → OpenGrimoire); optional video; AGENT_ENTRY_INDEX row | [context_graph_foam_obsidian_e2e_demo_plan](../plans/context_graph_foam_obsidian_e2e_demo_plan.md) Phase 4 |
| NEXT-5 | **LLM Wiki + OG mirror** | pending | LLM Wiki E2E: ingest/compile/lint boundaries; optional `Run-LlmWikiScheduledPipeline.ps1 -SyncOpenGrimoireWiki`; document SSOT vs mirror; link [OPENGRIMOIRE_BASE_FEATURES.md](../../../OpenGrimoire/docs/OPENGRIMOIRE_BASE_FEATURES.md) | [LLM_WIKI_VAULT.md](../../local-proto/docs/LLM_WIKI_VAULT.md), [LLM_WIKI_SCHEDULED_PIPELINE.md](../../local-proto/docs/LLM_WIKI_SCHEDULED_PIPELINE.md), [GUI + agent-native engineering spec](../../docs/superpowers/specs/2026-04-16-obsidian-vault-llm-wiki-gui-agent-native-engineering.md) |

---

## PENDING_OPEN_GRIMOIRE

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OG-2 | pending | Dwarf Fortress personality/NPC systems research: extract transferable patterns for persistent traits, social simulation, and intent evolution in agent context models. | [trustgraph-local-repo/research/USE_CASE_TO_PRODUCT_MAPPING.md](../../trustgraph-local-repo/research/USE_CASE_TO_PRODUCT_MAPPING.md) |

---

## PENDING_WORKSPACE_PRIVACY_AUDIT

**Purpose:** Future initiative — audit **Cursor workspaces**, **code repos**, and **data placement** (public vs private) so the operator keeps the **same privacy and security posture** with **less friction** (fewer env/path/junction/sync headaches). **Do not** bulk-move repos, vaults, or secrets until **WS-PRIV-7** is explicitly approved. **Not** a substitute for TOOL_SAFEGUARDS, SCP gates, or credential policy.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| WS-PRIV-0 | pending | **Charter:** Write one paragraph — goal (same bar, less headache), in-scope (inventory + principles + phased plan), out-of-scope (ad-hoc moves without backup and human gate) | This section; optional stub `local-proto/docs/WORKSPACE_PRIVACY_AUDIT_CHARTER.md` |
| WS-PRIV-1 | pending | **Inventory workspaces:** List Cursor roots (multi-root vs single-root), `MISCREPOS_ROOT` / junction usage, and where agents actually resolve `.cursor/` (local-proto vs MiscRepos vs other) | [REPO_BOUNDARY_INDEX.md](../../local-proto/docs/REPO_BOUNDARY_INDEX.md); [Ensure-HarnessSkillsJunction.ps1](../../local-proto/scripts/Ensure-HarnessSkillsJunction.ps1) |
| WS-PRIV-2 | pending | **Inventory repos:** Canonical vs mirror (MiscRepos, local-proto, Arc_Forge ObsidianVault, OpenGrimoire, `software`, OpenHarness); clone paths on disk (e.g. `C:\` vs `E:\`); what is git-tracked vs operator-only | [REPO_BOUNDARY_INDEX.md](../../local-proto/docs/REPO_BOUNDARY_INDEX.md); [OBSIDIAN_GITHUB_GAP_ANALYSIS.md](../../local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md) |
| WS-PRIV-3 | pending | **Classify data:** For each artifact class (handoff, vault notes, MCP config, `.env`, session DB, campaign RAG), tag **public OK** / **private repo only** / **never in git** / **vault mirror downstream**; align with redaction and `validate_output` expectations | [TOOL_SAFEGUARDS.md](../../local-proto/docs/TOOL_SAFEGUARDS.md); `.cursor/scripts/validate_output.py` |
| WS-PRIV-4 | pending | **Friction map:** Document concrete pain (duplicate `VAULT_SYNC_SAFE_BASE`, `OBSIDIAN_VAULT_ROOT`, safe-path defaults, skills junction, dual handoff) with **one owner** per artifact in a short table | [HANDOFF_FLOW.md](../HANDOFF_FLOW.md); [HITL_CONNECTIVITY.md](../../local-proto/docs/HITL_CONNECTIVITY.md); **2026-04-17:** [WORKSPACE_PATH_ENV_CHECKLIST.md § Single vault consolidation](../../local-proto/docs/WORKSPACE_PATH_ENV_CHECKLIST.md#single-vault-consolidation) + [adhoc inventory](adhoc/2026-04-17_single_vault_inventory.md) |
| WS-PRIV-5 | pending | **Principles doc:** Draft target rules (e.g. single SSOT per artifact, env templates not secrets, when vault sync is mandatory) — **review only**, no structural moves | Optional `local-proto/docs/WORKSPACE_PRIVACY_PRINCIPLES.md` |
| WS-PRIV-6 | pending | **Reformat proposals:** Enumerate options (e.g. fewer roots via meta-repo, private submodule, vault split Harness vs campaign-only, docs-only public fork) with pros/cons and **risk** (leak, drift, backup) | Links from WS-PRIV-2 table; decision-log when narrowed |
| WS-PRIV-7 | pending | **Human gate:** Operator approves written migration sequence, backups, and rollback; no execution before sign-off | `decision-log.md`; [GOVERNANCE_RITUAL.md](../docs/GOVERNANCE_RITUAL.md) if schedule-affecting |
| WS-PRIV-8 | pending | **Execute (phased):** Apply approved changes in small phases with verification after each (git hygiene, vault paths, docs, env templates); mark prior IDs done as you go | Same plan doc as WS-PRIV-6; update [REPO_BOUNDARY_INDEX.md](../../local-proto/docs/REPO_BOUNDARY_INDEX.md) when layout changes |
