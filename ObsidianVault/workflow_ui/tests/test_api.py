# PURPOSE: API route tests for workflow_ui. Uses tmp Campaigns and mocks for run stages.
# DEPENDENCIES: pytest, flask, workflow_ui.app (run from ObsidianVault).
# CONTINUE TESTING: Add storyboard_workflow unit tests if desired (see docs/DEVELOPMENT_PLAN_REMAINING.md).

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import app from parent vault; run tests with cwd=ObsidianVault or PYTHONPATH including it.
import sys
_VAULT = Path(__file__).resolve().parent.parent.parent
if str(_VAULT) not in sys.path:
    sys.path.insert(0, str(_VAULT))

import importlib.util
_wf_app_spec = importlib.util.find_spec("workflow_ui.app")
_wf_app_mod = importlib.util.module_from_spec(_wf_app_spec)
_VAULT_STR = str(_VAULT)
if _VAULT_STR not in sys.path:
    sys.path.insert(0, _VAULT_STR)
_wf_app_spec.loader.exec_module(_wf_app_mod)
app_module = _wf_app_mod
_flask_app = getattr(app_module, "app")


@pytest.fixture
def tmp_campaigns(tmp_path):
    campaigns = tmp_path / "Campaigns"
    campaigns.mkdir()
    return campaigns


@pytest.fixture
def client(tmp_campaigns):
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        app_module.app.config["TESTING"] = True
        app_module.app.config["RATELIMIT_ENABLED"] = False  # disable for most tests
        with app_module.app.test_client() as c:
            yield c


def test_get_api_arcs_empty(client):
    r = client.get("/api/arcs")
    assert r.status_code == 200
    data = r.get_json()
    assert "arcs" in data
    assert data["arcs"] == []


def test_get_api_arcs_with_dirs(client, tmp_campaigns):
    (tmp_campaigns / "first_arc").mkdir()
    (tmp_campaigns / "second_arc").mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arcs")
    assert r.status_code == 200
    data = r.get_json()
    assert set(data["arcs"]) == {"first_arc", "second_arc"}


def test_get_api_arc_tree_missing(client):
    r = client.get("/api/arc/nonexistent_arc/tree")
    assert r.status_code == 200
    data = r.get_json()
    assert data["arc_id"] == "nonexistent_arc"
    assert data["files"] == []
    assert data["encounters"] == []
    assert data["opportunities"] == []


def test_get_api_arc_tree_exists(client, tmp_campaigns):
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    (arc / "task_decomposition.yaml").write_text("arc_id: test_arc\nencounters: []\n")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/tree")
    assert r.status_code == 200
    data = r.get_json()
    assert data["arc_id"] == "test_arc"
    assert any(f["name"] == "task_decomposition.yaml" for f in data["files"])


def test_get_api_arc_artifacts(client, tmp_campaigns):
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/artifacts")
    assert r.status_code == 200
    data = r.get_json()
    assert "task_decomposition" in data
    assert "feedback" in data
    assert "has_encounters" in data


def test_get_task_decomposition_404(client, tmp_campaigns):
    (tmp_campaigns / "empty_arc").mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/empty_arc/task_decomposition")
    assert r.status_code == 404


def test_put_get_task_decomposition(client, tmp_campaigns):
    (tmp_campaigns / "test_arc").mkdir()
    body = {
        "arc_id": "test_arc",
        "storyboard_ref": "_rag_outputs/storyboard.md",
        "encounters": [{"id": "e1", "name": "Enc 1", "type": "combat", "sequence": 1}],
        "opportunities": [],
        "sequence_constraints": ["e1 first"],
    }
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.put(
            "/api/arc/test_arc/task_decomposition",
            json=body,
            content_type="application/json",
        )
    assert r.status_code == 200
    path = tmp_campaigns / "test_arc" / "task_decomposition.yaml"
    assert path.exists()
    r2 = client.get("/api/arc/test_arc/task_decomposition")
    assert r2.status_code == 200
    data = r2.get_json()
    assert data["arc_id"] == "test_arc"
    assert len(data["encounters"]) == 1
    assert data["encounters"][0]["id"] == "e1"


def test_get_feedback_empty(client, tmp_campaigns):
    (tmp_campaigns / "test_arc").mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/feedback")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("arc_id") == "test_arc"
    assert data.get("encounters", []) == []


