# Workflow GUI — Remaining Development Tasks

Agent-referenceable plan. Execute tasks in order; each has Goal, Files, Done-when, Reference.

## Source of truth

- **Audit plan:** `D:\CodeRepositories\.cursor\plans\workflow_gui_audit_and_i_o_testing_b75be279.plan.md` — §3.1 (API tests), §3.2 (manual I/O checklist), §5–6 (README Testing).
- **GUI spec:** [../Campaigns/docs/gui_spec.md](../Campaigns/docs/gui_spec.md).
- **App:** [../app.py](../app.py). **Tests:** [../tests/test_api.py](../tests/test_api.py).
- **Pattern for new API tests:** `client` fixture patches `app_module.CAMPAIGNS` with `tmp_campaigns`; mock workflow function at app boundary (e.g. `@patch("workflow_ui.app.run_stage_2")`) so RAG/LLM are not invoked.
- **User-integration audit (second workflow):** [GUI_AUDIT_USER_INTEGRATION.md](GUI_AUDIT_USER_INTEGRATION.md) — SME audit for first-run experience and adoption. Top 3 recommendations: (1) Add visible "Getting started" hint with pipeline order and S1 prerequisite, (2) One-line in-context help on each S1–S5 panel, (3) Emphasize pipeline order in tab layout or labels. Reusable prompt and input pack: [GUI_AUDIT_PROMPT.md](GUI_AUDIT_PROMPT.md).

---

## Roadmap status (current)

- **Wave A (P0–P1): complete** — debug mode now env-driven, error payloads normalized, onboarding/prereq status panel added, file viewer uses modal.
- **Wave B (P2–P3): complete** — client-side validation with field errors, progress indicators for S2/S4/session tasks, tab grouping, LocalStorage autosave with restore prompts.
- **Wave C (P4): complete** — modularization, live updates (polling toggle), wizard flow, OpenAPI `/docs`, Playwright E2E baseline.
- **Verification:** `python -m pytest tests/ -v` (workflow_ui) — 45 passed.

---

## Remaining Work Breakdown (all backlog items)

### A) Testing and verification

- **Playwright E2E expansion** (remaining): Add S2/S4/S5 coverage and assert artifact outputs for each stage.
  - Done when: Additional Playwright tests run with fixtures and validate stage outputs.
- **Manual I/O checklist alignment** (verify): Ensure steps mention wizard toggle and auto-refresh behavior.
  - Done when: checklist updated to reflect wizard and auto-refresh (if used).

### B) Documentation readiness

- **OpenAPI docs discoverability** (verify): Mention `/docs` in README and workflow_ui README.
  - Done when: both docs include a short `/docs` pointer.
- **README testing links** (verify): Ensure manual I/O checklist and remaining work doc are linked.
  - Done when: README contains direct links.

### C) UX + product readiness

- **In-context help (S1–S5)** (remaining): One-line prerequisites and outputs on each stage panel.
  - Done when: each stage panel includes a short “Requires/Outputs” line.
- **Cross-links to campaign_kb** (remaining): Link NPC/location IDs in feedback/encounters to KB entries.
  - Done when: feedback UI supports selection/autocomplete from KB sources.

### D) Security + operational readiness

- **Path traversal edge cases** (verify): URL-encoded traversal cases covered in tests.
  - Done when: explicit tests for encoded traversal pass.
- **Rate limiting docs** (verify): docs note limits and storage backend configuration.
  - Done when: docs mention storage backend config (Redis).

---

## Task 2: README — Testing section

**Goal:** Anyone (or any agent) can run tests and understand env requirements without opening the audit plan.

**Files:** [../README.md](../README.md).

**Done when:**
- New **Testing** section describes how to run tests (e.g. `cd ObsidianVault && pytest workflow_ui/tests/ -v`).
- Section lists env requirements: storyboard under `Campaigns/_rag_outputs/` (or path passed to Stage 1), `ingest_config.json` for Stage 2/4, and that "real" run stages need RAG/LLM.
- Section links to the manual I/O checklist (Task 3) and to this doc for remaining work.

**Reference:** Audit plan §5–6, §3.2.

---

## Task 3: Manual I/O checklist

**Goal:** A repeatable, stepwise checklist for validating GUI I/O in the browser.

**Files:** [manual_io_checklist.md](manual_io_checklist.md).

