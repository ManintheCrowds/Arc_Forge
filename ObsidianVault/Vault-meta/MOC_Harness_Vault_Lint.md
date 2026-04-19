---
title: "Harness theme — vault graph and lint"
tags: ["type/moc", "status/verified", "domain/harness"]
---

# Harness theme — vault graph and lint

Parent hub: **[[Harness/MOC_Harness_State]]**. Use this note for **Obsidian graph slices**, orphan budgets, and mechanical vault scans instead of routing everything through the harness super-hub.

## Vault-meta dashboards

- [[Vault-meta/Graph_and_lint_dashboard]] — Dataview lists, orphan budget, image-caption merge checklist
- [[Vault-meta/GRAPH_VIEWS]] — §2 / §2b filter recipes

## Scripts (MiscRepos repo root)

Set `OBSIDIAN_VAULT_ROOT` to this vault, then from **MiscRepos** root:

- `local-proto/scripts/Scan-ObsidianTagGaps.ps1`
- `local-proto/scripts/Scan-ObsidianOrphans.ps1`
- `local-proto/scripts/Get-ObsidianVaultGraphSlice2bMetrics.ps1` — default §2b; **`-Slice 2`** for full GRAPH_VIEWS §2

## Schema

- [[Vault-meta/00_HARNESS_VAULT_SCHEMA]] — tag dimensions and scanner exclusions
