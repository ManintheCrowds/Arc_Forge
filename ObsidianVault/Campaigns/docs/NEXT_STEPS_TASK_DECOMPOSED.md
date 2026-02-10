# Next Steps — Fine-Grained Task Decomposition

Sub-steps for each task ID from [NEXT_STEPS_ORCHESTRATION](NEXT_STEPS_ORCHESTRATION.md). Tick each sub-step when done; parent task is done when all its sub-steps are done.

---

## Phase 0: Single orchestration doc

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **0.1** | Create orchestration doc | `Campaigns/docs/NEXT_STEPS_ORCHESTRATION.md` | Doc exists with: source-of-truth links, phases 1–4 + task IDs, per-track summary. |
| **0.2** | Add link from README | `Campaigns/README_workflow.md` | One line under narrative workbench: link to NEXT_STEPS_ORCHESTRATION. |
| **0.3** | Add link from integration map | `Campaigns/docs/narrative_workbench_spec.md` | Integration Map section starts with "Orchestration: [NEXT_STEPS_ORCHESTRATION](...)". |

---

## Track A: Frame (Story Architect)

### A1 — Define Frame output format

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **A1.1** | Create frame format doc | `Campaigns/docs/frame_output_format.md` | Doc defines: exactly 3 frameworks; per-framework: title, one-line hook, 2–3 beats; no prose. Include example markdown shape (e.g. `## Framework A`, `**Hook:**`, bullets). |
| **A1.2** | Reference from README | `Campaigns/README_workflow.md` | One line: "Frame output format: [frame_output_format](docs/frame_output_format.md)." |
| **A1.3** | Reference from integration map or spec | `Campaigns/docs/narrative_workbench_spec.md` | Adventure drafting (V) row or Frame bullet points to frame_output_format. |

### A2 — Story Architect script

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **A2.1** | Add spine loader | `scripts/frame_workflow.py` | `_load_system_prompt_spine(path)` (reuse pattern from session_ingest/storyboard_workflow); default path = Campaigns/docs/prompts/system_prompt_spine.md. |
| **A2.2** | Implement run_story_architect | `scripts/frame_workflow.py` | Signature: `run_story_architect(premise_path, arc_state_path, config_path, output_path=None, system_prompt_path=None, tone_sliders=None)`. Reads premise + arc state; builds prompt = "Role: Story Architect" + spine + task + premise + arc state (+ optional tone); calls `generate_text`; writes markdown to output_path or default. Returns dict with status, output_path. |
| **A2.3** | Config resolution | `scripts/frame_workflow.py` | Same candidates as session_ingest: scripts/ingest_config.json, Campaigns/ingest_config.json. Require --config or use first existing. |
| **A2.4** | CLI entry point | `scripts/frame_workflow.py` | `main()`: --premise, --arc-state, --config, --output, --spine, --tone; calls run_story_architect; prints status and output_path. |
| **A2.5** | Default output path | `scripts/frame_workflow.py` | If output_path is None: write to Campaigns/_rag_outputs/frame_YYYY-MM-DD.md; create dir if needed. |

### A3 — Wire Frame upstream of Stage 1

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **A3.1** | Document order in README | `Campaigns/README_workflow.md` | New subsection "Frame (Story Architect) upstream of Stage 1": (1) Run Frame → get 3 frameworks; (2) DM selects/expands one; (3) Use that as storyboard input to Stage 1. Include CLI example for frame_workflow. |
| **A3.2** | Optional: script or doc for "Framework B → storyboard" | `Campaigns/docs/` or script | If implemented: doc or one-liner script that takes a chosen framework file and produces minimal storyboard for run_stage_1. Otherwise: README text is sufficient. |

