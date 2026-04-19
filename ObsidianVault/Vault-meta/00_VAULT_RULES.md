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

- **`Vault-meta/START_HERE.md`** — harness + LLM-Wiki hub (links to policy notes and major folders); **`Vault-meta/MOC_Operator_Base_Camp.md`** — short operator entry map (research runbooks, handoff pointers). **Display name *Obsidian Brain*:** safe in Obsidian UI only; do **not** rename the on-disk `ObsidianVault` folder without MiscRepos `local-proto/docs/WORKSPACE_PATH_ENV_CHECKLIST.md` **(B)** checklist + **WS-PRIV-7** sign-off (`MiscRepos/.cursor/state/pending_tasks.md` § **PENDING_WORKSPACE_PRIVACY_AUDIT**).
- **Brain Map / context atlas:** MiscRepos [BRAIN_MAP_HUB.md](../../../MiscRepos/docs/BRAIN_MAP_HUB.md) — set **`BRAIN_MAP_VAULT_ROOTS`** to this vault’s filesystem root and **`BRAIN_MAP_VAULT_LABELS`** so OpenGrimoire **`/context-atlas`** includes vault markdown nodes alongside `.cursor/state` (see hub § *Environment variables* and `MiscRepos/.cursor/brain-map.env.example`).
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
- `#campaign/<name>` (templates may use a placeholder such as `campaign/_replace_with_campaign_slug` until you assign a real campaign slug)
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
tags: ["type/npc", "status/draft", "campaign/_replace_with_campaign_slug"]
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

**Graph filters (saved-style recipes):** see **[[GRAPH_VIEWS]]** — TTRPG vs harness vs meta search strings and optional color groups. **Harness + LLM-Wiki pipeline (Capture→Publish):** [[00_HARNESS_WIKI_PIPELINE]].

Automated tag coverage: run `local-proto/scripts/Scan-ObsidianTagGaps.ps1` — reports land in `_meta/Tag-Gap-Report.*` (generated report path is excluded from the gap list). **Link hygiene:** `local-proto/scripts/Scan-ObsidianOrphans.ps1` writes `_meta/Orphan-Link-Report.*` (same path exclusions as the tag scan; complements **[[Graph_and_lint_dashboard]]**). Back-fill: `local-proto/scripts/Add-ObsidianVaultFrontmatter.ps1` (`-DryRun` first). **Ongoing:** after MiscRepos harness-related edits, run `sync_harness_to_vault.ps1`; for new non-Harness notes, `Add-ObsidianVaultFrontmatter.ps1 -DryRun` before applying — see **[[00_HARNESS_VAULT_SCHEMA]]** (section *Going forward (operator workflow)*).

### Harness link syntax: wikilinks vs Markdown paths

Use the right link shape so **Obsidian Graph** and **wikilink-based** scripts (orphan metrics, hub counts — see **[[Graph_and_lint_dashboard]]**) match what you intend; agents grepping the repo still read both forms.

| Use | When | Notes |
|-----|------|--------|
| **`[[wikilinks]]`** | Target note lives **in this vault** (`Harness/`, `Vault-meta/`, `LLM-Wiki/`, `Pointers/`, etc.) and you want a **graph edge** | Prefer **path-qualified** wikilinks if the display title is ambiguous (e.g. multiple `README.md`): `[[Harness/MOC_Harness_State]]`, not bare `[[README]]`. |
| **`[label](path)`** | Target is **outside the vault** (GitHub URL, sibling repo file) or the **SSOT is MiscRepos** and the vault only mirrors tables/docs | Paths like `../../docs/...` from `.cursor/state/` are for the **repo** copy of harness tables. **`sync_harness_to_vault.ps1`** may rewrite **mirror-only** link targets (e.g. mirrored adhoc docs under Harness **Docs**); do not hand-fix those rows under Harness — edit SSOT under **MiscRepos** `.cursor/state/` and re-sync per [Harness / vault write contract](../../../MiscRepos/local-proto/docs/HARNESS_VAULT_WRITE_CONTRACT.md). |

**Example (side by side):**

- In-vault hub (counts in graph + wikilink tooling): `See [[00_HARNESS_VAULT_SCHEMA]] for YAML tags and harness types.`
- Repo contract outside the vault tree: `See [Harness / vault write contract](../../../MiscRepos/local-proto/docs/HARNESS_VAULT_WRITE_CONTRACT.md) for who may edit the Harness mirror vs Vault-meta notes.`

### Ambiguous stems: README and task_decomposition

Several notes share the same **filename stem** (`README` or `task_decomposition`). Obsidian may prompt for disambiguation; wikilink-only metrics (orphan/hub scans — **[[Graph_and_lint_dashboard]]**) treat ambiguous targets as risk. **Rule:** never use bare `[[README]]` or bare `[[task_decomposition]]` for these paths; always use the **path-qualified** wikilink from the table below (this list is the operator/agent allowlist for those stems).

| Path | Path-qualified wikilink example |
|------|----------------------------------|
| `Harness/Bitcoin-Observations/README.md` | `[[Harness/Bitcoin-Observations/README]]` |
| `MOC-from-MiscRepos/README.md` | `[[MOC-from-MiscRepos/README]]` |
| `LLM-Wiki/Entities/README.md` | `[[LLM-Wiki/Entities/README]]` |
| `LLM-Wiki/Synthesis/README.md` | `[[LLM-Wiki/Synthesis/README]]` |
| `LLM-Wiki/Topics/README.md` | `[[LLM-Wiki/Topics/README]]` |
| `LLM-Wiki/Sources/README.md` | `[[LLM-Wiki/Sources/README]]` |
| `Campaigns/_session_memory/README.md` | `[[Campaigns/_session_memory/README]]` |
| `Campaigns/first_arc/task_decomposition.md` | `[[Campaigns/first_arc/task_decomposition]]` |
| `Campaigns/schemas/task_decomposition.md` | `[[Campaigns/schemas/task_decomposition]]` |

**Additional `README.md` (tooling trees):** `workflow_ui/README.md` and `scripts/tests/README.md` also use the stem `README` but sit under paths often excluded from §2-style graph slices (`workflow_ui/`, `scripts/`). If you link them from harness or operator docs, use full path wikilinks (e.g. `[[scripts/tests/README]]`) — same “no bare `[[README]]`” rule.
