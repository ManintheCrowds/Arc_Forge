---
title: "LLM Wiki log"
tags: ["type/llm-wiki-topic", "status/draft", "domain/llm-wiki"]
group: llm-wiki-log
color: amber
cssclasses:
  - vault-grp-llm-wiki-log
  - vault-col-amber

---

# LLM Wiki — log

Append-only chronicle: ingests, queries, lint passes. Use a consistent heading prefix per entry, e.g. `## [YYYY-MM-DD] ingest | Title`.

## [2026-04-10] setup | Vault scaffold

Initial `LLM-Wiki/` tree, [[Vault-meta/00_LLM_WIKI_VAULT]], and MiscRepos docs wired.

## [2026-04-20] harness | Pending backlog link target cleanup

In-vault markdown links that pointed at vault-root `(pending_tasks.md)` were rewritten to **`Harness/Pending-Tasks.md`** (including `#fragment` anchors). Stray **`ObsidianVault/pending_tasks.md`** removed after grep showed no remaining vault-local targets. **SSOT unchanged:** MiscRepos `.cursor/state/pending_tasks.md` (do not replace those paths in repo docs). **Tooling / docs (local-proto):** `scripts/Rewrite-VaultPendingTasksLinks.ps1` (`-DryRun` first), `scripts/sync_harness_to_vault.ps1` mirror rewrite pass, `docs/HARNESS_VAULT_WRITE_CONTRACT.md` operator bullet, `docs/LLM_WIKI_VAULT.md` scripts table row. **Obsidian:** reload vault; confirm backlinks hub on [[Harness/Pending-Tasks]] and spot-check a few deep anchors.
