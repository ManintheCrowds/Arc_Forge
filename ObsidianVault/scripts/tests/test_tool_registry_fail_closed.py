# PURPOSE: Ensure rag_pipeline never no-ops ensure_tool_allowed when tool_registry is missing.
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