### A4 — Tests

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **A4.1** | Test: run_story_architect writes file | `scripts/tests/test_frame_workflow.py` | Fixture: premise.md + arc_state.md + ingest_config.json in tmp_path. Mock rag_pipeline.load_pipeline_config and generate_text. Call run_story_architect with output_path; assert output file exists, status success. |
| **A4.2** | Test: output structure | `scripts/tests/test_frame_workflow.py` | Mocked generate_text returns string with "## Framework A", "## Framework B", "## Framework C" and "Hook:" and bullets. Assert output file content contains at least three section headers and bullet-like content. |
| **A4.3** | Test: missing premise or arc_state | `scripts/tests/test_frame_workflow.py` | Call with nonexistent premise_path (or arc_state_path); assert status error and reason mentions missing file. |
| **A4.4** | Run pytest | — | `pytest scripts/tests/test_frame_workflow.py -v` passes. |

---

## Track B: RAG chunk tags and retrieval modes

### B1 — RAG chunk schema and doc

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **B1.1** | Add "Chunk metadata schema" section | `campaign_kb/campaign/05_rag_integration.md` | Table or list: System, Faction, Location, Time_period, Mechanical_vs_narrative, Tone. For each: description + allowed values or examples (e.g. Tone: grimdark, heroic, absurd). |
| **B1.2** | Add "Retrieval modes" section | `campaign_kb/campaign/05_rag_integration.md` | Define Strict Canon, Loose Canon, Inspired By: what each means (exact match vs adjacent vs thematic); how they map to filters or ranking (e.g. strict = tag match only; loose = tag or neighbor; inspired = similarity score). |
| **B1.3** | Implementation note | `campaign_kb/campaign/05_rag_integration.md` | Short "Implementation" or "Next" note: ingestion must emit/store tags (B2); retrieval API must accept mode (B3). |

### B2 — Emit/store tags at ingestion

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **B2.1** | Decide storage shape | `scripts/ingest_pdfs.py` or `rag_pipeline` + 05_rag_integration | Choose: extra column in existing store, or sidecar JSON per chunk, or field in _rag_cache. Document in 05_rag_integration. |
| **B2.2** | Add tag computation or input | `scripts/ingest_pdfs.py` and/or `scripts/rag_pipeline.py` | Per chunk: compute or accept System, Faction, Location, Time_period, Mechanical_vs_narrative, Tone (can be defaults/empty initially). |
| **B2.3** | Persist tags | Same as B2.2 | Write tags to chosen storage; ensure re-ingest updates tags. |
| **B2.4** | Regression check | — | Existing ingest + retrieval pipeline still works; one test or manual run. |

### B3 — Retrieval API accepts mode

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **B3.1** | Add retrieval_mode parameter | `scripts/rag_pipeline.py` (or campaign_kb search) | Public search/retrieve function accepts e.g. `retrieval_mode: str = "Strict Canon"` (or enum). |
| **B3.2** | Implement filter/rank by mode | Same | Strict: only return chunks matching query tags strictly. Loose: include adjacent/similar tags. Inspired: rank by thematic similarity; may relax tag match. |
| **B3.3** | Document in 05_rag_integration | `campaign_kb/campaign/05_rag_integration.md` | "Retrieval API" subsection: how to pass mode; behavior per mode. |
| **B3.4** | Test | `scripts/tests/` or campaign_kb tests | Unit test: call retrieval with each mode; assert result shape or tag constraints (mocked store if needed). |

### B4 — Prompt-side instruction

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **B4.1** | Add optional retrieval_mode to one call site | e.g. `storyboard_workflow.py` or `frame_workflow.py` | Where generate_text or RAG is called: accept optional "Retrieval Mode: Strict Canon" (or Loose/Inspired); pass through to retrieval if B3 is done. |
| **B4.2** | Document pattern | `Campaigns/docs/narrative_workbench_spec.md` or README | One line or bullet: "To use retrieval mode: set Retrieval Mode in prompt or pass retrieval_mode to script." |

---

## Track C: Meta-prompt script

