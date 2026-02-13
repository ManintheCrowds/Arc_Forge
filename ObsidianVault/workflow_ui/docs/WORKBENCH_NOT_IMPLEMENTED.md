# Workbench Implementation Status

**Purpose:** Document what is implemented vs. not implemented in the Workbench view. Reference: [narrative_workbench_spec.md](../../Campaigns/docs/narrative_workbench_spec.md), [gui_spec.md](../../Campaigns/docs/gui_spec.md).

**Context:** The Workbench is the default view (Workbench / Legacy workflow tabs). The Legacy workflow (S1–S5 pipeline) is fully implemented. Phase 3 implementation is complete: module selector, note editor, workflow graph, Idea Web, Dependencies, Chat, Timeline, RAG search, and create module are all wired.

---

## Summary: What Works vs. What Doesn't

| Area | Status | Notes |
|------|--------|-------|
| Legacy workflow | ✅ Implemented | S1–S5, arc tree, KB, session memory, forms |
| Workspace tabs | ✅ Implemented | Workbench ↔ Legacy switching |
| Right tabs (Chat/RAG/Workflow) | ✅ Implemented | Panels switch when clicked |
| Bottom tabs (Timeline/Idea web/Dependencies) | ✅ Implemented | Panels switch when clicked |
| Idea Web | ✅ Implemented | `GET /api/workbench/idea-web`, graph from tags + wikilinks |
| Timeline | ✅ Implemented | `GET /api/workbench/timeline`, frontmatter date ordering |
| RAG search | ✅ Implemented | `rag-search` → `/api/kb/search` → `rag-results` |
| Workflow | ✅ Implemented | Mermaid graph, node selection, Run selected node → stage APIs |
| Module selector | ✅ Implemented | campaign/module, tree, filters via `/api/workbench/*` |
| Note editor | ✅ Implemented | tree click → load, save, preview, save-card; `PUT /api/arc/<id>/file/<path>` |
| Chat | ✅ Implemented | `POST /api/workbench/chat`, Ollama, context from active note |
| Dependencies | ✅ Implemented | `GET /api/workbench/dependencies`, graph from `depends_on` |
| Create module | ✅ Implemented | `POST /api/workbench/create-module`, dirs + stub files |

---

## Idea Web

**Location:** Bottom panel, `#bottom-idea-web`; tab `data-bottom="idea-web"`.

**Current state:** ✅ Implemented. `GET /api/workbench/idea-web?campaign=&module=` returns nodes/edges from tags + `[[wikilinks]]`. `idea_web.js` renders graph in `#bottom-idea-web`.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Wire bottom-tabs so Idea Web panel is visible when clicked | Quick | None |
| 2 | Define data source: notes with frontmatter `tags` + `[[links]]`; API or static scan of Campaigns | Medium | Campaigns structure |
| 3 | Add API: `GET /api/workbench/idea-web?campaign=&module=` returning `{ nodes: [{id,label,type,tags}], edges: [{from,to}] }` | Medium | Task 2 |
| 4 | Render graph client-side (e.g. D3, vis.js, or Mermaid) | Medium | Task 3 |
| 5 | Replace placeholder with "Not implemented. Coming soon." or similar until Task 4 done | Quick | None |

---

## Timeline

**Location:** Bottom panel, `#bottom-timeline`; tab `data-bottom="timeline"`.

**Current state:** ✅ Implemented. `GET /api/workbench/timeline?campaign=&module=` returns notes sorted by frontmatter `date`. Client renders timeline list.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Wire bottom-tabs so Timeline panel is visible when clicked | Quick | None |
| 2 | Define frontmatter schema: `date`, `session_date`, or `timeline_order`; document in Campaigns | Quick | None |
| 3 | Add API: `GET /api/workbench/timeline?campaign=&module=` returning `[{ path, date, title, ... }]` sorted by date | Medium | Task 2 |
| 4 | Render timeline list (collapsible by date/session) | Medium | Task 3 |
| 5 | Replace placeholder with "Not implemented. Coming soon." until Task 4 done | Quick | None |

---

## RAG Search

**Location:** Right panel, `#right-rag`; tab `data-right="rag"`. Elements: `#rag-query`, `#rag-search`, `#rag-results`.

**Current state:** ✅ Implemented. `rag-search` click → `GET /api/kb/search?query=...` → render into `rag-results`. Reuses `formatErr` from utils.js.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Wire right-tabs so RAG panel is visible when clicked | Quick | None |
| 2 | Add handler: `rag-search` click → read `rag-query` → `GET /api/kb/search?query=...` → render into `rag-results` | Quick | `/api/kb/search` exists |
| 3 | Reuse `formatErr` and display logic from kb.js or extract shared helper | Quick | Task 2 |
| 4 | Optionally scope by campaign/module when workbench module selector is wired | Medium | Module selector |

---

## Workflow

**Location:** Right panel, `#right-workflow`; tab `data-right="workflow"`. Elements: `#workflow-graph`, `#run-workflow-node`.

**Current state:** ✅ Implemented. Mermaid graph in `#workflow-graph`; node selection via Mermaid click callbacks; "Run selected node" invokes S1/S2/S4/S5 stage APIs.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Wire right-tabs so Workflow panel is visible when clicked | Quick | None |
| 2 | Define node→action mapping: e.g. Brainstorm=S1, Outline=frame, SceneDraft=S2, etc. | Medium | gui_spec, narrative_workbench_spec |
| 3 | Render graph (Mermaid or similar; Mermaid already loaded) | Medium | Task 2 |
| 4 | Implement selection: click node → store selected; "Run selected node" calls stage API | Medium | Task 3 |
| 5 | Replace placeholder with "Not implemented. Use Legacy workflow for now." until Task 4 done | Quick | None |

---

## Other Workbench Gaps (Brief)

- ~~**Right tabs / Bottom tabs:**~~ Done. `initRightTabs()`, `initBottomTabs()` in main.js.
- ~~**Module selector:**~~ Done. `workbench.js` populates `module-campaign`, `module-select`, `module-tree` via arc tree APIs.
- ~~**Create module:**~~ Done. `POST /api/workbench/create-module`; `create-module-btn` wired in workbench.js.
- ~~**Note editor:**~~ Done. Tree click → load; `save-note`, `save-card`, `toggle-preview`; `PUT /api/arc/<id>/file/<path>`; `citations-block` placeholder.
- ~~**Chat:**~~ Done. `POST /api/workbench/chat` with Ollama; context from `data-active-note-path`.
- ~~**Dependencies:**~~ Done. `GET /api/workbench/dependencies`; graph from `depends_on` frontmatter.

---

## Suggested Implementation Order

1. ~~**Wire right-tabs and bottom-tabs**~~ — Done.
2. ~~**RAG search**~~ — Done.
3. ~~**Timeline**~~ — Done.
4. ~~**Idea Web**~~ — Done.
5. ~~**Workflow**~~ — Done.
6. ~~**Module selector, Note editor, Create module, Chat, Dependencies**~~ — Done (Phase 3).

---

## References

- [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md)
- [UX_BACKLOG_TRIAGED.md](UX_BACKLOG_TRIAGED.md)
- [narrative_workbench_spec.md](../../Campaigns/docs/narrative_workbench_spec.md)
- [gui_spec.md](../../Campaigns/docs/gui_spec.md)
