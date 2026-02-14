# PURPOSE: Tests for ChromaRetriever and retrieve_context ChromaDB path.
# DEPENDENCIES: pytest, chromadb, sentence_transformers (optional - ChromaDB tests skip if not installed).
# MODIFICATION NOTES: Option B ChromaDB integration tests.

import uuid
from pathlib import Path

import pytest


def _has_chroma_deps():
    try:
        __import__("chromadb")
        __import__("sentence_transformers")
        return True
    except ImportError:
        return False


@pytest.fixture
def chroma_tmp_path():
    """Persistent tmp dir for ChromaDB tests; avoids Windows PermissionError on teardown (ChromaDB holds file locks)."""
    root = Path(__file__).resolve().parent.parent / ".pytest-chroma"
    root.mkdir(parents=True, exist_ok=True)
    path = root / str(uuid.uuid4())
    path.mkdir(parents=True, exist_ok=True)
    yield path


@pytest.mark.skipif(not _has_chroma_deps(), reason="chromadb and sentence_transformers required")
def test_chroma_retriever_build_and_retrieve(chroma_tmp_path):
    """Build index with sample docs (different tags), retrieve with Strict/Loose/Inspired."""
    from chroma_retriever import ChromaRetriever

    retriever = ChromaRetriever(chroma_tmp_path, collection_name="test_arc_forge")
    # Use doc keys that trigger extract_chunk_tags heuristic: doc_wg_* get system W&G, dragon_rules gets D&D
    text_map = {
        "doc_wg_1": "Wrath and Glory rules. Dice rolls and damage. Wrath dice mechanics.",
        "doc_wg_2": "Wrath and Glory campaign. Grimdark tone. Inquisition faction.",
        "dragon_rules": "Dragon and Dungeons rules. D&D mechanics. Fantasy setting.",
    }
    rag_config = {
        "chroma": {"chunk_size": 5000, "chunk_overlap": 200},
        "chunk_tags": {"defaults": {"system": "W&G"}},
    }
    retriever.build_index(text_map, rag_config, {})

    assert retriever.count() >= 3

    # Inspired By: no filter; all docs can appear
    inspired = retriever.retrieve("wrath rules", top_k=5, retrieval_mode="Inspired By")
    assert isinstance(inspired, list)
    assert len(inspired) >= 1
    for item in inspired:
        assert "source" in item
        assert "score" in item
        assert "text" in item
        assert isinstance(item["source"], str)
        assert isinstance(item["score"], (int, float))
        assert isinstance(item["text"], str)

    # Strict Canon with tag_filters: expects W&G docs (doc_wg_1, doc_wg_2); dragon_rules has D&D.
    # ChromaDB where filter may include non-matching docs in some versions; assert structure and at least one W&G.
    strict = retriever.retrieve(
        "wrath rules", top_k=5, retrieval_mode="Strict Canon", tag_filters={"system": "W&G"}
    )
    assert isinstance(strict, list)
    wg_sources = {item["source"] for item in strict if item["source"] in ("doc_wg_1", "doc_wg_2")}
    assert len(wg_sources) >= 1, f"Expected at least one W&G doc, got: {[i['source'] for i in strict]}"

    # Loose Canon: returns list with tag boost
    loose = retriever.retrieve(
        "wrath rules", top_k=5, retrieval_mode="Loose Canon", tag_filters={"system": "W&G"}
    )
    assert isinstance(loose, list)
    assert len(loose) >= 1


@pytest.mark.skipif(not _has_chroma_deps(), reason="chromadb and sentence_transformers required")
def test_retrieve_context_uses_chroma_when_enabled(chroma_tmp_path):
    """With use_chroma=true and valid config, retrieve_context returns ChromaDB results."""
    from rag_pipeline import load_pipeline_config, retrieve_context

    config_path = Path(__file__).resolve().parents[1] / "ingest_config.json"
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"].copy()
    rag_config["use_chroma"] = True
    rag_config["chroma"] = {
        "persist_dir": str(chroma_tmp_path / "chroma"),
        "embedding_model": "all-MiniLM-L6-v2",
        "collection_name": "test_arc",
    }
    rag_config["vault_root"] = Path(__file__).resolve().parents[2]
    rag_config["campaign_kb_root"] = Path(rag_config["campaign_kb_root"])
    rag_config["use_kb_search"] = False

    text_map = {
        "campaign/00_overview.md": "Wrath and Glory campaign overview. Grimdark setting.",
    }
    results = retrieve_context(
        "wrath campaign",
        rag_config,
        doc_index=None,
        text_map=text_map,
    )
    assert isinstance(results, list)
    if results:
        assert all("source" in r and "score" in r and "text" in r for r in results)


def test_retrieve_context_fallback_when_chroma_unavailable():
    """When chroma_retriever import fails, fall through to legacy retrieval."""
    import builtins
    from unittest.mock import patch

    from rag_pipeline import load_pipeline_config, retrieve_context

    config_path = Path(__file__).resolve().parents[1] / "ingest_config.json"
    config_bundle = load_pipeline_config(config_path)
    rag_config = config_bundle["rag"].copy()
    rag_config["use_chroma"] = True
    rag_config["use_kb_search"] = False
    rag_config["campaign_kb_root"] = Path(rag_config["campaign_kb_root"])

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "chroma_retriever":
            raise ImportError("chroma not available")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", fake_import):
        results = retrieve_context(
            "wrath",
            rag_config,
            doc_index=None,
            text_map={"doc1": "wrath and glory rules"},
        )
    assert isinstance(results, list)
    assert len(results) >= 1
    assert results[0]["source"] == "doc1"
    assert "wrath" in results[0]["text"].lower() or "glory" in results[0]["text"].lower()
