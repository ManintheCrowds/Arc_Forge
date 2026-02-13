# Next Steps — Orchestration (Single Reference)

One place for all tracks, phases, and task IDs. Full detail lives in track sections below or in linked specs.

**Fine-grained sub-steps:** [NEXT_STEPS_TASK_DECOMPOSED](NEXT_STEPS_TASK_DECOMPOSED.md) — each task ID broken into tickable sub-steps (e.g. A1.1–A1.3, A2.1–A2.5) with file references and done-when.

---

## Source-of-Truth Links

| What | Where |
|------|--------|
| **Narrative workbench** | [narrative_workbench_spec.md](narrative_workbench_spec.md) — Integration map and spec I–IX |
| **Phase 4 session memory** | Done: `session_ingest.run_archivist`, `run_foreshadowing`; see [README_workflow](../README_workflow.md) Post-session ingestion |
| **RAG** | [campaign_kb/campaign/05_rag_integration.md](../../campaign_kb/campaign/05_rag_integration.md), `scripts/rag_pipeline.py`, `scripts/ingest_pdfs.py` |
| **Workflow GUI** | [workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md](../../workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md), [gui_spec.md](gui_spec.md) |

---

## Phases and Task IDs (Summary)

| Phase | Task IDs | One-line goal |
|-------|----------|----------------|
| **Phase 0** | — | Single orchestration doc (this file); linked from README_workflow / integration map ✓ |
| **Phase 1** | C1, C2, A1 | Meta-prompt script + doc; Frame output format doc ✓ |
| **Phase 2** | A2, A3, A4 | Story Architect script; wire Frame → Stage 1; tests ✓ |
| **Phase 3** | B1, B2, B3, B4 | RAG chunk schema; ingestion tags; retrieval modes; prompt-side instruction (B1 ✓) |
| **Phase 4** | D1, D2, D3 | workflow_ui: Archivist/Foreshadow API + UI; Future work list. Track E = GUI backlog (no task IDs here) |

---

## Per-Track Task List (Summary)

### Track A: Frame (Story Architect)

| ID | Goal | Done when |
|----|------|-----------|
| A1 | Define Frame output format | [frame_output_format.md](frame_output_format.md) exists; ref’d from integration map or README_workflow ✓ |
| A2 | Story Architect script | `run_story_architect(...)` in e.g. `scripts/frame_workflow.py`; CLI runnable; output matches format ✓ |
| A3 | Wire Frame upstream of Stage 1 | README_workflow or spec describes order: Frame → Select+Expand → S1 ✓ |
| A4 | Tests | pytest with mocked `generate_text`; output has expected structure ✓ |

**Order:** A1 → A2 → A3 → A4 (A3 can be doc-only first).

---

### Track B: RAG Chunk Tags and Retrieval Modes

| ID | Goal | Done when |
|----|------|-----------|
| B1 | RAG chunk schema and doc | 05_rag_integration updated with chunk metadata schema + retrieval modes ✓ |
| B2 | Emit/store tags at ingestion | New/re-ingested chunks have tags; no regression |
| B3 | Retrieval API accepts mode | Callers can pass Strict/Loose/Inspired; behavior in 05_rag_integration |
| B4 | Prompt-side instruction | Optional "Retrieval Mode" at one call site; doc shows pattern |

**Order:** B1 → B2 → B3 → B4.

---

### Track C: Meta-prompt Script (Quick Win)

| ID | Goal | Done when |
|----|------|-----------|
| C1 | Script or CLI for meta-prompt | e.g. `scripts/meta_prompt.py`; reads context path, spine + meta-prompt + state → generate_text → output ✓ |
| C2 | Doc | One line in README_workflow or narrative_workbench_spec: how to run meta-prompt ✓ |

**Order:** C1 → C2. No dependency on Frame or RAG.

---

### Track D: Workflow UI — Archivist and Foreshadowing (Optional)

| ID | Goal | Done when |
|----|------|-----------|
| D1 | API endpoints | POST `/api/session/archivist`, POST `/api/session/foreshadow`; call run_archivist/run_foreshadowing; return status + output_path |
| D2 | UI controls | Buttons/form to trigger Archivist and Foreshadowing; link to output; doc in DEVELOPMENT_PLAN_REMAINING |
| D3 | List in Future work | If deferred, add item to DEVELOPMENT_PLAN_REMAINING Future work |

**Order:** D1 → D2; D3 anytime.

---

### Track E: Workflow GUI Backlog (Ordered)

From [DEVELOPMENT_PLAN_REMAINING.md](../../workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md). Implement when touching workflow_ui; no task IDs here.

1. Rate limiting on `/api/run/*` and/or PUTs  
2. Startup config/path validation and clear error messaging  
3. Path-traversal audit (and tests) for `/api/arc/<id>/file/<subpath>`  
4. OpenAPI or equivalent description of workflow_ui API  
5. UX: "Running…" state and dirty-form warning for task decomp and feedback  
6. Validation of task_decomposition and feedback schema before save  
7. In-app pipeline diagram (e.g. Mermaid from workflow_diagrams.md)  
8. Cross-links to campaign_kb (NPCs/locations) in encounter/feedback UI  
9. E2E tests (e.g. Playwright) for critical paths  

---

## Suggested Implementation Order

1. **Phase 0:** This doc + link from README_workflow / integration map ✓  
2. **Phase 1:** C1–C2 (meta-prompt), A1 (Frame output format) ✓  
3. **Phase 2:** A2 → A3 → A4 (Story Architect, wire, tests) ✓  
4. **Phase 3:** B1 ✓ → B2 → B3 → B4 (RAG schema, ingestion, retrieval, prompt)  
5. **Phase 4 (optional):** D1 → D2; E items as needed  

RAG (Phase 3) and Frame (Phase 2) can be swapped; both depend only on Phase 0 and Phase 1 docs.

---

## Next: Phase 2–3 Readiness

Phase 0–1 and Frame (Phase 2) are complete; B1 done. **Next:** Phase 3 (RAG B2–B4) or Phase 4 (workflow_ui Archivist/Foreshadowing).
