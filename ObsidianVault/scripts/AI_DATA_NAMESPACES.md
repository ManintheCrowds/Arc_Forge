# AI Data Namespaces (Micro-segmentation)

AI security: separate AI data from sync/user content. See [D:\local-first\AI_SECURITY.md](D:\local-first\AI_SECURITY.md).

## Namespaces

| Namespace | Storage | Contents |
|-----------|---------|----------|
| **AI embeddings** | ChromaDB `persist_dir` | Collection `arc_forge_rag`; chunk embeddings |
| **AI cache** | `Campaigns/_rag_cache/` | document_index.json, RAG pipeline outputs |
| **Campaign KB** | `campaign_kb/data/kb.sqlite3` | Ingested docs, search index (AI-adjacent) |
| **Sync / user content** | `Campaigns/` markdown | Arc files, encounters, session memory (user-owned) |

## Separation

- ChromaDB persist dir is separate from campaign markdown
- `_rag_cache` is under Campaigns but prefixed to distinguish from user content
- campaign_kb SQLite is dedicated to ingested/search data; not mixed with vault markdown
