<!--
# PURPOSE: Central dashboard for DM workflows and vault health.
# DEPENDENCIES: Dataview plugin (optional) for queries.
# MODIFICATION NOTES: Initial DM dashboard with core views.
-->

# DM Dashboard

**Narrative workbench (sections as panels):** [[Workbench]]

## Active Sessions (Most Recent)

```dataview
TABLE file.mtime AS Updated
FROM "Sessions"
WHERE contains(tags, "type/session")
SORT file.mtime DESC
LIMIT 10
```

## Draft Sources (Needs Review)

```dataview
TABLE file.mtime AS Updated, source_link AS PDF
FROM "Sources"
WHERE contains(tags, "status/draft") AND contains(tags, "type/source")
SORT file.mtime DESC
```

## Recent Rules

```dataview
TABLE file.mtime AS Updated, rule_type AS Type
FROM "Rules"
WHERE contains(tags, "type/rule")
SORT file.mtime DESC
LIMIT 10
```

## New NPCs

```dataview
TABLE file.mtime AS Updated
FROM "NPCs"
WHERE contains(tags, "type/npc")
SORT file.mtime DESC
LIMIT 10
```

## Unresolved Hooks (Tag: #hook/open)

```dataview
LIST
FROM ""
WHERE contains(tags, "hook/open")
SORT file.mtime DESC
```
