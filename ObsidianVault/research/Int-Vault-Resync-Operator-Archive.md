---
title: Int vault resync — operator archive
tags:
  - type/operator-runbook
  - status/verified
  - domain/harness
date: 2026-04-16
---

# Int vault resync — operator archive

Archived from MiscRepos harness work. **Do not treat this note as SSOT** for automation; canonical procedures live in the repo (`local-proto/docs/SCHEDULED_TASKS.md`, `.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md`, `.githooks/README.md`).

## Quick commands (MiscRepos root)

```powershell
# Full mirror (test / recovery)
.\local-proto\scripts\int-vault-resync.ps1 -HarnessRoot (Get-Location) -Trigger Scheduler -Force

# Inspect env
.\local-proto\scripts\Show-VaultSyncContext.ps1 -HarnessRoot (Get-Location)

# After registering the task in docs
schtasks /query /tn "Harness-IntVaultResync" /v /fo LIST
```

## Scheduled safety net

Register **Harness-IntVaultResync** (and optionally **Harness-VaultSync**) with Task Scheduler using the snippet in **MiscRepos** `local-proto/docs/SCHEDULED_TASKS.md` (`#### Harness-IntVaultResync`). Until a task exists on the host, the daily scheduler path is **spec only**, not running.

- Prereqs: `OBSIDIAN_VAULT_ROOT`, `VAULT_SYNC_SAFE_BASE` when vault is not under the script default safe base.
- Verify: `schtasks /run /tn "Harness-IntVaultResync"` then read `.cursor/state/int_vault_resync.log` in the repo.

## Git hooks (markdown churn)

From **MiscRepos** repo root:

```sh
git config core.hooksPath .githooks
```

See **MiscRepos** `.githooks/README.md`. On macOS/Linux: `chmod +x .githooks/post-commit .githooks/pre-push`.

Disable automation: `INT_VAULT_RESYNC_DISABLE=1`.

## This host (one-time setup log)

- **2026-04-16:** `git config core.hooksPath .githooks` applied in MiscRepos clone `C:\Users\Dell\Documents\GitHub\MiscRepos`.
- **2026-04-16:** Task Scheduler task **`Harness-IntVaultResync`** registered (daily **10:15**). **Harness-VaultSync** was *not* registered here to avoid duplicate mirror runs with the daily guarded job; add weekly **Harness-VaultSync** separately if you want that cadence instead (see `SCHEDULED_TASKS.md`).
- **2026-04-16:** `schtasks /run /tn "Harness-IntVaultResync"` smoke run → **Last Result: 0** (task action completed).

## Fingerprint / uncommitted markdown

The scheduler fingerprint uses **git `HEAD` + `handoff_latest.md` metadata** — **uncommitted markdown is not covered** by that skip logic (by design). Use **commit + hook**, **`int-vault-resync.ps1 -Force`**, or **`sync_harness_to_vault.ps1`** directly when you need the vault updated before commit.
