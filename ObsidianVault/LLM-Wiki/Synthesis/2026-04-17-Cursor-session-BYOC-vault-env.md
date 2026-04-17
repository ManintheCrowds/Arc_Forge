---
title: Cursor session log — BYOC archive + Obsidian vault env
date: 2026-04-17
tags:
  - type/synthesis
  - domain/cursor
  - domain/harness
source: Cursor agent transcript (logged by operator request)
---

# Session summary (logged from Cursor)

## What we did

1. **Nate B Jones / BYOC “working intelligence”** — Archived integrated notes in MiscRepos adhoc: `MiscRepos/.cursor/state/adhoc/2026-04-17_nate-b-jones-byoc-working-intelligence.md` (four layers, BYOC stack, cross-links to AI Trends SHA manifest, SCP-ANT1 + L402, CHAOS_BITCOIN_MAPPING, signing vs encryption vs payment table).
2. **Obsidian operator handoff** — Clarified “log into vault” vs **logging conversation**: MCP has **no cloud login**; Obsidian app opens the vault folder. Wrote `MiscRepos/.cursor/state/adhoc/2026-04-17_obsidian_vault_mcp_operator_handoff.md`.
3. **This note** — Conversation **logged into the vault** under `LLM-Wiki/Synthesis/` for Obsidian search and graph.

## Env confirmation (this machine)

**User env is set** (verified same day):

| Variable | Value |
|----------|--------|
| `OBSIDIAN_VAULT_ROOT` | `C:\Users\Dell\Documents\GitHub\Arc_Forge\ObsidianVault` |
| `VAULT_SYNC_SAFE_BASE` | `C:\Users\Dell\Documents\GitHub` |

Vault path exists on disk. Align `%USERPROFILE%\.cursor\mcp.json` obsidian-vault `env` with these values and **restart Cursor** after changes.

## Automation vs manual log

- **`session_save` MCP** — Use on future handoffs when obsidian-vault MCP is connected (writes `.cursor_context/sessions.db`).
- **`npm run vault:sync`** — Mirrors MiscRepos `.cursor/state` → `Harness/`; does **not** auto-import arbitrary chat unless scripted.
- **This file** — Manual **conversation export** into vault PKM tree.

## Wikilinks

- [[Handoff-Latest]] — after `vault:sync` from MiscRepos
- Harness docs: [[Harness/Docs/OBSIDIAN-VAULT-INTEGRATION]] if mirrored (filename may differ; check `Harness/Docs/` after sync)

## MiscRepos paths (for copy-out)

- `e:\local-proto\workspace` / `C:\Users\Dell\Documents\GitHub\MiscRepos` — multi-root workspace
- BYOC adhoc: `.cursor/state/adhoc/2026-04-17_nate-b-jones-byoc-working-intelligence.md`
- Vault MCP handoff adhoc: `.cursor/state/adhoc/2026-04-17_obsidian_vault_mcp_operator_handoff.md`
