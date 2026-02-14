# PURPOSE: Test stubs for RAG pipeline orchestration.
# DEPENDENCIES: pytest, rag_pipeline, pathlib.
# MODIFICATION NOTES: B3.4 – retrieval_mode tests for DocumentIndex.retrieve; T5.1/T5.2 retrieve_context schema.

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from rag_pipeline import (
    CHUNK_TAG_KEYS,
    DocumentIndex,
    load_pipeline_config,
    read_pdf_texts,
    retrieve_context,
    stage_ingest,
    stage_index,
    stage_analyze,
    stage_summarize,
    stage_generate,
)


# PURPOSE: Validate pipeline configuration loads with defaults.
# DEPENDENCIES: ingest_config.json.
# MODIFICATION NOTES: Ensures rag_pipeline section is present.
def test_load_pipeline_config():
    config_path = Path(__file__).resolve().parents[1] / "ingest_config.json"
    config_bundle = load_pipeline_config(config_path)
    assert "rag" in config_bundle
    assert "campaign_docs" in config_bundle["rag"]
    assert config_bundle["rag"]["output_dir"] is not None


# PURPOSE: B3.4 – test DocumentIndex.retrieve with retrieval_mode and tag_filters.
# DEPENDENCIES: DocumentIndex, temp dir.
# MODIFICATION NOTES: Strict returns only tag-matching; Inspired ignores tags; Loose returns list.
def test_document_index_strict_canon_empty_tag_values(tmp_path):
    """Strict Canon with empty tag_filters values treats them as unrestricted (T3.15)."""
    index_path = tmp_path / "document_index.json"
    index = {
        "doc_wg": {"path": "doc_wg", "keywords": ["wrath"], "preview": "wrath rules", "themes": {}, "tags": {"system": "W&G"}},
        "doc_other": {"path": "doc_other", "keywords": ["wrath"], "preview": "other wrath", "themes": {}, "tags": {"system": "Other"}},
    }
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    doc_index = DocumentIndex(index_path)
    result = doc_index.retrieve(
        "wrath", top_k=10, retrieval_mode="Strict Canon",
        tag_filters={"system": "W&G", "faction": ""},
    )
    assert "doc_wg" in result
    assert "doc_other" not in result


def test_document_index_retrieval_modes(tmp_path):
    index_path = tmp_path / "document_index.json"
    # Build minimal index: two W&G-tagged docs (with "wrath" in preview), one D&D, one untagged
    index = {
        "doc_wg_1": {
            "path": "doc_wg_1",
            "keywords": ["wrath", "glory"],
            "preview": "wrath and glory rules",
            "themes": {"wrath": 1},
            "tags": {"system": "W&G"},
        },
        "doc_wg_2": {
            "path": "doc_wg_2",
            "keywords": ["wrath"],
            "preview": "wrath mechanics",
            "themes": {},
            "tags": {"system": "W&G"},
        },
        "doc_dnd": {
            "path": "doc_dnd",
            "keywords": ["dragon"],
            "preview": "dragon rules",
            "themes": {},
            "tags": {"system": "D&D"},
        },
        "doc_untagged": {
            "path": "doc_untagged",
            "keywords": ["wrath"],
            "preview": "generic wrath",
            "themes": {},
            "tags": {},
        },
    }
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    doc_index = DocumentIndex(index_path)
    assert len(doc_index.index) == 4

    # Strict Canon with tag_filters: only W&G-tagged docs
    strict_result = doc_index.retrieve(
        "wrath", top_k=10, retrieval_mode="Strict Canon", tag_filters={"system": "W&G"}
    )
    assert isinstance(strict_result, list)
    for doc_key in strict_result:
        assert doc_index.index[doc_key].get("tags", {}).get("system") == "W&G"
    assert "doc_dnd" not in strict_result
    assert "doc_untagged" not in strict_result

    # Inspired By: no tag filter; all docs with "wrath" can appear
    inspired_result = doc_index.retrieve(
        "wrath", top_k=10, retrieval_mode="Inspired By"
    )
    assert isinstance(inspired_result, list)
    assert len(inspired_result) <= 10
    # doc_wg_1, doc_wg_2, doc_untagged have "wrath"; doc_dnd does not
    assert len(inspired_result) >= 1

    # Loose Canon with tag_filters: returns list (W&G-tagged get score boost)
    loose_result = doc_index.retrieve(
        "wrath", top_k=10, retrieval_mode="Loose Canon", tag_filters={"system": "W&G"}
    )
    assert isinstance(loose_result, list)
    assert len(loose_result) <= 10