def test_put_get_feedback(client, tmp_campaigns):
    (tmp_campaigns / "test_arc").mkdir()
    body = {
        "arc_id": "test_arc",
        "encounters": [{"id": "e1", "feedback": [{"type": "expand", "target": "x", "instruction": "add"}]}],
    }
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.put("/api/arc/test_arc/feedback", json=body, content_type="application/json")
    assert r.status_code == 200
    r2 = client.get("/api/arc/test_arc/feedback")
    assert r2.status_code == 200
    data = r2.get_json()
    assert len(data["encounters"]) == 1
    assert data["encounters"][0]["feedback"][0]["type"] == "expand"


def test_get_arc_file_404(client, tmp_campaigns):
    (tmp_campaigns / "test_arc").mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/file/nonexistent.md")
    assert r.status_code == 404


def test_get_arc_file_ok(client, tmp_campaigns):
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    (arc / "foo.md").write_text("# Hello", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/file/foo.md")
    assert r.status_code == 200
    assert b"Hello" in r.data


def test_get_arc_file_path_traversal_rejected(client, tmp_campaigns):
    (tmp_campaigns / "test_arc").mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r1 = client.get("/api/arc/test_arc/file/../foo.md")
        r2 = client.get("/api/arc/test_arc/file/encounters/../../campaign_kb/data/kb.sqlite3")
        r3 = client.get("/api/arc/test_arc/file/foo.md", headers={})  # normal; 404 is ok
    assert r1.status_code == 400
    assert r2.status_code == 400
    data1 = r1.get_json()
    assert data1.get("error") == "invalid path"


def test_get_arc_file_url_encoded_traversal_rejected(client, tmp_campaigns):
    """URL-encoded .. in subpath is decoded by Flask and rejected (400)."""
    (tmp_campaigns / "test_arc").mkdir()
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/file/..%2ffoo.md")
    assert r.status_code == 400
    assert r.get_json().get("error") == "invalid path"


def test_get_arc_file_arc_id_edge_case_safe(client, tmp_campaigns):
    """arc_id that secure_filename strips to empty (e.g. ....) falls back to first_arc; no escape."""
    (tmp_campaigns / "first_arc").mkdir()
    (tmp_campaigns / "first_arc" / "task_decomposition.yaml").write_text("arc_id: first_arc\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/..../file/task_decomposition.yaml")
    assert r.status_code == 200
    assert b"first_arc" in r.data


def test_get_arc_file_redundant_segments_allowed(client, tmp_campaigns):
    """Subpath with redundant segments (foo/../foo.md) resolves under arc and is allowed."""
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    (arc / "sub").mkdir()
    (arc / "sub" / "foo.md").write_text("# Foo\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/arc/test_arc/file/sub/../sub/foo.md")
    assert r.status_code == 200
    assert b"Foo" in r.data


def test_post_run_stage1_missing_storyboard(client, tmp_campaigns):
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/run/stage1",
            json={"arc_id": "test_arc", "storyboard_path": str(tmp_campaigns / "missing.md")},
            content_type="application/json",
        )
    assert r.status_code == 400
    assert "not found" in r.get_json().get("reason", "").lower()


