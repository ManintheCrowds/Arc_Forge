# MCP Capability Map

Per-server mapping of user/domain actions to agent tools. Update when adding tools. See agent-native architecture (compound-engineering plugin) for parity discipline.

## Workspace

- **Filesystem:** D:/portfolio-harness, D:/Arc_Forge (shared)
- **Obsidian vault:** D:/Arc_Forge/ObsidianVault (under Arc_Forge)
- **Foam workspace:** Any folder with .foam/ or foam-template; may overlap with ObsidianVault
- **SQLite:** D:/Arc_Forge/campaign_kb/data/kb.sqlite3
- No agent sandbox; agent and user work in same data space.

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
| Verify PentAGI | `run_terminal_cmd` → `.\.cursor\scripts\verify_pentagi_protection.ps1` | Done |
| Log agent event | `run_terminal_cmd` → `python .cursor/scripts/log_agent_event.py` | Done |
| Check handoff integrity | `run_terminal_cmd` → `python .cursor/scripts/check_handoff_integrity.py` | Done |
| Check intent checksum | `run_terminal_cmd` → `.\local-proto\scripts\check_intent_checksum.ps1` | Done |

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

**Note:** Get, create, update, revoke, export require APPROVAL_NEEDED per TOOL_SAFEGUARDS.

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
| Run verify_integration | `run_verification` | Done |
| Run Playwright smoke test | `run_playwright_smoke` | Done |

**Note:** Multi-stack (WatchTower, campaign_kb). See [DAGGR_MCP.md](DAGGR_MCP.md) for usage. For UI-driven verification, agent can also use cursor-ide-browser or playwright MCP to navigate to http://localhost:7860.

---

## observation

| User action | Agent tool | Status |
|-------------|------------|--------|
| Append observation | `observation_log_append` | Done |

---

## provenance

| User action | Agent tool | Status |
|-------------|------------|--------|
| Document provenance | `document_provenance_record` | Done |

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

## Parity workflow

When adding a new UI action or MCP tool:

1. Add row to this capability map
2. Update skill capability map if a skill uses the tool
3. Add to org-intent escalation_tools if human-gated
4. Test with natural language request

When adding a harness script: add to MCP_CAPABILITY_MAP (Harness section) and COMMANDS_README.md.

See [AGENT_NATIVE_CHECKLIST.md](AGENT_NATIVE_CHECKLIST.md) for PR checklist.
