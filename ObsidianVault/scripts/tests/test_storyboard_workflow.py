# PURPOSE: Backend unit tests for storyboard_workflow entry points (run_stage_1, run_stage_2, refine_encounter, export_final_specs).
# DEPENDENCIES: pytest, pathlib, unittest.mock; run from ObsidianVault with scripts/ on PYTHONPATH (e.g. pytest scripts/tests/test_storyboard_workflow.py -v).
# CONTINUE TESTING: Path traversal is in workflow_ui (api_arc_file); edge-case tests added here.

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is on path so "from storyboard_workflow import ..." and storyboard_workflow's "from rag_pipeline import ..." resolve.
_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from storyboard_workflow import export_final_specs, refine_encounter, run_stage_1, run_stage_2


@pytest.fixture
def tmp_storyboard(tmp_path):
    """Minimal storyboard with numbered sections (I. II. III.) for run_stage_1."""
    p = tmp_path / "storyboard.md"
    p.write_text(
        "I. Introduction\n\nII. Highway Chase\n\nIII. Boarding Action\n\nIV. Conclusion\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def tmp_task_decomposition(tmp_path):
    """Minimal task_decomposition.yaml for run_stage_2."""
    td = tmp_path / "task_decomposition.yaml"
    td.write_text(
        "arc_id: test_arc\n"
        "encounters:\n"
        "  - id: highway_chase\n"
        "    name: Highway Chase\n"
        "    type: combat\n"
        "    sequence: 1\n"
        "    storyboard_section: II. Highway Chase\n"
        "opportunities: []\n",
        encoding="utf-8",
    )
    return td


def test_run_stage_1_writes_task_decomposition(tmp_storyboard, tmp_path):
    """run_stage_1 produces task_decomposition.md and .yaml under output_dir/arc_id."""
    out_dir = tmp_path / "campaigns"
    out_dir.mkdir()
    result = run_stage_1(tmp_storyboard, arc_id="test_arc", output_dir=out_dir)
    assert set(result.keys()) >= {"status", "encounters", "opportunities", "md_path", "data_path"}
    assert result.get("status") == "success"
    assert "encounters" in result
    assert "md_path" in result
    assert "data_path" in result
    arc_dir = out_dir / "test_arc"
    assert (arc_dir / "task_decomposition.md").exists()
    assert (arc_dir / "task_decomposition.yaml").exists() or (arc_dir / "task_decomposition.json").exists()
    data_path = Path(result["data_path"])
    assert data_path.exists()


def test_run_stage_2_writes_drafts_with_mocked_draft(tmp_task_decomposition, tmp_path):
    """run_stage_2 writes encounter drafts when draft_encounter is mocked (no RAG/LLM)."""
    story_path = tmp_path / "storyboard.md"
    story_path.write_text("II. Highway Chase\n", encoding="utf-8")
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {"campaign_kb_root": ""}}', encoding="utf-8")
    output_dir = tmp_path / "test_arc"
    output_dir.mkdir()

    mock_draft = MagicMock(return_value="# Highway Chase\n\n## Setup\nPlaceholder.\n")
    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {"campaign_kb_root": str(tmp_path)}}

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        with patch("storyboard_workflow.draft_encounter", mock_draft):
            result = run_stage_2(
                tmp_task_decomposition, story_path, "test_arc", config_path, output_dir
            )
    assert set(result.keys()) >= {"status", "written", "encounters", "opportunities"}
    assert result.get("status") == "success"
    assert "written" in result
    assert result.get("encounters", 0) >= 1
    enc_dir = output_dir / "encounters"
    assert enc_dir.exists()
    drafts = list(enc_dir.glob("*_draft_v1.md"))
    assert len(drafts) >= 1


def test_refine_encounter_writes_next_draft_with_mocked_llm(tmp_path):
    """refine_encounter produces _draft_v2 when generate_text is mocked."""
    enc_dir = tmp_path / "encounters"
    enc_dir.mkdir()
    draft = enc_dir / "highway_chase_draft_v1.md"
    draft.write_text("# Highway Chase\n\n## Setup\nOriginal.\n", encoding="utf-8")
    feedback = tmp_path / "test_arc_feedback.yaml"
    feedback.write_text(
        "encounters:\n"
        "  - id: highway_chase\n"
        "    feedback:\n"
        "      - type: expand\n"
        "        target: Mechanics\n"
        "        instruction: Add Pilot (Agi) DN 4.\n",
        encoding="utf-8",
    )
    mock_rp = MagicMock()
    mock_rp.generate_text.return_value = "# Highway Chase\n\n## Setup\nRevised.\n\n## Mechanics\n- Pilot (Agi) DN 4.\n"

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        result = refine_encounter(draft, feedback, rag_config={"rag": {}})
    assert set(result.keys()) >= {"status", "output_path", "encounter_id", "version"}
    assert result.get("status") == "success"
    assert "output_path" in result
    assert "encounter_id" in result
    assert result.get("encounter_id") == "highway_chase"
    out_path = Path(result["output_path"])
    assert out_path.exists()
    assert "v2" in out_path.name or "draft_v2" in out_path.name


