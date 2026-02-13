# UI Pending Action Items — Task Decomposition

**Purpose:** Consolidated task breakdown for all pending workflow_ui UI work. Sources: [WORKBENCH_NOT_IMPLEMENTED.md](WORKBENCH_NOT_IMPLEMENTED.md), [UX_BACKLOG_TRIAGED.md](UX_BACKLOG_TRIAGED.md), [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md).

**Status legend:** Quick (~1h), Medium (~2–4h), Larger (~1–2d)

---

## Summary: Pending by Source

| Source | Pending items |
|--------|---------------|
| Workbench | ~~RAG search, Idea Web, Timeline, Workflow, Module selector, Note editor, Chat, Dependencies~~ — Done (Phase 3) |
| UX backlog | ~~UW-4 through UW-10~~ — Done |
| Development plan | ~~In-app pipeline diagram, cross-links KB, schema validation~~ — Done |
| Remaining | UW-1 (link checklist), UW-2 (step numbers), UW-3 (actionable errors) — quick wins |

---

## 1. RAG Search (Workbench right panel) — ✅ Done

**Goal:** Workbench RAG tab calls `/api/kb/search` and displays results.

**Current:** Implemented. RAG input/button wired; `rag-search` → `/api/kb/search` → `rag-results`.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Re-enable `#rag-query` and `#rag-search` in index.html (remove `disabled`) | Quick | None |
| 2 | Add handler in main.js or new module: `rag-search` click → read `rag-query` → `GET /api/kb/search?query=...` → render into `rag-results` | Quick | None |
| 3 | Reuse `formatErr` from utils.js for error display; format results as list or pre (mirror kb.js logic) | Quick | Task 2 |
| 4 | Update placeholder text in index.html to remove "Not wired" once functional | Quick | Task 3 |

---

## 2. Module Selector (Workbench left panel) — ✅ Done

**Goal:** Campaign and module dropdowns populated; filters and tree functional.

**Current:** Implemented. Arc tree APIs; `module-campaign`, `module-select`, `module-tree` populated.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Add `GET /api/workbench/campaigns` returning `{ campaigns: [name, ...] }` (scan `Campaigns/` dirs) | Medium | None |
| 2 | Add `GET /api/workbench/modules?campaign=` returning `{ modules: [name, ...] }` (scan `Campaigns/{campaign}/`) | Medium | Task 1 |
| 3 | Add `GET /api/workbench/tree?campaign=&module=&type=&status=&tags=` returning tree structure (scenes, npcs, locations by frontmatter) | Larger | Task 2 |
| 4 | Populate `module-campaign` on load; `module-select` on campaign change; `module-tree` on module change | Medium | Tasks 1–3 |
| 5 | Wire filters: `filter-type`, `filter-status`, `filter-tags` → pass to tree API or filter client-side | Medium | Task 4 |
| 6 | Remove "Not wired" placeholder once functional | Quick | Task 5 |

---

## 3. Create Module (Workbench left panel) — ✅ Done

**Goal:** "Create module" button creates campaign/module dirs with starter files.

**Current:** Implemented. `POST /api/workbench/create-module`; `create-module-btn` wired.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Add `POST /api/workbench/create-module` body: `{ campaign, module, starting_scenes, starting_npcs }` | Medium | None |
| 2 | Backend: create `Campaigns/{campaign}/{module}/`; add stub scene/npc files per counts | Medium | Task 1 |
| 3 | Wire `create-module-btn` click → read form → POST → display result in `create-module-out` | Quick | Task 2 |
| 4 | Refresh module tree after create | Quick | Task 3, Module selector |

---

## 4. Note Editor (Workbench center) — ✅ Done

**Goal:** Select note from tree → load into editor; Save, Save as card, Toggle preview work.

**Current:** Implemented. Tree click → load; `PUT /api/arc/<id>/file/<path>`; save-card, preview.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Ensure `/api/arc/<id>/file/<path>` or equivalent can read notes under campaigns (path traversal safe) | Quick | None |
| 2 | Add `PUT /api/workbench/note` or `/api/arc/<id>/file/<path>` for saving (if not exists) | Medium | Task 1 |
| 3 | Wire `module-tree` click → load file content into `note-editor` | Medium | Module selector |
| 4 | Wire `save-note` → PUT current content | Quick | Task 2, 3 |
| 5 | Wire `toggle-preview` → show/hide `note-preview`; render markdown (e.g. marked.js or existing lib) | Medium | Task 3 |
| 6 | Wire `save-card` → extract/save as card format (define card schema) | Larger | Task 4 |
| 7 | `citations-block`: placeholder until RAG inline citations spec exists | Quick | — |

---

## 5. Idea Web (Workbench bottom panel) — ✅ Done

**Goal:** Graph of notes by tags and wikilinks.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Define data source: frontmatter `tags`, `[[wikilinks]]`; document in Campaigns | Quick | None |
| 2 | Add `GET /api/workbench/idea-web?campaign=&module=` returning `{ nodes: [{id,label,type,tags}], edges: [{from,to}] }` | Medium | Task 1 |
| 3 | Client: parse markdown for `[[links]]`; aggregate with tags | Medium | Task 2 |
| 4 | Render graph (D3, vis.js, or Mermaid) in `#bottom-idea-web` | Medium | Task 3 |
| 5 | Update placeholder with "Coming soon" or functional UI | Quick | Task 4 |

---

## 6. Timeline (Workbench bottom panel) — ✅ Done

**Goal:** Chronological list of notes by frontmatter date.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Define frontmatter: `date`, `session_date`, or `timeline_order`; document in Campaigns | Quick | None |
| 2 | Add `GET /api/workbench/timeline?campaign=&module=` returning `[{ path, date, title, ... }]` sorted | Medium | Task 1 |
| 3 | Render list in `#bottom-timeline` (collapsible by date/session) | Medium | Task 2 |
| 4 | Update placeholder | Quick | Task 3 |

