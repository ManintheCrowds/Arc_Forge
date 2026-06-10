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
    ensure_tool_allowed("rag_pipeline.generate_text")


def test_generate_text_checks_tool_registry_before_provider_call(monkeypatch):
    import rag_pipeline

    def deny_tool(tool_name):
        raise RuntimeError(f"blocked {tool_name}")

    def provider_should_not_run(*args, **kwargs):
        raise AssertionError("provider helper should not run when registry denies generate_text")

    monkeypatch.setattr(rag_pipeline, "SUMMARIZATION_AVAILABLE", True)
    monkeypatch.setattr(rag_pipeline, "ensure_tool_allowed", deny_tool)
    monkeypatch.setattr(rag_pipeline, "_call_ollama_api", provider_should_not_run)

    with pytest.raises(RuntimeError, match="blocked rag_pipeline.generate_text"):
        rag_pipeline.generate_text("prompt", {"generation": {"provider": "ollama"}})
