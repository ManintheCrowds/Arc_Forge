---
title: "PKM: attention pockets and Brain Map parity (no OpenClaw)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# PKM: attention pockets and Brain Map parity (no OpenClaw)

Human Obsidian/Foam patterns that mirror **Voelbel’s Brain Map** idea (topology of what you co-touch) and **Second Brain** ledger discipline **without** installing ClawHub skills in Cursor.

## Attention pockets (tags)

Use a small, stable tag namespace so MOCs stay filterable:

| Tag | Use |
|-----|-----|
| `pocket/bitcoin` | Bitcoin research, meetups, L402, org-intent |
| `pocket/agents` | OpenClaw, Cursor harness, MCP, publishing automation |
| `pocket/people` | Collaborators, authors, contacts |
| `pocket/publishing` | Ghost, site migrations, newsletters |

Add `#pocket/...` in frontmatter `tags:` or inline—match your vault convention (Foam often uses YAML; Obsidian accepts both).

## Dataview (Obsidian)

Example: table of notes in the Bitcoin pocket (requires Dataview plugin):

```dataview
TABLE file.mtime AS updated
FROM #pocket/bitcoin
SORT file.mtime DESC
LIMIT 25
```

Example: combine pocket with “active” status if you use a `status` field:

```dataview
LIST
FROM #pocket/agents
WHERE status = "active"
```

Adjust `FROM`/`WHERE` to your metadata schema.

## Local graph and Foam graph

- Prefer **local graph** from a hub MOC note with **depth 1–2**, not the global vault graph.
- **Harness mirror:** After vault sync, notes under `Harness/` get injected tags (`type/*`, `domain/harness`, etc.). Filter the graph with `domain/harness` or exclude `status/mirror` when you want human-only context. Details: [.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md](../.cursor/docs/OBSIDIAN_VAULT_INTEGRATION.md) § Graph and organization.
- **Juggl** (optional): use for typed links or alternate layouts; same pocket tags apply.

## Co-access graph (harness / OpenGrimoire)

Session **co-access** (which markdown paths appear together in handoffs and daily notes) is implemented in-repo, separate from Obsidian’s note graph:

- Hub: [BRAIN_MAP_HUB.md](BRAIN_MAP_HUB.md) — `build_brain_map.py` → `brain-map-graph.json` → OpenGrimoire `/context-atlas`.

That graph answers “what did we touch together in agent sessions?” not “what wikilinks exist in the vault?”

## Optional: snapshot JSON into the vault (read-only)

After building the graph locally:

1. Run the parser per [BRAIN_MAP_HUB.md](BRAIN_MAP_HUB.md) (from MiscRepos / harness root with `.cursor/state` populated).
2. Copy `OpenGrimoire/public/brain-map-graph.json` (or `BRAIN_MAP_OUTPUT` if set) into a vault folder such as `Reference/brain-map-graph.json`.
3. Treat as **read-only artifact** for humans or custom scripts—**not** SSOT (regenerate when state changes).

Do not point remote LLM gateways at this file or at full-vault exports.

## Second Brain–style ledger (single file)

- One markdown file (e.g. `Ledger/second-brain-inbox.md`) with dated `## YYYY-MM-DD` sections and optional YAML on each block.
- Append-only for agents; humans curate outward to permanent notes.
- **Policy:** do not send the full ledger or bulk vault text to a **remote** LLM gateway. If you use clustering tools (e.g. Second Brain Visualizer–style), use a **localhost** model endpoint and narrow scopes.

## Vault MOC templates

Copy-ready hub notes: [docs/vault-templates/](vault-templates/README.md).
