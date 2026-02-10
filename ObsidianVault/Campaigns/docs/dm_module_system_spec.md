# TTRPG DM Module System (Hybrid Obsidian + Web UI)

## Intent
Design a system to co-create TTRPG adventure modules with a flexible, creative workflow (not a rigid phase gate), while keeping Obsidian as the source of truth and a web UI as the IDE-like experience.

## Map existing workflow_ui panels to DM tasks
Reference: `ObsidianVault/workflow_ui/templates/index.html`, `ObsidianVault/workflow_ui/static/app.js`

- **Arc file-tree** → Module file browser (scenes, NPCs, locations, factions, rules)
- **Encounters list (provenance)** → Scene/NPC list with citations to canon sources
- **Campaign KB tab (search/ingest/merge)** → RAG lookup, ingest new canon, merge seed docs
- **S1 Task Decomp** → Outline and beat breakdown for module chapters
- **S2 Drafts** → Scene/NPC draft generation with citations
- **S3 Feedback** → Human editorial pass and notes
- **S4 Refine** → Targeted rewrite of a scene/NPC based on feedback
- **S5 Export** → Export module pack (MD/PDF/JSON) + KB updates
- **Session memory** → Ongoing campaign continuity (recaps, foreshadow hooks)

## DM module workspace model (Obsidian-first)
**Proposed folder layout**
```
Campaigns/<Campaign>/Modules/<ModuleName>/
  README.md
  Outline.md
  Scenes/
  NPCs/
  Locations/
  Factions/
  Items/
  Rules/
  Handouts/
  SessionLogs/
  Exports/
```

**Frontmatter metadata for timeline/idea web**
```
---
type: scene|npc|location|faction|item|rule|session
module: <ModuleName>
campaign: <CampaignName>
tags: [hook, clue, combat, social]
depends_on: [<NoteA>, <NoteB>]
date: 012.M42-003  # or in-world date
location: <Planet/Region>
status: draft|final
---
```

## Flexible workflow graph (replaces rigid 6-phase model)
Default graph (editable by the DM):
```
Brainstorm -> Outline -> SceneDraft -> NPCs -> Review -> Export
       \-> RAGSearch -> CanonCheck -> Rewrite
```

**Node behaviors**
- **Brainstorm**: prompt-based ideation; saves to `Outline.md`
- **RAGSearch**: query campaign_kb; stores citations in note metadata
- **CanonCheck**: compares draft content against sources; flags conflicts
- **SceneDraft**: generates scenes with citations and structure
- **NPCs**: generates NPC cards (stat hooks + personality + ties)
- **Review**: DM edits and feedback tagging
- **Export**: structured module export (MD/PDF/JSON + handouts)

## IDE-like UI features (web UI)
- **Project file tree** with tabs (multi-note editing)
- **Chat per note or folder** (context = selected notes)
- **Inline citations** with source preview
- **Timeline view** (from frontmatter dates)
- **Idea web** (from links/tags/depends_on)
- **Workflow graph** (editable nodes; save templates)
- **Quick actions**: "Create scene", "Create NPC", "Generate hooks"

## Integration touchpoints
- **workflow_ui backend** → Obsidian vault (file read/write)
- **campaign_kb API** → RAG search/ingest/merge
- **Obsidian cursor integration** → index/search, session continuity, context loader
- **Daggr** → workflow visualization and step-by-step run introspection

## MVP scope
1. Module folder + metadata schema
2. Web UI: file tree + note viewer + chat panel
3. RAG search panel with citations
4. One workflow template (Brainstorm → Outline → SceneDraft → Export)
5. Export pipeline (MD + JSON)

## Other storage options (and why Obsidian wins here)
- **Plain filesystem**: simple and fast, but no metadata or graph context
- **SQLite-only**: structured data and queries, but poor authoring UX
- **Notion**: good collaboration but weaker local control and tooling
- **Custom DB + web UI only**: powerful but high build cost and risk

Obsidian provides local-first authoring, wiki-link graph, frontmatter metadata, and fits your creative workflow while still supporting automation and RAG integration.
