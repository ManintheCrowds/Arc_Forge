---
title: "Graph and lint dashboard"
tags: ["type/moc", "status/verified", "domain/ttrpg"]
---

# Graph and lint dashboard

Quick **Dataview** visibility: notes by `type/` tag, **no outgoing links**, **no incoming links**, and **strict orphans** (no links in either direction). Excludes paths that match the harness schema (`workflow_ui/`, `scripts/`, generated reports).

> If a table is empty, your vault may use different folder names — adjust the `WHERE` clauses. Run `local-proto/scripts/Scan-ObsidianOrphans.ps1` for a PowerShell report that matches the same exclusions.

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

High priority for a link from [[START_HERE]], a campaign index, or a domain MOC.

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
