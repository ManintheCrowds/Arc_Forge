# Arc Forge — Vault, campaign workbench, harness mirror

**Arc Forge** is an Obsidian-first **Wrath & Glory** and **Warhammer 40,000** campaign workbench: local vault, optional **campaign_kb** search, **workflow_ui** for the S1–S5 pipeline, and human-in-the-loop authority over AI suggestions (“AI proposes, human disposes”). The same repository also holds a **downstream mirror** of harness notes under `ObsidianVault/Harness/` and a compounding **LLM-Wiki** tree for technical writing—so not everything here is TTRPG prose.

*Programmer first. Cyberpunk. Bitcoin. Glitch. Goth.*

## Repository layout (read first)

Three layers share one git clone. **Canonical harness automation** (orchestrator, MCP, `.cursor` policy) lives in sibling **MiscRepos**; edit there, then mirror into the vault when needed.

| Layer | Where | Source of truth |
|-------|--------|-----------------|
| **Harness / AI harness memory** | `ObsidianVault/Harness/` | **MiscRepos** — e.g. run `MiscRepos/local-proto/scripts/sync_harness_to_vault.ps1` from your MiscRepos checkout. Mirrored files are not the place to invent orchestrator policy, gates, or MCP wiring. |
| **LLM-Wiki** | `ObsidianVault/LLM-Wiki/` · policy `ObsidianVault/Vault-meta/00_LLM_WIKI_VAULT.md` | Vault-local; keep compounding tech notes separate from campaign voice and from mirrored `Harness/`. |
| **TTRPG** | Rules, campaigns, RAG outputs, **workflow_ui**, scripts under `ObsidianVault/`; **campaign_kb** at repo root | `ObsidianVault/Vault-meta/00_VAULT_RULES.md` — folders and tags (including how to keep **Wrath & Glory** vs **40k** material distinct). |

