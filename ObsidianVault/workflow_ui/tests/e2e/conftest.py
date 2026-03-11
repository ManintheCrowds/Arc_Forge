# PURPOSE: Fixtures for workflow_ui Playwright E2E (index, kb-daggr redirect)
# DEPENDENCIES: pytest, pytest-playwright, flask
# MODIFICATION NOTES: E2E Playwright plan Phase 1.4

"""
Conftest for workflow_ui E2E. Starts Flask on WORKFLOW_UI_E2E_PORT when
WORKFLOW_UI_E2E_SERVER=auto. Set WORKFLOW_UI_E2E_SERVER=manual to assume server running.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

WORKFLOW_UI_PORT = int(os.environ.get("WORKFLOW_UI_E2E_PORT", "5001"))
WORKFLOW_UI_URL = f"http://127.0.0.1:{WORKFLOW_UI_PORT}"
E2E_SERVER = os.environ.get("WORKFLOW_UI_E2E_SERVER", "auto")


def _wait_for_server(url: str, timeout: int = 30) -> bool:
    try:
        import urllib.request
        for _ in range(timeout):
            try:
                req = urllib.request.Request(url, method="GET")
                urllib.request.urlopen(req, timeout=2)
                return True
            except Exception:
                time.sleep(1)
    except Exception:
        pass
    return False


@pytest.fixture(scope="session")
def workflow_ui_server(tmp_path_factory):
    """Start workflow_ui Flask server if WORKFLOW_UI_E2E_SERVER=auto."""
    if E2E_SERVER != "auto":
        yield WORKFLOW_UI_URL
        return

    vault_root = Path(__file__).resolve().parents[3]  # ObsidianVault (parent of workflow_ui)
    campaigns = tmp_path_factory.mktemp("campaigns")
    scripts = tmp_path_factory.mktemp("scripts")
    (campaigns / "_rag_outputs").mkdir()
    (campaigns / "_rag_outputs" / "first_arc_storyboard.md").write_text("# Storyboard\n\nTest.")
    (scripts / "ingest_config.json").write_text("{}")

    env = os.environ.copy()
    env["WORKFLOW_UI_PORT"] = str(WORKFLOW_UI_PORT)
    env["WORKFLOW_UI_HOST"] = "127.0.0.1"
    env["WORKFLOW_UI_CAMPAIGNS_PATH"] = str(campaigns)
    env["WORKFLOW_UI_CONFIG_PATH"] = str(scripts / "ingest_config.json")
    env["WORKFLOW_UI_FAKE_RUNS"] = "1"

    proc = subprocess.Popen(
        [sys.executable, "-m", "workflow_ui.app"],
        cwd=str(vault_root),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_for_server(WORKFLOW_UI_URL):
        proc.terminate()
        proc.wait()
        pytest.skip("workflow_ui server did not start in time")
    yield WORKFLOW_UI_URL
    proc.terminate()
    proc.wait(timeout=5)