**Done when:**
- `docs/manual_io_checklist.md` exists with the nine steps and Expected lines.
- README Testing section (Task 2) links to this file.

**Content (nine steps, each with one-line Expected):**
1. Load: Open `/` — **Expected:** CSS/JS load; arc selector and pipeline visible; tree/encounters load if any.
2. S1: Run Stage 1 for an arc with storyboard under `Campaigns/_rag_outputs/` — **Expected:** task_decomposition appears; tree/artifacts update; out-s1 shows success.
3. Task decomp form: Load arc with task_decomposition, edit, Save — **Expected:** form reflects file; reload shows changes.
4. S2: Run Stage 2 — **Expected:** encounter drafts under `encounters/` (and opportunities/ if any); tree/artifacts update.
5. Feedback form: Load arc, select encounter, add/remove/edit feedback, Save — **Expected:** `{arc_id}_feedback.yaml` updated; reload shows data.
6. S4: Pick draft from dropdown, Run Refine (feedback file present) — **Expected:** new `_draft_vN.md`; tree/artifacts refresh.
7. S5: Run Export — **Expected:** expanded storyboard, JSON, campaign_kb file; out-s5 shows paths.
8. File view: Click encounter in tree — **Expected:** content opens, or "Not found" for missing file.
9. Provenance: Encounters list — **Expected:** shows "draft vN" and "from {arc}_feedback.yaml" where applicable.

**Reference:** Audit plan §3.2.

---

## Task 4: API test — POST /api/run/stage2

**Goal:** Stage 2 is covered by pytest without invoking RAG/LLM.

**Files:** [../tests/test_api.py](../tests/test_api.py).

**Done when:**
- New test `test_post_run_stage2_ok` creates under `tmp_campaigns`: an arc dir with `task_decomposition.yaml`, and a storyboard under `tmp_campaigns/_rag_outputs/`.
- Test mocks `run_stage_2` at app boundary (e.g. `@patch("workflow_ui.app.run_stage_2")`) to return `{"status": "success"}`.
- Test POSTs to `/api/run/stage2` with `arc_id` (and `task_decomposition_path` / `storyboard_path` if required so paths resolve under patched CAMPAIGNS).
- Test asserts status 200 and response `status == "success"` (or mock called with expected paths).
- `pytest workflow_ui/tests/test_api.py -v -k stage2` passes.

**Reference:** Audit plan §3.1; app.py `api_run_stage2` (body: `arc_id`, `task_decomposition_path`, `storyboard_path`); existing `test_post_run_stage1_ok` as pattern.

---

## Task 5: API test — POST /api/run/stage4

**Goal:** Stage 4 (refine encounter) is covered by pytest without invoking LLM.

**Files:** [../tests/test_api.py](../tests/test_api.py).

**Done when:**
- New test `test_post_run_stage4_ok` creates under `tmp_campaigns`: an arc dir, a draft file (e.g. `encounters/foo_draft_v1.md`), and `{arc_id}_feedback.yaml`.
- Test mocks `refine_encounter` (e.g. `@patch("workflow_ui.app.refine_encounter")`) to return `{"status": "success", "path": "..."}`.
- Test POSTs to `/api/run/stage4` with `arc_id` and `draft_path` (absolute path under tmp). Omit `feedback_path` to exercise app deriving it from `arc_id`.
- Test asserts status 200 and mock called with given `draft_path` and derived `feedback_path`.
- `pytest workflow_ui/tests/test_api.py -v -k stage4` passes.

**Reference:** Audit plan §3.1; app.py `api_run_stage4` (body: `draft_path`, `arc_id`, optional `feedback_path`).

---

## Task 6: API test — POST /api/run/stage5

**Goal:** Stage 5 (export final specs) is covered by pytest.

**Files:** [../tests/test_api.py](../tests/test_api.py).

**Done when:**
- New test `test_post_run_stage5_ok` creates under `tmp_campaigns`: an arc dir with at least one encounter file (e.g. `encounters/foo_draft_v1.md`).
- Test mocks `export_final_specs` (e.g. `@patch("workflow_ui.app.export_final_specs")`) to return `{"status": "success", "paths": {}}`.
- Test POSTs to `/api/run/stage5` with `arc_id`.
- Test asserts status 200 and response `status == "success"` (or mock called with expected `arc_id` / `arc_dir`).
- `pytest workflow_ui/tests/test_api.py -v -k stage5` passes.

