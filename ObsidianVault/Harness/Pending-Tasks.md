# Pending Tasks (Labeled)

**Purpose:** Labeled task list for HITL and async development. Cross-references [INTEGRATED_HITL_ASYNC_ROADMAP.md](../plans/INTEGRATED_HITL_ASYNC_ROADMAP.md). Check [handoff_latest.md](handoff_latest.md) for current focus before assuming all pending tasks are actionable. **Waved roadmap:** [WAVED_PENDING_TASKS.md](../../local-proto/docs/WAVED_PENDING_TASKS.md) (Waves 5–8).

**Last synced:** 2026-03-09
**80% target:** Met (per INTEGRATED_HITL_ASYNC_ROADMAP)
**Next focus:** Quick wins complete; chaos + NIM testing plan (handoff Next) or Playwright audit per session_brief.

**Cross-ref (local-proto/TODO ↔ pending_tasks):** local-proto #7 = I1 (Continue.dev); #8 = I2 (Aider); #19 = AL2 (Bitcoin-Chaos); #21 = AL4 (Python Bitcoin); #23 = handoff Next (chaos + NIM testing).

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

## PENDING_OPTIONAL

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| F1 | done | Wave 2 validation: B1/B5 unit tests (osint_test.go PII block; browser_test.go private-URL) | [waved_closeout plan](../plans/waved_closeout_and_handoff_a26215a8.plan.md) |
| F2 | done | Integration flows for B1, B3, B5, B4 (manual or scripted per HITL_PLAYBOOK) | [HITL_PLAYBOOK](../../pentagi/docs/HITL_PLAYBOOK.md), [HITL_INTEGRATION_RUNBOOK](../../pentagi/docs/HITL_INTEGRATION_RUNBOOK.md) |
| I1 | pending | Evaluate Continue.dev: install, configure Ollama, test handoff paste flow | [continue_aider_eval plan](../plans/continue_aider_eval.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #7 |
| I2 | pending | Evaluate Aider: install, test with handoff-derived prompt | [continue_aider_eval plan](../plans/continue_aider_eval.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #8 |

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

---

## PENDING_CREDENTIALS (human checklist from setup_env.py)

| ID | Status | Task | Spec / Link |
|----|--------|------|--------------|
| CR1 | pending | PentAGI: Add INSTALLATION_ID, LICENSE_KEY (PentAGI Cloud) | [pentagi/.env](../../pentagi/.env) |
| CR2 | pending | PentAGI: Add OAUTH_* if using OAuth (Google/GitHub) | [pentagi/.env](../../pentagi/.env) |
| CR3 | pending | PentAGI: Add TAVILY_API_KEY, PERPLEXITY_API_KEY, etc. (search APIs; DuckDuckGo is free) | [pentagi/.env](../../pentagi/.env) |
| CR4 | pending | local-proto: Add CRAIGSLIST_EMAIL, CRAIGSLIST_PASSWORD (for browser flows) | [local-proto/.env](../../local-proto/.env) |
| CR5 | pending | local-proto: Add CURSOR_API_KEY (orchestrator) | [local-proto/.env](../../local-proto/.env) |
| CR6 | pending | Med-Vis: Add NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY | [Med-Vis/.env](../../Med-Vis/.env) |

**Note:** LLM and embeddings use Ollama by default (no API keys). Run `python .cursor/scripts/setup_env.py --force` to regenerate with Ollama defaults.

---

## PENDING_ALIGNMENT

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| AL1 | done | Alignment Analysis Seed: D:\alignment-seed — identity, goals, community capture; private data; CLI scripts | [D:\alignment-seed\README.md](D:\alignment-seed\README.md), [local-proto/TODO.md](../../local-proto/TODO.md) #18 |
| AL2 | in_progress | Bitcoin-Chaos Convergence: Execute plan phases A–C. Expect gap of operations; planning phase. | [bitcoin_chaos_convergence plan](D:\software\.cursor\plans\bitcoin_chaos_convergence_a219e7b9.plan.md), [integration plan](D:\software\.cursor\plans\bitcoin_chaos_convergence_integration_827d4828.plan.md), [local-proto/TODO.md](../../local-proto/TODO.md) #19 |
| AL2a | done | Plan integration: Fedimint/ACE/PentAGI column, observation framework, ACE-Harness mapping, Section 9.5 | [bitcoin_chaos_convergence_a219e7b9](D:\software\.cursor\plans\bitcoin_chaos_convergence_a219e7b9.plan.md) |
| A4 | done | Fedimint observation template | [FEDIMINT_OBSERVATION_TEMPLATE.md](../../docs/FEDIMINT_OBSERVATION_TEMPLATE.md) |
| A5 | done | Fedimint column in Chaos-Bitcoin mapping | [CHAOS_BITCOIN_MAPPING.md](../../docs/CHAOS_BITCOIN_MAPPING.md) |
| B4 | done | PENTAGI_FEDIMINT_ACE_ROADMAP consolidation doc | [PENTAGI_FEDIMINT_ACE_ROADMAP.md](../../docs/PENTAGI_FEDIMINT_ACE_ROADMAP.md) |
| B5 | done | ACE layers → harness components mapping | PENTAGI_FEDIMINT_ACE_ROADMAP §2 |
| B6 | pending | Add Fedimint AuthModule to BITCOIN_OBSERVATION_SOURCES | [integration plan](D:\software\.cursor\plans\bitcoin_chaos_convergence_integration_827d4828.plan.md) §6 |
| C4 | pending | Fedimint testnet exploration (3–5 guardian; AuthModule design) | deep-research-report §7 |
| C5 | pending | Capability token schema (Fedimint-native or standalone) | PentAGI protocol; deep-research-report §4 |
| AL3 | pending | Identity/Cultural Context: Add identity_context schema and template for multi-community, evolving self. Private data/. | bitcoin_chaos plan Section 8, [local-proto/TODO.md](../../local-proto/TODO.md) #20 |
| AL4 | pending | Python Bitcoin Modules (Research): Evaluate bitcoinlib, l402-requests, LangChainBitcoin. Skeptical of Coinbase, custodial. | bitcoin_chaos plan Section 9, [local-proto/TODO.md](../../local-proto/TODO.md) #21 |

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
| H1 | done | Playwright skills audit (gap inventory, audit checklist, recommendations) | [playwright_skills_audit_prep.plan.md](../plans/playwright_skills_audit_prep.plan.md) |
| H2 | pending | Run continual-learning once transcripts exist to populate AGENTS.md | [run_continual_learning_prompt.ps1](../scripts/run_continual_learning_prompt.ps1), [SKILL_SELF_IMPROVEMENT_WINS.md](../docs/SKILL_SELF_IMPROVEMENT_WINS.md) |
| H3 | pending | campaign_kb Playwright fixtures: Add fixtures/mocks so campaign_kb Daggr tests (search, merge, ingest) run without a real DB. Use in-memory SQLite or mock DB layer. | [daggr_test_matrix.md](../docs/daggr_test_matrix.md), [DAGGR_MCP.md](../docs/DAGGR_MCP.md) |
| H4 | pending | Add Playwright smoke to run_daggr_tests.ps1; add quantitative analysis (pass/fail counts, duration, per-stack breakdown) alongside smoke test | [run_daggr_tests.ps1](../scripts/run_daggr_tests.ps1), [daggr_test_matrix.md](../docs/daggr_test_matrix.md) |

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
| AT1 | pending | AI Trends MCP: Implement WhisperX fallback for videos without captions | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) |
| AT2 | pending | AI Trends MCP: Add Firecrawl/Playwright for FutureTools JS-heavy pages if scrape incomplete | [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md) |

---

## PENDING_AFTER_RESTART

| ID | Status | Task | Spec / Link |
|----|--------|------|-------------|
| R1 | pending | **obsidian-vault MCP:** Check Cursor Settings → MCP; confirm obsidian-vault shows running or has errors | Session 2026-03-11 |
| R2 | pending | **obsidian-vault MCP:** Re-test foam-pkm prompt 1 (create note in Obsidian vault about Bitcoin-Chaos mapping); verify agent uses `apply_patch` not `Write` | [TEST_PROMPTS.md](../skills/foam-pkm/TEST_PROMPTS.md) #1 |
| R3 | pending | **Critic follow-up:** Apply critic fixes (known-issues obsidian-vault entry; SKILL.md guardrail; AI_TASK_EVALS; TEST_PROMPTS procedure; test_mcp_and_audit skip) | Critic report 2026-03-11 |
