---
title: GitHub repos index
tags: ["type/moc", "status/verified", "domain/miscrepos"]
---

# GitHub repos index

Maps **active git workspaces** under this machine to their `docs/` entry points. **Canonical technical docs** usually live in the repo; the vault holds **[[00_HARNESS_VAULT_SCHEMA]]** mirrors under `Harness/` plus PKM notes.

**MiscRepos** (harness root for `sync_harness_to_vault.ps1`):

- Repo: `C:\Users\Dell\Documents\GitHub\MiscRepos`
- Harness state + mirrored docs: [[Harness/Handoff-Latest]] and siblings; **timeline / classification:** [[Harness/MOC_Harness_State]]; see `MiscRepos/local-proto/scripts/sync_harness_to_vault.ps1`
- **Runbooks and stack docs:** `MiscRepos/local-proto/docs/` — start with `OPENCLAW.md`, `REPO_BOUNDARY_INDEX.md`, `CAPABILITY_INDEX.md` if present
- **Brainstorms:** `MiscRepos/local-proto/docs/brainstorms/` (also check `MiscRepos/docs/brainstorms/` when present)
- **Cursor plans (repo-local):** `MiscRepos/local-proto/.cursor/plans/` — pointers only; promote to decision-log / vault when actionable
- **Gap analysis (repo):** `MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md`

**Arc_Forge** (contains this vault):

- Repo: `C:\Users\Dell\Documents\GitHub\Arc_Forge`
- This vault: `Arc_Forge/ObsidianVault` (Obsidian root); use [[START_HERE]] at the vault root for a folder map and links to [[00_VAULT_RULES]] / [[00_HARNESS_VAULT_SCHEMA]].

**Submodules / sibling repos** (clone paths typical on this machine):

| Area | Path (adjust if your clone differs) | Notes |
|------|----------------------------------------|--------|
| Plans / planning | `MiscRepos/plans` → often `Planswithinplans` | Submodule; planning docs live in that repo |
| OpenClaw simplex | `MiscRepos/openclaw-simplex` | Submodule |
| OpenHarness | `C:\Users\Dell\Documents\GitHub\OpenHarness` | Harness research / docs |
| OpenGrimoire | `C:\Users\Dell\Documents\GitHub\OpenGrimoire` | |
| OpenCompass | `C:\Users\Dell\Documents\GitHub\OpenCompass` | |
| SCP | `C:\Users\Dell\Documents\GitHub\SCP` | |
| Software | `C:\Users\Dell\Documents\GitHub\software` | |

**Tag hygiene:** After harness-related MiscRepos edits, run `sync_harness_to_vault.ps1` (YAML is injected after each copy). For other vault paths, `Add-ObsidianVaultFrontmatter.ps1 -DryRun` before applying. Check coverage with `Scan-ObsidianTagGaps.ps1` → `_meta/Tag-Gap-Report.*`. Details: [[00_HARNESS_VAULT_SCHEMA]] (*Going forward (operator workflow)*).

See also: [[00_VAULT_RULES]], [[00_HARNESS_VAULT_SCHEMA]].
