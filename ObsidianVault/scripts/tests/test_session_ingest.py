# PURPOSE: Unit tests for session_ingest (extract_session_summary, run_archivist, run_foreshadowing).
# DEPENDENCIES: pytest, pathlib, unittest.mock; run from ObsidianVault with scripts/ on PYTHONPATH.
# CONTINUE TESTING: Add edge-case tests (empty file, missing config).

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from session_ingest import extract_session_summary, run_archivist, run_foreshadowing


@pytest.fixture
def session_note_with_summary(tmp_path):
    """Session note containing the Session Summary (for Archivist) block."""
    p = tmp_path / "2025-01-27_session.md"
    p.write_text(
        "---\ntitle: Session 3\n---\n\n## Agenda\n- Prep.\n\n"
        "## Session Summary (for Archivist)\n\n"
        "- **Major events:** Fight at depot.\n"
        "- **NPCs interacted with:** Vorlag.\n"
        "- **Unresolved threads:** Smuggler escape.\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def session_note_without_summary(tmp_path):
    """Session note without the Session Summary block."""
    p = tmp_path / "no_summary.md"
    p.write_text("## Agenda\n- Nothing.\n\n## Recap\n- N/A.\n", encoding="utf-8")
    return p


@pytest.fixture
def session_note_malformed(tmp_path):
    """Session note with header-like text but no proper block."""
    p = tmp_path / "malformed.md"
    p.write_text("Session Summary (for Archivist) somewhere in the middle.\nNo ## header.\n", encoding="utf-8")
    return p


def test_extract_session_summary_has_block(session_note_with_summary):
    """extract_session_summary returns non-empty string when block exists."""
    out = extract_session_summary(session_note_with_summary)
    assert isinstance(out, str)
    assert len(out.strip()) > 0
    assert "Major events" in out or "Fight at depot" in out


def test_extract_session_summary_no_block(session_note_without_summary):
    """extract_session_summary returns empty string when block missing."""
    out = extract_session_summary(session_note_without_summary)
    assert out == "" or out.strip() == ""


def test_extract_session_summary_malformed(session_note_malformed):
    """extract_session_summary with text but no ## header returns empty (no ## Session Summary)."""
    out = extract_session_summary(session_note_malformed)
    assert out == "" or out.strip() == ""


def test_extract_session_summary_missing_file():
    """extract_session_summary returns empty for non-existent path."""
    out = extract_session_summary(Path("/nonexistent/session.md"))
    assert out == ""


def test_run_archivist_skips_when_no_summary(session_note_without_summary, tmp_path):
    """run_archivist returns skipped when session note has no Session Summary block."""
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")
    result = run_archivist(session_note_without_summary, config_path, output_path=tmp_path / "out.md")
    assert result.get("status") == "skipped"
    assert "reason" in result


def test_run_archivist_writes_output_with_mocked_llm(session_note_with_summary, tmp_path):
    """run_archivist writes output file when generate_text is mocked."""
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")
    output_path = tmp_path / "archivist_out.md"
    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {}}
    mock_rp.generate_text.return_value = "## Canonical timeline\n- 2025-01-27 | Fight at depot.\n\n## Flagged consequences\n- Smuggler retaliation.\n"

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        result = run_archivist(session_note_with_summary, config_path, output_path=output_path)

    assert result.get("status") == "success"
    assert result.get("output_path") == str(output_path)
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Canonical" in content or "timeline" in content or "Fight" in content


def test_run_foreshadowing_writes_threads_with_mocked_llm(tmp_path):
    """run_foreshadowing appends to threads file when generate_text is mocked."""
    context_path = tmp_path / "context.md"
    context_path.write_text("## Canonical timeline\n- Event.\n\n## Flagged consequences\n- One.\n", encoding="utf-8")
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")
    threads_path = tmp_path / "threads.md"

    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {}}
    mock_rp.generate_text.return_value = "1. Smuggler retaliation (high; 1-2 sessions).\n2. Ork truce collapse (medium).\n"

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        result = run_foreshadowing(context_path, config_path, output_path=threads_path)

    assert result.get("status") == "success"
    assert result.get("output_path") == str(threads_path)
    assert threads_path.exists()
    content = threads_path.read_text(encoding="utf-8")
    assert "Smuggler" in content or "retaliation" in content or "sessions" in content


def test_run_foreshadowing_error_when_context_missing(tmp_path):
    """run_foreshadowing returns error when context file does not exist."""
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")
    result = run_foreshadowing(tmp_path / "nonexistent.md", config_path)
    assert result.get("status") == "error"
    assert "reason" in result
