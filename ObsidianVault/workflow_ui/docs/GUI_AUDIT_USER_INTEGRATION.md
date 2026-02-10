# GUI Audit — User Integration (Second Workflow)

SME/user-integration audit of workflow_ui. Goal: how effectively a new user (GM) gets integrated—first-run experience, clarity of value, and paths to repeated use. Produced per plan [gui_audit_second_workflow](D:\CodeRepositories\.cursor\plans\gui_audit_second_workflow_8c8283f9.plan.md); input pack and reusable prompt in [GUI_AUDIT_PROMPT.md](GUI_AUDIT_PROMPT.md).

---

## Summary

The workflow_ui delivers a single dashboard that matches the backend contract (S1–S5, task decomp, feedback, KB, session memory) and supports users who already know the pipeline. **User integration is moderate:** a motivated GM can complete a full run using the manual I/O checklist or docs, but the first-run experience does not clearly communicate purpose, prerequisites, or next step. There is no in-app onboarding, and several barriers (no empty-state guidance, dense tab set, file view in alert) increase the risk of drop-off before first value. Top improvements: a visible “Getting started” or first-run hint, clearer pipeline order in the tab layout or labels, and in-context help (e.g. tooltips or one-line “what this does”) on each stage panel.

---

## Findings by category

### 1. First-run / empty state

- **Observation:** On load, the user sees arc dropdown (default `first_arc`), pipeline badges, and a tab strip. There is no welcome text, no “what is this” or “get started,” and no indication that a storyboard must exist (e.g. under `Campaigns/_rag_outputs/`) for S1 to succeed.
- **Impact:** High. New users may not know the pipeline order (S1 → … → S5) or that they must have a storyboard before running S1. Empty arc tree and “(no files)” do not explain what to do first.

### 2. Information hierarchy

- **Observation:** Primary actions (Run Stage 1, Run Stage 2, etc.) are clear per panel. Tabs are flat: Campaign KB, S1–S5, Session memory, Edit Task Decomp, Edit Feedback. Pipeline order is not visually emphasized in the tab order (e.g. S3 is “Feedback” between S2 and S4), and “Edit Task Decomp” / “Edit Feedback” are separate from S1/S3 panels, which can blur primary vs editing flows.
- **Impact:** Medium. Hierarchy is adequate for someone who knows the workflow; for new users, the equal weight of nine tabs makes the critical path (S1 → edit decomp → S2 → edit feedback → S4 → S5) less obvious.

### 3. Progressive disclosure

- **Observation:** Panels are hidden until the user switches tabs; each stage panel is a short blurb + button + output area. Complexity is mostly deferred to the forms (task decomp, feedback). Campaign KB and Session memory are optional and grouped in tabs, which is good. No wizard or step-by-step flow—user must know to open S1 first, then S2, etc.
- **Impact:** Medium. Disclosure is reasonable once the user knows the sequence; the missing piece is revealing that sequence progressively (e.g. “Start with S1” or a simple wizard).

### 4. Feedback and state

- **Observation:** Run buttons show “Running…” and are disabled during requests; output areas show success/error. Pipeline badges update when artifacts exist (green). Dirty-form warnings on task decomp and feedback prevent accidental tab switch. File view uses an alert for content (or “Not found”), which is functional but not ideal for long text.
- **Impact:** Low–Medium. Feedback and state are present and adequate for integration; the main gap is that errors (e.g. “storyboard not found” for S1) may not always point the user to a concrete fix (e.g. “Ensure a storyboard exists under Campaigns/_rag_outputs/”).

### 5. Onboarding and help

- **Observation:** No in-app tour, tooltips, or “Getting started” link. README and gui_spec exist in the repo; manual_io_checklist is in docs. Campaign KB panel states that campaign_kb must be running; S3 panel states “edit feedback in Edit Feedback.” No per-stage “what this does” or “you need X before running.”
- **Impact:** High. Onboarding is entirely outside the UI (docs, checklist). A new user inside the app has no in-context guidance to reach first value.