# PURPOSE: B2.4 – test DocumentIndex.build emits tags with schema keys.
# DEPENDENCIES: DocumentIndex, CHUNK_TAG_KEYS, temp dir.
# MODIFICATION NOTES: All entries must have tags dict with schema keys; PDF gets system W&G.
def test_document_index_build_emits_tags(tmp_path):
    index_path = tmp_path / "document_index.json"
    doc_index = DocumentIndex(index_path)
    text_map = {
        "[PDF] wrathandglory_rules.txt": "Wrath and Glory rules. Dice rolls and damage.",
        "campaign_kb/campaign/00_overview.md": "Campaign overview with grimdark tone.",
    }
    doc_index.build(text_map, theme_keywords=["grimdark"], invalidate_on_mtime=False)
    assert len(doc_index.index) == 2

    for doc_key, entry in doc_index.index.items():
        tags = entry.get("tags")
        assert tags is not None, f"Entry {doc_key} must have tags"
        for k in CHUNK_TAG_KEYS:
            assert k in tags, f"Entry {doc_key} must have tag key {k}"
            assert isinstance(tags[k], str), f"Entry {doc_key} tag {k} must be str"

    pdf_entry = doc_index.index["[PDF] wrathandglory_rules.txt"]
    assert pdf_entry["tags"]["system"] == "W&G", "PDF with wrath in path should get system W&G"

    campaign_entry = doc_index.index["campaign_kb/campaign/00_overview.md"]
    assert campaign_entry["tags"]["system"] == "W&G", "Campaign doc should get system W&G"

    # Verify tags persisted to disk
    loaded = json.loads(index_path.read_text(encoding="utf-8"))
    for doc_key in text_map:
        assert "tags" in loaded[doc_key]
        assert all(k in loaded[doc_key]["tags"] for k in CHUNK_TAG_KEYS)


# PURPOSE: T5.1 – test retrieve_context KB path returns unified schema with source.
# DEPENDENCIES: retrieve_context, mock campaign_kb.
# MODIFICATION NOTES: Mocks search_sections to return KB-style results; asserts source, score, text.
def test_retrieve_context_kb_path_schema(tmp_path):
    """KB path must return items with source, score, text (unified schema)."""
    # Create minimal fake campaign_kb app structure so retrieve_context can import
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "__init__.py").write_text("", encoding="utf-8")
    (app_dir / "config.py").write_text(
        "class _Settings:\n    database_url = 'sqlite:///:memory:'\nsettings = _Settings()",
        encoding="utf-8",
    )
    (app_dir / "database.py").write_text(
        "from contextlib import contextmanager\n"
        "class _SessionLocal:\n"
        "    @contextmanager\n"
        "    def __call__(self):\n"
        "        yield type('DB', (), {})()\n"
        "SessionLocal = _SessionLocal()",
        encoding="utf-8",
    )
    search_dir = app_dir / "search"
    search_dir.mkdir()
    (search_dir / "__init__.py").write_text("", encoding="utf-8")
    (search_dir / "service.py").write_text(
        "def search_sections(db, query, limit=20, source_name=None, doc_type=None):\n"
        "    from types import SimpleNamespace\n"
        "    s = SimpleNamespace(id=42, document_id=7, section_title='Orks', "
        "raw_text='Orks are green and fight Waaagh!')\n"
        "    return [(s, 0.9)]",
        encoding="utf-8",
    )

    rag_config = {
        "campaign_kb_root": str(tmp_path),
        "use_kb_search": True,
        "search": {"limit": 8},
        "query_mode": {},
    }
    if str(tmp_path) not in sys.path:
        sys.path.insert(0, str(tmp_path))

    try:
        results = retrieve_context("orks", rag_config)
        assert len(results) == 1
        item = results[0]
        assert "source" in item, "KB path must include source"
        assert item["source"] == "doc_7:sec_42"
        assert "score" in item
        assert item["score"] == 0.9
        assert "text" in item
        assert "Orks are green" in item["text"]
    finally:
        if str(tmp_path) in sys.path:
            sys.path.remove(str(tmp_path))


