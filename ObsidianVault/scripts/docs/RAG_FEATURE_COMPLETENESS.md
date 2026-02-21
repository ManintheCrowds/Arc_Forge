# RAG Pipeline Feature-Completeness Findings

**Source:** Comparison of [05_rag_integration.md](../../campaign_kb/campaign/05_rag_integration.md) and implementation in [rag_pipeline.py](../rag_pipeline.py). See also [rag_fully_developed_review_fa0144ea.plan.md](D:\CodeRepositories\.cursor\plans\rag_fully_developed_review_fa0144ea.plan.md).

## Summary

**Verdict: Partially complete.** Core retrieval and generation work. Several gaps and expectation mismatches exist.

## Implemented

| Feature | Status |
|---------|--------|
| Campaign docs + PDF text ingestion | Yes — `stage_ingest` reads from disk |
| DocumentIndex keyword/theme retrieval | Yes — default path when `use_chroma: false` |
| ChromaDB semantic retrieval | Yes — opt-in via `use_chroma: true` |
| Canon modes (Strict/Loose/Inspired By) | Yes — DocumentIndex and ChromaRetriever |
| Pattern analysis (entities, themes) | Yes — `build_pattern_report` |
| Summarization | Yes — `summarize_context` via ai_summarizer |
| Content pack generation | Yes — rules, bios, adventure, etc. |
| Storyboard generation | Yes — `generate_storyboard` with config-driven constraints |
| Query mode vs analysis mode | Yes — fast path for queries, full corpus for analysis |
| Citation-ready grounding prompts | Yes — prompts reference canonical context |

## Gaps

| Gap | Detail |
|-----|--------|
| Role-based prompts | 05_rag_integration implies Story Architect, Encounter Designer, Archivist, Foreshadow roles. Implementation: hardcoded Encounter Designer; Archivist/Foreshadow are separate workflows (session_ingest), not in core RAG pipeline. |
| Semantic retrieval default | ChromaDB is opt-in (`use_chroma: false`). Default path is keyword/theme via DocumentIndex. Most users get keyword retrieval. |
| Automated evaluation | Rubric exists (06_rag_evaluation); `_run_evaluation_if_enabled` is a placeholder. No coherence/canon/citation scoring in pipeline. |
| answer_query | Exists but not wired to workflow UI. Daggr RAG workflow and storyboard_workflow use `run_pipeline` only. |
| Session memory in RAG | RAG does not ingest session summaries. Archivist/Foreshadow outputs live in `_session_memory`; RAG corpus is campaign_docs + PDFs. |
| campaign_kb alignment | RAG `campaign_docs` ≠ campaign_kb DB. Two sources of truth. See TROUBLESHOOTING.md "campaign_docs vs campaign_kb DB". |

## Recommendations

1. Document when to enable Chroma vs rely on keyword retrieval (see 05_rag_integration ChromaDB section).
2. Wire `answer_query` to workflow UI if Q&A over context is desired.
3. Add automated evaluation hook using 06_rag_evaluation rubric when `evaluation.enabled` is true.
4. Align campaign_kb ingest with RAG sources when `use_kb_search` is true (ingest same campaign_docs into DB).
