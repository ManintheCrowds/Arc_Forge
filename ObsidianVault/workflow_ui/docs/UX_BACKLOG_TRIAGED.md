# UX Backlog (Triaged)

Prioritized UX improvements from [GUI_AUDIT_USER_INTEGRATION.md](GUI_AUDIT_USER_INTEGRATION.md) and post–Requires/Outputs review. Execute in suggested order.

**References:** [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md) §C, [manual_io_checklist.md](manual_io_checklist.md)

---

## Summary

| ID | Item | Effort | Priority | Suggested order |
|----|------|--------|----------|-----------------|
| UW-1 | Link to manual I/O checklist | Quick | P0 | 1 |
| UW-2 | Step numbers on tabs | Quick | P0 | 2 |
| UW-3 | Actionable error messages | Quick | P0 | 3 |
| UW-4 | Copy/scroll for file modal | Medium | P1 | 4 |
| UW-5 | "Not found" suggestions | Medium | P1 | 5 |
| UW-6 | Session memory path guidance | Medium | P1 | 6 |
| UW-7 | Cross-links to campaign_kb | Larger | P2 | 7 |
| UW-8 | Schema validation before save | Larger | P2 | 8 |
| UW-9 | In-app pipeline diagram | Larger | P2 | 9 |
| UW-10 | Optional first-run flow | Larger | P2 | 10 |

---

## Per-item entries

### UW-1: Link to manual I/O checklist

**Goal:** Users can open the manual I/O checklist from the onboarding block without leaving the app.

**Files:** [../templates/index.html](../templates/index.html) — onboarding block (lines 148–164)

**Done when:** Onboarding block contains a link to `docs/manual_io_checklist.md` or README; link opens in new tab.

**Implementation notes:** Add `<a href="..." target="_blank" rel="noopener noreferrer">`. If workflow_ui does not serve docs, add a Flask route (e.g. `/docs/<path>`) that serves files from `workflow_ui/docs/`, or link to README. Check app.py for existing doc-serving routes.

**Dependencies:** None.

---

### UW-2: Step numbers on tabs

**Goal:** Pipeline order (S1 → S5) is obvious at a glance.

**Files:** [../templates/index.html](../templates/index.html) — tab buttons (lines 178–182)

**Done when:** Stage tabs show step number (e.g. "S1 (1) Task Decomp" or "S1 — Step 1").

**Implementation notes:** Tab labels use `data-tab="s1"` etc.; change button text only. Keep `data-tab` unchanged for JS.

**Dependencies:** None.

---

### UW-3: Actionable error messages

**Goal:** When a stage fails, the user sees a concrete fix (e.g. where to put the storyboard).

**Files:** [../static/modules/utils.js](../static/modules/utils.js) (`formatErr`), [../static/modules/stages.js](../static/modules/stages.js) (out() calls), possibly [../app.py](../app.py) for structured error payloads

**Done when:** S1 failure shows "Storyboard not found. Ensure a storyboard exists under Campaigns/_rag_outputs/ (or pass a path)."; S2/S4 show similar prereq hints when relevant.

**Implementation notes:** Backend may return `error` or `reason`. Enhance `formatErr` or add stage-specific mapping (e.g. map "storyboard" / 404 → actionable message). Check app.py error responses for stage1/stage2/stage4.

**Dependencies:** None.

---

### UW-4: Copy/scroll for file modal

**Goal:** Long file content is scrollable and copyable.

**Files:** [../templates/index.html](../templates/index.html) (modal structure), [../static/modules/modal.js](../static/modules/modal.js) (`showFileModal`), [../static/style.css](../static/style.css)

**Done when:** File modal has Copy button and scrollable content area for long files.

**Implementation notes:** Modal uses `#file-modal-content` (pre). Add Copy button; ensure `.modal-content` has `overflow: auto` and `max-height`.

**Dependencies:** None.

---

### UW-5: "Not found" suggestions

