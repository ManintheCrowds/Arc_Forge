# GUI Audit — Reusable Prompt and Input Pack

Second-workflow artifact: audit brief (Step 1), input pack (Step 4), and composed prompt (Steps 2, 3, 6) for SME/user-integration audits of workflow_ui. Use this to re-run the audit (e.g. third workflow) with one copy-paste.

---

## 1. Audit brief (Step 1)

**Auditor persona:** Senior UX auditor with focus on adoption and first-run experience. Secondary persona: TTRPG Game Master (GM) who will use the tool for campaign prep—storyboard to encounter pipeline and optional session memory.

**Success criterion for "user integrated":** The user has completed at least one meaningful workflow without external help and has a clear intent to return. Concretely: (a) completed a full S1→S5 run for an arc (or equivalent: e.g. S1 + task decomp edit + S2 + feedback edit + S4 + S5), or (b) completed a focused path (e.g. Campaign KB search + ingest, or Session memory Archivist → Foreshadow) and understands where the outputs live and how to repeat. Evaluation lens: first meaningful workflow completed and intent to return.

---

## 2. Input pack (Step 4)

### (a) UI walkthrough (text)

- **Load:** User opens http://127.0.0.1:5050. Single-page app loads: header with title "Storyboard → Encounter Workflow", arc dropdown (default "first_arc"), and pipeline strip (badges: Storyboard, S1, S2, S3, S4, S5; Mermaid diagram when available). Left sidebar: "Arc file-tree" (list of files in current arc), "Encounters (with provenance)" (links to encounter/opportunity files). Main content: tab row (Campaign KB, S1 Task Decomp, S2 Drafts, S3 Feedback, S4 Refine, S5 Export, Session memory, Edit Task Decomp, Edit Feedback); one panel visible at a time.
- **Campaign KB tab:** KB status (— until "Check" clicked), search input + button, results area; Ingest PDFs (optional path), Merge seed doc button; requires campaign_kb running on port 8000.
- **S1 tab:** Short blurb; "Run Stage 1" button; output area (out-s1). Uses storyboard_path, arc_id, output_dir from backend.
- **S2 tab:** Blurb; "Run Stage 2" button; out-s2. Task decomposition + storyboard → encounter drafts (RAG + campaign).
- **S3 tab:** Human-only; points to "Edit Feedback"; out-s3.
- **S4 tab:** Draft dropdown (encounter .md), "Refine this encounter" button; draft and feedback path default from arc; out-s4.
- **S5 tab:** "Export final specs" button; out-s5.
- **Session memory tab:** Archivist path input + "Run Archivist"; Foreshadow dropdown + path input + "Run Foreshadow"; outputs to `Campaigns/_session_memory/` (e.g. `YYYY-MM-DD_archivist.md`, `threads.md`); out-session-memory.
- **Edit Task Decomp tab:** arc_id, storyboard_ref; Encounters list (+ Encounter), Opportunities (+ Opportunity), Sequence constraints (+ Constraint); "Save task_decomposition.yaml". Dirty-state warning on tab switch.
- **Edit Feedback tab:** Encounter selector; feedback items list (+ Feedback item); "Save feedback.yaml". Dirty-state warning on tab switch.
- **Arc tree / encounters:** Clicking an encounter opens file content in an alert (or "Not found"). Pipeline badges show which stages have artifacts (green border when present).

### (b) User and primary task

**User:** TTRPG Game Master (Wrath & Glory). **Primary task:** Run the storyboard→encounter pipeline (S1–S5) for an arc and optionally use Campaign KB (search, ingest, merge) and Session memory (Archivist, Foreshadow).

### (c) Optional user flows

- **First-time (pipeline):** Open http://127.0.0.1:5050 → see arc dropdown and pipeline strip → select arc (e.g. first_arc) → open S1 Task Decomp → Run Stage 1 (if storyboard exists under Campaigns/_rag_outputs/) → see out-s1 success and arc tree update → open Edit Task Decomp → edit/save → open S2 Drafts → Run Stage 2 → see encounter drafts in tree and out-s2 → open Edit Feedback → add feedback, Save → open S4 Refine → pick draft, Refine → open S5 Export → Export final specs → see out-s5 paths.
- **First-time (KB):** Open Campaign KB tab → Check status → if campaign_kb up, Search or Ingest PDFs / Merge seed doc.

---

## 3. Composed prompt (Steps 2, 3, 6)

Copy the block below into an AI chat; then paste the **Input pack** (section 2 above) or attach screenshots. Request output in the format specified at the end.

```
You are a senior UX/product expert auditing a graphical user interface. Your goal is to analyze how effectively the software gets users integrated—first-time experience, onboarding, clarity of value, and paths to repeated use.

**Context (Wrath & Glory stack):** This UI is the primary DM (Game Master) interface for a Wrath & Glory TTRPG tool. It drives a storyboard→encounter workflow (stages S1–S5), task decomposition and feedback forms, optional Campaign KB (search, ingest, merge when campaign_kb is running), and session memory (Archivist, Foreshadow). Evaluate for a TTRPG GM; "integration" = first meaningful workflow completed and intent to return.

**What to analyze (six categories):**
1. **First-run / empty state** – What does a new user see? Is the purpose and next step obvious?
2. **Information hierarchy** – Can users quickly find primary actions vs secondary/settings?
3. **Progressive disclosure** – Is complexity revealed in steps, or is everything visible at once?
4. **Feedback and state** – Are loading, success, and errors clear? Do users know what just happened?
5. **Onboarding and help** – Is there in-context guidance, tooltips, or a clear "getting started" path?
6. **Barriers to integration** – What might block or confuse a new user before they get value?

**Output format:**
- **Summary** (2–3 sentences): Overall assessment for user integration.
- **Findings** by category above: specific observations + impact (e.g. High/Medium/Low).
- **Recommendations**: Prioritized (Quick win / Medium / Larger change) with one concrete suggestion each.
- **Assumptions**: What you had to assume; note if screenshots or flows would change the audit.
- **Checklist** (optional): Per category, score 1–5 (1 = blocks integration, 5 = supports it) + one-line finding; one **Integration readiness** score (1–5); **Top 3 changes** to improve integration.
```

