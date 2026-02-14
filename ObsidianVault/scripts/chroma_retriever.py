# PURPOSE: ChromaDB-based semantic retriever for Arc Forge RAG pipeline.
# DEPENDENCIES: chromadb, sentence_transformers; rag_pipeline.extract_chunk_tags, ai_summarizer.chunk_text.
# MODIFICATION NOTES: Option B (ChromaDB-only) per DEVELOPMENT_PLAN_REMAINING.md.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Schema keys for chunk tags (must match rag_pipeline.CHUNK_TAG_KEYS)
CHUNK_TAG_KEYS = (
    "system",
    "faction",
    "location",
    "time_period",
    "mechanical_vs_narrative",
    "tone",
)

# Default chunk size for embedding (aligned with pdf_ingestion.max_chunk_size)
DEFAULT_CHUNK_SIZE = 8000
DEFAULT_CHUNK_OVERLAP = 200


def _safe_metadata(value: str) -> str:
    """ChromaDB metadata values must be str, int, float, or bool. Empty str is valid."""
    if value is None:
        return ""
    return str(value) if value else ""


class ChromaRetriever:
    """
    Semantic retriever using ChromaDB and sentence-transformers.
    Supports Strict/Loose/Inspired By canon modes via metadata filtering.
    """

    def __init__(
        self,
        persist_dir: Path,
        embedding_model: str = "all-MiniLM-L6-v2",
        collection_name: str = "arc_forge_rag",
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_model_name = embedding_model
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._model = None

    def _get_client(self):
        if self._client is None:
            import chromadb
            from chromadb.config import Settings
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    def _get_collection(self):
        if self._collection is None:
            self._collection = self._get_client().get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.embedding_model_name)
        return self._model

    def count(self) -> int:
        """Return number of documents in the collection."""
        try:
            return self._get_collection().count()
        except Exception:
            return 0

    def build_index(
        self,
        text_map: Dict[str, str],
        rag_config: Dict[str, Any],
        chunk_tags_config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Build ChromaDB index from text_map. For each doc: extract tags, chunk if large,
        embed, add to ChromaDB with metadata.
        """
        from rag_pipeline import extract_chunk_tags
        try:
            from ai_summarizer import chunk_text
            CHUNKING_AVAILABLE = True
        except ImportError:
            CHUNKING_AVAILABLE = False
            chunk_text = None

        chunk_tags_config = chunk_tags_config or {}
        collection = self._get_collection()
        if collection.count() > 0:
            self._client.delete_collection(self.collection_name)
            self._collection = None
            collection = self._get_collection()
        model = self._get_model()

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        max_chunk_size = rag_config.get("chroma", {}).get("chunk_size", DEFAULT_CHUNK_SIZE)
        chunk_overlap = rag_config.get("chroma", {}).get("chunk_overlap", DEFAULT_CHUNK_OVERLAP)

        for doc_key, text in text_map.items():
            doc_type = "campaign" if not doc_key.startswith("[PDF]") else "pdf"
            tags = extract_chunk_tags(doc_key, text, doc_type, chunk_tags_config)
            for k in CHUNK_TAG_KEYS:
                if k not in tags:
                    tags[k] = ""

            if CHUNKING_AVAILABLE and len(text) > max_chunk_size:
                chunks = chunk_text(text, max_chunk_size=max_chunk_size, overlap=chunk_overlap)
            else:
                chunks = [text]

            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                chunk_id = f"{doc_key}__chunk_{i}" if len(chunks) > 1 else doc_key
                chunk_id = chunk_id.replace("/", "_").replace("\\", "_")[:200]
                ids.append(chunk_id)
                documents.append(chunk[:100000])
                meta = {
                    "doc_key": doc_key,
                    **{k: _safe_metadata(tags.get(k, "")) for k in CHUNK_TAG_KEYS},
                }
                metadatas.append(meta)

        if not ids:
            logger.warning("No documents to add to ChromaDB index")
            return 0

        embeddings = model.encode(documents, show_progress_bar=False)
        collection.add(ids=ids, embeddings=embeddings.tolist(), documents=documents, metadatas=metadatas)
        logger.info(f"ChromaDB index built: {len(ids)} chunks from {len(text_map)} docs")
        return len(ids)

    def remove_docs(self, doc_keys: List[str]) -> int:
        """
        Remove all chunks whose doc_key metadata matches any of the given doc_keys.
        Returns number of chunks removed (approximate; ChromaDB does not return count).
        """
        if not doc_keys:
            return 0
        collection = self._get_collection()
        try:
            collection.delete(where={"doc_key": {"$in": doc_keys}})
            logger.info(f"ChromaDB removed chunks for docs: {doc_keys}")
            return len(doc_keys)
        except Exception as exc:
            logger.warning(f"ChromaDB remove_docs failed: {exc}")
            return 0

    def add_or_update_docs(
        self,
        text_map: Dict[str, str],
        rag_config: Dict[str, Any],
        chunk_tags_config: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        For each doc in text_map: remove existing chunks for that doc_key, then add new chunks.
        Enables incremental updates without full rebuild.
        """
        from rag_pipeline import extract_chunk_tags
        try:
            from ai_summarizer import chunk_text
            CHUNKING_AVAILABLE = True
        except ImportError:
            CHUNKING_AVAILABLE = False
            chunk_text = None

        chunk_tags_config = chunk_tags_config or {}
        collection = self._get_collection()
        model = self._get_model()
        max_chunk_size = rag_config.get("chroma", {}).get("chunk_size", DEFAULT_CHUNK_SIZE)
        chunk_overlap = rag_config.get("chroma", {}).get("chunk_overlap", DEFAULT_CHUNK_OVERLAP)
        total_added = 0

        for doc_key, text in text_map.items():
            self.remove_docs([doc_key])
            doc_type = "campaign" if not doc_key.startswith("[PDF]") else "pdf"
            tags = extract_chunk_tags(doc_key, text, doc_type, chunk_tags_config)
            for k in CHUNK_TAG_KEYS:
                if k not in tags:
                    tags[k] = ""

            if CHUNKING_AVAILABLE and len(text) > max_chunk_size:
                chunks = chunk_text(text, max_chunk_size=max_chunk_size, overlap=chunk_overlap)
            else:
                chunks = [text]

            ids: List[str] = []
            documents: List[str] = []
            metadatas: List[Dict[str, Any]] = []
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                chunk_id = f"{doc_key}__chunk_{i}" if len(chunks) > 1 else doc_key
                chunk_id = chunk_id.replace("/", "_").replace("\\", "_")[:200]
                ids.append(chunk_id)
                documents.append(chunk[:100000])
                meta = {
                    "doc_key": doc_key,
                    **{k: _safe_metadata(tags.get(k, "")) for k in CHUNK_TAG_KEYS},
                }
                metadatas.append(meta)

            if ids:
                embeddings = model.encode(documents, show_progress_bar=False)
                collection.add(ids=ids, embeddings=embeddings.tolist(), documents=documents, metadatas=metadatas)
                total_added += len(ids)

        logger.info(f"ChromaDB add_or_update_docs: {total_added} chunks from {len(text_map)} docs")
        return total_added

    def retrieve(
        self,
        query: str,
        top_k: int = 8,
        retrieval_mode: str = "Strict Canon",
        tag_filters: Optional[Dict[str, str]] = None,
        max_chunk_chars: int = 2000,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks. Returns list of {"source": doc_key, "score": float, "text": str}.
        """
        if not query.strip():
            return []

        collection = self._get_collection()
        model = self._get_model()
        query_embedding = model.encode([query], show_progress_bar=False).tolist()

        where_filter = None
        n_results = top_k

        if retrieval_mode == "Strict Canon" and tag_filters:
            and_clauses = []
            for k, v in tag_filters.items():
                if v:
                    and_clauses.append({k: v})
            if and_clauses:
                where_filter = {"$and": and_clauses} if len(and_clauses) > 1 else and_clauses[0]

        if retrieval_mode == "Loose Canon" and tag_filters:
            where_filter = None
            n_results = min(top_k * 2, 50)

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        if not results or not results["ids"] or not results["ids"][0]:
            return []

        ids_list = results["ids"][0]
        docs_list = results["documents"][0]
        metas_list = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids_list)
        dists_list = results["distances"][0] if results.get("distances") else [0.0] * len(ids_list)

        out: List[Dict[str, Any]] = []
        seen_doc_keys = set()

        for i, (doc_id, doc_text, meta, dist) in enumerate(zip(ids_list, docs_list, metas_list, dists_list)):
            doc_key = meta.get("doc_key", doc_id)
            if retrieval_mode == "Loose Canon" and tag_filters:
                match_count = sum(1 for k, v in tag_filters.items() if meta.get(k) == v)
                if match_count == len(tag_filters):
                    dist = dist - 0.5
                elif match_count > 0:
                    dist = dist - 0.2
            score = max(0.0, 1.0 - dist) if dist is not None else 1.0
            out.append({"source": doc_key, "score": float(score), "text": (doc_text or "")[:max_chunk_chars]})
            seen_doc_keys.add(doc_key)

        out.sort(key=lambda x: x["score"], reverse=True)
        return out[:top_k]
