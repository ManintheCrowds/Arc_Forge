---
title: "MCP Capability Map"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# MCP Capability Map

**Maintenance (P2):** Review this file when adding or removing MCP servers or tools; keep [MCP_SKILL_ROUTING.md](MCP_SKILL_ROUTING.md) and host `mcp.json` in sync. See [MCP_TRANSPARENCY.md](../../../openharness/docs/MCP_TRANSPARENCY.md) in OpenHarness when this workspace includes a sibling `openharness` clone. Least privilege: only enable servers the workflow needs.

Per-server mapping of user/domain actions to agent tools. Update when adding tools. See agent-native architecture (compound-engineering plugin) for parity discipline.

## Workspace

- **Filesystem:** D:/portfolio-harness, D:/Arc_Forge (shared)
- **Obsidian vault:** D:/Arc_Forge/ObsidianVault (under Arc_Forge)
- **Foam workspace:** Any folder with .foam/ or foam-template; may overlap with ObsidianVault
- **SQLite:** D:/Arc_Forge/campaign_kb/data/kb.sqlite3
- No agent sandbox; agent and user work in same data space.

---

## Overlapping surfaces — when to use which

Use **one** primary path per task; do not chain multiple browsers or duplicate fetches without reason.

### Web: fetch vs browser vs scraping

| Need | Primary | Fallback / notes |
|------|---------|------------------|
| Static page, no JS required, read-only | **web** / `mcp_web_fetch` (if configured) | Low protection only |
| In-editor UI testing, SPA, forms, maps, dashboards | **cursor-ide-browser** (`browser_*`) | Default for “test my app in the browser” in Cursor; lock → interact → unlock |
| Headless automation outside Cursor UI, CI-style scripts | **playwright** MCP (`playwright_browser_*`) | Optional second server; avoid using **both** playwright and cursor-ide-browser on the same page in one turn |
| Bulk URLs, extraction to markdown/HTML, stealth / high protection | **scrapling** MCP (`scrapling_*` / `mcp_scrapling_*`) | Prefer over raw fetch when JS or WAF; see scrapling tool docs |
| Daggr simple workflow smoke | **daggr** `run_playwright_smoke` | Starts Gradio if needed; not a substitute for full site exploration |

**Skill / deep reference:** [browser-web SKILL](../skills/browser-web/SKILL.md), [DIGITAL_WORLD_INTERFACE.md](DIGITAL_WORLD_INTERFACE.md).

### Docs and code retrieval (context budget)

| Need | Primary | Avoid |
|------|---------|--------|
| Third-party library / framework docs | **context7** (resolve-library-id → query-docs) | Pasting huge doc into chat |
| Our repo, symbol by name | **jcodemunch** `search_symbols` → `get_symbol` | Full-file read for large modules |
| Our repo, “how does X work?” | **codebase_search** with narrow `target_directories` | Unbounded grep |
| Our repo, known path + lines | **read_file** with `offset` / `limit` | @-mention of huge files |
| Structural codebase graph (dependencies, coupling) | **Nogic** MCP **when enabled** in `mcp.json`; local index; complements jCodeMunch | Treating graph as substitute for tests or git; see [NOGIC_WORKFLOW.md](NOGIC_WORKFLOW.md) |

### SQLite tool naming

Packaging may expose `mcp_sqlite_*` or `sqlite_*`. Use whichever your `mcp.json` exposes; behavior is the same (list/describe/read/write/create). Confirm names in the host tool list before assuming.

### BrowserStack MCP (if enabled)

Use for **managed** test runs, Percy, accessibility scans, Test Management API — not for routine local `localhost` debugging. For local app iteration, prefer **cursor-ide-browser** or **playwright** per table above.

---

## harness

Agent achieves via `run_terminal_cmd` from repo root. See [COMMANDS_README.md](COMMANDS_README.md) for full command reference.

