# Decision log

Append entries below using the schema in [README.md](README.md).

## 2025-02-06
- **[Development review]** Decision: Development review and gap analysis performed; state docs and READMEs are source of truth for status and test commands. Rationale: Plan implementation; handoff and known-issues updated so next session has single reference. (plan: dev_plan_review_and_gap_analysis_11477fa9)

## 2026-02-07
- **[Shell]** Decision: Use `;` to chain commands in PowerShell, not `&&`. Rationale: `&&` is not a valid statement separator in PowerShell; use `Set-Location D:\path; python -m pytest ...` or run commands separately. (plan: workflow_ui_task_decomposed_workflow_9b54f027)

## 2026-02-09
- **[RAG]** Decision: Add a model-as-judge critic loop with stored reports and CI gate for RAG outputs. Rationale: Enforce quality and traceability across docs, workflow UI, and code. (plan: rag-critic-loop_9a3ab95b)
- **[Security governance]** Decision: Standardize per-repo `project-metadata.yml` with data-tier labels and required scanning flags. Rationale: Portable labeling and enforceable security posture across repos. (plan: private-repo-audit-framework)
- **[Handoff workflow]** Decision: Always archive `handoff_latest.md` into `.cursor/state/handoff_archive/YYYYMMDD-HHMM.md` with a timestamped title before updates. Rationale: Prevents overwrites and preserves full history. (plan: draft-ci-security-workflows_ee6ca728)
- **[Security Phase0]** Decision: Triage CRITICAL credential findings in documentation as false positives. Rationale: All 10 CRITICAL findings are in D:/software docs (example API keys, example passwords, SMTP placeholder, Grafana reset SQL example); not live secrets. Scanner `security_audit.py` now treats files under `docs/` as allowlisted for CRITICAL credentials. (plan: codebase_and_github_upload_analysis)

## 2026-02-11
- **[Portfolio CI]** Decision: Implemented portfolio codebase deep evaluation plan—WatchTower_main test collection fixed (added __init__.py to test packages); workflow_ui + scripts CI added to Arc_Forge; moltbook-watchtower tests + Gitleaks CI; obsidian_cursor_integration pytest CI; Gitleaks for Arc_Forge; WatchTower_main tests workflow; software README hero (Problem→Solution→Impact). Rationale: Portfolio readiness and CI hardening per plan. Critic (domain: docs): software README hero pass (intent_alignment:4, safety:5, correctness:4, completeness:4, minimality:4). Critic (domain: code): CI workflows pass (no secrets, standard actions). (plan: portfolio_codebase_deep_evaluation_72c4aaba)
- **[Software tests]** Decision: Fix config validation tests with _TestSettings (settings_customise_sources to exclude env/dotenv) and build_settings(cors_origins=[]). Rationale: conftest and .env set SECRET_KEY/JWT_SECRET_KEY/DEBUG; pydantic-settings model_validate merges with env—tests require deterministic isolation. (plan: portfolio_codebase_deep_evaluation_72c4aaba)
- **[Software README]** Decision: Add badges (Python 3.11+, License) and Mermaid architecture diagram to software README. Rationale: Portfolio template asks for badges and one diagram; improves scannability. Critic (domain: docs): pass (intent_alignment:4, safety:5, correctness:4, completeness:4, minimality:4). (plan: portfolio_codebase_deep_evaluation_72c4aaba)

## 2026-02-12
- **[Cognition]** Decision: Implemented cognition batch: knowledge_seed_pattern, human_feedback_capture, product_scope_skill, refactor_reuse_skill. Created preferences.md, rejection_log.md; added product-scope and refactor-reuse skills with role-routing. Rationale: Complete tactical improvements per cognition_improvements_index. (plan: cognition_next_steps_8db593c8)
- **[Arc_Forge docs]** Decision: Error monitoring docs plan (error_monitoring_traceback_docs) completed—doc-only restructure; schema fix and error-reporting remain separate implementation tasks. Rationale: Document what cannot be resolved; improve scanability and cross-links. (plan: error_monitoring_traceback_docs_cc15a172)

