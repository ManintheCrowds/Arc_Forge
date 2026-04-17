---
title: "Single-vault inventory (2026-04-17)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Single-vault inventory (2026-04-17)

**Plan:** Single-vault merge and env alignment (2026-04-17); operator checklist in [WORKSPACE_PATH_ENV_CHECKLIST.md § Single vault consolidation](../../../local-proto/docs/WORKSPACE_PATH_ENV_CHECKLIST.md#single-vault-consolidation).

## Canonical vault (operator target)

| Role | Path |
|------|------|
| **Physical vault** | `C:\Users\Dell\Documents\GitHub\Arc_Forge\ObsidianVault` |
| **Env** | `OBSIDIAN_VAULT_ROOT` = same · `VAULT_SYNC_SAFE_BASE` = `C:\Users\Dell\Documents\GitHub` |

**Persist on Windows:** System Properties → Environment Variables (user or system) **or** copy lines into `local-proto/.env` from [`.env.example`](../../../local-proto/.env.example) — repo automation does not set the machine for you. Cursor MCP must use the same pair ([checklist § Single vault consolidation](../../../local-proto/docs/WORKSPACE_PATH_ENV_CHECKLIST.md#single-vault-consolidation)).

## Candidate duplicates (this host)

| Path | Present | Notes |
|------|---------|--------|
| `C:\Users\Dell\Documents\GitHub\Arc_Forge\ObsidianVault` | Yes | **Canonical.** Top-level dirs include `Harness`, `Interview-Archive`, `LLM-Wiki`, `Campaigns`, `MOC-from-MiscRepos`, etc. |
| `D:\Arc_Forge\ObsidianVault` | No | Common legacy path from default `VAULT_SYNC_SAFE_BASE`; not present on machine that ran this inventory. |
| `E:\Arc_Forge\ObsidianVault` | No | Alternate drive; not present. |

If you later find another vault tree on disk or iCloud, **diff only outside `Harness/`** before retiring the old root; then zip/archive the old folder — see [WORKSPACE_PATH_ENV_CHECKLIST.md](../../../local-proto/docs/WORKSPACE_PATH_ENV_CHECKLIST.md) § Single vault consolidation.

## Merge outside Harness (this run)

**No second vault detected** — no file copy merge required. If Obsidian still lists an old vault, remove it from the vault switcher after archiving that folder.

## Archive / retire (this run)

**N/A** — no duplicate roots to archive on this host. Re-run this inventory after copying machines or attaching old drives.
