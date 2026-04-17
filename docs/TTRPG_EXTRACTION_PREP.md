# TTRPG stack extraction prep (Phase 3)

**Goal:** Move or archive **TTRPG-first** code and docs so Arc_Forge can present primarily as **harness mirror (`ObsidianVault/Harness/`) + LLM-Wiki**. This document is an **inventory + decision + cutover checklist**—execute only after Phase 1 pipeline docs are stable and operators agree.

**Primary identity (target):** See `ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md` (Capture→Publish) and repository root `README.md`.

---

## 1. Inventory (bounded packages)

| Package | Path | Role | Notes for extraction |
|---------|------|------|----------------------|
| **workflow_ui** | `ObsidianVault/workflow_ui/` | Flask S1–S5 UI, tests, Playwright | Tight coupling to `ObsidianVault/` paths; needs path audit after move |
| **campaign_kb** | `campaign_kb/` at repo root | FastAPI + SQLite | Own `requirements.txt`, tests under `campaign_kb/tests/` |
| **Vault RAG / ingest scripts** | `ObsidianVault/scripts/` | PDF ingest, pipeline stages, pytest | Large surface; many tests reference `Campaigns/` layout |
| **TTRPG vault trees** | `ObsidianVault/Campaigns/`, `Sources/`, `Rules/`, … | PKM + arcs | May stay in vault **or** move with new Obsidian vault in target repo |
| **CI** | `.github/workflows/campaign_kb_tests.yml`, `workflow_ui_tests.yml`, `scripts_tests.yml` | Per-package tests | Split or point `working-directory` at submodule path |
| **Unified launcher** | `scripts/start_stack.ps1`, `start_stack.sh` | Starts KB + workflow_ui | Replace or delete when stack moves |
| **Root unified tests** | `scripts/run_tests.ps1`, `run_tests.sh` | Invokes all three | Trim to harness-only jobs or delete |

**Doc-only (usually stay or symlink):** `ObsidianVault/Campaigns/docs/narrative_workbench_spec.md` — remains **analogy** reference for the harness wiki pipeline vault page; optional copy to MiscRepos if you want one less TTRPG path.

---

## 2. Target repo shape (decision)

| Option | Pros | Cons |
|--------|------|------|
| **A. New repo** `Arc_Forge_TTRPG` (or similar) | Clean git history; Arc_Forge default branch is harness-first | Two remotes; cross-links; CI secrets duplicated |
| **B. Submodule** under Arc_Forge (`ttrpg/` subtree) | Single clone for operators who want both | Submodule friction; path churn |
| **C. Archive-only** | Export tarball + delete from main | Loses living git history unless archive repo exists |

**Recommendation:** **A** for long-term clarity if TTRPG remains actively developed; **B** if you need one workspace for players and harness rarely.

Record the **chosen option** here when decided: ___________________

---

## 3. CI cutover checklist

MiscRepos operator index (sibling clone layout): `../MiscRepos/local-proto/docs/REPO_BOUNDARY_INDEX.md` — maintenance rhythm includes a **TTRPG stack extraction** bullet that links back to this page.

- [ ] Create target repo (or submodule mount) and push initial tree from filtered `git filter-repo` or copy + fresh history (team choice).
- [ ] Update **Arc_Forge** root `README.md`: remove or shorten Quickstart for moved stack; link to new repo.
- [ ] Update **MiscRepos** `local-proto/docs/REPO_BOUNDARY_INDEX.md` Arc_Forge row if canonical paths change.
- [ ] Update **MiscRepos** `local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md` vault layout §2 and gap table if folder counts shift.
- [ ] **sync_harness_to_vault.ps1** — confirm `$docMappings` and vault paths unchanged; no dependency on `workflow_ui` for sync.
- [ ] Disable or relocate GitHub Actions that reference removed paths; add note in target repo README for new CI entrypoints.
- [ ] Leave **stub notes** in Arc_Forge vault (e.g. `Pointers/TTRPG_stack_moved.md`) with link to new repo for Obsidian graph hygiene.
- [ ] Run `Lint-LlmWikiVault.ps1` and optional `Lint-ObsidianVaultContract.ps1` after cutover.

---

## 4. Risks

- **Broken relative imports** in Python (`workflow_ui` importing vault paths).
- **Secrets / `.env`** patterns duplicated; document in target repo only.
- **Obsidian wikilinks** spanning repos do not resolve—prefer HTTP or `file://` stubs.

---

*Last updated with harness + wiki pipeline plan (Phase 3 prep).*