**Sibling documentation** (typical layout: `...\GitHub\{Arc_Forge,MiscRepos,OpenHarness}\`):

- [MiscRepos repo boundary index](../MiscRepos/local-proto/docs/REPO_BOUNDARY_INDEX.md) — what lives in MiscRepos vs Arc_Forge vs OpenHarness
- [Obsidian / GitHub gap analysis](../MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md) — vault paths, `OBSIDIAN_VAULT_ROOT`, `VAULT_SYNC_SAFE_BASE`, duplication notes

The repository folder is intended to be named **Arc_Forge**. Older configs may reference `D:\Arc_Forge`; set env and paths to match your machine. If your folder is still `wrath_and_glory`, rename on disk and reopen the workspace.

## Key concepts

| Concept | Description |
|---------|-------------|
| **RAG** | Retrieval-augmented generation over rules/lore and campaign content (NPCs, locations, missions) |
| **Narrative workbench** | Modular components for adventure arcs, pipeline (S1–S5), task decomposition, and feedback |
| **Human authority** | GM remains final arbiter; AI suggests, GM edits and approves |
| **Pipeline S1–S5** | Storyboard → encounter pipeline: task decomposition, encounter drafts, human feedback, refinement, export |
| **Session Archivist/Foreshadow** | Temporal continuity via session summaries, Archivist, and Foreshadow threads |

## Narrative workbench (what you run it for)

- **Adventure arcs**: Storyboard → encounter pipeline (S1–S5): task decomposition, encounter drafts, human feedback, refinement, export.
- **Visual and textual representation**: Pipeline view (Mermaid), arc file-tree (encounters, opportunities, task_decomposition, feedback, expanded storyboard), module tree in the workflow UI.
- **Branching narrative**: Encounter/opportunity structure (sequence, after/before, optional threads) and arc tree.
- **AI-assisted universe rendering**: RAG over rules/lore and campaign content; role-based prompts (Story Architect, Encounter Designer, Archivist, Foreshadowing Engine); support during and async from sessions.
- **Memory + continuity**: RAG over rules/lore and campaign content; session summaries, Archivist, Foreshadow threads.
- **Not** “an AI that writes adventures” — modular components, provenance, and human gatekeeping. Spec: [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md).

## Components

| Component | Role | How to run |
|-----------|------|------------|
| **campaign_kb** | FastAPI service: ingest (PDFs, seeds, DoD, docs, repos), full-text search, merge seed doc. SQLite at `campaign_kb/data/kb.sqlite3`. No GUI; API only. | See [Quickstart](#quickstart). |
| **ObsidianVault** | Vault + scripts: PDF ingest, RAG pipeline, storyboard workflow (S1–S5), session Archivist/Foreshadow. | Scripts run from `ObsidianVault`; workflow is driven by **workflow_ui** or CLI. |
| **workflow_ui** | Flask app (default port 5050). Single dashboard: arcs, pipeline (S1–S5), task decomp/feedback forms, session memory, optional Campaign KB panel. | See [Quickstart](#quickstart). |
| **Grimoire** | Separate Obsidian vault (cursor-bridge, dataview, omnisearch, pdf-plus). Use as alternate/reference vault for note-taking and linking; “run workflow” is done via **workflow_ui** (browser) or CLI, not from Grimoire. | Open in Obsidian as a second vault if desired. |

## Quickstart

1. **Start campaign_kb** (optional; needed for KB search/ingest/merge in the dashboard):
   ```bash
   cd campaign_kb
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. **Start workflow_ui** (main GM interface):
   ```bash
   cd ObsidianVault
   pip install -r workflow_ui/requirements.txt
   python -m workflow_ui.app
   ```
   Then open **http://127.0.0.1:5050**

Or use the **unified launcher** (starts both and opens the browser):
- Windows: `.\scripts\start_stack.ps1`
- Linux/macOS: `./scripts/start_stack.sh`

Having issues? See [ObsidianVault/workflow_ui/docs/TROUBLESHOOTING.md](ObsidianVault/workflow_ui/docs/TROUBLESHOOTING.md) (workflow UI) and [ObsidianVault/scripts/TROUBLESHOOTING.md](ObsidianVault/scripts/TROUBLESHOOTING.md) (PDF ingestion).

## Interfacing the user

- **Primary**: Use **workflow_ui** (browser at http://127.0.0.1:5050) for storyboard→encounter workflow (S1–S5), session memory (Archivist/Foreshadow), and — when campaign_kb is running — KB search, ingest, and merge.
- **Secondary**: Use **ObsidianVault** (and optionally **Grimoire**) in Obsidian for editing campaign markdown, session notes, and viewing outputs. Run workflow from the dashboard or CLI, not from Obsidian.
- **API / power users**: campaign_kb exposes OpenAPI at `/openapi.json` when running. workflow_ui routes are documented in [ObsidianVault/workflow_ui/README.md](ObsidianVault/workflow_ui/README.md). Script ingest/search/merge and run stages via curl/Postman or your own scripts.

## Architecture

- **Canonical architecture**: [ObsidianVault/Campaigns/docs/narrative_workbench_spec.md](ObsidianVault/Campaigns/docs/narrative_workbench_spec.md) — system prompt spine, role-based prompt layers, RAG strategy.
- **GUI spec**: [ObsidianVault/Campaigns/docs/gui_spec.md](ObsidianVault/Campaigns/docs/gui_spec.md) — one screen per stage, task decomp and feedback forms, pipeline view, provenance.
- **Workflow diagrams**: [ObsidianVault/Campaigns/docs/workflow_diagrams.md](ObsidianVault/Campaigns/docs/workflow_diagrams.md) — pipeline flowchart, data flow, arc file layout.

## UI roadmap status

- **Wave A (P0–P1): complete** — debug mode env-driven, error payloads normalized, onboarding/prereq status panel, modal file viewer.
- **Wave B (P2–P3): complete** — client-side validation with field errors, progress indicators (S2/S4/session), tab grouping, autosave drafts.
- **Wave C (P4): complete** — modularization, live updates (polling toggle), wizard flow, OpenAPI docs, E2E baseline.
- **Verification:** Unified run (`.\scripts\run_tests.ps1` or `./scripts/run_tests.sh`): campaign_kb 12 passed, workflow_ui 45 passed (1 skipped), ObsidianVault scripts 273 passed (9 skipped). Last run: see [ROADMAP_STATUS.md](ROADMAP_STATUS.md).
- **Remaining work breakdown:** see [ObsidianVault/workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md](ObsidianVault/workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md).

## Testing

Run tests per component:

```bash
# campaign_kb
cd campaign_kb && pytest tests/ -v

# workflow_ui (from ObsidianVault)
cd ObsidianVault && pytest workflow_ui/tests/ -v

# ObsidianVault scripts
cd ObsidianVault && pytest scripts/tests/ -v

# AI security unit tests only (fast, no LLM)
cd ObsidianVault/scripts && pytest tests/test_ai_security.py -v
```

Unified runner (all three from repo root):

```bash
# From Arc_Forge root
./scripts/run_tests.sh
# or on Windows (PowerShell):
# .\scripts\run_tests.ps1
```

See [scripts/run_tests.sh](scripts/run_tests.sh) (or run_tests.ps1) for exact paths and env notes. For browser I/O validation, see [ObsidianVault/workflow_ui/docs/manual_io_checklist.md](ObsidianVault/workflow_ui/docs/manual_io_checklist.md). workflow_ui exposes OpenAPI at **http://127.0.0.1:5050/docs** when running. Real runs of S2/S4 need RAG/LLM and storyboard under `Campaigns/_rag_outputs/` (or path passed to Stage 1) and `ingest_config.json` for Stage 2/4.

**RAG semantic retrieval (optional):** For ChromaDB-based semantic search, install `pip install -r ObsidianVault/scripts/requirements-rag.txt` and set `use_chroma: true` in `ingest_config.json` → `rag_pipeline`. See [campaign_kb/campaign/05_rag_integration.md](campaign_kb/campaign/05_rag_integration.md) for setup and config.

### CI (GitHub Actions)

| Workflow | Scope | Command (same as README above) |
|----------|-------|-------------------------------|
| [`.github/workflows/campaign_kb_tests.yml`](.github/workflows/campaign_kb_tests.yml) | `campaign_kb/**` | `cd campaign_kb && python -m pytest tests/ -v --tb=short` |
| [`.github/workflows/workflow_ui_tests.yml`](.github/workflows/workflow_ui_tests.yml) | `ObsidianVault/workflow_ui/**` | `cd ObsidianVault && pytest workflow_ui/tests/ -v` |
| [`.github/workflows/scripts_tests.yml`](.github/workflows/scripts_tests.yml) | `ObsidianVault/scripts/**` | `cd ObsidianVault && pytest scripts/tests/ -v` |

## Credentials and AI security

**No keys in code.** Use OS keychain (keyring) for production, or `.env` for development (`.env` is gitignored; never commit keys).

- **ObsidianVault `.cursor_context/`:** `sessions.db` and `tool_usage.log` are local Cursor integration artifacts—gitignored. Do not commit personal session telemetry.
- **Development:** Set `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` in `.env` or environment
- **Production:** `pip install keyring` (in requirements-enhancements.txt) then store keys via keyring
- `ObsidianVault/scripts/credential_vault.py` tries keyring first, falls back to `os.environ`

**AI security (MVP):** Credential vault, HITL consent (`cloud_ai_consent.py`), append-only audit log (`audit_ai.py`), kill switch in workflow_ui chat, tool registry for RAG pipeline. Align any operator-wide methodology with your own `AI_SECURITY` notes if you maintain them; in-repo behavior is covered by `ObsidianVault/scripts/tests/test_ai_security.py`. For tool safeguards in the wider harness, see [MiscRepos local-proto/docs/TOOL_SAFEGUARDS.md](../MiscRepos/local-proto/docs/TOOL_SAFEGUARDS.md) when that clone is present.

## Local-first alignment

Arc Forge aligns with [local-first principles](https://www.inkandswitch.com/local-first): vault and campaign markdown live on disk (you own your data); workflow_ui and scripts run locally. RAG/campaign_kb is optional—ingest and search can run fully offline with local embeddings. Community: [LoFi](https://lofi.so), [Local-First News](https://www.localfirstnews.com/).

## Agent harness and sibling repos

**Arc_Forge does not replace MiscRepos or OpenGrimoire merge bars.** Use this section together with [Repository layout](#repository-layout-read-first) and the MiscRepos boundary index.

- [docs/WORKSPACE_MCP_REGISTRY.md](docs/WORKSPACE_MCP_REGISTRY.md) — MCP registry stub and link to [MiscRepos MCP capability map](../MiscRepos/.cursor/docs/MCP_CAPABILITY_MAP.md)
- [docs/CURSOR_PLANS_TASK_STATE.md](docs/CURSOR_PLANS_TASK_STATE.md) — `.cursor/plans` as task state vs chat transcript
- [docs/USER_RULES_VS_POLICY_ENGINE.md](docs/USER_RULES_VS_POLICY_ENGINE.md) — user rules vs automated policy / CI
- Canonical **GitHub repo naming** and merge vs sibling policy: [OpenGrimoire `docs/engineering/OPENGRIMOIRE_NAMING_AND_URLS.md`](../OpenGrimoire/docs/engineering/OPENGRIMOIRE_NAMING_AND_URLS.md)

**Verification when siblings exist** (`...\GitHub\{Arc_Forge,OpenGrimoire,MiscRepos}\`):

```bash
cd ../OpenGrimoire && npm run verify
cd ../MiscRepos && python .cursor/scripts/checksum_integrity.py --verify --strict
```

Use the first when plans or tasks change **OpenGrimoire** application code or API docs; use the second when changing **rules, skills, or `.cursor` policy** in MiscRepos. See [OpenGrimoire CONTRIBUTING.md](../OpenGrimoire/CONTRIBUTING.md) § Pre-push / local verification.

## Next steps (repo evolution)

Rough priority after this README refresh:

1. **Vault contract** — One authoritative `Vault-meta` page for folder + tag rules so **Wrath & Glory** vs **40k** vs **Harness** stay separated in search, graph, and RAG (extends `00_VAULT_RULES.md` / `00_HARNESS_VAULT_SCHEMA.md`).
2. **Single canonical campaign tree** — Resolve `ObsidianVault` campaign notes vs `campaign_kb` overlap (see [OBSIDIAN_GITHUB_GAP_ANALYSIS.md](../MiscRepos/local-proto/docs/OBSIDIAN_GITHUB_GAP_ANALYSIS.md) § gaps) before any hard repo/vault split.
3. **Optional path/tag linter** — Small script in MiscRepos (env-gated to `OBSIDIAN_VAULT_ROOT`) to validate frontmatter against the contract.
4. **Phase-2 split only if needed** — Second vault or second repo for pure TTRPG if noise remains after 1–3.

## License and credits

Per project conventions. **Wrath & Glory** is a trademark of its respective owners. Rulebook and supplement PDFs are used locally only and are not distributed with this repo; place your own PDFs in the paths configured in `ObsidianVault/scripts/ingest_config.json` (e.g. `ObsidianVault/pdf/`). See this repo's root `.gitignore` for excluded paths (PDFs and optional derived caches).
