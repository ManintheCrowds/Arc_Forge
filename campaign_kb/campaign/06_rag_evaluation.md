<!--
# PURPOSE: Evaluation rubric and test checklist for RAG outputs.
# DEPENDENCIES: None.
# MODIFICATION NOTES: Initial evaluation templates for pattern and generation quality.
-->

# RAG Evaluation

## Scoring Rubric (1-5 scale)
- **Coherence:** internal consistency, clear logic, readable structure.
- **Canon Reuse:** references to seed/campaign sources, accurate terms.
- **Citation Density:** anchors to canonical docs or sections.
- **Tone Fit:** grimdark/gothic alignment with campaign tone.
- **Utility:** actionable hooks, usable rules/adventures/bios.

## Pattern Analysis Checks
- Entity coverage for NPCs, Factions, Locations, Items.
- Theme coverage using keyword list from `ingest_config.json`.
- Co-occurrence hints include at least 3 faction/NPC pairings.
- At least 5 actionable hooks derived from patterns.

## Generation Checks
- Rules include scope, mechanics, and example of play.
- Adventures include hook, 3 acts, adversaries, fallout.
- Bios include role, motivation, secret, and hook.
- Generated content cites at least 3 canonical anchors.

## Example Evaluation Sheet
| Output | Coherence | Canon Reuse | Citation Density | Tone Fit | Utility | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Rules |  |  |  |  |  |  |
| Adventure |  |  |  |  |  |  |
| Bios |  |  |  |  |  |  |

## Automated Evaluation (optional)

Enable heuristic evaluation in `ingest_config.json` under `rag_pipeline`:

```json
"evaluation": { "enabled": true }
```

When enabled, the pipeline runs `evaluate_content_pack` after generation and writes `rag_evaluation.json` to the output dir. Scores are heuristic-based (citation density, structure checks via regex for `## Scope`, `### Mechanics`, etc., tone keywords). Coherence defaults to placeholder (3.0); set `evaluation.coherence_method: "llm"` to use LLM-based coherence scoring (requires generation provider).

## Testing Checklist
- [ ] Run `rag_pipeline.py` against the campaign docs
- [ ] Validate output files in `Campaigns/_rag_outputs`
- [ ] Verify patterns align with faction/location/NPC docs
- [ ] Spot-check at least 5 generated hooks for canon conflicts
