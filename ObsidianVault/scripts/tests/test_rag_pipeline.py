# PURPOSE: Test stubs for RAG pipeline orchestration.
# DEPENDENCIES: pytest, rag_pipeline, pathlib.
# MODIFICATION NOTES: B3.4 – retrieval_mode tests for DocumentIndex.retrieve.

import json
from pathlib import Path

import pytest

from rag_pipeline import DocumentIndex, load_pipeline_config


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
# CONTINUE TESTING: add end-to-end pipeline run with mocked LLM calls.
