# PURPOSE: Unit tests for frame_workflow (run_story_architect).
# DEPENDENCIES: pytest, pathlib, unittest.mock; run from ObsidianVault with scripts/ on PYTHONPATH.
# CONTINUE TESTING: Add tests for missing premise/arc_state, empty generate_text.

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from frame_workflow import run_story_architect

MOCK_FRAME_OUTPUT = """## Framework A: Highway Chase
**Hook:** The convoy is ambushed; one cargo must be abandoned.

- Ambush; choice of cargo.
- Chase or stand; consequence for delay.
- Arrival; faction reaction.

## Framework B: Negotiation Gone Wrong
**Hook:** The smuggler demands a tribute.

- Meet; demand.
- Refuse or pay; escalation.
- Outcome.

## Framework C: Depot Siege
**Hook:** The depot is under attack.

- Approach; scouts.
- Assault; key objectives.
- Aftermath.
"""


@pytest.fixture
def premise_and_arc(tmp_path):
    """Minimal premise and arc state files."""
    premise = tmp_path / "premise.md"
    premise.write_text("Grimdark W&G campaign. Inquisition vs smugglers.\n", encoding="utf-8")
    arc = tmp_path / "arc_state.md"
    arc.write_text("Current arc: first_arc. Last session: depot raid.\n", encoding="utf-8")
    return premise, arc


def test_run_story_architect_writes_file_with_mocked_llm(premise_and_arc, tmp_path):
    """run_story_architect writes output file when generate_text is mocked."""
    premise_path, arc_state_path = premise_and_arc
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")
    output_path = tmp_path / "frame_out.md"

    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {}}
    mock_rp.generate_text.return_value = MOCK_FRAME_OUTPUT

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        result = run_story_architect(
            premise_path,
            arc_state_path,
            config_path,
            output_path=output_path,
        )

    assert result.get("status") == "success"
    assert result.get("output_path") == str(output_path)
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Framework A" in content
    assert "Framework B" in content
    assert "Framework C" in content
    assert "Hook:" in content
    assert content.count("## ") >= 3


def test_run_story_architect_output_has_expected_structure(premise_and_arc, tmp_path):
    """Output contains at least three sections and bullet-like content (beats)."""
    premise_path, arc_state_path = premise_and_arc
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")
    output_path = tmp_path / "frame_out.md"

    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {}}
    mock_rp.generate_text.return_value = MOCK_FRAME_OUTPUT

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        run_story_architect(
            premise_path,
            arc_state_path,
            config_path,
            output_path=output_path,
        )

    content = output_path.read_text(encoding="utf-8")
    sections = [s for s in content.split("## ") if s.strip() and not s.strip().startswith("#")]
    assert len(sections) >= 3
    assert "- " in content or "* " in content


def test_run_story_architect_error_when_premise_missing(tmp_path):
    """run_story_architect returns error when premise file does not exist."""
    arc_state = tmp_path / "arc_state.md"
    arc_state.write_text("Arc state.\n", encoding="utf-8")
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")

    result = run_story_architect(
        tmp_path / "nonexistent_premise.md",
        arc_state,
        config_path,
    )
    assert result.get("status") == "error"
    assert "reason" in result
    assert "premise" in result["reason"].lower() or "not found" in result["reason"].lower()


def test_run_story_architect_error_when_arc_state_missing(tmp_path):
    """run_story_architect returns error when arc state file does not exist."""
    premise = tmp_path / "premise.md"
    premise.write_text("Premise.\n", encoding="utf-8")
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {}}', encoding="utf-8")

    result = run_story_architect(
        premise,
        tmp_path / "nonexistent_arc.md",
        config_path,
    )
    assert result.get("status") == "error"
    assert "reason" in result
