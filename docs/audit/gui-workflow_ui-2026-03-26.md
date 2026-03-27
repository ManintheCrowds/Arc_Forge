# GUI audit — Arc_Forge `ObsidianVault/workflow_ui`

**Date:** 2026-03-26  
**Mode:** Read-only audit  
**Path:** `ObsidianVault/workflow_ui/`  
**Stack:** Flask, Jinja2, modular vanilla JS (`static/modules/*.js`), optional Gradio (`gradio_app.py`).  
**Non-goals:** `campaign_kb/` FastAPI service — API-only (no product HTML); see optional API-UX note in multi-repo playbook.

Default ports (from code/plans): Flask app via `python -m workflow_ui.app`; redirects use `GRADIO_APP_URL` (e.g. 7861), `CAMPAIGN_KB_DAGGR_URL` (e.g. 7860). Confirm in environment when running.

---

## 1. Server-rendered & tool routes (inventory)

| Path | Type | Main UI / behavior | Data / deps |
|------|------|-------------------|-------------|
| `/` | HTML | `templates/index.html` — KB Workflows / workbench entry | Static + client JS |
| `/guide/<filename>` | Markdown | Allowlisted docs only (`manual_io_checklist.md`, `WORKBENCH_NOT_IMPLEMENTED.md`) | Files under `workflow_ui/docs/` |
| `/tools/kb-daggr` | 302 | Redirect to `CAMPAIGN_KB_DAGGR_URL` | External Daggr UI |
| `/tools/gradio` | 302 | Redirect to `GRADIO_APP_URL` | Gradio app |
| `/tools/daggr-graphs` | HTML | `templates/daggr_graphs.html` — Daggr Hub, Mermaid | `data/daggr_schemas.json` via `_load_daggr_schemas()` |
| `/metrics` | Prometheus text | Metrics | `prometheus_client` |

**JSON API surface (drives UI):** Large set under `/api/*` in `app.py` (e.g. `/api/arcs`, `/api/modules`, `/api/arc/...`, `/api/run/stage*`, `/api/workbench/*`, `/api/session/*`, `/api/kb/*`, `/api/daggr/graph/...`) — lines 371–1183+ (`ObsidianVault/workflow_ui/app.py`).

**Client modules (representative):** `static/main.js`, `static/app.js`, `static/modules/workbench.js`, `wizard.js`, `pipeline.js`, `chat.js`, `modal.js`, `kb.js`, etc.

---

## 2. Critical user journeys

1. **Open app** — `/` loads; status arcs/modules via API.  
2. **Daggr Hub** — `/tools/daggr-graphs` → pick workflow → Mermaid graph → node click → `#daggr-node-card` (see E2E).  
3. **Campaign KB bridge** — `/tools/kb-daggr` redirect when Campaign KB Daggr is up.  
4. **Gradio demo** — `/tools/gradio` redirect when Gradio server running.  
5. **Workbench flows** — JS-driven: idea web, dependencies, chat, timeline (`/api/workbench/*`).  
6. **Arc editing** — Tree/file APIs + client editors (`/api/arc/...`, `static/modules/note_editor.js`, etc.).

---

## 3. Static pass

- **Errors:** `_error_response` / `_error_payload` helpers (`app.py` ~55–64).  
- **Security:** `serve_guide` uses filename allowlist (`app.py` ~361–367). Session file APIs resolve under `_session_memory`.  
- **a11y:** Jinja templates and dynamically built DOM require manual keyboard/ARIA review; Mermaid node interaction tested in E2E by role/selector, not full WCAG.

---

## 4. Visual & responsive

- Flask templates + custom JS: no shared design-token file like Tailwind; responsive behavior is per-template/CSS. Manual `sm/md/lg` check recommended for `index.html` and `daggr_graphs.html`.

---

## 5. Runtime pass

- **Browser:** Apply Browser Ready on `/tools/daggr-graphs` (Mermaid loads from CDN — E2E may skip on `.graph-error`).  
- **Dual server:** Gradio and Campaign KB redirects fail soft if downstream not running — document expected 502/connection errors for operators.

---

## 6. E2E alignment

| Area | Test | File |
|------|------|------|
| Index “KB Workflows” visible | `test_index_loads` | `tests/e2e/test_workflow_ui_playwright_smoke.py` |
| `/tools/kb-daggr` 302 | `test_tools_kb_daggr_redirect` | same |
| Daggr Hub graph + node card | `test_daggr_hub_loads_select_workflow_click_node_shows_card` | same (Mermaid CDN dependency) |

**Gaps (untested in cited E2E):** Full wizard/pipeline/stage runs, workbench chat, Gradio redirect in browser, arc file PUT flows, `/api/kb/search` from UI.

---

## 7. Issue list & backlog

| ID | Sev | Summary | Evidence |
|----|-----|---------|----------|
| WF-1 | P2 | Mermaid render depends on CDN; E2E may skip | `test_workflow_ui_playwright_smoke.py` ~64–68 |
| WF-2 | P2 | Many primary flows lack Playwright coverage | `static/modules/*` vs single E2E file |
| WF-3 | P3 | `index.html.bak` in templates — clarify if accidental ship risk | `templates/index.html.bak` |

**Backlog:** Add targeted E2E for one happy-path stage run; document required env vars for redirects in `README` or `docs/`; remove or gitignore `*.bak` in templates.

---

## Definition of done

- [x] Route/template/module inventory  
- [x] Journeys + API mapping  
- [x] E2E vs gap table  
- [x] Findings with file references  
- [ ] Full runtime screenshot pass (operator-owned when vault + services are up)  
