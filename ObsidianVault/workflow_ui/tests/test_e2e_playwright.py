# PURPOSE: Basic UI E2E coverage with Playwright (optional).
# DEPENDENCIES: playwright, pytest
# MODIFICATION NOTES: Wave C E2E baseline; skipped unless env configured.

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402


def _get_env(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value else None


def _free_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    _, port = sock.getsockname()
    sock.close()
    return port


def _wait_for_http(url: str, timeout_s: int = 15) -> None:
    import urllib.request

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Server did not start at {url}")


def _start_app(campaigns: Path, scripts: Path) -> tuple[subprocess.Popen, str]:
    rag_outputs = campaigns / "_rag_outputs"
    rag_outputs.mkdir(parents=True, exist_ok=True)
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "ingest_config.json").write_text("{}", encoding="utf-8")
    (rag_outputs / "first_arc_storyboard.md").write_text("# Storyboard\n\nTest.", encoding="utf-8")

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["WORKFLOW_UI_PORT"] = str(port)
    env["WORKFLOW_UI_HOST"] = "127.0.0.1"
    env["WORKFLOW_UI_CAMPAIGNS_PATH"] = str(campaigns)
    env["WORKFLOW_UI_CONFIG_PATH"] = str(scripts / "ingest_config.json")
    env["WORKFLOW_UI_FAKE_RUNS"] = "1"

    vault_root = Path(__file__).resolve().parents[2]
    proc = subprocess.Popen([sys.executable, "-m", "workflow_ui.app"], cwd=str(vault_root), env=env)
    _wait_for_http(base_url + "/")
    return proc, base_url


