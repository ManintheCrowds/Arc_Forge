# Structured Feedback Schema (Stage 3 → Stage 4)

Stage 3 is human-only: you review encounter drafts and produce **structured feedback**. Stage 4 reads that feedback and produces a new draft.

## Where to Put Feedback

- **Per-arc YAML:** `Campaigns/{arc_id}/{arc_id}_feedback.yaml`
- **Per-arc JSON:** `Campaigns/{arc_id}/{arc_id}_feedback.json`
- **Per-encounter:** `Campaigns/{arc_id}/encounters/{encounter_id}_feedback.md` (if you add a parser later)

Use YAML or JSON so scripts and future UI can read it without parsing prose.

## Allowed `type` Values

| type | Use for | Typical fields |
|------|---------|----------------|
| `expand` | Add more detail to a target | `target`, `instruction` |
| `change` | Change a value (e.g. DN, name) | `target`, `from`, `to` (or `instruction`) |
| `add_mechanic` | Add a rule or mechanic | `detail` |
| `remove` | Remove an element | `target` or `instruction` |
| `link_npc` | Tie encounter to NPC from 03_npcs | `npc_id`, `instruction` |
| `link_location` | Tie encounter to location from 02_locations | `location_id`, `instruction` |
| `other` | Free text | `instruction` or `detail` |

## YAML Example

See [../schemas/feedback_example.yaml](../schemas/feedback_example.yaml).

## JSON Example

See [../schemas/feedback_example.json](../schemas/feedback_example.json).

## Structure

Top level: `arc_id` and `encounters` list. Each encounter has `id` and `feedback` (list of items). Each feedback item has `type` and type-specific fields.
