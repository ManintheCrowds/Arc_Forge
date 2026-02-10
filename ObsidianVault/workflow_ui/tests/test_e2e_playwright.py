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


def test_e2e_load_and_s1_with_fixtures(tmp_path):
    # Prepare temp Campaigns + config
    campaigns = tmp_path / "Campaigns"
    scripts = tmp_path / "scripts"
    rag_outputs = campaigns / "_rag_outputs"
    rag_outputs.mkdir(parents=True, exist_ok=True)
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "ingest_config.json").write_text("{}", encoding="utf-8")
    storyboard = rag_outputs / "first_arc_storyboard.md"
    storyboard.write_text("# Storyboard\n\nTest.", encoding="utf-8")

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["WORKFLOW_UI_PORT"] = str(port)
    env["WORKFLOW_UI_HOST"] = "127.0.0.1"
    env["WORKFLOW_UI_CAMPAIGNS_PATH"] = str(campaigns)
    env["WORKFLOW_UI_CONFIG_PATH"] = str(scripts / "ingest_config.json")
    env["WORKFLOW_UI_FAKE_RUNS"] = "1"

    app_cwd = Path(__file__).resolve().parents[1]
    proc = subprocess.Popen([sys.executable, "-m", "workflow_ui.app"], cwd=str(app_cwd), env=env)
    try:
        _wait_for_http(base_url + "/")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            assert page.locator("text=Storyboard").first.is_visible()
            assert page.locator("#pipeline-badges").is_visible()

            page.click("#run-s1")
            page.wait_for_timeout(1000)
            out = page.locator("#out-s1").inner_text()
            assert "error" not in out.lower()
            td_path = campaigns / "first_arc" / "task_decomposition.yaml"
            assert td_path.exists()
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