| User action | Agent capability | Status |
|-------------|------------------|--------|
| Copy continue prompt | `run_terminal_cmd` → `.\.cursor\scripts\copy_continue_prompt.ps1` | Done |
| Copy session start prompt | `run_terminal_cmd` → `.\.cursor\scripts\copy_session_start_prompt.ps1` | Done |
| Copy summarize today prompt | `run_terminal_cmd` → `.\.cursor\scripts\copy_summarize_today_prompt.ps1` | Done |
| Show next goals | `run_terminal_cmd` → `.\.cursor\scripts\show_next_goals.ps1` | Done |
| Run meta-review | `run_terminal_cmd` → `.\.cursor\scripts\run_meta_review.ps1` | Done |
| Run pre-commit security (handoff/state) | `run_terminal_cmd` → sanitize_input, validate_output, mask_secrets | Done |
| Run pre-commit security (rules/skills) | `run_terminal_cmd` → checksum_integrity --verify --strict | Done |
| Run context audit | `run_terminal_cmd` → `.\.cursor\scripts\audit_context_engineering.ps1 -Rubric` | Done |
| Run AI evals | `run_terminal_cmd` → `.\.cursor\scripts\run_ai_evals.ps1` | Done |
| Run Daggr tests | `run_terminal_cmd` → `.\.cursor\scripts\run_daggr_tests.ps1` | Done |
| Setup credentials | `run_terminal_cmd` → `python .cursor/scripts/setup_env.py` | Done |
| Install curated agency-agents | `run_terminal_cmd` → `python .cursor/scripts/install_agency_agents.py --clone` | Done |
| Verify PentAGI | `run_terminal_cmd` → `.\.cursor\scripts\verify_pentagi_protection.ps1` | Done |
| Log agent event | `run_terminal_cmd` → `python .cursor/scripts/log_agent_event.py` | Done |
| Check handoff integrity | `run_terminal_cmd` → `python .cursor/scripts/check_handoff_integrity.py` | Done |
| Check intent checksum | `run_terminal_cmd` → `.\local-proto\scripts\check_intent_checksum.ps1` | Done |
| Merge OpenRAG MCP block | `run_terminal_cmd` → `python .cursor/scripts/merge_mcp_openrag.py` | Done |
| Start OpenRAG and verify | `run_terminal_cmd` → `.\.cursor\scripts\start_openrag.ps1` | Done |
| Start fish-speech server | `run_terminal_cmd` → `.\.cursor\scripts\start_fish_speech.ps1` | Done |
| Rebuild brain map graph | `run_terminal_cmd` → `python .cursor/scripts/build_brain_map.py` | Done |

---

## OpenGrimoire / Brain Map

| User action | Agent capability | Status |
|-------------|------------------|--------|
| Start OpenGrimoire dev server | `run_terminal_cmd` → `Set-Location D:\portfolio-harness\OpenGrimoire; npm run dev` (PowerShell; use `;` not `&&`). Port 3001. If chunk errors: `npm run clean` then `npm run dev`. See [OpenGrimoire/TROUBLESHOOTING.md](../../OpenGrimoire/TROUBLESHOOTING.md). | Done |
| View agent cognition graph | Read `.cursor/state/ports.json` (or `ports.json.template` if missing) for `services.opengrimoire.baseUrl`; if absent use `http://localhost:{defaults.opengrimoire}`. Navigate to `{baseUrl}/context-atlas` (or `/brain-map` legacy alias). See [PORT_REGISTRY.md](PORT_REGISTRY.md). | Done |
| Rebuild graph data | `run_terminal_cmd` → `python .cursor/scripts/build_brain_map.py` | Done |
| CRUD alignment context items (HTTP parity) | `run_terminal_cmd` from `OpenGrimoire`: `node scripts/alignment-context-cli.mjs list\|create\|patch\|delete` with `OPENGRIMOIRE_BASE_URL` and optional `ALIGNMENT_CONTEXT_API_SECRET`. Contract: [ALIGNMENT_CONTEXT_API.md](../../OpenGrimoire/docs/agent/ALIGNMENT_CONTEXT_API.md). | Done |
| Human operator CRUD (browser) | Log in as admin → `/admin/alignment` (session BFF, no shared secret in client). | Done |

**Note:** Brain Map visualizes co-access relationships from `.cursor/state/` (daily logs, handoffs, handoff_archive, decision-log). Parser outputs `OpenGrimoire/public/brain-map-graph.json`. API route `/api/brain-map/graph` serves the JSON; optional `BRAIN_MAP_SECRET` for access control when deployed beyond localhost.

**Optional thin MCP (stdio):** Package [`OpenGrimoire/mcp-server/README.md`](../../OpenGrimoire/mcp-server/README.md) — tools `opengrimoire_capabilities_get`, `opengrimoire_alignment_context_list`, `opengrimoire_brain_map_graph_get` are thin `fetch` wrappers to existing REST routes only (no duplicate business logic). Configure `OPENGRIMOIRE_BASE_URL` and alignment/brain-map secrets per README.

