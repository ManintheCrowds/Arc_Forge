# PURPOSE: Flask app for storyboard-to-encounter workflow GUI. Calls storyboard_workflow entry points.
# DEPENDENCIES: flask, yaml; scripts.storyboard_workflow, scripts.rag_pipeline (vault on sys.path).
# MODIFICATION NOTES: Phase 3 GUI; backend contract per Campaigns/docs/gui_spec.md.

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

import yaml
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

_UI_DIR = Path(__file__).resolve().parent
_VAULT = _UI_DIR.parent
_SCRIPTS = _VAULT / "scripts"
if str(_VAULT) not in sys.path:
    sys.path.insert(0, str(_VAULT))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Import after path fix (storyboard_workflow imports rag_pipeline as top-level; scripts/ must be on path)
from scripts.session_ingest import run_archivist, run_foreshadowing
from scripts.storyboard_workflow import (
    export_final_specs,
    refine_encounter,
    run_stage_1,
    run_stage_2,
)

app = Flask(__name__, static_folder=_UI_DIR / "static", template_folder=_UI_DIR / "templates")
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # 4MB
# Rate limiting: in-memory for single-process; set RATELIMIT_STORAGE_URL for Redis in multi-process.
app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")
app.config.setdefault("RATELIMIT_HEADERS_ENABLED", True)

limiter = Limiter(key_func=get_remote_address, app=app)


def _error_payload(message: str, detail: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"status": "error", "error": message, "reason": message}
    if detail:
        payload["detail"] = detail
    return payload


def _error_response(message: str, status_code: int, detail: str | None = None):
    return jsonify(_error_payload(message, detail=detail)), status_code


@app.errorhandler(429)
def ratelimit_exceeded(e):
    """Return JSON and Retry-After on rate limit (Flask-Limiter sets Retry-After when RATELIMIT_HEADERS_ENABLED)."""
    return _error_response("rate limit exceeded", 429)


SCRIPTS = _VAULT / "scripts"
CAMPAIGNS = Path(os.environ.get("WORKFLOW_UI_CAMPAIGNS_PATH", str(_VAULT / "Campaigns")))
CONFIG_PATH = Path(os.environ.get("WORKFLOW_UI_CONFIG_PATH", str(SCRIPTS / "ingest_config.json")))
CAMPAIGN_KB = _VAULT.parent / "campaign_kb"
# Base URL for campaign_kb API (proxy target); set CAMPAIGN_KB_URL to override.
CAMPAIGN_KB_URL = os.environ.get("CAMPAIGN_KB_URL", "http://127.0.0.1:8000").rstrip("/")
# Campaign KB Daggr UI (run: cd campaign_kb && python -m daggr_workflows.run_workflow ingest)
CAMPAIGN_KB_DAGGR_URL = os.environ.get("CAMPAIGN_KB_DAGGR_URL", "http://localhost:7860").rstrip("/")
# Workflow_ui Gradio app (run: python -m workflow_ui.gradio_app from ObsidianVault; default port 7861)
GRADIO_APP_URL = os.environ.get("GRADIO_APP_URL", "http://localhost:7861").rstrip("/")


def _validate_startup_paths() -> List[str]:
    """Validate CAMPAIGNS and CONFIG_PATH at startup. Returns list of user-facing error messages."""
    errors: List[str] = []
    if not CAMPAIGNS.exists():
        errors.append(f"CAMPAIGNS not found: {CAMPAIGNS}")
    elif not CAMPAIGNS.is_dir():
        errors.append(f"CAMPAIGNS is not a directory: {CAMPAIGNS}")
    if not CONFIG_PATH.exists():
        errors.append(f"CONFIG_PATH missing: {CONFIG_PATH} (required for session ingest: /api/session/archivist, /api/session/foreshadow)")
    return errors


def _arc_dir(arc_id: str) -> Path:
    return CAMPAIGNS / arc_id


def _list_arcs() -> List[str]:
    out: List[str] = []
    if not CAMPAIGNS.exists():
        return out
    for p in CAMPAIGNS.iterdir():
        if p.is_dir() and not p.name.startswith("_"):
            out.append(p.name)
    return sorted(out)


