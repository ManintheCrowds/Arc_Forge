# PURPOSE: Allowlist of tools the RAG pipeline can invoke (AI security P6).
# DEPENDENCIES: none
# MODIFICATION NOTES: Vet before adding; only call tools in this registry.

"""
Tool registry: allowlist of AI-invoked tools. Vet before adding.
See D:/local-first/AI_SECURITY.md (Tool registry, JIT access).
"""

ALLOWED_TOOLS = frozenset({
    "ai_summarizer.summarize_text",
    "entity_extractor.extract_entities_from_text",
})


def is_tool_allowed(tool_name: str) -> bool:
    """Return True if tool is in the allowlist."""
    return tool_name in ALLOWED_TOOLS


def ensure_tool_allowed(tool_name: str) -> None:
    """Raise if tool is not in the allowlist."""
    if not is_tool_allowed(tool_name):
        raise ValueError(
            f"Tool '{tool_name}' not in registry. Vet and add to tool_registry.ALLOWED_TOOLS."
        )
