---
title: "Pending Tasks (Labeled)"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
---

# Pending Tasks (Labeled)

**Purpose:** Labeled task list for HITL and async development. Cross-references [INTEGRATED_HITL_ASYNC_ROADMAP.md](../plans/INTEGRATED_HITL_ASYNC_ROADMAP.md). Check [handoff_latest.md](handoff_latest.md) for current focus before assuming all pending tasks are actionable. **Waved roadmap:** [WAVED_PENDING_TASKS.md](../../local-proto/docs/WAVED_PENDING_TASKS.md) (Waves 5–8).

**Last synced:** 2026-03-24 (OpenGrimoire Part A: OA-OG-P0/1/3/4 done; OA-OG-2/5 deferred — see table)
**80% target:** Met (per INTEGRATED_HITL_ASYNC_ROADMAP)
**Next focus:** AT3 visual (Playwright when Gradio exists); optional AT-H1–H4 (AI Trends hub follow-ups); I1/I2 (Continue.dev, Aider); AL2 (Bitcoin-Chaos). Testing Quality & Smoke (5 phases) done 2026-03-16. H4 done 2026-03-16 (JSON output for CI). CM-3 (Action Parity) done 2026-03-16 — daggr_run_workflow, WatchTower discovery, campaign_kb_ingest; critic 0.84.

**Cross-ref (local-proto/TODO ↔ pending_tasks):** local-proto #7 = I1 (Continue.dev); #8 = I2 (Aider); #19 = AL2 (Bitcoin-Chaos); #21 = AL4 (Python Bitcoin); #23 = handoff Next (chaos + NIM testing).

**Cross-ref (Arc_Forge ops / token offload ↔ this file):** Phase-style plans live under [`Arc_Forge/.cursor/plans/`](../../../Arc_Forge/.cursor/plans/) (e.g. `phase_1_ops_bootstrap_*.plan.md`, `phase_2_token_offload_*.plan.md`, `ops_bootstrap_with_local_ai_*.plan.md`). Reconcile “next focus” with this list and any workspace `handoff_latest.md` before pulling new parallel work.

**When executing C4, C5, CRY1, CRY2, LF1:** Load CL4R1T4S patterns and AUTHORITY_MODEL_TAXONOMY per [PENTAGI_FEDIMINT_ACE_ROADMAP](../../docs/PENTAGI_FEDIMINT_ACE_ROADMAP.md) §7.

---

## DONE_VIDEO_LEARNINGS

Video Learnings Quick Wins plan — all items completed. Plan: [video_learnings_quick_wins_240bc12e.plan.md](D:\software\.cursor\plans\video_learnings_quick_wins_240bc12e.plan.md).

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| high-1 | done | Add identify-but-advise-wrong eval prompts to AI_TASK_EVALS | [AI_TASK_EVALS.md](../docs/AI_TASK_EVALS.md) |
| high-2 | done | Add benign→harmful reversal scenarios to SCP reference | [secure-contain-protect/reference.md](../skills/secure-contain-protect/reference.md) |
| link-8 | done | Add bidirectional link learnings ↔ AI_TASK_EVALS | [learnings doc](../../docs/learnings/2026-03-18-video-nemoclaw-chatgpt-health.md) |
| gap-1 | done | OpenClaw incident history in OPENCLAW + SAFETY_CONSTITUTION | [OPENCLAW.md](../../local-proto/docs/OPENCLAW.md), [SAFETY_CONSTITUTION.md](../../local-proto/SAFETY_CONSTITUTION.md) |
| gap-2 | done | Calibration vignettes in calibration_test_suite | [calibration_test_suite.md](../scripts/calibration_test_suite.md) |
| gap-3 | done | Policy registry skeleton (schema, stub, TOOL_SAFEGUARDS note) | [TOOL_SAFEGUARDS_SCHEMA.md](../../local-proto/docs/TOOL_SAFEGUARDS_SCHEMA.md), [TOOL_SAFEGUARDS.md](../../local-proto/docs/TOOL_SAFEGUARDS.md) |
| low-7 | done | AI Trends ingestion note for video IDs | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) |
| low-9 | done | Create docs/solutions stub | [docs/solutions/README.md](../../docs/solutions/README.md) |
| med-5 | done | Inverted U-shaped performance in software AI docs | [AI_PRINCIPLES.md](D:\software\docs\AI_PRINCIPLES.md), [AI_DOCUMENTATION_INDEX.md](D:\software\docs\AI_DOCUMENTATION_INDEX.md) |
| med-6 | done | Frontier-ops skill triggers for high-stakes domains | [frontier-ops/SKILL.md](../skills/frontier-ops/SKILL.md) |

---

## PENDING_AI_TRENDS_HUB

**Purpose:** Follow-ups after GitHub + Hugging Face SCP-gated hub ingest (core pipeline **done** 2026-03-20). Optional enhancements only.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AT-H1 | pending | Optional `github.com/trending` HTML scrape (`github.mode: trending_page`) — brittle; review GitHub ToS | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § GitHub |
| AT-H2 | pending | **Wellbeing:** Wire `wellbeing_keywords` to tag/rank raw lines or `stack_intel.focus_prompt` (validate false negatives before any hard filter) | [ai_trends_config.json](../../local-proto/scripts/ai_trends_config.json) |
| AT-H3 | pending | **MCP_CAPABILITY_MAP** — add row for hub tools (`fetch_github_trending`, `fetch_huggingface_trending`, `ingest_*_to_raw`, default `run_ingestion_pipeline` sources) | [MCP_CAPABILITY_MAP.md](../docs/MCP_CAPABILITY_MAP.md) |
| AT-H4 | pending | **Operator:** If `AI-Trends-Ingest` Task Scheduler job predates hub ingest, update `--sources` to `youtube,futuretools,newsletters,github,huggingface` | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) § Cron |

