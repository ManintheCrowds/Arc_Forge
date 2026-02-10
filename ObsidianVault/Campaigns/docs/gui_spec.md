# GUI Spec: Storyboard-to-Encounter Workflow

Spec for a thin UI that orchestrates the workflow. One primary view per stage; structured I/O as forms; human-gated; GUI only calls existing Python entry points.

**Narrative workbench architecture:** [narrative_workbench_spec.md](narrative_workbench_spec.md)

**Backend contract:** The GUI calls the same entry points as the CLI. No new backend APIs. Backend is [scripts/storyboard_workflow.py](D:\arc_forge\ObsidianVault\scripts\storyboard_workflow.py): `run_stage_1`, `run_stage_2`, `refine_encounter`, `export_final_specs`. Pass paths and `arc_id`; read/write files under `Campaigns/{arc_id}/`.

**Diagrams:** Pipeline and file-tree are defined in [workflow_diagrams.md](workflow_diagrams.md). The GUI must show a pipeline view (Storyboard → S1 → … → S5) and an arc file-tree (`Campaigns/{arc_id}/` with encounters/, opportunities/, task_decomposition, feedback, expanded storyboard, JSON). Pipeline view can render that Mermaid in-app or use a minimal list/canvas that reflects the current stage and arc.

---

## One Screen per Stage

### Stage 1: Task Decomposition

| | |
|---|--|
| **Inputs** | `storyboard_path`, `arc_id`, `output_dir` (default Campaigns root), optional `storyboard_ref` |
| **Actions** | "Run Stage 1" (calls `run_stage_1(...)`); "Edit task decomposition" (opens Stage 1 form) |
| **Outputs** | Show or open `task_decomposition.md`, `task_decomposition.yaml`; link into arc file-tree |

### Stage 2: Encounter Drafts

| | |
|---|--|
| **Inputs** | `task_decomposition_path`, `storyboard_path`, `arc_id`, `config_path` (e.g. ingest_config.json) |
| **Actions** | "Run Stage 2" (calls `run_stage_2(...)`) |
| **Outputs** | List/link to `encounters/*_draft_v1.md`, `opportunities/*_draft_v1.md`; show in arc file-tree |

### Stage 3: Human Review (feedback only)

| | |
|---|--|
| **Inputs** | `arc_id`, path to `{arc_id}_feedback.yaml` (or .json) |
| **Actions** | "Edit feedback" (opens Stage 3 form); "Save feedback" (writes YAML/JSON). No AI/run. |
| **Outputs** | Show current feedback for each encounter; list encounter drafts to review (read-only pointers) |

**Note:** Stage 3 is human-only. The UI helps *compose* feedback; it does not run an AI.

### Stage 4: Refined Encounters

| | |
|---|--|
| **Inputs** | `draft_path` (one encounter draft, e.g. `highway_chase_draft_v1.md`), `feedback_path` (`{arc_id}_feedback.yaml`), `rag_config` (from config) |
| **Actions** | "Refine this encounter" (calls `refine_encounter(draft_path, feedback_path, rag_config)`); selector for which draft to refine |
| **Outputs** | New `*_draft_v2.md` (or next version); show version and source in provenance UI |

### Stage 5: Final Specs

| | |
|---|--|
| **Inputs** | `arc_id`, `arc_dir` (e.g. Campaigns/first_arc), `campaign_kb_path`, optional `storyboard_path` |
| **Actions** | "Export final specs" (calls `export_final_specs(...)`) |
| **Outputs** | Links to: hierarchical MD, expanded storyboard, JSON, `campaign_kb/campaign/04_missions_{arc}_encounters.md` |

---

## Stage 1 Form: Task Decomposition Editor

Edit the structure that [task_decomposition_example.yaml](../schemas/task_decomposition_example.yaml) defines.

**Load/save:** `task_decomposition.yaml` in the current arc dir. Optionally write or sync a human-readable `task_decomposition.md`.