def test_refine_encounter_error_when_generate_text_empty(tmp_path):
    """refine_encounter returns error when generate_text returns empty; no output file created."""
    enc_dir = tmp_path / "encounters"
    enc_dir.mkdir()
    draft = enc_dir / "highway_chase_draft_v1.md"
    draft.write_text("# Highway Chase\n\n## Setup\nOriginal.\n", encoding="utf-8")
    feedback = tmp_path / "test_arc_feedback.yaml"
    feedback.write_text(
        "encounters:\n"
        "  - id: highway_chase\n"
        "    feedback:\n"
        "      - type: expand\n"
        "        target: Mechanics\n"
        "        instruction: Add Pilot (Agi) DN 4.\n",
        encoding="utf-8",
    )
    mock_rp = MagicMock()
    mock_rp.generate_text.return_value = ""

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        result = refine_encounter(draft, feedback, rag_config={"rag": {}})
    assert result.get("status") == "error"
    assert "generate_text returned empty" in result.get("reason", "")
    # No _draft_v2.md should exist
    v2_files = list(enc_dir.glob("*_draft_v2.md"))
    assert len(v2_files) == 0


def test_refine_encounter_skipped_when_no_feedback(tmp_path):
    """refine_encounter returns skipped when feedback has no entry for that encounter."""
    enc_dir = tmp_path / "encounters"
    enc_dir.mkdir()
    draft = enc_dir / "other_encounter_draft_v1.md"
    draft.write_text("# Other\n", encoding="utf-8")
    feedback = tmp_path / "feedback.yaml"
    feedback.write_text("encounters:\n  - id: other_id\n    feedback: []\n", encoding="utf-8")
    result = refine_encounter(draft, feedback, rag_config={})
    assert result.get("status") == "skipped"
    assert "reason" in result


def test_export_final_specs_error_when_no_encounters(tmp_path):
    """export_final_specs returns error when arc dir has no encounter/opportunity files."""
    arc_dir = tmp_path / "test_arc"
    arc_dir.mkdir()
    campaign_kb = tmp_path / "campaign_kb"
    campaign_kb.mkdir()

    result = export_final_specs("test_arc", arc_dir, campaign_kb)
    assert result.get("status") == "error"
    assert "No encounter/opportunity files found" in result.get("reason", "")


def test_run_stage_2_empty_encounters_returns_success_no_files(tmp_path):
    """run_stage_2 returns success with written=[] when task_decomposition has no encounters/opportunities."""
    td = tmp_path / "task_decomposition.yaml"
    td.write_text(
        "arc_id: test_arc\nencounters: []\nopportunities: []\n",
        encoding="utf-8",
    )
    story_path = tmp_path / "storyboard.md"
    story_path.write_text("II. Highway Chase\n", encoding="utf-8")
    config_path = tmp_path / "ingest_config.json"
    config_path.write_text('{"rag": {"campaign_kb_root": ""}}', encoding="utf-8")
    output_dir = tmp_path / "test_arc"
    output_dir.mkdir()

    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {"campaign_kb_root": str(tmp_path)}}

    with patch.dict(sys.modules, {"rag_pipeline": mock_rp}):
        result = run_stage_2(td, story_path, "test_arc", config_path, output_dir)
    assert result.get("status") == "success"
    assert result.get("written") == []
    assert result.get("encounters", 0) == 0
    assert result.get("opportunities", 0) == 0
    enc_dir = output_dir / "encounters"
    opp_dir = output_dir / "opportunities"
    assert enc_dir.exists()
    assert opp_dir.exists()
    assert len(list(enc_dir.glob("*_draft_v1.md"))) == 0
    assert len(list(opp_dir.glob("*_draft_v1.md"))) == 0


def test_run_stage_1_raises_when_storyboard_missing(tmp_path):
    """run_stage_1 raises FileNotFoundError when storyboard path does not exist."""
    missing = tmp_path / "nonexistent_storyboard.md"
    out_dir = tmp_path / "campaigns"
    out_dir.mkdir()
    assert not missing.exists()
    with pytest.raises(FileNotFoundError):
        run_stage_1(missing, arc_id="test_arc", output_dir=out_dir)


def test_export_final_specs_produces_expanded_and_json(tmp_path):
    """export_final_specs writes expanded storyboard, encounters JSON, and returns paths."""
    arc_dir = tmp_path / "test_arc"
    enc_dir = arc_dir / "encounters"
    enc_dir.mkdir(parents=True)
    (enc_dir / "highway_chase_draft_v1.md").write_text("# Highway Chase\n\nSetup.\n", encoding="utf-8")
    campaign_kb = tmp_path / "campaign_kb"
    campaign_kb.mkdir()
    story_path = tmp_path / "storyboard.md"
    story_path.write_text("I. Intro\nII. Chase\n", encoding="utf-8")

    result = export_final_specs(
        "test_arc", arc_dir, campaign_kb, storyboard_path=story_path, vault_root=tmp_path
    )
    assert set(result.keys()) >= {"status", "final_md", "expanded_storyboard", "json_path", "campaign_kb_path"}
    assert result.get("status") == "success"
    expanded = arc_dir / "test_arc_expanded_storyboard.md"
    assert expanded.exists()
    assert "Chase" in expanded.read_text(encoding="utf-8")
    json_path = arc_dir / "test_arc_encounters.json"
    assert json_path.exists()
    import json as _json
    data = _json.loads(json_path.read_text(encoding="utf-8"))
    assert data.get("arc_id") == "test_arc"
    assert "encounters" in data and len(data["encounters"]) >= 1
