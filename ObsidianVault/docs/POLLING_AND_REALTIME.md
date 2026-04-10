---
title: "Polling and realtime (workflow_ui)"
tags: ["type/research", "status/draft", "domain/harness"]
---

# Polling and realtime (workflow_ui)

## Current behavior

There is **no** SSE or WebSocket for stage runs. After:

- `POST /api/run/stage1` (or stage2, 4, 5),

refresh arc state with:

- `GET /api/arc/<arc_id>/artifacts`
- `GET /api/arc/<arc_id>/tree`

The legacy UI may use **auto-refresh** toggles (see checklist on the main page) to poll on an interval.

## Future (epic)

- Job IDs + `GET /api/run/status/<job_id>` or SSE stream for long-running steps.
- Requires an async job queue or on-disk job state; not part of the current Flask app.