---

## PENDING_HITL

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| A1 | done | Create HITL_PLAYBOOK.md (when to ask, escalate, configure; cross-ref TOOL_SAFEGUARDS) | [pentagi/docs/HITL_PLAYBOOK.md](../../pentagi/docs/HITL_PLAYBOOK.md) |
| A2 | done | Create ETHICS_AND_VALUES.md (org-intent, escalation, protect operator; link ACE-first, org-intent-spec) | [pentagi/docs/ETHICS_AND_VALUES.md](../../pentagi/docs/ETHICS_AND_VALUES.md) |
| A3 | done | Document ASK_USER=true for production in .env.example and HITL_AND_ETHICS | [pentagi/.env.example](../../pentagi/.env.example), [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| B1 | done | OSINT ask-gate spec: when type=phone or username, require approval before GhostTrack; config flag ASK_BEFORE_OSINT_PII | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| B2 | done | Target allowlist spec: TARGET_ALLOWLIST or SCOPE_PATH; fail-fast when target not in scope | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| B3 | done | Terminal ask-gate spec: ASK_BEFORE_TERMINAL; mandatory approval before first run | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| B4 | done | Coder→terminal gate spec: code execution requires human approval; checkpoint before pentester delegation | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| B5 | done | Browser private-URL ask-gate spec: when SCRAPER_PRIVATE_URL set, require confirmation for private URLs | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| C1 | done | Defensive preamble spec: optional prompt block for defensive awareness, protection-oriented behavior | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| C2 | done | Org-intent enforcement spec: programmatic check before tool calls; audit trail of decisions vs intent | pentagi/docs/ |
| C3 | done | Worker-node isolation spec: run execution on isolated workers; avoid docker.sock on main node | pentagi/docs/ |

---

## PENDING_ASYNC

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| D1 | done | Create REQUIREMENTS.md (async assumptions, Section 3d Async HITL, hardware, security) | [local-proto/REQUIREMENTS.md](../../local-proto/REQUIREMENTS.md) |
| D2 | done | Create SAFETY_CONSTITUTION.md (6 sections; critic + dialectic) | [local-proto/SAFETY_CONSTITUTION.md](../../local-proto/SAFETY_CONSTITUTION.md) |
| D3 | done | Create OPENCLAW.md with full "Messaging: Prefer Signal (Required)" section | [local-proto/docs/OPENCLAW.md](../../local-proto/docs/OPENCLAW.md) |
| D4 | done | Create JARVIS.md (MCP, handoff integration path) | [local-proto/docs/JARVIS.md](../../local-proto/docs/JARVIS.md) |
| D5 | done | Create orchestrator_config.json (or document template) | .cursor/ |
| D6 | done | End-to-end handoff validation runbook (handoff → generate_next_prompt → paste) | local-proto/docs/ |

---

## PENDING_INTEGRATED

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| E1 | done | Create INTEGRATED_HITL_ASYNC_ROADMAP.md | [INTEGRATED_HITL_ASYNC_ROADMAP.md](../plans/INTEGRATED_HITL_ASYNC_ROADMAP.md) |
| E2 | done | Add pending_tasks.md to .cursor/state/ | [pending_tasks.md](pending_tasks.md) |
| E3 | done | Update AGENT_ENTRY_INDEX: add "HITL and async setup" row | [AGENT_ENTRY_INDEX.md](../docs/AGENT_ENTRY_INDEX.md) |

---

## PENDING_GOVERNANCE_SCHEDULE

**Purpose:** OS-level scheduling for weekly harness governance (log stub + meta-review prompt). **Not** local-proto hardware or async AI handoff—this is “run a script on a timer” on whatever machine you use. Docs: [GOVERNANCE_RITUAL.md](../docs/GOVERNANCE_RITUAL.md); troubleshooting: [TROUBLESHOOTING_AND_PLAYBOOKS.md](../docs/TROUBLESHOOTING_AND_PLAYBOOKS.md) § Governance; broader registry: [local-proto SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md).

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| GV-1 | pending | **Windows — Task Scheduler:** Create the weekly job per [GOVERNANCE_RITUAL § Scheduled task (Windows)](../docs/GOVERNANCE_RITUAL.md#scheduled-task-windows) only (no duplicate steps elsewhere). **Verify:** one manual run; check `.cursor/state/governance_runs/*.log`. | [scheduled_governance.ps1](../scripts/scheduled_governance.ps1) |
| GV-2 | pending | **Linux / macOS:** Install cron or launchd per [GOVERNANCE_RITUAL § Cron and launchd](../docs/GOVERNANCE_RITUAL.md#cron-and-launchd-linux-macos). **Verify:** log under `governance_runs/`; mark done after one successful run. | [GOVERNANCE_RITUAL.md](../docs/GOVERNANCE_RITUAL.md) |
| GV-3 | pending | ** — repeatable install:** Add `schtasks` / `Register-ScheduledTask` example (or `.xml` export) under `.cursor/scripts/` or document in SCHEDULED_TASKS with task name `Harness-GovernanceRuns` so setup is copy-paste. Align with existing rows (e.g. Harness-MetaReviewPrompt) to avoid duplicate weekly prompts. | [SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md) |

---

## PENDING_OPTIONAL

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| F1 | done | Wave 2 validation: B1/B5 unit tests (osint_test.go PII block; browser_test.go private-URL) | [waved_closeout plan](../plans/waved_closeout_and_handoff_a26215a8.plan.md) |
| F2 | done | Integration flows for B1, B3, B5, B4 (manual or scripted per HITL_PLAYBOOK) | [HITL_PLAYBOOK](../../pentagi/docs/HITL_PLAYBOOK.md), [HITL_INTEGRATION_RUNBOOK](../../pentagi/docs/HITL_INTEGRATION_RUNBOOK.md) |
| I1 | pending | Evaluate Continue.dev: install, configure Ollama, test handoff paste flow | [continue_aider_eval plan](../plans/continue_aider_eval.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #7. **What AI needs:** Install path (VS Code extension); Ollama config (add llama3.2 in Continue settings); handoff flow: generate_next_prompt.ps1 → copy_continue_prompt.ps1 → paste in new Continue chat. **Human:** Confirm install + Ollama; run flow; report result. |
| I2 | pending | Evaluate Aider: install, test with handoff-derived prompt | [continue_aider_eval plan](../plans/continue_aider_eval.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #8. **What AI needs:** Install (`pip install aider-chat`); Ollama (`ollama pull qwen2.5-coder`); handoff flow: generate_next_prompt.ps1 → use continue_prompt.txt → `aider --model ollama_chat/qwen2.5-coder` + paste. **Human:** Same as I1. |

---

## PENDING_SHORT_TERM

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| ST1 | done | **OpenClaw hardware recommendations (community request):** Create doc with AI-specific specs, Mac vs alternatives, Mac Mini availability, non-technical user guidance | [OPENCLAW.md](../../local-proto/docs/OPENCLAW.md), [REQUIREMENTS.md](../../local-proto/REQUIREMENTS.md) §4, [task decomposition](../../docs/plans/2026-03-13-openclaw-hardware-task-decomposition.md) |
| ST2 | pending | **Alpha R2 + AGA setup:** Execute runbook (AGA connection, Ollama, OpenClaw, local-proto). **Blocked:** Pending hardware arrival. | [ALPHA_R2_AGA_SETUP.md](../../local-proto/docs/ALPHA_R2_AGA_SETUP.md) |

---

## PENDING_FUTURE

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| G1 | pending | Tier 1 tools (git, filesystem, sqlite) for Jarvis path; apply TOOL_SAFEGUARDS | [TOOLS_TO_INTEGRATE.md](../../local-proto/docs/TOOLS_TO_INTEGRATE.md) |
| G2 | pending | PentAGI → Signal approval round-trip (webhook to receive human response) | [Wave 4 plan](../plans/wave_4_async_delivery_25e3cf38.plan.md) |
| G3 | pending | C2 Option B: ORG_INTENT_ENFORCE blocking (when classifier/human intent_ok flow designed) | [HITL_AND_ETHICS_PROJECT.md](../../pentagi/docs/HITL_AND_ETHICS_PROJECT.md) |
| G4 | pending | org-intent.example.json in pentagi examples (optional; for local testing) | [integration verification](../plans/integration_points_verification_763e7765.plan.md) |
| G5 | pending | Model escalation pattern: light model for execution, heavy model for verification; document in AI_TASK_EVALS | [BitDevs MPLS 2026-03-10](../../docs/bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md) |
| G6 | pending | Research: Fedimint CLI, MCP2CLI, LiteLLM + Routstr/OpenRouter | [BitDevs MPLS 2026-03-10](../../docs/bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md) |
| G7 | pending | IronClaw evaluation for Rust-based privacy-first AI path | [BitDevs MPLS 2026-03-10](../../docs/bitcoin_observations/2026-03-10-bitdevs-mpls-seminar-36.md), [IronClaw](https://github.com/nearai/ironclaw) |
| G8 | pending | **MCP OAuth 2.1 + Streamable HTTP** — Track for future auth and deployment. Streamable HTTP uses OAuth 2.1 (Auth Code + PKCE) for remote MCP; enables secure SaaS MCP. | [MCP Authorization](https://modelcontextprotocol.io/docs/tutorials/security/authorization), [LavX News](https://news.lavx.hu/article/authentication-and-authorization-in-model-context-protocol-oauth-2-1-and-the-streamable-http-transport). **What AI needs:** Priority and scope. Options: (a) Tracking only — add to roadmap; (b) Implementation — design and implement for specific MCP (e.g. SCP SaaS). **Human:** Choose tracking vs implementation; if (b), scope and MCP. |
| G9 | pending | **Research: AI pools + Bitcoin block space** — AI compute pools using Bitcoin block space/data as prompts for sovereign decentralized AI. Survey: Gonka AI, x402 Stacks, Lumerin, DeltaHash, Routstr. Brainstorm: docs/brainstorms/2026-03-16-ai-pools-bitcoin-block-space-brainstorm.md. | [BITCOIN_OBSERVATION_SOURCES](../../docs/BITCOIN_OBSERVATION_SOURCES.md), [Routstr SKILL](../skills/routstr/SKILL.md) |

---

## PENDING_OPENGRIMOIRE_HARNESS

**Purpose:** One standard for verification and discoverability across harness + OpenGrimoire without multiplying “sources of truth.” OpenGrimoire inventory doc links to workspace [MCP_CAPABILITY_MAP.md](../docs/MCP_CAPABILITY_MAP.md) instead of copying MCP lists.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OA-1 | pending | **Maintain OpenGrimoire systems inventory** — Keep [OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md](../../OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md) accurate when adding routes, APIs, scripts, or security flags. **Inventory must list:** app routes, API routes, `build_brain_map.py` + env vars, npm scripts, Playwright, Docker, alignment HTTP API, key docs; **must link (not duplicate)** full MCP server matrix from MCP_CAPABILITY_MAP. | [OPENGRIMOIRE_SYSTEMS_INVENTORY.md](../../OpenGrimoire/docs/OPENGRIMOIRE_SYSTEMS_INVENTORY.md) |
| OA-2 | done | **Document harness ↔ OpenGrimoire boundary for contributors** — Short subsection in openharness README: OpenGrimoire is portfolio implementation, not in-repo; brain map = session co-access + `CURSOR_STATE_DIR`. | [openharness/README.md](../../../openharness/README.md) § OpenGrimoire |
| OA-3 | done | **Multi-root brain map** — `build_brain_map.py` accepts `CURSOR_STATE_DIRS` + `CURSOR_STATE_DIR_LABELS` or repeated `--state-dir` / `--label`; merged graph includes `sourceRoots`; prefixed `label:session` on edges when multiple roots. Docs: BRAIN_MAP_HUB, BRAIN_MAP_SCHEMA, OPENGRIMOIRE_SYSTEMS_INVENTORY, OpenGrimoire README. | [build_brain_map.py](../scripts/build_brain_map.py) |
| OA-4 | done | **Single `npm run verify` for OpenGrimoire** — `lint` + `type-check` + `test`; `verify:e2e` adds Playwright. Documented in README + OPENGRIMOIRE_SYSTEMS_INVENTORY. **Done 2026-03-20.** | [OpenGrimoire/package.json](../../OpenGrimoire/package.json), [README](../../OpenGrimoire/README.md) § Scripts |
| OA-REST-1 | done | **Portable TOOL_SAFEGUARDS link** — `ARCHITECTURE_REST_CONTRACT.md` uses repo-relative `../../local-proto/docs/TOOL_SAFEGUARDS.md` plus wording for standalone `local-proto` clones (no machine-specific `D:` URLs). **Done 2026-03-20.** | [ARCHITECTURE_REST_CONTRACT.md](../../OpenGrimoire/docs/ARCHITECTURE_REST_CONTRACT.md) § Non-goals |
| OA-REST-2 | done | **Capabilities discovery (minimal)** — `GET /api/capabilities` hand-maintained manifest; extend with OpenAPI later and link ADR in contract doc. **Done 2026-03-20.** | [route.ts](../../OpenGrimoire/src/app/api/capabilities/route.ts), [ARCHITECTURE_REST_CONTRACT.md](../../OpenGrimoire/docs/ARCHITECTURE_REST_CONTRACT.md) § Capability discovery |
| OA-OG-P0 | done | **OpenGrimoire P0 (AC2):** Conditional Table columns for optional node fields when present (`trust_score`, `compass_axis`, `grimoire_tags`, `insight_level`); graph tooltip extended. **Done 2026-03-24.** | [BrainMapGraph.tsx](../../OpenGrimoire/src/components/BrainMap/BrainMapGraph.tsx); [scope_opengrimoire_mvp_agent_native.md](../../OpenGrimoire/docs/scope_opengrimoire_mvp_agent_native.md) |
| OA-OG-1 | done | **Action parity docs:** curl + existing CLI in [AGENT_INTEGRATION.md](../../OpenGrimoire/docs/AGENT_INTEGRATION.md). Thin MCP remains optional per [INTEGRATION_PATHS.md](../../OpenGrimoire/docs/agent/INTEGRATION_PATHS.md). **Done 2026-03-24.** | Same audit Part A row 1 |
| OA-OG-2 | deferred | **Admin alignment UI:** React Query/SWR / SSE — not in this slice; focus/visibility refetch already meets contract baseline. | [admin/alignment/page.tsx](../../OpenGrimoire/src/app/admin/alignment/page.tsx) |
| OA-OG-3 | done | **Discovery polish:** SharedNavBar + SiteFooter link `/capabilities`; keep capabilities route in sync per PR (discipline). **Done 2026-03-24.** | [capabilities/page.tsx](../../OpenGrimoire/src/app/capabilities/page.tsx), [SharedNavBar.tsx](../../OpenGrimoire/src/components/SharedNavBar.tsx) |
| OA-OG-4 | done | **P1:** Playwright: `e2e/capabilities.spec.ts` for `/api/capabilities`; context-atlas fixture asserts optional Table columns. **Done 2026-03-24.** | [agent_native_opengrimoire_2026-03-24.md](../../OpenGrimoire/docs/audit/agent_native_opengrimoire_2026-03-24.md) |
| OA-OG-5 | deferred | **P1:** A2UI on `/capabilities` — deferred until product scope explicitly requires agent-rendered discovery UI. | Scope R7 |

---

## PENDING_AGENT_NATIVE

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| CM-3 | done | **Action parity (CM-3)** — daggr_run_workflow, WatchTower discovery (scan/devices/status/failover), campaign_kb_ingest; MCP_CAPABILITY_MAP, agent-native checklist (MiscRepos stub → OpenHarness canonical + MISCOPS), product-scope/tech-lead skills. Critic 0.84; inputs_json docstring clarified. | action_parity_and_agent-native_improvement plan |
| AN1 | pending | **Agent-native audit** — Run `/agent-native-audit` against 8 principles (Action Parity, Tools as Primitives, Context Injection, Shared Workspace, CRUD Completeness, UI Integration, Capability Discovery, Prompt-Native Features). CM done; CV, BS, PT still pending. | security_vectors_task_decomposition plan §2 |

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

---

## PENDING_ALIGNMENT

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AL1 | done | Alignment Analysis Seed: D:\alignment-seed — identity, goals, community capture; private data; CLI scripts | [D:\alignment-seed\README.md](D:\alignment-seed\README.md), [local-proto/TODO.md](../../local-proto/TODO.md) #18 |
| AL2 | in_progress | Bitcoin-Chaos Convergence: Execute plan phases A–C. Expect gap of operations; planning phase. | [bitcoin_chaos_convergence plan](../../plans/bitcoin_chaos_convergence_a219e7b9.plan.md), [integration plan](../../plans/bitcoin_chaos_convergence_integration_827d4828.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #19 |
| AL2a | done | Plan integration: Fedimint/ACE/PentAGI column, observation framework, ACE-Harness mapping, Section 9.5 | [bitcoin_chaos_convergence_a219e7b9](../../plans/bitcoin_chaos_convergence_a219e7b9.plan.md) |
| A4 | done | Fedimint observation template | [FEDIMINT_OBSERVATION_TEMPLATE.md](../../docs/FEDIMINT_OBSERVATION_TEMPLATE.md) |
| A5 | done | Fedimint column in Chaos-Bitcoin mapping | [CHAOS_BITCOIN_MAPPING.md](../../docs/CHAOS_BITCOIN_MAPPING.md) |
| B4 | done | PENTAGI_FEDIMINT_ACE_ROADMAP consolidation doc | [PENTAGI_FEDIMINT_ACE_ROADMAP.md](../../docs/PENTAGI_FEDIMINT_ACE_ROADMAP.md) |
| B5 | done | ACE layers → harness components mapping | PENTAGI_FEDIMINT_ACE_ROADMAP §2 |
| B6 | done | Add Fedimint AuthModule to BITCOIN_OBSERVATION_SOURCES | [integration plan](../../plans/bitcoin_chaos_convergence_integration_827d4828.plan.md) §6 |
| C4 | pending | Fedimint testnet exploration (3–5 guardian; AuthModule design) | deep-research-report §7 |
| C5 | pending | Capability token schema (Fedimint-native or standalone) | PentAGI protocol; deep-research-report §4 |
| AL3 | pending | Identity/Cultural Context: Add identity_context schema and template for multi-community, evolving self. Private data/. | bitcoin_chaos plan Section 8, [local-proto/TODO.md](../../local-proto/TODO.md) #20 |
| AL4 | done | Python Bitcoin Modules (Research): Evaluate bitcoinlib, l402-requests, LangChainBitcoin. Skeptical of Coinbase, custodial. | [PYTHON_BITCOIN_MODULES_RESEARCH.md](../../docs/PYTHON_BITCOIN_MODULES_RESEARCH.md), [local-proto/TODO.md](../../local-proto/TODO.md) #21 |
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

## PENDING_GWS_MANUAL (human checklist)

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| GW1 | pending | Run `gws auth login -s drive,gmail,sheets` (or desired scopes) to authenticate | [GWS_INTEGRATION.md](../../docs/GWS_INTEGRATION.md) |
| GW2 | pending | For OpenClaw: `npx skills add https://github.com/googleworkspace/cli` | [GWS_INTEGRATION.md](../../docs/GWS_INTEGRATION.md), [OPENCLAW.md](../../local-proto/docs/OPENCLAW.md) |
| GW3 | pending | For headless/CI: `gws auth export --unmasked > credentials.json`; store path in credential-vault under key `gws` | [GWS_INTEGRATION.md](../../docs/GWS_INTEGRATION.md) |

---

## PENDING_CIRCUITBREAKER (critic/architect improvements)

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| CB-1 | done | Normalize install URL in scope_circuitbreaker_eval.md (`circuitbreaker` → `CircuitBreaker`) | [scope_circuitbreaker_eval.md](scope_circuitbreaker_eval.md), [circuitbreaker_critic_architect_brainstorm plan](../../plans/circuitbreaker_critic_architect_brainstorm_fd32a6e5.plan.md) |
| CB-2 | done | Add scope_circuitbreaker_eval.md link to AGENT_ENTRY_INDEX "Proxmox homelab visibility" row | [AGENT_ENTRY_INDEX.md](../docs/AGENT_ENTRY_INDEX.md) |
| CB-3 | done | Document docker-mcp cross-repo link assumption (local-first sibling of portfolio-harness) | [docker-mcp SKILL](../skills/docker-mcp/SKILL.md) |

---

## PENDING_OTHER

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| H1 | done | Playwright skills audit (gap inventory, audit checklist, recommendations) | [playwright_skills_audit_prep.plan.md](../plans/playwright_skills_audit_prep.plan.md) |
| H2 | pending | Run continual-learning once transcripts exist to populate AGENTS.md | [run_continual_learning_prompt.ps1](../scripts/run_continual_learning_prompt.ps1), [SKILL_SELF_IMPROVEMENT_WINS.md](../docs/SKILL_SELF_IMPROVEMENT_WINS.md) |
| H3 | done | campaign_kb Playwright fixtures: Add fixtures/mocks so campaign_kb Daggr tests (search, merge, ingest) run without a real DB. Use in-memory SQLite or mock DB layer. | [daggr_test_matrix.md](../docs/daggr_test_matrix.md), [DAGGR_MCP.md](../docs/DAGGR_MCP.md). **Done 2026-03-16:** conftest in-memory DB; test_search_workflow_returns_empty_when_no_data. |
| H4 | done | Add Playwright smoke to run_daggr_tests.ps1; add quantitative analysis (pass/fail counts, duration, per-stack breakdown) alongside smoke test; add -OutputFormat json for CI | [run_daggr_tests.ps1](../scripts/run_daggr_tests.ps1), [daggr_test_matrix.md](../docs/daggr_test_matrix.md). **Done 2026-03-16.** |
| H5 | pending | **Agent Korean-language switch:** Investigate and fix unexpected Korean responses when user sends short prompts (e.g. "do it") in English context. Check .cursorrules, workspace rules, language-preference handling. | [known-issues.md](known-issues.md) §Agent behavior. **What AI needs:** Confirmation fixed vs still happening. .cursorrules has "Respond in English unless user requests otherwise"; no "Always Korean" rule found. **Human:** Test "do it" in new chat; report (a) still Korean or (b) fixed. |
| H6 | done | **SCP fail-closed:** Make _scp_gate in observation_mcp.py and ai_trends_ingest.py fail-closed. On ImportError or Exception, reject append (return error) instead of pass-through. Per [bitcoin_ingestion_threat_model_2026-03-16.md](adhoc/bitcoin_ingestion_threat_model_2026-03-16.md) §5. **Done 2026-03-20:** observation returns JSON error; ingest skips writes and logs error. | [observation_mcp.py](../../local-proto/scripts/observation_mcp.py), [ai_trends_ingest.py](../../local-proto/scripts/ai_trends_ingest.py) |

---

## PENDING_VAULT (ObsidianVault integration)

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| V1 | done | Create sync_harness_to_vault.ps1: copy handoff, pending_tasks, decision-log, daily, docs to vault Harness/ | [local-proto/scripts/sync_harness_to_vault.ps1](../../local-proto/scripts/sync_harness_to_vault.ps1) |
| V2 | done | Fix OBSIDIAN_VAULT_ROOT case: obsidian_cursor_integration/mcp.json use D:/Arc_Forge/ | [obsidian_cursor_integration/mcp.json](../../obsidian_cursor_integration/mcp.json) |
| V3 | done | Document vault sync in SCHEDULED_TASKS and HANDOFF_FLOW (when to run sync) | [SCHEDULED_TASKS.md](../../local-proto/docs/SCHEDULED_TASKS.md), [HANDOFF_FLOW.md](../HANDOFF_FLOW.md) |
| V4 | done | Make session_save mandatory on handoff (not optional) when obsidian-vault available | [.cursorrules](../../.cursorrules), [HANDOFF_FLOW.md](../HANDOFF_FLOW.md) |
| V5 | done | Create Harness/Docs/ mirror: COMMANDS_README, MCP_CAPABILITY_MAP, SCHEDULED_TASKS, CHAOS_BITCOIN_MAPPING, bitcoin_observations | [sync_harness_to_vault.ps1](../../local-proto/scripts/sync_harness_to_vault.ps1) |
| V6 | done | Create OBSIDIAN_VAULT_INTEGRATION.md audit doc | [OBSIDIAN_VAULT_INTEGRATION.md](../docs/OBSIDIAN_VAULT_INTEGRATION.md) |

---

## PENDING_AI_TRENDS

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AT0 | done | AI Trends MCP: Implement server, ingest script, config, docs, mcp.json registration | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) |
| AT0a | done | AI Trends MCP: Critic fixes (ai_trends_utils, validation, allowlist, None guards, VTT parsing) | [ai_trends_critic_fixes plan](D:\software\.cursor\plans\ai_trends_critic_fixes_9dd9a42f.plan.md) |
| AT1 | pending | AI Trends MCP: Implement WhisperX fallback for videos without captions | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) |
| AT2 | pending | AI Trends MCP: Add Firecrawl/Playwright for FutureTools JS-heavy pages if scrape incomplete | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) |
| AT3 | done | AI Trends MCP: E2E testing — list_ingested MCP tool test; ai-trends in TOOL_MAP. Playwright deferred until Gradio UI exists. | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md), [local-proto/tests/test_ai_trends_mcp_e2e.py](../../local-proto/tests/test_ai_trends_mcp_e2e.py). **Done 2026-03-16.** |
| AT3b | pending | AI Trends MCP: Playwright E2E when Gradio UI exists — add Playwright test for AI Trends Gradio (if added). | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md). Blocked: no Gradio UI in current design. |

---

## PENDING_AFTER_RESTART

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| R1 | pending | **obsidian-vault MCP:** Check Cursor Settings → MCP; confirm obsidian-vault shows running or has errors | Session 2026-03-11. **What AI needs:** Whether MCP is running. Check Cursor Settings → MCP. If obsidian-vault tools (session_save, apply_patch, vault_search) not in agent list, MCP may not be loaded. **Human:** Report obsidian-vault status. |
| R2 | pending | **obsidian-vault MCP:** Re-test foam-pkm prompt 1 (create note in Obsidian vault about Bitcoin-Chaos mapping); verify agent uses `apply_patch` not `Write` | [TEST_PROMPTS.md](../skills/foam-pkm/TEST_PROMPTS.md) #1. **What AI needs:** Prompt: "Create a note in the Obsidian vault about Bitcoin-Chaos mapping, linking to CHAOS_BITCOIN_MAPPING". Expected: apply_patch. **Human:** New chat, paste prompt, verify behavior. |
| R3 | pending | **Critic follow-up:** Apply critic fixes (known-issues obsidian-vault entry; SKILL.md guardrail; AI_TASK_EVALS; TEST_PROMPTS procedure; test_mcp_and_audit skip) | Critic report 2026-03-11. **What AI needs:** Which fixes to apply. Options: (1) known-issues obsidian-vault entry; (2) foam-pkm SKILL.md guardrail (prefer apply_patch); (3) AI_TASK_EVALS; (4) TEST_PROMPTS procedure; (5) test_mcp_and_audit skip for obsidian-vault. **Human:** Choose all or subset. |

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

**How to get it running and generating money + fame:**

- ~~**Fix inj-4 gap**~~ — Done (2026-03-12): path_traversal patterns in sanitize_input.py; all 16/16 pass.
- **Ship promptfoo YAML config** — Add `promptfoo-scp.yaml` so users can run `npx promptfoo eval -c promptfoo-scp.yaml`; lowers friction, increases adoption.
- **Host SCP as SaaS MCP** — Deploy SCP MCP server (e.g. Fly.io, Railway, or self-host); agents connect via MCP URL. Enables "SCP as a service" for teams without local setup.
- **Shared threat registry (mycelium)** — SCP-R1..SCP-R6 above. Add optional network layer: anonymized pattern contributions, pull of shared registry. Each node contributes; all benefit. Differentiator vs single-org tools.
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
| SCP4 | done | **Pre-commit env (critic issue):** pre-commit installed; hooks installed. Run `python -m pre_commit run --all-files` for manual verification. Note: sanitize-input may flag existing state files (Morse-like, path refs); separate cleanup. | [.pre-commit-config.yaml](../../.pre-commit-config.yaml), [COMMANDS_README.md](../docs/COMMANDS_README.md) § OWASP |

---

## PENDING_BRAIN_MAP

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| BM-A11Y | pending | **BrowserStack MCP + Brain Map a11y:** Configure BrowserStack credentials in MCP; start Local (or use staging URL); run `startAccessibilityScan` and `accessibilityExpert` on Brain Map viewer (standalone and/or OpenGrimoire); append rows to **BrowserStack scan log** in [docs/BRAIN_MAP_AUDIT.md](../../docs/BRAIN_MAP_AUDIT.md) and in OpenHarness `docs/BRAIN_MAP_AUDIT.md` (public harness clone) with scan ID, scan run ID, URL, date. **Template row + viz tab keyboard (ArrowUp/Down) landed 2026-03-20; cloud scan still operator-dependent.** | [BRAIN_MAP_E2E.md](../../docs/BRAIN_MAP_E2E.md) Step 8, [BRAIN_MAP_AUDIT.md](../../docs/BRAIN_MAP_AUDIT.md) |

---

## OPENGRIMOIRE_ALIGNMENT

**Purpose:** Approach B alignment context in OpenGrimoire. OA-ALIGN-1 = read path shipped; follow-ons = auth hardening, writes, agent surfaces.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OA-ALIGN-1 | done | **Alignment context table + RLS + read route** — `20260319140000_alignment_context_items.sql`; `GET /api/alignment-context`; `src/lib/supabase/admin.ts` (`server-only`, service role). | [2026-03-19-opengrimoire-alignment-implementation.md](../../OpenGrimoire/docs/plans/2026-03-19-opengrimoire-alignment-implementation.md) |
| OA-ALIGN-SEC | done | **Harden read route for production** — `GET /api/alignment-context` returns **503** when `NODE_ENV=production` and `ALIGNMENT_CONTEXT_API_SECRET` missing/blank; header gate when set. `DEPLOYMENT.md` + audit + `.env.example` updated. Session/cookie auth remains future (OA-ALIGN-2+). | [route.ts](../../OpenGrimoire/src/app/api/alignment-context/route.ts), [DEPLOYMENT.md](../../OpenGrimoire/DEPLOYMENT.md) |
| OA-ALIGN-2 | done | **Write path + UI** — `POST /api/alignment-context`, `PATCH`/`DELETE /api/alignment-context/[id]`; admin BFF `/api/admin/alignment-context`; UI `/admin/alignment`. Optional hook deferred. | [route.ts](../../OpenGrimoire/src/app/api/alignment-context/route.ts), [ALIGNMENT_CONTEXT_API.md](../../OpenGrimoire/docs/agent/ALIGNMENT_CONTEXT_API.md) |
| OA-ALIGN-3 | done | **Agent parity** — `OpenGrimoire/scripts/alignment-context-cli.mjs` + manifest [ALIGNMENT_CONTEXT_API.md](../../OpenGrimoire/docs/agent/ALIGNMENT_CONTEXT_API.md); [MCP_CAPABILITY_MAP](../docs/MCP_CAPABILITY_MAP.md) § OpenGrimoire. | [OPERATOR_ALIGNMENT_SETUP.md](../../OpenGrimoire/docs/agent/OPERATOR_ALIGNMENT_SETUP.md) |

---

## OPENGRIMOIRE_FULL_REVIEW (product-scope)

**Purpose:** Prepare and execute a **full review of four OpenGrimoire systems** so the product can be declared *fully functioning* with explicit requirements, acceptance criteria, gaps, and verification. Uses **product-scope** discipline (numbered REQ, testable AC, 80% observer test). **Tech-lead:** keep findings in `OpenGrimoire/docs/plans/` + harness state; **critic** after each system or once at integration.

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OA-FR-SCOPE | pending | **Charter + definition of done** — Complete [SCOPE_OPENGRIMOIRE_FULL_REVIEW.md](../../OpenGrimoire/docs/plans/SCOPE_OPENGRIMOIRE_FULL_REVIEW.md): stakeholders, “fully functioning” definition, MVP vs deferred, review order, link this table. | [SCOPE_OPENGRIMOIRE_FULL_REVIEW.md](../../OpenGrimoire/docs/plans/SCOPE_OPENGRIMOIRE_FULL_REVIEW.md) |
| OA-FR-1 | pending | **System 1 — Survey & moderation:** REQ/AC matrix (submit survey, admin auth, moderate queue, RLS intent); gap list vs code + [PUBLIC_SURFACE_AUDIT.md](../../OpenGrimoire/docs/security/PUBLIC_SURFACE_AUDIT.md); smoke checklist (curl/Playwright optional). | [OpenGrimoire/src/app/survey](../../OpenGrimoire/src/app/survey), [admin](../../OpenGrimoire/src/app/admin), [api/survey](../../OpenGrimoire/src/app/api/survey) |
| OA-FR-2 | pending | **System 2 — Data visualization:** REQ/AC (routes, data sources, quotes, auto-play, debug flags); perf/logging gates; list test pages (`/visualization`, `/test-chord`, etc.) and data dependencies. | [DataVisualization](../../OpenGrimoire/src/components/DataVisualization), [useVisualizationData](../../OpenGrimoire/src/components/DataVisualization/shared/useVisualizationData.ts) |
| OA-FR-3 | pending | **System 3 — Brain map / context atlas:** REQ/AC (parser → JSON → API → UI); port resolution [PORT_REGISTRY.md](../docs/PORT_REGISTRY.md); `BRAIN_MAP_*` / empty state; link **BM-A11Y** and [BRAIN_MAP_E2E.md](../../docs/BRAIN_MAP_E2E.md). | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md), [BrainMapGraph](../../OpenGrimoire/src/components/BrainMap/BrainMapGraph.tsx) |
| OA-FR-4 | pending | **System 4 — Alignment & operator APIs:** REQ/AC (migration on Supabase, prod secret + header, public CRUD + admin BFF, CLI); close critic gaps (e.g. admin **PATCH title/body** parity, optional **PATCH `source`** policy). | [ALIGNMENT_CONTEXT_API.md](../../OpenGrimoire/docs/agent/ALIGNMENT_CONTEXT_API.md), § OPENGRIMOIRE_ALIGNMENT above |
| OA-FR-X | pending | **Cross-cutting:** Single go-live checklist — Docker/env parity with [DEPLOYMENT.md](../../OpenGrimoire/DEPLOYMENT.md), `.env.example` completeness, CI/test gaps, agent-native parity table (UI vs `alignment:cli` / harness commands), docs index for operators. | [DEPLOYMENT.md](../../OpenGrimoire/DEPLOYMENT.md), [MCP_CAPABILITY_MAP](../docs/MCP_CAPABILITY_MAP.md) § OpenGrimoire |

---

## PENDING_NEXT (Context Graph, Foam, Obsidian — E2E Demo & Education)

**Purpose:** Labeled next to-do's for presenting end-to-end functionality of Brain Map, Foam, and Obsidian. Addresses operator need for access and education. Plan: [context_graph_foam_obsidian_e2e_demo_plan](../plans/context_graph_foam_obsidian_e2e_demo_plan.md).

| ID | Label | Status | Task | Spec / Link |
|----|-------|--------|------|-------------|
| NEXT-P0 | **Prereq** | done | Create `docs/CONTEXT_PKM_PREREQUISITES.md` — list what operator needs (repo, state, Med-Vis, vault path, Foam path); access checklist | [CONTEXT_PKM_PREREQUISITES.md](../../docs/CONTEXT_PKM_PREREQUISITES.md) |
| NEXT-1 | **Brain Map** | pending | Brain Map E2E demo: document data flow; run parser; view graph/table; "How to read" section; optional `scripts/demo_brain_map.ps1` | [BRAIN_MAP_HUB.md](../../docs/BRAIN_MAP_HUB.md), [BRAIN_MAP_E2E.md](../../docs/BRAIN_MAP_E2E.md) |
| NEXT-2 | **Foam** | pending | Foam E2E demo: "What is Foam"; workspace path; agent actions; demo prompt; Foam vs Obsidian comparison | [foam-pkm SKILL](../skills/foam-pkm/SKILL.md), [MCP_CAPABILITY_MAP](../docs/MCP_CAPABILITY_MAP.md) |
| NEXT-3 | **Obsidian** | pending | Obsidian E2E demo: "What is Obsidian"; MCP tools; MCP setup; demo prompt; handoff + session_save; vault sync | [obsidian_cursor_integration/README](../../obsidian_cursor_integration/README.md), [MCP_SETUP.md](../../obsidian_cursor_integration/docs/MCP_SETUP.md) |
| NEXT-4 | **Unified** | pending | Create `docs/CONTEXT_PKM_E2E_DEMO.md` — single demo doc (Brain Map → Foam → Obsidian); optional video; add AGENT_ENTRY_INDEX row | [context_graph_foam_obsidian_e2e_demo_plan](../plans/context_graph_foam_obsidian_e2e_demo_plan.md) Phase 4 |

---

## PENDING_OPEN_GRIMOIRE

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| OG-1 | done | Narrative uses **OpenGrimoire** for the initiative; **OpenCompass** kept for upstream/tooling; inventory: [og1_opencompass_opengrimoire_audit.md](./og1_opencompass_opengrimoire_audit.md). | [local-proto/docs/OPS_BOOTSTRAP_OPEN_GRIMOIRE.md](../../local-proto/docs/OPS_BOOTSTRAP_OPEN_GRIMOIRE.md), [OpenGrimoire/docs/OPEN_GRIMOIRE_LOCAL_FIRST_INTEGRATION.md](../../OpenGrimoire/docs/OPEN_GRIMOIRE_LOCAL_FIRST_INTEGRATION.md) |
| OG-2 | pending | Dwarf Fortress personality/NPC systems research: extract transferable patterns for persistent traits, social simulation, and intent evolution in agent context models. | [trustgraph-local-repo/research/USE_CASE_TO_PRODUCT_MAPPING.md](../../trustgraph-local-repo/research/USE_CASE_TO_PRODUCT_MAPPING.md) |
