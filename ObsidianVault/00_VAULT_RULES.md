<!--
# PURPOSE: Define vault structure, tags, and YAML schema.
# DEPENDENCIES: Obsidian core features, Templates plugin (optional).
# MODIFICATION NOTES: Initial vault standards for Wrath & Glory DM knowledge base.
-->

# Obsidian DM Vault Rules

## Folder Map

- `Sources/` for source notes tied to PDFs or external docs
- `Campaigns/` for campaign overviews and arcs
- `NPCs/`, `Factions/`, `Locations/`, `Items/` for entity notes
- `Rules/` for mechanics, summaries, and house rules
- `Sessions/` for session logs and prep
- `Concepts/` for reusable ideas and lore
- `Timeline/` for ordered events
- `Inbox/` for raw capture

## Tag Taxonomy

- `#type/source`, `#type/npc`, `#type/faction`, `#type/location`, `#type/item`, `#type/rule`, `#type/session`, `#type/concept`, `#type/campaign`
- `#status/draft`, `#status/verified`
- `#campaign/<name>` (example: `#campaign/redacted_records`)
- `#faction/<name>` as needed
- `#region/<name>` as needed
- `#timeline/<era_or_year>` as needed

## YAML Schemas

### Source Note
```yaml
---
title: ""
source_file: ""
source_pages: ""
doc_type: ""
created: ""
tags: ["type/source", "status/draft"]
---
```

### Entity Note (NPC/Faction/Location/Item)
```yaml
---
title: ""
entity_type: ""
aliases: []
campaigns: []
created: ""
tags: ["type/npc", "status/draft"]
source_refs: []
---
```

### Rule Note
```yaml
---
title: ""
rule_type: ""
created: ""
tags: ["type/rule", "status/draft"]
source_refs: []
---
```

### Session Note
```yaml
---
title: ""
campaign: ""
session_date: ""
created: ""
tags: ["type/session", "status/draft"]
source_refs: []
---
```

## Linking Rules

- Source notes link outward to derived entities.
- Entities link back to Source notes using `source_refs`.
- Sessions link to NPCs, Locations, Items, and Rules referenced.

**Narrative workbench:** [[Campaigns/docs/narrative_workbench_spec]] — sections-as-panels use headers `[CAMPAIGN STATE]`, `[ACTIVE THREADS]`, `[SESSION INPUT]`, `[AI PROPOSALS]`, `[DM DECISIONS]`; see [[Campaigns/Workbench]].

## Ingestion Workflow (Hybrid)

1. Create a Source note per PDF with quotes and page refs.
2. Review Source note for accuracy.
3. Derive atomic notes (NPCs/Locations/Rules/etc.) with backlinks.
4. Mark as `status/verified` after review.
