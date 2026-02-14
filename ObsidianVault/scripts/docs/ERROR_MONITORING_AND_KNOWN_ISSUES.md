# Error monitoring and known issues (RAG pipeline)

First place to look for RAG pipeline error monitoring, traceback handling, and the KeyError 'source' fix. For cross-repo known issues, see [known-issues.md](D:\CodeRepositories\.cursor\state\known-issues.md).

## Table of contents

- [Quick reference](#quick-reference)
- [Known issue: KeyError 'source'](#known-issue-keyerror-source)
- [Current state](#current-state)
- [What cannot be resolved (yet)](#what-cannot-be-resolved-yet)
- [retrieve_context schema contract](#retrieve_context-schema-contract)
- [Improvements to automate error identification](#improvements-to-automate-error-identification)
- [Agent debugging tips](#agent-debugging-tips)
- [References](#references)

---

## Quick reference

| Component | What it does | Captures tracebacks? |
|-----------|--------------|----------------------|
| **Python traceback** | Uncaught exceptions print to stderr | Yes (manual inspection) |
| **pytest** | Runs tests; failures show tracebacks | Yes (for test runs) |
| **Daggr / report_run.py** | Reports workflow run completion to WatchTower: `success`, `duration_sec`, `project` | No — only success/fail flag |
| **WatchTower** | Flask app; POST `/api/daggr/run-complete`; Prometheus/Grafana metrics | No — run-level metrics only |
| **ingest_diagnostic.log** | Structured JSON logs for PDF ingestion | For ingestion only |
| **known-issues.md** | Manual log of known bugs and fixes | N/A |
| **TROUBLESHOOTING.md** | Per-repo playbooks | N/A |

**Key gap:** `KeyError 'source'` — `retrieve_context()` has two return schemas (KB vs DocumentIndex); `run_pipeline()` assumes `item["source"]` for all. See [rag_pipeline.py](D:\Arc_Forge\ObsidianVault\scripts\rag_pipeline.py) lines 1196–1205 vs 1231–1234 and lines 1410–1412.

---

## Known issue: KeyError 'source'

**Symptom:** During B2 tags ingestion (2026-02), running `python rag_pipeline.py --config ingest_config.json --query "orks"` produced:

```
KeyError: 'source'
  File "rag_pipeline.py", line 1412, in run_pipeline
    relevant_doc_keys = [item["source"] for item in query_context]
```

**Cause:** `retrieve_context()` has two return schemas but a single consumer expects one:

| Path | When | Return keys |
|------|------|-------------|
| KB search | `use_kb_search` True and `search_sections` returns results | `section_id`, `document_id`, `section_title`, `text`, `score` |
| DocumentIndex / fallback | KB search empty or disabled | `source`, `score`, `text` |

`run_pipeline()` always uses `item["source"]`. When KB search wins (campaign_kb has data), it fails.

**Code pointers:** KB path [rag_pipeline.py](D:\Arc_Forge\ObsidianVault\scripts\rag_pipeline.py) lines 1196–1205; DocumentIndex path lines 1231–1234; consumer line 1412.

**Fix (not yet applied):** Normalize `retrieve_context()` so all paths return items with a `source` key. See [retrieve_context schema contract](#retrieve_context-schema-contract) below.

---

## Current state

### What exists

Same as quick reference table above. Daggr `report_run.py` POSTs to WatchTower only when `WATCHTOWER_METRICS_URL` is set and WatchTower is running. Daggr workflows (search_workflow, etc.) use it; rag_pipeline does not.

### What is missing

- **No centralized exception capture** — Uncaught exceptions (e.g. KeyError) only appear in stdout/stderr; no automatic logging to file or remote.
- **No structured error reporting** — WatchTower/Daggr report *that* a run failed, not *why* (no traceback, no error type).
- **Daggr not fully operational** — `report_run.py` exists and can POST to WatchTower, but:
  - `WATCHTOWER_METRICS_URL` must be set
  - WatchTower must be running
  - daggr workflows (search_workflow, etc.) use it; rag_pipeline does not

---

## What cannot be resolved (yet)

These items are blocked or deferred:

| Blocker | Reason |
|---------|--------|
| **WatchTower error endpoint** | `POST /api/errors` does not exist; requires WatchTower changes and env (`WATCHTOWER_METRICS_URL`). |
| **Daggr integration for rag_pipeline** | `rag_pipeline` is not invoked from a Daggr workflow; no `with_run_reporting`; `report_run.py` is campaign_kb-specific. |
| **KB→text_map bridge** | When KB search returns results, `extract_entities_from_docs` and `summarize_context_from_docs` expect `text_map` keys; KB returns `document_id`, `section_id`, not file paths. Requires `run_pipeline` to augment `text_map` from `query_context` when KB path is used (or refactor downstream to accept `query_context` directly). |
| **Centralized exception capture** | No shared error-logging layer; each script would need explicit `try/except` + file/endpoint logging. |

---

## retrieve_context schema contract

**Target schema:** All paths must return items with `{source, score, text}`.

**KB path fix:** Add `source` to each item. Options: `source = str(section.document_id)`, `section_title`, or `f"doc_{section.document_id}:sec_{section.id}"`. Ensure downstream receives text (see "KB→text_map bridge" above).

**Consumer (temporary defensive measure):** `run_pipeline` line 1412 could use `item.get("source") or item.get("document_id")` as a stopgap; prefer normalization at source.

---

## Improvements to automate error identification

| # | Improvement | Status |
|---|-------------|--------|
| 1 | **Structured error logging** — Wrap `run_pipeline` (and other entry points) in `try/except` that logs `{error_type, message, traceback}` to a file (e.g. `_rag_cache/errors.log`) or to WatchTower if it gains an error endpoint. | [Done] — `log_structured_error` in error_handling.py; run_pipeline, main(), workflow_ui routes |
| 2 | **Unify retrieve_context return schema** — Define a single dict shape (`source`, `score`, `text`) and ensure KB search path maps its results to that shape. Prevents schema mismatches. | [Done] — KB path adds `source`; text_map augmented for downstream |
| 3 | **Daggr integration for rag_pipeline** — If rag_pipeline is invoked from a Daggr workflow, `with_run_reporting` would at least record success/fail. It does not capture tracebacks; that would need a separate error-reporting step. | [Not started] |
| 4 | **WatchTower error endpoint** — Add e.g. `POST /api/errors` to accept `{project, error_type, message, traceback}` and store or forward for alerting. Then scripts could POST on exception. | [Not started] |
| 5 | **Pytest coverage** — Add a test that runs `run_pipeline` with `use_kb_search` mocked to return KB-style results, and assert the consumer handles both schemas (or that normalize happens first). | [Done] — test_retrieve_context_kb_path_schema, test_retrieve_context_document_index_path_schema, test_run_pipeline_handles_unified_schema, test_log_structured_error |

---

## Agent debugging tips

Per [.cursorrules](D:\CodeRepositories\.cursorrules) and [prompt_engineering_tool_output_optimization.md](D:\CodeRepositories\.cursor\prompt_engineering_tool_output_optimization.md):

- **When debugging:** Cap terminal output (`tail -n 100`, `Select-Object -First 20`); avoid full log reads.
- **Error log size:** If `ingest_diagnostic.log` or debug logs grow large, read by range or tail first.
- **Grep/search:** Use `head_limit`, `target_directories` to narrow scope.

---

## References

- [known-issues.md](D:\CodeRepositories\.cursor\state\known-issues.md) — Cross-repo known issues
- [TROUBLESHOOTING_AND_PLAYBOOKS.md](D:\CodeRepositories\.cursor\docs\TROUBLESHOOTING_AND_PLAYBOOKS.md) — AI-facing index
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) — Scripts troubleshooting
- [campaign_kb/daggr_workflows/report_run.py](D:\Arc_Forge\campaign_kb\daggr_workflows\report_run.py) — WatchTower run reporting
