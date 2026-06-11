# PURPOSE: Ensure rag_pipeline never no-ops ensure_tool_allowed when tool_registry is missing.
from unittest.mock import patch

import pytest


def test_ensure_tool_allowed_missing_registry_raises():
    """Fallback used on ImportError must refuse all tool names."""
    from rag_pipeline import _ensure_tool_allowed_missing_registry

    with pytest.raises(RuntimeError, match="tool_registry"):
        _ensure_tool_allowed_missing_registry("ai_summarizer.summarize_text")


def test_tool_registry_allowlist_accepts_known_tools():
    from tool_registry import ensure_tool_allowed

    ensure_tool_allowed("ai_summarizer.summarize_text")
    ensure_tool_allowed("entity_extractor.extract_entities_from_text")
    ensure_tool_allowed("rag_pipeline.generate_text")


def test_generate_text_checks_tool_registry_before_provider_call():
    import rag_pipeline

    with (
        patch.object(rag_pipeline, "SUMMARIZATION_AVAILABLE", True),
        patch.object(rag_pipeline, "ensure_tool_allowed", side_effect=ValueError("denied")) as ensure_allowed,
        patch.object(rag_pipeline, "_call_ollama_api", return_value=("generated", {})) as provider_call,
    ):
        with pytest.raises(ValueError, match="denied"):
            rag_pipeline.generate_text("prompt", {"generation": {"provider": "ollama"}})

    ensure_allowed.assert_called_once_with("rag_pipeline.generate_text")
    provider_call.assert_not_called()