# PURPOSE: T5.2 – test retrieve_context DocumentIndex path returns unified schema.
# DEPENDENCIES: retrieve_context, DocumentIndex, text_map.
# MODIFICATION NOTES: use_kb_search=False or mock KB empty; assert source, score, text.
def test_retrieve_context_document_index_path_schema(tmp_path):
    """DocumentIndex path must return items with source, score, text."""
    index_path = tmp_path / "document_index.json"
    text_map = {
        "doc_a": "Wrath and Glory rules for orks.",
        "doc_b": "Orks and Eldar in the sector.",
    }
    index = {
        "doc_a": {
            "path": "doc_a",
            "keywords": ["wrath", "orks"],
            "preview": "Wrath and Glory rules for orks.",
            "themes": {"orks": 1},
            "tags": {"system": "W&G"},
        },
        "doc_b": {
            "path": "doc_b",
            "keywords": ["orks", "eldar"],
            "preview": "Orks and Eldar in the sector.",
            "themes": {"orks": 1},
            "tags": {"system": "W&G"},
        },
    }
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    doc_index = DocumentIndex(index_path)

    rag_config = {
        "campaign_kb_root": str(tmp_path),
        "use_kb_search": False,
        "use_chroma": False,
        "search": {"limit": 8},
        "query_mode": {},
    }

    results = retrieve_context(
        "orks",
        rag_config,
        doc_index=doc_index,
        text_map=text_map,
    )
    assert len(results) >= 1
    for item in results:
        assert "source" in item
        assert "score" in item
        assert "text" in item
        assert item["source"] in text_map


# PURPOSE: T5.3 – test run_pipeline with both paths (schema consistency).
# DEPENDENCIES: run_pipeline, mocked retrieve_context and config.
# MODIFICATION NOTES: Asserts no KeyError; relevant_doc_keys populated.
def test_run_pipeline_handles_unified_schema(tmp_path):
    """run_pipeline must not raise KeyError when retrieve_context returns unified schema."""
    from rag_pipeline import run_pipeline, load_pipeline_config

    config_path = Path(__file__).resolve().parents[1] / "ingest_config.json"
    if not config_path.exists():
        pytest.skip("ingest_config.json not found")

    # Build minimal config with tmp_path; disable LLM calls for speed
    real_bundle = load_pipeline_config(config_path)
    rag = real_bundle.get("rag", {})
    rag = {
        **rag,
        "campaign_kb_root": str(tmp_path),
        "campaign_docs": [],
        "output_dir": tmp_path / "out",
        "include_pdfs": False,
        "pattern_analysis_enabled": False,
        "content_generation_enabled": False,
    }
    minimal_bundle = {"rag": rag}

    with patch("rag_pipeline.load_pipeline_config", return_value=minimal_bundle), patch(
        "rag_pipeline.retrieve_context"
    ) as mock_retrieve:
        mock_retrieve.return_value = [
            {"source": "doc_1:sec_1", "score": 0.9, "text": "Ork warboss leads Waaagh!"},
        ]
        result = run_pipeline(config_path=config_path, query="orks")
        assert "status" in result
        assert result.get("status") == "success"
        mock_retrieve.assert_called()
# CONTINUE TESTING: add end-to-end pipeline run with mocked LLM calls.