## 2026-02-19
- **[Local-first]** Decision: Updated RESOURCES.md with Liveblocks, oreZ, PardusDB, SyncLayer, LoFi/34. Rationale: Gap analysis identified missing tools; prioritization P0–P4 in gap_analysis_localfirst_integration_20260219.md. (plan: gap_analysis_local-first_integration_readiness)

## 2026-02-20
- **[Handoff scripts]** Decision: Added .cmd wrappers and Windows redirect to .sh scripts to prevent "pick a file" and command-window popups on Windows. Rationale: .sh has no default app on Windows; docs now surface .ps1/.cmd first. (plan: windows_script_popup_fix_783017dc)

## 2026-02-27
- **[Context integration]** Decision: Created CONTEXT_INTEGRATION_AUDIT.md with tool inventory, quick wins, and Playwright MCP setup. Added Playwright MCP to .cursor/mcp.json. Rationale: Audit context systems, ensure Playwright available to MCP for Daggr/Gradio verification. (plan: context integration audit)
- **[Observability layer]** Decision: Implemented AI observability layer (OBSERVABILITY_LAYER.md, audit_wrapper.py) — observation, logging, maintenance above AI with no AI access. Audit path: %LOCALAPPDATA%\local-proto\audit\. Added Filesystem, SQLite, Git MCP servers to mcp.json with allowlist/safeguards. Rationale: Traceability per AI_SECURITY; human-only audit; MCP expansion per plan. (plan: ai_observability_layer_and_mcp_expansion_66a16773)

## 2026-02-24
- **[OSINT]** Decision: Cloned 7 repos (theHarvester, SpiderFoot, Maigret, Amass, Subfinder, nitefood/asn, asnmap) into osint-tools/. Rationale: Fills email/domain, username, ASN/geo gaps per plan; complements GhostTrack and PentAGI. (plan: osint_tools_research_65b48b80)
- **[PentAGI tests]** Decision: Use pure-Go SQLite (`modernc.org/sqlite`) for auth and services tests when `CGO_ENABLED=0`. Rationale: Avoids gcc dependency; CI and Windows dev can run tests without C toolchain. Build tags: `cgo` for gorm/dialects/sqlite, `!cgo` for modernc.org/sqlite.
- **[PentAGI dev]** Decision: Chocolatey `choco install mingw` can fail with lock file or permission errors when run without admin. Rationale: Documented in known-issues; use pure-Go SQLite for tests instead of installing Mingw.

## 2026-02-29
- **[Vehicle recovery]** Decision: Reapplied browser-web skill; verified DeFlock, 511mn, StolenCar.com, NICB with Browser Ready Pattern; documented findings in case note, DIGITAL_WORLD_INTERFACE, camera map, known-issues. Rationale: Verification pass per reapply_browser_skills plan; StolenCar.com confirmed unreachable.

