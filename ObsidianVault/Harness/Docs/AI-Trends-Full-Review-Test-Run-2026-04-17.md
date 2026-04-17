---
title: "AI Trends — full review test run (self-contained)"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
---

# AI Trends — full review test run (self-contained)

**Date:** 2026-04-17  
**Scope:** All pytest cases under `local-proto/tests` whose names match `ai_trends` (no live YouTube/Ollama/Firecrawl in new contract tests; hub tests remain mocked).

## Command

```bash
cd C:\Users\Dell\Documents\GitHub\MiscRepos
python -m pytest local-proto/tests -k "ai_trends" -v --tb=line
```

## Result

| Metric | Value |
|--------|--------|
| Selected | 61 |
| Passed | 60 |
| Skipped | 1 (`test_ai_trends_gradio_e2e` — AT3b) |
| Failed | 0 |

## New artifacts (this review)

| File | Role |
|------|------|
| [local-proto/tests/test_ai_trends_mcp_tools_contract.py](../../../local-proto/tests/test_ai_trends_mcp_tools_contract.py) | In-process MCP tool contracts (mocks) |
| [local-proto/tests/test_ai_trends_cli_smoke.py](../../../local-proto/tests/test_ai_trends_cli_smoke.py) | Subprocess: `stack_intel --skip-ollama`, `ingest --sources ""` |

## Architecture review (summary)

**Layering:** Utils/hub tests → MCP contract (mocked I/O) → CLI subprocess smoke → optional operator `mcp.json` e2e (`list_ingested`).

**Gap (optional):** Subprocess MCP stdio smoke with pinned `sys.executable` + env-only config (no `mcp.json`) would cover transport + `tools/list` without production network.

**Conventions:** Tests stay under `local-proto/tests/` to match existing CI that runs `pytest local-proto/tests`.
