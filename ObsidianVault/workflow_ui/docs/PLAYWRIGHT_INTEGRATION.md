# Playwright Integration Guide

How Playwright is integrated into workflow_ui and how to extend it to other projects or add more tests.

## Overview

Playwright is a browser automation library that runs end-to-end (E2E) tests in a real browser (Chromium by default). It drives the UI, performs actions (click, fill, navigate), and asserts outcomes.

**Workflow_ui reference:** `tests/test_e2e_playwright.py` — 3 tests covering Legacy S1, Workbench create-module, and Workbench workflow run.

---

## How It Works

### 1. Install

```bash
pip install playwright
python -m playwright install chromium
```

- **Chromium** — Browser binary used by Playwright (headless by default).
- **PowerShell:** Use `python -m playwright` (not `playwright`); the CLI may not be on PATH.

### 2. Run

```bash
cd D:\Arc_Forge\ObsidianVault
python -m pytest workflow_ui/tests/test_e2e_playwright.py -v
```

### 3. Optional Dependency

Tests use `pytest.importorskip("playwright.sync_api")`, so if Playwright is not installed, the E2E tests are skipped. Other tests (API, audit) still run.

---

## Architecture (workflow_ui)

| Component | Purpose |
|-----------|---------|
| `_start_app(campaigns, scripts)` | Spawn Flask app in subprocess with temp Campaigns; wait for HTTP |
| `_stop_app(proc)` | Terminate app cleanly |
| `_dismiss_first_run_overlay(page)` | Dismiss UW-10 overlay when testing Legacy (empty tree) |
| `sync_playwright()` | Context manager; launches Chromium |
| `page.goto()`, `page.click()`, `page.fill()` | Navigate and interact |
| `page.locator()`, `page.evaluate()` | Assert / call JS |

**CWD:** App runs from **vault root** (ObsidianVault) so `workflow_ui` is importable. Tests use `tmp_path` for Campaigns.

---

## Utilization Patterns

### Start server in fixture

```python
def _start_app(campaigns: Path, scripts: Path):
    proc = subprocess.Popen(
        [sys.executable, "-m", "workflow_ui.app"],
        cwd=str(vault_root),
        env={**os.environ, "WORKFLOW_UI_PORT": str(port), ...}
    )
    _wait_for_http(base_url + "/")
    return proc, base_url
```

### Handle overlays

```python
# Overlay blocks clicks; dismiss via JS
page.evaluate("""
    localStorage.setItem('workflow_ui:first_run_dismissed', '1');
    document.getElementById('first-run-overlay')?.classList.remove('visible');
""")
```

### Use app callbacks instead of DOM clicks

When elements are obscured (e.g. Mermaid SVG):

```python
page.evaluate("window.workflowSelect && window.workflowSelect('brainstorm')")
```

### Assert file output

```python
assert (campaigns / "first_arc" / "task_decomposition.yaml").exists()
```

---

## Extending Coverage

### Add a new E2E test

1. Copy `test_e2e_workbench_load_and_create_module` skeleton.
2. Use `_start_app`; `try/finally` with `_stop_app`.
3. `page.goto(base_url)` → `page.click(...)` → `assert ...`.
4. Assert both UI state and file-system artifacts.

### Suggested additions (DEVELOPMENT_PLAN_REMAINING)

- S2: Run Stage 2 → assert encounter drafts in `encounters/`
- S4: Run Refine → assert new `_draft_vN.md`
- S5: Run Export → assert artifact paths
- Note editor: Click tree item → assert content loaded

### Mocking

- Use `WORKFLOW_UI_FAKE_RUNS=1` for S1 to avoid RAG.
- For S2/S4/S5, either mock at app boundary (like API tests) or use real RAG/LLM (slower).

---

## Integrating into Other Projects

### For a Flask/FastAPI web app

1. **Dependencies:** `pip install playwright pytest`
2. **Install browser:** `python -m playwright install chromium`
3. **Start server:** Subprocess in fixture or `httpx.ASGITransport` for in-process.
4. **Test file:** `tests/test_e2e_playwright.py` with `sync_playwright()`.
5. **Skip if missing:** `pytest.importorskip("playwright.sync_api")` so CI works without Playwright.

### For a non-Python frontend

- Use Playwright Node.js API or Playwright Python against a running dev server.
- Or run a static build server in subprocess.

### CI/CD

- Install Playwright browsers in the pipeline: `python -m playwright install --with-deps chromium`
- Run: `pytest tests/ -v` (E2E tests run when Playwright is installed)

---

## Reference

- **Tests:** `workflow_ui/tests/test_e2e_playwright.py`
- **README:** `workflow_ui/README.md` § Playwright (E2E)
- **Manual I/O:** `docs/manual_io_checklist.md` — stepwise browser validation