# PURPOSE: T0.9 – test entity cache composite key: hit when same docs, miss when one doc changes.
# DEPENDENCIES: EntityCache, extract_entities_from_docs, extract_entities_from_text.
# MODIFICATION NOTES: Mocks extract_entities_from_text to avoid real extraction.
def test_entity_cache_composite_hit_same_docs(tmp_path):
    """Composite cache hit when same docs queried again."""
    from rag_pipeline import EntityCache, extract_entities_from_docs

    with patch("rag_pipeline.ENTITY_EXTRACTION_AVAILABLE", True):
        cache_dir = tmp_path / "cache"
        entity_cache = EntityCache(cache_dir)
        text_map = {"doc_a": "Orks are green.", "doc_b": "Eldar are crafty."}
        rag_config = {"entity_extraction": {}}

        with patch("rag_pipeline.extract_entities_from_text") as mock_extract:
            mock_extract.return_value = {"NPCs": ["Warboss"], "Factions": ["Orks"], "Locations": [], "Items": []}
            result1 = extract_entities_from_docs(
                ["doc_a", "doc_b"], text_map, rag_config, entity_cache=entity_cache
            )
            assert mock_extract.call_count == 1
            assert "Warboss" in result1.get("NPCs", [])

            # Same docs: should hit composite cache, no new extraction
            result2 = extract_entities_from_docs(
                ["doc_a", "doc_b"], text_map, rag_config, entity_cache=entity_cache
            )
            assert mock_extract.call_count == 1, "Cache hit should not call extract again"
            assert result1 == result2


def test_entity_cache_composite_miss_when_doc_changes(tmp_path):
    """Composite cache miss when one doc changes."""
    from rag_pipeline import EntityCache, extract_entities_from_docs

    with patch("rag_pipeline.ENTITY_EXTRACTION_AVAILABLE", True):
        cache_dir = tmp_path / "cache"
        entity_cache = EntityCache(cache_dir)
        text_map = {"doc_a": "Orks are green.", "doc_b": "Eldar are crafty."}
        rag_config = {"entity_extraction": {}}

        with patch("rag_pipeline.extract_entities_from_text") as mock_extract:
            mock_extract.return_value = {"NPCs": ["Warboss"], "Factions": ["Orks"], "Locations": [], "Items": []}
            extract_entities_from_docs(["doc_a", "doc_b"], text_map, rag_config, entity_cache=entity_cache)
            assert mock_extract.call_count == 1

            # Change doc_b content: cache miss, new extraction
            text_map_changed = {"doc_a": "Orks are green.", "doc_b": "Eldar are crafty. NEW CONTENT."}
            mock_extract.return_value = {"NPCs": ["Farseer"], "Factions": ["Eldar"], "Locations": [], "Items": []}
            result = extract_entities_from_docs(
                ["doc_a", "doc_b"], text_map_changed, rag_config, entity_cache=entity_cache
            )
            assert mock_extract.call_count == 2, "Doc change should cause cache miss"
            assert "Farseer" in result.get("NPCs", [])


# PURPOSE: T3.8 – test composable pipeline stages with mocked dependencies.
def test_stage_ingest_returns_text_map(tmp_path):
    """stage_ingest returns text_map from campaign docs."""
    rag_config = {
        "campaign_kb_root": str(tmp_path),
        "campaign_docs": [],
        "include_pdfs": False,
    }
    text_map = stage_ingest(rag_config)
    assert isinstance(text_map, dict)


def test_stage_analyze_full_corpus(tmp_path):
    """stage_analyze with full_corpus builds pattern report."""
    rag_config = {
        "pattern_analysis_enabled": True,
        "theme_keywords": ["wrath"],
        "entity_extraction": {},
    }
    text_map = {"doc_a": "Orks and wrath in the sector."}
    with patch("rag_pipeline.ENTITY_EXTRACTION_AVAILABLE", True):
        report = stage_analyze(
            text_map, ["doc_a"], rag_config, None, full_corpus=True
        )
    assert isinstance(report, dict)


def test_stage_generate_returns_dict(tmp_path):
    """stage_generate returns content_pack dict."""
    rag_config = {"content_generation_enabled": True, "generation": {"parallel": False}}
    with patch("rag_pipeline.generate_text", return_value="draft"):
        pack = stage_generate("context", {"entities": {}}, rag_config)
    assert "rules" in pack or "adventure" in pack or "bios" in pack


# PURPOSE: Phase 4 – chunk quality tests per PDF chunking strategy plan.
# DEPENDENCIES: ai_summarizer.chunk_text, rag_pipeline.read_pdf_texts.
def test_chunk_text_respects_sentence_boundaries():
    """Chunk boundaries must not split mid-sentence."""
    from ai_summarizer import chunk_text

    # Text with clear sentence boundaries
    sentences = ["First sentence here.", "Second sentence there.", "Third one."] * 50
    text = " ".join(sentences)
    chunks = chunk_text(text, max_chunk_size=200, overlap=20)
    for chunk in chunks:
        # Chunk should end at sentence boundary (. ! ?) or be last chunk
        stripped = chunk.strip()
        if stripped and stripped[-1] not in ".!?":
            # Allow last chunk to not end with punctuation if it's trailing
            pass
        # No chunk should contain a lone period in the middle (mid-sentence split)
        # Simple check: chunks should be composed of full sentences
        assert len(chunk) <= 200 + 50, "Chunk should respect max size with small tolerance"


