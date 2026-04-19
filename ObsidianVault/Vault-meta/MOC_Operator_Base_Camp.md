---
title: Operator base camp (MOC)
tags:
  - type/operator-moc
  - domain/harness
  - status/active
date: 2026-04-16
---

# Operator base camp (MOC)

**Canonical vault map:** [[Vault-meta/START_HERE]] — full priority table and TTRPG vs harness split. **This page** is the short **operator door** (default first open for harness sit-down when you want handoff + resync + wiki links without scanning the full index).

Five-minute entry map for **Harness** (mirrored harness state), **LLM Wiki** (compounding canon), and **research/** operator runbooks. SSOT for automation state remains **MiscRepos** `.cursor/state`; do not edit `Harness/**` as SSOT.

## Core links

- **Brain Map (vault in context atlas):** MiscRepos [BRAIN_MAP_HUB.md](../../../MiscRepos/docs/BRAIN_MAP_HUB.md) — set **`BRAIN_MAP_VAULT_ROOTS`** / **`BRAIN_MAP_VAULT_LABELS`** so OpenGrimoire `/context-atlas` includes this vault; § *Environment variables* + `MiscRepos/.cursor/brain-map.env.example`
- **Harness handoff hub:** [[Harness/Handoff-Latest]]
- **LLM Wiki index:** [[LLM-Wiki/_index]]
- **Vault resync / scheduler commands:** [[research/Int-Vault-Resync-Operator-Archive]]
- **LLM Wiki vault contract (Arc_Forge):** [[Vault-meta/00_LLM_WIKI_VAULT]]
- **Foam-pkm TEST_PROMPTS #1 sample note:** [[LLM-Wiki/Topics/Bitcoin-Chaos-mapping-foam-pkm-test1]]

## Repo specs (open in editor; not wikilinks)

- MiscRepos engineering spec: `MiscRepos/docs/superpowers/specs/2026-04-16-obsidian-vault-llm-wiki-gui-agent-native-engineering.md`
- Harness write contract: `MiscRepos/local-proto/docs/HARNESS_VAULT_WRITE_CONTRACT.md`

## Quick grep targets

| Need | Where |
|------|--------|
| MCP setup | `MiscRepos/obsidian_cursor_integration/docs/MCP_SETUP.md` |
| Sync script | `MiscRepos/local-proto/scripts/sync_harness_to_vault.ps1` |
| Guarded resync | `MiscRepos/local-proto/scripts/int-vault-resync.ps1` |
