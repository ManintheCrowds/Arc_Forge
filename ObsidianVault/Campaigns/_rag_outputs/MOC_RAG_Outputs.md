---
title: "RAG and pipeline outputs (staging)"
tags: ["type/moc", "status/verified", "campaign/redacted_records"]
---

# RAG and pipeline outputs (staging)

This folder holds **machine-generated and frame outputs** from the storyboard/RAG pipeline (`scripts/rag_pipeline.py` default `output_dir`). It is **staging**, not the canonical rules layer.

**Upstream (how these are produced):** [[Campaigns/README_workflow]]

**Campaign context:** [[Campaigns/Campaign_Index]] · First arc task decomposition (markdown): [[Campaigns/first_arc/task_decomposition]] · Schemas: [[Campaigns/schemas/task_decomposition]]

**Canonical TTRPG surface:** verified mechanics and house rules live under `Rules/` with `type/rule` and [[Sources/]] backlinks. Promote distilled content from the generated notes below into entity/rule notes when you accept it.

**Lint / graph:** [[Vault-meta/Graph_and_lint_dashboard]]

## Outputs in this folder

| Note | Role |
|------|------|
| [[first_arc_storyboard]] | Storyboard input for pipeline stages |
| [[frame_2026-02-12]] | Frame workflow output (dated example) |
| [[rag_context_summary]] | RAG context summary |
| [[rag_generated_rules]] | Draft rules text (promote to [[Rules/]]) |
| [[rag_generated_bios]] | Draft bios |
| [[rag_generated_adventure]] | Draft adventure text |
| [[rag_patterns]] | Extracted patterns |

> `rag_patterns.json` is JSON metadata alongside `rag_patterns.md`; open from the file tree if needed.

## See also

- [[Vault-meta/SCRIPTS_DOCS_INDEX]] — scripts and engineering docs (config, RAG research, feature tracking)
