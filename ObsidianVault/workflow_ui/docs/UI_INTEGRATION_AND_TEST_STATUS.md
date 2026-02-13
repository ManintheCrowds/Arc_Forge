# UI Integration and Test Status

**Purpose:** Single source of truth for workflow UI component coverage: integration matrix, gap analysis, render-state audit, and prioritized remaining work. Produced by Phase 3–4 review (workflow_ui_security_e2e_review plan).

**References:** [manual_io_checklist.md](manual_io_checklist.md), [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md), [UX_BACKLOG_TRIAGED.md](UX_BACKLOG_TRIAGED.md).

---

## 3.1 Integration matrix

Columns: UI component, Primary API(s), API tested, E2E tested, Manual I/O.

### Workbench components

| Component | API(s) | API | E2E | Manual |
|-----------|--------|-----|-----|--------|
| Module selector | `/api/modules`, `/api/workbench/campaigns`, `/api/workbench/modules`, `/api/modules/<c>/<m>/tree` | No | Via create-module | W1 |
| Note editor | `/api/modules/<c>/<m>/file/<path>` (workbench); Legacy uses `/api/arc/<id>/file/<path>` | Arc file: Yes; modules/file: No | Yes (note editor) | W2 |
| Create module | `POST /api/workbench/create-module` | Yes | Yes | W3 |
| Workflow | `/api/run/stage1–5` | Yes | Yes | W4 |
| Idea Web | `GET /api/workbench/idea-web` | Yes | No | W5 |
| Dependencies | `GET /api/workbench/dependencies` | Yes | No | W5 |
| Chat | `POST /api/workbench/chat` | Yes | No | W6 |
| Timeline | `GET /api/workbench/timeline` | No | No | (via W1) |
| RAG search | `GET /api/kb/search` | No | No | (in W5 area) |

### Legacy components

| Component | API(s) | API | E2E | Manual |
|-----------|--------|-----|-----|--------|
| Load/arcs | `/api/arcs`, `/api/arc/<id>/tree`, `/api/arc/<id>/artifacts` | Yes | Yes (load+S1) | 1 |
| S1 | `POST /api/run/stage1` | Yes | Yes | 2 |
| Task decomp form | `GET/PUT /api/arc/<id>/task_decomposition` | Yes | No | 3 |
| S2 | `POST /api/run/stage2` | Yes | Yes | 4 |
| Feedback form | `GET/PUT /api/arc/<id>/feedback` | Yes | No | 5 |
| S4 | `POST /api/run/stage4` | Yes | Yes | 6 |
| S5 | `POST /api/run/stage5` | Yes | Yes | 7 |
| File view | `GET /api/arc/<id>/file/<path>` | Yes | No | 8 |
| Provenance | (tree/artifacts) | Yes | No | 9 |

### Session memory

| Component | API(s) | API | E2E | Manual |
|-----------|--------|-----|-----|--------|
| Archivist | `POST /api/session/archivist` | Yes | No | 10 |
| Foreshadow | `POST /api/session/foreshadow` | Yes | No | 11 |

---

## 3.2 Gap analysis

### No API tests

- `/api/modules`, `/api/modules/<campaign>/<module>/tree`
- `/api/modules/<campaign>/<module>/file/<path>` (workbench file GET; note: arc file has tests)
- `/api/workbench/timeline`
- `/api/workbench/campaigns`, `/api/workbench/modules`
- `/api/kb/search` (requires campaign_kb; mock or skip)

### No E2E tests

- Task decomp form (edit, save)
- Feedback form (edit, save)
- File view (click encounter, content/Not found)
- Provenance display
- Session memory (Archivist, Foreshadow)
- Idea Web, Dependencies panels
- Chat panel
- RAG search panel

### Manual I/O coverage

All 20 steps (1–9, 10–11, W1–W6) are documented. No components lack a manual step.

---

## 4.1 Render-state audit

Placeholders, empty states, and hidden panels.

| Component | Condition | Expected behavior |
|-----------|-----------|-------------------|
| First-run overlay | `first_run_dismissed` not in localStorage | Shows; "Don't show again" hides it |
| Workspace views | `display: none` until tab clicked | Workbench or Legacy visible |
| Right panels | `right-panel` hidden until tab click | Chat, RAG, Workflow switch |
| Bottom panels | `bottom-panel` hidden until tab click | Timeline, Idea web, Dependencies |
| Note editor | No note selected | Placeholder: "Select a note to edit..." |
| Citations block | No citations | `#citations-block`: "No citations yet." |
| Note preview | Empty | `display: none` when empty |
| Module tree | Empty campaign | UW-10: "Get started" overlay or empty tree |
| Idea web / Dependencies | No data | "Loading…" → empty graph or "No data" |
| Timeline | No notes with date | Empty list |

---

## 4.2 Prioritized remaining work

From Phase 3 gaps, Phase 4 audit, [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md), and [UX_BACKLOG_TRIAGED.md](UX_BACKLOG_TRIAGED.md).

### P0 (quick, high impact)

1. Add API tests for `/api/modules`, `/api/modules/<c>/<m>/tree` (workbench tree)
2. Add API test for `/api/workbench/timeline`
3. Verify manual I/O checklist alignment with wizard/auto-refresh (DEVELOPMENT_PLAN §A)

### P1 (medium)

4. E2E: Task decomp form, feedback form, file view (Legacy steps 3, 5, 8)
5. E2E: Idea Web, Dependencies, Chat (Workbench W5, W6)
6. API test for `/api/modules/<campaign>/<module>/file/<path>` (workbench file GET)

### P2 (docs / UX backlog)

7. OpenAPI `/docs` mention in README
8. Remaining UX backlog items (UW-7 cross-links, UW-8 schema validation, etc.)

---

## Test counts (reference)

- **API tests:** ~55 in [test_api.py](../tests/test_api.py)
- **E2E tests:** 7 in [test_e2e_playwright.py](../tests/test_e2e_playwright.py)