---

## obsidian-vault

| User action | Agent tool | Status |
|-------------|------------|--------|
| Create note | `apply_patch` (new file) | Done |
| Edit note | `apply_patch` | Done |
| Search notes | `vault_search` | Done |
| Get note context | `note_context` | Done |
| Load context files | `load_context_files` | Done |
| Run automation | `run_automation` | Done |
| Session save/history | `session_save`, `session_history` | Done |
| Index health | `index_health` | Done |
| LLM summarize/suggest | `llm_summarize_local`, `llm_suggest_local` | Done |
| Delete note | filesystem `move_file` to `.trash/` or `apply_patch` (empty content) | Done |

---

## foam-pkm (Foam + Obsidian)

Skill: [foam-pkm](../skills/foam-pkm/SKILL.md). Tool selection by vault type: ObsidianVault → obsidian-vault MCP; Foam workspace → filesystem.

| User action | Foam (agent) | Obsidian (agent) | Status |
|-------------|--------------|------------------|--------|
| Create note | `write_file` | `apply_patch` (new file) | Done |
| Edit note | `edit_file` / `write_file` | `apply_patch` | Done |
| Search notes | `grep` or search_files | `vault_search` | Done |
| Get note context | `read_file` | `note_context` | Done |
| Create wikilink | Write `[[Note Title]]` | Same | Done |
| Daily note | Template + write to daily path | `session_save` or `apply_patch` | Done |
| Delete note | `move_file` to `.trash/` | `apply_patch` (empty) or move to .trash | Done |

**Note:** Foam has no MCP; agent uses filesystem. Graph visualization is UI-only (N/A for agent).

### Harness Obsidian vault scripts (terminal only)

No MCP tools—these run via **`run_terminal_cmd`** from repo root (operator or agent). See also [OBSIDIAN_GITHUB_GAP_ANALYSIS.md](../../local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md).

| Script | Purpose |
|--------|---------|
| `local-proto/scripts/Lint-ObsidianVaultContract.ps1` | Vault contract / frontmatter lint against harness rules |
| `local-proto/scripts/Scan-ObsidianTagGaps.ps1` | Tag / dimension gap scan → report under vault `_meta/` |
| `local-proto/scripts/Scan-ObsidianOrphans.ps1` | Read-only orphan / weak wikilink scan → `_meta/Orphan-Link-Report.md` (set `OBSIDIAN_VAULT_ROOT` or `-VaultRoot`) |
| `local-proto/scripts/Get-ObsidianVaultGraphSlice2bMetrics.ps1` | Read-only **GRAPH_VIEWS** §2 / §2b metrics (default `-Slice 2b`; `-Slice 2` for full §2) |
| `local-proto/scripts/Add-ObsidianVaultFrontmatter.ps1` | Add or normalize frontmatter (`-DryRun` first) |

**Agent onboarding:** same paths, env, and §2 definition as humans — [AGENT_ENTRY_INDEX.md](AGENT_ENTRY_INDEX.md) row *Running read-only Obsidian vault audits*; detail table [LLM_WIKI_VAULT.md](../../local-proto/docs/LLM_WIKI_VAULT.md) § Tagging and mechanical lint.

---

## credential-vault

| User action | Agent tool | Status |
|-------------|------------|--------|
| Store credential | `credential_vault_create` | Done |
| Retrieve credential | `credential_vault_get` | Done |
| Update credential | `credential_vault_update` | Done |
| List credentials | `credential_vault_list` | Done |
| Revoke credential | `credential_vault_revoke` | Done |
| Export vault | `credential_vault_export` | Done |

**Note:** Server-side gate: **retrieve** (`credential_vault_get`), create, update, revoke, and export require `CREDENTIAL_VAULT_APPROVE=1` or return `APPROVAL_NEEDED`. **`credential_vault_list`** is ungated (metadata only: site + created; no secrets). Audit: `credential_vault_gate.jsonl`. Agent must still output `APPROVAL_NEEDED` per [TOOL_SAFEGUARDS.md](../../local-proto/docs/TOOL_SAFEGUARDS.md) before calling; human sets env before confirming.

---

## capability (local-proto)

| User action | Agent tool | Status |
|-------------|------------|--------|
| Verify capability before High/Critical action | `verify_capability` | Done |

