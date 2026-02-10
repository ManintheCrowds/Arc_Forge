# Storyboard-to-Encounter Workflow

Workflow for turning storyboards into task decomposition, encounter drafts, human review, refined encounters, and final specs. Designed for human-guided prompts at each stage and future GUI/text UI integration.

## Overview

See [workflow_diagrams.md](docs/workflow_diagrams.md) for pipeline and file-tree diagrams.

**Narrative workbench architecture:** [docs/narrative_workbench_spec.md](docs/narrative_workbench_spec.md)

**Next steps (orchestration):** [docs/NEXT_STEPS_ORCHESTRATION.md](docs/NEXT_STEPS_ORCHESTRATION.md) — phases, task IDs, and per-track summary.

**Frame (Story Architect) output format:** [docs/frame_output_format.md](docs/frame_output_format.md) — structure of 3 session frameworks (title, hook, 2–3 beats; no prose).

```
Storyboard → Stage 1: Task Decomposition → Stage 2: Encounter Drafts
     → Stage 3: Human Review (feedback only) → Stage 4: Refined Encounters
     → Stage 5: Final Specs (4 outputs)
```

## Stage Summary

| Stage | Input | Output | Automation |
|-------|--------|--------|------------|
| 1 | Storyboard markdown | Task decomposition (encounters + opportunities, sequence) | Script proposes; human decides granularity |
| 2 | Task decomposition + storyboard | One draft file per encounter/opportunity (`_draft_v1.md`) | Full (RAG + campaign_kb with fallbacks) |
| 3 | Encounter draft(s) | Structured feedback (YAML/JSON or sectioned doc) | Human-only |
| 4 | Draft + feedback | New draft version (`_draft_v2.md`) or refined | Full (LLM + optional RAG) |
| 5 | All refined encounters | Hierarchical MD, expanded storyboard, JSON/YAML, 04_missions_*_encounters.md | Full |

## File Layout

```
Campaigns/
  first_arc/
    task_decomposition.md
    task_decomposition.yaml
    first_arc_feedback.yaml
    first_arc_expanded_storyboard.md
    first_arc_encounters.json
    first_arc_versions.json
    encounters/
      highway_chase_draft_v1.md
      highway_chase_draft_v2.md
      highway_chase.md
    opportunities/
      optional_negotiation_draft_v1.md
      optional_negotiation.md
```

## Entry Points (for scripts / future UI)

- **Stage 1:** `run_stage_1(storyboard_path, arc_id, output_dir)` → writes `task_decomposition.md` and `task_decomposition.yaml`
- **Stage 2:** `run_stage_2(task_decomposition_path, storyboard_path, arc_id, config_path)` → writes `encounters/*_draft_v1.md`, `opportunities/*_draft_v1.md`
- **Stage 3:** Human-only. See [Structured Feedback](docs/feedback_schema.md) (or inline below).
- **Stage 4:** `refine_encounter(draft_path, feedback_path, rag_config)` → writes next `*_draft_v{n}.md`
- **Stage 5:** `export_final_specs(arc_id, arc_dir, campaign_kb_path)` → writes hierarchical MD, expanded storyboard, JSON, and `04_missions_{arc}_encounters.md`

## RAG and campaign_kb

- **W&G mechanics:** RAG over PDF text in `Sources/_extracted_text`; fallback: generic DN/skill prompts.
- **Retrieval mode:** To use retrieval mode (Strict Canon / Loose Canon / Inspired By), set it in your prompt or pass `retrieval_mode` to `run_pipeline` (or in `encounter_spec` / `rag_config["query_mode"]` when calling `draft_encounter`). See campaign_kb `campaign/05_rag_integration.md` for behavior per mode.
- **NPCs:** `campaign_kb/campaign/03_npcs.md`; fallback: placeholders or prompt-only.
- **Locations:** `campaign_kb/campaign/02_locations.md`; fallback: placeholders or storyboard prose.
- **Sequence:** From task decomposition; kept in structured output and in `04_missions_*_encounters.md`.

## Versioning

- Drafts: `{slug}_draft_v1.md`, `_draft_v2.md`, …
- Final/refined: `{slug}.md` or `{slug}_refined.md`
- Optional `{arc}_versions.json`: `{"highway_chase": {"current": "draft_v2", "history": ["draft_v1", "draft_v2"]}}`

