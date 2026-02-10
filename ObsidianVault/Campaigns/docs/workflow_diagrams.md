# Workflow Diagrams

Pipeline, data flow, and file layout for the Storyboard-to-Encounter workflow. Source of truth for docs and future GUI.

## Pipeline Flowchart

```mermaid
flowchart LR
  Storyboard[Storyboard]
  S1_TaskDecomp[S1 Task Decomp]
  S2_Drafts[S2 Drafts]
  S3_Review[S3 Human Review]
  S4_Refine[S4 Refine]
  S5_Export[S5 Export]
  Outputs[4 outputs]

  Storyboard --> S1_TaskDecomp
  S1_TaskDecomp --> S2_Drafts
  S2_Drafts --> S3_Review
  S3_Review --> S4_Refine
  S4_Refine --> S5_Export
  S5_Export --> Outputs
```

- **S1:** Storyboard → task_decomposition.md / .yaml
- **S2:** Task decomposition + storyboard → encounters/*_draft_v1.md, opportunities/*_draft_v1.md
- **S3:** Human-only; produces structured feedback (YAML/JSON)
- **S4:** Draft + feedback → next *_draft_vN.md
- **S5:** All refined encounters → hierarchical MD, expanded storyboard, JSON, 04_missions_*_encounters.md

## Data Flow

RAG, campaign_kb, and storyboard feed stages as follows:

```mermaid
flowchart TB
  subgraph sources [Sources]
    Storyboard[Storyboard .md]
    RAG[RAG / W&G PDFs]
    CampaignKB[campaign_kb 02_locations 03_npcs]
  end

  subgraph stages [Stages]
    S1[S1 Task Decomp]
    S2[S2 Drafts]
    S4[S4 Refine]
  end

  Storyboard --> S1
  Storyboard --> S2
  RAG --> S2
  CampaignKB --> S2
  RAG --> S4
  CampaignKB --> S4
```

- **S1** uses only the storyboard.
- **S2** uses storyboard, task decomposition, RAG (mechanics), and campaign_kb (NPCs, locations).
- **S4** uses draft, feedback, RAG, and campaign_kb when applying feedback.

## File Layout (Arc Tree)

Layout for `Campaigns/{arc_id}/` (example: `first_arc`):

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

Mermaid-style block diagram of the same layout:

```mermaid
flowchart TB
  subgraph arc [Campaigns/first_arc]
    task_md[task_decomposition.md]
    task_yaml[task_decomposition.yaml]
    feedback[first_arc_feedback.yaml]
    expanded[first_arc_expanded_storyboard.md]
    json_out[first_arc_encounters.json]
    versions[first_arc_versions.json]
    subgraph encounters [encounters/]
      enc_draft1[highway_chase_draft_v1.md]
      enc_draft2[highway_chase_draft_v2.md]
      enc_final[highway_chase.md]
    end
    subgraph opportunities [opportunities/]
      opp_draft[optional_negotiation_draft_v1.md]
      opp_final[optional_negotiation.md]
    end
  end
```