**Note:** Stub returns verified=false until AuthModule (C4/C5). Before spend, PII, or irreversible actions, call verify_capability; if false, escalate (hb-4). Server: `local-proto/scripts/capability_mcp.py`.

---

## constraint-library

| User action | Agent tool | Status |
|-------------|------------|--------|
| List constraints | `constraint_library_list` | Done |
| Get constraint by id | `constraint_library_get` | Done |
| Add constraint | `constraint_library_add` | Done |
| Update constraint | `constraint_library_update` | Done |
| Remove constraint | `constraint_library_remove` | Done |

**Note:** Add, update, remove require APPROVAL_NEEDED per TOOL_SAFEGUARDS. Data source: `.cursor/state/rejection_log.json`. Id is 0-based index; indices shift after remove.

---

## docker

| User action | Agent tool | Status |
|-------------|------------|--------|
| Deploy stack | `docker_create_container` + `docker_start_container` | Done |
| List containers/images | `docker_list_containers`, `docker_list_images` | Done |
| Inspect container/image | `docker_inspect_container`, `docker_inspect_image` | Done |
| View logs | `docker_container_logs` | Done |
| Stop/start container | `docker_stop_container`, `docker_start_container` | Done |
| Remove container | `docker_remove_container` | Done (gated) |
| Prune images/volumes/system | `docker_prune_*` | Done (gated) |
| Run-once image update (Watchtower) | `run_terminal_cmd` → `docker run ... containrrr/watchtower --run-once [names]` | Done |
| Deploy Watchtower daemon (scheduled) | `run_terminal_cmd` → `docker run -d ... containrrr/watchtower --interval N` | Done (gated) |
| Rolling restart updates | `run_terminal_cmd` → Watchtower with `--rolling-restart` | Done |
| Check Watchtower logs | `docker_container_logs` (watchtower container) | Done |
| Stop Watchtower daemon | `docker_stop_container` (watchtower container) | Done |

**Note:** Watchtower (containrrr.dev/watchtower) for automated image updates. Run-once via `run_terminal_cmd`; daemon deploy requires APPROVAL_NEEDED. Skill: [docker-mcp](../skills/docker-mcp/SKILL.md).

---

## unhuman-deals

| User action | Agent tool | Status |
|-------------|------------|--------|
| Search products | `search_products` | Done |
| Get offers | `get_offers` | Done |

**Read-only.** No create/update/delete.

---

## filesystem

| User action | Agent tool | Status |
|-------------|------------|--------|
| Read file | `read_file` | Done |
| Write file | `write_file` | Done |
| List directory | `list_directory` | Done |
| Move/rename | `move_file` | Done |
| Edit file (line-based) | `edit_file` | Done |
| Create directory | `create_directory` | Done |
| Search files | `search_files` | Done |
| Delete file | `move_file` to `.trash/` or outside allowed dirs | Done (workaround) |

**Note:** @modelcontextprotocol/server-filesystem has no `delete_file`. Workaround: `move_file(source, ".trash/filename")` or move outside allowed directories. Create `.trash/` if needed.

---

## sqlite

| User action | Agent tool | Status |
|-------------|------------|--------|
| List tables | `list_tables` or catalog | Done |
| Describe table | `describe_table` | Done |
| Read data | `read_query` or `sqlite_execute` (SELECT) | Done |
| Write data | `write_query` or `sqlite_execute` (INSERT/UPDATE/DELETE) | Done |
| Create table | `create_table` | Done |

**Note:** Exact tool names vary by mcp-server-sqlite package. Verify with `uvx mcp-server-sqlite --help` or package docs.

---

## git

| User action | Agent tool | Status |
|-------------|------------|--------|
| Status, diff, log | git_* tools | Done |
| Commit, push, pull | git_* tools | Done |

---

## playwright

| User action | Agent tool | Status |
|-------------|------------|--------|
| Navigate, click, type | playwright_browser_* | Done |
| Screenshot | playwright_* | Done |

---

## lobster-university

| User action | Agent tool | Status |
|-------------|------------|--------|
| Sign register | `lobster_sign_register` | Done |
| Get attendance | `lobster_get_attendance` | Done |
| Get stats | `lobster_get_stats` | Done |
| Get recent | `lobster_get_recent` | Done |

---

## daggr