## Stage 3: How to Write Structured Feedback

Stage 3 is human-only: you review encounter drafts and produce **structured feedback**. Stage 4 reads that feedback and produces a new draft.

- **Where:** `Campaigns/{arc_id}/{arc_id}_feedback.yaml` or `.json`
- **Allowed `type` values:** `expand`, `change`, `add_mechanic`, `remove`, `link_npc`, `link_location`, `other`
- **Example:** [schemas/feedback_example.yaml](schemas/feedback_example.yaml), [schemas/feedback_example.json](schemas/feedback_example.json)
- **Full schema:** [docs/feedback_schema.md](docs/feedback_schema.md)

## Frame (Story Architect) upstream of Stage 1

To use **Frame** before the main pipeline: run the Story Architect first to get 3 session frameworks; choose one (or expand it); then feed the chosen framework (or its expansion) as the storyboard into Stage 1.

1. **Frame:** `python frame_workflow.py --premise path/to/premise.md --arc-state path/to/arc_state.md` → writes e.g. `Campaigns/_rag_outputs/frame_YYYY-MM-DD.md` (3 frameworks: title, hook, 2–3 beats).
2. **Select + Expand:** DM picks a framework (or edits/expands it) into a storyboard.
3. **Stage 1:** `python storyboard_workflow.py <storyboard.md> --stage 1 --arc-id <arc_id>`.

See [frame_output_format.md](docs/frame_output_format.md) for the Frame output structure.

## How to run (CLI)

From `ObsidianVault/scripts` (or with paths set accordingly):

```bash
# Frame (optional): Premise + arc state → 3 session frameworks
python frame_workflow.py --premise Campaigns/campaign_premise.md --arc-state Campaigns/first_arc/arc_state.md

# Stage 1: Storyboard → Task Decomposition
python storyboard_workflow.py "Campaigns/_rag_outputs/first_arc_storyboard.md" --stage 1 --arc-id first_arc

# Stage 2: Task Decomposition → Encounter Drafts (needs RAG/Ollama)
python storyboard_workflow.py "Campaigns/_rag_outputs/first_arc_storyboard.md" --stage 2 --task-decomp Campaigns/first_arc/task_decomposition.yaml --arc-id first_arc

# Stage 4: Refine one encounter from feedback
python storyboard_workflow.py --stage 4 --draft Campaigns/first_arc/encounters/highway_chase_draft_v1.md --feedback Campaigns/first_arc/first_arc_feedback.yaml

# Stage 5: Export final specs (hierarchical MD, expanded storyboard, JSON, campaign_kb)
python storyboard_workflow.py --stage 5 --arc-id first_arc --arc-dir Campaigns/first_arc --campaign-kb ../campaign_kb
```

Stage 3 is human-only: edit `Campaigns/{arc_id}/{arc_id}_feedback.yaml` (or `.json`), then run Stage 4.

## Post-session ingestion (Phase 4)

After a session, fill the **Session Summary (for Archivist)** block in your session note (see [Session_Summary_Template](docs/Session_Summary_Template.md)). Then:

1. **Archivist:** `python session_ingest.py --session path/to/session.md` (from `ObsidianVault/scripts`). Output: `Campaigns/_session_memory/YYYY-MM-DD_archivist.md` (canonical timeline, flagged consequences, retrieval anchors).
2. **Foreshadowing (optional):** `python session_ingest.py --foreshadow --context path/to/archivist_output.md`. Output appended to `Campaigns/_session_memory/threads.md`.
3. Check [[Workbench]] and `Campaigns/_session_memory/threads.md` for active threads and consequences.

Requires `--config path/to/ingest_config.json` if not using default under `scripts/`.

**Meta-prompt (VIII):** Evaluate campaign state and suggest the smallest high-impact change:  
`python meta_prompt.py --context path/to/campaign_state.md` (from `ObsidianVault/scripts`). Optional: `--output path/to/result.md`; without `--context`, reads campaign state from stdin.

## Interface-Ready Notes

- Each stage has a single callable entry point with explicit paths and `arc_id`.
- Stage 2 and 4 write versioned filenames; Stage 5 overwrites a fixed set of outputs.
- Task decomposition and feedback use parseable YAML/JSON for UI forms.
