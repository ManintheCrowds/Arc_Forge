# Arc Forge — Harness mirror + LLM-Wiki (TTRPG stack optional)

**Arc Forge** is primarily a **downstream mirror** of MiscRepos harness state under `ObsidianVault/Harness/` and a compounding **LLM-Wiki** tree under `ObsidianVault/LLM-Wiki/` for technical writing (Capture→Publish pipeline: `ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md`).

The repository still contains a **Wrath & Glory** (Warhammer 40,000 RPG) **campaign workbench**—`workflow_ui`, `campaign_kb`, vault campaigns, and RAG tooling—that is marked **extraction-target** (see [docs/TTRPG_EXTRACTION_PREP.md](docs/TTRPG_EXTRACTION_PREP.md)). Until extraction ships, those paths remain supported; **new operator energy** should go to harness sync + LLM-Wiki per the pipeline doc.

*Programmer first. Cyberpunk. Bitcoin. Glitch. Goth.*

## Repository layout (read first)

| Layer | Where | Source of truth |
|-------|--------|-----------------|
| **Harness / AI harness memory** | `ObsidianVault/Harness/` | **MiscRepos** — run `MiscRepos/local-proto/scripts/sync_harness_to_vault.ps1` from your MiscRepos checkout. Mirrored files are not the place to invent orchestrator policy, gates, or MCP wiring. |
| **LLM-Wiki** | `ObsidianVault/LLM-Wiki/` · policy `ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md` · pipeline `ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md` | Vault-local compounding layer; **MiscRepos** `local-proto/docs/LLM_WIKI_VAULT.md` for ingest/compile/lint sessions. |
| **TTRPG / 40k universe (extraction-target)** | `Campaigns/`, `Sources/`, `Rules/`, `workflow_ui`, `campaign_kb`, vault scripts | `ObsidianVault/Vault-meta/00_VAULT_RULES.md` — W&G *is* the 40k RPG; contract splits **universe/play** vs **harness & AI**. **campaign_kb** vs vault: [OBSIDIAN_GITHUB_GAP_ANALYSIS.md](../MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md) §5.1. |