---

## 7. Dependencies (Workbench bottom panel) — ✅ Done

**Goal:** Graph from `depends_on` or similar frontmatter.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Define frontmatter: `depends_on: [id, ...]` or equivalent | Quick | None |
| 2 | Add `GET /api/workbench/dependencies?campaign=&module=` returning nodes+edges | Medium | Task 1 |
| 3 | Render graph (reuse Idea Web renderer if possible) | Medium | Task 2, Idea Web |
| 4 | Update placeholder | Quick | Task 3 |

---

## 8. Workflow (Workbench right panel) — ✅ Done

**Goal:** Visual workflow graph; select node → "Run selected node" invokes stage.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Define node→action mapping (Brainstorm→?, Outline→frame, SceneDraft=S2, etc.) | Medium | gui_spec |
| 2 | Render Mermaid graph in `#workflow-graph` | Medium | Task 1 |
| 3 | Implement selection: click node → store `selectedNode`; "Run selected node" calls stage API | Medium | Task 2 |
| 4 | Re-enable `run-workflow-node` button; remove "Not implemented" text | Quick | Task 3 |

---

## 9. Chat (Workbench right panel, full) — ✅ Done

**Goal:** Per-note or per-folder chat with context (RAG, session memory).

**Current:** Implemented. `POST /api/workbench/chat`; Ollama; context from active note.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Define scope: per-note vs per-folder; context injection (current note, RAG results) | Medium | None |
| 2 | Add backend: `POST /api/workbench/chat` body: `{ message, context_path?, rag_query? }`; LLM call with context | Larger | Task 1 |
| 3 | Wire chat-send → POST → append response to `chat-history` | Medium | Task 2 |
| 4 | Persist history (optional): localStorage or backend | Medium | Task 3 |

---

## 10. UW-4: Copy/scroll for file modal (Legacy) — ✅ Done

**Goal:** Long file content scrollable and copyable.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Add Copy button to modal header; click → `navigator.clipboard.writeText(modalContent)` | Quick | None |
| 2 | Ensure `.modal-content` has `overflow: auto`, `max-height` (e.g. 70vh) in style.css | Quick | None |

---

## 11. UW-5: "Not found" suggestions (Legacy) — ✅ Done

**Goal:** 404 file view shows contextual hint.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | In `viewFile` (files.js), when 404: map `relPath` to hint (encounters→"Run S2", task_decomposition→"Run S1", etc.) | Quick | None |
| 2 | Pass hint to `showFileModal(..., note: hint)` | Quick | Task 1 |

---

## 12. UW-6: Session memory path guidance (Legacy) — ✅ Done

**Goal:** Archivist path dropdown like Foreshadow.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Extend `/api/session/files` or add endpoint to list `_session_memory/` dir | Quick | None |
| 2 | Populate `session-archivist-path` dropdown (or add new dropdown) from API | Medium | Task 1 |
| 3 | Allow manual override (current text input) | Quick | Task 2 |

---

## 13. UW-7: Cross-links to campaign_kb (Legacy) — ✅ Done

**Goal:** Feedback form NPC/location autocomplete from KB.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Identify feedback form fields for NPC/location IDs in forms.js | Quick | None |
| 2 | Add autocomplete: on focus/type → `GET /api/kb/search?query=...` → show dropdown | Medium | Task 1 |
| 3 | On select → fill field with KB id | Quick | Task 2 |

---

## 14. UW-8: Schema validation before save (Legacy) — ✅ Done

**Goal:** Validate task_decomposition and feedback before persist.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Load schemas from Campaigns/schemas (task_decomposition, feedback) | Medium | None |
| 2 | On Save click: validate in-memory form data against schema | Medium | Task 1 |
| 3 | If invalid: display field-level errors in `td-errors` / `fb-errors`; block persist | Quick | Task 2 |
| 4 | If valid: proceed with existing save logic | Quick | Task 3 |

---

## 15. UW-9: In-app pipeline diagram (Legacy) — ✅ Done

**Goal:** Mermaid pipeline visible in UI.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Extract Mermaid from workflow_diagrams.md (or define canonical diagram) | Quick | None |
| 2 | Ensure `#pipeline-strip-mermaid` or similar renders it (Mermaid already loaded) | Quick | Task 1 |
| 3 | Wire into onboarding or pipeline strip; verify render on load | Quick | Task 2 |

---

## 16. UW-10: Optional first-run flow (Legacy) — ✅ Done

**Goal:** Empty tree → "Get started" panel with steps; "Don't show again" checkbox.

### Task decomposition

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Detect empty tree (e.g. no arcs or arc has no files) | Quick | None |
| 2 | Show overlay or replace onboarding with "Get started" (3–4 steps) | Medium | Task 1 |
| 3 | Add "Don't show again" checkbox; persist to localStorage | Quick | Task 2 |
| 4 | On subsequent loads, if dismissed, skip overlay | Quick | Task 3 |

---

## Suggested implementation order

**Phase 1 — Quick wins:** ~~Done (RAG, UW-4, UW-5, UW-9)~~
**Phase 2 — Medium:** ~~Done (UW-6, UW-7, UW-8, Timeline, Module selector)~~
**Phase 3 — Larger:** ~~Done (Note editor, Idea Web, Dependencies, Workflow, Create module, Chat, UW-10)~~

**Remaining for Phase 3 Review:**
- UW-1: Link to manual I/O checklist
- UW-2: Step numbers on tabs
- UW-3: Actionable error messages
