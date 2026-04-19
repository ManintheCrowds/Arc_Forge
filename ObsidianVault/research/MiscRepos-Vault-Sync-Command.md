---
title: "MiscRepos harness → Obsidian vault sync"
tags:
  - type/runbook
  - status/verified
  - domain/harness
date: 2026-04-16
---

# MiscRepos harness → Obsidian vault sync

Archived command for repeating **Harness/** mirror sync from MiscRepos into this vault.

## PowerShell (explicit paths)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\local-proto\scripts\sync_harness_to_vault.ps1 -HarnessRoot "C:\Users\Dell\Documents\GitHub\MiscRepos" -VaultRoot "C:\Users\Dell\Documents\GitHub\Arc_Forge\ObsidianVault"
```

Run from **MiscRepos repo root** (parent of `local-proto/`).

## When env is already set

If `OBSIDIAN_VAULT_ROOT` and `VAULT_SYNC_SAFE_BASE` match your machine, you can omit `-VaultRoot` and use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\local-proto\scripts\sync_harness_to_vault.ps1 -HarnessRoot "C:\Users\Dell\Documents\GitHub\MiscRepos"
```

## References

- Mirrored doc in this vault (after sync): [[Harness/Docs/Intent-Elicitation-And-OG]]
- MiscRepos source: `docs/agent/INTENT_ELICITATION_AND_OG.md` under your clone (path if clone moves)