**Sibling documentation** (typical layout: `...\GitHub\{Arc_Forge,MiscRepos,OpenHarness}\`):

- [MiscRepos repo boundary index](../MiscRepos/local-proto/docs/REPO_BOUNDARY_INDEX.md)
- [Obsidian / GitHub gap analysis](../MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md)
- [MiscRepos harness + wiki Phase 2 automation](../MiscRepos/local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md)

The repository folder is intended to be named **Arc_Forge**. Older configs may reference `D:\Arc_Forge`; set env and paths to match your machine.

## Harness + LLM-Wiki pipeline (quick links)

- **Vault SSOT:** [ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md](ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md)
- **Optional scripts (MiscRepos):** `Show-LlmWikiCompileChecklist.ps1`, `Lint-ObsidianVaultContract.ps1` — see [HARNESS_WIKI_PIPELINE_PHASE2.md](../MiscRepos/local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md)

## TTRPG stack (legacy / extraction-target)

| Concept | Description |
|---------|-------------|
| **RAG** | Retrieval-augmented generation over rules/lore and campaign content |
| **Narrative workbench** | Modular arcs, pipeline (S1–S5), task decomposition, feedback |
| **Human authority** | GM remains final arbiter; AI suggests, GM edits and approves |
| **Pipeline S1–S5** | Storyboard → encounter pipeline through workflow UI |

**Spec:** [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md) — **analogy** for the harness wiki pipeline (same discipline, different gates).

### What you run it for (TTRPG)

- Adventure arcs, pipeline UI, session Archivist/Foreshadow, optional `campaign_kb` search — see [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md).

## Components

| Component | Role | How to run |
|-----------|------|------------|
| **Harness mirror** | Synced markdown under `ObsidianVault/Harness/` | From MiscRepos: `local-proto/scripts/sync_harness_to_vault.ps1` |
| **LLM-Wiki** | Compounding wiki | [ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md](ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md) |
| **campaign_kb** (TTRPG) | FastAPI search / ingest | `cd campaign_kb` → see [Quickstart](#quickstart-ttrpg) |
| **ObsidianVault** (TTRPG) | Vault scripts, RAG, campaigns | Scripts from `ObsidianVault`; workflow via **workflow_ui** or CLI |
| **workflow_ui** (TTRPG) | Flask app (port 5050) | See [Quickstart](#quickstart-ttrpg) |
| **Grimoire** | Optional second vault | Open in Obsidian |

## Quickstart (TTRPG)

1. **Start campaign_kb** (optional):
   ```bash
   cd campaign_kb
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. **Start workflow_ui**:
   ```bash
   cd ObsidianVault
   pip install -r workflow_ui/requirements.txt
   python -m workflow_ui.app
   ```
   Then open **http://127.0.0.1:5050**

Or: `.\scripts\start_stack.ps1` / `./scripts/start_stack.sh`

Troubleshooting: [ObsidianVault/workflow_ui/docs/TROUBLESHOOTING.md](ObsidianVault/workflow_ui/docs/TROUBLESHOOTING.md), [ObsidianVault/scripts/TROUBLESHOOTING.md](ObsidianVault/scripts/TROUBLESHOOTING.md).

## Interfacing the user (TTRPG)

- **Primary:** **workflow_ui** for S1–S5, session memory, KB when `campaign_kb` is running.
- **Secondary:** **ObsidianVault** in Obsidian for campaign markdown.
- **API:** campaign_kb `/openapi.json`; workflow_ui [ObsidianVault/workflow_ui/README.md](ObsidianVault/workflow_ui/README.md).

## Architecture (TTRPG)

- [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md)
- [ObsidianVault/Campaigns/docs/gui_spec.md](ObsidianVault/Campaigns/docs/gui_spec.md)
- [ObsidianVault/Campaigns/docs/workflow_diagrams.md](ObsidianVault/Campaigns/docs/workflow_diagrams.md)

## UI roadmap status (workflow_ui)

- Waves A–C: see [ROADMAP_STATUS.md](ROADMAP_STATUS.md), [ObsidianVault/workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md](ObsidianVault/workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md).

## Testing

```bash
cd campaign_kb && pytest tests/ -v
cd ObsidianVault && pytest workflow_ui/tests/ -v
cd ObsidianVault && pytest scripts/tests/ -v
cd ObsidianVault/scripts && pytest tests/test_ai_security.py -v
```

Unified: `./scripts/run_tests.sh` or `.\scripts\run_tests.ps1`

See [scripts/run_tests.sh](scripts/run_tests.sh). Browser I/O: [ObsidianVault/workflow_ui/docs/manual_io_checklist.md](ObsidianVault/workflow_ui/docs/manual_io_checklist.md). RAG optional: [campaign_kb/campaign/05_rag_integration.md](campaign_kb/campaign/05_rag_integration.md).

### CI (GitHub Actions)

| Workflow | Scope |
|----------|--------|
| [`.github/workflows/campaign_kb_tests.yml`](.github/workflows/campaign_kb_tests.yml) | `campaign_kb/**` |
| [`.github/workflows/workflow_ui_tests.yml`](.github/workflows/workflow_ui_tests.yml) | `ObsidianVault/workflow_ui/**` |
| [`.github/workflows/scripts_tests.yml`](.github/workflows/scripts_tests.yml) | `ObsidianVault/scripts/**` |

## Credentials and AI security

**No keys in code.** `.env` gitignored. ObsidianVault `.cursor_context/` gitignored.

**AI security (MVP):** See `ObsidianVault/scripts/tests/test_ai_security.py`. [MiscRepos TOOL_SAFEGUARDS.md](../MiscRepos/local-proto/docs/TOOL_SAFEGUARDS.md) when present.

## Local-first alignment

[local-first principles](https://www.inkandswitch.com/local-first). [LoFi](https://lofi.so), [Local-First News](https://www.localfirstnews.com/).

## Agent harness and sibling repos

**Arc_Forge does not replace MiscRepos or OpenGrimoire merge bars.**

- [docs/WORKSPACE_MCP_REGISTRY.md](docs/WORKSPACE_MCP_REGISTRY.md)
- [docs/CURSOR_PLANS_TASK_STATE.md](docs/CURSOR_PLANS_TASK_STATE.md)
- [docs/USER_RULES_VS_POLICY_ENGINE.md](docs/USER_RULES_VS_POLICY_ENGINE.md)
- [OpenGrimoire NAMING_AND_URLS](../OpenGrimoire/docs/engineering/OPENGRIMOIRE_NAMING_AND_URLS.md)

```bash
cd ../OpenGrimoire && npm run verify
cd ../MiscRepos && python .cursor/scripts/checksum_integrity.py --verify --strict
```

## Next steps (repo evolution)

1. **Operate harness + LLM-Wiki** — [00_HARNESS_WIKI_PIPELINE.md](ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md); optional [HARNESS_WIKI_PIPELINE_PHASE2.md](../MiscRepos/local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md).
2. **campaign_kb vs vault** — [OBSIDIAN_GITHUB_GAP_ANALYSIS.md](../MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md) §5.1.
3. **TTRPG extraction** — [docs/TTRPG_EXTRACTION_PREP.md](docs/TTRPG_EXTRACTION_PREP.md) when you split the stack.

## License and credits

Per project conventions. **Wrath & Glory** is a trademark of its respective owners. Rulebook PDFs are not distributed; configure `ObsidianVault/scripts/ingest_config.json`. See `.gitignore`.
