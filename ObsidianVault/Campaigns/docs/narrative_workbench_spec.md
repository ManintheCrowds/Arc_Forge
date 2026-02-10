# Narrative Workbench Spec (Canonical Architecture)

**Source:** ChatGPT conversation (collaborative narrative workbench). This doc is the normative architecture for the Arc Forge campaign workbench.

Problem understood. Goal clear. Break into two parallel systems: **(A) prompting + cognition layer** and **(B) minimal human interface layer**. No GUI coding required initially. Text-first. Later extensible.

Proceed stepwise. Analytical. Practical.

---

## I. Mental Model: What This System Is

Not "an AI that writes adventures."

It is:

- A collaborative narrative workbench
- With memory (RAG)
- Temporal continuity
- Human authority preserved
- Post-session ingestion loop

**Key constraint:** DM remains final arbiter. AI proposes. Human disposes.

---

## II. Core Prompting Architecture (Most Important Part)

You do not prompt it like ChatGPT.

You prompt it like a co-author with rules, memory, and scope.

### A. System Prompt (Immutable)

This is the spine. Write once. Rarely change.

Example structure (conceptual):

> You are a tabletop roleplaying narrative engine designed to collaborate with a human Game Master.
>
> Primary directives:
> 1. Preserve internal lore consistency using retrieved source material.
> 2. Treat the human DM as final authority.
> 3. Never introduce mechanics, factions, spells, or lore not grounded in retrieved texts or explicit DM input.
> 4. Favor suggestion over assertion.
> 5. Surface uncertainty explicitly.
> 6. Track narrative consequences across time.
>
> You do not write finished prose unless explicitly requested.
> You generate modular narrative components.
> You ask for clarification when ambiguity materially affects outcome.

This prevents "AI novelist syndrome."

### B. Role-Based Prompt Layers (Dynamic)

Instead of one giant prompt, you rotate roles.

Examples:

- **World Analyst** – checks lore consistency
- **Story Architect** – proposes arcs
- **Encounter Designer** – mechanical framing
- **Archivist** – summarizes sessions
- **Foreshadowing Engine** – long-term threads

You activate them explicitly.

```
Role: Story Architect
Task: Propose 3 possible directions for the next arc based on retrieved lore and last session summary.
Constraints: No new factions. Grimdark tone. Low heroism.
```

This dramatically improves controllability.

---

## III. RAG Strategy (Very Specific)

Do not dump books raw.

### A. Chunk by Semantic Function

Each chunk tagged with:

- System (W&G, D&D, etc.)
- Faction
- Location
- Time period
- Mechanical vs narrative
- Tone tags (grimdark, heroic, absurd)

This allows targeted retrieval.

### B. Retrieval Modes (Selectable)

Expose this to the DM as modes, not parameters.

Examples:

- **"Strict Canon"** – only exact matches
- **"Loose Canon"** – adjacent material allowed
- **"Inspired By"** – thematic similarity only

Prompt-side instruction:

```
Retrieval Mode: Strict Canon
Exclude homebrew.
```

---

## IV. Session-to-Session Memory Loop (Critical)

This is where most systems fail.

### A. Post-Session Input (Human-Facing)

Do not ask DMs to write essays.

Use structured capture:

**Session Summary (bullet-level):**

- Major events:
- NPCs interacted with:
- Unresolved threads:
- Player surprises:
- Tone shift:
- Player intent signals:

**AI role: Archivist**

It converts this into:

- Canonical timeline entries
- Flagged future consequences
- Retrieval anchors

Stored separately from raw text.

### B. Consequence Propagation Prompt

After ingestion:

```
Role: Foreshadowing Engine
Task: Identify delayed consequences likely to emerge in 2–5 sessions.
Limit: 5 items.
Probability estimate required.
```

This keeps long arcs alive.

---

## V. Adventure Drafting Workflow (Concrete)

**Step 1: Frame**

- Role: Story Architect
- Input: Campaign premise, current arc state, desired session length, tone sliders (grim ↔ absurd, lethal ↔ narrative)
- Task: Propose 3 session frameworks. No prose.

**Step 2: Select + Expand**