def test_post_run_stage1_ok(client, tmp_campaigns):
    rag = tmp_campaigns / "_rag_outputs"
    rag.mkdir()
    (rag / "first_arc_storyboard.md").write_text("I. Intro\nII. Scene\nIII. Combat (Chase)\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/run/stage1",
            json={
                "arc_id": "test_arc",
                "storyboard_path": str(rag / "first_arc_storyboard.md"),
                "output_dir": str(tmp_campaigns),
            },
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "success"
    td_yaml = tmp_campaigns / "test_arc" / "task_decomposition.yaml"
    assert td_yaml.exists()


def test_index_returns_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Storyboard" in r.data or b"storyboard" in r.data.lower()
    assert b"style.css" in r.data or b"url_for" not in r.data  # render_template resolves url_for
    # After fix, template is rendered so we get actual URLs, not literal {{ url_for }}
    assert b"static" in r.data or b"style" in r.data


def test_index_includes_kb_workflows_link(client):
    """Index page must include KB Workflows nav link (href /tools/kb-daggr or text)."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.data
    assert b"/tools/kb-daggr" in data or b"KB Workflows" in data
    assert b"/tools/gradio" in data or b"Gradio demo" in data


def test_post_run_stage2_ok(client, tmp_campaigns):
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    (arc / "task_decomposition.yaml").write_text("arc_id: test_arc\nencounters: []\n", encoding="utf-8")
    rag = tmp_campaigns / "_rag_outputs"
    rag.mkdir()
    (rag / "first_arc_storyboard.md").write_text("# Storyboard\n", encoding="utf-8")
    td_path = str((arc / "task_decomposition.yaml").resolve())
    story_path = str((rag / "first_arc_storyboard.md").resolve())
    mock_run = MagicMock(return_value={"status": "success"})
    with patch.object(app_module, "run_stage_2", mock_run):
        r = client.post(
            "/api/run/stage2",
            json={"arc_id": "test_arc", "task_decomposition_path": td_path, "storyboard_path": story_path},
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "success"
    assert mock_run.called


def test_post_run_stage4_ok(client, tmp_campaigns):
    mock_rp = MagicMock()
    mock_rp.load_pipeline_config.return_value = {"rag": {}}
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    enc_dir = arc / "encounters"
    enc_dir.mkdir()
    draft_file = enc_dir / "foo_draft_v1.md"
    draft_file.write_text("# Draft v1\n", encoding="utf-8")
    (arc / "test_arc_feedback.yaml").write_text("encounters: []\n", encoding="utf-8")
    mock_refine = MagicMock(return_value={"status": "success", "path": "/some/draft_v2.md"})
    with patch.dict(sys.modules, {"scripts.rag_pipeline": mock_rp}):
        with patch.object(app_module, "refine_encounter", mock_refine):
            r = client.post(
                "/api/run/stage4",
                json={"arc_id": "test_arc", "draft_path": str(draft_file.resolve())},
                content_type="application/json",
            )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "success"
    assert mock_refine.called
    args = mock_refine.call_args[0]
    assert str(draft_file.resolve()) in str(args[0]) or draft_file.name in str(args[0])
    assert "feedback" in str(args[1]).lower() or "test_arc_feedback" in str(args[1])


def test_post_run_stage5_ok(client, tmp_campaigns):
    arc = tmp_campaigns / "test_arc"
    arc.mkdir()
    (arc / "encounters").mkdir()
    (arc / "encounters" / "foo_draft_v1.md").write_text("# Encounter\n", encoding="utf-8")
    mock_export = MagicMock(return_value={"status": "success", "paths": {}})
    with patch.object(app_module, "export_final_specs", mock_export):
        r = client.post(
            "/api/run/stage5",
            json={"arc_id": "test_arc"},
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "success"
    assert mock_export.called


@pytest.fixture
def client_with_limiter(tmp_campaigns):
    """Client with rate limiting enabled (for rate-limit tests only). Fresh limiter state per test."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        app_module.app.config["TESTING"] = True
        app_module.app.config["RATELIMIT_ENABLED"] = True
        app_module.limiter.reset()
        with app_module.app.test_client() as c:
            yield c


def test_ratelimit_run_stage_exceeds_returns_429(client_with_limiter, tmp_campaigns):
    """Exceeding /api/run/stage1 limit (30/min) returns 429 and JSON body."""
    rag = tmp_campaigns / "_rag_outputs"
    rag.mkdir()
    (rag / "first_arc_storyboard.md").write_text("# Storyboard\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        with patch.object(app_module, "run_stage_1", MagicMock(return_value={"status": "success"})):
            for _ in range(30):
                r = client_with_limiter.post(
                    "/api/run/stage1",
                    json={
                        "arc_id": "test_arc",
                        "storyboard_path": str(rag / "first_arc_storyboard.md"),
                        "output_dir": str(tmp_campaigns),
                    },
                    content_type="application/json",
                )
                assert r.status_code == 200, f"Request within limit should be 200, got {r.status_code}"
            r31 = client_with_limiter.post(
                "/api/run/stage1",
                json={
                    "arc_id": "test_arc",
                    "storyboard_path": str(rag / "first_arc_storyboard.md"),
                    "output_dir": str(tmp_campaigns),
                },
                content_type="application/json",
            )
    assert r31.status_code == 429
    data = r31.get_json()
    assert data.get("error") == "rate limit exceeded"


def test_ratelimit_under_limit_returns_200(client_with_limiter, tmp_campaigns):
    """Under limit, /api/run/stage1 returns 200."""
    rag = tmp_campaigns / "_rag_outputs"
    rag.mkdir()
    (rag / "first_arc_storyboard.md").write_text("# Storyboard\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        with patch.object(app_module, "run_stage_1", MagicMock(return_value={"status": "success"})):
            r = client_with_limiter.post(
                "/api/run/stage1",
                json={
                    "arc_id": "test_arc",
                    "storyboard_path": str(rag / "first_arc_storyboard.md"),
                    "output_dir": str(tmp_campaigns),
                },
                content_type="application/json",
            )
    assert r.status_code == 200
    assert r.get_json().get("status") == "success"


def test_validate_startup_paths_missing_campaigns():
    """_validate_startup_paths returns error when CAMPAIGNS does not exist."""
    with patch.object(app_module, "CAMPAIGNS", Path("/nonexistent/campaigns_dir")):
        with patch.object(app_module, "CONFIG_PATH", Path(__file__).resolve()):  # exists (this file's dir)
            errors = app_module._validate_startup_paths()
    assert any("CAMPAIGNS not found" in e for e in errors)


def test_validate_startup_paths_missing_config():
    """_validate_startup_paths returns error when CONFIG_PATH does not exist."""
    with patch.object(app_module, "CAMPAIGNS", Path(__file__).resolve().parent):  # exists
        with patch.object(app_module, "CONFIG_PATH", Path("/nonexistent/ingest_config.json")):
            errors = app_module._validate_startup_paths()
    assert any("CONFIG_PATH missing" in e for e in errors)


def test_validate_startup_paths_ok(tmp_path):
    """_validate_startup_paths returns no errors when paths exist."""
    campaigns = tmp_path / "Campaigns"
    campaigns.mkdir()
    config_file = tmp_path / "ingest_config.json"
    config_file.write_text("{}", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", campaigns):
        with patch.object(app_module, "CONFIG_PATH", config_file):
            errors = app_module._validate_startup_paths()
    assert errors == []


def test_get_session_files_empty(client, tmp_campaigns):
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/session/files")
    assert r.status_code == 200
    data = r.get_json()
    assert "files" in data
    assert data["files"] == []


def test_get_session_files_ok(client, tmp_campaigns):
    memory = tmp_campaigns / "_session_memory"
    memory.mkdir(parents=True, exist_ok=True)
    (memory / "2025-01-30_archivist.md").write_text("# Archivist\n", encoding="utf-8")
    (memory / "threads.md").write_text("# Threads\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/session/files")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data["files"]) == 2
    names = {f["name"] for f in data["files"]}
    assert "2025-01-30_archivist.md" in names
    assert "threads.md" in names
    for f in data["files"]:
        assert "path" in f and "name" in f


def test_get_session_file_404(client, tmp_campaigns):
    memory = tmp_campaigns / "_session_memory"
    memory.mkdir(parents=True, exist_ok=True)
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/session/file/nonexistent.md")
    assert r.status_code == 404


def test_get_session_file_ok(client, tmp_campaigns):
    memory = tmp_campaigns / "_session_memory"
    memory.mkdir(parents=True, exist_ok=True)
    (memory / "out.md").write_text("# Session memory\n", encoding="utf-8")
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/session/file/out.md")
    assert r.status_code == 200
    assert b"Session memory" in r.data


def test_post_session_archivist_missing_path(client):
    r = client.post(
        "/api/session/archivist",
        json={},
        content_type="application/json",
    )
    assert r.status_code == 400
    assert "session_path" in r.get_json().get("reason", "").lower()


def test_post_session_archivist_ok(client, tmp_campaigns):
    session_note = tmp_campaigns / "session_note.md"
    session_note.write_text("# Session\n\n## Session Summary (for Archivist)\n\nStuff happened.\n", encoding="utf-8")
    mock_archivist = MagicMock(return_value={"status": "success", "output_path": str(tmp_campaigns / "_session_memory" / "out.md")})
    with patch.object(app_module, "run_archivist", mock_archivist):
        r = client.post(
            "/api/session/archivist",
            json={"session_path": str(session_note.resolve())},
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "success"
    assert data.get("output_path")
    assert mock_archivist.called


def test_post_session_foreshadow_missing_path(client):
    r = client.post(
        "/api/session/foreshadow",
        json={},
        content_type="application/json",
    )
    assert r.status_code == 400
    assert "context_path" in r.get_json().get("reason", "").lower()


def test_post_session_foreshadow_ok(client, tmp_campaigns):
    context_file = tmp_campaigns / "_session_memory" / "context.md"
    context_file.parent.mkdir(parents=True, exist_ok=True)
    context_file.write_text("# Archivist output\n", encoding="utf-8")
    mock_foreshadow = MagicMock(return_value={"status": "success", "output_path": str(tmp_campaigns / "_session_memory" / "threads.md")})
    with patch.object(app_module, "run_foreshadowing", mock_foreshadow):
        r = client.post(
            "/api/session/foreshadow",
            json={"context_path": str(context_file.resolve())},
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "success"
    assert data.get("output_path")
    assert mock_foreshadow.called


# --- Daggr integration verification: /tools/kb-daggr redirect (plan 3.3) ---


def test_tools_kb_daggr_returns_302(client):
    """GET /tools/kb-daggr must return 302."""
    r = client.get("/tools/kb-daggr")
    assert r.status_code == 302


def test_tools_kb_daggr_location_header(client):
    """GET /tools/kb-daggr Location must equal CAMPAIGN_KB_DAGGR_URL (or default)."""
    r = client.get("/tools/kb-daggr")
    assert r.status_code == 302
    expected = getattr(app_module, "CAMPAIGN_KB_DAGGR_URL", "http://localhost:7860")
    assert r.headers.get("Location") == expected


# --- Gradio integration: /tools/gradio redirect ---


def test_tools_gradio_returns_302(client):
    """GET /tools/gradio must return 302."""
    r = client.get("/tools/gradio")
    assert r.status_code == 302


def test_tools_gradio_location_header(client):
    """GET /tools/gradio Location must equal GRADIO_APP_URL (or default)."""
    r = client.get("/tools/gradio")
    assert r.status_code == 302
    expected = getattr(app_module, "GRADIO_APP_URL", "http://localhost:7861")
    assert r.headers.get("Location") == expected


# --- Workbench Phase 3 API tests ---


def test_workbench_idea_web(client, tmp_campaigns):
    """GET /api/workbench/idea-web returns nodes/edges from .md with tags + wikilinks."""
    arc = tmp_campaigns / "first_arc"
    arc.mkdir()
    (arc / "scene_a.md").write_text(
        "---\ntitle: Scene A\ntype: scene\ntags: [combat, intro]\n---\n\nPlot [[scene_b]] and [[npc_1]].\n",
        encoding="utf-8",
    )
    (arc / "scene_b.md").write_text(
        "---\ntitle: Scene B\ntype: scene\ntags: [drama]\n---\n\nFollow-up.\n",
        encoding="utf-8",
    )
    (arc / "npc_1.md").write_text(
        "---\ntitle: NPC 1\ntype: npc\ntags: [ally]\n---\n\nCharacter.\n",
        encoding="utf-8",
    )
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/workbench/idea-web?campaign=first_arc")
    assert r.status_code == 200
    data = r.get_json()
    assert "nodes" in data and "edges" in data
    assert len(data["nodes"]) >= 3
    assert any(e["from"] == "first_arc/scene_a.md" and e["to"] == "first_arc/scene_b.md" for e in data["edges"]) or any(
        e["from"] == "first_arc/scene_a.md" and e["to"] == "first_arc/npc_1.md" for e in data["edges"]
    )


def test_workbench_idea_web_invalid_campaign(client, tmp_campaigns):
    """GET /api/workbench/idea-web with invalid campaign returns 400."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/workbench/idea-web?campaign=_internal")
    assert r.status_code == 400


def test_workbench_dependencies(client, tmp_campaigns):
    """GET /api/workbench/dependencies returns nodes/edges from depends_on frontmatter."""
    arc = tmp_campaigns / "first_arc"
    arc.mkdir()
    (arc / "task_a.md").write_text(
        "---\ntitle: Task A\ntype: task\ndepends_on: [task_b]\n---\n\nNeeds B.\n",
        encoding="utf-8",
    )
    (arc / "task_b.md").write_text(
        "---\ntitle: Task B\ntype: task\n---\n\nPrerequisite.\n",
        encoding="utf-8",
    )
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/workbench/dependencies?campaign=first_arc")
    assert r.status_code == 200
    data = r.get_json()
    assert "nodes" in data and "edges" in data
    assert any(e["from"] == "first_arc/task_a.md" and e["to"] == "first_arc/task_b.md" for e in data["edges"])
    assert len(data["nodes"]) >= 2


def test_workbench_dependencies_invalid_campaign(client, tmp_campaigns):
    """GET /api/workbench/dependencies with invalid campaign returns 400."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.get("/api/workbench/dependencies?campaign=_internal")
    assert r.status_code == 400


def test_workbench_create_module(client, tmp_campaigns):
    """POST /api/workbench/create-module creates dirs + stub files."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/workbench/create-module",
            json={"campaign": "new_campaign", "module": "new_module", "starting_scenes": 2, "starting_npcs": 1},
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "created"
    assert "path" in data
    root = tmp_campaigns / "new_campaign" / "new_module"
    assert root.exists()
    assert (root / "README.md").exists()
    assert (root / "scene_01.md").exists()
    assert (root / "scene_02.md").exists()
    assert (root / "npc_01.md").exists()


def test_workbench_create_module_already_exists(client, tmp_campaigns):
    """POST /api/workbench/create-module for existing module returns 409."""
    (tmp_campaigns / "existing" / "mod").mkdir(parents=True)
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/workbench/create-module",
            json={"campaign": "existing", "module": "mod"},
            content_type="application/json",
        )
    assert r.status_code == 409


def test_workbench_create_module_missing_campaign(client, tmp_campaigns):
    """POST /api/workbench/create-module without campaign returns 400."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/workbench/create-module",
            json={"module": "mod"},
            content_type="application/json",
        )
    assert r.status_code == 400


def test_workbench_chat_ok(client, tmp_campaigns):
    """POST /api/workbench/chat returns 200 when Ollama responds (mocked)."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"response": "Hello from LLM"}'
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = client.post(
            "/api/workbench/chat",
            json={"message": "Hello"},
            content_type="application/json",
        )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "ok"
    assert "reply" in data
    assert "Hello from LLM" in data["reply"]


def test_workbench_chat_ollama_down(client, tmp_campaigns):
    """POST /api/workbench/chat returns 503 when Ollama is unavailable."""
    import urllib.error

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        r = client.post(
            "/api/workbench/chat",
            json={"message": "Hello"},
            content_type="application/json",
        )
    assert r.status_code == 503
    data = r.get_json()
    assert "error" in data or "LLM" in str(data).lower() or "Ollama" in str(data)


def test_workbench_chat_missing_message(client, tmp_campaigns):
    """POST /api/workbench/chat without message returns 400."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/workbench/chat",
            json={},
            content_type="application/json",
        )
    assert r.status_code == 400


def test_workbench_chat_context_path_traversal_rejected(client, tmp_campaigns):
    """POST /api/workbench/chat with context_path outside CAMPAIGNS does not read file."""
    leak_file = tmp_campaigns.parent / "leak.txt"
    leak_file.write_text("LEAKED_CONTENT", encoding="utf-8")

    captured = []

    def capturing_urlopen(req, **kwargs):
        captured.append(req.data)
        mock = MagicMock()
        mock.read.return_value = b'{"response": "Hello"}'
        mock.__enter__ = MagicMock(return_value=mock)
        mock.__exit__ = MagicMock(return_value=False)
        return mock

    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
            r = client.post(
                "/api/workbench/chat",
                json={"message": "hi", "context_path": "../leak.txt"},
                content_type="application/json",
            )
    assert r.status_code == 200
    assert len(captured) == 1
    body = json.loads(captured[0].decode())
    assert "LEAKED_CONTENT" not in body.get("prompt", "")


def test_workbench_create_module_traversal_rejected(client, tmp_campaigns):
    """POST /api/workbench/create-module rejects traversal (secure_filename strips ..)."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/workbench/create-module",
            json={"campaign": "..", "module": "x"},
            content_type="application/json",
        )
    assert r.status_code == 400


def test_workbench_create_module_path_containment(client, tmp_campaigns):
    """POST /api/workbench/create-module enforces path containment for valid paths."""
    with patch.object(app_module, "CAMPAIGNS", tmp_campaigns):
        r = client.post(
            "/api/workbench/create-module",
            json={"campaign": "safe", "module": "mod"},
            content_type="application/json",
        )
    assert r.status_code == 200
    mod_dir = tmp_campaigns / "safe" / "mod"
    assert mod_dir.exists()