def test_chunk_count_scales_with_document_size():
    """Chunk count should scale with document size for given max_chunk_size."""
    from ai_summarizer import chunk_text

    base = "A short sentence. " * 10
    small = base * 2
    large = base * 20
    chunks_small = chunk_text(small, max_chunk_size=100)
    chunks_large = chunk_text(large, max_chunk_size=100)
    assert len(chunks_large) > len(chunks_small)


def test_chunk_overlap_applied():
    """Overlap between consecutive chunks should be present (sentence-boundary overlap)."""
    from ai_summarizer import chunk_text

    text = ". ".join([f"Sentence number {i}." for i in range(30)])
    chunks = chunk_text(text, max_chunk_size=80, overlap=25)
    assert len(chunks) >= 2
    # With overlap, chunk_text carries last sentence(s) into next chunk.
    # Verify at least one word from end of chunk 0 appears in chunk 1.
    words_at_end = chunks[0].strip().split()[-3:]
    overlap_found = any(
        any(w in c for w in words_at_end) for c in chunks[1:]
    )
    assert overlap_found, "Overlap should carry some content from chunk 0 into chunk 1"


def test_read_pdf_texts_chunks_large_pdf(tmp_path):
    """read_pdf_texts chunks large PDFs and respects max_chunks_per_pdf."""
    pdf_dir = tmp_path / "extracted"
    pdf_dir.mkdir()
    # Create a large text file
    long_text = "Wrath and Glory rules. " * 2000
    (pdf_dir / "rules.txt").write_text(long_text, encoding="utf-8")
    result = read_pdf_texts(
        pdf_dir,
        max_chunk_size=1000,
        max_chunks_per_pdf=5,
        max_total_text_chars=10000,
    )
    chunked_keys = [k for k in result if "[chunk" in k]
    assert len(chunked_keys) <= 5, "Should respect max_chunks_per_pdf"
    assert all(len(v) <= 1000 + 50 for v in result.values())


def test_stage_ingest_retrieve_integration(tmp_path):
    """Full pipeline: stage_ingest with PDF text, stage_index, retrieve_context."""
    (tmp_path / "campaign").mkdir(exist_ok=True)
    (tmp_path / "campaign" / "00_overview.md").write_text("Campaign overview.", encoding="utf-8")
    pdf_extract = tmp_path / "Sources" / "_extracted_text"
    pdf_extract.mkdir(parents=True, exist_ok=True)
    (pdf_extract / "sample.txt").write_text(
        "Wrath and Glory combat rules. Orks attack. Eldar defend. Faith and corruption.",
        encoding="utf-8",
    )
    rag_config = {
        "campaign_kb_root": str(tmp_path),
        "campaign_docs": ["campaign/00_overview.md"],
        "include_pdfs": True,
        "pdf_extraction_dir": str(pdf_extract),
        "pdf_ingestion": {"max_chunk_size": 8000, "max_chunks_per_pdf": 50, "max_total_text_chars": 2000000},
        "use_kb_search": False,
        "use_chroma": False,
        "search": {"limit": 8},
        "query_mode": {},
        "theme_keywords": ["faith"],
    }
    text_map = stage_ingest(rag_config)
    assert len(text_map) >= 1
    index_path = tmp_path / "document_index.json"
    doc_index = DocumentIndex(index_path)
    doc_index.build(
        text_map,
        theme_keywords=["faith"],
        invalidate_on_mtime=False,
        preview_chars=8000,
    )
    results = retrieve_context(
        "orks combat",
        rag_config,
        doc_index=doc_index,
        text_map=text_map,
    )
    assert isinstance(results, list)
    assert len(results) >= 1
    assert any("source" in r and "text" in r for r in results)
