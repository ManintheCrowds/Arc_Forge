# PURPOSE: Human-in-the-loop consent for first cloud AI call.
# DEPENDENCIES: pathlib
# MODIFICATION NOTES: AI security P3; one-time confirm before OpenAI/Anthropic.

"""
One-time consent before first cloud AI (OpenAI, Anthropic) call.
Stores consent in ~/.config/arc_forge/cloud_ai_consent or env CLOUD_AI_CONSENT=1
"""

import os
from pathlib import Path

CONSENT_DIR = Path.home() / ".config" / "arc_forge"
CONSENT_FILE = CONSENT_DIR / "cloud_ai_consent"


def has_cloud_ai_consent() -> bool:
    """Return True if user has consented to cloud AI (OpenAI/Anthropic)."""
    if os.environ.get("CLOUD_AI_CONSENT", "").strip() == "1":
        return True
    if CONSENT_FILE.exists():
        try:
            return CONSENT_FILE.read_text().strip() == "1"
        except OSError:
            return False
    return False


def set_cloud_ai_consent() -> None:
    """Record that user has consented to cloud AI."""
    CONSENT_DIR.mkdir(parents=True, exist_ok=True)
    CONSENT_FILE.write_text("1")


def require_cloud_ai_consent() -> bool:
    """Return True if consented. Raise if not (caller should prompt and retry)."""
    if has_cloud_ai_consent():
        return True
    raise RuntimeError(
        "Cloud AI (OpenAI/Anthropic) consent required. "
        f"Create {CONSENT_FILE} with content '1' or set CLOUD_AI_CONSENT=1"
    )
