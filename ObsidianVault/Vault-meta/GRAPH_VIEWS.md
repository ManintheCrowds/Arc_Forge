---
title: "Graph views (filters and color groups)"
tags: ["type/moc", "status/verified", "domain/ttrpg"]
---

# Graph views (Karpathy-style separation)

Obsidian’s **global graph** shows every note at once unless you **filter**. Use separate “mental workspaces” for **TTRPG / 40k universe (W&G is the 40k RPG)**, **harness + AI + LLM-Wiki**, and **meta** so clusters are readable. Paste the **Search** string into the graph panel’s filter box (same syntax as search).

## Filter recipes (paste into graph search)

### 1. TTRPG / 40k universe (campaigns, entities, rules — not “W&G vs 40k”)

**Include** (broad PKM, exclude automation trees):

```text
(path:Campaigns OR path:Sources OR path:Rules OR path:NPCs OR path:Factions OR path:Locations OR path:Items OR path:Concepts OR path:Vehicle-Recovery OR path:Sessions OR path:Timeline OR path:Inbox) -path:Harness -path:workflow_ui -path:scripts -path:_meta -path:.cursor_context
```

**Tip:** Toggle **Hide attachments** on. For a tighter graph, add `-path:docs` if vault `docs/` is workflow-heavy.

### 1b. Curated TTRPG (hide pipeline staging)

Same as §1 but **omits** `Campaigns/_rag_outputs/` (frame/RAG machine outputs). Use when you want **Sources, Rules, entities, and human-authored campaign notes** without the staging cluster. See [[Campaigns/_rag_outputs/MOC_RAG_Outputs]].

```text
(path:Campaigns OR path:Sources OR path:Rules OR path:NPCs OR path:Factions OR path:Locations OR path:Items OR path:Concepts OR path:Vehicle-Recovery OR path:Sessions OR path:Timeline OR path:Inbox) -path:_rag_outputs -path:Harness -path:workflow_ui -path:scripts -path:_meta -path:.cursor_context
```

### 2. Harness + AI (MiscRepos mirror, research, LLM-Wiki, pointers)

Includes **`LLM-Wiki/`** so compounding technical notes stay with harness-side work, not the in-universe graph.

```text
(path:Harness OR path:LLM-Wiki OR path:Vault-meta OR path:Pointers OR path:research OR path:docs OR path:.cursor_context) -path:workflow_ui -path:scripts
```

### 2b. Harness + AI without archived handoff blob

Same as §2 but **hides** `Harness/Handoff-archive/` (current handoff + dailies + decision index only). Use when the archive cluster is too dense on the graph.

```text
(path:Harness OR path:LLM-Wiki OR path:Vault-meta OR path:Pointers OR path:research OR path:docs OR path:.cursor_context) -path:Handoff-archive -path:workflow_ui -path:scripts
```

### 3. Meta only (policy + index hub)

```text
path:Vault-meta OR file:START_HERE
```

### 4. Exclude code-adjacent noise (default “clean wiki” overlay)

When exploring any view, you can always append:

```text
-path:workflow_ui -path:scripts -path:.pytest-tmp
```

### 5. Harness + wiki pipeline (policy + Sources)

**Vault-meta** policy pages plus **[[00_HARNESS_WIKI_PIPELINE]]** and raw **LLM-Wiki/Sources** (Capture stage) without the full `Harness/` tree.

```text
(path:Vault-meta OR path:LLM-Wiki/Sources) -path:workflow_ui -path:scripts
```

## Local graph

Open **Local graph** from [[START_HERE]] or a campaign note: the filter applies from the **current note’s neighborhood**. Start from `Campaigns/Campaign_Index` or `Sources/Source_Index` for dense subgraphs.

## Color groups (global graph)

In **Graph view → Groups**, add rules so clusters read at a glance. Suggested scheme (adjust colors to your theme):

| Group rule (Obsidian) | Role |
|----------------------|------|
| `path:Harness` | Mirrored harness / agent state |
| `path:LLM-Wiki` | Compounding wiki (harness & AI side, not in-universe canon) |
| `path:Vault-meta` | Schema and MOCs |
| `path:Sources OR path:Rules` | TTRPG reference layer |
| `path:Campaigns` | Campaign / arcs |
| `path:Pointers OR path:Concepts` | Short ingest / ideas |

If you prefer **tag-based** groups: `tag:#type/harness-state`, `tag:#type/source`, etc. (requires consistent YAML tags).

## Orphans toggle

- **Exploration:** leave **Show orphans** on to spot unlinked notes.
- **Presentation / screenshots:** turn **Show orphans** off after linking notes from a MOC (see [[Graph_and_lint_dashboard]]).

## See also

- [[00_HARNESS_WIKI_PIPELINE]] — Capture→Publish harness + LLM-Wiki pipeline
- [[00_VAULT_RULES]] — folder map
- [[00_HARNESS_VAULT_SCHEMA]] — tag schema and exclusions
- [[Graph_and_lint_dashboard]] — Dataview + lint-style lists