| User action | Agent tool | Status |
|-------------|------------|--------|
| List workflows | `list_workflows` | Done |
| Get workflow graph schema | `get_graph_schema` | Done |
| Get stack overview | `get_stack_overview` | Done |
| Run workflow by name | `run_workflow` | Done |
| Run verify_integration | `run_verification` | Done |
| Run Playwright smoke test | `run_playwright_smoke` | Done |

**Note:** Multi-stack (WatchTower, campaign_kb). See [DAGGR_MCP.md](DAGGR_MCP.md) for usage. For UI-driven verification, agent can also use cursor-ide-browser or playwright MCP to navigate to http://localhost:7860.

---

## WatchTower (via daggr MCP)

| User action | Agent tool | Status |
|-------------|------------|--------|
| Scan network for devices | `watchtower_discovery_scan` | Done |
| List devices | `watchtower_discovery_devices` | Done |
| Get device states | `watchtower_discovery_devices_status` | Done |
| Trigger failover | `watchtower_discovery_failover` | Done |

**Note:** Requires WatchTower Flask API (WATCHTOWER_API_URL, default http://localhost:5000).

**Deferred (multi-stack follow-up):** First-class MCP tools for **encoder / monitoring REST** (e.g. `/api/encoders/*`, `/api/alerts/*`, `/api/monitoring/*`) remain **curl / `run_terminal_cmd` recipes** in runbooks until an operator story requires agent parity without shell. When needed, extend Daggr MCP or document patterns here; see [action_parity_audit_cm3_2026-03-16.md](../state/adhoc/action_parity_audit_cm3_2026-03-16.md) § supersession banner.

---

## campaign_kb (via daggr MCP)

| User action | Agent tool | Status |
|-------------|------------|--------|
| Ingest PDFs | `campaign_kb_ingest` (source=pdfs) | Done |
| Ingest seeds | `campaign_kb_ingest` (source=seeds) | Done |
| Ingest DoD site | `campaign_kb_ingest` (source=dod) | Done |
| Ingest docs | `campaign_kb_ingest` (source=docs) | Done |
| Ingest campaign-docs | `campaign_kb_ingest` (source=campaign-docs) | Done |
| Ingest repos | `campaign_kb_ingest` (source=repos) | Done |

**Note:** Requires campaign_kb FastAPI (CAMPAIGN_KB_API_URL, default http://localhost:8001). Search: `mcp_sqlite_read_query` or openrag. Merge: `run_workflow` (campaign_kb, merge). PDF ingest: set **`PDF_BACKEND`** to `pdfplumber` (default) or `opendataloader` on the campaign_kb service. For RAG citations, LangChainChatBot `pdf_ingest`, and SCP on extracted text, see [docs/integrations/OPENDATALOADER_PDF.md](../../docs/integrations/OPENDATALOADER_PDF.md).

---

## scp (Secure Contain Protect)

| User action | Agent tool | Status |
|-------------|------------|--------|
| Inspect content for injection/hostility | `scp_inspect` | Done |
| Sanitize before handoff/state | `scp_sanitize` / `scp_run_pipeline` | Done |
| Quarantine suspect content | `scp_quarantine` | Done |
| Validate tool output | `scp_validate_output` | Done |
| Redact secrets before sharing | `scp_mask_secrets` | Done |
| Contain content as data | `scp_contain` | Done |
| Enable semantic judge for handoff/state | `scp_run_pipeline` with `options: {"semantic_judge": true}` or `SCP_SEMANTIC_JUDGE=1` | Done |
| Pull, aggregate, analyze AI Trends ingested content | `scp_analyze_ai_trends(date?)` — reads `.cursor/state/ai_trends/raw/`, runs inspect on each file | Done |
| List quarantine entries | `scp_list_quarantine` — returns `{ "quarantine": […], "_scp_meta": … }` | Done |
| Read threat registry stats (path, fingerprint, section sizes) | `scp_registry_summary` | Done |
| Read one threat registry section (capped) | `scp_registry_section` | Done |

**Note:** SCP sits between content sources and sinks (handoff, state, LLM context). Tool JSON includes **`_scp_meta`** (package version, harness hints, optional registry fingerprint). `scp_run_pipeline` includes **`steps`** (inspect → optional semantic_judge → sanitize → contain/quarantine). Findings include power_words, multilingual_override, morse_like, encoding_blocks, homoglyphs, structural_anomalies. See [SKILL.md](../skills/secure-contain-protect/SKILL.md) Inspection Categories.

---

## ai_trends (hub + MCP)

Server: `local-proto/scripts/ai_trends_mcp.py`. Full tool list and operator CLIs: [AI_TRENDS_MCP.md](../../local-proto/docs/AI_TRENDS_MCP.md). Primitive vs composite / cron caution: [MCP_TOOL_LAYERS.md](../../local-proto/docs/MCP_TOOL_LAYERS.md).

| User action | Agent tool | Status |
|-------------|------------|--------|
| Preview GitHub trending-style repos (metadata JSON, no raw files) | `fetch_github_trending` | Done |
| Preview Hugging Face trending models (metadata JSON, no raw files) | `fetch_huggingface_trending` | Done |
| Ingest GitHub hub items to `raw/{date}/` (SCP-gated per file) | `ingest_github_trending_to_raw` | Done |
| Ingest Hugging Face hub items to `raw/{date}/` (SCP-gated per file) | `ingest_huggingface_trending_to_raw` | Done |
| Run multi-source cron-style ingest (subprocess to `ai_trends_ingest.py`) | `run_ingestion_pipeline` — default `sources`: `youtube,futuretools,newsletters,github,huggingface` | Done |
| List ingested raw files for a date (MCP parity / E2E) | `list_ingested` | Done |
| Fetch YouTube metadata (single video) | `fetch_youtube_video_info` | Done |
| SCP-gated summarize of a raw content file | `summarize_content` | Done (composite — prefer primitive chain per [MCP_TOOL_LAYERS.md](../../local-proto/docs/MCP_TOOL_LAYERS.md)) |
| Fetch YouTube channel metadata | `fetch_youtube_channel` | Done |
| List caption tracks for a video | `list_video_subs` | Done |

**Note:** Single-source hub writes match CLI `python local-proto/scripts/ai_trends_ingest.py --sources github` or `--sources huggingface`. Post-ingest analysis remains `scp_analyze_ai_trends` (scp section above). Full tool enumeration lives in `local-proto/scripts/ai_trends_mcp.py` (`@mcp.tool`); extend this table when adding user-facing tools.

---

## survival-kb + scp assist stack (composed)

End-to-end pattern for **retrieval-grounded survival assistance** with safety seams—not a single MCP server, but a **recommended tool chain**. Full narrative: [local-proto/docs/brainstorms/2026-03-20-survival-vision-harness-pipeline.md](../../local-proto/docs/brainstorms/2026-03-20-survival-vision-harness-pipeline.md); vision primitive contract: [local-proto/docs/SURVIVAL_VISION_PRIMITIVE_CONTRACT.md](../../local-proto/docs/SURVIVAL_VISION_PRIMITIVE_CONTRACT.md).

| User / agent goal | Primary tools | Notes |
|-------------------|---------------|--------|
| Search private survival corpus (FTS5) | `survival_search`, `survival_get_chunk`, `survival_list_sources` | Server: `local-proto/scripts/survival_mcp.py`; `SURVIVAL_KB_ROOT` for `survival_kb.sqlite`. Disclaimer on every response. |
| Ingest extracted text (offline) | `run_terminal_cmd` → `python local-proto/scripts/survival_kb_ingest.py` | Not an MCP tool; keeps CRUD off agent for copyright/safety. |
| Gate synthesized answer or handoff | `scp_inspect`, `scp_run_pipeline`, `scp_validate_output` | Run on **final** narrative or chunk destined for LLM/state; reversal tier on survival manuals may be benign—human review per SURVIVAL_MEDICAL_RAG_DISCLAIMER. |
| Observability on Survival MCP | `audit_wrapper` wrapping `survival_mcp.py` | Logs tool + args hash only; see [MCP_SERVERS.md](../../local-proto/docs/MCP_SERVERS.md). |
| Machine vision (future) | Separate primitive: image → labels JSON | **Not** `survival_mcp`; see SURVIVAL_VISION_PRIMITIVE_CONTRACT. Compose: vision → `survival_search`. |
| Provenance for fetched docs | `document_provenance_record` | When URLs or hashes are part of automation. |

**Status:** survival-kb tools Done; composed vision pipeline Doc only until a vision MCP is added.

---

## openrag

| User action | Agent tool | Status |
|-------------|------------|--------|
| Query RAG / retrieve from knowledge base | openrag MCP tools (query, retrieve) | Done |
| Search campaign lore / docs | openrag MCP | Done |

**Note:** Requires OpenRAG running. Set OPENRAG_URL and OPENRAG_API_KEY in [mcp.json](../mcp.json). Frame retrieved chunks as data per [RAG_PROMPT_INJECTION_MITIGATIONS.md](RAG_PROMPT_INJECTION_MITIGATIONS.md). See [OPENRAG_INTEGRATION.md](OPENRAG_INTEGRATION.md).

---

## fish-speech

| User action | Agent tool | Status |
|-------------|------------|--------|
| Text to speech | `fish_speech_tts` | Done |

**Note:** Local-first. Run fish-speech Docker server (port 8080); set FISH_SPEECH_URL if different. See [FISH_SPEECH_INTEGRATION.md](FISH_SPEECH_INTEGRATION.md).

---

## observation

| User action | Agent tool | Status |
|-------------|------------|--------|
| Append observation | `observation_log_append` | Done |
| List observations | `observation_list` | Done |
| Read observation log | `observation_read` | Done |

---

## provenance

| User action | Agent tool | Status |
|-------------|------------|--------|
| Document provenance | `document_provenance_record` | Done |
| Bitcoin provenance | `bitcoin_provenance_record` | Done |
| List provenance entries | `provenance_list` | Done |

---

## jcodemunch

| User action | Agent tool | Status |
|-------------|------------|--------|
| Search symbols | `search_symbols` | Done |
| Get symbol | `get_symbol` | Done |

---

## scrapling

| User action | Agent tool | Status |
|-------------|------------|--------|
| Scrape/extract | scrapling tools | Done |

---

## Agent→UI data flow

Agent writes to files, SQLite, or config propagate to Daggr/Gradio on next request or restart. See [AGENT_UI_DATA_FLOW.md](AGENT_UI_DATA_FLOW.md) for diagram and update mechanisms.

---

## Partial Patterns (run_terminal_cmd + curl)

Actions the agent achieves via `run_terminal_cmd` and curl (or read_file/write_file) rather than dedicated MCP tools. Use when MCP is unavailable or for one-off calls.

| User action | Agent achieves via | Example |
|-------------|-------------------|---------|
| Get encoder status | curl GET /api/encoders/status | `run_terminal_cmd("curl -s http://localhost:5000/api/encoders/status")` |
| Control encoder | curl POST /api/encoders/\<id\>/control | `run_terminal_cmd("curl -s -X POST http://localhost:5000/api/encoders/1/control -H Content-Type:application/json -d '{\"action\":\"start\"}'")` |
| Get alert history | curl GET /api/alerts/history | `run_terminal_cmd("curl -s http://localhost:5000/api/alerts/history")` |
| Get monitoring status | curl GET /api/monitoring/status | `run_terminal_cmd("curl -s http://localhost:5000/api/monitoring/status")` |
| Get encoder health | curl GET /api/health/encoder/\<id\> | `run_terminal_cmd("curl -s http://localhost:5000/api/health/encoder/1")` |
| Get detailed health | curl GET /api/health/detailed | `run_terminal_cmd("curl -s http://localhost:5000/api/health/detailed")` |
| workflow_ui status | curl GET /api/status | `run_terminal_cmd("curl -s http://localhost:<port>/api/status")` |
| List arcs | read_file (Campaigns/) | `read_file` on arc directories |
| Run Daggr workflow | run_terminal_cmd → python -m daggr_workflows.run_workflow | Prefer `mcp_daggr_run_workflow` when available |

**Base URL:** WatchTower Flask default http://localhost:5000. workflow_ui port from app config.

---

## Parity workflow

When adding a new UI action or MCP tool:

1. Add row to this capability map
2. Update skill capability map if a skill uses the tool
3. Add to org-intent escalation_tools if human-gated
4. Test with natural language request

When adding a harness script: add to MCP_CAPABILITY_MAP (Harness section) and COMMANDS_README.md.

PR checklist: [AGENT_NATIVE_CHECKLIST.md](AGENT_NATIVE_CHECKLIST.md) (stub) → [OpenHarness `docs/AGENT_NATIVE_CHECKLIST.md`](../../OpenHarness/docs/AGENT_NATIVE_CHECKLIST.md) (normative) + [AGENT_NATIVE_CHECKLIST_MISCOPS.md](AGENT_NATIVE_CHECKLIST_MISCOPS.md) (MiscRepos addendum).
