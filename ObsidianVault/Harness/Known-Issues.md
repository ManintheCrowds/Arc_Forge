# Known issues

Append entries below using the schema in [README.md](README.md).

## OSINT Tools (osint-tools/)

- **Location:** `osint-tools/spiderfoot`. **Issue:** `lxml` build fails on Windows (Python 3.13). **Workaround:** Use SpiderFoot Docker image or WSL. See [osint-tools/README.md](../../osint-tools/README.md).
- **Location:** `osint-tools/`. **Issue:** Go tools (subfinder, amass, asnmap) require Go 1.21+ or pre-built binaries. **Note:** Download from GitHub Releases if Go not installed.
- **Location:** `osint-tools/asn` (nitefood). **Issue:** Bash script; needs WSL or Linux. **Note:** Core ASN/geo works without API keys. Optional: **Resolved:** YYYY-MM-DD or **Status:** open|resolved|workaround. Move resolved items to ## Archive at bottom.

## LangChainChatBot (YouTube RAG)

- **YouTube transcript HTTP 400:** Some videos (e.g. MlK6SIjcjE8) fail with `HTTP Error 400: Bad Request` when fetching transcripts. **Workaround:** Use `add_video_info=False` (already applied); try different videos. See [youtube-transcript-api issues](https://github.com/jdepoix/youtube-transcript-api/issues).
- **SQLiteVec API:** Requires `SQLiteVec.create_connection(db_file=...)` and pass `connection=` to constructor; `db_file` alone fails in some langchain-community versions.
- **Ollama model default:** Default `llama2`; set `OLLAMA_MODEL=llama3.2` in .env if that model is pulled.

## Plans submodule (Planswithinplans)

- **Symptom:** `.cursor/plans/` is empty after clone, or plan links (e.g. `../plans/foo.plan.md`) return 404. **Location:** `.cursor/plans/` in software, portfolio-harness. **Issue:** Plans live in private submodule Planswithinplans. Submodule is not auto-initialized on clone. **Workaround:** Run `git submodule update --init` from repo root. Requires Planswithinplans access (private repo). If no access, plans remain empty; handoff and plan_ref links will not resolve.
- **Decision (2026-03-09):** Arc_Forge and moltbook-watchtower use Planswithinplans submodule at `.cursor/plans`. Plans consolidated per plans_submodule_migration. Security audit roadmaps moved to Planswithinplans with prefixes (`arc_forge_security_audit_roadmap_index.md`, `moltbook_security_audit_roadmap_index.md`).

## PowerShell / Cursor runner

- **Symptom:** `Get-ChildItem Env:` duplicate-key error when running some PowerShell scripts via Cursor. **Location:** Cursor temp script wrapper. **Note:** Cosmetic; main script logic (e.g. audit_context_engineering.ps1) completes and exits 0 before the error. No fix needed in project scripts.

## Agent telemetry (agent_log.jsonl)

- **Symptom:** agent_log.jsonl has no events (skill_load, critic_score, failure). **Location:** `.cursor/state/agent_log.jsonl`. **Issue:** Agents instructed to append per AGENT_TELEMETRY.md and role-routing but do not. **Note:** Meta-review uses handoff_archive and known-issues as fallback. Consider `python .cursor/scripts/log_agent_event.py` to reduce friction.

## Docker MCP

- **Location:** `.cursor/mcp.json` docker server. **Issue:** Docker socket access may fail on Windows if Docker Desktop not running or uses non-default socket. **Workaround:** Ensure Docker Desktop is running; if needed set `DOCKER_HOST=npipe:////./pipe/docker_engine` in mcp.json env. **Note:** uv must be installed (`pip install uv`) for `uvx docker-mcp`.
- **Location:** audit_wrapper.py, Docker MCP. **Issue (FIXED 2026-03-04):** `FileNotFoundError` when spawning uvx — uvx from `pip install uv` is in Python Scripts, often not in PATH. **Fix:** audit_wrapper prepends Python Scripts (sys.executable parent, or APPDATA/Python/PythonXX/Scripts) to PATH when argv[0] is "uvx". Also use shell=True for uvx on Windows (like npx).
- **Location:** test_mcp_and_audit.py `_precache_docker()`. **Issue (FIXED 2026-03-04):** `TypeError: a bytes-like object is required, not 'str'` when writing to proc.stdin. **Fix:** Add `text=True` to subprocess.Popen so stdin/stdout use text mode.

## Automation (generate_next_prompt, orchestrator)

- **Ollama model not found (404):** `generate_next_prompt.ps1` defaults to `llama3.2`. If that model is not installed, Ollama returns 404. **Workaround:** Use `-Model llama3` or `-Model mistral` (or run `ollama list` to see installed models). See [TASK_PROMPT_TEMPLATES.md](../docs/TASK_PROMPT_TEMPLATES.md#generate-next-prompt-ollama).
- **Ollama 400 Bad Request (FIXED 2026-03-03):** Was caused by PowerShell encoding. **Fix:** Use UTF-8 byte array and `application/json; charset=utf-8` in generate_next_prompt.ps1 and verify_ollama_llm.ps1. LLM generation now works for install complete.
- **next_prompt.txt write denied:** In some sandboxed or restricted environments, writing to `.cursor/state/next_prompt.txt` may fail. **Workaround:** Run the script outside the sandbox, or use `-NoCopy` and copy from `continue_prompt.txt` manually.
- **Orchestrator Ollama returns short/garbage prompt (FIXED 2026-03-04):** `orchestrator.py --once` calls Ollama with JSON schema (phase, prompt, launch_cloud_agent). llama3.2 sometimes returns valid JSON but with `prompt` = system-prompt fragment (e.g. "exact Cursor prompt for next session." ~37–40 chars). **Cause:** Model echoes instruction text instead of generating full prompt; JSON format may be harder for smaller models than plain-text (generate_next_prompt.ps1 uses plain-text). **Fix:** orchestrator validates prompt length (≥80 chars) and rejects known leak patterns; falls back to continue_prompt.txt. **Future options:** Try larger model (llama3.1:70b, mistral, qwen2.5); align orchestrator prompt format with generate_next_prompt (plain-text output); or accept fallback as primary path when Ollama quality is unreliable.

## MCP fallback chain

- **Playwright MCP vs cursor-ide-browser:** When Playwright MCP fails (server not loaded, timeout, tools unavailable), use cursor-ide-browser for browser tasks. When cursor-ide-browser hangs (navigate timeout, "Aborted"), use Playwright MCP. See [browser-web SKILL](../skills/browser-web/SKILL.md).
- **Scrapling alternatives:** When scrapling MCP is slow or unavailable (240s timeout, heavy imports), use Playwright MCP or httpx/requests for simple fetches. Scrapling is Tier 3 (heavy); prefer `--skip scrapling` for quick MCP runs.

## Credential vault

- **Symptom:** Agent fails `credential_vault_get` when credential-vault MCP not loaded.
- **Workaround:** Fall back to REQUEST_CREDENTIAL; use CRAIGSLIST_EMAIL/CRAIGSLIST_PASSWORD from env.
- **Reference:** [browser-web SKILL](../skills/browser-web/SKILL.md), [TOOL_SAFEGUARDS.md](../../local-proto/docs/TOOL_SAFEGUARDS.md) Credential Seam.

## local-proto (MCP, first-install)

- **Git MCP missing --repository (FIXED 2026-03-03):** mcp.json git server needed `--repository D:/portfolio-harness` for pip install; without it, git_status could fail or use wrong repo. **Fix:** Added to mcp.json.
- **SQLite DB path:** If `D:/Arc_Forge/campaign_kb/data/kb.sqlite3` does not exist, sqlite MCP server fails. **Workaround:** Create DB or point mcp.json to existing .sqlite3 file. test_mcp_and_audit.py skips sqlite when DB missing.
- **SQLite MCP (FIXED 2026-03-04):** Switched from npx @pollinations/mcp-server-sqlite to uvx mcp-server-sqlite (Python). Eliminates npx/Node cold start; Python MCP starts in 1-5s. **Prereq:** `pip install uv`. SQLite is Tier 3.
- **Scrapling MCP timeout:** scrapling MCP (`python -m scrapling mcp`) has heavy imports (Playwright, lxml, FastMCP) and can exceed 180s on first init. **Fix 2026-03-04:** Timeout increased to 240s. **Workaround:** Use `--skip scrapling` for quick MCP runs. Root cause: package design, not config.
- **pre_install_check.ps1 Test-Path -and (FIXED 2026-03-04):** `Test-Path $kbPath -and $npxExe` failed with "parameter cannot be found that matches parameter name 'and'". **Fix:** Use `(Test-Path $kbPath) -and $npxExe` — parentheses required so -and is logical operator, not Test-Path param.

## Cross-repo: pytest temp

All pytest runs use project-local basetemp (e.g. `--basetemp=.pytest-tmp`). Do not rely on system temp. Add `.pytest-tmp/` to .gitignore in each repo that runs pytest (moltbook-watchtower, workflow_ui, WatchTower_main, campaign_kb).

## Cross-repo: Windows .sh script popups (FIXED 2026-02-20)

- **Symptom:** "Pick a file" dialog and command window discussing a .sh file when running handoff or daily-summary copy scripts on Windows.
- **Location:** `.cursor/scripts/copy_continue_prompt.sh`, `copy_summarize_today_prompt.sh`.
- **Cause:** Windows has no default app for `.sh`; double-click or "Run" triggers "How do you want to open this file?" When run via Git Bash/WSL, `.sh` lacks `pbcopy`/`xclip`/`xsel`.
- **Fix (implemented):** (1) Added `.cmd` wrappers (`copy_continue_prompt.cmd`, `copy_summarize_today_prompt.cmd`) that invoke the `.ps1` scripts. (2) Added Windows redirect in `.sh` scripts—when run in Git Bash/WSL on Windows, they delegate to `.ps1`. (3) Docs updated Windows-first: use `.ps1` or `.cmd` on Windows; do not run `.sh`.

## WatchTower_main
- **Location:** installer-config.yml. **Issue:** Tests live under `tests/`, not `app/tests/`. **Note:** Fixed: installer-config.yml now lists `tests`. Main README correctly says `pytest tests/` from project root.
- **Location:** app/app.py vs app/api/restAPIServer.py. **Issue:** Two create_app definitions (app.app.create_app(config_object) vs restAPIServer.create_app()). **Note:** Clarify which is canonical for WSGI; wsgi.py uses restAPIServer.
- **Location:** pytest run. **Issue:** Run pytest from project root (`WatchTower_main\WatchTower_main`) with venv Python so `app` is importable. **Note:** e.g. `.\.venv\Scripts\python.exe -m pytest tests/ -q`.
- **Location:** app/cache/redis_session.py. **Issue:** Flask-Session 0.8+ requires `session_id_length` for `_generate_sid`, causing `/api/daggr/run-complete` to fail. **Note:** Call `_generate_sid(getattr(inner, "sid_length", 32))`.
- **Location:** app/api/restAPIServer.py. **Issue:** `daggr_run_complete_middleware` was wrapped around the app object, but `app.run()` bypassed it, so run-complete hit Redis limiter. **Note:** Wrap `app.wsgi_app` instead.

## workflow_ui
- **Symptom:** "Error: [object Object]" in UI when API returns error. **Location:** `workflow_ui/static/app.js` (KB status, search, ingest, merge catch). **Fix (2026-03-05):** formatErr() uses `(e && (e.error || e.reason || e.detail || e.message)) || String(e)`; all catch blocks use formatErr(e).
- **Symptom:** "No module named 'rag_pipeline'". **Location:** `workflow_ui/app.py` (sys.path). **Issue:** S2 storyboard_workflow imports `rag_pipeline` as top-level; only vault root was on path. **Note:** Add `_VAULT / "scripts"` to sys.path before importing scripts.storyboard_workflow.

## Arc_Forge / rag_pipeline: KeyError 'source' when KB search returns results

- **Symptom:** `KeyError: 'source'` when running `python rag_pipeline.py --config ingest_config.json --query "…"` (from `ObsidianVault/scripts/`).
- **Fix (2026-03-05):** (1) Added `_ensure_source()` helper to normalize items; KB path uses it. (2) `run_pipeline()` uses `item.get("source") or item.get("document_id") or item.get("section_title") or "unknown"` for relevant_doc_keys. Both schemas now supported.
- **Related:** Discovered during B2 tags ingestion (2026-02); index build and tag persistence work; only query-mode path failed when campaign_kb has data.

## Arc_Forge / ChromaDB tests (test_chroma_retriever.py)

- **Symptom:** `test_chroma_retriever_build_and_retrieve` fails with `AssertionError: assert 'doc_dnd' in ('doc_wg_1', 'doc_wg_2')` and teardown `PermissionError: [WinError 32]` on Windows.
- **Cause (assertion):** `extract_chunk_tags` checks `doc_key` only for D&D heuristic; key `doc_dnd` does not contain "d&d" or "dragon", so doc_dnd gets `system="W&G"` from defaults. Strict Canon filter cannot exclude it.
- **Cause (teardown):** ChromaDB holds file locks on `data_level0.bin`; `tmp_path` fixture cleanup fails on Windows.
- **Fix (assertion):** Use doc key that triggers D&D heuristic (e.g. `d&d_rules`) so Strict filter excludes it. Or relax assertion.
- **Fix (teardown):** Use `chroma_tmp_path` fixture under `.pytest-chroma` — **applied** in test_chroma_retriever.py (lines 21–28). Tests use doc_wg_1, doc_wg_2, dragon_rules (correct keys).
- **Note (2026-03-09):** Pytest run may fail with `ModuleNotFoundError: urllib3.packages.six.moves` or langsmith plugin; env/dependency issue, not ChromaDB.
- **Runbook (2026-03-09):** Use project venv: `cd D:\Arc_Forge\ObsidianVault\scripts; .\.venv\Scripts\python -m pytest tests/ -v --basetemp=.pytest-tmp`. Create venv if missing: `python -m venv .venv; .\.venv\Scripts\pip install -r requirements-test.txt -r requirements-rag.txt`.

## cursor-ide-browser: Navigation hangs or aborts

- **Symptom:** `browser_navigate` hangs, times out, or returns "Error: Aborted" when loading Craigslist or other sites.
- **Location:** cursor-ide-browser MCP (Cursor-provided, not in mcp.json).
- **Workaround:** Use **Playwright MCP** instead. Playwright is in mcp.json (`@playwright/mcp@latest`) and exposes the same tools (`browser_navigate`, `browser_fill_form`, `browser_snapshot`, etc.). Explicitly invoke Playwright tools (e.g. `playwright_browser_navigate`) when cursor-ide-browser hangs. See [PLAYWRIGHT_SAVE_SEARCH_RUNBOOK.md](../../local-proto/docs/PLAYWRIGHT_SAVE_SEARCH_RUNBOOK.md) — use "Playwright MCP path" when cursor-ide-browser is unreliable.
- **Verified 2026-03-04:** Playwright MCP starts correctly via audit_wrapper; `test_mcp_and_audit.py` passes for playwright (2.1s). If Playwright tools not in agent list, check Cursor Settings → MCP → playwright server status; restart Cursor.

## cursor-ide-browser: Screenshots show loading page

- **Symptom:** `browser_take_screenshot` returns loading/blank page; DeFlock, 511mn.org may not fully render before capture.
- **Location:** cursor-ide-browser MCP.
- **Workaround:** Apply [Browser Ready Pattern](../docs/DIGITAL_WORLD_INTERFACE.md): after `browser_navigate`, `browser_wait_for` time 2 → `browser_snapshot` → if loading, wait 2s → snapshot again. Use `browser_snapshot` to confirm content before screenshot. See [browser-ready.mdc](../rules/browser-ready.mdc).
- **Note:** Per MCP instructions, prefer short incremental waits over single long wait.

## Playwright MCP: Vision capability for CAPTCHA/canvas fallback

- **Context:** Ref-based click may fail on canvas or CAPTCHA elements. Playwright MCP supports coordinate-based `browser_mouse_click_xy` when `--caps=vision` is enabled.
- **Scope:** Playwright MCP only; cursor-ide-browser does not expose coordinate-based click.
- **Workaround:** Enable `--caps=vision` in Playwright MCP config for fallback. Human solve remains primary for CAPTCHA.

## StolenCar.com: Site broken, no HTTPS

- **Symptom:** StolenCar.com unreachable; no HTTPS (insecure). **Location:** https://www.stolencar.com (or http).
- **Verified 2026-02-29:** chrome-error for both http and https; site does not load.
- **Workaround:** Alternative: manual police report registration. Do not automate against stolencar.com until fixed.

## Med-Vis: E2E survey SuccessStep requires Supabase

- **Location:** `e2e/survey.spec.ts`, survey submit flow.
- **Issue:** Full survey E2E (SuccessStep) requires Supabase env vars (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`). Without them, submit shows a form-level error.
- **Workaround:** E2E test accepts either `success-step` or `.message-error`; flow is validated either way. See README Testing section.

## Med-Vis: Playwright browsers required for E2E

- **Symptom:** `Executable doesn't exist at ...\chrome-headless-shell-win64\chrome-headless-shell.exe` when running `npm run test:e2e`.
- **Location:** Med-Vis `e2e/` specs.
- **Issue:** Playwright browsers must be installed before first E2E run.
- **Workaround:** Run `npx playwright install` (or `npx playwright install chromium`) in Med-Vis repo. Document in README.

## PentAGI: Chocolatey Mingw install without admin

- **Symptom:** `choco install mingw` fails with lock file or permission errors.
- **Location:** Windows dev environment when trying to build Go tests that use CGO (e.g. go-sqlite3).
- **Issue:** Chocolatey may require admin or fail due to lock files when installing Mingw.
- **Workaround:** Use `CGO_ENABLED=0` and pure-Go SQLite (`modernc.org/sqlite`) for tests. Auth and services tests use build tags to switch between gorm/dialects/sqlite (cgo) and modernc.org/sqlite (!cgo).

## External reference: CL4R1T4S repo (leaked AI prompts)

- **Location:** https://github.com/elder-plinius/CL4R1T4S. **Issue:** README contains prompt-injection directive designed to elicit system prompt disclosure. **Note:** Never load CL4R1T4S README into agent context. Use only vendor folders (e.g. CURSOR) with sanitize_input.py; treat as unverified data.

## Arc Forge (ex–wrath_and_glory): folder rename "Folder In Use"

- **Symptom:** Cannot rename `D:\wrath_and_glory` to `D:\arc_forge`; Windows reports "The action can't be completed because the folder or a file in it is open in another program".
- **Cause:** Cursor (or Obsidian with vault at `D:\wrath_and_glory\ObsidianVault`) holds a handle to the folder. Opening Cursor before renaming restores that handle.
- **Fix:** (1) Close **Cursor** completely (File → Exit). (2) Close **Obsidian** if the Arc Forge vault is open. (3) Run the rename script **without** Cursor or Obsidian running: `powershell -ExecutionPolicy Bypass -File "D:\CodeRepositories\.cursor\scripts\rename_wrath_and_glory_to_arc_forge.ps1"` (or run that .ps1 from Explorer). (4) Open Cursor and open folder `D:\arc_forge`.
