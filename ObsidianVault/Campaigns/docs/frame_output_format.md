# Frame Output Format (Story Architect)

**Source:** [narrative_workbench_spec](narrative_workbench_spec.md) § V — Step 1: Frame. Role: Story Architect. Output of `run_story_architect` must match this structure so downstream (Select+Expand → Stage 1) can consume it.

---

## Requirement

**No prose.** The Story Architect proposes exactly **3 session frameworks**. Each framework is a skeleton: title, one-line hook, and 2–3 beats. No narrative paragraphs.

---

## Structure (per framework)

For each of the 3 frameworks, the output must include:

| Field | Description | Example |
|-------|-------------|--------|
| **Title** | Short label for the session direction | "Highway Chase" / "Negotiation Gone Wrong" |
| **Hook** | One-line premise or question | "The convoy is ambushed; one cargo must be abandoned." |
| **Beats** | 2–3 bullet points: key story beats only | "- Ambush; choice of cargo.<br>- Chase or stand; consequence for delay.<br>- Arrival; faction reaction." |

Additional optional fields (if the script or prompt supports them): tone note (e.g. grim, lethal), estimated session length.

---

## Markdown shape

Implementers and tests can assume a shape like:

```markdown
## Framework A: <Title>
**Hook:** <one line>

- Beat 1
- Beat 2
- [Beat 3]

## Framework B: <Title>
**Hook:** <one line>

- Beat 1
- Beat 2

## Framework C: <Title>
**Hook:** <one line>

- Beat 1
- Beat 2
- Beat 3
```

Section headers may be `## Framework A`, `## Option 1`, or similar, as long as there are exactly three distinct frameworks and each has a title, hook, and 2–3 beats. No long prose blocks.

---

## Done-when (A1)

- This doc exists.
- Referenced from [README_workflow](../README_workflow.md) or the [Integration Map](narrative_workbench_spec.md#integration-map-this-project).
- Script output (A2) and tests (A4) assert against this structure (e.g. three sections, presence of hook and beats).
