---
title: "Harness state and daily log (mirror map)"
tags: ["type/moc", "status/verified", "domain/harness"]
---

# Harness state and daily log (mirror map)

Obsidian **`Harness/`** is a **read-mostly mirror** of agent state from the MiscRepos harness (see `local-proto/scripts/sync_harness_to_vault.ps1`). Files here are **not** the canonical edit surface unless you are intentionally round-tripping; the vault exists so you can **browse, search, and graph** the same text the agent uses.

## Hub diet (rename blast radius)

This note is the **default “where is harness mirror surface X?”** map. **Fan-in** is dominated by **Harness/Daily**, **Harness/Handoff-archive**, **Harness/Handoff-Latest**, plus a small set of **Vault-meta** entry links (dozens of inbound `[[Harness/MOC_Harness_State]]` wikilinks total). That is expected for a super-hub; do **not** bulk-edit historical mirrors to “delink” them.

For **new** notes, when the topic is a **narrow recurring theme** (OpenGrimoire audits, vault graph/lint/metrics), link to a **theme hub** below instead of adding more prose-only pointers here. Keep **this MOC** for mirror-surface orientation and first-time navigation.

**Renames:** the vault has **`alwaysUpdateLinks`: true** in `.obsidian/app.json`, so Obsidian updates many wikilinks when a moved note keeps its relationship to the graph; still prefer **path-qualified** `[[Harness/...]]` / `[[Vault-meta/...]]` where stems collide (see **[[Vault-meta/00_VAULT_RULES]]**).

## Theme hubs

- [[Vault-meta/MOC_Harness_OpenGrimoire]] — OpenGrimoire GUI, audits, observability backlog pointers
- [[Vault-meta/MOC_Harness_Vault_Lint]] — graph views, orphan budget, tag/orphan scripts, §2 metrics

## What each surface is

| Vault path | Canonical source (harness repo) | Role |
|------------|----------------------------------|------|
| [[Harness/Handoff-Latest]] | `.cursor/state/handoff_latest.md` | Latest session handoff (replaced each time you write a new handoff); footer **Vault navigation** is re-built on each sync |
| [[Harness/Decision-Index]] | `.cursor/state/decision_index.md` | Table mapping `decision_id` to `handoff_latest` or `handoff_archive/` paths |
| `Harness/Handoff-archive/*.md` | `.cursor/state/handoff_archive/*.md` | Immutable archived copies of prior `handoff_latest` (UTC `YYYYMMDD-HHMMSS.md` names) |
| [[Harness/Pending-Tasks]] | `.cursor/state/pending_tasks.md` | Queue / next actions |
| [[Harness/Decision-Log]] | `.cursor/state/decision-log.md` | Decision history |
| [[Harness/Known-Issues]] | `.cursor/state/known-issues.md` | Open issues |
| `Harness/Daily/YYYY-MM-DD.md` | `.cursor/state/daily/YYYY-MM-DD.md` | **Dated** session notes (often mentions handoff #, what shipped) |
| [[Harness/Docs/Commands-README]] | `.cursor/docs/...` + `local-proto/docs/...` | How to run handoff/daily commands |

**Archived handoffs** are mirrored into **`Harness/Handoff-archive/`** on each `sync_harness_to_vault.ps1` run (same basenames as the repo). **Linear navigation** (Prev / Index / Next) is appended to each archive file by `Update-HandoffArchiveNavigation.ps1`. Canonical history remains in git; the vault is for **browsing and graphing** the chain.

## Why some dailies look undocumented

- Bodies are **short mirror logs**—not full essays. Empty days may say “No recorded activity.”
- **YAML** is injected on sync (`type/harness-state`, `status/mirror`) for Obsidian; the *meaning* of the note is in the title date and body.

## Linear Daily chain

Each file under `Harness/Daily/` gets a **Navigation** footer (Previous / Index / Next) when you run **`sync_harness_to_vault.ps1`** (it calls `Update-HarnessDailyNavigation.ps1` at the end). Open any daily and use the footer to walk the timeline.

```dataview
TABLE file.link AS Daily, file.mtime AS Updated
FROM "Harness/Daily"
SORT file.name ASC
```

## Relating Handoff-Latest to Daily

[[Harness/Handoff-Latest]] often includes `Updated:` or session text. Find the **same calendar day** in `Harness/Daily/` (filename `YYYY-MM-DD`) for the companion log; that is the usual “linear” attachment between **handoff narrative** and **daily stub**. After sync, the **Vault navigation** section at the bottom of Handoff-Latest links to that daily (when `Updated:` parses) and to [[Harness/Decision-Index]] / prior archive from `supersedes:` when resolvable.

## Handoff archive (Dataview)

```dataview
TABLE file.link AS Archive, file.mtime AS Updated
FROM "Harness/Handoff-archive"
SORT file.name ASC
```

## See also

- [[Vault-meta/00_HARNESS_VAULT_SCHEMA]] — tag dimensions for harness notes
- [[Vault-meta/GitHub-Repos-Index]] — repo entry points
- [[Vault-meta/START_HERE]] — vault-wide hub
