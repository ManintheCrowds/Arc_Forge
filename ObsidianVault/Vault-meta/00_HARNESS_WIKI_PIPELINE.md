<!--
# PURPOSE: Domain-agnostic Capture→Publish pipeline for harness mirror + LLM-Wiki (horizontal from narrative workbench).
# DEPENDENCIES: 00_VAULT_RULES, 00_HARNESS_VAULT_SCHEMA, 00_LLM_WIKI_VAULT; MiscRepos sync_harness_to_vault.ps1.
# MODIFICATION NOTES: Stage gates reference SSOT in MiscRepos, not TTRPG PDFs.
-->

---
title: "Harness + LLM-Wiki pipeline (Capture to Publish)"
tags: ["type/moc", "status/verified", "domain/harness"]
---

# Harness + LLM-Wiki pipeline

Single operator page for turning **harness signal** into **compounding wiki artifacts** without inventing new SSOT under `ObsidianVault/`. Same *human authority / modular outputs / ingestion loop* shape as the narrative workbench ([[Campaigns/docs/narrative_workbench_spec]]), but **gates** are repo-boundary and vault-contract checks—not lore PDFs.

**Prerequisites:** [[00_VAULT_RULES]] (two domains) · [[00_HARNESS_VAULT_SCHEMA]] (tags, mirror rules) · [[00_LLM_WIKI_VAULT]] (LLM-Wiki layers) · MiscRepos clone: `local-proto/docs/LLM_WIKI_VAULT.md` (ingest / compile / lint sessions).

## Stages (domain-agnostic)

| Stage | Abstract job | This vault / MiscRepos |
|-------|--------------|-------------------------|
| **Capture** | Raw signal | MiscRepos `.cursor/state/handoff_latest.md` (diff), OpenHarness `async_tasks.yaml` excerpts (via MiscRepos), MCP map snippets, commit messages; operator clips into [[LLM-Wiki/Sources]] (immutable) or [[Pointers]] stubs |
| **Structure** | Entities, decisions, open questions | New/updated `LLM-Wiki/Entities/`, `LLM-Wiki/Topics/`; wikilinks to mirrored `Harness/**` files (read-only context) |
| **Draft** | Candidate render | `LLM-Wiki/Synthesis/*.md`; do **not** draft new orchestrator policy here—draft **summaries** that point to MiscRepos file paths |
| **Review** | Human gate vs SSOT | MiscRepos `local-proto/docs/REPO_BOUNDARY_INDEX.md`, `local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md`; mirror rules in [[00_HARNESS_VAULT_SCHEMA]] *Source-of-truth quick reference*; `status/draft` → `status/verified` on derived pages only |
| **Publish** | Canonical tier | (1) From MiscRepos: `local-proto/scripts/sync_harness_to_vault.ps1` when harness sources change. (2) Update [[LLM-Wiki/_index]] + append [[LLM-Wiki/log]]. (3) `local-proto/scripts/Lint-LlmWikiVault.ps1` with `OBSIDIAN_VAULT_ROOT` set. (4) Optional: `local-proto/scripts/Lint-ObsidianVaultContract.ps1` |

## Stage gates (replace TTRPG checks)

| Instead of (narrative bench) | Use (harness + wiki) |
|------------------------------|----------------------|
| “Grounded in retrieved PDF?” | “Cited path exists in MiscRepos or mirrored `Harness/` doc?” |
| “DM approval” | “No new gate strings / orchestrator policy unless merged in MiscRepos first” |
| “Promote to Rules/” | “Promote to `status/verified` + index row; Sources stay immutable” |

## Context assembly (RAG lateral)

For **harness** compile sessions, treat “retrieval” as **context assembly**: paste or link excerpts from latest handoff, `ENTITY_CRUD_MATRIX` (MiscRepos), `MCP_CAPABILITY_MAP` (MiscRepos), OpenHarness YAML—then synthesize in `Synthesis/`. Prefer **links + short quotes** in [[LLM-Wiki/Sources]] over duplicating full prose. Deeper rollout: see MiscRepos `local-proto/docs/LLM_WIKI_SEARCH.md` (grep vs index vs MCP)—**no** separate Chroma service required for the default pipeline.

## Forbidden (mirror discipline)

- Do not edit `Harness/**` to change canonical harness policy—edit MiscRepos (or OpenHarness where applicable), then re-sync.
- Do not move truth from `LLM-Wiki/Sources/` into `Synthesis/` by deleting or rewriting Sources during a compile; use a dedicated **compile** session per `LLM_WIKI_VAULT.md`.

## Pipeline UI

**Optional:** Obsidian + Dataview + [[GRAPH_VIEWS]] filters under §2 (Harness + AI + LLM-Wiki) are enough for many operators. Flask `workflow_ui` is **not** part of this pipeline; it remains **TTRPG stack** (extraction roadmap: Arc_Forge repo root [`docs/TTRPG_EXTRACTION_PREP.md`](../../docs/TTRPG_EXTRACTION_PREP.md)—open from git clone, not only Obsidian wikilinks).

## See also

- [[GRAPH_VIEWS]] — graph filters including harness + LLM-Wiki
- [[00_LLM_WIKI_VAULT]] — Sources / Entities / Topics / Synthesis / log
- MiscRepos `local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md` — optional automation (compile checklist + vault contract lint)
