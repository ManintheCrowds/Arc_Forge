# PURPOSE: Gradio UI for workflow_ui (KB search demo). Runs standalone; calls workflow_ui /api/kb/search.
# DEPENDENCIES: gradio>=4.0.0; requests (optional, for calling Flask app).
# MODIFICATION NOTES: Per GRADIO_FRAMEWORK and gradio_adoption_workflow_ui.plan.md.

"""
Gradio app for workflow_ui: Campaign KB Search and optional tool demos.
Launch standalone: python -m workflow_ui.gradio_app (from ObsidianVault).
Then open /tools/gradio in the Flask app (redirects here) or http://localhost:7861.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request


def _kb_search_via_flask(query: str, limit: int, source_name: str) -> str:
    """Call workflow_ui Flask /api/kb/search. Returns markdown or error message."""
    base = os.environ.get("WORKFLOW_UI_URL", "http://127.0.0.1:5050").rstrip("/")
    params = {"query": (query or "").strip(), "limit": limit or 20}
    if (source_name or "").strip():
        params["source_name"] = source_name.strip()
    url = f"{base}/api/kb/search?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode()
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            return f"**API error {e.code}**\n\n{body or e.reason}"
        except Exception:
            return f"**API error {e.code}**\n\n{e.reason}"
    except OSError as e:
        return f"**Connection error**\n\nIs the workflow_ui Flask app running at {base}? {e}"
    try:
        obj = json.loads(data)
        if "error" in obj:
            return f"**Error**\n\n{obj.get('error', data)}"
        sections = obj.get("sections") or obj.get("results") or []
        if not sections:
            return "No sections matched."
        lines = []
        for i, item in enumerate(sections[: int(limit or 20)], 1):
            if isinstance(item, dict):
                text = item.get("normalized_text") or item.get("text") or ""
                title = item.get("document_title") or item.get("title") or "—"
                source = item.get("source_name") or item.get("source") or "—"
                lines.append(f"### {i}. {title} ({source})\n{text[:500]}...")
            else:
                lines.append(str(item))
        return "\n\n".join(lines) if lines else "No sections matched."
    except Exception as e:
        return f"**Parse error**\n\n{e}\n\nRaw: {data[:500]}"


def _workflow_demo_instructions() -> str:
    """Return markdown instructions for running campaign_kb workflows (no backend call)."""
    base = os.environ.get("CAMPAIGN_KB_DAGGR_URL", "http://localhost:7860").rstrip("/")
    return f"""## Workflow demo (quick reference)

**Campaign KB workflows** (ingest, search, merge) run in a separate Daggr app. Use the main app header link **KB Workflows** to open them, or run manually:

- **Ingest:** `python -m daggr_workflows.run_workflow ingest` (from campaign_kb root)
- **Search:** `python -m daggr_workflows.run_workflow search`
- **Merge:** `python -m daggr_workflows.run_workflow merge`

Daggr UI (if running): **{base}**

*This screen is for quick reference only. Full workflow UIs are in the main app and campaign_kb.*"""


def create_blocks():
    """Build Gradio Blocks app: KB Search + Workflow demo tabs. No Daggr; single-block UIs per GRADIO_FRAMEWORK."""
    import gradio as gr

    with gr.Blocks(title="Workflow UI – Gradio", css="footer {visibility: hidden}") as blocks:
        gr.Markdown("## Workflow UI – Gradio\nUse the tabs below: **Campaign KB Search** or **Workflow demo** (quick reference).")
        with gr.Tabs():
            with gr.TabItem("Campaign KB Search"):
                gr.Markdown("Uses the same backend as the main app: **workflow_ui** `/api/kb/search` (proxies to campaign_kb). Ensure the Flask app is running (e.g. `python -m workflow_ui.app` on port 5050).")
                with gr.Row():
                    query_in = gr.Textbox(label="Query", placeholder="e.g. tier 2 requisition", lines=2)
                    limit_in = gr.Number(label="Limit", value=20, minimum=1, maximum=100)
                    source_in = gr.Textbox(label="Source name (optional)", value="", lines=1)
                btn = gr.Button("Search")
                out = gr.Markdown(label="Results")
                btn.click(
                    fn=_kb_search_via_flask,
                    inputs=[query_in, limit_in, source_in],
                    outputs=out,
                )
                gr.Markdown("---\n*For full ingest/merge workflows, use KB Workflows in the main app (header link).*")
            with gr.TabItem("Workflow demo"):
                gr.Markdown("Quick reference for running campaign_kb Daggr workflows. No backend call.")
                demo_btn = gr.Button("Show instructions")
                demo_out = gr.Markdown(label="Instructions")
                demo_btn.click(
                    fn=_workflow_demo_instructions,
                    inputs=[],
                    outputs=demo_out,
                )
        gr.Markdown("---\nConventions: `.cursor/docs/GRADIO_FRAMEWORK.md`")
    return blocks


def main():
    import gradio as gr
    port = int(os.environ.get("GRADIO_PORT", "7861"))
    blocks = create_blocks()
    blocks.launch(server_name="127.0.0.1", server_port=port, share=False)


if __name__ == "__main__":
    main()