**Fields (top-level):**

- `arc_id` (text)
- `storyboard_ref` (text, optional)

**Encounters (list).** Each item:

- `id` (text, slug)
- `name` (text)
- `type` (dropdown: combat, social, exploration, environmental)
- `sequence` (number)
- `storyboard_section` (text, optional)
- `after` (text, optional; id of previous encounter or null)
- `before` (text, optional; id of next encounter or null)

**Opportunities (list).** Each item:

- `id`, `name`, `type`, `sequence`, `storyboard_section`, `optional` (bool), `note` (text)

**Sequence constraints (list):** free text lines, e.g. "Highway Chase before Boardings".

**Actions:** Add encounter; remove encounter; reorder encounters (update sequence and after/before). Same for opportunities. Save to `task_decomposition.yaml`.

---

## Stage 3 Form: Feedback Editor

Edit the structure that [feedback_schema.md](feedback_schema.md) and [feedback_example.yaml](../schemas/feedback_example.yaml) define.

**Load/save:** `{arc_id}_feedback.yaml` (or .json) in the current arc dir.

**Top-level:** `arc_id` (text).

**Encounters (list).** Each encounter has:

- `id` (text; must match an encounter id from task decomposition)
- `feedback` (list of feedback items)

**Feedback item.** Each item has:

- **type** (dropdown): `expand`, `change`, `add_mechanic`, `remove`, `link_npc`, `link_location`, `other`
- **Type-specific fields:**
  - expand: `target`, `instruction`
  - change: `target`, `from`, `to` (or `instruction`)
  - add_mechanic: `detail`
  - remove: `target` or `instruction`
  - link_npc: `npc_id`, `instruction`
  - link_location: `location_id`, `instruction`
  - other: `instruction` or `detail`

**Actions:** Encounter selector (which encounter gets feedback); add feedback item; remove feedback item; reorder items; choose type and show only that type’s fields; Save to `{arc_id}_feedback.yaml`.

---

## Pipeline View and Arc File-Tree

**Pipeline view:** Always visible (or toggle). Shows the five stages (Storyboard → S1 → S2 → S3 → S4 → S5) and, for the selected arc, which artifacts exist (task_decomposition, encounters/*.md, feedback file, expanded storyboard, JSON, campaign_kb file). Prefer rendering the Mermaid from [workflow_diagrams.md](workflow_diagrams.md) in-app, or a minimal list/canvas that updates when the user runs a stage or changes arc.

**Arc file-tree:** Tree or flat list of `Campaigns/{arc_id}/`:

- task_decomposition.md, task_decomposition.yaml
- {arc_id}_feedback.yaml
- first_arc_expanded_storyboard.md, first_arc_encounters.json (after S5)
- encounters/ (highway_chase_draft_v1.md, highway_chase.md, …)
- opportunities/ (optional_negotiation_draft_v1.md, …)

Allow opening/viewing encounter drafts and task_decomposition from this tree.

---

## Provenance and Versions

Where encounter drafts are shown, display **version and source**, e.g.:

- "Highway Chase – draft v2, from first_arc_feedback.yaml"

Optional: per-encounter **lifecycle** (draft_v1 → feedback → draft_v2 → … → final) as a small list or inline diagram so the user sees how each draft was produced.

---

## Summary Checklist for Implementation

- [ ] Pipeline view (Storyboard → S1 → … → S5) and arc file-tree
- [ ] One screen (or tab) per stage with inputs, Run action, outputs
- [ ] Stage 1 form: task decomposition (encounters, opportunities, sequence_constraints); load/save .yaml
- [ ] Stage 3 form: feedback (encounter id, list of items with type + type-specific fields); load/save .yaml
- [ ] Provenance: version and source for each encounter draft
- [ ] All stage actions call `run_stage_1`, `run_stage_2`, `refine_encounter`, `export_final_specs` from storyboard_workflow.py with paths and arc_id
