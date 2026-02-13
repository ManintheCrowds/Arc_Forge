# Manual I/O Checklist — Workflow GUI

Repeatable, stepwise checklist for validating GUI I/O in the browser. Run from ObsidianVault; open http://127.0.0.1:5050.

Wizard flow available via toggle; auto-refresh optional. Use wizard for guided step-by-step; standard view for free navigation.

## Nine steps (Task 3)

| Step | Action | Expected |
|------|--------|----------|
| 1 | **Load:** Open `/` | CSS/JS load; arc selector and pipeline visible; tree/encounters load if any. |
| 2 | **S1:** Run Stage 1 for an arc with storyboard under `Campaigns/_rag_outputs/` | task_decomposition appears; tree/artifacts update; out-s1 shows success. |
| 3 | **Task decomp form:** Load arc with task_decomposition, edit, Save | Form reflects file; reload shows changes. |
| 4 | **S2:** Run Stage 2 | Encounter drafts under `encounters/` (and opportunities/ if any); tree/artifacts update. |
| 5 | **Feedback form:** Load arc, select encounter, add/remove/edit feedback, Save | `{arc_id}_feedback.yaml` updated; reload shows data. |
| 6 | **S4:** Pick draft from dropdown, Run Refine (feedback file present) | New `_draft_vN.md`; tree/artifacts refresh. |
| 7 | **S5:** Run Export | Expanded storyboard, JSON, campaign_kb file; out-s5 shows paths. |
| 8 | **File view:** Click encounter in tree | Content opens, or "Not found" for missing file. |
| 9 | **Provenance:** Encounters list | Shows "draft vN" and "from {arc}_feedback.yaml" where applicable. |

**Reference:** Audit plan §3.2; [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md) Task 3.

---

## Optional: Session memory

| Step | Action | Expected |
|------|--------|----------|
| 10 | **Archivist:** Enter path to session note (with Session Summary block), Run Archivist | Status success; output in `Campaigns/_session_memory/YYYY-MM-DD_archivist.md`; result shows output_path. |
| 11 | **Foreshadow:** Enter path to archivist output (or dropdown), Run Foreshadow | Status success; threads.md updated; result shows output_path. |

---

## Workbench (Phase 3)

| Step | Action | Expected |
|------|--------|----------|
| W1 | **Load Workbench:** Switch to Workbench tab, select campaign/module | Module selector populated; tree shows notes; right/bottom tabs visible. |
| W2 | **Note editor:** Click a note in the tree | Note loads in editor; Save, Toggle preview, Save as card work. |
| W3 | **Create module:** Enter campaign + module name, click Create module | Dirs and stub files created; tree refreshes. |
| W4 | **Workflow:** Open Workflow tab, select a node, click Run selected node | Stage runs; output or error shown. |
| W5 | **Idea Web / Dependencies:** Open bottom tabs | Graph shows nodes/edges from tags+wikilinks or depends_on; or empty if no data. |
| W6 | **Chat:** Open Chat tab, send a message | Reply appears (requires Ollama); or 503 if Ollama down. |