### C1 — Script or CLI for meta-prompt

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **C1.1** | Create script file | `scripts/meta_prompt.py` | Purpose comment; reuse _load_system_prompt_spine pattern (or import from session_ingest if no circular deps). |
| **C1.2** | Implement run_meta_prompt | `scripts/meta_prompt.py` | Reads campaign state from path or stdin; prompt = spine + meta-prompt text ("Evaluate current campaign state…") + campaign state; call generate_text; return or write result. |
| **C1.3** | Config resolution | `scripts/meta_prompt.py` | Same as session_ingest: --config optional; default to scripts/ingest_config.json or Campaigns/ingest_config.json. |
| **C1.4** | CLI | `scripts/meta_prompt.py` | main(): --context (path to campaign state), --config, --output (optional write), --spine (optional). If no --context, read stdin. Print result to stdout unless --output. |
| **C1.5** | Runnable | — | `python meta_prompt.py --context path/to/campaign_state.md` runs and prints LLM output (or error if no config). |

### C2 — Doc

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **C2.1** | Add to README_workflow | `Campaigns/README_workflow.md` | One line: "Meta-prompt (VIII): run `python meta_prompt.py --context path/to/campaign_state.md`." (from scripts dir). |
| **C2.2** | Update integration map | `Campaigns/docs/narrative_workbench_spec.md` | Meta-prompt (VIII) row: "Implemented; CLI: …" and link to README or meta_prompt.py. |

---

## Track D: Workflow UI — Archivist and Foreshadowing (optional)

### D1 — API endpoints

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **D1.1** | Resolve session_ingest import path | `workflow_ui/app.py` or blueprint | Ensure run_archivist and run_foreshadowing are callable (e.g. add scripts to path, or copy minimal wrapper). CONFIG_PATH from app config or env. |
| **D1.2** | POST /api/session/archivist | `workflow_ui/` | Body: session_path or session_note path. Call run_archivist(session_path, config_path); return JSON: status, output_path (and reason if error). |
| **D1.3** | POST /api/session/foreshadow | `workflow_ui/` | Body: context_path (or archivist output path). Call run_foreshadowing(context_path, config_path); return JSON: status, output_path. |
| **D1.4** | Test endpoints | `workflow_ui/tests/` or manual | With mock or real config: POST archivist with path; POST foreshadow with path; assert 200 and output_path in response. |

### D2 — UI controls

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **D2.1** | Add "Session" or "Memory" section | workflow_ui frontend | Place for Archivist and Foreshadowing actions. |
| **D2.2** | Button or form: Run Archivist | Same | Sends session path (from input or file picker) to POST /api/session/archivist; show status and link to output_path (e.g. _session_memory/YYYY-MM-DD_archivist.md). |
| **D2.3** | Button or form: Run Foreshadowing | Same | Sends context path to POST /api/session/foreshadow; show link to threads.md or output_path. |
| **D2.4** | Document in DEVELOPMENT_PLAN_REMAINING | `workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md` | "Session memory: Archivist/Foreshadowing UI" done or in progress. |

### D3 — List in Future work (if deferred)

| Sub | Action | File(s) | Done when |
|-----|--------|---------|-----------|
| **D3.1** | Add Future work item | `workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md` | "Session memory: Archivist/Foreshadowing endpoints + UI" in Future work section. |

---

## Track E: Workflow GUI backlog

No sub-decomposition here; implement in order 1–9 when touching workflow_ui. See [NEXT_STEPS_ORCHESTRATION](NEXT_STEPS_ORCHESTRATION.md) and [DEVELOPMENT_PLAN_REMAINING](../../workflow_ui/docs/DEVELOPMENT_PLAN_REMAINING.md).

---

## Execution order (tick list)

- [ ] **Phase 0:** 0.1 → 0.2 → 0.3  
- [ ] **Phase 1:** C1.1–C1.5, C2.1–C2.2; A1.1–A1.3  
- [ ] **Phase 2:** A2.1–A2.5 → A3.1–A3.2 → A4.1–A4.4  
- [ ] **Phase 3:** B1.1–B1.3 → B2.1–B2.4 → B3.1–B3.4 → B4.1–B4.2  
- [ ] **Phase 4 (optional):** D1.1–D1.4 → D2.1–D2.4; D3.1 if deferred  

RAG (Phase 3) and Frame (Phase 2) can be swapped; both need Phase 0 and Phase 1 docs.
