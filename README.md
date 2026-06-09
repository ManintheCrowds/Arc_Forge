# Arc Forge â€” Harness mirror + LLM-Wiki

**Arc Forge** is a **downstream mirror** of MiscRepos harness state under `ObsidianVault/Harness/` and a compounding **LLM-Wiki** tree under `ObsidianVault/LLM-Wiki/` for technical writing (Captureâ†’Publish pipeline: `ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md`).

Sync harness state from MiscRepos with `local-proto/scripts/sync_harness_to_vault.ps1`. Compound wiki content per [00_LLM_WIKI_VAULT.md](ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md) and [LLM_WIKI_VAULT.md](../MiscRepos/local-proto/docs/LLM_WIKI_VAULT.md).

*Programmer first. Cyberpunk. Bitcoin. Glitch. Goth.*

## Repository layout (read first)

| Layer | Where | Source of truth |
|-------|--------|-----------------|
| **Harness / AI harness memory** | `ObsidianVault/Harness/` | **MiscRepos** â€” run `MiscRepos/local-proto/scripts/sync_harness_to_vault.ps1` from your MiscRepos checkout. Mirrored files are not the place to invent orchestrator policy, gates, or MCP wiring. |
| **LLM-Wiki** | `ObsidianVault/LLM-Wiki/` Â· policy `ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md` Â· pipeline `ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md` | Vault-local compounding layer; **MiscRepos** `local-proto/docs/LLM_WIKI_VAULT.md` for ingest/compile/lint sessions. |

**Sibling documentation** (typical layout: `...\GitHub\{Arc_Forge,MiscRepos,OpenHarness}\`):

- [MiscRepos repo boundary index](../MiscRepos/local-proto/docs/REPO_BOUNDARY_INDEX.md)
- [Obsidian / GitHub gap analysis](../MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md)
- [MiscRepos harness + wiki Phase 2 automation](../MiscRepos/local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md)

The repository folder is intended to be named **Arc_Forge**. Older configs may reference `D:\Arc_Forge`; set env and paths to match your machine.

## Harness + LLM-Wiki pipeline (quick links)

- **Vault SSOT:** [ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md](ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md)
- **Optional scripts (MiscRepos):** `Show-LlmWikiCompileChecklist.ps1`, `Lint-ObsidianVaultContract.ps1` â€” see [HARNESS_WIKI_PIPELINE_PHASE2.md](../MiscRepos/local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md)

## Components

| Component | Role | How to run |
|-----------|------|------------|
| **Harness mirror** | Synced markdown under `ObsidianVault/Harness/` | From MiscRepos: `local-proto/scripts/sync_harness_to_vault.ps1` |
| **LLM-Wiki** | Compounding wiki | [ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md](ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md) |

## Quickstart

1. **Sync harness mirror** (from MiscRepos checkout):
   ```powershell
   .\local-proto\scripts\sync_harness_to_vault.ps1
   ```
2. **Open vault in Obsidian** â€” `ObsidianVault/` (set `OBSIDIAN_VAULT_ROOT` to your path).
3. **LLM-Wiki sessions** â€” follow [00_HARNESS_WIKI_PIPELINE.md](ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md).

## Testing

```bash
cd ObsidianVault && pytest scripts/tests/ -v
cd ObsidianVault/scripts && pytest tests/test_ai_security.py -v
```

Unified (includes legacy paths): `./scripts/run_tests.sh` or `.\scripts\run_tests.ps1`

See [scripts/run_tests.sh](scripts/run_tests.sh).

### CI (GitHub Actions)

| Workflow | Scope |
|----------|--------|
| [`.github/workflows/workflow_ui_tests.yml`](.github/workflows/workflow_ui_tests.yml) | `ObsidianVault/workflow_ui/**` |
| [`.github/workflows/scripts_tests.yml`](.github/workflows/scripts_tests.yml) | `ObsidianVault/scripts/**` |
| [`.github/workflows/campaign_kb_tests.yml`](.github/workflows/campaign_kb_tests.yml) | `campaign_kb/**` (legacy) |

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

1. **Operate harness + LLM-Wiki** â€” [00_HARNESS_WIKI_PIPELINE.md](ObsidianVault/Vault-meta/00_HARNESS_WIKI_PIPELINE.md); optional [HARNESS_WIKI_PIPELINE_PHASE2.md](../MiscRepos/local-proto/docs/HARNESS_WIKI_PIPELINE_PHASE2.md).

## Deprecated legacy stack

Legacy campaign/workbench paths (`workflow_ui`, `campaign_kb`, vault campaigns) are **deprecated** and scheduled for extraction. Do not extend for new work. See [docs/TTRPG_EXTRACTION_PREP.md](docs/TTRPG_EXTRACTION_PREP.md).

Legacy-only references: [ObsidianVault/workflow_ui/README.md](ObsidianVault/workflow_ui/README.md), [campaign_kb/](campaign_kb/), [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md).

## License and credits

Per project conventions. Legacy game content is subject to extraction; see [docs/TTRPG_EXTRACTION_PREP.md](docs/TTRPG_EXTRACTION_PREP.md). See `.gitignore`.
