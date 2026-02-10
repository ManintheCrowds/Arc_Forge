<!--
# PURPOSE: RAG integration guide for the Wrath and Glory knowledge stack.
# DEPENDENCIES: ObsidianVault scripts, campaign_kb search service.
# MODIFICATION NOTES: Initial integration blueprint with reuse-first mapping.
-->

# RAG Integration

## Goals
- Unify ingestion, retrieval, and generation into a single, consistent flow.
- Enable pattern analysis across factions, locations, NPCs, and missions.
- Support content generation for rules, adventures, and bios grounded in canon.

## Reuse vs. Create (source of truth)
- Ingestion (PDF + seed): `D:\Arc_Forge\ObsidianVault\scripts\ingest_pdfs.py`
- Summarization: `D:\Arc_Forge\ObsidianVault\scripts\ai_summarizer.py`
- Entity extraction: `D:\Arc_Forge\ObsidianVault\scripts\entity_extractor.py`
- Full-text retrieval: `D:\Arc_Forge\campaign_kb\app\search\service.py`
- Web API scaffolding: `D:\Arc_Forge\ObsidianVault\scripts\web_api.py`
- Orchestration (new): `D:\Arc_Forge\ObsidianVault\scripts\rag_pipeline.py`

## Data Sources and Ingestion
- Primary sources: seed docs, campaign docs, extracted PDF text.
- Ingestion outputs: Obsidian notes under `Sources/` and structured entities.
- Canon priority: seed docs, campaign docs, extracted PDFs, generated notes (in that order).

## Indexing and Retrieval
- Current retrieval: full-text search in `campaign_kb` (Sections table).
- Optional vector layer: can be added later; keep outputs citation-ready now.
- Retrieval targets:
  - Sections for queries
  - Canon anchors for generation prompts

## Pattern Analysis Workflow
- Inputs: campaign docs + extracted PDFs.
- Outputs: entity counts, co-occurrence hints, theme tallies.
- Canon bias: prefer seed + campaign sources when scoring patterns.

## Content Generation Workflow
- Inputs: context summary + top entities + user prompt.
- Outputs: rules, adventure arcs, bios, rumors.
- Guardrails:
  - Must cite canonical sources when possible.
  - Flag speculative details explicitly.

## Prompt Templates (base)
**Rules Draft Prompt**
```
Use only the provided context. Draft a concise rules module with:
- Scope
- Mechanics
- Example of play
Context:
{context}
```

**Adventure Seed Prompt**
```
Generate a 3-act adventure outline grounded in the context.
Include: hook, key scenes, adversaries, and fallout.
Context:
{context}
```

**Bio Pack Prompt**
```
Generate 3 NPC bios tied to the factions/locations provided.
Each bio: role, motivation, secret, hook.
Context:
{context}
```

## RAG Metadata Schema (doc-level)
- RAG_Link: `campaign/05_rag_integration.md`
- RAG_Entity_Types: NPC, Faction, Location, Item, Theme
- RAG_Pattern_Targets: fields that should be mined for patterns
- RAG_Generation_Targets: outputs that should be generated from this doc
- RAG_Source_Priority: ordered list of canonical sources

## Chunk metadata schema (chunk-level)

Per-chunk tags for targeted retrieval. Keys match the schema below; values are strings (or empty).

| Field | Description | Allowed values / examples |
|-------|--------------|---------------------------|
| **System** | Game system or source book | `W&G`, `D&D`, `generic` |
| **Faction** | Faction or faction-adjacent | e.g. `Inquisition`, `Smugglers`, (empty) |
| **Location** | Place or region | e.g. `Footfall`, `void`, (empty) |
| **Time_period** | Era or time frame | e.g. `current`, `historical`, (empty) |
| **Mechanical_vs_narrative** | Content type | `mechanical`, `narrative`, or empty |
| **Tone** | Tone tag for matching | `grimdark`, `heroic`, `absurd`, `neutral`, or empty |

Ingestion (B2) stores these per chunk in the document index. Omitted keys are treated as unrestricted for filtering.

## Retrieval modes

DM-facing modes for how strictly to match chunk tags. Selectable when calling the retrieval API (e.g. `run_pipeline(..., retrieval_mode="Loose Canon")`).

| Mode | Meaning | Filtering / ranking |
|------|---------|--------------------|
| **Strict Canon** | Only chunks whose tags match the request (or configured tag_filters). | Include only entries where tags satisfy all requested filters; no tag = not included unless filter is optional. |
| **Loose Canon** | Chunks that match or are adjacent/similar in tag space. | Include chunks with overlapping or related tags; apply score boost for exact tag match, lower boost for adjacent. |
| **Inspired By** | Thematic similarity only; tag match optional. | Do not filter by tags; rank by existing keyword/theme/preview similarity. Use when DM wants mood or theme over strict canon. |

Implementation: retrieval accepts `retrieval_mode` (B3); filter/rank behavior is implemented in `DocumentIndex.retrieve()` and `retrieve_context()`.

## Implementation (chunk tags and retrieval)

- **Ingestion (B2):** Chunk tags are stored per document key in `Campaigns/_rag_cache/document_index.json` as an optional `"tags"` dict on each index entry (keys = schema field names above). Re-ingest updates index and tags.
- **Retrieval (B3):** The retrieval API accepts `retrieval_mode` (`Strict Canon` | `Loose Canon` | `Inspired By`) and optional `tag_filters`; behavior is documented in the "Retrieval API" subsection below.

## Retrieval API

- **How to pass retrieval_mode:** Call `run_pipeline(config_path, query=..., retrieval_mode="Loose Canon")` or pass `retrieval_mode` into `retrieve_context()`. Default can be set in config under `rag_config["query_mode"]["retrieval_mode"]`.
- **Behavior per mode:** See "Retrieval modes" above. Strict = filter to tag-matched chunks only; Loose = include adjacent/similar tags with scoring; Inspired = no tag filter, rank by text similarity only.
- **Optional tag_filters:** When using Strict or Loose, callers can pass a dict of requested tag values (e.g. `{"system": "W&G", "tone": "grimdark"}`). Omitted keys are unrestricted.

## Evaluation (minimum viable)
- Coherence (1-5): internal consistency and tone fit.
- Citation density (1-5): references to canonical sources.
- Canon reuse (1-5): overlap with seed/campaign docs.
- See `campaign/06_rag_evaluation.md` for scoring templates.

## Pipeline Overview
```mermaid
flowchart LR
    sourceDocs["SourceDocs"] --> ingest["Ingest"]
    ingest --> extractText["ExtractText"]
    extractText --> entities["EntityExtraction"]
    extractText --> summaries["Summarization"]
    entities --> index["Indexing"]
    summaries --> index
    index --> retrieve["Retrieve"]
    retrieve --> generate["GenerateContent"]
    generate --> outputs["RulesAdventuresBios"]
```
