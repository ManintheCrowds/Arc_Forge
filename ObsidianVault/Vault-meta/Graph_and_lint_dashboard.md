---
title: "Graph and lint dashboard"
tags: ["type/moc", "status/verified", "domain/ttrpg"]
---

# Graph and lint dashboard

Quick **Dataview** visibility: notes by `type/` tag, **no outgoing links**, **no incoming links**, and **strict orphans** (no links in either direction). Excludes paths that match the harness schema (`workflow_ui/`, `scripts/`, generated reports).

> If a table is empty, your vault may use different folder names — adjust the `WHERE` clauses. Run `local-proto/scripts/Scan-ObsidianOrphans.ps1` for a PowerShell report that matches the same exclusions.
>
> **§2 graph slice** (Harness + AI, for orphan budget): paste filter in **[[GRAPH_VIEWS]]** (*2. Harness + AI*). Numeric baseline for that slice: **[[Harness/Docs/Obsidian-Vault-Audit-Snapshot-2026-04-17]]** (mirrored from MiscRepos `adhoc/`; run `local-proto/scripts/sync_harness_to_vault.ps1` if the note is missing).
>
> **Ambiguous stems (`README`, `task_decomposition`):** multiple vault files share those display stems — use path-qualified wikilinks only; path inventory and agent rule in **[[00_VAULT_RULES]]** (subsection *Ambiguous stems: README and task_decomposition*).

## Orphan budget (§2)

**Strict orphan** here matches the **Strict orphans** Dataview block below: a `.md` note with **no** incoming and **no** outgoing `[[wikilinks]]` (Obsidian’s link model). Markdown `[]()` links alone do not count.

**Budget (no regression):** For files inside the **§2** path slice defined in **[[GRAPH_VIEWS]]** (*2. Harness + AI*), the **strict orphan count must stay ≤ 95** until a new full audit updates the baseline (OBV-0 baseline, 2026-04-17). When you intentionally ratchet, document the new cap and date in the same place you record audit counts.

**How to measure:** Run `local-proto/scripts/Get-ObsidianVaultGraphSlice2bMetrics.ps1` from MiscRepos with `OBSIDIAN_VAULT_ROOT` set — **`-Slice 2`** for **§2** strict-orphan count vs the budget above; default **`-Slice 2b`** matches **[[GRAPH_VIEWS]]** *2b* (omits `Harness/Handoff-archive/`). Wikilink resolution is **vault-wide** (same rules as `Scan-ObsidianOrphans.ps1`). For a dated baseline narrative and methodology notes, see MiscRepos `.cursor/state/adhoc/2026-04-17_obsidian_vault_audit_snapshot.md` (**[[Harness/Docs/Obsidian-Vault-Audit-Snapshot-2026-04-17]]**). The Dataview lists on this page are **not** identical to GRAPH_VIEWS path filters—use the script or audit for compliance checks.

## Image caption / embed merge pass

Use after a batch of notes that add or reorganize images/embeds (normalize captions, split figures, etc.).

1. **Normalize embeds** — Pick one embed style per note (`![[path/in/vault.png]]` vs `![](relative-or-url)`) and align with **[[00_VAULT_RULES]]** link conventions where they apply; avoid duplicate alt text + redundant caption lines.
2. **Restore graph edges** — If you split content across new files, add at least one `[[wikilink]]` so stubs are not strict orphans (see **Strict orphans** below).
3. **Mechanical verify** — From MiscRepos root with `OBSIDIAN_VAULT_ROOT` set, run `local-proto/scripts/Scan-ObsidianOrphans.ps1` (and `Scan-ObsidianTagGaps.ps1` if you always pair tag lint with graph passes).
4. **Completion record (required)** — Append one line: `YYYY-MM-DD | caption-merge pass | §2 strict orphans: <n> | batch: <short-id>` to your **Harness weekly note** *or* `LLM-Wiki/log.md`. That line is the completion signal for the pass.

## Notes by type tag (`type/*`)

```dataview
TABLE length(rows) AS count
FROM ""
WHERE !contains(file.path, "workflow_ui") AND !contains(file.path, "scripts/") AND !contains(file.path, "_meta/Tag-Gap-Report")
FLATTEN file.tags AS T
WHERE startswith(T, "type/")
GROUP BY T
SORT T ASC
```

## Files with no outgoing wikilinks

```dataview
TABLE length(file.inlinks) AS backlinks
FROM ""
WHERE length(file.outlinks) = 0
  AND !contains(file.path, "workflow_ui")
  AND !contains(file.path, "scripts/")
  AND !contains(file.path, "_meta/Tag-Gap-Report")
  AND file.name != "Graph_and_lint_dashboard"
SORT file.name ASC
```

## Files with no backlinks (nothing links here)

May include intentional leaf notes; still useful for MOC passes.

```dataview
TABLE length(file.outlinks) AS outlinks
FROM ""
WHERE length(file.inlinks) = 0
  AND !contains(file.path, "workflow_ui")
  AND !contains(file.path, "scripts/")
  AND !contains(file.path, "_meta/Tag-Gap-Report")
SORT file.name ASC
```

## Strict orphans (no outlinks and no inlinks)

High priority for a link from [[Vault-meta/START_HERE]], a campaign index, or a domain MOC.

```dataview
LIST
FROM ""
WHERE length(file.outlinks) = 0 AND length(file.inlinks) = 0
  AND !contains(file.path, "workflow_ui")
  AND !contains(file.path, "scripts/")
  AND !contains(file.path, "_meta/Tag-Gap-Report")
SORT file.name ASC
```

## Weak connectivity (≤1 outlink and ≤1 backlink)

Candidates to strengthen hub-and-spoke structure.

```dataview
TABLE length(file.outlinks) AS out_n, length(file.inlinks) AS in_n
FROM ""
WHERE length(file.outlinks) <= 1 AND length(file.inlinks) <= 1
  AND !contains(file.path, "workflow_ui")
  AND !contains(file.path, "scripts/")
  AND !contains(file.path, "_meta/Tag-Gap-Report")
SORT file.name ASC
```

## Tag lint (reminder)

YAML tag gaps: run `Scan-ObsidianTagGaps.ps1` from MiscRepos `local-proto/scripts/` — see [[00_HARNESS_VAULT_SCHEMA]].

## See also

- [[GRAPH_VIEWS]] — filter recipes for the graph UI
- [[00_VAULT_RULES]]