## 2026-03-02
- **[Frontier operations]** Decision: Implemented frontier-ops-kb (knowledge base), frontier-ops skill, calibration measurement harness, MCP seam design docs, role-routing branch. Rationale: Ingest Frontier AI Operations and MCP concepts per plan; calibration > knowledge; MCP as standardized seam design.
- **[Intent alignment]** Decision: Added frontier-ops and planning to AGENT_INTENT role table; tightened handoff intent and intent_surface for post-vehicle-case state. Rationale: Single source of truth for roles; intent clarity per INTENT_ENGINEERING; human as final arbiter.
- **[Vehicle recovery]** Decision: Vehicle recovered at 1515 Park Ave Minneapolis. Documented post-recovery: stolen NEO4IC ZYPHR 2 BLACK jacket (~$180), forensic leads (Wendy's receipt, cigarette trash). Added jacket marketplace monitoring (Craigslist, FB Marketplace, Poshmark, Mercari); receipt search before disposal. Rationale: Case status update; actionable follow-up for jacket and forensic evidence.
- **[Vehicle recovery]** Decision: Corrected plate attribution (victim ZHL 655; perp unknown) and time window (9:16–9:36 PM). Rationale: User correction.
- **[Playwright audit]** Decision: Vehicle case closed. New focus: Playwright skills audit prep. Created playwright_skills_audit_prep.plan.md with gap inventory (account creation, navigation, agentic), audit checklist, recommendations. Rationale: User reports browser skills not operating as needed; audit before implementing.

## 2026-03-03
- **[OpenClaw/Jarvis eval]** Decision: OpenClaw recommended for Signal-first HITL; Jarvis for MCP handoff path. Both local/offline. OpenClaw aligns with TOOL_SAFEGUARDS (Signal, SOUL.md); Jarvis needs custom MCP wiring. Rationale: Wave 4 D3/D4 eval per wave_2_high-priority_gates plan. (plan: wave_2_high-priority_gates_817efedf)

## 2026-03-04
- **[AI credential vault]** Decision: Created AI_CREDENTIAL_VAULT_DESIGN.md — proposal for AI-managed credential system (create, store, retrieve, rotate, revoke) with human gates at create/rotate/revoke; vault MCP or local tool; encrypted storage. Rationale: Unblock save-search flows without per-run human credential injection; extends TOOL_SAFEGUARDS credential seam.
- **[AI credential vault implementation]** Decision: Implemented credential vault per scope_credential_vault.md — credential_vault/ (encrypted JSON), credential_vault_mcp.py (MCP server), mcp.json credential-vault entry, browser-web SKILL and TOOL_SAFEGUARDS updates, PLAYWRIGHT_SAVE_SEARCH_RUNBOOK vault-first flow. Rationale: Plan ai_credential_vault_product_scope_76f8a8bd.
- **[Governance and audit]** Decision: Implemented governance and audit gap closure — audit_wrapper org-intent gate (ORG_INTENT_ENFORCE, ORG_INTENT_PATH), intent_decisions.jsonl audit trail, escalation_tools in org-intent.example.json, decision-log intent_ref, AGENT_TELEMETRY intent_check. ORG_INTENT_ENFORCE=0 by default (audit-only). Rationale: Plan governance_and_audit_gaps_69757350.

## 2026-03-09
- **[Plan preservation]** Decision: Keep `.cursor/plans/` in D:\software repo; do not remove plans. Unstaged plan deletions. Rationale: Plans are operational context; removal loses traceability. For privacy: consider private repo, private submodule, or repo visibility change—Git has no per-folder visibility. (plan: bitcoin_chaos_convergence_integration_827d4828)
- **[Bitcoin-Chaos integration]** Decision: Integration sub-tasks A4, A5, B4, B5 done (Fedimint template, CHAOS_BITCOIN_MAPPING, PENTAGI_FEDIMINT_ACE_ROADMAP, ACE-Harness mapping). B6, C4, C5 pending. Status in pending_tasks.md. Rationale: Track integration progress; handoff continuity.
- **[Plan submodule migration]** Decision: Migrated `.cursor/plans/` to private repo Planswithinplans (https://github.com/ManintheCrowds/Planswithinplans) as git submodule. software and portfolio-harness now reference submodule at .cursor/plans; plans stay versioned but not publicly visible when parent repos are public. Run `git submodule update --init` after clone if you have access. Rationale: Plan preservation decision; privacy without removal. (plan: plans_submodule_migration_9ca49db0)
- **[Value Hierarchy Review Easy Wins]** Decision: All 6 easy wins + S1 done. Path validation for LOCAL_PROTO_AUDIT_DIR; evil.com→malicious-payload.example.invalid. (plan: value_hierarchy_review_easy_wins_a205c561)
- **[Critique follow-up]** Decision: Path validation for LOCAL_PROTO_AUDIT_DIR; TACTICAL_CRITIQUE_PLANS.md (NIM/Llama, drift baseline, portable-skills, plan strategy); shorter decision-log format.