def _arc_tree(arc_id: str) -> Dict[str, Any]:
    d = _arc_dir(arc_id)
    if not d.exists():
        return {"arc_id": arc_id, "files": [], "encounters": [], "opportunities": []}
    files: List[Dict[str, Any]] = []
    for p in sorted(d.iterdir()):
        if p.name.startswith("."):
            continue
        rel = p.relative_to(d)
        if p.is_file():
            files.append({"name": rel.as_posix(), "path": str(p), "rel": rel.as_posix(), "kind": "file"})
        elif p.is_dir():
            for q in sorted(p.iterdir()):
                if q.is_file():
                    r = rel / q.name
                    files.append({"name": r.as_posix(), "path": str(q), "rel": r.as_posix(), "kind": "file"})
    enc_dir = d / "encounters"
    opp_dir = d / "opportunities"
    encounters: List[Dict[str, Any]] = []
    opportunities: List[Dict[str, Any]] = []
    for sub, out_list, label in [
        (enc_dir, encounters, "encounter"),
        (opp_dir, opportunities, "opportunity"),
    ]:
        if not sub.exists():
            continue
        for f in sorted(sub.glob("*.md")):
            stem = f.stem
            version = None
            source = None
            if "_draft_v" in stem:
                base, v = stem.rsplit("_draft_v", 1)
                try:
                    version = f"draft v{v}"
                except Exception:
                    version = stem
                source = f"{arc_id}_feedback.yaml"
            else:
                version = "final"
            rel = f.relative_to(d)
            out_list.append({
                "id": stem.split("_draft_v")[0] if "_draft_v" in stem else stem,
                "name": f.name,
                "path": str(f),
                "rel": rel.as_posix(),
                "version": version,
                "source": source,
            })
    return {"arc_id": arc_id, "files": files, "encounters": encounters, "opportunities": opportunities}


def _module_root(campaign: str, module: str) -> Path:
    return CAMPAIGNS / campaign / "Modules" / module


def _list_modules() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not CAMPAIGNS.exists():
        return out
    for campaign_dir in sorted(CAMPAIGNS.iterdir()):
        if not campaign_dir.is_dir() or campaign_dir.name.startswith("_"):
            continue
        modules_dir = campaign_dir / "Modules"
        modules: List[str] = []
        if modules_dir.exists() and modules_dir.is_dir():
            modules = sorted([p.name for p in modules_dir.iterdir() if p.is_dir()])
        out.append({"name": campaign_dir.name, "modules": modules})
    return out


def _module_tree(campaign: str, module: str) -> Dict[str, Any]:
    root = _module_root(campaign, module)
    if not root.exists():
        return {"campaign": campaign, "module": module, "files": []}
    files: List[Dict[str, Any]] = []
    for f in sorted(root.rglob("*.md")):
        rel = f.relative_to(root)
        files.append({"name": rel.as_posix(), "rel": rel.as_posix(), "path": str(f), "kind": "file"})
    return {"campaign": campaign, "module": module, "files": files}


def _write_note(path: Path, title: str, note_type: str, module: str, campaign: str) -> None:
    content = (
        "---\n"
        f"type: {note_type}\n"
        f"module: {module}\n"
        f"campaign: {campaign}\n"
        "tags: []\n"
        "depends_on: []\n"
        "date: \"\"\n"
        "location: \"\"\n"
        "status: draft\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Goals\n\n"
        "## Hooks\n\n"
        "## Encounters\n\n"
        "## Links\n\n"
        "## Notes\n"
    )
    path.write_text(content, encoding="utf-8")


def _resolve_session_path(raw: str) -> Path:
    """Resolve session/context path: relative to vault, or absolute."""
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (_VAULT / p).resolve()
    return p


