---
title: "LLM Wiki vault policy"
tags: ["type/moc", "status/verified", "domain/llm-wiki"]
---

# LLM Wiki — vault SSOT

This vault implements a **Karpathy-style LLM Wiki**: a compounding, interlinked markdown layer **separate from** [[Vault-meta/00_HARNESS_VAULT_SCHEMA|Harness]] operational mirrors.

**Vault contract:** LLM-Wiki is on the **harness & AI** side of the vault (compounding technical memory)—**not** in-universe TTRPG canon. See [[00_VAULT_RULES]] (*Vault contract: two domains*). Tags use **`domain/llm-wiki`** here; do not file wiki synthesis as `domain/ttrpg` unless it is explicitly in-character reference material (prefer keeping those in `Campaigns/` / `Sources/` instead).

**Operator pipeline (Capture→Publish):** [[00_HARNESS_WIKI_PIPELINE]] — same shape as the narrative workbench, gated on MiscRepos SSOT instead of PDF lore.

**MiscRepos reference (repo clone):** `MiscRepos/local-proto/docs/LLM_WIKI_VAULT.md` (operator guide); archived gist: `MiscRepos/local-proto/docs/references/karpathy-llm-wiki-snapshot.md`.

## Three layers (this vault)

| Layer | Location | Who writes |
|--------|-----------|------------|
| **Raw / immutable sources** | `LLM-Wiki/Sources/` | Humans add clips and files. Agents **read only** — do not overwrite. |
| **Derived wiki** | `LLM-Wiki/Entities/`, `Topics/`, `Synthesis/`, [[LLM-Wiki/_index]] | Agents (and you) maintain synthesis pages; cross-link aggressively. |
| **Chronicle** | [[LLM-Wiki/log]] | Append-only ingest / lint / query log (optional but recommended). |

**Harness (`Harness/`):** Synced from MiscRepos via `sync_harness_to_vault.ps1`. **Do not** fold harness state into LLM-Wiki pages or edit harness files during wiki-compile sessions unless you intentionally reconcile.

**Pointers (`Pointers/`):** Lightweight stubs before material lands in `LLM-Wiki/Sources/` or the derived tree.

## Tag convention (`tags` in YAML)

Aligned with `Scan-ObsidianTagGaps.ps1`: every note needs `type/*`, `status/*`, and `domain/llm-wiki` (or other `domain/*` where appropriate).

| Path pattern | `type` | `status` (typical) |
|--------------|--------|---------------------|
| `LLM-Wiki/Sources/*.md` | `type/llm-wiki-source` | `status/archived` |
| `LLM-Wiki/Entities/*.md` | `type/llm-wiki-entity` | `status/draft` or `status/compiled` |
| `LLM-Wiki/Topics/*.md` | `type/llm-wiki-topic` | `status/draft` |
| `LLM-Wiki/Synthesis/*.md` | `type/llm-wiki-synthesis` | `status/draft` |
| `LLM-Wiki/_index.md` | `type/moc` | `status/verified` |

**Optional frontmatter (convention):** `last_compiled: YYYY-MM-DD`, `sources:` (list of wikilinks or paths).

## Workflows

1. **Ingest:** Add raw markdown to `LLM-Wiki/Sources/` (or repo + pointer). Run an agent session to read sources and update Entities/Topics/Synthesis and [[LLM-Wiki/_index]]; append [[LLM-Wiki/log]].
2. **Query:** Ask questions; file good answers back into the wiki (Karpathy: answers compound).
3. **Lint:** Periodically scan for orphans, stale claims, contradictions; update pages in one pass.

## Automation (MiscRepos scripts)

Full session templates (ingest / compile / lint), lint bundle flags, and **search-layer brainstorm** live in the MiscRepos clone:

- `local-proto/docs/LLM_WIKI_VAULT.md`
- `local-proto/docs/LLM_WIKI_SEARCH.md`

Mechanical lint only (no ingest/compile logic in scripts):

- `local-proto/scripts/Lint-LlmWikiVault.ps1` — runs tag-gap + orphan scans; optional `-FailOnTagGaps`, `-FailOnStrictOrphans`.

## See also

- [[00_HARNESS_WIKI_PIPELINE]] — harness + LLM-Wiki Capture→Publish stages and gates
- [[LLM-Wiki/_index]] — catalog hub
- [[START_HERE]] — vault root hub
