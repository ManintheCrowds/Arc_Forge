<!--
# PURPOSE: Define vault structure, tags, and YAML schema.
# DEPENDENCIES: Obsidian core features, Templates plugin (optional).
# MODIFICATION NOTES: Vault contract — TTRPG/universe vs harness+AI (W&G is 40k TTRPG, not a separate “game line” from 40k lore).
-->

---
title: "Obsidian DM Vault Rules"
tags: ["type/moc", "status/verified", "domain/ttrpg"]
---

# Obsidian DM Vault Rules

## Vault contract: two domains

**Lore intent:** **Wrath & Glory** is the Warhammer **40,000** tabletop RPG—same universe and continuity. Do **not** treat “40k” and “W&G” as two competing game lines in tags or folder policy. Optional tags like `system/wrath-and-glory` are for *mechanics* or edition notes, not for splitting the setting from “40k.”

| Domain | What it covers | Primary folders / roots | Tag anchor |
|--------|----------------|-------------------------|------------|
| **TTRPG / 40k universe** | Campaigns, lore, entities, rules, sessions, PDF-derived sources, RAG staging under `Campaigns/_rag_outputs/` until promoted | `Campaigns/`, `Sources/`, `Rules/`, `NPCs/`, `Factions/`, `Locations/`, `Items/`, `Sessions/`, `Timeline/`, `Concepts/`, `Vehicle-Recovery/`, `Inbox/` | `domain/ttrpg` plus existing `type/*`, `campaign/*`, etc. ([[00_HARNESS_VAULT_SCHEMA]] for the three-dimension rule) |
| **Harness & AI** | Mirrored MiscRepos harness state, operator research, ingest pointers, compounding **LLM-Wiki** (technical memory—not in-universe canon) | `Harness/`, `LLM-Wiki/`, `Pointers/`, vault `research/`, vault `docs/` as used for work | `domain/harness` (and harness `type/*` from [[00_HARNESS_VAULT_SCHEMA]]); LLM-Wiki detail in [[00_LLM_WIKI_VAULT]] |

**Rule of thumb:** If a reader should file it under “what happens in the Imperium / our table,” it belongs in **TTRPG**. If it belongs under “how we run agents, MCP, sync, and tooling,” it belongs in **Harness & AI**—even when the *topic* is 40k IP (e.g. Bitcoin-Chaos mapping is still harness research, not campaign canon).

## Folder Map

- **`START_HERE.md`** (vault root) — hub links to policy notes and major folders
- **`Vault-meta/`** — this file, [[00_HARNESS_VAULT_SCHEMA]], [[GitHub-Repos-Index]], [[SCRIPTS_DOCS_INDEX]] (rules, harness schema, repo index, scripts-doc MOC)
- **`Pointers/`** — short ingest and stub notes (news digests, integration pointers, Bitcoin chaos stub)
- **`Concepts/`** — brainstorms and reusable ideas that are not yet entity notes
- **`Vehicle-Recovery/`** — campaign-adjacent vehicle recovery fiction
- `Harness/` — mirrored MiscRepos harness state and docs (not TTRPG)
- `Sources/` for source notes tied to PDFs or external docs
- `Campaigns/` for campaign overviews and arcs; **`Campaigns/_rag_outputs/`** — machine-generated frame/RAG staging (see [[Campaigns/_rag_outputs/MOC_RAG_Outputs]]); promote verified rules to `Rules/`
- `NPCs/`, `Factions/`, `Locations/`, `Items/` for entity notes
- `Rules/` for mechanics, summaries, and house rules
- `Sessions/` for session logs and prep
- `Timeline/` for ordered events
- `Inbox/` for raw capture (optional; `Pointers/` is preferred for labeled ingest)
- `_meta/` — generated tag-gap reports from `Scan-ObsidianTagGaps.ps1`

## Tag Taxonomy

- **`domain/ttrpg`** — all in-universe play and lore (40k setting through Wrath & Glory); use on campaign-facing notes unless a more specific domain from [[00_HARNESS_VAULT_SCHEMA]] applies.
- **`domain/harness`** — harness mirrors, operator research, LLM-Wiki pages that are tooling/memory (see **[[00_HARNESS_VAULT_SCHEMA]]**).
- `#type/source`, `#type/npc`, `#type/faction`, `#type/location`, `#type/item`, `#type/rule`, `#type/session`, `#type/concept`, `#type/campaign`, `#type/pipeline-output` (machine-generated campaign artifacts under `Campaigns/_rag_outputs/`; still use `campaign/<name>` plus `status/draft` until promoted)
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

## Harness, LLM-Wiki, research, and MOC notes (harness & AI)

Notes under `Harness/`, **`LLM-Wiki/`**, `research/`, and folders like `Pointers/` use the **same** `type/` + `status/` + domain pattern. Prefer **`domain/harness`** (or tags defined in **[[00_LLM_WIKI_VAULT]]** for wiki-only pages) so they stay graph- and search-separable from **`domain/ttrpg`** universe notes. See **[[00_HARNESS_VAULT_SCHEMA]]** for types like `type/harness-state`, exclusions for `workflow_ui/` mirrors, and YAML examples.

**Graph filters (saved-style recipes):** see **[[GRAPH_VIEWS]]** — TTRPG vs harness vs meta search strings and optional color groups.

Automated tag coverage: run `local-proto/scripts/Scan-ObsidianTagGaps.ps1` — reports land in `_meta/Tag-Gap-Report.*` (generated report path is excluded from the gap list). **Link hygiene:** `local-proto/scripts/Scan-ObsidianOrphans.ps1` writes `_meta/Orphan-Link-Report.*` (same path exclusions as the tag scan; complements **[[Graph_and_lint_dashboard]]**). Back-fill: `local-proto/scripts/Add-ObsidianVaultFrontmatter.ps1` (`-DryRun` first). **Ongoing:** after MiscRepos harness-related edits, run `sync_harness_to_vault.ps1`; for new non-Harness notes, `Add-ObsidianVaultFrontmatter.ps1 -DryRun` before applying — see **[[00_HARNESS_VAULT_SCHEMA]]** (section *Going forward (operator workflow)*).
