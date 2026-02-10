# Session Memory

Output directory for Phase 4 Session Memory.

- **Archivist:** `YYYY-MM-DD_archivist.md` — canonical timeline entries, flagged future consequences, retrieval anchors. Run: `python session_ingest.py --session path/to/session.md`.
- **Foreshadowing:** `threads.md` — delayed consequences (2–5 sessions, limit 5). Run: `python session_ingest.py --foreshadow --context path/to/archivist_output.md`.

See [docs/narrative_workbench_spec](../docs/narrative_workbench_spec.md) and [docs/archivist_output_format](../docs/archivist_output_format.md).
