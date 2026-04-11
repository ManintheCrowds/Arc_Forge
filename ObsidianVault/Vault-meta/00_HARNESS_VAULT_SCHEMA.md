<!--
# PURPOSE: YAML tags and note types for Harness, research, MOCs, and repo-adjacent content (non-TTRPG).
# DEPENDENCIES: Obsidian core; complements 00_VAULT_RULES.md (TTRPG/DM).
# MODIFICATION NOTES: Added for Obsidian system audit — extended taxonomy + tag-gap scanner contract.
-->

---
title: "Harness and cross-repo vault schema"
tags: ["type/moc", "status/verified", "domain/harness"]
---

# Harness and cross-repo vault schema

**Contract (read [[00_VAULT_RULES]] first):** The intentional split in this vault is **in-universe TTRPG (40k through Wrath & Glory)** vs **harness & AI work** (mirrored automation, research, **[[00_LLM_WIKI_VAULT]]**). W&G is *not* a separate “game line” from 40k for tagging—you separate **universe/play** from **tooling and agent memory**.

TTRPG/universe notes follow [[00_VAULT_RULES]]. This page covers **`Harness/`**, **`LLM-Wiki/`** (policy on that page), **`research/`**, **`Pointers/`** (ingest/stub notes), and **maps of content (MOCs)**.

## Tag dimensions (YAML `tags` array)

Every note in scope must include **three dimensions** (same array):

1. **Type** — one tag with prefix `type/`
2. **Status** — one tag with prefix `status/`
3. **Domain** — at least one of:
   - `domain/<name>` (preferred for work notes), e.g. `domain/harness`, `domain/llm-wiki`, `domain/openclaw`, `domain/bitcoin`, `domain/infra`
   - **TTRPG / 40k universe:** `domain/ttrpg` and/or `campaign/<name>`, `faction/<name>`, `region/<name>`, or `timeline/<...>` (counts as domain per [[00_VAULT_RULES]])

## Type tags (`type/`)

| Tag | Use |
|-----|-----|
| `type/harness-state` | Mirrored harness state: `Harness/Handoff-Latest.md`, `Decision-Index.md`, `Pending-Tasks.md`, `Decision-Log.md`, `Known-Issues.md`, `Harness/Daily/*`, `Harness/Handoff-archive/*` |
| `type/harness-doc` | Mirrored docs under `Harness/Docs/` |
| `type/harness-bitcoin-obs` | Files under `Harness/Bitcoin-Observations/` |
| `type/research` | `research/` and long-form investigation notes |
| `type/ingest-pointer` | Short vault-root ingest / news / SCP pointers |
| `type/moc` | Index / map-of-content notes (e.g. [[GitHub-Repos-Index]]), and vault policy pages such as [[00_VAULT_RULES]] and this file |
| `type/stub` | One-line pointer to canonical doc elsewhere |
| `type/source` … `type/campaign` | TTRPG — see [[00_VAULT_RULES]] |

## Status tags (`status/`)

| Tag | Use |
|-----|-----|
| `status/draft` | Default for new or unreviewed |
| `status/verified` | Human-reviewed |
| `status/mirror` | Content mirrored from git; **canonical** may live in repo |
| `status/stale` | Known out of date; fix or refresh |

## Domain tags (`domain/`)

Use **`domain/<short-name>`** for non-TTRPG work: `domain/harness`, `domain/openclaw`, `domain/bitcoin`, `domain/infra`, `domain/miscrepos`, `domain/research`, `domain/scp`, etc.

## Exclusions (tag-gap scanner and human review)

The following paths are **code-adjacent mirrors** or generated noise — **do not** bulk-retag; prefer **one MOC** linking to the canonical repo path:

- `workflow_ui/**` — app/docs mirror; canonical in Arc_Forge repo
- `scripts/**` (under vault) — scripts subtree
- `.pytest-tmp/**`, `**/.pytest_cache/**` — test artifacts

**Always exclude:** `.obsidian/`

## YAML examples

### Harness mirrored state file
```yaml
---
title: "Decision Log"
tags: ["type/harness-state", "status/mirror", "domain/harness"]
---
```

### Harness/Docs mirror
```yaml
---
title: "Scheduled Tasks"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---
```

### Research note
```yaml
---
title: "External repos landscape"
tags: ["type/research", "status/draft", "domain/research"]
---
```

### MOC
```yaml
---
title: "GitHub repos index"
tags: ["type/moc", "status/verified", "domain/miscrepos"]
---
```

## Source-of-truth quick reference

| Content | Canonical | Vault role |
|---------|-----------|--------------|
| Harness state + listed harness docs | MiscRepos paths in `sync_harness_to_vault.ps1` | `Harness/**` mirror (including `Handoff-archive/` + `Decision-Index.md`); **[[Harness/MOC_Harness_State]]** explains handoff vs daily logs and linear chains |
| CHAOS Bitcoin mapping | `MiscRepos/docs/CHAOS_BITCOIN_MAPPING.md` | **Repo canonical**; vault `Harness/Docs/Chaos-Bitcoin-Mapping.md` + optional root stub note are mirrors—edit repo first, then re-sync |
| Runbooks / ADRs near code | Repo | Link + optional summary |
| TTRPG / campaign (40k universe, W&G) | Vault (`Campaigns/`, entities, `Sources/`, etc.) | Primary narrative SSOT |
| **campaign_kb** (FastAPI + SQLite under `Arc_Forge/campaign_kb/`) | Service + index | **Not** narrative canon—ingest, search, merge; see **campaign_kb vs vault** in MiscRepos `OBSIDIAN_GITHUB_GAP_ANALYSIS.md` |
| Submodule docs (`plans`, etc.) | Submodule repo | MOC links only |

See also: `local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md` in MiscRepos.

## Going forward (operator workflow)

1. **MiscRepos changes that touch harness sources** (`.cursor/state/**`, mapped `local-proto/docs/**`, `.cursor/docs/**`, `docs/bitcoin_observations/**`, etc.): from the MiscRepos repo root, set `OBSIDIAN_VAULT_ROOT` to this vault and `VAULT_SYNC_SAFE_BASE` to the parent of the vault (see gap analysis doc), then run `local-proto/scripts/sync_harness_to_vault.ps1` (use `-DryRun` first if unsure). Each copy into `Harness/` is followed by a **post-copy YAML injection** in that script, so mirror notes keep `type/` + `status/` + domain tags without hand-editing the vault. The same script then runs **`Update-HarnessDailyNavigation.ps1`** (linear **Daily** chain), **`Update-HandoffArchiveNavigation.ps1`** (linear **Handoff-archive** chain), and **`Add-HandoffLatestVaultLinks.ps1`** (**Vault navigation** footer on `Handoff-Latest.md`: daily link, decision index, optional wikilinks from `decision_index.md` for `supersedes:` / archived `decision_id`).
2. **New or edited non-Harness vault notes** (Campaigns, Sources, vault `docs/`, `Pointers/`, etc.): run `local-proto/scripts/Add-ObsidianVaultFrontmatter.ps1 -DryRun` to see what would be added, then run without `-DryRun` to apply the path-based defaults—or add compliant YAML by hand per this page and [[00_VAULT_RULES]].
3. **Check coverage:** `local-proto/scripts/Scan-ObsidianTagGaps.ps1` writes `_meta/Tag-Gap-Report.*` (the report file itself is excluded from the gap list).

**Bulk backfill (one-off / catch-up):** `Add-ObsidianVaultFrontmatter.ps1` is idempotent for files still missing dimensions.