### 6. Barriers to integration

- **Observation:** (a) Unclear first step (no storyboard? no arc?); (b) Prerequisites not surfaced (storyboard path, ingest_config.json, campaign_kb for KB/RAG); (c) Many tabs with no suggested order; (d) File content in alert limits readability; (e) Session memory paths are free-text (easy to typo or mis-path).
- **Impact:** High for (a)–(c); medium for (d)–(e). Combined, they increase the chance a new user abandons before completing one full pipeline run.

---

## Recommendations

| Priority | Recommendation |
|----------|----------------|
| **Quick win** | Add a short “Getting started” line or collapsible block at the top of the main content (or under the pipeline strip): e.g. “Start with S1 Task Decomp (requires a storyboard under Campaigns/_rag_outputs/). Then edit task decomposition, run S2, edit feedback, run S4 per encounter, then S5 Export.” Link to manual_io_checklist or README. |
| **Quick win** | On each stage panel (S1–S5), add one line of in-context help: e.g. S1 “Requires storyboard in Campaigns/_rag_outputs/ or passed path”; S2 “Uses task_decomposition and storyboard; needs ingest_config.json”; S4 “Pick a draft and ensure feedback is saved.” |
| **Medium** | Reorder or group tabs to reflect pipeline order: e.g. “Pipeline: S1 → S2 → S3 → S4 → S5” as a group, then “Forms: Task Decomp, Feedback,” then “Campaign KB,” “Session memory.” Or add a small “1–5” or “Step N” label on stage tabs. |
| **Medium** | Replace file-content alert with a modal or side panel that shows encounter/file content (with scroll and optional copy), and “Not found” with a short suggestion (e.g. “Run S2 to generate drafts”). |
| **Larger change** | Optional first-run flow: on first load (e.g. no arc or empty tree), show a single “Get started” panel with 3–4 steps (e.g. “1. Ensure storyboard exists. 2. Select arc. 3. Run S1. 4. Open Edit Task Decomp.”) and a “Don’t show again” checkbox. |
| **Larger change** | Add a “Prerequisites” or “Setup” section (collapsible) listing: storyboard location, ingest_config.json, campaign_kb URL (for KB/RAG), and optional session memory paths. |

---

## Assumptions

- Audit based on code and docs (templates, app.js, gui_spec, manual_io_checklist). No live screenshots or session with a real first-time user.
- User is assumed to have started the app (e.g. via README or launcher) and has basic familiarity with “arc” and “storyboard” concepts from the Wrath & Glory stack.
- Campaign KB and Session memory are secondary to the core S1–S5 pipeline for this integration criterion; improving their in-context help is still recommended.

---

## Checklist (scores 1–5)

| Category | Score | One-line finding |
|----------|-------|-------------------|
| First-run / empty state | 2 | No welcome or first-step guidance; purpose and prerequisites unclear. |
| Information hierarchy | 3 | Primary actions clear per panel; tab set is flat and pipeline order not emphasized. |
| Progressive disclosure | 3 | Panels hide until selected; no guided sequence or wizard. |
| Feedback and state | 4 | Running state, success/error, dirty-form warnings present; error messages could be more actionable. |
| Onboarding and help | 2 | No in-app help or tooltips; docs exist outside UI. |
| Barriers to integration | 2 | Unclear first step and prerequisites; many tabs; file view in alert. |

**Integration readiness (1–5):** **3** — A motivated GM with docs can integrate; typical first-time user would benefit from in-app guidance and clearer pipeline order.

**Top 3 changes to improve integration**

1. **Add a visible “Getting started” hint** (or collapsible block) that states the pipeline order and the S1 prerequisite (storyboard), with a link to the manual I/O checklist or README.
2. **Add one-line in-context help** on each S1–S5 panel (what’s needed before running, what the step produces).
3. **Emphasize pipeline order in the UI** (tab order, labels, or grouping) so the critical path S1 → … → S5 is obvious at a glance.
