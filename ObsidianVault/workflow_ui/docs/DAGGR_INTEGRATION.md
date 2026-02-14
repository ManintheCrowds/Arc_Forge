# Daggr / KB Workflows Integration

**Decision:** workflow_ui uses a **redirect** to the Daggr app at `/tools/kb-daggr`. Daggr workflows are not embedded in the Flask app.

## Rationale

- **Redirect (current):** `/tools/kb-daggr` returns 302 to `CAMPAIGN_KB_DAGGR_URL` (default `http://localhost:7860`). The Daggr app runs as a separate process (`python -m daggr_workflows.single_app <workflow>` from campaign_kb).
- **Embedding:** Would require mounting a Gradio/Daggr app inside Flask (e.g. via `gradio.mount_gradio_app` or similar). This adds process coupling, shared-memory concerns, and complicates deployment (one process vs many).

## Why redirect

1. **Separation of concerns:** campaign_kb Daggr workflows use `SessionLocal()`, app.config, and ObsidianVault scripts. Running them in a separate process avoids Flask/Gradio event-loop conflicts.
2. **Deployment flexibility:** Users can run Daggr on a different host/port. Set `CAMPAIGN_KB_DAGGR_URL` to point to the Daggr instance.
3. **Alignment with GRADIO_FRAMEWORK:** Per `.cursor/docs/GRADIO_FRAMEWORK.md`, "mounting in Flask" is optional; "link to Gradio URL" is documented. Redirect is the simpler pattern.
4. **Use Daggr for:** ingest, search, merge, rag (multi-node workflows). **Use gr.Blocks for:** single-block UIs like the Gradio demo (KB Search) at `/tools/gradio`.

## Configuration

| Env var | Purpose |
|---------|---------|
| `CAMPAIGN_KB_DAGGR_URL` | Redirect target for /tools/kb-daggr (default http://localhost:7860) |
| `GRADIO_APP_URL` | Redirect target for /tools/gradio (default http://localhost:7861) |

## Future options

If embedding becomes desirable (e.g. single-process deployment, shared auth):
- Use Gradio's `mount_gradio_app(flask_app, blocks, path="/tools/kb-daggr")`.
- Ensure campaign_kb and ObsidianVault scripts are on `sys.path` when Flask starts.
- Document any cwd/path requirements for the RAG workflow.