---

## 4. Task decomposition (for agents and re-runs)

Discrete tasks to run a GUI audit (third workflow or later). Order respects dependencies; suggested files are for future AI agents.

| Task ID | Task | Inputs | Outputs | Depends on | Suggested files |
|---------|------|--------|---------|------------|-----------------|
| **T1** | **Write or refresh audit brief** | Persona and success-criterion notes | Section 1 (Audit brief) in this doc | — | [GUI_AUDIT_PROMPT.md](GUI_AUDIT_PROMPT.md), [GUI_AUDIT_USER_INTEGRATION.md](GUI_AUDIT_USER_INTEGRATION.md) |
| **T2** | **Build or refresh input pack** | Current UI state (code or screenshots) | Section 2 (Input pack): walkthrough, user+task, flows | — | [templates/index.html](../templates/index.html), [static/app.js](../static/app.js), [static/style.css](../static/style.css), [Campaigns/docs/gui_spec.md](../../Campaigns/docs/gui_spec.md) |
| **T3** | **Compose or reuse audit prompt** | Six categories, SME lens, output format | Section 3 (Composed prompt) block | T1 | [GUI_AUDIT_PROMPT.md](GUI_AUDIT_PROMPT.md) |
| **T4** | **Run audit (AI)** | Composed prompt + input pack (and optional screenshots) | Raw audit output (Summary, Findings, Recommendations, Assumptions, Checklist) | T2, T3 | — |
| **T5** | **Write audit report** | Raw audit output from T4 | `workflow_ui/docs/GUI_AUDIT_USER_INTEGRATION.md` with Summary, Findings, Recommendations, Assumptions, Checklist | T4 | [GUI_AUDIT_USER_INTEGRATION.md](GUI_AUDIT_USER_INTEGRATION.md) |
| **T6** | **Update dev plan** | Audit report, top 3 recommendations | One line under Source of truth in `DEVELOPMENT_PLAN_REMAINING.md` | T5 | [DEVELOPMENT_PLAN_REMAINING.md](DEVELOPMENT_PLAN_REMAINING.md) |

**Sequence:** T1 → T2 → T3 (can parallelize T1 and T2). Then T4 (run AI) → T5 (write report) → T6 (optional, update dev plan).

**Quick re-run (no brief/pack change):** Use existing sections 1–2 and 3; run T4 → T5 → T6.

---

## 5. Suggested files for future AI agents

When re-running the audit, extending the prompt, or implementing recommendations, agents should read these first.

| Purpose | Files |
|---------|--------|
| **Audit docs (this workflow)** | `workflow_ui/docs/GUI_AUDIT_PROMPT.md`, `workflow_ui/docs/GUI_AUDIT_USER_INTEGRATION.md` |
| **UI implementation** | `workflow_ui/templates/index.html`, `workflow_ui/static/app.js`, `workflow_ui/static/style.css` |
| **Backend and API** | `workflow_ui/app.py`, `workflow_ui/tests/test_api.py` |
| **Spec and data flow** | `ObsidianVault/Campaigns/docs/gui_spec.md`, `ObsidianVault/Campaigns/docs/workflow_diagrams.md`, `ObsidianVault/Campaigns/docs/narrative_workbench_spec.md` |
| **Manual validation** | `workflow_ui/docs/manual_io_checklist.md` |
| **Remaining work and audit link** | `workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md` |
| **Stack context** | `README.md` (repo root), `workflow_ui/README.md` |

**Paths relative to workflow_ui:** `../` = workflow_ui parent (ObsidianVault); `../../Campaigns/docs/` = ObsidianVault/Campaigns/docs.

---

## 6. How to re-run (third workflow)

1. Open this file and copy **section 3 (Composed prompt)** into your AI chat.
2. Paste or attach **section 2 (Input pack)**—or update the walkthrough/screenshots if the UI changed (task T2).
3. Run the model and save the response (T4). T4 writes raw audit output to `workflow_ui/docs/_audit_raw_output.md`; T5 reads that file and writes the formatted report to `workflow_ui/docs/GUI_AUDIT_USER_INTEGRATION.md`.
4. Create or update `workflow_ui/docs/GUI_AUDIT_USER_INTEGRATION.md` with the model output (T5).
5. Optionally update `DEVELOPMENT_PLAN_REMAINING.md` to reference the new audit and top 3 recommendations (T6).

For agent-driven runs: use the machine-parseable spec `workflow_ui/docs/gui_audit_tasks.yaml` and per-task instructions in `workflow_ui/docs/audit_tasks/` (T1_audit_brief.md … T6_update_dev_plan.md).
