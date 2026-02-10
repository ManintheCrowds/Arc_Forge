# Task Decomposition Output Format (Stage 1)

Stage 1 produces a task decomposition from a storyboard. Human decides granularity (one beat = one encounter vs multiple sub-encounters).

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `arc_id` | string | Arc identifier (e.g. `first_arc`) |
| `storyboard_ref` | string | Path to storyboard relative to Campaigns |
| `encounters` | list | Ordered encounters; each has `id`, `name`, `type`, `sequence`, optional `storyboard_section`, `after`, `before` |
| `opportunities` | list | Optional side scenes; same shape plus `optional: true` and `note` |
| `sequence_constraints` | list | Human-readable constraints (e.g. "Highway Chase before Train Hijacking") |

Encounter/opportunity `type`: `combat`, `social`, `exploration`, `environmental`.

## Example

See [task_decomposition_example.yaml](task_decomposition_example.yaml).

## Outputs

Stage 1 writes:
- `Campaigns/{arc_id}/task_decomposition.md` (human-readable)
- `Campaigns/{arc_id}/task_decomposition.yaml` (parseable mirror)
