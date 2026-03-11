# PURPOSE: Fixtures for campaign_kb Playwright E2E (search workflow Gradio)
# DEPENDENCIES: pytest, pytest-playwright
# MODIFICATION NOTES: E2E Playwright plan Phase 1.3; uses port 7861 to avoid WatchTower conflict

"""
Conftest for campaign_kb E2E. Starts Gradio search workflow on CAMPAIGN_KB_E2E_PORT (7861)
when CAMPAIGN_KB_E2E_SERVER=auto. Set CAMPAIGN_KB_E2E_SERVER=manual to assume server running.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Use 7861 to avoid conflict with WatchTower Daggr (7860)
CAMPAIGN_KB_PORT = int(os.environ.get("CAMPAIGN_KB_E2E_PORT", "7861"))
CAMPAIGN_KB_URL = f"http://127.0.0.1:{CAMPAIGN_KB_PORT}"
E2E_SERVER = os.environ.get("CAMPAIGN_KB_E2E_SERVER", "auto")


def _wait_for_server(url: str, timeout: int = 45) -> bool:
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
def campaign_kb_server():
    """Start campaign_kb Gradio search workflow if CAMPAIGN_KB_E2E_SERVER=auto."""
    if E2E_SERVER != "auto":
        yield CAMPAIGN_KB_URL
        return

    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["GRADIO_SERVER_PORT"] = str(CAMPAIGN_KB_PORT)
    env["GRADIO_SERVER_NAME"] = "127.0.0.1"
    env.setdefault("DATABASE_URL", "sqlite:///:memory:")

    proc = subprocess.Popen(
        [sys.executable, "-m", "daggr_workflows.single_app", "search"],
        cwd=str(root),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_server(CAMPAIGN_KB_URL):
        proc.terminate()
        proc.wait()
        pytest.skip("campaign_kb Gradio server did not start in time")

    yield CAMPAIGN_KB_URL
    proc.terminate()
    proc.wait(timeout=5)
