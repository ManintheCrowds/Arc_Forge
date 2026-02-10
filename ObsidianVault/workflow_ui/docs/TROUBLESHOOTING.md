# Workflow UI – Troubleshooting

## KB status or search shows "Error: [object Object]"

**Symptom:** Campaign KB tab shows "KB status: Error: [object Object]" or search/ingest/merge results show "[object Object]" in red.

**Cause:** The API returns a JSON error body (e.g. `{ "error": "...", "detail": "..." }`). The frontend rejects with that object; using `e.message || String(e)` on a plain object yields "[object Object]".

**Fix:** In `workflow_ui/static/app.js`, for any KB-related `.catch()`, use a string derived from the response: `(e && (e.error || e.reason || e.detail || e.message)) || String(e)`. See known-issues (workflow_ui) in `.cursor/state/known-issues.md`.

---

## S2 Drafts: "No module named 'rag_pipeline'"

**Symptom:** Clicking "Run Stage 2" shows **No module named 'rag_pipeline'**.

**Cause:** `storyboard_workflow.run_stage_2` does `from rag_pipeline import load_pipeline_config`. Only the vault root was on `sys.path`; `rag_pipeline` lives in `vault/scripts/rag_pipeline.py`.

**Fix:** In `workflow_ui/app.py`, add the scripts directory to `sys.path` before importing from scripts:

```python
_SCRIPTS = _VAULT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
```

See known-issues (workflow_ui) in `.cursor/state/known-issues.md`.

---

## Pytest fails or wrong cwd (PowerShell)

**Symptom:** `cd D:\path && pytest tests/ -v` fails with a parse or "command not found" error.

**Cause:** PowerShell does not support `&&` for chaining commands.

**Fix:** Use `;` instead of `&&`. Run pytest from the workflow_ui directory so `pytest.ini` (basetemp=.pytest-tmp) is used:

```powershell
cd D:\Arc_Forge\ObsidianVault\workflow_ui; python -m pytest tests/ -v
```

---

## Campaign KB search: "campaign_kb required"

**Symptom:** KB status shows an error or search returns nothing / connection error.

**Cause:** The workflow_ui Flask app proxies KB search to the campaign_kb service. If campaign_kb is not running, status check and search fail.

**Fix:** Start campaign_kb (e.g. from campaign_kb project root):

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then in workflow_ui, click "Check" for KB status; search should work when campaign_kb is up.
