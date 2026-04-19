---
title: "Obsidian vault numeric audit snapshot (2026-04-17)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# Obsidian vault numeric audit snapshot (2026-04-17)

Read-only passes against `Arc_Forge/ObsidianVault` (exclusions: `workflow_ui/`, `scripts/`, `.pytest-tmp/`, `_meta/Tag-Gap-Report`). **Tracked work:** `.cursor/state/pending_tasks.md` § **PENDING_OBSIDIAN_BRAIN_VAULT** (`OBV-*`), § **PENDING_STACK_ATLAS** (`STK-*`).

## Pass 1 (vault-wide, wikilink parser)

- Total `.md`: **258**
- No outgoing `[[wikilinks]]`: **137**
- No incoming (resolved): **126**
- Strict orphans (no in, no out): **105**
- Ambiguous multi-stem link events: **3**
- Duplicate stems: **README** ×7 paths, **task_decomposition** ×2
- Top inlink hub: `Harness/MOC_Harness_State.md` (~**115**)

## Pass 2 (GRAPH_VIEWS §2 paths + YAML tags)

- §2 slice `.md`: **183** (71% of vault)
- `domain/harness` in YAML: **161** vault / **157** §2 (four harness-tagged notes outside §2 folders)
- Dominant `type/*`: `harness-state` **66**, `harness-session-snapshot` **60**, `type/source` **25** (mostly outside §2)
- §2 strict orphans: **95**; ambiguous link events from §2 files: **3**

## Notes

- Parser counts **wikilinks only**; Markdown links to vault paths are excluded.
- Re-run after large merges; see `OBV-0` in pending_tasks for “living” reference row.