def _list_session_memory_files() -> List[Dict[str, str]]:
    """List .md files under Campaigns/_session_memory. Paths are absolute for API use."""
    memory_dir = CAMPAIGNS / "_session_memory"
    if not memory_dir.exists() or not memory_dir.is_dir():
        return []
    out: List[Dict[str, str]] = []
    base_res = memory_dir.resolve()
    for f in sorted(memory_dir.glob("*.md")):
        try:
            full = f.resolve()
            if base_res in full.parents or full.parent == base_res:
                out.append({"path": str(full), "name": f.name})
        except (OSError, ValueError):
            continue
    return out


def _artifacts(arc_id: str) -> Dict[str, bool]:
    d = _arc_dir(arc_id)
    return {
        "task_decomposition": (d / "task_decomposition.yaml").exists() or (d / "task_decomposition.json").exists(),
        "task_decomposition_md": (d / "task_decomposition.md").exists(),
        "feedback": (d / f"{arc_id}_feedback.yaml").exists() or (d / f"{arc_id}_feedback.json").exists(),
        "expanded_storyboard": (d / f"{arc_id}_expanded_storyboard.md").exists(),
        "encounters_json": (d / f"{arc_id}_encounters.json").exists(),
        "has_encounters": (d / "encounters").exists() and any((d / "encounters").glob("*.md")),
        "has_opportunities": (d / "opportunities").exists() and any((d / "opportunities").glob("*.md")),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def api_status():
    campaigns_ok = CAMPAIGNS.exists() and CAMPAIGNS.is_dir()
    config_ok = CONFIG_PATH.exists()
    kb_data, kb_code = _kb_proxy_get("/openapi.json")
    kb_ok = kb_code == 200
    kb_detail = None
    if not kb_ok:
        kb_detail = kb_data.get("detail") or kb_data.get("error") or kb_data
    return jsonify({
        "campaigns": {"ok": campaigns_ok, "path": str(CAMPAIGNS)},
        "config": {"ok": config_ok, "path": str(CONFIG_PATH)},
        "campaign_kb": {"ok": kb_ok, "url": CAMPAIGN_KB_URL, "detail": kb_detail},
    })


@app.route("/api/arcs", methods=["GET"])
def api_arcs():
    return jsonify({"arcs": _list_arcs()})


@app.route("/api/modules", methods=["GET"])
def api_modules():
    return jsonify({"campaigns": _list_modules()})


@app.route("/api/modules/<campaign>/<module>/tree", methods=["GET"])
def api_module_tree(campaign, module):
    campaign = secure_filename(campaign) or ""
    module = secure_filename(module) or ""
    if not campaign or not module:
        return _error_response("invalid module", 400)
    return jsonify(_module_tree(campaign, module))


@app.route("/api/modules/<campaign>/<module>/file/<path:subpath>", methods=["GET"])
def api_module_file(campaign, module, subpath):
    campaign = secure_filename(campaign) or ""
    module = secure_filename(module) or ""
    if not campaign or not module:
        return _error_response("invalid module", 400)
    if subpath.startswith("/") or "\\" in subpath:
        return _error_response("invalid path", 400)
    base = _module_root(campaign, module)
    full = (base / subpath).resolve()
    base_res = base.resolve()
    if base_res not in full.parents:
        return _error_response("invalid path", 400)
    if not full.is_file():
        return _error_response("not_found", 404)
    try:
        return full.read_text(encoding="utf-8")
    except Exception as e:
        return _error_response("read_failed", 500, detail=str(e))


@app.route("/api/modules/create", methods=["POST"])
@limiter.limit("20/minute")
def api_modules_create():
    body = request.get_json(force=True, silent=True) or {}
    campaign = secure_filename(body.get("campaign_name") or "")
    module = secure_filename(body.get("module_name") or "")
    if not campaign or not module:
        return _error_response("campaign_name and module_name required", 400)
    root = _module_root(campaign, module)
    if root.exists():
        return _error_response("module already exists", 409)
    scene_count = int(body.get("starting_scene_count") or 1)
    npc_count = int(body.get("npc_count") or 1)
    root.mkdir(parents=True, exist_ok=False)
    (root / "Scenes").mkdir(parents=True, exist_ok=True)
    (root / "NPCs").mkdir(parents=True, exist_ok=True)
    (root / "Locations").mkdir(parents=True, exist_ok=True)
    (root / "Factions").mkdir(parents=True, exist_ok=True)
    (root / "Rules").mkdir(parents=True, exist_ok=True)
    (root / "Exports").mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(f"# {module}\n\nModule scaffold for {campaign}.\n", encoding="utf-8")
    _write_note(root / "Outline.md", f"{module} Outline", "outline", module, campaign)
    for i in range(1, max(scene_count, 0) + 1):
        _write_note(root / "Scenes" / f"scene_{i:02d}.md", f"Scene {i:02d}", "scene", module, campaign)
    for i in range(1, max(npc_count, 0) + 1):
        _write_note(root / "NPCs" / f"npc_{i:02d}.md", f"NPC {i:02d}", "npc", module, campaign)
    _write_note(root / "Locations" / "location_01.md", "Location 01", "location", module, campaign)
    _write_note(root / "Factions" / "faction_01.md", "Faction 01", "faction", module, campaign)
    _write_note(root / "Rules" / "rule_notes.md", "Rules Notes", "rule", module, campaign)
    return jsonify({"status": "created", "path": str(root)})


@app.route("/api/arc/<arc_id>/tree", methods=["GET"])
def api_arc_tree(arc_id):
    arc_id = secure_filename(arc_id) or "first_arc"
    return jsonify(_arc_tree(arc_id))


@app.route("/api/arc/<arc_id>/artifacts", methods=["GET"])
def api_arc_artifacts(arc_id):
    arc_id = secure_filename(arc_id) or "first_arc"
    return jsonify(_artifacts(arc_id))


@app.route("/api/arc/<arc_id>/task_decomposition", methods=["GET", "PUT"])
@limiter.limit("60/minute")
def api_task_decomposition(arc_id):
    arc_id = secure_filename(arc_id) or "first_arc"
    path = _arc_dir(arc_id) / "task_decomposition.yaml"
    if request.method == "GET":
        if not path.exists():
            path = _arc_dir(arc_id) / "task_decomposition.json"
        if not path.exists():
            return _error_response("not_found", 404)
        text = path.read_text(encoding="utf-8")
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(text)
        return jsonify(data)
    # PUT
    data = request.get_json(force=True, silent=True) or {}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return jsonify({"status": "saved", "path": str(path)})


@app.route("/api/arc/<arc_id>/feedback", methods=["GET", "PUT"])
@limiter.limit("60/minute")
def api_feedback(arc_id):
    arc_id = secure_filename(arc_id) or "first_arc"
    path = _arc_dir(arc_id) / f"{arc_id}_feedback.yaml"
    if request.method == "GET":
        if not path.exists():
            path = _arc_dir(arc_id) / f"{arc_id}_feedback.json"
        if not path.exists():
            return jsonify({"arc_id": arc_id, "encounters": []})
        text = path.read_text(encoding="utf-8")
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(text)
        return jsonify(data)
    # PUT
    data = request.get_json(force=True, silent=True) or {}
    data["arc_id"] = data.get("arc_id") or arc_id
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return jsonify({"status": "saved", "path": str(path)})


@app.route("/api/arc/<arc_id>/file/<path:subpath>", methods=["GET"])
def api_arc_file(arc_id, subpath):
    arc_id = secure_filename(arc_id) or "first_arc"
    # Reject absolute or backslash segments; allow ".." but only when resolved path stays under arc.
    if subpath.startswith("/") or "\\" in subpath:
        return _error_response("invalid path", 400)
    base = _arc_dir(arc_id)
    full = (base / subpath).resolve()
    base_res = base.resolve()
    if base_res not in full.parents:
        return _error_response("invalid path", 400)
    if not full.is_file():
        return _error_response("not_found", 404)
    try:
        return full.read_text(encoding="utf-8")
    except Exception as e:
        return _error_response("read_failed", 500, detail=str(e))


@app.route("/api/run/stage1", methods=["POST"])
@limiter.limit("30/minute")
def api_run_stage1():
    body = request.get_json(force=True, silent=True) or {}
    storyboard_path = Path(body.get("storyboard_path") or str(CAMPAIGNS / "_rag_outputs" / "first_arc_storyboard.md"))
    arc_id = body.get("arc_id") or "first_arc"
    output_dir = Path(body.get("output_dir") or str(CAMPAIGNS))
    if not storyboard_path.is_absolute():
        storyboard_path = (CAMPAIGNS / storyboard_path).resolve()
    if not storyboard_path.exists():
        return _error_response(
            "storyboard not found",
            400,
            detail=f"Expected under {CAMPAIGNS / '_rag_outputs'} or provide storyboard_path. Got: {storyboard_path}",
        )
    if os.environ.get("WORKFLOW_UI_FAKE_RUNS") == "1":
        out_dir = (output_dir / arc_id).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        td_path = out_dir / "task_decomposition.yaml"
        td_data = {
            "arc_id": arc_id,
            "storyboard_ref": str(storyboard_path),
            "encounters": [],
            "opportunities": [],
            "sequence_constraints": [],
        }
        with open(td_path, "w", encoding="utf-8") as f:
            yaml.dump(td_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return jsonify({"status": "success", "path": str(td_path), "fake": True})
    try:
        res = run_stage_1(storyboard_path.resolve(), arc_id, output_dir.resolve(), body.get("storyboard_ref"))
        return jsonify(res)
    except Exception as e:
        return _error_response("stage1_failed", 500, detail=str(e))


@app.route("/api/run/stage2", methods=["POST"])
@limiter.limit("30/minute")
def api_run_stage2():
    body = request.get_json(force=True, silent=True) or {}
    arc_id = body.get("arc_id") or "first_arc"
    td_path = Path(body.get("task_decomposition_path") or str(_arc_dir(arc_id) / "task_decomposition.yaml"))
    storyboard_path = Path(body.get("storyboard_path") or str(CAMPAIGNS / "_rag_outputs" / "first_arc_storyboard.md"))
    config_path = Path(body.get("config_path") or str(CONFIG_PATH))
    output_dir = _arc_dir(arc_id)
    if not td_path.exists():
        return _error_response(
            "task_decomposition not found",
            400,
            detail=f"Expected {td_path} (or pass task_decomposition_path).",
        )
    if not storyboard_path.exists():
        return _error_response(
            "storyboard not found",
            400,
            detail=f"Expected under {CAMPAIGNS / '_rag_outputs'} or provide storyboard_path. Got: {storyboard_path}",
        )
    try:
        res = run_stage_2(td_path.resolve(), storyboard_path.resolve(), arc_id, config_path.resolve(), output_dir)
        return jsonify(res)
    except Exception as e:
        return _error_response("stage2_failed", 500, detail=str(e))


@app.route("/api/run/stage4", methods=["POST"])
@limiter.limit("30/minute")
def api_run_stage4():
    body = request.get_json(force=True, silent=True) or {}
    draft_path = Path(body.get("draft_path", ""))
    feedback_path = body.get("feedback_path")
    arc_id = body.get("arc_id")
    if not draft_path or not draft_path.exists():
        return _error_response("draft_path required", 400, detail="draft_path must exist.")
    if not feedback_path and arc_id:
        feedback_path = str(_arc_dir(arc_id) / f"{arc_id}_feedback.yaml")
        if not Path(feedback_path).exists():
            feedback_path = str(_arc_dir(arc_id) / f"{arc_id}_feedback.json")
    feedback_path = Path(feedback_path) if feedback_path else None
    if not feedback_path or not feedback_path.exists():
        return _error_response(
            "feedback_path required",
            400,
            detail="Provide feedback_path or arc_id; feedback file must exist.",
        )
    try:
        from scripts.rag_pipeline import load_pipeline_config
        cfg = load_pipeline_config(Path(body.get("config_path") or str(CONFIG_PATH)))
        rag_config = cfg["rag"]
        res = refine_encounter(draft_path.resolve(), feedback_path.resolve(), rag_config)
        return jsonify(res)
    except Exception as e:
        return _error_response("stage4_failed", 500, detail=str(e))


@app.route("/api/run/stage5", methods=["POST"])
@limiter.limit("30/minute")
def api_run_stage5():
    body = request.get_json(force=True, silent=True) or {}
    arc_id = body.get("arc_id") or "first_arc"
    arc_dir = Path(body.get("arc_dir") or str(_arc_dir(arc_id)))
    campaign_kb_path = Path(body.get("campaign_kb_path") or str(CAMPAIGN_KB))
    storyboard_path = body.get("storyboard_path")
    if storyboard_path:
        storyboard_path = Path(storyboard_path)
    else:
        storyboard_path = CAMPAIGNS / "_rag_outputs" / f"{arc_id}_storyboard.md"
        if not storyboard_path.exists():
            storyboard_path = CAMPAIGNS / "_rag_outputs" / "first_arc_storyboard.md"
        storyboard_path = storyboard_path if storyboard_path.exists() else None
    try:
        res = export_final_specs(
            arc_id,
            arc_dir.resolve(),
            campaign_kb_path.resolve(),
            storyboard_path=storyboard_path.resolve() if storyboard_path and storyboard_path.exists() else None,
            vault_root=_VAULT,
        )
        return jsonify(res)
    except Exception as e:
        return _error_response("stage5_failed", 500, detail=str(e))


@app.route("/api/session/files", methods=["GET"])
def api_session_files():
    """List .md files under Campaigns/_session_memory for dropdown (Foreshadow context)."""
    return jsonify({"files": _list_session_memory_files()})


@app.route("/api/session/file/<path:subpath>", methods=["GET"])
def api_session_file(subpath):
    """Read a file under Campaigns/_session_memory. Path restricted to that directory (no traversal)."""
    memory_dir = (CAMPAIGNS / "_session_memory").resolve()
    safe = secure_filename(Path(subpath).name) if subpath else ""
    if not safe:
        return _error_response("invalid path", 400)
    full = (memory_dir / safe).resolve()
    if full.parent != memory_dir or not full.is_file():
        return _error_response("not_found", 404)
    try:
        return full.read_text(encoding="utf-8")
    except Exception as e:
        return _error_response("read_failed", 500, detail=str(e))


@app.route("/api/session/archivist", methods=["POST"])
def api_session_archivist():
    body = request.get_json(force=True, silent=True) or {}
    session_path_raw = body.get("session_path")
    if not session_path_raw:
        return _error_response("session_path required", 400)
    session_path = _resolve_session_path(str(session_path_raw))
    if not session_path.exists() or not session_path.is_file():
        return _error_response(
            "session note not found",
            400,
            detail=f"Expected a file under {CAMPAIGNS / '_session_memory'} or provide an absolute path. Got: {session_path}",
        )
    output_path = body.get("output_path")
    output_path = _resolve_session_path(str(output_path)) if output_path else None
    try:
        res = run_archivist(session_path, CONFIG_PATH, output_path=output_path, system_prompt_path=None)
        return jsonify(res)
    except Exception as e:
        return _error_response("archivist_failed", 500, detail=str(e))


@app.route("/api/session/foreshadow", methods=["POST"])
def api_session_foreshadow():
    body = request.get_json(force=True, silent=True) or {}
    context_path_raw = body.get("context_path")
    if not context_path_raw:
        return _error_response("context_path required", 400)
    context_path = _resolve_session_path(str(context_path_raw))
    if not context_path.exists() or not context_path.is_file():
        return _error_response(
            "context file not found",
            400,
            detail=f"Expected a file under {CAMPAIGNS / '_session_memory'} or provide an absolute path. Got: {context_path}",
        )
    output_path = body.get("output_path")
    output_path = _resolve_session_path(str(output_path)) if output_path else None
    try:
        res = run_foreshadowing(context_path, CONFIG_PATH, output_path=output_path, system_prompt_path=None)
        return jsonify(res)
    except Exception as e:
        return _error_response("foreshadow_failed", 500, detail=str(e))


def _kb_proxy_get(path: str, params: Dict[str, str] | None = None) -> tuple[Any, int]:
    """Proxy GET to campaign_kb. Returns (response_data, status_code)."""
    url = f"{CAMPAIGN_KB_URL}{path}"
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            if body.strip():
                return json.loads(body), e.code
            return _error_payload("campaign_kb_error", detail=e.reason), e.code
        except Exception:
            return _error_payload("campaign_kb_error", detail=str(e)), e.code
    except Exception as e:
        return _error_payload("campaign_kb_unreachable", detail=str(e)), 503


def _kb_proxy_post(path: str, body: Dict[str, Any] | None = None) -> tuple[Any, int]:
    """Proxy POST to campaign_kb. Returns (response_data, status_code)."""
    url = f"{CAMPAIGN_KB_URL}{path}"
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            if body.strip():
                return json.loads(body), e.code
            return _error_payload("campaign_kb_error", detail=e.reason), e.code
        except Exception:
            return _error_payload("campaign_kb_error", detail=str(e)), e.code
    except Exception as e:
        return _error_payload("campaign_kb_unreachable", detail=str(e)), 503


@app.route("/api/kb/status", methods=["GET"])
def api_kb_status():
    """Check if campaign_kb is reachable."""
    data, code = _kb_proxy_get("/openapi.json")
    if code == 200:
        return jsonify({"status": "ok", "campaign_kb_url": CAMPAIGN_KB_URL})
    return jsonify(data), code


@app.route("/api/kb/search", methods=["GET"])
def api_kb_search():
    """Proxy search to campaign_kb GET /search."""
    query = request.args.get("query", "").strip()
    if not query:
        return _error_response("query required", 400)
    params = {
        "query": query,
        "limit": request.args.get("limit", "20"),
        "source_name": request.args.get("source_name") or None,
        "doc_type": request.args.get("doc_type") or None,
    }
    data, code = _kb_proxy_get("/search", params)
    return jsonify(data), code


@app.route("/api/kb/ingest/pdfs", methods=["POST"])
def api_kb_ingest_pdfs():
    """Proxy PDF ingest to campaign_kb POST /ingest/pdfs."""
    body = request.get_json(force=True, silent=True) or {}
    data, code = _kb_proxy_post("/ingest/pdfs", {"pdf_root": body.get("pdf_root")})
    return jsonify(data), code


@app.route("/api/kb/merge", methods=["POST"])
def api_kb_merge():
    """Proxy merge to campaign_kb POST /merge."""
    body = request.get_json(force=True, silent=True) or {}
    data, code = _kb_proxy_post("/merge", {
        "output_path": body.get("output_path"),
        "max_citations": body.get("max_citations", 25),
    })
    return jsonify(data), code


@app.route("/tools/kb-daggr")
def tools_kb_daggr():
    """Redirect to Campaign KB Daggr UI (ingest/search/merge workflows)."""
    return redirect(CAMPAIGN_KB_DAGGR_URL, code=302)


@app.route("/tools/gradio")
def tools_gradio():
    """Redirect to workflow_ui Gradio app (KB search demo). Run: python -m workflow_ui.gradio_app from ObsidianVault."""
    return redirect(GRADIO_APP_URL, code=302)


@app.route("/api/diagrams/pipeline")
def api_diagrams_pipeline():
    diagrams = _VAULT / "Campaigns" / "docs" / "workflow_diagrams.md"
    if diagrams.exists():
        return diagrams.read_text(encoding="utf-8")
    return "Pipeline diagram not found.", 404


@app.route("/api/diagrams/pipeline_mermaid")
def api_diagrams_pipeline_mermaid():
    diagrams = _VAULT / "Campaigns" / "docs" / "workflow_diagrams.md"
    if not diagrams.exists():
        return jsonify({"mermaid": ""})
    text = diagrams.read_text(encoding="utf-8")
    start = text.find("```mermaid")
    if start == -1:
        return jsonify({"mermaid": ""})
    start += len("```mermaid")
    end = text.find("```", start)
    mermaid = text[start:end].strip() if end != -1 else text[start:].strip()
    return jsonify({"mermaid": mermaid})


def _openapi_spec() -> Dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "workflow_ui API",
            "version": "0.1.0",
            "description": "Workflow UI API for storyboard-to-encounter pipeline.",
        },
        "paths": {
            "/api/arcs": {"get": {"summary": "List arcs", "responses": {"200": {"description": "OK"}}}},
            "/api/arc/{arc_id}/tree": {"get": {"summary": "Arc file tree", "responses": {"200": {"description": "OK"}}}},
            "/api/arc/{arc_id}/artifacts": {"get": {"summary": "Arc artifacts", "responses": {"200": {"description": "OK"}}}},
            "/api/arc/{arc_id}/task_decomposition": {
                "get": {"summary": "Get task decomposition", "responses": {"200": {"description": "OK"}}},
                "put": {"summary": "Save task decomposition", "responses": {"200": {"description": "OK"}}},
            },
            "/api/arc/{arc_id}/feedback": {
                "get": {"summary": "Get feedback", "responses": {"200": {"description": "OK"}}},
                "put": {"summary": "Save feedback", "responses": {"200": {"description": "OK"}}},
            },
            "/api/arc/{arc_id}/file/{subpath}": {"get": {"summary": "Read arc file", "responses": {"200": {"description": "OK"}}}},
            "/api/run/stage1": {"post": {"summary": "Run Stage 1", "responses": {"200": {"description": "OK"}}}},
            "/api/run/stage2": {"post": {"summary": "Run Stage 2", "responses": {"200": {"description": "OK"}}}},
            "/api/run/stage4": {"post": {"summary": "Run Stage 4", "responses": {"200": {"description": "OK"}}}},
            "/api/run/stage5": {"post": {"summary": "Run Stage 5", "responses": {"200": {"description": "OK"}}}},
            "/api/session/files": {"get": {"summary": "List session files", "responses": {"200": {"description": "OK"}}}},
            "/api/session/file/{subpath}": {"get": {"summary": "Read session file", "responses": {"200": {"description": "OK"}}}},
            "/api/session/archivist": {"post": {"summary": "Run Archivist", "responses": {"200": {"description": "OK"}}}},
            "/api/session/foreshadow": {"post": {"summary": "Run Foreshadow", "responses": {"200": {"description": "OK"}}}},
            "/api/kb/status": {"get": {"summary": "Campaign KB status", "responses": {"200": {"description": "OK"}}}},
            "/api/kb/search": {"get": {"summary": "Campaign KB search", "responses": {"200": {"description": "OK"}}}},
            "/api/kb/ingest/pdfs": {"post": {"summary": "Campaign KB ingest PDFs", "responses": {"200": {"description": "OK"}}}},
            "/api/kb/merge": {"post": {"summary": "Campaign KB merge", "responses": {"200": {"description": "OK"}}}},
            "/api/diagrams/pipeline_mermaid": {"get": {"summary": "Pipeline mermaid", "responses": {"200": {"description": "OK"}}}},
        },
    }


@app.route("/openapi.json", methods=["GET"])
def openapi_json():
    return jsonify(_openapi_spec())


@app.route("/docs", methods=["GET"])
def openapi_docs():
    return """
<!doctype html>
<html>
  <head>
    <title>workflow_ui API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({ url: '/openapi.json', dom_id: '#swagger-ui' });
    </script>
  </body>
</html>
""".strip()


if __name__ == "__main__":
    startup_errors = _validate_startup_paths()
    if startup_errors:
        for msg in startup_errors:
            print(msg, file=sys.stderr)
        sys.exit(1)
    debug_enabled = os.environ.get("FLASK_ENV") == "development" or os.environ.get("FLASK_DEBUG") == "1"
    host = os.environ.get("WORKFLOW_UI_HOST", "127.0.0.1")
    port = int(os.environ.get("WORKFLOW_UI_PORT", "5050"))
    app.run(host=host, port=port, debug=debug_enabled)