def _stop_app(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


def _dismiss_first_run_overlay(page):
    """Dismiss UW-10 first-run overlay so Legacy buttons are clickable."""
    page.evaluate("""
        localStorage.setItem('workflow_ui:first_run_dismissed', '1');
        const el = document.getElementById('first-run-overlay');
        if (el) el.classList.remove('visible');
    """)


def test_e2e_load_and_s1_with_fixtures(tmp_path):
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            assert page.locator("text=Storyboard").first.is_visible()
            assert page.locator("#pipeline-badges").is_visible()

            page.click('button[data-workspace="legacy"]')
            page.wait_for_timeout(500)
            _dismiss_first_run_overlay(page)
            page.wait_for_timeout(200)
            page.click("#run-s1")
            page.wait_for_timeout(1000)
            out = page.locator("#out-s1").inner_text()
            assert "error" not in out.lower()
            td_path = campaigns / "first_arc" / "task_decomposition.yaml"
            assert td_path.exists()
            browser.close()
    finally:
        _stop_app(proc)


def test_e2e_workbench_load_and_create_module(tmp_path):
    """Workbench: module selector, create module, verify dirs created."""
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(800)

            assert page.locator("#workspace-workbench").is_visible()
            assert page.locator("#module-campaign").is_visible()
            assert page.locator("#module-tree").is_visible()
            assert page.locator("#create-module-btn").is_visible()

            page.fill("#create-campaign", "E2ETestCampaign")
            page.fill("#create-module", "E2ETestModule")
            page.click("#create-module-btn")
            page.wait_for_timeout(1000)

            out = page.locator("#create-module-out").inner_text()
            assert "error" not in out.lower()
            mod_dir = campaigns / "E2ETestCampaign" / "E2ETestModule"
            assert mod_dir.exists()
            assert (mod_dir / "README.md").exists()
            browser.close()
    finally:
        _stop_app(proc)


def test_e2e_workbench_workflow_run_stage(tmp_path):
    """Workbench: run workflow node (S1), assert artifact output."""
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(1500)

            page.click('button[data-right="workflow"]')
            page.wait_for_timeout(1200)
            page.wait_for_selector("#workflow-graph .mermaid", state="visible")
            page.evaluate("window.workflowSelect && window.workflowSelect('brainstorm')")
            page.wait_for_timeout(300)
            page.click("#run-workflow-node")
            page.wait_for_timeout(2000)

            td_path = campaigns / "first_arc" / "task_decomposition.yaml"
            assert td_path.exists()
            browser.close()
    finally:
        _stop_app(proc)


def test_e2e_workbench_note_editor_load(tmp_path):
    """Workbench: fixture with module + notes; click tree item; assert content loads in editor."""
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    mod_dir = campaigns / "E2ENoteCampaign" / "E2ENoteModule"
    mod_dir.mkdir(parents=True)
    (mod_dir / "scene_01.md").write_text(
        "---\ntype: scene\ntitle: Scene 01\n---\n\n# Scene 01\n\nFixture content.",
        encoding="utf-8",
    )
    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(800)

            page.select_option("#module-campaign", "E2ENoteCampaign")
            page.wait_for_timeout(600)
            page.select_option("#module-select", "E2ENoteModule")
            page.wait_for_timeout(800)

            page.wait_for_selector("li.tree-node[data-path*='scene_01']", state="visible", timeout=5000)
            page.click("li.tree-node[data-path*='scene_01']")
            page.wait_for_timeout(800)

            editor = page.locator("#note-editor")
            content = editor.input_value()
            assert "Scene" in content or "scene" in content
            browser.close()
    finally:
        _stop_app(proc)


def test_e2e_legacy_s2_drafts(tmp_path):
    """Legacy: fixture with task_decomposition + storyboard; run S2; assert encounter drafts."""
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    arc_dir = campaigns / "first_arc"
    arc_dir.mkdir(parents=True)
    (campaigns / "_rag_outputs").mkdir(parents=True, exist_ok=True)
    (campaigns / "_rag_outputs" / "first_arc_storyboard.md").write_text("# Storyboard\n\nTest.", encoding="utf-8")
    (arc_dir / "task_decomposition.yaml").write_text(
        "arc_id: first_arc\nencounters: []\nopportunities: []\n",
        encoding="utf-8",
    )
    (scripts / "ingest_config.json").write_text("{}", encoding="utf-8")

    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            page.click('button[data-workspace="legacy"]')
            page.wait_for_timeout(500)
            _dismiss_first_run_overlay(page)
            page.wait_for_timeout(200)

            page.click('button[data-tab="s2"]')
            page.wait_for_timeout(400)
            page.click("#run-s2")
            page.wait_for_timeout(2000)

            enc_dir = arc_dir / "encounters"
            assert enc_dir.exists()
            drafts = list(enc_dir.glob("*_draft_v1.md"))
            assert len(drafts) >= 1
            out = page.locator("#out-s2").inner_text()
            assert "error" not in out.lower()
            browser.close()
    finally:
        _stop_app(proc)


def test_e2e_legacy_s4_refine(tmp_path):
    """Legacy: fixture with draft + feedback; run S4; assert new _draft_v2.md."""
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    arc_dir = campaigns / "first_arc"
    enc_dir = arc_dir / "encounters"
    enc_dir.mkdir(parents=True)
    (enc_dir / "highway_chase_draft_v1.md").write_text("# Highway Chase\n\n## Setup\nOriginal.\n", encoding="utf-8")
    (arc_dir / "first_arc_feedback.yaml").write_text(
        "arc_id: first_arc\nencounters:\n  - id: highway_chase\n    feedback:\n      - type: expand\n        target: Mechanics\n        instruction: Add Pilot.\n",
        encoding="utf-8",
    )
    (campaigns / "_rag_outputs").mkdir(parents=True, exist_ok=True)
    (campaigns / "_rag_outputs" / "first_arc_storyboard.md").write_text("# Storyboard\n", encoding="utf-8")
    (scripts / "ingest_config.json").write_text("{}", encoding="utf-8")

    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            page.click('button[data-workspace="legacy"]')
            page.wait_for_timeout(500)
            _dismiss_first_run_overlay(page)
            page.wait_for_timeout(400)

            page.click('button[data-tab="s4"]')
            page.wait_for_timeout(600)
            page.select_option("#s4-draft", index=1)
            page.wait_for_timeout(300)
            page.click("#run-s4")
            page.wait_for_timeout(2000)

            v2_files = list(enc_dir.glob("*_draft_v2.md"))
            assert len(v2_files) >= 1
            out = page.locator("#out-s4").inner_text()
            assert "error" not in out.lower()
            browser.close()
    finally:
        _stop_app(proc)


def test_e2e_legacy_s5_export(tmp_path):
    """Legacy: fixture with drafts; run S5; assert artifacts."""
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    arc_dir = campaigns / "first_arc"
    enc_dir = arc_dir / "encounters"
    enc_dir.mkdir(parents=True)
    (enc_dir / "foo_draft_v1.md").write_text("# Foo\n\nSetup.\n", encoding="utf-8")
    (campaigns / "_rag_outputs").mkdir(parents=True, exist_ok=True)
    (campaigns / "_rag_outputs" / "first_arc_storyboard.md").write_text("# Storyboard\n", encoding="utf-8")
    (scripts / "ingest_config.json").write_text("{}", encoding="utf-8")

    proc, base_url = _start_app(campaigns, scripts)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            page.click('button[data-workspace="legacy"]')
            page.wait_for_timeout(500)
            _dismiss_first_run_overlay(page)
            page.wait_for_timeout(200)

            page.click('button[data-tab="s5"]')
            page.wait_for_timeout(400)
            page.click("#run-s5")
            page.wait_for_timeout(2000)

            expanded = arc_dir / "first_arc_expanded_storyboard.md"
            json_path = arc_dir / "first_arc_encounters.json"
            assert expanded.exists()
            assert json_path.exists()
            out = page.locator("#out-s5").inner_text()
            assert "error" not in out.lower()
            browser.close()
    finally:
        _stop_app(proc)