- DM chooses.
- Expand Option B. Add 2 complications. Include moral ambiguity.

**Step 3: Mechanics Pass**

- Role: Encounter Designer
- Convert narrative beats into encounters. Reference system mechanics only.

**Step 4: Flavor Pass (Optional)**

- Role: World Stylist
- Write boxed text only. Max 120 words total.

---

## VI. "GUI" Without a GUI (You Can Do This Now)

You do not need a graphical interface.

You need structured markdown + conventions.

### A. Sections as Panels

Use headers like pseudo-panels:

- `## [CAMPAIGN STATE]`
- `## [ACTIVE THREADS]`
- `## [SESSION INPUT]`
- `## [AI PROPOSALS]`
- `## [DM DECISIONS]`

This feels like a UI.

### B. Dark-Mode Aesthetic by Convention

- Short lines
- High contrast language
- Bullet density
- Minimal adjectives

Think Obsidian vault, not website.

---

## VII. If You Want Visual Inspiration (Optional)

These inform vibe, not function.

---

## VIII. One Prompt to Rule Iteration (Meta-Prompt)

This is the DM's main lever.

- Evaluate current campaign state.
- Identify narrative entropy.
- Propose the smallest change that produces the largest future divergence.
- Explain reasoning.

This keeps stories alive without bloat.

---

## IX. Summary (Compressed)

- Treat prompting as system design, not chat
- Separate roles, retrieval, and authority
- Capture sessions structurally
- Think "text UI" first
- AI proposes. Human curates.
- Minimalism is a discipline, not a feature

---

## Integration Map (This Project)

Ties each spec section to existing files and gaps. **Orchestration:** [NEXT_STEPS_ORCHESTRATION](NEXT_STEPS_ORCHESTRATION.md) — single reference for phases and task IDs (Frame, RAG, meta-prompt, workflow_ui).

| Spec section | Current state | Target / gap |
|--------------|---------------|--------------|
| **System prompt (II.A)** | Not implemented | Shared file or snippet loaded by scripts. See `Campaigns/docs/prompts/system_prompt_spine.md`. |
| **Role layers (II.B)** | Workflow stages are pipeline steps, not explicit roles | World Analyst, Story Architect, Encounter Designer, Archivist, Foreshadowing. Encounter Designer wired in storyboard_workflow; others as doc/backlog. |
| **RAG (III)** | campaign_kb/campaign/05_rag_integration.md + `_rag_cache` | Chunk tags + retrieval_mode implemented. Tags stored per chunk in document_index.json; retrieval accepts Strict Canon / Loose Canon / Inspired By and optional tag_filters. Pass retrieval_mode to run_pipeline or in encounter_spec/rag_config. |
| **Session loop (IV)** | campaign_kb/campaign/06_session_log.md, Templates/session_note.md | Session Summary block in Phase 2; Archivist script: `session_ingest.run_archivist`; output: `Campaigns/_session_memory/YYYY-MM-DD_archivist.md`. Foreshadowing: `session_ingest.run_foreshadowing`; output: `Campaigns/_session_memory/threads.md`. |
| **Adventure drafting (V)** | Storyboard → S1→S2→S3→S4→S5 ([README_workflow](../README_workflow.md)) | "Frame" is upstream of current Stage 1; output format: [frame_output_format](frame_output_format.md). "Mechanics" = S1–S2; "Flavor" = optional boxed text in drafts; "Select+Expand" = DM edits task_decomposition / storyboard before S2. |
| **Text UI (VI)** | [DM_Dashboard](../DM_Dashboard.md), [Workbench](../Workbench.md) | Section-headers-as-panels and Session Summary shape added in Phase 2. |
| **Meta-prompt (VIII)** | Implemented | Spine in `system_prompt_spine.md`. CLI: `python meta_prompt.py --context path/to/campaign_state.md` (see [README_workflow](../README_workflow.md)). |

**Post-Session Input (Human-Facing):** Session Summary template is in [Session_Summary_Template](Session_Summary_Template.md) and embedded in [Templates/session_note](../../Templates/session_note.md).

**Archivist output format:** [archivist_output_format](archivist_output_format.md) — canonical timeline entries, flagged future consequences, retrieval anchors.