**Goal:** When file view returns 404, user gets a hint on what to do next.

**Files:** [../static/modules/files.js](../static/modules/files.js) — `viewFile`, lines 14–17

**Done when:** When file returns 404, modal note suggests context (e.g. for `encounters/` path: "Run S2 to generate drafts").

**Implementation notes:** `showFileModal` accepts `note` param. Pass contextual hint based on `relPath` (e.g. if path contains "encounters" → "Run S2 to generate drafts"; if path contains "task_decomposition" → "Run S1 first").

**Dependencies:** None.

---

### UW-6: Session memory path guidance

**Goal:** Reduce typos and mis-paths when entering Archivist session note path.

**Files:** [../templates/index.html](../templates/index.html) (session-memory panel), [../static/modules/session.js](../static/modules/session.js) if exists, or [../static/modules/api.js](../static/modules/api.js)

**Done when:** Archivist path input has dropdown or prefill of existing `_session_memory/` files (like Foreshadow dropdown).

**Implementation notes:** Foreshadow already has `session-foreshadow-dropdown`; `/api/session/files` exists. Populate Archivist path dropdown from similar API or extend `/api/session/files` to list session memory dir contents.

**Dependencies:** None.

---

### UW-7: Cross-links to campaign_kb

**Goal:** Feedback UI supports NPC/location autocomplete from KB sources.

**Files:** [../static/modules/forms.js](../static/modules/forms.js), [../static/modules/kb.js](../static/modules/kb.js)

**Done when:** Feedback form fields for NPC/location IDs support selection/autocomplete from KB entries.

**Implementation notes:** Reference: DEVELOPMENT_PLAN_REMAINING §C. Requires `/api/kb/search` or similar; integrate into feedback form fields.

**Dependencies:** campaign_kb API must be reachable.

---

### UW-8: Schema validation before save

**Goal:** Task_decomposition and feedback validate against schema before persist; field-level errors shown.

**Files:** Forms module, validation logic; [../../Campaigns/schemas/](../../Campaigns/schemas/) for task_decomposition and feedback schemas

**Done when:** Save task_decomposition and feedback validates against schema; field-level errors shown in `td-errors` and `fb-errors` divs before persist.

**Implementation notes:** Schemas: `task_decomposition_example.yaml`, `task_decomposition_schema.md`, `feedback_example.yaml`, `feedback_schema.md`. `td-errors` and `fb-errors` divs exist.

**Dependencies:** None.

---

### UW-9: In-app pipeline diagram

**Goal:** Mermaid pipeline diagram visible in UI so users see the flow visually.

**Files:** [../../Campaigns/docs/workflow_diagrams.md](../../Campaigns/docs/workflow_diagrams.md) (source), [../templates/index.html](../templates/index.html), pipeline module

**Done when:** Mermaid diagram from workflow_diagrams.md rendered in UI (e.g. in onboarding or pipeline strip).

**Implementation notes:** App already loads Mermaid; `#pipeline-strip-mermaid` exists. Check workflow_diagrams.md for diagram format.

**Dependencies:** None.

---

### UW-10: Optional first-run flow

**Goal:** On first load (empty tree), show a short "Get started" panel with steps and "Don't show again" checkbox.

**Files:** [../templates/index.html](../templates/index.html), [../static/modules/state.js](../static/modules/state.js) or similar for localStorage

**Done when:** On first load (empty tree), show "Get started" panel with 3–4 steps and "Don't show again" checkbox; dismissed state stored in localStorage.

**Implementation notes:** Detect empty tree; use localStorage key for "dismissed"; overlay or replace onboarding temporarily.

**Dependencies:** None.

---

## Suggested order (for agents)

1. **UW-1, UW-2, UW-3** — quick wins
2. **UW-4, UW-5, UW-6** — medium effort
3. **UW-7–UW-10** — larger; can be done in parallel by different sessions

**Recommended next:** UW-1 (link to manual I/O checklist).