**Reference:** Audit plan §3.1; app.py `api_run_stage5` (body: `arc_id`).

---

## Session memory (Archivist / Foreshadow)

**Goal:** DMs can run Archivist (session note → canonical timeline/retrieval anchors) and Foreshadow (context → delayed consequences in threads) from the workflow UI.

**How to use:**
- Open the **Session memory** tab.
- **Archivist:** Enter the path to a session note that contains a `## Session Summary (for Archivist)` block (relative to vault or absolute). Click **Run Archivist**. Output is written to `Campaigns/_session_memory/YYYY-MM-DD_archivist.md` by default, or to the optional `output_path` if provided via API.
- **Foreshadow:** Enter the path to a context file (Archivist output or session summary). Click **Run Foreshadow**. Output is appended to `Campaigns/_session_memory/threads.md` by default.

**API:** `POST /api/session/archivist` (body: `session_path`, optional `output_path`); `POST /api/session/foreshadow` (body: `context_path`, optional `output_path`). Both return `{ "status": "success"|"skipped"|"error", "output_path": "...", "reason": "..." }`.

**Output location:** `Campaigns/_session_memory/` (e.g. `YYYY-MM-DD_archivist.md`, `threads.md`).

---

## Task 7 (optional): Backend unit tests for storyboard_workflow

**Goal:** Backend behavior of `run_stage_1`, `run_stage_2`, `refine_encounter`, `export_final_specs` is testable with tmp dirs and mocks.

**Files:** Create `ObsidianVault/scripts/tests/test_storyboard_workflow.py` (or `scripts/tests/` under vault). Create `scripts/tests/` if missing.

**Done:** `ObsidianVault/scripts/tests/test_storyboard_workflow.py` — tmp dirs, fixtures, mocks for RAG/LLM; one test per entry point; edge-case tests for refine_encounter (empty generate_text), export_final_specs (no encounters), run_stage_2 (empty encounters), run_stage_1 (missing storyboard raises); return-shape assertions.

**Done when:**
- Tests use tmp dirs and fixtures (storyboard, task_decomposition, draft, feedback YAML).
- RAG/LLM calls are mocked where used (e.g. in `run_stage_2`, `refine_encounter`).
- At least one test per entry point asserts output files or return shape.

**Verified 2026-02-07:** From vault scripts dir: `python -m pytest tests/test_storyboard_workflow.py -v` — 9 passed.

**Reference:** Audit plan §3.1 "Backend (storyboard_workflow) unit tests".

---

## Rate limiting (implemented)

- **Scope**: `/api/run/stage1`, `stage2`, `stage4`, `stage5` (30 requests/minute per IP); `PUT /api/arc/<id>/task_decomposition` and `PUT /api/arc/<id>/feedback` (60/minute per IP).
- **Implementation**: Flask-Limiter with in-memory storage (single-process dev); 429 responses return JSON `{"error": "rate limit exceeded"}` and `Retry-After` header. For multi-process deploy, configure Redis via `RATELIMIT_STORAGE_URL`.

---

## Future work (backlog)

- ~~Rate limiting on `/api/run/*` and/or PUTs.~~ (done)
- ~~Startup config/path validation and clear error messaging.~~ (done)

## Startup config/path validation (implemented)

- **When**: In `if __name__ == "__main__"` before `app.run()`; app aborts with clear messages to stderr if validation fails.
- **What**: `_validate_startup_paths()` checks: CAMPAIGNS exists and is a directory; CONFIG_PATH exists (required for session ingest). CAMPAIGN_KB / CAMPAIGN_KB_URL are not validated at startup (validate on first /api/kb/* if desired).
- **Required paths**: CAMPAIGNS = `{vault}/Campaigns`; CONFIG_PATH = `{vault}/scripts/ingest_config.json`. If missing, the app prints error messages and exits with code 1.
- Path-traversal audit (and tests) for `/api/arc/<id>/file/<subpath>`.
- OpenAPI or equivalent description of workflow_ui API.
- UX: "Running…" state and dirty-form warning for task decomp and feedback.
- Validation of task_decomposition and feedback schema before save.
- In-app pipeline diagram (e.g. Mermaid from workflow_diagrams.md).
- Cross-links to campaign_kb (e.g. NPCs/locations) in encounter/feedback UI.
- E2E tests (e.g. Playwright) for critical paths once the above is stable.
